---
tags: [power-bi, copilot, fabric, dax, analytics, low-code]
---
# Lab 075 : Power BI Copilot — Analytique autonome et narration de données

<div class="lab-meta">
  <span><strong>Niveau :</strong> <span class="level-badge level-100">L100</span></span>
  <span><strong>Parcours :</strong> Tous les parcours</span>
  <span><strong>Durée :</strong> ~45 min</span>
  <span><strong>💰 Coût :</strong> <span class="level-badge cost-free">Gratuit</span> — Utilise des données de rapports simulées</span>
</div>

## Ce que vous apprendrez

- Ce qu'est **Power BI Copilot** et comment il transforme la création de rapports avec le langage naturel
- Comment les rapports assistés par Copilot et générés par Copilot se comparent à la création manuelle
- Analyser un jeu de données de rapports pour mesurer les **gains de temps**, la **précision** et l'**adoption** par département
- Comprendre comment la génération de mesures DAX fonctionne avec Copilot
- Construire un **rapport d'impact** quantifiant la valeur de Copilot pour l'équipe analytique

## Introduction

**Power BI Copilot** apporte l'IA générative directement dans l'expérience Power BI au sein de Microsoft Fabric. Les analystes et les utilisateurs métier peuvent :

- **Créer des rapports** en décrivant ce qu'ils veulent en langage naturel
- **Générer des mesures DAX** sans mémoriser la syntaxe complexe
- **Construire des narrations** qui résument automatiquement les insights clés
- **Poser des questions** sur leurs données avec des requêtes conversationnelles

### Méthodes de création

| Méthode | Qui | Fonctionnement | Durée typique |
|--------|-----|-------------|-------------|
| **Manuelle** | Analyste | Construit chaque visuel manuellement, écrit le DAX manuellement | 2–4 heures |
| **Assistée par Copilot** | Analyste | L'analyste démarre ; Copilot suggère des visuels, génère le DAX | 1–2 heures |
| **Générée par Copilot** | Utilisateur métier | Décrit le rapport en langage naturel ; Copilot le construit | 15–30 min |

### Le scénario

Vous êtes un **Responsable d'équipe BI** dans une entreprise de taille moyenne. Votre équipe pilote Power BI Copilot depuis 3 mois. Vous disposez de **10 rapports** répartis dans 4 départements — certains manuels, certains assistés par Copilot et certains entièrement générés par Copilot. La direction veut savoir : _« Copilot fait-il vraiment gagner du temps ? La qualité est-elle acceptable ? »_

Votre jeu de données (`powerbi_reports.csv`) contient les réponses. Votre mission : analyser les données et construire un rapport d'impact convaincant.

!!! info "Données simulées"
    Ce lab utilise un jeu de données de rapports simulé. Les données reflètent des patterns réels : les rapports générés par Copilot sont plus rapides mais légèrement moins précis ; les rapports assistés par Copilot combinent rapidité et qualité de niveau analyste.

## Prérequis

| Exigence | Raison |
|---|---|
| Python 3.10+ | Exécuter les scripts d'analyse |
| Bibliothèque `pandas` | Manipulation des données |

```bash
pip install pandas
```

---

!!! tip "Démarrage rapide avec GitHub Codespaces"
    [![Open in GitHub Codespaces](https://github.com/codespaces/badge.svg)](https://codespaces.new/lcarli/AI-LearningHub?quickstart=1)

    Toutes les dépendances sont pré-installées dans le devcontainer.


## 📦 Fichiers de support

!!! note "Téléchargez ces fichiers avant de commencer le lab"
    Enregistrez tous les fichiers dans un dossier `lab-075/` de votre répertoire de travail.

| Fichier | Description | Téléchargement |
|------|-------------|----------|
| `broken_powerbi.py` | Exercice de correction de bugs (3 bugs + auto-tests) | [📥 Télécharger](https://github.com/lcarli/AI-LearningHub/raw/main/docs/docs/en/labs/lab-075/broken_powerbi.py) |
| `powerbi_reports.csv` | Jeu de données | [📥 Télécharger](https://github.com/lcarli/AI-LearningHub/raw/main/docs/docs/en/labs/lab-075/powerbi_reports.csv) |

---

## Étape 1 : Comprendre les métriques

Avant d'analyser, comprenez ce que chaque colonne du jeu de données mesure :

| Colonne | Description |
|--------|-----------|
| **created_by** | `analyst` ou `business_user` — qui a construit le rapport |
| **creation_method** | `manual`, `copilot_assisted` ou `copilot_generated` |
| **pages** | Nombre de pages du rapport |
| **visuals** | Nombre total d'éléments visuels (graphiques, tableaux, cartes) |
| **dax_measures** | Nombre de mesures DAX dans le modèle de données |
| **copilot_queries** | Nombre d'interactions Copilot utilisées lors de la création |
| **time_saved_min** | Minutes estimées économisées par rapport à une création entièrement manuelle |
| **accuracy_score** | Score de qualité (0,0–1,0) basé sur la revue de précision des données |

### Formules clés

```
Copilot Adoption Rate = (Copilot reports ÷ Total reports) × 100

Avg Time Saved = Sum(time_saved_min for copilot reports) ÷ Count(copilot reports)

Quality Gap = Avg accuracy(manual) − Avg accuracy(copilot_generated)
```

---

## Étape 2 : Charger et explorer le jeu de données

Le jeu de données contient **10 rapports** répartis dans 4 départements :

```python
import pandas as pd

df = pd.read_csv("lab-075/powerbi_reports.csv")

print(f"Total reports: {len(df)}")
print(f"Creation methods: {df['creation_method'].value_counts().to_dict()}")
print(f"Departments: {df['department'].unique().tolist()}")
print(f"\nAll reports:")
print(df[["report_id", "report_name", "creation_method", "time_saved_min", "accuracy_score"]].to_string(index=False))
```

**Sortie attendue :**

```
Total reports: 10
Creation methods: {'copilot_assisted': 4, 'copilot_generated': 4, 'manual': 2}
Departments: ['Sales', 'Marketing', 'Operations', 'HR', 'Finance']
```

---

## Étape 3 : Mesurer l'adoption de Copilot

Combien de rapports ont utilisé Copilot sous une forme ou une autre ?

```python
copilot_reports = df[df["creation_method"].isin(["copilot_assisted", "copilot_generated"])]
manual_reports = df[df["creation_method"] == "manual"]

copilot_count = len(copilot_reports)
total = len(df)
adoption_rate = copilot_count / total * 100

print(f"Copilot-assisted/generated reports: {copilot_count}")
print(f"Manual reports:                     {len(manual_reports)}")
print(f"Copilot adoption rate:              {adoption_rate:.0f}%")
```

**Sortie attendue :**

```
Copilot-assisted/generated reports: 8
Manual reports:                     2
Copilot adoption rate:              80%
```

Décomposez par méthode de création :

```python
for method, group in df.groupby("creation_method"):
    print(f"\n{method}:")
    print(f"  Reports: {len(group)}")
    print(f"  Avg pages: {group['pages'].mean():.1f}")
    print(f"  Avg visuals: {group['visuals'].mean():.1f}")
    print(f"  Avg DAX measures: {group['dax_measures'].mean():.1f}")
```

!!! tip "Insight"
    **80 % des rapports** utilisent désormais Copilot — un signal d'adoption fort. Les rapports manuels tendent à avoir plus de pages et de visuels, suggérant que les tableaux de bord complexes sont encore construits à la main. Les rapports générés par Copilot sont plus petits mais créés par des utilisateurs métier qui n'auraient pas pu les construire auparavant.

---

## Étape 4 : Calculer les gains de temps

La colonne `time_saved_min` estime le temps que Copilot a fait gagner par rapport à une création entièrement manuelle :

```python
total_time_saved = df["time_saved_min"].sum()
copilot_time_saved = copilot_reports["time_saved_min"].sum()
avg_time_saved = copilot_reports["time_saved_min"].mean()

print(f"Total time saved (all reports):      {total_time_saved} min")
print(f"Total time saved (copilot reports):  {copilot_time_saved} min")
print(f"Avg time saved per copilot report:   {avg_time_saved:.1f} min")
print(f"Total hours saved:                   {total_time_saved / 60:.1f} hours")
```

**Sortie attendue :**

```
Total time saved (all reports):      395 min
Total time saved (copilot reports):  395 min
Avg time saved per copilot report:   49.4 min
Total hours saved:                   6.6 hours
```

Décomposez par méthode :

```python
for method in ["copilot_assisted", "copilot_generated"]:
    subset = df[df["creation_method"] == method]
    print(f"\n{method}:")
    print(f"  Total saved: {subset['time_saved_min'].sum()} min")
    print(f"  Avg saved:   {subset['time_saved_min'].mean():.1f} min")
```

---

## Étape 5 : Évaluer la qualité et la précision

Les gains de temps sont sans valeur si la qualité en pâtit. Comparez les scores de précision :

```python
for method in df["creation_method"].unique():
    subset = df[df["creation_method"] == method]
    avg_acc = subset["accuracy_score"].mean()
    print(f"  {method:>20s}: avg accuracy = {avg_acc:.2f}")
```

**Sortie attendue :**

```
              manual: avg accuracy = 0.96
    copilot_assisted: avg accuracy = 0.94
   copilot_generated: avg accuracy = 0.85
```

```python
# Quality gap analysis
manual_acc = manual_reports["accuracy_score"].mean()
assisted_acc = df[df["creation_method"] == "copilot_assisted"]["accuracy_score"].mean()
generated_acc = df[df["creation_method"] == "copilot_generated"]["accuracy_score"].mean()

print(f"\nQuality gap (manual vs. assisted):  {(manual_acc - assisted_acc) * 100:.1f}pp")
print(f"Quality gap (manual vs. generated): {(manual_acc - generated_acc) * 100:.1f}pp")
```

!!! warning "Compromis de qualité"
    Les **rapports assistés par Copilot** (analyste + Copilot) atteignent une **précision de 0,94** — seulement 2pp en dessous du manuel. Les **rapports générés par Copilot** (utilisateur métier + Copilot) obtiennent **0,85** — acceptable pour l'exploration mais pouvant nécessiter une révision par un analyste avant distribution aux dirigeants.

---

## Étape 6 : Construire le rapport d'impact

```python
total_copilot_queries = copilot_reports["copilot_queries"].sum()

report = f"""# 📊 Power BI Copilot Impact Report

## Adoption Summary
| Metric | Value |
|--------|-------|
| Total Reports | {len(df)} |
| Copilot Reports | {copilot_count} ({adoption_rate:.0f}%) |
| Manual Reports | {len(manual_reports)} |
| Total Copilot Queries | {total_copilot_queries} |

## Time Savings
| Metric | Value |
|--------|-------|
| Total Time Saved | {total_time_saved} min ({total_time_saved / 60:.1f} hours) |
| Avg per Copilot Report | {avg_time_saved:.1f} min |
| Copilot-Assisted Avg | {df[df['creation_method']=='copilot_assisted']['time_saved_min'].mean():.1f} min |
| Copilot-Generated Avg | {df[df['creation_method']=='copilot_generated']['time_saved_min'].mean():.1f} min |

## Quality Assessment
| Method | Avg Accuracy | Rating |
|--------|-------------|--------|
| Manual | {manual_acc:.2f} | ⭐⭐⭐ Gold standard |
| Copilot-Assisted | {assisted_acc:.2f} | ⭐⭐⭐ Production-ready |
| Copilot-Generated | {generated_acc:.2f} | ⭐⭐ Review recommended |

## Recommendations
1. **Encourage Copilot-assisted** for analyst-built reports — saves ~41 min with near-manual quality
2. **Use Copilot-generated** for exploratory/departmental reports — saves ~58 min, good for self-service
3. **Add review step** for Copilot-generated reports going to executives — accuracy gap of {(manual_acc - generated_acc) * 100:.0f}pp
4. **Track DAX measure accuracy** — Copilot-generated DAX may need validation for complex calculations
"""

print(report)

with open("lab-075/impact_report.md", "w") as f:
    f.write(report)
print("💾 Saved to lab-075/impact_report.md")
```

---

## 🐛 Exercice de correction de bugs

Le fichier `lab-075/broken_powerbi.py` contient **3 bugs** qui produisent des métriques Power BI incorrectes. Pouvez-vous les trouver et les corriger tous ?

Exécutez les auto-tests pour voir lesquels échouent :

```bash
python lab-075/broken_powerbi.py
```

Vous devriez voir **3 tests échoués**. Chaque test correspond à un bug :

| Test | Ce qu'il vérifie | Indice |
|------|---------------|------|
| Test 1 | Nombre de rapports Copilot | Devrait compter les méthodes copilot, pas `manual` |
| Test 2 | Temps total économisé | Devrait sommer `time_saved_min`, pas le moyenner |
| Test 3 | Précision moyenne par méthode | Devrait filtrer par méthode avant de calculer la moyenne |

Corrigez les 3 bugs, puis relancez. Quand vous voyez `All passed!`, c'est terminé !

---


## 🧠 Vérification des connaissances

??? question "**Q1 (Choix multiple) :** Quelle est la différence clé entre la création de rapports « copilot_assisted » et « copilot_generated » ?"

    - A) Copilot-assisted utilise un modèle différent de copilot-generated
    - B) Copilot-assisted est démarré par un analyste qui utilise Copilot pour l'aide ; copilot-generated est créé entièrement à partir d'une description en langage naturel
    - C) Les rapports copilot-generated sont toujours plus précis
    - D) Les rapports copilot-assisted ne peuvent pas inclure de mesures DAX

    ??? success "✅ Révéler la réponse"
        **Correct : B) Copilot-assisted est démarré par un analyste qui utilise Copilot pour l'aide ; copilot-generated est créé entièrement à partir d'une description en langage naturel**

        En mode copilot-assisted, un analyste pilote le processus et utilise Copilot pour suggérer des visuels, générer du DAX ou créer des résumés narratifs. En mode copilot-generated, un utilisateur métier décrit le rapport souhaité en langage naturel et Copilot le construit de zéro — plus rapide mais avec moins de supervision humaine.

??? question "**Q2 (Choix multiple) :** Pourquoi les rapports générés par Copilot pourraient-ils nécessiter une étape de révision avant distribution aux dirigeants ?"

    - A) Ils utilisent trop de visuels
    - B) Ils ont des scores de précision plus bas en raison de moins de supervision humaine lors de la création
    - C) Ils sont générés trop rapidement
    - D) Ils ne peuvent pas inclure de mesures DAX

    ??? success "✅ Révéler la réponse"
        **Correct : B) Ils ont des scores de précision plus bas en raison de moins de supervision humaine lors de la création**

        Les rapports générés par Copilot ont une précision moyenne d'environ 0,85 contre environ 0,96 pour les rapports manuels. Sans qu'un analyste valide les mappages de données, la logique de filtres et les calculs DAX, il y a un risque plus élevé d'erreurs subtiles — en particulier pour les métriques métier complexes.

??? question "**Q3 (Exécutez le lab) :** Combien de rapports ont été créés avec Copilot (assistés ou générés) ?"

    Exécutez l'analyse de l'étape 3 sur [📥 `powerbi_reports.csv`](https://github.com/lcarli/AI-LearningHub/raw/main/docs/docs/en/labs/lab-075/powerbi_reports.csv) et comptez les rapports copilot.

    ??? success "✅ Révéler la réponse"
        **8 rapports**

        Sur les 10 rapports du jeu de données, 4 sont `copilot_assisted` (R02, R04, R07, R09) et 4 sont `copilot_generated` (R03, R05, R08, R10). Seulement 2 sont `manual` (R01, R06). Total des rapports copilot = **8**.

??? question "**Q4 (Exécutez le lab) :** Quel est le temps total économisé sur tous les rapports ?"

    Exécutez l'analyse de l'étape 4 pour calculer le temps total économisé.

    ??? success "✅ Révéler la réponse"
        **395 minutes**

        Somme de toutes les valeurs `time_saved_min` : 0 + 45 + 60 + 30 + 50 + 0 + 55 + 65 + 35 + 55 = **395 minutes** (6,6 heures). Les rapports manuels (R01, R06) ont 0 de temps économisé puisqu'ils sont la référence.

??? question "**Q5 (Exécutez le lab) :** Quel est le temps moyen économisé par rapport Copilot ?"

    Divisez le temps total économisé par copilot par le nombre de rapports copilot.

    ??? success "✅ Révéler la réponse"
        **49,4 minutes**

        Temps total économisé par les rapports copilot = 45 + 60 + 30 + 50 + 55 + 65 + 35 + 55 = 395 min. Nombre de rapports copilot = 8. Moyenne = 395 ÷ 8 = **49,4 minutes** par rapport.

---

## Résumé

| Sujet | Ce que vous avez appris |
|-------|-----------------|
| Power BI Copilot | Création de rapports, génération DAX et narration de données assistées par IA |
| Méthodes de création | Manuelle, assistée par Copilot (analyste+IA), générée par Copilot (utilisateur métier+IA) |
| Gains de temps | 49,4 min en moyenne par rapport Copilot ; 395 min au total pour le pilote |
| Compromis de qualité | Assisté=0,94 de précision (proche du manuel) ; Généré=0,85 (révision nécessaire) |
| Adoption | 80 % des rapports ont utilisé Copilot — signal d'adoption fort du pilote |
| BI en libre-service | Le mode généré par Copilot permet aux utilisateurs métier de créer leurs propres rapports |

---

## Prochaines étapes

- **[Lab 048](lab-048-work-iq-power-bi.md)** — Tableaux de bord Work IQ Power BI (analytique avancée avec Viva Insights)
- **[Lab 047](lab-047-work-iq-copilot-analytics.md)** — Analytique d'adoption Work IQ Copilot (mesurer l'utilisation de Copilot dans M365)
- **[Lab 074](lab-074-foundry-agent-service.md)** — Foundry Agent Service (déployer des agents IA qui alimentent Power BI)
- **[Lab 038](lab-038-cost-optimization.md)** — Optimisation des coûts IA (gérer les coûts de Copilot et de l'IA)