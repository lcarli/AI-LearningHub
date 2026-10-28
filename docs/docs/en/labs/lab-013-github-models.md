---
tags: [local-models, foundry-local, ollama, free, python, llm]
lab:
  id: '013'
  level: L100
  journey: llm-foundations
  time_min: 45
  cost:
    tier: free
    requires: []
    estimate_usd: US$ 0; runs on local hardware.
    simulation: false
    cleanup: false
  status: active
  last_verified: '2026-10-27'
  languages: [en, pt, fr]
---
# Lab 013: Free LLM Backends — Foundry Local and Ollama

<div class="lab-meta">
  <span><strong>Level:</strong> <span class="level-badge level-100">L100</span></span>
  <span><strong>Journey:</strong> LLM Foundations</span>
  <span><strong>Time:</strong> ~45 min</span>
  <span><strong>💰 Cost:</strong> <span class="level-badge cost-free">Free</span> — local execution, no account or credit card</span>
</div>

!!! info "Why this lab changed"
    GitHub Models inference was retired on July 30, 2026. This lab now provides the shared free backend used by the hub: Foundry Local on supported Windows devices or Ollama on Windows, macOS, and Linux.

## What You'll Learn

- Choose between Foundry Local and Ollama
- Start an OpenAI-compatible local endpoint
- Call a local chat model from Python
- Configure the environment variables used by other labs
- Verify that no prompts or data leave your machine

## Choose a Runtime

=== "Foundry Local"
    Best for supported Windows devices and DirectML acceleration.

    ```powershell
    winget install Microsoft.FoundryLocal
    foundry model run phi-4-mini
    $env:LOCAL_LLM_BASE_URL = "http://localhost:5273/v1"
    $env:LOCAL_LLM_MODEL = "phi-4-mini"
    ```

=== "Ollama"
    Cross-platform and easy to use on Windows, macOS, and Linux.

    1. Install [Ollama](https://ollama.com/download).
    2. Start a small model:

    ```bash
    ollama run phi4-mini
    ```

    Configure the shared endpoint:

    === "PowerShell"
        ```powershell
        $env:LOCAL_LLM_BASE_URL = "http://localhost:11434/v1"
        $env:LOCAL_LLM_MODEL = "phi4-mini"
        ```

    === "macOS / Linux"
        ```bash
        export LOCAL_LLM_BASE_URL="http://localhost:11434/v1"
        export LOCAL_LLM_MODEL="phi4-mini"
        ```

## Supporting Files

| File | Description | Download |
|------|-------------|----------|
| `requirements.txt` | Python dependency | [Download](lab-013/requirements.txt) |
| `starter.py` | Local-backend exercises | [Download](lab-013/starter.py) |

## Exercise 1 — Verify the Endpoint

Install the client and run the starter:

```bash
pip install -r requirements.txt
python starter.py
```

The OpenAI SDK accepts both runtimes because they expose an OpenAI-compatible API:

```python
import os
from openai import OpenAI

client = OpenAI(
    base_url=os.environ["LOCAL_LLM_BASE_URL"],
    api_key="local",
)

response = client.chat.completions.create(
    model=os.environ["LOCAL_LLM_MODEL"],
    messages=[{"role": "user", "content": "Explain MCP in two sentences."}],
)
print(response.choices[0].message.content)
```

## Exercise 2 — Confirm Local Processing

1. Disconnect from the internet after the model download completes.
2. Run `python starter.py` again.
3. Confirm the response still succeeds.
4. Stop the runtime and confirm the script reports a connection error rather than silently switching to a cloud service.

## Shared Configuration for Other Labs

The migrated labs use these variables:

| Variable | Example | Purpose |
|----------|---------|---------|
| `LOCAL_LLM_BASE_URL` | `http://localhost:11434/v1` | OpenAI-compatible endpoint |
| `LOCAL_LLM_MODEL` | `phi4-mini` | Installed chat model |
| `LOCAL_EMBEDDING_MODEL` | Runtime-specific | Optional embedding model |

!!! warning "Model capabilities vary"
    Tool calling, structured output, embeddings, and context limits depend on the selected model and runtime. Each lab lists the capabilities it requires.

## Knowledge Check

??? question "Why do the labs use environment variables instead of hardcoding the endpoint?"
    They let the same code work with Foundry Local, Ollama, or a documented paid backend without rewriting the exercise.

??? question "Does the OpenAI SDK mean the request is sent to OpenAI?"
    No. The SDK is only the client library. `base_url` determines where the request is sent.

## Next Steps

- [Lab 015 — Ollama: Local LLMs](lab-015-ollama-local-llms.md)
- [Lab 078 — Foundry Local](lab-078-foundry-local.md)
- [Lab 017 — Structured Output](lab-017-structured-output.md)

## Supporting kit

The site build generates stable PDF and ZIP downloads. The ZIP contains the lab guide and every supporting file declared for this lab.

- [Download generated PDF](../downloads/kits/lab-013-kit-en.pdf)
- [Download generated ZIP](../downloads/kits/lab-013-kit-en.zip)
