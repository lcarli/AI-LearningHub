---
tags: [challenge, local-ai, agent, tools, rag, python]
---
# Challenge 008: Build a Local-Only Agent

<div class="lab-meta">
  <span><strong>Level:</strong> <span class="level-badge level-200">L200</span></span>
  <span><strong>Type:</strong> Challenge</span>
  <span><strong>Time:</strong> ~75 min</span>
  <span><strong>💰 Cost:</strong> <span class="level-badge cost-free">Free (local)</span></span>
</div>

## Scenario

OutdoorGear wants a tiny support agent that works without Azure, GitHub Models, hosted LLMs, or network calls. It should classify a request, use local tools over local data, and return a grounded answer with a trace.

Your job is to finish the local-only agent and prove that it can handle product search, policy lookup, and bundle recommendation requests without cloud configuration.

---

## Objective

Fix `starter_local_agent.py` so the local agent routes requests correctly, uses only local data, returns useful answers, reports no cloud usage, and generates a validation code.

Your final local agent should:

- Require no cloud configuration
- Classify three supported intents
- Search products locally
- Look up policy text locally
- Build a camping bundle within budget
- Return answer, trace, intent, and `uses_cloud: False`

---

## Starter Files

Save these files in one folder named `challenge-008/`:

| File | Purpose | Download |
|------|---------|----------|
| `local_data.json` | Local product and policy data | [Download](https://github.com/lcarli/AI-LearningHub/raw/main/docs/docs/en/challenges/challenge-008/local_data.json) |
| `eval_requests.json` | Evaluation requests | [Download](https://github.com/lcarli/AI-LearningHub/raw/main/docs/docs/en/challenges/challenge-008/eval_requests.json) |
| `starter_local_agent.py` | Broken local-only agent | [Download](https://github.com/lcarli/AI-LearningHub/raw/main/docs/docs/en/challenges/challenge-008/starter_local_agent.py) |
| `test_local_agent.py` | Acceptance tests | [Download](https://github.com/lcarli/AI-LearningHub/raw/main/docs/docs/en/challenges/challenge-008/test_local_agent.py) |
| `validate_local_agent.py` | Generates the final completion code | [Download](https://github.com/lcarli/AI-LearningHub/raw/main/docs/docs/en/challenges/challenge-008/validate_local_agent.py) |

---

## Challenge Brief

You receive local product/policy data, evaluation requests, and a broken local agent. There is no walkthrough: decide how to route intents, call local tools, compose answers, and prove that no cloud dependency is required.

---

## Constraints

- Use only the Python standard library in `starter_local_agent.py`.
- Do not call any network, hosted model, or cloud API.
- Do not hardcode answers by request ID.
- Preserve the public function names used by the tests.
- Keep traces useful enough to show which local tool ran.

---

## Acceptance Criteria

Your solution is complete when:

- `python -m pytest test_local_agent.py` passes
- Product search returns `RainShell Pro Jacket`
- Policy lookup returns the 60-day return policy
- Bundle recommendation includes the expected three camping items under budget
- The trace records intent and tool execution
- `uses_cloud` is `False`

---

## Validation

When your implementation is ready, run:

```bash
python -m pytest test_local_agent.py
python validate_local_agent.py
```

Enter the completion code printed by `validate_local_agent.py`:

<div class="challenge-validator" data-answer="CH008-A1B101A9">
  <input type="text" aria-label="Completion code" placeholder="CH008-XXXXXXXX" />
  <button type="button">Validate</button>
  <p class="challenge-validator-result" aria-live="polite"></p>
</div>

---

## Hints

??? tip "Hint 1 — Local-only is a requirement"
    A local agent can still be useful if intent routing and tools are deterministic.

??? tip "Hint 2 — Keep routing narrow"
    The fixture requests are intentionally scoped to product search, policy lookup, and bundle recommendation.

??? tip "Hint 3 — Trace the tool, not just the answer"
    A trace helps prove that the agent made a decision and used a local tool.

---

## Rubric

| Area | Points | What good looks like |
|------|:------:|----------------------|
| Local-only behavior | 25 | No cloud or network dependency |
| Intent routing | 25 | Three request types classified correctly |
| Tool outputs | 25 | Product, policy, and bundle answers are correct |
| Traceability | 15 | Trace shows intent and selected local tool |
| Simplicity | 10 | Deterministic local implementation |

---

## Related Labs

- [Lab 015 — Ollama Local LLMs](../labs/lab-015-ollama-local-llms.md)
- [Lab 078 — Foundry Local](../labs/lab-078-foundry-local.md)
- [Lab 020 — MCP Server in Python](../labs/lab-020-mcp-server-python.md)
