---
tags: [python, free, github-models, streaming]
---
# Lab 019: Streaming Responses in Agents

<div class="lab-meta">
  <span><strong>Level:</strong> <span class="level-badge level-100">L100</span></span>
  <span><strong>Path:</strong> <a href="../paths/pro-code/">⚙️ Pro Code Agents</a></span>
  <span><strong>Time:</strong> ~25 min</span>
  <span><strong>💰 Cost:</strong> <span class="level-badge cost-github">GitHub Free</span> — Free GitHub account, no credit card</span>
</div>

## What You'll Learn

- Why streaming matters for AI agent UX
- How to use `stream=True` with the OpenAI Python SDK
- How to handle streamed tool calls (tricky — different from regular streaming)
- How to yield streaming tokens from a FastAPI endpoint
- How to stream from Semantic Kernel

---

## Introduction

Without streaming, users stare at a blank screen for 3–10 seconds while the model generates a long response. With streaming, text appears **token by token** as it's generated — just like ChatGPT.

For agents, streaming is especially important because tool calls can add significant latency. Showing intermediate output ("Searching products... Found 3 results. Generating answer...") makes the wait feel much shorter.

---

## Step 1: Basic Streaming

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

# stream=True returns a generator instead of a complete response
stream = client.chat.completions.create(
    model="gpt-4o-mini",
    messages=[
        {"role": "system", "content": "You are an outdoor gear advisor."},
        {"role": "user", "content": "Explain the three-layer clothing system for outdoor activities in detail."}
    ],
    stream=True,
)

# Iterate over chunks as they arrive
for chunk in stream:
    delta = chunk.choices[0].delta
    if delta.content:
        print(delta.content, end="", flush=True)

print("\n\n✅ Done!")
```

The `flush=True` is critical — without it, Python buffers output and you lose the streaming effect.

---

## Step 2: Collect the Full Response While Streaming

Sometimes you want to show streaming output AND have the full text for further processing:

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

## Step 3: Streaming with Tool Calls

Streaming and tool calling together requires careful handling. The tool call is delivered across multiple chunks:

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

!!! tip "Streaming + tools is complex"
    Most production code uses non-streaming for the tool-calling phase and only streams the final answer generation. That's simpler and usually sufficient.

---

## Step 4: Streaming in a FastAPI Endpoint

This is the pattern for real web applications:

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

Start the server:
```bash
uvicorn main:app --reload
```

Test with curl:
```bash
curl "http://localhost:8000/stream?question=What+tent+is+best+for+winter+camping"
```

Or consume in JavaScript (browser):
```javascript
const source = new EventSource('/stream?question=What+boots+for+hiking%3F');
source.onmessage = (event) => {
    if (event.data === '[DONE]') { source.close(); return; }
    document.getElementById('response').innerText += event.data;
};
```

---

## Step 5: Streaming in Semantic Kernel

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

## Step 6: Show Progress During Tool Calls

For better UX, show users what's happening while tools execute:

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

This pattern is used in production agents: tool calls run non-streamed (for simpler code), and only the final LLM answer is streamed.

---

## 🧠 Knowledge Check

??? question "1. Why is flush=True important when printing streamed tokens?"
    Python buffers stdout by default. Without `flush=True`, text accumulates in the buffer and gets printed all at once at the end — defeating the purpose of streaming. `flush=True` forces the buffer to be written immediately on each `print()` call.

??? question "2. Why does streaming with tool calls require more complex code than basic streaming?"
    Tool call data arrives **across multiple chunks** — each chunk contains a small piece of the function name, ID, and arguments. You must accumulate these pieces and reconstruct the complete tool call object before you can execute it. Regular text streaming is simpler because each chunk is already complete text you can display immediately.

??? question "3. What is Server-Sent Events (SSE) and why is it used for AI streaming in web apps?"
    SSE is a web standard where the server sends a stream of events over a single HTTP connection, formatted as `data: <content>\n\n`. It's simpler than WebSockets for one-way server→client streaming. Browsers have built-in `EventSource` API support, and it works through proxies and load balancers better than WebSockets. Most AI chat interfaces (ChatGPT, Copilot) use SSE for streaming responses.

---

## Summary

| Approach | When to use |
|----------|------------|
| `stream=True` basic | CLI tools, simple scripts |
| Collect while streaming | Need both streaming UX + full text for processing |
| FastAPI + SSE | Web applications, chat interfaces |
| SK `get_streaming_...` | Production SK agents |
| Progress messages | When tool calls add significant latency |

---

## Next Steps

- **Tool calling deep dive:** → [Lab 018 — Function Calling & Tool Use](lab-018-function-calling.md)
- **Build a web UI for your agent:** → [Lab 041 — Custom GitHub Copilot Extension](lab-041-copilot-extension.md)
- **Production streaming with Foundry:** → [Lab 030 — Foundry Agent Service](lab-030-foundry-agent-mcp.md)
