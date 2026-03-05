---
tags: [multimodal, rag, images, tables, gpt4o-vision, python]
---
# Lab 083: Multi-Modal RAG — Images, Tables & Charts in Documents

<div class="lab-meta">
  <span><strong>Level:</strong> <span class="level-badge level-300">L300</span></span>
  <span><strong>Path:</strong> All paths</span>
  <span><strong>Time:</strong> ~90 min</span>
  <span><strong>💰 Cost:</strong> <span class="level-badge cost-free">Free</span></span>
</div>

!!! info "Tradução em andamento"
    Este lab ainda está sendo traduzido. O conteúdo abaixo está em inglês.



## What You'll Learn

- What **multi-modal RAG** is — retrieval-augmented generation that handles images, tables, and charts alongside text
- How **GPT-4o vision** enables understanding of visual content within documents for richer retrieval
- Compare **text-only vs multi-modal retrieval** scores to quantify the improvement from visual understanding
- Analyze **chunk types** (text, image, table) and their impact on retrieval quality
- Debug a broken multi-modal RAG analysis script by fixing 3 bugs

## Introduction

Traditional RAG pipelines work well with text — they chunk documents, embed the chunks, and retrieve the most relevant ones for a query. But enterprise documents are not just text. They contain **bar charts**, **pie charts**, **product photos**, **architectural diagrams**, **data tables**, and **flowcharts** that carry critical information.

A text-only RAG pipeline misses this information entirely. When a user asks "What was Q1 revenue by region?", the answer might be in a **bar chart** — which text-only embedding scores at 0.15 (nearly useless) while a multi-modal approach scores 0.82 (highly relevant).

| Approach | Handles Text | Handles Images | Handles Tables | Typical Use Case |
|----------|:---:|:---:|:---:|---|
| **Text-only RAG** | ✅ | ❌ | ⚠️ (text only) | Simple Q&A over text documents |
| **Multi-modal RAG** | ✅ | ✅ | ✅ | Documents with charts, photos, diagrams |

### The Scenario

You are building a **document intelligence system** for OutdoorGear Inc. The corpus includes quarterly reports with charts, product catalogs with photos, training manuals with diagrams, investor decks with visualizations, and sales spreadsheets. You will analyze **15 document chunks** to compare text-only and multi-modal retrieval performance.

!!! info "No GPT-4o API Required"
    This lab analyzes a **pre-recorded benchmark dataset** of retrieval scores. You don't need an OpenAI API key — all analysis is done locally with pandas. The dataset simulates real retrieval scores from a multi-modal RAG pipeline.

## Prerequisites

| Requirement | Why |
|---|---|
| Python 3.10+ | Run analysis scripts |
| `pandas` library | DataFrame operations |

```bash
pip install pandas
```

---

!!! tip "Quick Start with GitHub Codespaces"
    [![Open in GitHub Codespaces](https://github.com/codespaces/badge.svg)](https://codespaces.new/lcarli/AI-LearningHub?quickstart=1)

    All dependencies are pre-installed in the devcontainer.


## 📦 Supporting Files

!!! note "Download these files before starting the lab"
    Save all files to a `lab-083/` folder in your working directory.

| File | Description | Download |
|------|-------------|----------|
| `broken_multimodal.py` | Bug-fix exercise (3 bugs + self-tests) | [📥 Download](https://github.com/lcarli/AI-LearningHub/raw/main/docs/docs/en/labs/lab-083/broken_multimodal.py) |
| `multimodal_chunks.csv` | Dataset — 15 document chunks with retrieval scores | [📥 Download](https://github.com/lcarli/AI-LearningHub/raw/main/docs/docs/en/labs/lab-083/multimodal_chunks.csv) |

---

## Step 1: Understanding Multi-Modal RAG

A multi-modal RAG pipeline extends traditional RAG with visual understanding:

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

### How Visual Chunks Are Processed

| Chunk Type | Text-Only Pipeline | Multi-Modal Pipeline |
|-----------|-------------------|---------------------|
| **Text** | Embed text → retrieve by cosine similarity | Same as text-only |
| **Table** | Embed serialized table text | Embed text + understand structure |
| **Image** | ❌ Skip or use alt text (low quality) | GPT-4o describes the image → embed description + visual features |

The key insight: **images carry information that text cannot capture**. A bar chart, product photo, or architecture diagram conveys meaning that gets lost when the image is simply skipped or described by alt text alone.

---

## Step 2: Load the Chunk Dataset

The dataset contains **15 chunks** from 5 documents, each with text-only and multi-modal retrieval scores:

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

**Expected output:**

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

## Step 3: Compare Text-Only vs Multi-Modal Scores

Analyze how multi-modal retrieval improves over text-only:

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

**Expected output:**

```
Average retrieval scores by chunk type:
   text: text=0.806  multimodal=0.806  improvement=+0.000
  table: text=0.780  multimodal=0.898  improvement=+0.117
  image: text=0.138  multimodal=0.853  improvement=+0.715
```

!!! tip "Insight"
    **Text chunks** see no improvement — they're already well-served by text embeddings. **Table chunks** gain +0.117 from structural understanding. **Image chunks** see a massive +0.715 improvement — text-only retrieval scores just 0.138 on average for images, while multi-modal scores 0.853. This is the primary value proposition of multi-modal RAG.

---

## Step 4: Analyze Image Chunks

Deep dive into chunks with images:

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

**Expected output:**

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

## Step 5: Calculate Improvement Metrics

Compute the average improvement for image chunks:

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

**Expected output:**

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

!!! tip "Insight"
    Multi-modal retrieval is **6.2x better** than text-only for image chunks. Even across all 15 chunks (including text-only ones), the overall retrieval score improves significantly because 40% of chunks (6/15) contain images.

---

## Step 6: Document-Level Analysis

Compare multi-modal impact per document:

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

**Expected output:**

```
Retrieval improvement by document:
            investor_deck.pptx: text=0.577  mm=0.840  Δ=+0.263  images=Yes
          product_catalog.docx: text=0.608  mm=0.838  Δ=+0.230  images=Yes
        quarterly_report.pdf: text=0.513  mm=0.850  Δ=+0.337  images=Yes
             sales_data.xlsx: text=0.820  mm=0.920  Δ=+0.100  images=No
           training_manual.pdf: text=0.427  mm=0.840  Δ=+0.413  images=Yes
```

!!! tip "Insight"
    Documents with images see the largest improvements. The **training manual** benefits most (+0.413) because it contains assembly diagrams and photos that are critical for answering how-to questions. The **sales spreadsheet** (no images) still benefits from improved table understanding (+0.100).

---

## 🐛 Bug-Fix Exercise

The file `lab-083/broken_multimodal.py` has **3 bugs** in the analysis functions. Can you find and fix them all?

Run the self-tests to see which ones fail:

```bash
python lab-083/broken_multimodal.py
```

You should see **3 failed tests**. Each test corresponds to one bug:

| Test | What it checks | Hint |
|------|---------------|------|
| Test 1 | Multi-modal improvement calculation | Should compute improvement using image chunks for both scores, not mixed |
| Test 2 | Image chunk count | Should check `has_image`, not `has_table` |
| Test 3 | Average multi-modal score | Should use `retrieval_score_multimodal`, not `retrieval_score_text_only` |

Fix all 3 bugs, then re-run. When you see `All passed!`, you're done!

---

## 🧠 Knowledge Check

??? question "**Q1 (Multiple Choice):** Why do image chunks score poorly with text-only retrieval?"

    - A) Because images are always low quality
    - B) Because text embeddings cannot capture visual information — charts, photos, and diagrams have minimal extractable text
    - C) Because image files are too large to embed
    - D) Because text-only models refuse to process images

    ??? success "✅ Reveal Answer"
        **Correct: B) Because text embeddings cannot capture visual information — charts, photos, and diagrams have minimal extractable text**

        A bar chart showing "Q1 revenue by region" has very little extractable text (maybe axis labels), so its text embedding has almost no semantic overlap with a query about revenue. Multi-modal RAG uses GPT-4o vision to *understand* the chart content and generate a rich description, producing an embedding that accurately represents the chart's information.

??? question "**Q2 (Multiple Choice):** What role does GPT-4o vision play in a multi-modal RAG pipeline?"

    - A) It generates the final answer to the user's query
    - B) It converts images into text descriptions that can be embedded alongside document text
    - C) It replaces the vector database entirely
    - D) It only handles OCR for scanned documents

    ??? success "✅ Reveal Answer"
        **Correct: B) It converts images into text descriptions that can be embedded alongside document text**

        GPT-4o vision analyzes each image chunk — charts, photos, diagrams — and produces a detailed text description of what the image contains. This description is then embedded alongside the document text, enabling the retrieval system to find relevant images when a user asks a question. The description bridges the gap between visual content and text-based retrieval.

??? question "**Q3 (Run the Lab):** How many chunks contain images (`has_image == True`)?"

    Load [📥 `multimodal_chunks.csv`](https://github.com/lcarli/AI-LearningHub/raw/main/docs/docs/en/labs/lab-083/multimodal_chunks.csv) and count rows where `has_image == True`.

    ??? success "✅ Reveal Answer"
        **6**

        6 out of 15 chunks contain images: C03 (bar chart), C05 (product photo), C08 (assembly diagram), C09 (stake placement photo), C11 (pie chart), and C15 (line graph). These represent 40% of the corpus.

??? question "**Q4 (Run the Lab):** What is the average multi-modal score improvement for image chunks compared to their text-only scores?"

    For chunks where `has_image == True`, compute `retrieval_score_multimodal.mean() - retrieval_score_text_only.mean()`.

    ??? success "✅ Reveal Answer"
        **+0.715**

        Image chunks average text-only score: (0.15 + 0.10 + 0.12 + 0.08 + 0.18 + 0.20) ÷ 6 = **0.138**. Average multi-modal score: (0.82 + 0.91 + 0.85 + 0.79 + 0.87 + 0.88) ÷ 6 = **0.853**. Improvement = 0.853 − 0.138 = **+0.715**.

??? question "**Q5 (Run the Lab):** How many total chunks are in the dataset?"

    Count all rows in the dataset.

    ??? success "✅ Reveal Answer"
        **15**

        The dataset contains 15 chunks across 5 documents: quarterly_report.pdf (3), product_catalog.docx (3), training_manual.pdf (2), investor_deck.pptx (3), sales_data.xlsx (1), product_catalog.docx (1), quarterly_report.pdf (1), and sales_data.xlsx (1) — totaling 15 chunks.

---

## Summary

| Topic | What You Learned |
|-------|-----------------|
| Multi-Modal RAG | Extends text RAG with visual understanding of images, charts, and diagrams |
| GPT-4o Vision | Converts images to rich text descriptions for embedding and retrieval |
| Image Chunks | 6 out of 15 chunks contain images — 40% of the corpus |
| Score Improvement | Image chunks improve from 0.138 (text-only) to 0.853 (multi-modal) — +0.715 gain |
| Text Chunks | No improvement needed — already well-served by text embeddings |
| Table Chunks | Moderate improvement (+0.117) from structural understanding |
| Overall Impact | Multi-modal retrieval significantly improves quality for visually-rich documents |

---

## Next Steps

- Explore [Azure AI Document Intelligence](https://learn.microsoft.com/azure/ai-services/document-intelligence/) for production-grade document parsing
- Try building a multi-modal RAG pipeline with [LangChain's multi-modal support](https://python.langchain.com/docs/how_to/multimodal_inputs/)
- Review **[Lab 080](lab-080-markitdown-mcp.md)** for document-to-Markdown conversion as a preprocessing step
