---
tags: [challenge, guardrails, red-team, safety, pii, python, local]
---
# Défi 007 : Red team des garde-fous d'agents

<div class="lab-meta">
  <span><strong>Niveau :</strong> <span class="level-badge level-300">L300</span></span>
  <span><strong>Type :</strong> Défi</span>
  <span><strong>Durée :</strong> ~60 min</span>
  <span><strong>💰 Coût :</strong> <span class="level-badge cost-free">Gratuit (local)</span></span>
</div>

## Scénario

OutdoorGear prépare un agent de support orienté client. Avant le lancement, l'équipe sécurité vous donne un petit jeu de red team avec questions sûres, exposition de PII, tentatives de jailbreak, demandes dangereuses et demandes hors périmètre.

Votre tâche consiste à implémenter une couche locale de garde-fous qui bloque, masque ou autorise correctement chaque requête.

---

## Objectif

Corrigez `starter_guardrails.py` afin que la couche de garde-fous classe correctement les scénarios, masque les adresses email, rapporte les métriques de red team et génère un code de validation.

Votre couche finale doit :

- Autoriser les questions normales de support OutdoorGear
- Masquer les adresses email avant le traitement par l'agent
- Bloquer les tentatives de jailbreak
- Bloquer les demandes dangereuses liées à la sécurité physique
- Bloquer les demandes d'automatisation hors périmètre
- Éviter les faux positifs sur les questions sûres de support

---

## Fichiers de départ

Enregistrez ces fichiers dans un dossier nommé `challenge-007/` :

| Fichier | Objectif | Télécharger |
|---------|----------|-------------|
| `scenarios.json` | Scénarios sûrs et de red team | [Télécharger](https://github.com/lcarli/AI-LearningHub/raw/main/docs/docs/en/challenges/challenge-007/scenarios.json) |
| `starter_guardrails.py` | Couche de garde-fous cassée | [Télécharger](https://github.com/lcarli/AI-LearningHub/raw/main/docs/docs/en/challenges/challenge-007/starter_guardrails.py) |
| `test_guardrails.py` | Tests d'acceptation | [Télécharger](https://github.com/lcarli/AI-LearningHub/raw/main/docs/docs/en/challenges/challenge-007/test_guardrails.py) |
| `validate_guardrails.py` | Génère le code final de réussite | [Télécharger](https://github.com/lcarli/AI-LearningHub/raw/main/docs/docs/en/challenges/challenge-007/validate_guardrails.py) |

---

## Brief du défi

Vous recevez des scénarios fixtures et une implémentation de garde-fous cassée. Il n'y a pas de walkthrough : décidez quels signaux doivent déclencher blocage, masquage ou autorisation, puis faites correspondre les métriques de red team au comportement attendu.

---

## Contraintes

- Utilisez uniquement la bibliothèque standard Python dans `starter_guardrails.py`.
- Ne hardcodez pas le comportement par ID de scénario.
- Ne bloquez pas les questions normales de produit/retour.
- Le masquage doit préserver le reste de la requête utilisateur.
- Les blocages doivent être déterministes.

---

## Critères d'acceptation

Votre solution est complète lorsque :

- `python -m pytest test_guardrails.py` passe
- Les questions sûres de produit et de retour sont autorisées
- Les adresses email sont masquées
- Les requêtes de jailbreak, dangereuses et hors périmètre sont bloquées
- `false_positive == 0`

---

## Validation

Lorsque votre implémentation est prête, exécutez :

```bash
python -m pytest test_guardrails.py
python validate_guardrails.py
```

Saisissez le code de réussite imprimé par `validate_guardrails.py` :

<div class="challenge-validator" data-answer="CH007-452A3ED6">
  <input type="text" aria-label="Code de réussite" placeholder="CH007-XXXXXXXX" />
  <button type="button">Valider</button>
  <p class="challenge-validator-result" aria-live="polite"></p>
</div>

---

## Indices

??? tip "Indice 1 — Le masquage n'est pas le blocage"
    Un utilisateur peut fournir une adresse email dans une requête de support valide.

??? tip "Indice 2 — Le périmètre compte"
    Une requête peut être inoffensive mais rester hors périmètre pour un agent de support OutdoorGear.

??? tip "Indice 3 — Les patterns de sécurité peuvent être simples"
    Ce défi ne nécessite pas de classification ML. Des contrôles déterministes par phrases et regex suffisent.

---

## Rubrique

| Domaine | Points | Ce qui est attendu |
|---------|:------:|--------------------|
| Classification | 35 | Décisions correctes autoriser/bloquer/masquer |
| Traitement des PII | 20 | Email masqué sans perdre le sens de la requête |
| Périmètre de sécurité | 20 | Requêtes dangereuses et hors périmètre bloquées |
| Métriques | 15 | Résumé de red team exact |
| Simplicité | 10 | Petit code de garde-fous déterministe |

---

## Labs associés

- [Lab 008 — IA responsable pour agents](../labs/lab-008-responsible-ai.md)
- [Lab 036 — Défense contre l'injection de prompt et sécurité](../labs/lab-036-prompt-injection-security.md)
- [Lab 082 — Garde-fous d'agents](../labs/lab-082-agent-guardrails.md)
