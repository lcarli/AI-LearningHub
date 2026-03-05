---
tags: [mcp, csharp, free, github-models]
---
# Lab 021 : Construire un serveur MCP en C#

<div class="lab-meta">
  <span><strong>Niveau :</strong> <span class="level-badge level-200">L200</span></span>
  <span><strong>Parcours :</strong> <a href="../paths/mcp/">MCP</a></span>
  <span><strong>Durée :</strong> ~45 min</span>
  <span><strong>💰 Coût :</strong> <span class="level-badge cost-free">Gratuit (local + Ollama)</span></span>
</div>

## Ce que vous apprendrez

- Créer un serveur MCP avec le **SDK .NET officiel ModelContextProtocol**
- Exposer des **outils**, des **ressources** et des **prompts** depuis C#
- Tester le serveur avec **MCP Inspector**
- Le connecter au **mode Agent de GitHub Copilot** via `mcp.json`

---

## Introduction

Python est idéal pour le prototypage rapide MCP, mais .NET est courant dans les environnements d'entreprise. Le package NuGet officiel `ModelContextProtocol` rend la construction de serveurs MCP en C# nativement supportée.

---

## Prérequis

- [.NET 8 SDK](https://dot.net) ou version ultérieure — gratuit
- [Lab 012 : Qu'est-ce que MCP ?](lab-012-what-is-mcp.md) recommandé
- Node.js (pour MCP Inspector) — gratuit

---

## 📦 Fichiers d'accompagnement

!!! note "Téléchargez ces fichiers avant de commencer le lab"
    Enregistrez tous les fichiers dans un dossier `lab-021/` dans votre répertoire de travail.

| Fichier | Description | Téléchargement |
|---------|-------------|----------------|
| `BrokenMcpServer.cs` | Exercice de correction de bugs (3 bugs + auto-tests) | [📥 Télécharger](https://github.com/lcarli/AI-LearningHub/raw/main/docs/docs/en/labs/lab-021/BrokenMcpServer.cs) |

---

## Exercice du lab

### Étape 1 : Créer le projet

```bash
mkdir mcp-csharp-demo && cd mcp-csharp-demo
dotnet new console -o ProductServer
cd ProductServer
dotnet add package ModelContextProtocol --prerelease
dotnet add package Microsoft.Extensions.Hosting
```

### Étape 2 : Construire le serveur MCP

Remplacez `Program.cs` par :

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

Créez `ProductTools.cs` :

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

### Étape 3 : Exécuter et tester avec MCP Inspector

**Terminal 1** — compiler le serveur :
```bash
dotnet build
```

**Tester avec MCP Inspector :**
```bash
npx @modelcontextprotocol/inspector dotnet run
```

Dans Inspector, cliquez sur **Tools** et testez `search_products` avec la requête `"camping"`. Vous devriez voir la tente renvoyée.

### Étape 4 : Ajouter une ressource

Les ressources exposent des données en lecture seule (fichiers, vues de base de données, etc.). Ajoutez dans `ProductTools.cs` :

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

Mettez à jour `Program.cs` pour enregistrer les ressources :
```csharp
builder.Services
    .AddMcpServer()
    .WithStdioServerTransport()
    .WithTools<ProductTools>()
    .WithResources<ProductResources>();  // ← ajoutez ceci
```

### Étape 5 : Connecter à GitHub Copilot

Ajoutez dans `.vscode/mcp.json` de votre espace de travail :

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

Activez le mode Agent dans VS Code, puis demandez : *« Quels produits de camping sont en stock ? »*

---

## Différences clés vs SDK Python

| | Python | C# |
|---|---|---|
| Décorateur | `@mcp.tool()` | `[McpServerTool]` |
| Description | docstring | `[Description("...")]` |
| Ressources | `@mcp.resource()` | `[McpServerResource(...)]` |
| Transport | `mcp.run(transport="stdio")` | `.WithStdioServerTransport()` |
| Conteneur DI | — | `Microsoft.Extensions.Hosting` |

---

## 🐛 Exercice de correction de bugs : Réparer le serveur MCP cassé

Ce lab inclut un fichier de serveur MCP C# volontairement cassé. Votre défi : trouver et corriger 3 bugs.

```
lab-021/
└── BrokenMcpServer.cs    ← 3 bugs intentionnels à trouver et corriger
```

**Configuration :**
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

**Les 3 bugs :**

| # | Outil | Symptôme | Type |
|---|-------|----------|------|
| 1 | `list_categories` | `NullReferenceException` au démarrage | Initialisation null |
| 2 | `search_products` | Retourne toujours une liste vide `[]` | Inversion logique (`!`) |
| 3 | `get_product_details` | Retourne "not found" pour les IDs en minuscules | Comparaison sensible à la casse |

**Vérifiez vos corrections :** Après avoir corrigé les 3 bugs, connectez-vous avec MCP Inspector et exécutez :

- `list_categories()` → devrait retourner `["Backpacks", "Sleeping Bags", "Tents"]`
- `search_products(keyword: "tent")` → devrait retourner P001, P002, P003
- `get_product_details(productId: "p001")` → devrait retourner les détails de TrailBlazer Tent 2P

---

## 🧠 Quiz de connaissances

??? question "**Q1 (Exécutez le lab) :** Après avoir corrigé les 3 bugs et appelé `list_categories()`, que retourne l'outil ? Listez les catégories dans l'ordre où elles apparaissent dans la sortie."

    Corrigez les bugs, démarrez le serveur, connectez-vous avec MCP Inspector et appelez `list_categories()`.

    ??? success "✅ Révéler la réponse"
        **`["Backpacks", "Sleeping Bags", "Tents"]`**

        Les catégories sont retournées par ordre alphabétique car le code original utilise une `List<string>` triée. Le bug #1 (`categories = null`) causait une `NullReferenceException` avant de retourner quoi que ce soit — le corriger révèle la liste correctement triée.

??? question "**Q2 (Exécutez le lab) :** Après avoir corrigé le bug #3 (le bug de comparaison sensible à la casse), quelle valeur de `StringComparison` remplace `StringComparison.Ordinal` dans la correction ?"

    Lisez attentivement la description du bug #3, puis regardez la correction que vous avez appliquée dans [📥 `BrokenMcpServer.cs`](https://github.com/lcarli/AI-LearningHub/raw/main/docs/docs/en/labs/lab-021/BrokenMcpServer.cs).

    ??? success "✅ Révéler la réponse"
        **`StringComparison.OrdinalIgnoreCase`**

        Le code original utilisait `StringComparison.Ordinal` qui est sensible à la casse, donc `get_product_details("p001")` échouait car les IDs stockés sont en majuscules (`"P001"`). Le remplacer par `OrdinalIgnoreCase` fait fonctionner les recherches d'ID quelle que soit la casse envoyée par le client.

??? question "**Q3 (Choix multiple) :** Le bug #2 dans `search_products` causait un retour de liste toujours vide. Quelle était la cause racine ?"

    - A) Le paramètre keyword était null
    - B) L'appel `Contains()` était inversé avec `!` — il filtrait les correspondances au lieu de les garder
    - C) La liste de produits n'était pas initialisée
    - D) La recherche était sensible à la casse et aucun produit ne correspondait

    ??? success "✅ Révéler la réponse"
        **Correct : B — Inversion logique**

        Le code avait `!product.Name.Contains(keyword)` — le `!` inversait la condition, donc les produits qui contenaient le mot-clé étaient exclus, et les produits qui ne contenaient pas le mot-clé étaient retournés. Avec une liste de résultats vide, il n'y avait aucun produit non-correspondant non plus. Supprimer le `!` corrige la logique.

---

## Prochaines étapes

- **Déployer ce serveur dans le cloud :** → [Lab 028 — Déployer MCP sur Azure Container Apps](lab-028-deploy-mcp-azure.md)
- **Version Python du serveur MCP :** → [Lab 020 — Serveur MCP en Python](lab-020-mcp-server-python.md)
