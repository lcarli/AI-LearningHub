# Lab 020: Build an MCP Server in Python

<div class="lab-meta">
  <span><strong>Level:</strong> <span class="level-badge level-200">L200</span></span>
  <span><strong>Path:</strong> <a href="../paths/mcp/">🔌 MCP</a></span>
  <span><strong>Time:</strong> ~45 min</span>
  <span><strong>💰 Cost:</strong> <span class="level-badge cost-free">Free</span> — Runs locally, no cloud account needed</span>
</div>

## What You'll Learn

- How to build an MCP server from scratch using **FastMCP** (Python)
- How to define **Tools** with proper schemas and descriptions
- How to run the server and connect it to the **MCP Inspector** and **GitHub Copilot (VS Code)**
- How to add HTTP/SSE transport for cloud-agent compatibility

---

## Introduction

An MCP server is a program that exposes tools (functions) to AI agents via the MCP protocol. When an agent needs to perform an action — query a database, call an API, read a file — it calls your MCP server's tools.

In this lab we build a **product search MCP server** with two tools:

1. `list_categories` — returns product categories
2. `search_products` — searches products by keyword

---

## Prerequisites Setup

```bash
pip install fastmcp
```

Make sure you have Python 3.10+:
```bash
python --version
```

---

## Lab Exercise

### Step 1: Create the project

```bash
mkdir products-mcp-server
cd products-mcp-server
```

Create `server.py`:

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

### Step 2: Define your Tools

Add the tools after the `PRODUCTS` list:

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

### Step 3: Run the server (stdio mode)

Add the entry point at the bottom of `server.py`:

```python
if __name__ == "__main__":
    mcp.run()
```

Run it:
```bash
python server.py
```

The server is now listening on **stdio**. This is the default mode for local tools.

### Step 4: Test with the MCP Inspector

Open a **new terminal** and run:
```bash
npx @modelcontextprotocol/inspector python server.py
```

The Inspector will open in your browser. Try:

1. Click **"Tools"** to see your three tools
2. Click `list_categories` → **"Run tool"** → see the categories
3. Click `search_products` → fill in `keyword: "tent"` → **"Run tool"**

!!! success "You should see the Camping Tent in the results"

### Step 5: Run as HTTP/SSE server (for remote agents)

For cloud-hosted agents like Microsoft Foundry, we need HTTP/SSE transport. Add the startup option:

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

Run in HTTP mode:
```bash
python server.py --http
```

You'll see:
```
INFO:     Uvicorn running on http://0.0.0.0:8000
```

Test with curl:
```bash
curl http://localhost:8000/sse
```

### Step 6: Connect to GitHub Copilot in VS Code

1. In VS Code, create `.vscode/mcp.json` in your workspace:

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

2. Open GitHub Copilot Chat in VS Code
3. Type: `@copilot What product categories are available?`

GitHub Copilot will call your `list_categories` tool and include the result in its response!

!!! tip "VS Code MCP support"
    Make sure you have the **GitHub Copilot** extension version 1.99+ installed.  
    You may need to enable MCP in VS Code settings: `"chat.mcp.enabled": true`

---

## Adding a Resource (Bonus)

MCP also supports **Resources** — data the agent can read. Add a resource that exposes the full product catalog:

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

## Summary

You've built a fully functional MCP server that:

- ✅ Defines **3 tools** with proper descriptions (the LLM uses these to decide when to call)
- ✅ Runs in **stdio mode** for local tools
- ✅ Runs in **HTTP/SSE mode** for remote agents
- ✅ Works with the **MCP Inspector** for testing
- ✅ Integrates with **GitHub Copilot in VS Code**

---

## Next Steps

- **C# version:** → [Lab 021 — MCP Server in C#](lab-021-mcp-server-csharp.md)
- **Connect to Microsoft Foundry Agent Service:** → [Lab 030 — Foundry Agent Service + MCP](lab-030-foundry-agent-mcp.md)
- **Add real database queries:** → [Lab 031 — pgvector Semantic Search](lab-031-pgvector-semantic-search.md)
