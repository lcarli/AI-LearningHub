# Lab 017: Structured Output & JSON Mode

<div class="lab-meta">
  <span><strong>Level:</strong> <span class="level-badge level-100">L100</span></span>
  <span><strong>Path:</strong> All paths</span>
  <span><strong>Time:</strong> ~25 min</span>
  <span><strong>💰 Cost:</strong> <span class="level-badge cost-github">GitHub Free</span> — Free GitHub account, no credit card</span>
</div>

!!! info "Tradução em andamento"
    Este lab ainda está sendo traduzido. O conteúdo abaixo está em inglês.



## What You'll Learn

- Why unstructured LLM output is fragile in agent systems
- How to use **JSON mode** to force valid JSON output
- How to define **schemas** with Pydantic (Python) and C# classes
- How to use **structured output** with the OpenAI API
- Practical patterns: extraction, classification, function output

---

## Introduction

In production agent systems, you rarely just display the LLM's text to users. You parse it, store it in databases, pass it to other services, or trigger actions based on it.

The problem: LLMs are chatty. Ask for JSON and you might get:

```
Sure! Here's the JSON you asked for:
```json
{"name": "hiking boots", "price": 129.99}
```
I hope that helps!
```

Now your JSON parser crashes because of the extra text. This is a real problem that structured output solves completely.

---

## Prerequisites Setup

```bash
pip install openai pydantic
```

Set `GITHUB_TOKEN` from [Lab 013](lab-013-github-models.md).

---

## Lab Exercise

### Step 1: The problem — parsing unstructured output

=== "Python"

    ```python
    import os, json
    from openai import OpenAI

    client = OpenAI(
        base_url="https://models.inference.ai.azure.com",
        api_key=os.environ["GITHUB_TOKEN"],
    )

    # BAD approach - asking for JSON in the prompt
    response = client.chat.completions.create(
        model="gpt-4o-mini",
        messages=[{
            "role": "user",
            "content": "Extract the product info as JSON: 'The ProTrek X200 hiking boots cost $189.99 and come in black.'"
        }],
    )

    text = response.choices[0].message.content
    print(text)  # May include "Sure! Here's the JSON: ```json ... ```"

    # This will often FAIL:
    try:
        data = json.loads(text)
    except json.JSONDecodeError:
        print("Parse failed! LLM added extra text.")
    ```

### Step 2: JSON mode — guaranteed valid JSON

JSON mode forces the model to output only valid JSON, nothing else.

=== "Python"

    ```python
    response = client.chat.completions.create(
        model="gpt-4o-mini",
        response_format={"type": "json_object"},  # ← Enable JSON mode
        messages=[
            {
                "role": "system",
                "content": "You are a data extractor. Always respond with valid JSON only."
            },
            {
                "role": "user",
                "content": "Extract product info from: 'The ProTrek X200 hiking boots cost $189.99 and come in black.'"
            }
        ],
    )

    text = response.choices[0].message.content
    data = json.loads(text)  # Always succeeds now
    print(data)
    # {"name": "ProTrek X200", "type": "hiking boots", "price": 189.99, "colors": ["black"]}
    ```

!!! warning "JSON mode requirement"
    When using `json_object` mode, your system or user message **must** mention the word "JSON" — otherwise the API returns an error.

### Step 3: Structured output with Pydantic schema

JSON mode gives you valid JSON, but not necessarily the *shape* you want. **Structured output** with a schema enforces the exact fields and types.

=== "Python"

    ```python
    from pydantic import BaseModel
    from openai import OpenAI
    import os

    client = OpenAI(
        base_url="https://models.inference.ai.azure.com",
        api_key=os.environ["GITHUB_TOKEN"],
    )

    # Define the schema
    class ProductInfo(BaseModel):
        name: str
        category: str
        price: float
        colors: list[str]
        in_stock: bool

    # Parse with structured output
    response = client.beta.chat.completions.parse(
        model="gpt-4o-mini",
        messages=[
            {"role": "system", "content": "Extract product information accurately."},
            {"role": "user", "content": "The ProTrek X200 hiking boots cost $189.99, come in black and brown, and are currently available."},
        ],
        response_format=ProductInfo,  # ← Pass the Pydantic model
    )

    product = response.choices[0].message.parsed  # Already a ProductInfo object!
    print(product.name)      # "ProTrek X200"
    print(product.price)     # 189.99
    print(product.colors)    # ["black", "brown"]
    print(product.in_stock)  # True
    ```

=== "C#"

    ```csharp
    using OpenAI.Chat;
    using System.Text.Json;

    // Define the schema as a C# class
    public class ProductInfo
    {
        public string Name { get; set; } = "";
        public string Category { get; set; } = "";
        public decimal Price { get; set; }
        public List<string> Colors { get; set; } = new();
        public bool InStock { get; set; }
    }

    // Use JSON mode + deserialize
    var client = new ChatClient(
        model: "gpt-4o-mini",
        apiKey: Environment.GetEnvironmentVariable("GITHUB_TOKEN"),
        options: new OpenAIClientOptions { Endpoint = new Uri("https://models.inference.ai.azure.com") }
    );

    var completion = await client.CompleteChatAsync(
        new SystemChatMessage("Extract product information. Respond with JSON only."),
        new UserChatMessage("The ProTrek X200 hiking boots cost $189.99, come in black and brown, and are available.")
    );

    var product = JsonSerializer.Deserialize<ProductInfo>(completion.Value.Content[0].Text);
    Console.WriteLine($"{product.Name}: ${product.Price}");
    ```

### Step 4: Practical patterns

#### Pattern 1 — Classification

```python
from pydantic import BaseModel
from typing import Literal

class SupportTicket(BaseModel):
    category: Literal["billing", "shipping", "returns", "technical", "other"]
    priority: Literal["low", "medium", "high", "urgent"]
    summary: str
    requires_human: bool

response = client.beta.chat.completions.parse(
    model="gpt-4o-mini",
    messages=[
        {"role": "system", "content": "Classify support tickets accurately."},
        {"role": "user", "content": "My order arrived broken and I need a replacement ASAP for my daughter's birthday tomorrow."},
    ],
    response_format=SupportTicket,
)

ticket = response.choices[0].message.parsed
print(f"Category: {ticket.category}")       # "shipping" or "returns"
print(f"Priority: {ticket.priority}")       # "urgent"
print(f"Human needed: {ticket.requires_human}")  # True
```

#### Pattern 2 — Extraction with nested objects

```python
from pydantic import BaseModel

class Address(BaseModel):
    street: str
    city: str
    state: str
    zip_code: str

class OrderDetails(BaseModel):
    order_id: str
    customer_name: str
    shipping_address: Address
    items: list[str]
    total: float

# Extract structured data from unstructured text
text = """
Hi, I'm John Smith, order #ORD-2024-1234.
I ordered a tent and sleeping bag. Total was $289.98.
Ship to 123 Main St, Seattle, WA 98101.
"""
```

#### Pattern 3 — Agent tool output

Use structured output for MCP tool return values to make parsing reliable:

```python
class SearchResult(BaseModel):
    products: list[dict]
    total_found: int
    has_more: bool
    suggested_query: str | None = None

@mcp.tool()
def search_products(query: str) -> dict:
    """Search the product catalog."""
    # ... do the search ...
    result = SearchResult(
        products=found_products,
        total_found=len(all_matches),
        has_more=len(all_matches) > 10,
    )
    return result.model_dump()  # Pydantic → dict → JSON
```

### Step 5: Temperature = 0 for structured tasks

When extracting structured data, always use `temperature=0`:

```python
response = client.beta.chat.completions.parse(
    model="gpt-4o-mini",
    temperature=0,          # ← Deterministic for extraction
    messages=[...],
    response_format=MySchema,
)
```

Extraction is a factual task — you want the same answer every time, not a creative variation.

---

## Summary

| Approach | When to use | Python |
|----------|------------|--------|
| **Prompt-only** | Never for production | ❌ Fragile |
| **JSON mode** | Simple JSON, no strict schema | `response_format={"type": "json_object"}` |
| **Structured output** | Exact schema required | `response_format=MyPydanticModel` |

The golden rule: **any LLM output that your code will parse should use structured output.**

---

## Next Steps

- **Use structured output in an MCP tool:** → [Lab 020 — MCP Server in Python](lab-020-mcp-server-python.md)
- **Use with Semantic Kernel function results:** → [Lab 023 — SK Plugins, Memory & Planners](lab-023-sk-plugins-memory.md)
