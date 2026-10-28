---
tags:
- llm
- tokens
- attention
- training
- hallucination
lab:
  id: '004'
  level: L50
  journey: llm-foundations
  time_min: 45
  cost:
    tier: free
    requires: []
    estimate_usd: 0 within the documented free path or simulation.
    simulation: true
    cleanup: false
  roles:
  - student
  - developer
  - architect
  technologies:
  - llm
  - tokens
  - attention
  - training
  - hallucination
  status: active
  last_verified: '2026-10-27'
  languages:
  - en
  - pt
  - fr
---
# Lab 004: How LLMs Work: Tokens, Attention, Training, and Hallucination

<div class="lab-meta">
  <span><strong>Level:</strong> <span class="level-badge level-50">L50</span></span>
  <span><strong>Journey:</strong> llm-foundations</span>
  <span><strong>Time:</strong> ~45 min</span>
  <span><strong>Cost:</strong> <span class="level-badge cost-free">Free</span></span>
</div>

!!! info "Free-first design"
    The required route is local, simulated, or works with GitHub Copilot Free. Any organization, cloud, or paid route is marked optional.

!!! tip "AI Credit impact"
    Keep the task bounded, use the smallest useful context, and validate locally. Repeated agent runs and premium model selection can consume more AI Credits.

## What You'll Learn

- Trace text through tokenization, next-token prediction, and decoding
- Explain pre-training, instruction tuning, preference alignment, and evaluation
- Use attention as a relationship mechanism rather than a human-memory analogy
- Diagnose hallucination as an optimization and evidence problem

## Prerequisites

- Python 3.10+ for the local exercise
- A text editor and terminal
- Lab 097

## Outcome and evidence

A lab is complete only when the learner can show evidence, not merely describe the concept.

| Capability | Required evidence |
|---|---|
| Trace text through tokenization, next-token prediction, and decoding | `evidence/step-1.txt` plus a passing local check |
| Explain pre-training, instruction tuning, preference alignment, and evaluation | `evidence/step-2.txt` plus a passing local check |
| Use attention as a relationship mechanism rather than a human-memory analogy | `evidence/step-3.txt` plus a passing local check |
| Diagnose hallucination as an optimization and evidence problem | `evidence/step-4.txt` plus a passing local check |

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
flowchart LR
  T[Text] --> K[Tokens]
  K --> A[Attention layers]
  A --> P[Next-token probabilities]
  P --> D[Decoder]
  D --> O[Output]
  E[Evidence and tools] --> A
```

## Scenario

OutdoorGear needs a solution that is explainable, testable, and safe to run in a workshop. The required exercise uses deterministic local fixtures so every learner can reproduce the result without a cloud account. A real service can later replace only the adapter boundary.

## Guided exercise

### Step 1

**Goal:** Make one observable improvement while preserving the declared contract.

**Action:** Run `token_attention_lab.py` and compare token estimates for prose, code, and JSON.

**Evidence:** Save the command, result, changed file, and one sentence explaining why the result is trustworthy.

**Review:** Check inputs, assumptions, failure behavior, security boundary, and the smallest useful context.

### Step 2

**Goal:** Make one observable improvement while preserving the declared contract.

**Action:** Inspect the probability table and choose the next token with greedy and sampled decoding.

**Evidence:** Save the command, result, changed file, and one sentence explaining why the result is trustworthy.

**Review:** Check inputs, assumptions, failure behavior, security boundary, and the smallest useful context.

### Step 3

**Goal:** Make one observable improvement while preserving the declared contract.

**Action:** Map query tokens to evidence tokens with the attention heat-map table.

**Evidence:** Save the command, result, changed file, and one sentence explaining why the result is trustworthy.

**Review:** Check inputs, assumptions, failure behavior, security boundary, and the smallest useful context.

### Step 4

**Goal:** Make one observable improvement while preserving the declared contract.

**Action:** Classify five answers as grounded, unsupported, outdated, or contradictory.

**Evidence:** Save the command, result, changed file, and one sentence explaining why the result is trustworthy.

**Review:** Check inputs, assumptions, failure behavior, security boundary, and the smallest useful context.

### Run locally

```bash
cd docs/docs/en/labs/lab-004
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

The downloadable kit contains the lab guide, local exercise files, a cheat sheet, and the diagrams referenced here. CI publishes deterministic PDF and ZIP artifacts.

| Item | Purpose |
|---|---|
| `README.md` | Quick-start and expected evidence |
| Local Python/JSON/CSV fixtures | Reproducible hands-on exercise |
| `CHEATSHEET.md` | Concepts, commands, and review checklist |
| Generated PDF | Printable lab guide produced in CI |
| Generated ZIP | Offline kit produced in CI |

## Optional real path

Replace only the adapter boundary with an approved hosted service. Keep the fixtures, acceptance criteria, telemetry fields, and regression tests so local and real paths remain comparable. Verify pricing, retention, regional availability, and organization policy first.

## Knowledge check

??? question "Why can a fluent answer still be false?"

    ??? success "Answer"
        Fluency optimizes likely continuation; truth requires evidence and verification.

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

- [The Illustrated Transformer](https://jalammar.github.io/illustrated-transformer/)
- [Attention Is All You Need](https://arxiv.org/abs/1706.03762)
