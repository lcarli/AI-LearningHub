---
tags: [python, free, github-models, tool-calling, function-calling]
---
# Lab 018: Function Calling & Tool Use

<div class="lab-meta">
  <span><strong>Level:</strong> <span class="level-badge level-100">L100</span></span>
  <span><strong>Path:</strong> <a href="../paths/pro-code/">⚙️ Pro Code Agents</a> · <a href="../paths/semantic-kernel/">🧠 Semantic Kernel</a></span>
  <span><strong>Time:</strong> ~35 min</span>
  <span><strong>💰 Cost:</strong> <span class="level-badge cost-github">GitHub Free</span> — Free GitHub account, no credit card</span>
</div>

!!! info "Tradução em andamento"
    Este lab ainda está sendo traduzido. O conteúdo abaixo está em inglês.



## What You'll Learn

- What function calling (tool use) is and how it works at the API level
- How to define tools that the LLM can call
- How to **parse and execute tool calls** from the model's response
- How to implement a **tool execution loop** (the agent loop)
- Common patterns: parallel tools, required tools, tool error handling
- The difference between function calling and Semantic Kernel plugins

---

## Introduction

**Function calling** (also called "tool use") is the mechanism that transforms an LLM from a text generator into an agent. Instead of just producing text, the model can say: "I need to call `get_weather("Seattle")` before I can answer."

Your code then executes that function, returns the result, and the model uses it to generate a grounded answer.

This is the foundation of every AI agent:

![Agent Tool-Calling Loop](../../assets/diagrams/agent-tool-loop.svg)

---

## How Function Calling Works

### 1. You define tools as JSON schemas

```python
tools = [
    {
        "type": "function",
        "function": {
            "name": "search_products",
            "description": "Search OutdoorGear products by criteria",
            "parameters": {
                "type": "object",
                "properties": {
                    "category": {
                        "type": "string",
                        "description": "Product category (e.g., 'tent', 'sleeping bag', 'backpack')"
                    },
                    "max_price": {
                        "type": "number",
                        "description": "Maximum price in USD"
                    },
                    "in_stock": {
                        "type": "boolean",
                        "description": "If true, only return in-stock items"
                    }
                },
                "required": ["category"]
            }
        }
    }
]
```

### 2. The LLM responds with a tool call (not text)

```json
{
  "role": "assistant",
  "tool_calls": [
    {
      "id": "call_abc123",
      "type": "function",
      "function": {
        "name": "search_products",
        "arguments": "{\"category\": \"tent\", \"max_price\": 200}"
      }
    }
  ]
}
```

### 3. You execute the function and return the result

```python
result = search_products(category="tent", max_price=200)
# Add result to messages as a "tool" role message
```

### 4. The LLM generates the final answer using the tool result

---

## Step 1: Set Up

```bash
pip install openai
export GITHUB_TOKEN=your_github_token
```

---

## Step 2: Define Your Tool Functions

```python
import json
from typing import Optional

# Simulated OutdoorGear product database
PRODUCTS = [
    {"id": "P001", "name": "TrailBlazer Tent 2P", "category": "tent", "price": 189.99, "in_stock": True, "weight_kg": 1.8},
    {"id": "P002", "name": "Summit Dome 4P",      "category": "tent", "price": 349.99, "in_stock": True, "weight_kg": 3.2},
    {"id": "P003", "name": "UltraLight Solo",      "category": "tent", "price": 249.99, "in_stock": False, "weight_kg": 0.9},
    {"id": "P004", "name": "ArcticDown -20°C",     "category": "sleeping bag", "price": 299.99, "in_stock": True, "weight_kg": 1.5},
    {"id": "P005", "name": "ThreeSeasons 0°C",     "category": "sleeping bag", "price": 149.99, "in_stock": True, "weight_kg": 1.1},
    {"id": "P006", "name": "Osprey Atmos 65L",     "category": "backpack",     "price": 279.99, "in_stock": True, "weight_kg": 2.1},
    {"id": "P007", "name": "DayHiker 22L",          "category": "backpack",     "price": 89.99,  "in_stock": True, "weight_kg": 0.8},
]


def search_products(category: str, max_price: Optional[float] = None, in_stock: Optional[bool] = None) -> list:
    """Search products by category, price, and availability."""
    results = [p for p in PRODUCTS if category.lower() in p["category"].lower()]
    if max_price is not None:
        results = [p for p in results if p["price"] <= max_price]
    if in_stock is not None:
        results = [p for p in results if p["in_stock"] == in_stock]
    return results


def get_product_details(product_id: str) -> dict:
    """Get full details for a specific product by ID."""
    for product in PRODUCTS:
        if product["id"] == product_id:
            return product
    return {"error": f"Product {product_id} not found"}


def calculate_total(product_ids: list, discount_percent: float = 0) -> dict:
    """Calculate total price for a list of products with optional discount."""
    total = 0.0
    items = []
    for pid in product_ids:
        product = get_product_details(pid)
        if "error" not in product:
            items.append({"name": product["name"], "price": product["price"]})
            total += product["price"]
    discount = total * (discount_percent / 100)
    return {
        "items": items,
        "subtotal": round(total, 2),
        "discount": round(discount, 2),
        "total": round(total - discount, 2)
    }
```

---

## Step 3: Define Tool Schemas

```python
TOOLS = [
    {
        "type": "function",
        "function": {
            "name": "search_products",
            "description": "Search OutdoorGear products by category, price, and availability.",
            "parameters": {
                "type": "object",
                "properties": {
                    "category": {
                        "type": "string",
                        "description": "Product category: 'tent', 'sleeping bag', or 'backpack'"
                    },
                    "max_price": {
                        "type": "number",
                        "description": "Maximum price in USD. Omit if no price limit."
                    },
                    "in_stock": {
                        "type": "boolean",
                        "description": "Set to true to only return products currently in stock."
                    }
                },
                "required": ["category"]
            }
        }
    },
    {
        "type": "function",
        "function": {
            "name": "get_product_details",
            "description": "Get full details (price, weight, stock) for a specific product by its ID.",
            "parameters": {
                "type": "object",
                "properties": {
                    "product_id": {
                        "type": "string",
                        "description": "The product ID, e.g. 'P001'"
                    }
                },
                "required": ["product_id"]
            }
        }
    },
    {
        "type": "function",
        "function": {
            "name": "calculate_total",
            "description": "Calculate the total price for a list of products, with optional discount.",
            "parameters": {
                "type": "object",
                "properties": {
                    "product_ids": {
                        "type": "array",
                        "items": {"type": "string"},
                        "description": "List of product IDs to include in the total"
                    },
                    "discount_percent": {
                        "type": "number",
                        "description": "Discount percentage to apply (0-100). Default: 0"
                    }
                },
                "required": ["product_ids"]
            }
        }
    }
]
```

---

## Step 4: The Tool Execution Loop

This is the core of every function-calling agent:

```python
import os
import json
from openai import OpenAI

client = OpenAI(
    base_url="https://models.inference.ai.azure.com",
    api_key=os.environ["GITHUB_TOKEN"],
)

# Map function names to actual Python functions
TOOL_FUNCTIONS = {
    "search_products": search_products,
    "get_product_details": get_product_details,
    "calculate_total": calculate_total,
}


def run_agent(user_message: str) -> str:
    """Run the agent loop: chat → tool calls → results → final answer."""
    messages = [
        {
            "role": "system",
            "content": (
                "You are a helpful shopping assistant for OutdoorGear Inc. "
                "Use the provided tools to answer questions about products. "
                "Never invent product data — always use tool results."
            )
        },
        {"role": "user", "content": user_message}
    ]

    while True:
        # Call the LLM
        response = client.chat.completions.create(
            model="gpt-4o-mini",
            messages=messages,
            tools=TOOLS,
            tool_choice="auto",  # LLM decides whether to call a tool
        )

        message = response.choices[0].message
        messages.append(message)  # always append LLM's response to history

        # Check if the LLM wants to call a tool
        if response.choices[0].finish_reason == "tool_calls":
            # Execute each requested tool
            for tool_call in message.tool_calls:
                func_name = tool_call.function.name
                func_args = json.loads(tool_call.function.arguments)

                print(f"  🔧 Calling: {func_name}({func_args})")

                # Execute the function
                if func_name in TOOL_FUNCTIONS:
                    result = TOOL_FUNCTIONS[func_name](**func_args)
                else:
                    result = {"error": f"Unknown function: {func_name}"}

                # Add tool result to messages
                messages.append({
                    "role": "tool",
                    "tool_call_id": tool_call.id,
                    "content": json.dumps(result),
                })
        else:
            # No more tool calls — return the final answer
            return message.content


# Test it!
if __name__ == "__main__":
    questions = [
        "What tents do you have under $250 that are in stock?",
        "Show me the details for product P004 and calculate what it costs with a 10% discount.",
        "I need a lightweight tent and a sleeping bag for 0°C camping. What would be the total cost?",
    ]

    for q in questions:
        print(f"\n{'='*60}")
        print(f"User: {q}")
        print(f"{'='*60}")
        answer = run_agent(q)
        print(f"Agent: {answer}")
```

---

## Step 5: Parallel Tool Calls

The LLM can request multiple tool calls in a single response. Handle them all before returning:

```python
# The loop above already handles this — message.tool_calls is a list
# When LLM calls two tools at once, you'll see:
# 🔧 Calling: search_products({'category': 'tent'})
# 🔧 Calling: search_products({'category': 'sleeping bag'})
# (both in the same iteration)
```

Try asking: *"Compare all tents and sleeping bags under $300"* — you'll see two parallel tool calls.

---

## Step 6: Controlling Tool Choice

```python
# Auto (default): LLM decides whether and which tool to call
tool_choice="auto"

# Required: LLM MUST call at least one tool
tool_choice="required"

# Force a specific tool:
tool_choice={"type": "function", "function": {"name": "search_products"}}

# No tools (force text response):
tool_choice="none"
```

---

## Step 7: 🧪 Interactive Challenge — Fix the Broken Tool Definition

The schema below has **3 bugs** that will cause the tool to fail or behave incorrectly. Find and fix them:

```python
# BROKEN — find the 3 bugs
broken_tool = {
    "type": "functions",                    # Bug 1: wrong type
    "function": {
        "name": "get_inventory",
        "description": "",                  # Bug 2: empty description
        "parameters": {
            "type": "object",
            "properties": {
                "warehouse_id": {
                    "type": "int",          # Bug 3: wrong JSON Schema type
                    "description": "Warehouse identifier"
                }
            }
            # Missing "required" key — also a bug (but not counted)
        }
    }
}
```

??? question "Show the fixes"
    **Bug 1:** `"type": "functions"` → should be `"type": "function"` (singular)

    **Bug 2:** Empty description — the LLM uses descriptions to decide when to call a tool. Without it, the LLM won't know what the tool does and may never call it (or call it inappropriately).

    **Bug 3:** `"type": "int"` → should be `"type": "integer"` — JSON Schema uses `integer`, not `int`.

    **Bonus bug:** The `required` key is missing. Add `"required": ["warehouse_id"]` to ensure the LLM always passes a warehouse ID.

---

## Function Calling vs. Semantic Kernel Plugins

| | Direct Function Calling | Semantic Kernel Plugin |
|--|------------------------|------------------------|
| **Level** | Low-level API | High-level abstraction |
| **Schema** | You write JSON manually | Inferred from Python type hints |
| **Languages** | Any OpenAI-compatible client | Python, C#, Java |
| **Flexibility** | Full control | Less boilerplate |
| **When to use** | Learning, custom control | Production SK agents |

In practice, SK plugins **generate the JSON schema automatically** from your Python function signatures and docstrings. Under the hood, it's the same API call.

---

## 🧠 Knowledge Check

??? question "**Q1 (Multiple Choice):** When the LLM returns `finish_reason='tool_calls'`, what should your agent loop do next?"

    - A) Return the partial answer to the user and wait for confirmation
    - B) Execute the requested function(s), add results as `role: tool` messages, then call the LLM again
    - C) Discard the response and retry with a different prompt
    - D) Switch to a different model that supports the tool

    ??? success "✅ Reveal Answer"
        **Correct: B**

        `finish_reason='tool_calls'` means the LLM needs external data before it can answer. Your loop must: (1) read `response.choices[0].message.tool_calls`, (2) call each requested function with the provided arguments, (3) add the LLM's message AND tool results to history with `role: tool`, then (4) call the LLM again. Repeat until `finish_reason == 'stop'`.

??? question "**Q2 (Run the Lab):** Using the `search_products` function defined in Step 2, how many tents are currently **in stock**?"

    Run the search manually or trace through the product list in Step 2. Count tents where `in_stock == True`.

    ??? success "✅ Reveal Answer"
        **2 tents are in stock: P001 (TrailBlazer Tent 2P, $189.99) and P002 (Summit Dome 4P, $349.99)**

        P003 (UltraLight Solo) is marked `"in_stock": False`. So `search_products("tent", in_stock=True)` returns exactly 2 items.

??? question "**Q3 (Run the Lab):** What does `calculate_total(["P001", "P007"])` return as the `total` field? (No discount applied)"

    Look up the prices for P001 and P007 in the PRODUCTS list and add them together.

    ??? success "✅ Reveal Answer"
        **$279.98**

        P001 (TrailBlazer Tent 2P) = $189.99 + P007 (DayHiker 22L) = $89.99 = **$279.98**. The function applies no discount when `discount_percent=0`, so `total == subtotal == 279.98`.

---

## Summary

| Concept | Key takeaway |
|---------|-------------|
| **Tool schema** | JSON object with `name`, `description`, and `parameters` |
| **finish_reason** | `"tool_calls"` = LLM wants to call a function; `"stop"` = final answer |
| **Tool result** | Added as `role: "tool"` message with matching `tool_call_id` |
| **Agent loop** | Keep calling LLM until `finish_reason == "stop"` |
| **Parallel tools** | One response can contain multiple tool calls — handle them all |

---

## Next Steps

- **Higher-level abstraction:** → [Lab 014 — SK Hello Agent](lab-014-sk-hello-agent.md) — SK manages the loop automatically
- **Build an MCP server:** → [Lab 020 — MCP Server in Python](lab-020-mcp-server-python.md) — tools exposed via standard protocol
- **Streaming with tools:** → [Lab 019 — Streaming Responses](lab-019-streaming-responses.md)
