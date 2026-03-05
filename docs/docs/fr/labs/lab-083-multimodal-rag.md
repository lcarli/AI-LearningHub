---
tags: [multimodal, rag, images, tables, gpt4o-vision, python]
---
# Lab 083 : RAG multimodal — Images, tableaux et graphiques dans les documents

<div class="lab-meta">
  <span><strong>Niveau :</strong> <span class="level-badge level-300">L300</span></span>
  <span><strong>Parcours :</strong> Tous les parcours</span>
  <span><strong>Durée :</strong> ~90 min</span>
  <span><strong>💰 Coût :</strong> <span class="level-badge cost-free">Gratuit</span></span>
</div>

## Ce que vous apprendrez

- Ce qu'est le **RAG multimodal** — la génération augmentée par récupération qui gère les images, tableaux et graphiques en plus du texte
- Comment **GPT-4o vision** permet la compréhension du contenu visuel dans les documents pour une récupération plus riche
- Comparer les scores de récupération **texte seul vs multimodal** pour quantifier l'amélioration apportée par la compréhension visuelle
- Analyser les **types de chunks** (texte, image, tableau) et leur impact sur la qualité de récupération
- Déboguer un script d'analyse RAG multimodal cassé en corrigeant 3 bugs

## Introduction

Les pipelines RAG traditionnels fonctionnent bien avec le texte — ils découpent les documents, vectorisent les chunks et récupèrent les plus pertinents pour une requête. Mais les documents d'entreprise ne sont pas que du texte. Ils contiennent des **diagrammes à barres**, des **camemberts**, des **photos de produits**, des **diagrammes d'architecture**, des **tableaux de données** et des **organigrammes** qui portent des informations critiques.

Un pipeline RAG texte seul manque entièrement ces informations. Quand un utilisateur demande « Quel était le chiffre d'affaires du T1 par région ? », la réponse peut se trouver dans un **diagramme à barres** — que l'embedding texte seul score à 0.15 (quasi inutile) tandis qu'une approche multimodale score à 0.82 (hautement pertinent).

| Approche | Gère le texte | Gère les images | Gère les tableaux | Cas d'usage typique |
|----------|:---:|:---:|:---:|---|
| **RAG texte seul** | ✅ | ❌ | ⚠️ (texte seul) | Q&R simple sur des documents texte |
| **RAG multimodal** | ✅ | ✅ | ✅ | Documents avec graphiques, photos, diagrammes |

### Le scénario

Vous construisez un **système d'intelligence documentaire** pour OutdoorGear Inc. Le corpus comprend des rapports trimestriels avec graphiques, des catalogues de produits avec photos, des manuels de formation avec diagrammes, des présentations pour investisseurs avec visualisations et des tableurs de ventes. Vous analyserez **15 chunks de documents** pour comparer les performances de récupération texte seul et multimodal.

!!! info "Aucune API GPT-4o requise"
    Ce lab analyse un **jeu de données de benchmark pré-enregistré** de scores de récupération. Vous n'avez pas besoin de clé API OpenAI — toute l'analyse est faite localement avec pandas. Le jeu de données simule des scores de récupération réels d'un pipeline RAG multimodal.

## Prérequis

| Exigence | Pourquoi |
|---|---|
| Python 3.10+ | Exécuter les scripts d'analyse |
| Bibliothèque `pandas` | Opérations sur les DataFrames |

```bash
pip install pandas
```

---

!!! tip "Démarrage rapide avec GitHub Codespaces"
    [![Open in GitHub Codespaces](https://github.com/codespaces/badge.svg)](https://codespaces.new/lcarli/AI-LearningHub?quickstart=1)

    Toutes les dépendances sont pré-installées dans le devcontainer.


## 📦 Fichiers de support

!!! note "Téléchargez ces fichiers avant de commencer le lab"
    Enregistrez tous les fichiers dans un dossier `lab-083/` de votre répertoire de travail.

| Fichier | Description | Téléchargement |
|------|-------------|----------|
| `broken_multimodal.py` | Exercice de correction de bugs (3 bugs + auto-tests) | [📥 Télécharger](https://github.com/lcarli/AI-LearningHub/raw/main/docs/docs/en/labs/lab-083/broken_multimodal.py) |
| `multimodal_chunks.csv` | Jeu de données — 15 chunks de documents avec scores de récupération | [📥 Télécharger](https://github.com/lcarli/AI-LearningHub/raw/main/docs/docs/en/labs/lab-083/multimodal_chunks.csv) |

---

## Étape 1 : Comprendre le RAG multimodal

Un pipeline RAG multimodal étend le RAG traditionnel avec la compréhension visuelle :

```
┌──────────────┐     ┌──────────────┐     ┌──────────────┐
│  Document    │────▶│  Chunker     │────▶│  Chunks      │
│  (PDF/DOCX)  │     │  (text +     │     │  (text,      │
│              │     │   visual)    │     │   image,     │
└──────────────┘     └──────────────┘     │   table)     │
                                          └──────┬───────┘
                                                 │
                     ┌──────────────┐     ┌──────▼───────┐
                     │  Query       │────▶│  Retrieval   │
                     │              │     │  (text +     │
                     │              │     │   vision)    │
                     └──────────────┘     └──────┬───────┘
                                                 │
                                          ┌──────▼───────┐
                                          │  LLM + GPT-4o│
                                          │  (generate)  │
                                          └──────────────┘
```

### Comment les chunks visuels sont traités

| Type de chunk | Pipeline texte seul | Pipeline multimodal |
|-----------|-------------------|---------------------|
| **Texte** | Vectoriser le texte → récupérer par similarité cosinus | Identique au texte seul |
| **Tableau** | Vectoriser le texte sérialisé du tableau | Vectoriser le texte + comprendre la structure |
| **Image** | ❌ Ignorer ou utiliser le texte alternatif (faible qualité) | GPT-4o décrit l'image → vectoriser la description + caractéristiques visuelles |

L'observation clé : **les images portent des informations que le texte ne peut pas capturer**. Un diagramme à barres, une photo de produit ou un diagramme d'architecture véhicule un sens qui se perd quand l'image est simplement ignorée ou décrite uniquement par le texte alternatif.

---

## Étape 2 : Charger le jeu de données de chunks

Le jeu de données contient **15 chunks** provenant de 5 documents, chacun avec des scores de récupération texte seul et multimodal :

```python
import pandas as pd

chunks = pd.read_csv("lab-083/multimodal_chunks.csv")
chunks["has_image"] = chunks["has_image"].astype(str).str.lower() == "true"
chunks["has_table"] = chunks["has_table"].astype(str).str.lower() == "true"

print(f"Total chunks: {len(chunks)}")
print(f"Chunk types: {chunks['chunk_type'].value_counts().to_dict()}")
print(f"Documents: {sorted(chunks['document'].unique())}")
print(f"\nDataset preview:")
print(chunks[["chunk_id", "document", "chunk_type", "has_image", "retrieval_score_text_only",
              "retrieval_score_multimodal"]].to_string(index=False))
```

**Sortie attendue :**

```
Total chunks: 15
Chunk types: {'text': 5, 'image': 6, 'table': 4}
Documents: ['investor_deck.pptx', 'product_catalog.docx', 'quarterly_report.pdf', 'sales_data.xlsx', 'training_manual.pdf']
```

| chunk_id | document | chunk_type | has_image | text_only | multimodal |
|----------|---------|-----------|-----------|-----------|------------|
| C01 | quarterly_report.pdf | text | False | 0.85 | 0.85 |
| C03 | quarterly_report.pdf | image | True | 0.15 | 0.82 |
| C05 | product_catalog.docx | image | True | 0.10 | 0.91 |
| ... | ... | ... | ... | ... | ... |

---

## Étape 3 : Comparer les scores texte seul vs multimodal

Analysez comment la récupération multimodale s'améliore par rapport au texte seul :

```python
print("Average retrieval scores by chunk type:")
for ctype in ["text", "table", "image"]:
    subset = chunks[chunks["chunk_type"] == ctype]
    text_avg = subset["retrieval_score_text_only"].mean()
    mm_avg = subset["retrieval_score_multimodal"].mean()
    improvement = mm_avg - text_avg
    print(f"  {ctype:>5}: text={text_avg:.3f}  multimodal={mm_avg:.3f}  "
          f"improvement={improvement:+.3f}")
```

**Sortie attendue :**

```
Average retrieval scores by chunk type:
   text: text=0.806  multimodal=0.806  improvement=+0.000
  table: text=0.780  multimodal=0.898  improvement=+0.117
  image: text=0.138  multimodal=0.853  improvement=+0.715
```

!!! tip "Observation"
    Les **chunks texte** ne voient aucune amélioration — ils sont déjà bien servis par les embeddings texte. Les **chunks tableau** gagnent +0.117 grâce à la compréhension structurelle. Les **chunks image** voient une amélioration massive de +0.715 — la récupération texte seul score seulement 0.138 en moyenne pour les images, tandis que le multimodal score 0.853. C'est la proposition de valeur principale du RAG multimodal.

---

## Étape 4 : Analyser les chunks avec images

Analyse approfondie des chunks contenant des images :

```python
image_chunks = chunks[chunks["has_image"] == True]
print(f"Image chunks: {len(image_chunks)}/{len(chunks)}")

print(f"\nImage chunk details:")
for _, c in image_chunks.iterrows():
    improvement = c["retrieval_score_multimodal"] - c["retrieval_score_text_only"]
    print(f"  {c['chunk_id']} ({c['document']}):")
    print(f"    Description: {c['image_description']}")
    print(f"    Text-only: {c['retrieval_score_text_only']:.2f} → Multimodal: {c['retrieval_score_multimodal']:.2f} "
          f"(+{improvement:.2f})")
```

**Sortie attendue :**

```
Image chunks: 6/15

Image chunk details:
  C03 (quarterly_report.pdf):
    Description: Bar chart showing Q1 revenue by region
    Text-only: 0.15 → Multimodal: 0.82 (+0.67)
  C05 (product_catalog.docx):
    Description: Photo of Alpine Explorer Tent with dimensions
    Text-only: 0.10 → Multimodal: 0.91 (+0.81)
  C08 (training_manual.pdf):
    Description: Diagram of tent assembly steps 1-5
    Text-only: 0.12 → Multimodal: 0.85 (+0.73)
  C09 (training_manual.pdf):
    Description: Photo showing correct stake placement
    Text-only: 0.08 → Multimodal: 0.79 (+0.71)
  C11 (investor_deck.pptx):
    Description: Pie chart of market share by competitor
    Text-only: 0.18 → Multimodal: 0.87 (+0.69)
  C15 (quarterly_report.pdf):
    Description: Line graph of monthly active users trend
    Text-only: 0.20 → Multimodal: 0.88 (+0.68)
```

---

## Étape 5 : Calculer les métriques d'amélioration

Calculez l'amélioration moyenne pour les chunks avec images :

```python
image_text_avg = image_chunks["retrieval_score_text_only"].mean()
image_mm_avg = image_chunks["retrieval_score_multimodal"].mean()
avg_improvement = image_mm_avg - image_text_avg

print(f"Image chunks — average scores:")
print(f"  Text-only:    {image_text_avg:.3f}")
print(f"  Multi-modal:  {image_mm_avg:.3f}")
print(f"  Improvement:  +{avg_improvement:.3f}")
print(f"  Multiplier:   {image_mm_avg/image_text_avg:.1f}x better")
```

**Sortie attendue :**

```
Image chunks — average scores:
  Text-only:    0.138
  Multi-modal:  0.853
  Improvement:  +0.715
  Multiplier:   6.2x better
```

```python
overall_text = chunks["retrieval_score_text_only"].mean()
overall_mm = chunks["retrieval_score_multimodal"].mean()
print(f"\nOverall retrieval scores:")
print(f"  Text-only:    {overall_text:.3f}")
print(f"  Multi-modal:  {overall_mm:.3f}")
print(f"  Improvement:  +{overall_mm - overall_text:.3f}")
```

!!! tip "Observation"
    La récupération multimodale est **6.2x meilleure** que le texte seul pour les chunks avec images. Même sur l'ensemble des 15 chunks (y compris ceux en texte seul), le score de récupération global s'améliore significativement car 40% des chunks (6/15) contiennent des images.

---

## Étape 6 : Analyse au niveau du document

Comparez l'impact multimodal par document :

```python
print("Retrieval improvement by document:")
for doc in sorted(chunks["document"].unique()):
    subset = chunks[chunks["document"] == doc]
    text_avg = subset["retrieval_score_text_only"].mean()
    mm_avg = subset["retrieval_score_multimodal"].mean()
    has_images = subset["has_image"].any()
    print(f"  {doc:>30}: text={text_avg:.3f}  mm={mm_avg:.3f}  "
          f"Δ={mm_avg-text_avg:+.3f}  images={'Yes' if has_images else 'No'}")
```

**Sortie attendue :**

```
Retrieval improvement by document:
            investor_deck.pptx: text=0.577  mm=0.840  Δ=+0.263  images=Yes
          product_catalog.docx: text=0.608  mm=0.838  Δ=+0.230  images=Yes
        quarterly_report.pdf: text=0.513  mm=0.850  Δ=+0.337  images=Yes
             sales_data.xlsx: text=0.820  mm=0.920  Δ=+0.100  images=No
           training_manual.pdf: text=0.427  mm=0.840  Δ=+0.413  images=Yes
```

!!! tip "Observation"
    Les documents avec images voient les plus grandes améliorations. Le **manuel de formation** bénéficie le plus (+0.413) car il contient des diagrammes d'assemblage et des photos essentiels pour répondre aux questions pratiques. Le **tableur de ventes** (sans images) bénéficie tout de même de la compréhension améliorée des tableaux (+0.100).

---

## 🐛 Exercice de correction de bugs

Le fichier `lab-083/broken_multimodal.py` contient **3 bugs** dans les fonctions d'analyse. Pouvez-vous les trouver et les corriger tous ?

Exécutez les auto-tests pour voir lesquels échouent :

```bash
python lab-083/broken_multimodal.py
```

Vous devriez voir **3 tests échoués**. Chaque test correspond à un bug :

| Test | Ce qu'il vérifie | Indice |
|------|---------------|------|
| Test 1 | Calcul de l'amélioration multimodale | Devrait calculer l'amélioration en utilisant les chunks image pour les deux scores, pas un mélange |
| Test 2 | Nombre de chunks avec images | Devrait vérifier `has_image`, pas `has_table` |
| Test 3 | Score multimodal moyen | Devrait utiliser `retrieval_score_multimodal`, pas `retrieval_score_text_only` |

Corrigez les 3 bugs, puis relancez. Quand vous voyez `All passed!`, c'est terminé !

---

## 🧠 Vérification des connaissances

??? question "**Q1 (Choix multiple) :** Pourquoi les chunks avec images scorent-ils mal avec la récupération texte seul ?"

    - A) Parce que les images sont toujours de basse qualité
    - B) Parce que les embeddings texte ne peuvent pas capturer l'information visuelle — les graphiques, photos et diagrammes ont un texte extractible minimal
    - C) Parce que les fichiers image sont trop volumineux pour être vectorisés
    - D) Parce que les modèles texte seul refusent de traiter les images

    ??? success "✅ Révéler la réponse"
        **Correct : B) Parce que les embeddings texte ne peuvent pas capturer l'information visuelle — les graphiques, photos et diagrammes ont un texte extractible minimal**

        Un diagramme à barres montrant « Chiffre d'affaires T1 par région » a très peu de texte extractible (peut-être des étiquettes d'axes), donc son embedding texte a presque aucun chevauchement sémantique avec une requête sur le chiffre d'affaires. Le RAG multimodal utilise GPT-4o vision pour *comprendre* le contenu du graphique et générer une description riche, produisant un embedding qui représente fidèlement les informations du graphique.

??? question "**Q2 (Choix multiple) :** Quel rôle joue GPT-4o vision dans un pipeline RAG multimodal ?"

    - A) Il génère la réponse finale à la requête de l'utilisateur
    - B) Il convertit les images en descriptions textuelles qui peuvent être vectorisées aux côtés du texte du document
    - C) Il remplace entièrement la base de données vectorielle
    - D) Il ne gère que l'OCR pour les documents numérisés

    ??? success "✅ Révéler la réponse"
        **Correct : B) Il convertit les images en descriptions textuelles qui peuvent être vectorisées aux côtés du texte du document**

        GPT-4o vision analyse chaque chunk image — graphiques, photos, diagrammes — et produit une description textuelle détaillée de ce que l'image contient. Cette description est ensuite vectorisée aux côtés du texte du document, permettant au système de récupération de trouver les images pertinentes quand un utilisateur pose une question. La description comble le fossé entre le contenu visuel et la récupération basée sur le texte.

??? question "**Q3 (Exécutez le lab) :** Combien de chunks contiennent des images (`has_image == True`) ?"

    Chargez [📥 `multimodal_chunks.csv`](https://github.com/lcarli/AI-LearningHub/raw/main/docs/docs/en/labs/lab-083/multimodal_chunks.csv) et comptez les lignes où `has_image == True`.

    ??? success "✅ Révéler la réponse"
        **6**

        6 des 15 chunks contiennent des images : C03 (diagramme à barres), C05 (photo de produit), C08 (diagramme d'assemblage), C09 (photo de placement de sardines), C11 (camembert) et C15 (graphique linéaire). Ils représentent 40% du corpus.

??? question "**Q4 (Exécutez le lab) :** Quelle est l'amélioration moyenne du score multimodal pour les chunks avec images par rapport à leurs scores texte seul ?"

    Pour les chunks où `has_image == True`, calculez `retrieval_score_multimodal.mean() - retrieval_score_text_only.mean()`.

    ??? success "✅ Révéler la réponse"
        **+0.715**

        Score moyen texte seul des chunks image : (0.15 + 0.10 + 0.12 + 0.08 + 0.18 + 0.20) ÷ 6 = **0.138**. Score multimodal moyen : (0.82 + 0.91 + 0.85 + 0.79 + 0.87 + 0.88) ÷ 6 = **0.853**. Amélioration = 0.853 − 0.138 = **+0.715**.

??? question "**Q5 (Exécutez le lab) :** Combien de chunks au total y a-t-il dans le jeu de données ?"

    Comptez toutes les lignes du jeu de données.

    ??? success "✅ Révéler la réponse"
        **15**

        Le jeu de données contient 15 chunks répartis sur 5 documents : quarterly_report.pdf (3), product_catalog.docx (3), training_manual.pdf (2), investor_deck.pptx (3), sales_data.xlsx (1), product_catalog.docx (1), quarterly_report.pdf (1) et sales_data.xlsx (1) — totalisant 15 chunks.

---

## Résumé

| Sujet | Ce que vous avez appris |
|-------|-----------------|
| RAG multimodal | Étend le RAG texte avec la compréhension visuelle des images, graphiques et diagrammes |
| GPT-4o Vision | Convertit les images en descriptions textuelles riches pour la vectorisation et la récupération |
| Chunks avec images | 6 des 15 chunks contiennent des images — 40% du corpus |
| Amélioration des scores | Les chunks image passent de 0.138 (texte seul) à 0.853 (multimodal) — gain de +0.715 |
| Chunks texte | Aucune amélioration nécessaire — déjà bien servis par les embeddings texte |
| Chunks tableau | Amélioration modérée (+0.117) grâce à la compréhension structurelle |
| Impact global | La récupération multimodale améliore significativement la qualité pour les documents visuellement riches |

---

## Prochaines étapes

- Explorez [Azure AI Document Intelligence](https://learn.microsoft.com/azure/ai-services/document-intelligence/) pour l'analyse de documents de production
- Essayez de construire un pipeline RAG multimodal avec le [support multimodal de LangChain](https://python.langchain.com/docs/how_to/multimodal_inputs/)
- Consultez le **[Lab 080](lab-080-markitdown-mcp.md)** pour la conversion document-vers-Markdown comme étape de prétraitement
