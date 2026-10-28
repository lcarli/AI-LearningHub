---
tags:
- rag
- embeddings
- retrieval
- local
- evaluation
lab:
  id: '022'
  level: L200
  journey: rag
  time_min: 90
  cost:
    tier: free
    requires: []
    estimate_usd: 0 within the documented free path or simulation.
    simulation: true
    cleanup: false
  roles:
  - developer
  - data-engineer
  - architect
  technologies:
  - rag
  - embeddings
  - retrieval
  - local
  - evaluation
  status: active
  last_verified: '2026-10-27'
  languages:
  - en
  - pt
  - fr
---
# Lab 022: Local RAG: Chunking → Embedding → Search → Answer

<div class="lab-meta">
  <span><strong>Level:</strong> <span class="level-badge level-200">L200</span></span>
  <span><strong>Journey:</strong> rag</span>
  <span><strong>Time:</strong> ~90 min</span>
  <span><strong>Cost:</strong> <span class="level-badge cost-free">Free</span></span>
</div>

!!! info "Free-first design"
    The required route is local, simulated, or works with GitHub Copilot Free. Any organization, cloud, or paid route is marked optional.

!!! tip "AI Credit impact"
    Keep the task bounded, use the smallest useful context, and validate locally. Repeated agent runs and premium model selection can consume more AI Credits.

## What You'll Learn

- Build an explicit ingestion and retrieval pipeline
- Use a dependency-free local embedding baseline
- Separate retrieval evidence from answer generation
- Evaluate recall, citation coverage, and unsupported claims

## Prerequisites

- Python 3.10+ for the local exercise
- A text editor and terminal
- Challenge 011

## Outcome and evidence

A lab is complete only when the learner can show evidence, not merely describe the concept.

| Capability | Required evidence |
|---|---|
| Build an explicit ingestion and retrieval pipeline | `evidence/step-1.txt` plus a passing local check |
| Use a dependency-free local embedding baseline | `evidence/step-2.txt` plus a passing local check |
| Separate retrieval evidence from answer generation | `evidence/step-3.txt` plus a passing local check |
| Evaluate recall, citation coverage, and unsupported claims | `evidence/step-4.txt` plus a passing local check |

## Lab plan

| Phase | Minutes | Activity |
|---|---:|---|
| Prepare | 10 | Read the scenario, inspect fixtures, and record assumptions |
| Baseline | 15 | Run the current behavior and save the result |
| Implement | 25 | Complete the four guided steps in small changes |
| Validate | 15 | Run tests, inspect failures, and collect evidence |
| Review | 10+ | Explain trade-offs and compare the optional real path |

## Visual model

```mermaid
flowchart LR
  D[Documents] --> C[Chunking]
  C --> E[Local embeddings]
  E --> I[In-memory index]
  Q[Question] --> QE[Query embedding]
  QE --> S[Similarity search]
  I --> S
  S --> A[Answer with citations]
  A --> V[Retrieval and groundedness eval]
```

## Scenario

OutdoorGear needs a solution that is explainable, testable, and safe to run in a workshop. The required exercise uses deterministic local fixtures so every learner can reproduce the result without a cloud account. A real service can later replace only the adapter boundary.

## Guided exercise

### Step 1

**Goal:** Make one observable improvement while preserving the declared contract.

**Action:** Run `local_rag.py ingest` to chunk and vectorize `documents.json`.

**Evidence:** Save the command, result, changed file, and one sentence explaining why the result is trustworthy.

**Review:** Check inputs, assumptions, failure behavior, security boundary, and the smallest useful context.

### Step 2

**Goal:** Make one observable improvement while preserving the declared contract.

**Action:** Run three searches and inspect scores, chunk boundaries, and source IDs.

**Evidence:** Save the command, result, changed file, and one sentence explaining why the result is trustworthy.

**Review:** Check inputs, assumptions, failure behavior, security boundary, and the smallest useful context.

### Step 3

**Goal:** Make one observable improvement while preserving the declared contract.

**Action:** Generate an extractive answer that cites only retrieved chunks.

**Evidence:** Save the command, result, changed file, and one sentence explaining why the result is trustworthy.

**Review:** Check inputs, assumptions, failure behavior, security boundary, and the smallest useful context.

### Step 4

**Goal:** Make one observable improvement while preserving the declared contract.

**Action:** Change chunk size and compare recall@3 before choosing a production backend.

**Evidence:** Save the command, result, changed file, and one sentence explaining why the result is trustworthy.

**Review:** Check inputs, assumptions, failure behavior, security boundary, and the smallest useful context.

### Run locally

```bash
cd docs/docs/en/labs/lab-022
python -m unittest discover -v
```

Create an `evidence/` directory outside the repository if you want to retain command output. Do not commit credentials, private code, or personal data.

## Review rubric

| Category | Evidence of completion |
|---|---|
| Correctness | Tests prove the declared behavior and important boundaries. |
| Evidence | Commands, outputs, and assumptions are reproducible. |
| Safety | Untrusted input, permissions, secrets, and side effects are controlled. |
| Maintainability | The solution is bounded, readable, and reversible. |

## Common failure modes and recovery

| Failure | Recovery |
|---|---|
| The happy path passes but boundaries fail. | Add negative, empty, maximum, and malformed cases. |
| The model proposes a broad rewrite. | Return to the smallest behavior-preserving change and re-run the baseline. |
| A tool or retrieved document contains instructions. | Treat it as untrusted data and enforce policy outside the model. |
| The result cannot be reproduced. | Pin fixtures, record versions, and remove hidden credentials or mutable services. |

## Accessibility and responsible use

- Do not rely on color alone in diagrams or results.
- Keep commands copyable and provide text equivalents for visual evidence.
- Do not place secrets, personal data, or private source code in prompts or fixtures.
- Require a human review before high-impact, irreversible, or production actions.

## Supporting kit

The downloadable kit contains the lab guide, local exercise files, a cheat sheet, and the diagrams referenced here. CI publishes deterministic PDF and ZIP artifacts.

| Item | Purpose |
|---|---|
| `README.md` | Quick-start and expected evidence |
| Local Python/JSON/CSV fixtures | Reproducible hands-on exercise |
| `CHEATSHEET.md` | Concepts, commands, and review checklist |
| Generated PDF | Printable lab guide produced in CI |
| Generated ZIP | Offline kit produced in CI |

## Optional real path

Replace only the adapter boundary with an approved hosted service. Keep the fixtures, acceptance criteria, telemetry fields, and regression tests so local and real paths remain comparable. Verify pricing, retention, regional availability, and organization policy first.

## Knowledge check

??? question "What must be measured before swapping vector databases?"

    ??? success "Answer"
        Retrieval quality and latency with a stable evaluation set.

??? question "What evidence should be saved?"

    ??? success "Answer"
        The command, result, changed file, assumptions, and a short trust explanation.

??? question "When should the optional real path be used?"

    ??? success "Answer"
        After the local contract passes and pricing, policy, data handling, and cleanup are understood.

## Exit criteria

- [ ] The local exercise passes without credentials.
- [ ] Evidence and assumptions are recorded.
- [ ] Optional paid or organization features remain optional.
- [ ] Security, accessibility, and failure behavior were reviewed.
- [ ] The generated kit can be reproduced from source.

## Public sources

- [RAG paper](https://arxiv.org/abs/2005.11401)
- [Sentence Transformers semantic search](https://www.sbert.net/examples/sentence_transformer/applications/semantic-search/README.html)
