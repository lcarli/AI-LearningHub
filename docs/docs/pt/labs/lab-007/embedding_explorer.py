"""
embedding_explorer.py — OutdoorGear Inc. Embedding Similarity Demo

Lab 007: What are Embeddings?
Uses the GitHub Models free tier (no credit card needed).

USAGE:
  export GITHUB_TOKEN=<your PAT>   # Linux/macOS
  set GITHUB_TOKEN=<your PAT>      # Windows

  python embedding_explorer.py

WHAT THIS DEMO SHOWS:
  1. Getting embeddings for product descriptions
  2. Computing cosine similarity between embeddings
  3. Finding the most similar product to a customer query
  4. Demonstrating semantic vs. keyword search
"""

import os
import math

# pip install openai
from openai import OpenAI

# ---------------------------------------------------------------------------
# Setup: GitHub Models (free, no Azure subscription needed)
# ---------------------------------------------------------------------------
client = OpenAI(
    base_url="https://models.inference.ai.azure.com",
    api_key=os.environ["GITHUB_TOKEN"],
)

EMBEDDING_MODEL = "text-embedding-3-small"  # Available on GitHub Models free tier


# ---------------------------------------------------------------------------
# OutdoorGear product catalog (simulated knowledge base)
# ---------------------------------------------------------------------------
PRODUCTS = [
    {
        "id": "P001",
        "name": "TrailBlazer Tent 2P",
        "description": "Lightweight 2-person backpacking tent, 3-season, 1.8kg, "
                        "aluminum poles, 2000mm waterproof rating, freestanding design",
    },
    {
        "id": "P002",
        "name": "Summit Dome 4P",
        "description": "4-season expedition tent for 4 people, 3.2kg, steel poles, "
                        "snow load rated, vestibule entry, extreme weather tested",
    },
    {
        "id": "P003",
        "name": "TrailBlazer Solo",
        "description": "Ultra-light solo tent, 3-season, 850g, single-wall design, "
                        "freestanding, ideal for fast and light backpacking trips",
    },
    {
        "id": "P004",
        "name": "ArcticDown -20°C Sleeping Bag",
        "description": "Winter sleeping bag with 800-fill power down, rated to -20°C, "
                        "mummy shape, draft collar, water-resistant shell, 1.4kg",
    },
    {
        "id": "P005",
        "name": "SummerLight +5°C Sleeping Bag",
        "description": "Lightweight summer sleeping bag, synthetic insulation, "
                        "rated to +5°C, side zipper for ventilation, 700g, quick-drying",
    },
    {
        "id": "P006",
        "name": "Osprey Atmos 65L Backpack",
        "description": "65-liter backpacking pack with anti-gravity suspension, "
                        "hipbelt pockets, hydration compatible, fits torso 40-52cm, 1.98kg",
    },
    {
        "id": "P007",
        "name": "DayHiker 22L Daypack",
        "description": "22-liter lightweight daypack, padded laptop sleeve, "
                        "hydration compatible, multiple pockets, 580g",
    },
]


# ---------------------------------------------------------------------------
# Helper functions
# ---------------------------------------------------------------------------

def get_embedding(text: str) -> list[float]:
    """Request an embedding vector from GitHub Models."""
    response = client.embeddings.create(
        model=EMBEDDING_MODEL,
        input=text,
    )
    return response.data[0].embedding


def cosine_similarity(vec_a: list[float], vec_b: list[float]) -> float:
    """
    Compute cosine similarity between two vectors.

    cosine_similarity = dot(A, B) / (|A| * |B|)

    Returns a value between -1 and 1:
      1.0  = identical direction (semantically very similar)
      0.0  = orthogonal (unrelated)
     -1.0  = opposite direction (rarely occurs with embeddings)
    """
    dot_product = sum(a * b for a, b in zip(vec_a, vec_b))
    magnitude_a = math.sqrt(sum(a * a for a in vec_a))
    magnitude_b = math.sqrt(sum(b * b for b in vec_b))

    if magnitude_a == 0 or magnitude_b == 0:
        return 0.0

    return dot_product / (magnitude_a * magnitude_b)


# ---------------------------------------------------------------------------
# Demo 1: Embed all products and find the best match for a query
# ---------------------------------------------------------------------------

def semantic_search(query: str, top_k: int = 3) -> None:
    """Find the top_k most semantically similar products to the query."""
    print(f"\n{'='*60}")
    print(f"QUERY: '{query}'")
    print(f"{'='*60}")

    # Step 1: Embed the query
    print("\nGenerating query embedding...")
    query_embedding = get_embedding(query)
    print(f"  ✓ Query embedding: {len(query_embedding)} dimensions")

    # Step 2: Embed all products and compute similarity
    print("\nComparing with product catalog...")
    results = []

    for product in PRODUCTS:
        product_text = f"{product['name']}: {product['description']}"
        product_embedding = get_embedding(product_text)
        similarity = cosine_similarity(query_embedding, product_embedding)
        results.append((similarity, product))

    # Step 3: Sort by similarity (highest first)
    results.sort(key=lambda x: x[0], reverse=True)

    # Step 4: Display top results
    print(f"\nTop {top_k} matches:")
    for i, (score, product) in enumerate(results[:top_k], 1):
        bar = "█" * int(score * 40)
        print(f"\n  {i}. [{product['id']}] {product['name']}")
        print(f"     Similarity: {score:.4f}  {bar}")
        print(f"     {product['description'][:80]}...")


# ---------------------------------------------------------------------------
# Demo 2: Semantic vs. keyword search comparison
# ---------------------------------------------------------------------------

def compare_search_approaches() -> None:
    """Illustrate why semantic search beats keyword matching."""
    print(f"\n{'='*60}")
    print("DEMO: Semantic vs. Keyword Search")
    print(f"{'='*60}")

    query = "I need something to sleep in the cold"
    keyword = "sleeping"

    print(f"\nQuery: '{query}'")
    print(f"Keyword filter (contains '{keyword}'):")

    keyword_matches = [
        p for p in PRODUCTS if keyword.lower() in p["description"].lower()
    ]
    if keyword_matches:
        for p in keyword_matches:
            print(f"  ✓ [{p['id']}] {p['name']}")
    else:
        print("  ✗ No keyword matches found")

    print("\nSemantic matches (top 2):")
    query_embedding = get_embedding(query)
    results = []
    for product in PRODUCTS:
        text = f"{product['name']}: {product['description']}"
        emb = get_embedding(text)
        score = cosine_similarity(query_embedding, emb)
        results.append((score, product))
    results.sort(key=lambda x: x[0], reverse=True)
    for score, product in results[:2]:
        print(f"  ✓ [{product['id']}] {product['name']} (score: {score:.4f})")

    print("\n💡 Notice: Semantic search understands intent even without exact keyword matches!")


# ---------------------------------------------------------------------------
# Demo 3: Similarity between related vs. unrelated products
# ---------------------------------------------------------------------------

def visualize_similarity_matrix() -> None:
    """Show similarity scores between a subset of products."""
    print(f"\n{'='*60}")
    print("DEMO: Similarity Matrix (subset)")
    print(f"{'='*60}")

    subset = PRODUCTS[:4]  # First 4 products
    embeddings = []

    print("\nGenerating embeddings for product subset...")
    for product in subset:
        text = f"{product['name']}: {product['description']}"
        emb = get_embedding(text)
        embeddings.append(emb)
        print(f"  ✓ {product['name']}")

    print("\nCosine similarity matrix:")
    header = "".join(f"  {p['id']:>6}" for p in subset)
    print(f"       {header}")

    for i, prod_i in enumerate(subset):
        row = f"  {prod_i['id']:>5}"
        for j, _ in enumerate(subset):
            score = cosine_similarity(embeddings[i], embeddings[j])
            row += f"  {score:>6.3f}"
        print(row)

    print("\n💡 Notice: P001 and P003 (both tents) have higher similarity than P001 and P004 (tent vs. sleeping bag)")


# ---------------------------------------------------------------------------
# Main
# ---------------------------------------------------------------------------

if __name__ == "__main__":
    print("OutdoorGear Inc. — Embedding Explorer")
    print("Using model:", EMBEDDING_MODEL)
    print("(Each API call uses your GitHub Models free tier quota)\n")

    # Demo 1: Semantic search queries
    semantic_search("lightweight tent for solo hiking", top_k=3)
    semantic_search("cold weather sleeping solution", top_k=3)
    semantic_search("pack to carry gear on a day hike", top_k=3)

    # Demo 2: Semantic vs. keyword
    compare_search_approaches()

    # Demo 3: Similarity matrix
    visualize_similarity_matrix()

    print(f"\n{'='*60}")
    print("✅ Embedding Explorer complete!")
    print("Try modifying the QUERIES above to explore other product matches.")
    print(f"{'='*60}")
