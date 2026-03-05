# 🔌 Trilha Model Context Protocol (MCP)

<span class="level-badge level-100">L100</span> <span class="level-badge level-200">L200</span> <span class="level-badge level-300">L300</span>

Model Context Protocol (MCP) é um **padrão aberto** criado pela Anthropic que oferece aos agentes de IA uma maneira unificada e consistente de se conectar a ferramentas externas, APIs e fontes de dados.

Pense nele como "USB-C para agentes de IA" — uma interface padrão para que qualquer agente possa se conectar a qualquer ferramenta.

---

## O que Você Vai Construir

Ao final desta trilha você terá:

- ✅ Compreensão profunda de como o MCP funciona (protocolo, transportes, ferramentas vs. recursos vs. prompts)
- ✅ Experiência consumindo servidores MCP existentes a partir do Claude Desktop e VS Code
- ✅ Construído seu próprio servidor MCP em **Python** e/ou **C#**
- ✅ Conectado um servidor MCP a um **Agente Microsoft Foundry**
- ✅ Exposto um **banco de dados PostgreSQL** de forma segura através de um servidor MCP

---

## Laboratórios da Trilha (4 laboratórios, ~170 min no total)

| Lab | Título | Nível | Custo |
|-----|--------|-------|-------|
| [Lab 012](../../labs/lab-012-what-is-mcp.md) | O que é MCP? Anatomia do Protocolo | <span class="level-badge level-100">L100</span> | ✅ Free |
| [Lab 020](../../labs/lab-020-mcp-server-python.md) | Construir um Servidor MCP em Python | <span class="level-badge level-200">L200</span> | ✅ Free |
| [Lab 021](../../labs/lab-021-mcp-server-csharp.md) | Construir um Servidor MCP em C# | <span class="level-badge level-200">L200</span> | ✅ Free |
| [Lab 028](../../labs/lab-028-deploy-mcp-azure.md) | Implantar Servidor MCP no Azure Container Apps | <span class="level-badge level-300">L300</span> | Free |

---

## Conceitos Principais

### Arquitetura MCP

![Arquitetura MCP](../../assets/diagrams/mcp-architecture.svg)

### Três primitivos no MCP

| Primitivo | Descrição | Exemplo |
|-----------|-----------|---------|
| **Tools** | Funções que o LLM pode chamar | `search_products(query)` |
| **Resources** | Dados que o LLM pode ler | `file://data/products.csv` |
| **Prompts** | Templates de prompt reutilizáveis | `summarize_sales_report` |

---

## Recursos Externos

- [Documentação Oficial do MCP](https://modelcontextprotocol.io)
- [MCP para Iniciantes (Microsoft)](https://github.com/microsoft/mcp-for-beginners)
- [Servidor MCP do Azure](https://learn.microsoft.com/azure/developer/azure-mcp-server/)
- [MCP Inspector (ferramenta de depuração)](https://github.com/modelcontextprotocol/inspector)
