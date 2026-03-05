---
tags: [mcp, csharp, free, github-models]
---
# Lab 021: Construa um Servidor MCP em C#

<div class="lab-meta">
  <span><strong>Nível:</strong> <span class="level-badge level-200">L200</span></span>
  <span><strong>Trilha:</strong> <a href="../paths/mcp/">MCP</a></span>
  <span><strong>Tempo:</strong> ~45 min</span>
  <span><strong>💰 Custo:</strong> <span class="level-badge cost-free">Gratuito (local + Ollama)</span></span>
</div>

## O que Você Vai Aprender

- Criar um servidor MCP usando o **ModelContextProtocol .NET SDK** oficial
- Expor **tools**, **resources** e **prompts** a partir do C#
- Testar o servidor com o **MCP Inspector**
- Conectá-lo ao **GitHub Copilot Agent Mode** via `mcp.json`

---

## Introdução

Python é ótimo para prototipagem rápida de MCP, mas .NET é comum em ambientes corporativos. O pacote NuGet oficial `ModelContextProtocol` torna a construção de servidores MCP em C# uma experiência de primeira classe.

---

## Pré-requisitos

- [.NET 8 SDK](https://dot.net) ou posterior — gratuito
- [Lab 012: O que é MCP?](lab-012-what-is-mcp.md) recomendado
- Node.js (para o MCP Inspector) — gratuito

---

## 📦 Arquivos de Apoio

!!! note "Baixe estes arquivos antes de iniciar o lab"
    Salve todos os arquivos em uma pasta `lab-021/` no seu diretório de trabalho.

| Arquivo | Descrição | Download |
|------|-------------|----------|
| `BrokenMcpServer.cs` | Exercício de correção de bugs (3 bugs + auto-testes) | [📥 Download](https://github.com/lcarli/AI-LearningHub/raw/main/docs/docs/en/labs/lab-021/BrokenMcpServer.cs) |

---

## Exercício do Lab

### Passo 1: Criar o projeto

```bash
mkdir mcp-csharp-demo && cd mcp-csharp-demo
dotnet new console -o ProductServer
cd ProductServer
dotnet add package ModelContextProtocol --prerelease
dotnet add package Microsoft.Extensions.Hosting
```

### Passo 2: Construir o servidor MCP

Substitua `Program.cs` por:

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

Crie `ProductTools.cs`:

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

### Passo 3: Executar e testar com o MCP Inspector

**Terminal 1** — compilar o servidor:
```bash
dotnet build
```

**Testar com o MCP Inspector:**
```bash
npx @modelcontextprotocol/inspector dotnet run
```

No Inspector, clique em **Tools** e teste `search_products` com a consulta `"camping"`. Você deverá ver a barraca retornada.

### Passo 4: Adicionar um Resource

Resources expõem dados somente leitura (arquivos, views de banco de dados, etc.). Adicione ao `ProductTools.cs`:

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

Atualize `Program.cs` para registrar os resources:
```csharp
builder.Services
    .AddMcpServer()
    .WithStdioServerTransport()
    .WithTools<ProductTools>()
    .WithResources<ProductResources>();  // ← adicione isto
```

### Passo 5: Conectar ao GitHub Copilot

Adicione ao `.vscode/mcp.json` no seu workspace:

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

Ative o Agent Mode no VS Code e pergunte: *"Quais produtos de camping estão em estoque?"*

---

## Principais Diferenças vs Python SDK

| | Python | C# |
|---|---|---|
| Decorator | `@mcp.tool()` | `[McpServerTool]` |
| Descrição | docstring | `[Description("...")]` |
| Resources | `@mcp.resource()` | `[McpServerResource(...)]` |
| Transporte | `mcp.run(transport="stdio")` | `.WithStdioServerTransport()` |
| Container DI | — | `Microsoft.Extensions.Hosting` |

---

## 🐛 Exercício de Correção de Bugs: Corrija o Servidor MCP Quebrado

Este lab inclui um arquivo de servidor MCP em C# deliberadamente quebrado. Seu desafio: encontrar e corrigir 3 bugs.

```
lab-021/
└── BrokenMcpServer.cs    ← 3 bugs intencionais para encontrar e corrigir
```

**Configuração:**
```bash
mkdir mcp-bugfix && cd mcp-bugfix
dotnet new console -o BugFixServer
cd BugFixServer
dotnet add package ModelContextProtocol --prerelease
dotnet add package Microsoft.Extensions.Hosting

# Copie o arquivo quebrado sobre o Program.cs
cp ../lab-021/BrokenMcpServer.cs Program.cs
dotnet run
```

**Os 3 bugs:**

| # | Tool | Sintoma | Tipo |
|---|------|---------|------|
| 1 | `list_categories` | `NullReferenceException` na inicialização | Inicialização nula |
| 2 | `search_products` | Sempre retorna lista vazia `[]` | Inversão de lógica (`!`) |
| 3 | `get_product_details` | Retorna "not found" para IDs em minúsculas | Comparação sensível a maiúsculas/minúsculas |

**Verifique suas correções:** Após corrigir todos os 3 bugs, conecte-se com o MCP Inspector e execute:

- `list_categories()` → deve retornar `["Backpacks", "Sleeping Bags", "Tents"]`
- `search_products(keyword: "tent")` → deve retornar P001, P002, P003
- `get_product_details(productId: "p001")` → deve retornar os detalhes do TrailBlazer Tent 2P

---

## 🧠 Verificação de Conhecimento

??? question "**Q1 (Execute o Lab):** Após corrigir todos os 3 bugs e chamar `list_categories()`, o que a tool retorna? Liste as categorias na ordem em que aparecem na saída."

    Corrija os bugs, inicie o servidor, conecte-se com o MCP Inspector e chame `list_categories()`.

    ??? success "✅ Revelar Resposta"
        **`["Backpacks", "Sleeping Bags", "Tents"]`**

        As categorias são retornadas em ordem alfabética porque o código original usa uma `List<string>` ordenada. O bug #1 (`categories = null`) causava uma `NullReferenceException` antes de retornar qualquer coisa — corrigi-lo revela a lista corretamente ordenada.

??? question "**Q2 (Execute o Lab):** Após corrigir o bug #3 (o bug de comparação sensível a maiúsculas/minúsculas), qual valor de `StringComparison` substitui `StringComparison.Ordinal` na correção?"

    Leia a descrição do bug #3 cuidadosamente e depois observe a correção que você aplicou em [📥 `BrokenMcpServer.cs`](https://github.com/lcarli/AI-LearningHub/raw/main/docs/docs/en/labs/lab-021/BrokenMcpServer.cs).

    ??? success "✅ Revelar Resposta"
        **`StringComparison.OrdinalIgnoreCase`**

        O código original usava `StringComparison.Ordinal`, que é sensível a maiúsculas/minúsculas, então `get_product_details("p001")` falhava porque os IDs armazenados são em maiúsculas (`"P001"`). Substituí-lo por `OrdinalIgnoreCase` faz as buscas de ID funcionarem independentemente do formato de maiúsculas/minúsculas enviado pelo cliente.

??? question "**Q3 (Múltipla Escolha):** O bug #2 em `search_products` fazia com que sempre retornasse uma lista vazia. Qual foi a causa raiz?"

    - A) O parâmetro keyword era nulo
    - B) A chamada `Contains()` foi invertida com `!` — ela filtrava PARA FORA os resultados correspondentes em vez de mantê-los
    - C) A lista de produtos não foi inicializada
    - D) A busca era sensível a maiúsculas/minúsculas e nenhum produto correspondia

    ??? success "✅ Revelar Resposta"
        **Correto: B — Inversão de lógica**

        O código tinha `!product.Name.Contains(keyword)` — o `!` negava a condição, então os produtos que CONTINHAM a palavra-chave eram excluídos, e os produtos que NÃO continham a palavra-chave eram retornados. Com uma lista de resultados vazia, não havia produtos não correspondentes também. Remover o `!` corrige a lógica.

---

## Próximos Passos

- **Implantar este servidor na nuvem:** → [Lab 028 — Implantar MCP no Azure Container Apps](lab-028-deploy-mcp-azure.md)
- **Versão Python do servidor MCP:** → [Lab 020 — Servidor MCP em Python](lab-020-mcp-server-python.md)
