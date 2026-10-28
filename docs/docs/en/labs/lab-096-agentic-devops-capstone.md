---
tags:
- github-copilot
- devops
- spec-driven
- cicd
- observability
lab:
  id: 096
  level: L400
  journey: copilot
  time_min: 210
  cost:
    tier: free-conditional
    requires:
    - github
    - copilot-free
    estimate_usd: 0 within the documented free path or simulation.
    simulation: true
    cleanup: false
  roles:
  - developer
  - student
  - architect
  technologies:
  - github-copilot
  - devops
  - spec-driven
  - cicd
  - observability
  status: active
  last_verified: '2026-10-27'
  languages:
  - en
  - pt
  - fr
---
# Lab 096: Capstone — Agentic DevOps: Spec → Plan → Agent → Review → Deploy

<div class="lab-meta">
  <span><strong>Level:</strong> <span class="level-badge level-400">L400</span></span>
  <span><strong>Journey:</strong> copilot</span>
  <span><strong>Time:</strong> ~210 min</span>
  <span><strong>Cost:</strong> <span class="level-badge cost-free">Free in a public repository; paid features are optional</span></span>
</div>

!!! info "Free-first design"
    The required route is local, simulated, or works with GitHub Copilot Free. Any organization, cloud, or paid route is marked optional.

!!! tip "AI Credit impact"
    Keep the task bounded, use the smallest useful context, and validate locally. Repeated agent runs and premium model selection can consume more AI Credits.

## What You'll Learn

- Turn an ambiguous request into an acceptance-testable specification
- Use plan and agent boundaries with review checkpoints
- Gate CI/CD on tests, security, and human approval
- Connect deployment evidence to observability and rollback

## Prerequisites

- Python 3.10+ for the local exercise
- A text editor and terminal
- Challenge 010

## Outcome and evidence

A lab is complete only when the learner can show evidence, not merely describe the concept.

| Capability | Required evidence |
|---|---|
| Turn an ambiguous request into an acceptance-testable specification | `evidence/step-1.txt` plus a passing local check |
| Use plan and agent boundaries with review checkpoints | `evidence/step-2.txt` plus a passing local check |
| Gate CI/CD on tests, security, and human approval | `evidence/step-3.txt` plus a passing local check |
| Connect deployment evidence to observability and rollback | `evidence/step-4.txt` plus a passing local check |

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
  S[Spec] --> P[Plan]
  P --> A[Agent implementation]
  A --> R[Human and Copilot review]
  R --> C[CI/CD gates]
  C --> D[Deploy]
  D --> O[Observability]
  O -->|failure| B[Rollback]
  O -->|healthy| E[Evidence]
```

## Scenario

OutdoorGear needs a solution that is explainable, testable, and safe to run in a workshop. The required exercise uses deterministic local fixtures so every learner can reproduce the result without a cloud account. A real service can later replace only the adapter boundary.

## Guided exercise

### Step 1

**Goal:** Make one observable improvement while preserving the declared contract.

**Action:** Complete `capstone_spec.md` with scope, non-goals, risks, and acceptance criteria.

**Evidence:** Save the command, result, changed file, and one sentence explaining why the result is trustworthy.

**Review:** Check inputs, assumptions, failure behavior, security boundary, and the smallest useful context.

### Step 2

**Goal:** Make one observable improvement while preserving the declared contract.

**Action:** Generate a file-level plan and implement one vertical slice.

**Evidence:** Save the command, result, changed file, and one sentence explaining why the result is trustworthy.

**Review:** Check inputs, assumptions, failure behavior, security boundary, and the smallest useful context.

### Step 3

**Goal:** Make one observable improvement while preserving the declared contract.

**Action:** Run local tests and the workflow validator before review.

**Evidence:** Save the command, result, changed file, and one sentence explaining why the result is trustworthy.

**Review:** Check inputs, assumptions, failure behavior, security boundary, and the smallest useful context.

### Step 4

**Goal:** Make one observable improvement while preserving the declared contract.

**Action:** Simulate deployment, health checks, telemetry, incident detection, and rollback.

**Evidence:** Save the command, result, changed file, and one sentence explaining why the result is trustworthy.

**Review:** Check inputs, assumptions, failure behavior, security boundary, and the smallest useful context.

### Run locally

```bash
cd docs/docs/en/labs/lab-096
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

??? question "Who authorizes production deployment?"

    ??? success "Answer"
        A defined human or protected environment gate, never the model alone.

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

- [GitHub Copilot coding agent](https://docs.github.com/copilot/concepts/agents/coding-agent/about-coding-agent)
- [GitHub Actions environments](https://docs.github.com/actions/deployment/targeting-different-environments/managing-environments-for-deployment)
