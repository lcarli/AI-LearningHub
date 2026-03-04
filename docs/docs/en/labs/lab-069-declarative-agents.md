---
tags: [declarative-agents, m365-copilot, teams, manifest, low-code]
---
# Lab 069: Declarative Agents for Microsoft 365 Copilot

<div class="lab-meta">
  <span><strong>Level:</strong> <span class="level-badge level-100">L100</span></span>
  <span><strong>Path:</strong> All paths</span>
  <span><strong>Time:</strong> ~60 min</span>
  <span><strong>💰 Cost:</strong> <span class="level-badge cost-free">Free</span> — Mock manifest (no M365 Copilot license required)</span>
</div>

## What You'll Learn

- What **declarative agents** are and how they extend Microsoft 365 Copilot
- Define agent behavior through a **JSON manifest** without writing code
- Configure **knowledge sources** (SharePoint, Graph connectors, files)
- Add **API plugins** to give your agent custom capabilities
- Set up **conversation starters** for guided user interactions
- Validate and troubleshoot manifest configurations

!!! abstract "Prerequisite"
    Familiarity with **Microsoft 365 Copilot** concepts is recommended. No coding experience is required — declarative agents are configured entirely through JSON manifests.

## Introduction

**Declarative agents** let you customize Microsoft 365 Copilot's behavior without writing code. Instead of building a custom agent from scratch, you define a JSON manifest that specifies:

- **Instructions** — System prompt that shapes the agent's persona and behavior
- **Knowledge sources** — Where the agent retrieves information (SharePoint sites, Graph connectors, uploaded files)
- **API plugins** — External APIs the agent can call to take actions
- **Conversation starters** — Pre-defined prompts that guide users toward the agent's capabilities

| Component | Purpose | Example |
|-----------|---------|---------|
| **Instructions** | Define persona, tone, and boundaries | "You are an HR assistant. Only answer HR-related questions." |
| **Knowledge Sources** | Ground responses in organizational data | SharePoint site with company policies |
| **API Plugins** | Enable actions beyond chat | Submit PTO requests via HR API |
| **Conversation Starters** | Guide users to productive interactions | "What is the company leave policy?" |

### The Scenario

You are building a **company HR assistant** as a declarative agent for Microsoft 365 Copilot. The agent should answer questions about company policies, help employees submit time-off requests, and provide onboarding guidance. You will examine a manifest file, understand each component, and validate the configuration.

---

## Prerequisites

| Requirement | Why |
|---|---|
| Python 3.10+ | Run validation scripts |
| `json` (built-in) | Parse manifest files |

No additional packages required — the `json` module is included with Python.

---

## Step 1: Understanding Declarative Agent Architecture

Declarative agents sit between the user and Microsoft 365 Copilot, customizing its behavior:

```
User → [Teams / M365 App] → [Declarative Agent Manifest]
                                      ↓
                             [Instructions] → Persona + Boundaries
                             [Knowledge]    → SharePoint, Graph, Files
                             [Plugins]      → API Actions
                             [Starters]     → Guided Conversations
                                      ↓
                            Microsoft 365 Copilot → Response
```

Key principles:

1. **No code required** — All configuration is in JSON
2. **Scoped knowledge** — The agent only accesses specified sources
3. **Plugin actions** — The agent can call APIs to perform tasks
4. **Guardrails** — Instructions define what the agent should and should not do

!!! info "Declarative vs Custom Agents"
    Declarative agents extend Copilot — they inherit its reasoning, safety, and grounding capabilities. Custom agents (built with Bot Framework or Copilot Studio) are standalone and require more development effort but offer greater flexibility for complex workflows.

---

## Step 2: Load and Explore the Manifest

Load the declarative agent manifest and examine its structure:

```python
import json

with open("lab-069/declarative_agent.json", "r") as f:
    manifest = json.load(f)

print(f"Agent Name: {manifest['name']}")
print(f"Description: {manifest['description']}")
print(f"\nTop-level keys: {list(manifest.keys())}")
print(f"Instructions length: {len(manifest['instructions'])} characters")
```

**Expected:**

```
Agent Name: HR Assistant
Description: A declarative agent for answering HR policy questions and managing time-off requests.
```

---

## Step 3: Knowledge Sources Analysis

Examine the knowledge sources configured for the agent:

```python
knowledge = manifest["knowledge_sources"]
print(f"Number of knowledge sources: {len(knowledge)}")
for i, source in enumerate(knowledge):
    print(f"\n  Source {i+1}:")
    print(f"    Type: {source['type']}")
    print(f"    Name: {source['name']}")
    print(f"    Description: {source['description']}")
```

**Expected:**

```
Number of knowledge sources: 3
```

!!! tip "Scoped Knowledge"
    Each knowledge source limits what the agent can access. By specifying exactly 3 sources (e.g., SharePoint site for policies, Graph connector for org data, uploaded file for benefits guide), the agent is grounded in verified organizational information and cannot access data outside its scope.

---

## Step 4: API Plugin Configuration

Examine the API plugins available to the agent:

```python
plugins = manifest["api_plugins"]
print(f"Number of API plugins: {len(plugins)}")
for plugin in plugins:
    print(f"\n  Plugin: {plugin['name']}")
    print(f"  Description: {plugin['description']}")
    print(f"  Endpoint: {plugin['endpoint']}")
    print(f"  Operations: {[op['name'] for op in plugin['operations']]}")
```

**Expected:**

```
Number of API plugins: 1
```

!!! warning "Plugin Security"
    API plugins allow the agent to take actions — submitting requests, updating records, or querying external systems. Each plugin should use OAuth 2.0 authentication and be restricted to the minimum required permissions. Always validate that plugin endpoints are internal and trusted.

---

## Step 5: Conversation Starters

Examine the conversation starters that guide users:

```python
starters = manifest["conversation_starters"]
print(f"Number of conversation starters: {len(starters)}")
for i, starter in enumerate(starters):
    print(f"\n  Starter {i+1}: {starter['text']}")
    print(f"    Category: {starter.get('category', 'general')}")
```

**Expected:**

```
Number of conversation starters: 4
```

Conversation starters appear as clickable suggestions when users first interact with the agent. They guide users toward the agent's core capabilities and reduce the "blank prompt" problem.

---

## Step 6: Manifest Validation

Validate the manifest for completeness and common issues:

```python
required_fields = ["name", "description", "instructions", "knowledge_sources",
                   "api_plugins", "conversation_starters"]
missing = [f for f in required_fields if f not in manifest]
print(f"Missing required fields: {missing if missing else 'None'}")

# Validation checks
checks = {
    "Has name": bool(manifest.get("name")),
    "Has description": bool(manifest.get("description")),
    "Has instructions": len(manifest.get("instructions", "")) > 50,
    "Knowledge sources > 0": len(manifest.get("knowledge_sources", [])) > 0,
    "Conversation starters > 0": len(manifest.get("conversation_starters", [])) > 0,
}

print("\nValidation Results:")
for check, passed in checks.items():
    status = "✅ PASS" if passed else "❌ FAIL"
    print(f"  {status} — {check}")

print(f"\nOverall: {'All checks passed' if all(checks.values()) else 'Some checks failed'}")
```

---

## 🐛 Bug-Fix Exercise

The file `lab-069/broken_manifest.py` has **3 bugs** in how it validates the manifest:

```bash
python lab-069/broken_manifest.py
```

| Test | What it checks | Hint |
|------|---------------|------|
| Test 1 | Knowledge source count | Should read from `knowledge_sources`, not `data_sources` |
| Test 2 | Plugin validation | Should check `api_plugins`, not `extensions` |
| Test 3 | Starter text extraction | Should access `starter['text']`, not `starter['prompt']` |

---

## 📁 Supporting Files

```
lab-069/
├── declarative_agent.json   ← Complete declarative agent manifest
└── broken_manifest.py       ← Bug-fix exercise (3 bugs + self-tests)
```

```bash
cd docs/docs/en/labs
python lab-069/broken_manifest.py    # Bug-fix exercise
```

---

## 🧠 Knowledge Check

??? question "**Q1 (Multiple Choice):** What is the main advantage of declarative agents over custom-built agents?"

    - A) They are faster at inference
    - B) They require no code — all configuration is defined in a JSON manifest
    - C) They can access any data source without restrictions
    - D) They run on-premises only

    ??? success "✅ Reveal Answer"
        **Correct: B) They require no code — all configuration is defined in a JSON manifest**

        Declarative agents extend Microsoft 365 Copilot by configuring behavior through a JSON manifest. This includes instructions (system prompt), knowledge sources, API plugins, and conversation starters. No coding is required, making them accessible to non-developers while still providing scoped, governed agent capabilities.

??? question "**Q2 (Multiple Choice):** Why are scoped knowledge sources important for declarative agents?"

    - A) They make the agent respond faster
    - B) They ensure the agent only accesses verified, authorized data — preventing hallucination from ungrounded sources
    - C) They are required by the Teams app store
    - D) They reduce the manifest file size

    ??? success "✅ Reveal Answer"
        **Correct: B) They ensure the agent only accesses verified, authorized data — preventing hallucination from ungrounded sources**

        By explicitly listing knowledge sources (SharePoint sites, Graph connectors, files), the agent is grounded in organizational data. It cannot access data outside its scope, reducing hallucination risk and ensuring compliance with data access policies. This is a key governance advantage of declarative agents.

??? question "**Q3 (Run the Lab):** How many knowledge sources are configured in the manifest?"

    Load the manifest JSON and check `len(manifest['knowledge_sources'])`.

    ??? success "✅ Reveal Answer"
        **3 knowledge sources**

        The HR Assistant agent has 3 knowledge sources configured, providing it with scoped access to company policies, organizational data, and employee benefits information. Each source is explicitly declared in the manifest.

??? question "**Q4 (Run the Lab):** How many API plugins are configured?"

    Check `len(manifest['api_plugins'])`.

    ??? success "✅ Reveal Answer"
        **1 API plugin**

        The agent has 1 API plugin configured, enabling it to perform actions like submitting time-off requests through an HR API. API plugins allow declarative agents to go beyond chat and take real actions on behalf of users.

??? question "**Q5 (Run the Lab):** How many conversation starters are defined?"

    Check `len(manifest['conversation_starters'])`.

    ??? success "✅ Reveal Answer"
        **4 conversation starters**

        The manifest defines 4 conversation starters that appear as clickable suggestions when users first interact with the agent. These guide users toward the agent's core capabilities — asking about leave policies, submitting time-off requests, checking benefits, and getting onboarding help.

---

## Summary

| Topic | What You Learned |
|-------|-----------------|
| Declarative Agents | Extend M365 Copilot through JSON manifest configuration |
| Instructions | Define persona, tone, and behavioral boundaries |
| Knowledge Sources | Scope agent access to verified organizational data |
| API Plugins | Enable agents to perform actions via external APIs |
| Conversation Starters | Guide users toward productive interactions |
| Manifest Validation | Verify completeness and correctness of agent configuration |

---

## Next Steps

- **[Lab 070](lab-070-agent-ux-patterns.md)** — Agent UX Patterns (design effective agent interactions)
- **[Lab 066](lab-066-copilot-studio-governance.md)** — Copilot Studio Governance (govern agent deployments)
- **[Lab 008](lab-008-responsible-ai.md)** — Responsible AI (foundational governance principles)
