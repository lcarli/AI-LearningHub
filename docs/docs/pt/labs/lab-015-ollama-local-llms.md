---
tags: [ollama, local-llm, free, python]
---
# Lab 015: Ollama — Execute LLMs Localmente de Graça

<div class="lab-meta">
  <span><strong>Nível:</strong> <span class="level-badge level-100">L100</span></span>
  <span><strong>Caminho:</strong> Todos os caminhos</span>
  <span><strong>Tempo:</strong> ~30 min</span>
  <span><strong>💰 Custo:</strong> <span class="level-badge cost-free">Gratuito</span> — Roda na sua máquina, sem nuvem, sem chave de API</span>
</div>

!!! tip "Experimente também o Foundry Local"
    O Microsoft **Foundry Local** é uma alternativa ao Ollama com uma API compatível com OpenAI. Veja o **[Lab 078: Foundry Local](lab-078-foundry-local.md)** para um guia prático.

## O Que Você Vai Aprender

- Instalar e executar o **Ollama** para servir LLMs localmente
- Executar o **Phi-4** (poderoso modelo pequeno da Microsoft) e o **Llama 3.2** na sua própria máquina
- Gerar **embeddings de texto** localmente com `nomic-embed-text`
- Chamar o Ollama a partir de **Python** e **C#** usando a API compatível com OpenAI
- Usar o Ollama como backend de LLM para o **Semantic Kernel** (sem necessidade de chave de API)

---

## Introdução

O **Ollama** é uma ferramenta de código aberto que torna a execução de LLMs no seu laptop tão fácil quanto `ollama run phi4`. Sem chave de API, sem conta na nuvem, sem custos de uso — apenas o seu próprio hardware.

Isso é valioso para:
- **Privacidade**: dados sensíveis nunca saem da sua máquina
- **Desenvolvimento offline**: funciona sem internet
- **Controle de custos**: zero custos de API durante o desenvolvimento
- **Aprendizado**: experimente livremente sem se preocupar com cobranças

!!! info "Requisitos de hardware"
    O Ollama funciona em Mac (Apple Silicon ou Intel), Windows e Linux.  
    Para melhor desempenho: 16GB+ de RAM. Funciona com 8GB, mas mais lento.  
    GPU é opcional — os modelos rodam na CPU também (apenas mais lento).

---

## Configuração de Pré-requisitos

### Instalar o Ollama

1. Acesse [ollama.com](https://ollama.com) e baixe o instalador para o seu sistema operacional
2. Instale e verifique:

```bash
ollama --version
# ollama version 0.5.x
```

O Ollama roda como um serviço em segundo plano em `http://localhost:11434`.

---

!!! tip "Início Rápido com GitHub Codespaces"
    [![Open in GitHub Codespaces](https://github.com/codespaces/badge.svg)](https://codespaces.new/lcarli/AI-LearningHub?quickstart=1)

    Todas as dependências já estão pré-instaladas no devcontainer.


## 📦 Arquivos de Apoio

!!! note "Baixe estes arquivos antes de iniciar o laboratório"
    Salve todos os arquivos em uma pasta `lab-015/` no seu diretório de trabalho.

| Arquivo | Descrição | Download |
|---------|-----------|----------|
| `Modelfile` | Configuração de modelo do Ollama | [📥 Download](https://github.com/lcarli/AI-LearningHub/raw/main/docs/docs/en/labs/lab-015/Modelfile) |
| `chat_starter.py` | Script inicial com TODOs | [📥 Download](https://github.com/lcarli/AI-LearningHub/raw/main/docs/docs/en/labs/lab-015/chat_starter.py) |

---

## Exercício do Laboratório

### Passo 1: Execute seu primeiro modelo

```bash
ollama run phi4
```

Isso baixa o Phi-4 (~9GB) na primeira execução e depois inicia um chat interativo.

```
>>> What are AI agents?
AI agents are autonomous systems that use LLMs as their reasoning engine...
>>> /bye
```

Outros modelos para experimentar:

```bash
ollama run llama3.2        # Meta Llama 3.2 3B — rápido, pequeno
ollama run llama3.2:1b     # Ainda menor, muito rápido
ollama run mistral         # Mistral 7B — bom equilíbrio
ollama run deepseek-r1     # Modelo de raciocínio (como o1)
ollama run phi4-mini       # Phi-4 Mini — mais rápido, menos RAM
```

Verifique o que você tem instalado:
```bash
ollama list
```

### Passo 2: Baixe um modelo de embedding

```bash
ollama pull nomic-embed-text
```

Isso fornece um modelo de embedding local gratuito — perfeito para RAG sem nenhum custo de API.

### Passo 3: Chame o Ollama a partir do Python

A API do Ollama é **100% compatível com OpenAI**, então o mesmo código que chama o GitHub Models ou Azure OpenAI funciona aqui:

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

### Passo 4: Gere embeddings localmente

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

### Passo 5: Use o Ollama com o Semantic Kernel

Como o Ollama é compatível com OpenAI, integrá-lo ao Semantic Kernel é trivial:

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

### Passo 6: Use o Ollama como backend de um servidor MCP

Como o Ollama é compatível com OpenAI, qualquer servidor MCP que chame um LLM pode usá-lo localmente. Basta trocar a configuração do cliente:

```python
# In your MCP server's config.py
LLM_BASE_URL = "http://localhost:11434/v1"
LLM_MODEL = "phi4"
EMBED_MODEL = "nomic-embed-text"
LLM_API_KEY = "ollama"
```

Nenhuma outra alteração de código é necessária.

### Passo 7: Ollama via API REST diretamente

Você também pode chamar a API nativa do Ollama (não compatível com OpenAI):

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

## 📁 Arquivos Iniciais

Dois arquivos são fornecidos para ajudá-lo a acompanhar:

```bash
# From your cloned repo:
cd AI-LearningHub/docs/docs/en/labs/lab-015

# Chat with any local model
python chat_starter.py

# Create the OutdoorGear custom model first:
ollama create outdoorgear -f Modelfile
ollama run outdoorgear
```

O [📥 `Modelfile`](https://github.com/lcarli/AI-LearningHub/raw/main/docs/docs/en/labs/lab-015/Modelfile) cria uma persona personalizada de **Consultor de Equipamentos Outdoor** em cima do Phi-4. O [📥 `chat_starter.py`](https://github.com/lcarli/AI-LearningHub/raw/main/docs/docs/en/labs/lab-015/chat_starter.py) tem 5 exercícios cobrindo completação básica, modelos personalizados, comparação e streaming.

---

## Comparação de Modelos (em um laptop típico)

| Modelo | Tamanho | RAM necessária | Velocidade | Qualidade |
|--------|---------|----------------|------------|-----------|
| `phi4-mini` | 2.5GB | 4GB | ⚡⚡⚡ Rápido | Bom |
| `llama3.2:1b` | 1.3GB | 4GB | ⚡⚡⚡ Muito rápido | Básico |
| `llama3.2` | 2.0GB | 6GB | ⚡⚡ Rápido | Bom |
| `phi4` | 9.1GB | 12GB | ⚡ Moderado | Excelente |
| `mistral` | 4.1GB | 8GB | ⚡⚡ Rápido | Muito bom |
| `deepseek-r1` | 4.7GB | 8GB | ⚡ Moderado | Melhor raciocínio |

---

## Resumo

Agora você tem uma stack de LLM totalmente local:

- ✅ **Ollama** servindo modelos em `localhost:11434`
- ✅ **Phi-4** (ou Llama) para chat/raciocínio — gratuito, privado, offline
- ✅ **nomic-embed-text** para embeddings — gratuito, local
- ✅ O mesmo código funciona para Ollama, GitHub Models e Azure OpenAI — basta mudar a URL base

---

## Próximos Passos

- **Construa um app RAG com embeddings locais:** → [Lab 022 — RAG com GitHub Models + pgvector](lab-022-rag-github-models-pgvector.md)
- **Use com plugins do Semantic Kernel:** → [Lab 023 — Plugins, Memória e Planejadores do SK](lab-023-sk-plugins-memory.md)
- **IA local em produção:** → [Lab 044 — Phi-4 + Ollama em Produção](lab-044-phi4-ollama-production.md)
