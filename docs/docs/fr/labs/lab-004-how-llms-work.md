---
tags:
- llm
- tokens
- attention
- training
- hallucination
lab:
  id: '004'
  level: L50
  journey: llm-foundations
  time_min: 45
  cost:
    tier: free
    requires: []
    estimate_usd: 0 within the documented free path or simulation.
    simulation: true
    cleanup: false
  roles:
  - student
  - developer
  - architect
  technologies:
  - llm
  - tokens
  - attention
  - training
  - hallucination
  status: active
  last_verified: '2026-10-27'
  languages:
  - en
  - pt
  - fr
---
# Lab 004: Fonctionnement des LLM : tokens, attention, entraînement et hallucination

<div class="lab-meta">
  <span><strong>Niveau:</strong> <span class="level-badge level-50">L50</span></span>
  <span><strong>Parcours:</strong> llm-foundations</span>
  <span><strong>Durée:</strong> ~45 min</span>
  <span><strong>Coût:</strong> <span class="level-badge cost-free">Gratuit</span></span>
</div>

!!! info "Conception gratuite d'abord"
    Le parcours obligatoire est local, simulé ou compatible avec GitHub Copilot Free. Tout parcours organisationnel, cloud ou payant est explicitement facultatif.

!!! tip "Impact sur les AI Credits"
    Limitez la tâche, utilisez le plus petit contexte utile et validez localement. Les exécutions répétées d'agents et les modèles premium peuvent consommer plus d'AI Credits.

## Ce que vous apprendrez

- Suivre le texte de la tokenisation à la prédiction puis au décodage
- Expliquer préentraînement, réglage par instructions, alignement et évaluation
- Présenter l'attention comme un mécanisme de relations, pas une mémoire humaine
- Diagnostiquer l'hallucination comme un problème d'optimisation et de preuves

## Prérequis

- Python 3.10+ pour l'exercice local
- Un éditeur de texte et un terminal
- Lab 097

## Résultat et preuves

Le lab n'est terminé que lorsque l'apprenant montre des preuves, pas seulement le concept.

| Capacité | Preuve requise |
|---|---|
| Suivre le texte de la tokenisation à la prédiction puis au décodage | `evidence/step-1.txt` plus un contrôle local réussi |
| Expliquer préentraînement, réglage par instructions, alignement et évaluation | `evidence/step-2.txt` plus un contrôle local réussi |
| Présenter l'attention comme un mécanisme de relations, pas une mémoire humaine | `evidence/step-3.txt` plus un contrôle local réussi |
| Diagnostiquer l'hallucination comme un problème d'optimisation et de preuves | `evidence/step-4.txt` plus un contrôle local réussi |

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
  T[Text] --> K[Tokens]
  K --> A[Attention layers]
  A --> P[Next-token probabilities]
  P --> D[Decoder]
  D --> O[Output]
  E[Evidence and tools] --> A
```

## Scénario

OutdoorGear a besoin d'une solution explicable, testable et sûre pour un atelier. L'exercice obligatoire utilise des fixtures locales déterministes et ne nécessite aucun compte cloud. Un service réel pourra ensuite remplacer uniquement l'adaptateur.

## Exercice guidé

### Step 1

**Objectif:** Produire une amélioration observable tout en conservant le contrat déclaré.

**Action:** Exécutez `token_attention_lab.py` et comparez prose, code et JSON.

**Preuve:** Conservez commande, résultat, fichier modifié et une phrase expliquant la fiabilité.

**Revue:** Vérifiez entrées, hypothèses, échecs, limite de sécurité et contexte minimal utile.

### Step 2

**Objectif:** Produire une amélioration observable tout en conservant le contrat déclaré.

**Action:** Inspectez les probabilités et choisissez le token suivant par décodage glouton ou échantillonné.

**Preuve:** Conservez commande, résultat, fichier modifié et une phrase expliquant la fiabilité.

**Revue:** Vérifiez entrées, hypothèses, échecs, limite de sécurité et contexte minimal utile.

### Step 3

**Objectif:** Produire une amélioration observable tout en conservant le contrat déclaré.

**Action:** Reliez les tokens de requête aux preuves avec la table d'attention.

**Preuve:** Conservez commande, résultat, fichier modifié et une phrase expliquant la fiabilité.

**Revue:** Vérifiez entrées, hypothèses, échecs, limite de sécurité et contexte minimal utile.

### Step 4

**Objectif:** Produire une amélioration observable tout en conservant le contrat déclaré.

**Action:** Classez cinq réponses : fondée, non étayée, obsolète ou contradictoire.

**Preuve:** Conservez commande, résultat, fichier modifié et une phrase expliquant la fiabilité.

**Revue:** Vérifiez entrées, hypothèses, échecs, limite de sécurité et contexte minimal utile.

### Exécuter localement

```bash
cd docs/docs/fr/labs/lab-004
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

??? question "Pourquoi une réponse fluide peut-elle être fausse ?"

    ??? success "Réponse"
        La fluidité optimise la suite probable ; la vérité exige preuves et vérification.

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

- [The Illustrated Transformer](https://jalammar.github.io/illustrated-transformer/)
- [Attention Is All You Need](https://arxiv.org/abs/1706.03762)
