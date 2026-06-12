---
tags: [challenge, guardrails, red-team, safety, pii, python, local]
---
# Challenge 007: Red-Team Agent Guardrails

<div class="lab-meta">
  <span><strong>Level:</strong> <span class="level-badge level-300">L300</span></span>
  <span><strong>Type:</strong> Challenge</span>
  <span><strong>Time:</strong> ~60 min</span>
  <span><strong>💰 Cost:</strong> <span class="level-badge cost-free">Free (local)</span></span>
</div>

## Scenario

OutdoorGear is preparing a customer-facing support agent. Before launch, the safety team gives you a small red-team set with safe questions, PII exposure, jailbreak attempts, harmful requests, and off-topic requests.

Your job is to implement a local guardrail layer that blocks, redacts, or allows each request correctly.

---

## Objective

Fix `starter_guardrails.py` so the guardrail layer classifies scenarios correctly, redacts email addresses, reports red-team metrics, and generates a validation code.

Your final guardrail layer should:

- Allow normal OutdoorGear support questions
- Redact email addresses before agent processing
- Block jailbreak attempts
- Block harmful physical-safety requests
- Block off-topic automation requests
- Avoid false positives on safe support questions

---

## Starter Files

Save these files in one folder named `challenge-007/`:

| File | Purpose | Download |
|------|---------|----------|
| `scenarios.json` | Red-team and safe scenarios | [Download](https://github.com/lcarli/AI-LearningHub/raw/main/docs/docs/en/challenges/challenge-007/scenarios.json) |
| `starter_guardrails.py` | Broken guardrail layer | [Download](https://github.com/lcarli/AI-LearningHub/raw/main/docs/docs/en/challenges/challenge-007/starter_guardrails.py) |
| `test_guardrails.py` | Acceptance tests | [Download](https://github.com/lcarli/AI-LearningHub/raw/main/docs/docs/en/challenges/challenge-007/test_guardrails.py) |
| `validate_guardrails.py` | Generates the final completion code | [Download](https://github.com/lcarli/AI-LearningHub/raw/main/docs/docs/en/challenges/challenge-007/validate_guardrails.py) |

---

## Challenge Brief

You receive scenario fixtures and a broken guardrail implementation. There is no walkthrough: decide which signals should trigger block, redact, or allow, and make the red-team metrics match the expected behavior.

---

## Constraints

- Use only the Python standard library in `starter_guardrails.py`.
- Do not hardcode behavior by scenario ID.
- Do not block normal product/return questions.
- Redaction should preserve the rest of the user request.
- Blocks should be deterministic.

---

## Acceptance Criteria

Your solution is complete when:

- `python -m pytest test_guardrails.py` passes
- Safe product and return questions are allowed
- Email addresses are redacted
- Jailbreak, harmful, and off-topic requests are blocked
- `false_positive == 0`

---

## Validation

When your implementation is ready, run:

```bash
python -m pytest test_guardrails.py
python validate_guardrails.py
```

Enter the completion code printed by `validate_guardrails.py`:

<div class="challenge-validator" data-answer="CH007-452A3ED6">
  <input type="text" aria-label="Completion code" placeholder="CH007-XXXXXXXX" />
  <button type="button">Validate</button>
  <p class="challenge-validator-result" aria-live="polite"></p>
</div>

---

## Hints

??? tip "Hint 1 — Redaction is not the same as blocking"
    A user can provide an email address in an otherwise valid support request.

??? tip "Hint 2 — Scope matters"
    A request can be harmless but still off-topic for an OutdoorGear support agent.

??? tip "Hint 3 — Safety patterns can be simple"
    This challenge does not need ML classification. Deterministic phrase and regex checks are enough.

---

## Rubric

| Area | Points | What good looks like |
|------|:------:|----------------------|
| Classification | 35 | Correct allow/block/redact decisions |
| PII handling | 20 | Email redacted without losing request meaning |
| Safety scope | 20 | Harmful and off-topic requests blocked |
| Metrics | 15 | Red-team summary is accurate |
| Simplicity | 10 | Small deterministic guardrail code |

---

## Related Labs

- [Lab 008 — Responsible AI for Agents](../labs/lab-008-responsible-ai.md)
- [Lab 036 — Prompt Injection Defense & Security](../labs/lab-036-prompt-injection-security.md)
- [Lab 082 — Agent Guardrails](../labs/lab-082-agent-guardrails.md)
