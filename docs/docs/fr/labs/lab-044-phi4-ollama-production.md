---
tags: [phi4, ollama, local-llm, free, python]
---
# Lab 044 : Phi-4 + Ollama en production

<div class="lab-meta">
  <span><strong>Niveau :</strong> <span class="level-badge level-400">L400</span></span>
  <span><strong>Parcours :</strong> <a href="../paths/pro-code/">Pro Code</a></span>
  <span><strong>Durée :</strong> ~90 min</span>
  <span><strong>💰 Coût :</strong> <span class="level-badge cost-free">Gratuit (local)</span> — 8 Go+ de RAM pour Phi-4-mini</span>
</div>

## Ce que vous apprendrez

- Exécuter **Microsoft Phi-4** localement via Ollama (coût nul, pas d'internet requis)
- **Évaluer les performances** de Phi-4-mini vs GPT-4o-mini sur des tâches de raisonnement
- Construire un **agent local-first** avec basculement automatique vers le cloud
- Ajouter la **mise en cache des réponses** pour éviter les appels LLM redondants
- **Traitement par lots** pour les cas d'utilisation à haut débit

---

## Introduction

Phi-4 est la famille de petits modèles de langage de pointe de Microsoft. **Phi-4-mini** (3,8 milliards de paramètres) fonctionne sur un ordinateur portable avec 8 Go de RAM et égale GPT-4o-mini sur de nombreux benchmarks de raisonnement — gratuitement, localement, sans aucun souci de confidentialité.

Ce lab construit une configuration d'inférence locale de qualité production : mise en cache, traitement par lots, basculement et évaluation des performances.

---

## Prérequis

- [Ollama](https://ollama.ai) installé
- 8 Go+ de RAM (16 Go recommandés pour de meilleures performances)
- Python 3.11+
- `pip install openai httpx`
- Optionnel : `GITHUB_TOKEN` pour le basculement vers le cloud

---

## Exercice pratique

### Étape 1 : Télécharger les modèles Phi-4

```bash
# Phi-4-mini: 3.8B parameters, fast, fits in 8GB RAM
ollama pull phi4-mini

# Phi-4: 14B parameters, higher quality, needs 16GB RAM
ollama pull phi4

# Verify
ollama list
```

### Étape 2 : Tester Phi-4 via l'API compatible OpenAI d'Ollama

Ollama expose une API compatible OpenAI à `http://localhost:11434/v1`, vous pouvez donc utiliser le même client Python `openai` :

```python
# test_phi4.py
from openai import OpenAI

# Ollama — local, free, private
local_client = OpenAI(
    base_url="http://localhost:11434/v1",
    api_key="ollama",  # placeholder, Ollama doesn't need a real key
)

response = local_client.chat.completions.create(
    model="phi4-mini",
    messages=[
        {"role": "system", "content": "You are a helpful assistant."},
        {"role": "user",   "content": "What is 17 × 23?"}
    ]
)
print(response.choices[0].message.content)
# Expected: 391
```

### Étape 3 : Construire un client local-first avec basculement vers le cloud

```python
# local_first_client.py
import os, time, hashlib, json
from pathlib import Path
from openai import OpenAI

class LocalFirstClient:
    """
    Try local Phi-4 first. Fall back to GitHub Models (cloud) if:
    - Ollama is not running
    - Local inference exceeds the timeout
    - The task requires capabilities beyond Phi-4
    """

    def __init__(self, local_timeout: float = 30.0, cache_dir: Path = Path(".cache")):
        self.local_timeout = local_timeout
        self.cache_dir = cache_dir
        self.cache_dir.mkdir(exist_ok=True)

        self.local = OpenAI(
            base_url="http://localhost:11434/v1",
            api_key="ollama",
            timeout=local_timeout,
        )

        self.cloud = OpenAI(
            base_url="https://models.inference.ai.azure.com",
            api_key=os.environ.get("GITHUB_TOKEN", ""),
        )

        self.stats = {"local_hits": 0, "cloud_hits": 0, "cache_hits": 0}

    def _cache_key(self, model: str, messages: list) -> str:
        content = json.dumps({"model": model, "messages": messages}, sort_keys=True)
        return hashlib.md5(content.encode()).hexdigest()

    def _get_cache(self, key: str) -> str | None:
        cache_file = self.cache_dir / f"{key}.json"
        if cache_file.exists():
            return json.loads(cache_file.read_text())["response"]
        return None

    def _set_cache(self, key: str, response: str):
        cache_file = self.cache_dir / f"{key}.json"
        cache_file.write_text(json.dumps({"response": response}))

    def chat(self, messages: list, prefer_local: bool = True, use_cache: bool = True) -> dict:
        """
        Returns: {"response": str, "source": "cache"|"local"|"cloud", "latency_ms": float}
        """
        cache_key = self._cache_key("phi4-mini", messages)

        if use_cache:
            cached = self._get_cache(cache_key)
            if cached:
                self.stats["cache_hits"] += 1
                return {"response": cached, "source": "cache", "latency_ms": 0}

        if prefer_local:
            try:
                start = time.perf_counter()
                resp = self.local.chat.completions.create(
                    model="phi4-mini", messages=messages
                )
                latency = (time.perf_counter() - start) * 1000
                result = resp.choices[0].message.content
                self.stats["local_hits"] += 1
                if use_cache:
                    self._set_cache(cache_key, result)
                return {"response": result, "source": "local", "latency_ms": round(latency, 1)}
            except Exception as e:
                print(f"  [local failed: {e}] → falling back to cloud")

        # Cloud fallback
        start = time.perf_counter()
        resp = self.cloud.chat.completions.create(
            model="gpt-4o-mini", messages=messages
        )
        latency = (time.perf_counter() - start) * 1000
        result = resp.choices[0].message.content
        self.stats["cloud_hits"] += 1
        if use_cache:
            self._set_cache(cache_key, result)
        return {"response": result, "source": "cloud", "latency_ms": round(latency, 1)}

    def print_stats(self):
        total = sum(self.stats.values())
        print(f"\n=== Request Stats ===")
        print(f"Total requests: {total}")
        for k, v in self.stats.items():
            pct = (v / total * 100) if total > 0 else 0
            print(f"  {k}: {v} ({pct:.0f}%)")
```

### Étape 4 : Benchmark Phi-4-mini vs GPT-4o-mini

```python
# benchmark.py
import time
from local_first_client import LocalFirstClient

client = LocalFirstClient(use_cache=False)  # disable cache for fair benchmark

TASKS = [
    {"name": "Simple Q&A",    "msg": "What is the return policy for OutdoorGear?",        "sys": "Answer briefly."},
    {"name": "Math",           "msg": "A store buys boots at $80 and sells at $189.99. Margin?", "sys": "Show calculation."},
    {"name": "Reasoning",      "msg": "I need gear for a 3-day winter hike above treeline. What do I need?", "sys": "List essentials only."},
    {"name": "Code generation","msg": "Write a Python function to calculate shipping cost: free over $75, else $5.99.", "sys": "Return only code."},
    {"name": "Summarization",  "msg": "Summarize in one sentence: The TrailBlazer X200 is a waterproof Gore-Tex hiking boot with a Vibram outsole. It's 3-season rated and priced at $189.99.", "sys": "One sentence only."},
]

print(f"{'Task':<20} {'Source':<8} {'Latency':>10}   Response")
print("-"*80)

for task in TASKS:
    messages = [
        {"role": "system", "content": task["sys"]},
        {"role": "user",   "content": task["msg"]},
    ]

    # Local (Phi-4-mini)
    local_result = client.chat(messages, prefer_local=True)
    print(f"{task['name']:<20} {'phi4-mini':<8} {local_result['latency_ms']:>8.0f}ms   {local_result['response'][:60]}")

    # Cloud (GPT-4o-mini)
    cloud_result = client.chat(messages, prefer_local=False)
    print(f"{'':20} {'gpt-4o-mini':<8} {cloud_result['latency_ms']:>8.0f}ms   {cloud_result['response'][:60]}")
    print()
```

```bash
python benchmark.py
```

### Étape 5 : Traitement par lots pour un haut débit

```python
# batch_processor.py
import asyncio
from local_first_client import LocalFirstClient

async def process_batch(questions: list[str], client: LocalFirstClient, concurrency: int = 3):
    """Process multiple questions concurrently."""
    semaphore = asyncio.Semaphore(concurrency)

    async def process_one(q: str) -> dict:
        async with semaphore:
            loop = asyncio.get_event_loop()
            # Run sync client in thread pool
            result = await loop.run_in_executor(
                None,
                lambda: client.chat([
                    {"role": "system", "content": "Answer product questions briefly."},
                    {"role": "user",   "content": q}
                ])
            )
            return {"question": q, **result}

    return await asyncio.gather(*[process_one(q) for q in questions])


async def main():
    client = LocalFirstClient()

    questions = [
        "What tents do you carry?",
        "Cheapest hiking boot?",
        "Return policy?",
        "Waterproof jackets available?",
        "Warranty on climbing gear?",
    ]

    print(f"Processing {len(questions)} questions...")
    start = __import__("time").perf_counter()
    results = await process_batch(questions, client)
    elapsed = __import__("time").perf_counter() - start

    for r in results:
        print(f"[{r['source']}] {r['question'][:40]:<40} → {r['response'][:60]}")

    print(f"\nProcessed {len(results)} questions in {elapsed:.1f}s")
    client.print_stats()

asyncio.run(main())
```

---

## Comparaison des performances (résultats typiques)

| Modèle | Latence moy. | Qualité | Coût | Confidentialité |
|-------|------------|---------|------|---------|
| phi4-mini (local) | 800–2000ms | ★★★★☆ | Gratuit | ✅ Local |
| phi4 (local) | 3000–8000ms | ★★★★★ | Gratuit | ✅ Local |
| gpt-4o-mini (cloud) | 300–800ms | ★★★★★ | ~0,00015 $/1k tok | ☁️ Cloud |

!!! tip "Quand choisir le local"
    Utilisez Phi-4-mini pour : les tâches à fort volume, les données sensibles, les scénarios hors ligne et le développement.
    Utilisez le cloud pour : le raisonnement complexe, les SLA de production et les tâches nécessitant les dernières capacités.

---

## Prochaines étapes

- **Conteneurisez votre configuration IA locale :** Ajoutez Ollama au devcontainer (déjà préconfiguré dans `.devcontainer/devcontainer.json`)
- **Intégrez Phi-4 dans du RAG :** → [Lab 022 — RAG avec pgvector](lab-022-rag-github-models-pgvector.md)
