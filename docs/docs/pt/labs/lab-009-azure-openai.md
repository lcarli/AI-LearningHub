---
tags: [azure, foundry, free, python, llm, azure-required]
---
# Lab 009: Azure OpenAI Service Quickstart

<div class="lab-meta">
  <span><strong>Level:</strong> <span class="level-badge level-100">L100</span></span>
  <span><strong>Path:</strong> <a href="../paths/foundry/">🏭 Microsoft Foundry</a></span>
  <span><strong>Time:</strong> ~30 min</span>
  <span><strong>💰 Cost:</strong> <span class="level-badge cost-azure-free">Azure Free</span> — Azure free account, minimal usage</span>
</div>

!!! info "Tradução em andamento"
    Este lab ainda está sendo traduzido. O conteúdo abaixo está em inglês.



## What You'll Learn

- What Azure OpenAI Service is and how it differs from OpenAI and GitHub Models
- How to create an Azure OpenAI resource and deploy a model
- How to call Azure OpenAI via the Python SDK and REST API
- API key authentication vs. Microsoft Entra ID (managed identity)
- When to use Azure OpenAI vs. GitHub Models vs. Ollama

---

## Introduction

**Azure OpenAI Service** provides access to OpenAI's models (GPT-4o, GPT-4o-mini, o1, and embeddings) through Azure infrastructure. This means:

- **Enterprise compliance**: Data stays in your Azure tenant, governed by your policies
- **Private networking**: Deploy behind a VNet, no public internet exposure
- **Azure integrations**: Works natively with Azure AI Search, Azure AI Foundry, Key Vault, and more
- **SLAs**: Enterprise-grade uptime guarantees

!!! info "Azure OpenAI vs. GitHub Models vs. OpenAI"
    | | GitHub Models | OpenAI (direct) | Azure OpenAI |
    |--|--------------|-----------------|--------------|
    | **Cost** | Free tier | Pay-per-token | Pay-per-token |
    | **Auth** | GitHub PAT | API key | API key or managed identity |
    | **Data residency** | GitHub/Azure | OpenAI US | Your Azure region |
    | **Enterprise features** | ❌ | Limited | ✅ Full |
    | **Rate limits** | Low (dev only) | Standard | Configurable |
    | **Best for** | Learning, dev | Consumer apps | Enterprise production |

For all **L200+ labs in this hub**, you can use GitHub Models (free). Azure OpenAI is the recommended path when moving to production.

---

## Prerequisites Setup

### Create an Azure Account

→ [Azure Free Account](https://azure.microsoft.com/free/) — $200 credit, 12 months free services

!!! warning "Free tier limitations"
    Azure OpenAI in the free tier has very limited quota. For these exercises, a few API calls are all you need.

### Request Azure OpenAI Access

Azure OpenAI requires an application:
1. Go to [aka.ms/oai/access](https://aka.ms/oai/access)
2. Fill out the form with your use case
3. Wait for approval (usually a few hours to 1 day)

!!! tip "While waiting for approval"
    Complete this lab's conceptual sections and use [GitHub Models](lab-013-github-models.md) for the hands-on exercises — the code is identical.

---

## Step 1: Create an Azure OpenAI Resource

1. In the [Azure Portal](https://portal.azure.com), search for **Azure OpenAI**
2. Click **+ Create**
3. Fill in:
   - **Subscription**: your subscription
   - **Resource group**: create new → `rg-learning-hub`
   - **Region**: `East US 2` (best model availability)
   - **Name**: `aoai-learning-hub-[yourname]` (must be globally unique)
   - **Pricing tier**: Standard S0
4. Click **Review + Create** → **Create**

---

## Step 2: Deploy a Model

1. Open your Azure OpenAI resource
2. Click **"Go to Azure OpenAI Studio"** → [oai.azure.com](https://oai.azure.com)
3. Click **Deployments** → **+ Create new deployment**
4. Configure:
   - **Model**: `gpt-4o-mini`
   - **Deployment name**: `gpt-4o-mini` (same as model name, easier to remember)
   - **Tokens per minute**: 10K (enough for labs)
5. Click **Deploy**

Also deploy an embedding model:
- **Model**: `text-embedding-3-small`
- **Deployment name**: `text-embedding-3-small`

---

## Step 3: Get Your Endpoint and Keys

From your Azure OpenAI resource:
1. Click **Keys and Endpoint** in the left menu
2. Copy **KEY 1** and the **Endpoint** URL

Store them as environment variables:

=== "Windows (PowerShell)"
    ```powershell
    $env:AZURE_OPENAI_API_KEY = "your_key_here"
    $env:AZURE_OPENAI_ENDPOINT = "https://your-resource.openai.azure.com/"
    $env:AZURE_OPENAI_DEPLOYMENT = "gpt-4o-mini"
    ```

=== "macOS / Linux"
    ```bash
    export AZURE_OPENAI_API_KEY="your_key_here"
    export AZURE_OPENAI_ENDPOINT="https://your-resource.openai.azure.com/"
    export AZURE_OPENAI_DEPLOYMENT="gpt-4o-mini"
    ```

!!! danger "Never commit API keys"
    Use environment variables, Azure Key Vault, or `.env` files (add `.env` to `.gitignore`). Never hardcode API keys in source code.

---

## Step 4: Your First Chat Completion

```bash
pip install openai
```

```python
import os
from openai import AzureOpenAI

# Azure OpenAI uses AzureOpenAI, not OpenAI
client = AzureOpenAI(
    api_key=os.environ["AZURE_OPENAI_API_KEY"],
    azure_endpoint=os.environ["AZURE_OPENAI_ENDPOINT"],
    api_version="2024-02-01",  # Check latest: aka.ms/oai/docs
)

response = client.chat.completions.create(
    model=os.environ["AZURE_OPENAI_DEPLOYMENT"],  # deployment name, not model name
    messages=[
        {"role": "system", "content": "You are an expert outdoor gear advisor."},
        {"role": "user", "content": "What's the best sleeping bag for winter camping at -10°C?"}
    ],
    max_tokens=300,
    temperature=0.7,
)

print(response.choices[0].message.content)
print(f"\nTokens used: {response.usage.total_tokens}")
```

!!! tip "Same API, different client"
    The code is identical to OpenAI — just use `AzureOpenAI` instead of `OpenAI`, add `azure_endpoint` and `api_version`. That's it.

---

## Step 5: Embeddings with Azure OpenAI

```python
import os
from openai import AzureOpenAI

client = AzureOpenAI(
    api_key=os.environ["AZURE_OPENAI_API_KEY"],
    azure_endpoint=os.environ["AZURE_OPENAI_ENDPOINT"],
    api_version="2024-02-01",
)

texts = [
    "waterproof hiking jacket",
    "rain-resistant outdoor coat",
    "dry sleeping bag liner",
]

response = client.embeddings.create(
    input=texts,
    model="text-embedding-3-small",  # your deployment name
)

for i, embedding in enumerate(response.data):
    print(f"'{texts[i]}': {len(embedding.embedding)} dimensions")
    print(f"  First 5 values: {embedding.embedding[:5]}")
```

---

## Step 6: Switch Between Backends with One Variable

This pattern lets you write code once and run it against GitHub Models (free) in development and Azure OpenAI in production:

```python
import os
from openai import AzureOpenAI, OpenAI


def get_client():
    """Return the appropriate client based on environment."""
    backend = os.environ.get("LLM_BACKEND", "github")  # default to free

    if backend == "azure":
        return AzureOpenAI(
            api_key=os.environ["AZURE_OPENAI_API_KEY"],
            azure_endpoint=os.environ["AZURE_OPENAI_ENDPOINT"],
            api_version="2024-02-01",
        ), os.environ.get("AZURE_OPENAI_DEPLOYMENT", "gpt-4o-mini")
    else:
        # GitHub Models (free)
        return OpenAI(
            base_url="https://models.inference.ai.azure.com",
            api_key=os.environ["GITHUB_TOKEN"],
        ), "gpt-4o-mini"


client, model = get_client()

response = client.chat.completions.create(
    model=model,
    messages=[{"role": "user", "content": "Hello!"}]
)
print(response.choices[0].message.content)
```

Usage:
```bash
# Development (free):
LLM_BACKEND=github python app.py

# Production (Azure):
LLM_BACKEND=azure python app.py
```

---

## Step 7: Managed Identity (Production Best Practice)

In production, **never use API keys**. Use Managed Identity instead:

```python
from azure.identity import DefaultAzureCredential, get_bearer_token_provider
from openai import AzureOpenAI

# Works in Azure App Service, Functions, Container Apps, AKS — anywhere with managed identity
token_provider = get_bearer_token_provider(
    DefaultAzureCredential(),
    "https://cognitiveservices.azure.com/.default"
)

client = AzureOpenAI(
    azure_endpoint=os.environ["AZURE_OPENAI_ENDPOINT"],
    azure_ad_token_provider=token_provider,
    api_version="2024-02-01",
)
# No api_key needed — credentials come from the managed identity
```

```bash
pip install azure-identity
```

Assign your app the **Cognitive Services OpenAI User** role in Azure RBAC.

---

## Azure OpenAI in Azure AI Foundry

Azure AI Foundry provides a unified portal for managing Azure OpenAI and other AI services:

1. Go to [ai.azure.com](https://ai.azure.com)
2. Create a **Hub** (once per organization) and a **Project** (once per application)
3. Deploy models through the **Model Catalog**
4. Use the **Playground** to test interactively
5. Access **Evaluation** and **Monitoring** tools

→ See [Lab 030 — Foundry Agent Service + MCP](lab-030-foundry-agent-mcp.md) for a full Foundry walkthrough.

---

## 🧠 Knowledge Check

??? question "1. What is the key code difference between using OpenAI directly and Azure OpenAI?"
    Use `AzureOpenAI` instead of `OpenAI`, and provide `azure_endpoint` and `api_version`. The `model` parameter takes your **deployment name**, not the model name. Everything else (messages, temperature, etc.) is identical.

??? question "2. Why should you use Managed Identity instead of API keys in production?"
    API keys are static secrets that can be leaked, stolen, or accidentally committed to source control. Managed Identity uses Azure's built-in identity system — no secret is ever stored in code or config files. Access is controlled through Azure RBAC, is automatically rotated, and leaves audit trails.

??? question "3. When would you choose GitHub Models over Azure OpenAI?"
    **GitHub Models** is ideal for development, learning, and prototyping — it's free with just a GitHub account, no Azure subscription needed, no deployment to configure. Choose **Azure OpenAI** when you need: data residency requirements, private networking, enterprise SLAs, integration with Azure AI Search or Foundry, or production-grade reliability.

---

## Summary

| Concept | Key takeaway |
|---------|-------------|
| **AzureOpenAI client** | Same API as OpenAI, just different constructor parameters |
| **Deployment name** | You deploy a model with a name — use that name, not the model name |
| **API version** | Required parameter — check the latest at aka.ms/oai/docs |
| **Managed identity** | Use in production — no static secrets |
| **Foundry** | The portal that wraps Azure OpenAI with eval, monitoring, and agent tools |

---

## Next Steps

- **Build a full agent with Foundry:** → [Lab 030 — Foundry Agent Service + MCP](lab-030-foundry-agent-mcp.md)
- **Add RAG to your Azure OpenAI app:** → [Lab 031 — pgvector Semantic Search on Azure](lab-031-pgvector-semantic-search.md)
- **Free alternative for labs:** → [Lab 013 — GitHub Models](lab-013-github-models.md)
