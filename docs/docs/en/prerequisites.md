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

- ✅ **GitHub Copilot Free** — completion quota plus a limited monthly AI Credits allowance
- ✅ **GitHub Codespaces** — 60 hours/month free cloud dev environment
- ✅ **GitHub Actions** — 2,000 minutes/month free CI/CD

!!! info "Student eligibility"
    Check the [GitHub Student Developer Pack](https://education.github.com/pack) for current benefits. This hub does not assume that a paid Copilot plan is available.

---

## 2. Local LLM Backend (Free)

**Required for:** L200 labs that use LLMs without Azure.

Use Foundry Local or Ollama. Both run on your machine and expose an OpenAI-compatible endpoint.

**Setup:**

1. Complete [Lab 013 — Free LLM Backends](labs/lab-013-github-models.md).
2. Set `LOCAL_LLM_BASE_URL` and `LOCAL_LLM_MODEL`.
3. Keep the local runtime running while completing dependent labs.

!!! note "Hardware"
    Small models can run on CPU. Larger or faster models may require compatible GPU/NPU hardware and are marked **GRÁTIS***.

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
