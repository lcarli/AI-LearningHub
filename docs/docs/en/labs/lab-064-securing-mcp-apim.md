---
tags: [security, apim, mcp, oauth, enterprise, governance]
---
# Lab 064: Securing MCP at Scale with Azure API Management

<div class="lab-meta">
  <span><strong>Level:</strong> <span class="level-badge level-400">L400</span></span>
  <span><strong>Path:</strong> <a href="../paths/pro-code/">⚙️ Pro Code</a></span>
  <span><strong>Time:</strong> ~90 min</span>
  <span><strong>💰 Cost:</strong> <span class="level-badge cost-free">Free</span> — Mock server data (no Azure subscription required)</span>
</div>

## What You'll Learn

- Use **Azure API Management (APIM)** as a centralized gateway for MCP servers
- Enforce **OAuth 2.0** authentication across all MCP endpoints
- Apply **rate limiting**, **DLP policies**, and **logging** to MCP traffic
- Audit MCP server compliance across teams and identify security gaps
- Analyze **error rates**, **latency**, and **call volumes** across an MCP fleet

!!! abstract "Prerequisite"
    Complete **[Lab 012: What Is MCP?](lab-012-what-is-mcp.md)** and **[Lab 020: MCP Server (Python)](lab-020-mcp-server-python.md)** first. This lab assumes familiarity with MCP architecture and tool-serving patterns.

## Introduction

As organizations scale their AI agent deployments, the number of **MCP servers** grows rapidly — each team builds its own, with different authentication schemes, rate limits, and data-loss-prevention (DLP) controls. Without centralized governance, you end up with a patchwork of inconsistent security policies.

**Azure API Management** solves this by sitting in front of all MCP servers as a unified gateway:

| Concern | Without APIM | With APIM |
|---------|-------------|-----------|
| **Authentication** | Each server rolls its own (API key, basic, OAuth…) | Centralized OAuth 2.0 with Azure AD |
| **Rate Limiting** | No limits or inconsistent per-server limits | Uniform policy across all endpoints |
| **DLP** | No scanning of tool inputs/outputs | Content inspection and PII redaction |
| **Monitoring** | Scattered logs, no unified view | Centralized metrics, alerts, and dashboards |

### The Scenario

You are a **Platform Security Engineer** at a company running **10 MCP servers** across **6 teams**. Management wants a compliance report: which servers meet the security baseline (OAuth + DLP + logging), which don't, and what the risk exposure looks like.

You have a fleet inventory dataset with authentication types, rate limits, DLP status, logging status, call volumes, latency, and error rates.

---

## Prerequisites

| Requirement | Why |
|---|---|
| Python 3.10+ | Run analysis scripts |
| `pandas` | Analyze server fleet data |

```bash
pip install pandas
```

---

## 📦 Supporting Files

!!! note "Download these files before starting the lab"
    Save all files to a `lab-064/` folder in your working directory.

| File | Description | Download |
|------|-------------|----------|
| `broken_apim.py` | Bug-fix exercise (3 bugs + self-tests) | [📥 Download](https://github.com/lcarli/AI-LearningHub/raw/main/docs/docs/en/labs/lab-064/broken_apim.py) |
| `mcp_servers.csv` | Dataset | [📥 Download](https://github.com/lcarli/AI-LearningHub/raw/main/docs/docs/en/labs/lab-064/mcp_servers.csv) |

---

## Step 1: Understanding the APIM Security Model

When APIM sits in front of MCP servers, every tool call flows through a policy pipeline:

```
Agent → APIM Gateway → [Auth Policy] → [Rate Limit] → [DLP Scan] → MCP Server
                                                                        ↓
Agent ← APIM Gateway ← [Response DLP] ← [Logging] ←────────────── Response
```

Key policies for MCP:

| Policy | Purpose | Example |
|--------|---------|---------|
| **validate-jwt** | Verify OAuth 2.0 tokens | Reject calls without valid Azure AD token |
| **rate-limit-by-key** | Throttle per client/team | 100 RPM per agent |
| **set-body** | DLP content inspection | Redact SSN, credit card numbers from tool outputs |
| **log-to-eventhub** | Centralized audit logging | Every tool call → Event Hub → Log Analytics |

!!! tip "Why OAuth Over API Keys?"
    API keys have no user identity, no token expiry, and no scope control. If a key leaks, anyone can call the MCP server until you manually rotate it. OAuth 2.0 tokens expire automatically, carry user/app identity, and can be scoped to specific tools.

---

## Step 2: Load and Explore the MCP Server Fleet

The dataset contains **10 MCP servers** across **6 teams**:

```python
import pandas as pd

servers = pd.read_csv("lab-064/mcp_servers.csv")
print(f"Total MCP servers: {len(servers)}")
print(f"Teams: {sorted(servers['team'].unique())}")
print(f"\nServers per team:")
print(servers.groupby("team")["server_name"].count().sort_values(ascending=False))
```

**Expected:**

```
Total MCP servers: 10
Teams: ['Analytics', 'Commerce', 'Finance', 'HR', 'Logistics', 'Marketing', 'Operations', 'Support']

Commerce      2
Operations    2
Analytics     1
Finance       1
HR            1
Logistics     1
Marketing     1
Support       1
```

---

## Step 3: Compliance Audit

A server is **compliant** if it has all three: OAuth 2.0 authentication, DLP enabled, and logging enabled. Check the fleet:

```python
compliant = servers[servers["compliant"] == True]
non_compliant = servers[servers["compliant"] == False]

print(f"Compliant servers:     {len(compliant)}")
print(f"Non-compliant servers: {len(non_compliant)}")
print(f"\nNon-compliant details:")
print(non_compliant[["server_name", "team", "auth_type", "has_dlp", "has_logging"]].to_string(index=False))
```

**Expected:**

```
Compliant servers:     6
Non-compliant servers: 4

Non-compliant details:
     server_name       team auth_type has_dlp has_logging
 customer-support   Support   api_key   false       true
 analytics-export Analytics   api_key   false      false
       legacy-erp Operations    basic   false      false
   maps-geocoding  Logistics   api_key   false       true
```

!!! warning "Risk Alert"
    4 of 10 servers are non-compliant — that's **40% of the fleet**. The `legacy-erp` server is the worst offender: basic auth, no DLP, no logging, and the highest error rate.

---

## Step 4: Authentication Gap Analysis

Identify servers that are **not** using OAuth 2.0:

```python
non_oauth = servers[servers["auth_type"] != "oauth2"]
print(f"Servers without OAuth 2.0: {len(non_oauth)}")
print(non_oauth[["server_name", "auth_type", "monthly_calls"]].to_string(index=False))

total_non_oauth_calls = non_oauth["monthly_calls"].sum()
total_calls = servers["monthly_calls"].sum()
pct = total_non_oauth_calls / total_calls * 100
print(f"\nNon-OAuth call volume: {total_non_oauth_calls:,} / {total_calls:,} ({pct:.1f}%)")
```

**Expected:**

```
Servers without OAuth 2.0: 4

     server_name auth_type  monthly_calls
 customer-support   api_key         28000
 analytics-export   api_key         12000
       legacy-erp     basic          8000
   maps-geocoding   api_key         22000

Non-OAuth call volume: 70,000 / 194,500 (36.0%)
```

!!! danger "36% of All MCP Calls Use Weak Authentication"
    Over a third of monthly API calls go through servers with API keys or basic auth. A single leaked key could expose customer support data, analytics exports, ERP records, or geocoding services.

---

## Step 5: DLP Coverage Analysis

Check which servers lack data-loss-prevention scanning:

```python
no_dlp = servers[servers["has_dlp"].astype(str).str.lower() == "false"]
print(f"Servers without DLP: {len(no_dlp)}")
print(no_dlp[["server_name", "team", "monthly_calls"]].to_string(index=False))
```

**Expected:**

```
Servers without DLP: 4

     server_name       team  monthly_calls
 customer-support   Support         28000
 analytics-export Analytics         12000
       legacy-erp Operations          8000
   maps-geocoding  Logistics         22000
```

The 4 servers without DLP handle **70,000 monthly calls** — any of these could leak PII or sensitive data through tool outputs without detection.

---

## Step 6: Error Rate and Latency Analysis

Identify servers with the highest error rates and latency:

```python
print("Error rates (sorted):")
error_sorted = servers.sort_values("error_rate_pct", ascending=False)
print(error_sorted[["server_name", "error_rate_pct", "avg_latency_ms"]].to_string(index=False))

highest_error = error_sorted.iloc[0]
print(f"\nHighest error rate: {highest_error['server_name']} at {highest_error['error_rate_pct']}%")
print(f"Its average latency: {highest_error['avg_latency_ms']}ms")
```

**Expected:**

```
Highest error rate: legacy-erp at 5.8%
Its average latency: 450ms
```

!!! tip "Insight"
    The `legacy-erp` server stands out as the highest-risk server: basic auth, no DLP, no logging, highest error rate (5.8%), and highest latency (450ms). This should be the top priority for APIM onboarding.

---

## Step 7: Total Call Volume

Calculate the total monthly calls across all MCP servers:

```python
total = servers["monthly_calls"].sum()
print(f"Total monthly calls across fleet: {total:,}")
```

**Expected:**

```
Total monthly calls across fleet: 194,500
```

---

## Step 8: APIM Migration Priority

Create a prioritized migration plan based on risk:

```python
servers["risk_score"] = (
    (servers["auth_type"] != "oauth2").astype(int) * 3 +
    (servers["has_dlp"].astype(str).str.lower() == "false").astype(int) * 2 +
    (servers["has_logging"].astype(str).str.lower() == "false").astype(int) * 1 +
    servers["error_rate_pct"] / servers["error_rate_pct"].max()
)

priority = servers.sort_values("risk_score", ascending=False)
print("Migration Priority:")
print(priority[["server_name", "auth_type", "has_dlp", "has_logging", "risk_score"]]
      .head(5).to_string(index=False))
```

This produces a risk-ranked list to guide the APIM onboarding sequence.

---

## 🐛 Bug-Fix Exercise

The file `lab-064/broken_apim.py` has **3 bugs** in how it analyzes the MCP server fleet:

```bash
python lab-064/broken_apim.py
```

| Test | What it checks | Hint |
|------|---------------|------|
| Test 1 | Count non-compliant servers | Should count `compliant == False`, not `True` |
| Test 2 | Total monthly calls | Should be the **sum**, not the **average** |
| Test 3 | Servers without OAuth | Should filter `auth_type != "oauth2"`, not `== "oauth2"` |

---


## 🧠 Knowledge Check

??? question "**Q1 (Multiple Choice):** Why is APIM the recommended approach for securing MCP servers at scale?"

    - A) It replaces MCP with a different protocol
    - B) It provides centralized authentication, throttling, and monitoring across all MCP endpoints
    - C) It eliminates the need for OAuth 2.0
    - D) It only works with Azure-hosted MCP servers

    ??? success "✅ Reveal Answer"
        **Correct: B) It provides centralized authentication, throttling, and monitoring across all MCP endpoints**

        APIM acts as a unified gateway in front of all MCP servers, enforcing consistent OAuth 2.0 validation, rate limiting, DLP content inspection, and audit logging — regardless of how each individual MCP server was originally built. Without APIM, each team implements (or skips) these controls independently.

??? question "**Q2 (Multiple Choice):** Why is API key authentication insufficient for production MCP servers?"

    - A) API keys are too long to store securely
    - B) API keys provide no user identity, no token expiry, and no scope control
    - C) API keys only work with REST APIs, not MCP
    - D) API keys require Azure AD to function

    ??? success "✅ Reveal Answer"
        **Correct: B) API keys provide no user identity, no token expiry, and no scope control**

        API keys are static secrets: if one leaks, anyone can use it indefinitely until manually rotated. They carry no information about *who* is calling or *what* they're allowed to do. OAuth 2.0 tokens expire automatically, embed user/app identity claims, and can be scoped to specific permissions (e.g., read-only access to a specific tool).

??? question "**Q3 (Run the Lab):** How many MCP servers in the fleet are non-compliant?"

    Filter the servers DataFrame for `compliant == False` and count the rows.

    ??? success "✅ Reveal Answer"
        **4 non-compliant servers**

        The non-compliant servers are: `customer-support` (api_key, no DLP), `analytics-export` (api_key, no DLP, no logging), `legacy-erp` (basic auth, no DLP, no logging), and `maps-geocoding` (api_key, no DLP). All 4 lack OAuth and DLP; 2 also lack logging.

??? question "**Q4 (Run the Lab):** What is the total monthly call volume across all 10 MCP servers?"

    Sum the `monthly_calls` column across all servers.

    ??? success "✅ Reveal Answer"
        **194,500 total monthly calls**

        45,000 + 32,000 + 28,000 + 18,000 + 15,000 + 12,000 + 5,000 + 8,000 + 22,000 + 9,500 = **194,500**. Of these, 70,000 (36%) go through servers without OAuth 2.0 — a significant security exposure.

??? question "**Q5 (Run the Lab):** Which MCP server has the highest error rate, and what is it?"

    Sort servers by `error_rate_pct` descending and inspect the top row.

    ??? success "✅ Reveal Answer"
        **legacy-erp at 5.8%**

        The `legacy-erp` server (Operations team) has the highest error rate at 5.8%, nearly 3× the next highest (payment-gateway at 2.1%). Combined with basic auth, no DLP, no logging, and 450ms average latency, it is the highest-risk server in the fleet and should be the top priority for APIM onboarding.

---

## Summary

| Topic | What You Learned |
|-------|-----------------|
| APIM as Gateway | Centralized security, rate limiting, and monitoring for MCP |
| OAuth 2.0 | Token-based auth with identity, expiry, and scope control |
| DLP Policies | Content inspection to prevent PII/sensitive data leakage |
| Compliance Audit | Systematic assessment of fleet security posture |
| Risk Prioritization | Data-driven migration planning based on auth, DLP, and error rates |

---

## Next Steps

- **[Lab 012](lab-012-what-is-mcp.md)** — What Is MCP? (foundational MCP concepts)
- **[Lab 028](lab-028-deploy-mcp-azure.md)** — Deploy MCP to Azure (deploy the servers that APIM protects)
- **[Lab 036](lab-036-prompt-injection-security.md)** — Prompt Injection Security (complementary security layer)
