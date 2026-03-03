# Prerequisites & Accounts

This page tells you exactly what accounts and tools you need for each lab level — and how to get them for free.

---

## Quick Reference

| You have | You can run |
|----------|-------------|
| Nothing (just a browser) | L50 labs |
| Free GitHub account | L50, L100, L200 labs |
| Free GitHub account + M365 Dev tenant | L50–L200 + Teams labs |
| Azure free trial ($200 credit) | Most L300 labs |
| Azure subscription (pay-as-you-go) | All labs including L400 |

---

## 1. GitHub Account (Free)

**Required for:** L100 and above.

Sign up at [github.com](https://github.com/signup) — it's free, no credit card needed.

With a free GitHub account you get access to:

- ✅ **GitHub Copilot Free Tier** — 2,000 code completions/month + 50 chat messages/month
- ✅ **GitHub Models** — free inference API for GPT-4o, Llama, Phi, and more (rate limited)
- ✅ **GitHub Codespaces** — 60 hours/month free cloud dev environment
- ✅ **GitHub Actions** — 2,000 minutes/month free CI/CD

!!! tip "GitHub Copilot for Students"
    If you're a student, get **GitHub Copilot Pro for free** via the [GitHub Student Developer Pack](https://education.github.com/pack).

---

## 2. GitHub Models (Free LLM Inference)

**Required for:** L200 labs that use LLMs without Azure.

GitHub Models provides free API access to frontier LLMs from your GitHub account. No credit card required.

**Setup:**

1. Go to [github.com/marketplace/models](https://github.com/marketplace/models)
2. Pick a model (e.g., `gpt-4o`, `Phi-4`, `Llama-3.3-70B`)
3. Click **"Use this model"** → **"Get API key"** to get your personal access token
4. Store it as `GITHUB_TOKEN` in your environment

**Available models include:**
- OpenAI: `gpt-4o`, `gpt-4o-mini`, `o1-mini`
- Meta: `Llama-3.3-70B-Instruct`, `Llama-3.2-90B-Vision`
- Microsoft: `Phi-4`, `Phi-3.5-MoE`
- Mistral: `Mistral-Large`

!!! warning "Rate limits"
    GitHub Models is rate-limited for free accounts. For lab purposes this is more than sufficient. If you hit limits, wait a few minutes and retry.

---

## 3. Azure Free Account

**Required for:** L300 labs.

Azure offers a free account with:

- ✅ **$200 credit** for 30 days
- ✅ **12 months** of popular free services
- ✅ **Always-free** services (includes some compute, storage, AI)

Sign up at [azure.microsoft.com/free](https://azure.microsoft.com/free) — requires a credit card for identity verification, but you won't be charged during the free period.

!!! note "Azure for Students"
    Students get **$100 credit** with **no credit card** via [Azure for Students](https://azure.microsoft.com/free/students).

### Azure Services used in L300 labs

| Service | Free tier? | Notes |
|---------|-----------|-------|
| Azure AI Foundry | ✅ Yes (limited) | Some models require pay-as-you-go |
| Azure Database for PostgreSQL Flexible Server | ✅ Yes (Burstable B1ms) | pgvector extension available |
| Azure Container Apps | ✅ Yes (limited) | For hosting MCP servers |
| Application Insights | ✅ Yes (5GB/month) | For observability labs |

---

## 4. Azure Subscription (Pay-as-you-go)

**Required for:** L400 labs and heavier L300 usage.

After your free credits run out, you'll need a **pay-as-you-go** subscription.

!!! danger "Watch your costs"
    L400 labs use more expensive services. Each lab includes an estimated monthly cost at the top. Always **set budget alerts** in the Azure portal.

    → [How to set a budget alert in Azure](https://learn.microsoft.com/azure/cost-management-billing/costs/tutorial-acm-create-budgets)

---

## 5. Microsoft 365 Developer Tenant (Optional)

**Required for:** Labs in the **Agent Builder — Teams** path.

Get a free M365 developer subscription:

1. Join the [Microsoft 365 Developer Program](https://developer.microsoft.com/microsoft-365/dev-program) (free)
2. Set up an instant sandbox with 25 user licenses
3. Use it for Teams AI Library and Copilot Studio labs

---

## 6. Local Development Tools

All coding labs assume you have these installed locally (all free):

| Tool | Install link | Labs |
|------|-------------|------|
| **VS Code** | [code.visualstudio.com](https://code.visualstudio.com) | All coding labs |
| **Python 3.11+** | [python.org](https://python.org) | Python labs |
| **.NET 8 SDK** | [dotnet.microsoft.com](https://dotnet.microsoft.com/download) | C# labs |
| **Docker Desktop** | [docker.com](https://www.docker.com/products/docker-desktop/) | Labs with local PostgreSQL |
| **Node.js 20+** | [nodejs.org](https://nodejs.org) | Some MCP labs |
| **Git** | [git-scm.com](https://git-scm.com) | All labs |

!!! tip "Use GitHub Codespaces to skip local setup"
    Many labs include a **Open in Codespaces** button. This gives you a fully configured cloud dev environment in your browser — included in the GitHub free tier (60 hrs/month).

---

## Summary Table

| Level | Accounts needed | Estimated cost |
|-------|----------------|----------------|
| <span class="level-badge level-50">L50</span> | None | Free |
| <span class="level-badge level-100">L100</span> | GitHub (free) | Free |
| <span class="level-badge level-200">L200</span> | GitHub (free) | Free |
| <span class="level-badge level-300">L300</span> | GitHub + Azure free trial | ~$0–$10/lab |
| <span class="level-badge level-400">L400</span> | GitHub + Azure paid | ~$10–$50/lab |
