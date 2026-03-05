---
tags: [langchain, langgraph, python, free, github-models, agents]
---
# Lab 029: LangChain & LangGraph Básico

<div class="lab-meta">
  <span><strong>Nível:</strong> <span class="level-badge level-200">L200</span></span>
  <span><strong>Trilha:</strong> <a href="../paths/pro-code/">💻 Pro Code</a></span>
  <span><strong>Tempo:</strong> ~60 min</span>
  <span><strong>💰 Custo:</strong> <span class="level-badge cost-free">Gratuito</span> — GitHub Models nível gratuito</span>
</div>

## O que Você Vai Aprender

- Construir um agente conversacional com **LangChain** e um loop de chamada de ferramentas
- Modelar lógica de agente multi-etapas como um **grafo de estado LangGraph**
- Entender a diferença entre **cadeias** do LangChain e **grafos** do LangGraph
- Adicionar roteamento condicional: quando chamar uma ferramenta vs. retornar uma resposta
- Persistir estado da conversa com **checkpointers do LangGraph**

---

## Introdução

LangChain é um dos frameworks open-source mais populares para construir aplicações alimentadas por LLM. LangGraph o estende com máquinas de estado explícitas — grafos onde nós são funções e arestas são transições.

**Quando usar cada um:**

| | LangChain | LangGraph |
|---|---|---|
| Melhor para | Pipelines lineares, cadeias RAG, agentes simples | Agentes multi-etapas complexos, lógica de ramificação, ciclos |
| Estado | Implícito (passado pela cadeia) | Explícito (dict de estado tipado) |
| Loops | Não nativo | Suporte de primeira classe |
| Visibilidade | Logs da cadeia | Traces de execução do grafo |

Neste lab construímos o mesmo assistente de compras OutdoorGear de duas formas: primeiro com LangChain (mais simples), depois com LangGraph (controle mais explícito).

---

## Pré-requisitos

```bash
pip install langchain langchain-openai langgraph
```

Nenhuma assinatura Azure necessária — usamos o endpoint compatível com OpenAI do GitHub Models:

```bash
export GITHUB_TOKEN=<your PAT with models:read scope>
```

---

## Parte 1: Agente LangChain

### Passo 1: Ferramentas

```python
# tools.py
from langchain_core.tools import tool

PRODUCTS = [
    {"id": "P001", "name": "TrailBlazer Tent 2P",    "category": "Tents",   "price": 249.99},
    {"id": "P002", "name": "Summit Dome 4P",          "category": "Tents",   "price": 549.99},
    {"id": "P003", "name": "TrailBlazer Solo",        "category": "Tents",   "price": 299.99},
    {"id": "P004", "name": "ArcticDown -20°C Bag",    "category": "Bags",    "price": 389.99},
    {"id": "P005", "name": "SummerLight +5°C Bag",    "category": "Bags",    "price": 149.99},
    {"id": "P006", "name": "Osprey Atmos 65L",        "category": "Packs",   "price": 289.99},
    {"id": "P007", "name": "DayHiker 22L",            "category": "Packs",   "price":  89.99},
]

@tool
def search_products(keyword: str, max_price: float = 9999) -> str:
    """Search OutdoorGear products by keyword. Optionally filter by max_price in USD."""
    matches = [
        p for p in PRODUCTS
        if keyword.lower() in p["name"].lower() and p["price"] <= max_price
    ]
    if not matches:
        return f"No products found for '{keyword}'"
    return "\n".join(f"[{p['id']}] {p['name']} — ${p['price']:.2f}" for p in matches)


@tool
def get_product_details(product_id: str) -> str:
    """Get full details for a specific product by ID (e.g. 'P001')."""
    product = next((p for p in PRODUCTS if p["id"].upper() == product_id.upper()), None)
    if not product:
        return f"Product '{product_id}' not found"
    return str(product)


@tool
def calculate_total(product_ids: list[str], quantities: list[int]) -> str:
    """
    Calculate the total price for a list of products and quantities.

    Args:
        product_ids: List of product IDs (e.g. ['P001', 'P006'])
        quantities:  List of quantities, same order as product_ids (e.g. [1, 2])
    """
    total = 0.0
    lines = []
    for pid, qty in zip(product_ids, quantities):
        product = next((p for p in PRODUCTS if p["id"].upper() == pid.upper()), None)
        if product:
            subtotal = product["price"] * qty
            total += subtotal
            lines.append(f"{product['name']} × {qty} = ${subtotal:.2f}")
        else:
            lines.append(f"Unknown product: {pid}")
    lines.append(f"─────────────────")
    lines.append(f"Total: ${total:.2f}")
    return "\n".join(lines)
```

### Passo 2: Agente LangChain com Chamada de Ferramentas

```python
# langchain_agent.py
import os
from langchain_openai import ChatOpenAI
from langchain.agents import AgentExecutor, create_tool_calling_agent
from langchain_core.prompts import ChatPromptTemplate
from tools import search_products, get_product_details, calculate_total

# GitHub Models endpoint
llm = ChatOpenAI(
    model="gpt-4o-mini",
    api_key=os.environ["GITHUB_TOKEN"],
    base_url="https://models.inference.ai.azure.com",
)

tools = [search_products, get_product_details, calculate_total]

prompt = ChatPromptTemplate.from_messages([
    ("system", "You are a helpful OutdoorGear product advisor. "
               "Use the available tools to answer customer questions. "
               "Always check product details before making recommendations."),
    ("placeholder", "{chat_history}"),
    ("human", "{input}"),
    ("placeholder", "{agent_scratchpad}"),
])

agent = create_tool_calling_agent(llm, tools, prompt)
executor = AgentExecutor(agent=agent, tools=tools, verbose=True)

# Try it
result = executor.invoke({
    "input": "I need a lightweight tent for solo hiking under $350. What do you recommend?",
    "chat_history": [],
})
print("\n" + result["output"])
```

Execute:
```bash
python langchain_agent.py
```

You should see the agent call `search_products`, inspect a result, then provide a recommendation.

---

## Parte 2: Agente LangGraph

LangGraph modela o agente como uma máquina de estados. Isso torna a lógica explícita e testável.

### Passo 3: Definir o estado do grafo

```python
# langgraph_agent.py
import os
import json
from typing import Annotated, TypedDict
from langchain_openai import ChatOpenAI
from langchain_core.messages import HumanMessage, ToolMessage, AIMessage, BaseMessage
from langgraph.graph import StateGraph, END
from langgraph.graph.message import add_messages
from tools import search_products, get_product_details, calculate_total

# State: messages list that auto-appends (add_messages reducer)
class AgentState(TypedDict):
    messages: Annotated[list[BaseMessage], add_messages]

tools_list = [search_products, get_product_details, calculate_total]
tools_by_name = {t.name: t for t in tools_list}

llm = ChatOpenAI(
    model="gpt-4o-mini",
    api_key=os.environ["GITHUB_TOKEN"],
    base_url="https://models.inference.ai.azure.com",
).bind_tools(tools_list)
```

### Passo 4: Definir os nós do grafo

```python
# Node 1: Call the LLM
def call_llm(state: AgentState) -> AgentState:
    """Send the current messages to the LLM and append its response."""
    response = llm.invoke(state["messages"])
    return {"messages": [response]}


# Node 2: Execute tool calls
def execute_tools(state: AgentState) -> AgentState:
    """Execute any tool calls in the last LLM message."""
    last_message = state["messages"][-1]
    tool_results = []

    for tool_call in last_message.tool_calls:
        tool = tools_by_name[tool_call["name"]]
        result = tool.invoke(tool_call["args"])
        tool_results.append(
            ToolMessage(content=str(result), tool_call_id=tool_call["id"])
        )

    return {"messages": tool_results}


# Routing: should we call tools or are we done?
def should_call_tools(state: AgentState) -> str:
    """Return 'tools' if the LLM requested tool calls, 'end' otherwise."""
    last_message = state["messages"][-1]
    if hasattr(last_message, "tool_calls") and last_message.tool_calls:
        return "tools"
    return "end"
```

### Passo 5: Construir e executar o grafo

```python
# Build the graph
graph = StateGraph(AgentState)
graph.add_node("llm", call_llm)
graph.add_node("tools", execute_tools)

graph.set_entry_point("llm")
graph.add_conditional_edges("llm", should_call_tools, {"tools": "tools", "end": END})
graph.add_edge("tools", "llm")   # After tools, go back to LLM

agent = graph.compile()

# Run it
initial_state = {
    "messages": [
        HumanMessage(content="Compare the TrailBlazer Tent 2P and TrailBlazer Solo. "
                              "Which should I buy for a 2-week solo thru-hike?")
    ]
}

for step in agent.stream(initial_state, stream_mode="values"):
    last_msg = step["messages"][-1]
    if isinstance(last_msg, AIMessage) and last_msg.content:
        print(f"\n🤖 Agent: {last_msg.content}")
    elif isinstance(last_msg, ToolMessage):
        print(f"\n🔧 Tool result: {last_msg.content[:100]}...")
```

---

## Parte 3: Adicionar Memória Persistente (Checkpointer)

LangGraph pode persistir o estado entre execuções usando um checkpointer — é assim que você constrói agentes multi-turno que lembram conversas:

```python
from langgraph.checkpoint.memory import MemorySaver

# Add memory to the graph
memory = MemorySaver()
agent_with_memory = graph.compile(checkpointer=memory)

# Thread ID ties messages to a specific "conversation"
config = {"configurable": {"thread_id": "customer-session-42"}}

# Turn 1
result = agent_with_memory.invoke(
    {"messages": [HumanMessage(content="What tents do you have?")]},
    config=config,
)
print(result["messages"][-1].content)

# Turn 2 — the agent remembers Turn 1!
result = agent_with_memory.invoke(
    {"messages": [HumanMessage(content="Which is the lightest?")]},
    config=config,
)
print(result["messages"][-1].content)
```

---

## 🧠 Verificação de Conhecimento

??? question "1. Qual é a principal vantagem do LangGraph sobre um agente LangChain simples?"
    LangGraph usa uma **máquina de estados explícita** (grafo com nós e arestas) para modelar a lógica do agente. Isso torna **ramificação, loops e roteamento condicional** cidadãos de primeira classe — visíveis, testáveis e depuráveis. Um agente LangChain esconde o fluxo de controle dentro do framework.

??? question "2. What does the `add_messages` reducer do in LangGraph state?"
    `add_messages` is a **reducer function** that tells LangGraph how to update the `messages` field: it **appends** new messages instead of replacing the whole list. Without it, each node return would overwrite the message history rather than adding to it.

??? question "3. Como o checkpointing do LangGraph habilita conversas multi-turno?"
    A checkpointer **persists the graph state** (all messages) to storage (memory, Redis, PostgreSQL) keyed by a `thread_id`. When you invoke the agent with the same `thread_id`, LangGraph loads the previous state and continues from where it left off — the agent "remembers" prior turns without you managing history manually.

---

## Resumo

| Conceito | LangChain | LangGraph |
|---------|-----------|-----------|
| **Estrutura** | Cadeia linear | Grafo dirigido (nós + arestas) |
| **Loops** | Não nativo | `graph.add_edge("tools", "llm")` |
| **Ramificação** | Limitada | `add_conditional_edges()` |
| **State** | Implicit | Explicit `TypedDict` |
| **Memória** | Manual | `MemorySaver` / `PostgresSaver` |
| **Depuração** | Logs da cadeia | Trace completo de execução do grafo |

---

## Próximos Passos

- **Aprofundamento em chamada de funções:** → [Lab 018 — Function Calling & Tool Use](lab-018-function-calling.md)
- **Multi-agente com Semantic Kernel:** → [Lab 034 — Multi-Agent Systems](lab-034-multi-agent-sk.md)
- **Agentes AutoGen em produção:** → [Lab 040 — Production Multi-Agent](lab-040-autogen-multi-agent.md)
