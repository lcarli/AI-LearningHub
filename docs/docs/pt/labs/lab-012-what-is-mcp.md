# Lab 012: What is MCP? Anatomy of the Protocol

<div class="lab-meta">
  <span><strong>Level:</strong> <span class="level-badge level-100">L100</span></span>
  <span><strong>Path:</strong> <a href="../paths/mcp/">🔌 MCP</a></span>
  <span><strong>Time:</strong> ~20 min</span>
  <span><strong>💰 Cost:</strong> <span class="level-badge cost-free">Free</span> — No account needed</span>
</div>

!!! info "Tradução em andamento"
    Este lab ainda está sendo traduzido. O conteúdo abaixo está em inglês.



## What You'll Learn

- What MCP is and why it was created
- The three MCP primitives: **Tools**, **Resources**, and **Prompts**
- MCP transport options: **stdio** vs **HTTP/SSE**
- How to explore MCP servers with the **MCP Inspector**
- How MCP integrates with GitHub Copilot, Foundry, Claude, and other agents

---

## Introduction

### The problem MCP solves

Before MCP, if you wanted to connect an AI agent to a database, you had to write custom integration code for every combination of agent + data source. N agents × M data sources = N×M custom integrations.

**MCP solves this with a standard protocol:**

![MCP Architecture](../../assets/diagrams/mcp-architecture.svg)

MCP was created by Anthropic in 2024 and quickly adopted by Microsoft, OpenAI, Google, and others as the industry standard.

---

## The Three MCP Primitives

### 1. 🔧 Tools

Functions the LLM can **call** — the most common primitive.

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

The LLM reads the `description` and decides when to call this tool.

### 2. 📁 Resources

Data the LLM can **read** — like files, URLs, or database records.

```json
{
  "uri": "file:///data/products.csv",
  "name": "Product catalog",
  "mimeType": "text/csv"
}
```

### 3. 💬 Prompts

Reusable **prompt templates** the LLM can use.

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

## Transport Options

MCP communicates over two transports:

| Transport | Use case | How it works |
|-----------|----------|-------------|
| **stdio** | Local tools, CLI agents | Parent process spawns MCP server as child; communicates via stdin/stdout |
| **HTTP/SSE** | Remote servers, cloud agents | MCP server exposes HTTP endpoints; agent connects via Server-Sent Events |

In this hub's labs, we use **HTTP/SSE** so cloud-hosted agents (like Foundry Agent Service) can reach your MCP server.

---

## MCP Message Flow

When an agent calls a tool, here's what happens:

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

## Using the MCP Inspector

The **MCP Inspector** is a browser-based tool for exploring any MCP server without writing code.

!!! tip "Try it now — no install needed"
    Run this command (requires Node.js):
    ```bash
    npx @modelcontextprotocol/inspector
    ```
    Or visit [inspector.modelcontextprotocol.io](https://inspector.modelcontextprotocol.io) in your browser.

With the inspector you can:

- Connect to any MCP server (local or remote)
- Browse available tools, resources, and prompts
- Call tools manually and see the JSON responses
- Debug your own MCP servers

---

## MCP in the Microsoft Ecosystem

| Product | MCP support |
|---------|------------|
| **GitHub Copilot (VS Code)** | ✅ Connect MCP servers in `.vscode/mcp.json` |
| **Microsoft Foundry Agent Service** | ✅ Connect MCP servers as agent tools |
| **Semantic Kernel** | ✅ MCP plugin adapter available |
| **Claude Desktop** | ✅ Native MCP support |
| **Azure MCP Server** | ✅ Microsoft-hosted MCP server for Azure services |

### VS Code MCP configuration (`.vscode/mcp.json`)

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

Once configured, GitHub Copilot in VS Code can call your MCP server's tools from chat.

---

## Summary

MCP is an **open standard** that lets any AI agent connect to any tool or data source via a consistent protocol. It has three primitives (Tools, Resources, Prompts) and two transports (stdio and HTTP/SSE). The MCP Inspector lets you explore servers without writing code.

---

## Next Steps

Ready to build your own MCP server?

- **Python:** → [Lab 020 — Build an MCP Server in Python](lab-020-mcp-server-python.md)
- **C#:** → [Lab 021 — Build an MCP Server in C#](lab-021-mcp-server-csharp.md)
