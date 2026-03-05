"""
outdoorgear_mcp_server_starter.py — OutdoorGear MCP Server Starter

Lab 020: Build an MCP Server in Python

This starter file contains TODO markers where you need to write the code.
Follow the instructions in each TODO to complete the lab.

Prerequisites:
  pip install fastmcp

Run with:
  python outdoorgear_mcp_server_starter.py
"""

from fastmcp import FastMCP

# ============================================================
# Server initialization
# ============================================================

# TODO 1: Initialize the FastMCP server with:
#   name = "outdoorgear-catalog"
#   description = "OutdoorGear Inc. product catalog MCP server"
# mcp = FastMCP(...)
mcp = None  # Replace this line with the FastMCP initialization


# ============================================================
# Data: OutdoorGear product catalog
# ============================================================

PRODUCTS = [
    {
        "id": "P001",
        "name": "TrailBlazer Tent 2P",
        "category": "Tents",
        "description": "Lightweight 2-person backpacking tent, 3-season, aluminum poles",
        "price_usd": 249.99,
        "weight_grams": 1800,
        "in_stock": True,
        "season": "3-season",
    },
    {
        "id": "P002",
        "name": "Summit Dome 4P",
        "category": "Tents",
        "description": "4-season expedition tent for 4 people, steel poles, snow rated",
        "price_usd": 549.99,
        "weight_grams": 3200,
        "in_stock": True,
        "season": "4-season",
    },
    {
        "id": "P003",
        "name": "TrailBlazer Solo",
        "category": "Tents",
        "description": "Ultra-light solo tent, 3-season, 850g, fast-and-light hiking",
        "price_usd": 299.99,
        "weight_grams": 850,
        "in_stock": True,
        "season": "3-season",
    },
    {
        "id": "P004",
        "name": "ArcticDown -20°C Sleeping Bag",
        "category": "Sleeping Bags",
        "description": "Winter sleeping bag, 800-fill down, rated to -20°C, mummy shape",
        "price_usd": 389.99,
        "weight_grams": 1400,
        "in_stock": True,
        "season": "winter",
    },
    {
        "id": "P005",
        "name": "SummerLight +5°C Sleeping Bag",
        "category": "Sleeping Bags",
        "description": "Lightweight summer sleeping bag, synthetic insulation, +5°C",
        "price_usd": 149.99,
        "weight_grams": 700,
        "in_stock": True,
        "season": "summer",
    },
    {
        "id": "P006",
        "name": "Osprey Atmos 65L Backpack",
        "category": "Backpacks",
        "description": "65-liter backpacking pack, anti-gravity suspension, hipbelt pockets",
        "price_usd": 289.99,
        "weight_grams": 1980,
        "in_stock": True,
        "season": "all",
    },
    {
        "id": "P007",
        "name": "DayHiker 22L Daypack",
        "category": "Backpacks",
        "description": "22-liter lightweight daypack, laptop sleeve, hydration compatible",
        "price_usd": 89.99,
        "weight_grams": 580,
        "in_stock": True,
        "season": "all",
    },
]


# ============================================================
# TOOL 1: list_categories
# ============================================================

# TODO 2: Define a tool called `list_categories` using the @mcp.tool() decorator.
#
# Requirements:
#   - Takes no parameters
#   - Returns a sorted list of unique category names (strings) from PRODUCTS
#   - Include a docstring: "List all available product categories."
#
# Hint: use set() + sorted() to get unique sorted categories
#
# @mcp.tool()
# def list_categories() -> list[str]:
#     ...


# ============================================================
# TOOL 2: search_products
# ============================================================

# TODO 3: Define a tool called `search_products` using the @mcp.tool() decorator.
#
# Parameters:
#   - keyword: str — search term matched against product name and description
#   - category: str | None = None — optional filter (use list_categories for valid values)
#   - max_price: float | None = None — optional maximum price in USD
#   - in_stock_only: bool = True — if True, only return in-stock items
#   - max_results: int = 5 — maximum number of results
#
# Returns: list[dict] — matching products (each dict has id, name, category, price_usd, in_stock)
#
# Docstring should explain each parameter (the LLM reads this to decide when/how to use the tool!)
#
# @mcp.tool()
# def search_products(keyword: str, ...) -> list[dict]:
#     ...


# ============================================================
# TOOL 3: get_product_details
# ============================================================

# TODO 4: Define a tool called `get_product_details` using the @mcp.tool() decorator.
#
# Parameters:
#   - product_id: str — the product ID (e.g. "P001")
#
# Returns:
#   - The full product dict if found (all fields including description, weight_grams, season)
#   - {"error": "Product not found", "product_id": product_id} if not found
#
# @mcp.tool()
# def get_product_details(product_id: str) -> dict:
#     ...


# ============================================================
# TOOL 4: compare_products  (CHALLENGE — more advanced)
# ============================================================

# TODO 5 (Challenge): Define a tool called `compare_products`.
#
# Parameters:
#   - product_ids: list[str] — list of product IDs to compare (2-4 items)
#
# Returns: dict with structure:
#   {
#     "products": [...],          # list of found products
#     "not_found": [...],         # product_ids that weren't found
#     "lightest": "P003",         # id of lightest product (by weight_grams)
#     "cheapest": "P007",         # id of cheapest product (by price_usd)
#   }
#
# @mcp.tool()
# def compare_products(product_ids: list[str]) -> dict:
#     ...


# ============================================================
# Entry point
# ============================================================

if __name__ == "__main__":
    # TODO 6: Start the server by calling mcp.run()
    # This runs the server in stdio mode (default for local development)
    pass  # Replace with: mcp.run()
