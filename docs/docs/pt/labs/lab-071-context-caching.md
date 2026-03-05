---
tags: [caching, cost-optimization, anthropic, google, openai, python]
---
# Lab 071: Cache de Contexto — Reduzindo Custos para Agentes com Documentos Grandes

<div class="lab-meta">
  <span><strong>Nível:</strong> <span class="level-badge level-300">L300</span></span>
  <span><strong>Trilha:</strong> Todas as trilhas</span>
  <span><strong>Tempo:</strong> ~60 min</span>
  <span><strong>💰 Custo:</strong> <span class="level-badge cost-free">Gratuito</span> — Usa dados de benchmark simulados</span>
</div>

## O que Você Vai Aprender

- O que é **cache de contexto** e como os provedores (Anthropic, Google, OpenAI) o implementam
- Como acertos de cache reduzem o **tempo até o primeiro token (TTFT)** e o **custo por requisição**
- Analisar um CSV de benchmark para quantificar economia de latência e custo em 3 provedores
- Identificar quando o cache oferece o maior ROI para cargas de trabalho de agentes com documentos grandes
- Criar um **relatório de desempenho de cache** comparando a economia entre acertos e falhas

## Introdução

Quando um agente processa o mesmo documento de 100 mil tokens em múltiplas rodadas, você paga por esses tokens de entrada toda vez — a menos que use **cache de contexto**. Todos os três principais provedores agora oferecem mecanismos de cache:

| Provedor | Recurso | Como Funciona |
|----------|---------|---------------|
| **Anthropic** | Prompt Caching | Pontos de cache em mensagens de sistema/usuário; tokens em cache cobrados a 10% do preço de entrada |
| **Google** | Context Caching | Criação explícita de cache via API; tokens em cache cobrados a 25% do preço de entrada |
| **OpenAI** | Automatic Caching | Correspondência automática de prefixo para prompts ≥1024 tokens; tokens em cache cobrados a 50% do preço de entrada |

### O Cenário

Você é um **Engenheiro de Plataforma de IA** em uma empresa de tecnologia jurídica. Seu agente de revisão de contratos processa documentos de 150 mil a 200 mil tokens. Cada contrato requer de 3 a 5 perguntas de acompanhamento sobre o mesmo documento. A liderança quer saber: _"Quanto dinheiro e latência podemos economizar habilitando o cache de contexto?"_

Você tem um **dataset de benchmark** (`cache_benchmark.csv`) com 15 requisições em 3 provedores — uma mistura de acertos e falhas de cache. Seu trabalho: analisar os dados e criar um relatório de economia de custos.

!!! info "Dados Simulados"
    Este lab usa um CSV de benchmark simulado para que qualquer pessoa possa acompanhar sem chaves de API. A estrutura dos dados e as proporções de custo refletem o comportamento real de cache da documentação de cada provedor.

## Pré-requisitos

| Requisito | Por quê |
|---|---|
| Python 3.10+ | Executar os scripts de análise |
| Biblioteca `pandas` | Manipulação de dados |

```bash
pip install pandas
```

---

!!! tip "Início Rápido com GitHub Codespaces"
    [![Open in GitHub Codespaces](https://github.com/codespaces/badge.svg)](https://codespaces.new/lcarli/AI-LearningHub?quickstart=1)

    Todas as dependências estão pré-instaladas no devcontainer.


## 📦 Arquivos de Apoio

!!! note "Baixe estes arquivos antes de iniciar o lab"
    Salve todos os arquivos em uma pasta `lab-071/` no seu diretório de trabalho.

| Arquivo | Descrição | Download |
|---------|-----------|----------|
| `broken_cache.py` | Exercício de correção de bugs (3 bugs + autotestes) | [📥 Download](https://github.com/lcarli/AI-LearningHub/raw/main/docs/docs/en/labs/lab-071/broken_cache.py) |
| `cache_benchmark.csv` | Dataset de benchmark | [📥 Download](https://github.com/lcarli/AI-LearningHub/raw/main/docs/docs/en/labs/lab-071/cache_benchmark.csv) |

---

## Etapa 1: Entender a Mecânica do Cache de Contexto

Antes de analisar os dados, entenda os conceitos-chave:

| Conceito | Definição |
|----------|-----------|
| **Falha de Cache (Cache Miss)** | Primeira requisição — contexto completo enviado ao modelo, sem dados em cache |
| **Acerto de Cache (Cache Hit)** | Requisição subsequente — contexto encontrado no cache, processamento de entrada reduzido |
| **TTFT** | Tempo até o primeiro token — quão rápido o modelo começa a responder |
| **Custo de Entrada** | Custo cobrado quando o contexto NÃO está em cache (preço integral) |
| **Custo em Cache** | Custo cobrado quando o contexto ESTÁ em cache (preço com desconto) |

### Insight Principal

Acertos de cache economizam dinheiro de duas formas:

1. **Menor custo por token** — tokens em cache são cobrados a uma fração do preço de entrada
2. **Menor latência** — o modelo não precisa reprocessar o contexto completo, então o TTFT cai drasticamente

---

## Etapa 2: Carregar e Explorar os Dados de Benchmark

O dataset tem **15 requisições** em 3 provedores. Comece carregando-o:

```python
import pandas as pd

df = pd.read_csv("lab-071/cache_benchmark.csv")

print(f"Total requests: {len(df)}")
print(f"Providers: {df['provider'].unique().tolist()}")
print(f"Cache statuses: {df['cache_status'].value_counts().to_dict()}")
print(f"\nColumns: {list(df.columns)}")
print(f"\nFirst 5 rows:\n{df.head()}")
```

**Saída esperada:**

```
Total requests: 15
Providers: ['anthropic', 'google', 'openai']
Cache statuses: {'hit': 9, 'miss': 6}
```

Explore os dados por provedor:

```python
summary = df.groupby("provider").agg(
    requests=("request_id", "count"),
    hits=("cache_status", lambda x: (x == "hit").sum()),
    misses=("cache_status", lambda x: (x == "miss").sum()),
    avg_tokens=("context_tokens", "mean"),
).reset_index()
print(summary)
```

---

## Etapa 3: Analisar o Impacto na Latência — Comparação de TTFT

O maior benefício do cache para o usuário é a **redução de latência**. Compare o TTFT para acertos vs. falhas de cache:

```python
hits = df[df["cache_status"] == "hit"]
misses = df[df["cache_status"] == "miss"]

avg_hit_ttft = hits["ttft_ms"].mean()
avg_miss_ttft = misses["ttft_ms"].mean()
speedup = avg_miss_ttft / avg_hit_ttft

print(f"Avg TTFT (cache hit):  {avg_hit_ttft:.0f} ms")
print(f"Avg TTFT (cache miss): {avg_miss_ttft:.0f} ms")
print(f"Speedup factor:        {speedup:.1f}x faster with cache")
```

**Saída esperada:**

```
Avg TTFT (cache hit):  217 ms
Avg TTFT (cache miss): 2583 ms
Speedup factor:        11.9x faster with cache
```

Agora detalhe por provedor:

```python
ttft_by_provider = df.groupby(["provider", "cache_status"])["ttft_ms"].mean().unstack()
ttft_by_provider["speedup"] = ttft_by_provider["miss"] / ttft_by_provider["hit"]
print(ttft_by_provider.round(0))
```

!!! tip "Insight"
    Acertos de cache são aproximadamente **10–15x mais rápidos** em todos os provedores. Para um agente lidando com perguntas de acompanhamento em um documento grande, isso significa respostas em menos de um segundo em vez de esperas de 2–3 segundos por turno.

---

## Etapa 4: Analisar a Economia de Custos

Agora compute o impacto financeiro. Cada linha tem `input_cost_usd` (cobrado na falha) e `cached_cost_usd` (cobrado no acerto):

```python
total_miss_cost = misses["input_cost_usd"].sum()
total_hit_cost = hits["cached_cost_usd"].sum()
savings = total_miss_cost - total_hit_cost

print(f"Total cost (cache misses): ${total_miss_cost:.2f}")
print(f"Total cost (cache hits):   ${total_hit_cost:.2f}")
print(f"Total savings:             ${savings:.2f}")
print(f"Savings ratio:             {savings / total_miss_cost * 100:.0f}%")
```

**Saída esperada:**

```
Total cost (cache misses): $1.80
Total cost (cache hits):   $0.36
Total savings:             $1.44
Savings ratio:             80%
```

Detalhe por provedor:

```python
cost_by_provider = []
for provider, group in df.groupby("provider"):
    miss_cost = group[group["cache_status"] == "miss"]["input_cost_usd"].sum()
    hit_cost = group[group["cache_status"] == "hit"]["cached_cost_usd"].sum()
    cost_by_provider.append({
        "Provider": provider,
        "Miss Cost": f"${miss_cost:.2f}",
        "Hit Cost": f"${hit_cost:.2f}",
        "Savings": f"${miss_cost - hit_cost:.2f}",
    })

print(pd.DataFrame(cost_by_provider).to_string(index=False))
```

---

## Etapa 5: Calcular a Taxa de Acerto de Cache e Métricas de ROI

```python
hit_rate = len(hits) / len(df) * 100
cost_per_request_with_cache = (total_miss_cost + total_hit_cost) / len(df)
cost_per_request_without_cache = total_miss_cost / len(misses)

print(f"Overall cache hit rate:          {hit_rate:.0f}%")
print(f"Avg cost/request (with cache):   ${cost_per_request_with_cache:.3f}")
print(f"Avg cost/request (without cache):${cost_per_request_without_cache:.3f}")
```

### Projetando a Economia Anual

```python
daily_requests = 500
annual_requests = daily_requests * 365
annual_savings = (savings / len(df)) * annual_requests

print(f"\nProjected annual savings at {daily_requests} requests/day:")
print(f"  ${annual_savings:,.0f}")
```

!!! warning "Considerações do Mundo Real"
    As taxas de acerto de cache dependem dos padrões de uso. Perguntas de acompanhamento sequenciais sobre o mesmo documento obtêm taxas de acerto próximas de 100%. Consultas diversas e não relacionadas podem ter 0% de acertos. Dimensione suas estimativas de economia com base nos padrões reais de conversa do seu agente.

---

## Etapa 6: Criar o Relatório de Desempenho de Cache

Combine toda a análise em um relatório resumido:

```python
report = f"""# 📊 Context Caching Benchmark Report

## Overview
| Metric | Value |
|--------|-------|
| Total Requests | {len(df)} |
| Cache Hits | {len(hits)} ({hit_rate:.0f}%) |
| Cache Misses | {len(misses)} |
| Providers Tested | {', '.join(df['provider'].unique())} |

## Latency Impact
| Metric | Value |
|--------|-------|
| Avg TTFT (hit) | {avg_hit_ttft:.0f} ms |
| Avg TTFT (miss) | {avg_miss_ttft:.0f} ms |
| Speedup | {speedup:.1f}x |

## Cost Impact
| Metric | Value |
|--------|-------|
| Total Miss Cost | ${total_miss_cost:.2f} |
| Total Hit Cost | ${total_hit_cost:.2f} |
| Total Savings | ${savings:.2f} |
| Savings Rate | {savings / total_miss_cost * 100:.0f}% |

## Recommendation
Enable context caching for all large-document agent workflows.
Expected ROI: {savings / total_miss_cost * 100:.0f}% cost reduction, {speedup:.0f}x latency improvement.
"""

print(report)

with open("lab-071/cache_report.md", "w") as f:
    f.write(report)
print("💾 Saved to lab-071/cache_report.md")
```

---

## 🐛 Exercício de Correção de Bugs

O arquivo `lab-071/broken_cache.py` contém **3 bugs** que produzem métricas de cache incorretas. Você consegue encontrar e corrigir todos?

Execute os autotestes para ver quais falham:

```bash
python lab-071/broken_cache.py
```

Você deve ver **3 testes com falha**. Cada teste corresponde a um bug:

| Teste | O que verifica | Dica |
|-------|---------------|------|
| Teste 1 | TTFT médio em cache | Deve calcular a média do TTFT de acertos, não de falhas |
| Teste 2 | Economia total de custos | Deve ser a soma dos custos de entrada das falhas menos a soma dos custos em cache dos acertos |
| Teste 3 | Taxa de acerto de cache | Deve contar acertos / total, não falhas / total |

Corrija todos os 3 bugs e execute novamente. Quando você vir `All passed!`, está pronto!

---


## 🧠 Verificação de Conhecimento

??? question "**Q1 (Múltipla Escolha):** Qual é o principal benefício do cache de contexto para conversas de agente com múltiplos turnos?"

    - A) Melhora a precisão do raciocínio do modelo
    - B) Reduz os custos de tokens de entrada e o tempo até o primeiro token em contextos repetidos
    - C) Permite que o modelo lembre conversas anteriores permanentemente
    - D) Aumenta o tamanho máximo da janela de contexto

    ??? success "✅ Revelar Resposta"
        **Correta: B) Reduz os custos de tokens de entrada e o tempo até o primeiro token em contextos repetidos**

        O cache de contexto armazena tokens de entrada previamente processados para que não precisem ser reenviados e reprocessados. Isso reduz tanto o custo (tokens em cache são cobrados com desconto) quanto a latência (o TTFT cai drasticamente porque o modelo pula a releitura do contexto em cache).

??? question "**Q2 (Múltipla Escolha):** Qual provedor cobra a menor taxa por tokens em cache em relação ao preço integral de entrada?"

    - A) OpenAI (50% do preço de entrada)
    - B) Google (25% do preço de entrada)
    - C) Anthropic (10% do preço de entrada)
    - D) Todos os provedores cobram a mesma taxa para cache

    ??? success "✅ Revelar Resposta"
        **Correta: C) Anthropic (10% do preço de entrada)**

        O prompt caching da Anthropic cobra tokens em cache a apenas 10% do preço padrão de entrada, tornando-o o desconto mais agressivo. Google cobra 25% e OpenAI cobra 50%. No entanto, os modelos de precificação mudam — sempre consulte a documentação mais recente.

??? question "**Q3 (Execute o Lab):** Qual é o TTFT médio para **acertos** de cache em todos os provedores?"

    Execute a análise da Etapa 3 no [📥 `cache_benchmark.csv`](https://github.com/lcarli/AI-LearningHub/raw/main/docs/docs/en/labs/lab-071/cache_benchmark.csv) e verifique os resultados.

    ??? success "✅ Revelar Resposta"
        **217 ms**

        As 9 requisições com acerto de cache têm TTFTs de 180, 175, 190, 220, 210, 230, 250, 240 e 260 ms. A média é (180+175+190+220+210+230+250+240+260) ÷ 9 = **217 ms** (arredondado).

??? question "**Q4 (Execute o Lab):** Qual é o TTFT médio para **falhas** de cache em todos os provedores?"

    Execute a análise da Etapa 3 para descobrir.

    ??? success "✅ Revelar Resposta"
        **2583 ms**

        As 6 requisições com falha de cache têm TTFTs de 2800, 2750, 3200, 3100, 1800 e 1850 ms. A média é (2800+2750+3200+3100+1800+1850) ÷ 6 = **2583 ms** (arredondado).

??? question "**Q5 (Execute o Lab):** Qual é a economia total de custos (custos de falha menos custos de acerto) em todas as 15 requisições?"

    Execute a análise da Etapa 4 para calcular.

    ??? success "✅ Revelar Resposta"
        **$1,44**

        Custos totais de entrada das falhas = $0,45 + $0,45 + $0,20 + $0,20 + $0,25 + $0,25 = **$1,80**. Custos totais em cache dos acertos = $0,045×3 + $0,05×3 + $0,025×3 = $0,135 + $0,15 + $0,075 = **$0,36**. Economia = $1,80 − $0,36 = **$1,44**.

---

## Resumo

| Tópico | O que Você Aprendeu |
|--------|---------------------|
| Cache de Contexto | Armazena tokens de entrada processados para evitar reenvio em requisições de acompanhamento |
| Impacto no TTFT | Acertos de cache reduzem o TTFT em ~12x (de ~2,6s para ~217ms) |
| Economia de Custos | 80% de redução de custo em requisições com cache em todos os provedores |
| Comparação de Provedores | Anthropic (10%), Google (25%), OpenAI (50%) de desconto em tokens em cache |
| Análise de ROI | Como projetar economia com base no volume de requisições e taxas de acerto |
| Metodologia de Benchmark | Estruturação de experimentos de cache com rastreamento de acertos/falhas |

---

## Próximos Passos

- **[Lab 038](lab-038-cost-optimization.md)** — Otimização de Custos de IA (estratégias de custo mais amplas além do cache)
- **[Lab 019](lab-019-streaming-responses.md)** — Respostas em Streaming (otimização complementar de latência)
- **[Lab 033](lab-033-agent-observability.md)** — Observabilidade de Agentes (monitorar taxas de acerto de cache em produção)
- **[Lab 072](lab-072-structured-outputs.md)** — Saídas Estruturadas (JSON garantido para pipelines de agentes com custo eficiente)
