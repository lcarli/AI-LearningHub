---
tags: [observability, opentelemetry, multi-agent, genai-conventions, azure-monitor, foundry, python]
---
# Lab 050: Observabilidade Multi-Agente com Convenções Semânticas GenAI

<div class="lab-meta">
  <span><strong>Nível:</strong> <span class="level-badge level-400">L400</span></span>
  <span><strong>Trilha:</strong> <a href="../paths/foundry/">🏭 Microsoft Foundry</a></span>
  <span><strong>Tempo:</strong> ~120 min</span>
  <span><strong>💰 Custo:</strong> <span class="level-badge cost-free">Gratuito</span> — Análise de traces offline com conjunto de dados fornecido (Azure Monitor opcional)</span>
</div>

## O que Você Vai Aprender

- Aplicar **convenções semânticas GenAI** a sistemas multi-agente: spans de agente, spans de modelo, spans de ferramenta
- Rastrear **transferências entre agentes**, decisões de roteamento e padrões de reprocessamento
- Distinguir spans `INTERNAL` (lógica do agente) vs `CLIENT` (chamadas LLM/ferramenta)
- Analisar **pontuações de qualidade**, **custos de tokens** e **latência** em um pipeline multi-agente
- Construir **métricas de dashboard** de observabilidade a partir de dados brutos de spans
- Entender como as convenções padronizam a telemetria entre **Foundry, Semantic Kernel, LangChain, AutoGen**

!!! abstract "Pré-requisito"
    Complete o **[Lab 049: Foundry IQ — Rastreamento de Agentes](lab-049-foundry-iq-agent-tracing.md)** primeiro. Este lab pressupõe familiaridade com spans, atributos e convenções GenAI do OpenTelemetry.

## Introdução

![Rastreamento Multi-Agente](../../assets/diagrams/multi-agent-tracing.svg)

O rastreamento de agente único é difícil. O rastreamento **multi-agente** é exponencialmente mais difícil. Quando um Roteador transfere para um Especialista, que chama ferramentas, que passa resultados para um Revisor — você precisa de uma forma padrão de capturar cada etapa para poder reconstruir o fluxo completo de execução.

As **convenções semânticas GenAI do OpenTelemetry** resolvem isso com três tipos de spans:

| Tipo de Span | Tipo | Atributos Principais | Exemplo |
|-----------|------|----------------|---------|
| **Span de Agente** | `INTERNAL` | `gen_ai.agent.name`, `gen_ai.agent.id` | Router, ProductSpec, Reviewer |
| **Span de Modelo** | `CLIENT` | `gen_ai.request.model`, `gen_ai.usage.*_tokens` | `chat gpt-4o` |
| **Span de Ferramenta** | `CLIENT` | `gen_ai.tool.name` | `search_products` |

### O Cenário

A OutdoorGear Inc. fez upgrade para um **sistema multi-agente** com 4 agentes especialistas orquestrados por um Roteador:

1. **Agente Roteador** — classifica consultas recebidas e despacha para o especialista correto
2. **Especialista em Produtos** — lida com busca de produtos e recomendações
3. **Especialista em Pedidos** — processa status de pedidos e consultas de envio
4. **Especialista em Suporte** — lida com reclamações e questões sensíveis
5. **Agente Revisor** — verifica cada resposta quanto à qualidade e conformidade com políticas

Você tem **5 traces complexos** com 46 spans mostrando o pipeline completo de agentes, incluindo um trace com **revisão falha e reprocessamento**.

---

## Pré-requisitos

| Requisito | Por quê |
|---|---|
| Python 3.10+ | Executar scripts de análise |
| `pandas` | Analisar dados de spans |
| Lab 049 concluído | Entendimento dos conceitos básicos do OpenTelemetry |

```bash
pip install pandas
```

---

!!! tip "Início Rápido com GitHub Codespaces"
    [![Open in GitHub Codespaces](https://github.com/codespaces/badge.svg)](https://codespaces.new/lcarli/AI-LearningHub?quickstart=1)

    Todas as dependências estão pré-instaladas no devcontainer.


## 📦 Arquivos de Suporte

!!! note "Baixe estes arquivos antes de iniciar o lab"
    Salve todos os arquivos em uma pasta `lab-050/` no seu diretório de trabalho.

| Arquivo | Descrição | Download |
|------|-------------|----------|
| `broken_conventions.py` | Exercício de correção de bugs (3 bugs + auto-testes) | [📥 Download](https://github.com/lcarli/AI-LearningHub/raw/main/docs/docs/en/labs/lab-050/broken_conventions.py) |
| `dashboard_builder.py` | Script inicial com TODOs | [📥 Download](https://github.com/lcarli/AI-LearningHub/raw/main/docs/docs/en/labs/lab-050/dashboard_builder.py) |
| `multi_agent_spans.csv` | Conjunto de dados | [📥 Download](https://github.com/lcarli/AI-LearningHub/raw/main/docs/docs/en/labs/lab-050/multi_agent_spans.csv) |

---

## Passo 1: Entendendo a Estrutura de Traces Multi-Agente

Em um sistema multi-agente, o trace forma uma **árvore**:

```
root: router_agent (INTERNAL)
├── classify_query (CLIENT, gpt-4o-mini)
├── product_specialist (INTERNAL)
│   ├── search_reasoning (CLIENT, gpt-4o)
│   ├── search_products (CLIENT, tool)
│   └── format_response (CLIENT, gpt-4o)
└── reviewer (INTERNAL)
    └── quality_check (CLIENT, gpt-4o-mini)
```

Convenções principais:

- **Spans de agente** são `INTERNAL` — representam a lógica e orquestração próprias do agente
- **Chamadas LLM** são `CLIENT` — requisições de saída para endpoints de modelo
- **Chamadas de ferramenta** são `CLIENT` — requisições de saída para ferramentas/APIs
- Relacionamentos **pai-filho** mostram a cadeia de transferência
- **`gen_ai.agent.name`** é definido APENAS em spans de agente, não em spans de LLM/ferramenta

!!! tip "Por que `INTERNAL` para Agentes?"
    A tomada de decisão de um agente acontece localmente (roteamento, planejamento, recuperação de memória). Não cruza um limite de rede — então é `INTERNAL`. A chamada LLM que o agente *faz* é `CLIENT` porque vai pela rede até uma API.

---

## Passo 2: Carregar e Explorar os Dados de Traces

O conjunto de dados tem **46 spans** em **5 traces**:

```python
import pandas as pd

spans = pd.read_csv("lab-050/multi_agent_spans.csv")
print(f"Total spans: {len(spans)}")
print(f"Traces: {spans['trace_id'].nunique()}")
print(f"\nSpans per trace:")
print(spans.groupby("trace_id")["span_id"].count())
```

**Esperado:**

| Trace | Spans | Cenário |
|-------|-------|----------|
| A001 | 8 | Busca de produto (simples) |
| A002 | 10 | Consulta de pedido complexa |
| A003 | 9 | Tratamento de reclamação |
| A004 | 5 | FAQ (sem revisor) |
| A005 | 14 | Reembolso com revisão falha + reprocessamento |

---

## Passo 3: Análise de Spans de Agente

Extraia e analise os spans de agente:

```python
agent_spans = spans[(spans["kind"] == "INTERNAL") & (spans["agent_name"].notna())]
print(f"Total agent spans: {len(agent_spans)}")
print(f"Unique agents: {sorted(agent_spans['agent_name'].unique())}")
print(f"\nSpans per agent:")
print(agent_spans["agent_name"].value_counts().sort_index())
```

**Esperado:**

```
Total agent spans: 16
Unique agents: ['FAQSpec', 'OrderSpec', 'ProductSpec', 'RefundSpec', 'Reviewer', 'Router', 'SupportSpec']

Reviewer     5
Router       5
RefundSpec   2
...
```

!!! tip "Insight"
    **Router aparece em todos os 5 traces** — é o ponto de entrada. **Reviewer aparece em 4 traces** (não no A004, o FAQ simples). **RefundSpec aparece duas vezes** no trace A005 porque a primeira tentativa falhou na revisão e foi reprocessada.

---

## Passo 4: Análise de Uso de Tokens LLM

Analise o consumo de tokens em todas as chamadas de modelo:

```python
llm_spans = spans[spans["model"].notna()]
print(f"Total LLM calls: {len(llm_spans)}")

by_model = llm_spans.groupby("model").agg(
    calls=("span_id", "count"),
    total_input=("input_tokens", "sum"),
    total_output=("output_tokens", "sum"),
).reset_index()
by_model["total_tokens"] = by_model["total_input"] + by_model["total_output"]
print(by_model.to_string(index=False))

total_tokens = int(llm_spans["input_tokens"].sum() + llm_spans["output_tokens"].sum())
print(f"\nGrand total: {total_tokens:,} tokens")
```

**Esperado:**

| Modelo | Chamadas | Entrada | Saída | Total |
|-------|-------|-------|--------|-------|
| gpt-4o | 12 | 3.830 | 1.890 | 5.720 |
| gpt-4o-mini | 10 | 1.045 | 177 | 1.222 |
| **Total** | **22** | **4.875** | **2.067** | **6.942** |

!!! tip "Insight de Custo"
    O gpt-4o lida com o raciocínio pesado (82% dos tokens) enquanto o gpt-4o-mini faz classificação leve e verificações de qualidade (18%). Este é um padrão eficiente em custos — use modelos caros apenas para raciocínio complexo.

---

## Passo 5: Análise de Chamadas de Ferramentas

```python
tool_spans = spans[spans["tool_name"].notna()]
print(f"Total tool calls: {len(tool_spans)}")
print(f"\nTools used:")
print(tool_spans["tool_name"].value_counts())

trace_tools = tool_spans.groupby("trace_id").size()
print(f"\nTrace with most tool calls: {trace_tools.idxmax()} ({trace_tools.max()} calls)")
```

**Esperado:**

```
Total tool calls: 8

search_products         1
get_order_status        1
get_shipping_info       1
calculate_eta           1
get_customer_history    1
search_faq              1
get_order_details       1
check_refund_policy     1

Trace with most tool calls: A002 (3 calls)
```

---

## Passo 6: Análise de Pontuação de Qualidade

Agentes revisores atribuem pontuações de qualidade. Analise-as:

```python
quality_spans = spans[spans["quality_score"].notna()]
print(f"Quality assessments: {len(quality_spans)}")
print(f"Average quality:     {quality_spans['quality_score'].mean():.3f}")
print(f"Min quality:         {quality_spans['quality_score'].min():.2f}")
print(f"Max quality:         {quality_spans['quality_score'].max():.2f}")

# Traces that fell below the quality threshold
below_threshold = quality_spans[quality_spans["quality_score"] < 0.8]
print(f"\nTraces below 0.8 threshold: {below_threshold['trace_id'].unique().tolist()}")
```

**Esperado:**

```
Quality assessments: 5
Average quality:     0.790
Min quality:         0.45
Max quality:         0.95

Traces below 0.8 threshold: ['A003', 'A005']
```

### Investigando a Revisão Falha (Trace A005)

```python
a005 = spans[spans["trace_id"] == "A005"].sort_values("span_id")
print(a005[["span_id", "span_name", "agent_name", "kind", "quality_score", "status"]]
      .to_string(index=False))
```

Isso mostra o **padrão de reprocessamento**: a primeira verificação do revisor (s40) pontuou 0.45 com status ERROR. O Especialista em Reembolso foi reinvocado (s42), produziu uma resposta revisada, e a segunda verificação do revisor (s45) passou com 0.85.

---

## Passo 7: Construir Métricas de Dashboard

Combine tudo em um resumo de dashboard:

```python
# Overall metrics
total_traces = spans["trace_id"].nunique()
total_spans = len(spans)
total_agent_spans = len(agent_spans)
total_llm_calls = len(llm_spans)
total_tools = len(tool_spans)
error_spans = spans[spans["status"] == "ERROR"]
avg_quality = quality_spans["quality_score"].mean()
dashboard = f"""
╔══════════════════════════════════════════════════╗
║         Multi-Agent Observability Dashboard      ║
╠══════════════════════════════════════════════════╣
║ Traces:           {total_traces:>5}                          ║
║ Total Spans:      {total_spans:>5}                          ║
║ Agent Spans:      {total_agent_spans:>5}  (INTERNAL)                ║
║ LLM Calls:        {total_llm_calls:>5}  (CLIENT)                  ║
║ Tool Calls:       {total_tools:>5}  (CLIENT)                  ║
║ Error Spans:      {len(error_spans):>5}                          ║
║ Total Tokens:     {total_tokens:>5,}                        ║
║ Avg Quality:      {avg_quality:>5.3f}                        ║
║ Below Threshold:  {len(below_threshold):>5}  traces                  ║
╚══════════════════════════════════════════════════╝
"""
print(dashboard)
```

---

## 🐛 Exercício de Correção de Bugs

O arquivo `lab-050/broken_conventions.py` tem **3 bugs** em como ele interpreta as convenções semânticas GenAI:

```bash
python lab-050/broken_conventions.py
```

| Teste | O que verifica | Dica |
|------|---------------|------|
| Teste 1 | Nomes de agentes vêm de `agent_name`, não de `span_name` | Qual coluna tem a identidade do agente? |
| Teste 2 | Spans de agente devem ser do tipo `INTERNAL` E ter um `agent_name` | Não conte spans de LLM/ferramenta |
| Teste 3 | Total de tokens = entrada + saída | Não esqueça output_tokens |

---


## 🧠 Verificação de Conhecimento

??? question "**Q1 (Múltipla Escolha):** Nas convenções semânticas GenAI, qual tipo de span deve ser usado para a lógica interna de roteamento/planejamento de um agente?"

    - A) CLIENT — porque o agente é um cliente do LLM
    - B) SERVER — porque o agente serve requisições de usuários
    - C) INTERNAL — porque o roteamento acontece localmente, não pela rede
    - D) PRODUCER — porque o agente produz respostas

    ??? success "✅ Revelar Resposta"
        **Correto: C) INTERNAL**

        A tomada de decisão do agente (roteamento, planejamento, recuperação de memória) acontece dentro do processo — não cruza um limite de rede. `CLIENT` é usado para chamadas de saída para LLMs e ferramentas. A convenção é: lógica do agente = `INTERNAL`, chamadas externas = `CLIENT`.

??? question "**Q2 (Múltipla Escolha):** Por que o trace A005 tem 14 spans enquanto o A001 tem apenas 8?"

    - A) A005 usa um modelo maior
    - B) A005 teve uma revisão de qualidade falha e precisou de um loop de reprocessamento
    - C) A005 tem mais tokens de entrada do usuário
    - D) A005 usa um algoritmo de roteamento diferente

    ??? success "✅ Revelar Resposta"
        **Correto: B) A005 teve uma revisão de qualidade falha e precisou de um loop de reprocessamento**

        O Revisor pontuou a primeira resposta do A005 em 0.45 (ERROR). O sistema reinvocou o Especialista em Reembolso para revisar a resposta, então o Revisor verificou novamente (pontuação: 0.85, OK). Esse reprocessamento adicionou spans extras: segundo especialista (2 chamadas LLM) + segundo revisor (1 chamada LLM) = 5 spans adicionais.

??? question "**Q3 (Execute o Lab):** Quantos spans de agente totais (kind=INTERNAL com um agent_name) existem em todos os 5 traces?"

    Filtre o DataFrame de spans por `kind == "INTERNAL"` e `agent_name` não nulo.

    ??? success "✅ Revelar Resposta"
        **16 spans de agente**

        Em 5 traces: A001(3) + A002(3) + A003(3) + A004(2) + A005(5) = **16**. A004 tem menos porque pula o Revisor. A005 tem mais por causa do reprocessamento (RefundSpec×2 + Reviewer×2).

??? question "**Q4 (Execute o Lab):** Qual trace tem mais chamadas de ferramentas, e quantas?"

    Agrupe spans de ferramentas por `trace_id` e encontre o máximo.

    ??? success "✅ Revelar Resposta"
        **Trace A002 — 3 chamadas de ferramentas**

        A002 (consulta de pedido complexa) chamou: `get_order_status`, `get_shipping_info` e `calculate_eta`. Este é o trace mais intensivo em ferramentas. A005 tem 2 chamadas de ferramentas, e os demais têm 1 cada.

??? question "**Q5 (Execute o Lab):** Qual é a pontuação média de qualidade em todas as avaliações do revisor?"

    Filtre por spans com `quality_score` não nulo e calcule a média.

    ??? success "✅ Revelar Resposta"
        **0,790**

        Pontuações de qualidade dos spans do revisor: A001 (0,95), A002 (0,92), A003 (0,78), A005-primeiro (0,45), A005-reprocessamento (0,85). A004 (FAQ) não tem revisor. Os dados têm 5 entradas de quality_score. Média = (0,95 + 0,92 + 0,78 + 0,45 + 0,85) / 5 = **0,790**. Dois traces (A003 e A005) ficaram abaixo do limiar de qualidade de 0,8.

---

## Resumo

| Tópico | O que Você Aprendeu |
|-------|-----------------|
| Convenções GenAI | Atributos padrão: agent.name, request.model, usage.tokens |
| Tipos de Span | INTERNAL (lógica do agente) vs CLIENT (chamadas LLM/ferramenta) |
| Hierarquia de Traces | Spans pai-filho mostrando transferências entre agentes |
| Padrões de Reprocessamento | Revisões falhas disparam loops de reprocessamento (visíveis nos traces) |
| Métricas de Dashboard | Contagens de agentes, uso de tokens, chamadas de ferramentas, pontuações de qualidade |
| Cross-Framework | Mesmas convenções funcionam em Foundry, SK, LangChain, AutoGen |

---

## Próximos Passos

- **[Lab 033](lab-033-agent-observability.md)** — Observabilidade de Agentes com Application Insights (abordagem complementar nativa do Azure)
- **[Lab 034](lab-034-multi-agent-sk.md)** — Orquestração Multi-Agente com Semantic Kernel (construa os agentes que este lab rastreia)
- **[Lab 035](lab-035-agent-evaluation.md)** — Avaliação de Agentes com Azure AI Eval SDK (pontuação de qualidade que alimenta o Revisor)
