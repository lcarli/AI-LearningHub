---
tags: [fabric, real-time-intelligence, kql, eventstreams, iot, python]
---
# Lab 051: Fabric IQ — Real-Time Intelligence Agents

<div class="lab-meta">
  <span><strong>Nível:</strong> <span class="level-badge level-300">L300</span></span>
  <span><strong>Caminho:</strong> Todos os caminhos</span>
  <span><strong>Tempo:</strong> ~75 min</span>
  <span><strong>💰 Custo:</strong> <span class="level-badge cost-free">Gratuito</span> — Usa conjunto de dados simulado incluso (capacidade do Fabric opcional)</span>
</div>

## O Que Você Vai Aprender

- Como **Eventstreams** ingerem dados de sensores IoT em tempo real no Microsoft Fabric
- Consultar dados de streaming com **KQL (Kusto Query Language)** para detecção instantânea de anomalias
- Detectar **anomalias de temperatura, umidade e estoque** usando regras baseadas em limites
- Usar o **Fabric Activator** para disparar alertas automatizados quando condições são atendidas
- Construir um **agente de IA** que lê dados em tempo real e apresenta insights acionáveis
- Analisar **padrões de atividade de armazém** (aberturas de porta, frequência de sensores) entre locais

## Introdução

![Pipeline RTI do Fabric](../../assets/diagrams/fabric-rti-pipeline.svg)

**Real-Time Intelligence (RTI)** no Microsoft Fabric é uma plataforma totalmente gerenciada para capturar, transformar e agir sobre dados de streaming — tudo dentro do workspace do Fabric. Diferente de pipelines batch tradicionais que processam dados horas ou dias após a chegada, o RTI oferece visibilidade em sub-segundos do que está acontecendo *agora*.

### O Cenário

A OutdoorGear Inc. opera **5 armazéns** nos EUA (Nova York, Los Angeles, Chicago, Dallas e Seattle). Cada armazém é equipado com sensores IoT que monitoram quatro métricas principais:

| Tipo de Sensor | O Que Mede | Limite Crítico |
|-------------|------------------|--------------------|
| **temperature** | Temperatura ambiente (°C) | > 30°C (risco de dano ao produto) |
| **humidity** | Umidade relativa (%) | > 80% (risco de dano por umidade) |
| **stock_level** | Unidades restantes no compartimento | < 10 unidades (reabastecimento urgente) |
| **door_opens** | Contagem de aberturas de porta por intervalo | Alta atividade = tráfego incomum |

Um agente de IA monitora esses feeds de sensores em tempo real, detecta anomalias e dispara alertas — para que os gerentes de armazém possam agir antes que os produtos sejam danificados ou o estoque acabe.

---

## Pré-requisitos

| Requisito | Por quê |
|---|---|
| Python 3.10+ | Executar scripts de análise |
| `pandas` | Analisar dados de eventos de sensores |

```bash
pip install pandas
```

---

!!! tip "Início Rápido com GitHub Codespaces"
    [![Abrir no GitHub Codespaces](https://github.com/codespaces/badge.svg)](https://codespaces.new/lcarli/AI-LearningHub?quickstart=1)

    Todas as dependências estão pré-instaladas no devcontainer.


## 📦 Arquivos de Apoio

!!! note "Baixe estes arquivos antes de iniciar o lab"
    Salve todos os arquivos em uma pasta `lab-051/` no seu diretório de trabalho.

| Arquivo | Descrição | Download |
|------|-------------|----------|
| `broken_alerting.py` | Exercício de correção de bugs (3 bugs + auto-testes) | [📥 Download](https://github.com/lcarli/AI-LearningHub/raw/main/docs/docs/en/labs/lab-051/broken_alerting.py) |
| `sensor_events.csv` | Conjunto de dados | [📥 Download](https://github.com/lcarli/AI-LearningHub/raw/main/docs/docs/en/labs/lab-051/sensor_events.csv) |

---

## Etapa 1: Entendendo o Fabric Real-Time Intelligence

Antes de escrever código, entenda os quatro componentes do RTI que formam o pipeline de ponta a ponta:

| Componente | Função | Analogia |
|-----------|------|---------|
| **Eventstream** | Pipeline gerenciado de ingestão de dados em tempo real — captura eventos de hubs IoT, Kafka ou aplicações personalizadas | A esteira que traz os dados |
| **Eventhouse** | Banco de dados colunar de séries temporais otimizado para dados de streaming; armazena eventos para consulta | O armazém onde os dados são guardados |
| **KQL (Kusto Query Language)** | Linguagem de consulta para filtrar, agregar e analisar dados de séries temporais em escala | O SQL da análise em tempo real |
| **Activator** | Motor de regras que dispara ações automatizadas (e-mails, mensagens do Teams, fluxos do Power Automate) quando condições de dados são atendidas | O sistema de alarme que age sobre anomalias |

### Como Eles Funcionam Juntos

```
IoT Sensors → Eventstream → Eventhouse → KQL Queries → Activator → Alerts
                (ingest)     (store)      (analyze)     (act)
```

1. **Eventstream** captura eventos brutos de sensores (payloads JSON) do IoT Hub ou fontes personalizadas
2. Os eventos chegam em uma tabela do **Eventhouse** (`SensorEvents`) para consulta colunar rápida
3. **Consultas KQL** são executadas contra o Eventhouse para detectar anomalias em quase tempo real
4. **Activator** monitora os resultados das consultas KQL e dispara alertas quando condições são atendidas
5. Um **agente de IA** pode consultar o Eventhouse diretamente, correlacionar anomalias e gerar resumos em linguagem natural para os gerentes de armazém

!!! info "Este Lab Usa Dados Simulados"
    Em produção, os eventos fluem continuamente do IoT Hub através dos Eventstreams. Neste lab, simulamos o pipeline com um snapshot CSV de 50 eventos de sensores e usamos pandas para demonstrar as consultas equivalentes em KQL. A lógica mapeia 1:1 para KQL em produção.

---

## Etapa 2: Carregar e Explorar Eventos de Sensores

O conjunto de dados tem **50 eventos de sensores** de **5 armazéns** cobrindo todos os 4 tipos de sensores:

```python
import pandas as pd

events = pd.read_csv("lab-051/sensor_events.csv")
print(f"Total events:   {len(events)}")
print(f"Warehouses:     {events['warehouse_id'].nunique()}")
print(f"Sensor types:   {sorted(events['sensor_type'].unique())}")
print(f"\nEvents per warehouse:")
print(events["warehouse_id"].value_counts().sort_index())
print(f"\nEvents per sensor type:")
print(events["sensor_type"].value_counts().sort_index())
```

**Saída esperada:**

```
Total events:   50
Warehouses:     5
Sensor types:   ['door_opens', 'humidity', 'stock_level', 'temperature']

Events per warehouse:
WH-CHI    10
WH-DAL    10
WH-LAX    10
WH-NYC    10
WH-SEA    10

Events per sensor type:
door_opens     12
humidity       12
stock_level    13
temperature    13
```

### Pré-visualizar os Dados

```python
print(events[["timestamp", "warehouse_id", "sensor_type", "value"]].head(10).to_string(index=False))
```

Cada evento tem um `timestamp`, `warehouse_id`, `sensor_type` e `value` numérico. Esta é a forma dos dados que um Eventstream entregaria em uma tabela do Eventhouse.

---

## Etapa 3: Detecção de Anomalias Estilo KQL

No Fabric em produção, você escreveria consultas KQL contra o Eventhouse. Aqui usamos pandas para replicar a mesma lógica — cada filtro pandas mapeia diretamente para uma cláusula `where` do KQL.

### 3a. Anomalias de Temperatura (> 30°C)

**Equivalente KQL:**

```kql
SensorEvents
| where sensor_type == "temperature"
| where value > 30
| project timestamp, warehouse_id, value
| order by value desc
```

**Equivalente Python:**

```python
temp = events[events["sensor_type"] == "temperature"]
temp_anomalies = temp[temp["value"] > 30].sort_values("value", ascending=False)
print(f"🌡️ Temperature anomalies (> 30°C): {len(temp_anomalies)}")
print(temp_anomalies[["timestamp", "warehouse_id", "value"]].to_string(index=False))
```

**Saída esperada:**

```
🌡️ Temperature anomalies (> 30°C): 3
          timestamp warehouse_id  value
 2026-06-15 14:20:00       WH-NYC   38.0
 2026-06-15 11:45:00       WH-DAL   35.0
 2026-06-15 09:30:00       WH-DAL   32.0
```

!!! warning "Alerta Crítico"
    WH-NYC a **38°C** está perigosamente alto — produtos perecíveis e eletrônicos podem ser danificados acima de 35°C. Uma regra do Activator notificaria imediatamente o gerente do armazém de NYC e acionaria o sistema HVAC.

### 3b. Estoque Crítico (< 10 Unidades)

**Equivalente KQL:**

```kql
SensorEvents
| where sensor_type == "stock_level"
| where value < 10
| project timestamp, warehouse_id, value
| order by value asc
```

**Equivalente Python:**

```python
stock = events[events["sensor_type"] == "stock_level"]
stock_critical = stock[stock["value"] < 10].sort_values("value")
print(f"📦 Stock critically low (< 10 units): {len(stock_critical)}")
print(stock_critical[["timestamp", "warehouse_id", "value"]].to_string(index=False))
```

**Saída esperada:**

```
📦 Stock critically low (< 10 units): 2
          timestamp warehouse_id  value
 2026-06-15 13:00:00       WH-LAX    3.0
 2026-06-15 10:15:00       WH-LAX    8.0
```

!!! tip "Insight"
    Ambos os eventos de estoque crítico estão no **WH-LAX** — o estoque caiu de 8 unidades para 3 unidades em poucas horas. Um agente de IA detectaria essa tendência e recomendaria um reabastecimento de emergência antes que o armazém fique completamente sem estoque.

### 3c. Alertas de Umidade (> 80%)

**Equivalente KQL:**

```kql
SensorEvents
| where sensor_type == "humidity"
| where value > 80
| project timestamp, warehouse_id, value
```

**Equivalente Python:**

```python
humidity = events[events["sensor_type"] == "humidity"]
humidity_alerts = humidity[humidity["value"] > 80]
print(f"💧 Humidity alerts (> 80%): {len(humidity_alerts)}")
print(humidity_alerts[["timestamp", "warehouse_id", "value"]].to_string(index=False))
```

**Saída esperada:**

```
💧 Humidity alerts (> 80%): 1
          timestamp warehouse_id  value
 2026-06-15 15:10:00       WH-CHI   85.0
```

---

## Etapa 4: Análise de Atividade do Armazém

Analise os eventos de abertura de porta por armazém — atividade incomumente alta pode indicar preocupações de segurança ou períodos de pico de expedição:

```python
doors = events[events["sensor_type"] == "door_opens"]
door_activity = doors.groupby("warehouse_id")["value"].sum().reset_index()
door_activity.columns = ["Warehouse", "Total Door Opens"]
door_activity = door_activity.sort_values("Total Door Opens", ascending=False)
print("🚪 Door Activity by Warehouse:")
print(door_activity.to_string(index=False))
print(f"\nMost active: {door_activity.iloc[0]['Warehouse']} "
      f"({int(door_activity.iloc[0]['Total Door Opens'])} total door opens)")
```

**Saída esperada:**

```
🚪 Door Activity by Warehouse:
 Warehouse  Total Door Opens
    WH-DAL              14.0
    WH-NYC              12.0
    WH-SEA              10.0
    WH-CHI               9.0
    WH-LAX               7.0

Most active: WH-DAL (14 total door opens)
```

!!! tip "Insight"
    **WH-DAL lidera com 14 aberturas de porta no total** — combinado com suas duas anomalias de temperatura (32°C e 35°C), aberturas frequentes de porta podem estar permitindo a entrada de ar quente. Um agente de IA correlacionaria esses sinais: _"O armazém de Dallas tem alta atividade de portas E temperaturas crescentes — considere adicionar uma cortina de ar na doca de carregamento 3."_

---

## Etapa 5: Construir um Painel de Alertas

Combine todas as anomalias em um único painel resumido que um agente de IA apresentaria a um gerente de operações de armazém:

```python
temp_count = len(temp_anomalies)
stock_count = len(stock_critical)
humidity_count = len(humidity_alerts)
total_anomalies = temp_count + stock_count + humidity_count

# Affected warehouses
affected = set()
affected.update(temp_anomalies["warehouse_id"].tolist())
affected.update(stock_critical["warehouse_id"].tolist())
affected.update(humidity_alerts["warehouse_id"].tolist())

dashboard = f"""
╔══════════════════════════════════════════════════╗
║       Fabric RTI — Anomaly Alert Dashboard       ║
╠══════════════════════════════════════════════════╣
║ Total Events Analyzed:  {len(events):>5}                     ║
║ Warehouses Monitored:   {events['warehouse_id'].nunique():>5}                     ║
║ ─────────────────────────────────────────────── ║
║ 🌡️  Temperature Alerts:  {temp_count:>5}  (> 30°C)            ║
║ 📦 Stock Critical:       {stock_count:>5}  (< 10 units)        ║
║ 💧 Humidity Alerts:      {humidity_count:>5}  (> 80%)             ║
║ ─────────────────────────────────────────────── ║
║ ⚠️  Total Anomalies:     {total_anomalies:>5}                     ║
║ 🏭 Warehouses Affected: {len(affected):>5}  ({', '.join(sorted(affected))})  ║
║ 🚪 Most Active:         WH-DAL (14 door opens)  ║
╚══════════════════════════════════════════════════╝

Priority Actions:
  1. 🔴 WH-NYC: Temperature at 38°C — check HVAC immediately
  2. 🔴 WH-LAX: Stock at 3 units — trigger emergency reorder
  3. 🟡 WH-DAL: Two temperature spikes + high door activity
  4. 🟡 WH-CHI: Humidity at 85% — activate dehumidifiers
"""
print(dashboard)
```

**Saída esperada:**

```
╔══════════════════════════════════════════════════╗
║       Fabric RTI — Anomaly Alert Dashboard       ║
╠══════════════════════════════════════════════════╣
║ Total Events Analyzed:     50                     ║
║ Warehouses Monitored:       5                     ║
║ ─────────────────────────────────────────────── ║
║ 🌡️  Temperature Alerts:      3  (> 30°C)            ║
║ 📦 Stock Critical:           2  (< 10 units)        ║
║ 💧 Humidity Alerts:          1  (> 80%)             ║
║ ─────────────────────────────────────────────── ║
║ ⚠️  Total Anomalies:         6                     ║
║ 🏭 Warehouses Affected:     4  (WH-CHI, WH-DAL, WH-LAX, WH-NYC)  ║
║ 🚪 Most Active:         WH-DAL (14 door opens)  ║
╚══════════════════════════════════════════════════╝
```

!!! info "Integração com Agente de IA"
    Em produção, um agente de IA consultaria o Eventhouse via KQL, executaria essa lógica de detecção de anomalias e postaria um resumo em linguagem natural em um canal do Teams ou e-mail. O Fabric Activator cuida dos alertas automatizados, enquanto o agente de IA fornece a *interpretação* — transformando números brutos em recomendações acionáveis.

---

## 🐛 Exercício de Correção de Bugs

O arquivo `lab-051/broken_alerting.py` tem **3 bugs** que produzem resultados incorretos de detecção de anomalias. Execute os auto-testes:

```bash
python lab-051/broken_alerting.py
```

Você deverá ver **3 testes falhando**:

| Teste | O que verifica | Dica |
|------|---------------|------|
| Teste 1 | O limite de temperatura é parametrizado | O limite está fixo em 50 em vez de usar o parâmetro `threshold` |
| Teste 2 | O alerta de estoque usa a comparação correta | Alertas de estoque disparam quando o valor está *abaixo* do limite, não acima |
| Teste 3 | A taxa de anomalias é calculada por armazém | O denominador deve ser eventos *por armazém*, não eventos totais de todos os armazéns |

Corrija todos os 3 bugs e execute novamente até ver `🎉 All 3 tests passed`.

---


## 🧠 Verificação de Conhecimento

??? question "**Q1 (Múltipla Escolha):** O que é um Eventstream no Microsoft Fabric?"

    - A) Um pipeline de processamento de dados em lote que roda em agendamento
    - B) Um pipeline gerenciado de ingestão de dados em tempo real que captura eventos de streaming
    - C) Uma ferramenta de visualização para criar painéis
    - D) Um serviço de treinamento de modelos de machine learning

    ??? success "✅ Revelar Resposta"
        **Correto: B) Um pipeline gerenciado de ingestão de dados em tempo real que captura eventos de streaming**

        Um Eventstream é o ponto de entrada para dados em tempo real no Fabric. Ele captura eventos de fontes como IoT Hub, Kafka ou aplicações personalizadas, os transforma em trânsito e os direciona para destinos como um Eventhouse para consulta. Diferente de pipelines batch, Eventstreams processam dados continuamente com latência de sub-segundo.

??? question "**Q2 (Múltipla Escolha):** O que o Fabric Activator faz?"

    - A) Otimiza o desempenho de consultas KQL
    - B) Gerencia a capacidade de armazenamento do Eventhouse
    - C) Dispara ações automatizadas quando condições de dados são atendidas
    - D) Converte dados em lote para formato de streaming

    ??? success "✅ Revelar Resposta"
        **Correto: C) Dispara ações automatizadas quando condições de dados são atendidas**

        O Activator é o motor de regras do Fabric para alertas em tempo real. Você define condições (ex.: "temperature > 30°C") e ações (ex.: enviar uma notificação do Teams, disparar um fluxo do Power Automate). Ele monitora continuamente os resultados das consultas KQL e dispara alertas no momento em que uma condição é atendida — sem necessidade de polling.

??? question "**Q3 (Execute o Lab):** Quantas leituras de temperatura excedem 30°C?"

    Filtre o DataFrame de eventos para `sensor_type == "temperature"` e `value > 30`.

    ??? success "✅ Revelar Resposta"
        **3**

        Três anomalias de temperatura excedem 30°C: WH-NYC a 38°C, WH-DAL a 35°C e WH-DAL a 32°C. A leitura de NYC a 38°C é a mais crítica — bem acima do limite de 35°C para danos ao produto.

??? question "**Q4 (Execute o Lab):** Qual armazém tem mais door_opens?"

    Filtre por `sensor_type == "door_opens"`, agrupe por `warehouse_id` e some os valores.

    ??? success "✅ Revelar Resposta"
        **WH-DAL (14 aberturas de porta no total)**

        Dallas lidera com 14 aberturas de porta no total, seguido por WH-NYC (12), WH-SEA (10), WH-CHI (9) e WH-LAX (7). Combinado com as duas anomalias de temperatura de Dallas, a alta atividade de portas pode estar contribuindo para o acúmulo de calor.

??? question "**Q5 (Execute o Lab):** Quantas leituras de estoque estão criticamente baixas (< 10 unidades)?"

    Filtre por `sensor_type == "stock_level"` e `value < 10`.

    ??? success "✅ Revelar Resposta"
        **2**

        Duas leituras de estoque no WH-LAX estão criticamente baixas: 8 unidades e 3 unidades. Ambos os eventos estão no mesmo armazém, sugerindo uma tendência rápida de esgotamento de estoque que requer um reabastecimento de emergência.

---

## Resumo

| Tópico | O Que Você Aprendeu |
|-------|-----------------|
| Eventstreams | Ingestão em tempo real de dados de sensores IoT no Fabric |
| Eventhouse & KQL | Armazenamento colunar e linguagem de consulta para análise de séries temporais |
| Detecção de Anomalias | Alertas baseados em limites para temperatura, umidade e níveis de estoque |
| Activator | Ações automatizadas disparadas por condições de dados |
| Integração com Agente de IA | Agentes consultam dados do Eventhouse e geram recomendações acionáveis |
| Painel de Alertas | Combinando múltiplos tipos de anomalias em uma visão unificada de operações |

---

## Próximos Passos

- **[Lab 052](lab-052-fabric-rti-advanced.md)** — Fabric RTI Avançado: Agregações de Janela Deslizante & Detecção de Tendências
- **[Lab 053](lab-053-fabric-agent-activator.md)** — Construindo um Agente de IA com Fabric Activator & Semantic Kernel