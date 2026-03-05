---
tags: [a2a, mcp, multi-agent, architecture, capstone, python]
---
# Lab 055 : A2A + MCP Full Stack — Capstone d'interopérabilité des agents

<div class="lab-meta">
  <span><strong>Niveau :</strong> <span class="level-badge level-400">L400</span></span>
  <span><strong>Parcours :</strong> <a href="../paths/pro-code/">⚙️ Pro Code</a></span>
  <span><strong>Durée :</strong> ~120 min</span>
  <span><strong>💰 Coût :</strong> <span class="level-badge cost-free">Gratuit</span> — Utilise des données de traces simulées (aucune ressource cloud requise)</span>
</div>

!!! tip "Les trois protocoles agentiques"
    Ce capstone couvre A2A + MCP. Le troisième protocole — **AG-UI** (interaction agent↔utilisateur) — est traité dans le **[Lab 077](lab-077-agui-protocol.md)**.

## Ce que vous apprendrez

- Comment **A2A + MCP** fonctionnent ensemble dans une architecture multi-agents full-stack
- Analyser un **système de planification de voyage** avec 3 agents spécialisés à l'aide de traces de délégation
- Distinguer les **appels A2A** (délégation agent-à-agent) des **appels MCP** (accès agent-outil)
- Effectuer une **analyse du coût en tokens** dans un système d'agents distribué
- Comprendre les **modèles de gestion d'erreurs et de relance** dans les workflows multi-agents
- Appliquer des **principes de conception** pour construire des architectures d'agents de qualité production

## Introduction

A2A et MCP sont des **protocoles complémentaires** qui remplissent des rôles différents dans un système multi-agents :

| Protocole | Rôle | Exemple |
|-----------|------|---------|
| **A2A** | Délégation de tâches agent-à-agent | Le coordinateur demande à FlightAgent de trouver des vols |
| **MCP** | Accès agent-outil | FlightAgent appelle une API de réservation via un serveur MCP |

Dans ce lab capstone, vous analyserez un **système de planification de voyage** qui utilise les deux protocoles. L'agent coordinateur reçoit une demande client et délègue des sous-tâches à des agents spécialisés via A2A. Chaque agent spécialisé utilise ensuite MCP pour accéder à ses outils et APIs back-end.

### L'architecture

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

Le jeu de données des traces de délégation (`delegation_traces.csv`) capture **20 événements** d'une session complète de planification de voyage — 8 appels A2A entre agents et 12 appels MCP des agents vers les outils.

!!! info "Pourquoi deux protocoles ?"
    A2A gère la couche *sociale* — les agents se découvrent, négocient et délèguent des tâches à leurs pairs. MCP gère la couche *outils* — les agents accèdent aux bases de données, APIs et services externes. Séparer ces préoccupations permet une mise à l'échelle indépendante, des périmètres de sécurité distincts et une évolution indépendante des protocoles.

## Prérequis

| Exigence | Pourquoi |
|----------|----------|
| Python 3.10+ | Analyser les traces de délégation |
| Bibliothèque `pandas` | Opérations DataFrame sur les données de traces |

```bash
pip install pandas
```

---

!!! tip "Démarrage rapide avec GitHub Codespaces"
    [![Open in GitHub Codespaces](https://github.com/codespaces/badge.svg)](https://codespaces.new/lcarli/AI-LearningHub?quickstart=1)

    Toutes les dépendances sont pré-installées dans le devcontainer.


## 📦 Fichiers de support

!!! note "Téléchargez ces fichiers avant de commencer le lab"
    Enregistrez tous les fichiers dans un dossier `lab-055/` dans votre répertoire de travail.

| Fichier | Description | Télécharger |
|---------|-------------|-------------|
| `broken_delegation.py` | Exercice de correction de bugs (3 bugs + auto-tests) | [📥 Télécharger](https://github.com/lcarli/AI-LearningHub/raw/main/docs/docs/en/labs/lab-055/broken_delegation.py) |
| `delegation_traces.csv` | Jeu de données | [📥 Télécharger](https://github.com/lcarli/AI-LearningHub/raw/main/docs/docs/en/labs/lab-055/delegation_traces.csv) |

---

## Étape 1 : Comprendre l'architecture

Avant de plonger dans les données, comprenez ce que fait chaque composant :

### Rôles des agents

| Agent | Rôle A2A | Outils MCP |
|-------|----------|------------|
| **Coordinator** | Reçoit la demande client, délègue aux spécialistes | Aucun (orchestration uniquement) |
| **FlightAgent** | Trouve et réserve des vols | `booking_api`, `pricing_api`, `payment_api` |
| **HotelAgent** | Trouve et réserve des hôtels | `booking_api`, `reviews_api` |
| **ItineraryAgent** | Planifie et met à jour les itinéraires | `maps_api`, `calendar_api`, `weather_api` |

### Flux d'appels

1. Le client envoie une demande de voyage au **Coordinator**
2. Le coordinateur utilise **A2A** pour déléguer des sous-tâches (trouver des vols, trouver des hôtels, planifier l'itinéraire)
3. Chaque spécialiste utilise **MCP** pour appeler ses outils back-end
4. Les résultats remontent via A2A vers le coordinateur
5. Le coordinateur assemble la réponse finale

### Périmètres des protocoles

| Périmètre | Protocole | Auth |
|------------|----------|------|
| Client → Coordinator | HTTP/API | Clé API |
| Coordinator → Spécialistes | **A2A** | OAuth 2.0 |
| Spécialistes → Outils | **MCP** | Jetons service-à-service |

!!! tip "OAuth à travers les périmètres A2A"
    Lorsque le coordinateur délègue à FlightAgent via A2A, il doit transmettre un jeton OAuth limité aux permissions du client. FlightAgent utilise ensuite un jeton de service *séparé* pour ses appels MCP vers l'API de réservation. Ce modèle d'authentification à deux couches empêche l'escalade de privilèges.

---

## Étape 2 : Charger et explorer les traces de délégation

Chargez les données de traces contenant les 20 événements de la session de planification de voyage :

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

**Sortie attendue :**

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

## Étape 3 : Analyser les modèles d'appels A2A vs MCP

Séparez les traces par protocole pour comprendre la structure de délégation :

### 3a — Nombre d'appels par protocole

```python
a2a_calls = traces[traces["protocol"] == "A2A"]
mcp_calls = traces[traces["protocol"] == "MCP"]

print(f"A2A calls (agent → agent): {len(a2a_calls)}")
print(f"MCP calls (agent → tool):  {len(mcp_calls)}")
print(f"Total calls:               {len(traces)}")
```

**Sortie attendue :**

```
A2A calls (agent → agent): 8
MCP calls (agent → tool):  12
Total calls:               20
```

### 3b — Détail des délégations A2A

```python
print("A2A Delegations (Coordinator → Specialists):")
print(a2a_calls[["request_id", "source_agent", "target_agent", "action", "status"]].to_string(index=False))
```

**Sortie attendue :**

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

### 3c — Utilisation des outils MCP par agent

```python
print("MCP tool calls per agent:")
print(mcp_calls.groupby("source_agent")["action"].count().to_string())
print(f"\nUnique MCP tools used: {mcp_calls['target_agent'].nunique()}")
```

**Sortie attendue :**

```
MCP tool calls per agent:
source_agent
FlightAgent       5
HotelAgent        3
ItineraryAgent    4

Unique MCP tools used: 7
```

### 3d — Analyse des erreurs

```python
errors = traces[traces["status"] == "ERROR"]
print(f"Total errors: {len(errors)}")
print(f"\nFailed events:")
print(errors[["request_id", "source_agent", "target_agent", "protocol", "action"]].to_string(index=False))
```

**Sortie attendue :**

```
Total errors: 2

Failed events:
request_id source_agent target_agent protocol         action
      R006  Coordinator  FlightAgent      A2A   find_flights
      R006  FlightAgent  booking_api      MCP search_flights
```

!!! warning "Défaillances en cascade"
    Remarquez que R006 a des erreurs à la fois dans l'appel A2A et l'appel MCP. Lorsque l'outil MCP `booking_api` échoue, FlightAgent ne peut pas terminer la tâche A2A — l'erreur se propage vers le haut. Les systèmes de production nécessitent une logique de relance et des disjoncteurs aux deux périmètres de protocole.

---

## Étape 4 : Analyse du coût en tokens

Les appels A2A consomment des tokens LLM (les agents raisonnent sur les tâches), tandis que les appels MCP sont généralement sans tokens (appels API directs) :

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

**Sortie attendue :**

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

### Répartition des coûts

```python
COST_PER_1K_TOKENS = 0.005  # example: GPT-4o-mini pricing

cost = total_tokens / 1000 * COST_PER_1K_TOKENS
print(f"Estimated cost at ${COST_PER_1K_TOKENS}/1K tokens: ${cost:.4f}")
print(f"Average tokens per A2A call: {a2a_tokens / len(a2a_calls):.0f}")
print(f"Most expensive call: {a2a_calls.loc[a2a_calls['tokens_used'].idxmax(), 'action']} "
      f"({a2a_calls['tokens_used'].max()} tokens)")
```

---

## Étape 5 : Modèles de gestion d'erreurs et de relance

Analysez comment les erreurs se propagent et concevez des stratégies de relance :

### 5a — Taux d'erreur par protocole

```python
for protocol in ["A2A", "MCP"]:
    subset = traces[traces["protocol"] == protocol]
    error_count = (subset["status"] == "ERROR").sum()
    total = len(subset)
    print(f"{protocol}: {error_count}/{total} errors ({error_count/total*100:.0f}%)")
```

**Sortie attendue :**

```
A2A: 1/8 errors (12%)
MCP: 1/12 errors (8%)
```

### 5b — Analyse de la latence

```python
print("Average latency by protocol:")
print(traces.groupby("protocol")["duration_ms"].mean().to_string())

print(f"\nSlowest call: {traces.loc[traces['duration_ms'].idxmax(), 'action']} "
      f"({traces['duration_ms'].max()} ms)")
print(f"Fastest call: {traces.loc[traces['duration_ms'].idxmin(), 'action']} "
      f"({traces['duration_ms'].min()} ms)")
```

### 5c — Modèles de conception pour la relance

| Modèle | Couche A2A | Couche MCP |
|--------|------------|------------|
| **Relance** | Relancer la tâche A2A complète avec backoff exponentiel | Relancer l'appel d'outil spécifique |
| **Repli** | Rediriger vers un agent alternatif | Utiliser un point de terminaison API de secours |
| **Disjoncteur** | Arrêter de déléguer à un agent défaillant | Arrêter d'appeler un outil défaillant |
| **Timeout** | Définir un timeout par tâche dans la requête A2A | Définir un timeout par appel dans MCP |
| **Idempotence** | Inclure une clé d'idempotence dans l'ID de tâche | Inclure dans les paramètres d'appel d'outil |

---

## Étape 6 : Principes de conception

Sur la base de cette analyse, voici les principes clés pour construire des systèmes A2A + MCP :

| Principe | Description |
|----------|-------------|
| **Séparation des préoccupations** | A2A pour la délégation, MCP pour l'accès aux outils — ne les mélangez pas |
| **Conscience des tokens** | Seuls les appels A2A consomment des tokens LLM ; optimisez les prompts des agents |
| **Périmètres d'authentification** | Séparez les scopes OAuth pour A2A (contexte utilisateur) et MCP (contexte service) |
| **Isolation des erreurs** | Gérez les erreurs à chaque périmètre de protocole indépendamment |
| **Observabilité** | Tracez à la fois les appels A2A et MCP avec des IDs de requête corrélés |
| **Idempotence** | Concevez toutes les opérations pour qu'elles soient réexécutables en toute sécurité |

---

## 🐛 Exercice de correction de bugs

Le fichier `lab-055/broken_delegation.py` contient **3 bugs** dans les fonctions d'analyse de traces. Pouvez-vous tous les trouver et les corriger ?

Exécutez les auto-tests pour voir lesquels échouent :

```bash
python lab-055/broken_delegation.py
```

Vous devriez voir **3 tests échoués**. Chaque test correspond à un bug :

| Test | Ce qu'il vérifie | Indice |
|------|-------------------|--------|
| Test 1 | Nombre d'appels A2A | Devrait filtrer par `protocol == "A2A"`, pas compter toutes les lignes |
| Test 2 | Latence moyenne | Devrait inclure TOUTES les requêtes (y compris les erreurs), pas seulement les OK |
| Test 3 | Taux de succès | Devrait diviser par le nombre total de requêtes, pas par le nombre d'agents uniques |

Corrigez les 3 bugs, puis relancez. Quand vous voyez `🎉 All 3 tests passed`, c'est terminé !

---


## 🧠 Vérification des connaissances

??? question "**Q1 (Choix multiple) :** Quelle est la différence clé entre A2A et MCP ?"

    - A) A2A est plus rapide que MCP
    - B) A2A gère la délégation agent-à-agent ; MCP gère l'accès agent-outil
    - C) A2A utilise REST ; MCP utilise GraphQL
    - D) A2A est pour les agents cloud ; MCP est pour les agents locaux

    ??? success "✅ Révéler la réponse"
        **Correct : B) A2A gère la délégation agent-à-agent ; MCP gère l'accès agent-outil**

        A2A (Agent-to-Agent) est un protocole pair-à-pair permettant aux agents de se découvrir mutuellement et de déléguer des tâches. MCP (Model Context Protocol) est un protocole client-serveur permettant aux agents d'accéder aux outils, bases de données et APIs. Ils sont complémentaires — un système multi-agents utilise généralement les deux.

??? question "**Q2 (Choix multiple) :** Pourquoi l'architecture utilise-t-elle des protocoles séparés pour la communication entre agents et l'accès aux outils ?"

    - A) Pour réduire le nombre total d'appels API
    - B) Parce que les agents et les outils utilisent des langages de programmation différents
    - C) Pour permettre une mise à l'échelle indépendante, des périmètres de sécurité distincts et une évolution indépendante des protocoles
    - D) Parce que A2A est propriétaire et MCP est open source

    ??? success "✅ Révéler la réponse"
        **Correct : C) Pour permettre une mise à l'échelle indépendante, des périmètres de sécurité distincts et une évolution indépendante des protocoles**

        Séparer la communication agent-à-agent (A2A) de l'accès agent-outil (MCP) permet de mettre à l'échelle chaque couche indépendamment, d'appliquer des scopes d'authentification différents à chaque périmètre (OAuth contexte utilisateur pour A2A, jetons de service pour MCP), et de faire évoluer les protocoles sans casser l'autre couche.

??? question "**Q3 (Exécuter le lab) :** Combien d'appels A2A y a-t-il dans les traces de délégation ?"

    Filtrez [📥 `delegation_traces.csv`](https://github.com/lcarli/AI-LearningHub/raw/main/docs/docs/en/labs/lab-055/delegation_traces.csv) par `protocol == "A2A"` et comptez les lignes.

    ??? success "✅ Révéler la réponse"
        **8**

        Il y a 8 appels A2A — un pour chaque requête du coordinateur vers un agent spécialiste (R001–R008). Les 12 événements restants sont des appels MCP des spécialistes vers leurs outils back-end.

??? question "**Q4 (Exécuter le lab) :** Combien d'appels MCP y a-t-il dans les traces de délégation ?"

    Filtrez `delegation_traces.csv` par `protocol == "MCP"` et comptez les lignes.

    ??? success "✅ Révéler la réponse"
        **12**

        Il y a 12 appels MCP — FlightAgent en fait 5 (recherche, tarification, réservation, paiement, nouvelle recherche), HotelAgent en fait 3 (recherche, réservation, réservation), et ItineraryAgent en fait 4 (itinéraire, disponibilité, prévisions, mise à jour).

??? question "**Q5 (Exécuter le lab) :** Quel est le nombre total de tokens consommés pour tous les événements ?"

    Additionnez la colonne `tokens_used` dans `delegation_traces.csv`.

    ??? success "✅ Révéler la réponse"
        **3330**

        Seuls les appels A2A consomment des tokens (raisonnement LLM). Les 8 appels A2A utilisent : 450 + 520 + 680 + 380 + 350 + 460 + 290 + 200 = **3330 tokens**. Les 12 appels MCP utilisent 0 token (appels API directs).

---

## Résumé

| Sujet | Ce que vous avez appris |
|-------|------------------------|
| Architecture | A2A pour la délégation d'agents + MCP pour l'accès aux outils dans un système unifié |
| Planificateur de voyage | Coordinator → FlightAgent / HotelAgent / ItineraryAgent |
| Modèles d'appels | 8 délégations A2A déclenchant 12 appels d'outils MCP |
| Coûts en tokens | Seuls les appels A2A consomment des tokens LLM (3330 au total) |
| Gestion des erreurs | Défaillances en cascade à travers les périmètres de protocole ; modèles de relance |
| Principes de conception | Séparation des préoccupations, périmètres d'authentification, observabilité |

---

## Prochaines étapes

- **[Lab 054](lab-054-a2a-protocol.md)** — Protocole A2A — Construire des systèmes multi-agents interopérables
- **[Lab 056](lab-056-federated-connectors.md)** — Connecteurs fédérés M365 Copilot avec MCP