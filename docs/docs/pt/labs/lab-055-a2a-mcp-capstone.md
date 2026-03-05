---
tags: [a2a, mcp, multi-agent, architecture, capstone, python]
---
# Lab 055: A2A + MCP Full Stack — Capstone de Interoperabilidade de Agentes

<div class="lab-meta">
  <span><strong>Nível:</strong> <span class="level-badge level-400">L400</span></span>
  <span><strong>Trilha:</strong> <a href="../paths/pro-code/">⚙️ Pro Code</a></span>
  <span><strong>Tempo:</strong> ~120 min</span>
  <span><strong>💰 Custo:</strong> <span class="level-badge cost-free">Gratuito</span> — Usa dados de trace simulados (sem necessidade de recursos na nuvem)</span>
</div>

!!! tip "Os Três Protocolos Agênticos"
    Este capstone cobre A2A + MCP. O terceiro protocolo — **AG-UI** (interação agente↔usuário) — é abordado no **[Lab 077](lab-077-agui-protocol.md)**.

## O Que Você Vai Aprender

- Como **A2A + MCP** trabalham juntos em uma arquitetura multi-agente full-stack
- Analisar um **sistema de planejamento de viagens** com 3 agentes especializados usando traces de delegação
- Distinguir **chamadas A2A** (delegação agente-para-agente) de **chamadas MCP** (acesso agente-para-ferramenta)
- Realizar **análise de custo de tokens** em um sistema de agentes distribuído
- Entender **tratamento de erros e padrões de retry** em fluxos de trabalho multi-agente
- Aplicar **princípios de design** para construir arquiteturas de agentes prontas para produção

## Introdução

A2A e MCP são **protocolos complementares** que desempenham papéis diferentes em um sistema multi-agente:

| Protocolo | Papel | Exemplo |
|-----------|-------|---------|
| **A2A** | Delegação de tarefas agente-para-agente | Coordenador pede ao FlightAgent para encontrar voos |
| **MCP** | Acesso agente-para-ferramenta | FlightAgent chama uma API de reservas via servidor MCP |

Neste lab capstone, você vai analisar um **sistema de planejamento de viagens** que usa ambos os protocolos. O agente Coordenador recebe uma requisição do cliente e delega sub-tarefas para agentes especializados via A2A. Cada agente especializado então usa MCP para acessar suas ferramentas e APIs de back-end.

### A Arquitetura

```
                        Customer Request
                              │
                              ▼
                    ┌──────────────────┐
                    │   Coordinator    │
                    │   Agent          │
                    └──────┬───────────┘
                           │ A2A
           ┌───────────────┼───────────────┐
           ▼               ▼               ▼
    ┌─────────────┐ ┌─────────────┐ ┌──────────────┐
    │ FlightAgent │ │ HotelAgent  │ │ Itinerary    │
    │             │ │             │ │ Agent        │
    └──────┬──────┘ └──────┬──────┘ └──────┬───────┘
      MCP  │          MCP  │          MCP  │
           ▼               ▼               ▼
    ┌─────────────┐ ┌─────────────┐ ┌──────────────┐
    │ booking_api │ │ booking_api │ │ maps_api     │
    │ pricing_api │ │ reviews_api │ │ calendar_api │
    │ payment_api │ │             │ │ weather_api  │
    └─────────────┘ └─────────────┘ └──────────────┘
```

O dataset de traces de delegação (`delegation_traces.csv`) captura **20 eventos** de uma sessão completa de planejamento de viagem — 8 chamadas A2A entre agentes e 12 chamadas MCP de agentes para ferramentas.

!!! info "Por Que Dois Protocolos?"
    A2A lida com a camada *social* — agentes descobrindo, negociando e delegando tarefas a pares. MCP lida com a camada de *ferramentas* — agentes acessando bancos de dados, APIs e serviços externos. Separar essas responsabilidades permite escalabilidade independente, limites de segurança e evolução de protocolo.

## Pré-requisitos

| Requisito | Motivo |
|---|---|
| Python 3.10+ | Analisar traces de delegação |
| Biblioteca `pandas` | Operações com DataFrame nos dados de trace |

```bash
pip install pandas
```

---

!!! tip "Início Rápido com GitHub Codespaces"
    [![Open in GitHub Codespaces](https://github.com/codespaces/badge.svg)](https://codespaces.new/lcarli/AI-LearningHub?quickstart=1)

    Todas as dependências estão pré-instaladas no devcontainer.


## 📦 Arquivos de Apoio

!!! note "Baixe estes arquivos antes de iniciar o lab"
    Salve todos os arquivos em uma pasta `lab-055/` no seu diretório de trabalho.

| Arquivo | Descrição | Download |
|---------|-----------|----------|
| `broken_delegation.py` | Exercício de correção de bugs (3 bugs + auto-testes) | [📥 Download](https://github.com/lcarli/AI-LearningHub/raw/main/docs/docs/en/labs/lab-055/broken_delegation.py) |
| `delegation_traces.csv` | Dataset | [📥 Download](https://github.com/lcarli/AI-LearningHub/raw/main/docs/docs/en/labs/lab-055/delegation_traces.csv) |

---

## Etapa 1: Entendendo a Arquitetura

Antes de mergulhar nos dados, entenda o que cada componente faz:

### Papéis dos Agentes

| Agente | Papel A2A | Ferramentas MCP |
|--------|-----------|-----------------|
| **Coordinator** | Recebe requisição do cliente, delega para especialistas | Nenhuma (apenas orquestração) |
| **FlightAgent** | Encontra e reserva voos | `booking_api`, `pricing_api`, `payment_api` |
| **HotelAgent** | Encontra e reserva hotéis | `booking_api`, `reviews_api` |
| **ItineraryAgent** | Planeja e atualiza itinerários | `maps_api`, `calendar_api`, `weather_api` |

### Fluxo de Chamadas

1. Cliente envia uma requisição de viagem para o **Coordinator**
2. Coordinator usa **A2A** para delegar sub-tarefas (encontrar voos, encontrar hotéis, planejar itinerário)
3. Cada especialista usa **MCP** para chamar suas ferramentas de back-end
4. Resultados fluem de volta via A2A para o Coordinator
5. Coordinator monta a resposta final

### Limites de Protocolo

| Limite | Protocolo | Autenticação |
|--------|-----------|--------------|
| Cliente → Coordinator | HTTP/API | API key |
| Coordinator → Especialistas | **A2A** | OAuth 2.0 |
| Especialistas → Ferramentas | **MCP** | Tokens serviço-para-serviço |

!!! tip "OAuth Através dos Limites A2A"
    Quando o Coordinator delega para o FlightAgent via A2A, ele deve passar um token OAuth com escopo nas permissões do cliente. O FlightAgent então usa um token de serviço *separado* para suas chamadas MCP à API de reservas. Esse modelo de autenticação em duas camadas previne escalonamento de privilégios.

---

## Etapa 2: Carregar e Explorar Traces de Delegação

Carregue os dados de trace contendo todos os 20 eventos da sessão de planejamento de viagem:

```python
import pandas as pd

traces = pd.read_csv("lab-055/delegation_traces.csv")
print(f"Total events: {len(traces)}")
print(f"Unique request IDs: {traces['request_id'].nunique()}")
print(f"Protocols: {traces['protocol'].unique().tolist()}")
print(f"Statuses: {traces['status'].unique().tolist()}")
print(f"\nFirst 5 events:")
print(traces.head().to_string(index=False))
```

**Saída esperada:**

```
Total events: 20
Unique request IDs: 8
Protocols: ['A2A', 'MCP']
Statuses: ['OK', 'ERROR']

First 5 events:
request_id source_agent target_agent protocol        action  duration_ms  tokens_used status
      R001  Coordinator  FlightAgent      A2A  find_flights         2500          450     OK
      R001  FlightAgent  booking_api      MCP search_flights        1800            0     OK
      R001  FlightAgent  pricing_api      MCP    get_prices          600            0     OK
      R002  Coordinator   HotelAgent      A2A   find_hotels         3200          520     OK
      R002   HotelAgent  booking_api      MCP search_hotels         2400            0     OK
```

---

## Etapa 3: Analisar Padrões de Chamadas A2A vs MCP

Separe os traces por protocolo para entender a estrutura de delegação:

### 3a — Contagem de Chamadas por Protocolo

```python
a2a_calls = traces[traces["protocol"] == "A2A"]
mcp_calls = traces[traces["protocol"] == "MCP"]

print(f"A2A calls (agent → agent): {len(a2a_calls)}")
print(f"MCP calls (agent → tool):  {len(mcp_calls)}")
print(f"Total calls:               {len(traces)}")
```

**Saída esperada:**

```
A2A calls (agent → agent): 8
MCP calls (agent → tool):  12
Total calls:               20
```

### 3b — Detalhamento da Delegação A2A

```python
print("A2A Delegations (Coordinator → Specialists):")
print(a2a_calls[["request_id", "source_agent", "target_agent", "action", "status"]].to_string(index=False))
```

**Saída esperada:**

```
A2A Delegations (Coordinator → Specialists):
request_id source_agent   target_agent           action status
      R001  Coordinator    FlightAgent     find_flights     OK
      R002  Coordinator     HotelAgent      find_hotels     OK
      R003  Coordinator ItineraryAgent   plan_itinerary     OK
      R004  Coordinator    FlightAgent     book_flight      OK
      R005  Coordinator     HotelAgent      book_hotel      OK
      R006  Coordinator    FlightAgent     find_flights  ERROR
      R007  Coordinator ItineraryAgent update_itinerary     OK
      R008  Coordinator     HotelAgent     cancel_hotel     OK
```

### 3c — Uso de Ferramentas MCP por Agente

```python
print("MCP tool calls per agent:")
print(mcp_calls.groupby("source_agent")["action"].count().to_string())
print(f"\nUnique MCP tools used: {mcp_calls['target_agent'].nunique()}")
```

**Saída esperada:**

```
MCP tool calls per agent:
source_agent
FlightAgent       5
HotelAgent        3
ItineraryAgent    4

Unique MCP tools used: 7
```

### 3d — Análise de Erros

```python
errors = traces[traces["status"] == "ERROR"]
print(f"Total errors: {len(errors)}")
print(f"\nFailed events:")
print(errors[["request_id", "source_agent", "target_agent", "protocol", "action"]].to_string(index=False))
```

**Saída esperada:**

```
Total errors: 2

Failed events:
request_id source_agent target_agent protocol         action
      R006  Coordinator  FlightAgent      A2A   find_flights
      R006  FlightAgent  booking_api      MCP search_flights
```

!!! warning "Falhas em Cascata"
    Observe que R006 tem erros *tanto* na chamada A2A quanto na chamada MCP. Quando a ferramenta MCP `booking_api` falha, o FlightAgent não consegue completar a tarefa A2A — o erro propaga em cascata. Sistemas em produção precisam de lógica de retry e circuit breakers em ambos os limites de protocolo.

---

## Etapa 4: Análise de Custo de Tokens

Chamadas A2A consomem tokens de LLM (agentes raciocinam sobre tarefas), enquanto chamadas MCP são tipicamente isentas de tokens (chamadas diretas a APIs):

```python
total_tokens = traces["tokens_used"].sum()
a2a_tokens = a2a_calls["tokens_used"].sum()
mcp_tokens = mcp_calls["tokens_used"].sum()

print(f"Total tokens consumed: {total_tokens}")
print(f"  A2A tokens: {a2a_tokens} ({a2a_tokens/total_tokens*100:.0f}%)")
print(f"  MCP tokens: {mcp_tokens} ({mcp_tokens/total_tokens*100:.0f}%)")

print(f"\nTokens per A2A call:")
print(a2a_calls[["request_id", "action", "tokens_used"]].to_string(index=False))
```

**Saída esperada:**

```
Total tokens consumed: 3330
  A2A tokens: 3330 (100%)
  MCP tokens: 0 (0%)

Tokens per A2A call:
request_id           action  tokens_used
      R001     find_flights          450
      R002      find_hotels          520
      R003   plan_itinerary          680
      R004      book_flight          380
      R005       book_hotel          350
      R006     find_flights          460
      R007 update_itinerary          290
      R008     cancel_hotel          200
```

### Detalhamento de Custos

```python
COST_PER_1K_TOKENS = 0.005  # example: GPT-4o-mini pricing

cost = total_tokens / 1000 * COST_PER_1K_TOKENS
print(f"Estimated cost at ${COST_PER_1K_TOKENS}/1K tokens: ${cost:.4f}")
print(f"Average tokens per A2A call: {a2a_tokens / len(a2a_calls):.0f}")
print(f"Most expensive call: {a2a_calls.loc[a2a_calls['tokens_used'].idxmax(), 'action']} "
      f"({a2a_calls['tokens_used'].max()} tokens)")
```

---

## Etapa 5: Tratamento de Erros e Padrões de Retry

Analise como erros se propagam e projete estratégias de retry:

### 5a — Taxa de Erro por Protocolo

```python
for protocol in ["A2A", "MCP"]:
    subset = traces[traces["protocol"] == protocol]
    error_count = (subset["status"] == "ERROR").sum()
    total = len(subset)
    print(f"{protocol}: {error_count}/{total} errors ({error_count/total*100:.0f}%)")
```

**Saída esperada:**

```
A2A: 1/8 errors (12%)
MCP: 1/12 errors (8%)
```

### 5b — Análise de Latência

```python
print("Average latency by protocol:")
print(traces.groupby("protocol")["duration_ms"].mean().to_string())

print(f"\nSlowest call: {traces.loc[traces['duration_ms'].idxmax(), 'action']} "
      f"({traces['duration_ms'].max()} ms)")
print(f"Fastest call: {traces.loc[traces['duration_ms'].idxmin(), 'action']} "
      f"({traces['duration_ms'].min()} ms)")
```

### 5c — Padrões de Design para Retry

| Padrão | Camada A2A | Camada MCP |
|--------|------------|------------|
| **Retry** | Retentar a tarefa A2A completa com backoff exponencial | Retentar a chamada de ferramenta específica |
| **Fallback** | Rotear para um agente alternativo | Usar um endpoint de API de backup |
| **Circuit Breaker** | Parar de delegar para um agente com falhas | Parar de chamar uma ferramenta com falhas |
| **Timeout** | Definir timeout por tarefa na requisição A2A | Definir timeout por chamada no MCP |
| **Idempotência** | Incluir chave de idempotência no ID da tarefa | Incluir nos parâmetros da chamada de ferramenta |

---

## Etapa 6: Princípios de Design

Com base nesta análise, aqui estão os princípios-chave para construir sistemas A2A + MCP:

| Princípio | Descrição |
|-----------|-----------|
| **Separação de Responsabilidades** | A2A para delegação, MCP para acesso a ferramentas — não misture |
| **Consciência de Tokens** | Apenas chamadas A2A consomem tokens de LLM; otimize os prompts dos agentes |
| **Limites de Autenticação** | Escopos OAuth separados para A2A (contexto do usuário) e MCP (contexto do serviço) |
| **Isolamento de Erros** | Trate erros em cada limite de protocolo de forma independente |
| **Observabilidade** | Rastreie chamadas A2A e MCP com IDs de requisição correlacionados |
| **Idempotência** | Projete todas as operações para serem seguras de retentar |

---

## 🐛 Exercício de Correção de Bugs

O arquivo `lab-055/broken_delegation.py` possui **3 bugs** nas funções de análise de traces. Você consegue encontrar e corrigir todos?

Execute os auto-testes para ver quais falham:

```bash
python lab-055/broken_delegation.py
```

Você deve ver **3 testes falhando**. Cada teste corresponde a um bug:

| Teste | O que verifica | Dica |
|-------|---------------|------|
| Teste 1 | Contagem de chamadas A2A | Deve filtrar por `protocol == "A2A"`, não contar todas as linhas |
| Teste 2 | Latência média | Deve incluir TODAS as requisições (incluindo erros), não apenas OK |
| Teste 3 | Taxa de sucesso | Deve dividir pela contagem total de requisições, não pela contagem de agentes únicos |

Corrija todos os 3 bugs e execute novamente. Quando você ver `🎉 All 3 tests passed`, está pronto!

---


## 🧠 Verificação de Conhecimento

??? question "**Q1 (Múltipla Escolha):** Qual é a principal diferença entre A2A e MCP?"

    - A) A2A é mais rápido que MCP
    - B) A2A lida com delegação agente-para-agente; MCP lida com acesso agente-para-ferramenta
    - C) A2A usa REST; MCP usa GraphQL
    - D) A2A é para agentes na nuvem; MCP é para agentes locais

    ??? success "✅ Revelar Resposta"
        **Correto: B) A2A lida com delegação agente-para-agente; MCP lida com acesso agente-para-ferramenta**

        A2A (Agent-to-Agent) é um protocolo peer-to-peer para agentes se descobrirem e delegarem tarefas. MCP (Model Context Protocol) é um protocolo cliente-servidor para agentes acessarem ferramentas, bancos de dados e APIs. Eles são complementares — um sistema multi-agente tipicamente usa ambos.

??? question "**Q2 (Múltipla Escolha):** Por que a arquitetura usa protocolos separados para comunicação entre agentes e acesso a ferramentas?"

    - A) Para reduzir o número total de chamadas de API
    - B) Porque agentes e ferramentas usam linguagens de programação diferentes
    - C) Para permitir escalabilidade independente, limites de segurança e evolução de protocolo
    - D) Porque A2A é proprietário e MCP é open source

    ??? success "✅ Revelar Resposta"
        **Correto: C) Para permitir escalabilidade independente, limites de segurança e evolução de protocolo**

        Separar a comunicação agente-para-agente (A2A) do acesso agente-para-ferramenta (MCP) permite escalar cada camada de forma independente, aplicar escopos de autenticação diferentes em cada limite (OAuth de contexto do usuário para A2A, tokens de serviço para MCP), e evoluir os protocolos sem quebrar a outra camada.

??? question "**Q3 (Execute o Lab):** Quantas chamadas A2A existem nos traces de delegação?"

    Filtre [📥 `delegation_traces.csv`](https://github.com/lcarli/AI-LearningHub/raw/main/docs/docs/en/labs/lab-055/delegation_traces.csv) por `protocol == "A2A"` e conte as linhas.

    ??? success "✅ Revelar Resposta"
        **8**

        Existem 8 chamadas A2A — uma para cada requisição do Coordinator para um agente especialista (R001–R008). Os 12 eventos restantes são chamadas MCP dos especialistas para suas ferramentas de back-end.

??? question "**Q4 (Execute o Lab):** Quantas chamadas MCP existem nos traces de delegação?"

    Filtre `delegation_traces.csv` por `protocol == "MCP"` e conte as linhas.

    ??? success "✅ Revelar Resposta"
        **12**

        Existem 12 chamadas MCP — FlightAgent faz 5 (search, pricing, booking, payment, search-retry), HotelAgent faz 3 (search, booking, booking), e ItineraryAgent faz 4 (directions, availability, forecast, update).

??? question "**Q5 (Execute o Lab):** Qual é o número total de tokens consumidos em todos os eventos?"

    Some a coluna `tokens_used` em `delegation_traces.csv`.

    ??? success "✅ Revelar Resposta"
        **3330**

        Apenas chamadas A2A consomem tokens (raciocínio do LLM). As 8 chamadas A2A usam: 450 + 520 + 680 + 380 + 350 + 460 + 290 + 200 = **3330 tokens**. Todas as 12 chamadas MCP usam 0 tokens (chamadas diretas a APIs).

---

## Resumo

| Tópico | O Que Você Aprendeu |
|--------|---------------------|
| Arquitetura | A2A para delegação de agentes + MCP para acesso a ferramentas em um sistema unificado |
| Planejador de Viagens | Coordinator → FlightAgent / HotelAgent / ItineraryAgent |
| Padrões de Chamada | 8 delegações A2A acionando 12 chamadas de ferramentas MCP |
| Custos de Tokens | Apenas chamadas A2A consomem tokens de LLM (3330 no total) |
| Tratamento de Erros | Falhas em cascata através dos limites de protocolo; padrões de retry |
| Princípios de Design | Separação de responsabilidades, limites de autenticação, observabilidade |

---

## Próximos Passos

- **[Lab 054](lab-054-a2a-protocol.md)** — Protocolo A2A — Construa Sistemas Multi-Agente Interoperáveis
- **[Lab 056](lab-056-federated-connectors.md)** — Conectores Federados M365 Copilot com MCP
