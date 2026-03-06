---
tags: [github-models, free, python, llm]
---
# Lab 013: GitHub Models — Inferência LLM Gratuita

<div class="lab-meta">
  <span><strong>Nível:</strong> <span class="level-badge level-100">L100</span></span>
  <span><strong>Trilha:</strong> <a href="../paths/copilot/">🤖 GitHub Copilot</a> · <a href="../paths/rag/">📚 RAG</a></span>
  <span><strong>Tempo:</strong> ~25 min</span>
  <span><strong>💰 Custo:</strong> <span class="level-badge cost-github">GitHub Free</span> — Conta GitHub gratuita, sem cartão de crédito</span>
</div>

## O Que Você Vai Aprender

- O que é o GitHub Models e quais modelos estão disponíveis
- Como usar o **playground** do GitHub Models (navegador, sem código)
- Como chamar o GitHub Models via **REST API** e **Python SDK**
- Como gerar **embeddings de texto** gratuitamente (necessário para os labs de RAG)

---

## Introdução

O **GitHub Models** oferece acesso gratuito via API a LLMs de ponta — GPT-4o, Llama, Phi, Mistral e mais — usando seu token de acesso pessoal do GitHub. Sem conta Azure, sem cartão de crédito, sem cadastro além do que você já possui.

Este é o backend de LLM usado em todos os **labs L200** neste hub.

---

## Configuração de Pré-requisitos

### 1. Crie um token de acesso pessoal do GitHub

1. Acesse [github.com/settings/tokens](https://github.com/settings/tokens)
2. Clique em **"Generate new token (classic)"**
3. Nome: `github-models-labs`
4. Expiração: 90 dias
5. Escopos: nenhum necessário (acesso somente leitura é suficiente para a API do Models)
6. Clique em **"Generate token"** — copie e salve imediatamente

### 2. Armazene o token como variável de ambiente

=== "Windows (PowerShell)"
    ```powershell
    $env:GITHUB_TOKEN = "ghp_your_token_here"
    ```

=== "macOS / Linux"
    ```bash
    export GITHUB_TOKEN="ghp_your_token_here"
    ```

=== "VS Code / Codespaces"
    Adicione ao seu arquivo `.env` (nunca faça commit deste arquivo no git!):
    ```
    GITHUB_TOKEN=ghp_your_token_here
    ```

---

## 📦 Arquivos de Apoio

!!! note "Baixe estes arquivos antes de iniciar o lab"
    Salve todos os arquivos em uma pasta `lab-013/` no seu diretório de trabalho.

| Arquivo | Descrição | Download |
|---------|-----------|----------|
| `requirements.txt` | Dependências Python | [📥 Download](https://github.com/lcarli/AI-LearningHub/raw/main/docs/docs/en/labs/lab-013/requirements.txt) |
| `starter.py` | Script inicial com TODOs | [📥 Download](https://github.com/lcarli/AI-LearningHub/raw/main/docs/docs/en/labs/lab-013/starter.py) |

---

## Exercício do Lab

### Passo 1: Explore o Playground

1. Acesse [github.com/marketplace/models](https://github.com/marketplace/models)
2. Clique em **"gpt-4o"**
3. Clique em **"Playground"**
4. Digite uma mensagem e pressione Enter

Agora você está conversando com o GPT-4o gratuitamente, diretamente no navegador.

Experimente diferentes modelos:
- `gpt-4o-mini` — mais rápido e mais econômico
- `Phi-4` — modelo pequeno mas poderoso da Microsoft
- `Llama-3.3-70B-Instruct` — modelo open-source da Meta

### Passo 2: Faça sua primeira chamada à API

=== "Python"

    Instale o OpenAI Python SDK (é compatível com o GitHub Models):
    ```bash
    pip install openai
    ```

    Crie `hello_models.py`:
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

    Execute:
    ```bash
    python hello_models.py
    ```

=== "C#"

    Adicione o pacote NuGet:
    ```bash
    dotnet add package Azure.AI.Inference
    ```

    Crie `Program.cs`:
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

### Passo 3: Gere embeddings de texto

Embeddings são o ingrediente principal para RAG. Vamos gerar um:

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

!!! info "O que é um embedding?"
    Um embedding é uma lista de números (um vetor) que representa o *significado* de um trecho de texto.  
    Textos semelhantes produzem vetores que ficam próximos no espaço vetorial.  
    É assim que a busca semântica funciona: compara o vetor da consulta com todos os vetores dos documentos e retorna os mais próximos.

### Passo 4: Modelos Disponíveis

Verifique quais modelos estão disponíveis via API:

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

## 📁 Arquivos Iniciais

Baixe o arquivo inicial para acompanhar:

```bash
pip install -r requirements.txt
python starter.py
```

O [📥 `starter.py`](https://github.com/lcarli/AI-LearningHub/raw/main/docs/docs/en/labs/lab-013/starter.py) contém 4 exercícios com comentários `TODO`. Complete cada TODO para construir um cliente funcional do GitHub Models.

---

## Limites de Taxa

O GitHub Models é gratuito, mas possui limites de taxa:

| Plano | Requisições/min | Tokens/dia |
|-------|-----------------|------------|
| Free | ~15 | ~150.000 |
| Copilot Pro/Business | Maior | Maior |

Para fins de lab, esses limites são mais que suficientes. Se você atingir um limite, aguarde 1 minuto.

---

## Resumo

O GitHub Models oferece **acesso gratuito a LLMs de ponta** usando apenas sua conta GitHub. Você pode usar a interface do playground no navegador ou chamar a API via Python/C#/REST. A API é compatível com OpenAI, então qualquer código que funcione com OpenAI funciona aqui também.

---

## Próximos Passos

- **Construa um agente com Semantic Kernel:** → [Lab 014 — SK Hello Agent](lab-014-sk-hello-agent.md)
- **Construa um app de RAG:** → [Lab 022 — RAG com GitHub Models + pgvector](lab-022-rag-github-models-pgvector.md)
