---
tags: [semantic-kernel, multi-agent, python, free, github-models]
---
# Lab 034: Orquestração Multi-Agente com Semantic Kernel

<div class="lab-meta">
  <span><strong>Nível:</strong> <span class="level-badge level-300">L300</span></span>
  <span><strong>Trilha:</strong> <a href="../paths/semantic-kernel/">Semantic Kernel</a></span>
  <span><strong>Tempo:</strong> ~60 min</span>
  <span><strong>💰 Custo:</strong> <span class="level-badge cost-github">GitHub Gratuito</span> — GitHub Models API</span>
</div>
!!! warning "Semantic Kernel -> Microsoft Agent Framework"
    O Semantic Kernel agora faz parte do **Microsoft Agent Framework (MAF)**, que unifica SK e AutoGen em um único framework. Os conceitos neste lab ainda se aplicam — o MAF é construído sobre eles. Veja **[Lab 076: Microsoft Agent Framework](lab-076-microsoft-agent-framework.md)** para o guia de migração.



## O que Você Vai Aprender

- Projetar um **sistema multi-agente** com um orquestrador e agentes especialistas
- Usar o **SK `AgentGroupChat`** para colaboração estruturada entre agentes
- Criar `ProductAgent`, `PolicyAgent` e `OrderAgent` como especialistas
- Rotear solicitações de usuários para o especialista correto automaticamente
- Agregar respostas de múltiplos agentes em uma resposta coerente

---

## Introdução

Um único agente lidando com toda tarefa rapidamente se torna ingerenciável. O **padrão multi-agente** divide responsabilidades:

- **Orquestrador** — entende a intenção do usuário e delega
- **Agentes especialistas** — foco profundo em um domínio (produtos, políticas, pedidos)

O `AgentGroupChat` do Semantic Kernel fornece a infraestrutura para os agentes colaborarem: revezando-se, chamando as funções uns dos outros e chegando a uma resposta coordenada.

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

## Pré-requisitos

- Python 3.11+
- `pip install semantic-kernel openai`
- `GITHUB_TOKEN` configurado

---

## Exercício do Lab

### Passo 1: Instalar dependências

```bash
pip install semantic-kernel openai
export GITHUB_TOKEN=your_github_token_here
```

### Passo 2: Definir ferramentas dos agentes (plugins)

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

### Passo 3: Construir o sistema multi-agente

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

### Passo 4: Executar o sistema multi-agente

```bash
python multi_agent.py
```

Saída esperada (abreviada):
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

## Padrões de Orquestração Comparados

| Padrão | Quando usar |
|--------|-------------|
| **Sequencial** | Os passos devem acontecer em ordem (A → B → C) |
| **Paralelo** | Tarefas independentes que podem ser executadas simultaneamente |
| **AgentGroupChat** | Colaborativo, conversacional, roteamento dinâmico |
| **Handoff** | Um agente passa o contexto completo para outro |

---

## Próximos Passos

- **Avaliação de Agentes:** → [Lab 035 — Avaliar qualidade do agente](lab-035-agent-evaluation.md)
- **AutoGen em Produção:** → [Lab 040 — Production Multi-Agent with AutoGen](lab-040-autogen-multi-agent.md)
