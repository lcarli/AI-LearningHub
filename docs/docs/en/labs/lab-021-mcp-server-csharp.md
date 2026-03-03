---
tags: [mcp, csharp, free, github-models]
---
# Lab 021: Build an MCP Server in C#

<div class="lab-meta">
  <span><strong>Level:</strong> <span class="level-badge level-200">L200</span></span>
  <span><strong>Path:</strong> <a href="../paths/mcp/">MCP</a></span>
  <span><strong>Time:</strong> ~45 min</span>
  <span><strong>💰 Cost:</strong> <span class="level-badge cost-free">Free (local + Ollama)</span></span>
</div>

## What You'll Learn

- Create an MCP server using the official **ModelContextProtocol .NET SDK**
- Expose **tools**, **resources**, and **prompts** from C#
- Test the server with **MCP Inspector**
- Connect it to **GitHub Copilot Agent Mode** via `mcp.json`

---

## Introduction

Python is great for rapid MCP prototyping, but .NET is common in enterprise environments. The official `ModelContextProtocol` NuGet package makes building MCP servers in C# first-class.

---

## Prerequisites

- [.NET 8 SDK](https://dot.net) or later — free
- [Lab 012: What is MCP?](lab-012-what-is-mcp.md) recommended
- Node.js (for MCP Inspector) — free

---

## Lab Exercise

### Step 1: Create the project

```bash
mkdir mcp-csharp-demo && cd mcp-csharp-demo
dotnet new console -o ProductServer
cd ProductServer
dotnet add package ModelContextProtocol --prerelease
dotnet add package Microsoft.Extensions.Hosting
```

### Step 2: Build the MCP server

Replace `Program.cs` with:

```csharp
using Microsoft.Extensions.DependencyInjection;
using Microsoft.Extensions.Hosting;
using ModelContextProtocol.Server;
using System.ComponentModel;

var builder = Host.CreateApplicationBuilder(args);

builder.Services
    .AddMcpServer()
    .WithStdioServerTransport()
    .WithTools<ProductTools>();

await builder.Build().RunAsync();
```

Create `ProductTools.cs`:

```csharp
using ModelContextProtocol.Server;
using System.ComponentModel;
using System.Text.Json;

[McpServerToolType]
public class ProductTools
{
    private static readonly List<Product> _products = new()
    {
        new("P001", "TrailBlazer X200", "footwear", 189.99m, true),
        new("P002", "Summit Pro Tent",  "camping",   349.00m, true),
        new("P003", "HydroFlow Bottle", "hydration",  34.99m, false),
        new("P004", "ClimbTech Harness","climbing",  129.99m, true),
    };

    [McpServerTool, Description("Search products by name or category keyword.")]
    public static string SearchProducts(
        [Description("Keyword to search in product name or category")] string query)
    {
        var q = query.ToLowerInvariant();
        var matches = _products
            .Where(p => p.Name.Contains(q, StringComparison.OrdinalIgnoreCase)
                     || p.Category.Contains(q, StringComparison.OrdinalIgnoreCase))
            .ToList();

        return matches.Count == 0
            ? "No products found."
            : JsonSerializer.Serialize(matches);
    }

    [McpServerTool, Description("Get details for a specific product by ID.")]
    public static string GetProduct(
        [Description("Product ID, e.g. P001")] string productId)
    {
        var product = _products.FirstOrDefault(p =>
            p.Id.Equals(productId, StringComparison.OrdinalIgnoreCase));

        return product is null
            ? $"Product '{productId}' not found."
            : JsonSerializer.Serialize(product);
    }

    [McpServerTool, Description("List all product categories.")]
    public static string ListCategories()
    {
        var categories = _products.Select(p => p.Category).Distinct().OrderBy(c => c);
        return string.Join(", ", categories);
    }
}

public record Product(string Id, string Name, string Category, decimal Price, bool InStock);
```

### Step 3: Run and test with MCP Inspector

**Terminal 1** — build the server:
```bash
dotnet build
```

**Test with MCP Inspector:**
```bash
npx @modelcontextprotocol/inspector dotnet run
```

In Inspector, click **Tools** and test `search_products` with query `"camping"`. You should see the tent returned.

### Step 4: Add a Resource

Resources expose read-only data (files, database views, etc.). Add to `ProductTools.cs`:

```csharp
[McpServerResourceType]
public class ProductResources
{
    [McpServerResource(UriTemplate = "products://catalog", Name = "Full Catalog",
        Description = "Complete product catalog as JSON", MimeType = "application/json")]
    public static string GetCatalog()
    {
        return JsonSerializer.Serialize(_products, new JsonSerializerOptions { WriteIndented = true });
    }
}
```

Update `Program.cs` to register resources:
```csharp
builder.Services
    .AddMcpServer()
    .WithStdioServerTransport()
    .WithTools<ProductTools>()
    .WithResources<ProductResources>();  // ← add this
```

### Step 5: Connect to GitHub Copilot

Add to `.vscode/mcp.json` in your workspace:

```json
{
  "servers": {
    "product-server-csharp": {
      "type": "stdio",
      "command": "dotnet",
      "args": ["run", "--project", "/path/to/ProductServer"]
    }
  }
}
```

Enable Agent Mode in VS Code, then ask: *"What camping products are in stock?"*

---

## Key Differences vs Python SDK

| | Python | C# |
|---|---|---|
| Decorator | `@mcp.tool()` | `[McpServerTool]` |
| Description | docstring | `[Description("...")]` |
| Resources | `@mcp.resource()` | `[McpServerResource(...)]` |
| Transport | `mcp.run(transport="stdio")` | `.WithStdioServerTransport()` |
| DI container | — | `Microsoft.Extensions.Hosting` |

---

---

## 🐛 Bug-Fix Exercise: Fix the Broken MCP Server

This lab includes a deliberately broken C# MCP server file. Your challenge: find and fix 3 bugs.

```
lab-021/
└── BrokenMcpServer.cs    ← 3 intentional bugs to find and fix
```

**Setup:**
```bash
mkdir mcp-bugfix && cd mcp-bugfix
dotnet new console -o BugFixServer
cd BugFixServer
dotnet add package ModelContextProtocol --prerelease
dotnet add package Microsoft.Extensions.Hosting

# Copy the broken file over Program.cs
cp ../lab-021/BrokenMcpServer.cs Program.cs
dotnet run
```

**The 3 bugs:**

| # | Tool | Symptom | Type |
|---|------|---------|------|
| 1 | `list_categories` | `NullReferenceException` on startup | Null initialization |
| 2 | `search_products` | Always returns empty list `[]` | Logic inversion (`!`) |
| 3 | `get_product_details` | Returns "not found" for lowercase IDs | Case-sensitive comparison |

**Verify your fixes:** After fixing all 3 bugs, connect with the MCP Inspector and run:

- `list_categories()` → should return `["Backpacks", "Sleeping Bags", "Tents"]`
- `search_products(keyword: "tent")` → should return P001, P002, P003
- `get_product_details(productId: "p001")` → should return TrailBlazer Tent 2P details

---

## 🧠 Knowledge Check

??? question "**Q1 (Run the Lab):** After fixing all 3 bugs and calling `list_categories()`, what does the tool return? List the categories in the order they appear in the output."

    Fix the bugs, start the server, connect with MCP Inspector, and call `list_categories()`.

    ??? success "✅ Reveal Answer"
        **`["Backpacks", "Sleeping Bags", "Tents"]`**

        The categories are returned in alphabetical order because the original code uses a sorted `List<string>`. Bug #1 (`categories = null`) caused a `NullReferenceException` before returning anything — fixing it reveals the properly sorted list.

??? question "**Q2 (Run the Lab):** After fixing bug #3 (the case-sensitive comparison bug), what `StringComparison` value replaces `StringComparison.Ordinal` in the fix?"

    Read the bug #3 description carefully, then look at the fix you applied in `BrokenMcpServer.cs`.

    ??? success "✅ Reveal Answer"
        **`StringComparison.OrdinalIgnoreCase`**

        The original code used `StringComparison.Ordinal` which is case-sensitive, so `get_product_details("p001")` failed because the stored IDs are uppercase (`"P001"`). Replacing it with `OrdinalIgnoreCase` makes ID lookups work regardless of the case the client sends.

??? question "**Q3 (Multiple Choice):** Bug #2 in `search_products` caused it to always return an empty list. What was the root cause?"

    - A) The keyword parameter was null
    - B) The `Contains()` call was inverted with `!` — it filtered OUT matches instead of keeping them
    - C) The product list was not initialized
    - D) The search was case-sensitive and no products matched

    ??? success "✅ Reveal Answer"
        **Correct: B — Logic inversion**

        The code had `!product.Name.Contains(keyword)` — the `!` negated the condition, so products that DID contain the keyword were excluded, and products that did NOT contain the keyword were returned. With an empty results list, there were no non-matching products either. Removing the `!` fixes the logic.

---

## Next Steps

- **Deploy this server to the cloud:** → [Lab 028 — Deploy MCP to Azure Container Apps](lab-028-deploy-mcp-azure.md)
- **Python version of MCP server:** → [Lab 020 — MCP Server in Python](lab-020-mcp-server-python.md)
