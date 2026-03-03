# Lab 013: GitHub Models — Free LLM Inference

<div class="lab-meta">
  <span><strong>Level:</strong> <span class="level-badge level-100">L100</span></span>
  <span><strong>Path:</strong> <a href="../paths/copilot/">🤖 GitHub Copilot</a> · <a href="../paths/rag/">📚 RAG</a></span>
  <span><strong>Time:</strong> ~25 min</span>
  <span><strong>💰 Cost:</strong> <span class="level-badge cost-github">GitHub Free</span> — Free GitHub account, no credit card</span>
</div>

## What You'll Learn

- What GitHub Models is and which models are available
- How to use the GitHub Models **playground** (browser, no code)
- How to call GitHub Models via the **REST API** and **Python SDK**
- How to generate **text embeddings** for free (needed for RAG labs)

---

## Introduction

**GitHub Models** gives you free API access to frontier LLMs — GPT-4o, Llama, Phi, Mistral, and more — using your GitHub personal access token. No Azure account, no credit card, no sign-up beyond what you already have.

This is the LLM backend used in all **L200 labs** in this hub.

---

## Prerequisites Setup

### 1. Create a GitHub personal access token

1. Go to [github.com/settings/tokens](https://github.com/settings/tokens)
2. Click **"Generate new token (classic)"**
3. Name: `github-models-labs`
4. Expiration: 90 days
5. Scopes: none needed (read-only access is sufficient for Models API)
6. Click **"Generate token"** — copy and save it immediately

### 2. Store the token as an environment variable

=== "Windows (PowerShell)"
    ```powershell
    $env:GITHUB_TOKEN = "ghp_your_token_here"
    ```

=== "macOS / Linux"
    ```bash
    export GITHUB_TOKEN="ghp_your_token_here"
    ```

=== "VS Code / Codespaces"
    Add to your `.env` file (never commit this file to git!):
    ```
    GITHUB_TOKEN=ghp_your_token_here
    ```

---

## Lab Exercise

### Step 1: Explore the Playground

1. Go to [github.com/marketplace/models](https://github.com/marketplace/models)
2. Click on **"gpt-4o"**
3. Click **"Playground"**
4. Type a message and press Enter

You're now chatting with GPT-4o for free, directly in the browser.

Try different models:
- `gpt-4o-mini` — faster and cheaper
- `Phi-4` — Microsoft's small but powerful model
- `Llama-3.3-70B-Instruct` — Meta's open-source model

### Step 2: Make your first API call

=== "Python"

    Install the OpenAI Python SDK (it's compatible with GitHub Models):
    ```bash
    pip install openai
    ```

    Create `hello_models.py`:
    ```python
    import os
    from openai import OpenAI

    client = OpenAI(
        base_url="https://models.inference.ai.azure.com",
        api_key=os.environ["GITHUB_TOKEN"],
    )

    response = client.chat.completions.create(
        model="gpt-4o-mini",
        messages=[
            {"role": "system", "content": "You are a helpful assistant."},
            {"role": "user", "content": "What is the Model Context Protocol?"},
        ],
        max_tokens=500,
    )

    print(response.choices[0].message.content)
    ```

    Run it:
    ```bash
    python hello_models.py
    ```

=== "C#"

    Add the NuGet package:
    ```bash
    dotnet add package Azure.AI.Inference
    ```

    Create `Program.cs`:
    ```csharp
    using Azure;
    using Azure.AI.Inference;

    var endpoint = new Uri("https://models.inference.ai.azure.com");
    var credential = new AzureKeyCredential(Environment.GetEnvironmentVariable("GITHUB_TOKEN")!);
    var client = new ChatCompletionsClient(endpoint, credential);

    var response = await client.CompleteAsync(new ChatCompletionsOptions
    {
        Model = "gpt-4o-mini",
        Messages =
        {
            new ChatRequestSystemMessage("You are a helpful assistant."),
            new ChatRequestUserMessage("What is the Model Context Protocol?"),
        },
        MaxTokens = 500,
    });

    Console.WriteLine(response.Value.Content);
    ```

=== "REST (curl)"

    ```bash
    curl https://models.inference.ai.azure.com/chat/completions \
      -H "Authorization: Bearer $GITHUB_TOKEN" \
      -H "Content-Type: application/json" \
      -d '{
        "model": "gpt-4o-mini",
        "messages": [
          {"role": "user", "content": "What is the Model Context Protocol?"}
        ]
      }'
    ```

### Step 3: Generate text embeddings

Embeddings are the key ingredient for RAG. Let's generate one:

=== "Python"

    ```python
    import os
    from openai import OpenAI

    client = OpenAI(
        base_url="https://models.inference.ai.azure.com",
        api_key=os.environ["GITHUB_TOKEN"],
    )

    response = client.embeddings.create(
        model="text-embedding-3-small",
        input="A waterproof outdoor camping tent",
    )

    vector = response.data[0].embedding
    print(f"Embedding dimensions: {len(vector)}")
    print(f"First 5 values: {vector[:5]}")
    ```

!!! info "What is an embedding?"
    An embedding is a list of numbers (a vector) that represents the *meaning* of a piece of text.  
    Similar texts produce vectors that are close together in vector space.  
    This is how semantic search works: compare the query vector to all document vectors and return the closest ones.

### Step 4: Available Models

Check what models are available via the API:

```python
import os
from openai import OpenAI

client = OpenAI(
    base_url="https://models.inference.ai.azure.com",
    api_key=os.environ["GITHUB_TOKEN"],
)

models = client.models.list()
for model in models.data:
    print(model.id)
```

---

## Rate Limits

GitHub Models is free but rate-limited:

| Tier | Requests/min | Tokens/day |
|------|-------------|-----------|
| Free | ~15 | ~150,000 |
| Copilot Pro/Business | Higher | Higher |

For lab purposes, these limits are more than sufficient. If you hit a limit, wait 1 minute.

---

## Summary

GitHub Models gives you **free access to frontier LLMs** using just your GitHub account. You can use the playground browser UI or call the API from Python/C#/REST. The API is OpenAI-compatible, so any code that works with OpenAI works here too.

---

## Next Steps

- **Build an agent with Semantic Kernel:** → [Lab 014 — SK Hello Agent](lab-014-sk-hello-agent.md)
- **Build a RAG app:** → [Lab 022 — RAG with GitHub Models + pgvector](lab-022-rag-github-models.md)
