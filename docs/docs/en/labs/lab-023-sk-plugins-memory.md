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

## Next Steps

- **Multi-agent orchestration with SK:** → [Lab 034 — SK Multi-Agent Systems](lab-034-multi-agent-sk.md)
- **RAG pipeline with SK:** → [Lab 022 — RAG with pgvector](lab-022-rag-github-models-pgvector.md)
