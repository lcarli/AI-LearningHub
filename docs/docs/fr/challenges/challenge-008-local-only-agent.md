---
tags: [challenge, local-ai, agent, tools, rag, python]
---
# Défi 008 : Construire un agent 100 % local

<div class="lab-meta">
  <span><strong>Niveau :</strong> <span class="level-badge level-200">L200</span></span>
  <span><strong>Type :</strong> Défi</span>
  <span><strong>Durée :</strong> ~75 min</span>
  <span><strong>💰 Coût :</strong> <span class="level-badge cost-free">Gratuit (local)</span></span>
</div>

## Scénario

OutdoorGear veut un petit agent de support qui fonctionne sans Azure, GitHub Models, LLM hébergé ou appel réseau. Il doit classifier une requête, utiliser des outils locaux sur des données locales et retourner une réponse ancrée avec une trace.

Votre tâche consiste à terminer l'agent 100 % local et à prouver qu'il gère recherche produit, consultation de politique et recommandation de bundle sans configuration cloud.

---

## Objectif

Corrigez `starter_local_agent.py` afin que l'agent local route correctement les requêtes, utilise uniquement des données locales, retourne des réponses utiles, rapporte aucune utilisation cloud et génère un code de validation.

Votre agent local final doit :

- Ne nécessiter aucune configuration cloud
- Classifier trois intents supportées
- Rechercher des produits localement
- Consulter du texte de politique localement
- Construire un bundle camping sous budget
- Retourner réponse, trace, intent et `uses_cloud: False`

---

## Fichiers de départ

Enregistrez ces fichiers dans un dossier nommé `challenge-008/` :

| Fichier | Objectif | Télécharger |
|---------|----------|-------------|
| `local_data.json` | Données locales de produits et politiques | [Télécharger](https://github.com/lcarli/AI-LearningHub/raw/main/docs/docs/en/challenges/challenge-008/local_data.json) |
| `eval_requests.json` | Requêtes d'évaluation | [Télécharger](https://github.com/lcarli/AI-LearningHub/raw/main/docs/docs/en/challenges/challenge-008/eval_requests.json) |
| `starter_local_agent.py` | Agent local cassé | [Télécharger](https://github.com/lcarli/AI-LearningHub/raw/main/docs/docs/en/challenges/challenge-008/starter_local_agent.py) |
| `test_local_agent.py` | Tests d'acceptation | [Télécharger](https://github.com/lcarli/AI-LearningHub/raw/main/docs/docs/en/challenges/challenge-008/test_local_agent.py) |
| `validate_local_agent.py` | Génère le code final de réussite | [Télécharger](https://github.com/lcarli/AI-LearningHub/raw/main/docs/docs/en/challenges/challenge-008/validate_local_agent.py) |

---

## Brief du défi

Vous recevez des données locales de produits/politiques, des requêtes d'évaluation et un agent local cassé. Il n'y a pas de walkthrough : décidez comment router les intents, appeler les outils locaux, composer les réponses et prouver qu'aucune dépendance cloud n'est requise.

---

## Contraintes

- Utilisez uniquement la bibliothèque standard Python dans `starter_local_agent.py`.
- N'appelez aucun réseau, modèle hébergé ou API cloud.
- Ne hardcodez pas les réponses par ID de requête.
- Préservez les noms publics des fonctions utilisés par les tests.
- Gardez des traces utiles pour montrer quel outil local a été exécuté.

---

## Critères d'acceptation

Votre solution est complète lorsque :

- `python -m pytest test_local_agent.py` passe
- La recherche produit retourne `RainShell Pro Jacket`
- La consultation de politique retourne la fenêtre de retour de 60 jours
- La recommandation de bundle inclut les trois articles camping attendus sous budget
- La trace enregistre l'intent et l'exécution de l'outil
- `uses_cloud` vaut `False`

---

## Validation

Lorsque votre implémentation est prête, exécutez :

```bash
python -m pytest test_local_agent.py
python validate_local_agent.py
```

Saisissez le code de réussite imprimé par `validate_local_agent.py` :

<div class="challenge-validator" data-answer="CH008-A1B101A9">
  <input type="text" aria-label="Code de réussite" placeholder="CH008-XXXXXXXX" />
  <button type="button">Valider</button>
  <p class="challenge-validator-result" aria-live="polite"></p>
</div>

---

## Indices

??? tip "Indice 1 — Local-only est une exigence"
    Un agent local peut rester utile si le routage d'intent et les outils sont déterministes.

??? tip "Indice 2 — Gardez le routage étroit"
    Les requêtes fixtures sont volontairement limitées à recherche produit, consultation de politique et recommandation de bundle.

??? tip "Indice 3 — Tracez l'outil, pas seulement la réponse"
    Une trace aide à prouver que l'agent a pris une décision et utilisé un outil local.

---

## Rubrique

| Domaine | Points | Ce qui est attendu |
|---------|:------:|--------------------|
| Comportement local-only | 25 | Aucune dépendance cloud ou réseau |
| Routage d'intent | 25 | Trois types de requête correctement classifiés |
| Sorties d'outils | 25 | Réponses produit, politique et bundle correctes |
| Traçabilité | 15 | Trace montrant intent et outil local sélectionné |
| Simplicité | 10 | Implémentation locale déterministe |

---

## Labs associés

- [Lab 015 — Ollama LLMs locaux](../labs/lab-015-ollama-local-llms.md)
- [Lab 078 — Foundry Local](../labs/lab-078-foundry-local.md)
- [Lab 020 — Serveur MCP en Python](../labs/lab-020-mcp-server-python.md)
