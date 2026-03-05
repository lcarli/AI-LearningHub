---
tags: [observability, opentelemetry, azure-monitor, foundry, python, tracing]
---
# Lab 049 : Foundry IQ — Traçage des agents avec OpenTelemetry

<div class="lab-meta">
  <span><strong>Niveau :</strong> <span class="level-badge level-300">L300</span></span>
  <span><strong>Parcours :</strong> <a href="../paths/foundry/">🏭 Microsoft Foundry</a></span>
  <span><strong>Durée :</strong> ~75 min</span>
  <span><strong>💰 Coût :</strong> <span class="level-badge cost-free">Gratuit</span> — Mode local avec ConsoleSpanExporter (Azure Monitor optionnel)</span>
</div>

## Ce que vous apprendrez

- Comment **OpenTelemetry** fournit l'observabilité pour les agents IA (traces, spans, attributs)
- Instrumenter le code d'un agent avec les **conventions sémantiques GenAI** pour les appels de modèle et l'utilisation d'outils
- Capturer l'**utilisation de tokens, la latence et les taux d'erreur** sous forme de télémétrie structurée
- Analyser les traces d'un agent pour identifier les problèmes de performance et les facteurs de coût
- (Optionnel) Exporter les traces vers **Azure Monitor / Application Insights** et le **portail Foundry**
- Configurer les **contrôles de confidentialité** pour l'enregistrement du contenu

## Introduction

![Architecture de traçage Foundry IQ](../../assets/diagrams/foundry-iq-tracing.svg)

Les agents en production échouent silencieusement. La qualité d'une réponse se dégrade — mais personne ne le remarque jusqu'à ce qu'un client se plaigne. Les coûts explosent parce qu'un prompt est devenu trop long — mais la facture arrive 30 jours plus tard. Un appel d'outil commence à expirer — mais l'agent renvoie une réponse de secours au lieu d'une erreur.

**Foundry IQ** est la couche d'observabilité qui rend le comportement des agents visible. Il utilise **OpenTelemetry** — le framework d'observabilité standard de l'industrie — avec les **conventions sémantiques GenAI** qui définissent exactement comment capturer la télémétrie spécifique à l'IA comme le nombre de tokens, les noms de modèles et les appels d'outils.

### Le scénario

L'agent de service client d'OutdoorGear Inc. traite plus de 1 000 requêtes par jour. L'équipe a besoin de :

1. **Suivi de la latence** — quelles requêtes prennent le plus de temps et pourquoi ?
2. **Visibilité des coûts** — combien de tokens sont consommés et à quel coût ?
3. **Détection des erreurs** — quelles traces échouent, et quelle est la cause racine ?
4. **Surveillance de la qualité** — les réponses se dégradent-elles au fil du temps ?

Vous disposez de **10 traces d'exemple** de l'agent à analyser, plus un script de démarrage pour ajouter le traçage à du nouveau code.

---

## Prérequis

| Prérequis | Pourquoi |
|---|---|
| Python 3.10+ | Exécuter l'analyse et l'instrumentation |
| `pandas` | Analyser les données de traces d'exemple |
| `opentelemetry-api`, `opentelemetry-sdk` | Traçage local (ConsoleSpanExporter) |
| (Optionnel) Projet Azure AI Foundry | Export de traces en direct vers le portail Foundry |

```bash
pip install pandas opentelemetry-api opentelemetry-sdk
```

Pour le mode Azure (optionnel) :
```bash
pip install azure-ai-projects azure-monitor-opentelemetry opentelemetry-instrumentation-openai-v2
```

---

!!! tip "Démarrage rapide avec GitHub Codespaces"
    [![Ouvrir dans GitHub Codespaces](https://github.com/codespaces/badge.svg)](https://codespaces.new/lcarli/AI-LearningHub?quickstart=1)

    Toutes les dépendances sont préinstallées dans le devcontainer.


## 📦 Fichiers d'accompagnement

!!! note "Téléchargez ces fichiers avant de commencer le lab"
    Enregistrez tous les fichiers dans un dossier `lab-049/` dans votre répertoire de travail.

| Fichier | Description | Télécharger |
|------|-------------|----------|
| `broken_tracing.py` | Exercice de correction de bugs (3 bugs + auto-tests) | [📥 Télécharger](https://github.com/lcarli/AI-LearningHub/raw/main/docs/docs/en/labs/lab-049/broken_tracing.py) |
| `sample_traces.csv` | Jeu de données | [📥 Télécharger](https://github.com/lcarli/AI-LearningHub/raw/main/docs/docs/en/labs/lab-049/sample_traces.csv) |
| `traced_agent.py` | Script de démarrage avec TODOs | [📥 Télécharger](https://github.com/lcarli/AI-LearningHub/raw/main/docs/docs/en/labs/lab-049/traced_agent.py) |

---

## Étape 1 : Comprendre OpenTelemetry pour l'IA

OpenTelemetry définit trois types de signaux. Pour le traçage des agents, nous nous concentrons sur les **traces** :

| Signal | Ce qu'il capture | Exemple pour un agent |
|--------|-----------------|---------------|
| **Traces** | Flux de requête de bout en bout sous forme d'arbre de spans | Boucle d'agent → Appel LLM → Appel d'outil → Réponse |
| **Métriques** | Mesures agrégées dans le temps | Consommation de tokens, nombre de requêtes, histogrammes de latence |
| **Logs** | Événements discrets | « Agent selected tool: search_products » |

### Spans et attributs

Un **span** représente une opération unique au sein d'une trace. Chaque span possède :

- **Nom** : par ex., `chat gpt-4o`
- **Kind** : `CLIENT` (appel sortant vers LLM/outil) ou `INTERNAL` (logique de l'agent)
- **Durée** : de l'heure de début à l'heure de fin
- **Attributs** : métadonnées clé-valeur suivant les conventions GenAI
- **Statut** : `OK` ou `ERROR`
- **Parent** : relie les spans en arbre

### Conventions sémantiques GenAI

La communauté OpenTelemetry définit des noms d'attributs standards pour les opérations IA :

| Attribut | Description | Exemple |
|-----------|-------------|---------|
| `gen_ai.operation.name` | Type d'opération | `chat` |
| `gen_ai.request.model` | Modèle demandé | `gpt-4o` |
| `gen_ai.usage.input_tokens` | Tokens de prompt consommés | `150` |
| `gen_ai.usage.output_tokens` | Tokens de complétion | `85` |
| `gen_ai.response.finish_reason` | Pourquoi le modèle s'est arrêté | `stop`, `tool_calls` |
| `gen_ai.system` | Fournisseur | `openai` |

!!! tip "Pourquoi les standards sont importants"
    Utiliser les conventions sémantiques GenAI signifie que vos traces sont lisibles par **n'importe quel** backend compatible OpenTelemetry — Jaeger, Zipkin, Datadog, Azure Monitor, Grafana Tempo — sans parsing personnalisé.

---

## Étape 2 : Analyser les traces d'exemple

Avant d'instrumenter du code, analysons des données de traces réelles. Chargez les 10 traces d'exemple :

```python
import pandas as pd

traces = pd.read_csv("lab-049/sample_traces.csv")
print(f"Loaded {len(traces)} traces")
print(traces[["trace_id", "query_type", "model", "duration_ms", "status"]].to_string(index=False))
```

### 2a — Analyse de latence

```python
avg_latency = traces["duration_ms"].mean()
p95 = traces["duration_ms"].quantile(0.95)
slowest = traces.loc[traces["duration_ms"].idxmax()]

print(f"Average latency:  {avg_latency:.1f} ms  ({avg_latency/1000:.2f}s)")
print(f"P95 latency:      {p95:.0f} ms")
print(f"Slowest trace:    {slowest['trace_id']} at {slowest['duration_ms']} ms ({slowest['status']})")
```

**Attendu :**
```
Average latency:  3150.0 ms  (3.15s)
P95 latency:      7650 ms
Slowest trace:    t006 at 8500 ms (ERROR)
```

### 2b — Utilisation des tokens

```python
total_input = traces["input_tokens"].sum()
total_output = traces["output_tokens"].sum()
total_tokens = total_input + total_output

print(f"Total input tokens:  {total_input:,}")
print(f"Total output tokens: {total_output:,}")
print(f"Total tokens:        {total_tokens:,}")

# Cost estimate (gpt-4o pricing: $5/1M input, $15/1M output)
input_cost = total_input / 1_000_000 * 5
output_cost = total_output / 1_000_000 * 15
print(f"Estimated cost:      ${input_cost + output_cost:.4f}")
```

### 2c — Analyse des erreurs

```python
errors = traces[traces["status"] == "ERROR"]
error_rate = len(errors) / len(traces) * 100
print(f"Error rate: {error_rate:.1f}% ({len(errors)} of {len(traces)} traces)")
if len(errors) > 0:
    print(f"Error types: {errors['error_type'].value_counts().to_dict()}")
```

### 2d — Ventilation par type de requête

```python
by_type = traces.groupby("query_type").agg(
    count=("trace_id", "count"),
    avg_ms=("duration_ms", "mean"),
    avg_tokens=("input_tokens", "mean"),
).reset_index()
print(by_type.to_string(index=False))
```

---

## Étape 3 : Instrumenter un agent (mode local)

Ouvrez `lab-049/traced_agent.py` et complétez les **5 TODOs** :

| TODO | Ce qu'il faut implémenter |
|------|------------------|
| TODO 1 | Configurer `TracerProvider` avec `ConsoleSpanExporter` |
| TODO 2 | Encapsuler l'appel LLM dans un span avec les attributs GenAI |
| TODO 3 | Enregistrer l'utilisation des tokens comme attributs du span |
| TODO 4 | Créer un span racine pour la boucle de l'agent |
| TODO 5 | Enregistrer les erreurs avec `span.set_status(StatusCode.ERROR)` |

Exécutez le script de démarrage pour voir la sortie des traces dans votre console :

```bash
python lab-049/traced_agent.py
```

Avant de compléter les TODOs, le script affiche `❌ TODO 1 not implemented`. Après avoir complété le TODO 1, vous verrez des données de span au format JSON imprimées dans la console.

---

## Étape 4 : Exporter vers Azure Monitor (Optionnel)

Si vous avez un projet Azure AI Foundry, remplacez le ConsoleSpanExporter par Azure Monitor :

```python
from azure.ai.projects import AIProjectClient
from azure.identity import DefaultAzureCredential
from azure.monitor.opentelemetry import configure_azure_monitor
from opentelemetry.instrumentation.openai_v2 import OpenAIInstrumentor

# Get connection string from Foundry project
project = AIProjectClient(
    credential=DefaultAzureCredential(),
    endpoint="https://<your-resource>.services.ai.azure.com/api/projects/<your-project>",
)
conn_str = project.telemetry.get_application_insights_connection_string()

# Configure Azure Monitor exporter
configure_azure_monitor(connection_string=conn_str)

# Auto-instrument OpenAI SDK
OpenAIInstrumentor().instrument()
```

Naviguez ensuite vers **Portail Foundry → Traçage** pour voir vos traces dans une chronologie visuelle.

!!! warning "Enregistrement du contenu"
    Par défaut, le contenu des messages n'est **PAS** enregistré dans les spans (protection de la vie privée). Pour l'activer :

    ```bash
    # PowerShell
    $env:OTEL_INSTRUMENTATION_GENAI_CAPTURE_MESSAGE_CONTENT = "true"

    # Bash
    export OTEL_INSTRUMENTATION_GENAI_CAPTURE_MESSAGE_CONTENT=true
    ```

    ⚠️ N'activez jamais cela en production avec des données clients à moins d'avoir des politiques de traitement des données appropriées.

---

## Étape 5 : Construire des règles d'alerte

En production, vous configureriez des alertes dans Azure Monitor pour :

| Alerte | Condition | Sévérité |
|-------|-----------|----------|
| Latence élevée | Durée P95 > 10s | Avertissement |
| Pic d'erreurs | Taux d'erreur > 5 % en 5 min | Critique |
| Coût des tokens | Coût quotidien des tokens > 50 $ | Avertissement |
| Baisse de qualité | Score d'évaluation moyen < 0,7 | Critique |

Cela correspond aux règles d'alerte Azure Monitor utilisant des requêtes KQL sur les données Application Insights.

---

## 🐛 Exercice de correction de bugs

Le fichier `lab-049/broken_tracing.py` contient **3 bugs** dans la logique d'analyse des traces :

```bash
python lab-049/broken_tracing.py
```

| Test | Ce qu'il vérifie | Indice |
|------|---------------|------|
| Test 1 | La latence moyenne doit inclure TOUTES les traces | Ne pas filtrer par statut |
| Test 2 | Le coût des tokens utilise des tarifs différents pour l'entrée et la sortie | L'entrée est moins chère |
| Test 3 | Dénominateur du taux d'erreur | Diviser par le total, pas par les erreurs |

---


## 🧠 Quiz de connaissances

??? question "**Q1 (Choix multiple) :** Que contrôle la variable d'environnement `OTEL_INSTRUMENTATION_GENAI_CAPTURE_MESSAGE_CONTENT` ?"

    - A) Si les traces sont exportées vers Azure Monitor
    - B) Si le contenu des messages de requête/réponse LLM est enregistré dans les spans
    - C) Si les résultats des appels d'outils sont journalisés
    - D) Le nombre maximum de spans par trace

    ??? success "✅ Révéler la réponse"
        **Correct : B) Si le contenu des messages de requête/réponse LLM est enregistré dans les spans**

        Par défaut, le contenu des messages n'est PAS inclus dans les spans pour protéger la vie privée. Définir cette variable sur `true` capture le texte complet du prompt et de la complétion — utile pour le débogage mais dangereux en production avec de vraies données clients.

??? question "**Q2 (Choix multiple) :** Dans OpenTelemetry, quel est le `span kind` correct pour la logique interne d'un agent (routage, planification, raisonnement) ?"

    - A) CLIENT
    - B) SERVER
    - C) INTERNAL
    - D) PRODUCER

    ??? success "✅ Révéler la réponse"
        **Correct : C) INTERNAL**

        Les spans `INTERNAL` représentent des opérations qui ne franchissent pas de frontière réseau — comme le raisonnement de l'agent, les décisions de routage et les recherches en mémoire. Les spans `CLIENT` sont utilisés pour les appels sortants vers les LLM, les outils et les API externes.

??? question "**Q3 (Exécutez le lab) :** Quelle est la durée moyenne des traces sur les 10 traces d'exemple ?"

    Chargez [📥 `sample_traces.csv`](https://github.com/lcarli/AI-LearningHub/raw/main/docs/docs/en/labs/lab-049/sample_traces.csv) et calculez `traces["duration_ms"].mean()`.

    ??? success "✅ Révéler la réponse"
        **3 150,0 ms (3,15 secondes)**

        Somme de toutes les durées : 2500+1800+5200+1200+3100+8500+1500+2000+4000+1700 = 31 500 ms ÷ 10 = **3 150 ms**. Notez que la trace la plus lente (t006, 8500 ms) est une ERREUR — elle fait significativement monter la moyenne.

??? question "**Q4 (Exécutez le lab) :** Quel est le nombre total de tokens (entrée + sortie) sur toutes les traces ?"

    Sommez les colonnes `input_tokens` et `output_tokens`.

    ??? success "✅ Révéler la réponse"
        **3 255 tokens**

        Entrée : 150+120+350+100+200+500+130+160+280+110 = **2 100**. Sortie : 85+60+200+45+120+300+55+90+150+50 = **1 155**. Total : 2 100 + 1 155 = **3 255**.

??? question "**Q5 (Exécutez le lab) :** Quelle trace a la latence la plus élevée et quel est son statut ?"

    Trouvez la ligne avec le `duration_ms` maximum.

    ??? success "✅ Révéler la réponse"
        **Trace t006 — 8 500 ms — statut : ERROR (timeout)**

        La trace la plus lente est aussi la seule erreur. Elle a tenté 3 appels d'outils pour une requête de statut de commande mais a expiré. Ce pattern (lent = erreur) est courant — les timeouts sont une cause principale à la fois de la haute latence et des erreurs dans les systèmes d'agents.

---

## Résumé

| Sujet | Ce que vous avez appris |
|-------|-----------------|
| OpenTelemetry | Framework d'observabilité standard de l'industrie (traces, métriques, logs) |
| Conventions GenAI | Attributs standards pour l'IA : modèle, tokens, appels d'outils |
| Analyse de traces | Latence, coût des tokens, taux d'erreur à partir de données de traces structurées |
| Instrumentation | TracerProvider, SpanProcessor, attributs de span |
| Intégration Azure | Application Insights, tableau de bord de traçage du portail Foundry |
| Confidentialité | Contrôles d'enregistrement du contenu via des variables d'environnement |

---

## Prochaines étapes

- **[Lab 050](lab-050-multi-agent-observability.md)** — Observabilité multi-agents avec les conventions sémantiques GenAI (L400)
- **[Lab 033](lab-033-agent-observability.md)** — Observabilité des agents avec Application Insights (approche complémentaire)
- **[Lab 038](lab-038-cost-optimization.md)** — Optimisation des coûts IA (utiliser les données de traces pour réduire les coûts)
