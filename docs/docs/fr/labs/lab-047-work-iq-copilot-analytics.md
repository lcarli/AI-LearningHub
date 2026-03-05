---
tags: [enterprise, work-iq, copilot-analytics, python, viva-insights, m365]
---
# Lab 047 : Work IQ — Analytique d'adoption de Copilot

<div class="lab-meta">
  <span><strong>Niveau :</strong> <span class="level-badge level-200">L200</span></span>
  <span><strong>Parcours :</strong> Tous les parcours</span>
  <span><strong>Durée :</strong> ~45 min</span>
  <span><strong>💰 Coût :</strong> <span class="level-badge cost-free">Gratuit</span> — Utilise un jeu de données simulé inclus (Viva Insights en production nécessite une licence M365 Copilot)</span>
</div>

## Ce que vous apprendrez

- Ce qu'est **Work IQ** et pourquoi l'analytique d'adoption est importante pour les déploiements IA
- Comment lire et interpréter les données d'utilisation de Copilot depuis Viva Insights et le Centre d'administration M365
- Analyser les taux d'adoption par département avec Python et pandas
- Identifier les **freins à l'adoption** : écarts de licences, écarts d'activation et faible engagement
- Construire un **tableau de bord d'adoption** qui transforme les données brutes en synthèse exécutive

## Introduction

![Flux d'analytique Work IQ](../../assets/diagrams/work-iq-analytics-flow.svg)

**Work IQ** est le framework de Microsoft pour mesurer et optimiser l'adoption de l'IA dans une organisation. À mesure que les entreprises passent du *déploiement* de Microsoft 365 Copilot à la *démonstration du ROI*, la capacité à analyser les données d'adoption devient une compétence essentielle.

En 2025-2026, la question est passée de _« Avons-nous déployé Copilot ? »_ à _« Est-il réellement utilisé ? Par qui ? Pour quoi ? Et quelle valeur crée-t-il ? »_

### Le scénario

Vous êtes le **responsable de l'adoption IA** chez OutdoorGear Inc. L'entreprise a déployé M365 Copilot auprès de 52 employés dans 7 départements il y a trois mois. La direction veut des réponses :

1. Quels départements utilisent réellement Copilot ?
2. Où les licences sont-elles inutilisées — et pourquoi ?
3. Quelles fonctionnalités les gens utilisent-ils le plus ?
4. Combien de temps Copilot a-t-il fait économiser à l'organisation ?

Vous disposez d'un **export de données d'utilisation** (similaire à ce que fournissent Viva Insights et le Centre d'administration M365). Votre mission : transformer les données brutes en un **tableau de bord d'adoption** exploitable.

!!! info "Données réelles vs. simulées"
    Ce lab utilise un **jeu de données simulé** (`copilot_usage_data.csv`) pour que tout le monde puisse suivre sans licence M365 Copilot. La structure des données reflète ce que vous verriez dans les exports Viva Insights. Si vous disposez d'un environnement M365 en production, vous pouvez substituer vos propres données.

## Prérequis

| Prérequis | Pourquoi |
|---|---|
| Python 3.10+ | Exécuter les scripts d'analyse |
| Bibliothèque `pandas` | Manipulation de données |
| (Optionnel) Licence M365 Copilot + Viva Insights | Pour des données réelles au lieu de simulées |

```bash
pip install pandas
```

---

!!! tip "Démarrage rapide avec GitHub Codespaces"
    [![Ouvrir dans GitHub Codespaces](https://github.com/codespaces/badge.svg)](https://codespaces.new/lcarli/AI-LearningHub?quickstart=1)

    Toutes les dépendances sont préinstallées dans le devcontainer.


## 📦 Fichiers d'accompagnement

!!! note "Téléchargez ces fichiers avant de commencer le lab"
    Enregistrez tous les fichiers dans un dossier `lab-047/` dans votre répertoire de travail.

| Fichier | Description | Télécharger |
|------|-------------|----------|
| `broken_scorecard.py` | Exercice de correction de bugs (3 bugs + auto-tests) | [📥 Télécharger](https://github.com/lcarli/AI-LearningHub/raw/main/docs/docs/en/labs/lab-047/broken_scorecard.py) |
| `copilot_usage_data.csv` | Jeu de données | [📥 Télécharger](https://github.com/lcarli/AI-LearningHub/raw/main/docs/docs/en/labs/lab-047/copilot_usage_data.csv) |
| `scorecard_builder.py` | Script de démarrage avec TODOs | [📥 Télécharger](https://github.com/lcarli/AI-LearningHub/raw/main/docs/docs/en/labs/lab-047/scorecard_builder.py) |

---

## Étape 1 : Comprendre les métriques clés

Avant de toucher aux données, vous devez comprendre ce que Work IQ mesure. Ce sont les mêmes métriques suivies par Viva Insights et le Centre d'administration M365 :

| Métrique | Ce qu'elle mesure | Pourquoi c'est important |
|--------|-----------------|----------------|
| **Licencié** | L'utilisateur a une licence M365 Copilot attribuée | Licence ≠ utilisation ; suit l'allocation de l'investissement |
| **Activé** | L'administrateur a activé Copilot pour l'utilisateur | L'écart entre licencié et activé = dépenses gaspillées |
| **Jours actifs** | Jours où l'utilisateur a interagi avec une fonctionnalité Copilot | Mesure la profondeur d'engagement, pas juste un essai ponctuel |
| **Réunions assistées** | Réunions où Copilot a généré des résumés/actions | Cas d'usage à forte valeur pour les managers |
| **E-mails rédigés** | E-mails composés ou affinés avec l'aide de Copilot | Mesure la productivité rédactionnelle |
| **Documents résumés** | Documents résumés ou analysés par Copilot | Mesure l'efficacité du travail de connaissance |
| **Chats** | Interactions Copilot Chat (questions, brainstorming) | Mesure l'exploration et l'utilité quotidienne |
| **Temps économisé (min)** | Minutes estimées économisées par Copilot | La métrique ROI ultime |

### Formules clés

```
Adoption Rate = (Active Users ÷ Enabled Users) × 100

Enablement Gap = Licensed Users − Enabled Users
    → Users with a paid license that admins haven't turned on

Licensing Gap = Total Users − Licensed Users
    → Users without any Copilot license at all
```

!!! warning "Confidentialité Viva Insights"
    En production, Viva Insights applique une **taille de groupe minimale de 5 utilisateurs** pour tous les rapports. Vous ne pouvez pas détailler les départements de moins de 5 personnes. Nos données simulées ignorent cela à des fins d'apprentissage, mais gardez-le à l'esprit pour les déploiements réels.

---

## Étape 2 : Charger et explorer le jeu de données

Le jeu de données contient **52 enregistrements utilisateurs** répartis dans 7 départements. Commencez par le charger en Python :

```python
import pandas as pd

df = pd.read_csv("lab-047/copilot_usage_data.csv")

# Convert string booleans to Python booleans
for col in ["licensed", "enabled"]:
    df[col] = df[col].astype(str).str.strip().str.lower() == "true"

print(f"Total records: {len(df)}")
print(f"Departments: {df['department'].nunique()}")
print(f"\nColumn types:\n{df.dtypes}")
print(f"\nFirst 5 rows:\n{df.head()}")
```

**Sortie attendue :**

```
Total records: 52
Departments: 7
```

Prenez un moment pour explorer :

```python
# Quick summary by department
summary = df.groupby("department").agg(
    total=("user_id", "count"),
    licensed=("licensed", "sum"),
    enabled=("enabled", "sum"),
).reset_index()
print(summary)
```

??? question "**🤔 Avant de continuer :** Quel département *prédisez-vous* aura le taux d'adoption le plus élevé ?"

    Réfléchissez-y — puis passez à l'étape 3 pour découvrir si vous aviez raison !

---

## Étape 3 : Calculer les taux d'adoption par département

Calculez maintenant le taux d'adoption pour chaque département. Rappel : **taux d'adoption = utilisateurs actifs ÷ utilisateurs activés × 100**.

Un utilisateur « actif » est toute personne avec `active_days > 0` (elle a utilisé Copilot au moins une fois pendant le mois).

```python
results = []
for dept, group in df.groupby("department"):
    total = len(group)
    licensed = group["licensed"].sum()
    enabled = group["enabled"].sum()
    active = len(group[(group["enabled"] == True) & (group["active_days"] > 0)])
    rate = (active / enabled * 100) if enabled > 0 else 0

    results.append({
        "Department": dept,
        "Total": total,
        "Licensed": licensed,
        "Enabled": enabled,
        "Active": active,
        "Adoption %": round(rate, 1),
    })

adoption_df = pd.DataFrame(results).sort_values("Adoption %", ascending=False)
print(adoption_df.to_string(index=False))
```

**Sortie attendue :**

| Department | Total | Licensed | Enabled | Active | Adoption % |
|------------|-------|----------|---------|--------|------------|
| Finance | 6 | 6 | 6 | 6 | 100.0 |
| Engineering | 12 | 11 | 10 | 9 | 90.0 |
| Marketing | 8 | 8 | 7 | 6 | 85.7 |
| Operations | 7 | 6 | 5 | 4 | 80.0 |
| Sales | 10 | 8 | 5 | 4 | 80.0 |
| HR | 5 | 3 | 3 | 2 | 66.7 |
| Legal | 4 | 3 | 2 | 1 | 50.0 |

!!! tip "Observation"
    **Finance est en tête à 100 %** — chaque utilisateur activé est actif. **Legal est à 50 %** — seul 1 utilisateur activé sur 2 a déjà ouvert Copilot. Mais notez que Legal a aussi le moins d'utilisateurs activés (2). Les petits échantillons peuvent être trompeurs — c'est pourquoi Viva Insights applique une taille de groupe minimale de 5.

---

## Étape 4 : Identifier les freins à l'adoption

Trois types de freins empêchent l'adoption de Copilot :

### 4a — Écart d'activation (Licencié mais NON activé)

```python
gap = df[(df["licensed"] == True) & (df["enabled"] == False)]
print(f"Enablement gap: {len(gap)} users\n")
print(gap[["department", "user_id"]].to_string(index=False))
```

**Sortie attendue :**

```
Enablement gap: 7 users

  department user_id
 Engineering ENG-011
   Marketing MKT-008
       Sales SLS-004
       Sales SLS-005
       Sales SLS-006
       Legal LEG-003
  Operations OPS-006
```

!!! warning "Le problème des ventes"
    **Sales a 3 utilisateurs licenciés bloqués dans l'écart d'activation** — soit 37,5 % de leurs utilisateurs licenciés ! Il s'agit probablement d'un oubli administratif. Un simple ticket IT pourrait débloquer 3 utilisateurs actifs supplémentaires.

### 4b — Écart de licences (Pas de licence du tout)

```python
unlicensed = df[df["licensed"] == False]
print(f"Unlicensed users: {len(unlicensed)}")
print(unlicensed.groupby("department")["user_id"].count())
```

### 4c — Utilisateurs à utilisation nulle (Activé mais jamais utilisé)

```python
zero_usage = df[(df["enabled"] == True) & (df["active_days"] == 0)]
print(f"Enabled but never used: {len(zero_usage)} users")
print(zero_usage[["department", "user_id"]].to_string(index=False))
```

Ces utilisateurs ont Copilot disponible mais ne l'ont jamais utilisé. Ils ont peut-être besoin de formation, de campagnes de sensibilisation ou d'un rappel de leur manager.

---

## Étape 5 : Analyse de l'utilisation des fonctionnalités

Quelles fonctionnalités de Copilot apportent le plus de valeur chez OutdoorGear ?

```python
active = df[df["active_days"] > 0]

features = {
    "Meetings Assisted": active["meetings_assisted"].sum(),
    "Emails Drafted": active["emails_drafted"].sum(),
    "Docs Summarized": active["docs_summarized"].sum(),
    "Chats": active["chats"].sum(),
}

print("Feature Usage (total interactions among active users):")
for feat, count in sorted(features.items(), key=lambda x: x[1], reverse=True):
    pct = count / sum(features.values()) * 100
    print(f"  {feat:>20s}: {count:>5d}  ({pct:.1f}%)")
```

**Sortie attendue :**

| Fonctionnalité | Total | Part |
|---------|-------|-------|
| Chats | 400 | 32,8 % |
| Meetings Assisted | 303 | 24,8 % |
| Emails Drafted | 260 | 21,3 % |
| Docs Summarized | 257 | 21,1 % |

!!! tip "Observation"
    **Les Chats dominent** à 32,8 % — les utilisateurs utilisent principalement Copilot pour les questions-réponses, le brainstorming et les recherches rapides. Les réunions sont la deuxième fonctionnalité la plus utilisée, portée par Finance et Engineering où les managers s'appuient sur les résumés de réunions.

---

## Étape 6 : Construire le tableau de bord

Combinez maintenant toute votre analyse en un seul **tableau de bord d'adoption** pour la direction :

```python
total_time = int(active["time_saved_min"].sum())

scorecard = f"""# 📊 OutdoorGear Inc. — Copilot Adoption Scorecard

**Reporting Period:** March 2026 (1-month snapshot)

## Overall Metrics
| Metric | Value |
|--------|-------|
| Total Users | {len(df)} |
| Licensed | {df['licensed'].sum()} |
| Enabled | {df['enabled'].sum()} |
| Active | {len(active)} |
| Overall Adoption Rate | {len(active) / df['enabled'].sum() * 100:.1f}% |
| Time Saved | {total_time} min ({total_time / 60:.1f} hours) |
| Enablement Gap | {len(gap)} users |

## Department Ranking
{adoption_df.to_markdown(index=False)}

## Top Actions
1. **Close the Sales enablement gap** — 3 licensed users not yet enabled
2. **Investigate Legal adoption** — only 1 of 2 enabled users is active
3. **Scale Finance's success** — 100% adoption; learn what they're doing right
4. **Run training for zero-usage users** — {len(zero_usage)} enabled users never opened Copilot
"""

print(scorecard)

with open("lab-047/scorecard_report.md", "w") as f:
    f.write(scorecard)
print("💾 Saved to lab-047/scorecard_report.md")
```

---

## 🐛 Exercice de correction de bugs

Le fichier `lab-047/broken_scorecard.py` contient **3 bugs** qui produisent des métriques d'adoption incorrectes. Pouvez-vous tous les trouver et les corriger ?

Exécutez les auto-tests pour voir lesquels échouent :

```bash
python lab-047/broken_scorecard.py
```

Vous devriez voir **3 tests échoués**. Chaque test correspond à un bug :

| Test | Ce qu'il vérifie | Indice |
|------|---------------|------|
| Test 1 | Dénominateur du taux d'adoption | Devrait utiliser les utilisateurs activés, pas le total |
| Test 2 | Logique de filtre de l'écart d'activation | Vérifiez les conditions booléennes |
| Test 3 | Facteur de conversion du temps | Conversion minutes → heures |

Corrigez les 3 bugs, puis relancez. Quand vous voyez `🎉 All 3 tests passed`, c'est terminé !

---


## 🧠 Quiz de connaissances

??? question "**Q1 (Choix multiple) :** Dans Microsoft Viva Insights, quelle est la taille de groupe minimale par défaut pour protéger la vie privée des employés ?"

    - A) 3 utilisateurs
    - B) 5 utilisateurs
    - C) 10 utilisateurs
    - D) 25 utilisateurs

    ??? success "✅ Révéler la réponse"
        **Correct : B) 5 utilisateurs**

        Viva Insights applique une taille de groupe minimale de **5** par défaut. Les rapports pour les groupes de moins de 5 personnes sont supprimés pour éviter l'identification des habitudes d'utilisation individuelles. Les administrateurs peuvent augmenter (mais pas diminuer) ce seuil.

??? question "**Q2 (Choix multiple) :** Quelle métrique indique le mieux que les utilisateurs utilisent Copilot de manière *régulière* dans le temps, plutôt que de simplement l'essayer une fois ?"

    - A) Total d'e-mails rédigés
    - B) Nombre d'utilisateurs licenciés
    - C) Moyenne mensuelle de jours actifs
    - D) Temps économisé en minutes

    ??? success "✅ Révéler la réponse"
        **Correct : C) Moyenne mensuelle de jours actifs**

        Un nombre élevé de jours actifs signifie que l'utilisateur revient sur Copilot jour après jour — cela mesure la **fidélisation** et la **formation d'habitudes**, pas juste un essai ponctuel. Le total d'e-mails ou le temps économisé peuvent être gonflés par une seule journée d'utilisation intensive.

??? question "**Q3 (Exécutez le lab) :** Quel département a le taux d'adoption Copilot le plus élevé (actifs ÷ activés × 100) ?"

    Exécutez l'analyse de l'étape 3 sur [📥 `copilot_usage_data.csv`](https://github.com/lcarli/AI-LearningHub/raw/main/docs/docs/en/labs/lab-047/copilot_usage_data.csv) et vérifiez les résultats.

    ??? success "✅ Révéler la réponse"
        **Finance — 100,0 %**

        Finance a 6 utilisateurs licenciés, 6 activés et 6 actifs — chaque utilisateur activé utilise activement Copilot. Cela fait de Finance le département modèle pour diffuser les bonnes pratiques d'adoption aux autres équipes.

??? question "**Q4 (Exécutez le lab) :** Combien d'utilisateurs dans l'organisation se trouvent dans l'« écart d'activation » (licensed = true, enabled = false) ?"

    Exécutez l'analyse de l'étape 4a pour le découvrir.

    ??? success "✅ Révéler la réponse"
        **7 utilisateurs**

        Les 7 utilisateurs dans l'écart d'activation sont : ENG-011, MKT-008, SLS-004, SLS-005, SLS-006, LEG-003 et OPS-006. Sales représente à lui seul 3 d'entre eux — le moyen le plus rapide d'améliorer l'adoption globale est d'activer ces utilisateurs.

??? question "**Q5 (Exécutez le lab) :** Combien y a-t-il de « power users » (employés avec `active_days >= 20`) ?"

    Filtrez le jeu de données pour les utilisateurs avec 20+ jours actifs et comptez-les.

    ??? success "✅ Révéler la réponse"
        **10 power users**

        - Engineering : ENG-001 (22), ENG-002 (20), ENG-004 (21), ENG-007 (23), ENG-009 (20) → 5
        - Marketing : MKT-003 (20) → 1
        - Finance : FIN-001 (22), FIN-002 (21), FIN-003 (20), FIN-005 (23) → 4
        - **Total : 10 power users** répartis entre Engineering, Marketing et Finance

---

## Résumé

| Sujet | Ce que vous avez appris |
|-------|-----------------|
| Work IQ | Framework pour mesurer l'adoption de l'IA et démontrer le ROI |
| Taux d'adoption | actifs ÷ activés × 100 — la métrique de santé principale |
| Écart d'activation | Licencié mais non activé — la correction la plus rapide pour une faible adoption |
| Mix de fonctionnalités | Quelles fonctionnalités Copilot apportent le plus de valeur |
| Temps économisé | Convertir les minutes en impact business pour la direction |
| Tableau de bord | Combiner les métriques en un rapport prêt pour la direction |

---

## Prochaines étapes

- **[Lab 048](lab-048-work-iq-power-bi.md)** *(à venir)* — Construire des tableaux de bord Power BI avancés avec Viva Insights Advanced Reporting
- **[Lab 033](lab-033-agent-observability.md)** — Observabilité des agents avec Application Insights (même approche analytique pour les agents personnalisés)
- **[Lab 035](lab-035-agent-evaluation.md)** — Évaluation des agents avec le SDK Azure AI Eval (mesurer la qualité des agents, pas seulement l'adoption)
- **[Lab 038](lab-038-cost-optimization.md)** — Optimisation des coûts IA (le volet financier du ROI)
