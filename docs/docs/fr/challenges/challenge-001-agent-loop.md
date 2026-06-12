---
tags: [challenge, agent-loop, tools, python, local]
---
# Défi 001 : Construire une boucle d'agent à partir de zéro

<div class="lab-meta">
  <span><strong>Niveau :</strong> <span class="level-badge level-100">L100</span></span>
  <span><strong>Type :</strong> Défi</span>
  <span><strong>Durée :</strong> ~60 min</span>
  <span><strong>💰 Coût :</strong> <span class="level-badge cost-free">Gratuit (local)</span></span>
</div>

## Scénario

OutdoorGear veut un petit agent assistant produit capable de raisonner sur un catalogue local. L'équipe ne veut **pas** encore utiliser Semantic Kernel, LangGraph, AutoGen ou un LLM hébergé. Elle veut d'abord vérifier que vous comprenez la boucle centrale :

> percevoir → décider → agir → observer → répondre

Votre tâche consiste à terminer une petite boucle d'agent en Python qui choisit des outils, les exécute, stocke les observations et produit une réponse finale ancrée dans les résultats.

---

## Objectif

Faites passer tous les tests en implémentant les fonctions manquantes dans `starter_agent_loop.py`.

À la fin, votre agent doit pouvoir :

- Rechercher des produits avec catégorie, mots de requête, budget et filtre de stock
- Consulter les détails d'un produit par SKU
- Recommander un petit bundle de camping en stock sous un budget donné
- Exécuter une boucle qui appelle exactement un outil avant de répondre aux requêtes supportées
- Retourner une trace montrant ce que l'agent a fait

---

## Fichiers de départ

Enregistrez ces fichiers dans un dossier nommé `challenge-001/` :

| Fichier | Objectif | Télécharger |
|---------|----------|-------------|
| `products.json` | Catalogue mock OutdoorGear | [Télécharger](https://github.com/lcarli/AI-LearningHub/raw/main/docs/docs/en/challenges/challenge-001/products.json) |
| `starter_agent_loop.py` | Implémentation de départ avec TODOs | [Télécharger](https://github.com/lcarli/AI-LearningHub/raw/main/docs/docs/en/challenges/challenge-001/starter_agent_loop.py) |
| `test_agent_loop.py` | Tests d'acceptation | [Télécharger](https://github.com/lcarli/AI-LearningHub/raw/main/docs/docs/en/challenges/challenge-001/test_agent_loop.py) |

---

## Configuration

```bash
cd challenge-001
python -m pip install pytest
python -m pytest test_agent_loop.py
```

Les tests doivent échouer au départ. Votre tâche est de les faire passer.

---

## Contraintes

- Utilisez uniquement la bibliothèque standard Python dans `starter_agent_loop.py`.
- N'appelez pas d'API LLM.
- N'utilisez pas de framework d'agents.
- Gardez la boucle lisible : le but est de comprendre le flux de contrôle.
- Préservez la forme de retour de `run_agent()` :

```python
{
    "final_answer": "...",
    "trace": [
        {"step": 1, "type": "tool", "tool": "...", "arguments": {...}},
        {"step": 2, "type": "final"}
    ]
}
```

---

## Critères d'acceptation

Votre solution est complète lorsque :

- `python -m pytest test_agent_loop.py` passe
- La demande de veste appelle `search_products` avant de répondre
- La demande de bundle camping appelle `recommend_bundle` avant de répondre
- La réponse finale inclut des noms de produits, des prix et une justification courte
- Les produits hors stock ne sont pas recommandés
- La boucle s'arrête avec une réponse finale avant `max_steps`

---

## Indices

??? tip "Indice 1 — Commencez par les outils"
    Implémentez `search_products`, `get_product_details` et `recommend_bundle` avant de toucher à la boucle. Une boucle d'agent n'est utile que si les outils sont fiables.

??? tip "Indice 2 — Gardez le parsing simple"
    Vous n'avez pas besoin de NLP avancé. De simples vérifications de mots comme `jacket`, `camping`, `under` et `SKU` suffisent pour ce défi.

??? tip "Indice 3 — Utilisez les observations comme mémoire"
    `state.observations` est la mémoire court terme de la boucle. Après l'exécution d'un outil, la réponse finale doit se baser sur la dernière observation, pas sur le catalogue d'origine.

??? tip "Indice 4 — Décidez de manière déterministe"
    S'il n'y a pas encore d'observations, choisissez un outil. S'il existe déjà au moins une observation utile, choisissez `final`.

---

## Rubrique

| Domaine | Points | Ce qui est attendu |
|---------|:------:|--------------------|
| Correction des outils | 30 | Les filtres, la recherche par SKU et la sélection du bundle sont exacts |
| Boucle d'agent | 30 | Flux clair percevoir → décider → agir → observer → répondre |
| Réponse ancrée | 20 | La réponse utilise les observations des outils et cite des produits concrets |
| Traçabilité | 10 | La trace montre l'appel d'outil et l'étape finale |
| Simplicité | 10 | Pas de framework, d'API ou de sur-ingénierie inutile |

---

## Objectifs bonus

- Ajouter le support de "comparer deux SKUs"
- Ajouter une réponse d'erreur lorsqu'aucun produit ne correspond
- Ajouter un second appel d'outil avant la réponse finale pour les demandes ambiguës
- Créer un parser de `max_price` qui accepte `$150`, `150 dollars` et `under 150`

---

## Labs associés

- [Lab 001 — Que sont les agents IA ?](../labs/lab-001-what-are-ai-agents.md)
- [Lab 018 — Appel de fonctions et utilisation d'outils](../labs/lab-018-function-calling.md)
- [Lab 020 — Serveur MCP en Python](../labs/lab-020-mcp-server-python.md)
