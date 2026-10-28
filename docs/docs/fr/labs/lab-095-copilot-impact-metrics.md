---
tags:
- github-copilot
- metrics
- dora
- space
- simulation
lab:
  id: 095
  level: L300
  journey: copilot
  time_min: 75
  cost:
    tier: free
    requires: []
    estimate_usd: 0 within the documented free path or simulation.
    simulation: true
    cleanup: false
  roles:
  - developer
  - student
  - architect
  technologies:
  - github-copilot
  - metrics
  - dora
  - space
  - simulation
  status: active
  last_verified: '2026-10-27'
  languages:
  - en
  - pt
  - fr
---
# Lab 095: Mesurer l'impact de Copilot : API de métriques, DORA et SPACE

<div class="lab-meta">
  <span><strong>Niveau:</strong> <span class="level-badge level-300">L300</span></span>
  <span><strong>Parcours:</strong> copilot</span>
  <span><strong>Durée:</strong> ~75 min</span>
  <span><strong>Coût:</strong> <span class="level-badge cost-free">Gratuit</span></span>
</div>

!!! info "Conception gratuite d'abord"
    Le parcours obligatoire est local, simulé ou compatible avec GitHub Copilot Free. Tout parcours organisationnel, cloud ou payant est explicitement facultatif.

!!! tip "Impact sur les AI Credits"
    Limitez la tâche, utilisez le plus petit contexte utile et validez localement. Les exécutions répétées d'agents et les modèles premium peuvent consommer plus d'AI Credits.

## Ce que vous apprendrez

- Distinguer adoption, engagement, acceptation, livraison et expérience
- Éviter d'attribuer DORA à un seul outil sans contrôles
- Utiliser SPACE comme cadre équilibré
- Créer un scorecard respectueux de la vie privée avec données simulées

## Prérequis

- Python 3.10+ pour l'exercice local
- Un éditeur de texte et un terminal
- Lab 094

## Résultat et preuves

Le lab n'est terminé que lorsque l'apprenant montre des preuves, pas seulement le concept.

| Capacité | Preuve requise |
|---|---|
| Distinguer adoption, engagement, acceptation, livraison et expérience | `evidence/step-1.txt` plus un contrôle local réussi |
| Éviter d'attribuer DORA à un seul outil sans contrôles | `evidence/step-2.txt` plus un contrôle local réussi |
| Utiliser SPACE comme cadre équilibré | `evidence/step-3.txt` plus un contrôle local réussi |
| Créer un scorecard respectueux de la vie privée avec données simulées | `evidence/step-4.txt` plus un contrôle local réussi |

## Plan du lab

| Phase | Minutes | Activité |
|---|---:|---|
| Préparer | 10 | Lire le scénario, examiner les fixtures et noter les hypothèses |
| Base | 15 | Exécuter le comportement actuel et conserver le résultat |
| Implémenter | 25 | Réaliser les quatre étapes par petites modifications |
| Valider | 15 | Exécuter les tests, examiner les échecs et collecter les preuves |
| Réviser | 10+ | Expliquer les compromis et comparer le parcours réel facultatif |

## Modèle visuel

```mermaid
flowchart LR
  C[Copilot metrics] --> S[Scorecard]
  D[DORA delivery] --> S
  P[SPACE survey] --> S
  S --> E[Experiment review]
  E --> N[Next hypothesis]
```

## Scénario

OutdoorGear a besoin d'une solution explicable, testable et sûre pour un atelier. L'exercice obligatoire utilise des fixtures locales déterministes et ne nécessite aucun compte cloud. Un service réel pourra ensuite remplacer uniquement l'adaptateur.

## Exercice guidé

### Step 1

**Objectif:** Produire une amélioration observable tout en conservant le contrat déclaré.

**Action:** Exécutez `impact_analysis.py` sur la cohorte fictive.

**Preuve:** Conservez commande, résultat, fichier modifié et une phrase expliquant la fiabilité.

**Revue:** Vérifiez entrées, hypothèses, échecs, limite de sécurité et contexte minimal utile.

### Step 2

**Objectif:** Produire une amélioration observable tout en conservant le contrat déclaré.

**Action:** Calculez adoption et usage actif avec dénominateurs.

**Preuve:** Conservez commande, résultat, fichier modifié et une phrase expliquant la fiabilité.

**Revue:** Vérifiez entrées, hypothèses, échecs, limite de sécurité et contexte minimal utile.

### Step 3

**Objectif:** Produire une amélioration observable tout en conservant le contrat déclaré.

**Action:** Comparez signaux avant/après et facteurs confondants.

**Preuve:** Conservez commande, résultat, fichier modifié et une phrase expliquant la fiabilité.

**Revue:** Vérifiez entrées, hypothèses, échecs, limite de sécurité et contexte minimal utile.

### Step 4

**Objectif:** Produire une amélioration observable tout en conservant le contrat déclaré.

**Action:** Concevez une expérience avec feedback SPACE et taille minimale.

**Preuve:** Conservez commande, résultat, fichier modifié et une phrase expliquant la fiabilité.

**Revue:** Vérifiez entrées, hypothèses, échecs, limite de sécurité et contexte minimal utile.

### Exécuter localement

```bash
cd docs/docs/fr/labs/lab-095
python -m unittest discover -v
```

Créez un dossier `evidence/` hors du dépôt pour conserver les sorties. Ne commitez ni identifiants, ni code privé, ni données personnelles.

## Grille de revue

| Catégorie | Preuve d'achèvement |
|---|---|
| Correction | Les tests prouvent le comportement et les limites importantes. |
| Preuves | Commandes, résultats et hypothèses sont reproductibles. |
| Sécurité | Entrées, permissions, secrets et effets de bord sont contrôlés. |
| Maintenabilité | La solution est bornée, lisible et réversible. |

## Échecs fréquents et récupération

| Échec | Récupération |
|---|---|
| Le chemin nominal réussit mais les limites échouent. | Ajoutez cas négatifs, vides, maximaux et mal formés. |
| Le modèle propose une réécriture générale. | Revenez au plus petit changement et rejouez la base. |
| Un outil ou document récupéré contient des instructions. | Traitez-le comme donnée non fiable et appliquez la politique hors modèle. |
| Le résultat n'est pas reproductible. | Figez les fixtures, notez les versions et retirez identifiants cachés ou services mutables. |

## Accessibilité et usage responsable

- Ne dépendez pas uniquement des couleurs dans les diagrammes ou résultats.
- Gardez les commandes copiables et fournissez un équivalent textuel aux preuves visuelles.
- Ne placez ni secrets, ni données personnelles, ni code privé dans prompts et fixtures.
- Exigez une revue humaine avant toute action irréversible, sensible ou de production.

## Kit d'accompagnement

Le kit téléchargeable contient le guide, les exercices locaux, une fiche mémo et les diagrammes cités. La CI publie des artefacts PDF et ZIP déterministes.

| Élément | Objectif |
|---|---|
| `README.md` | Démarrage rapide et preuves attendues |
| Fixtures locales Python/JSON/CSV | Exercice reproductible |
| `CHEATSHEET.md` | Concepts, commandes et liste de vérification |
| PDF généré | Guide imprimable produit en CI |
| ZIP généré | Kit hors ligne produit en CI |

## Parcours réel facultatif

Remplacez uniquement l'adaptateur par un service hébergé approuvé. Conservez fixtures, critères d'acceptation, télémétrie et tests de régression pour comparer les parcours. Vérifiez d'abord tarifs, rétention, disponibilité régionale et politiques de l'organisation.

## Vérification des connaissances

??? question "Le taux d'acceptation prouve-t-il la productivité ?"

    ??? success "Réponse"
        Non. Il faut aussi le contexte de livraison et d'expérience.

??? question "Quelles preuves conserver ?"

    ??? success "Réponse"
        Commande, résultat, fichier modifié, hypothèses et brève explication de confiance.

??? question "Quand utiliser le parcours réel facultatif ?"

    ??? success "Réponse"
        Après réussite du contrat local et compréhension des coûts, politiques, données et nettoyage.

## Critères de sortie

- [ ] L'exercice local réussit sans identifiants.
- [ ] Les preuves et hypothèses sont consignées.
- [ ] Les fonctions payantes ou organisationnelles restent facultatives.
- [ ] Sécurité, accessibilité et comportements d'échec ont été vérifiés.
- [ ] Le kit peut être reproduit depuis les sources.

## Sources publiques

- [GitHub Copilot usage metrics REST API](https://docs.github.com/rest/copilot/copilot-usage-metrics)
- [DORA metrics](https://dora.dev/guides/dora-metrics-four-keys/)
- [SPACE framework](https://queue.acm.org/detail.cfm?id=3454124)
