---
tags: [evaluation, python, free, github-models]
---
# Lab 035 : Évaluation des agents avec le SDK Azure AI Eval

<div class="lab-meta">
  <span><strong>Niveau :</strong> <span class="level-badge level-300">L300</span></span>
  <span><strong>Parcours :</strong> <a href="../paths/pro-code/">Pro Code</a></span>
  <span><strong>Durée :</strong> ~60 min</span>
  <span><strong>💰 Coût :</strong> <span class="level-badge cost-github">GitHub Gratuit</span> — utilise GitHub Models pour l'évaluation</span>
</div>

## Ce que vous apprendrez

- Pourquoi l'évaluation **LLM-as-judge** fonctionne et quand l'utiliser
- Mesurer l'**ancrage**, la **pertinence**, la **cohérence** et la **fluidité**
- Construire un **jeu de données de référence** pour les tests de régression
- Évaluer automatiquement votre agent RAG avec le SDK `azure-ai-evaluation`
- Suivre les métriques de qualité dans le temps et détecter les régressions

---

## Introduction

Comment savoir si votre agent s'est amélioré ou dégradé après une modification ? Les tests manuels ne passent pas à l'échelle.

L'**évaluation LLM-as-judge** utilise un second LLM indépendant pour noter les réponses de votre agent selon des critères tels que :

- **Ancrage (Groundedness)** — La réponse est-elle soutenue par les documents récupérés ?
- **Pertinence (Relevance)** — La réponse traite-t-elle ce que l'utilisateur a demandé ?
- **Cohérence (Coherence)** — La réponse est-elle logiquement structurée ?
- **Fluidité (Fluency)** — La grammaire est-elle correcte ?

Ce lab construit un pipeline d'évaluation automatisé pour l'assistant OutdoorGear.

---

## Prérequis

- Python 3.11+
- `pip install azure-ai-evaluation openai`
- `GITHUB_TOKEN` configuré

---

## 📦 Fichiers de support

!!! note "Téléchargez ces fichiers avant de commencer le lab"
    Enregistrez tous les fichiers dans un dossier `lab-035/` de votre répertoire de travail.

| Fichier | Description | Téléchargement |
|------|-------------|----------|
| `eval_dataset.jsonl` | Jeu de données d'évaluation | [📥 Télécharger](https://github.com/lcarli/AI-LearningHub/raw/main/docs/docs/en/labs/lab-035/eval_dataset.jsonl) |

---

## Exercice du lab

### Étape 1 : Installer le SDK d'évaluation

```bash
pip install azure-ai-evaluation openai
```

### Étape 2 : Créer un jeu de données de référence

Un **jeu de données de référence** est un ensemble de questions de test avec des réponses de qualité connue. Créez [📥 `eval_dataset.jsonl`](https://github.com/lcarli/AI-LearningHub/raw/main/docs/docs/en/labs/lab-035/eval_dataset.jsonl) :

```jsonl
{"query": "What is the return policy?", "response": "We offer a 60-day return window. Items must be unused in original packaging.", "context": "60-day return window. Items must be unused in original packaging. Worn footwear non-refundable unless defective."}
{"query": "Do you sell waterproof jackets?", "response": "Yes, we have the StormShell Jacket at $349 — a 3-layer Gore-Tex Pro shell.", "context": "StormShell Jacket ($349): 3-layer Gore-Tex Pro shell. 20k/20k waterproof rating."}
{"query": "How long does standard shipping take?", "response": "Standard shipping takes 3-5 business days and costs $5.99.", "context": "Standard $5.99 (3-5 days). Express $14.99 (1-2 days). Free on orders $75+."}
{"query": "What is the capital of France?", "response": "Paris is the capital of France.", "context": "OutdoorGear Inc. sells outdoor equipment including tents, boots, and apparel."}
{"query": "Tell me about the TrailBlazer X200", "response": "The TrailBlazer X200 is a waterproof hiking boot with Vibram outsole, priced at $189.99.", "context": "TrailBlazer X200 ($189.99): Waterproof Gore-Tex hiking boot. Vibram outsole. 3-season rated."}
```

Notez la 4ᵉ entrée — l'agent répond à une question sans rapport avec la base de connaissances. L'évaluation de l'ancrage devrait signaler cela.

### Étape 3 : Exécuter les évaluateurs intégrés

```python
# evaluate_agent.py
import os, json
from pathlib import Path
from azure.ai.evaluation import (
    GroundednessEvaluator,
    RelevanceEvaluator,
    CoherenceEvaluator,
    FluencyEvaluator,
)

# Use GitHub Models as the judge LLM
model_config = {
    "azure_endpoint": "https://models.inference.ai.azure.com",
    "api_key": os.environ["GITHUB_TOKEN"],
    "azure_deployment": "gpt-4o",
    "api_version": "2024-02-01",
}

# Initialize evaluators
groundedness = GroundednessEvaluator(model_config=model_config)
relevance    = RelevanceEvaluator(model_config=model_config)
coherence    = CoherenceEvaluator(model_config=model_config)
fluency      = FluencyEvaluator(model_config=model_config)

# Load dataset
dataset = [
    json.loads(line)
    for line in Path("eval_dataset.jsonl").read_text().splitlines()
    if line.strip()
]

results = []
for i, item in enumerate(dataset, 1):
    query    = item["query"]
    response = item["response"]
    context  = item["context"]

    print(f"Evaluating {i}/{len(dataset)}: {query[:50]}...")

    scores = {
        "query":        query,
        "response":     response[:80] + "...",
        "groundedness": groundedness(query=query, response=response, context=context)["groundedness"],
        "relevance":    relevance(query=query,    response=response, context=context)["relevance"],
        "coherence":    coherence(query=query,    response=response)["coherence"],
        "fluency":      fluency(response=response)["fluency"],
    }
    results.append(scores)

# Print report
print("\n" + "="*80)
print(f"{'Query':<45} {'Ground':>7} {'Relev':>6} {'Coher':>6} {'Fluency':>8}")
print("-"*80)
for r in results:
    print(
        f"{r['query'][:44]:<45} "
        f"{r['groundedness']:>7.1f} "
        f"{r['relevance']:>6.1f} "
        f"{r['coherence']:>6.1f} "
        f"{r['fluency']:>8.1f}"
    )

# Summary
print("="*80)
for metric in ["groundedness", "relevance", "coherence", "fluency"]:
    avg = sum(r[metric] for r in results) / len(results)
    status = "✅" if avg >= 3.5 else "⚠️" if avg >= 2.5 else "❌"
    print(f"{status} Avg {metric:15}: {avg:.2f}/5.0")
```

```bash
python evaluate_agent.py
```

Sortie attendue :
```
============================================================
Query                                         Ground  Relev  Coher  Fluency
------------------------------------------------------------
What is the return policy?                       4.0    5.0    5.0      5.0
Do you sell waterproof jackets?                  5.0    5.0    4.0      5.0
How long does standard shipping take?            5.0    5.0    5.0      5.0
What is the capital of France?                   1.0    1.0    4.0      5.0  ← signalé !
Tell me about the TrailBlazer X200               5.0    5.0    5.0      5.0
============================================================
✅ Avg groundedness    : 4.00/5.0
✅ Avg relevance       : 4.20/5.0
✅ Avg coherence       : 4.60/5.0
✅ Avg fluency         : 5.00/5.0
```

La question sur Paris est correctement signalée avec un faible ancrage (1.0) — la réponse n'est pas soutenue par le contexte OutdoorGear.

### Étape 4 : Construire un évaluateur personnalisé

Parfois vous avez besoin de critères spécifiques au domaine. Voici un évaluateur personnalisé pour la **précision des prix** :

```python
# custom_evaluator.py
from azure.ai.evaluation import PromptTemplateEvaluator

PRICE_ACCURACY_TEMPLATE = """
You are evaluating whether an AI assistant correctly stated product prices.

Query: {{query}}
Response: {{response}}
Ground truth context: {{context}}

Score the price accuracy from 1-5:
- 5: All prices mentioned are exactly correct
- 4: Prices are approximately correct (within 10%)
- 3: Some prices correct, some missing
- 2: Prices are wrong or made up
- 1: No prices when prices were relevant, or completely wrong prices

Return a JSON object: {"price_accuracy": <score>, "reason": "<brief explanation>"}
"""

price_evaluator = PromptTemplateEvaluator(
    prompt_template=PRICE_ACCURACY_TEMPLATE,
    model_config=model_config,
    result_key="price_accuracy",
)

# Test it
result = price_evaluator(
    query="How much is the TrailBlazer X200?",
    response="The TrailBlazer X200 costs $189.99.",
    context="TrailBlazer X200 ($189.99): Waterproof Gore-Tex hiking boot."
)
print(f"Price accuracy score: {result['price_accuracy']}")
```

### Étape 5 : Automatiser en CI/CD

Ajoutez ceci à votre workflow GitHub Actions (voir [Lab 037](lab-037-cicd-github-actions.md)) :

```yaml
- name: Evaluate agent quality
  run: |
    pip install azure-ai-evaluation openai
    python evaluate_agent.py | tee eval_report.txt
    # Fail if avg groundedness < 3.5
    python -c "
    import json, sys
    results = [json.loads(l) for l in open('eval_results.jsonl')]
    avg_g = sum(r['groundedness'] for r in results) / len(results)
    print(f'Avg groundedness: {avg_g:.2f}')
    sys.exit(0 if avg_g >= 3.5 else 1)
    "
  env:
    GITHUB_TOKEN: ${{ secrets.GITHUB_TOKEN }}
```

---

## Référence des métriques d'évaluation

| Métrique | Ce qu'elle mesure | Bon score |
|--------|-----------------|------------|
| Ancrage (Groundedness) | Réponse soutenue par le contexte | ≥ 4.0 |
| Pertinence (Relevance) | Répond à la question de l'utilisateur | ≥ 4.0 |
| Cohérence (Coherence) | Logique, bien structurée | ≥ 4.0 |
| Fluidité (Fluency) | Grammaticalement correcte | ≥ 4.5 |

Les scores vont de 1 à 5. En dessous de 3.0 en ancrage, cela indique généralement une hallucination.

---


## 🧠 Vérification des connaissances

??? question "**Q1 (Exécutez le lab) :** Chargez `lab-035/eval_dataset.jsonl` en Python. Combien d'exemples contient le jeu de données, et combien sont dans la catégorie `out_of_scope` ?"

    Exécutez le code de chargement de la section Fichiers de support ci-dessus.

    ??? success "✅ Révéler la réponse"
        **20 exemples au total. 1 exemple est dans la catégorie `out_of_scope`.**

        Le jeu de données contient exactement 20 lignes. Exécutez `sum(1 for d in dataset if d["category"] == "out_of_scope")` pour confirmer qu'il y a 1 exemple hors périmètre. Cet exemple teste si votre agent refuse correctement de répondre aux questions sans rapport avec l'équipement de plein air.

??? question "**Q2 (Exécutez le lab) :** Pour l'unique exemple `out_of_scope` dans `eval_dataset.jsonl`, quelle est la valeur du champ `product_ids` ?"

    Chargez le jeu de données et filtrez par `category == "out_of_scope"`. Affichez le champ `product_ids`.

    ??? success "✅ Révéler la réponse"
        **`[]` (liste vide)**

        L'exemple hors périmètre a `"product_ids": []` car la question ne porte sur aucun produit spécifique — il teste si l'agent refuse de répondre aux questions non pertinentes (comme demander des recettes de cuisine). Un agent bien conçu devrait retourner un message de refus plutôt que d'halluciner une réponse. Votre métrique d'évaluation devrait vérifier que le score d'`ancrage` de l'agent est élevé et qu'il ne référence AUCUN identifiant de produit.

??? question "**Q3 (Choix multiple) :** Combien d'exemples dans `eval_dataset.jsonl` sont dans la catégorie `tents` ?"

    - A) 3
    - B) 5
    - C) 7
    - D) 4

    ??? success "✅ Révéler la réponse"
        **Correct : B — 5 exemples**

        La catégorie `tents` contient 5 exemples, ce qui en fait la plus grande catégorie individuelle. Exécutez `sum(1 for d in dataset if d["category"] == "tents")` pour confirmer. La répartition complète : tents(5), backpacks(4), sleeping_bags(3), pricing(3), recommendations(3), out_of_scope(1), comparisons(1).

---

## Prochaines étapes

- **CI/CD pour les agents :** → [Lab 037 — GitHub Actions pour les agents IA](lab-037-cicd-github-actions.md)
- **Évaluation RAG d'entreprise :** → [Lab 042 — RAG d'entreprise avec évaluations](lab-042-enterprise-rag.md)