# What's New

Track the latest labs, content updates, and improvements to the AI Agents Learning Hub.

---

## March 2025

### 🚀 New Labs Added

| Lab | Title | Level | Path |
|-----|-------|-------|------|
| [Lab 040](labs/lab-040-autogen-multi-agent.md) | Production Multi-Agent with AutoGen | L400 | Pro Code |
| [Lab 044](labs/lab-044-phi4-ollama-production.md) | Phi-4 + Ollama in Production | L400 | Pro Code |
| [Lab 035](labs/lab-035-agent-evaluation.md) | Agent Evaluation with Azure AI Eval SDK | L300 | Pro Code |
| [Lab 034](labs/lab-034-multi-agent-sk.md) | Multi-Agent Orchestration with Semantic Kernel | L300 | Semantic Kernel |
| [Lab 033](labs/lab-033-agent-observability.md) | Agent Observability with Application Insights | L300 | Foundry |
| [Lab 032](labs/lab-032-row-level-security.md) | Row Level Security for Agents | L300 | Foundry |
| [Lab 025](labs/lab-025-vscode-chat-participant.md) | VS Code Copilot Chat Participant | L200 | Agent Builder — VS Code |
| [Lab 024](labs/lab-024-teams-ai-library.md) | Teams AI Library Bot | L200 | Agent Builder — Teams |
| [Lab 011](labs/lab-011-copilot-studio-first-agent.md) | Copilot Studio — First Agent | L100 | Agent Builder — Teams |

### ✨ Infrastructure & Developer Experience

- **GitHub Codespaces support** — `.devcontainer/` with Python 3.12, .NET 8, Node 20, Azure CLI, and all lab dependencies pre-installed. Click **Code → Codespaces → New codespace** for a zero-setup environment.
- **Glossary** — 40+ AI agent terms, from Agent and RAG to pgvector and Row Level Security
- **CONTRIBUTING.md** — Full guide for contributors with lab template, numbering scheme, and code standards
- **GitHub Issue Templates** — Bug reports, new lab proposals, and translation requests
- **GitHub PR Template** — Checklist for lab contributions

### 📦 Sample Datasets

All labs now share a consistent **OutdoorGear Inc.** scenario with ready-to-use datasets:

| File | Contents |
|------|----------|
| [`data/products.csv`](https://raw.githubusercontent.com/lcarli/AI-LearningHub/main/data/products.csv) | 25 outdoor gear products with categories, prices, specs |
| [`data/knowledge-base.json`](https://raw.githubusercontent.com/lcarli/AI-LearningHub/main/data/knowledge-base.json) | 42 RAG-ready documents: policies, FAQs, product guides |
| [`data/orders.csv`](https://raw.githubusercontent.com/lcarli/AI-LearningHub/main/data/orders.csv) | 20 sample customer orders for RLS and order tracking labs |

### 🏗️ Infrastructure Templates

Deploy-to-Azure one-click buttons for three Bicep templates:

| Template | What it deploys |
|----------|----------------|
| `infra/lab-028-mcp-container-apps/` | Azure Container Apps + ACR for MCP servers |
| `infra/lab-030-foundry/` | Azure AI Foundry + Storage + AI Services |
| `infra/lab-031-pgvector/` | Azure PostgreSQL Flexible Server with pgvector |

---

## February 2025

### Labs Added

| Lab | Title | Level |
|-----|-------|-------|
| [Lab 028](labs/lab-028-deploy-mcp-azure.md) | Deploy MCP to Azure Container Apps | L300 |
| [Lab 030](labs/lab-030-foundry-agent-mcp.md) | Foundry Agent Service + MCP | L300 |
| [Lab 031](labs/lab-031-pgvector-semantic-search.md) | pgvector Semantic Search on Azure | L300 |
| [Lab 027](labs/lab-027-agent-memory-patterns.md) | Agent Memory Patterns | L200 |
| [Lab 026](labs/lab-026-agentic-rag.md) | Agentic RAG Pattern | L200 |
| [Lab 023](labs/lab-023-sk-plugins-memory.md) | SK Plugins, Memory & Planners | L200 |
| [Lab 022](labs/lab-022-rag-github-models-pgvector.md) | RAG with GitHub Models + pgvector | L200 |
| [Lab 021](labs/lab-021-mcp-server-csharp.md) | MCP Server in C# | L200 |
| [Lab 037](labs/lab-037-cicd-github-actions.md) | CI/CD for AI Agents | L300 |
| [Lab 036](labs/lab-036-prompt-injection-security.md) | Prompt Injection Defense & Security | L300 |

---

## January 2025 — Initial Release

The AI Agents Learning Hub launched with:

- 8 learning paths (Copilot, Foundry, MCP, SK, RAG, Teams, VS Code, Pro Code)
- Labs 001–017: L50 awareness content through L100 foundations
- Lab 020: MCP Server in Python
- Custom MkDocs Material theme with level badges
- Multilingual support (i18n plugin)

---

## Roadmap

Labs coming soon:

- **Lab 041** — Custom GitHub Copilot Extension (webhooks + OAuth)
- **Lab 042** — Enterprise RAG with Full Evaluation Pipeline
- **Lab 043** — Multi-modal Agents with GPT-4o Vision
- More translations (Portuguese, Spanish, French)

Want to contribute a lab? See [CONTRIBUTING.md](https://github.com/lcarli/AI-LearningHub/blob/main/CONTRIBUTING.md) or [open a proposal issue](https://github.com/lcarli/AI-LearningHub/issues/new?template=new_lab_proposal.md).
