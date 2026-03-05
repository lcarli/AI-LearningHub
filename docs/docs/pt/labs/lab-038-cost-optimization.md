---
tags: [cost-optimization, azure, production, monitoring, L300]
---
# Lab 038: Otimização de Custos de IA

<div class="lab-meta">
  <span><strong>Nível:</strong> <span class="level-badge level-300">L300</span></span>
  <span><strong>Trilha:</strong> <a href="../paths/pro-code/">💻 Pro Code</a></span>
  <span><strong>Tempo:</strong> ~45 min</span>
  <span><strong>💰 Custo:</strong> <span class="level-badge cost-azure">Azure Free Tier</span> — A maioria das estratégias são gratuitas para implementar</span>
</div>

## O que Você Vai Aprender

- Entender os fatores de custo de APIs de IA (tokens, escolha de modelo, frequência de requisições)
- Aplicar **5 estratégias-chave** para reduzir custos: cache, batching, roteamento de modelos, compressão de prompts e streaming
- Implementar **cache semântico** para evitar chamadas LLM duplicadas
- Construir um **roteador de modelos** que usa modelos baratos para consultas simples e modelos caros para as complexas
- Monitorar e alertar sobre custos com **Azure Monitor**

---

## Introdução

Um agente de IA em produção pode facilmente custar $50–500/mês mesmo com uso modesto, se não otimizado. A boa notícia: a maioria das estratégias de redução de custos também melhora a latência e a experiência do usuário.

**As principais alavancas de custo:**

| Fator | Impacto | Otimização |
|--------|--------|-------------|
| **Escolha do modelo** | Diferença de custo de 10–50× | Rotear para modelo mais barato quando possível |
| **Contagem de tokens** | Custo linear | Comprimir prompts, cortar histórico |
| **Acertos de cache** | Elimina o custo inteiramente | Cache semântico para consultas repetidas |
| **Volume de requisições** | Custo linear | Batch, debounce, deduplicar |
| **Tamanho da saída** | Custo linear | Usar `max_tokens`, saída estruturada |

---

## Parte 1: Meça Sua Linha de Base

Antes de otimizar, meça o que você está gastando:

```python
# cost_tracker.py
from openai import OpenAI
import os

# Model pricing (USD per 1M tokens, as of 2025)
# Update these from: https://azure.microsoft.com/pricing/details/cognitive-services/openai-service/
MODEL_PRICING = {
    "gpt-4o":       {"input": 2.50,  "output": 10.00},
    "gpt-4o-mini":  {"input": 0.15,  "output":  0.60},
    "gpt-3.5-turbo":{"input": 0.50,  "output":  1.50},
}

class CostTracker:
    def __init__(self):
        self.total_input_tokens = 0
        self.total_output_tokens = 0
        self.total_requests = 0
        self.total_cost_usd = 0.0
        self.calls = []

    def track(self, model: str, usage):
        pricing = MODEL_PRICING.get(model, {"input": 0.01, "output": 0.03})
        input_cost  = (usage.prompt_tokens / 1_000_000)     * pricing["input"]
        output_cost = (usage.completion_tokens / 1_000_000) * pricing["output"]
        call_cost   = input_cost + output_cost

        self.total_input_tokens  += usage.prompt_tokens
        self.total_output_tokens += usage.completion_tokens
        self.total_requests      += 1
        self.total_cost_usd      += call_cost
        self.calls.append({"model": model, "cost_usd": call_cost})

        return call_cost

    def summary(self) -> str:
        return (
            f"Requests: {self.total_requests}\n"
            f"Input tokens: {self.total_input_tokens:,}\n"
            f"Output tokens: {self.total_output_tokens:,}\n"
            f"Estimated cost: ${self.total_cost_usd:.6f}"
        )


tracker = CostTracker()
client = OpenAI(
    base_url="https://models.inference.ai.azure.com",
    api_key=os.environ["GITHUB_TOKEN"],
)

def chat(messages, model="gpt-4o-mini") -> str:
    response = client.chat.completions.create(model=model, messages=messages, max_tokens=200)
    tracker.track(model, response.usage)
    return response.choices[0].message.content

# Baseline: 10 product queries
queries = [
    "What tents do you have?",
    "Show me tents",                     # near-duplicate
    "List your tent products",           # near-duplicate
    "What sleeping bags are available?",
    "Tell me about sleeping bags",       # near-duplicate
    "Do you have winter sleeping bags?",
    "What backpacks do you sell?",
    "Tell me about backpacks",           # near-duplicate
    "What's the cheapest backpack?",
    "Which backpack is most affordable?",# near-duplicate
]

print("=== BASELINE (no optimization) ===")
for query in queries:
    answer = chat([
        {"role": "system", "content": "You are an OutdoorGear product advisor."},
        {"role": "user",   "content": query},
    ])
    print(f"Q: {query[:50]:<50} → {answer[:40]}...")

print("\n" + tracker.summary())
```

---

## Parte 2: Estratégia 1 — Cache Semântico

Um **cache semântico** armazena respostas de LLM e as reutiliza para consultas semanticamente similares, mesmo quando a formulação difere:

```python
# semantic_cache.py
import json
import math
from openai import OpenAI
import os

client = OpenAI(
    base_url="https://models.inference.ai.azure.com",
    api_key=os.environ["GITHUB_TOKEN"],
)

def get_embedding(text: str) -> list[float]:
    response = client.embeddings.create(model="text-embedding-3-small", input=text)
    return response.data[0].embedding

def cosine_similarity(a: list[float], b: list[float]) -> float:
    dot = sum(x*y for x, y in zip(a, b))
    mag_a = math.sqrt(sum(x*x for x in a))
    mag_b = math.sqrt(sum(x*x for x in b))
    return dot / (mag_a * mag_b) if mag_a and mag_b else 0.0

class SemanticCache:
    def __init__(self, similarity_threshold: float = 0.92):
        self.threshold = similarity_threshold
        self.cache: list[dict] = []  # [{query, embedding, response}]
        self.hits = 0
        self.misses = 0

    def get(self, query: str) -> str | None:
        query_emb = get_embedding(query)
        for entry in self.cache:
            score = cosine_similarity(query_emb, entry["embedding"])
            if score >= self.threshold:
                self.hits += 1
                return entry["response"]
        self.misses += 1
        return None

    def set(self, query: str, response: str) -> None:
        embedding = get_embedding(query)
        self.cache.append({"query": query, "embedding": embedding, "response": response})

    @property
    def hit_rate(self) -> float:
        total = self.hits + self.misses
        return self.hits / total if total > 0 else 0.0

cache = SemanticCache(similarity_threshold=0.92)

def chat_with_cache(query: str, system: str = "You are an OutdoorGear product advisor.") -> tuple[str, bool]:
    cached = cache.get(query)
    if cached:
        return cached, True   # (response, from_cache)

    response = client.chat.completions.create(
        model="gpt-4o-mini",
        messages=[{"role": "system", "content": system}, {"role": "user", "content": query}],
        max_tokens=200,
    )
    answer = response.choices[0].message.content
    cache.set(query, answer)
    return answer, False   # (response, from_cache)

# Test with near-duplicates
print("=== WITH SEMANTIC CACHE ===")
for query in queries:  # reuse queries from Part 1
    answer, from_cache = chat_with_cache(query)
    status = "💾 CACHE" if from_cache else "🌐 API"
    print(f"{status} | {query[:45]:<45}")

print(f"\nCache hit rate: {cache.hit_rate:.0%}")
print(f"API calls saved: {cache.hits}")
```

---

## Parte 3: Estratégia 2 — Roteador de Modelos

Use modelos baratos para consultas simples, modelos caros para as complexas:

```python
# model_router.py
import os
from openai import OpenAI

client = OpenAI(
    base_url="https://models.inference.ai.azure.com",
    api_key=os.environ["GITHUB_TOKEN"],
)

CHEAP_MODEL   = "gpt-4o-mini"    # $0.15/M input — for simple Q&A
PREMIUM_MODEL = "gpt-4o"         # $2.50/M input — for complex reasoning

# Signals that indicate a complex query needing the premium model
COMPLEX_SIGNALS = [
    "compare", "recommend", "which is better", "analyze", "explain why",
    "trade-off", "pros and cons", "for my specific", "help me decide",
]

def route_query(query: str) -> str:
    """Return the appropriate model name based on query complexity."""
    query_lower = query.lower()
    if any(signal in query_lower for signal in COMPLEX_SIGNALS):
        return PREMIUM_MODEL
    return CHEAP_MODEL

def smart_chat(query: str, system: str = "You are an OutdoorGear product advisor.") -> dict:
    model = route_query(query)
    response = client.chat.completions.create(
        model=model,
        messages=[{"role": "system", "content": system}, {"role": "user", "content": query}],
        max_tokens=300,
    )
    return {
        "answer":  response.choices[0].message.content,
        "model":   model,
        "tokens":  response.usage.total_tokens,
    }

# Test routing
test_queries = [
    ("What tents do you have?",                             "→ simple listing"),
    ("What's the price of the DayHiker 22L?",              "→ simple lookup"),
    ("Compare the TrailBlazer Tent 2P vs Summit Dome 4P",  "→ comparison"),
    ("I'm going on a 2-week alpine climb in January, which sleeping bag and tent should I buy and why?",
                                                           "→ complex recommendation"),
]

print("=== MODEL ROUTER ===")
for query, description in test_queries:
    result = smart_chat(query)
    model_label = "💎 GPT-4o" if result["model"] == PREMIUM_MODEL else "⚡ GPT-4o-mini"
    print(f"\n{model_label} {description}")
    print(f"  Q: {query[:70]}")
    print(f"  A: {result['answer'][:80]}...")
```

---

## Parte 4: Estratégia 3 — Compressão de Prompts

Corte o histórico de conversas para manter apenas as mais recentes + resumo:

```python
# prompt_compression.py
MAX_HISTORY_TURNS = 3  # Keep last N turns before summarizing older ones

def compress_history(messages: list[dict], max_turns: int = MAX_HISTORY_TURNS) -> list[dict]:
    """
    Keep the system message + last `max_turns` conversation pairs.
    Summarize older turns into a single context message.
    """
    system = [m for m in messages if m["role"] == "system"]
    conversation = [m for m in messages if m["role"] != "system"]

    if len(conversation) <= max_turns * 2:
        return messages  # No compression needed

    older = conversation[:-max_turns * 2]
    recent = conversation[-max_turns * 2:]

    # Summarize older turns (in production: call the LLM to summarize)
    summary_lines = []
    for i in range(0, len(older), 2):
        if i + 1 < len(older):
            summary_lines.append(f"User asked: {older[i]['content'][:60]}...")

    summary_msg = {
        "role": "system",
        "content": f"[Earlier conversation summary: {'; '.join(summary_lines)}]"
    }

    return system + [summary_msg] + recent

# Measure token savings
long_history = (
    [{"role": "system", "content": "You are an OutdoorGear advisor."}]
    + [msg
       for i in range(10)
       for msg in [
           {"role": "user",      "content": f"Turn {i}: What about product P00{i%7+1}?"},
           {"role": "assistant", "content": f"Product P00{i%7+1} is a great choice for outdoor activities."},
       ]]
)

compressed = compress_history(long_history, max_turns=3)
original_tokens  = sum(len(m["content"].split()) for m in long_history)
compressed_tokens = sum(len(m["content"].split()) for m in compressed)
savings = 1 - compressed_tokens / original_tokens

print(f"=== PROMPT COMPRESSION ===")
print(f"Original:   {len(long_history)} messages, ~{original_tokens} tokens")
print(f"Compressed: {len(compressed)} messages, ~{compressed_tokens} tokens")
print(f"Savings:    {savings:.0%}")
```

---

## Parte 5: Monitoramento de Custos com Azure Monitor

Em produção, acompanhe os custos com Azure Monitor:

```python
# azure_cost_monitor.py (requires azure-monitor-opentelemetry)
# pip install azure-monitor-opentelemetry

from azure.monitor.opentelemetry import configure_azure_monitor
from opentelemetry import metrics

configure_azure_monitor(
    connection_string=os.environ["APPLICATIONINSIGHTS_CONNECTION_STRING"]
)

meter = metrics.get_meter("outdoorgear.agent")

token_counter = meter.create_counter(
    "ai.tokens.used",
    description="Total LLM tokens consumed",
    unit="tokens",
)

cost_gauge = meter.create_up_down_counter(
    "ai.cost.usd",
    description="Estimated AI API cost",
    unit="USD",
)

def track_llm_call(model: str, input_tokens: int, output_tokens: int, cost: float):
    attrs = {"model": model, "service": "outdoorgear-agent"}
    token_counter.add(input_tokens,  {**attrs, "type": "input"})
    token_counter.add(output_tokens, {**attrs, "type": "output"})
    cost_gauge.add(cost, attrs)
```

No Portal do Azure, crie um alerta:

```
Alert rule: AI cost > $10/day
Signal: Custom metric ai.cost.usd
Threshold: > 10 (sum over 24h)
Action: Email engineering@outdoorgear.example.com
```

---

## 🧠 Verificação de Conhecimento

??? question "1. O que é cache semântico e como ele difere do cache de correspondência exata?"
    **Cache de correspondência exata** retorna resultados em cache apenas quando a entrada é idêntica byte a byte. **Cache semântico** usa embeddings para encontrar respostas em cache para entradas semanticamente similares — "Mostre-me tendas" e "Que tendas vocês têm?" obtêm a mesma resposta em cache mesmo com formulações diferentes. O cache semântico é muito mais eficaz para IA conversacional.

??? question "2. Quando você NÃO deve usar um modelo barato em um roteador de modelos?"
    Use um modelo premium para: **raciocínio em múltiplos passos** (cadeia de pensamento), **comparações** entre opções complexas, **recomendações personalizadas** que requerem pesar muitos fatores, **tarefas onde erros são custosos** (médico, financeiro, jurídico). Use modelos baratos para: consultas, listagens, formatação, perguntas e respostas simples onde a tolerância a erros é maior.

??? question "3. Quais são os riscos de comprimir agressivamente o histórico de prompts?"
    O agente pode **perder contexto** que precisa: um usuário mencionou uma alergia 5 turnos atrás e o resumo comprimido perdeu isso. Um histórico mal resumido pode causar **respostas contraditórias** em conversas longas. Sempre mantenha os N turnos mais recentes na íntegra; apenas resuma turnos mais antigos. Teste com cenários que exigem contexto de longo alcance.

---

## Resumo

| Estratégia | Economia Potencial | Complexidade |
|----------|-------------------|------------|
| Cache semântico | 40–80% das chamadas de API | Média |
| Roteamento de modelos | Redução de custo de 10–40× | Baixa |
| Compressão de prompts | Redução de 20–60% dos tokens | Baixa |
| Batching de requisições | 10–30% (trade-off de latência) | Média |
| Limitação de saída (`max_tokens`) | 5–20% | Muito Baixa |

---

## Próximos Passos

- **Observe o que você otimizou:** → [Lab 033 — Observabilidade de Agentes](lab-033-agent-observability.md)
- **Avalie a qualidade após otimização:** → [Lab 035 — Avaliação de Agentes](lab-035-agent-evaluation.md)
- **Deploy completo em produção:** → [Lab 028 — Deploy MCP no Azure](lab-028-deploy-mcp-azure.md)