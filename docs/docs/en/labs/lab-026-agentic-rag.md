# Lab 026: Agentic RAG Pattern

<div class="lab-meta">
  <span><strong>Level:</strong> <span class="level-badge level-200">L200</span></span>
  <span><strong>Path:</strong> <a href="../paths/rag/">RAG</a></span>
  <span><strong>Time:</strong> ~40 min</span>
  <span><strong>💰 Cost:</strong> <span class="level-badge cost-github">GitHub Free</span> + Docker (local)</span>
</div>

## What You'll Learn

- Why naive RAG fails on complex questions
- **Query rewriting** — improving retrieval before searching
- **Hypothetical Document Embeddings (HyDE)** — generate to retrieve
- **Multi-hop RAG** — iterative retrieval for multi-part questions
- **Self-reflection** — agent evaluates its own answer quality

---

## Introduction

Naive RAG: embed query → search → generate. Works fine for simple questions. Fails for:

- Vague questions: *"Tell me about it"* (what is "it"?)
- Multi-hop: *"What's cheaper — camping or climbing gear? What would I save?"*
- Knowledge gaps: *"What's the newest product?"* (may need to know current date)
- Hallucination: model invents facts not in context

Agentic RAG adds reasoning loops around retrieval. The agent *decides* how to search, *evaluates* results, and *retries* if needed.

---

## Prerequisites

- Completed [Lab 022](lab-022-rag-github-models-pgvector.md) (pgvector running + documents ingested)
- `GITHUB_TOKEN` set
- pgvector container running: `docker start pgvector-rag`

!!! tip "Sample data already loaded?"
    If you ran Lab 022's ingest step with the sample dataset, you already have 42 documents in pgvector ready for this lab. If not, run Lab 022's Step 3 first.

---

## Lab Exercise

### Step 1: Query rewriting

Before searching, ask the LLM to rewrite the user's question into better search queries.

```python
import os
from openai import OpenAI
from search import search  # from Lab 022

client = OpenAI(
    base_url="https://models.inference.ai.azure.com",
    api_key=os.environ["GITHUB_TOKEN"],
)

def rewrite_query(original: str) -> list[str]:
    """Generate 3 search query variations for better recall."""
    response = client.chat.completions.create(
        model="gpt-4o-mini",
        temperature=0,
        messages=[
            {
                "role": "system",
                "content": (
                    "You generate search queries. Given a user question, produce 3 different "
                    "search queries that would find relevant information. "
                    "Return one query per line, no numbering or bullets."
                )
            },
            {"role": "user", "content": f"Question: {original}"}
        ]
    )
    queries = response.choices[0].message.content.strip().split("\n")
    return [q.strip() for q in queries if q.strip()]

# Test
question = "Is this tent good for rain?"
queries = rewrite_query(question)
print("Rewritten queries:")
for q in queries:
    print(f"  • {q}")
# Example output:
# • Summit Pro Tent waterproof rating
# • tent performance in wet weather conditions
# • camping shelter rain protection features
```

### Step 2: Retrieve with multiple queries and deduplicate

```python
def retrieve_with_rewriting(question: str, top_k: int = 3) -> list[dict]:
    queries = [question] + rewrite_query(question)

    seen_titles = set()
    all_docs = []

    for q in queries:
        results = search(q, top_k=top_k)
        for doc in results:
            if doc["title"] not in seen_titles and doc["similarity"] > 0.70:
                seen_titles.add(doc["title"])
                all_docs.append(doc)

    # Sort by best similarity across queries
    all_docs.sort(key=lambda d: d["similarity"], reverse=True)
    return all_docs[:top_k]
```

### Step 3: HyDE — Hypothetical Document Embeddings

Instead of embedding the question, generate a *hypothetical answer* and embed that. This often matches the real document better.

```python
def hyde_search(question: str, top_k: int = 3) -> list[dict]:
    # Generate a hypothetical answer
    hyp_response = client.chat.completions.create(
        model="gpt-4o-mini",
        temperature=0.3,
        messages=[
            {"role": "system", "content": "Write a short, factual answer to this question as if you knew the answer. Be specific."},
            {"role": "user", "content": question}
        ]
    )
    hypothetical_answer = hyp_response.choices[0].message.content

    print(f"  [HyDE] Generated hypothesis: {hypothetical_answer[:80]}...")

    # Search using the hypothetical answer (more content = better embedding match)
    return search(hypothetical_answer, top_k=top_k)
```

### Step 4: Multi-hop RAG

For complex questions, retrieve → generate partial answer → retrieve again.

```python
def multi_hop_answer(question: str) -> str:
    max_hops = 3
    context_docs = []
    current_question = question

    for hop in range(max_hops):
        print(f"\n  [Hop {hop+1}] Searching: {current_question}")

        new_docs = retrieve_with_rewriting(current_question)
        context_docs.extend(new_docs)

        context = "\n\n".join([
            f"**{d['title']}**\n{d['content']}" for d in context_docs
        ])

        # Ask the model: can I answer, or do I need more info?
        check_response = client.chat.completions.create(
            model="gpt-4o-mini",
            temperature=0,
            messages=[
                {
                    "role": "system",
                    "content": (
                        "Given context and a question, respond with JSON: "
                        '{"can_answer": true/false, "answer": "...", "follow_up_query": "..."}\n'
                        "Set can_answer=true if context fully answers the question. "
                        "Otherwise, set follow_up_query to what you still need."
                    )
                },
                {"role": "user", "content": f"Context:\n{context}\n\nQuestion: {question}"}
            ]
        )

        import json
        result = json.loads(check_response.choices[0].message.content)

        if result["can_answer"]:
            print(f"  ✅ Answered after {hop+1} hop(s)")
            return result["answer"]

        current_question = result.get("follow_up_query", question)
        print(f"  🔄 Need more info: {current_question}")

    # Final attempt with all gathered context
    return answer_with_context(question, context_docs)

def answer_with_context(question: str, docs: list[dict]) -> str:
    context = "\n\n".join([f"**{d['title']}**\n{d['content']}" for d in docs])
    response = client.chat.completions.create(
        model="gpt-4o-mini",
        temperature=0,
        messages=[
            {"role": "system", "content": "Answer based only on the provided context. Be honest if information is incomplete."},
            {"role": "user", "content": f"Context:\n{context}\n\nQuestion: {question}"}
        ]
    )
    return response.choices[0].message.content

# Test multi-hop
print(multi_hop_answer("What's the cheapest product suitable for a Rainier climb?"))
```

### Step 5: Self-reflection (answer quality check)

```python
from pydantic import BaseModel

class AnswerQuality(BaseModel):
    is_grounded: bool          # Is the answer supported by the context?
    has_hallucination: bool    # Did the model add facts not in context?
    confidence: float          # 0.0 to 1.0
    issues: list[str]          # List of specific problems, if any

def check_answer_quality(question: str, context: str, answer: str) -> AnswerQuality:
    response = client.beta.chat.completions.parse(
        model="gpt-4o-mini",
        temperature=0,
        messages=[
            {
                "role": "system",
                "content": "You are a RAG quality evaluator. Check if the answer is grounded in the context."
            },
            {
                "role": "user",
                "content": f"Context:\n{context}\n\nQuestion: {question}\n\nAnswer: {answer}"
            }
        ],
        response_format=AnswerQuality,
    )
    return response.choices[0].message.parsed
```

---

## Agentic RAG Architecture Summary

```
User Question
     │
     ▼
Query Rewriting ──► 3 query variants
     │
     ▼
Parallel Search ──► deduplicated docs
     │
     ▼
Can I answer? ──No──► Follow-up search (multi-hop)
     │Yes
     ▼
Generate Answer
     │
     ▼
Self-Reflection ──► Is it grounded?
     │
     ▼
Return Answer (or retry)
```

---

## Next Steps

- **Agent memory across sessions:** → [Lab 027 — Agent Memory Patterns](lab-027-agent-memory-patterns.md)
- **Evaluate RAG quality at scale:** → [Lab 035 — Agent Evaluation](lab-035-agent-evaluation.md)
