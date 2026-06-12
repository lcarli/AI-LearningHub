---
tags: [challenge, token-budget, cost, context, python, local]
---
# Défi 004 : Optimiser un budget de tokens

<div class="lab-meta">
  <span><strong>Niveau :</strong> <span class="level-badge level-200">L200</span></span>
  <span><strong>Type :</strong> Défi</span>
  <span><strong>Durée :</strong> ~60 min</span>
  <span><strong>💰 Coût :</strong> <span class="level-badge cost-free">Gratuit (local)</span></span>
</div>

## Scénario

OutdoorGear dispose d'un assistant de support qui envoie trop de contexte au modèle. Il inclut de longs textes juridiques et du contenu marketing même lorsqu'un résumé court de politique suffirait. L'équipe veut des prompts plus courts sans perdre en qualité de réponse.

Votre tâche consiste à corriger un optimiseur local de budget de prompt qui sélectionne un contexte compact et pertinent tout en gardant chaque prompt sous une limite stricte de tokens.

---

## Objectif

Corrigez `starter_token_budget.py` afin que l'optimiseur sélectionne le bon document de contexte pour chaque requête, évite le contexte non pertinent, construise des prompts compacts, rapporte la conformité au budget et génère un code de validation.

Votre optimiseur final doit :

- Estimer les tokens de prompt de manière déterministe
- Normaliser les mots-clés pour la correspondance lexicale
- Préférer les résumés concis et pertinents aux documents longs et bruités
- Sélectionner le contexte dans un budget de tokens de contexte
- Construire des prompts sous le budget total de chaque requête
- Rapporter les documents sélectionnés et la conformité au budget

---

## Fichiers de départ

Enregistrez ces fichiers dans un dossier nommé `challenge-004/` :

| Fichier | Objectif | Télécharger |
|---------|----------|-------------|
| `context_docs.json` | Contexte de support compact et verbeux | [Télécharger](https://github.com/lcarli/AI-LearningHub/raw/main/docs/docs/en/challenges/challenge-004/context_docs.json) |
| `requests.json` | Requêtes de support avec budget | [Télécharger](https://github.com/lcarli/AI-LearningHub/raw/main/docs/docs/en/challenges/challenge-004/requests.json) |
| `starter_token_budget.py` | Optimiseur de budget cassé | [Télécharger](https://github.com/lcarli/AI-LearningHub/raw/main/docs/docs/en/challenges/challenge-004/starter_token_budget.py) |
| `test_token_budget.py` | Tests d'acceptation | [Télécharger](https://github.com/lcarli/AI-LearningHub/raw/main/docs/docs/en/challenges/challenge-004/test_token_budget.py) |
| `validate_token_budget.py` | Génère le code final de réussite | [Télécharger](https://github.com/lcarli/AI-LearningHub/raw/main/docs/docs/en/challenges/challenge-004/validate_token_budget.py) |

---

## Brief du défi

Vous recevez des documents compacts, des documents verbeux, des requêtes budgétées et un optimiseur cassé. Il n'y a pas de walkthrough : décidez comment estimer les tokens, classer le contexte, sélectionner les preuves et construire des prompts qui respectent le budget.

---

## Contraintes

- Utilisez uniquement la bibliothèque standard Python dans `starter_token_budget.py`.
- N'appelez pas d'API LLM.
- Ne hardcodez pas le comportement par ID de requête.
- N'incluez pas de documents non pertinents simplement parce qu'il reste de la place.
- Gardez la structure du prompt courte et ancrée.

---

## Critères d'acceptation

Votre solution est complète lorsque :

- `python -m pytest test_token_budget.py` passe
- Le document concis attendu est sélectionné pour chaque requête
- Les documents verbeux ou non pertinents ne passent pas devant les correspondances concises
- Chaque prompt respecte son `max_prompt_tokens`
- L'évaluation rapporte `within_budget is True`
- L'évaluation rapporte `all_prompts_under_budget is True`

---

## Validation

Lorsque votre implémentation est prête, exécutez :

```bash
python -m pytest test_token_budget.py
python validate_token_budget.py
```

Saisissez le code de réussite imprimé par `validate_token_budget.py` :

<div class="challenge-validator" data-answer="CH004-67CBEAD0">
  <input type="text" aria-label="Code de réussite" placeholder="CH004-XXXXXXXX" />
  <button type="button">Valider</button>
  <p class="challenge-validator-result" aria-live="polite"></p>
</div>

---

## Indices

??? tip "Indice 1 — L'estimation de tokens n'a pas besoin d'être parfaite"
    Elle doit seulement être déterministe et assez proche pour comparer les tailles de prompts.

??? tip "Indice 2 — La pertinence ne suffit pas"
    Un document long avec les bons mots peut être moins utile qu'un résumé concis avec la même preuve.

??? tip "Indice 3 — Budgétez au moment de la sélection"
    Il est plus facile de respecter le budget si vous rejetez le contexte avant de construire le prompt final.

??? tip "Indice 4 — Le template de prompt compte"
    Un template d'instructions verbeux peut consommer le budget que vous essayez d'économiser.

---

## Rubrique

| Domaine | Points | Ce qui est attendu |
|---------|:------:|--------------------|
| Estimation des tokens | 20 | Déterministe, proche de mots, utile pour les budgets |
| Classement du contexte | 30 | Sélectionne les documents concis et pertinents |
| Construction du prompt | 25 | Reste ancrée et sous budget |
| Évaluation | 15 | Rapporte correctement les documents sélectionnés et la conformité |
| Simplicité | 10 | Logique locale déterministe, sans sur-ingénierie |

---

## Objectifs bonus

- Ajouter des budgets séparés pour prompt système, contexte et réponse
- Rapporter les économies de tokens par rapport au baseline verbeux
- Ajouter un fallback lorsqu'aucun document ne tient dans le budget
- Ajouter une nouvelle requête avec budget plus serré et mettre à jour localement le payload du validateur

---

## Labs associés

- [Lab 038 — Optimisation des coûts IA](../labs/lab-038-cost-optimization.md)
- [Lab 071 — Cache de contexte](../labs/lab-071-context-caching.md)
- [Lab 072 — Benchmark de fiabilité des sorties structurées](../labs/lab-072-structured-outputs.md)
