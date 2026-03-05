---
tags: [a2a, protocol, multi-agent, interoperability, python, free]
---
# Lab 054 : Protocole A2A — Construire des systèmes multi-agents interopérables

<div class="lab-meta">
  <span><strong>Niveau :</strong> <span class="level-badge level-200">L200</span></span>
  <span><strong>Parcours :</strong> Tous les parcours</span>
  <span><strong>Durée :</strong> ~75 min</span>
  <span><strong>💰 Coût :</strong> <span class="level-badge cost-free">Gratuit</span> — Utilise uniquement des données JSON locales</span>
</div>

!!! tip "Les trois protocoles agentiques"
    A2A est l'un des trois protocoles ouverts de l'ère agentique : **MCP** (agent↔outils, [Lab 012](lab-012-what-is-mcp.md)), **A2A** (agent↔agent, ce lab), et **AG-UI** (agent↔utilisateur, [Lab 077](lab-077-agui-protocol.md)). Ensemble, ils forment la pile complète d'interopérabilité.

## Ce que vous apprendrez

- Ce qu'est le **protocole A2A (Agent-to-Agent)** — JSON-RPC 2.0 sur HTTPS, gouverné par la Linux Foundation
- Comment les **Agent Cards** fonctionnent comme mécanisme de découverte des capacités des agents
- Comment analyser programmatiquement les Agent Cards et inspecter les **skills**, le **streaming** et les **pushNotifications**
- Les différences clés entre **A2A** (communication pair-à-pair entre agents) et **MCP** (accès agent-outil)

## Introduction

Les systèmes d'IA modernes consistent rarement en un seul agent. Les solutions réelles nécessitent **plusieurs agents spécialisés** qui se découvrent mutuellement, négocient leurs capacités et collaborent sur des tâches. Le **protocole Agent-to-Agent (A2A)** standardise cette communication.

A2A et MCP résolvent des problèmes différents :

| Protocole | Objectif | Direction |
|-----------|----------|-----------|
| **A2A** | Communication Agent ↔ Agent | Pair-à-pair — les agents délèguent des tâches à d'autres agents |
| **MCP** | Accès Agent → Outil | Client-serveur — les agents appellent des outils, bases de données, APIs |

Pensez à A2A comme des agents *qui se parlent entre eux*, et à MCP comme des agents *qui utilisent des outils*. Un système multi-agents complet utilise généralement **les deux** protocoles.

### Le scénario

Vous êtes un **architecte d'intégration** chez OutdoorGear Inc. L'entreprise exploite **3 agents spécialisés** :

1. **ProductSearchAgent** — recherche dans le catalogue de produits par catégorie, prix et disponibilité
2. **OrderManagementAgent** — gère les commandes, retours et mises à jour d'expédition
3. **CustomerSupportAgent** — traite les demandes, réclamations et réponses FAQ

Chaque agent publie une **Agent Card** — un document JSON décrivant son identité, ses capacités, ses compétences et ses exigences d'authentification. Votre travail consiste à charger ces cartes, analyser ce que chaque agent peut faire, et comprendre comment A2A leur permet de se découvrir et de collaborer.

!!! info "Essentiels du protocole A2A"
    A2A utilise **JSON-RPC 2.0 sur HTTPS** comme couche de transport. Chaque agent publie une Agent Card à une URL bien connue (généralement `/.well-known/agent.json`). Les agents clients découvrent les agents disponibles en récupérant ces cartes, en inspectant leurs compétences et en envoyant des requêtes de tâches via le protocole JSON-RPC.

## Prérequis

| Exigence | Pourquoi |
|----------|----------|
| Python 3.10+ | Analyser et parser les Agent Cards |
| `json` (intégré) | Charger les données des Agent Cards |

Aucun paquet externe n'est requis — ce lab utilise uniquement la bibliothèque standard Python.

---

!!! tip "Démarrage rapide avec GitHub Codespaces"
    [![Open in GitHub Codespaces](https://github.com/codespaces/badge.svg)](https://codespaces.new/lcarli/AI-LearningHub?quickstart=1)

    Toutes les dépendances sont pré-installées dans le devcontainer.


## 📦 Fichiers de support

!!! note "Téléchargez ces fichiers avant de commencer le lab"
    Enregistrez tous les fichiers dans un dossier `lab-054/` dans votre répertoire de travail.

| Fichier | Description | Télécharger |
|---------|-------------|-------------|
| `agent_cards.json` | Fichier de configuration / données | [📥 Télécharger](https://github.com/lcarli/AI-LearningHub/raw/main/docs/docs/en/labs/lab-054/agent_cards.json) |
| `broken_a2a.py` | Exercice de correction de bugs (3 bugs + auto-tests) | [📥 Télécharger](https://github.com/lcarli/AI-LearningHub/raw/main/docs/docs/en/labs/lab-054/broken_a2a.py) |

---

## Étape 1 : Comprendre le protocole A2A

A2A définit un standard pour la **communication pair-à-pair entre agents**. Le protocole spécifie :

| Concept | Description |
|---------|-------------|
| **Agent Card** | Document JSON annonçant l'identité, l'URL, les capacités, les compétences et l'authentification d'un agent |
| **Skills** | Opérations nommées qu'un agent peut effectuer (ex. `search_products`, `track_order`) |
| **Capabilities** | Indicateurs de fonctionnalités : `streaming`, `pushNotifications`, `stateTransitionHistory` |
| **Task** | Une unité de travail envoyée d'un agent à un autre via JSON-RPC 2.0 |
| **Artifact** | Le résultat renvoyé par un agent après l'achèvement d'une tâche |

### Structure d'une Agent Card

```json
{
  "name": "ProductSearchAgent",
  "description": "Searches the OutdoorGear product catalog",
  "url": "https://agents.outdoorgear.com/product-search",
  "version": "1.0.0",
  "provider": "OutdoorGear Inc.",
  "capabilities": {
    "streaming": true,
    "pushNotifications": false,
    "stateTransitionHistory": false
  },
  "skills": [
    {"id": "search_products", "name": "Search Products", "description": "Search by category, price, and stock"}
  ],
  "authentication": {"type": "bearer", "required": true}
}
```

### Flux de communication A2A

```
┌─────────────┐   1. Fetch Agent Card    ┌─────────────────┐
│  Client     │ ───────────────────────►  │  Remote Agent   │
│  Agent      │   2. Inspect skills      │  (Agent Card)   │
│             │ ◄───────────────────────  │                 │
│             │   3. Send JSON-RPC task   │                 │
│             │ ───────────────────────►  │                 │
│             │   4. Receive artifact     │                 │
│             │ ◄───────────────────────  │                 │
└─────────────┘                           └─────────────────┘
```

---

## Étape 2 : Charger les Agent Cards

Chargez les trois Agent Cards OutdoorGear depuis le fichier JSON :

```python
import json

with open("lab-054/agent_cards.json") as f:
    cards = json.load(f)

print(f"Total agents: {len(cards)}")
for card in cards:
    print(f"  • {card['name']} (v{card['version']}) — {card['description']}")
```

**Sortie attendue :**

```
Total agents: 3
  • ProductSearchAgent (v1.0.0) — Searches the OutdoorGear product catalog by category, price range, and availability
  • OrderManagementAgent (v2.1.0) — Manages customer orders including status tracking, returns, and shipping updates
  • CustomerSupportAgent (v1.3.0) — Handles customer inquiries, complaints, and FAQ responses with sentiment awareness
```

---

## Étape 3 : Analyser les capacités des agents

Analysez les capacités, compétences et authentification de chaque agent pour construire un résumé de découverte :

### 3a — Inventaire des compétences

```python
total_skills = 0
for card in cards:
    skills = card["skills"]
    total_skills += len(skills)
    print(f"\n{card['name']} — {len(skills)} skill(s):")
    for skill in skills:
        print(f"  • {skill['name']}: {skill['description']}")

print(f"\nTotal skills across all agents: {total_skills}")
```

**Sortie attendue :**

```
ProductSearchAgent — 2 skill(s):
  • Search Products: Search by category, price, and stock
  • Get Product Details: Retrieve full specs for a product ID

OrderManagementAgent — 3 skill(s):
  • Track Order: Get real-time order status
  • Process Return: Initiate a product return
  • Update Shipping: Change shipping address or speed

CustomerSupportAgent — 2 skill(s):
  • Answer FAQ: Respond to common questions
  • Handle Complaint: Process and resolve complaints

Total skills across all agents: 7
```

### 3b — Indicateurs de capacités

```python
print("Agent Capabilities Matrix:")
print(f"{'Agent':<25} {'Streaming':<12} {'Push':<12} {'History':<12}")
print("-" * 61)
for card in cards:
    caps = card["capabilities"]
    print(f"{card['name']:<25} {str(caps['streaming']):<12} "
          f"{str(caps['pushNotifications']):<12} "
          f"{str(caps['stateTransitionHistory']):<12}")

push_count = sum(1 for c in cards if c["capabilities"]["pushNotifications"])
print(f"\nAgents supporting pushNotifications: {push_count}")
```

**Sortie attendue :**

```
Agent Capabilities Matrix:
Agent                     Streaming    Push         History
-------------------------------------------------------------
ProductSearchAgent        True         False        False
OrderManagementAgent      False        True         True
CustomerSupportAgent      True         True         False

Agents supporting pushNotifications: 2
```

### 3c — Types d'authentification

```python
auth_types = sorted(set(c["authentication"]["type"] for c in cards))
print(f"Authentication types used: {auth_types}")

for card in cards:
    auth = card["authentication"]
    print(f"  {card['name']}: {auth['type']} (required={auth['required']})")
```

**Sortie attendue :**

```
Authentication types used: ['bearer', 'oauth2']
  ProductSearchAgent: bearer (required=True)
  OrderManagementAgent: bearer (required=True)
  CustomerSupportAgent: oauth2 (required=True)
```

---

## Étape 4 : A2A vs MCP — Comparaison des protocoles

Comprendre quand utiliser chaque protocole est essentiel pour une architecture multi-agents :

| Dimension | A2A | MCP |
|-----------|-----|-----|
| **Objectif** | Délégation de tâches agent-à-agent | Accès agent-outil |
| **Transport** | JSON-RPC 2.0 sur HTTPS | JSON-RPC 2.0 sur stdio/SSE |
| **Découverte** | Agent Cards à `/.well-known/agent.json` | Manifestes d'outils dans le serveur MCP |
| **Direction** | Pair-à-pair (bidirectionnel) | Client → Serveur (unidirectionnel) |
| **Auth** | OAuth 2.0, jetons bearer | Défini par le serveur (clés API, OAuth) |
| **Gouvernance** | Linux Foundation | Anthropic (standard ouvert) |
| **Cas d'usage** | « Demander à un autre agent de faire quelque chose » | « Appeler un outil / lire une ressource » |

### Quand utiliser lequel

```
Customer asks: "Find me a waterproof tent under $200 and track my last order"

                    ┌──────────────────┐
                    │  Coordinator     │
                    │  Agent           │
                    └──────┬───────────┘
                           │
              ┌────────────┼────────────┐
         A2A  │       A2A  │            │ A2A
              ▼            ▼            ▼
    ┌──────────────┐ ┌──────────┐ ┌──────────────┐
    │ ProductSearch │ │ Order    │ │ Customer     │
    │ Agent        │ │ Mgmt     │ │ Support      │
    └──────┬───────┘ └────┬─────┘ └──────┬───────┘
      MCP  │         MCP  │         MCP  │
           ▼              ▼              ▼
    ┌──────────────┐ ┌──────────┐ ┌──────────────┐
    │ Catalog DB   │ │ Order DB │ │ FAQ KB       │
    │ (MCP Server) │ │ (MCP)    │ │ (MCP Server) │
    └──────────────┘ └──────────┘ └──────────────┘
```

- **A2A** connecte le coordinateur aux agents spécialisés (délégation pair-à-pair)
- **MCP** connecte chaque agent à ses outils et sources de données back-end

---

## Étape 5 : Construire un flux requête/réponse A2A simulé

Simulez comment un agent client découvre et communique avec un agent distant en utilisant A2A :

```python
import json

def discover_agent(cards, skill_id):
    """Find an agent that has the requested skill."""
    for card in cards:
        for skill in card["skills"]:
            if skill["id"] == skill_id:
                return card
    return None

def build_a2a_request(card, skill_id, params):
    """Build a JSON-RPC 2.0 request for an A2A task."""
    return {
        "jsonrpc": "2.0",
        "method": "tasks/send",
        "id": "req-001",
        "params": {
            "id": "task-001",
            "message": {
                "role": "user",
                "parts": [{"type": "text", "text": json.dumps(params)}]
            },
            "metadata": {
                "target_agent": card["name"],
                "skill": skill_id
            }
        }
    }

def mock_a2a_response(request):
    """Simulate an A2A response."""
    return {
        "jsonrpc": "2.0",
        "id": request["id"],
        "result": {
            "id": request["params"]["id"],
            "status": {"state": "completed"},
            "artifacts": [
                {
                    "parts": [{"type": "text", "text": "Found 3 matching products"}]
                }
            ]
        }
    }

# Discovery: find who can search products
agent = discover_agent(cards, "search_products")
print(f"Discovered agent: {agent['name']} at {agent['url']}")

# Build request
request = build_a2a_request(agent, "search_products", {"category": "tents", "max_price": 200})
print(f"\nA2A Request:\n{json.dumps(request, indent=2)}")

# Get response
response = mock_a2a_response(request)
print(f"\nA2A Response:\n{json.dumps(response, indent=2)}")
```

**Sortie attendue :**

```
Discovered agent: ProductSearchAgent at https://agents.outdoorgear.com/product-search

A2A Request:
{
  "jsonrpc": "2.0",
  "method": "tasks/send",
  "id": "req-001",
  "params": {
    "id": "task-001",
    "message": {
      "role": "user",
      "parts": [{"type": "text", "text": "{\"category\": \"tents\", \"max_price\": 200}"}]
    },
    "metadata": {
      "target_agent": "ProductSearchAgent",
      "skill": "search_products"
    }
  }
}

A2A Response:
{
  "jsonrpc": "2.0",
  "id": "req-001",
  "result": {
    "id": "task-001",
    "status": {"state": "completed"},
    "artifacts": [
      {
        "parts": [{"type": "text", "text": "Found 3 matching products"}]
      }
    ]
  }
}
```

---

## 🐛 Exercice de correction de bugs

Le fichier `lab-054/broken_a2a.py` contient **3 bugs** dans le parseur d'Agent Cards. Pouvez-vous tous les trouver et les corriger ?

Exécutez les auto-tests pour voir lesquels échouent :

```bash
python lab-054/broken_a2a.py
```

Vous devriez voir **3 tests échoués**. Chaque test correspond à un bug :

| Test | Ce qu'il vérifie | Indice |
|------|-------------------|--------|
| Test 1 | Nombre total de compétences pour tous les agents | Devrait additionner les compétences de *toutes* les cartes, pas seulement la première |
| Test 2 | Agents supportant les notifications push | Vérifiez `pushNotifications`, pas `streaming` |
| Test 3 | Types d'authentification | Retournez le champ `type` (string), pas le champ `required` (bool) |

Corrigez les 3 bugs, puis relancez. Quand vous voyez `🎉 All 3 tests passed`, c'est terminé !

---


## 🧠 Vérification des connaissances

??? question "**Q1 (Choix multiple) :** Quel mécanisme de transport le protocole A2A utilise-t-il ?"

    - A) gRPC sur HTTP/2
    - B) JSON-RPC 2.0 sur HTTPS
    - C) GraphQL sur WebSocket
    - D) REST sur HTTP avec OpenAPI

    ??? success "✅ Révéler la réponse"
        **Correct : B) JSON-RPC 2.0 sur HTTPS**

        Le protocole A2A utilise **JSON-RPC 2.0 sur HTTPS** comme couche de transport. Cela fournit un format standardisé de requête/réponse avec des noms de méthodes, des paramètres et des codes d'erreur — le tout transmis de manière sécurisée via HTTPS.

??? question "**Q2 (Choix multiple) :** Quel est l'objectif principal d'une Agent Card dans A2A ?"

    - A) Stocker l'historique des conversations de l'agent
    - B) Découverte des capacités — annoncer ce qu'un agent peut faire
    - C) Chiffrer les messages entre agents
    - D) Limiter le débit des requêtes entrantes

    ??? success "✅ Révéler la réponse"
        **Correct : B) Découverte des capacités — annoncer ce qu'un agent peut faire**

        Une Agent Card est un document JSON publié à une URL bien connue qui décrit l'identité d'un agent, ses compétences, ses capacités (streaming, notifications push) et ses exigences d'authentification. Les agents clients récupèrent ces cartes pour **découvrir** ce que les agents distants peuvent faire avant d'envoyer des requêtes de tâches.

??? question "**Q3 (Exécuter le lab) :** Combien de compétences au total existent pour les 3 agents OutdoorGear ?"

    Additionnez les tableaux de compétences de toutes les Agent Cards dans [📥 `agent_cards.json`](https://github.com/lcarli/AI-LearningHub/raw/main/docs/docs/en/labs/lab-054/agent_cards.json).

    ??? success "✅ Révéler la réponse"
        **7**

        ProductSearchAgent a 2 compétences (`search_products`, `get_details`), OrderManagementAgent a 3 compétences (`track_order`, `process_return`, `update_shipping`), et CustomerSupportAgent a 2 compétences (`answer_faq`, `handle_complaint`). Total : 2 + 3 + 2 = **7**.

??? question "**Q4 (Exécuter le lab) :** Combien d'agents supportent `pushNotifications` ?"

    Vérifiez le champ `capabilities.pushNotifications` dans chaque Agent Card.

    ??? success "✅ Révéler la réponse"
        **2**

        OrderManagementAgent (`pushNotifications: true`) et CustomerSupportAgent (`pushNotifications: true`) supportent les notifications push. ProductSearchAgent ne les supporte pas (`pushNotifications: false`).

??? question "**Q5 (Exécuter le lab) :** Quels types d'authentification sont utilisés par les 3 agents ?"

    Inspectez le champ `authentication.type` dans chaque carte et collectez les valeurs uniques.

    ??? success "✅ Révéler la réponse"
        **bearer et oauth2**

        ProductSearchAgent et OrderManagementAgent utilisent l'authentification par jeton `bearer`. CustomerSupportAgent utilise `oauth2`. Les deux types d'authentification uniques sont **bearer** et **oauth2**.

---

## Résumé

| Sujet | Ce que vous avez appris |
|-------|------------------------|
| Protocole A2A | JSON-RPC 2.0 sur HTTPS pour la communication pair-à-pair entre agents |
| Agent Cards | Documents JSON pour la découverte des capacités (compétences, capacités, auth) |
| Compétences & Capacités | Comment les agents annoncent ce qu'ils peuvent faire et les fonctionnalités qu'ils supportent |
| A2A vs MCP | A2A pour la délégation agent↔agent ; MCP pour l'accès agent→outil |
| Flux de découverte | Récupérer l'Agent Card → Inspecter les compétences → Envoyer la tâche → Recevoir l'artifact |

---

## Prochaines étapes

- **[Lab 055](lab-055-a2a-mcp-capstone.md)** — A2A + MCP Full Stack — Capstone d'interopérabilité des agents
- **[Lab 056](lab-056-federated-connectors.md)** — Connecteurs fédérés M365 Copilot avec MCP