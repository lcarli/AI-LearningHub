---
tags: [observability, opentelemetry, multi-agent, genai-conventions, azure-monitor, foundry, python]
---
# Lab 050 : Observabilité multi-agents avec les conventions sémantiques GenAI

<div class="lab-meta">
  <span><strong>Niveau :</strong> <span class="level-badge level-400">L400</span></span>
  <span><strong>Parcours :</strong> <a href="../paths/foundry/">🏭 Microsoft Foundry</a></span>
  <span><strong>Durée :</strong> ~120 min</span>
  <span><strong>💰 Coût :</strong> <span class="level-badge cost-free">Gratuit</span> — Analyse de traces hors ligne avec le jeu de données fourni (Azure Monitor optionnel)</span>
</div>

## Ce que vous apprendrez

- Appliquer les **conventions sémantiques GenAI** aux systèmes multi-agents : spans d'agent, spans de modèle, spans d'outil
- Tracer les **transferts entre agents**, les décisions de routage et les patterns de relance
- Distinguer les span kinds `INTERNAL` (logique de l'agent) vs `CLIENT` (appels LLM/outils)
- Analyser les **scores de qualité**, les **coûts en tokens** et la **latence** dans un pipeline multi-agents
- Construire des **métriques de tableau de bord** d'observabilité à partir de données de spans brutes
- Comprendre comment les conventions standardisent la télémétrie entre **Foundry, Semantic Kernel, LangChain, AutoGen**

!!! abstract "Prérequis"
    Complétez d'abord le **[Lab 049 : Foundry IQ — Traçage des agents](lab-049-foundry-iq-agent-tracing.md)**. Ce lab suppose une familiarité avec les spans OpenTelemetry, les attributs et les conventions GenAI.

## Introduction

![Traçage multi-agents](../../assets/diagrams/multi-agent-tracing.svg)

Le traçage d'un seul agent est difficile. Le traçage **multi-agents** est exponentiellement plus complexe. Quand un Router transfère à un Spécialiste, qui appelle des outils, qui transmet les résultats à un Réviseur — vous avez besoin d'un moyen standard pour capturer chaque étape afin de pouvoir reconstituer le flux d'exécution complet.

Les **conventions sémantiques GenAI d'OpenTelemetry** résolvent ce problème avec trois types de spans :

| Type de span | Kind | Attributs clés | Exemple |
|-----------|------|----------------|---------|
| **Span d'agent** | `INTERNAL` | `gen_ai.agent.name`, `gen_ai.agent.id` | Router, ProductSpec, Reviewer |
| **Span de modèle** | `CLIENT` | `gen_ai.request.model`, `gen_ai.usage.*_tokens` | `chat gpt-4o` |
| **Span d'outil** | `CLIENT` | `gen_ai.tool.name` | `search_products` |

### Le scénario

OutdoorGear Inc. a migré vers un **système multi-agents** avec 4 agents spécialistes orchestrés par un Router :

1. **Router Agent** — classifie les requêtes entrantes et les dispatche au bon spécialiste
2. **Product Specialist** — gère la recherche de produits et les recommandations
3. **Order Specialist** — traite les statuts de commandes et les requêtes d'expédition
4. **Support Specialist** — gère les plaintes et les sujets sensibles
5. **Reviewer Agent** — vérifie chaque réponse pour la qualité et la conformité aux politiques

Vous disposez de **5 traces complexes** avec 46 spans montrant le pipeline complet des agents, y compris une trace avec un **échec de revue et une relance**.

---

## Prérequis

| Prérequis | Pourquoi |
|---|---|
| Python 3.10+ | Exécuter les scripts d'analyse |
| `pandas` | Analyser les données de spans |
| Lab 049 complété | Compréhension des bases d'OpenTelemetry |

```bash
pip install pandas
```

---

!!! tip "Démarrage rapide avec GitHub Codespaces"
    [![Ouvrir dans GitHub Codespaces](https://github.com/codespaces/badge.svg)](https://codespaces.new/lcarli/AI-LearningHub?quickstart=1)

    Toutes les dépendances sont préinstallées dans le devcontainer.


## 📦 Fichiers d'accompagnement

!!! note "Téléchargez ces fichiers avant de commencer le lab"
    Enregistrez tous les fichiers dans un dossier `lab-050/` dans votre répertoire de travail.

| Fichier | Description | Télécharger |
|------|-------------|----------|
| `broken_conventions.py` | Exercice de correction de bugs (3 bugs + auto-tests) | [📥 Télécharger](https://github.com/lcarli/AI-LearningHub/raw/main/docs/docs/en/labs/lab-050/broken_conventions.py) |
| `dashboard_builder.py` | Script de démarrage avec TODOs | [📥 Télécharger](https://github.com/lcarli/AI-LearningHub/raw/main/docs/docs/en/labs/lab-050/dashboard_builder.py) |
| `multi_agent_spans.csv` | Jeu de données | [📥 Télécharger](https://github.com/lcarli/AI-LearningHub/raw/main/docs/docs/en/labs/lab-050/multi_agent_spans.csv) |

---

## Étape 1 : Comprendre la structure des traces multi-agents

Dans un système multi-agents, la trace forme un **arbre** :

```
root: router_agent (INTERNAL)
├── classify_query (CLIENT, gpt-4o-mini)
├── product_specialist (INTERNAL)
│   ├── search_reasoning (CLIENT, gpt-4o)
│   ├── search_products (CLIENT, tool)
│   └── format_response (CLIENT, gpt-4o)
└── reviewer (INTERNAL)
    └── quality_check (CLIENT, gpt-4o-mini)
```

Conventions clés :

- Les **spans d'agent** sont `INTERNAL` — ils représentent la logique propre et l'orchestration de l'agent
- Les **appels LLM** sont `CLIENT` — requêtes sortantes vers les points de terminaison de modèles
- Les **appels d'outils** sont `CLIENT` — requêtes sortantes vers les outils/API
- Les relations **parent-enfant** montrent la chaîne de transfert
- **`gen_ai.agent.name`** est défini UNIQUEMENT sur les spans d'agent, pas sur les spans LLM/outils

!!! tip "Pourquoi `INTERNAL` pour les agents ?"
    La prise de décision d'un agent se fait localement (routage, planification, récupération en mémoire). Elle ne franchit pas de frontière réseau — donc c'est `INTERNAL`. L'appel LLM que l'agent *effectue* est `CLIENT` car il passe par le réseau vers une API.

---

## Étape 2 : Charger et explorer les données de traces

Le jeu de données contient **46 spans** répartis dans **5 traces** :

```python
import pandas as pd

spans = pd.read_csv("lab-050/multi_agent_spans.csv")
print(f"Total spans: {len(spans)}")
print(f"Traces: {spans['trace_id'].nunique()}")
print(f"\nSpans per trace:")
print(spans.groupby("trace_id")["span_id"].count())
```

**Attendu :**

| Trace | Spans | Scénario |
|-------|-------|----------|
| A001 | 8 | Recherche de produit (simple) |
| A002 | 10 | Requête de commande complexe |
| A003 | 9 | Traitement de plainte |
| A004 | 5 | FAQ (pas de réviseur) |
| A005 | 14 | Remboursement avec échec de revue + relance |

---

## Étape 3 : Analyse des spans d'agent

Extrayez et analysez les spans d'agent :

```python
agent_spans = spans[(spans["kind"] == "INTERNAL") & (spans["agent_name"].notna())]
print(f"Total agent spans: {len(agent_spans)}")
print(f"Unique agents: {sorted(agent_spans['agent_name'].unique())}")
print(f"\nSpans per agent:")
print(agent_spans["agent_name"].value_counts().sort_index())
```

**Attendu :**

```
Total agent spans: 16
Unique agents: ['FAQSpec', 'OrderSpec', 'ProductSpec', 'RefundSpec', 'Reviewer', 'Router', 'SupportSpec']

Reviewer     5
Router       5
RefundSpec   2
...
```

!!! tip "Observation"
    **Router apparaît dans les 5 traces** — c'est le point d'entrée. **Reviewer apparaît dans 4 traces** (pas A004, la FAQ simple). **RefundSpec apparaît deux fois** dans la trace A005 car la première tentative a échoué à la revue et a été relancée.

---

## Étape 4 : Analyse de l'utilisation des tokens LLM

Analysez la consommation de tokens dans tous les appels de modèle :

```python
llm_spans = spans[spans["model"].notna()]
print(f"Total LLM calls: {len(llm_spans)}")

by_model = llm_spans.groupby("model").agg(
    calls=("span_id", "count"),
    total_input=("input_tokens", "sum"),
    total_output=("output_tokens", "sum"),
).reset_index()
by_model["total_tokens"] = by_model["total_input"] + by_model["total_output"]
print(by_model.to_string(index=False))

total_tokens = int(llm_spans["input_tokens"].sum() + llm_spans["output_tokens"].sum())
print(f"\nGrand total: {total_tokens:,} tokens")
```

**Attendu :**

| Modèle | Appels | Entrée | Sortie | Total |
|-------|-------|-------|--------|-------|
| gpt-4o | 12 | 3 830 | 1 890 | 5 720 |
| gpt-4o-mini | 10 | 1 045 | 177 | 1 222 |
| **Total** | **22** | **4 875** | **2 067** | **6 942** |

!!! tip "Observation sur les coûts"
    gpt-4o gère le raisonnement complexe (82 % des tokens) tandis que gpt-4o-mini effectue la classification légère et les vérifications de qualité (18 %). C'est un pattern économique — n'utilisez les modèles coûteux que pour le raisonnement complexe.

---

## Étape 5 : Analyse des appels d'outils

```python
tool_spans = spans[spans["tool_name"].notna()]
print(f"Total tool calls: {len(tool_spans)}")
print(f"\nTools used:")
print(tool_spans["tool_name"].value_counts())

trace_tools = tool_spans.groupby("trace_id").size()
print(f"\nTrace with most tool calls: {trace_tools.idxmax()} ({trace_tools.max()} calls)")
```

**Attendu :**

```
Total tool calls: 8

search_products         1
get_order_status        1
get_shipping_info       1
calculate_eta           1
get_customer_history    1
search_faq              1
get_order_details       1
check_refund_policy     1

Trace with most tool calls: A002 (3 calls)
```

---

## Étape 6 : Analyse des scores de qualité

Les agents réviseurs attribuent des scores de qualité. Analysez-les :

```python
quality_spans = spans[spans["quality_score"].notna()]
print(f"Quality assessments: {len(quality_spans)}")
print(f"Average quality:     {quality_spans['quality_score'].mean():.3f}")
print(f"Min quality:         {quality_spans['quality_score'].min():.2f}")
print(f"Max quality:         {quality_spans['quality_score'].max():.2f}")

# Traces that fell below the quality threshold
below_threshold = quality_spans[quality_spans["quality_score"] < 0.8]
print(f"\nTraces below 0.8 threshold: {below_threshold['trace_id'].unique().tolist()}")
```

**Attendu :**

```
Quality assessments: 5
Average quality:     0.790
Min quality:         0.45
Max quality:         0.95

Traces below 0.8 threshold: ['A003', 'A005']
```

### Investigation de la revue échouée (Trace A005)

```python
a005 = spans[spans["trace_id"] == "A005"].sort_values("span_id")
print(a005[["span_id", "span_name", "agent_name", "kind", "quality_score", "status"]]
      .to_string(index=False))
```

Cela montre le **pattern de relance** : la première vérification du réviseur (s40) a obtenu un score de 0,45 avec le statut ERROR. Le Refund Specialist a été ré-invoqué (s42), a produit une réponse révisée, et la deuxième vérification du réviseur (s45) est passée à 0,85.

---

## Étape 7 : Construire les métriques du tableau de bord

Combinez tout en un résumé de tableau de bord :

```python
# Overall metrics
total_traces = spans["trace_id"].nunique()
total_spans = len(spans)
total_agent_spans = len(agent_spans)
total_llm_calls = len(llm_spans)
total_tools = len(tool_spans)
error_spans = spans[spans["status"] == "ERROR"]
avg_quality = quality_spans["quality_score"].mean()

dashboard = f"""
╔══════════════════════════════════════════════════╗
║         Multi-Agent Observability Dashboard      ║
╠══════════════════════════════════════════════════╣
║ Traces:           {total_traces:>5}                          ║
║ Total Spans:      {total_spans:>5}                          ║
║ Agent Spans:      {total_agent_spans:>5}  (INTERNAL)                ║
║ LLM Calls:        {total_llm_calls:>5}  (CLIENT)                  ║
║ Tool Calls:       {total_tools:>5}  (CLIENT)                  ║
║ Error Spans:      {len(error_spans):>5}                          ║
║ Total Tokens:     {total_tokens:>5,}                        ║
║ Avg Quality:      {avg_quality:>5.3f}                        ║
║ Below Threshold:  {len(below_threshold):>5}  traces                  ║
╚══════════════════════════════════════════════════╝
"""
print(dashboard)
```

---

## 🐛 Exercice de correction de bugs

Le fichier `lab-050/broken_conventions.py` contient **3 bugs** dans la façon dont il interprète les conventions sémantiques GenAI :

```bash
python lab-050/broken_conventions.py
```

| Test | Ce qu'il vérifie | Indice |
|------|---------------|------|
| Test 1 | Les noms d'agents proviennent de `agent_name`, pas de `span_name` | Quelle colonne contient l'identité de l'agent ? |
| Test 2 | Les spans d'agent doivent être de kind `INTERNAL` ET avoir un `agent_name` | Ne comptez pas les spans LLM/outils |
| Test 3 | Total de tokens = entrée + sortie | N'oubliez pas les output_tokens |

---


## 🧠 Quiz de connaissances

??? question "**Q1 (Choix multiple) :** Dans les conventions sémantiques GenAI, quel span kind doit être utilisé pour la logique interne de routage/planification d'un agent ?"

    - A) CLIENT — parce que l'agent est un client du LLM
    - B) SERVER — parce que l'agent sert les requêtes utilisateur
    - C) INTERNAL — parce que le routage se fait localement, pas via le réseau
    - D) PRODUCER — parce que l'agent produit des réponses

    ??? success "✅ Révéler la réponse"
        **Correct : C) INTERNAL**

        La prise de décision de l'agent (routage, planification, récupération en mémoire) se fait au sein du processus — elle ne franchit pas de frontière réseau. `CLIENT` est utilisé pour les appels sortants vers les LLM et les outils. La convention est : logique de l'agent = `INTERNAL`, appels externes = `CLIENT`.

??? question "**Q2 (Choix multiple) :** Pourquoi la trace A005 a-t-elle 14 spans alors que A001 n'en a que 8 ?"

    - A) A005 utilise un modèle plus grand
    - B) A005 a eu un échec de revue de qualité et a nécessité une boucle de relance
    - C) A005 a plus de tokens d'entrée utilisateur
    - D) A005 utilise un algorithme de routage différent

    ??? success "✅ Révéler la réponse"
        **Correct : B) A005 a eu un échec de revue de qualité et a nécessité une boucle de relance**

        Le Reviewer a attribué à la première réponse d'A005 un score de 0,45 (ERROR). Le système a ré-invoqué le Refund Specialist pour réviser la réponse, puis le Reviewer a vérifié à nouveau (score : 0,85, OK). Cette relance a ajouté des spans supplémentaires : deuxième spécialiste (2 appels LLM) + deuxième réviseur (1 appel LLM) = 5 spans supplémentaires.

??? question "**Q3 (Exécutez le lab) :** Combien y a-t-il de spans d'agent au total (kind=INTERNAL avec un agent_name) dans les 5 traces ?"

    Filtrez le DataFrame des spans pour `kind == "INTERNAL"` et `agent_name` non nul.

    ??? success "✅ Révéler la réponse"
        **16 spans d'agent**

        Sur les 5 traces : A001(3) + A002(3) + A003(3) + A004(2) + A005(5) = **16**. A004 en a moins car il saute le Reviewer. A005 en a plus à cause de la relance (RefundSpec×2 + Reviewer×2).

??? question "**Q4 (Exécutez le lab) :** Quelle trace a le plus d'appels d'outils, et combien ?"

    Regroupez les spans d'outils par `trace_id` et trouvez le maximum.

    ??? success "✅ Révéler la réponse"
        **Trace A002 — 3 appels d'outils**

        A002 (requête de commande complexe) a appelé : `get_order_status`, `get_shipping_info` et `calculate_eta`. C'est la trace la plus intensive en outils. A005 a 2 appels d'outils, et les autres en ont 1 chacune.

??? question "**Q5 (Exécutez le lab) :** Quel est le score de qualité moyen sur toutes les évaluations du réviseur ?"

    Filtrez les spans avec un `quality_score` non nul et calculez la moyenne.

    ??? success "✅ Révéler la réponse"
        **0,790**

        Scores de qualité des spans du réviseur : A001 (0,95), A002 (0,92), A003 (0,78), A005-premier (0,45), A005-relance (0,85). A004 (FAQ) n'a pas de réviseur. Les données contiennent 5 entrées quality_score. Moyenne = (0,95 + 0,92 + 0,78 + 0,45 + 0,85) / 5 = **0,790**. Deux traces (A003 et A005) sont passées sous le seuil de qualité de 0,8.

---

## Résumé

| Sujet | Ce que vous avez appris |
|-------|-----------------|
| Conventions GenAI | Attributs standards : agent.name, request.model, usage.tokens |
| Span Kinds | INTERNAL (logique de l'agent) vs CLIENT (appels LLM/outils) |
| Hiérarchie des traces | Spans parent-enfant montrant les transferts entre agents |
| Patterns de relance | Les échecs de revue déclenchent des boucles de relance (visibles dans les traces) |
| Métriques de tableau de bord | Nombre d'agents, utilisation des tokens, appels d'outils, scores de qualité |
| Inter-frameworks | Les mêmes conventions fonctionnent entre Foundry, SK, LangChain, AutoGen |

---

## Prochaines étapes

- **[Lab 033](lab-033-agent-observability.md)** — Observabilité des agents avec Application Insights (approche complémentaire Azure-native)
- **[Lab 034](lab-034-multi-agent-sk.md)** — Orchestration multi-agents avec Semantic Kernel (construire les agents que ce lab trace)
- **[Lab 035](lab-035-agent-evaluation.md)** — Évaluation des agents avec le SDK Azure AI Eval (le scoring de qualité qui alimente le Reviewer)
