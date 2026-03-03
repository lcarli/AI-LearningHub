/*
 * BrokenMcpServer.cs — OutdoorGear MCP Server (C#) — INTENTIONALLY BROKEN
 *
 * Lab 021: Build an MCP Server in C# — Interactive Bug-Fix Exercise
 *
 * This file contains 3 deliberate bugs. Your task is to:
 *   1. Read the error description in each BUG comment
 *   2. Identify the problem in the code
 *   3. Fix it — then test with the MCP Inspector to confirm it works
 *
 * Prerequisites:
 *   dotnet add package ModelContextProtocol --prerelease
 *   dotnet add package Microsoft.Extensions.Hosting
 *
 * Expected behavior when all bugs are fixed:
 *   - list_categories returns sorted category names (no NullReferenceException)
 *   - search_products returns filtered results (not always empty list)
 *   - get_product_details returns product for "p001" lowercase input (not "not found")
 */

using Microsoft.Extensions.DependencyInjection;
using Microsoft.Extensions.Hosting;
using ModelContextProtocol.Server;
using System.ComponentModel;

// ─── Entry point ──────────────────────────────────────────────────────────────
var builder = Host.CreateApplicationBuilder(args);
builder.Services
    .AddMcpServer()
    .WithStdioServerTransport()
    .WithToolsFromAssembly();

await builder.Build().RunAsync();

// ─── Data ─────────────────────────────────────────────────────────────────────
public static class ProductCatalog
{
    public static readonly List<Product> Products = new()
    {
        new("P001", "TrailBlazer Tent 2P",          "Tents",         249.99m, 1800, true),
        new("P002", "Summit Dome 4P",                "Tents",         549.99m, 3200, true),
        new("P003", "TrailBlazer Solo",              "Tents",         299.99m,  850, true),
        new("P004", "ArcticDown -20°C Sleeping Bag", "Sleeping Bags", 389.99m, 1400, true),
        new("P005", "SummerLight +5°C Sleeping Bag", "Sleeping Bags", 149.99m,  700, true),
        new("P006", "Osprey Atmos 65L Backpack",     "Backpacks",     289.99m, 1980, true),
        new("P007", "DayHiker 22L Daypack",          "Backpacks",      89.99m,  580, true),
    };
}

public record Product(
    string Id,
    string Name,
    string Category,
    decimal PriceUsd,
    int WeightGrams,
    bool InStock
);

// ─── MCP Tools ────────────────────────────────────────────────────────────────
[McpServerToolType]
public static class OutdoorGearTools
{
    // =========================================================================
    // TOOL 1: list_categories
    //
    // ❌ BUG #1 — NullReferenceException
    //
    // Expected: Returns ["Backpacks", "Sleeping Bags", "Tents"] (sorted)
    // Actual:   Throws NullReferenceException when the loop runs
    //
    // Hint: Look at how `categories` is initialized before the loop.
    // Fix: Initialize it as an empty List<string>() instead of null.
    // =========================================================================
    [McpServerTool, Description("List all available product categories in the catalog.")]
    public static List<string> list_categories()
    {
        List<string>? categories = null;  // ← BUG #1: should be new List<string>()

        foreach (var product in ProductCatalog.Products)
        {
            if (!categories!.Contains(product.Category))
            {
                categories.Add(product.Category);
            }
        }

        categories.Sort();
        return categories;
    }

    // =========================================================================
    // TOOL 2: search_products
    //
    // ❌ BUG #2 — Always returns empty list
    //
    // Expected: search_products("tent") returns P001, P002, P003
    // Actual:   Returns [] for every query
    //
    // Hint: Look at the keyword matching condition. The logic is inverted.
    // Fix: Remove the `!` from the Contains check.
    // =========================================================================
    [McpServerTool, Description(
        "Search for products by keyword. " +
        "Optionally filter by category name (use list_categories to see valid values). " +
        "Returns matching products with id, name, category, and price.")]
    public static List<object> search_products(
        [Description("Keyword to search for in product names")] string keyword,
        [Description("Optional category filter")] string? category = null,
        [Description("Optional maximum price in USD")] decimal? maxPrice = null)
    {
        var results = new List<object>();
        var keywordLower = keyword.ToLower();

        foreach (var product in ProductCatalog.Products)
        {
            // BUG #2: condition is negated — skips matches, keeps non-matches
            if (!product.Name.ToLower().Contains(keywordLower))  // ← remove the `!`
            {
                continue;
            }

            if (category != null && product.Category != category)
                continue;

            if (maxPrice.HasValue && product.PriceUsd > maxPrice.Value)
                continue;

            results.Add(new
            {
                product.Id,
                product.Name,
                product.Category,
                product.PriceUsd,
                product.InStock,
            });
        }

        return results;
    }

    // =========================================================================
    // TOOL 3: get_product_details
    //
    // ❌ BUG #3 — Case-sensitive ID matching breaks LLM tool calls
    //
    // Expected: get_product_details("p001") returns the TrailBlazer Tent 2P
    // Actual:   Returns {"error": "Product not found"} for lowercase IDs
    //
    // Hint: LLMs often call tools with lowercase parameter values even when
    //       IDs are uppercase in the docs. The comparison must be case-insensitive.
    // Fix: Change StringComparison.Ordinal to StringComparison.OrdinalIgnoreCase
    // =========================================================================
    [McpServerTool, Description(
        "Get full details for a specific product by its ID (e.g. 'P001'). " +
        "Returns all fields including weight, description, and stock status.")]
    public static object get_product_details(
        [Description("The product ID, e.g. P001, P002, ... P007")] string productId)
    {
        // BUG #3: Ordinal is case-sensitive; "p001" != "P001"
        var product = ProductCatalog.Products
            .FirstOrDefault(p => string.Equals(p.Id, productId, StringComparison.Ordinal));  // ← fix comparison

        if (product is null)
        {
            return new { error = "Product not found", productId };
        }

        return new
        {
            product.Id,
            product.Name,
            product.Category,
            product.PriceUsd,
            product.WeightGrams,
            product.InStock,
        };
    }
}
