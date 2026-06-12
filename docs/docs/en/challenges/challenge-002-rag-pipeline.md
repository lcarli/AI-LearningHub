---
tags: [challenge, rag, retrieval, evaluation, python, local]
---
# Challenge 002: Fix a Broken RAG Pipeline

<div class="lab-meta">
  <span><strong>Level:</strong> <span class="level-badge level-200">L200</span></span>
  <span><strong>Type:</strong> Challenge</span>
  <span><strong>Time:</strong> ~75 min</span>
  <span><strong>💰 Cost:</strong> <span class="level-badge cost-free">Free (local)</span></span>
</div>

## Scenario

OutdoorGear has a local RAG prototype for support questions. It should retrieve the right policy or product guide, then answer using only retrieved context. The current prototype is broken: retrieval ranks poor chunks first, answers ignore evidence, and evaluation reports misleading metrics.

Your job is to fix the pipeline without using an LLM, vector database, or RAG framework.

---

## Objective

Implement the missing or broken logic in `starter_rag_pipeline.py` so the RAG pipeline retrieves the right source documents, produces grounded answers, reports correct evaluation metrics, and generates a validation code.

Your final pipeline should:

- Normalize query/document text for retrieval
- Chunk documents while preserving source metadata
- Rank chunks by relevance
- Produce concise answers from retrieved evidence
- Evaluate top-1 retrieval accuracy and required-term answer coverage

---

## Starter Files

Save these files in one folder named `challenge-002/`:

| File | Purpose | Download |
|------|---------|----------|
| `documents.json` | Mock OutdoorGear knowledge base | [Download](https://github.com/lcarli/AI-LearningHub/raw/main/docs/docs/en/challenges/challenge-002/documents.json) |
| `queries.json` | Evaluation queries and expected evidence | [Download](https://github.com/lcarli/AI-LearningHub/raw/main/docs/docs/en/challenges/challenge-002/queries.json) |
| `starter_rag_pipeline.py` | Broken RAG pipeline | [Download](https://github.com/lcarli/AI-LearningHub/raw/main/docs/docs/en/challenges/challenge-002/starter_rag_pipeline.py) |
| `test_rag_pipeline.py` | Acceptance tests | [Download](https://github.com/lcarli/AI-LearningHub/raw/main/docs/docs/en/challenges/challenge-002/test_rag_pipeline.py) |
| `validate_rag_pipeline.py` | Generates the final completion code | [Download](https://github.com/lcarli/AI-LearningHub/raw/main/docs/docs/en/challenges/challenge-002/validate_rag_pipeline.py) |

---

## Challenge Brief

You receive a tiny knowledge base, a set of evaluation queries, and a broken local RAG pipeline. There is no walkthrough: decide how to chunk, score, retrieve, answer, and evaluate so the system behaves like a reliable grounded support assistant.

---

## Constraints

- Use only the Python standard library in `starter_rag_pipeline.py`.
- Do not call an LLM API.
- Do not use embeddings or a vector database.
- Do not hardcode answers for individual query IDs.
- Use retrieved evidence in `answer_question()`.
- Preserve the public function names used by the tests.

---

## Acceptance Criteria

Your solution is complete when:

- `python -m pytest test_rag_pipeline.py` passes
- Chunk metadata preserves `chunk_id`, `doc_id`, `title`, and `text`
- The top document for each fixture query is correct
- Answers include the required evidence terms
- Evaluation reports `top1_accuracy == 1.0`
- Evaluation reports `required_coverage == 1.0`

---

## Validation

When your implementation is ready, run:

```bash
python -m pytest test_rag_pipeline.py
python validate_rag_pipeline.py
```

Enter the completion code printed by `validate_rag_pipeline.py`:

<div class="challenge-validator" data-answer="CH002-3E640D5D">
  <input type="text" aria-label="Completion code" placeholder="CH002-XXXXXXXX" />
  <button type="button">Validate</button>
  <p class="challenge-validator-result" aria-live="polite"></p>
</div>

---

## Hints

??? tip "Hint 1 — Retrieval quality starts with normalization"
    Punctuation, case, and common stop words can dominate a small lexical retriever if you do not normalize them.

??? tip "Hint 2 — Chunking is part of retrieval"
    A chunk should be small enough to score precisely but still carry enough source metadata to explain where the answer came from.

??? tip "Hint 3 — Answer from evidence, not from the query"
    If a required term is not present in the retrieved context, the answer should not invent it.

??? tip "Hint 4 — Metrics need the right denominator"
    Top-1 accuracy and coverage are per-query metrics. Check what you are dividing by.

---

## Rubric

| Area | Points | What good looks like |
|------|:------:|----------------------|
| Retrieval | 35 | Correct top document for each query |
| Chunking | 20 | Metadata preserved and chunk sizes controlled |
| Grounded answers | 20 | Answers include evidence from retrieved chunks |
| Evaluation | 15 | Metrics reflect query-level performance |
| Simplicity | 10 | No framework or hardcoded query-specific answers |

---

## Stretch Goals

- Add reciprocal rank fusion over title and body scores
- Return citations with chunk IDs in the answer
- Add a "not enough evidence" answer when retrieval confidence is low
- Add one new query to `queries.json` and update the validator payload locally

---

## Related Labs

- [Lab 006 — What is RAG?](../labs/lab-006-what-is-rag.md)
- [Lab 007 — What are Embeddings?](../labs/lab-007-what-are-embeddings.md)
- [Lab 022 — RAG with GitHub Models + pgvector](../labs/lab-022-rag-github-models-pgvector.md)
