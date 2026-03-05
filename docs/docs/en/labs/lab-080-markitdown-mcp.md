---
tags: [markitdown, mcp, document-ingestion, pdf, python]
---
# Lab 080: MarkItDown + MCP — Document Ingestion for Agents

<div class="lab-meta">
  <span><strong>Level:</strong> <span class="level-badge level-200">L200</span></span>
  <span><strong>Path:</strong> All paths</span>
  <span><strong>Time:</strong> ~60 min</span>
  <span><strong>💰 Cost:</strong> <span class="level-badge cost-free">Free</span></span>
</div>

## What You'll Learn

- What **Microsoft MarkItDown** is — a library that converts PDF, Word, Excel, PowerPoint, HTML, and images into clean Markdown for LLM consumption
- How MarkItDown's **MCP server** exposes document conversion as a tool that any MCP-compatible agent can call
- Analyze **conversion quality** across different file types to understand strengths and limitations
- Measure **conversion speed** and identify which formats are fastest to process
- Debug a broken MarkItDown analysis script by fixing 3 bugs

## Introduction

Large Language Models work best with **plain text**, but enterprise documents come in dozens of formats — PDFs with tables, Word documents with embedded images, Excel spreadsheets, PowerPoint decks, and HTML pages. Manually converting these to text loses structure, and OCR-based approaches are slow and error-prone.

**Microsoft MarkItDown** solves this by converting rich documents into **well-structured Markdown** that preserves tables, headings, lists, and image references. It supports PDF, DOCX, XLSX, PPTX, HTML, CSV, JSON, and even images (via OCR/captioning). When combined with its **MCP server**, any agent can call `convert_to_markdown` as a tool — enabling seamless document ingestion workflows.

### The Scenario

You are a **Platform Engineer** at OutdoorGear Inc. The company has a growing document corpus — quarterly reports, product catalogs, training manuals, and contracts — that agents need to search and reason over. You will evaluate MarkItDown's conversion quality across **12 file conversions** covering 7 different file types.

!!! info "No MarkItDown Installation Required"
    This lab analyzes a **pre-recorded benchmark dataset** of conversion results. You don't need to install MarkItDown — all analysis is done locally with pandas. If you want to run live conversions, install with `pip install markitdown`.

## Prerequisites

| Requirement | Why |
|---|---|
| Python 3.10+ | Run analysis scripts |
| `pandas` library | DataFrame operations |
| (Optional) `markitdown` | For live document conversions |

```bash
pip install pandas
```

---

## 📦 Supporting Files

!!! note "Download these files before starting the lab"
    Save all files to a `lab-080/` folder in your working directory.

| File | Description | Download |
|------|-------------|----------|
| `broken_markitdown.py` | Bug-fix exercise (3 bugs + self-tests) | [📥 Download](https://github.com/lcarli/AI-LearningHub/raw/main/docs/docs/en/labs/lab-080/broken_markitdown.py) |
| `conversion_results.csv` | Dataset — 12 file conversions across 7 formats | [📥 Download](https://github.com/lcarli/AI-LearningHub/raw/main/docs/docs/en/labs/lab-080/conversion_results.csv) |

---

## Step 1: Understanding MarkItDown

MarkItDown follows a simple pipeline — detect the file type, apply the appropriate converter, and produce structured Markdown:

```
┌──────────────┐     ┌──────────────┐     ┌──────────────┐
│  Input File  │────▶│  Converter   │────▶│  Markdown    │
│  (PDF/DOCX…) │     │  (per-type)  │     │  (structured)│
└──────────────┘     └──────────────┘     └──────────────┘
```

Supported converters:

| Format | Converter | Preserves |
|--------|-----------|-----------|
| **PDF** | `pdfminer` | Text, headings, tables (limited) |
| **DOCX** | `python-docx` | Headings, tables, lists, styles |
| **XLSX** | `openpyxl` | Sheet data as Markdown tables |
| **PPTX** | `python-pptx` | Slide text, speaker notes, images |
| **HTML** | `BeautifulSoup` | Structure, links, tables |
| **CSV/JSON** | Built-in | Tabular data |
| **Images** | OCR / LLM captioning | Extracted text or descriptions |

### MCP Server Integration

MarkItDown ships with an **MCP server** that exposes conversion as a tool:

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

Any MCP-compatible agent (GitHub Copilot, Claude Desktop, custom agents) can call this tool to ingest documents on the fly.

---

## Step 2: Load the Conversion Results

The dataset contains **12 file conversions** across 7 different formats:

```python
import pandas as pd

results = pd.read_csv("lab-080/conversion_results.csv")
print(f"Total conversions: {len(results)}")
print(f"File types: {sorted(results['file_type'].unique())}")
print(f"\nDataset preview:")
print(results[["test_id", "input_file", "file_type", "conversion_success", "quality_score"]].to_string(index=False))
```

**Expected output:**

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

## Step 3: Analyze Conversion Success

Calculate overall success rate and identify failures:

```python
successful = results[results["conversion_success"] == True]
failed = results[results["conversion_success"] == False]

print(f"Successful conversions: {len(successful)}/{len(results)}")
print(f"Success rate: {len(successful)/len(results)*100:.0f}%")

if len(failed) > 0:
    print(f"\nFailed conversions:")
    print(failed[["test_id", "input_file", "file_type"]].to_string(index=False))
```

**Expected output:**

```
Successful conversions: 11/12
Success rate: 92%

Failed conversions:
 test_id      input_file file_type
     D11 corrupted_file.pdf       pdf
```

!!! tip "Insight"
    The only failure is a **corrupted PDF** (D11, file_size_kb = 0). MarkItDown handles all 7 supported formats successfully when the input file is valid.

---

## Step 4: Analyze Conversion Quality

Compare quality scores across file types:

```python
print("Quality scores by file type (successful only):")
quality = successful.groupby("file_type")["quality_score"].agg(["mean", "count"])
quality.columns = ["avg_quality", "count"]
print(quality.sort_values("avg_quality", ascending=False).to_string())

avg_quality = successful["quality_score"].mean()
print(f"\nOverall average quality: {avg_quality:.3f}")
```

**Expected output:**

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

!!! tip "Insight"
    Structured formats (CSV, JSON, XLSX) achieve near-perfect quality (≥0.98), while **images** have the lowest quality (0.72) — OCR/captioning is inherently lossy. PDFs vary based on complexity; the large training manual (D10, 12 MB) scored 0.82.

---

## Step 5: Analyze Conversion Speed

Measure conversion times and identify bottlenecks:

```python
print("Conversion time by file type (successful only):")
for _, row in successful.sort_values("conversion_time_ms", ascending=False).iterrows():
    print(f"  {row['test_id']} ({row['file_type']:>5}): {row['conversion_time_ms']:,}ms "
          f"({row['file_size_kb']:,} KB)")
```

**Expected output:**

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

**Expected output:**

```
Extracted elements (successful conversions):
  Tables found:   31
  Images found:   62
  Headings found: 103
```

!!! tip "Insight"
    Large PDFs and images are the slowest to convert. The **training manual** (D10, 12 MB) took 4.5 seconds but extracted 15 tables, 28 images, and 32 headings — a rich document that would be extremely tedious to process manually.

---

## Step 6: MCP Server Architecture

When MarkItDown runs as an MCP server, agents can convert documents on demand:

```
┌──────────────┐     ┌──────────────┐     ┌──────────────┐
│   Agent      │────▶│  MCP Server  │────▶│  MarkItDown  │
│  (Copilot,   │     │  (stdio/SSE) │     │  (converter) │
│   Claude)    │◀────│              │◀────│              │
└──────────────┘     └──────────────┘     └──────────────┘
     request              route              convert
     markdown             return             to .md
```

To start the MCP server locally:

```bash
# Install MarkItDown with MCP support
pip install 'markitdown[mcp]'

# Start the MCP server (stdio transport)
markitdown --mcp
```

Then add it to your MCP client configuration:

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

## 🐛 Bug-Fix Exercise

The file `lab-080/broken_markitdown.py` has **3 bugs** in the analysis functions. Can you find and fix them all?

Run the self-tests to see which ones fail:

```bash
python lab-080/broken_markitdown.py
```

You should see **3 failed tests**. Each test corresponds to one bug:

| Test | What it checks | Hint |
|------|---------------|------|
| Test 1 | Success rate calculation | Should count `True`, not `False` |
| Test 2 | Average quality calculation | Must filter to successful conversions first |
| Test 3 | Total tables found | Should sum `tables_found`, not `images_found` |

Fix all 3 bugs, then re-run. When you see `All passed!`, you're done!

---

## 🧠 Knowledge Check

??? question "**Q1 (Multiple Choice):** What formats does MarkItDown support for conversion to Markdown?"

    - A) Only PDF and Word documents
    - B) PDF, DOCX, XLSX, PPTX, HTML, CSV, JSON, and images
    - C) Only text-based formats like HTML and CSV
    - D) Any format, including video and audio files

    ??? success "✅ Reveal Answer"
        **Correct: B) PDF, DOCX, XLSX, PPTX, HTML, CSV, JSON, and images**

        MarkItDown supports a wide range of document formats including PDF (via pdfminer), Word documents (python-docx), Excel spreadsheets (openpyxl), PowerPoint presentations (python-pptx), HTML (BeautifulSoup), CSV, JSON, and images (via OCR or LLM captioning). It does not support audio or video files.

??? question "**Q2 (Multiple Choice):** How does MarkItDown's MCP server enable agent-based document ingestion?"

    - A) It converts documents to embeddings directly
    - B) It exposes a `convert_to_markdown` tool that any MCP-compatible agent can call
    - C) It requires agents to download and parse files themselves
    - D) It stores converted documents in a vector database automatically

    ??? success "✅ Reveal Answer"
        **Correct: B) It exposes a `convert_to_markdown` tool that any MCP-compatible agent can call**

        The MarkItDown MCP server runs as a standard MCP tool server (via stdio or SSE transport). It exposes a `convert_to_markdown` tool that accepts a file URI and returns the converted Markdown. Any MCP-compatible client — GitHub Copilot, Claude Desktop, or custom agents — can call this tool to ingest documents on the fly without any custom integration code.

??? question "**Q3 (Run the Lab):** How many of the 12 file conversions were successful?"

    Load [📥 `conversion_results.csv`](https://github.com/lcarli/AI-LearningHub/raw/main/docs/docs/en/labs/lab-080/conversion_results.csv) and count rows where `conversion_success == True`.

    ??? success "✅ Reveal Answer"
        **11 of 12**

        All conversions succeeded except D11 (`corrupted_file.pdf`), which was a corrupted PDF with 0 KB file size. MarkItDown reliably handles valid files across all 7 tested formats.

??? question "**Q4 (Run the Lab):** What is the total number of tables found across all successful conversions?"

    Filter to successful conversions and compute `tables_found.sum()`.

    ??? success "✅ Reveal Answer"
        **31**

        Sum of `tables_found` across the 11 successful conversions: D01(6) + D02(2) + D03(5) + D04(1) + D05(0) + D06(0) + D07(1) + D08(1) + D09(0) + D10(15) + D12(0) = **31 tables**.

??? question "**Q5 (Run the Lab):** What is the average quality score for successful conversions?"

    Filter to `conversion_success == True`, then compute `quality_score.mean()`.

    ??? success "✅ Reveal Answer"
        **≈ 0.916**

        Quality scores for the 11 successful conversions: 0.92 + 0.95 + 0.98 + 0.85 + 0.97 + 0.94 + 0.96 + 0.99 + 0.98 + 0.82 + 0.72 = **10.08**. Average = 10.08 ÷ 11 ≈ **0.916**.

---

## Summary

| Topic | What You Learned |
|-------|-----------------|
| MarkItDown | Converts PDF, DOCX, XLSX, PPTX, HTML, CSV, JSON, and images to structured Markdown |
| MCP Integration | MCP server exposes `convert_to_markdown` tool for any compatible agent |
| Quality Analysis | Structured formats (CSV, JSON, XLSX) achieve ≥0.98 quality; images lowest at 0.72 |
| Speed Analysis | Large PDFs and images are slowest; CSV/JSON convert in under 50ms |
| Success Rate | 11/12 conversions succeeded — only corrupted files fail |
| Element Extraction | 31 tables, 62 images, 103 headings extracted across successful conversions |

---

## Next Steps

- **[Lab 081](lab-081-agentic-coding-tools.md)** — Agentic Coding Tools: Claude Code vs Copilot CLI
- Explore the [MarkItDown GitHub repository](https://github.com/microsoft/markitdown) for advanced configuration and custom converters
