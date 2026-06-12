---
tags: [challenge, rag, retrieval, evaluation, python, local]
---
# Défi 002 : Corriger un pipeline RAG cassé

<div class="lab-meta">
  <span><strong>Niveau :</strong> <span class="level-badge level-200">L200</span></span>
  <span><strong>Type :</strong> Défi</span>
  <span><strong>Durée :</strong> ~75 min</span>
  <span><strong>💰 Coût :</strong> <span class="level-badge cost-free">Gratuit (local)</span></span>
</div>

## Scénario

OutdoorGear possède un prototype RAG local pour les questions de support. Il devrait récupérer la bonne politique ou le bon guide produit, puis répondre uniquement à partir du contexte récupéré. Le prototype actuel est cassé : la récupération classe de mauvais chunks en premier, les réponses ignorent les preuves et l'évaluation rapporte des métriques trompeuses.

Votre tâche consiste à corriger le pipeline sans utiliser de LLM, de base vectorielle ou de framework RAG.

---

## Objectif

Implémentez la logique manquante ou cassée dans `starter_rag_pipeline.py` afin que le pipeline RAG récupère les bons documents sources, produise des réponses ancrées, rapporte des métriques d'évaluation correctes et génère un code de validation.

Votre pipeline final doit :

- Normaliser le texte des requêtes et documents pour la récupération
- Découper les documents en préservant les métadonnées de source
- Classer les chunks par pertinence
- Produire des réponses concises à partir des preuves récupérées
- Évaluer l'exactitude top-1 de récupération et la couverture des termes requis dans les réponses

---

## Fichiers de départ

Enregistrez ces fichiers dans un dossier nommé `challenge-002/` :

| Fichier | Objectif | Télécharger |
|---------|----------|-------------|
| `documents.json` | Base de connaissances mock OutdoorGear | [Télécharger](https://github.com/lcarli/AI-LearningHub/raw/main/docs/docs/en/challenges/challenge-002/documents.json) |
| `queries.json` | Requêtes d'évaluation et preuves attendues | [Télécharger](https://github.com/lcarli/AI-LearningHub/raw/main/docs/docs/en/challenges/challenge-002/queries.json) |
| `starter_rag_pipeline.py` | Pipeline RAG cassé | [Télécharger](https://github.com/lcarli/AI-LearningHub/raw/main/docs/docs/en/challenges/challenge-002/starter_rag_pipeline.py) |
| `test_rag_pipeline.py` | Tests d'acceptation | [Télécharger](https://github.com/lcarli/AI-LearningHub/raw/main/docs/docs/en/challenges/challenge-002/test_rag_pipeline.py) |
| `validate_rag_pipeline.py` | Génère le code final de réussite | [Télécharger](https://github.com/lcarli/AI-LearningHub/raw/main/docs/docs/en/challenges/challenge-002/validate_rag_pipeline.py) |

---

## Brief du défi

Vous recevez une petite base de connaissances, un ensemble de requêtes d'évaluation et un pipeline RAG local cassé. Il n'y a pas de walkthrough : décidez comment découper, scorer, récupérer, répondre et évaluer pour que le système se comporte comme un assistant de support fiable et ancré.

---

## Contraintes

- Utilisez uniquement la bibliothèque standard Python dans `starter_rag_pipeline.py`.
- N'appelez pas d'API LLM.
- N'utilisez pas d'embeddings ni de base vectorielle.
- Ne hardcodez pas de réponses pour des IDs de requête spécifiques.
- Utilisez les preuves récupérées dans `answer_question()`.
- Préservez les noms publics des fonctions utilisés par les tests.

---

## Critères d'acceptation

Votre solution est complète lorsque :

- `python -m pytest test_rag_pipeline.py` passe
- Les métadonnées des chunks préservent `chunk_id`, `doc_id`, `title` et `text`
- Le document en tête pour chaque requête fixture est correct
- Les réponses incluent les termes de preuve requis
- L'évaluation rapporte `top1_accuracy == 1.0`
- L'évaluation rapporte `required_coverage == 1.0`

---

## Validation

Lorsque votre implémentation est prête, exécutez :

```bash
python -m pytest test_rag_pipeline.py
python validate_rag_pipeline.py
```

Saisissez le code de réussite imprimé par `validate_rag_pipeline.py` :

<div class="challenge-validator" data-answer="CH002-3E640D5D">
  <input type="text" aria-label="Code de réussite" placeholder="CH002-XXXXXXXX" />
  <button type="button">Valider</button>
  <p class="challenge-validator-result" aria-live="polite"></p>
</div>

---

## Indices

??? tip "Indice 1 — La qualité de récupération commence par la normalisation"
    La ponctuation, la casse et les stop words peuvent dominer un petit récupérateur lexical si vous ne normalisez pas le texte.

??? tip "Indice 2 — Le chunking fait partie de la récupération"
    Un chunk doit être assez petit pour être scoré précisément, mais conserver assez de métadonnées de source pour expliquer d'où vient la réponse.

??? tip "Indice 3 — Répondez à partir des preuves, pas de la requête"
    Si un terme requis n'apparaît pas dans le contexte récupéré, la réponse ne doit pas l'inventer.

??? tip "Indice 4 — Les métriques ont besoin du bon dénominateur"
    L'exactitude top-1 et la couverture sont des métriques par requête. Vérifiez par quoi vous divisez.

---

## Rubrique

| Domaine | Points | Ce qui est attendu |
|---------|:------:|--------------------|
| Récupération | 35 | Bon document en tête pour chaque requête |
| Chunking | 20 | Métadonnées préservées et tailles de chunks contrôlées |
| Réponses ancrées | 20 | Les réponses incluent des preuves issues des chunks récupérés |
| Évaluation | 15 | Les métriques reflètent la performance par requête |
| Simplicité | 10 | Pas de framework ni de réponses hardcodées par requête |

---

## Objectifs bonus

- Ajouter une reciprocal rank fusion sur les scores du titre et du corps
- Retourner des citations avec les IDs de chunks dans la réponse
- Ajouter une réponse "preuves insuffisantes" lorsque la confiance de récupération est faible
- Ajouter une nouvelle requête dans `queries.json` et mettre à jour localement le payload du validateur

---

## Labs associés

- [Lab 006 — Qu'est-ce que RAG ?](../labs/lab-006-what-is-rag.md)
- [Lab 007 — Que sont les embeddings ?](../labs/lab-007-what-are-embeddings.md)
- [Lab 022 — RAG avec GitHub Models + pgvector](../labs/lab-022-rag-github-models-pgvector.md)
