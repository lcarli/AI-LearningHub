---
tags: [challenge, observability, incident, tracing, python, local]
---
# Challenge 006: Investigate an Agent Observability Incident

<div class="lab-meta">
  <span><strong>Level:</strong> <span class="level-badge level-300">L300</span></span>
  <span><strong>Type:</strong> Challenge</span>
  <span><strong>Time:</strong> ~60 min</span>
  <span><strong>💰 Cost:</strong> <span class="level-badge cost-free">Free (local)</span></span>
</div>

## Scenario

OutdoorGear's support agent had a latency spike and one failed request. You receive a small trace export with root agent spans and child tool/LLM spans. The current incident analyzer calculates metrics over the wrong spans and reports the wrong root cause.

Your job is to fix the analyzer so an on-call engineer can identify the failed trace, dependency root cause, error rate, and p95 latency.

---

## Objective

Fix `starter_observability.py` so it summarizes the incident correctly and generates a validation code.

Your final analyzer should:

- Isolate root agent request spans
- Compute error rate over root requests only
- Compute nearest-rank p95 latency over root requests
- Identify the failed root trace
- Attribute root cause to the failing dependency span

---

## Starter Files

Save these files in one folder named `challenge-006/`:

| File | Purpose | Download |
|------|---------|----------|
| `traces.json` | Mock agent trace export | [Download](https://github.com/lcarli/AI-LearningHub/raw/main/docs/docs/en/challenges/challenge-006/traces.json) |
| `starter_observability.py` | Broken incident analyzer | [Download](https://github.com/lcarli/AI-LearningHub/raw/main/docs/docs/en/challenges/challenge-006/starter_observability.py) |
| `test_observability.py` | Acceptance tests | [Download](https://github.com/lcarli/AI-LearningHub/raw/main/docs/docs/en/challenges/challenge-006/test_observability.py) |
| `validate_observability.py` | Generates the final completion code | [Download](https://github.com/lcarli/AI-LearningHub/raw/main/docs/docs/en/challenges/challenge-006/validate_observability.py) |

---

## Challenge Brief

You receive trace spans and a broken analyzer. There is no walkthrough: decide which spans count as requests, how to compute SRE metrics, and how to attribute the incident to the right child dependency.

---

## Constraints

- Use only the Python standard library in `starter_observability.py`.
- Do not hardcode the final summary dictionary.
- Metrics must be computed from spans.
- Child spans can explain root cause, but they should not inflate request counts.

---

## Acceptance Criteria

Your solution is complete when:

- `python -m pytest test_observability.py` passes
- Root requests are `tr-001`, `tr-002`, `tr-003`, and `tr-004`
- Error rate is `25.0`
- p95 latency is `2200`
- Incident trace is `tr-003`
- Root cause is `inventory_api_timeout`

---

## Validation

When your implementation is ready, run:

```bash
python -m pytest test_observability.py
python validate_observability.py
```

Enter the completion code printed by `validate_observability.py`:

<div class="challenge-validator" data-answer="CH006-FC7D7B5F">
  <input type="text" aria-label="Completion code" placeholder="CH006-XXXXXXXX" />
  <button type="button">Validate</button>
  <p class="challenge-validator-result" aria-live="polite"></p>
</div>

---

## Hints

??? tip "Hint 1 — Separate request spans from child spans"
    Root request metrics should not count every tool or LLM span.

??? tip "Hint 2 — Root cause is usually below the root"
    The agent span tells you the request failed; the child dependency often tells you why.

??? tip "Hint 3 — p95 has a definition"
    Use nearest-rank p95 for this challenge.

---

## Rubric

| Area | Points | What good looks like |
|------|:------:|----------------------|
| Span filtering | 25 | Root agent requests are isolated correctly |
| Metrics | 30 | Error rate and p95 use the right denominator |
| Root cause | 25 | Dependency failure is identified correctly |
| Incident summary | 10 | Output is concise and actionable |
| Simplicity | 10 | Local deterministic analysis |

---

## Related Labs

- [Lab 033 — Agent Observability with App Insights](../labs/lab-033-agent-observability.md)
- [Lab 049 — Foundry IQ Agent Tracing](../labs/lab-049-foundry-iq-agent-tracing.md)
- [Lab 050 — Multi-Agent Observability](../labs/lab-050-multi-agent-observability.md)
