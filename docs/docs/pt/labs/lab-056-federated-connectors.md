---
tags: [connectors, mcp, m365, copilot, federation, enterprise]
---
# Lab 056: Conectores Federados M365 Copilot com MCP

<div class="lab-meta">
  <span><strong>Nível:</strong> <span class="level-badge level-300">L300</span></span>
  <span><strong>Trilha:</strong> Todas as trilhas</span>
  <span><strong>Tempo:</strong> ~90 min</span>
  <span><strong>💰 Custo:</strong> <span class="level-badge cost-free">Gratuito</span> — Usa dados comparativos simulados (sem necessidade de tenant M365)</span>
</div>

## O Que Você Vai Aprender

- A diferença entre **conectores sincronizados (indexados)** e **conectores federados (em tempo real)** no Microsoft 365 Copilot
- Como **MCP pode atuar como um conector federado** — fornecendo acesso a dados em tempo real sem indexação
- Como **citações** funcionam em conectores federados vs sincronizados
- **Considerações de OAuth e conformidade** para dados regulados (saúde, jurídico, finanças)
- Quando escolher cada tipo de conector com base em latência, atualidade e requisitos de conformidade

## Introdução

O Microsoft 365 Copilot usa **conectores** para trazer dados externos para a experiência do Copilot. Existem duas arquiteturas fundamentais:

| Tipo de Conector | Como Funciona | Localização dos Dados |
|------------------|--------------|----------------------|
| **Sincronizado (Indexado)** | Rastreia e copia dados para o índice do Microsoft Search | Dados armazenados nos servidores da Microsoft |
| **Federado (Tempo Real)** | Consulta o sistema de origem em tempo de execução — nenhum dado é copiado | Dados permanecem no sistema de origem |

Cada abordagem tem trade-offs:

| Dimensão | Federado | Sincronizado |
|----------|----------|--------------|
| **Latência** | Maior (consulta em tempo real) | Menor (pré-indexado) |
| **Atualidade dos Dados** | Sempre atual (0 seg) | Depende do agendamento de rastreamento |
| **Conformidade** | Dados nunca saem da origem | Dados copiados para servidores da Microsoft |
| **Acesso Offline** | Requer disponibilidade da origem | Funciona mesmo se a origem estiver fora do ar |

### O Cenário

A OutdoorGear Inc. precisa conectar **múltiplas fontes de dados** ao Microsoft 365 Copilot:

- **Catálogo de produtos** e **histórico de pedidos** — podem ser indexados (sincronizados) para busca rápida
- **Registros médicos de pacientes**, **dados salariais de funcionários** e **contratos jurídicos** — dados regulados que **nunca** devem sair do sistema de origem (apenas federado)
- **Preços de ações em tempo real** e **rastreamento de envios** — precisam dos dados mais atualizados possível

Seu trabalho é analisar um dataset comparativo de 20 consultas (10 federadas, 10 sincronizadas) e determinar quando cada tipo de conector é a escolha certa.

!!! info "MCP como Conector Federado"
    Um servidor MCP pode servir como conector federado para o M365 Copilot. O servidor MCP consulta o sistema de origem em tempo real e retorna resultados com citações — nenhum dado é indexado ou armazenado nos servidores da Microsoft. Isso torna o MCP ideal para dados regulados que devem estar em conformidade com requisitos HIPAA, GDPR ou SOX.

## Pré-requisitos

| Requisito | Motivo |
|---|---|
| Python 3.10+ | Analisar dados comparativos de conectores |
| Biblioteca `pandas` | Operações com DataFrame |

```bash
pip install pandas
```

---

!!! tip "Início Rápido com GitHub Codespaces"
    [![Open in GitHub Codespaces](https://github.com/codespaces/badge.svg)](https://codespaces.new/lcarli/AI-LearningHub?quickstart=1)

    Todas as dependências estão pré-instaladas no devcontainer.


## 📦 Arquivos de Apoio

!!! note "Baixe estes arquivos antes de iniciar o lab"
    Salve todos os arquivos em uma pasta `lab-056/` no seu diretório de trabalho.

| Arquivo | Descrição | Download |
|---------|-----------|----------|
| `broken_connector.py` | Exercício de correção de bugs (3 bugs + auto-testes) | [📥 Download](https://github.com/lcarli/AI-LearningHub/raw/main/docs/docs/en/labs/lab-056/broken_connector.py) |
| `connector_comparison.csv` | Dataset | [📥 Download](https://github.com/lcarli/AI-LearningHub/raw/main/docs/docs/en/labs/lab-056/connector_comparison.csv) |

---

## Etapa 1: Entendendo os Tipos de Conectores

### Conectores Sincronizados (Indexados)

Conectores sincronizados **rastreiam** uma fonte de dados em um agendamento e **copiam** o conteúdo para o índice do Microsoft Search:

```
┌─────────────┐    Crawl     ┌──────────────┐    Index    ┌─────────────┐
│  Source      │ ──────────► │  Microsoft   │ ─────────► │  Copilot    │
│  System      │  (schedule) │  Graph       │  (fast)    │  Search     │
│             │             │  Connector    │            │             │
└─────────────┘             └──────────────┘            └─────────────┘
```

- ✅ **Consultas rápidas** — dados pré-indexados
- ✅ **Funciona offline** — sistema de origem pode estar fora do ar
- ❌ **Dados desatualizados** — depende da frequência de rastreamento
- ❌ **Risco de conformidade** — dados copiados para servidores da Microsoft

### Conectores Federados (Tempo Real)

Conectores federados consultam o sistema de origem **em tempo de execução** — nenhum dado é copiado:

```
┌─────────────┐   Real-time   ┌──────────────┐   Results   ┌─────────────┐
│  Source      │ ◄──────────► │  Federated   │ ──────────► │  Copilot    │
│  System      │    query      │  Connector   │  + citation │  Search     │
│             │              │  (MCP Server) │             │             │
└─────────────┘              └──────────────┘             └─────────────┘
```

- ✅ **Sempre atualizado** — consulta dados ao vivo
- ✅ **Em conformidade** — dados nunca saem da origem
- ✅ **Citações** — respostas incluem links para a fonte
- ❌ **Latência maior** — overhead de consulta em tempo real
- ❌ **Dependência da origem** — requer disponibilidade do sistema de origem

---

## Etapa 2: Carregar o Dataset Comparativo

O dataset contém **20 consultas** — cada consulta foi executada tanto por um conector federado quanto por um sincronizado:

```python
import pandas as pd

df = pd.read_csv("lab-056/connector_comparison.csv")
print(f"Total queries: {len(df)}")
print(f"Connector types: {df['connector_type'].unique().tolist()}")
print(f"Columns: {list(df.columns)}")
print(f"\nFirst 6 rows:")
print(df.head(6).to_string(index=False))
```

**Saída esperada:**

```
Total queries: 20
Connector types: ['federated', 'synced']
Columns: ['query_id', 'query_text', 'connector_type', 'latency_ms', 'results_count',
           'data_freshness_sec', 'data_size_kb', 'compliant']

First 6 rows:
query_id                      query_text connector_type  latency_ms  results_count  data_freshness_sec  data_size_kb compliant
     Q01             Show all hiking boots      federated         450              5                   0            12      true
     Q02             Show all hiking boots         synced         120              5                3600            12      true
     Q03           Find tents under $300      federated         520              3                   0             8      true
     Q04           Find tents under $300         synced          95              3                7200             8      true
     Q05  Customer order history C001      federated         680              4                   0            15      true
     Q06  Customer order history C001         synced         150              4                1800            15      true
```

---

## Etapa 3: Comparar Latência vs Atualidade

Analise os trade-offs de desempenho entre os tipos de conectores:

### 3a — Latência Média por Tipo

```python
fed = df[df["connector_type"] == "federated"]
syn = df[df["connector_type"] == "synced"]

avg_fed_latency = fed["latency_ms"].mean()
avg_syn_latency = syn["latency_ms"].mean()
ratio = avg_fed_latency / avg_syn_latency

print(f"Average federated latency: {avg_fed_latency:.0f} ms")
print(f"Average synced latency:    {avg_syn_latency:.1f} ms")
print(f"Federated/Synced ratio:    {ratio:.1f}×")
```

**Saída esperada:**

```
Average federated latency: 473 ms
Average synced latency:    109.8 ms
Federated/Synced ratio:    4.3×
```

### 3b — Comparação de Atualidade

```python
print("Data freshness (seconds since last update):")
print(f"  Federated average: {fed['data_freshness_sec'].mean():.0f} sec (always 0 — real-time)")
print(f"  Synced average:    {syn['data_freshness_sec'].mean():.0f} sec")
print(f"  Synced max:        {syn['data_freshness_sec'].max():.0f} sec ({syn['data_freshness_sec'].max()/3600:.1f} hours)")
```

**Saída esperada:**

```
Data freshness (seconds since last update):
  Federated average: 0 sec (always 0 — real-time)
  Synced average:    3660 sec
  Synced max:        14400 sec (4.0 hours)
```

### 3c — Distribuição de Latência

```python
print("Latency ranges:")
for ctype, group in df.groupby("connector_type"):
    print(f"  {ctype}: {group['latency_ms'].min()}–{group['latency_ms'].max()} ms "
          f"(median: {group['latency_ms'].median():.0f} ms)")
```

**Saída esperada:**

```
Latency ranges:
  federated: 290–680 ms (median: 465 ms)
  synced: 88–150 ms (median: 105 ms)
```

---

## Etapa 4: Análise de Conformidade

Determine quais consultas envolvem dados regulados que não podem ser indexados:

### 4a — Consultas Não Conformes

```python
non_compliant = df[df["compliant"] == False]
print(f"Non-compliant queries: {len(non_compliant)}")
print(f"\nDetails:")
print(non_compliant[["query_id", "query_text", "connector_type"]].to_string(index=False))
```

**Saída esperada:**

```
Non-compliant queries: 3

Details:
query_id               query_text connector_type
     Q10  Patient medical records         synced
     Q12      Employee salary data         synced
     Q18    Legal contract clauses         synced
```

### 4b — Por Que Sincronizado Não é Conforme para Dados Regulados

```python
# Compare federated vs synced for the same regulated queries
regulated_queries = ["Patient medical records", "Employee salary data", "Legal contract clauses"]
for query_text in regulated_queries:
    rows = df[df["query_text"] == query_text]
    fed_row = rows[rows["connector_type"] == "federated"].iloc[0]
    syn_row = rows[rows["connector_type"] == "synced"].iloc[0]
    print(f"\n{query_text}:")
    print(f"  Federated: compliant={fed_row['compliant']}, latency={fed_row['latency_ms']}ms, freshness={fed_row['data_freshness_sec']}s")
    print(f"  Synced:    compliant={syn_row['compliant']}, latency={syn_row['latency_ms']}ms, freshness={syn_row['data_freshness_sec']}s")
```

**Saída esperada:**

```
Patient medical records:
  Federated: compliant=True, latency=550ms, freshness=0s
  Synced:    compliant=False, latency=130ms, freshness=3600s

Employee salary data:
  Federated: compliant=True, latency=420ms, freshness=0s
  Synced:    compliant=False, latency=105ms, freshness=1800s

Legal contract clauses:
  Federated: compliant=True, latency=480ms, freshness=0s
  Synced:    compliant=False, latency=115ms, freshness=7200s
```

!!! warning "Conformidade Não é Negociável"
    Para dados regulados (HIPAA, GDPR, SOX), o conector sincronizado **copia dados para servidores da Microsoft** durante a indexação. Isso viola requisitos de residência e soberania de dados. O conector federado (ex.: servidor MCP) mantém os dados no sistema de origem — apenas resultados de consultas são retornados em tempo de execução, nunca armazenados.

---

## Etapa 5: Quando Usar Cada Tipo de Conector

Com base na análise, aqui estão os critérios de decisão:

### Matriz de Decisão

| Critério | Usar Federado | Usar Sincronizado |
|----------|--------------|-------------------|
| **Dados regulados** (HIPAA, GDPR, SOX) | ✅ Obrigatório | ❌ Não conforme |
| **Atualidade em tempo real necessária** | ✅ Sempre atual | ❌ Desatualizado (atraso no rastreamento) |
| **Baixa latência é crítica** | ❌ ~473ms média | ✅ ~110ms média |
| **Origem pode ficar offline** | ❌ Requer origem | ✅ Funciona a partir do índice |
| **Grandes conjuntos de resultados** | ❌ Custo em tempo de execução | ✅ Pré-indexado |
| **Dados que mudam raramente** | ⚠️ Excessivo | ✅ Rastreamento captura atualizações |

### Recomendações para OutdoorGear

```python
recommendations = {
    "Product catalog": "Synced — low latency, not regulated, changes infrequently",
    "Order history": "Synced — historical data, benefits from indexing",
    "Patient medical records": "Federated — HIPAA regulated, must not leave source",
    "Employee salary data": "Federated — PII/compensation data, compliance required",
    "Real-time stock prices": "Federated — must be current, stale data is worse than slow",
    "Legal contracts": "Federated — SOX regulated, data sovereignty required",
    "Product reviews": "Synced — public data, benefits from fast search",
    "Shipping tracking": "Federated — real-time status updates needed",
}

print("OutdoorGear Connector Recommendations:")
for source, rec in recommendations.items():
    connector = "🔄 Federated" if "Federated" in rec else "📦 Synced"
    print(f"  {connector}  {source}: {rec.split(' — ')[1]}")
```

---

## 🐛 Exercício de Correção de Bugs

O arquivo `lab-056/broken_connector.py` possui **3 bugs** nas funções de análise de conectores. Você consegue encontrar e corrigir todos?

Execute os auto-testes para ver quais falham:

```bash
python lab-056/broken_connector.py
```

Você deve ver **3 testes falhando**. Cada teste corresponde a um bug:

| Teste | O que verifica | Dica |
|-------|---------------|------|
| Teste 1 | Atualidade média por tipo | Deve retornar `data_freshness_sec`, não `latency_ms` |
| Teste 2 | Contagem de não conformes | Deve contar `compliant == False`, não `compliant == True` |
| Teste 3 | Proporção de latência | Deve calcular `federated / synced`, não `synced / federated` |

Corrija todos os 3 bugs e execute novamente. Quando você ver `🎉 All 3 tests passed`, está pronto!

---


## 🧠 Verificação de Conhecimento

??? question "**Q1 (Múltipla Escolha):** Qual é a principal vantagem de um conector federado sobre um conector sincronizado?"

    - A) Menor latência para todos os tipos de consulta
    - B) Atualidade de dados em tempo real sem indexação — dados nunca saem da origem
    - C) Melhor suporte para acesso offline
    - D) Configuração de autenticação mais simples

    ??? success "✅ Revelar Resposta"
        **Correto: B) Atualidade de dados em tempo real sem indexação — dados nunca saem da origem**

        Conectores federados consultam o sistema de origem em tempo de execução, garantindo que os resultados estejam sempre atualizados (atualidade de 0 segundos). Como nenhum dado é copiado ou indexado, ele permanece no sistema de origem — tornando-o conforme com requisitos de residência de dados (HIPAA, GDPR, SOX).

??? question "**Q2 (Múltipla Escolha):** Por que conectores sincronizados não são conformes para dados regulados como registros médicos de pacientes?"

    - A) Conectores sincronizados não suportam criptografia
    - B) Dados são copiados para servidores da Microsoft durante a indexação, violando requisitos de residência de dados
    - C) Conectores sincronizados não conseguem lidar com grandes datasets
    - D) Conectores sincronizados não suportam autenticação OAuth

    ??? success "✅ Revelar Resposta"
        **Correto: B) Dados são copiados para servidores da Microsoft durante a indexação, violando requisitos de residência de dados**

        Quando um conector sincronizado rastreia uma fonte de dados, ele **copia o conteúdo para o índice de pesquisa da Microsoft**. Para dados regulados (registros de pacientes HIPAA, dados pessoais GDPR, dados financeiros SOX), isso viola requisitos de soberania e residência de dados. Os dados devem permanecer no sistema de origem — apenas conectores federados garantem isso.

??? question "**Q3 (Execute o Lab):** Qual é a latência média para consultas de conectores federados?"

    Filtre [�� `connector_comparison.csv`](https://github.com/lcarli/AI-LearningHub/raw/main/docs/docs/en/labs/lab-056/connector_comparison.csv) por `connector_type == "federated"` e calcule `latency_ms.mean()`.

    ??? success "✅ Revelar Resposta"
        **473 ms**

        As 10 consultas federadas têm latências: 450, 520, 680, 380, 550, 420, 610, 290, 480, 350. Soma = 4730, média = 4730 ÷ 10 = **473 ms**.

??? question "**Q4 (Execute o Lab):** Quantas consultas sincronizadas são não conformes?"

    Filtre por `connector_type == "synced"` e `compliant == False`.

    ??? success "✅ Revelar Resposta"
        **3**

        Três consultas sincronizadas são não conformes: Q10 (Registros médicos de pacientes), Q12 (Dados salariais de funcionários) e Q18 (Cláusulas de contratos jurídicos). Estas envolvem dados regulados que não devem ser copiados para servidores externos.

??? question "**Q5 (Execute o Lab):** Qual é a proporção aproximada de latência federado-para-sincronizado?"

    Divida a latência média federada pela latência média sincronizada.

    ??? success "✅ Revelar Resposta"
        **≈ 4,3×**

        Latência média federada = 473 ms. Latência média sincronizada ≈ 110 ms. Proporção = 473 ÷ 110 ≈ **4,3×**. Consultas federadas são cerca de 4,3 vezes mais lentas que consultas sincronizadas — o trade-off pela atualidade em tempo real e conformidade.

---

## Resumo

| Tópico | O Que Você Aprendeu |
|--------|---------------------|
| Tipos de Conectores | Sincronizado (indexado, rápido, desatualizado) vs Federado (tempo real, conforme, mais lento) |
| MCP como Conector | Servidores MCP podem servir como conectores federados para M365 Copilot |
| Conformidade | Dados regulados requerem conectores federados — sincronizados copiam dados para a Microsoft |
| Trade-off de Latência | Federado ≈ 4,3× mais lento mas sempre atualizado; sincronizado é rápido mas desatualizado |
| Critérios de Decisão | Escolha com base em regulamentação, necessidades de atualidade, tolerância a latência e acesso offline |

---

## Próximos Passos

- **[Lab 054](lab-054-a2a-protocol.md)** — Protocolo A2A — Construa Sistemas Multi-Agente Interoperáveis
- **[Lab 055](lab-055-a2a-mcp-capstone.md)** — A2A + MCP Full Stack — Capstone de Interoperabilidade de Agentes
