---
tags: [fabric, ai-functions, batch-enrichment, etl, python, pandas]
---
# Lab 053: Fabric IQ — Batch AI Enrichment with AI Functions

<div class="lab-meta">
  <span><strong>Level:</strong> <span class="level-badge level-300">L300</span></span>
  <span><strong>Path:</strong> All paths</span>
  <span><strong>Time:</strong> ~90 min</span>
  <span><strong>💰 Cost:</strong> <span class="level-badge cost-free">Free</span> — Uses mock AI functions locally (Fabric capacity optional)</span>
</div>

!!! info "Traduction en cours"
    Ce lab est en cours de traduction. Le contenu ci-dessous est en anglais.



## What You'll Learn

- What **Fabric AI Functions** are and how they integrate AI into Spark/pandas workflows (`ai.classify`, `ai.summarize`, `ai.extract`, `ai.embed`)
- Design **AI ETL pipelines** that enrich tabular data with LLM-powered transformations
- Process data in **batch** — applying classification, summarization, and entity extraction to entire DataFrames
- Build and test with **mock AI functions** locally, then swap to real Fabric `ai.*()` calls in production

## Introduction

![AI ETL Pipeline](../../assets/diagrams/fabric-ai-etl.svg)

Traditional ETL pipelines move and transform structured data — clean, filter, join, aggregate. **AI Functions** add a new dimension: they let you call an LLM on every row of a DataFrame, treating classification, summarization, and extraction as native column operations.

In Microsoft Fabric, the `ai.*()` functions run directly inside Spark notebooks. You write `df["sentiment"] = ai.classify(df["text"], ["positive", "neutral", "negative"])` and Fabric handles batching, rate-limiting, and model routing behind the scenes.

### The Scenario

You are a **Data Engineer** at OutdoorGear Inc. The product team has collected **20 customer reviews** for outdoor gear and wants you to build an enrichment pipeline that:

1. **Classifies** each review's sentiment (positive / neutral / negative)
2. **Summarizes** each review into a short snippet
3. **Extracts** key entities (pros and cons) from the review text
4. **Embeds** the review text for downstream semantic search *(discussed conceptually)*

Because you're developing locally, you'll use **mock AI functions** that mimic the behavior of Fabric's `ai.*()` calls. Once the pipeline is validated, swapping to real models requires changing only the function implementations.

!!! info "Mock vs. Real AI Functions"
    This lab uses mock functions (rule-based, no LLM needed) so anyone can follow along without a Fabric capacity. The mock functions produce deterministic results that match the expected outputs. In production Fabric, you would replace these mocks with `ai.classify()`, `ai.summarize()`, etc.

## Prerequisites

| Requirement | Why |
|---|---|
| Python 3.10+ | Run the enrichment pipeline |
| `pandas` library | DataFrame operations |
| (Optional) Microsoft Fabric capacity | For real `ai.*()` functions |

```bash
pip install pandas
```

---

!!! tip "Quick Start with GitHub Codespaces"
    [![Open in GitHub Codespaces](https://github.com/codespaces/badge.svg)](https://codespaces.new/lcarli/AI-LearningHub?quickstart=1)

    All dependencies are pre-installed in the devcontainer.


## 📦 Supporting Files

!!! note "Download these files before starting the lab"
    Save all files to a `lab-053/` folder in your working directory.

| File | Description | Download |
|------|-------------|----------|
| `broken_pipeline.py` | Bug-fix exercise (3 bugs + self-tests) | [📥 Download](https://github.com/lcarli/AI-LearningHub/raw/main/docs/docs/en/labs/lab-053/broken_pipeline.py) |
| `product_reviews.csv` | Dataset | [📥 Download](https://github.com/lcarli/AI-LearningHub/raw/main/docs/docs/en/labs/lab-053/product_reviews.csv) |

---

## Step 1: Understanding Fabric AI Functions

Fabric AI Functions are native operations that apply LLM capabilities to DataFrame columns. They abstract away prompt engineering, batching, and API management:

| Function | Signature | Description |
|----------|-----------|-------------|
| `ai.classify()` | `ai.classify(column, categories)` | Classifies text into one of the provided categories using an LLM |
| `ai.summarize()` | `ai.summarize(column, max_length=None)` | Generates a concise summary of each text value |
| `ai.extract()` | `ai.extract(column, fields)` | Extracts structured fields (entities, keywords) from text |
| `ai.embed()` | `ai.embed(column, model=None)` | Generates vector embeddings for downstream similarity search |

### How They Work in Fabric

In a real Fabric Spark notebook, you'd write:

```python
from synapse.ml.fabric import ai

# Classify sentiment in one line
df["sentiment"] = ai.classify(df["review_text"], ["positive", "neutral", "negative"])

# Summarize reviews
df["summary"] = ai.summarize(df["review_text"], max_length=50)
```

Fabric handles:

- **Batching** — groups rows into optimal batch sizes for the model endpoint
- **Rate limiting** — respects token-per-minute limits automatically
- **Error handling** — retries transient failures with exponential backoff
- **Model routing** — uses the workspace's default model or a specified one

!!! tip "Why Mock First?"
    Building with mocks lets you validate pipeline logic, data types, and downstream consumers *before* spending compute on real LLM calls. This is a best practice for any AI ETL pipeline.

---

## Step 2: Load the Reviews Dataset

The dataset contains **20 product reviews** for OutdoorGear products:

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

**Expected output:**

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

Take a moment to explore the data:

```python
print(reviews[["review_id", "product_name", "rating", "review_text"]].head(5).to_string(index=False))
```

---

## Step 3: Implement Mock AI Functions

Instead of calling a real LLM, we create deterministic mock functions that mimic Fabric's `ai.*()` behavior:

### 3a — `mock_classify(rating)`

Classifies sentiment based on the numeric rating:

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

- Rating ≥ 4 → `"positive"`
- Rating = 3 → `"neutral"`
- Rating ≤ 2 → `"negative"`

### 3b — `mock_summarize(text)`

Returns a truncated version of the review text:

```python
def mock_summarize(text: str) -> str:
    """Mock ai.summarize() — returns first 50 characters."""
    if len(text) <= 50:
        return text
    return text[:50] + "..."
```

### 3c — `mock_extract(text)`

Extracts simple keywords by scanning for positive/negative indicator words:

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

!!! tip "Real vs. Mock"
    In production Fabric, `ai.classify()` sends the review text to an LLM with the candidate labels — it understands context, sarcasm, and nuance. Our mock uses the rating as a proxy, which is a reasonable heuristic for this dataset but wouldn't generalize to unlabeled text.

---

## Step 4: Run the Enrichment Pipeline

Apply the mock functions to every row in the DataFrame:

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

**Expected output:**

```
Enriched DataFrame columns: ['review_id', 'product_id', 'product_name', 'category',
                              'rating', 'review_text', 'sentiment', 'summary', 'entities']

Sentiment distribution:
positive    13
neutral      4
negative     3
```

### Verify the Results

```python
# Show a sample of enriched data
sample_cols = ["review_id", "product_name", "rating", "sentiment", "summary"]
print(reviews[sample_cols].head(6).to_string(index=False))
```

**Expected:**

| review_id | product_name | rating | sentiment | summary |
|-----------|-------------|--------|-----------|---------|
| R001 | Alpine Explorer Tent | 5 | positive | Amazing tent! Held up perfectly in heavy rain. Se... |
| R002 | Alpine Explorer Tent | 4 | positive | Solid tent but a bit heavy for long hikes. Great ... |
| R003 | Alpine Explorer Tent | 5 | positive | Best tent I've ever owned. Worth every penny. |
| R004 | Alpine Explorer Tent | 3 | neutral | Decent tent but nothing special at this price poi... |
| R005 | Alpine Explorer Tent | 4 | positive | Good quality materials. Survived a storm with no ... |
| R006 | TrailMaster X4 Tent | 4 | positive | Great ventilation and the zipper is smooth. Sligh... |

### Sentiment Breakdown

| Sentiment | Count | Ratings |
|-----------|-------|---------|
| Positive (rating ≥ 4) | 13 | Ratings 4 and 5 |
| Neutral (rating = 3) | 4 | Rating 3 |
| Negative (rating ≤ 2) | 3 | Ratings 1 and 2 |

---

## Step 5: Analyze Enriched Data

Now that the reviews are enriched, analyze them to extract business insights:

### 5a — Average Rating by Sentiment

```python
print("Average rating by sentiment:")
print(reviews.groupby("sentiment")["rating"].mean().to_string())
```

**Expected:**

```
negative    1.666667
neutral     3.000000
positive    4.384615
```

### 5b — Product-Level Analysis

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

**Expected:**

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

### 5c — Best-Rated Product (2+ reviews)

```python
multi_review = product_stats[product_stats["review_count"] >= 2]
best = multi_review.sort_values("avg_rating", ascending=False).iloc[0]
print(f"Highest-rated product (2+ reviews): {multi_review.sort_values('avg_rating', ascending=False).index[0]}")
print(f"  Average rating: {best['avg_rating']:.2f}")
```

**Expected:**

```
Highest-rated product (2+ reviews): Alpine Explorer Tent
  Average rating: 4.20
```

### 5d — Sentiment by Category

```python
print("Sentiment distribution by category:")
print(pd.crosstab(reviews["category"], reviews["sentiment"]))
```

---

## Step 6: Production Considerations

When moving from mocks to real Fabric AI Functions, consider these factors:

### Batch Size

| Batch Size | Trade-off |
|------------|-----------|
| Small (1–10 rows) | Higher latency per row; easier to debug |
| Medium (50–100 rows) | Good balance of throughput and cost |
| Large (500+ rows) | Maximum throughput; risk of timeouts and rate limits |

Fabric's `ai.*()` functions handle batching automatically, but you can tune it:

```python
# In Fabric, control batch behavior via configuration
spark.conf.set("spark.synapse.ml.ai.batchSize", 50)
```

### Mock → Real Swap

The key advantage of our mock-first approach: swapping to real functions requires changing only the function implementations:

```python
# ── Mock (local development) ────────────────────
reviews["sentiment"] = reviews["rating"].apply(mock_classify)

# ── Real Fabric (production) ────────────────────
# from synapse.ml.fabric import ai
# reviews["sentiment"] = ai.classify(reviews["review_text"],
#                                    ["positive", "neutral", "negative"])
```

### Cost Awareness

| Factor | Impact |
|--------|--------|
| Token count | Each review consumes input tokens; longer reviews cost more |
| Model choice | GPT-4o vs. GPT-4o-mini — 10× cost difference |
| Redundant calls | Cache results to avoid re-processing unchanged rows |
| Column count | Each `ai.*()` call is a separate LLM invocation per row |

!!! warning "Cost Tip"
    For 20 reviews, cost is negligible. For 200,000 reviews, a single `ai.classify()` column could cost $50+ with GPT-4o. Always prototype with a sample, validate results, then scale.

---

## 🐛 Bug-Fix Exercise

The file `lab-053/broken_pipeline.py` has **3 bugs** in the AI enrichment functions. Can you find and fix them all?

Run the self-tests to see which ones fail:

```bash
python lab-053/broken_pipeline.py
```

You should see **3 failed tests**. Each test corresponds to one bug:

| Test | What it checks | Hint |
|------|---------------|------|
| Test 1 | Sentiment classification thresholds | Rating 3 should be neutral, not positive |
| Test 2 | Reviews-per-product grouping | Should group by `product_name`, not `review_id` |
| Test 3 | Average rating filtered by sentiment | Must filter the DataFrame before computing the mean |

Fix all 3 bugs, then re-run. When you see `🎉 All 3 tests passed`, you're done!

---


## 🧠 Knowledge Check

??? question "**Q1 (Multiple Choice):** What does `ai.classify()` do in Fabric AI Functions?"

    - A) Splits text into sentences for NLP processing
    - B) Classifies text into predefined categories using an LLM
    - C) Trains a custom classification model on your data
    - D) Converts text to numeric feature vectors

    ??? success "✅ Reveal Answer"
        **Correct: B) Classifies text into predefined categories using an LLM**

        `ai.classify()` sends each text value to an LLM along with the candidate labels you provide (e.g., `["positive", "neutral", "negative"]`). The LLM returns the best-matching label. It does not train a model — it uses the LLM's existing knowledge via in-context learning.

??? question "**Q2 (Multiple Choice):** Why is batch size important when using AI Functions at scale?"

    - A) Larger batches always produce more accurate results
    - B) Batch size determines which LLM model is used
    - C) Balances throughput, cost, and rate-limit compliance
    - D) Smaller batches use fewer tokens per row

    ??? success "✅ Reveal Answer"
        **Correct: C) Balances throughput, cost, and rate-limit compliance**

        Batch size affects how many rows are sent to the LLM endpoint per request. Too small = high latency overhead; too large = risk of rate-limit errors and timeouts. The optimal batch size balances throughput (rows/second), cost (tokens/request), and API rate limits.

??? question "**Q3 (Run the Lab):** How many reviews have a positive sentiment (rating ≥ 4)?"

    Apply `mock_classify()` to the rating column and count the `"positive"` values.

    ??? success "✅ Reveal Answer"
        **13**

        Ratings of 4 or 5 map to `"positive"`. There are 9 reviews with rating 4 and 4 reviews with rating 5, totaling **13 positive reviews** out of 20.

??? question "**Q4 (Run the Lab):** Which product has the most reviews?"

    Group by `product_name` and count the rows.

    ??? success "✅ Reveal Answer"
        **Alpine Explorer Tent — 5 reviews**

        Alpine Explorer Tent (P001) has reviews R001–R005, making it the most-reviewed product. The next most-reviewed products (Peak Performer Boots, Explorer Pro Backpack, TrailMaster X4 Tent) each have 3 reviews.

??? question "**Q5 (Run the Lab):** What is the average rating across all 20 reviews?"

    Compute `reviews["rating"].mean()`.

    ??? success "✅ Reveal Answer"
        **3.70**

        Sum of all ratings: 5+4+5+3+4+4+2+4+5+4+3+5+4+2+4+3+5+3+4+1 = 74. Average = 74 ÷ 20 = **3.70**.

---

## Summary

| Topic | What You Learned |
|-------|-----------------|
| AI Functions | `ai.classify`, `ai.summarize`, `ai.extract`, `ai.embed` as DataFrame operations |
| Mock-First Development | Build and validate pipeline logic before using real LLM calls |
| Batch Enrichment | Apply AI transformations to every row of a dataset |
| Sentiment Analysis | Rating-based classification: positive (≥4), neutral (3), negative (≤2) |
| Product Analytics | Group-by analysis on enriched data for business insights |
| Production Readiness | Batch size, cost, caching, and mock-to-real swap patterns |

---

## Next Steps

- **[Lab 051](lab-051-fabric-iq-event-streams.md)** *(coming soon)* — Fabric IQ — Real-Time Event Stream Processing
- **[Lab 052](lab-052-fabric-iq-nl-to-sql.md)** *(coming soon)* — Fabric IQ — Natural Language to SQL with AI
