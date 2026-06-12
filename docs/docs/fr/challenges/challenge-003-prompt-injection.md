---
tags: [challenge, security, prompt-injection, rag, python, local]
---
# Défi 003 : Défendre un agent contre le prompt injection

<div class="lab-meta">
  <span><strong>Niveau :</strong> <span class="level-badge level-200">L200</span></span>
  <span><strong>Type :</strong> Défi</span>
  <span><strong>Durée :</strong> ~60 min</span>
  <span><strong>💰 Coût :</strong> <span class="level-badge cost-free">Gratuit (local)</span></span>
</div>

## Scénario

OutdoorGear a importé des avis clients dans la base de connaissances d'un agent de support. Un avis importé contient des instructions malveillantes qui tentent d'écraser la politique de l'agent, de révéler des instructions cachées et d'affirmer que les retours sont illimités.

Votre tâche consiste à renforcer un helper de support local de type RAG afin de bloquer les tentatives de prompt injection, exclure le contexte dangereux et répondre aux questions sûres uniquement à partir de documents de politique fiables.

---

## Objectif

Corrigez `starter_prompt_defense.py` afin que la suite de défense bloque les attaques, autorise les requêtes sûres, supprime le contexte malveillant, évite de divulguer le texte attaquant et génère un code de validation.

Votre défense finale doit :

- Normaliser le texte avant les contrôles de politique
- Détecter les patterns courants de prompt injection
- Supprimer le contexte non fiable ou malveillant des documents récupérés
- Bloquer les requêtes utilisateur malveillantes
- Répondre aux requêtes sûres uniquement avec du contexte fiable
- Rapporter correctement les métriques de défense

---

## Fichiers de départ

Enregistrez ces fichiers dans un dossier nommé `challenge-003/` :

| Fichier | Objectif | Télécharger |
|---------|----------|-------------|
| `documents.json` | Contexte de support fiable et non fiable | [Télécharger](https://github.com/lcarli/AI-LearningHub/raw/main/docs/docs/en/challenges/challenge-003/documents.json) |
| `requests.json` | Requêtes sûres et malveillantes | [Télécharger](https://github.com/lcarli/AI-LearningHub/raw/main/docs/docs/en/challenges/challenge-003/requests.json) |
| `starter_prompt_defense.py` | Implémentation de défense cassée | [Télécharger](https://github.com/lcarli/AI-LearningHub/raw/main/docs/docs/en/challenges/challenge-003/starter_prompt_defense.py) |
| `test_prompt_defense.py` | Tests d'acceptation | [Télécharger](https://github.com/lcarli/AI-LearningHub/raw/main/docs/docs/en/challenges/challenge-003/test_prompt_defense.py) |
| `validate_prompt_defense.py` | Génère le code final de réussite | [Télécharger](https://github.com/lcarli/AI-LearningHub/raw/main/docs/docs/en/challenges/challenge-003/validate_prompt_defense.py) |

---

## Brief du défi

Vous recevez des documents avec des niveaux de confiance mixtes, des requêtes sûres, des requêtes d'attaque et une couche de défense cassée. Il n'y a pas de walkthrough : décidez comment détecter l'intention d'attaque, filtrer le contexte, répondre en sécurité et évaluer si l'agent divulgue des instructions contrôlées par l'attaquant.

---

## Contraintes

- Utilisez uniquement la bibliothèque standard Python dans `starter_prompt_defense.py`.
- N'appelez pas d'API LLM.
- Ne hardcodez pas le comportement par ID de requête.
- Ne répondez pas à partir de contenu non fiable d'avis clients.
- Les requêtes sûres doivent toujours recevoir une réponse.
- Le texte d'attaque ne doit pas apparaître dans les réponses sûres.

---

## Critères d'acceptation

Votre solution est complète lorsque :

- `python -m pytest test_prompt_defense.py` passe
- Les trois requêtes d'attaque sont bloquées
- Les deux requêtes sûres sont autorisées
- L'avis malveillant est exclu du contexte sûr
- Les réponses sûres citent des faits de la politique officielle
- `leakage_count == 0`

---

## Validation

Lorsque votre implémentation est prête, exécutez :

```bash
python -m pytest test_prompt_defense.py
python validate_prompt_defense.py
```

Saisissez le code de réussite imprimé par `validate_prompt_defense.py` :

<div class="challenge-validator" data-answer="CH003-EF57BB85">
  <input type="text" aria-label="Code de réussite" placeholder="CH003-XXXXXXXX" />
  <button type="button">Valider</button>
  <p class="challenge-validator-result" aria-live="polite"></p>
</div>

---

## Indices

??? tip "Indice 1 — Traitez séparément entrée utilisateur et contexte récupéré"
    Une requête utilisateur peut être malveillante, mais les documents récupérés peuvent aussi contenir des instructions malveillantes.

??? tip "Indice 2 — Les métadonnées de confiance comptent"
    Le fixture inclut un champ `trusted`. Utilisez-le, mais ne vous reposez pas uniquement sur les métadonnées.

??? tip "Indice 3 — Cherchez l'intention, pas seulement les phrases exactes"
    Les attaquants peuvent dire "ignore", "bypass", "admin_override" ou "system prompt" avec différentes casses.

??? tip "Indice 4 — Les réponses sûres doivent être ennuyeuses"
    Une réponse sûre de politique doit citer des faits de politique. Elle ne doit pas mentionner de prompts cachés, d'overrides ou de retours illimités.

---

## Rubrique

| Domaine | Points | Ce qui est attendu |
|---------|:------:|--------------------|
| Détection d'attaques | 30 | Bloque des patterns variés de prompt injection |
| Filtrage du contexte | 25 | Supprime le contexte dangereux et conserve les documents fiables |
| Réponse sûre | 20 | Répond aux requêtes sûres à partir de preuves officielles |
| Prévention des fuites | 15 | Aucune chaîne contrôlée par l'attaquant n'apparaît dans les réponses |
| Simplicité | 10 | Contrôles locaux déterministes, sans sur-ingénierie |

---

## Objectifs bonus

- Ajouter des niveaux de sévérité pour les attaques
- Retourner un message de refus sûr pour les requêtes bloquées
- Ajouter des raisons d'exclusion par document
- Ajouter une nouvelle variante d'attaque et mettre à jour localement le payload du validateur

---

## Labs associés

- [Lab 008 — IA responsable pour agents](../labs/lab-008-responsible-ai.md)
- [Lab 036 — Défense contre l'injection de prompt et sécurité](../labs/lab-036-prompt-injection-security.md)
- [Lab 082 — Garde-fous d'agents](../labs/lab-082-agent-guardrails.md)
