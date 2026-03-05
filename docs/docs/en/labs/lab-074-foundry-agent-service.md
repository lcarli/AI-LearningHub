---
tags: [foundry, agent-service, multi-agent, production, enterprise, python, persona-developer, persona-architect]
---
# Lab 074: Foundry Agent Service — Production Multi-Agent Deployment

<div class="lab-meta">
  <span><strong>Level:</strong> <span class="level-badge level-300">L300</span></span>
  <span><strong>Path:</strong> <a href="../paths/foundry/">🏭 Microsoft Foundry</a></span>
  <span><strong>Time:</strong> ~120 min</span>
  <span><strong>💰 Cost:</strong> <span class="level-badge cost-free">Free</span> — Uses mock agent data</span>
</div>

## What You'll Learn

- What the **Foundry Agent Service** is and how it orchestrates production multi-agent systems
- How agent types (specialist, orchestrator) work together in a deployment
- Analyze agent fleet health: request volumes, latency, error rates, and status
- Identify **degraded agents** and **configuration risks** (e.g., disabled content filters)
- Build a **fleet health dashboard** for production monitoring

## Introduction

The **Azure AI Foundry Agent Service** provides a managed platform for deploying, orchestrating, and monitoring multi-agent systems at enterprise scale. Instead of building custom orchestration, you define agents with specific tools, memory, and models — and the service handles routing, state management, and scaling.

### Agent Types

| Type | Role | Example |
|------|------|---------|
| **Orchestrator** | Routes requests to specialists, manages conversation flow | SupportRouter, Coordinator |
| **Specialist** | Handles a specific domain with dedicated tools and memory | ProductAdvisor, OrderProcessor |

### The Scenario

You are a **Platform SRE** managing a multi-agent deployment for an e-commerce company. The fleet has **8 agents** — 2 orchestrators and 6 specialists — running on Azure Container Apps. You've been alerted that one agent is degraded and need to investigate.

Your dataset (`foundry_agents.csv`) contains the current fleet status. Your job: analyze health metrics, identify issues, and produce a fleet status report.

!!! info "Mock Data"
    This lab uses a mock agent fleet CSV that mirrors the metrics you'd see in Azure AI Foundry's monitoring dashboard. The patterns (latency spikes, error rates, degraded status) represent common production scenarios.

## Prerequisites

| Requirement | Why |
|---|---|
| Python 3.10+ | Run the analysis scripts |
| `pandas` library | Data manipulation |

```bash
pip install pandas
```

---

!!! tip "Quick Start with GitHub Codespaces"
    [![Open in GitHub Codespaces](https://github.com/codespaces/badge.svg)](https://codespaces.new/lcarli/AI-LearningHub?quickstart=1)

    All dependencies are pre-installed in the devcontainer.


## 📦 Supporting Files

!!! note "Download these files before starting the lab"
    Save all files to a `lab-074/` folder in your working directory.

| File | Description | Download |
|------|-------------|----------|
| `broken_foundry.py` | Bug-fix exercise (3 bugs + self-tests) | [📥 Download](https://github.com/lcarli/AI-LearningHub/raw/main/docs/docs/en/labs/lab-074/broken_foundry.py) |
| `foundry_agents.csv` | Dataset | [📥 Download](https://github.com/lcarli/AI-LearningHub/raw/main/docs/docs/en/labs/lab-074/foundry_agents.csv) |

---

## Step 1: Understand the Fleet Architecture

Before analyzing data, understand how the agents fit together:

```
                    ┌─────────────────┐
                    │   Coordinator   │ (orchestrator)
                    │    FA05         │
                    └────────┬────────┘
                             │ routes to
              ┌──────────────┼──────────────┐
              ▼              ▼              ▼
     ┌──────────────┐ ┌──────────────┐ ┌──────────────┐
     │SupportRouter │ │ProductAdvisor│ │OrderProcessor│
     │    FA03      │ │    FA01      │ │    FA02      │
     └──────────────┘ └──────────────┘ └──────────────┘
              │
     ┌────────┼────────┬──────────────┐
     ▼        ▼        ▼              ▼
  ┌────────┐┌────────┐┌────────┐┌──────────┐
  │Inventory││Quality ││Analytics││LegacyBridge│
  │  FA04  ││  FA06  ││  FA07  ││   FA08    │
  └────────┘└────────┘└────────┘└──────────┘
```

### Key Configuration Fields

| Field | Description |
|-------|-----------|
| **memory_type** | How the agent persists state: `cosmos_db` (durable), `ai_search` (vector), `session_only` (ephemeral), `none` |
| **deployment** | Infrastructure: `container_apps` (managed) or `vm` (self-hosted) |
| **content_filter** | Whether Azure AI content safety is `enabled` or `disabled` |
| **status** | Agent health: `active` or `degraded` |

---

## Step 2: Load and Explore the Fleet Data

```python
import pandas as pd

df = pd.read_csv("lab-074/foundry_agents.csv")

print(f"Total agents: {len(df)}")
print(f"Agent types: {df['agent_type'].value_counts().to_dict()}")
print(f"Statuses: {df['status'].value_counts().to_dict()}")
print(f"\nFull fleet:")
print(df[["agent_id", "agent_name", "agent_type", "model", "status"]].to_string(index=False))
```

**Expected output:**

```
Total agents: 8
Agent types: {'specialist': 6, 'orchestrator': 2}
Statuses: {'active': 7, 'degraded': 1}
```

---

## Step 3: Analyze Request Volume and Load Distribution

How is traffic distributed across the fleet?

```python
total_requests = df["requests_24h"].sum()
print(f"Total 24h requests across fleet: {total_requests:,}")

print("\nRequest distribution:")
for _, row in df.sort_values("requests_24h", ascending=False).iterrows():
    pct = row["requests_24h"] / total_requests * 100
    bar = "█" * int(pct / 2)
    print(f"  {row['agent_name']:>20s}: {row['requests_24h']:>5,}  ({pct:>5.1f}%) {bar}")
```

**Expected output:**

```
Total 24h requests across fleet: 9,380
```

| Agent | Requests | Share |
|-------|----------|-------|
| Coordinator | 3,200 | 34.1% |
| SupportRouter | 2,100 | 22.4% |
| ProductAdvisor | 1,250 | 13.3% |
| OrderProcessor | 890 | 9.5% |
| QualityReviewer | 780 | 8.3% |
| InventoryMonitor | 560 | 6.0% |
| AnalyticsAgent | 420 | 4.5% |
| LegacyBridge | 180 | 1.9% |

!!! tip "Insight"
    The **Coordinator orchestrator handles 34% of all traffic** — it's the entry point for most requests. If it goes down, the entire system is affected. The SupportRouter is the second-busiest, routing customer support queries to specialists.

---

## Step 4: Identify Degraded and At-Risk Agents

### 4a — Degraded Agents

```python
degraded = df[df["status"] == "degraded"]
print(f"Degraded agents: {len(degraded)}")
for _, agent in degraded.iterrows():
    print(f"\n  Agent: {agent['agent_name']} ({agent['agent_id']})")
    print(f"  Error rate: {agent['error_rate_pct']}%")
    print(f"  Avg latency: {agent['avg_latency_ms']}ms")
    print(f"  Requests: {agent['requests_24h']}")
```

**Expected output:**

```
Degraded agents: 1

  Agent: AnalyticsAgent (FA07)
  Error rate: 8.5%
  Avg latency: 850ms
  Requests: 420
```

### 4b — High Error Rate Agents

```python
high_error = df[df["error_rate_pct"] > 5.0]
print(f"\nAgents with error rate > 5%: {len(high_error)}")
for _, agent in high_error.iterrows():
    print(f"  {agent['agent_name']}: {agent['error_rate_pct']}% errors")
```

### 4c — Content Filter Status

```python
disabled_filter = df[df["content_filter"] == "disabled"]
print(f"\nAgents with disabled content filter: {len(disabled_filter)}")
for _, agent in disabled_filter.iterrows():
    print(f"  {agent['agent_name']} ({agent['agent_id']}) — deployment: {agent['deployment']}")
```

!!! warning "Security Risk"
    **LegacyBridge (FA08)** has its content filter **disabled** and runs on a self-hosted VM. This is a compliance risk — all production agents should have content safety enabled, especially those handling customer data.

---

## Step 5: Analyze Memory and Infrastructure Patterns

```python
print("Memory type distribution:")
print(df.groupby("memory_type")["agent_name"].apply(list).to_string())

print("\nDeployment distribution:")
print(df.groupby("deployment")["agent_name"].apply(list).to_string())

# Agents without durable memory
no_durable = df[df["memory_type"].isin(["session_only", "none"])]
print(f"\nAgents without durable memory: {len(no_durable)}")
for _, agent in no_durable.iterrows():
    print(f"  {agent['agent_name']}: memory={agent['memory_type']}")
```

```python
# Latency by model
print("\nAvg latency by model:")
for model, group in df.groupby("model"):
    print(f"  {model}: {group['avg_latency_ms'].mean():.0f}ms")
```

---

## Step 6: Build the Fleet Health Report

```python
avg_latency = df["avg_latency_ms"].mean()
avg_error = df["error_rate_pct"].mean()

report = f"""# 📊 Foundry Agent Service — Fleet Health Report

## Fleet Overview
| Metric | Value |
|--------|-------|
| Total Agents | {len(df)} |
| Orchestrators | {(df['agent_type'] == 'orchestrator').sum()} |
| Specialists | {(df['agent_type'] == 'specialist').sum()} |
| Active | {(df['status'] == 'active').sum()} |
| Degraded | {(df['status'] == 'degraded').sum()} |
| Total 24h Requests | {total_requests:,} |
| Avg Latency | {avg_latency:.0f}ms |
| Avg Error Rate | {avg_error:.1f}% |

## Alerts
| Priority | Issue | Agent | Action |
|----------|-------|-------|--------|
| 🔴 High | Degraded status, 8.5% error rate | AnalyticsAgent (FA07) | Investigate AI Search connection |
| 🟡 Medium | Content filter disabled | LegacyBridge (FA08) | Enable content safety |
| 🟡 Medium | 12% error rate, VM deployment | LegacyBridge (FA08) | Migrate to Container Apps |
| 🟢 Low | Session-only memory | SupportRouter (FA03) | Consider durable memory for analytics |

## Recommendations
1. **Fix AnalyticsAgent** — likely an AI Search index connectivity issue causing 8.5% errors
2. **Enable content filter on LegacyBridge** — compliance requirement for production
3. **Migrate LegacyBridge to Container Apps** — self-hosted VMs lack auto-scaling and monitoring
4. **Add monitoring dashboards** — track per-agent latency and error rate trends
"""

print(report)

with open("lab-074/fleet_report.md", "w") as f:
    f.write(report)
print("💾 Saved to lab-074/fleet_report.md")
```

---

## 🐛 Bug-Fix Exercise

The file `lab-074/broken_foundry.py` contains **3 bugs** that produce incorrect fleet metrics. Can you find and fix them all?

Run the self-tests to see which ones fail:

```bash
python lab-074/broken_foundry.py
```

You should see **3 failed tests**. Each test corresponds to one bug:

| Test | What it checks | Hint |
|------|---------------|------|
| Test 1 | Total 24h requests | Should sum requests, not average them |
| Test 2 | Degraded agent count | Should count `degraded` status, not `active` |
| Test 3 | Agents without durable memory | Should count `none`/`session_only`, not `cosmos_db` |

Fix all 3 bugs, then re-run. When you see `All passed!`, you're done!

---


## 🧠 Knowledge Check

??? question "**Q1 (Multiple Choice):** What is the role of an orchestrator agent in a Foundry multi-agent deployment?"

    - A) It performs a specific domain task like order processing
    - B) It routes requests to specialist agents and manages conversation flow
    - C) It stores agent memory in Cosmos DB
    - D) It monitors agent health and restarts failed agents

    ??? success "✅ Reveal Answer"
        **Correct: B) It routes requests to specialist agents and manages conversation flow**

        Orchestrator agents act as the "traffic controller" in a multi-agent system. They receive incoming requests, determine which specialist(s) should handle them, route the conversation accordingly, and manage the overall flow. Specialists handle the domain-specific work.

??? question "**Q2 (Multiple Choice):** Why is a disabled content filter a security risk for production agents?"

    - A) It makes the agent slower
    - B) It allows the agent to generate harmful, biased, or policy-violating content
    - C) It prevents the agent from accessing external APIs
    - D) It increases token costs

    ??? success "✅ Reveal Answer"
        **Correct: B) It allows the agent to generate harmful, biased, or policy-violating content**

        Azure AI Content Safety filters detect and block harmful content (hate speech, violence, self-harm, sexual content). Disabling the filter means the agent can produce or respond to such content without guardrails — a compliance and reputational risk in any production deployment.

??? question "**Q3 (Run the Lab):** What is the total number of requests across the entire fleet in the last 24 hours?"

    Run the Step 3 analysis on [📥 `foundry_agents.csv`](https://github.com/lcarli/AI-LearningHub/raw/main/docs/docs/en/labs/lab-074/foundry_agents.csv) and check the results.

    ??? success "✅ Reveal Answer"
        **9,380 requests**

        Sum of all agent `requests_24h` values: 1,250 + 890 + 2,100 + 560 + 3,200 + 780 + 420 + 180 = **9,380**.

??? question "**Q4 (Run the Lab):** How many agents are in a degraded state?"

    Run the Step 4a analysis to find out.

    ??? success "✅ Reveal Answer"
        **1 agent**

        Only **AnalyticsAgent (FA07)** is in a `degraded` state, with an 8.5% error rate and 850ms average latency — significantly worse than the other agents. This likely indicates a backend connectivity issue with its AI Search memory store.

??? question "**Q5 (Run the Lab):** How many agents have their content filter disabled?"

    Run the Step 4c analysis to check content filter status.

    ??? success "✅ Reveal Answer"
        **1 agent**

        Only **LegacyBridge (FA08)** has `content_filter=disabled`. It's also the only agent deployed on a self-hosted VM rather than Container Apps, and has the highest error rate (12.0%) in the fleet. This agent needs immediate attention.

---

## Summary

| Topic | What You Learned |
|-------|-----------------|
| Foundry Agent Service | Managed platform for multi-agent orchestration and deployment |
| Agent Types | Orchestrators route; specialists execute domain tasks |
| Fleet Monitoring | Track requests, latency, error rates, and status per agent |
| Degraded Detection | Identify agents with elevated error rates or latency |
| Content Safety | All production agents should have content filters enabled |
| Memory Patterns | Cosmos DB for durable, AI Search for vector, session_only for ephemeral |

---

## Next Steps

- **[Lab 034](lab-034-multi-agent-sk.md)** — Multi-Agent with Semantic Kernel (building the agents themselves)
- **[Lab 033](lab-033-agent-observability.md)** — Agent Observability with Application Insights (deeper monitoring)
- **[Lab 030](lab-030-foundry-agent-mcp.md)** — Foundry Agent + MCP (connecting agents to external tools)
- **[Lab 075](lab-075-powerbi-copilot.md)** — Power BI Copilot (visualizing fleet data with AI-assisted dashboards)
