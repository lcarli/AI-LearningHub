---
tags: [mcp, python, free, github-models]
---
# Lab 020: Construa um Servidor MCP em Python

<div class="lab-meta">
  <span><strong>Nível:</strong> <span class="level-badge level-200">L200</span></span>
  <span><strong>Caminho:</strong> <a href="../paths/mcp/">🔌 MCP</a></span>
  <span><strong>Tempo:</strong> ~45 min</span>
  <span><strong>💰 Custo:</strong> <span class="level-badge cost-free">Gratuito</span> — Executa localmente, sem necessidade de conta na nuvem</span>
</div>

## O Que Você Vai Aprender

- Como construir um servidor MCP do zero usando **FastMCP** (Python)
- Como definir **Tools** com esquemas e descrições adequados
- Como executar o servidor e conectá-lo ao **MCP Inspector** e ao **GitHub Copilot (VS Code)**
- Como adicionar transporte HTTP/SSE para compatibilidade com agentes na nuvem

---

## Introdução

Um servidor MCP é um programa que expõe ferramentas (funções) para agentes de IA por meio do protocolo MCP. Quando um agente precisa realizar uma ação — consultar um banco de dados, chamar uma API, ler um arquivo — ele chama as ferramentas do seu servidor MCP.

Neste laboratório, construímos um **servidor MCP de busca de produtos** com duas ferramentas:

1. `list_categories` — retorna categorias de produtos
2. `search_products` — busca produtos por palavra-chave

---

## Configuração de Pré-requisitos

```bash
pip install fastmcp
```

Certifique-se de ter Python 3.10+:
```bash
python --version
```

---

!!! tip "Início Rápido com GitHub Codespaces"
    [![Open in GitHub Codespaces](https://github.com/codespaces/badge.svg)](https://codespaces.new/lcarli/AI-LearningHub?quickstart=1)

    Todas as dependências já estão pré-instaladas no devcontainer.


## 📦 Arquivos de Apoio

!!! note "Baixe estes arquivos antes de iniciar o laboratório"
    Salve todos os arquivos em uma pasta `lab-020/` no seu diretório de trabalho.

| Arquivo | Descrição | Download |
|---------|-----------|----------|
| `outdoorgear_mcp_server_starter.py` | Script inicial com TODOs | [📥 Download](https://github.com/lcarli/AI-LearningHub/raw/main/docs/docs/en/labs/lab-020/outdoorgear_mcp_server_starter.py) |

---

## Exercício do Laboratório

### Passo 1: Crie o projeto

```bash
mkdir products-mcp-server
cd products-mcp-server
```

Crie `server.py`:

```python
from fastmcp import FastMCP

# Initialize the MCP server
mcp = FastMCP(
    name="products-mcp-server",
    description="A product catalog MCP server for learning",
)

# Mock product data (in a real server, this would query a database)
PRODUCTS = [
    {"id": 1, "name": "Waterproof Hiking Boots", "category": "Footwear", "price": 129.99},
    {"id": 2, "name": "Camping Tent 4-Person", "category": "Camping", "price": 249.99},
    {"id": 3, "name": "LED Headlamp 500lm", "category": "Lighting", "price": 34.99},
    {"id": 4, "name": "Stainless Steel Water Bottle", "category": "Hydration", "price": 24.99},
    {"id": 5, "name": "Trekking Poles Set", "category": "Hiking", "price": 79.99},
    {"id": 6, "name": "Solar-Powered Charger", "category": "Electronics", "price": 59.99},
    {"id": 7, "name": "Thermal Sleeping Bag -10°C", "category": "Camping", "price": 189.99},
    {"id": 8, "name": "First Aid Kit Pro", "category": "Safety", "price": 44.99},
]
```

### Passo 2: Defina suas Tools

Adicione as ferramentas após a lista `PRODUCTS`:

```python
@mcp.tool()
def list_categories() -> list[str]:
    """List all available product categories in the catalog."""
    categories = sorted(set(p["category"] for p in PRODUCTS))
    return categories


@mcp.tool()
def search_products(
    keyword: str,
    category: str | None = None,
    max_price: float | None = None,
    max_results: int = 5,
) -> list[dict]:
    """
    Search products by keyword.

    Args:
        keyword: Search term to match against product names
        category: Optional category filter (use list_categories to see options)
        max_price: Optional maximum price filter
        max_results: Maximum number of results to return (default: 5)
    """
    results = []
    keyword_lower = keyword.lower()

    for product in PRODUCTS:
        # Filter by keyword
        if keyword_lower not in product["name"].lower():
            continue
        # Filter by category
        if category and product["category"] != category:
            continue
        # Filter by price
        if max_price and product["price"] > max_price:
            continue
        results.append(product)

    return results[:max_results]


@mcp.tool()
def get_product_by_id(product_id: int) -> dict | None:
    """
    Get a specific product by its ID.

    Args:
        product_id: The unique product ID
    """
    for product in PRODUCTS:
        if product["id"] == product_id:
            return product
    return None
```

### Passo 3: Execute o servidor (modo stdio)

Adicione o ponto de entrada no final de `server.py`:

```python
if __name__ == "__main__":
    mcp.run()
```

Execute:
```bash
python server.py
```

O servidor agora está ouvindo em **stdio**. Este é o modo padrão para ferramentas locais.

### Passo 4: Teste com o MCP Inspector

Abra um **novo terminal** e execute:
```bash
npx @modelcontextprotocol/inspector python server.py
```

O Inspector será aberto no seu navegador. Experimente:

1. Clique em **"Tools"** para ver suas três ferramentas
2. Clique em `list_categories` → **"Run tool"** → veja as categorias
3. Clique em `search_products` → preencha `keyword: "tent"` → **"Run tool"**

!!! success "Você deverá ver a Camping Tent nos resultados"

### Passo 5: Execute como servidor HTTP/SSE (para agentes remotos)

Para agentes hospedados na nuvem como Microsoft Foundry, precisamos de transporte HTTP/SSE. Adicione a opção de inicialização:

```python
if __name__ == "__main__":
    import sys
    if "--http" in sys.argv:
        # HTTP/SSE mode for remote agents
        mcp.run(transport="sse", host="0.0.0.0", port=8000)
    else:
        # stdio mode for local tools (default)
        mcp.run()
```

Execute no modo HTTP:
```bash
python server.py --http
```

Você verá:
```
INFO:     Uvicorn running on http://0.0.0.0:8000
```

Teste com curl:
```bash
curl http://localhost:8000/sse
```

### Passo 6: Conecte ao GitHub Copilot no VS Code

1. No VS Code, crie `.vscode/mcp.json` no seu workspace:

```json
{
  "servers": {
    "products": {
      "type": "stdio",
      "command": "python",
      "args": ["server.py"],
      "cwd": "${workspaceFolder}"
    }
  }
}
```

2. Abra o GitHub Copilot Chat no VS Code
3. Digite: `@copilot What product categories are available?`

O GitHub Copilot chamará sua ferramenta `list_categories` e incluirá o resultado na resposta!

!!! tip "Suporte a MCP no VS Code"
    Certifique-se de ter a extensão **GitHub Copilot** versão 1.99+ instalada.  
    Pode ser necessário habilitar o MCP nas configurações do VS Code: `"chat.mcp.enabled": true`

---

## Adicionando um Resource (Bônus)

O MCP também suporta **Resources** — dados que o agente pode ler. Adicione um recurso que expõe o catálogo completo de produtos:

```python
@mcp.resource("products://catalog")
def get_product_catalog() -> str:
    """The full product catalog as CSV."""
    lines = ["id,name,category,price"]
    for p in PRODUCTS:
        lines.append(f"{p['id']},{p['name']},{p['category']},{p['price']}")
    return "\n".join(lines)
```

---

## 📁 Arquivo Inicial

Este laboratório inclui um arquivo inicial com marcadores TODO para guiá-lo na construção do servidor:

```
lab-020/
└── outdoorgear_mcp_server_starter.py   ← 6 TODOs para completar
```

```bash
# Copy the starter file to your working directory
cp lab-020/outdoorgear_mcp_server_starter.py products-mcp-server/server.py
cd products-mcp-server

# Install dependencies
pip install fastmcp

# Work through the TODOs in the file, then run:
python server.py
```

O arquivo inicial contém o catálogo de produtos OutdoorGear (P001–P007) já preenchido. Você implementa: `list_categories`, `search_products`, `get_product_details` e uma ferramenta desafio `compare_products`.

---

## 🏆 Desafio: Adicione uma Tool `compare_products`

Depois que suas 3 ferramentas básicas estiverem funcionando, adicione uma quarta:

```python
@mcp.tool()
def compare_products(product_ids: list[str]) -> dict:
    """
    Compare multiple products side by side.

    Args:
        product_ids: List of 2–4 product IDs to compare (e.g. ["P001", "P003"])
    """
    # TODO: implement comparison
    # Return: {"products": [...], "not_found": [...], "lightest": "...", "cheapest": "..."}
```

Teste no MCP Inspector perguntando:
> *"Compare a TrailBlazer Tent 2P e a TrailBlazer Solo. Qual é mais leve?"*

O agente deverá chamar `compare_products(["P001", "P003"])` e retornar uma comparação estruturada.

---

## Resumo

Você construiu um servidor MCP totalmente funcional que:

- ✅ Define **3 ferramentas** com descrições adequadas (o LLM usa essas descrições para decidir quando chamar)
- ✅ Executa em **modo stdio** para ferramentas locais
- ✅ Executa em **modo HTTP/SSE** para agentes remotos
- ✅ Funciona com o **MCP Inspector** para testes
- ✅ Integra com o **GitHub Copilot no VS Code**

---

## Próximos Passos

- **Versão em C#:** → [Lab 021 — Servidor MCP em C#](lab-021-mcp-server-csharp.md)
- **Conectar ao Microsoft Foundry Agent Service:** → [Lab 030 — Foundry Agent Service + MCP](lab-030-foundry-agent-mcp.md)
- **Adicionar consultas reais a banco de dados:** → [Lab 031 — pgvector Busca Semântica](lab-031-pgvector-semantic-search.md)
