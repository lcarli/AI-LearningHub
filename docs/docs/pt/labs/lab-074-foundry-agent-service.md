---
tags: [foundry, agent-service, multi-agent, production, enterprise, python]
---
# Lab 074: Foundry Agent Service — Implantação Multi-Agente em Produção

<div class="lab-meta">
  <span><strong>Nível:</strong> <span class="level-badge level-300">L300</span></span>
  <span><strong>Trilha:</strong> <a href="../paths/foundry/">🏭 Microsoft Foundry</a></span>
  <span><strong>Tempo:</strong> ~120 min</span>
  <span><strong>💰 Custo:</strong> <span class="level-badge cost-free">Gratuito</span> — Usa dados simulados de agentes</span>
</div>

## O que Você Vai Aprender

- O que é o **Foundry Agent Service** e como ele orquestra sistemas multi-agente em produção
- Como os tipos de agentes (especialista, orquestrador) trabalham juntos em uma implantação
- Analisar a saúde da frota de agentes: volumes de requisições, latência, taxas de erro e status
- Identificar **agentes degradados** e **riscos de configuração** (ex.: filtros de conteúdo desativados)
- Construir um **painel de saúde da frota** para monitoramento em produção

## Introdução

O **Azure AI Foundry Agent Service** fornece uma plataforma gerenciada para implantar, orquestrar e monitorar sistemas multi-agente em escala empresarial. Em vez de construir orquestração personalizada, você define agentes com ferramentas, memória e modelos específicos — e o serviço cuida do roteamento, gerenciamento de estado e escalabilidade.

### Tipos de Agentes

| Tipo | Função | Exemplo |
|------|--------|---------|
| **Orquestrador** | Roteia requisições para especialistas, gerencia o fluxo de conversa | SupportRouter, Coordinator |
| **Especialista** | Lida com um domínio específico com ferramentas e memória dedicadas | ProductAdvisor, OrderProcessor |

### O Cenário

Você é um **SRE de Plataforma** gerenciando uma implantação multi-agente para uma empresa de e-commerce. A frota tem **8 agentes** — 2 orquestradores e 6 especialistas — rodando no Azure Container Apps. Você foi alertado de que um agente está degradado e precisa investigar.

Seu dataset (`foundry_agents.csv`) contém o status atual da frota. Sua tarefa: analisar métricas de saúde, identificar problemas e produzir um relatório de status da frota.

!!! info "Dados Simulados"
    Este lab usa um CSV simulado de frota de agentes que espelha as métricas que você veria no painel de monitoramento do Azure AI Foundry. Os padrões (picos de latência, taxas de erro, status degradado) representam cenários comuns de produção.

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
    Salve todos os arquivos em uma pasta `lab-074/` no seu diretório de trabalho.

| Arquivo | Descrição | Download |
|---------|-----------|----------|
| `broken_foundry.py` | Exercício de correção de bugs (3 bugs + autotestes) | [📥 Download](https://github.com/lcarli/AI-LearningHub/raw/main/docs/docs/en/labs/lab-074/broken_foundry.py) |
| `foundry_agents.csv` | Dataset | [📥 Download](https://github.com/lcarli/AI-LearningHub/raw/main/docs/docs/en/labs/lab-074/foundry_agents.csv) |

---

## Etapa 1: Entenda a Arquitetura da Frota

Antes de analisar os dados, entenda como os agentes se encaixam:

```
                    ┌─────────────────┐
                    │   Coordinator   │ (orchestrator)
                    │    FA05         │
                    └────────┬────────┘
                             │ routes to
              ┌──────────────┼──────────────┐
              ▼              ▼              ▼
     ┌──────────────┐ ┌──────────────┐ ┌──────────────┐
     │SupportRouter │ │ProductAdvisor│ │OrderProcessor│
     │    FA03      │ │    FA01      │ │    FA02      │
     └──────────────┘ └──────────────┘ └──────────────┘
              │
     ┌────────┼────────┬──────────────┐
     ▼        ▼        ▼              ▼
  ┌────────┐┌────────┐┌────────┐┌──────────┐
  │Inventory││Quality ││Analytics││LegacyBridge│
  │  FA04  ││  FA06  ││  FA07  ││   FA08    │
  └────────┘└────────┘└────────┘└──────────┘
```

### Campos de Configuração Principais

| Campo | Descrição |
|-------|-----------|
| **memory_type** | Como o agente persiste estado: `cosmos_db` (durável), `ai_search` (vetorial), `session_only` (efêmero), `none` |
| **deployment** | Infraestrutura: `container_apps` (gerenciado) ou `vm` (auto-hospedado) |
| **content_filter** | Se a segurança de conteúdo do Azure AI está `enabled` ou `disabled` |
| **status** | Saúde do agente: `active` ou `degraded` |

---

## Etapa 2: Carregue e Explore os Dados da Frota

```python
import pandas as pd

df = pd.read_csv("lab-074/foundry_agents.csv")

print(f"Total agents: {len(df)}")
print(f"Agent types: {df['agent_type'].value_counts().to_dict()}")
print(f"Statuses: {df['status'].value_counts().to_dict()}")
print(f"\nFull fleet:")
print(df[["agent_id", "agent_name", "agent_type", "model", "status"]].to_string(index=False))
```

**Saída esperada:**

```
Total agents: 8
Agent types: {'specialist': 6, 'orchestrator': 2}
Statuses: {'active': 7, 'degraded': 1}
```

---

## Etapa 3: Analise o Volume de Requisições e a Distribuição de Carga

Como o tráfego está distribuído pela frota?

```python
total_requests = df["requests_24h"].sum()
print(f"Total 24h requests across fleet: {total_requests:,}")

print("\nRequest distribution:")
for _, row in df.sort_values("requests_24h", ascending=False).iterrows():
    pct = row["requests_24h"] / total_requests * 100
    bar = "█" * int(pct / 2)
    print(f"  {row['agent_name']:>20s}: {row['requests_24h']:>5,}  ({pct:>5.1f}%) {bar}")
```

**Saída esperada:**

```
Total 24h requests across fleet: 9,380
```

| Agente | Requisições | Participação |
|--------|-------------|--------------|
| Coordinator | 3.200 | 34,1% |
| SupportRouter | 2.100 | 22,4% |
| ProductAdvisor | 1.250 | 13,3% |
| OrderProcessor | 890 | 9,5% |
| QualityReviewer | 780 | 8,3% |
| InventoryMonitor | 560 | 6,0% |
| AnalyticsAgent | 420 | 4,5% |
| LegacyBridge | 180 | 1,9% |

!!! tip "Insight"
    O **orquestrador Coordinator lida com 34% de todo o tráfego** — ele é o ponto de entrada para a maioria das requisições. Se ele cair, todo o sistema é afetado. O SupportRouter é o segundo mais ocupado, roteando consultas de suporte ao cliente para especialistas.

---

## Etapa 4: Identifique Agentes Degradados e em Risco

### 4a — Agentes Degradados

```python
degraded = df[df["status"] == "degraded"]
print(f"Degraded agents: {len(degraded)}")
for _, agent in degraded.iterrows():
    print(f"\n  Agent: {agent['agent_name']} ({agent['agent_id']})")
    print(f"  Error rate: {agent['error_rate_pct']}%")
    print(f"  Avg latency: {agent['avg_latency_ms']}ms")
    print(f"  Requests: {agent['requests_24h']}")
```

**Saída esperada:**

```
Degraded agents: 1

  Agent: AnalyticsAgent (FA07)
  Error rate: 8.5%
  Avg latency: 850ms
  Requests: 420
```

### 4b — Agentes com Alta Taxa de Erro

```python
high_error = df[df["error_rate_pct"] > 5.0]
print(f"\nAgents with error rate > 5%: {len(high_error)}")
for _, agent in high_error.iterrows():
    print(f"  {agent['agent_name']}: {agent['error_rate_pct']}% errors")
```

### 4c — Status do Filtro de Conteúdo

```python
disabled_filter = df[df["content_filter"] == "disabled"]
print(f"\nAgents with disabled content filter: {len(disabled_filter)}")
for _, agent in disabled_filter.iterrows():
    print(f"  {agent['agent_name']} ({agent['agent_id']}) — deployment: {agent['deployment']}")
```

!!! warning "Risco de Segurança"
    **LegacyBridge (FA08)** tem seu filtro de conteúdo **desativado** e roda em uma VM auto-hospedada. Isso é um risco de conformidade — todos os agentes em produção devem ter a segurança de conteúdo habilitada, especialmente aqueles que lidam com dados de clientes.

---

## Etapa 5: Analise Padrões de Memória e Infraestrutura

```python
print("Memory type distribution:")
print(df.groupby("memory_type")["agent_name"].apply(list).to_string())

print("\nDeployment distribution:")
print(df.groupby("deployment")["agent_name"].apply(list).to_string())

# Agents without durable memory
no_durable = df[df["memory_type"].isin(["session_only", "none"])]
print(f"\nAgents without durable memory: {len(no_durable)}")
for _, agent in no_durable.iterrows():
    print(f"  {agent['agent_name']}: memory={agent['memory_type']}")
```

```python
# Latency by model
print("\nAvg latency by model:")
for model, group in df.groupby("model"):
    print(f"  {model}: {group['avg_latency_ms'].mean():.0f}ms")
```

---

## Etapa 6: Construa o Relatório de Saúde da Frota

```python
avg_latency = df["avg_latency_ms"].mean()
avg_error = df["error_rate_pct"].mean()

report = f"""# 📊 Foundry Agent Service — Fleet Health Report

## Fleet Overview
| Metric | Value |
|--------|-------|
| Total Agents | {len(df)} |
| Orchestrators | {(df['agent_type'] == 'orchestrator').sum()} |
| Specialists | {(df['agent_type'] == 'specialist').sum()} |
| Active | {(df['status'] == 'active').sum()} |
| Degraded | {(df['status'] == 'degraded').sum()} |
| Total 24h Requests | {total_requests:,} |
| Avg Latency | {avg_latency:.0f}ms |
| Avg Error Rate | {avg_error:.1f}% |

## Alerts
| Priority | Issue | Agent | Action |
|----------|-------|-------|--------|
| 🔴 High | Degraded status, 8.5% error rate | AnalyticsAgent (FA07) | Investigate AI Search connection |
| 🟡 Medium | Content filter disabled | LegacyBridge (FA08) | Enable content safety |
| 🟡 Medium | 12% error rate, VM deployment | LegacyBridge (FA08) | Migrate to Container Apps |
| 🟢 Low | Session-only memory | SupportRouter (FA03) | Consider durable memory for analytics |

## Recommendations
1. **Fix AnalyticsAgent** — likely an AI Search index connectivity issue causing 8.5% errors
2. **Enable content filter on LegacyBridge** — compliance requirement for production
3. **Migrate LegacyBridge to Container Apps** — self-hosted VMs lack auto-scaling and monitoring
4. **Add monitoring dashboards** — track per-agent latency and error rate trends
"""

print(report)

with open("lab-074/fleet_report.md", "w") as f:
    f.write(report)
print("💾 Saved to lab-074/fleet_report.md")
```

---

## 🐛 Exercício de Correção de Bugs

O arquivo `lab-074/broken_foundry.py` contém **3 bugs** que produzem métricas incorretas da frota. Você consegue encontrar e corrigir todos?

Execute os autotestes para ver quais falham:

```bash
python lab-074/broken_foundry.py
```

Você deverá ver **3 testes falhando**. Cada teste corresponde a um bug:

| Teste | O que verifica | Dica |
|-------|---------------|------|
| Teste 1 | Total de requisições em 24h | Deve somar as requisições, não calcular a média |
| Teste 2 | Contagem de agentes degradados | Deve contar o status `degraded`, não `active` |
| Teste 3 | Agentes sem memória durável | Deve contar `none`/`session_only`, não `cosmos_db` |

Corrija todos os 3 bugs e execute novamente. Quando você vir `All passed!`, está pronto!

---


## 🧠 Verificação de Conhecimento

??? question "**Q1 (Múltipla Escolha):** Qual é o papel de um agente orquestrador em uma implantação multi-agente do Foundry?"

    - A) Ele executa uma tarefa de domínio específico, como processamento de pedidos
    - B) Ele roteia requisições para agentes especialistas e gerencia o fluxo de conversa
    - C) Ele armazena a memória do agente no Cosmos DB
    - D) Ele monitora a saúde dos agentes e reinicia agentes com falha

    ??? success "✅ Revelar Resposta"
        **Correta: B) Ele roteia requisições para agentes especialistas e gerencia o fluxo de conversa**

        Agentes orquestradores atuam como o "controlador de tráfego" em um sistema multi-agente. Eles recebem requisições de entrada, determinam qual(is) especialista(s) deve(m) tratá-las, roteiam a conversa adequadamente e gerenciam o fluxo geral. Os especialistas lidam com o trabalho específico do domínio.

??? question "**Q2 (Múltipla Escolha):** Por que um filtro de conteúdo desativado é um risco de segurança para agentes em produção?"

    - A) Ele torna o agente mais lento
    - B) Ele permite que o agente gere conteúdo prejudicial, tendencioso ou que viole políticas
    - C) Ele impede que o agente acesse APIs externas
    - D) Ele aumenta os custos de tokens

    ??? success "✅ Revelar Resposta"
        **Correta: B) Ele permite que o agente gere conteúdo prejudicial, tendencioso ou que viole políticas**

        Os filtros do Azure AI Content Safety detectam e bloqueiam conteúdo prejudicial (discurso de ódio, violência, autolesão, conteúdo sexual). Desativar o filtro significa que o agente pode produzir ou responder a esse tipo de conteúdo sem proteções — um risco de conformidade e reputação em qualquer implantação em produção.

??? question "**Q3 (Execute o Lab):** Qual é o número total de requisições em toda a frota nas últimas 24 horas?"

    Execute a análise da Etapa 3 no [📥 `foundry_agents.csv`](https://github.com/lcarli/AI-LearningHub/raw/main/docs/docs/en/labs/lab-074/foundry_agents.csv) e verifique os resultados.

    ??? success "✅ Revelar Resposta"
        **9.380 requisições**

        Soma de todos os valores `requests_24h` dos agentes: 1.250 + 890 + 2.100 + 560 + 3.200 + 780 + 420 + 180 = **9.380**.

??? question "**Q4 (Execute o Lab):** Quantos agentes estão em estado degradado?"

    Execute a análise da Etapa 4a para descobrir.

    ??? success "✅ Revelar Resposta"
        **1 agente**

        Apenas o **AnalyticsAgent (FA07)** está em estado `degraded`, com uma taxa de erro de 8,5% e latência média de 850ms — significativamente pior que os outros agentes. Isso provavelmente indica um problema de conectividade com o backend do seu armazenamento de memória AI Search.

??? question "**Q5 (Execute o Lab):** Quantos agentes têm o filtro de conteúdo desativado?"

    Execute a análise da Etapa 4c para verificar o status do filtro de conteúdo.

    ??? success "✅ Revelar Resposta"
        **1 agente**

        Apenas o **LegacyBridge (FA08)** tem `content_filter=disabled`. Ele também é o único agente implantado em uma VM auto-hospedada em vez de Container Apps, e possui a maior taxa de erro (12,0%) da frota. Este agente precisa de atenção imediata.

---

## Resumo

| Tópico | O que Você Aprendeu |
|--------|---------------------|
| Foundry Agent Service | Plataforma gerenciada para orquestração e implantação multi-agente |
| Tipos de Agentes | Orquestradores roteiam; especialistas executam tarefas de domínio |
| Monitoramento da Frota | Acompanhe requisições, latência, taxas de erro e status por agente |
| Detecção de Degradação | Identifique agentes com taxas de erro ou latência elevadas |
| Segurança de Conteúdo | Todos os agentes em produção devem ter filtros de conteúdo habilitados |
| Padrões de Memória | Cosmos DB para durável, AI Search para vetorial, session_only para efêmero |

---

## Próximos Passos

- **[Lab 034](lab-034-multi-agent-sk.md)** — Multi-Agente com Semantic Kernel (construindo os agentes)
- **[Lab 033](lab-033-agent-observability.md)** — Observabilidade de Agentes com Application Insights (monitoramento aprofundado)
- **[Lab 030](lab-030-foundry-agent-mcp.md)** — Foundry Agent + MCP (conectando agentes a ferramentas externas)
- **[Lab 075](lab-075-powerbi-copilot.md)** — Power BI Copilot (visualizando dados da frota com dashboards assistidos por IA)
