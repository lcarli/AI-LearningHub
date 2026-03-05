# 🏭 Microsoft Foundry Path

<span class="level-badge level-200">L200</span> <span class="level-badge level-300">L300</span> <span class="level-badge level-400">L400</span>

Microsoft Foundry (Azure AI Foundry) is Microsoft's enterprise-grade platform for building, deploying, and managing AI agents at scale. It brings together model catalog, agent orchestration, evaluation, monitoring, and governance under one unified portal and SDK.

---

## What You'll Build

By the end of this path you will have:

- ✅ Navigated the Azure AI Foundry portal and deployed a model
- ✅ Built an **AI Agent** with tools and MCP integration
- ✅ Connected a **PostgreSQL database** via MCP for semantic search
- ✅ Secured data with **Row Level Security**
- ✅ Observed and traced agent calls with **Application Insights**
- ✅ Evaluated agent quality with the **Azure AI Evaluation SDK**

---

## Path Labs (7 labs, ~525 min total)

| Lab | Title | Level | Cost |
|-----|-------|-------|------|
| [Lab 009](../../labs/lab-009-azure-openai.md) | Azure OpenAI Service Quickstart | <span class="level-badge level-100">L100</span> | ⚠️ Azure |
| [Lab 030](../../labs/lab-030-foundry-agent-mcp.md) | Microsoft Foundry Agent Service + MCP | <span class="level-badge level-300">L300</span> | Free |
| [Lab 032](../../labs/lab-032-row-level-security.md) | Row Level Security for Agents | <span class="level-badge level-300">L300</span> | ✅ Free |
| [Lab 033](../../labs/lab-033-agent-observability.md) | Agent Observability with Application Insights | <span class="level-badge level-300">L300</span> | ✅ Free |
| [Lab 049](../../labs/lab-049-foundry-iq-agent-tracing.md) | Foundry IQ — Agent Tracing with OpenTelemetry | <span class="level-badge level-300">L300</span> | ✅ Free |
| [Lab 074](../../labs/lab-074-foundry-agent-service.md) | Foundry Agent Service — Production Multi-Agent Deployment | <span class="level-badge level-300">L300</span> | ✅ Free |
| [Lab 050](../../labs/lab-050-multi-agent-observability.md) | Multi-Agent Observability with GenAI Semantic Conventions | <span class="level-badge level-400">L400</span> | ✅ Free |

---

## Microsoft Foundry Key Components

| Component | Description |
|-----------|-------------|
| **Model Catalog** | 1,800+ models including OpenAI, Meta, Mistral, Cohere |
| **Agent Service** | Managed agent runtime with tool calling, code interpreter, MCP |
| **Evaluation SDK** | Quality metrics: groundedness, coherence, relevance, safety |
| **Azure Monitor** | Distributed tracing, metrics, Application Insights integration |
| **Content Safety** | Built-in responsible AI guardrails |

---

## Prerequisites

!!! warning "Azure subscription required"
    All labs in this path require an Azure subscription.  
    → [Set up your Azure account](../../prerequisites.md)

---

## External Resources

- [Microsoft Foundry Docs](https://learn.microsoft.com/azure/ai-foundry/)
- [Azure AI Agent Service](https://learn.microsoft.com/azure/ai-services/agents/)
- [Azure AI Evaluation SDK](https://learn.microsoft.com/azure/ai-foundry/how-to/develop/agent-evaluate-sdk)
- [Tracing with App Insights](https://learn.microsoft.com/azure/ai-services/agents/concepts/tracing)
