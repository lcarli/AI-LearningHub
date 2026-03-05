---
tags: [markitdown, mcp, document-ingestion, pdf, python]
---
# Lab 080 : MarkItDown + MCP — Ingestion de documents pour agents

<div class="lab-meta">
  <span><strong>Niveau :</strong> <span class="level-badge level-200">L200</span></span>
  <span><strong>Parcours :</strong> Tous les parcours</span>
  <span><strong>Durée :</strong> ~60 min</span>
  <span><strong>💰 Coût :</strong> <span class="level-badge cost-free">Gratuit</span></span>
</div>

## Ce que vous apprendrez

- Ce qu'est **Microsoft MarkItDown** — une bibliothèque qui convertit PDF, Word, Excel, PowerPoint, HTML et images en Markdown propre pour la consommation par les LLM
- Comment le **serveur MCP** de MarkItDown expose la conversion de documents comme un outil que tout agent compatible MCP peut appeler
- Analyser la **qualité de conversion** sur différents types de fichiers pour comprendre les forces et limites
- Mesurer la **vitesse de conversion** et identifier quels formats sont les plus rapides à traiter
- Déboguer un script d'analyse MarkItDown cassé en corrigeant 3 bugs

## Introduction

Les grands modèles de langage fonctionnent mieux avec du **texte brut**, mais les documents d'entreprise se présentent dans des dizaines de formats — PDF avec tableaux, documents Word avec images intégrées, tableurs Excel, présentations PowerPoint et pages HTML. Les convertir manuellement en texte fait perdre la structure, et les approches basées sur l'OCR sont lentes et sujettes aux erreurs.

**Microsoft MarkItDown** résout ce problème en convertissant les documents riches en **Markdown bien structuré** qui préserve les tableaux, titres, listes et références d'images. Il prend en charge PDF, DOCX, XLSX, PPTX, HTML, CSV, JSON et même les images (via OCR/captioning). Combiné avec son **serveur MCP**, tout agent peut appeler `convert_to_markdown` comme outil — permettant des workflows d'ingestion de documents sans couture.

### Le scénario

Vous êtes un **ingénieur de plateforme** chez OutdoorGear Inc. L'entreprise possède un corpus documentaire croissant — rapports trimestriels, catalogues de produits, manuels de formation et contrats — sur lequel les agents doivent rechercher et raisonner. Vous évaluerez la qualité de conversion de MarkItDown sur **12 conversions de fichiers** couvrant 7 types de fichiers différents.

!!! info "Aucune installation de MarkItDown requise"
    Ce lab analyse un **jeu de données de benchmark pré-enregistré** des résultats de conversion. Vous n'avez pas besoin d'installer MarkItDown — toute l'analyse est faite localement avec pandas. Si vous souhaitez exécuter des conversions en direct, installez avec `pip install markitdown`.

## Prérequis

| Exigence | Pourquoi |
|---|---|
| Python 3.10+ | Exécuter les scripts d'analyse |
| Bibliothèque `pandas` | Opérations sur les DataFrames |
| (Optionnel) `markitdown` | Pour les conversions de documents en direct |

```bash
pip install pandas
```

---

!!! tip "Démarrage rapide avec GitHub Codespaces"
    [![Open in GitHub Codespaces](https://github.com/codespaces/badge.svg)](https://codespaces.new/lcarli/AI-LearningHub?quickstart=1)

    Toutes les dépendances sont pré-installées dans le devcontainer.


## 📦 Fichiers de support

!!! note "Téléchargez ces fichiers avant de commencer le lab"
    Enregistrez tous les fichiers dans un dossier `lab-080/` de votre répertoire de travail.

| Fichier | Description | Téléchargement |
|------|-------------|----------|
| `broken_markitdown.py` | Exercice de correction de bugs (3 bugs + auto-tests) | [📥 Télécharger](https://github.com/lcarli/AI-LearningHub/raw/main/docs/docs/en/labs/lab-080/broken_markitdown.py) |
| `conversion_results.csv` | Jeu de données — 12 conversions de fichiers sur 7 formats | [📥 Télécharger](https://github.com/lcarli/AI-LearningHub/raw/main/docs/docs/en/labs/lab-080/conversion_results.csv) |

---

## Étape 1 : Comprendre MarkItDown

MarkItDown suit un pipeline simple — détecter le type de fichier, appliquer le convertisseur approprié et produire du Markdown structuré :

```
┌──────────────┐     ┌──────────────┐     ┌──────────────┐
│  Input File  │────▶│  Converter   │────▶│  Markdown    │
│  (PDF/DOCX…) │     │  (per-type)  │     │  (structured)│
└──────────────┘     └──────────────┘     └──────────────┘
```

Convertisseurs pris en charge :

| Format | Convertisseur | Préserve |
|--------|-----------|-----------|
| **PDF** | `pdfminer` | Texte, titres, tableaux (limité) |
| **DOCX** | `python-docx` | Titres, tableaux, listes, styles |
| **XLSX** | `openpyxl` | Données de feuille en tableaux Markdown |
| **PPTX** | `python-pptx` | Texte des diapositives, notes du présentateur, images |
| **HTML** | `BeautifulSoup` | Structure, liens, tableaux |
| **CSV/JSON** | Intégré | Données tabulaires |
| **Images** | OCR / captioning LLM | Texte extrait ou descriptions |

### Intégration du serveur MCP

MarkItDown est livré avec un **serveur MCP** qui expose la conversion comme outil :

```json
{
  "tools": [
    {
      "name": "convert_to_markdown",
      "description": "Convert a document file to Markdown",
      "inputSchema": {
        "type": "object",
        "properties": {
          "uri": { "type": "string", "description": "File path or URL" }
        }
      }
    }
  ]
}
```

Tout agent compatible MCP (GitHub Copilot, Claude Desktop, agents personnalisés) peut appeler cet outil pour ingérer des documents à la volée.

---

## Étape 2 : Charger les résultats de conversion

Le jeu de données contient **12 conversions de fichiers** sur 7 formats différents :

```python
import pandas as pd

results = pd.read_csv("lab-080/conversion_results.csv")
print(f"Total conversions: {len(results)}")
print(f"File types: {sorted(results['file_type'].unique())}")
print(f"\nDataset preview:")
print(results[["test_id", "input_file", "file_type", "conversion_success", "quality_score"]].to_string(index=False))
```

**Sortie attendue :**

```
Total conversions: 12
File types: ['csv', 'docx', 'html', 'image', 'json', 'pdf', 'pptx', 'xlsx']
```

| test_id | input_file | file_type | conversion_success | quality_score |
|---------|-----------|-----------|-------------------|---------------|
| D01 | quarterly_report.pdf | pdf | True | 0.92 |
| D02 | product_catalog.docx | docx | True | 0.95 |
| ... | ... | ... | ... | ... |
| D11 | corrupted_file.pdf | pdf | False | 0.00 |
| D12 | scanned_receipt.png | image | True | 0.72 |

---

## Étape 3 : Analyser le taux de réussite des conversions

Calculez le taux de réussite global et identifiez les échecs :

```python
successful = results[results["conversion_success"] == True]
failed = results[results["conversion_success"] == False]

print(f"Successful conversions: {len(successful)}/{len(results)}")
print(f"Success rate: {len(successful)/len(results)*100:.0f}%")

if len(failed) > 0:
    print(f"\nFailed conversions:")
    print(failed[["test_id", "input_file", "file_type"]].to_string(index=False))
```

**Sortie attendue :**

```
Successful conversions: 11/12
Success rate: 92%

Failed conversions:
 test_id      input_file file_type
     D11 corrupted_file.pdf       pdf
```

!!! tip "Observation"
    Le seul échec est un **PDF corrompu** (D11, file_size_kb = 0). MarkItDown gère avec succès les 7 formats pris en charge lorsque le fichier d'entrée est valide.

---

## Étape 4 : Analyser la qualité de conversion

Comparez les scores de qualité entre les types de fichiers :

```python
print("Quality scores by file type (successful only):")
quality = successful.groupby("file_type")["quality_score"].agg(["mean", "count"])
quality.columns = ["avg_quality", "count"]
print(quality.sort_values("avg_quality", ascending=False).to_string())

avg_quality = successful["quality_score"].mean()
print(f"\nOverall average quality: {avg_quality:.3f}")
```

**Sortie attendue :**

```
Quality scores by file type (successful only):
           avg_quality  count
csv              0.990      1
json             0.980      1
xlsx             0.980      1
html             0.970      1
docx             0.955      2
pdf              0.893      3
pptx             0.850      1
image            0.720      1

Overall average quality: ≈ 0.916
```

!!! tip "Observation"
    Les formats structurés (CSV, JSON, XLSX) atteignent une qualité quasi parfaite (≥0.98), tandis que les **images** ont la qualité la plus basse (0.72) — l'OCR/captioning est intrinsèquement avec perte. Les PDF varient selon la complexité ; le grand manuel de formation (D10, 12 Mo) a obtenu 0.82.

---

## Étape 5 : Analyser la vitesse de conversion

Mesurez les temps de conversion et identifiez les goulots d'étranglement :

```python
print("Conversion time by file type (successful only):")
for _, row in successful.sort_values("conversion_time_ms", ascending=False).iterrows():
    print(f"  {row['test_id']} ({row['file_type']:>5}): {row['conversion_time_ms']:,}ms "
          f"({row['file_size_kb']:,} KB)")
```

**Sortie attendue :**

```
  D10 (  pdf): 4,500ms (12,000 KB)
  D12 (image): 2,200ms (450 KB)
  D04 ( pptx): 1,800ms (5,200 KB)
  D01 (  pdf): 1,200ms (2,450 KB)
  ...
  D08 (  csv):    30ms (45 KB)
```

```python
total_tables = successful["tables_found"].sum()
total_images = successful["images_found"].sum()
total_headings = successful["headings_found"].sum()

print(f"\nExtracted elements (successful conversions):")
print(f"  Tables found:   {total_tables}")
print(f"  Images found:   {total_images}")
print(f"  Headings found: {total_headings}")
```

**Sortie attendue :**

```
Extracted elements (successful conversions):
  Tables found:   31
  Images found:   62
  Headings found: 103
```

!!! tip "Observation"
    Les gros PDF et les images sont les plus lents à convertir. Le **manuel de formation** (D10, 12 Mo) a pris 4.5 secondes mais a extrait 15 tableaux, 28 images et 32 titres — un document riche qui serait extrêmement fastidieux à traiter manuellement.

---

## Étape 6 : Architecture du serveur MCP

Lorsque MarkItDown fonctionne comme serveur MCP, les agents peuvent convertir des documents à la demande :

```
┌──────────────┐     ┌──────────────┐     ┌──────────────┐
│   Agent      │────▶│  MCP Server  │────▶│  MarkItDown  │
│  (Copilot,   │     │  (stdio/SSE) │     │  (converter) │
│   Claude)    │◀────│              │◀────│              │
└──────────────┘     └──────────────┘     └──────────────┘
     request              route              convert
     markdown             return             to .md
```

Pour démarrer le serveur MCP localement :

```bash
# Install MarkItDown with MCP support
pip install 'markitdown[mcp]'

# Start the MCP server (stdio transport)
markitdown --mcp
```

Puis ajoutez-le à votre configuration client MCP :

```json
{
  "mcpServers": {
    "markitdown": {
      "command": "markitdown",
      "args": ["--mcp"]
    }
  }
}
```

---

## 🐛 Exercice de correction de bugs

Le fichier `lab-080/broken_markitdown.py` contient **3 bugs** dans les fonctions d'analyse. Pouvez-vous les trouver et les corriger tous ?

Exécutez les auto-tests pour voir lesquels échouent :

```bash
python lab-080/broken_markitdown.py
```

Vous devriez voir **3 tests échoués**. Chaque test correspond à un bug :

| Test | Ce qu'il vérifie | Indice |
|------|---------------|------|
| Test 1 | Calcul du taux de réussite | Devrait compter `True`, pas `False` |
| Test 2 | Calcul de la qualité moyenne | Doit d'abord filtrer les conversions réussies |
| Test 3 | Total des tableaux trouvés | Devrait sommer `tables_found`, pas `images_found` |

Corrigez les 3 bugs, puis relancez. Quand vous voyez `All passed!`, c'est terminé !

---

## 🧠 Vérification des connaissances

??? question "**Q1 (Choix multiple) :** Quels formats MarkItDown prend-il en charge pour la conversion en Markdown ?"

    - A) Uniquement les documents PDF et Word
    - B) PDF, DOCX, XLSX, PPTX, HTML, CSV, JSON et images
    - C) Uniquement les formats texte comme HTML et CSV
    - D) Tout format, y compris les fichiers vidéo et audio

    ??? success "✅ Révéler la réponse"
        **Correct : B) PDF, DOCX, XLSX, PPTX, HTML, CSV, JSON et images**

        MarkItDown prend en charge un large éventail de formats de documents incluant PDF (via pdfminer), documents Word (python-docx), tableurs Excel (openpyxl), présentations PowerPoint (python-pptx), HTML (BeautifulSoup), CSV, JSON et images (via OCR ou captioning LLM). Il ne prend pas en charge les fichiers audio ou vidéo.

??? question "**Q2 (Choix multiple) :** Comment le serveur MCP de MarkItDown permet-il l'ingestion de documents par les agents ?"

    - A) Il convertit les documents en embeddings directement
    - B) Il expose un outil `convert_to_markdown` que tout agent compatible MCP peut appeler
    - C) Il nécessite que les agents téléchargent et analysent les fichiers eux-mêmes
    - D) Il stocke automatiquement les documents convertis dans une base de données vectorielle

    ??? success "✅ Révéler la réponse"
        **Correct : B) Il expose un outil `convert_to_markdown` que tout agent compatible MCP peut appeler**

        Le serveur MCP de MarkItDown fonctionne comme un serveur d'outils MCP standard (via le transport stdio ou SSE). Il expose un outil `convert_to_markdown` qui accepte un URI de fichier et retourne le Markdown converti. Tout client compatible MCP — GitHub Copilot, Claude Desktop ou agents personnalisés — peut appeler cet outil pour ingérer des documents à la volée sans code d'intégration personnalisé.

??? question "**Q3 (Exécutez le lab) :** Combien des 12 conversions de fichiers ont réussi ?"

    Chargez [📥 `conversion_results.csv`](https://github.com/lcarli/AI-LearningHub/raw/main/docs/docs/en/labs/lab-080/conversion_results.csv) et comptez les lignes où `conversion_success == True`.

    ??? success "✅ Révéler la réponse"
        **11 sur 12**

        Toutes les conversions ont réussi sauf D11 (`corrupted_file.pdf`), qui était un PDF corrompu avec une taille de fichier de 0 Ko. MarkItDown gère de manière fiable les fichiers valides dans les 7 formats testés.

??? question "**Q4 (Exécutez le lab) :** Quel est le nombre total de tableaux trouvés dans toutes les conversions réussies ?"

    Filtrez les conversions réussies et calculez `tables_found.sum()`.

    ??? success "✅ Révéler la réponse"
        **31**

        Somme de `tables_found` sur les 11 conversions réussies : D01(6) + D02(2) + D03(5) + D04(1) + D05(0) + D06(0) + D07(1) + D08(1) + D09(0) + D10(15) + D12(0) = **31 tableaux**.

??? question "**Q5 (Exécutez le lab) :** Quel est le score de qualité moyen pour les conversions réussies ?"

    Filtrez sur `conversion_success == True`, puis calculez `quality_score.mean()`.

    ??? success "✅ Révéler la réponse"
        **≈ 0.916**

        Scores de qualité des 11 conversions réussies : 0.92 + 0.95 + 0.98 + 0.85 + 0.97 + 0.94 + 0.96 + 0.99 + 0.98 + 0.82 + 0.72 = **10.08**. Moyenne = 10.08 ÷ 11 ≈ **0.916**.

---

## Résumé

| Sujet | Ce que vous avez appris |
|-------|-----------------|
| MarkItDown | Convertit PDF, DOCX, XLSX, PPTX, HTML, CSV, JSON et images en Markdown structuré |
| Intégration MCP | Le serveur MCP expose l'outil `convert_to_markdown` pour tout agent compatible |
| Analyse de qualité | Les formats structurés (CSV, JSON, XLSX) atteignent ≥0.98 de qualité ; les images sont les plus basses à 0.72 |
| Analyse de vitesse | Les gros PDF et images sont les plus lents ; CSV/JSON se convertissent en moins de 50 ms |
| Taux de réussite | 11/12 conversions réussies — seuls les fichiers corrompus échouent |
| Extraction d'éléments | 31 tableaux, 62 images, 103 titres extraits des conversions réussies |

---

## Prochaines étapes

- **[Lab 081](lab-081-agentic-coding-tools.md)** — Outils de codage agentiques : Claude Code vs Copilot CLI
- Explorez le [dépôt GitHub MarkItDown](https://github.com/microsoft/markitdown) pour la configuration avancée et les convertisseurs personnalisés
