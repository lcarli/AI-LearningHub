---
tags: [semantic-kernel, multi-agent, python, free, github-models, persona-developer, persona-architect]
---
# Lab 034: Multi-Agent Orchestration with Semantic Kernel

<div class="lab-meta">
  <span><strong>Level:</strong> <span class="level-badge level-300">L300</span></span>
  <span><strong>Path:</strong> <a href="../paths/semantic-kernel/">Semantic Kernel</a></span>
  <span><strong>Time:</strong> ~60 min</span>
  <span><strong>💰 Cost:</strong> <span class="level-badge cost-github">GitHub Free</span> — GitHub Models API</span>
</div>
!!! warning "Semantic Kernel -> Microsoft Agent Framework"
    Semantic Kernel is now part of **Microsoft Agent Framework (MAF)**, which unifies SK and AutoGen into a single framework. The concepts in this lab still apply — MAF builds on top of them. See **[Lab 076: Microsoft Agent Framework](lab-076-microsoft-agent-framework.md)** for the migration guide.



## What You'll Learn

- Design a **multi-agent system** with an orchestrator and specialist agents
- Use **SK `AgentGroupChat`** for structured agent-to-agent collaboration
- Create `ProductAgent`, `PolicyAgent`, and `OrderAgent` as specialists
- Route user requests to the right specialist automatically
- Aggregate answers from multiple agents into one coherent response

---

## Introduction

A single agent handling every task quickly becomes unmaintainable. The **multi-agent pattern** splits responsibilities:

- **Orchestrator** — understands user intent and delegates
- **Specialist agents** — deep focus on one domain (products, policy, orders)

Semantic Kernel's `AgentGroupChat` provides the infrastructure for agents to collaborate: taking turns, calling each other's functions, and reaching a coordinated answer.

```
User Query
    │
    ▼
OrchestratorAgent
    ├─→ ProductAgent   (catalog, specs, recommendations)
    ├─→ PolicyAgent    (returns, shipping, warranties)
    └─→ OrderAgent     (order history, status, tracking)
         │
         ▼
    Final Answer
```

---

## Prerequisites

- Python 3.11+
- `pip install semantic-kernel openai`
- `GITHUB_TOKEN` set

---

## Lab Exercise

### Step 1: Install dependencies

```bash
pip install semantic-kernel openai
export GITHUB_TOKEN=your_github_token_here
```

### Step 2: Define agent tools (plugins)

```python
# plugins.py
from semantic_kernel.functions import kernel_function
from typing import Annotated

PRODUCTS = [
    {"name": "TrailBlazer X200", "category": "footwear", "price": 189.99,
     "description": "Waterproof Gore-Tex hiking boot. Vibram outsole. 3-season."},
    {"name": "Summit Pro Tent",   "category": "camping",  "price": 349.00,
     "description": "2-person 4-season tent. DAC aluminum poles. 2.1kg."},
    {"name": "ClimbTech Pro Harness", "category": "climbing", "price": 129.99,
     "description": "CE EN12277. 15kN rated. Dyneema blend."},
    {"name": "OmniPack 45L",     "category": "packs",    "price": 279.99,
     "description": "Technical 45L pack. Hip belt. Hydration sleeve."},
    {"name": "StormShell Jacket", "category": "clothing", "price": 349.00,
     "description": "3-layer Gore-Tex Pro. 20k/20k waterproof."},
]

ORDERS = [
    {"order_id": "ORD-001", "customer": "Alex Chen", "product": "TrailBlazer X200", "status": "delivered", "date": "2024-11-15"},
    {"order_id": "ORD-002", "customer": "Alex Chen", "product": "OmniPack 45L",     "status": "shipped",   "date": "2025-01-10"},
]

POLICIES = {
    "return":   "60-day return window. Unused in original packaging. Worn footwear non-refundable unless defective.",
    "shipping": "Standard $5.99 (3-5 days). Express $14.99 (1-2 days). Free on orders $75+.",
    "warranty": "2-year warranty. Lifetime on climbing gear. Proof of purchase required.",
}

class ProductPlugin:
    @kernel_function(description="Search products by keyword, category, or feature")
    def search_products(
        self,
        query: Annotated[str, "Search term e.g. 'hiking boots' or 'waterproof'"]
    ) -> str:
        q = query.lower()
        matches = [
            p for p in PRODUCTS
            if q in p["name"].lower() or q in p["category"].lower() or q in p["description"].lower()
        ]
        if not matches:
            return f"No products found for '{query}'."
        return "\n".join(
            f"- {p['name']} (${p['price']}): {p['description']}"
            for p in matches
        )

    @kernel_function(description="Get all products in a specific category")
    def get_by_category(
        self,
        category: Annotated[str, "Category name: footwear, camping, climbing, packs, clothing"]
    ) -> str:
        matches = [p for p in PRODUCTS if p["category"].lower() == category.lower()]
        if not matches:
            return f"No products in category '{category}'."
        return "\n".join(f"- {p['name']} (${p['price']})" for p in matches)


class PolicyPlugin:
    @kernel_function(description="Get information about return, shipping, or warranty policy")
    def get_policy(
        self,
        policy_type: Annotated[str, "One of: return, shipping, warranty"]
    ) -> str:
        key = policy_type.lower().strip()
        if key not in POLICIES:
            return f"Unknown policy type '{policy_type}'. Options: return, shipping, warranty."
        return POLICIES[key]


class OrderPlugin:
    @kernel_function(description="Look up order history or status for a customer")
    def get_orders(
        self,
        customer_name: Annotated[str, "Customer's full name"]
    ) -> str:
        matches = [o for o in ORDERS if customer_name.lower() in o["customer"].lower()]
        if not matches:
            return f"No orders found for customer '{customer_name}'."
        return "\n".join(
            f"- {o['order_id']}: {o['product']} — {o['status']} (ordered {o['date']})"
            for o in matches
        )

    @kernel_function(description="Get status of a specific order by order ID")
    def get_order_status(
        self,
        order_id: Annotated[str, "Order ID like ORD-001"]
    ) -> str:
        for o in ORDERS:
            if o["order_id"].upper() == order_id.upper():
                return f"Order {o['order_id']}: {o['product']} is **{o['status']}** (ordered {o['date']})."
        return f"Order '{order_id}' not found."
```

### Step 3: Build the multi-agent system

```python
# multi_agent.py
import asyncio, os
from semantic_kernel import Kernel
from semantic_kernel.agents import ChatCompletionAgent, AgentGroupChat
from semantic_kernel.agents.strategies import TerminationStrategy
from semantic_kernel.connectors.ai.open_ai import OpenAIChatCompletion
from semantic_kernel.contents import ChatMessageContent, AuthorRole
from plugins import ProductPlugin, PolicyPlugin, OrderPlugin


def create_kernel_with_model() -> Kernel:
    """Create a kernel using GitHub Models (OpenAI-compatible)."""
    kernel = Kernel()
    service = OpenAIChatCompletion(
        ai_model_id="gpt-4o-mini",
        api_key=os.environ["GITHUB_TOKEN"],
        base_url="https://models.inference.ai.azure.com",
        service_id="github_models",
    )
    kernel.add_service(service)
    return kernel


class DoneWhenConcluded(TerminationStrategy):
    """End the group chat when the Orchestrator says [DONE]."""
    async def should_agent_terminate(self, agent, history):
        return any("[DONE]" in str(msg.content) for msg in history if msg.role == AuthorRole.ASSISTANT)


async def run_customer_service(user_query: str, customer_name: str = "Alex Chen"):
    product_kernel = create_kernel_with_model()
    product_kernel.add_plugin(ProductPlugin(), "products")
    product_agent = ChatCompletionAgent(
        kernel=product_kernel,
        name="ProductAgent",
        instructions=(
            "You are a product specialist for OutdoorGear Inc. "
            "Use the products plugin to answer questions about catalog items, specs, prices, and recommendations."
        ),
    )

    policy_kernel = create_kernel_with_model()
    policy_kernel.add_plugin(PolicyPlugin(), "policy")
    policy_agent = ChatCompletionAgent(
        kernel=policy_kernel,
        name="PolicyAgent",
        instructions=(
            "You are a policy specialist for OutdoorGear Inc. "
            "Use the policy plugin to answer questions about returns, shipping, and warranties. "
            "Always quote the exact policy text."
        ),
    )

    order_kernel = create_kernel_with_model()
    order_kernel.add_plugin(OrderPlugin(), "orders")
    order_agent = ChatCompletionAgent(
        kernel=order_kernel,
        name="OrderAgent",
        instructions=(
            f"You are an order specialist for OutdoorGear Inc. "
            f"The current customer is: {customer_name}. "
            "Use the orders plugin to look up order history and status."
        ),
    )

    orchestrator_kernel = create_kernel_with_model()
    orchestrator = ChatCompletionAgent(
        kernel=orchestrator_kernel,
        name="Orchestrator",
        instructions=(
            "You are the customer service orchestrator for OutdoorGear Inc. "
            "Coordinate specialist agents to answer customer questions.\n\n"
            "1. Determine which specialists are needed\n"
            "2. Ask them by mentioning: @ProductAgent, @PolicyAgent, @OrderAgent\n"
            "3. Synthesize their answers into a final response\n"
            "4. End your final answer with [DONE]\n\n"
            "Do NOT answer from memory — always delegate to specialists first."
        ),
    )

    chat = AgentGroupChat(
        agents=[orchestrator, product_agent, policy_agent, order_agent],
        termination_strategy=DoneWhenConcluded(agents=[orchestrator], maximum_iterations=10),
    )

    await chat.add_chat_message(ChatMessageContent(role=AuthorRole.USER, content=user_query))

    print(f"\n{'='*60}\nCustomer ({customer_name}): {user_query}\n{'='*60}")
    async for response in chat.invoke():
        agent_name = response.name or "Unknown"
        content = str(response.content).replace("[DONE]", "").strip()
        if content:
            print(f"\n[{agent_name}]\n{content}")
    print(f"\n{'='*60}\n")


async def main():
    queries = [
        ("What waterproof boots do you have, and can I return them if they don't fit?", "Alex Chen"),
        ("What's the status of my order ORD-002?", "Alex Chen"),
        ("I need gear for a winter mountaineering trip — what do you recommend?", "Jordan Kim"),
    ]
    for query, customer in queries:
        await run_customer_service(query, customer)
        await asyncio.sleep(1)

if __name__ == "__main__":
    asyncio.run(main())
```

### Step 4: Run the multi-agent system

```bash
python multi_agent.py
```

Expected output (abbreviated):
```
============================================================
Customer (Alex Chen): What waterproof boots do you have, and can I return them?
============================================================

[Orchestrator]
@ProductAgent find waterproof boots. @PolicyAgent what is our footwear return policy?

[ProductAgent]
- TrailBlazer X200 ($189.99): Waterproof Gore-Tex hiking boot. Vibram outsole. 3-season.

[PolicyAgent]
Return Policy: 60-day return window. Unused in original packaging.
Worn footwear non-refundable unless defective.

[Orchestrator]
We have the **TrailBlazer X200** ($189.99) — a Gore-Tex waterproof hiking boot.
Returns: 60 days from purchase, must be unused. Once worn, non-refundable unless defective. [DONE]
```

---

## Orchestration Patterns Compared

| Pattern | When to use |
|---------|-------------|
| **Sequential** | Steps must happen in order (A → B → C) |
| **Parallel** | Independent tasks that can run simultaneously |
| **AgentGroupChat** | Collaborative, conversational, dynamic routing |
| **Handoff** | One agent passes full context to another |

---

## Next Steps

- **Agent Evaluation:** → [Lab 035 — Evaluate agent quality](lab-035-agent-evaluation.md)
- **Production AutoGen:** → [Lab 040 — Production Multi-Agent with AutoGen](lab-040-autogen-multi-agent.md)
