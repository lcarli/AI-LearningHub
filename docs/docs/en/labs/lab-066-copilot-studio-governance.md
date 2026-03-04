---
tags: [copilot-studio, governance, dlp, power-platform, enterprise]
---
# Lab 066: Copilot Studio Enterprise Governance

<div class="lab-meta">
  <span><strong>Level:</strong> <span class="level-badge level-300">L300</span></span>
  <span><strong>Path:</strong> All paths</span>
  <span><strong>Time:</strong> ~75 min</span>
  <span><strong>💰 Cost:</strong> <span class="level-badge cost-free">Free</span> — Mock data (no Copilot Studio license required)</span>
</div>

## What You'll Learn

- How to **audit Copilot Studio agents** across a Power Platform tenant
- Enforce **DLP policies** on agent connectors and data flows
- Detect **ungoverned agents** created outside of IT-managed environments
- Apply **environment-level security** to isolate production agents
- Identify **compliance gaps** between citizen-developed and IT-managed agents
- Build a **governance dashboard** summarizing agent posture

!!! abstract "Prerequisite"
    Complete **[Lab 065: Purview DSPM for AI](lab-065-purview-dspm-ai.md)** first. This lab assumes familiarity with data governance concepts and DLP policy fundamentals.

## Introduction

As organizations adopt **Microsoft Copilot Studio**, citizen developers and professional developers alike create agents across the Power Platform. Without proper governance, agents proliferate unchecked — connecting to sensitive data sources, bypassing DLP policies, and operating without audit trails.

**Copilot Studio Enterprise Governance** addresses these challenges:

- Which agents exist and who created them?
- Do agents comply with organizational **DLP policies**?
- Are agents operating in **managed environments** or personal sandboxes?
- Which agents have **failed security scans**?

| Governance Capability | What It Does | Example |
|----------------------|-------------|---------|
| **Agent Inventory** | Catalogs all agents across the tenant | 12 agents across 4 environments |
| **DLP Enforcement** | Evaluates connector usage against DLP rules | Block agents using unapproved external APIs |
| **Security Scanning** | Detects misconfigurations and vulnerabilities | Agent exposing internal KB without auth |
| **Environment Isolation** | Separates dev/test/prod agents | Production agents locked to IT-managed environments |
| **Creator Governance** | Tracks citizen vs IT-created agents | Flag unreviewed citizen-developed agents |

### The Scenario

You are a **Power Platform Administrator** tasked with auditing all Copilot Studio agents in your tenant. The organization has **12 agents** built by different teams. Some were created by IT, others by citizen developers. Your job: identify ungoverned agents, flag DLP violations, and produce a governance report.

---

## Prerequisites

| Requirement | Why |
|---|---|
| Python 3.10+ | Run analysis scripts |
| `pandas` | Analyze agent inventory data |

```bash
pip install pandas
```

---

## Step 1: Understanding Copilot Studio Governance

Copilot Studio governance operates through multiple layers:

```
Tenant Admin Center → Environment Management → DLP Policies → Agent Inventory
                                                                     ↓
Governance Report ← Security Scan ← Connector Audit ←──────── Agent Config
```

Each agent is evaluated against:

1. **Environment classification** — Is the agent in a managed or default environment?
2. **DLP policy compliance** — Does the agent use only approved connectors?
3. **Security scan status** — Has the agent passed automated security checks?
4. **Creator type** — Was it built by IT or a citizen developer?

!!! info "Citizen vs IT-Managed Agents"
    Citizen-developed agents are created by business users using low-code tools. While they accelerate innovation, they often lack security reviews, proper error handling, and compliance controls. Governance ensures these agents meet the same standards as IT-managed ones.

---

## Step 2: Load and Explore the Agent Inventory

The dataset contains **12 Copilot Studio agents** across the tenant:

```python
import pandas as pd

agents = pd.read_csv("lab-066/studio_agents.csv")
print(f"Total agents: {len(agents)}")
print(f"Environments: {sorted(agents['environment'].unique())}")
print(f"Creator types: {sorted(agents['creator_type'].unique())}")
print(f"\nAgents per environment:")
print(agents.groupby("environment")["agent_id"].count().sort_values(ascending=False))
```

**Expected:**

```
Total agents: 12
Environments: ['Default', 'Development', 'Production', 'Sandbox']
Creator types: ['citizen', 'it_managed']
```

---

## Step 3: DLP Policy Compliance Check

Identify agents that violate DLP policies:

```python
dlp_violations = agents[agents["dlp_compliant"] == False]
print(f"DLP non-compliant agents: {len(dlp_violations)}")
print(dlp_violations[["agent_id", "agent_name", "environment", "creator_type", "connector_count"]]
      .to_string(index=False))
```

**Expected:**

```
DLP non-compliant agents: 4
```

!!! warning "Connector Risk"
    Non-compliant agents typically use connectors that access external APIs or data sources outside of the organization's approved list. Each unapproved connector represents a potential data exfiltration path.

---

## Step 4: Security Scan Analysis

Check which agents have failed security scans:

```python
failed_scans = agents[agents["security_scan"] == "failed"]
print(f"Failed security scans: {len(failed_scans)}")
print(failed_scans[["agent_id", "agent_name", "creator_type", "environment"]].to_string(index=False))

unprotected = agents[agents["authentication"] == "none"]
print(f"\nAgents without authentication: {len(unprotected)}")
print(unprotected[["agent_id", "agent_name", "environment"]].to_string(index=False))
```

**Expected:**

```
Failed security scans: 3

Agents without authentication: 3
```

!!! danger "Unprotected Agents"
    Agents without authentication are publicly accessible. Any user — or external attacker — can interact with them. These agents must be immediately secured or disabled.

---

## Step 5: Citizen Developer Governance

Analyze the split between citizen-developed and IT-managed agents:

```python
citizen = agents[agents["creator_type"] == "citizen"]
it_managed = agents[agents["creator_type"] == "it_managed"]
print(f"Citizen-created agents: {len(citizen)}")
print(f"IT-managed agents: {len(it_managed)}")
print(f"\nCitizen agents by environment:")
print(citizen.groupby("environment")["agent_id"].count().sort_values(ascending=False))

citizen_noncompliant = citizen[citizen["dlp_compliant"] == False]
print(f"\nCitizen agents violating DLP: {len(citizen_noncompliant)}")
```

**Expected:**

```
Citizen-created agents: 8
IT-managed agents: 4
```

!!! tip "Governance Insight"
    Citizen developers created 8 of 12 agents (67%). While this shows strong adoption, citizen agents are more likely to have DLP violations and failed security scans. Consider implementing mandatory review workflows for citizen-created agents before they reach production.

---

## Step 6: Governance Dashboard

Combine all findings into a governance summary:

```python
dashboard = f"""
╔════════════════════════════════════════════════════════╗
║     Copilot Studio Governance Report                   ║
╠════════════════════════════════════════════════════════╣
║ Total Agents:                {len(agents):>5}                     ║
║ Citizen-Created:             {len(citizen):>5}                     ║
║ IT-Managed:                  {len(it_managed):>5}                     ║
║ DLP Non-Compliant:           {len(dlp_violations):>5}                     ║
║ Failed Security Scans:       {len(failed_scans):>5}                     ║
║ No Authentication:           {len(unprotected):>5}                     ║
║ Production Agents:           {len(agents[agents['environment'] == 'Production']):>5}                     ║
╚════════════════════════════════════════════════════════╝
"""
print(dashboard)
```

---

## 🐛 Bug-Fix Exercise

The file `lab-066/broken_governance.py` has **3 bugs** in how it analyzes governance data:

```bash
python lab-066/broken_governance.py
```

| Test | What it checks | Hint |
|------|---------------|------|
| Test 1 | DLP violation count | Should filter `dlp_compliant == False`, not `True` |
| Test 2 | Citizen agent count | Should filter `creator_type == "citizen"`, not `"it_managed"` |
| Test 3 | Failed scan percentage | Should filter `security_scan == "failed"`, not `"passed"` |

---

## 📁 Supporting Files

- 📥 [broken_governance.py](https://github.com/lcarli/AI-LearningHub/raw/main/docs/docs/en/labs/lab-066/broken_governance.py)
- 📥 [studio_agents.csv](https://github.com/lcarli/AI-LearningHub/raw/main/docs/docs/en/labs/lab-066/studio_agents.csv)

```
lab-066/
├── studio_agents.csv       ← 12 Copilot Studio agents across environments
└── broken_governance.py    ← Bug-fix exercise (3 bugs + self-tests)
```

```bash
pip install pandas
cd docs/docs/en/labs
python lab-066/broken_governance.py    # Bug-fix exercise
```

---

## 🧠 Knowledge Check

??? question "**Q1 (Multiple Choice):** What is the primary risk of ungoverned Copilot Studio agents?"

    - A) They consume too much compute
    - B) They can access sensitive data without DLP controls, authentication, or audit trails
    - C) They slow down the Power Platform
    - D) They prevent IT from creating new agents

    ??? success "✅ Reveal Answer"
        **Correct: B) They can access sensitive data without DLP controls, authentication, or audit trails**

        Ungoverned agents bypass organizational security policies. They may connect to sensitive data sources using unapproved connectors, operate without authentication, and lack audit logging — creating compliance gaps and data exfiltration risks.

??? question "**Q2 (Multiple Choice):** Why is environment isolation important for Copilot Studio governance?"

    - A) It makes agents run faster
    - B) It separates development, testing, and production agents to enforce different security policies per lifecycle stage
    - C) It reduces licensing costs
    - D) It is only needed for custom code agents

    ??? success "✅ Reveal Answer"
        **Correct: B) It separates development, testing, and production agents to enforce different security policies per lifecycle stage**

        Environment isolation ensures that experimental agents in sandbox environments cannot access production data, and that production agents meet stricter DLP, authentication, and review requirements. Without isolation, a citizen developer's prototype could accidentally connect to production databases.

??? question "**Q3 (Run the Lab):** How many agents failed security scans?"

    Filter the agents DataFrame for `security_scan == "failed"` and count the rows.

    ??? success "✅ Reveal Answer"
        **3 agents failed security scans**

        These agents had misconfigurations such as missing authentication, exposed internal knowledge bases, or unapproved connector usage. Failed scans require immediate remediation before the agents can be promoted to production.

??? question "**Q4 (Run the Lab):** How many agents have no authentication configured?"

    Filter for `authentication == "none"` and count.

    ??? success "✅ Reveal Answer"
        **3 agents have no authentication**

        Agents without authentication are publicly accessible, meaning anyone with the endpoint URL can interact with them. This is a critical security gap that must be resolved by configuring Azure AD or other identity providers.

??? question "**Q5 (Run the Lab):** How many agents were created by citizen developers?"

    Filter for `creator_type == "citizen"` and count.

    ??? success "✅ Reveal Answer"
        **8 agents were created by citizen developers**

        Citizen developers created 8 of the 12 total agents (67%). While citizen development accelerates innovation, these agents require additional governance review to ensure DLP compliance, proper authentication, and security scan passage before production deployment.

---

## Summary

| Topic | What You Learned |
|-------|-----------------|
| Agent Inventory | Catalog and audit all Copilot Studio agents across the tenant |
| DLP Enforcement | Detect agents using unapproved connectors and data sources |
| Security Scanning | Identify agents with failed security scans and misconfigurations |
| Environment Isolation | Separate dev/test/prod to enforce lifecycle-appropriate policies |
| Creator Governance | Track citizen vs IT-managed agent creation and compliance rates |
| Governance Dashboards | Build summary reports for executive and compliance stakeholders |

---

## Next Steps

- **[Lab 065](lab-065-purview-dspm-ai.md)** — Purview DSPM for AI (complementary data governance)
- **[Lab 064](lab-064-securing-mcp-apim.md)** — Securing MCP with APIM (infrastructure-level security)
- **[Lab 008](lab-008-responsible-ai.md)** — Responsible AI (foundational governance principles)
