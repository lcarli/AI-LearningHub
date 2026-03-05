---
tags: [langchain, langgraph, python, free, github-models, agents]
---
# Lab 029 : Bases de LangChain et LangGraph

<div class="lab-meta">
  <span><strong>Niveau :</strong> <span class="level-badge level-200">L200</span></span>
  <span><strong>Parcours :</strong> <a href="../paths/pro-code/">💻 Pro Code</a></span>
  <span><strong>Durée :</strong> ~60 min</span>
  <span><strong>💰 Coût :</strong> <span class="level-badge cost-free">Gratuit</span> — Niveau gratuit GitHub Models</span>
</div>

## Ce que vous apprendrez

- Construire un agent conversationnel avec **LangChain** et une boucle d'appel d'outils
- Modéliser la logique d'agent multi-étapes comme un **graphe d'état LangGraph**
- Comprendre la différence entre les **chaînes** LangChain et les **graphes** LangGraph
- Ajouter un routage conditionnel : quand appeler un outil vs retourner une réponse
- Persister l'état de conversation avec les **checkpointers LangGraph**

---

## Introduction

LangChain est l'un des frameworks open-source les plus populaires pour construire des applications alimentées par des LLM. LangGraph l'étend avec des machines à états explicites — des graphes où les nœuds sont des fonctions et les arêtes sont des transitions.

**Quand utiliser chacun :**

| | LangChain | LangGraph |
|---|---|---|
| Idéal pour | Pipelines linéaires, chaînes RAG, agents simples | Agents multi-étapes complexes, logique de branchement, cycles |
| État | Implicite (passé à travers la chaîne) | Explicite (dictionnaire d'état typé) |
| Boucles | Pas natif | Support natif |
| Visibilité | Journaux de chaîne | Traces d'exécution du graphe |

Dans ce lab, nous construisons le même assistant shopping OutdoorGear de deux manières : d'abord avec LangChain (plus simple), puis avec LangGraph (contrôle plus explicite).

---

## Prérequis

```bash
pip install langchain langchain-openai langgraph
```

Pas besoin d'abonnement Azure — nous utilisons le point de terminaison compatible OpenAI de GitHub Models :

```bash
export GITHUB_TOKEN=<your PAT with models:read scope>
```

---

## Partie 1 : Agent LangChain

### Étape 1 : Outils

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

### Étape 2 : Agent LangChain avec appel d'outils

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

Exécutez-le :
```bash
python langchain_agent.py
```

Vous devriez voir l'agent appeler `search_products`, inspecter un résultat, puis fournir une recommandation.

---

## Partie 2 : Agent LangGraph

LangGraph modélise l'agent comme une machine à états. Cela rend la logique explicite et testable.

### Étape 3 : Définir l'état du graphe

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

### Étape 4 : Définir les nœuds du graphe

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

### Étape 5 : Construire et exécuter le graphe

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

## Partie 3 : Ajouter la mémoire persistante (Checkpointer)

LangGraph peut persister l'état entre les exécutions grâce à un checkpointer — c'est ainsi que vous construisez des agents multi-tours qui se souviennent des conversations :

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

## 🧠 Vérification des connaissances

??? question "1. Quel est le principal avantage de LangGraph par rapport à un simple agent LangChain ?"
    LangGraph utilise une **machine à états explicite** (graphe avec nœuds et arêtes) pour modéliser la logique de l'agent. Cela rend le **branchement, les boucles et le routage conditionnel** natifs — visibles, testables et déboguables. Un agent LangChain masque le flux de contrôle à l'intérieur du framework.

??? question "2. Que fait le réducteur `add_messages` dans l'état LangGraph ?"
    `add_messages` est une **fonction réducteur** qui indique à LangGraph comment mettre à jour le champ `messages` : elle **ajoute** les nouveaux messages au lieu de remplacer la liste entière. Sans elle, chaque retour de nœud écraserait l'historique des messages au lieu de l'enrichir.

??? question "3. Comment le checkpointing LangGraph permet-il les conversations multi-tours ?"
    Un checkpointer **persiste l'état du graphe** (tous les messages) dans un stockage (mémoire, Redis, PostgreSQL) indexé par un `thread_id`. Lorsque vous invoquez l'agent avec le même `thread_id`, LangGraph charge l'état précédent et continue là où il s'était arrêté — l'agent « se souvient » des tours précédents sans que vous ayez à gérer l'historique manuellement.

---

## Résumé

| Concept | LangChain | LangGraph |
|---------|-----------|-----------|
| **Structure** | Chaîne linéaire | Graphe orienté (nœuds + arêtes) |
| **Boucles** | Pas natif | `graph.add_edge("tools", "llm")` |
| **Branchement** | Limité | `add_conditional_edges()` |
| **État** | Implicite | `TypedDict` explicite |
| **Mémoire** | Manuelle | `MemorySaver` / `PostgresSaver` |
| **Débogage** | Journaux de chaîne | Trace d'exécution complète du graphe |

---

## Prochaines étapes

- **Plongée approfondie dans l'appel de fonctions :** → [Lab 018 — Appel de fonctions et utilisation d'outils](lab-018-function-calling.md)
- **Multi-agents avec Semantic Kernel :** → [Lab 034 — Systèmes multi-agents](lab-034-multi-agent-sk.md)
- **Agents AutoGen en production :** → [Lab 040 — Multi-agent en production](lab-040-autogen-multi-agent.md)
