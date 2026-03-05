---
tags: [ag-ui, protocol, frontend, copilotkit, events, python]
---
# Lab 077 : Protocole AG-UI — Connecter les agents aux interfaces utilisateur

<div class="lab-meta">
  <span><strong>Niveau :</strong> <span class="level-badge level-200">L200</span></span>
  <span><strong>Parcours :</strong> Tous les parcours</span>
  <span><strong>Durée :</strong> ~60 min</span>
  <span><strong>💰 Coût :</strong> <span class="level-badge cost-free">Gratuit</span> — Utilise des données d'événements simulées</span>
</div>

## Ce que vous apprendrez

- Ce qu'est le **protocole AG-UI** et comment il connecte les agents aux interfaces utilisateur frontend
- Comment AG-UI complète la **trilogie d'interopérabilité** : MCP (outils) + A2A (agents) + AG-UI (utilisateurs)
- Analyser **12 types d'événements** et leurs directions (agent→frontend vs. frontend→agent)
- Comprendre les catégories d'événements : cycle de vie, texte, outil, état et entrée
- Construire un **diagramme de flux d'événements** à partir d'une trace d'interaction réelle

## Introduction

Le **protocole AG-UI (Agent–User Interface)** est un protocole basé sur les événements qui standardise la communication entre les agents IA et les applications frontend. Alors que **MCP** connecte les agents aux outils et **A2A** connecte les agents entre eux, **AG-UI** ferme la boucle en connectant les agents aux **utilisateurs** via leurs interfaces.

### La trilogie d'interopérabilité

| Protocole | Connecte | Objectif |
|----------|----------|---------|
| **MCP** | Agent ↔ Outils | Accès standardisé aux outils/ressources |
| **A2A** | Agent ↔ Agent | Collaboration multi-agents |
| **AG-UI** | Agent ↔ Utilisateur | Streaming en temps réel et interaction UI |

### Comment ça fonctionne

AG-UI utilise un **modèle d'événements en streaming**. Au lieu d'un schéma requête/réponse, l'agent et le frontend échangent un flux continu d'événements typés :

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

### Le scénario

Vous êtes un **ingénieur frontend** intégrant un agent IA dans une interface alimentée par CopilotKit. Vous disposez d'un jeu de données de **12 types d'événements** (`agui_events.csv`) qui définit chaque événement du protocole AG-UI. Votre mission : analyser les événements, comprendre leurs directions et catégories, et cartographier le flux d'événements d'une interaction agent typique.

!!! info "Données simulées"
    Ce lab utilise un jeu de données de types d'événements simulé. Les noms d'événements, directions et catégories correspondent à la spécification du protocole AG-UI telle que définie par CopilotKit.

## Prérequis

| Exigence | Pourquoi |
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
    Enregistrez tous les fichiers dans un dossier `lab-077/` de votre répertoire de travail.

| Fichier | Description | Téléchargement |
|------|-------------|----------|
| `broken_agui.py` | Exercice de correction de bugs (3 bugs + auto-tests) | [📥 Télécharger](https://github.com/lcarli/AI-LearningHub/raw/main/docs/docs/en/labs/lab-077/broken_agui.py) |
| `agui_events.csv` | 12 types d'événements AG-UI avec directions et catégories | [📥 Télécharger](https://github.com/lcarli/AI-LearningHub/raw/main/docs/docs/en/labs/lab-077/agui_events.csv) |

---

## Étape 1 : Comprendre le modèle d'événements

Les événements AG-UI sont organisés par **direction** et **catégorie** :

| Direction | Signification |
|-----------|---------|
| **agent→frontend** | L'agent envoie des données à l'UI (texte en streaming, appels d'outils, mises à jour d'état) |
| **frontend→agent** | L'utilisateur/UI envoie une entrée à l'agent (commande d'exécution, résultats d'outils) |

| Catégorie | Exemples |
|----------|---------|
| **lifecycle** | `LifecycleStarted`, `LifecycleCompleted` — marque les limites d'exécution de l'agent |
| **text** | `TextMessageStart`, `TextMessageContent`, `TextMessageEnd` — sortie de texte en streaming |
| **tool** | `ToolCallStart`, `ToolCallArgs`, `ToolCallEnd`, `ToolResult` — exécution d'outils |
| **state** | `StateUpdate`, `StateSnapshot` — synchronisation d'état partagé |
| **input** | `RunAgent` — le frontend lance une exécution d'agent |

---

## Étape 2 : Charger et explorer les événements

```python
import pandas as pd

df = pd.read_csv("lab-077/agui_events.csv")

print(f"Total event types: {len(df)}")
print(f"Directions: {df['direction'].value_counts().to_dict()}")
print(f"Categories: {df['category'].value_counts().to_dict()}")
print(f"\nAll events:")
print(df[["event_name", "direction", "category"]].to_string(index=False))
```

**Sortie attendue :**

```
Total event types: 12
Directions: {'agent_to_frontend': 9, 'frontend_to_agent': 3}
Categories: {'tool': 4, 'text': 3, 'lifecycle': 2, 'state': 2, 'input': 1}
```

---

## Étape 3 : Analyser les directions des événements

Quels événements vont de l'agent vers le frontend, et lesquels vont dans l'autre sens ?

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

!!! tip "Aperçu de conception"
    Le protocole est **fortement asymétrique** : **9 événements** vont de l'agent vers le frontend, mais seulement **3** du frontend vers l'agent. Cela reflète la réalité selon laquelle les agents produisent la majorité des données (texte en streaming, appels d'outils, mises à jour d'état) tandis que les frontends envoient principalement des commandes et des résultats d'outils.

---

## Étape 4 : Cartographier le flux d'événements

Construisez une chronologie des événements pour une interaction agent typique :

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

## Étape 5 : Analyser les catégories en profondeur

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

!!! warning "Responsabilité du frontend"
    Lorsque l'agent émet un événement `ToolCallEnd`, le **frontend est responsable** de l'exécution de l'outil et du renvoi d'un événement `ToolResult`. Si le frontend ne répond pas, l'agent attendra indéfiniment. Implémentez toujours une gestion de timeout pour l'exécution des outils.

---

## Étape 6 : Construire le résumé du protocole

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

## 🐛 Exercice de correction de bugs

Le fichier `lab-077/broken_agui.py` contient **3 bugs** qui produisent une analyse d'événements incorrecte. Pouvez-vous les trouver et les corriger tous ?

Exécutez les auto-tests pour voir lesquels échouent :

```bash
python lab-077/broken_agui.py
```

Vous devriez voir **3 tests échoués**. Chaque test correspond à un bug :

| Test | Ce qu'il vérifie | Indice |
|------|---------------|------|
| Test 1 | Nombre d'événements agent→frontend | Devrait filtrer `agent_to_frontend`, pas `frontend_to_agent` |
| Test 2 | Nombre total de types d'événements | Devrait utiliser `len(df)`, pas `df['category'].nunique()` |
| Test 3 | Nombre d'événements frontend→agent | Devrait compter la direction `frontend_to_agent`, pas la catégorie `input` |

Corrigez les 3 bugs, puis relancez. Quand vous voyez `All passed!`, c'est terminé !

---


## 🧠 Vérification des connaissances

??? question "**Q1 (Choix multiple) :** Quel rôle joue AG-UI dans la trilogie d'interopérabilité ?"

    - A) Il connecte les agents aux outils et API externes
    - B) Il connecte les agents entre eux pour la collaboration
    - C) Il connecte les agents aux interfaces utilisateur frontend via des événements en streaming
    - D) Il connecte les agents aux bases de données pour le stockage

    ??? success "✅ Révéler la réponse"
        **Correct : C) Il connecte les agents aux interfaces utilisateur frontend via des événements en streaming**

        La trilogie d'interopérabilité se compose de MCP (agent↔outils), A2A (agent↔agents) et AG-UI (agent↔utilisateurs). AG-UI utilise un modèle d'événements en streaming pour permettre la communication en temps réel entre les agents IA et les applications frontend comme CopilotKit.

??? question "**Q2 (Choix multiple) :** Pourquoi le protocole AG-UI est-il asymétrique (plus d'événements agent→frontend que frontend→agent) ?"

    - A) Le frontend est trop lent pour envoyer beaucoup d'événements
    - B) Les agents produisent la majorité des données (texte, appels d'outils, état) tandis que les frontends envoient principalement des commandes et résultats d'outils
    - C) Le protocole limite les événements frontend pour des raisons de sécurité
    - D) Les événements frontend sont regroupés en moins de messages

    ??? success "✅ Révéler la réponse"
        **Correct : B) Les agents produisent la majorité des données (texte, appels d'outils, état) tandis que les frontends envoient principalement des commandes et résultats d'outils**

        Dans une interaction typique, l'agent diffuse des tokens de texte, émet des événements d'appels d'outils et pousse des mises à jour d'état — tout cela allant vers le frontend. Le rôle du frontend est principalement d'initier les exécutions (`RunAgent`) et de retourner les résultats d'exécution d'outils (`ToolResult`).

??? question "**Q3 (Exécutez le lab) :** Combien de types d'événements vont de l'agent vers le frontend ?"

    Exécutez l'analyse de l'étape 3 sur [📥 `agui_events.csv`](https://github.com/lcarli/AI-LearningHub/raw/main/docs/docs/en/labs/lab-077/agui_events.csv) et comptez les événements `agent_to_frontend`.

    ??? success "✅ Révéler la réponse"
        **9 événements**

        Les événements suivants vont de l'agent vers le frontend : `LifecycleStarted`, `LifecycleCompleted`, `TextMessageStart`, `TextMessageContent`, `TextMessageEnd`, `ToolCallStart`, `ToolCallArgs`, `ToolCallEnd` et `StateUpdate`. Cela fait **9** sur 12 types d'événements au total.

??? question "**Q4 (Exécutez le lab) :** Combien de types d'événements vont du frontend vers l'agent ?"

    Comptez les événements avec la direction `frontend_to_agent`.

    ??? success "✅ Révéler la réponse"
        **3 événements**

        Seuls **3 événements** vont du frontend vers l'agent : `RunAgent` (entrée), `ToolResult` (outil) et `StateSnapshot` (état). Le protocole est fortement asymétrique — les agents envoient 3× plus de types d'événements que les frontends.

??? question "**Q5 (Exécutez le lab) :** Quel est le nombre total de types d'événements dans le protocole AG-UI ?"

    Chargez le CSV et vérifiez le nombre total de lignes.

    ??? success "✅ Révéler la réponse"
        **12 types d'événements**

        Le protocole AG-UI définit exactement **12 types d'événements** répartis en 5 catégories : tool (4), text (3), lifecycle (2), state (2) et input (1).

---

## Résumé

| Sujet | Ce que vous avez appris |
|-------|-----------------|
| Protocole AG-UI | Protocole basé sur les événements connectant les agents aux interfaces frontend |
| Trilogie d'interopérabilité | MCP (outils) + A2A (agents) + AG-UI (utilisateurs) = écosystème d'agents complet |
| Modèle d'événements | 12 types d'événements : 9 agent→frontend, 3 frontend→agent |
| Catégories | lifecycle, text, tool, state, input |
| Architecture de streaming | Un flux continu d'événements remplace le modèle requête/réponse |
| Responsabilité du frontend | L'UI doit exécuter les outils et retourner les résultats lorsque l'agent le demande |

---

## Prochaines étapes

- **[Lab 029](lab-029-mcp-protocol.md)** — Protocole MCP (le volet outils de la trilogie)
- **[Lab 070](lab-070-agent-ux-patterns.md)** — Modèles UX d'agents (patrons de conception pour les interfaces alimentées par des agents)
- **[Lab 076](lab-076-microsoft-agent-framework.md)** — Microsoft Agent Framework (créer des agents qui parlent AG-UI)
- **[Lab 034](lab-034-multi-agent-sk.md)** — Multi-Agent avec Semantic Kernel (agents qui collaborent via A2A)
