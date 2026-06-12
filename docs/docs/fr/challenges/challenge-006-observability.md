---
tags: [challenge, observability, incident, tracing, python, local]
---
# Défi 006 : Investiguer un incident d'observabilité d'agent

<div class="lab-meta">
  <span><strong>Niveau :</strong> <span class="level-badge level-300">L300</span></span>
  <span><strong>Type :</strong> Défi</span>
  <span><strong>Durée :</strong> ~60 min</span>
  <span><strong>💰 Coût :</strong> <span class="level-badge cost-free">Gratuit (local)</span></span>
</div>

## Scénario

L'agent de support OutdoorGear a connu un pic de latence et une requête a échoué. Vous recevez une petite exportation de traces avec des spans racine d'agent et des spans enfants d'outils/LLM. L'analyseur actuel calcule les métriques sur les mauvais spans et rapporte la mauvaise cause racine.

Votre tâche consiste à corriger l'analyseur afin qu'un ingénieur d'astreinte identifie la trace en échec, la dépendance responsable, le taux d'erreur et la latence p95.

---

## Objectif

Corrigez `starter_observability.py` pour qu'il résume correctement l'incident et génère un code de validation.

Votre analyseur final doit :

- Isoler les spans racine de requêtes d'agent
- Calculer le taux d'erreur uniquement sur les requêtes racine
- Calculer la latence p95 nearest-rank sur les requêtes racine
- Identifier la trace racine en échec
- Attribuer la cause racine au span de dépendance en échec

---

## Fichiers de départ

Enregistrez ces fichiers dans un dossier nommé `challenge-006/` :

| Fichier | Objectif | Télécharger |
|---------|----------|-------------|
| `traces.json` | Export mock de traces d'agent | [Télécharger](https://github.com/lcarli/AI-LearningHub/raw/main/docs/docs/en/challenges/challenge-006/traces.json) |
| `starter_observability.py` | Analyseur d'incident cassé | [Télécharger](https://github.com/lcarli/AI-LearningHub/raw/main/docs/docs/en/challenges/challenge-006/starter_observability.py) |
| `test_observability.py` | Tests d'acceptation | [Télécharger](https://github.com/lcarli/AI-LearningHub/raw/main/docs/docs/en/challenges/challenge-006/test_observability.py) |
| `validate_observability.py` | Génère le code final de réussite | [Télécharger](https://github.com/lcarli/AI-LearningHub/raw/main/docs/docs/en/challenges/challenge-006/validate_observability.py) |

---

## Brief du défi

Vous recevez des spans de trace et un analyseur cassé. Il n'y a pas de walkthrough : décidez quels spans comptent comme requêtes, comment calculer les métriques SRE et comment attribuer l'incident à la bonne dépendance enfant.

---

## Contraintes

- Utilisez uniquement la bibliothèque standard Python dans `starter_observability.py`.
- Ne hardcodez pas le dictionnaire final de résumé.
- Les métriques doivent être calculées à partir des spans.
- Les spans enfants peuvent expliquer la cause racine, mais ne doivent pas gonfler les comptes de requêtes.

---

## Critères d'acceptation

Votre solution est complète lorsque :

- `python -m pytest test_observability.py` passe
- Les requêtes racine sont `tr-001`, `tr-002`, `tr-003` et `tr-004`
- Le taux d'erreur est `25.0`
- La latence p95 est `2200`
- La trace d'incident est `tr-003`
- La cause racine est `inventory_api_timeout`

---

## Validation

Lorsque votre implémentation est prête, exécutez :

```bash
python -m pytest test_observability.py
python validate_observability.py
```

Saisissez le code de réussite imprimé par `validate_observability.py` :

<div class="challenge-validator" data-answer="CH006-FC7D7B5F">
  <input type="text" aria-label="Code de réussite" placeholder="CH006-XXXXXXXX" />
  <button type="button">Valider</button>
  <p class="challenge-validator-result" aria-live="polite"></p>
</div>

---

## Indices

??? tip "Indice 1 — Séparez les spans de requête des spans enfants"
    Les métriques de requêtes racine ne doivent pas compter chaque outil ou span LLM.

??? tip "Indice 2 — La cause racine est souvent sous la racine"
    Le span de l'agent dit que la requête a échoué ; la dépendance enfant indique souvent pourquoi.

??? tip "Indice 3 — p95 a une définition"
    Utilisez le p95 nearest-rank pour ce défi.

---

## Rubrique

| Domaine | Points | Ce qui est attendu |
|---------|:------:|--------------------|
| Filtrage des spans | 25 | Les requêtes racine d'agent sont isolées correctement |
| Métriques | 30 | Taux d'erreur et p95 utilisent le bon dénominateur |
| Cause racine | 25 | La défaillance de dépendance est identifiée correctement |
| Résumé d'incident | 10 | Sortie concise et actionnable |
| Simplicité | 10 | Analyse locale déterministe |

---

## Labs associés

- [Lab 033 — Observabilité d'agents avec App Insights](../labs/lab-033-agent-observability.md)
- [Lab 049 — Traçage d'agents Foundry IQ](../labs/lab-049-foundry-iq-agent-tracing.md)
- [Lab 050 — Observabilité multi-agent](../labs/lab-050-multi-agent-observability.md)
