---
tags: [ag-ui, protocol, frontend, copilotkit, events, python]
---
# Lab 077: Protocolo AG-UI — Conecte Agentes a Interfaces de Usuário

<div class="lab-meta">
  <span><strong>Nível:</strong> <span class="level-badge level-200">L200</span></span>
  <span><strong>Trilha:</strong> Todas as trilhas</span>
  <span><strong>Tempo:</strong> ~60 min</span>
  <span><strong>💰 Custo:</strong> <span class="level-badge cost-free">Gratuito</span> — Usa dados de eventos simulados</span>
</div>

## O que Você Vai Aprender

- O que é o **Protocolo AG-UI** e como ele conecta agentes a interfaces de usuário frontend
- Como o AG-UI completa a **trilogia de interoperabilidade**: MCP (ferramentas) + A2A (agentes) + AG-UI (usuários)
- Analisar **12 tipos de eventos** e suas direções (agente→frontend vs. frontend→agente)
- Entender as categorias de eventos: ciclo de vida, texto, ferramenta, estado e entrada
- Construir um **diagrama de fluxo de eventos** a partir de um rastreamento de interação real

## Introdução

O **Protocolo AG-UI (Agent–User Interface)** é um protocolo baseado em eventos que padroniza como agentes de IA se comunicam com aplicações frontend. Enquanto o **MCP** conecta agentes a ferramentas e o **A2A** conecta agentes a outros agentes, o **AG-UI** fecha o ciclo conectando agentes a **usuários** por meio de suas interfaces.

### A Trilogia de Interoperabilidade

| Protocolo | Conecta | Propósito |
|-----------|---------|-----------|
| **MCP** | Agente ↔ Ferramentas | Acesso padronizado a ferramentas/recursos |
| **A2A** | Agente ↔ Agente | Colaboração multi-agente |
| **AG-UI** | Agente ↔ Usuário | Streaming em tempo real e interação com a UI |

### Como Funciona

O AG-UI utiliza um **modelo de eventos por streaming**. Em vez de requisição/resposta, o agente e o frontend trocam um fluxo contínuo de eventos tipados:

```
Frontend                          Agent
   │                                │
   │── RunAgent (start) ──────────►│
   │                                │
   │◄──── LifecycleStarted ────────│
   │◄──── TextMessageStart ────────│
   │◄──── TextMessageContent ──────│
   │◄──── TextMessageEnd ──────────│
   │◄──── ToolCallStart ──────────│
   │◄──── ToolCallArgs ───────────│
   │◄──── ToolCallEnd ────────────│
   │                                │
   │── ToolResult (response) ─────►│
   │                                │
   │◄──── StateUpdate ─────────────│
   │◄──── LifecycleCompleted ──────│
   │                                │
```

### O Cenário

Você é um **Engenheiro Frontend** integrando um agente de IA em uma UI baseada em CopilotKit. Você tem um conjunto de dados com **12 tipos de eventos** (`agui_events.csv`) que define todos os eventos do protocolo AG-UI. Sua tarefa: analisar os eventos, entender suas direções e categorias, e mapear o fluxo de eventos para uma interação típica com o agente.

!!! info "Dados Simulados"
    Este laboratório usa um conjunto de dados simulado de tipos de eventos. Os nomes dos eventos, direções e categorias espelham a especificação do protocolo AG-UI conforme definido pelo CopilotKit.

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

!!! note "Baixe estes arquivos antes de iniciar o laboratório"
    Salve todos os arquivos em uma pasta `lab-077/` no seu diretório de trabalho.

| Arquivo | Descrição | Download |
|---------|-----------|----------|
| `broken_agui.py` | Exercício de Correção de Bugs (3 bugs + autotestes) | [📥 Download](https://github.com/lcarli/AI-LearningHub/raw/main/docs/docs/en/labs/lab-077/broken_agui.py) |
| `agui_events.csv` | 12 tipos de eventos AG-UI com direções e categorias | [📥 Download](https://github.com/lcarli/AI-LearningHub/raw/main/docs/docs/en/labs/lab-077/agui_events.csv) |

---

## Etapa 1: Entenda o Modelo de Eventos

Os eventos AG-UI são organizados por **direção** e **categoria**:

| Direção | Significado |
|---------|-------------|
| **agente→frontend** | O agente envia dados para a UI (streaming de texto, chamadas de ferramentas, atualizações de estado) |
| **frontend→agente** | O usuário/UI envia entrada para o agente (comando de execução, resultados de ferramentas) |

| Categoria | Exemplos |
|-----------|---------|
| **lifecycle** | `LifecycleStarted`, `LifecycleCompleted` — marca os limites de execução do agente |
| **text** | `TextMessageStart`, `TextMessageContent`, `TextMessageEnd` — saída de texto por streaming |
| **tool** | `ToolCallStart`, `ToolCallArgs`, `ToolCallEnd`, `ToolResult` — execução de ferramentas |
| **state** | `StateUpdate`, `StateSnapshot` — sincronização de estado compartilhado |
| **input** | `RunAgent` — o frontend inicia uma execução do agente |

---

## Etapa 2: Carregue e Explore os Eventos

```python
import pandas as pd

df = pd.read_csv("lab-077/agui_events.csv")

print(f"Total event types: {len(df)}")
print(f"Directions: {df['direction'].value_counts().to_dict()}")
print(f"Categories: {df['category'].value_counts().to_dict()}")
print(f"\nAll events:")
print(df[["event_name", "direction", "category"]].to_string(index=False))
```

**Saída esperada:**

```
Total event types: 12
Directions: {'agent_to_frontend': 9, 'frontend_to_agent': 3}
Categories: {'tool': 4, 'text': 3, 'lifecycle': 2, 'state': 2, 'input': 1}
```

---

## Etapa 3: Analise as Direções dos Eventos

Quais eventos fluem do agente para o frontend, e quais vão na direção oposta?

```python
agent_to_ui = df[df["direction"] == "agent_to_frontend"]
ui_to_agent = df[df["direction"] == "frontend_to_agent"]

print(f"Agent → Frontend events: {len(agent_to_ui)}")
for _, row in agent_to_ui.iterrows():
    print(f"  {row['event_name']:>25s}  [{row['category']}]")

print(f"\nFrontend → Agent events: {len(ui_to_agent)}")
for _, row in ui_to_agent.iterrows():
    print(f"  {row['event_name']:>25s}  [{row['category']}]")
```

!!! tip "Insight de Design"
    O protocolo é **fortemente assimétrico**: **9 eventos** fluem do agente para o frontend, mas apenas **3** do frontend para o agente. Isso reflete a realidade de que os agentes produzem a maior parte dos dados (streaming de texto, chamadas de ferramentas, atualizações de estado) enquanto os frontends enviam principalmente comandos e resultados de ferramentas.

---

## Etapa 4: Mapeie o Fluxo de Eventos

Construa uma linha do tempo de eventos para uma interação típica com o agente:

```python
# Define a typical interaction sequence
sequence = [
    "RunAgent",
    "LifecycleStarted",
    "TextMessageStart",
    "TextMessageContent",
    "TextMessageEnd",
    "ToolCallStart",
    "ToolCallArgs",
    "ToolCallEnd",
    "ToolResult",
    "StateUpdate",
    "TextMessageStart",
    "TextMessageContent",
    "TextMessageEnd",
    "LifecycleCompleted"
]

print("Typical AG-UI Event Flow:")
print("=" * 60)
for i, event_name in enumerate(sequence, 1):
    match = df[df["event_name"] == event_name]
    if not match.empty:
        row = match.iloc[0]
        direction = "►" if row["direction"] == "frontend_to_agent" else "◄"
        side = "Frontend" if row["direction"] == "frontend_to_agent" else "Agent   "
        print(f"  {i:>2}. {side} {direction} {event_name:<25s} [{row['category']}]")
```

---

## Etapa 5: Analise as Categorias em Profundidade

```python
print("Events by category:\n")
for category, group in df.groupby("category"):
    print(f"  {category.upper()} ({len(group)} events):")
    for _, row in group.iterrows():
        arrow = "→" if row["direction"] == "agent_to_frontend" else "←"
        print(f"    {arrow} {row['event_name']}")
    print()

# Summary statistics
print("Category × Direction matrix:")
pivot = df.groupby(["category", "direction"]).size().unstack(fill_value=0)
print(pivot.to_string())
```

!!! warning "Responsabilidade do Frontend"
    Quando o agente emite um evento `ToolCallEnd`, o **frontend é responsável** por executar a ferramenta e enviar de volta um evento `ToolResult`. Se o frontend não responder, o agente ficará esperando indefinidamente. Sempre implemente tratamento de timeout para execução de ferramentas.

---

## Etapa 6: Construa o Resumo do Protocolo

```python
report = f"""# 📋 AG-UI Protocol Summary

## Overview
| Metric | Value |
|--------|-------|
| Total Event Types | {len(df)} |
| Agent → Frontend | {len(agent_to_ui)} |
| Frontend → Agent | {len(ui_to_agent)} |
| Categories | {df['category'].nunique()} |

## Event Catalog
"""

for _, row in df.iterrows():
    arrow = "→ Frontend" if row["direction"] == "agent_to_frontend" else "→ Agent"
    report += f"| `{row['event_name']}` | {row['category']} | {arrow} |\n"

report += f"""
## Protocol Trilogy
| Protocol | Connection | Events |
|----------|-----------|--------|
| MCP | Agent ↔ Tools | Request/Response |
| A2A | Agent ↔ Agent | Task-based |
| AG-UI | Agent ↔ User | {len(df)} streaming events |
"""

print(report)

with open("lab-077/protocol_summary.md", "w") as f:
    f.write(report)
print("💾 Saved to lab-077/protocol_summary.md")
```

---

## 🐛 Exercício de Correção de Bugs

O arquivo `lab-077/broken_agui.py` contém **3 bugs** que produzem análises de eventos incorretas. Você consegue encontrar e corrigir todos?

Execute os autotestes para ver quais falham:

```bash
python lab-077/broken_agui.py
```

Você deverá ver **3 testes falhando**. Cada teste corresponde a um bug:

| Teste | O que verifica | Dica |
|-------|---------------|------|
| Teste 1 | Contagem de eventos agente→frontend | Deveria filtrar `agent_to_frontend`, não `frontend_to_agent` |
| Teste 2 | Total de tipos de eventos | Deveria usar `len(df)`, não `df['category'].nunique()` |
| Teste 3 | Contagem de eventos frontend→agente | Deveria contar a direção `frontend_to_agent`, não a categoria `input` |

Corrija todos os 3 bugs e execute novamente. Quando você vir `All passed!`, está feito!

---


## 🧠 Verificação de Conhecimento

??? question "**Q1 (Múltipla Escolha):** Qual é o papel do AG-UI na trilogia de interoperabilidade?"

    - A) Conecta agentes a ferramentas e APIs externas
    - B) Conecta agentes a outros agentes para colaboração
    - C) Conecta agentes a interfaces de usuário frontend por meio de eventos de streaming
    - D) Conecta agentes a bancos de dados para armazenamento

    ??? success "✅ Revelar Resposta"
        **Correta: C) Conecta agentes a interfaces de usuário frontend por meio de eventos de streaming**

        A trilogia de interoperabilidade consiste em MCP (agente↔ferramentas), A2A (agente↔agentes) e AG-UI (agente↔usuários). O AG-UI utiliza um modelo de eventos por streaming para permitir comunicação em tempo real entre agentes de IA e aplicações frontend como CopilotKit.

??? question "**Q2 (Múltipla Escolha):** Por que o protocolo AG-UI é assimétrico (mais eventos agente→frontend do que frontend→agente)?"

    - A) O frontend é lento demais para enviar muitos eventos
    - B) Os agentes produzem a maior parte dos dados (texto, chamadas de ferramentas, estado) enquanto os frontends enviam principalmente comandos e resultados de ferramentas
    - C) O protocolo limita os eventos do frontend por razões de segurança
    - D) Os eventos do frontend são agrupados em menos mensagens

    ??? success "✅ Revelar Resposta"
        **Correta: B) Os agentes produzem a maior parte dos dados (texto, chamadas de ferramentas, estado) enquanto os frontends enviam principalmente comandos e resultados de ferramentas**

        Em uma interação típica, o agente transmite tokens de texto por streaming, emite eventos de chamadas de ferramentas e envia atualizações de estado — tudo fluindo para o frontend. O papel do frontend é principalmente iniciar execuções (`RunAgent`) e retornar resultados de execução de ferramentas (`ToolResult`).

??? question "**Q3 (Execute o Laboratório):** Quantos tipos de eventos fluem do agente para o frontend?"

    Execute a análise da Etapa 3 no [📥 `agui_events.csv`](https://github.com/lcarli/AI-LearningHub/raw/main/docs/docs/en/labs/lab-077/agui_events.csv) e conte os eventos `agent_to_frontend`.

    ??? success "✅ Revelar Resposta"
        **9 eventos**

        Os seguintes eventos fluem do agente para o frontend: `LifecycleStarted`, `LifecycleCompleted`, `TextMessageStart`, `TextMessageContent`, `TextMessageEnd`, `ToolCallStart`, `ToolCallArgs`, `ToolCallEnd` e `StateUpdate`. São **9** de 12 tipos de eventos no total.

??? question "**Q4 (Execute o Laboratório):** Quantos tipos de eventos fluem do frontend para o agente?"

    Conte os eventos com direção `frontend_to_agent`.

    ??? success "✅ Revelar Resposta"
        **3 eventos**

        Apenas **3 eventos** fluem do frontend para o agente: `RunAgent` (input), `ToolResult` (tool) e `StateSnapshot` (state). O protocolo é fortemente assimétrico — os agentes enviam 3× mais tipos de eventos do que os frontends.

??? question "**Q5 (Execute o Laboratório):** Qual é o número total de tipos de eventos no protocolo AG-UI?"

    Carregue o CSV e verifique a contagem total de linhas.

    ??? success "✅ Revelar Resposta"
        **12 tipos de eventos**

        O protocolo AG-UI define exatamente **12 tipos de eventos** em 5 categorias: tool (4), text (3), lifecycle (2), state (2) e input (1).

---

## Resumo

| Tópico | O que Você Aprendeu |
|--------|---------------------|
| Protocolo AG-UI | Protocolo baseado em eventos que conecta agentes a interfaces de usuário frontend |
| Trilogia de Interoperabilidade | MCP (ferramentas) + A2A (agentes) + AG-UI (usuários) = ecossistema completo de agentes |
| Modelo de Eventos | 12 tipos de eventos: 9 agente→frontend, 3 frontend→agente |
| Categorias | lifecycle, text, tool, state, input |
| Arquitetura de Streaming | Fluxo contínuo de eventos substitui o padrão de requisição/resposta |
| Responsabilidade do Frontend | A UI deve executar ferramentas e retornar resultados quando o agente solicita |

---

## Próximos Passos

- **[Lab 029](lab-029-mcp-protocol.md)** — Protocolo MCP (o pilar de ferramentas da trilogia)
- **[Lab 070](lab-070-agent-ux-patterns.md)** — Padrões de UX para Agentes (padrões de design para UIs com agentes)
- **[Lab 076](lab-076-microsoft-agent-framework.md)** — Microsoft Agent Framework (construa agentes que falam AG-UI)
- **[Lab 034](lab-034-multi-agent-sk.md)** — Multi-Agente com Semantic Kernel (agentes que colaboram via A2A)
