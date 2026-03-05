---
tags: [fabric, real-time-intelligence, kql, eventstreams, iot, python]
---
# Lab 051: Fabric IQ — Real-Time Intelligence Agents

<div class="lab-meta">
  <span><strong>Level:</strong> <span class="level-badge level-300">L300</span></span>
  <span><strong>Path:</strong> All paths</span>
  <span><strong>Time:</strong> ~75 min</span>
  <span><strong>💰 Cost:</strong> <span class="level-badge cost-free">Free</span> — Uses included mock dataset (Fabric capacity optional)</span>
</div>

## What You'll Learn

- How **Eventstreams** ingest real-time IoT sensor data into Microsoft Fabric
- Query streaming data with **KQL (Kusto Query Language)** for instant anomaly detection
- Detect **temperature, humidity, and stock anomalies** using threshold-based rules
- Use **Fabric Activator** to trigger automated alerts when conditions are met
- Build an **AI agent** that reads real-time data and surfaces actionable insights
- Analyze **warehouse activity patterns** (door opens, sensor frequency) across locations

## Introduction

![Fabric RTI Pipeline](../../assets/diagrams/fabric-rti-pipeline.svg)

**Real-Time Intelligence (RTI)** in Microsoft Fabric is a fully managed platform for capturing, transforming, and acting on streaming data — all within the Fabric workspace. Unlike traditional batch pipelines that process data hours or days after it arrives, RTI gives you sub-second visibility into what's happening *right now*.

### The Scenario

OutdoorGear Inc. operates **5 warehouses** across the US (New York, Los Angeles, Chicago, Dallas, and Seattle). Each warehouse is equipped with IoT sensors monitoring four key metrics:

| Sensor Type | What It Measures | Critical Threshold |
|-------------|------------------|--------------------|
| **temperature** | Ambient temperature (°C) | > 30°C (product damage risk) |
| **humidity** | Relative humidity (%) | > 80% (moisture damage risk) |
| **stock_level** | Units remaining in bin | < 10 units (reorder urgently) |
| **door_opens** | Door open count per interval | High activity = unusual traffic |

An AI agent monitors these sensor feeds in real time, detects anomalies, and triggers alerts — so warehouse managers can act before products are damaged or stock runs out.

---

## Prerequisites

| Requirement | Why |
|---|---|
| Python 3.10+ | Run analysis scripts |
| `pandas` | Analyze sensor event data |

```bash
pip install pandas
```

---

!!! tip "Quick Start with GitHub Codespaces"
    [![Open in GitHub Codespaces](https://github.com/codespaces/badge.svg)](https://codespaces.new/lcarli/AI-LearningHub?quickstart=1)

    All dependencies are pre-installed in the devcontainer.


## 📦 Supporting Files

!!! note "Download these files before starting the lab"
    Save all files to a `lab-051/` folder in your working directory.

| File | Description | Download |
|------|-------------|----------|
| `broken_alerting.py` | Bug-fix exercise (3 bugs + self-tests) | [📥 Download](https://github.com/lcarli/AI-LearningHub/raw/main/docs/docs/en/labs/lab-051/broken_alerting.py) |
| `sensor_events.csv` | Dataset | [📥 Download](https://github.com/lcarli/AI-LearningHub/raw/main/docs/docs/en/labs/lab-051/sensor_events.csv) |

---

## Step 1: Understanding Fabric Real-Time Intelligence

Before writing code, understand the four RTI components that form the end-to-end pipeline:

| Component | Role | Analogy |
|-----------|------|---------|
| **Eventstream** | Managed real-time data ingestion pipeline — captures events from IoT hubs, Kafka, or custom apps | The conveyor belt that brings data in |
| **Eventhouse** | Columnar time-series database optimized for streaming data; stores events for querying | The warehouse where data is stored |
| **KQL (Kusto Query Language)** | Query language for filtering, aggregating, and analyzing time-series data at scale | The SQL of real-time analytics |
| **Activator** | Rule engine that triggers automated actions (emails, Teams messages, Power Automate flows) when data conditions are met | The alarm system that acts on anomalies |

### How They Work Together

```
IoT Sensors → Eventstream → Eventhouse → KQL Queries → Activator → Alerts
                (ingest)     (store)      (analyze)     (act)
```

1. **Eventstream** captures raw sensor events (JSON payloads) from IoT Hub or custom sources
2. Events land in an **Eventhouse** table (`SensorEvents`) for fast columnar querying
3. **KQL queries** run against the Eventhouse to detect anomalies in near-real-time
4. **Activator** monitors KQL query results and fires alerts when conditions are met
5. An **AI agent** can query the Eventhouse directly, correlate anomalies, and generate plain-language summaries for warehouse managers

!!! info "This Lab Uses Mock Data"
    In production, events flow continuously from IoT Hub through Eventstreams. In this lab, we simulate the pipeline with a CSV snapshot of 50 sensor events and use pandas to demonstrate the KQL-equivalent queries. The logic maps 1:1 to production KQL.

---

## Step 2: Load and Explore Sensor Events

The dataset has **50 sensor events** from **5 warehouses** covering all 4 sensor types:

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

**Expected output:**

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

### Preview the Data

```python
print(events[["timestamp", "warehouse_id", "sensor_type", "value"]].head(10).to_string(index=False))
```

Each event has a `timestamp`, `warehouse_id`, `sensor_type`, and numeric `value`. This is the shape of data that an Eventstream would deliver into an Eventhouse table.

---

## Step 3: KQL-Style Anomaly Detection

In production Fabric, you'd write KQL queries against the Eventhouse. Here we use pandas to replicate the same logic — every pandas filter maps directly to a KQL `where` clause.

### 3a. Temperature Anomalies (> 30°C)

**KQL equivalent:**

```kql
SensorEvents
| where sensor_type == "temperature"
| where value > 30
| project timestamp, warehouse_id, value
| order by value desc
```

**Python equivalent:**

```python
temp = events[events["sensor_type"] == "temperature"]
temp_anomalies = temp[temp["value"] > 30].sort_values("value", ascending=False)
print(f"🌡️ Temperature anomalies (> 30°C): {len(temp_anomalies)}")
print(temp_anomalies[["timestamp", "warehouse_id", "value"]].to_string(index=False))
```

**Expected output:**

```
🌡️ Temperature anomalies (> 30°C): 3
          timestamp warehouse_id  value
 2026-06-15 14:20:00       WH-NYC   38.0
 2026-06-15 11:45:00       WH-DAL   35.0
 2026-06-15 09:30:00       WH-DAL   32.0
```

!!! warning "Critical Alert"
    WH-NYC at **38°C** is dangerously high — perishable goods and electronics can be damaged above 35°C. An Activator rule would immediately notify the NYC warehouse manager and trigger the HVAC system.

### 3b. Stock Critical (< 10 Units)

**KQL equivalent:**

```kql
SensorEvents
| where sensor_type == "stock_level"
| where value < 10
| project timestamp, warehouse_id, value
| order by value asc
```

**Python equivalent:**

```python
stock = events[events["sensor_type"] == "stock_level"]
stock_critical = stock[stock["value"] < 10].sort_values("value")
print(f"📦 Stock critically low (< 10 units): {len(stock_critical)}")
print(stock_critical[["timestamp", "warehouse_id", "value"]].to_string(index=False))
```

**Expected output:**

```
📦 Stock critically low (< 10 units): 2
          timestamp warehouse_id  value
 2026-06-15 13:00:00       WH-LAX    3.0
 2026-06-15 10:15:00       WH-LAX    8.0
```

!!! tip "Insight"
    Both critical stock events are at **WH-LAX** — stock dropped from 8 units to 3 units over a few hours. An AI agent would detect this trend and recommend an emergency restock before the warehouse runs out completely.

### 3c. Humidity Alerts (> 80%)

**KQL equivalent:**

```kql
SensorEvents
| where sensor_type == "humidity"
| where value > 80
| project timestamp, warehouse_id, value
```

**Python equivalent:**

```python
humidity = events[events["sensor_type"] == "humidity"]
humidity_alerts = humidity[humidity["value"] > 80]
print(f"💧 Humidity alerts (> 80%): {len(humidity_alerts)}")
print(humidity_alerts[["timestamp", "warehouse_id", "value"]].to_string(index=False))
```

**Expected output:**

```
💧 Humidity alerts (> 80%): 1
          timestamp warehouse_id  value
 2026-06-15 15:10:00       WH-CHI   85.0
```

---

## Step 4: Warehouse Activity Analysis

Analyze door open events per warehouse — unusually high activity may indicate security concerns or peak shipping periods:

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

**Expected output:**

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
    **WH-DAL leads with 14 total door opens** — combined with its two temperature anomalies (32°C and 35°C), frequent door openings could be letting hot air in. An AI agent would correlate these signals: _"Dallas warehouse has high door activity AND rising temperatures — consider adding an air curtain to loading dock 3."_

---

## Step 5: Build an Alert Dashboard

Combine all anomalies into a single summary dashboard that an AI agent would present to a warehouse operations manager:

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

**Expected output:**

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

!!! info "AI Agent Integration"
    In production, an AI agent would query the Eventhouse via KQL, run this anomaly detection logic, and post a natural-language summary to a Teams channel or email. Fabric Activator handles the automated alerting, while the AI agent provides the *interpretation* — turning raw numbers into actionable recommendations.

---

## 🐛 Bug-Fix Exercise

The file `lab-051/broken_alerting.py` has **3 bugs** that produce incorrect anomaly detection results. Run the self-tests:

```bash
python lab-051/broken_alerting.py
```

You should see **3 failed tests**:

| Test | What it checks | Hint |
|------|---------------|------|
| Test 1 | Temperature threshold is parameterized | The threshold is hardcoded to 50 instead of using the `threshold` parameter |
| Test 2 | Stock alert uses correct comparison | Stock alerts trigger when value is *below* the threshold, not above |
| Test 3 | Anomaly rate is calculated per warehouse | The denominator should be events *per warehouse*, not total events across all warehouses |

Fix all 3 bugs and re-run until you see `🎉 All 3 tests passed`.

---


## 🧠 Knowledge Check

??? question "**Q1 (Multiple Choice):** What is an Eventstream in Microsoft Fabric?"

    - A) A batch data processing pipeline that runs on a schedule
    - B) A managed real-time data ingestion pipeline that captures streaming events
    - C) A visualization tool for creating dashboards
    - D) A machine learning model training service

    ??? success "✅ Reveal Answer"
        **Correct: B) A managed real-time data ingestion pipeline that captures streaming events**

        An Eventstream is the entry point for real-time data in Fabric. It captures events from sources like IoT Hub, Kafka, or custom applications, transforms them in-flight, and routes them to destinations like an Eventhouse for querying. Unlike batch pipelines, Eventstreams process data continuously with sub-second latency.

??? question "**Q2 (Multiple Choice):** What does Fabric Activator do?"

    - A) Optimizes KQL query performance
    - B) Manages Eventhouse storage capacity
    - C) Triggers automated actions when data conditions are met
    - D) Converts batch data into streaming format

    ??? success "✅ Reveal Answer"
        **Correct: C) Triggers automated actions when data conditions are met**

        Activator is Fabric's rule engine for real-time alerting. You define conditions (e.g., "temperature > 30°C") and actions (e.g., send a Teams notification, trigger a Power Automate flow). It continuously monitors KQL query results and fires alerts the moment a condition is met — no polling required.

??? question "**Q3 (Run the Lab):** How many temperature readings exceed 30°C?"

    Filter the events DataFrame for `sensor_type == "temperature"` and `value > 30`.

    ??? success "✅ Reveal Answer"
        **3**

        Three temperature anomalies exceed 30°C: WH-NYC at 38°C, WH-DAL at 35°C, and WH-DAL at 32°C. The NYC reading at 38°C is the most critical — well above the 35°C threshold for product damage.

??? question "**Q4 (Run the Lab):** Which warehouse has the most door_opens?"

    Filter for `sensor_type == "door_opens"`, group by `warehouse_id`, and sum the values.

    ??? success "✅ Reveal Answer"
        **WH-DAL (14 total door opens)**

        Dallas leads with 14 total door opens, followed by WH-NYC (12), WH-SEA (10), WH-CHI (9), and WH-LAX (7). Combined with Dallas's two temperature anomalies, the high door activity may be contributing to heat buildup.

??? question "**Q5 (Run the Lab):** How many stock readings are critically low (< 10 units)?"

    Filter for `sensor_type == "stock_level"` and `value < 10`.

    ??? success "✅ Reveal Answer"
        **2**

        Two stock readings at WH-LAX are critically low: 8 units and 3 units. Both events are at the same warehouse, suggesting a rapid stock depletion trend that requires an emergency reorder.

---

## Summary

| Topic | What You Learned |
|-------|-----------------|
| Eventstreams | Real-time ingestion of IoT sensor data into Fabric |
| Eventhouse & KQL | Columnar storage and query language for time-series analytics |
| Anomaly Detection | Threshold-based alerts for temperature, humidity, and stock levels |
| Activator | Automated actions triggered by data conditions |
| AI Agent Integration | Agents query Eventhouse data and generate actionable recommendations |
| Alert Dashboard | Combining multiple anomaly types into a unified operations view |

---

## Next Steps

- **[Lab 052](lab-052-fabric-rti-advanced.md)** — Fabric RTI Advanced: Sliding-Window Aggregations & Trend Detection
- **[Lab 053](lab-053-fabric-agent-activator.md)** — Building an AI Agent with Fabric Activator & Semantic Kernel
