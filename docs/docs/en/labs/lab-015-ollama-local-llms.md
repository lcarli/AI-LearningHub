---
tags: [ollama, local-llm, free, python]
---
# Lab 015: Ollama — Run LLMs Locally for Free

<div class="lab-meta">
  <span><strong>Level:</strong> <span class="level-badge level-100">L100</span></span>
  <span><strong>Path:</strong> All paths</span>
  <span><strong>Time:</strong> ~30 min</span>
  <span><strong>💰 Cost:</strong> <span class="level-badge cost-free">Free</span> — Runs on your machine, no cloud, no API key</span>
</div>

!!! tip "Also try Foundry Local"
    Microsoft **Foundry Local** is an alternative to Ollama with an OpenAI-compatible API. See **[Lab 078: Foundry Local](lab-078-foundry-local.md)** for a hands-on guide.

## What You'll Learn

- Install and run **Ollama** to serve LLMs locally
- Run **Phi-4** (Microsoft's powerful small model) and **Llama 3.2** on your own machine
- Generate **text embeddings** locally with `nomic-embed-text`
- Call Ollama from **Python** and **C#** using the OpenAI-compatible API
- Use Ollama as the LLM backend for **Semantic Kernel** (no API key needed)

---

## Introduction

**Ollama** is an open-source tool that makes running LLMs on your laptop as easy as `ollama run phi4`. No API key, no cloud account, no usage costs — just your own hardware.

This is valuable for:
- **Privacy**: sensitive data never leaves your machine
- **Offline development**: works without internet
- **Cost control**: zero API costs during development
- **Learning**: experiment freely without worrying about bills

!!! info "Hardware requirements"
    Ollama works on Mac (Apple Silicon or Intel), Windows, and Linux.  
    For best performance: 16GB+ RAM. Works with 8GB but slower.  
    GPU is optional — models run on CPU too (just slower).

---

## Prerequisites Setup

### Install Ollama

1. Go to [ollama.com](https://ollama.com) and download the installer for your OS
2. Install and verify:

```bash
ollama --version
# ollama version 0.5.x
```

Ollama runs as a background service on `http://localhost:11434`.

---

!!! tip "Quick Start with GitHub Codespaces"
    [![Open in GitHub Codespaces](https://github.com/codespaces/badge.svg)](https://codespaces.new/lcarli/AI-LearningHub?quickstart=1)

    All dependencies are pre-installed in the devcontainer.


## 📦 Supporting Files

!!! note "Download these files before starting the lab"
    Save all files to a `lab-015/` folder in your working directory.

| File | Description | Download |
|------|-------------|----------|
| `Modelfile` | Ollama model configuration | [📥 Download](https://github.com/lcarli/AI-LearningHub/raw/main/docs/docs/en/labs/lab-015/Modelfile) |
| `chat_starter.py` | Starter script with TODOs | [📥 Download](https://github.com/lcarli/AI-LearningHub/raw/main/docs/docs/en/labs/lab-015/chat_starter.py) |

---

## Lab Exercise

### Step 1: Run your first model

```bash
ollama run phi4
```

This downloads Phi-4 (~9GB) on first run, then starts an interactive chat.

```
>>> What are AI agents?
AI agents are autonomous systems that use LLMs as their reasoning engine...
>>> /bye
```

Other models to try:

```bash
ollama run llama3.2        # Meta Llama 3.2 3B — fast, small
ollama run llama3.2:1b     # Even smaller, very fast
ollama run mistral         # Mistral 7B — good balance
ollama run deepseek-r1     # Reasoning model (like o1)
ollama run phi4-mini       # Phi-4 Mini — faster, less RAM
```

Check what you have installed:
```bash
ollama list
```

### Step 2: Pull an embedding model

```bash
ollama pull nomic-embed-text
```

This gives you a free local embedding model — perfect for RAG without any API costs.

### Step 3: Call Ollama from Python

Ollama's API is **100% OpenAI-compatible**, so the same code that calls GitHub Models or Azure OpenAI works here:

```python
from openai import OpenAI

# Point to local Ollama instead of OpenAI
client = OpenAI(
    base_url="http://localhost:11434/v1",
    api_key="ollama",  # required by the client, but value doesn't matter
)

response = client.chat.completions.create(
    model="phi4",
    messages=[
        {"role": "system", "content": "You are a helpful assistant."},
        {"role": "user", "content": "Explain the difference between RAG and fine-tuning in 3 sentences."},
    ],
    temperature=0.3,
)

print(response.choices[0].message.content)
```

### Step 4: Generate embeddings locally

```python
from openai import OpenAI

client = OpenAI(
    base_url="http://localhost:11434/v1",
    api_key="ollama",
)

response = client.embeddings.create(
    model="nomic-embed-text",
    input="waterproof hiking boots for mountain trails",
)

vector = response.data[0].embedding
print(f"Dimensions: {len(vector)}")   # 768
print(f"First 5:    {vector[:5]}")
```

### Step 5: Use Ollama with Semantic Kernel

Because Ollama is OpenAI-compatible, plugging it into Semantic Kernel is trivial:

=== "Python"

    ```python
    import asyncio
    from semantic_kernel import Kernel
    from semantic_kernel.connectors.ai.open_ai import OpenAIChatCompletion

    async def main():
        kernel = Kernel()

        # Use Ollama instead of GitHub Models — just change base_url and model
        kernel.add_service(
            OpenAIChatCompletion(
                ai_model_id="phi4",
                api_key="ollama",
                base_url="http://localhost:11434/v1",
            )
        )

        # The rest of your agent code is identical!
        from semantic_kernel.contents import ChatHistory
        history = ChatHistory()
        history.add_system_message("You are a helpful AI assistant.")
        history.add_user_message("What is Semantic Kernel?")

        chat = kernel.get_service(type=OpenAIChatCompletion)
        result = await chat.get_chat_message_content(
            chat_history=history,
            settings=kernel.get_prompt_execution_settings_from_service_id("default"),
        )
        print(result)

    asyncio.run(main())
    ```

=== "C#"

    ```csharp
    using Microsoft.SemanticKernel;
    using Microsoft.SemanticKernel.ChatCompletion;

    var builder = Kernel.CreateBuilder();
    builder.AddOpenAIChatCompletion(
        modelId: "phi4",
        apiKey: "ollama",
        endpoint: new Uri("http://localhost:11434/v1")
    );
    var kernel = builder.Build();

    var chat = kernel.GetRequiredService<IChatCompletionService>();
    var history = new ChatHistory("You are a helpful AI assistant.");
    history.AddUserMessage("What is Semantic Kernel?");

    var response = await chat.GetChatMessageContentAsync(history);
    Console.WriteLine(response.Content);
    ```

### Step 6: Use Ollama as an MCP server backend

Since Ollama is OpenAI-compatible, any MCP server that calls an LLM can use it locally. Just swap the client configuration:

```python
# In your MCP server's config.py
LLM_BASE_URL = "http://localhost:11434/v1"
LLM_MODEL = "phi4"
EMBED_MODEL = "nomic-embed-text"
LLM_API_KEY = "ollama"
```

No other code changes needed.

### Step 7: Ollama via REST API directly

You can also call Ollama's native API (not OpenAI-compatible):

```bash
curl http://localhost:11434/api/chat -d '{
  "model": "phi4",
  "messages": [
    {"role": "user", "content": "Why is the sky blue?"}
  ],
  "stream": false
}'
```

---

## 📁 Starter Files

Two files are provided to help you follow along:

```bash

# Chat with any local model
python chat_starter.py

# Create the OutdoorGear custom model first:
ollama create outdoorgear -f Modelfile
ollama run outdoorgear
```

The [📥 `Modelfile`](https://github.com/lcarli/AI-LearningHub/raw/main/docs/docs/en/labs/lab-015/Modelfile) creates a custom **OutdoorGear Advisor** persona on top of Phi-4. The [📥 `chat_starter.py`](https://github.com/lcarli/AI-LearningHub/raw/main/docs/docs/en/labs/lab-015/chat_starter.py) has 5 exercises covering basic completion, custom models, comparison, and streaming.

---

## Model Comparison (on a typical laptop)

| Model | Size | RAM needed | Speed | Quality |
|-------|------|-----------|-------|---------|
| `phi4-mini` | 2.5GB | 4GB | ⚡⚡⚡ Fast | Good |
| `llama3.2:1b` | 1.3GB | 4GB | ⚡⚡⚡ Very fast | Basic |
| `llama3.2` | 2.0GB | 6GB | ⚡⚡ Fast | Good |
| `phi4` | 9.1GB | 12GB | ⚡ Moderate | Excellent |
| `mistral` | 4.1GB | 8GB | ⚡⚡ Fast | Very good |
| `deepseek-r1` | 4.7GB | 8GB | ⚡ Moderate | Best reasoning |

---

## Summary

You now have a fully local LLM stack:

- ✅ **Ollama** serving models on `localhost:11434`
- ✅ **Phi-4** (or Llama) for chat/reasoning — free, private, offline
- ✅ **nomic-embed-text** for embeddings — free, local
- ✅ Same code works for Ollama, GitHub Models, and Azure OpenAI — just change base URL

---

## Next Steps

- **Build a RAG app with local embeddings:** → [Lab 022 — RAG with GitHub Models + pgvector](lab-022-rag-github-models-pgvector.md)
- **Use with Semantic Kernel plugins:** → [Lab 023 — SK Plugins, Memory & Planners](lab-023-sk-plugins-memory.md)
- **Production local AI:** → [Lab 044 — Phi-4 + Ollama in Production](lab-044-phi4-ollama-production.md)
