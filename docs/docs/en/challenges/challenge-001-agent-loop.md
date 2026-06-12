---
tags: [challenge, agent-loop, tools, python, local]
---
# Challenge 001: Build an Agent Loop from Scratch

<div class="lab-meta">
  <span><strong>Level:</strong> <span class="level-badge level-100">L100</span></span>
  <span><strong>Type:</strong> Challenge</span>
  <span><strong>Time:</strong> ~60 min</span>
  <span><strong>💰 Cost:</strong> <span class="level-badge cost-free">Free (local)</span></span>
</div>

## Scenario

OutdoorGear wants a tiny product-assistant agent that can reason over a local product catalog. The team does **not** want to use Semantic Kernel, LangGraph, AutoGen, or any hosted LLM yet. First, they want to prove that you understand the core loop:

> perceive → decide → act → observe → answer

Your job is to finish a small Python agent loop that chooses tools, executes them, stores observations, and produces a grounded final answer.

---

## Objective

Implement the missing logic in `starter_agent_loop.py` so the local product assistant can complete the two target requests and produce a validation code.

You should end with an agent that can:

- Search for matching products using category, query words, budget, and stock filters
- Look up product details by SKU
- Recommend a small in-stock camping bundle under a budget
- Run a loop that calls exactly one tool before producing a final answer for supported requests
- Return a trace showing what the agent did

---

## Starter Files

Save these files in one folder named `challenge-001/`:

| File | Purpose | Download |
|------|---------|----------|
| `products.json` | Mock OutdoorGear product catalog | [Download](https://github.com/lcarli/AI-LearningHub/raw/main/docs/docs/en/challenges/challenge-001/products.json) |
| `starter_agent_loop.py` | Starter implementation with TODOs | [Download](https://github.com/lcarli/AI-LearningHub/raw/main/docs/docs/en/challenges/challenge-001/starter_agent_loop.py) |
| `test_agent_loop.py` | Acceptance tests | [Download](https://github.com/lcarli/AI-LearningHub/raw/main/docs/docs/en/challenges/challenge-001/test_agent_loop.py) |
| `validate_agent_loop.py` | Generates the final completion code | [Download](https://github.com/lcarli/AI-LearningHub/raw/main/docs/docs/en/challenges/challenge-001/validate_agent_loop.py) |

---

## Challenge Brief

You receive a product catalog, a starter implementation, and tests. There is no walkthrough: decide how to parse the request, choose a tool, execute it, store the observation, and produce the final answer.

---

## Constraints

- Use only the Python standard library in `starter_agent_loop.py`.
- Do not call an LLM API.
- Do not use an agent framework.
- Keep the loop readable: the point is to understand the control flow.
- Preserve the return shape from `run_agent()`:

```python
{
    "final_answer": "...",
    "trace": [
        {"step": 1, "type": "tool", "tool": "...", "arguments": {...}},
        {"step": 2, "type": "final"}
    ]
}
```

---

## Acceptance Criteria

Your solution is complete when:

- `python -m pytest test_agent_loop.py` passes
- The jacket request calls `search_products` before answering
- The camping bundle request calls `recommend_bundle` before answering
- The final answer includes product names, prices, and a short rationale
- Out-of-stock products are not recommended
- The loop stops with a final answer before `max_steps`

---

## Validation

When your implementation is ready, run:

```bash
python -m pytest test_agent_loop.py
python validate_agent_loop.py
```

Enter the completion code printed by `validate_agent_loop.py`:

<div class="challenge-validator" data-answer="CH001-4707D4F5">
  <input type="text" aria-label="Completion code" placeholder="CH001-XXXXXXXX" />
  <button type="button">Validate</button>
  <p class="challenge-validator-result" aria-live="polite"></p>
</div>

---

## Hints

??? tip "Hint 1 — Start with tools"
    The loop is easier to reason about when each tool has a clear contract and deterministic output.

??? tip "Hint 2 — Keep parsing simple"
    You do not need advanced NLP. The target requests are intentionally narrow.

??? tip "Hint 3 — Use observations as memory"
    `state.observations` is the loop's short-term memory. After a tool runs, the final answer should be based on the latest observation, not on the original catalog.

??? tip "Hint 4 — Decide deterministically"
    A good solution makes the same decision every time for the same state.

---

## Rubric

| Area | Points | What good looks like |
|------|:------:|----------------------|
| Tool correctness | 30 | Filters, SKU lookup, and bundle selection are accurate |
| Agent loop | 30 | Clear perceive → decide → act → observe → answer flow |
| Grounded answer | 20 | Answer uses tool observations and names concrete products |
| Traceability | 10 | Trace shows tool call and final step |
| Simplicity | 10 | No unnecessary framework, API, or over-engineering |

---

## Stretch Goals

- Add support for "compare two SKUs"
- Add an error answer when no product matches
- Add a second tool call before the final answer for ambiguous requests
- Add a `max_price` parser that handles `$150`, `150 dollars`, and `under 150`

---

## Related Labs

- [Lab 001 — What are AI Agents?](../labs/lab-001-what-are-ai-agents.md)
- [Lab 018 — Function Calling & Tool Use](../labs/lab-018-function-calling.md)
- [Lab 020 — MCP Server in Python](../labs/lab-020-mcp-server-python.md)
