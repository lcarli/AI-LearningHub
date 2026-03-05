---
tags: [memory, python, free, github-models]
---
# Lab 027: Agent Memory Patterns

<div class="lab-meta">
  <span><strong>Nível:</strong> <span class="level-badge level-200">L200</span></span>
  <span><strong>Trilha:</strong> <a href="../paths/pro-code/">Pro Code</a> / <a href="../paths/semantic-kernel/">SK</a></span>
  <span><strong>Tempo:</strong> ~35 min</span>
  <span><strong>💰 Custo:</strong> <span class="level-badge cost-free">Gratuito (local)</span></span>
</div>

## O que Você Vai Aprender

- Os **4 tipos de memória de agente** e quando usar cada um
- **Memória em contexto** (gerenciamento do histórico de conversas)
- **Memória externa** (vector store + SQLite para dados estruturados)
- **Memória episódica** (o que aconteceu em sessões anteriores)
- Construindo um **agente com memória** que lembra as preferências do usuário

---

## Introdução

Sem memória, toda conversa com o agente começa do zero. Um agente de atendimento ao cliente que esquece o nome do cliente no meio da conversa, ou um assistente que não consegue lembrar o que você decidiu na semana passada, cria uma experiência frustrante.

Os quatro tipos de memória:

| Tipo | Armazenamento | Duração | Exemplo |
|------|---------------|---------|---------|
| **Em contexto** | Janela de contexto do LLM | Requisição única | Histórico de conversas |
| **Semântica externa** | Banco de dados vetorial | Persistente | Tickets de suporte anteriores |
| **Estruturada externa** | Banco de dados SQL | Persistente | Preferências do usuário, histórico de pedidos |
| **Episódica** | Chave-valor / arquivo | Sessão ou persistente | "Na última sessão discutimos X" |

---

## Pré-requisitos

- Python 3.11+
- `pip install openai chromadb`
- `GITHUB_TOKEN` set

!!! tip "Dados de exemplo incluídos"
    This lab uses `orders.csv` and `products.csv` from the repo.
    ```bash
    curl -O https://raw.githubusercontent.com/lcarli/AI-LearningHub/main/data/orders.csv
    curl -O https://raw.githubusercontent.com/lcarli/AI-LearningHub/main/data/products.csv
    ```

---

## Exercício do Lab

### Passo 1: Memória em contexto (histórico de conversas)

A memória mais simples — apenas mantenha o histórico de mensagens. O desafio: janelas de contexto têm limites.

```python
import os
from openai import OpenAI

client = OpenAI(
    base_url="https://models.inference.ai.azure.com",
    api_key=os.environ["GITHUB_TOKEN"],
)

class ConversationAgent:
    def __init__(self, system_prompt: str, max_history: int = 20):
        self.system_prompt = system_prompt
        self.max_history = max_history
        self.history: list[dict] = []

    def chat(self, user_message: str) -> str:
        self.history.append({"role": "user", "content": user_message})

        # Trim history to avoid exceeding context window
        recent = self.history[-self.max_history:]

        messages = [{"role": "system", "content": self.system_prompt}] + recent

        response = client.chat.completions.create(
            model="gpt-4o-mini",
            messages=messages,
        )
        reply = response.choices[0].message.content
        self.history.append({"role": "assistant", "content": reply})
        return reply

    def summarize_history(self) -> str:
        """Compress old history into a summary to save context."""
        if len(self.history) < 10:
            return ""

        old_messages = self.history[:-6]  # everything except last 3 exchanges
        summary_response = client.chat.completions.create(
            model="gpt-4o-mini",
            messages=[
                {"role": "system", "content": "Summarize this conversation in 3-5 bullet points, focusing on key decisions and facts."},
                {"role": "user", "content": str(old_messages)}
            ]
        )
        summary = summary_response.choices[0].message.content

        # Replace old history with summary
        self.history = [
            {"role": "system", "content": f"[Conversation summary]\n{summary}"}
        ] + self.history[-6:]

        return summary

# Test
agent = ConversationAgent("You are a helpful outdoor gear shopping assistant.")
print(agent.chat("Hi, I'm Alex. I'm looking for hiking gear."))
print(agent.chat("I have a $300 budget and I'm planning a 3-day trip."))
print(agent.chat("What's my name and what did I say my budget was?"))  # Tests memory
```

### Passo 2: Memória estruturada com SQLite

Para fatos que precisam de precisão (preferências, pedidos, configurações), use um banco de dados, não a janela de contexto.

```python
import sqlite3, json
from datetime import datetime

class UserMemoryStore:
    def __init__(self, db_path: str = "agent_memory.db"):
        self.conn = sqlite3.connect(db_path)
        self._init_db()

    def _init_db(self):
        self.conn.executescript("""
            CREATE TABLE IF NOT EXISTS user_preferences (
                user_id  TEXT NOT NULL,
                key      TEXT NOT NULL,
                value    TEXT NOT NULL,
                updated  TEXT NOT NULL,
                PRIMARY KEY (user_id, key)
            );
            CREATE TABLE IF NOT EXISTS user_sessions (
                id         INTEGER PRIMARY KEY AUTOINCREMENT,
                user_id    TEXT NOT NULL,
                summary    TEXT NOT NULL,
                timestamp  TEXT NOT NULL
            );
        """)
        self.conn.commit()

    def set_preference(self, user_id: str, key: str, value):
        self.conn.execute(
            "INSERT OR REPLACE INTO user_preferences VALUES (?, ?, ?, ?)",
            (user_id, key, json.dumps(value), datetime.now().isoformat())
        )
        self.conn.commit()

    def get_preferences(self, user_id: str) -> dict:
        rows = self.conn.execute(
            "SELECT key, value FROM user_preferences WHERE user_id = ?", (user_id,)
        ).fetchall()
        return {k: json.loads(v) for k, v in rows}

    def save_session(self, user_id: str, summary: str):
        self.conn.execute(
            "INSERT INTO user_sessions (user_id, summary, timestamp) VALUES (?, ?, ?)",
            (user_id, summary, datetime.now().isoformat())
        )
        self.conn.commit()

    def get_recent_sessions(self, user_id: str, limit: int = 3) -> list[str]:
        rows = self.conn.execute(
            "SELECT summary FROM user_sessions WHERE user_id = ? ORDER BY timestamp DESC LIMIT ?",
            (user_id, limit)
        ).fetchall()
        return [r[0] for r in rows]

# Test
store = UserMemoryStore()
store.set_preference("alex-001", "budget", 300)
store.set_preference("alex-001", "activity", "hiking")
store.set_preference("alex-001", "shoe_size", 10.5)

prefs = store.get_preferences("alex-001")
print(f"Alex's preferences: {prefs}")
```

### Passo 3: Memória episódica semântica com ChromaDB

ChromaDB é um banco de dados vetorial gratuito e local — sem necessidade de Docker.

```python
import chromadb
from openai import OpenAI
import os

client = OpenAI(
    base_url="https://models.inference.ai.azure.com",
    api_key=os.environ["GITHUB_TOKEN"],
)

chroma = chromadb.PersistentClient(path="./agent_chroma_memory")
episodes = chroma.get_or_create_collection("episodes")

def embed(text: str) -> list[float]:
    return client.embeddings.create(
        model="text-embedding-3-small", input=text
    ).data[0].embedding

def remember_episode(user_id: str, session_id: str, summary: str):
    """Store a session summary as a searchable memory."""
    episodes.add(
        ids=[f"{user_id}-{session_id}"],
        embeddings=[embed(summary)],
        documents=[summary],
        metadatas=[{"user_id": user_id, "session_id": session_id}]
    )

def recall_relevant(user_id: str, query: str, top_k: int = 3) -> list[str]:
    """Find past sessions relevant to current query."""
    results = episodes.query(
        query_embeddings=[embed(query)],
        n_results=top_k,
        where={"user_id": user_id}
    )
    return results["documents"][0] if results["documents"] else []

# Store some past sessions
remember_episode("alex-001", "2024-01-15",
    "Alex bought TrailBlazer X200 size 10.5. Planning Rainier hike in July. Budget $300.")
remember_episode("alex-001", "2024-02-03",
    "Alex returned to ask about tent options. Interested in Summit Pro. Partner also hikes.")
remember_episode("alex-001", "2024-03-01",
    "Alex bought Summit Pro tent. Mentioned wanting crampons for summit attempt.")

# Recall relevant memories
memories = recall_relevant("alex-001", "What gear has Alex bought before?")
for m in memories:
    print(f"📝 {m}")
```

### Passo 4: Agente com memória

Combine os três tipos de memória em um único agente:

```python
class MemoryAwareAgent:
    def __init__(self, user_id: str):
        self.user_id = user_id
        self.store = UserMemoryStore()
        self.conversation: list[dict] = []

    def _build_system_prompt(self, user_query: str) -> str:
        prefs = self.store.get_preferences(self.user_id)
        memories = recall_relevant(self.user_id, user_query, top_k=2)

        parts = ["You are a helpful outdoor gear assistant."]

        if prefs:
            parts.append(f"\nUser preferences: {json.dumps(prefs)}")

        if memories:
            parts.append("\nRelevant past interactions:")
            for m in memories:
                parts.append(f"  - {m}")

        return "\n".join(parts)

    def chat(self, message: str) -> str:
        system = self._build_system_prompt(message)
        self.conversation.append({"role": "user", "content": message})

        response = client.chat.completions.create(
            model="gpt-4o-mini",
            messages=[{"role": "system", "content": system}] + self.conversation[-10:]
        )
        reply = response.choices[0].message.content
        self.conversation.append({"role": "assistant", "content": reply})
        return reply

agent = MemoryAwareAgent("alex-001")
print(agent.chat("Hi, do you remember what I've bought before?"))
print(agent.chat("I'm thinking about doing a Rainier summit this summer — what do I still need?"))
```

---

## Guia de Decisão de Padrões de Memória

```
Is the data needed only in this conversation?
    YES → In-context (message history)

Is it structured/precise (numbers, IDs, settings)?
    YES → Structured DB (SQLite, PostgreSQL)

Is it unstructured but needs semantic search?
    YES → Vector DB (ChromaDB, pgvector)

Is it a summary of past sessions?
    YES → Episodic memory (vector + metadata filter)
```

---

## Próximos Passos

- **RAG agêntico usa memória de recuperação:** → [Lab 026 — Agentic RAG](lab-026-agentic-rag.md)
- **SK possui abstrações de memória integradas:** → [Lab 023 — SK Plugins & Memory](lab-023-sk-plugins-memory.md)
