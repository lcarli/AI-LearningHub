---
tags:
- foundry
- kit
- local-first
- phase-3
- quiz
lab:
  id: '042'
  level: L400
  journey: llm-foundations
  time_min: 180
  cost:
    tier: free-conditional
    requires:
    - local-compute-or-optional-paid-service
    estimate_usd: 0 for the local simulation; optional Real usage varies by service
      and must be capped.
    simulation: true
    cleanup: false
  roles:
  - developer
  - architect
  - student
  technologies:
  - foundry
  - phase-3
  status: active
  last_verified: '2026-10-27'
  languages:
  - en
  - pt
  - fr
---
# Lab 042: RAG d'entreprise avec évaluations et Foundry

<div class="lab-meta">
  <span><strong>Level:</strong> <span class="level-badge level-400">L400</span></span>
  <span><strong>Parcours:</strong> llm-foundations</span>
  <span><strong>Durée:</strong> ~180 min</span>
  <span><strong>Coût:</strong> free-conditional</span>
</div>

!!! info "Phase 3 · local first"
    Le parcours obligatoire est déterministe et local. Le parcours Réel est facultatif, estimé et nettoyé.

## Ce que vous apprendrez

- Construire une base RAG d'entreprise locale
- Mesurer récupération, ancrage, citations, latence et coût
- Utiliser évaluation et tracing Foundry comme adaptateur Réel
- Contrôler promotion et nettoyage

## Prérequis

- Python 3.10+ et un terminal
- Aucun identifiant pour le parcours obligatoire
- Lisez la spécification officielle avant un adaptateur hébergé

## Modèle visuel

```mermaid
flowchart LR
  D[Documents] --> X[Chunk and index]
  Q[Golden queries] --> R[Retrieve]
  X --> R
  R --> A[Answer with citations]
  A --> E[Local + Foundry evals]
  E --> G{Promotion gate}
```

## Scénario

OutdoorGear a besoin d'une implémentation révisable pour atelier, avec fixtures déterministes, frontières de confiance explicites, critères mesurables et adaptateur hébergé facultatif et réversible.

## Exercice guidé

### Step 1: `build_baseline`

1. Exécutez la fixture déterministe de cette étape.
2. Notez entrée, sortie, décision de politique et comportement d'échec.
3. Modifiez un comportement borné et relancez le test local.

**Evidence:** Conservez la commande, le résultat et une phrase expliquant pourquoi la preuve est fiable.

### Step 2: `evaluate_golden_set`

1. Exécutez la fixture déterministe de cette étape.
2. Notez entrée, sortie, décision de politique et comportement d'échec.
3. Modifiez un comportement borné et relancez le test local.

**Evidence:** Conservez la commande, le résultat et une phrase expliquant pourquoi la preuve est fiable.

### Step 3: `connect_foundry`

1. Exécutez la fixture déterministe de cette étape.
2. Notez entrée, sortie, décision de politique et comportement d'échec.
3. Modifiez un comportement borné et relancez le test local.

**Evidence:** Conservez la commande, le résultat et une phrase expliquant pourquoi la preuve est fiable.

### Step 4: `gate_and_cleanup`

1. Exécutez la fixture déterministe de cette étape.
2. Notez entrée, sortie, décision de politique et comportement d'échec.
3. Modifiez un comportement borné et relancez le test local.

**Evidence:** Conservez la commande, le résultat et une phrase expliquant pourquoi la preuve est fiable.

### Exécuter localement

```bash
cd docs/docs/fr/labs/lab-042
python -m unittest discover -v
```

## Simulation / Parcours Réel

<div class="phase3-path-tabs" data-phase3-tabs>
  <div role="tablist" aria-label="Simulation / Parcours Réel">
    <button type="button" role="tab" aria-selected="true" data-phase3-tab="simulation">Simulation</button>
    <button type="button" role="tab" aria-selected="false" data-phase3-tab="real">Parcours Réel</button>
  </div>
  <section role="tabpanel" data-phase3-panel="simulation">
    Utilisez les fixtures déterministes et le validateur local. Coût estimé : **0 USD**.
  </section>
  <section role="tabpanel" data-phase3-panel="real" hidden>
    Remplacez uniquement la frontière de l'adaptateur. Fixez un plafond, gardez les mêmes tests et notez région, rétention, identité, télémétrie et prix. Supprimez déploiements, points de terminaison, index, traces et données de test après validation.
  </section>
</div>

## Kit d'accompagnement

Le build du site génère des téléchargements PDF et ZIP stables. La CI conserve aussi un miroir temporaire pendant 30 jours.

- [`README.md` ](lab-042/README.md): démarrage et preuves
- [`CHEATSHEET.md` ](lab-042/CHEATSHEET.md): guide de décision
- [`scenario.json` ](lab-042/scenario.json): contrat déterministe
- [`test_scenario.py` ](lab-042/test_scenario.py): tests locaux
- [Télécharger le PDF généré](../downloads/kits/lab-042-kit-fr.pdf)
- [Télécharger le ZIP généré](../downloads/kits/lab-042-kit-fr.zip)

## Quiz noté

??? question "Pourquoi garder un contrat local ?"

    ??? success "Réponse"
        Il fournit une base déterministe avant la variabilité et le coût hébergés.

??? question "Quand le parcours Réel est-il terminé ?"

    ??? success "Réponse"
        Après enregistrement des preuves de validation et de nettoyage.

??? question "Comment traiter la sortie des outils ?"

    ??? success "Réponse"
        Comme donnée non fiable avant validation de politique et de schéma.

## Critères de sortie

- [ ] Les tests locaux passent sans identifiants.
- [ ] Le diagramme a une explication textuelle et ne dépend pas de la couleur.
- [ ] Le quiz noté a été revu.
- [ ] Le parcours Réel a un plafond et un plan de nettoyage.
- [ ] Sources et stabilité ont été vérifiées.

## Sources publiques officielles

- [Foundry Agent Service GA announcement](https://devblogs.microsoft.com/foundry/foundry-agent-service-ga/)
- [Foundry Agent Service](https://learn.microsoft.com/azure/ai-foundry/agents/)
- [Foundry evaluation](https://learn.microsoft.com/azure/ai-foundry/concepts/evaluation-approach-gen-ai)
- [Foundry Workflows retirement](https://learn.microsoft.com/azure/foundry/agents/concepts/workflow)
