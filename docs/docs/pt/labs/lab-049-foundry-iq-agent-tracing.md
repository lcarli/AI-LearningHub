---
tags: [observability, opentelemetry, azure-monitor, foundry, python, tracing]
---
# Lab 049: Foundry IQ — Rastreamento de Agentes com OpenTelemetry

<div class="lab-meta">
  <span><strong>Nível:</strong> <span class="level-badge level-300">L300</span></span>
  <span><strong>Trilha:</strong> <a href="../paths/foundry/">🏭 Microsoft Foundry</a></span>
  <span><strong>Tempo:</strong> ~75 min</span>
  <span><strong>💰 Custo:</strong> <span class="level-badge cost-free">Gratuito</span> — Modo local com ConsoleSpanExporter (Azure Monitor opcional)</span>
</div>

## O que Você Vai Aprender

- Como o **OpenTelemetry** fornece observabilidade para agentes de IA (traces, spans, atributos)
- Instrumentar código de agente com as **convenções semânticas GenAI** para chamadas de modelo e uso de ferramentas
- Capturar **uso de tokens, latência e taxas de erro** como telemetria estruturada
- Analisar traces de agentes para identificar problemas de desempenho e fatores de custo
- (Opcional) Exportar traces para o **Azure Monitor / Application Insights** e o **portal Foundry**
- Configurar **controles de privacidade** para gravação de conteúdo

## Introdução

![Arquitetura de Rastreamento Foundry IQ](../../assets/diagrams/foundry-iq-tracing.svg)

Agentes em produção falham silenciosamente. Uma resposta degrada em qualidade — mas ninguém percebe até que um cliente reclame. Os custos disparam porque um prompt ficou longo demais — mas a fatura chega 30 dias depois. Uma chamada de ferramenta começa a expirar — mas o agente retorna uma resposta alternativa em vez de um erro.

**Foundry IQ** é a camada de observabilidade que torna o comportamento do agente visível. Ele usa o **OpenTelemetry** — o framework de observabilidade padrão da indústria — com **convenções semânticas GenAI** que definem exatamente como capturar telemetria específica de IA, como contagens de tokens, nomes de modelos e chamadas de ferramentas.

### O Cenário

O agente de atendimento ao cliente da OutdoorGear Inc. lida com mais de 1.000 consultas por dia. A equipe precisa de:

1. **Rastreamento de latência** — quais consultas demoram mais e por quê?
2. **Visibilidade de custos** — quantos tokens são consumidos e a que custo?
3. **Detecção de erros** — quais traces falham e qual é a causa raiz?
4. **Monitoramento de qualidade** — as respostas estão piorando ao longo do tempo?

Você tem **10 traces de amostra** do agente para analisar, além de um script inicial para adicionar rastreamento ao novo código.

---

## Pré-requisitos

| Requisito | Por quê |
|---|---|
| Python 3.10+ | Executar a análise e instrumentação |
| `pandas` | Analisar dados de traces de amostra |
| `opentelemetry-api`, `opentelemetry-sdk` | Rastreamento local (ConsoleSpanExporter) |
| (Opcional) Projeto Azure AI Foundry | Exportação de traces ao vivo para o portal Foundry |

```bash
pip install pandas opentelemetry-api opentelemetry-sdk
```

Para o modo Azure (opcional):
```bash
pip install azure-ai-projects azure-monitor-opentelemetry opentelemetry-instrumentation-openai-v2
```

---

!!! tip "Início Rápido com GitHub Codespaces"
    [![Open in GitHub Codespaces](https://github.com/codespaces/badge.svg)](https://codespaces.new/lcarli/AI-LearningHub?quickstart=1)

    Todas as dependências estão pré-instaladas no devcontainer.


## 📦 Arquivos de Suporte

!!! note "Baixe estes arquivos antes de iniciar o lab"
    Salve todos os arquivos em uma pasta `lab-049/` no seu diretório de trabalho.

| Arquivo | Descrição | Download |
|------|-------------|----------|
| `broken_tracing.py` | Exercício de correção de bugs (3 bugs + auto-testes) | [📥 Download](https://github.com/lcarli/AI-LearningHub/raw/main/docs/docs/en/labs/lab-049/broken_tracing.py) |
| `sample_traces.csv` | Conjunto de dados | [📥 Download](https://github.com/lcarli/AI-LearningHub/raw/main/docs/docs/en/labs/lab-049/sample_traces.csv) |
| `traced_agent.py` | Script inicial com TODOs | [📥 Download](https://github.com/lcarli/AI-LearningHub/raw/main/docs/docs/en/labs/lab-049/traced_agent.py) |

---

## Passo 1: Entendendo o OpenTelemetry para IA

O OpenTelemetry define três tipos de sinais. Para rastreamento de agentes, focamos em **traces**:

| Sinal | O que Captura | Exemplo de Agente |
|--------|-----------------|---------------|
| **Traces** | Fluxo de requisição de ponta a ponta como uma árvore de spans | Loop do agente → Chamada LLM → Chamada de ferramenta → Resposta |
| **Métricas** | Medições agregadas ao longo do tempo | Consumo de tokens, contagem de requisições, histogramas de latência |
| **Logs** | Eventos discretos | "Agente selecionou ferramenta: search_products" |

### Spans e Atributos

Um **span** representa uma única operação dentro de um trace. Cada span possui:

- **Nome**: ex., `chat gpt-4o`
- **Tipo**: `CLIENT` (chamada de saída para LLM/ferramenta) ou `INTERNAL` (lógica do agente)
- **Duração**: tempo de início até tempo de término
- **Atributos**: metadados chave-valor seguindo as convenções GenAI
- **Status**: `OK` ou `ERROR`
- **Pai**: vincula spans em uma árvore

### Convenções Semânticas GenAI

A comunidade OpenTelemetry define nomes de atributos padrão para operações de IA:

| Atributo | Descrição | Exemplo |
|-----------|-------------|---------|
| `gen_ai.operation.name` | Tipo de operação | `chat` |
| `gen_ai.request.model` | Modelo solicitado | `gpt-4o` |
| `gen_ai.usage.input_tokens` | Tokens de prompt consumidos | `150` |
| `gen_ai.usage.output_tokens` | Tokens de conclusão | `85` |
| `gen_ai.response.finish_reason` | Por que o modelo parou | `stop`, `tool_calls` |
| `gen_ai.system` | Provedor | `openai` |

!!! tip "Por que Padrões Importam"
    Usar convenções semânticas GenAI significa que seus traces são legíveis por **qualquer** backend compatível com OpenTelemetry — Jaeger, Zipkin, Datadog, Azure Monitor, Grafana Tempo — sem análise personalizada.

---

## Passo 2: Analisar Traces de Amostra

Antes de instrumentar o código, vamos analisar dados reais de traces. Carregue os 10 traces de amostra:

```python
import pandas as pd

traces = pd.read_csv("lab-049/sample_traces.csv")
print(f"Loaded {len(traces)} traces")
print(traces[["trace_id", "query_type", "model", "duration_ms", "status"]].to_string(index=False))
```

### 2a — Análise de Latência

```python
avg_latency = traces["duration_ms"].mean()
p95 = traces["duration_ms"].quantile(0.95)
slowest = traces.loc[traces["duration_ms"].idxmax()]

print(f"Average latency:  {avg_latency:.1f} ms  ({avg_latency/1000:.2f}s)")
print(f"P95 latency:      {p95:.0f} ms")
print(f"Slowest trace:    {slowest['trace_id']} at {slowest['duration_ms']} ms ({slowest['status']})")
```

**Esperado:**
```
Average latency:  3150.0 ms  (3.15s)
P95 latency:      7650 ms
Slowest trace:    t006 at 8500 ms (ERROR)
```

### 2b — Uso de Tokens

```python
total_input = traces["input_tokens"].sum()
total_output = traces["output_tokens"].sum()
total_tokens = total_input + total_output

print(f"Total input tokens:  {total_input:,}")
print(f"Total output tokens: {total_output:,}")
print(f"Total tokens:        {total_tokens:,}")

# Cost estimate (gpt-4o pricing: $5/1M input, $15/1M output)
input_cost = total_input / 1_000_000 * 5
output_cost = total_output / 1_000_000 * 15
print(f"Estimated cost:      ${input_cost + output_cost:.4f}")
```

### 2c — Análise de Erros

```python
errors = traces[traces["status"] == "ERROR"]
error_rate = len(errors) / len(traces) * 100
print(f"Error rate: {error_rate:.1f}% ({len(errors)} of {len(traces)} traces)")
if len(errors) > 0:
    print(f"Error types: {errors['error_type'].value_counts().to_dict()}")
```

### 2d — Detalhamento por Tipo de Consulta

```python
by_type = traces.groupby("query_type").agg(
    count=("trace_id", "count"),
    avg_ms=("duration_ms", "mean"),
    avg_tokens=("input_tokens", "mean"),
).reset_index()
print(by_type.to_string(index=False))
```

---

## Passo 3: Instrumentar um Agente (Modo Local)

Abra `lab-049/traced_agent.py` e complete os **5 TODOs**:

| TODO | O que implementar |
|------|------------------|
| TODO 1 | Configurar `TracerProvider` com `ConsoleSpanExporter` |
| TODO 2 | Envolver a chamada LLM em um span com atributos GenAI |
| TODO 3 | Registrar uso de tokens como atributos do span |
| TODO 4 | Criar um span raiz para o loop do agente |
| TODO 5 | Registrar erros com `span.set_status(StatusCode.ERROR)` |

Execute o script inicial para ver a saída de traces no seu console:

```bash
python lab-049/traced_agent.py
```

Antes de completar os TODOs, o script imprime `❌ TODO 1 not implemented`. Após completar o TODO 1, você verá dados de span formatados em JSON impressos no console.

---

## Passo 4: Exportar para o Azure Monitor (Opcional)

Se você tem um projeto Azure AI Foundry, substitua o ConsoleSpanExporter pelo Azure Monitor:

```python
from azure.ai.projects import AIProjectClient
from azure.identity import DefaultAzureCredential
from azure.monitor.opentelemetry import configure_azure_monitor
from opentelemetry.instrumentation.openai_v2 import OpenAIInstrumentor

# Get connection string from Foundry project
project = AIProjectClient(
    credential=DefaultAzureCredential(),
    endpoint="https://<your-resource>.services.ai.azure.com/api/projects/<your-project>",
)
conn_str = project.telemetry.get_application_insights_connection_string()

# Configure Azure Monitor exporter
configure_azure_monitor(connection_string=conn_str)

# Auto-instrument OpenAI SDK
OpenAIInstrumentor().instrument()
```

Em seguida, navegue até **Portal Foundry → Tracing** para ver seus traces em uma linha do tempo visual.

!!! warning "Gravação de Conteúdo"
    Por padrão, o conteúdo das mensagens **NÃO** é gravado nos spans (proteção de privacidade). Para habilitar:

    ```bash
    # PowerShell
    $env:OTEL_INSTRUMENTATION_GENAI_CAPTURE_MESSAGE_CONTENT = "true"

    # Bash
    export OTEL_INSTRUMENTATION_GENAI_CAPTURE_MESSAGE_CONTENT=true
    ```

    ⚠️ Nunca habilite isso em produção com dados de clientes, a menos que você tenha políticas adequadas de tratamento de dados.

---

## Passo 5: Criar Regras de Alerta

Em produção, você configuraria alertas no Azure Monitor para:

| Alerta | Condição | Severidade |
|-------|-----------|----------|
| Alta latência | Duração P95 > 10s | Aviso |
| Pico de erros | Taxa de erro > 5% em 5 min | Crítico |
| Custo de tokens | Custo diário de tokens > $50 | Aviso |
| Queda de qualidade | Pontuação média de avaliação < 0.7 | Crítico |

Esses correspondem a regras de alerta do Azure Monitor usando consultas KQL em dados do Application Insights.

---

## 🐛 Exercício de Correção de Bugs

O arquivo `lab-049/broken_tracing.py` tem **3 bugs** na lógica de análise de traces:

```bash
python lab-049/broken_tracing.py
```

| Teste | O que verifica | Dica |
|------|---------------|------|
| Teste 1 | A latência média deve incluir TODOS os traces | Não filtre por status |
| Teste 2 | O custo de tokens usa taxas diferentes para entrada vs saída | Entrada é mais barata |
| Teste 3 | Denominador da taxa de erro | Divida pelo total, não pelos erros |

---


## 🧠 Verificação de Conhecimento

??? question "**Q1 (Múltipla Escolha):** O que a variável de ambiente `OTEL_INSTRUMENTATION_GENAI_CAPTURE_MESSAGE_CONTENT` controla?"

    - A) Se os traces são exportados para o Azure Monitor
    - B) Se o conteúdo das mensagens de requisição/resposta do LLM é gravado nos spans
    - C) Se os resultados das chamadas de ferramentas são registrados
    - D) O número máximo de spans por trace

    ??? success "✅ Revelar Resposta"
        **Correto: B) Se o conteúdo das mensagens de requisição/resposta do LLM é gravado nos spans**

        Por padrão, o conteúdo das mensagens NÃO é incluído nos spans para proteger a privacidade. Definir essa variável como `true` captura o texto completo do prompt e da conclusão — útil para depuração, mas perigoso em produção com dados reais de clientes.

??? question "**Q2 (Múltipla Escolha):** No OpenTelemetry, qual é o `span kind` correto para a lógica interna de um agente (roteamento, planejamento, raciocínio)?"

    - A) CLIENT
    - B) SERVER
    - C) INTERNAL
    - D) PRODUCER

    ??? success "✅ Revelar Resposta"
        **Correto: C) INTERNAL**

        Spans `INTERNAL` representam operações que não cruzam um limite de rede — como raciocínio do agente, decisões de roteamento e consultas à memória. Spans `CLIENT` são usados para chamadas de saída para LLMs, ferramentas e APIs externas.

??? question "**Q3 (Execute o Lab):** Qual é a duração média dos traces em todos os 10 traces de amostra?"

    Carregue [📥 `sample_traces.csv`](https://github.com/lcarli/AI-LearningHub/raw/main/docs/docs/en/labs/lab-049/sample_traces.csv) e calcule `traces["duration_ms"].mean()`.

    ??? success "✅ Revelar Resposta"
        **3.150,0 ms (3,15 segundos)**

        Soma de todas as durações: 2500+1800+5200+1200+3100+8500+1500+2000+4000+1700 = 31.500 ms ÷ 10 = **3.150 ms**. Note que o trace mais lento (t006, 8500ms) é um ERROR — ele eleva significativamente a média.

??? question "**Q4 (Execute o Lab):** Qual é a contagem total de tokens (entrada + saída) em todos os traces?"

    Some as colunas `input_tokens` e `output_tokens`.

    ??? success "✅ Revelar Resposta"
        **3.255 tokens**

        Entrada: 150+120+350+100+200+500+130+160+280+110 = **2.100**. Saída: 85+60+200+45+120+300+55+90+150+50 = **1.155**. Total: 2.100 + 1.155 = **3.255**.

??? question "**Q5 (Execute o Lab):** Qual trace tem a maior latência e qual é seu status?"

    Encontre a linha com o valor máximo de `duration_ms`.

    ??? success "✅ Revelar Resposta"
        **Trace t006 — 8.500 ms — status: ERROR (timeout)**

        O trace mais lento também é o único erro. Ele tentou 3 chamadas de ferramentas para uma consulta de status de pedido, mas expirou. Esse padrão (lento = erro) é comum — timeouts são uma causa principal tanto de alta latência quanto de erros em sistemas de agentes.

---

## Resumo

| Tópico | O que Você Aprendeu |
|-------|-----------------|
| OpenTelemetry | Framework de observabilidade padrão da indústria (traces, métricas, logs) |
| Convenções GenAI | Atributos padrão para IA: modelo, tokens, chamadas de ferramentas |
| Análise de Traces | Latência, custo de tokens, taxa de erro a partir de dados estruturados de traces |
| Instrumentação | TracerProvider, SpanProcessor, atributos de span |
| Integração Azure | Application Insights, painel de rastreamento do portal Foundry |
| Privacidade | Controles de gravação de conteúdo via variáveis de ambiente |

---

## Próximos Passos

- **[Lab 050](lab-050-multi-agent-observability.md)** — Observabilidade Multi-Agente com Convenções Semânticas GenAI (L400)
- **[Lab 033](lab-033-agent-observability.md)** — Observabilidade de Agentes com Application Insights (abordagem complementar)
- **[Lab 038](lab-038-cost-optimization.md)** — Otimização de Custos de IA (usando dados de traces para reduzir custos)
