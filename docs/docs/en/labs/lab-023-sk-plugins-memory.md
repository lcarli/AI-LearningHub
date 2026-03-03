---
tags: [semantic-kernel, python, free, github-models]
---
# Lab 023: Semantic Kernel — Plugins, Memory & Planners

<div class="lab-meta">
  <span><strong>Level:</strong> <span class="level-badge level-200">L200</span></span>
  <span><strong>Path:</strong> <a href="../paths/semantic-kernel/">Semantic Kernel</a></span>
  <span><strong>Time:</strong> ~45 min</span>
  <span><strong>💰 Cost:</strong> <span class="level-badge cost-github">GitHub Free</span></span>
</div>

## What You'll Learn

- Create **native function plugins** in Python and C#
- Use **KernelArguments** to pass typed data between plugins
- Add **in-memory vector store** for semantic memory
- Use **auto function calling** to let the LLM orchestrate plugins
- Understand how SK planners work

---

## Introduction

[Lab 014](lab-014-sk-hello-agent.md) built a minimal SK agent. This lab goes deeper: multiple plugins working together, semantic memory, and letting the kernel decide which tools to call.

---

## Prerequisites

=== "Python"
    ```bash
    pip install semantic-kernel openai
    ```

=== "C#"
    ```bash
    dotnet add package Microsoft.SemanticKernel
    dotnet add package Microsoft.SemanticKernel.Connectors.InMemory --prerelease
    ```

Set `GITHUB_TOKEN`.

---

## Lab Exercise

### Step 1: Create a multi-plugin agent

=== "Python"

    ```python
    import os, asyncio
    from semantic_kernel import Kernel
    from semantic_kernel.connectors.ai.open_ai import OpenAIChatCompletion
    from semantic_kernel.functions import kernel_function
    from semantic_kernel.connectors.ai.open_ai import OpenAIChatPromptExecutionSettings
    from semantic_kernel.connectors.ai.function_choice_behavior import FunctionChoiceBehavior

    # --- Plugin 1: Products ---
    class ProductPlugin:
        @kernel_function(description="Search products by keyword")
        def search_products(self, query: str) -> str:
            catalog = [
                {"id": "P001", "name": "TrailBlazer X200", "price": 189.99, "category": "footwear"},
                {"id": "P002", "name": "Summit Pro Tent",  "price": 349.00, "category": "camping"},
                {"id": "P003", "name": "ClimbTech Harness","price": 129.99, "category": "climbing"},
            ]
            results = [p for p in catalog if query.lower() in p["name"].lower() or query.lower() in p["category"].lower()]
            return str(results) if results else "No products found."

        @kernel_function(description="Get the current shopping cart total")
        def get_cart_total(self) -> str:
            return "Current cart: 1x TrailBlazer X200 ($189.99). Total: $189.99"

    # --- Plugin 2: Weather (for trip planning) ---
    class WeatherPlugin:
        @kernel_function(description="Get trail conditions for a location")
        def get_trail_conditions(self, location: str) -> str:
            conditions = {
                "olympic": "Muddy, 45°F, light rain. Waterproof boots recommended.",
                "rainier": "Snow above 5000ft. Crampons required above treeline.",
                "cascades": "Clear, 62°F. Ideal conditions.",
            }
            for key, val in conditions.items():
                if key in location.lower():
                    return val
            return f"No trail data for {location}. Check local ranger station."

    # --- Plugin 3: Math/Utilities ---
    class UtilityPlugin:
        @kernel_function(description="Calculate total price with tax")
        def calculate_with_tax(self, subtotal: float, tax_rate: float = 0.098) -> str:
            total = subtotal * (1 + tax_rate)
            return f"${subtotal:.2f} + {tax_rate*100:.1f}% tax = ${total:.2f}"

    async def main():
        kernel = Kernel()
        kernel.add_service(OpenAIChatCompletion(
            ai_model_id="gpt-4o-mini",
            api_key=os.environ["GITHUB_TOKEN"],
            base_url="https://models.inference.ai.azure.com/openai",
        ))

        # Register all plugins
        kernel.add_plugin(ProductPlugin(), plugin_name="Products")
        kernel.add_plugin(WeatherPlugin(), plugin_name="Weather")
        kernel.add_plugin(UtilityPlugin(), plugin_name="Utils")

        # Auto function calling — kernel decides which tools to use
        settings = OpenAIChatPromptExecutionSettings(
            function_choice_behavior=FunctionChoiceBehavior.Auto()
        )

        questions = [
            "What camping gear do you have, and what's the total with Washington state tax?",
            "I'm planning a hike on Mount Rainier — what gear and conditions should I expect?",
        ]

        for question in questions:
            print(f"\n❓ {question}")
            result = await kernel.invoke_prompt(
                question,
                execution_settings=settings,
            )
            print(f"💬 {result}")

    asyncio.run(main())
    ```

### Step 2: Add semantic memory

Semantic memory lets you store facts and retrieve them by meaning (not keyword).

=== "Python"

    ```python
    import os, asyncio
    from semantic_kernel import Kernel
    from semantic_kernel.connectors.ai.open_ai import OpenAIChatCompletion, OpenAITextEmbedding
    from semantic_kernel.memory import SemanticTextMemory, VolatileMemoryStore

    async def demo_memory():
        kernel = Kernel()
        kernel.add_service(OpenAIChatCompletion(
            ai_model_id="gpt-4o-mini",
            api_key=os.environ["GITHUB_TOKEN"],
            base_url="https://models.inference.ai.azure.com/openai",
        ))
        embedding_service = OpenAITextEmbedding(
            ai_model_id="text-embedding-3-small",
            api_key=os.environ["GITHUB_TOKEN"],
            base_url="https://models.inference.ai.azure.com/openai",
        )

        memory = SemanticTextMemory(
            storage=VolatileMemoryStore(),
            embeddings_generator=embedding_service,
        )

        # Store facts
        facts = [
            ("boot-care",    "Clean boots after each use. Apply waterproofing spray every 3 months."),
            ("tent-setup",   "Always stake tent before raising poles in wind."),
            ("harness-check","Inspect harness stitching and buckles before every climb."),
            ("layering",     "Base layer wicks moisture. Mid layer insulates. Shell blocks wind/rain."),
        ]

        collection = "outdoor-tips"
        for key, fact in facts:
            await memory.save_information(collection, id=key, text=fact)

        # Retrieve by meaning
        queries = ["how do I maintain my footwear?", "safety check before climbing"]
        for q in queries:
            results = await memory.search(collection, q, limit=2, min_relevance_score=0.7)
            print(f"\n🔍 '{q}'")
            for r in results:
                print(f"  [{r.relevance:.2f}] {r.text}")

    asyncio.run(demo_memory())
    ```

### Step 3: Combining plugins with memory

```python
from semantic_kernel.core_plugins.text_memory_plugin import TextMemoryPlugin

async def agent_with_memory():
    kernel = Kernel()
    # ... (add services as above) ...

    memory = SemanticTextMemory(
        storage=VolatileMemoryStore(),
        embeddings_generator=embedding_service,
    )

    # TextMemoryPlugin exposes memory as a kernel function
    kernel.add_plugin(TextMemoryPlugin(memory), plugin_name="Memory")
    kernel.add_plugin(ProductPlugin(), plugin_name="Products")

    # Now the agent can use memory AND product search together
    settings = OpenAIChatPromptExecutionSettings(
        function_choice_behavior=FunctionChoiceBehavior.Auto()
    )

    result = await kernel.invoke_prompt(
        "I'm going hiking in wet weather — what should I remember about gear maintenance?",
        execution_settings=settings,
    )
    print(result)
```

### Step 4: Understanding planners

SK planners decompose a goal into steps. The modern approach is **auto function calling** (as used above) — the LLM generates a plan and executes it in one loop.

For explainability, you can log each function call:

```python
from semantic_kernel.filters import FunctionInvocationContext

async def log_function_calls(context: FunctionInvocationContext, next):
    print(f"  📞 Calling: {context.function.plugin_name}.{context.function.name}")
    print(f"     Args: {context.arguments}")
    await next(context)
    print(f"     Result: {str(context.result)[:100]}")

kernel.add_filter("function_invocation", log_function_calls)
```

---

## Key Concepts Summary

| Concept | What it does |
|---------|-------------|
| **Plugin** | Groups related `@kernel_function` methods |
| **KernelArguments** | Typed dict passed between functions |
| **Auto Function Calling** | LLM decides which plugins to call |
| **Semantic Memory** | Vector store for meaning-based retrieval |
| **TextMemoryPlugin** | Bridges memory store into the plugin system |
| **Filter** | Middleware — log, auth, or modify function calls |

---

---

## 🐛 Bug-Fix Exercise: Fix the Broken SK Plugin

This lab includes a deliberately broken Semantic Kernel plugin. Find and fix 3 bugs!

```
lab-023/
└── broken_plugin.py    ← 3 intentional bugs to find and fix
```

**Setup:**
```bash
pip install semantic-kernel openai

# Run the test suite to see which tests fail
python lab-023/broken_plugin.py
```

**The 3 bugs:**

| # | Function | Symptom | Type |
|---|----------|---------|------|
| 1 | `search_products` | SK doesn't discover the function | Missing `@kernel_function` decorator |
| 2 | `get_cart_total` | Returns `$2.00` instead of `$339.98` | Accumulates quantity not price |
| 3 | `calculate_price_with_tax` | Returns `$291.59` instead of `$269.99` | Tax applied twice |

**Verify your fixes:** The built-in test runner checks each function:
```bash
python lab-023/broken_plugin.py
# Expected output:
# ✅ Passed — found 3 tents
# ✅ Passed — cart total = $339.98
# ✅ Passed — price with tax = $269.99
# 🎉 All tests passed! Your plugin is bug-free.
```

---

## 🧠 Knowledge Check

??? question "**Q1 (Run the Lab):** After fixing bug #2, what does `get_cart_total()` return when the cart contains P001 (×1) at $249.99 and P007 (×1) at $89.99?"

    Fix bug #2 in `broken_plugin.py` and run it, or calculate manually: P001 price × 1 + P007 price × 1.

    ??? success "✅ Reveal Answer"
        **$339.98**

        The cart contains 1× P001 (TrailBlazer Tent 2P, $249.99) and 1× P007 (DayHiker 22L, $89.99). `total = 249.99 + 89.99 = $339.98`. Bug #2 was accumulating the item *quantity* instead of `price * quantity`, so single-item carts returned the quantity number (e.g., `$1.00`, `$2.00`) instead of the price.

??? question "**Q2 (Run the Lab):** After fixing ALL 3 bugs, run `python lab-023/broken_plugin.py`. How many SK functions does the test runner discover in the OutdoorGearPlugin?"

    After all fixes, run the script. Look for the "SK discovers N functions" line in the output.

    ??? success "✅ Reveal Answer"
        **3 functions: `search_products`, `get_cart_total`, and `calculate_price_with_tax`**

        Before fixing bug #1 (missing `@kernel_function` decorator), SK could only discover 2 functions. After adding the decorator back to `search_products`, all 3 are visible to the SK planner. This is why decorators matter — without `@kernel_function`, SK simply ignores the function.

??? question "**Q3 (Multiple Choice):** Bug #3 caused `calculate_price_with_tax(249.99, tax_rate=0.08)` to return ~$291.59 instead of $269.99. What was the root cause?"

    - A) The base price was doubled before tax was applied
    - B) Tax was applied to the result of a previous tax calculation (applied twice)
    - C) The function used the wrong tax rate variable
    - D) The tax was subtracted instead of added

    ??? success "✅ Reveal Answer"
        **Correct: B — Tax was applied twice**

        The buggy code first computed `price_with_tax = price * (1 + tax_rate)` → $269.99, then applied tax *again* on that result: `$269.99 * 1.08 = $291.59`. The fix: compute and return in a single step — `return round(price * (1 + tax_rate), 2)`.

---

## Next Steps

- **Multi-agent orchestration with SK:** → [Lab 034 — SK Multi-Agent Systems](lab-034-multi-agent-sk.md)
- **RAG pipeline with SK:** → [Lab 022 — RAG with pgvector](lab-022-rag-github-models-pgvector.md)
