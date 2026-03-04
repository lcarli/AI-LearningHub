---
tags: [security, entra-id, obo, identity, oauth, enterprise]
---
# Lab 063: Agent Identity — Entra OBO Flow & Least Privilege

<div class="lab-meta">
  <span><strong>Level:</strong> <span class="level-badge level-300">L300</span></span>
  <span><strong>Path:</strong> All paths</span>
  <span><strong>Time:</strong> ~75 min</span>
  <span><strong>💰 Cost:</strong> <span class="level-badge cost-free">Free</span> — Uses mock scenario data (no Entra tenant required)</span>
</div>

## What You'll Learn

- How the **OAuth 2.0 On-Behalf-Of (OBO) flow** passes user identity through an agent chain
- The difference between **delegated permissions** (act as user) and **application permissions** (act as app)
- Identify **compliance violations** in agent permission configurations
- Apply **least-privilege principles** to agent identity design
- Implement **human-in-the-loop** gates for high-risk agent actions
- Analyze a **15-scenario dataset** across 4 agents for security posture

---

## Introduction

When agents access enterprise resources — reading email, querying databases, modifying SharePoint — they need an identity. **How** they authenticate determines the security posture of your entire system.

The **On-Behalf-Of (OBO) flow** ensures agents act with the user's identity and permissions, maintaining the principle of least privilege. The alternative — **client_credentials** (application permissions) — gives the agent its own identity with potentially broad access, bypassing user-level authorization.

This lab analyzes 15 real-world scenarios to show why OBO is the default choice and when client_credentials creates compliance risks.

### The Scenarios

You'll examine **15 scenarios** across **4 agents**, each with different permission configurations:

| Agent | Description | Scenarios |
|-------|-------------|-----------|
| **MailAgent** | Reads and sends email on behalf of users | 4 |
| **FileAgent** | Accesses SharePoint and OneDrive files | 4 |
| **CalendarAgent** | Manages calendar events and scheduling | 4 |
| **AdminAgent** | Performs directory and compliance operations | 3 |

---

## Prerequisites

```bash
pip install pandas
```

This lab analyzes pre-computed scenario data — no Entra ID tenant, Azure subscription, or application registration required. To implement OBO flows in production, you would need an Entra ID tenant with app registrations.

---

## Part 1: Understanding OBO Flow

### Step 1: OBO vs client_credentials

The two primary authentication flows for agents:

```
OBO Flow (Delegated — Recommended):
  User → [Auth] → Agent → [OBO token exchange] → Resource API
  Agent acts AS the user — user's permissions apply

Client Credentials (Application — Use with caution):
  Agent → [App secret/cert] → Resource API
  Agent acts AS ITSELF — app permissions apply (often broader)
```

Key concepts:

| Concept | Description |
|---------|-------------|
| **OBO (On-Behalf-Of)** | Agent exchanges user token for downstream API token, preserving user identity |
| **Delegated permissions** | Agent acts as the signed-in user — limited to user's own access |
| **Application permissions** | Agent acts as itself — can access all users' data (e.g., read ALL mailboxes) |
| **Least privilege** | Grant only the minimum permissions needed for the task |
| **Human-in-the-loop** | Require explicit user approval for high-risk actions |

!!! warning "Why OBO Matters"
    With client_credentials, a MailAgent could read **every user's** email — not just the requesting user's. OBO ensures the agent can only access what the user themselves can access. This is the difference between a controlled tool and a security liability.

---

## Part 2: Load Scenario Data

### Step 2: Load `identity_scenarios.csv`

The scenario dataset contains 15 identity configurations across 4 agents:

```python
# identity_analysis.py
import pandas as pd

scenarios = pd.read_csv("lab-063/identity_scenarios.csv")

print(f"Scenarios: {len(scenarios)}")
print(f"Agents: {scenarios['agent'].unique().tolist()}")
print(f"Auth flows: {scenarios['auth_flow'].unique().tolist()}")
print(scenarios[["scenario_id", "agent", "auth_flow", "risk_level", "compliant"]].to_string(index=False))
```

**Expected output:**

```
Scenarios: 15
Agents: ['MailAgent', 'FileAgent', 'CalendarAgent', 'AdminAgent']
Auth flows: ['obo', 'client_credentials']

scenario_id          agent          auth_flow risk_level  compliant
        S01      MailAgent                obo        low       True
        S02      MailAgent                obo        low       True
        S03      MailAgent                obo     medium       True
        S04      MailAgent                obo     medium       True
        S05      MailAgent  client_credentials   critical      False
        S06      FileAgent                obo        low       True
        S07      FileAgent  client_credentials   critical      False
        S08      FileAgent                obo     medium       True
        S09      FileAgent                obo        low       True
        S10   CalendarAgent  client_credentials   critical      False
        S11   CalendarAgent                obo        low       True
        S12   CalendarAgent                obo     medium       True
        S13      AdminAgent                obo       high       True
        S14      AdminAgent  client_credentials       high      False
        S15      AdminAgent                obo     medium       True
```

---

## Part 3: Compliance Analysis

### Step 3: Identify compliance violations

```python
# Compliance violations
violations = scenarios[scenarios["compliant"] == False]
print(f"Compliance violations: {len(violations)}/{len(scenarios)}")
print("\nViolation details:")
print(violations[["scenario_id", "agent", "auth_flow", "risk_level", "description"]].to_string(index=False))
```

**Expected output:**

```
Compliance violations: 4/15

Violation details:
scenario_id          agent          auth_flow risk_level                                          description
        S05      MailAgent  client_credentials   critical  Read all users' mail with app-level permissions
        S07      FileAgent  client_credentials   critical  Access all SharePoint sites without user context
        S10   CalendarAgent  client_credentials   critical  Modify any user's calendar without delegation
        S14      AdminAgent  client_credentials       high  Directory read with app permissions instead of OBO
```

!!! warning "Critical Finding"
    All 4 compliance violations use **client_credentials** — not OBO. Three are critical-risk (S05, S07, S10) because they grant broad access to all users' data. The pattern is clear: client_credentials without scoping creates compliance violations.

```python
# Verify: do all violations use client_credentials?
violation_flows = violations["auth_flow"].unique().tolist()
print(f"\nAuth flows in violations: {violation_flows}")
print(f"All violations use client_credentials: {violation_flows == ['client_credentials']}")
```

**Expected output:**

```
Auth flows in violations: ['client_credentials']
All violations use client_credentials: True
```

---

## Part 4: Risk Level Analysis

### Step 4: Analyze risk distribution

```python
# Risk level distribution
print("Risk level distribution:")
for level in ["low", "medium", "high", "critical"]:
    count = len(scenarios[scenarios["risk_level"] == level])
    if count > 0:
        print(f"  {level:>8}: {count}")

# Critical-risk scenarios
critical = scenarios[scenarios["risk_level"] == "critical"]
print(f"\nCritical-risk scenarios: {len(critical)}")
print(critical[["scenario_id", "agent", "auth_flow", "description"]].to_string(index=False))
```

**Expected output:**

```
Risk level distribution:
      low: 5
   medium: 4
     high: 3
 critical: 3

Critical-risk scenarios: 3
scenario_id          agent          auth_flow                                          description
        S05      MailAgent  client_credentials  Read all users' mail with app-level permissions
        S07      FileAgent  client_credentials  Access all SharePoint sites without user context
        S10   CalendarAgent  client_credentials  Modify any user's calendar without delegation
```

!!! info "Risk Pattern"
    All 3 critical-risk scenarios involve agents with **client_credentials accessing user data** (mail, files, calendar) without user context. The AdminAgent's client_credentials scenario (S14) is high-risk but not critical because directory reads are less sensitive than accessing individual users' data.

---

## Part 5: OBO Flow Analysis

### Step 5: OBO adoption rate

```python
# OBO vs client_credentials
obo_count = len(scenarios[scenarios["auth_flow"] == "obo"])
total = len(scenarios)
obo_pct = obo_count / total * 100

print(f"OBO flow: {obo_count}/{total} = {obo_pct:.1f}%")
print(f"Client credentials: {total - obo_count}/{total} = {(total - obo_count)/total*100:.1f}%")

# OBO by agent
print("\nOBO usage by agent:")
for agent in scenarios["agent"].unique():
    agent_data = scenarios[scenarios["agent"] == agent]
    agent_obo = len(agent_data[agent_data["auth_flow"] == "obo"])
    agent_total = len(agent_data)
    print(f"  {agent:>15}: {agent_obo}/{agent_total} OBO")
```

**Expected output:**

```
OBO flow: 11/15 = 73.3%
Client credentials: 4/15 = 26.7%

OBO usage by agent:
      MailAgent: 4/5 OBO
      FileAgent: 3/4 OBO
  CalendarAgent: 2/4 OBO
     AdminAgent: 2/3 OBO
```

73.3% of scenarios use OBO — good, but the 26.7% using client_credentials accounts for **all** compliance violations. Every agent has at least one client_credentials scenario that should be reviewed.

---

## Part 6: Remediation Strategy

### Step 6: Fix compliance violations

For each violation, the remediation is to switch from client_credentials to OBO:

| Scenario | Current | Fix | Notes |
|----------|---------|-----|-------|
| S05 | App reads all mail | OBO — read only requesting user's mail | Eliminates cross-user data access |
| S07 | App accesses all SharePoint | OBO — access only user's authorized sites | Respects site permissions |
| S10 | App modifies any calendar | OBO — modify only user's own calendar | Prevents cross-user modification |
| S14 | App directory read | OBO — directory read as user | Limits scope to user's directory view |

```python
# Compliance improvement after remediation
compliant_count = scenarios["compliant"].sum()
total = len(scenarios)
print(f"Current compliance: {compliant_count}/{total} = {compliant_count/total*100:.1f}%")
print(f"After remediation:  {total}/{total} = 100.0%")
print(f"\nAction: Convert {total - compliant_count} client_credentials scenarios to OBO")
```

### Step 7: Human-in-the-loop for high-risk actions

Even with OBO, some actions warrant explicit user approval:

```python
# High-risk + medium scenarios that should have human-in-the-loop
hitl_candidates = scenarios[scenarios["risk_level"].isin(["high", "critical", "medium"])]
print(f"Scenarios needing human-in-the-loop review: {len(hitl_candidates)}")
print(hitl_candidates[["scenario_id", "agent", "risk_level", "description"]].to_string(index=False))
```

!!! info "Defense in Depth"
    OBO + least privilege + human-in-the-loop form three layers of defense. OBO ensures correct identity. Least privilege limits what that identity can do. Human-in-the-loop adds a confirmation step for sensitive actions — even if the agent has permission, the user explicitly approves.

---

## 🐛 Bug-Fix Exercise

The file `lab-063/broken_identity.py` has **3 bugs** in the identity analysis functions. Run the self-tests:

```bash
python lab-063/broken_identity.py
```

You should see **3 failed tests**:

| Test | What it checks | Hint |
|------|---------------|------|
| Test 1 | Compliance violation count | Are you counting `compliant == True` instead of `compliant == False`? |
| Test 2 | Critical-risk count | Are you filtering for `risk_level == "high"` instead of `risk_level == "critical"`? |
| Test 3 | OBO percentage | Are you filtering for `auth_flow == "client_credentials"` instead of `auth_flow == "obo"`? |

Fix all 3 bugs and re-run until you see `🎉 All 3 tests passed`.

---

## 📁 Supporting Files

```
lab-063/
├── identity_scenarios.csv  ← 15 scenarios × 4 agents (auth flow, risk, compliance)
└── broken_identity.py      ← Bug-fix exercise (3 bugs + self-tests)
```

**Quick start:**

```bash
pip install pandas
cd docs/docs/en/labs

# Follow along with the lab steps
python -c "import pandas; print('ready!')"

# Or fix the bugs
python lab-063/broken_identity.py
```

---

## 🧠 Knowledge Check

??? question "**Q1 (Multiple Choice):** What is the purpose of the OAuth 2.0 On-Behalf-Of (OBO) flow?"

    - A) To give agents their own independent identity with full admin access
    - B) To pass the user's identity through the agent chain so the agent acts as the user
    - C) To bypass authentication entirely for faster agent execution
    - D) To create a new user account for each agent instance

    ??? success "✅ Reveal Answer"
        **Correct: B) To pass the user's identity through the agent chain so the agent acts as the user**

        The OBO flow exchanges the user's token for a downstream API token, preserving the user's identity and permissions. The agent acts **as** the user — it can only access what the user can access. This is the foundation of least-privilege agent identity: the agent inherits the user's authorization scope, not a broad application-level scope.

??? question "**Q2 (Multiple Choice):** What is the key difference between delegated and application permissions?"

    - A) Delegated is faster; application is more accurate
    - B) Delegated acts as the signed-in user; application acts as the app itself
    - C) Delegated requires no authentication; application requires OAuth
    - D) There is no practical difference — they are interchangeable

    ??? success "✅ Reveal Answer"
        **Correct: B) Delegated acts as the signed-in user; application acts as the app itself**

        With **delegated permissions** (OBO), the agent acts as the user — it can read the user's own email but not other users' email. With **application permissions** (client_credentials), the agent acts as itself with app-level access — it could read ALL users' email. This distinction is critical: all 4 compliance violations in the benchmark use application permissions where delegated permissions should have been used.

??? question "**Q3 (Run the Lab):** How many compliance violations exist in the 15 scenarios?"

    Calculate `(scenarios["compliant"] == False).sum()`.

    ??? success "✅ Reveal Answer"
        **4 violations (S05, S07, S10, S14)**

        Four scenarios are non-compliant: S05 (MailAgent reads all users' mail), S07 (FileAgent accesses all SharePoint), S10 (CalendarAgent modifies any calendar), and S14 (AdminAgent directory read with app permissions). All four use client_credentials instead of OBO, granting broader access than necessary.

??? question "**Q4 (Run the Lab):** How many scenarios are classified as critical risk?"

    Calculate `(scenarios["risk_level"] == "critical").sum()`.

    ??? success "✅ Reveal Answer"
        **3 scenarios (S05, S07, S10)**

        Three scenarios are critical-risk: S05 (MailAgent), S07 (FileAgent), and S10 (CalendarAgent). All three involve agents using client_credentials to access user data (mail, files, calendar) without user context. S14 (AdminAgent) is high-risk but not critical because directory reads are less sensitive than accessing individual users' personal data.

??? question "**Q5 (Run the Lab):** What percentage of scenarios use the OBO flow?"

    Calculate `(scenarios["auth_flow"] == "obo").sum() / len(scenarios) * 100`.

    ??? success "✅ Reveal Answer"
        **73.3% (11/15)**

        11 of 15 scenarios use OBO — a solid majority, but the remaining 4 (26.7%) using client_credentials account for all compliance violations. The remediation path is clear: convert all 4 client_credentials scenarios to OBO, bringing compliance from 73.3% to 100%. Every agent (MailAgent, FileAgent, CalendarAgent, AdminAgent) has at least one scenario that needs conversion.

---

## Summary

| Topic | What You Learned |
|-------|-----------------|
| OBO Flow | Passes user identity through agent chain — agent acts as user |
| Delegated vs Application | Delegated = user scope; Application = app-wide scope |
| Compliance | 4/15 violations — all from client_credentials, not OBO |
| Risk Levels | 3 critical-risk scenarios — all client_credentials accessing user data |
| OBO Adoption | 73.3% OBO — the 26.7% client_credentials causes all violations |
| Remediation | Convert client_credentials to OBO; add human-in-the-loop for high risk |

---

## Next Steps

- **[Lab 062](lab-062-ondevice-phi-silica.md)** — On-Device Agents with Phi Silica (privacy through on-device inference)
- **[Lab 061](lab-061-slm-phi4-mini.md)** — SLMs with Phi-4 Mini (another approach to privacy-first AI)
- **[Lab 042](lab-042-enterprise-rag.md)** — Enterprise RAG (applying identity controls to data retrieval)
