---
tags: [python, free, github-models, streaming]
---
# Lab 019: Respostas em Streaming com Agentes

<div class="lab-meta">
  <span><strong>Nível:</strong> <span class="level-badge level-100">L100</span></span>
  <span><strong>Caminho:</strong> <a href="../paths/pro-code/">⚙️ Pro Code Agents</a></span>
  <span><strong>Tempo:</strong> ~25 min</span>
  <span><strong>💰 Custo:</strong> <span class="level-badge cost-github">GitHub Free</span> — Conta GitHub gratuita, sem cartão de crédito</span>
</div>

## O Que Você Vai Aprender

- Por que streaming é importante para a UX de agentes de IA
- Como usar `stream=True` com o SDK Python da OpenAI
- Como lidar com chamadas de ferramentas em streaming (complexo — diferente do streaming comum)
- Como retornar tokens em streaming a partir de um endpoint FastAPI
- Como fazer streaming com Semantic Kernel

---

## Introdução

Sem streaming, os usuários ficam olhando para uma tela em branco por 3–10 segundos enquanto o modelo gera uma resposta longa. Com streaming, o texto aparece **token por token** conforme é gerado — assim como no ChatGPT.

Para agentes, o streaming é especialmente importante porque chamadas de ferramentas podem adicionar latência significativa. Mostrar saídas intermediárias ("Buscando produtos... Encontrados 3 resultados. Gerando resposta...") faz a espera parecer muito mais curta.

---

## Passo 1: Streaming Básico

```bash
pip install openai
export GITHUB_TOKEN=your_github_token
```

```python
import os
from openai import OpenAI

client = OpenAI(
    base_url="https://models.inference.ai.azure.com",
    api_key=os.environ["GITHUB_TOKEN"],
)

print("Streaming response:\n")

# stream=True retorna um gerador em vez de uma resposta completa
stream = client.chat.completions.create(
    model="gpt-4o-mini",
    messages=[
        {"role": "system", "content": "You are an outdoor gear advisor."},
        {"role": "user", "content": "Explain the three-layer clothing system for outdoor activities in detail."}
    ],
    stream=True,
)

# Itera sobre os chunks conforme eles chegam
for chunk in stream:
    delta = chunk.choices[0].delta
    if delta.content:
        print(delta.content, end="", flush=True)

print("\n\n✅ Done!")
```

O `flush=True` é crítico — sem ele, o Python faz buffer da saída e você perde o efeito de streaming.

---

## Passo 2: Coletar a Resposta Completa Durante o Streaming

Às vezes você quer mostrar a saída em streaming E ter o texto completo para processamento posterior:

```python
full_response = []

stream = client.chat.completions.create(
    model="gpt-4o-mini",
    messages=[{"role": "user", "content": "List 5 essential items for day hiking."}],
    stream=True,
)

for chunk in stream:
    delta = chunk.choices[0].delta
    if delta.content:
        print(delta.content, end="", flush=True)
        full_response.append(delta.content)

full_text = "".join(full_response)
print(f"\n\nFull response ({len(full_text)} chars):\n{full_text}")
```

---

## Passo 3: Streaming com Chamadas de Ferramentas

Streaming e chamadas de ferramentas juntos requerem tratamento cuidadoso. A chamada de ferramenta é entregue em múltiplos chunks:

```python
import json

def stream_with_tools(user_message: str, tools: list):
    """Stream a response that may include tool calls."""
    messages = [
        {"role": "system", "content": "You are an OutdoorGear advisor. Use tools when needed."},
        {"role": "user", "content": user_message}
    ]

    # Accumulators for the streaming tool call
    current_tool_calls = {}
    full_content = []

    stream = client.chat.completions.create(
        model="gpt-4o-mini",
        messages=messages,
        tools=tools,
        tool_choice="auto",
        stream=True,
    )

    finish_reason = None

    for chunk in stream:
        choice = chunk.choices[0]
        delta = choice.delta
        finish_reason = choice.finish_reason

        # Handle regular text content
        if delta.content:
            print(delta.content, end="", flush=True)
            full_content.append(delta.content)

        # Handle tool call chunks — they come piece by piece
        if delta.tool_calls:
            for tc in delta.tool_calls:
                idx = tc.index

                if idx not in current_tool_calls:
                    current_tool_calls[idx] = {
                        "id": tc.id or "",
                        "type": "function",
                        "function": {"name": "", "arguments": ""}
                    }

                if tc.id:
                    current_tool_calls[idx]["id"] = tc.id
                if tc.function.name:
                    current_tool_calls[idx]["function"]["name"] += tc.function.name
                if tc.function.arguments:
                    current_tool_calls[idx]["function"]["arguments"] += tc.function.arguments

    # After streaming, handle any tool calls
    if finish_reason == "tool_calls":
        print(f"\n  🔧 Tool calls requested: {len(current_tool_calls)}")
        for idx, tc in current_tool_calls.items():
            print(f"     → {tc['function']['name']}({tc['function']['arguments']})")
        # Execute tools and continue (same as non-streaming pattern from Lab 018)

    return "".join(full_content), current_tool_calls
```

!!! tip "Streaming + ferramentas é complexo"
    A maioria do código de produção usa modo não-streaming para a fase de chamada de ferramentas e só faz streaming da geração da resposta final. Isso é mais simples e geralmente suficiente.

---

## Passo 4: Streaming em um Endpoint FastAPI

Este é o padrão para aplicações web reais:

```python
# pip install fastapi uvicorn openai
from fastapi import FastAPI
from fastapi.responses import StreamingResponse
import os
from openai import OpenAI

app = FastAPI()
client = OpenAI(
    base_url="https://models.inference.ai.azure.com",
    api_key=os.environ["GITHUB_TOKEN"],
)


async def generate_stream(user_message: str):
    """Async generator that yields SSE-formatted chunks."""
    stream = client.chat.completions.create(
        model="gpt-4o-mini",
        messages=[
            {"role": "system", "content": "You are an outdoor gear advisor."},
            {"role": "user", "content": user_message}
        ],
        stream=True,
    )

    for chunk in stream:
        delta = chunk.choices[0].delta
        if delta.content:
            # Server-Sent Events format: data: <content>\n\n
            yield f"data: {delta.content}\n\n"

    yield "data: [DONE]\n\n"


@app.get("/stream")
async def stream_endpoint(question: str = "What gear do I need for a weekend hike?"):
    return StreamingResponse(
        generate_stream(question),
        media_type="text/event-stream",
        headers={"Cache-Control": "no-cache", "X-Accel-Buffering": "no"}
    )
```

Inicie o servidor:
```bash
uvicorn main:app --reload
```

Teste com curl:
```bash
curl "http://localhost:8000/stream?question=What+tent+is+best+for+winter+camping"
```

Ou consuma em JavaScript (navegador):
```javascript
const source = new EventSource('/stream?question=What+boots+for+hiking%3F');
source.onmessage = (event) => {
    if (event.data === '[DONE]') { source.close(); return; }
    document.getElementById('response').innerText += event.data;
};
```

---

## Passo 5: Streaming no Semantic Kernel

```python
import asyncio
import os
from semantic_kernel import Kernel
from semantic_kernel.connectors.ai.open_ai import OpenAIChatCompletion
from semantic_kernel.contents import ChatHistory

async def stream_sk_response():
    kernel = Kernel()
    kernel.add_service(
        OpenAIChatCompletion(
            ai_model_id="gpt-4o-mini",
            api_key=os.environ["GITHUB_TOKEN"],
            base_url="https://models.inference.ai.azure.com",
        )
    )

    chat = kernel.get_service(type=OpenAIChatCompletion)
    history = ChatHistory()
    history.add_system_message("You are a friendly outdoor gear advisor.")
    history.add_user_message("What are the key features to look for in a hiking backpack?")

    print("Streaming SK response:\n")

    # SK streaming uses get_streaming_chat_message_content
    async for chunk in chat.get_streaming_chat_message_content(
        chat_history=history,
        settings=None,
        kernel=kernel,
    ):
        if chunk.content:
            print(chunk.content, end="", flush=True)

    print("\n")


asyncio.run(stream_sk_response())
```

---

## Passo 6: Mostrar Progresso Durante Chamadas de Ferramentas

Para uma melhor UX, mostre aos usuários o que está acontecendo enquanto as ferramentas são executadas:

```python
import time

def run_agent_with_progress(user_message: str) -> str:
    messages = [
        {"role": "system", "content": "You are an OutdoorGear advisor. Use tools to answer accurately."},
        {"role": "user", "content": user_message}
    ]

    step = 0
    while True:
        step += 1
        response = client.chat.completions.create(
            model="gpt-4o-mini",
            messages=messages,
            tools=TOOLS,  # from Lab 018
            tool_choice="auto",
        )

        message = response.choices[0].message
        messages.append(message)

        if response.choices[0].finish_reason == "tool_calls":
            for tc in message.tool_calls:
                # Show progress to user
                print(f"  ⏳ Looking up: {tc.function.name}...", end="", flush=True)
                
                # Execute tool
                args = json.loads(tc.function.arguments)
                result = TOOL_FUNCTIONS[tc.function.name](**args)
                
                print(f" ✅")  # Done
                
                messages.append({
                    "role": "tool",
                    "tool_call_id": tc.id,
                    "content": json.dumps(result),
                })
        else:
            # Stream the final answer
            print("\n")
            stream = client.chat.completions.create(
                model="gpt-4o-mini",
                messages=messages,
                stream=True,
            )
            result_text = []
            for chunk in stream:
                if chunk.choices[0].delta.content:
                    content = chunk.choices[0].delta.content
                    print(content, end="", flush=True)
                    result_text.append(content)
            print("\n")
            return "".join(result_text)
```

Esse padrão é usado em agentes de produção: chamadas de ferramentas são executadas sem streaming (para código mais simples), e apenas a resposta final do LLM é transmitida em streaming.

---

## 🧠 Verificação de Conhecimento

??? question "1. Por que `flush=True` é importante ao imprimir tokens em streaming?"
    O Python faz buffer do stdout por padrão. Sem `flush=True`, o texto se acumula no buffer e é impresso todo de uma vez no final — anulando o propósito do streaming. `flush=True` força o buffer a ser escrito imediatamente em cada chamada `print()`.

??? question "2. Por que o streaming com chamadas de ferramentas requer código mais complexo do que o streaming básico?"
    Os dados da chamada de ferramenta chegam **em múltiplos chunks** — cada chunk contém um pequeno pedaço do nome da função, ID e argumentos. Você precisa acumular essas partes e reconstruir o objeto completo da chamada de ferramenta antes de poder executá-la. O streaming de texto comum é mais simples porque cada chunk já é texto completo que você pode exibir imediatamente.

??? question "3. O que é Server-Sent Events (SSE) e por que é usado para streaming de IA em aplicações web?"
    SSE é um padrão web onde o servidor envia um fluxo de eventos através de uma única conexão HTTP, formatado como `data: <conteúdo>\n\n`. É mais simples que WebSockets para streaming unidirecional servidor→cliente. Os navegadores têm suporte nativo à API `EventSource`, e funciona melhor através de proxies e balanceadores de carga do que WebSockets. A maioria das interfaces de chat com IA (ChatGPT, Copilot) usa SSE para respostas em streaming.

---

## Resumo

| Abordagem | Quando usar |
|----------|------------|
| `stream=True` básico | Ferramentas CLI, scripts simples |
| Coletar durante o streaming | Precisa de UX de streaming + texto completo para processamento |
| FastAPI + SSE | Aplicações web, interfaces de chat |
| SK `get_streaming_...` | Agentes SK em produção |
| Mensagens de progresso | Quando chamadas de ferramentas adicionam latência significativa |

---

## Próximos Passos

- **Aprofundamento em chamadas de ferramentas:** → [Lab 018 — Function Calling & Tool Use](lab-018-function-calling.md)
- **Construir uma UI web para seu agente:** → [Lab 041 — Custom GitHub Copilot Extension](lab-041-copilot-extension.md)
- **Streaming em produção com Foundry:** → [Lab 030 — Foundry Agent Service](lab-030-foundry-agent-mcp.md)
