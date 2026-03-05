---
tags: [enterprise, microsoft-365, agent-governance, pro-code, mcp, observability]
---
# Lab 046: Microsoft Agent 365 — Enterprise Agent Governance

<div class="lab-meta">
  <span><strong>Level:</strong> <span class="level-badge level-300">L300</span></span>
  <span><strong>Path:</strong> <a href="../paths/pro-code/">⚙️ Pro Code</a></span>
  <span><strong>Time:</strong> ~75 min</span>
  <span><strong>💰 Cost:</strong> <span class="level-badge cost-azure">Paid — Microsoft 365 Copilot license + Azure subscription + Frontier program</span></span>
</div>

!!! info "Tradução em andamento"
    Este lab ainda está sendo traduzido. O conteúdo abaixo está em inglês.



## What You'll Learn

- What Microsoft Agent 365 is and how it differs from agent *frameworks*
- How Agent 365 gives every AI agent its own **Entra Agent Identity**
- How to install and configure the **Agent 365 CLI**
- How to create an **Agent Blueprint** (the enterprise governance template)
- How to add **observability (OpenTelemetry)** to an existing Python agent using the Agent 365 SDK
- How to **publish an agent** to the Microsoft 365 Admin Center
- How to create an **agent instance** that appears in the org chart in Teams

---

## Introduction

Most AI agent frameworks focus on *building* agents — how they reason, call tools, and remember context. **Microsoft Agent 365** solves a different problem: **how do enterprises govern, secure, and manage agents at scale?**

Think of Agent 365 as the *control plane* for AI agents in your Microsoft 365 tenant:

![Agent 365 Control Plane](../../assets/diagrams/agent-365-control-plane.svg)

An agent enhanced with Agent 365 gets:

| Capability | What it means |
|-----------|--------------|
| **Entra Agent ID** | Its own identity in Azure AD — like a user account, but for an agent |
| **Blueprint** | IT-approved template defining capabilities, MCP permissions, and governance policies |
| **Notifications** | Can receive and respond to @mentions in Teams, emails, Word comments |
| **Governed MCP Tools** | Access to Mail, Calendar, Teams, SharePoint under admin control |
| **Observability** | Full OpenTelemetry traces of every tool call and LLM inference |

!!! warning "Preview program required"
    Microsoft Agent 365 is in **Frontier preview**. You need to join the [Microsoft Copilot Frontier Program](https://adoption.microsoft.com/copilot/frontier-program/) and have at least one **Microsoft 365 Copilot** license in your tenant.

---

## Architecture: Agent 365 Layers

![Agent 365 Layered Architecture](../../assets/diagrams/agent-365-layers.svg)

Agent 365 SDK sits *above* your agent framework. It does **not** replace it — it wraps and enhances it.

---

## Prerequisites

- [ ] **Microsoft 365 Copilot license** (at least 1 in your tenant)
- [ ] **Frontier program access** — [enroll here](https://adoption.microsoft.com/copilot/frontier-program/)
- [ ] **Azure subscription** — resource creation rights
- [ ] **Entra ID permissions** — Global Admin, Agent ID Administrator, or Agent ID Developer role
- [ ] **.NET 8.0 or later** — for the Agent 365 CLI
- [ ] **Python 3.11+** and pip
- [ ] **GitHub Models token** (free) — for the OutdoorGear agent we'll enhance

!!! tip "No Frontier access? Follow along anyway"
    If you don't have Frontier access yet, you can still follow Steps 1–4 locally with mock tooling. The starter file includes a mock mode. Steps 5–7 require a real tenant.

---

!!! tip "Quick Start with GitHub Codespaces"
    [![Open in GitHub Codespaces](https://github.com/codespaces/badge.svg)](https://codespaces.new/lcarli/AI-LearningHub?quickstart=1)

    All dependencies are pre-installed in the devcontainer.


## 📦 Supporting Files

!!! note "Download these files before starting the lab"
    Save all files to a `lab-046/` folder in your working directory.

| File | Description | Download |
|------|-------------|----------|
| `a365.config.sample.json` | Configuration / data file | [📥 Download](https://github.com/lcarli/AI-LearningHub/raw/main/docs/docs/en/labs/lab-046/a365.config.sample.json) |
| `broken_observability.py` | Bug-fix exercise (3 bugs + self-tests) | [📥 Download](https://github.com/lcarli/AI-LearningHub/raw/main/docs/docs/en/labs/lab-046/broken_observability.py) |
| `outdoorgear_a365_starter.py` | Starter script with TODOs | [📥 Download](https://github.com/lcarli/AI-LearningHub/raw/main/docs/docs/en/labs/lab-046/outdoorgear_a365_starter.py) |

---

## Step 1: Install the Agent 365 CLI

The Agent 365 CLI (`a365`) is the command-line backbone for the entire agent development lifecycle.

```bash
# Install (requires .NET 8.0+)
dotnet tool install --global Microsoft.Agents.A365.DevTools.Cli --prerelease

# Verify installation
a365 -h
```

Expected output:
```
Microsoft Agent 365 CLI
Version: x.x.x-preview

Usage: a365 [command] [options]

Commands:
  config      Manage Agent 365 configuration
  setup       Set up agent blueprint and Azure resources
  deploy      Deploy agent code to Azure
  publish     Publish agent to Microsoft 365 admin center
  ...
```

!!! note "Always use --prerelease"
    Until Agent 365 is GA, always include `--prerelease` in install/update commands. Without it, the package won't be found in NuGet feeds.

---

## Step 2: Register a Custom Client App in Entra ID

The CLI needs its own Entra app registration to authenticate against your tenant.

**In Azure Portal → Entra ID → App registrations:**

1. Click **New registration**
2. Name: `Agent365-CLI-App`
3. Supported account types: **Accounts in this organizational directory only**
4. Click **Register**
5. Copy the **Application (client) ID** — you'll need it in Step 3
6. Go to **API Permissions → Add a permission → Microsoft Graph**
7. Add these **Application permissions**:
   - `AgentLifecycle.ReadWrite.All`
   - `Application.ReadWrite.All`
8. Click **Grant admin consent**

```bash
# Verify you can authenticate
az login --tenant YOUR_TENANT_ID
```

---

## Step 3: Initialize Agent 365 Configuration

```bash
# Create a new Agent 365 config
a365 config init
```

The CLI will prompt for:
- Tenant ID
- Azure subscription ID
- Resource group name
- The client app ID from Step 2
- Your agent's messaging endpoint URL

This creates an `a365.config.json` file in your project directory:

```json
{
  "tenantId": "YOUR_TENANT_ID",
  "subscriptionId": "YOUR_SUBSCRIPTION_ID",
  "resourceGroup": "rg-outdoorgear-agent",
  "clientAppId": "YOUR_CLIENT_APP_ID",
  "agentMessagingEndpoint": "https://your-agent.azurewebsites.net/api/messages",
  "agentBlueprintName": "OutdoorGearAgent",
  "mcpPermissions": [
    "mail.read",
    "calendar.readwrite",
    "teams.message.send"
  ]
}
```

!!! tip "Use the sample config"
    The lab includes `lab-046/a365.config.sample.json` as a reference. Copy it, fill in your values, rename to `a365.config.json`.

---

## Step 4: Add Agent 365 SDK to Your Python Agent

Install the Agent 365 SDK packages:

```bash
pip install openai \
  microsoft-agents-a365-observability-core \
  microsoft-agents-a365-observability-extensions-openai \
  microsoft-agents-a365-notifications \
  microsoft-agents-a365-tooling \
  microsoft-agents-a365-tooling-extensions-openai
```

### 4a. Add Observability (OpenTelemetry)

The SDK instruments your agent automatically for the OpenAI Agents SDK:

```python
from openai import AsyncOpenAI
from agents import Agent, Runner
from microsoft.agents.a365.observability.core import A365ObservabilityProvider
from microsoft.agents.a365.observability.extensions.openai import OpenAIAgentInstrumentation

# Initialize observability
observability = A365ObservabilityProvider(
    service_name="OutdoorGearAgent",
    service_version="1.0.0",
    exporter_endpoint="https://your-otel-collector.endpoint"
)

# Auto-instrument the OpenAI Agents SDK
instrumentation = OpenAIAgentInstrumentation(provider=observability)
instrumentation.instrument()

# Every agent run is now traced automatically!
```

### 4b. Add Governed MCP Tooling

Connect to Microsoft 365 MCP servers (Mail, Calendar, Teams) under admin control:

```python
from microsoft.agents.a365.tooling import A365ToolingClient
from microsoft.agents.a365.tooling.extensions.openai import OpenAIMcpRegistrationService

async def setup_m365_tools(agent: Agent) -> Agent:
    """Register governed M365 MCP tools to an existing agent."""
    
    tooling_client = A365ToolingClient(
        agent_id="YOUR_ENTRA_AGENT_ID",
        tenant_id="YOUR_TENANT_ID"
    )
    
    # Get available governed MCP servers for this agent
    mcp_servers = await tooling_client.get_mcp_servers()
    
    # Register with OpenAI Agents SDK
    registration_service = OpenAIMcpRegistrationService(agent)
    for server in mcp_servers:
        await registration_service.register(server)
    
    return agent
```

### 4c. Add Notifications (Teams / Outlook)

Make your agent respond to @mentions and emails:

```python
from microsoft.agents.a365.notifications import A365NotificationHandler

class OutdoorGearNotificationHandler(A365NotificationHandler):
    
    async def on_teams_mention(self, context):
        """Called when @OutdoorGearAgent is mentioned in Teams."""
        user_message = context.activity.text
        # Pass to your agent's run loop
        response = await Runner.run(
            self.agent,
            input=user_message,
            context=context
        )
        await context.send_activity(response.final_output)
    
    async def on_email_received(self, context):
        """Called when agent mailbox receives an email."""
        subject = context.activity.subject
        body = context.activity.body
        # Handle email queries
        response = await Runner.run(
            self.agent,
            input=f"Email subject: {subject}\n\n{body}"
        )
        await context.reply_to_email(response.final_output)
```

---

## Step 5: Create the Agent Blueprint

The blueprint is the IT-approved enterprise template for your agent. Create it with one CLI command:

```bash
a365 setup
```

This command:
1. Creates an **Azure Entra Agent ID** (service principal for your agent)
2. Registers the agent's **MCP tool permissions** as defined in `a365.config.json`
3. Creates the **Agent Blueprint** in Azure
4. Outputs a `blueprintId` you'll need for publishing

```
✅ Agent identity created: OutdoorGearAgent (ID: agt-12345-...)
✅ MCP permissions registered: mail.read, calendar.readwrite, teams.message.send
✅ Blueprint created: OutdoorGearAgent-Blueprint-v1
   Blueprint ID: bpnt-67890-...
```

---

## Step 6: Deploy Agent Code to Azure

If you don't have an existing Azure deployment:

```bash
# Deploy to Azure App Service
a365 deploy --target azure-app-service --resource-group rg-outdoorgear-agent

# Or deploy to Azure Container Apps
a365 deploy --target azure-container-apps --resource-group rg-outdoorgear-agent
```

Your agent must be reachable at the messaging endpoint URL you set in `a365.config.json`.

---

## Step 7: Publish to Microsoft 365 Admin Center

```bash
a365 publish --blueprint-id bpnt-67890-...
```

After publishing:

1. Go to [Microsoft 365 Admin Center](https://admin.microsoft.com) → **Agents**
2. Find **OutdoorGearAgent** in the registry
3. Click **Create instance** to instantiate the agent for your organization
4. The agent gets:
   - Its own entry in your org chart
   - An email address (`outdoorgear-agent@yourorg.com`)
   - Ability to be @mentioned in Teams
   - Visibility in the **Agent Map** (who uses it, what data it accesses)

!!! info "Agent shows in Teams within minutes"
    After creating an instance, your agent appears in Teams search. Users can @mention it in chats and channels. It also appears in Outlook contacts.

---

## 🐛 Bug-Fix Exercise: Fix the Broken Observability Setup

The lab includes a broken observability configuration. Find and fix 3 bugs!

```
lab-046/
└── broken_observability.py    ← 3 intentional bugs to find and fix
```

**Setup:**
```bash
pip install microsoft-agents-a365-observability-core \
            microsoft-agents-a365-observability-extensions-openai

python lab-046/broken_observability.py
```

**The 3 bugs:**

| # | Component | Symptom | Type |
|---|-----------|---------|------|
| 1 | `A365ObservabilityProvider` | `TypeError: missing required argument 'service_name'` | Missing required parameter |
| 2 | `OpenAIAgentInstrumentation` | Traces show `service_name: unknown` instead of `OutdoorGearAgent` | Provider not passed to instrumentation |
| 3 | Exporter endpoint | `ConnectionRefusedError: localhost:4317` | Wrong endpoint — should use HTTPS collector |

**Verify your fixes:** After fixing all 3 bugs, run:
```bash
python lab-046/broken_observability.py
# Expected:
# ✅ ObservabilityProvider initialized: OutdoorGearAgent v1.0.0
# ✅ Instrumentation active — traces will include service_name: OutdoorGearAgent
# ✅ Exporter endpoint validated: https://...
# 🎉 Observability configured correctly!
```

---


## 🧠 Knowledge Check

??? question "**Q1 (Multiple Choice):** An agent built with LangChain wants to use Microsoft Agent 365. What does Agent 365 provide that LangChain does NOT?"

    - A) The ability to call external APIs and tools
    - B) Multi-step reasoning and planning
    - C) Entra-backed identity, governed MCP tools, observability, and enterprise governance/compliance
    - D) A better LLM model for reasoning

    ??? success "✅ Reveal Answer"
        **Correct: C**

        Agent 365 is NOT an agent framework — it doesn't help you build reasoning logic. LangChain already handles tool calling, multi-step reasoning, and planning. What Agent 365 adds is the **enterprise layer**: a unique Entra identity for the agent, IT-approved governed MCP access to M365 workloads, OpenTelemetry observability, blueprint-based governance, and the ability for IT admins to see, monitor, and control the agent from the M365 Admin Center.

??? question "**Q2 (Multiple Choice):** What is an Agent Blueprint in Microsoft Agent 365?"

    - A) A Bicep/ARM template for deploying Azure resources
    - B) An IT-approved, pre-configured template defining an agent's capabilities, MCP permissions, governance policies, and compliance constraints
    - C) A Python class that all Agent 365 agents must inherit from
    - D) A diagram of the agent's tool call flow

    ??? success "✅ Reveal Answer"
        **Correct: B**

        A blueprint comes from Microsoft Entra and is the *enterprise template* from which compliant agent instances are created. It defines what the agent can do (capabilities), what M365 data it can access (MCP permissions), how it's governed (DLP policies, external access restrictions, logging rules), and lifecycle metadata. Every agent instance created from the blueprint inherits all these rules — ensuring no "shadow agents" with uncontrolled access.

??? question "**Q3 (Run the Lab):** Open `lab-046/outdoorgear_a365_starter.py`. How many TODO comments are in the file?"

    Open the starter file and count the `# TODO` markers.

    ??? success "✅ Reveal Answer"
        **5 TODOs**

        The starter file has 5 integration points for you to complete:
        1. TODO 1: Initialize `A365ObservabilityProvider` with service name and version
        2. TODO 2: Apply `OpenAIAgentInstrumentation` to auto-instrument traces
        3. TODO 3: Implement `on_teams_mention` handler
        4. TODO 4: Connect to governed MCP tooling servers
        5. TODO 5: Register the agent's Entra Agent ID

??? question "**Q4 (Multiple Choice):** A user @mentions your OutdoorGear Agent in a Teams channel. Which Agent 365 SDK component receives and routes this notification to your agent code?"

    - A) `A365ObservabilityProvider`
    - B) `A365ToolingClient`
    - C) `A365NotificationHandler`
    - D) `OpenAIMcpRegistrationService`

    ??? success "✅ Reveal Answer"
        **Correct: C — `A365NotificationHandler`**

        The `A365NotificationHandler` receives events from Microsoft 365 applications — Teams @mentions, incoming emails to the agent's mailbox, Word comment notifications, and more. You subclass it and override methods like `on_teams_mention()` and `on_email_received()`. The `A365ObservabilityProvider` handles telemetry, `A365ToolingClient` manages MCP tool access, and `OpenAIMcpRegistrationService` registers MCP servers with the OpenAI Agents SDK.

---

## Summary

| Concept | Key takeaway |
|---------|-------------|
| **Agent 365 ≠ agent framework** | It adds *enterprise capabilities* on top of your existing agent — doesn't replace SK, LangChain, etc. |
| **Entra Agent ID** | Every agent gets its own identity — like a user account but for an agent |
| **Blueprint** | IT-approved template; all instances inherit its governance rules |
| **Observability** | OpenTelemetry auto-instrumentation — every tool call and LLM inference is traced |
| **Governed MCP** | M365 tools (Mail, Calendar, Teams, SharePoint) accessible under IT control |
| **Notifications** | Agents can be @mentioned in Teams, receive emails, respond to Word comments |
| **Frontier required** | Still in preview — needs M365 Copilot license + Frontier program enrollment |

---

## Next Steps

- **Build the underlying agent first:** → [Lab 016 — OpenAI Agents SDK](lab-016-openai-agents-sdk.md)
- **Add MCP tools to your agent:** → [Lab 020 — MCP Server in Python](lab-020-mcp-server-python.md)
- **Observability deep dive:** → [Lab 033 — Agent Observability with App Insights](lab-033-agent-observability.md)
- **Enterprise RAG pipeline:** → [Lab 042 — Enterprise RAG with Evaluations](lab-042-enterprise-rag.md)
