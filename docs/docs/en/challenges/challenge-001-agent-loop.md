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

## Goal

Make all tests pass by implementing the missing functions in `starter_agent_loop.py`.

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

---

## Setup

```bash
cd challenge-001
python -m pip install pytest
python -m pytest test_agent_loop.py
```

The tests should fail at first. Your task is to make them pass.

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

## Hints

??? tip "Hint 1 — Start with tools"
    Implement `search_products`, `get_product_details`, and `recommend_bundle` before touching the loop. An agent loop is only useful if tools are reliable.

??? tip "Hint 2 — Keep parsing simple"
    You do not need advanced NLP. Simple keyword checks for `jacket`, `camping`, `under`, and `SKU` are enough for this challenge.

??? tip "Hint 3 — Use observations as memory"
    `state.observations` is the loop's short-term memory. After a tool runs, the final answer should be based on the latest observation, not on the original catalog.

??? tip "Hint 4 — Decide deterministically"
    If there are no observations yet, choose a tool. If there is at least one useful observation, choose `final`.

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
