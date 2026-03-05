# Lab 012 : Qu'est-ce que MCP ? Anatomie du protocole

<div class="lab-meta">
  <span><strong>Niveau :</strong> <span class="level-badge level-100">L100</span></span>
  <span><strong>Parcours :</strong> <a href="../paths/mcp/">🔌 MCP</a></span>
  <span><strong>Durée :</strong> ~20 min</span>
  <span><strong>💰 Coût :</strong> <span class="level-badge cost-free">Gratuit</span> — Aucun compte nécessaire</span>
</div>

## Ce que vous apprendrez

- Ce qu'est MCP et pourquoi il a été créé
- Les trois primitives MCP : **Tools**, **Resources** et **Prompts**
- Les options de transport MCP : **stdio** vs **HTTP/SSE**
- Comment explorer les serveurs MCP avec le **MCP Inspector**
- Comment MCP s'intègre avec GitHub Copilot, Foundry, Claude et d'autres agents

---

## Introduction

### Le problème que MCP résout

Avant MCP, si vous vouliez connecter un agent IA à une base de données, vous deviez écrire du code d'intégration personnalisé pour chaque combinaison agent + source de données. N agents × M sources de données = N×M intégrations personnalisées.

**MCP résout ce problème avec un protocole standard :**

![Architecture MCP](../../assets/diagrams/mcp-architecture.svg)

MCP a été créé par Anthropic en 2024 et rapidement adopté par Microsoft, OpenAI, Google et d'autres comme standard de l'industrie.

---

## Les trois primitives MCP

### 1. 🔧 Tools

Fonctions que le LLM peut **appeler** — la primitive la plus courante.

```json
{
  "name": "search_products",
  "description": "Search products by keyword or semantic similarity",
  "inputSchema": {
    "type": "object",
    "properties": {
      "query": { "type": "string", "description": "Search term" },
      "max_results": { "type": "integer", "default": 10 }
    },
    "required": ["query"]
  }
}
```

Le LLM lit la `description` et décide quand appeler cet outil.

### 2. 📁 Resources

Données que le LLM peut **lire** — comme des fichiers, des URL ou des enregistrements de base de données.

```json
{
  "uri": "file:///data/products.csv",
  "name": "Product catalog",
  "mimeType": "text/csv"
}
```

### 3. 💬 Prompts

**Modèles de prompts** réutilisables que le LLM peut utiliser.

```json
{
  "name": "summarize_sales_report",
  "description": "Summarize a monthly sales report in 3 bullet points",
  "arguments": [
    { "name": "month", "required": true }
  ]
}
```

---

## Options de transport

MCP communique via deux transports :

| Transport | Cas d'utilisation | Fonctionnement |
|-----------|----------|-------------|
| **stdio** | Outils locaux, agents CLI | Le processus parent lance le serveur MCP en tant que processus enfant ; communique via stdin/stdout |
| **HTTP/SSE** | Serveurs distants, agents cloud | Le serveur MCP expose des points de terminaison HTTP ; l'agent se connecte via Server-Sent Events |

Dans les labs de ce hub, nous utilisons **HTTP/SSE** afin que les agents hébergés dans le cloud (comme Foundry Agent Service) puissent atteindre votre serveur MCP.

---

## Flux de messages MCP

Lorsqu'un agent appelle un outil, voici ce qui se passe :

```
1. User asks: "Find me waterproof outdoor tools"
       │
       ▼
2. LLM reads available tools from MCP server
   (tools/list response)
       │
       ▼
3. LLM decides to call: search_products("waterproof outdoor tools")
       │
       ▼
4. Agent sends: tools/call { name: "search_products", arguments: {...} }
       │
       ▼
5. MCP Server executes the function
   (queries database, calls API, reads file...)
       │
       ▼
6. MCP Server returns result as text/JSON
       │
       ▼
7. LLM incorporates result into its response
       │
       ▼
8. User sees: "Here are waterproof outdoor tools: ..."
```

---

## Utiliser le MCP Inspector

Le **MCP Inspector** est un outil basé sur le navigateur permettant d'explorer n'importe quel serveur MCP sans écrire de code.

!!! tip "Essayez-le maintenant — aucune installation nécessaire"
    Exécutez cette commande (nécessite Node.js) :
    ```bash
    npx @modelcontextprotocol/inspector
    ```
    Ou visitez [inspector.modelcontextprotocol.io](https://inspector.modelcontextprotocol.io) dans votre navigateur.

Avec l'inspecteur, vous pouvez :

- Vous connecter à n'importe quel serveur MCP (local ou distant)
- Parcourir les outils, ressources et prompts disponibles
- Appeler des outils manuellement et voir les réponses JSON
- Déboguer vos propres serveurs MCP

---

## MCP dans l'écosystème Microsoft

| Produit | Support MCP |
|---------|------------|
| **GitHub Copilot (VS Code)** | ✅ Connecter des serveurs MCP dans `.vscode/mcp.json` |
| **Microsoft Foundry Agent Service** | ✅ Connecter des serveurs MCP comme outils d'agent |
| **Semantic Kernel** | ✅ Adaptateur de plugin MCP disponible |
| **Claude Desktop** | ✅ Support MCP natif |
| **Azure MCP Server** | ✅ Serveur MCP hébergé par Microsoft pour les services Azure |

### Configuration MCP dans VS Code (`.vscode/mcp.json`)

```json
{
  "servers": {
    "my-products-server": {
      "type": "http",
      "url": "http://localhost:8000/sse"
    }
  }
}
```

Une fois configuré, GitHub Copilot dans VS Code peut appeler les outils de votre serveur MCP depuis le chat.

---

## Résumé

MCP est un **standard ouvert** qui permet à n'importe quel agent IA de se connecter à n'importe quel outil ou source de données via un protocole cohérent. Il possède trois primitives (Tools, Resources, Prompts) et deux transports (stdio et HTTP/SSE). Le MCP Inspector vous permet d'explorer les serveurs sans écrire de code.

---

## Étapes suivantes

Prêt à construire votre propre serveur MCP ?

- **Python :** → [Lab 020 — Construire un serveur MCP en Python](lab-020-mcp-server-python.md)
- **C# :** → [Lab 021 — Construire un serveur MCP en C#](lab-021-mcp-server-csharp.md)
