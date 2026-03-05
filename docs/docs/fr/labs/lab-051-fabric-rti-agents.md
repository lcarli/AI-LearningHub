---
tags: [fabric, real-time-intelligence, kql, eventstreams, iot, python]
---
# Lab 051 : Fabric IQ — Agents Real-Time Intelligence

<div class="lab-meta">
  <span><strong>Niveau :</strong> <span class="level-badge level-300">L300</span></span>
  <span><strong>Parcours :</strong> Tous les parcours</span>
  <span><strong>Durée :</strong> ~75 min</span>
  <span><strong>💰 Coût :</strong> <span class="level-badge cost-free">Gratuit</span> — Utilise un jeu de données simulé inclus (capacité Fabric optionnelle)</span>
</div>

## Ce que vous apprendrez

- Comment les **Eventstreams** ingèrent des données de capteurs IoT en temps réel dans Microsoft Fabric
- Interroger des données en streaming avec **KQL (Kusto Query Language)** pour une détection instantanée des anomalies
- Détecter les **anomalies de température, d'humidité et de stock** à l'aide de règles basées sur des seuils
- Utiliser **Fabric Activator** pour déclencher des alertes automatisées lorsque des conditions sont remplies
- Construire un **agent IA** qui lit les données en temps réel et fait remonter des informations exploitables
- Analyser les **modèles d'activité des entrepôts** (ouvertures de portes, fréquence des capteurs) à travers les sites

## Introduction

![Fabric RTI Pipeline](../../assets/diagrams/fabric-rti-pipeline.svg)

**Real-Time Intelligence (RTI)** dans Microsoft Fabric est une plateforme entièrement managée pour capturer, transformer et agir sur les données en streaming — le tout au sein de l'espace de travail Fabric. Contrairement aux pipelines batch traditionnels qui traitent les données des heures ou des jours après leur arrivée, RTI vous offre une visibilité en moins d'une seconde sur ce qui se passe *en ce moment*.

### Le scénario

OutdoorGear Inc. exploite **5 entrepôts** à travers les États-Unis (New York, Los Angeles, Chicago, Dallas et Seattle). Chaque entrepôt est équipé de capteurs IoT surveillant quatre métriques clés :

| Type de capteur | Ce qu'il mesure | Seuil critique |
|-----------------|-----------------|----------------|
| **temperature** | Température ambiante (°C) | > 30°C (risque de dommages aux produits) |
| **humidity** | Humidité relative (%) | > 80% (risque de dommages par l'humidité) |
| **stock_level** | Unités restantes dans le bac | < 10 unités (réapprovisionnement urgent) |
| **door_opens** | Nombre d'ouvertures de porte par intervalle | Activité élevée = trafic inhabituel |

Un agent IA surveille ces flux de capteurs en temps réel, détecte les anomalies et déclenche des alertes — afin que les responsables d'entrepôt puissent agir avant que les produits ne soient endommagés ou que le stock ne soit épuisé.

---

## Prérequis

| Exigence | Pourquoi |
|---|---|
| Python 3.10+ | Exécuter les scripts d'analyse |
| `pandas` | Analyser les données d'événements des capteurs |

```bash
pip install pandas
```

---

!!! tip "Démarrage rapide avec GitHub Codespaces"
    [![Open in GitHub Codespaces](https://github.com/codespaces/badge.svg)](https://codespaces.new/lcarli/AI-LearningHub?quickstart=1)

    Toutes les dépendances sont pré-installées dans le devcontainer.


## 📦 Fichiers de support

!!! note "Téléchargez ces fichiers avant de commencer le lab"
    Enregistrez tous les fichiers dans un dossier `lab-051/` dans votre répertoire de travail.

| Fichier | Description | Télécharger |
|---------|-------------|-------------|
| `broken_alerting.py` | Exercice de correction de bugs (3 bugs + auto-tests) | [📥 Télécharger](https://github.com/lcarli/AI-LearningHub/raw/main/docs/docs/en/labs/lab-051/broken_alerting.py) |
| `sensor_events.csv` | Jeu de données | [📥 Télécharger](https://github.com/lcarli/AI-LearningHub/raw/main/docs/docs/en/labs/lab-051/sensor_events.csv) |

---

## Étape 1 : Comprendre Fabric Real-Time Intelligence

Avant d'écrire du code, comprenez les quatre composants RTI qui forment le pipeline de bout en bout :

| Composant | Rôle | Analogie |
|-----------|------|----------|
| **Eventstream** | Pipeline d'ingestion de données en temps réel managé — capture les événements depuis les hubs IoT, Kafka ou des applications personnalisées | Le tapis roulant qui amène les données |
| **Eventhouse** | Base de données en colonnes optimisée pour les séries temporelles et les données en streaming ; stocke les événements pour l'interrogation | L'entrepôt où les données sont stockées |
| **KQL (Kusto Query Language)** | Langage de requête pour filtrer, agréger et analyser les données de séries temporelles à grande échelle | Le SQL de l'analytique en temps réel |
| **Activator** | Moteur de règles qui déclenche des actions automatisées (e-mails, messages Teams, flux Power Automate) lorsque des conditions sur les données sont remplies | Le système d'alarme qui réagit aux anomalies |

### Comment ils fonctionnent ensemble

```
IoT Sensors → Eventstream → Eventhouse → KQL Queries → Activator → Alerts
                (ingest)     (store)      (analyze)     (act)
```

1. **Eventstream** capture les événements bruts des capteurs (charges utiles JSON) depuis IoT Hub ou des sources personnalisées
2. Les événements arrivent dans une table **Eventhouse** (`SensorEvents`) pour une interrogation en colonnes rapide
3. Les **requêtes KQL** s'exécutent sur l'Eventhouse pour détecter les anomalies en quasi temps réel
4. **Activator** surveille les résultats des requêtes KQL et déclenche des alertes lorsque les conditions sont remplies
5. Un **agent IA** peut interroger directement l'Eventhouse, corréler les anomalies et générer des résumés en langage naturel pour les responsables d'entrepôt

!!! info "Ce lab utilise des données simulées"
    En production, les événements circulent en continu depuis IoT Hub via les Eventstreams. Dans ce lab, nous simulons le pipeline avec un instantané CSV de 50 événements de capteurs et utilisons pandas pour démontrer les requêtes équivalentes à KQL. La logique correspond 1:1 à la production KQL.

---

## Étape 2 : Charger et explorer les événements des capteurs

Le jeu de données contient **50 événements de capteurs** provenant de **5 entrepôts** couvrant les 4 types de capteurs :

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

**Sortie attendue :**

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

### Aperçu des données

```python
print(events[["timestamp", "warehouse_id", "sensor_type", "value"]].head(10).to_string(index=False))
```

Chaque événement possède un `timestamp`, un `warehouse_id`, un `sensor_type` et une `value` numérique. C'est la forme des données qu'un Eventstream délivrerait dans une table Eventhouse.

---

## Étape 3 : Détection d'anomalies à la manière KQL

En production avec Fabric, vous écririez des requêtes KQL sur l'Eventhouse. Ici, nous utilisons pandas pour reproduire la même logique — chaque filtre pandas correspond directement à une clause `where` KQL.

### 3a. Anomalies de température (> 30°C)

**Équivalent KQL :**

```kql
SensorEvents
| where sensor_type == "temperature"
| where value > 30
| project timestamp, warehouse_id, value
| order by value desc
```

**Équivalent Python :**

```python
temp = events[events["sensor_type"] == "temperature"]
temp_anomalies = temp[temp["value"] > 30].sort_values("value", ascending=False)
print(f"🌡️ Temperature anomalies (> 30°C): {len(temp_anomalies)}")
print(temp_anomalies[["timestamp", "warehouse_id", "value"]].to_string(index=False))
```

**Sortie attendue :**

```
🌡️ Temperature anomalies (> 30°C): 3
          timestamp warehouse_id  value
 2026-06-15 14:20:00       WH-NYC   38.0
 2026-06-15 11:45:00       WH-DAL   35.0
 2026-06-15 09:30:00       WH-DAL   32.0
```

!!! warning "Alerte critique"
    WH-NYC à **38°C** est dangereusement élevé — les denrées périssables et l'électronique peuvent être endommagés au-dessus de 35°C. Une règle Activator notifierait immédiatement le responsable de l'entrepôt de NYC et déclencherait le système CVC.

### 3b. Stock critique (< 10 unités)

**Équivalent KQL :**

```kql
SensorEvents
| where sensor_type == "stock_level"
| where value < 10
| project timestamp, warehouse_id, value
| order by value asc
```

**Équivalent Python :**

```python
stock = events[events["sensor_type"] == "stock_level"]
stock_critical = stock[stock["value"] < 10].sort_values("value")
print(f"📦 Stock critically low (< 10 units): {len(stock_critical)}")
print(stock_critical[["timestamp", "warehouse_id", "value"]].to_string(index=False))
```

**Sortie attendue :**

```
📦 Stock critically low (< 10 units): 2
          timestamp warehouse_id  value
 2026-06-15 13:00:00       WH-LAX    3.0
 2026-06-15 10:15:00       WH-LAX    8.0
```

!!! tip "Observation"
    Les deux événements de stock critique sont à **WH-LAX** — le stock est passé de 8 unités à 3 unités en quelques heures. Un agent IA détecterait cette tendance et recommanderait un réapprovisionnement d'urgence avant que l'entrepôt ne soit complètement en rupture de stock.

### 3c. Alertes d'humidité (> 80%)

**Équivalent KQL :**

```kql
SensorEvents
| where sensor_type == "humidity"
| where value > 80
| project timestamp, warehouse_id, value
```

**Équivalent Python :**

```python
humidity = events[events["sensor_type"] == "humidity"]
humidity_alerts = humidity[humidity["value"] > 80]
print(f"💧 Humidity alerts (> 80%): {len(humidity_alerts)}")
print(humidity_alerts[["timestamp", "warehouse_id", "value"]].to_string(index=False))
```

**Sortie attendue :**

```
💧 Humidity alerts (> 80%): 1
          timestamp warehouse_id  value
 2026-06-15 15:10:00       WH-CHI   85.0
```

---

## Étape 4 : Analyse de l'activité des entrepôts

Analysez les événements d'ouverture de portes par entrepôt — une activité anormalement élevée peut indiquer des problèmes de sécurité ou des périodes d'expédition de pointe :

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

**Sortie attendue :**

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

!!! tip "Observation"
    **WH-DAL est en tête avec 14 ouvertures de portes au total** — combiné avec ses deux anomalies de température (32°C et 35°C), les ouvertures fréquentes de portes pourraient laisser entrer l'air chaud. Un agent IA corrèlerait ces signaux : _« L'entrepôt de Dallas a une forte activité de portes ET des températures en hausse — envisagez d'ajouter un rideau d'air au quai de chargement 3. »_

---

## Étape 5 : Construire un tableau de bord d'alertes

Combinez toutes les anomalies dans un tableau de bord récapitulatif unique qu'un agent IA présenterait à un responsable des opérations d'entrepôt :

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

**Sortie attendue :**

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

!!! info "Intégration d'un agent IA"
    En production, un agent IA interrogerait l'Eventhouse via KQL, exécuterait cette logique de détection d'anomalies et publierait un résumé en langage naturel dans un canal Teams ou par e-mail. Fabric Activator gère les alertes automatisées, tandis que l'agent IA fournit l'*interprétation* — transformant les chiffres bruts en recommandations exploitables.

---

## 🐛 Exercice de correction de bugs

Le fichier `lab-051/broken_alerting.py` contient **3 bugs** qui produisent des résultats incorrects de détection d'anomalies. Exécutez les auto-tests :

```bash
python lab-051/broken_alerting.py
```

Vous devriez voir **3 tests échoués** :

| Test | Ce qu'il vérifie | Indice |
|------|-------------------|--------|
| Test 1 | Le seuil de température est paramétré | Le seuil est codé en dur à 50 au lieu d'utiliser le paramètre `threshold` |
| Test 2 | L'alerte de stock utilise la bonne comparaison | Les alertes de stock se déclenchent quand la valeur est *inférieure* au seuil, pas supérieure |
| Test 3 | Le taux d'anomalies est calculé par entrepôt | Le dénominateur devrait être les événements *par entrepôt*, pas le total des événements de tous les entrepôts |

Corrigez les 3 bugs et relancez jusqu'à voir `🎉 All 3 tests passed`.

---


## 🧠 Vérification des connaissances

??? question "**Q1 (Choix multiple) :** Qu'est-ce qu'un Eventstream dans Microsoft Fabric ?"

    - A) Un pipeline de traitement de données par lots qui s'exécute selon un calendrier
    - B) Un pipeline d'ingestion de données en temps réel managé qui capture les événements en streaming
    - C) Un outil de visualisation pour créer des tableaux de bord
    - D) Un service d'entraînement de modèles de machine learning

    ??? success "✅ Révéler la réponse"
        **Correct : B) Un pipeline d'ingestion de données en temps réel managé qui capture les événements en streaming**

        Un Eventstream est le point d'entrée des données en temps réel dans Fabric. Il capture les événements provenant de sources comme IoT Hub, Kafka ou des applications personnalisées, les transforme en vol et les achemine vers des destinations comme un Eventhouse pour l'interrogation. Contrairement aux pipelines batch, les Eventstreams traitent les données en continu avec une latence inférieure à la seconde.

??? question "**Q2 (Choix multiple) :** Que fait Fabric Activator ?"

    - A) Optimise les performances des requêtes KQL
    - B) Gère la capacité de stockage de l'Eventhouse
    - C) Déclenche des actions automatisées lorsque des conditions sur les données sont remplies
    - D) Convertit les données par lots en format streaming

    ??? success "✅ Révéler la réponse"
        **Correct : C) Déclenche des actions automatisées lorsque des conditions sur les données sont remplies**

        Activator est le moteur de règles de Fabric pour les alertes en temps réel. Vous définissez des conditions (par ex. « temperature > 30°C ») et des actions (par ex. envoyer une notification Teams, déclencher un flux Power Automate). Il surveille en continu les résultats des requêtes KQL et déclenche des alertes dès qu'une condition est remplie — sans interrogation périodique nécessaire.

??? question "**Q3 (Exécuter le lab) :** Combien de relevés de température dépassent 30°C ?"

    Filtrez le DataFrame des événements pour `sensor_type == "temperature"` et `value > 30`.

    ??? success "✅ Révéler la réponse"
        **3**

        Trois anomalies de température dépassent 30°C : WH-NYC à 38°C, WH-DAL à 35°C et WH-DAL à 32°C. Le relevé de NYC à 38°C est le plus critique — bien au-dessus du seuil de 35°C pour les dommages aux produits.

??? question "**Q4 (Exécuter le lab) :** Quel entrepôt a le plus de door_opens ?"

    Filtrez pour `sensor_type == "door_opens"`, regroupez par `warehouse_id` et faites la somme des valeurs.

    ??? success "✅ Révéler la réponse"
        **WH-DAL (14 ouvertures de portes au total)**

        Dallas est en tête avec 14 ouvertures de portes au total, suivi de WH-NYC (12), WH-SEA (10), WH-CHI (9) et WH-LAX (7). Combiné avec les deux anomalies de température de Dallas, la forte activité de portes peut contribuer à l'accumulation de chaleur.

??? question "**Q5 (Exécuter le lab) :** Combien de relevés de stock sont en niveau critique (< 10 unités) ?"

    Filtrez pour `sensor_type == "stock_level"` et `value < 10`.

    ??? success "✅ Révéler la réponse"
        **2**

        Deux relevés de stock à WH-LAX sont en niveau critique : 8 unités et 3 unités. Les deux événements sont dans le même entrepôt, ce qui suggère une tendance rapide d'épuisement des stocks nécessitant un réapprovisionnement d'urgence.

---

## Résumé

| Sujet | Ce que vous avez appris |
|-------|------------------------|
| Eventstreams | Ingestion en temps réel des données de capteurs IoT dans Fabric |
| Eventhouse & KQL | Stockage en colonnes et langage de requête pour l'analytique de séries temporelles |
| Détection d'anomalies | Alertes basées sur des seuils pour la température, l'humidité et les niveaux de stock |
| Activator | Actions automatisées déclenchées par des conditions sur les données |
| Intégration d'un agent IA | Les agents interrogent les données de l'Eventhouse et génèrent des recommandations exploitables |
| Tableau de bord d'alertes | Combinaison de plusieurs types d'anomalies dans une vue opérationnelle unifiée |

---

## Prochaines étapes

- **[Lab 052](lab-052-fabric-rti-advanced.md)** — Fabric RTI Avancé : Agrégations par fenêtre glissante et détection de tendances
- **[Lab 053](lab-053-fabric-agent-activator.md)** — Construire un agent IA avec Fabric Activator & Semantic Kernel
