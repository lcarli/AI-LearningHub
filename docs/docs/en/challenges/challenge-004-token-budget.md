---
tags: [challenge, token-budget, cost, context, python, local]
---
# Challenge 004: Optimize a Token Budget

<div class="lab-meta">
  <span><strong>Level:</strong> <span class="level-badge level-200">L200</span></span>
  <span><strong>Type:</strong> Challenge</span>
  <span><strong>Time:</strong> ~60 min</span>
  <span><strong>💰 Cost:</strong> <span class="level-badge cost-free">Free (local)</span></span>
</div>

## Scenario

OutdoorGear has a support assistant that sends too much context to the model. It includes long legal text and brand-story content even when a concise policy summary would answer the question. The team wants shorter prompts without losing answer quality.

Your job is to fix a local prompt-budget optimizer that selects compact relevant context and keeps every prompt under a strict token limit.

---

## Objective

Fix `starter_token_budget.py` so the optimizer selects the right context document for each request, avoids irrelevant context, builds compact prompts, reports budget compliance, and generates a validation code.

Your final optimizer should:

- Estimate prompt tokens deterministically
- Normalize keywords for lexical matching
- Prefer concise relevant summaries over long noisy documents
- Select context within a context-token budget
- Build prompts that stay under each request's total budget
- Report selected documents and budget compliance

---

## Starter Files

Save these files in one folder named `challenge-004/`:

| File | Purpose | Download |
|------|---------|----------|
| `context_docs.json` | Compact and verbose support context | [Download](https://github.com/lcarli/AI-LearningHub/raw/main/docs/docs/en/challenges/challenge-004/context_docs.json) |
| `requests.json` | Budgeted support requests | [Download](https://github.com/lcarli/AI-LearningHub/raw/main/docs/docs/en/challenges/challenge-004/requests.json) |
| `starter_token_budget.py` | Broken budget optimizer | [Download](https://github.com/lcarli/AI-LearningHub/raw/main/docs/docs/en/challenges/challenge-004/starter_token_budget.py) |
| `test_token_budget.py` | Acceptance tests | [Download](https://github.com/lcarli/AI-LearningHub/raw/main/docs/docs/en/challenges/challenge-004/test_token_budget.py) |
| `validate_token_budget.py` | Generates the final completion code | [Download](https://github.com/lcarli/AI-LearningHub/raw/main/docs/docs/en/challenges/challenge-004/validate_token_budget.py) |

---

## Challenge Brief

You receive compact docs, verbose docs, budgeted requests, and a broken optimizer. There is no walkthrough: decide how to estimate tokens, rank context, select evidence, and build prompts that stay within the budget.

---

## Constraints

- Use only the Python standard library in `starter_token_budget.py`.
- Do not call an LLM API.
- Do not hardcode behavior by request ID.
- Do not include irrelevant docs just because there is room.
- Keep prompt structure short and grounded.

---

## Acceptance Criteria

Your solution is complete when:

- `python -m pytest test_token_budget.py` passes
- The concise expected document is selected for each request
- Verbose or irrelevant documents are not selected over concise matches
- Every prompt is within its `max_prompt_tokens`
- Evaluation reports `within_budget is True`
- Evaluation reports `all_prompts_under_budget is True`

---

## Validation

When your implementation is ready, run:

```bash
python -m pytest test_token_budget.py
python validate_token_budget.py
```

Enter the completion code printed by `validate_token_budget.py`:

<div class="challenge-validator" data-answer="CH004-67CBEAD0">
  <input type="text" aria-label="Completion code" placeholder="CH004-XXXXXXXX" />
  <button type="button">Validate</button>
  <p class="challenge-validator-result" aria-live="polite"></p>
</div>

---

## Hints

??? tip "Hint 1 — Token estimation does not need to be perfect"
    It only needs to be deterministic and close enough to compare prompt sizes.

??? tip "Hint 2 — Relevance is not enough"
    A long document with the right words may be less useful than a concise summary with the same evidence.

??? tip "Hint 3 — Budget at selection time"
    It is easier to stay under budget if you reject context before building the final prompt.

??? tip "Hint 4 — Prompt template matters"
    A verbose instruction template can consume the same budget you are trying to save.

---

## Rubric

| Area | Points | What good looks like |
|------|:------:|----------------------|
| Token estimation | 20 | Deterministic, word-like, useful for budgets |
| Context ranking | 30 | Selects concise relevant docs |
| Prompt construction | 25 | Stays grounded and under budget |
| Evaluation | 15 | Reports correct selected docs and compliance |
| Simplicity | 10 | Local deterministic logic, no over-engineering |

---

## Stretch Goals

- Add separate budgets for system prompt, context, and answer
- Report token savings versus the verbose baseline
- Add a fallback when no document fits the budget
- Add a new request with a tighter budget and update the validator payload locally

---

## Related Labs

- [Lab 038 — AI Cost Optimization](../labs/lab-038-cost-optimization.md)
- [Lab 071 — Context Caching](../labs/lab-071-context-caching.md)
- [Lab 072 — Structured Outputs Reliability Benchmark](../labs/lab-072-structured-outputs.md)
