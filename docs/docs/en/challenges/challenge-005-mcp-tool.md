---
tags: [challenge, mcp, tools, schema, privacy, python, local]
---
# Challenge 005: Build a Safe MCP-Style Tool

<div class="lab-meta">
  <span><strong>Level:</strong> <span class="level-badge level-200">L200</span></span>
  <span><strong>Type:</strong> Challenge</span>
  <span><strong>Time:</strong> ~60 min</span>
  <span><strong>💰 Cost:</strong> <span class="level-badge cost-free">Free (local)</span></span>
</div>

## Scenario

OutdoorGear wants to expose an order-status lookup tool to agents through an MCP-style contract. The current tool leaks customer email addresses, accepts extra arguments, and has an incomplete schema.

Your job is to design a safe local tool contract and execution path before the tool is exposed to any agent runtime.

---

## Objective

Fix `starter_mcp_tool.py` so the tool manifest is valid, argument validation is strict, invalid calls are blocked, order lookups redact PII, and the validator generates a completion code.

Your final tool should:

- Define a clear `get_order_status` manifest with an input schema
- Accept only `order_id`
- Reject unknown tools and extra arguments
- Return safe order-status data without `customer_email`
- Report contract metrics accurately

---

## Starter Files

Save these files in one folder named `challenge-005/`:

| File | Purpose | Download |
|------|---------|----------|
| `orders.json` | Mock OutdoorGear orders | [Download](https://github.com/lcarli/AI-LearningHub/raw/main/docs/docs/en/challenges/challenge-005/orders.json) |
| `tool_requests.json` | Valid and invalid tool calls | [Download](https://github.com/lcarli/AI-LearningHub/raw/main/docs/docs/en/challenges/challenge-005/tool_requests.json) |
| `starter_mcp_tool.py` | Broken MCP-style tool implementation | [Download](https://github.com/lcarli/AI-LearningHub/raw/main/docs/docs/en/challenges/challenge-005/starter_mcp_tool.py) |
| `test_mcp_tool.py` | Acceptance tests | [Download](https://github.com/lcarli/AI-LearningHub/raw/main/docs/docs/en/challenges/challenge-005/test_mcp_tool.py) |
| `validate_mcp_tool.py` | Generates the final completion code | [Download](https://github.com/lcarli/AI-LearningHub/raw/main/docs/docs/en/challenges/challenge-005/validate_mcp_tool.py) |

---

## Challenge Brief

You receive mock orders, valid and invalid tool calls, and a broken tool implementation. There is no walkthrough: decide how to describe the tool, validate arguments, dispatch execution, and redact sensitive fields.

---

## Constraints

- Use only the Python standard library in `starter_mcp_tool.py`.
- Do not expose `customer_email` in tool results.
- Do not accept extra arguments.
- Do not execute unknown tools.
- Preserve the public function names used by the tests.

---

## Acceptance Criteria

Your solution is complete when:

- `python -m pytest test_mcp_tool.py` passes
- The manifest includes a valid `inputSchema`
- Only `order_id` is accepted as input
- Unknown tools and extra PII arguments are blocked
- Successful calls return `delivered` and `processing`
- Tool results are redacted

---

## Validation

When your implementation is ready, run:

```bash
python -m pytest test_mcp_tool.py
python validate_mcp_tool.py
```

Enter the completion code printed by `validate_mcp_tool.py`:

<div class="challenge-validator" data-answer="CH005-CD4DDCBC">
  <input type="text" aria-label="Completion code" placeholder="CH005-XXXXXXXX" />
  <button type="button">Validate</button>
  <p class="challenge-validator-result" aria-live="polite"></p>
</div>

---

## Hints

??? tip "Hint 1 — The schema is a security boundary"
    A loose schema invites agents to send fields the tool should never see.

??? tip "Hint 2 — Redaction belongs near the tool"
    Do not rely on the agent to hide sensitive fields after the tool returns them.

??? tip "Hint 3 — Fail closed"
    Unknown tools, missing required fields, and extra arguments should raise errors.

---

## Rubric

| Area | Points | What good looks like |
|------|:------:|----------------------|
| Manifest contract | 25 | Clear name, description, schema, and required fields |
| Argument validation | 25 | Missing and extra fields are rejected |
| Safe execution | 25 | Correct order status with PII redacted |
| Error handling | 15 | Unknown or invalid calls fail closed |
| Simplicity | 10 | Small deterministic tool code |

---

## Related Labs

- [Lab 012 — What is MCP?](../labs/lab-012-what-is-mcp.md)
- [Lab 020 — MCP Server in Python](../labs/lab-020-mcp-server-python.md)
- [Lab 064 — Securing MCP with APIM](../labs/lab-064-securing-mcp-apim.md)
