---
tags:
- streaming
- sse
- ux
- local
lab:
  id: 019
  level: L100
  journey: llm-foundations
  time_min: 50
  cost:
    tier: free
    requires: []
    estimate_usd: 0 within the documented free path or simulation.
    simulation: true
    cleanup: false
  roles:
  - developer
  - student
  technologies:
  - streaming
  - sse
  - ux
  - local
  status: active
  last_verified: '2026-10-27'
  languages:
  - en
  - pt
  - fr
---
# Lab 019: Streaming Responses: Events, Cancellation, and Safe UX

<div class="lab-meta">
  <span><strong>Level:</strong> <span class="level-badge level-100">L100</span></span>
  <span><strong>Journey:</strong> llm-foundations</span>
  <span><strong>Time:</strong> ~50 min</span>
  <span><strong>Cost:</strong> <span class="level-badge cost-free">Free</span></span>
</div>

!!! info "Free-first design"
    The required route is local, simulated, or works with GitHub Copilot Free. Any organization, cloud, or paid route is marked optional.

!!! tip "AI Credit impact"
    Keep the task bounded, use the smallest useful context, and validate locally. Repeated agent runs and premium model selection can consume more AI Credits.

## What You'll Learn

- Model streaming as typed events rather than raw text fragments
- Handle partial JSON, cancellation, retries, and final usage metadata
- Keep moderation and tool approvals outside the rendering loop
- Measure time-to-first-event and total completion time

## Prerequisites

- Python 3.10+ for the local exercise
- A text editor and terminal
- Lab 070

## Outcome and evidence

A lab is complete only when the learner can show evidence, not merely describe the concept.

| Capability | Required evidence |
|---|---|
| Model streaming as typed events rather than raw text fragments | `evidence/step-1.txt` plus a passing local check |
| Handle partial JSON, cancellation, retries, and final usage metadata | `evidence/step-2.txt` plus a passing local check |
| Keep moderation and tool approvals outside the rendering loop | `evidence/step-3.txt` plus a passing local check |
| Measure time-to-first-event and total completion time | `evidence/step-4.txt` plus a passing local check |

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
sequenceDiagram
  participant C as Client
  participant A as Agent
  C->>A: request
  A-->>C: response.started
  A-->>C: content.delta
  A-->>C: tool.arguments.done
  A-->>C: response.completed + usage
  C->>A: cancel (optional)
```

## Scenario

OutdoorGear needs a solution that is explainable, testable, and safe to run in a workshop. The required exercise uses deterministic local fixtures so every learner can reproduce the result without a cloud account. A real service can later replace only the adapter boundary.

## Guided exercise

### Step 1

**Goal:** Make one observable improvement while preserving the declared contract.

**Action:** Run `streaming_demo.py` to replay a deterministic event stream.

**Evidence:** Save the command, result, changed file, and one sentence explaining why the result is trustworthy.

**Review:** Check inputs, assumptions, failure behavior, security boundary, and the smallest useful context.

### Step 2

**Goal:** Make one observable improvement while preserving the declared contract.

**Action:** Cancel after the third delta and verify cleanup runs once.

**Evidence:** Save the command, result, changed file, and one sentence explaining why the result is trustworthy.

**Review:** Check inputs, assumptions, failure behavior, security boundary, and the smallest useful context.

### Step 3

**Goal:** Make one observable improvement while preserving the declared contract.

**Action:** Buffer tool arguments until the complete event arrives.

**Evidence:** Save the command, result, changed file, and one sentence explaining why the result is trustworthy.

**Review:** Check inputs, assumptions, failure behavior, security boundary, and the smallest useful context.

### Step 4

**Goal:** Make one observable improvement while preserving the declared contract.

**Action:** Compare perceived latency with and without progressive rendering.

**Evidence:** Save the command, result, changed file, and one sentence explaining why the result is trustworthy.

**Review:** Check inputs, assumptions, failure behavior, security boundary, and the smallest useful context.

### Run locally

```bash
cd docs/docs/en/labs/lab-019
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

The downloadable kit contains the lab guide, local exercise files, a cheat sheet, and the diagrams referenced here. The site build generates stable PDF and ZIP downloads; CI also keeps a temporary artifact mirror for 30 days.

| Item | Purpose |
|---|---|
| [`README.md`](lab-019/README.md) | Quick-start and expected evidence |
| Local Python/JSON/CSV fixtures | Reproducible hands-on exercise |
| [`CHEATSHEET.md`](lab-019/CHEATSHEET.md) | Concepts, commands, and review checklist |
| [Generated PDF](../downloads/kits/lab-019-kit-en.pdf) | Printable lab guide produced in CI |
| [Generated ZIP](../downloads/kits/lab-019-kit-en.zip) | Offline kit produced in CI |

## Optional real path

Replace only the adapter boundary with an approved hosted service. Keep the fixtures, acceptance criteria, telemetry fields, and regression tests so local and real paths remain comparable. Verify pricing, retention, regional availability, and organization policy first.

## Knowledge check

??? question "Why not parse JSON from every text delta?"

    ??? success "Answer"
        A delta is incomplete by design; parse only the completed typed payload.

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

- [Server-Sent Events](https://html.spec.whatwg.org/multipage/server-sent-events.html)
