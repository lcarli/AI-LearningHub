---
tags: [foundry, agent-service, multi-agent, production, enterprise, python]
---
# Lab 074 : Foundry Agent Service — Déploiement multi-agents en production

<div class="lab-meta">
  <span><strong>Niveau :</strong> <span class="level-badge level-300">L300</span></span>
  <span><strong>Parcours :</strong> <a href="../paths/foundry/">🏭 Microsoft Foundry</a></span>
  <span><strong>Durée :</strong> ~120 min</span>
  <span><strong>💰 Coût :</strong> <span class="level-badge cost-free">Gratuit</span> — Utilise des données d'agents simulées</span>
</div>

## Ce que vous apprendrez

- Ce qu'est le **Foundry Agent Service** et comment il orchestre les systèmes multi-agents en production
- Comment les types d'agents (spécialiste, orchestrateur) collaborent dans un déploiement
- Analyser la santé de la flotte d'agents : volumes de requêtes, latence, taux d'erreur et statut
- Identifier les **agents dégradés** et les **risques de configuration** (par ex. filtres de contenu désactivés)
- Construire un **tableau de bord de santé de la flotte** pour le monitoring en production

## Introduction

Le **Azure AI Foundry Agent Service** fournit une plateforme managée pour déployer, orchestrer et surveiller des systèmes multi-agents à l'échelle de l'entreprise. Au lieu de construire une orchestration personnalisée, vous définissez des agents avec des outils, une mémoire et des modèles spécifiques — et le service gère le routage, la gestion d'état et la mise à l'échelle.

### Types d'agents

| Type | Rôle | Exemple |
|------|------|---------|
| **Orchestrateur** | Route les requêtes vers les spécialistes, gère le flux de conversation | SupportRouter, Coordinator |
| **Spécialiste** | Gère un domaine spécifique avec des outils et une mémoire dédiés | ProductAdvisor, OrderProcessor |

### Le scénario

Vous êtes un **SRE plateforme** gérant un déploiement multi-agents pour une entreprise de commerce en ligne. La flotte comprend **8 agents** — 2 orchestrateurs et 6 spécialistes — fonctionnant sur Azure Container Apps. Vous avez été alerté qu'un agent est dégradé et devez enquêter.

Votre jeu de données (`foundry_agents.csv`) contient le statut actuel de la flotte. Votre mission : analyser les métriques de santé, identifier les problèmes et produire un rapport de statut de la flotte.

!!! info "Données simulées"
    Ce lab utilise un CSV de flotte d'agents simulé qui reflète les métriques que vous verriez dans le tableau de bord de monitoring d'Azure AI Foundry. Les patterns (pics de latence, taux d'erreur, statut dégradé) représentent des scénarios courants en production.

## Prérequis

| Exigence | Raison |
|---|---|
| Python 3.10+ | Exécuter les scripts d'analyse |
| Bibliothèque `pandas` | Manipulation des données |

```bash
pip install pandas
```

---

!!! tip "Démarrage rapide avec GitHub Codespaces"
    [![Open in GitHub Codespaces](https://github.com/codespaces/badge.svg)](https://codespaces.new/lcarli/AI-LearningHub?quickstart=1)

    Toutes les dépendances sont pré-installées dans le devcontainer.


## 📦 Fichiers de support

!!! note "Téléchargez ces fichiers avant de commencer le lab"
    Enregistrez tous les fichiers dans un dossier `lab-074/` de votre répertoire de travail.

| Fichier | Description | Téléchargement |
|------|-------------|----------|
| `broken_foundry.py` | Exercice de correction de bugs (3 bugs + auto-tests) | [📥 Télécharger](https://github.com/lcarli/AI-LearningHub/raw/main/docs/docs/en/labs/lab-074/broken_foundry.py) |
| `foundry_agents.csv` | Jeu de données | [📥 Télécharger](https://github.com/lcarli/AI-LearningHub/raw/main/docs/docs/en/labs/lab-074/foundry_agents.csv) |

---

## Étape 1 : Comprendre l'architecture de la flotte

Avant d'analyser les données, comprenez comment les agents s'articulent :

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

### Champs de configuration clés

| Champ | Description |
|-------|-----------|
| **memory_type** | Comment l'agent persiste son état : `cosmos_db` (durable), `ai_search` (vectoriel), `session_only` (éphémère), `none` |
| **deployment** | Infrastructure : `container_apps` (managé) ou `vm` (auto-hébergé) |
| **content_filter** | Si la sécurité du contenu Azure AI est `enabled` ou `disabled` |
| **status** | Santé de l'agent : `active` ou `degraded` |

---

## Étape 2 : Charger et explorer les données de la flotte

```python
import pandas as pd

df = pd.read_csv("lab-074/foundry_agents.csv")

print(f"Total agents: {len(df)}")
print(f"Agent types: {df['agent_type'].value_counts().to_dict()}")
print(f"Statuses: {df['status'].value_counts().to_dict()}")
print(f"\nFull fleet:")
print(df[["agent_id", "agent_name", "agent_type", "model", "status"]].to_string(index=False))
```

**Sortie attendue :**

```
Total agents: 8
Agent types: {'specialist': 6, 'orchestrator': 2}
Statuses: {'active': 7, 'degraded': 1}
```

---

## Étape 3 : Analyser le volume de requêtes et la distribution de charge

Comment le trafic est-il distribué dans la flotte ?

```python
total_requests = df["requests_24h"].sum()
print(f"Total 24h requests across fleet: {total_requests:,}")

print("\nRequest distribution:")
for _, row in df.sort_values("requests_24h", ascending=False).iterrows():
    pct = row["requests_24h"] / total_requests * 100
    bar = "█" * int(pct / 2)
    print(f"  {row['agent_name']:>20s}: {row['requests_24h']:>5,}  ({pct:>5.1f}%) {bar}")
```

**Sortie attendue :**

```
Total 24h requests across fleet: 9,380
```

| Agent | Requêtes | Part |
|-------|----------|-------|
| Coordinator | 3 200 | 34,1 % |
| SupportRouter | 2 100 | 22,4 % |
| ProductAdvisor | 1 250 | 13,3 % |
| OrderProcessor | 890 | 9,5 % |
| QualityReviewer | 780 | 8,3 % |
| InventoryMonitor | 560 | 6,0 % |
| AnalyticsAgent | 420 | 4,5 % |
| LegacyBridge | 180 | 1,9 % |

!!! tip "Insight"
    Le **Coordinator orchestrateur gère 34 % de tout le trafic** — c'est le point d'entrée de la plupart des requêtes. S'il tombe en panne, tout le système est affecté. Le SupportRouter est le deuxième plus sollicité, routant les requêtes de support client vers les spécialistes.

---

## Étape 4 : Identifier les agents dégradés et à risque

### 4a — Agents dégradés

```python
degraded = df[df["status"] == "degraded"]
print(f"Degraded agents: {len(degraded)}")
for _, agent in degraded.iterrows():
    print(f"\n  Agent: {agent['agent_name']} ({agent['agent_id']})")
    print(f"  Error rate: {agent['error_rate_pct']}%")
    print(f"  Avg latency: {agent['avg_latency_ms']}ms")
    print(f"  Requests: {agent['requests_24h']}")
```

**Sortie attendue :**

```
Degraded agents: 1

  Agent: AnalyticsAgent (FA07)
  Error rate: 8.5%
  Avg latency: 850ms
  Requests: 420
```

### 4b — Agents avec taux d'erreur élevé

```python
high_error = df[df["error_rate_pct"] > 5.0]
print(f"\nAgents with error rate > 5%: {len(high_error)}")
for _, agent in high_error.iterrows():
    print(f"  {agent['agent_name']}: {agent['error_rate_pct']}% errors")
```

### 4c — Statut du filtre de contenu

```python
disabled_filter = df[df["content_filter"] == "disabled"]
print(f"\nAgents with disabled content filter: {len(disabled_filter)}")
for _, agent in disabled_filter.iterrows():
    print(f"  {agent['agent_name']} ({agent['agent_id']}) — deployment: {agent['deployment']}")
```

!!! warning "Risque de sécurité"
    **LegacyBridge (FA08)** a son filtre de contenu **désactivé** et fonctionne sur une VM auto-hébergée. C'est un risque de conformité — tous les agents en production devraient avoir la sécurité du contenu activée, en particulier ceux qui traitent des données clients.

---

## Étape 5 : Analyser les patterns de mémoire et d'infrastructure

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

## Étape 6 : Construire le rapport de santé de la flotte

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

## 🐛 Exercice de correction de bugs

Le fichier `lab-074/broken_foundry.py` contient **3 bugs** qui produisent des métriques de flotte incorrectes. Pouvez-vous les trouver et les corriger tous ?

Exécutez les auto-tests pour voir lesquels échouent :

```bash
python lab-074/broken_foundry.py
```

Vous devriez voir **3 tests échoués**. Chaque test correspond à un bug :

| Test | Ce qu'il vérifie | Indice |
|------|---------------|------|
| Test 1 | Total des requêtes sur 24h | Devrait sommer les requêtes, pas les moyenner |
| Test 2 | Nombre d'agents dégradés | Devrait compter le statut `degraded`, pas `active` |
| Test 3 | Agents sans mémoire durable | Devrait compter `none`/`session_only`, pas `cosmos_db` |

Corrigez les 3 bugs, puis relancez. Quand vous voyez `All passed!`, c'est terminé !

---


## 🧠 Vérification des connaissances

??? question "**Q1 (Choix multiple) :** Quel est le rôle d'un agent orchestrateur dans un déploiement multi-agents Foundry ?"

    - A) Il effectue une tâche de domaine spécifique comme le traitement des commandes
    - B) Il route les requêtes vers les agents spécialistes et gère le flux de conversation
    - C) Il stocke la mémoire de l'agent dans Cosmos DB
    - D) Il surveille la santé des agents et redémarre les agents en échec

    ??? success "✅ Révéler la réponse"
        **Correct : B) Il route les requêtes vers les agents spécialistes et gère le flux de conversation**

        Les agents orchestrateurs agissent comme le « contrôleur de trafic » dans un système multi-agents. Ils reçoivent les requêtes entrantes, déterminent quel(s) spécialiste(s) doivent les traiter, routent la conversation en conséquence et gèrent le flux global. Les spécialistes gèrent le travail spécifique au domaine.

??? question "**Q2 (Choix multiple) :** Pourquoi un filtre de contenu désactivé est-il un risque de sécurité pour les agents en production ?"

    - A) Cela rend l'agent plus lent
    - B) Cela permet à l'agent de générer du contenu nuisible, biaisé ou violant les politiques
    - C) Cela empêche l'agent d'accéder aux API externes
    - D) Cela augmente les coûts en tokens

    ??? success "✅ Révéler la réponse"
        **Correct : B) Cela permet à l'agent de générer du contenu nuisible, biaisé ou violant les politiques**

        Les filtres Azure AI Content Safety détectent et bloquent le contenu nuisible (discours haineux, violence, automutilation, contenu sexuel). Désactiver le filtre signifie que l'agent peut produire ou répondre à un tel contenu sans garde-fous — un risque de conformité et de réputation dans tout déploiement de production.

??? question "**Q3 (Exécutez le lab) :** Quel est le nombre total de requêtes dans toute la flotte au cours des dernières 24 heures ?"

    Exécutez l'analyse de l'étape 3 sur [📥 `foundry_agents.csv`](https://github.com/lcarli/AI-LearningHub/raw/main/docs/docs/en/labs/lab-074/foundry_agents.csv) et vérifiez les résultats.

    ??? success "✅ Révéler la réponse"
        **9 380 requêtes**

        Somme de toutes les valeurs `requests_24h` des agents : 1 250 + 890 + 2 100 + 560 + 3 200 + 780 + 420 + 180 = **9 380**.

??? question "**Q4 (Exécutez le lab) :** Combien d'agents sont dans un état dégradé ?"

    Exécutez l'analyse de l'étape 4a pour le découvrir.

    ??? success "✅ Révéler la réponse"
        **1 agent**

        Seul **AnalyticsAgent (FA07)** est dans un état `degraded`, avec un taux d'erreur de 8,5 % et une latence moyenne de 850 ms — nettement pire que les autres agents. Cela indique probablement un problème de connectivité backend avec son magasin de mémoire AI Search.

??? question "**Q5 (Exécutez le lab) :** Combien d'agents ont leur filtre de contenu désactivé ?"

    Exécutez l'analyse de l'étape 4c pour vérifier le statut du filtre de contenu.

    ??? success "✅ Révéler la réponse"
        **1 agent**

        Seul **LegacyBridge (FA08)** a `content_filter=disabled`. C'est aussi le seul agent déployé sur une VM auto-hébergée plutôt que sur Container Apps, et il a le taux d'erreur le plus élevé (12,0 %) de la flotte. Cet agent nécessite une attention immédiate.

---

## Résumé

| Sujet | Ce que vous avez appris |
|-------|-----------------|
| Foundry Agent Service | Plateforme managée pour l'orchestration et le déploiement multi-agents |
| Types d'agents | Les orchestrateurs routent ; les spécialistes exécutent les tâches de domaine |
| Monitoring de la flotte | Suivre les requêtes, la latence, les taux d'erreur et le statut par agent |
| Détection de dégradation | Identifier les agents avec des taux d'erreur ou une latence élevés |
| Sécurité du contenu | Tous les agents en production devraient avoir les filtres de contenu activés |
| Patterns de mémoire | Cosmos DB pour le durable, AI Search pour le vectoriel, session_only pour l'éphémère |

---

## Prochaines étapes

- **[Lab 034](lab-034-multi-agent-sk.md)** — Multi-agents avec Semantic Kernel (construire les agents eux-mêmes)
- **[Lab 033](lab-033-agent-observability.md)** — Observabilité des agents avec Application Insights (monitoring approfondi)
- **[Lab 030](lab-030-foundry-agent-mcp.md)** — Foundry Agent + MCP (connecter les agents à des outils externes)
- **[Lab 075](lab-075-powerbi-copilot.md)** — Power BI Copilot (visualiser les données de flotte avec des tableaux de bord assistés par IA)