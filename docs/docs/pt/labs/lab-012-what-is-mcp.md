# Lab 012: O que é MCP? Anatomia do Protocolo

<div class="lab-meta">
  <span><strong>Nível:</strong> <span class="level-badge level-100">L100</span></span>
  <span><strong>Trilha:</strong> <a href="../paths/mcp/">🔌 MCP</a></span>
  <span><strong>Tempo:</strong> ~20 min</span>
  <span><strong>💰 Custo:</strong> <span class="level-badge cost-free">Gratuito</span> — Nenhuma conta necessária</span>
</div>

## O que Você Vai Aprender

- O que é MCP e por que foi criado
- Os três primitivos do MCP: **Tools**, **Resources** e **Prompts**
- Opções de transporte do MCP: **stdio** vs **HTTP/SSE**
- Como explorar servidores MCP com o **MCP Inspector**
- Como o MCP se integra com GitHub Copilot, Foundry, Claude e outros agentes

---

## Introdução

### O problema que o MCP resolve

Antes do MCP, se você quisesse conectar um agente de IA a um banco de dados, era necessário escrever código de integração personalizado para cada combinação de agente + fonte de dados. N agentes × M fontes de dados = N×M integrações personalizadas.

**O MCP resolve isso com um protocolo padrão:**

![Arquitetura MCP](../../assets/diagrams/mcp-architecture.svg)

O MCP foi criado pela Anthropic em 2024 e rapidamente adotado pela Microsoft, OpenAI, Google e outros como o padrão da indústria.

---

## Os Três Primitivos do MCP

### 1. 🔧 Tools

Funções que o LLM pode **chamar** — o primitivo mais comum.

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

O LLM lê a `description` e decide quando chamar essa ferramenta.

### 2. 📁 Resources

Dados que o LLM pode **ler** — como arquivos, URLs ou registros de banco de dados.

```json
{
  "uri": "file:///data/products.csv",
  "name": "Product catalog",
  "mimeType": "text/csv"
}
```

### 3. 💬 Prompts

**Modelos de prompt** reutilizáveis que o LLM pode usar.

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

## Opções de Transporte

O MCP se comunica por dois transportes:

| Transporte | Caso de uso | Como funciona |
|-----------|----------|-------------|
| **stdio** | Ferramentas locais, agentes CLI | O processo pai inicia o servidor MCP como filho; comunica-se via stdin/stdout |
| **HTTP/SSE** | Servidores remotos, agentes na nuvem | O servidor MCP expõe endpoints HTTP; o agente conecta via Server-Sent Events |

Nos labs deste hub, usamos **HTTP/SSE** para que agentes hospedados na nuvem (como Foundry Agent Service) possam acessar seu servidor MCP.

---

## Fluxo de Mensagens do MCP

Quando um agente chama uma ferramenta, eis o que acontece:

```
1. Usuário pergunta: "Encontre ferramentas outdoor à prova d'água"
       │
       ▼
2. LLM lê as ferramentas disponíveis do servidor MCP
   (resposta tools/list)
       │
       ▼
3. LLM decide chamar: search_products("waterproof outdoor tools")
       │
       ▼
4. Agente envia: tools/call { name: "search_products", arguments: {...} }
       │
       ▼
5. Servidor MCP executa a função
   (consulta banco de dados, chama API, lê arquivo...)
       │
       ▼
6. Servidor MCP retorna o resultado como texto/JSON
       │
       ▼
7. LLM incorpora o resultado em sua resposta
       │
       ▼
8. Usuário vê: "Aqui estão as ferramentas outdoor à prova d'água: ..."
```

---

## Usando o MCP Inspector

O **MCP Inspector** é uma ferramenta baseada em navegador para explorar qualquer servidor MCP sem escrever código.

!!! tip "Experimente agora — sem instalação necessária"
    Execute este comando (requer Node.js):
    ```bash
    npx @modelcontextprotocol/inspector
    ```
    Ou acesse [inspector.modelcontextprotocol.io](https://inspector.modelcontextprotocol.io) no seu navegador.

Com o inspector você pode:

- Conectar a qualquer servidor MCP (local ou remoto)
- Navegar pelas ferramentas, recursos e prompts disponíveis
- Chamar ferramentas manualmente e ver as respostas JSON
- Depurar seus próprios servidores MCP

---

## MCP no Ecossistema Microsoft

| Produto | Suporte a MCP |
|---------|------------|
| **GitHub Copilot (VS Code)** | ✅ Conecte servidores MCP em `.vscode/mcp.json` |
| **Microsoft Foundry Agent Service** | ✅ Conecte servidores MCP como ferramentas do agente |
| **Semantic Kernel** | ✅ Adaptador de plugin MCP disponível |
| **Claude Desktop** | ✅ Suporte nativo a MCP |
| **Azure MCP Server** | ✅ Servidor MCP hospedado pela Microsoft para serviços Azure |

### Configuração MCP no VS Code (`.vscode/mcp.json`)

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

Uma vez configurado, o GitHub Copilot no VS Code pode chamar as ferramentas do seu servidor MCP a partir do chat.

---

## Resumo

O MCP é um **padrão aberto** que permite que qualquer agente de IA se conecte a qualquer ferramenta ou fonte de dados por meio de um protocolo consistente. Ele possui três primitivos (Tools, Resources, Prompts) e dois transportes (stdio e HTTP/SSE). O MCP Inspector permite explorar servidores sem escrever código.

---

## Próximos Passos

Pronto para construir seu próprio servidor MCP?

- **Python:** → [Lab 020 — Construa um Servidor MCP em Python](lab-020-mcp-server-python.md)
- **C#:** → [Lab 021 — Construa um Servidor MCP em C#](lab-021-mcp-server-csharp.md)
