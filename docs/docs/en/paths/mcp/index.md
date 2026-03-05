# 🔌 Model Context Protocol (MCP) Path

<span class="level-badge level-100">L100</span> <span class="level-badge level-200">L200</span> <span class="level-badge level-300">L300</span>

Model Context Protocol (MCP) is an **open standard** created by Anthropic that gives AI agents a unified, consistent way to connect to external tools, APIs, and data sources.

Think of it as "USB-C for AI agents" — one standard interface so any agent can plug in to any tool.

---

## What You'll Build

By the end of this path you will have:

- ✅ Deep understanding of how MCP works (protocol, transports, tools vs. resources vs. prompts)
- ✅ Experience consuming existing MCP servers from Claude Desktop and VS Code
- ✅ Built your own MCP server in **Python** and/or **C#**
- ✅ Connected an MCP server to a **Microsoft Foundry Agent**
- ✅ Exposed a **PostgreSQL database** securely through an MCP server

---

## Path Labs (4 labs, ~170 min total)

| Lab | Title | Level | Cost |
|-----|-------|-------|------|
| [Lab 012](../../labs/lab-012-what-is-mcp.md) | What is MCP? Anatomy of the Protocol | <span class="level-badge level-100">L100</span> | ✅ Free |
| [Lab 020](../../labs/lab-020-mcp-server-python.md) | Build an MCP Server in Python | <span class="level-badge level-200">L200</span> | ✅ Free |
| [Lab 021](../../labs/lab-021-mcp-server-csharp.md) | Build an MCP Server in C# | <span class="level-badge level-200">L200</span> | ✅ Free |
| [Lab 028](../../labs/lab-028-deploy-mcp-azure.md) | Deploy MCP Server to Azure Container Apps | <span class="level-badge level-300">L300</span> | Free |

---

## Key Concepts

### MCP Architecture
```
┌──────────────┐      MCP Protocol      ┌──────────────┐
│  AI Agent    │ ◄───────────────────► │  MCP Server  │
│ (LLM Host)   │   JSON-RPC over        │  (your code) │
└──────────────┘   stdio / HTTP/SSE     └──────────────┘
                                              │
                                        ┌─────▼──────┐
                                        │  Database  │
                                        │  APIs, etc.│
                                        └────────────┘
```

### Three primitives in MCP

| Primitive | Description | Example |
|-----------|-------------|---------|
| **Tools** | Functions the LLM can call | `search_products(query)` |
| **Resources** | Data the LLM can read | `file://data/products.csv` |
| **Prompts** | Reusable prompt templates | `summarize_sales_report` |

---

## External Resources

- [MCP Official Docs](https://modelcontextprotocol.io)
- [MCP for Beginners (Microsoft)](https://github.com/microsoft/mcp-for-beginners)
- [Azure MCP Server](https://learn.microsoft.com/azure/developer/azure-mcp-server/)
- [MCP Inspector (debugging tool)](https://github.com/modelcontextprotocol/inspector)
