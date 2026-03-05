---
tags: [fabric, ai-functions, batch-enrichment, etl, python, pandas]
---
# Lab 053 : Fabric IQ — Enrichissement IA par lots avec AI Functions

<div class="lab-meta">
  <span><strong>Niveau :</strong> <span class="level-badge level-300">L300</span></span>
  <span><strong>Parcours :</strong> Tous les parcours</span>
  <span><strong>Durée :</strong> ~90 min</span>
  <span><strong>💰 Coût :</strong> <span class="level-badge cost-free">Gratuit</span> — Utilise des fonctions IA mock en local (capacité Fabric optionnelle)</span>
</div>

## Ce que vous apprendrez

- Ce que sont les **Fabric AI Functions** et comment elles intègrent l'IA dans les workflows Spark/pandas (`ai.classify`, `ai.summarize`, `ai.extract`, `ai.embed`)
- Concevoir des **pipelines ETL IA** qui enrichissent les données tabulaires avec des transformations alimentées par LLM
- Traiter les données par **lots** — en appliquant la classification, le résumé et l'extraction d'entités à des DataFrames entiers
- Construire et tester avec des **fonctions IA mock** en local, puis basculer vers les vrais appels Fabric `ai.*()` en production

## Introduction

![AI ETL Pipeline](../../assets/diagrams/fabric-ai-etl.svg)

Les pipelines ETL traditionnels déplacent et transforment des données structurées — nettoyage, filtrage, jointure, agrégation. Les **AI Functions** ajoutent une nouvelle dimension : elles vous permettent d'appeler un LLM sur chaque ligne d'un DataFrame, en traitant la classification, le résumé et l'extraction comme des opérations natives sur les colonnes.

Dans Microsoft Fabric, les fonctions `ai.*()` s'exécutent directement dans les notebooks Spark. Vous écrivez `df["sentiment"] = ai.classify(df["text"], ["positive", "neutral", "negative"])` et Fabric gère le regroupement par lots, la limitation de débit et le routage du modèle en arrière-plan.

### Le scénario

Vous êtes un **Data Engineer** chez OutdoorGear Inc. L'équipe produit a collecté **20 avis clients** sur des équipements de plein air et souhaite que vous construisiez un pipeline d'enrichissement qui :

1. **Classifie** le sentiment de chaque avis (positif / neutre / négatif)
2. **Résume** chaque avis en un court extrait
3. **Extrait** les entités clés (avantages et inconvénients) du texte de l'avis
4. **Encode** le texte de l'avis pour la recherche sémantique en aval *(abordé conceptuellement)*

Comme vous développez en local, vous utiliserez des **fonctions IA mock** qui imitent le comportement des appels `ai.*()` de Fabric. Une fois le pipeline validé, basculer vers les vrais modèles ne nécessite que de modifier les implémentations des fonctions.

!!! info "Mock vs. AI Functions réelles"
    Ce lab utilise des fonctions mock (basées sur des règles, sans LLM nécessaire) afin que tout le monde puisse suivre sans capacité Fabric. Les fonctions mock produisent des résultats déterministes qui correspondent aux sorties attendues. En production dans Fabric, vous remplaceriez ces mocks par `ai.classify()`, `ai.summarize()`, etc.

## Prérequis

| Prérequis | Pourquoi |
|---|---|
| Python 3.10+ | Exécuter le pipeline d'enrichissement |
| Bibliothèque `pandas` | Opérations sur les DataFrames |
| (Optionnel) Capacité Microsoft Fabric | Pour les vraies fonctions `ai.*()` |

```bash
pip install pandas
```

---

!!! tip "Démarrage rapide avec GitHub Codespaces"
    [![Open in GitHub Codespaces](https://github.com/codespaces/badge.svg)](https://codespaces.new/lcarli/AI-LearningHub?quickstart=1)

    Toutes les dépendances sont pré-installées dans le devcontainer.


## 📦 Fichiers de support

!!! note "Téléchargez ces fichiers avant de commencer le lab"
    Enregistrez tous les fichiers dans un dossier `lab-053/` de votre répertoire de travail.

| Fichier | Description | Télécharger |
|------|-------------|----------|
| `broken_pipeline.py` | Exercice de correction de bugs (3 bugs + auto-tests) | [📥 Télécharger](https://github.com/lcarli/AI-LearningHub/raw/main/docs/docs/en/labs/lab-053/broken_pipeline.py) |
| `product_reviews.csv` | Jeu de données | [📥 Télécharger](https://github.com/lcarli/AI-LearningHub/raw/main/docs/docs/en/labs/lab-053/product_reviews.csv) |

---

## Étape 1 : Comprendre les Fabric AI Functions

Les Fabric AI Functions sont des opérations natives qui appliquent les capacités des LLM aux colonnes de DataFrames. Elles abstraient l'ingénierie de prompts, le regroupement par lots et la gestion des API :

| Fonction | Signature | Description |
|----------|-----------|-------------|
| `ai.classify()` | `ai.classify(column, categories)` | Classifie le texte dans l'une des catégories fournies en utilisant un LLM |
| `ai.summarize()` | `ai.summarize(column, max_length=None)` | Génère un résumé concis de chaque valeur textuelle |
| `ai.extract()` | `ai.extract(column, fields)` | Extrait des champs structurés (entités, mots-clés) du texte |
| `ai.embed()` | `ai.embed(column, model=None)` | Génère des embeddings vectoriels pour la recherche par similarité en aval |

### Comment elles fonctionnent dans Fabric

Dans un vrai notebook Spark de Fabric, vous écririez :

```python
from synapse.ml.fabric import ai

# Classify sentiment in one line
df["sentiment"] = ai.classify(df["review_text"], ["positive", "neutral", "negative"])

# Summarize reviews
df["summary"] = ai.summarize(df["review_text"], max_length=50)
```

Fabric gère :

- **Le regroupement par lots** — regroupe les lignes en tailles de lots optimales pour le point de terminaison du modèle
- **La limitation de débit** — respecte automatiquement les limites de tokens par minute
- **La gestion des erreurs** — réessaie les échecs transitoires avec un backoff exponentiel
- **Le routage du modèle** — utilise le modèle par défaut de l'espace de travail ou un modèle spécifié

!!! tip "Pourquoi commencer par les mocks ?"
    Construire avec des mocks vous permet de valider la logique du pipeline, les types de données et les consommateurs en aval *avant* de dépenser du calcul sur de vrais appels LLM. C'est une bonne pratique pour tout pipeline ETL IA.

---

## Étape 2 : Charger le jeu de données d'avis

Le jeu de données contient **20 avis produits** pour les produits OutdoorGear :

```python
import pandas as pd

reviews = pd.read_csv("lab-053/product_reviews.csv")
print(f"Total reviews: {len(reviews)}")
print(f"Unique products: {reviews['product_name'].nunique()}")
print(f"Rating range: {reviews['rating'].min()} – {reviews['rating'].max()}")
print(f"Average rating: {reviews['rating'].mean():.2f}")
print(f"\nReviews per product:")
print(reviews.groupby("product_name").size().sort_values(ascending=False))
```

**Sortie attendue :**

```
Total reviews: 20
Unique products: 7
Rating range: 1 – 5
Average rating: 3.70

Reviews per product:
product_name
Alpine Explorer Tent       5
Peak Performer Boots       3
Explorer Pro Backpack      3
TrailMaster X4 Tent        3
CozyNights Sleeping Bag    2
DayTripper Pack            2
Summit Water Bottle        2
```

Prenez un moment pour explorer les données :

```python
print(reviews[["review_id", "product_name", "rating", "review_text"]].head(5).to_string(index=False))
```

---

## Étape 3 : Implémenter les fonctions IA mock

Au lieu d'appeler un vrai LLM, nous créons des fonctions mock déterministes qui imitent le comportement de `ai.*()` de Fabric :

### 3a — `mock_classify(rating)`

Classifie le sentiment en fonction de la note numérique :

```python
def mock_classify(rating: int) -> str:
    """Mock ai.classify() — maps rating to sentiment."""
    if rating >= 4:
        return "positive"
    elif rating == 3:
        return "neutral"
    else:
        return "negative"
```

- Note ≥ 4 → `"positive"`
- Note = 3 → `"neutral"`
- Note ≤ 2 → `"negative"`

### 3b — `mock_summarize(text)`

Retourne une version tronquée du texte de l'avis :

```python
def mock_summarize(text: str) -> str:
    """Mock ai.summarize() — returns first 50 characters."""
    if len(text) <= 50:
        return text
    return text[:50] + "..."
```

### 3c — `mock_extract(text)`

Extrait des mots-clés simples en recherchant des mots indicateurs positifs/négatifs :

```python
POSITIVE_WORDS = {"amazing", "great", "best", "perfect", "incredible", "love",
                  "good", "solid", "comfortable", "warm", "durable"}
NEGATIVE_WORDS = {"broke", "terrible", "disappointed", "cheap", "thin",
                  "cramped", "snags", "cracked"}

def mock_extract(text: str) -> dict:
    """Mock ai.extract() — finds pros and cons keywords."""
    words = set(text.lower().split())
    pros = sorted(words & POSITIVE_WORDS)
    cons = sorted(words & NEGATIVE_WORDS)
    return {"pros": pros, "cons": cons}
```

!!! tip "Réel vs. Mock"
    En production dans Fabric, `ai.classify()` envoie le texte de l'avis à un LLM avec les labels candidats — il comprend le contexte, le sarcasme et les nuances. Notre mock utilise la note comme proxy, ce qui est une heuristique raisonnable pour ce jeu de données mais ne se généraliserait pas à du texte non étiqueté.

---

## Étape 4 : Exécuter le pipeline d'enrichissement

Appliquez les fonctions mock à chaque ligne du DataFrame :

```python
# Classify sentiment
reviews["sentiment"] = reviews["rating"].apply(mock_classify)

# Summarize reviews
reviews["summary"] = reviews["review_text"].apply(mock_summarize)

# Extract entities
reviews["entities"] = reviews["review_text"].apply(mock_extract)

print("Enriched DataFrame columns:", list(reviews.columns))
print(f"\nSentiment distribution:")
print(reviews["sentiment"].value_counts())
```

**Sortie attendue :**

```
Enriched DataFrame columns: ['review_id', 'product_id', 'product_name', 'category',
                              'rating', 'review_text', 'sentiment', 'summary', 'entities']

Sentiment distribution:
positive    13
neutral      4
negative     3
```

### Vérifier les résultats

```python
# Show a sample of enriched data
sample_cols = ["review_id", "product_name", "rating", "sentiment", "summary"]
print(reviews[sample_cols].head(6).to_string(index=False))
```

**Attendu :**

| review_id | product_name | rating | sentiment | summary |
|-----------|-------------|--------|-----------|---------|
| R001 | Alpine Explorer Tent | 5 | positive | Amazing tent! Held up perfectly in heavy rain. Se... |
| R002 | Alpine Explorer Tent | 4 | positive | Solid tent but a bit heavy for long hikes. Great ... |
| R003 | Alpine Explorer Tent | 5 | positive | Best tent I've ever owned. Worth every penny. |
| R004 | Alpine Explorer Tent | 3 | neutral | Decent tent but nothing special at this price poi... |
| R005 | Alpine Explorer Tent | 4 | positive | Good quality materials. Survived a storm with no ... |
| R006 | TrailMaster X4 Tent | 4 | positive | Great ventilation and the zipper is smooth. Sligh... |

### Répartition des sentiments

| Sentiment | Nombre | Notes |
|-----------|-------|---------|
| Positif (note ≥ 4) | 13 | Notes 4 et 5 |
| Neutre (note = 3) | 4 | Note 3 |
| Négatif (note ≤ 2) | 3 | Notes 1 et 2 |

---

## Étape 5 : Analyser les données enrichies

Maintenant que les avis sont enrichis, analysez-les pour en extraire des informations commerciales :

### 5a — Note moyenne par sentiment

```python
print("Average rating by sentiment:")
print(reviews.groupby("sentiment")["rating"].mean().to_string())
```

**Attendu :**

```
negative    1.666667
neutral     3.000000
positive    4.384615
```

### 5b — Analyse au niveau produit

```python
product_stats = reviews.groupby("product_name").agg(
    review_count=("review_id", "count"),
    avg_rating=("rating", "mean"),
).sort_values("review_count", ascending=False)

print(f"Overall average rating: {reviews['rating'].mean():.2f}")
print(f"\nMost reviewed product: {product_stats.index[0]} ({product_stats.iloc[0]['review_count']:.0f} reviews)")
print(f"\nProduct statistics:")
print(product_stats.to_string())
```

**Attendu :**

```
Overall average rating: 3.70

Most reviewed product: Alpine Explorer Tent (5 reviews)

Product statistics:
                         review_count  avg_rating
product_name
Alpine Explorer Tent                5    4.200000
Explorer Pro Backpack               3    3.666667
Peak Performer Boots                3    4.000000
TrailMaster X4 Tent                 3    3.333333
CozyNights Sleeping Bag             2    4.000000
DayTripper Pack                     2    3.500000
Summit Water Bottle                 2    2.500000
```

### 5c — Produit le mieux noté (2+ avis)

```python
multi_review = product_stats[product_stats["review_count"] >= 2]
best = multi_review.sort_values("avg_rating", ascending=False).iloc[0]
print(f"Highest-rated product (2+ reviews): {multi_review.sort_values('avg_rating', ascending=False).index[0]}")
print(f"  Average rating: {best['avg_rating']:.2f}")
```

**Attendu :**

```
Highest-rated product (2+ reviews): Alpine Explorer Tent
  Average rating: 4.20
```

### 5d — Sentiment par catégorie

```python
print("Sentiment distribution by category:")
print(pd.crosstab(reviews["category"], reviews["sentiment"]))
```

---

## Étape 6 : Considérations de production

Lors du passage des mocks aux vraies Fabric AI Functions, tenez compte de ces facteurs :

### Taille de lot

| Taille de lot | Compromis |
|------------|-----------|
| Petite (1–10 lignes) | Latence plus élevée par ligne ; plus facile à déboguer |
| Moyenne (50–100 lignes) | Bon équilibre entre débit et coût |
| Grande (500+ lignes) | Débit maximal ; risque de délais d'expiration et de limites de débit |

Les fonctions `ai.*()` de Fabric gèrent le regroupement par lots automatiquement, mais vous pouvez l'ajuster :

```python
# In Fabric, control batch behavior via configuration
spark.conf.set("spark.synapse.ml.ai.batchSize", 50)
```

### Passage Mock → Réel

L'avantage clé de notre approche mock-first : basculer vers les vraies fonctions ne nécessite que de modifier les implémentations des fonctions :

```python
# ── Mock (local development) ────────────────────
reviews["sentiment"] = reviews["rating"].apply(mock_classify)

# ── Real Fabric (production) ────────────────────
# from synapse.ml.fabric import ai
# reviews["sentiment"] = ai.classify(reviews["review_text"],
#                                    ["positive", "neutral", "negative"])
```

### Sensibilisation aux coûts

| Facteur | Impact |
|--------|--------|
| Nombre de tokens | Chaque avis consomme des tokens d'entrée ; les avis plus longs coûtent plus cher |
| Choix du modèle | GPT-4o vs. GPT-4o-mini — différence de coût de 10× |
| Appels redondants | Mettez en cache les résultats pour éviter de retraiter les lignes inchangées |
| Nombre de colonnes | Chaque appel `ai.*()` est une invocation LLM distincte par ligne |

!!! warning "Astuce coût"
    Pour 20 avis, le coût est négligeable. Pour 200 000 avis, une seule colonne `ai.classify()` pourrait coûter 50 $+ avec GPT-4o. Prototypez toujours avec un échantillon, validez les résultats, puis montez en charge.

---

## 🐛 Exercice de correction de bugs

Le fichier `lab-053/broken_pipeline.py` contient **3 bugs** dans les fonctions d'enrichissement IA. Pouvez-vous les trouver et les corriger tous ?

Exécutez les auto-tests pour voir lesquels échouent :

```bash
python lab-053/broken_pipeline.py
```

Vous devriez voir **3 tests échoués**. Chaque test correspond à un bug :

| Test | Ce qu'il vérifie | Indice |
|------|---------------|------|
| Test 1 | Seuils de classification des sentiments | La note 3 devrait être neutre, pas positive |
| Test 2 | Regroupement des avis par produit | Devrait grouper par `product_name`, pas par `review_id` |
| Test 3 | Note moyenne filtrée par sentiment | Doit filtrer le DataFrame avant de calculer la moyenne |

Corrigez les 3 bugs, puis relancez. Quand vous voyez `🎉 All 3 tests passed`, c'est terminé !

---


## 🧠 Vérification des connaissances

??? question "**Q1 (Choix multiple) :** Que fait `ai.classify()` dans les Fabric AI Functions ?"

    - A) Découpe le texte en phrases pour le traitement NLP
    - B) Classifie le texte dans des catégories prédéfinies en utilisant un LLM
    - C) Entraîne un modèle de classification personnalisé sur vos données
    - D) Convertit le texte en vecteurs de caractéristiques numériques

    ??? success "✅ Révéler la réponse"
        **Correct : B) Classifie le texte dans des catégories prédéfinies en utilisant un LLM**

        `ai.classify()` envoie chaque valeur textuelle à un LLM avec les labels candidats que vous fournissez (par ex., `["positive", "neutral", "negative"]`). Le LLM retourne le label le plus approprié. Il n'entraîne pas de modèle — il utilise les connaissances existantes du LLM via l'apprentissage en contexte.

??? question "**Q2 (Choix multiple) :** Pourquoi la taille de lot est-elle importante lors de l'utilisation des AI Functions à grande échelle ?"

    - A) Les lots plus grands produisent toujours des résultats plus précis
    - B) La taille de lot détermine quel modèle LLM est utilisé
    - C) Équilibre le débit, le coût et le respect des limites de débit
    - D) Les lots plus petits utilisent moins de tokens par ligne

    ??? success "✅ Révéler la réponse"
        **Correct : C) Équilibre le débit, le coût et le respect des limites de débit**

        La taille de lot affecte le nombre de lignes envoyées au point de terminaison LLM par requête. Trop petit = surcharge de latence élevée ; trop grand = risque d'erreurs de limitation de débit et de délais d'expiration. La taille de lot optimale équilibre le débit (lignes/seconde), le coût (tokens/requête) et les limites de débit de l'API.

??? question "**Q3 (Exécuter le lab) :** Combien d'avis ont un sentiment positif (note ≥ 4) ?"

    Appliquez `mock_classify()` à la colonne de notes et comptez les valeurs `"positive"`.

    ??? success "✅ Révéler la réponse"
        **13**

        Les notes de 4 ou 5 correspondent à `"positive"`. Il y a 9 avis avec la note 4 et 4 avis avec la note 5, soit un total de **13 avis positifs** sur 20.

??? question "**Q4 (Exécuter le lab) :** Quel produit a le plus d'avis ?"

    Groupez par `product_name` et comptez les lignes.

    ??? success "✅ Révéler la réponse"
        **Alpine Explorer Tent — 5 avis**

        Alpine Explorer Tent (P001) a les avis R001–R005, ce qui en fait le produit le plus évalué. Les produits suivants les plus évalués (Peak Performer Boots, Explorer Pro Backpack, TrailMaster X4 Tent) ont chacun 3 avis.

??? question "**Q5 (Exécuter le lab) :** Quelle est la note moyenne sur l'ensemble des 20 avis ?"

    Calculez `reviews["rating"].mean()`.

    ??? success "✅ Révéler la réponse"
        **3.70**

        Somme de toutes les notes : 5+4+5+3+4+4+2+4+5+4+3+5+4+2+4+3+5+3+4+1 = 74. Moyenne = 74 ÷ 20 = **3,70**.

---

## Résumé

| Sujet | Ce que vous avez appris |
|-------|-----------------|
| AI Functions | `ai.classify`, `ai.summarize`, `ai.extract`, `ai.embed` comme opérations sur les DataFrames |
| Développement mock-first | Construire et valider la logique du pipeline avant d'utiliser de vrais appels LLM |
| Enrichissement par lots | Appliquer des transformations IA à chaque ligne d'un jeu de données |
| Analyse de sentiment | Classification basée sur la note : positif (≥4), neutre (3), négatif (≤2) |
| Analytique produit | Analyse par regroupement sur les données enrichies pour des insights commerciaux |
| Préparation à la production | Taille de lot, coût, mise en cache et patterns de passage mock vers réel |

---

## Prochaines étapes

- **[Lab 051](lab-051-fabric-iq-event-streams.md)** *(bientôt disponible)* — Fabric IQ — Traitement de flux d'événements en temps réel
- **[Lab 052](lab-052-fabric-iq-nl-to-sql.md)** *(bientôt disponible)* — Fabric IQ — Langage naturel vers SQL avec l'IA
