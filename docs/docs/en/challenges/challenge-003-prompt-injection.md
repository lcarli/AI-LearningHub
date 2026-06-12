---
tags: [challenge, security, prompt-injection, rag, python, local]
---
# Challenge 003: Defend an Agent from Prompt Injection

<div class="lab-meta">
  <span><strong>Level:</strong> <span class="level-badge level-200">L200</span></span>
  <span><strong>Type:</strong> Challenge</span>
  <span><strong>Time:</strong> ~60 min</span>
  <span><strong>💰 Cost:</strong> <span class="level-badge cost-free">Free (local)</span></span>
</div>

## Scenario

OutdoorGear imported customer reviews into a support-agent knowledge base. One imported review contains malicious instructions that try to override the agent's policy, reveal hidden instructions, and claim returns are unlimited.

Your job is to harden a local RAG-style support helper so it blocks prompt-injection attempts, excludes unsafe context, and answers safe questions from trusted policy documents only.

---

## Objective

Fix `starter_prompt_defense.py` so the defense suite blocks attacks, allows safe requests, removes malicious context, avoids leaking attacker text, and generates a validation code.

Your final defense should:

- Normalize text before policy checks
- Detect common prompt-injection patterns
- Remove untrusted or malicious context from retrieved documents
- Block malicious user requests
- Answer safe requests using only trusted context
- Report defense metrics accurately

---

## Starter Files

Save these files in one folder named `challenge-003/`:

| File | Purpose | Download |
|------|---------|----------|
| `documents.json` | Trusted and untrusted support context | [Download](https://github.com/lcarli/AI-LearningHub/raw/main/docs/docs/en/challenges/challenge-003/documents.json) |
| `requests.json` | Safe and malicious user requests | [Download](https://github.com/lcarli/AI-LearningHub/raw/main/docs/docs/en/challenges/challenge-003/requests.json) |
| `starter_prompt_defense.py` | Broken defense implementation | [Download](https://github.com/lcarli/AI-LearningHub/raw/main/docs/docs/en/challenges/challenge-003/starter_prompt_defense.py) |
| `test_prompt_defense.py` | Acceptance tests | [Download](https://github.com/lcarli/AI-LearningHub/raw/main/docs/docs/en/challenges/challenge-003/test_prompt_defense.py) |
| `validate_prompt_defense.py` | Generates the final completion code | [Download](https://github.com/lcarli/AI-LearningHub/raw/main/docs/docs/en/challenges/challenge-003/validate_prompt_defense.py) |

---

## Challenge Brief

You receive mixed-trust documents, safe requests, attack requests, and a broken defense layer. There is no walkthrough: decide how to detect attack intent, filter context, answer safely, and evaluate whether the agent leaked attacker-controlled instructions.

---

## Constraints

- Use only the Python standard library in `starter_prompt_defense.py`.
- Do not call an LLM API.
- Do not hardcode behavior by request ID.
- Do not answer from untrusted customer-review content.
- Safe requests must still be answered.
- Attack text must not appear in safe answers.

---

## Acceptance Criteria

Your solution is complete when:

- `python -m pytest test_prompt_defense.py` passes
- All three attack requests are blocked
- Both safe requests are allowed
- The malicious review is excluded from safe context
- Safe answers cite official policy facts
- `leakage_count == 0`

---

## Validation

When your implementation is ready, run:

```bash
python -m pytest test_prompt_defense.py
python validate_prompt_defense.py
```

Enter the completion code printed by `validate_prompt_defense.py`:

<div class="challenge-validator" data-answer="CH003-EF57BB85">
  <input type="text" aria-label="Completion code" placeholder="CH003-XXXXXXXX" />
  <button type="button">Validate</button>
  <p class="challenge-validator-result" aria-live="polite"></p>
</div>

---

## Hints

??? tip "Hint 1 — Treat user input and retrieved context separately"
    A user request can be malicious, but retrieved documents can also contain malicious instructions.

??? tip "Hint 2 — Trust metadata matters"
    The fixture includes a `trusted` field. Use it, but do not rely on metadata alone.

??? tip "Hint 3 — Look for intent, not only exact phrases"
    Attackers may say "ignore", "bypass", "admin_override", or "system prompt" in different casing.

??? tip "Hint 4 — Safe answers should be boring"
    A safe policy answer should quote policy facts. It should not mention hidden prompts, overrides, or unlimited returns.

---

## Rubric

| Area | Points | What good looks like |
|------|:------:|----------------------|
| Attack detection | 30 | Blocks varied prompt-injection patterns |
| Context filtering | 25 | Removes unsafe context while preserving trusted policy docs |
| Safe answering | 20 | Answers safe requests from official evidence |
| Leakage prevention | 15 | No attacker-controlled strings in answers |
| Simplicity | 10 | Deterministic local checks, no over-engineering |

---

## Stretch Goals

- Add severity levels for attacks
- Return a safe refusal message for blocked requests
- Add per-document reasons for exclusion
- Add a new attack variant and update the validator payload locally

---

## Related Labs

- [Lab 008 — Responsible AI for Agents](../labs/lab-008-responsible-ai.md)
- [Lab 036 — Prompt Injection Defense & Security](../labs/lab-036-prompt-injection-security.md)
- [Lab 082 — Agent Guardrails](../labs/lab-082-agent-guardrails.md)
