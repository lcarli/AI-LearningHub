---
tags: [ux, adaptive-cards, teams, proactive, accessibility, python]
---
# Lab 070 : Patterns UX des agents — Chat, Adaptive Cards et notifications proactives

<div class="lab-meta">
  <span><strong>Niveau :</strong> <span class="level-badge level-100">L100</span></span>
  <span><strong>Parcours :</strong> Tous les parcours</span>
  <span><strong>Durée :</strong> ~60 min</span>
  <span><strong>💰 Coût :</strong> <span class="level-badge cost-free">Gratuit</span> — Données d'interaction simulées (ni Teams ni Azure Bot Service requis)</span>
</div>

## Ce que vous apprendrez

- Les **patterns UX** essentiels pour les interactions d'agents IA en environnement d'entreprise
- Concevoir des **interfaces de chat** efficaces avec des indicateurs de saisie et des citations de sources
- Construire des **Adaptive Cards** pour l'affichage de données structurées et la saisie utilisateur
- Implémenter des patterns de **notifications proactives** pour les messages initiés par l'agent
- Appliquer les bonnes pratiques d'**accessibilité** à l'UX des agents
- Mesurer la qualité UX à l'aide de métriques de **satisfaction utilisateur**

!!! abstract "Prérequis"
    Une familiarité avec les concepts de **chatbot** est recommandée. Aucune expérience en développement front-end n'est requise — ce lab analyse les patterns UX à l'aide de données d'interaction simulées.

## Introduction

L'intelligence d'un agent IA n'est efficace que dans la mesure de son **expérience utilisateur**. Une mauvaise UX — indicateurs de saisie manquants, pas de citations de sources, Adaptive Cards inaccessibles — érode la confiance et l'adoption des utilisateurs. Une excellente UX d'agent suit des patterns établis :

| Pattern UX | Objectif | Impact |
|-----------|---------|--------|
| **Indicateur de saisie** | Montre que l'agent traite la demande | Réduit la latence perçue |
| **Citation de source** | Lie les réponses aux documents sources | Renforce la confiance et la vérifiabilité |
| **Adaptive Cards** | Affichage structuré avec actions | Permet des interactions riches |
| **Notifications proactives** | Messages initiés par l'agent | Tient les utilisateurs informés |
| **Messages d'erreur** | États d'erreur clairs et exploitables | Réduit la frustration |
| **Accessibilité** | Support des lecteurs d'écran, navigation clavier | Garantit un accès inclusif |

### Le scénario

Vous êtes un **Designer UX** auditant les patterns d'interaction d'un agent d'entreprise. Vous disposez de données sur **12 patterns UX** utilisés dans l'organisation, incluant les scores de satisfaction, l'état d'implémentation et la conformité en matière d'accessibilité. Votre mission : identifier les patterns à fort impact, trouver les lacunes et recommander des améliorations.

---

## Prérequis

| Exigence | Raison |
|---|---|
| Python 3.10+ | Exécuter les scripts d'analyse |
| `pandas` | Analyser les données des patterns UX |

```bash
pip install pandas
```

---

!!! tip "Démarrage rapide avec GitHub Codespaces"
    [![Open in GitHub Codespaces](https://github.com/codespaces/badge.svg)](https://codespaces.new/lcarli/AI-LearningHub?quickstart=1)

    Toutes les dépendances sont pré-installées dans le devcontainer.


## 📦 Fichiers de support

!!! note "Téléchargez ces fichiers avant de commencer le lab"
    Enregistrez tous les fichiers dans un dossier `lab-070/` de votre répertoire de travail.

| Fichier | Description | Téléchargement |
|------|-------------|----------|
| `broken_ux.py` | Exercice de correction de bugs (3 bugs + auto-tests) | [📥 Télécharger](https://github.com/lcarli/AI-LearningHub/raw/main/docs/docs/en/labs/lab-070/broken_ux.py) |
| `ux_patterns.csv` | Jeu de données | [📥 Télécharger](https://github.com/lcarli/AI-LearningHub/raw/main/docs/docs/en/labs/lab-070/ux_patterns.csv) |

---

## Étape 1 : Comprendre les principes UX des agents

Une UX d'agent efficace suit une approche en couches :

```
User Input → [Typing Indicator] → Agent Processing → [Response Formatting]
                                                            ↓
                                                   ┌── Plain Text Chat
                                                   ├── Adaptive Card
                                                   ├── Source Citation
                                                   └── Error Message
                                                            ↓
                                              [Accessibility Check] → User
```

Principes clés :

1. **Réactivité** — Toujours accuser réception de la saisie utilisateur immédiatement (indicateurs de saisie)
2. **Transparence** — Citer les sources et expliquer les niveaux de confiance
3. **Structure** — Utiliser les Adaptive Cards pour les données complexes, le texte brut pour les réponses simples
4. **Proactivité** — Notifier les utilisateurs d'événements importants sans nécessiter de prompt
5. **Accessibilité** — Assurer que toutes les interactions fonctionnent avec les lecteurs d'écran et la navigation clavier

!!! info "Pourquoi l'UX est importante pour l'adoption des agents"
    Les recherches montrent que les agents avec des patterns UX appropriés (citations de sources, indicateurs de saisie, erreurs claires) ont un taux de rétention des utilisateurs 2 à 3 fois supérieur aux agents avec de simples réponses textuelles. Les utilisateurs font davantage confiance aux agents lorsqu'ils peuvent vérifier les réponses et comprendre l'état de l'agent.

---

## Étape 2 : Charger et explorer les patterns UX

Le jeu de données contient **12 patterns UX** avec des scores de satisfaction et des données d'implémentation :

```python
import pandas as pd

patterns = pd.read_csv("lab-070/ux_patterns.csv")
print(f"Total patterns: {len(patterns)}")
print(f"Categories: {sorted(patterns['category'].unique())}")
print(f"\nAll patterns:")
print(patterns[["pattern_id", "pattern_name", "category", "satisfaction_score"]]
      .to_string(index=False))
```

**Attendu :**

```
Total patterns: 12
```

---

## Étape 3 : Analyse de la satisfaction

Identifiez les patterns avec la satisfaction la plus élevée et la plus basse :

```python
print("Patterns ranked by satisfaction score:")
ranked = patterns.sort_values("satisfaction_score", ascending=False)
print(ranked[["pattern_name", "category", "satisfaction_score"]].to_string(index=False))

highest = patterns.loc[patterns["satisfaction_score"].idxmax()]
print(f"\nHighest satisfaction: {highest['pattern_name']} ({highest['satisfaction_score']})")
print(f"Average satisfaction: {patterns['satisfaction_score'].mean():.2f}")
```

**Attendu :**

```
Highest satisfaction: Source Citation (4.8)
Average satisfaction: 4.17
```

!!! tip "Les citations de sources gagnent"
    La Citation de source a le score de satisfaction le plus élevé (4.8 sur 5.0). Les utilisateurs préfèrent fortement les agents qui lient les réponses à des sources vérifiables — cela renforce la confiance et permet aux utilisateurs d'approfondir. Ce pattern devrait être implémenté dans chaque agent d'entreprise.

---

## Étape 4 : Analyse par catégorie

Analysez les patterns par catégorie :

```python
print("Average satisfaction by category:")
cat_stats = patterns.groupby("category").agg(
    count=("pattern_id", "count"),
    avg_satisfaction=("satisfaction_score", "mean")
).sort_values("avg_satisfaction", ascending=False)
print(cat_stats.to_string())
```

Les catégories regroupent les patterns connexes (par ex. les patterns de « confiance » comme les citations de sources et les indicateurs de confiance, les patterns de « réactivité » comme les indicateurs de saisie et le streaming).

---

## Étape 5 : Vérification de la conformité en accessibilité

Vérifiez quels patterns respectent les normes d'accessibilité :

```python
accessible = patterns[patterns["accessible"] == True]
not_accessible = patterns[patterns["accessible"] == False]
print(f"Accessible patterns: {len(accessible)} / {len(patterns)}")
print(f"Non-accessible patterns: {len(not_accessible)}")

if len(not_accessible) > 0:
    print(f"\nPatterns needing accessibility fixes:")
    print(not_accessible[["pattern_name", "category", "satisfaction_score"]].to_string(index=False))
```

!!! warning "Lacunes en accessibilité"
    Tout pattern non accessible est un risque de conformité et exclut les utilisateurs qui dépendent des technologies d'assistance. Les Adaptive Cards doivent inclure `altText` pour les images, `label` pour les champs de saisie et les propriétés `speak` appropriées pour les lecteurs d'écran.

---

## Étape 6 : Tableau de bord de la qualité UX

Construisez un rapport complet de qualité UX :

```python
total = len(patterns)
avg_sat = patterns["satisfaction_score"].mean()
highest_name = patterns.loc[patterns["satisfaction_score"].idxmax(), "pattern_name"]
highest_score = patterns["satisfaction_score"].max()
accessible_count = (patterns["accessible"] == True).sum()

dashboard = f"""
╔════════════════════════════════════════════════════════╗
║     Agent UX Patterns — Quality Report                 ║
╠════════════════════════════════════════════════════════╣
║ Total Patterns:              {total:>5}                     ║
║ Average Satisfaction:        {avg_sat:>5.2f}                     ║
║ Highest Satisfaction:  {highest_name:>12} ({highest_score})           ║
║ Accessible Patterns:         {accessible_count:>5} / {total}                ║
║ Categories:                  {patterns['category'].nunique():>5}                     ║
╚════════════════════════════════════════════════════════╝
"""
print(dashboard)
```

---

## 🐛 Exercice de correction de bugs

Le fichier `lab-070/broken_ux.py` contient **3 bugs** dans la façon dont il analyse les données des patterns UX :

```bash
python lab-070/broken_ux.py
```

| Test | Ce qu'il vérifie | Indice |
|------|---------------|------|
| Test 1 | Nombre de patterns | Devrait compter toutes les lignes avec `len()`, pas les catégories uniques |
| Test 2 | Pattern avec la satisfaction la plus élevée | Devrait utiliser `idxmax()`, pas `idxmin()` |
| Test 3 | Satisfaction moyenne | Devrait utiliser `mean()`, pas `median()` |

---


## 🧠 Vérification des connaissances

??? question "**Q1 (Choix multiple) :** Pourquoi les indicateurs de saisie sont-ils importants pour l'UX des agents IA ?"

    - A) Ils rendent l'agent plus intelligent
    - B) Ils réduisent la latence perçue et signalent que l'agent traite activement la requête
    - C) Ils sont requis par Microsoft Teams
    - D) Ils améliorent la précision des réponses de l'agent

    ??? success "✅ Révéler la réponse"
        **Correct : B) Ils réduisent la latence perçue et signalent que l'agent traite activement la requête**

        Les indicateurs de saisie fournissent un retour visuel immédiat indiquant que l'agent a reçu le message de l'utilisateur et travaille sur une réponse. Sans eux, les utilisateurs peuvent penser que l'agent est en panne ou ne répond pas, surtout lors de temps de traitement plus longs. Ce pattern simple améliore significativement la réactivité perçue et la confiance des utilisateurs.

??? question "**Q2 (Choix multiple) :** Quel est le principal avantage des Adaptive Cards par rapport aux réponses en texte brut ?"

    - A) Elles sont plus rapides à afficher
    - B) Elles permettent un affichage de données structurées avec des éléments interactifs comme des boutons, des champs de saisie et des mises en page formatées
    - C) Elles fonctionnent sans internet
    - D) Elles sont plus simples à implémenter

    ??? success "✅ Révéler la réponse"
        **Correct : B) Elles permettent un affichage de données structurées avec des éléments interactifs comme des boutons, des champs de saisie et des mises en page formatées**

        Les Adaptive Cards transforment les réponses des agents du texte brut en expériences riches et interactives. Elles peuvent afficher des tableaux, des images, des boutons d'action, des formulaires de saisie et du texte formaté — permettant aux utilisateurs d'interagir directement avec les données plutôt que de taper des requêtes de suivi. Elles sont particulièrement efficaces pour les workflows d'approbation, les résumés de données et les processus en plusieurs étapes.

??? question "**Q3 (Exécutez le lab) :** Quel pattern UX a le score de satisfaction utilisateur le plus élevé ?"

    Triez les patterns par `satisfaction_score` en ordre décroissant et vérifiez la première entrée.

    ??? success "✅ Révéler la réponse"
        **Citation de source avec un score de satisfaction de 4.8**

        La Citation de source est le pattern UX le mieux noté (4.8 sur 5.0). Les utilisateurs préfèrent fortement les agents qui lient les réponses à des documents sources vérifiables, car cela renforce la confiance et leur permet de vérifier les informations. Ce pattern devrait être un standard dans chaque agent d'entreprise.

??? question "**Q4 (Exécutez le lab) :** Quel est le score de satisfaction moyen de tous les patterns ?"

    Calculez `patterns['satisfaction_score'].mean()`.

    ??? success "✅ Révéler la réponse"
        **4.17 de satisfaction moyenne**

        Le score de satisfaction moyen pour les 12 patterns UX est de 4.17 sur 5.0, indiquant une réception généralement positive par les utilisateurs. Cependant, l'écart entre le score le plus élevé (4.8) et les scores les plus bas suggère que certains patterns nécessitent des améliorations pour atteindre la qualité des meilleurs.

??? question "**Q5 (Exécutez le lab) :** Combien de patterns UX contient le jeu de données ?"

    Vérifiez `len(patterns)`.

    ??? success "✅ Révéler la réponse"
        **12 patterns**

        Le jeu de données contient 12 patterns UX couvrant des catégories comme la confiance (citations de sources, indicateurs de confiance), la réactivité (indicateurs de saisie, streaming), la structure (Adaptive Cards, carrousels), la proactivité (notifications, suggestions) et l'accessibilité (support lecteur d'écran, navigation clavier).

---

## Résumé

| Sujet | Ce que vous avez appris |
|-------|-----------------|
| UX Chat | Concevoir un chat réactif avec indicateurs de saisie et streaming |
| Citations de sources | Renforcer la confiance en liant les réponses à des sources vérifiables |
| Adaptive Cards | Afficher des données structurées avec des éléments interactifs |
| Notifications proactives | Permettre les messages initiés par l'agent pour des mises à jour opportunes |
| Accessibilité | Assurer une UX inclusive avec le support des lecteurs d'écran et du clavier |
| Métriques de satisfaction | Mesurer et comparer l'efficacité des patterns UX |

---

## Prochaines étapes

- **[Lab 069](lab-069-declarative-agents.md)** — Agents déclaratifs (configurer le comportement d'un agent via des manifestes)
- **[Lab 066](lab-066-copilot-studio-governance.md)** — Gouvernance Copilot Studio (gouverner les déploiements d'agents)
- **[Lab 008](lab-008-responsible-ai.md)** — IA responsable (principes fondamentaux d'UX et de sécurité)