---
tags: [rag, agentic-rag, python, free, github-models]
---
# Lab 026 : Pattern RAG agentique

<div class="lab-meta">
  <span><strong>Niveau :</strong> <span class="level-badge level-200">L200</span></span>
  <span><strong>Parcours :</strong> <a href="../paths/rag/">RAG</a></span>
  <span><strong>Durée :</strong> ~40 min</span>
  <span><strong>💰 Coût :</strong> <span class="level-badge cost-github">GitHub Free</span> + Docker (local)</span>
</div>

## Ce que vous apprendrez

- Pourquoi le RAG naïf échoue sur les questions complexes
- **Réécriture de requêtes** — améliorer la récupération avant la recherche
- **Hypothetical Document Embeddings (HyDE)** — générer pour récupérer
- **RAG multi-hop** — récupération itérative pour les questions en plusieurs parties
- **Auto-réflexion** — l'agent évalue la qualité de sa propre réponse

---

## Introduction

RAG naïf : vectoriser la requête → chercher → générer. Fonctionne bien pour les questions simples. Échoue pour :

- Questions vagues : *« Parle-moi de ça »* (qu'est-ce que « ça » ?)
- Multi-hop : *« Qu'est-ce qui est moins cher — le matériel de camping ou d'escalade ? Combien j'économiserais ? »*
- Lacunes de connaissances : *« Quel est le produit le plus récent ? »* (peut nécessiter de connaître la date actuelle)
- Hallucination : le modèle invente des faits absents du contexte

Le RAG agentique ajoute des boucles de raisonnement autour de la récupération. L'agent *décide* comment chercher, *évalue* les résultats, et *réessaie* si nécessaire.

---

## Prérequis

- Avoir terminé le [Lab 022](lab-022-rag-github-models-pgvector.md) (pgvector en fonctionnement + documents ingérés)
- `GITHUB_TOKEN` configuré
- Conteneur pgvector en fonctionnement : `docker start pgvector-rag`

!!! tip "Données d'exemple déjà chargées ?"
    Si vous avez exécuté l'étape d'ingestion du Lab 022 avec le jeu de données, vous avez déjà 42 documents dans pgvector prêts pour ce lab. Sinon, exécutez d'abord l'étape 3 du Lab 022.

---

## Exercice du lab

### Étape 1 : Réécriture de requêtes

Avant de chercher, demandez au LLM de réécrire la question de l'utilisateur en meilleures requêtes de recherche.

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

### Étape 2 : Récupérer avec plusieurs requêtes et dédupliquer

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

### Étape 3 : HyDE — Hypothetical Document Embeddings

Au lieu de vectoriser la question, générez une *réponse hypothétique* et vectorisez-la. Cela correspond souvent mieux au vrai document.

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

### Étape 4 : RAG multi-hop

Pour les questions complexes, récupérer → générer une réponse partielle → récupérer à nouveau.

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

### Étape 5 : Auto-réflexion (vérification de la qualité de la réponse)

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

## Résumé de l'architecture RAG agentique

```
Question de l'utilisateur
     │
     ▼
Réécriture de requêtes ──► 3 variantes de requêtes
     │
     ▼
Recherche parallèle ──► documents dédupliqués
     │
     ▼
Puis-je répondre ? ──Non──► Recherche de suivi (multi-hop)
     │Oui
     ▼
Générer la réponse
     │
     ▼
Auto-réflexion ──► Est-elle fondée ?
     │
     ▼
Retourner la réponse (ou réessayer)
```

---

## Prochaines étapes

- **Mémoire d'agent entre sessions :** → [Lab 027 — Patterns de mémoire d'agent](lab-027-agent-memory-patterns.md)
- **Évaluer la qualité du RAG à grande échelle :** → [Lab 035 — Évaluation d'agent](lab-035-agent-evaluation.md)
