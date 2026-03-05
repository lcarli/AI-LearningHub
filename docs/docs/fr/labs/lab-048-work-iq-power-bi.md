---
tags: [enterprise, work-iq, copilot-analytics, python, power-bi, viva-insights, roi]
---
# Lab 048 : Work IQ — Analytique d'impact Copilot & Power BI

<div class="lab-meta">
  <span><strong>Niveau :</strong> <span class="level-badge level-300">L300</span></span>
  <span><strong>Parcours :</strong> Tous les parcours</span>
  <span><strong>Durée :</strong> ~90 min</span>
  <span><strong>💰 Coût :</strong> <span class="level-badge cost-free">Gratuit</span> — Utilise des jeux de données simulés inclus (Viva Insights en production nécessite une licence M365 Copilot)</span>
</div>

## Ce que vous apprendrez

- Comment fonctionne l'**attribution d'impact** — relier l'utilisation de Copilot aux résultats business
- Calculer la **valeur monétaire du temps économisé** (ROI) à partir des données d'adoption de Copilot
- Utiliser la **corrélation de Pearson** pour mesurer la relation entre utilisation et KPI
- Analyser les **tendances d'adoption mois par mois** pour identifier les schémas de croissance
- Rédiger un **récit d'impact exécutif** qui raconte une histoire fondée sur les données
- Comprendre comment ces analyses correspondent aux tableaux de bord **Power BI** et à Viva Insights Advanced Reporting

!!! abstract "Prérequis"
    Complétez d'abord le **[Lab 047 : Work IQ — Analytique d'adoption de Copilot](lab-047-work-iq-copilot-analytics.md)**. Ce lab s'appuie sur les concepts d'analyse d'adoption et le scénario OutdoorGear Inc. du Lab 047.

## Introduction

![Modèle d'attribution d'impact](../../assets/diagrams/impact-attribution-model.svg)

Dans le Lab 047, vous avez répondu à _« Qui utilise Copilot ? »_. Maintenant, les dirigeants veulent une réponse à la question plus difficile : _« Quelle valeur Copilot crée-t-il ? »_

L'**attribution d'impact** relie l'utilisation des outils IA aux résultats business concrets — croissance du chiffre d'affaires, temps de réponse plus rapides, satisfaction des employés et livraison des projets. C'est l'analyse qui sécurise la poursuite de l'investissement IA.

### Le scénario

Trois mois se sont écoulés depuis le déploiement de M365 Copilot chez OutdoorGear Inc. Vous disposez maintenant de :

1. **Données d'utilisation Copilot** — 3 mois de métriques agrégées par département (utilisateurs actifs, utilisation des fonctionnalités, temps économisé)
2. **KPI de résultats business** — variation du chiffre d'affaires, taux de résolution des tickets, temps de réponse, scores de satisfaction, livraison des projets

Votre mission : **prouver (ou réfuter) que Copilot génère une amélioration business mesurable** — et présenter vos résultats au conseil d'administration.

!!! warning "Corrélation ≠ Causalité"
    Ce lab vous apprend à trouver des **corrélations** entre utilisation et résultats. La corrélation ne PROUVE PAS que Copilot a *causé* l'amélioration — d'autres facteurs (nouvelles embauches, changements de processus, saisonnalité) pourraient y contribuer. Présentez toujours vos résultats comme « les départements avec une utilisation plus élevée de Copilot *tendent à* montrer de meilleurs résultats » plutôt que « Copilot a *causé* l'amélioration ».

---

## 📦 Fichiers d'accompagnement

!!! note "Téléchargez ces fichiers avant de commencer le lab"
    Enregistrez tous les fichiers dans un dossier `lab-048/` dans votre répertoire de travail.

| Fichier | Description | Télécharger |
|------|-------------|----------|
| `broken_roi_calculator.py` | Exercice de correction de bugs (3 bugs + auto-tests) | [📥 Télécharger](https://github.com/lcarli/AI-LearningHub/raw/main/docs/docs/en/labs/lab-048/broken_roi_calculator.py) |
| `business_outcomes.csv` | Jeu de données | [📥 Télécharger](https://github.com/lcarli/AI-LearningHub/raw/main/docs/docs/en/labs/lab-048/business_outcomes.csv) |
| `copilot_quarterly_summary.csv` | Jeu de données | [📥 Télécharger](https://github.com/lcarli/AI-LearningHub/raw/main/docs/docs/en/labs/lab-048/copilot_quarterly_summary.csv) |
| `impact_analyzer.py` | Script de démarrage avec TODOs | [📥 Télécharger](https://github.com/lcarli/AI-LearningHub/raw/main/docs/docs/en/labs/lab-048/impact_analyzer.py) |

---

## Étape 1 : Comprendre l'analytique d'impact

Avant de coder, comprenez les trois piliers de l'analytique d'impact :

| Pilier | Ce qu'il mesure | Exemple |
|--------|-----------------|---------|
| **ROI (Retour sur investissement)** | Valeur monétaire du temps économisé vs. coût des licences | 188 heures économisées × 50 $/h = 9 400 $ |
| **Corrélation** | Relation statistique entre utilisation et résultats | r = 0,97 entre jours actifs et satisfaction |
| **Analyse de tendances** | Comment l'adoption et les résultats évoluent dans le temps | 60 % de croissance des utilisateurs actifs sur 3 mois |

### Viva Insights Advanced Reporting

Dans un environnement M365 en production, Viva Insights Advanced Reporting vous offre :

- **Plus de 100 métriques Copilot** découpées par département, rôle, manager et localisation
- **Import de données organisationnelles** pour ajouter des attributs personnalisés (centre de coûts, date d'embauche, etc.)
- **Contrôles de confidentialité** : taille de groupe minimale de 5, agrégation des données, accès basé sur les rôles
- **Modèles Power BI** pour des tableaux de bord préconstruits

Dans ce lab, nous simulons ces capacités avec Python et des exports CSV.

!!! tip "Connexion Power BI"
    Si vous avez Power BI Desktop installé, vous pouvez charger les deux CSV directement dans Power BI pour créer des tableaux de bord interactifs. Toute l'analyse que nous faisons en Python correspond 1:1 aux visuels Power BI : tables → matrice, corrélations → nuages de points, tendances → graphiques en courbes.

---

## Étape 2 : Charger et fusionner les jeux de données

Vous avez deux jeux de données à utiliser :

**[📥 `copilot_quarterly_summary.csv`](https://github.com/lcarli/AI-LearningHub/raw/main/docs/docs/en/labs/lab-048/copilot_quarterly_summary.csv)** — Données d'utilisation agrégées (21 lignes : 7 départements × 3 mois)

| Colonne | Description |
|--------|-------------|
| `department` | Nom du département |
| `month` | Mois (2026-01, 2026-02, 2026-03) |
| `licensed` / `enabled` / `active_users` | Nombre d'utilisateurs |
| `avg_active_days` | Moyenne de jours actifs parmi les utilisateurs actifs |
| `total_meetings` / `total_emails` / `total_docs` / `total_chats` | Totaux par fonctionnalité |
| `total_time_saved_min` | Minutes estimées économisées |

**[📥 `business_outcomes.csv`](https://github.com/lcarli/AI-LearningHub/raw/main/docs/docs/en/labs/lab-048/business_outcomes.csv)** — KPI départementaux (21 lignes : 7 départements × 3 mois)

| Colonne | Description |
|--------|-------------|
| `revenue_change_pct` | Variation du chiffre d'affaires vs. année précédente (%) |
| `tickets_resolved_per_person` | Tickets de support résolus par personne |
| `avg_response_hours` | Temps de réponse moyen (heures) |
| `employee_satisfaction` | Score de satisfaction (0-100) |
| `projects_on_time_pct` | Projets livrés dans les délais (%) |

Chargez-les et fusionnez-les :

```python
import pandas as pd

usage = pd.read_csv("lab-048/copilot_quarterly_summary.csv")
outcomes = pd.read_csv("lab-048/business_outcomes.csv")

# Merge on department + month
merged = pd.merge(usage, outcomes, on=["department", "month"])
print(f"Merged: {len(merged)} rows × {len(merged.columns)} columns")
print(merged.head())
```

**Attendu :** 21 lignes × 17 colonnes.

---

## Étape 3 : Calculer le ROI — Valeur monétaire du temps économisé

La métrique ROI la plus simple : **combien vaut le temps économisé ?**

```python
HOURLY_RATE = 50  # Average fully-loaded cost per employee-hour

total_minutes = usage["total_time_saved_min"].sum()
total_hours = total_minutes / 60
dollar_value = total_hours * HOURLY_RATE

print(f"Total time saved: {total_minutes:,} minutes")
print(f"                = {total_hours:.1f} hours")
print(f"Dollar value:    = ${dollar_value:,.0f} (at ${HOURLY_RATE}/hr)")
```

**Sortie attendue :**

```
Total time saved: 11,280 minutes
                = 188.0 hours
Dollar value:    = $9,400 (at $50/hr)
```

### Ventilation du ROI par département

```python
dept_roi = usage.groupby("department")["total_time_saved_min"].sum().reset_index()
dept_roi["hours"] = dept_roi["total_time_saved_min"] / 60
dept_roi["dollar_value"] = dept_roi["hours"] * HOURLY_RATE
dept_roi = dept_roi.sort_values("dollar_value", ascending=False)
print(dept_roi[["department", "hours", "dollar_value"]].to_string(index=False))
```

**Sortie attendue :**

| Département | Heures | Valeur monétaire |
|------------|-------|-------------|
| Engineering | 65,2 | 3 262 $ |
| Finance | 45,9 | 2 296 $ |
| Marketing | 34,3 | 1 713 $ |
| Operations | 19,6 | 979 $ |
| Sales | 15,5 | 775 $ |
| HR | 6,4 | 321 $ |
| Legal | 1,1 | 54 $ |

!!! tip "Observation"
    Engineering génère le plus de valeur absolue (3 262 $) car il a le plus d'utilisateurs. Mais **Finance a le ROI par utilisateur le plus élevé** — 6 utilisateurs générant 2 296 $ contre 12 utilisateurs chez Engineering générant 3 262 $. La valeur par utilisateur de Finance est de **383 $** contre **272 $** pour Engineering.

---

## Étape 4 : Corréler l'utilisation avec les résultats business

Maintenant la question cruciale : **une utilisation plus élevée de Copilot est-elle corrélée à de meilleurs résultats business ?**

```python
# Pearson correlation between average active days and employee satisfaction
correlation = merged["avg_active_days"].corr(merged["employee_satisfaction"])
print(f"Correlation (active_days ↔ satisfaction): {correlation:.3f}")
```

**Sortie attendue :**

```
Correlation (active_days ↔ satisfaction): 0.970
```

Une corrélation de **0,970** est extrêmement forte. Les départements avec une moyenne de jours actifs plus élevée montrent systématiquement une satisfaction des employés plus élevée.

### Matrice de corrélation

Vérifiez plusieurs métriques de résultats en une fois :

```python
usage_cols = ["avg_active_days", "active_users"]
outcome_cols = ["employee_satisfaction", "revenue_change_pct",
                "projects_on_time_pct", "avg_response_hours"]

corr_matrix = merged[usage_cols + outcome_cols].corr()
print("\nCorrelation with avg_active_days:")
for col in outcome_cols:
    r = corr_matrix.loc["avg_active_days", col]
    direction = "↑ positive" if r > 0 else "↓ negative"
    print(f"  {col:>30s}: r = {r:+.3f}  ({direction})")
```

Vous devriez voir :

- **employee_satisfaction** : forte positive (~0,97)
- **revenue_change_pct** : forte positive
- **projects_on_time_pct** : forte positive
- **avg_response_hours** : forte **négative** (utilisation plus élevée → temps de réponse *plus bas* = plus rapide)

!!! warning "Rappel : Corrélation ≠ Causalité"
    Une corrélation de 0,97 est impressionnante, mais elle ne prouve pas que Copilot a *causé* l'augmentation de la satisfaction. Les départements performants ont peut-être adopté Copilot plus rapidement *parce qu'ils* sont déjà efficaces. Présentez cela comme une preuve d'une **relation**, pas comme une preuve de causalité.

---

## Étape 5 : Analyse de tendances — Croissance mois par mois

Suivez comment l'adoption progresse dans le temps :

```python
monthly = usage.groupby("month")["active_users"].sum().reset_index()
monthly.columns = ["Month", "Active Users"]
print(monthly.to_string(index=False))

jan = monthly[monthly["Month"] == "2026-01"]["Active Users"].values[0]
mar = monthly[monthly["Month"] == "2026-03"]["Active Users"].values[0]
growth = (mar - jan) / jan * 100
print(f"\nGrowth (Jan → Mar): {jan} → {mar} = {growth:.1f}%")
```

**Sortie attendue :**

```
   Month  Active Users
 2026-01            20
 2026-02            28
 2026-03            32

Growth (Jan → Mar): 20 → 32 = 60.0%
```

### Tendances au niveau départemental

```python
print("\nDepartment-level growth (Jan → Mar):")
for dept in usage["department"].unique():
    d = usage[usage["department"] == dept]
    j = d[d["month"] == "2026-01"]["active_users"].values[0]
    m = d[d["month"] == "2026-03"]["active_users"].values[0]
    g = ((m - j) / j * 100) if j > 0 else float("inf")
    arrow = "📈" if g > 50 else "📊" if g > 0 else "⚠️"
    print(f"  {arrow} {dept}: {j} → {m} ({g:+.0f}%)")
```

### Amélioration de la satisfaction par département

```python
print("\nSatisfaction improvement (Jan → Mar):")
for dept in outcomes["department"].unique():
    d = outcomes[outcomes["department"] == dept]
    j = d[d["month"] == "2026-01"]["employee_satisfaction"].values[0]
    m = d[d["month"] == "2026-03"]["employee_satisfaction"].values[0]
    delta = m - j
    print(f"  {dept:>15s}: {j} → {m}  (Δ = {delta:+d})")
```

**Sortie attendue :**

| Département | Jan | Mar | Δ |
|------------|-----|-----|---|
| Finance | 75 | 88 | **+13** ← le plus élevé |
| Engineering | 72 | 84 | +12 |
| Marketing | 70 | 80 | +10 |
| Operations | 68 | 76 | +8 |
| HR | 62 | 68 | +6 |
| Sales | 65 | 70 | +5 |
| Legal | 58 | 62 | +4 ← le plus faible |

!!! tip "L'histoire s'écrit d'elle-même"
    **Finance** (adoption Copilot la plus élevée à 100 %) montre la **plus grande amélioration de satisfaction (+13)**. **Legal** (adoption la plus faible à 50 %) montre la **plus petite amélioration (+4)**. C'est l'histoire de corrélation que vous présenterez au conseil d'administration.

---

## Étape 6 : Construire le récit d'impact

Combinez tous les résultats en un document prêt pour la direction :

```python
narrative = f"""# 📋 OutdoorGear Inc. — Copilot Impact Report
## Q1 2026 (January – March)

### Executive Summary

Over Q1 2026, Microsoft 365 Copilot adoption at OutdoorGear Inc. grew
**{growth:.0f}%** (from {jan} to {mar} active users). The estimated value of
time saved is **${dollar_value:,.0f}** ({total_hours:.0f} hours at $50/hr).

There is a **strong positive correlation (r = {correlation:.2f})** between
Copilot usage intensity and employee satisfaction — departments with higher
average active days consistently report higher satisfaction scores.

### Key Metrics

| Metric | Value |
|--------|-------|
| Active Users (March) | {mar} of 52 employees |
| Adoption Growth (Q1) | {growth:.0f}% |
| Total Time Saved | {total_hours:.0f} hours |
| Estimated ROI | ${dollar_value:,.0f} |
| Usage ↔ Satisfaction Correlation | r = {correlation:.2f} |

### Department Spotlight: Finance 🏆

Finance achieved **100% adoption** with all 6 employees actively using Copilot
an average of 20.5 days/month. They show the **largest satisfaction improvement
(+13 points)** and the **highest per-user ROI ($383/user)**.

### Top 3 Recommendations

1. **Enable the 7 users in the licensing gap** — Sales has 3 licensed users
   not yet enabled. This is the fastest path to increasing adoption.
2. **Replicate Finance's playbook** — interview the Finance team to understand
   what drove their 100% adoption and apply those practices org-wide.
3. **Targeted training for Legal and HR** — lowest adoption departments
   need hands-on enablement sessions, not just license assignment.
"""

print(narrative)

with open("lab-048/impact_narrative.md", "w") as f:
    f.write(narrative)
print("💾 Saved to lab-048/impact_narrative.md")
```

---

## Étape 7 : Tableau de bord Power BI (Optionnel)

Si vous avez **Power BI Desktop** installé, vous pouvez créer une version interactive de cette analyse :

1. **Ouvrez Power BI Desktop** → Obtenir des données → Texte/CSV
2. Chargez `copilot_quarterly_summary.csv` et `business_outcomes.csv`
3. Dans la vue **Modèle**, créez une relation sur `department` + `month`
4. Créez ces visuels :

| Type de visuel | Axe X | Axe Y | Objectif |
|-------------|--------|--------|---------|
| Barres groupées | Department | active_users | Adoption par département |
| Graphique en courbes | Month | active_users | Tendance d'adoption |
| Nuage de points | avg_active_days | employee_satisfaction | Visualisation de la corrélation |
| Carte | — | dollar_value | Titre ROI |
| Matrice | Department × Month | Tous les KPI | Ventilation détaillée |

!!! info "Pas de Power BI ? Pas de problème"
    L'analyse Python ci-dessus produit des insights identiques. Power BI ajoute l'interactivité (filtrage, exploration, partage) mais les données et formules sous-jacentes sont les mêmes. Si vous avez **matplotlib** installé, vous pouvez aussi créer des graphiques en Python :

    ```python
    # pip install matplotlib
    import matplotlib.pyplot as plt

    fig, axes = plt.subplots(1, 2, figsize=(14, 5))

    # Chart 1: Adoption trend
    monthly.plot(x="Month", y="Active Users", kind="bar", ax=axes[0], color="#3b82f6")
    axes[0].set_title("Copilot Adoption Growth")
    axes[0].set_ylabel("Active Users")

    # Chart 2: Correlation scatter
    axes[1].scatter(merged["avg_active_days"], merged["employee_satisfaction"],
                    c="#8b5cf6", s=60, alpha=0.7)
    axes[1].set_xlabel("Avg Active Days")
    axes[1].set_ylabel("Employee Satisfaction")
    axes[1].set_title(f"Usage vs Satisfaction (r = {correlation:.2f})")

    plt.tight_layout()
    plt.savefig("lab-048/impact_charts.png", dpi=150)
    plt.show()
    print("📊 Charts saved to lab-048/impact_charts.png")
    ```

---

## 🐛 Exercice de correction de bugs

Le fichier `lab-048/broken_roi_calculator.py` contient **3 bugs** qui produisent des analyses d'impact erronées. Exécutez les auto-tests :

```bash
python lab-048/broken_roi_calculator.py
```

Vous devriez voir **3 tests échoués** :

| Test | Ce qu'il vérifie | Indice |
|------|---------------|------|
| Test 1 | Calcul du ROI | Vérifiez la conversion d'unités (minutes → heures) |
| Test 2 | Colonne de corrélation | Quelle colonne mesure réellement l'*utilisation* ? |
| Test 3 | Base du taux de croissance | Quel mois est le *point de départ* ? |

Corrigez les 3 bugs et relancez jusqu'à voir `🎉 All 3 tests passed`.

---


## 🧠 Quiz de connaissances

??? question "**Q1 (Choix multiple) :** Que signifie « attribution d'impact » dans le contexte de Work IQ ?"

    - A) Compter combien d'utilisateurs ont une licence Copilot
    - B) Relier l'utilisation des outils IA à des résultats business mesurables
    - C) Suivre quel département a le plus d'utilisateurs actifs
    - D) Mesurer le coût total des licences IA

    ??? success "✅ Révéler la réponse"
        **Correct : B) Relier l'utilisation des outils IA à des résultats business mesurables**

        L'attribution d'impact va au-delà des métriques d'adoption (qui utilise Copilot ?) pour répondre à la question du ROI : l'utilisation de Copilot est-elle corrélée à de meilleurs résultats business comme la croissance du chiffre d'affaires, des temps de réponse plus rapides et une meilleure satisfaction des employés ?

??? question "**Q2 (Choix multiple) :** Pourquoi le principe « corrélation ≠ causalité » est-il essentiel lors de la présentation du ROI de Copilot à la direction ?"

    - A) Parce que les corrélations sont toujours peu fiables
    - B) Parce que d'autres facteurs pourraient expliquer les améliorations business
    - C) Parce que les données d'utilisation de Copilot ne sont pas précises
    - D) Parce que la direction ne comprend pas les statistiques

    ??? success "✅ Révéler la réponse"
        **Correct : B) Parce que d'autres facteurs pourraient expliquer les améliorations business**

        Les départements performants peuvent adopter les outils IA plus rapidement parce qu'ils sont déjà bien gérés — l'amélioration pourrait être due à la qualité du leadership, aux recrutements, aux changements de processus ou aux tendances saisonnières. Présentez toujours les résultats comme « les départements avec une utilisation plus élevée *tendent à* montrer de meilleurs résultats » plutôt que de revendiquer une causalité directe.

??? question "**Q3 (Exécutez le lab) :** Quelle est la valeur monétaire totale estimée du temps économisé dans tous les départements sur le T1 2026 (à 50 $/h) ?"

    Calculez : sommez toutes les valeurs `total_time_saved_min`, convertissez en heures, multipliez par 50 $.

    ??? success "✅ Révéler la réponse"
        **9 400 $**

        Temps total économisé : 11 280 minutes ÷ 60 = 188,0 heures × 50 $/h = **9 400 $**. Engineering contribue le plus en valeur absolue (3 262 $), mais Finance a le ROI par utilisateur le plus élevé (383 $/utilisateur).

??? question "**Q4 (Exécutez le lab) :** Quel département montre la plus grande amélioration de satisfaction des employés de janvier à mars 2026 ?"

    Comparez les scores `employee_satisfaction` de janvier et mars pour chaque département.

    ??? success "✅ Révéler la réponse"
        **Finance (+13 points : 75 → 88)**

        Finance est passé de 75 à 88, un delta de +13. Cela correspond au fait que Finance a le taux d'adoption Copilot le plus élevé (100 %). Engineering est second avec +12 (72 → 84). Legal montre la plus petite amélioration (+4), en accord avec sa faible adoption.

??? question "**Q5 (Exécutez le lab) :** Quel est le taux de croissance global de l'adoption de janvier à mars 2026 ?"

    Sommez les `active_users` pour janvier et mars dans tous les départements, puis calculez le pourcentage de croissance.

    ??? success "✅ Révéler la réponse"
        **60,0 %**

        Janvier : 6+4+2+1+4+0+3 = **20** utilisateurs actifs. Mars : 9+6+4+2+6+1+4 = **32** utilisateurs actifs. Croissance = (32 − 20) ÷ 20 × 100 = **60,0 %**.

---

## Résumé

| Sujet | Ce que vous avez appris |
|-------|-----------------|
| Attribution d'impact | Relier les données d'utilisation aux KPI business |
| Calcul du ROI | Temps économisé → heures → valeur monétaire |
| Corrélation de Pearson | Mesurer les relations statistiques (r = 0,97) |
| Analyse de tendances | Croissance de l'adoption mois par mois (60 %) |
| Récit d'impact | Narration prête pour la direction avec des données |
| Correspondance Power BI | Comment l'analyse Python correspond aux visuels Power BI |

---

## Prochaines étapes

- **[Lab 033](lab-033-agent-observability.md)** — Observabilité des agents avec Application Insights (surveiller les agents personnalisés comme Viva surveille Copilot)
- **[Lab 038](lab-038-cost-optimization.md)** — Optimisation des coûts IA (le volet financier du ROI pour les déploiements IA personnalisés)
- **[Lab 035](lab-035-agent-evaluation.md)** — Évaluation des agents avec le SDK Azure AI Eval (métriques de qualité, pas seulement d'adoption)
