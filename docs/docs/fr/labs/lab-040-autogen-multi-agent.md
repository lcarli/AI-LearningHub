---
tags:
- kit
- local-first
- maf
- phase-3
- quiz
lab:
  id: '040'
  level: L400
  journey: ai-agents
  time_min: 150
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
  - maf
  - phase-3
  status: active
  last_verified: '2026-10-27'
  languages:
  - en
  - pt
  - fr
---
# Lab 040: Systèmes multi-agents de production avec Microsoft Agent Framework

<div class="lab-meta">
  <span><strong>Level:</strong> <span class="level-badge level-400">L400</span></span>
  <span><strong>Parcours:</strong> ai-agents</span>
  <span><strong>Durée:</strong> ~150 min</span>
  <span><strong>Coût:</strong> free-conditional</span>
</div>

!!! info "Phase 3 · local first"
    Le parcours obligatoire est déterministe et local. Le parcours Réel est facultatif, estimé et nettoyé.

## Ce que vous apprendrez

- Concevoir une topologie MAF de production
- Migrer les conversations AutoGen avec le guide officiel
- Appliquer identité, politique, télémétrie, budgets et reprise
- Prouver rollback et approbation humaine

## Prérequis

- Python 3.10+ et un terminal
- Aucun identifiant pour le parcours obligatoire
- Lisez la spécification officielle avant un adaptateur hébergé

## Modèle visuel

```mermaid
flowchart LR
  I[Ingress] --> G[Policy gateway]
  G --> W[MAF workflow]
  W --> A1[Specialist]
  W --> A2[Reviewer]
  A1 & A2 --> O[OpenTelemetry]
  W --> H[Human approval]
```

## Scénario

OutdoorGear a besoin d'une implémentation révisable pour atelier, avec fixtures déterministes, frontières de confiance explicites, critères mesurables et adaptateur hébergé facultatif et réversible.

## Exercice guidé

### Step 1: `model_boundaries`

1. Exécutez la fixture déterministe de cette étape.
2. Notez entrée, sortie, décision de politique et comportement d'échec.
3. Modifiez un comportement borné et relancez le test local.

**Evidence:** Conservez la commande, le résultat et une phrase expliquant pourquoi la preuve est fiable.

### Step 2: `migrate_autogen`

1. Exécutez la fixture déterministe de cette étape.
2. Notez entrée, sortie, décision de politique et comportement d'échec.
3. Modifiez un comportement borné et relancez le test local.

**Evidence:** Conservez la commande, le résultat et une phrase expliquant pourquoi la preuve est fiable.

### Step 3: `inject_failures`

1. Exécutez la fixture déterministe de cette étape.
2. Notez entrée, sortie, décision de politique et comportement d'échec.
3. Modifiez un comportement borné et relancez le test local.

**Evidence:** Conservez la commande, le résultat et une phrase expliquant pourquoi la preuve est fiable.

### Step 4: `prove_operations`

1. Exécutez la fixture déterministe de cette étape.
2. Notez entrée, sortie, décision de politique et comportement d'échec.
3. Modifiez un comportement borné et relancez le test local.

**Evidence:** Conservez la commande, le résultat et une phrase expliquant pourquoi la preuve est fiable.

### Exécuter localement

```bash
cd docs/docs/fr/labs/lab-040
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

- [`README.md` ](lab-040/README.md): démarrage et preuves
- [`CHEATSHEET.md` ](lab-040/CHEATSHEET.md): guide de décision
- [`scenario.json` ](lab-040/scenario.json): contrat déterministe
- [`test_scenario.py` ](lab-040/test_scenario.py): tests locaux
- [Télécharger le PDF généré](../downloads/kits/lab-040-kit-fr.pdf)
- [Télécharger le ZIP généré](../downloads/kits/lab-040-kit-fr.zip)

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

- [Microsoft Agent Framework 1.0 GA](https://devblogs.microsoft.com/agent-framework/microsoft-agent-framework-version-1-0/)
- [AutoGen to Agent Framework migration](https://learn.microsoft.com/agent-framework/migration-guide/from-autogen/)
