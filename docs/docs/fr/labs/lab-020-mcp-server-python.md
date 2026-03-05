---
tags: [mcp, python, free, github-models]
---
# Lab 020 : Construire un serveur MCP en Python

<div class="lab-meta">
  <span><strong>Niveau :</strong> <span class="level-badge level-200">L200</span></span>
  <span><strong>Parcours :</strong> <a href="../paths/mcp/">🔌 MCP</a></span>
  <span><strong>Durée :</strong> ~45 min</span>
  <span><strong>💰 Coût :</strong> <span class="level-badge cost-free">Gratuit</span> — S'exécute localement, aucun compte cloud nécessaire</span>
</div>

## Ce que vous apprendrez

- Comment construire un serveur MCP à partir de zéro en utilisant **FastMCP** (Python)
- Comment définir des **outils (Tools)** avec des schémas et descriptions appropriés
- Comment exécuter le serveur et le connecter au **MCP Inspector** et à **GitHub Copilot (VS Code)**
- Comment ajouter le transport HTTP/SSE pour la compatibilité avec les agents cloud

---

## Introduction

Un serveur MCP est un programme qui expose des outils (fonctions) aux agents IA via le protocole MCP. Quand un agent a besoin d'effectuer une action — interroger une base de données, appeler une API, lire un fichier — il appelle les outils de votre serveur MCP.

Dans ce lab, nous construisons un **serveur MCP de recherche de produits** avec deux outils :

1. `list_categories` — retourne les catégories de produits
2. `search_products` — recherche des produits par mot-clé

---

## Prérequis

```bash
pip install fastmcp
```

Assurez-vous d'avoir Python 3.10+ :
```bash
python --version
```

---

!!! tip "Démarrage rapide avec GitHub Codespaces"
    [![Open in GitHub Codespaces](https://github.com/codespaces/badge.svg)](https://codespaces.new/lcarli/AI-LearningHub?quickstart=1)

    Toutes les dépendances sont pré-installées dans le devcontainer.


## 📦 Fichiers de support

!!! note "Téléchargez ces fichiers avant de commencer le lab"
    Enregistrez tous les fichiers dans un dossier `lab-020/` dans votre répertoire de travail.

| Fichier | Description | Téléchargement |
|---------|-------------|----------------|
| `outdoorgear_mcp_server_starter.py` | Script de démarrage avec des TODOs | [📥 Télécharger](https://github.com/lcarli/AI-LearningHub/raw/main/docs/docs/en/labs/lab-020/outdoorgear_mcp_server_starter.py) |

---

## Exercice du lab

### Étape 1 : Créer le projet

```bash
mkdir products-mcp-server
cd products-mcp-server
```

Créez `server.py` :

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

### Étape 2 : Définir vos outils

Ajoutez les outils après la liste `PRODUCTS` :

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

### Étape 3 : Exécuter le serveur (mode stdio)

Ajoutez le point d'entrée à la fin de `server.py` :

```python
if __name__ == "__main__":
    mcp.run()
```

Exécutez-le :
```bash
python server.py
```

Le serveur écoute maintenant sur **stdio**. C'est le mode par défaut pour les outils locaux.

### Étape 4 : Tester avec le MCP Inspector

Ouvrez un **nouveau terminal** et exécutez :
```bash
npx @modelcontextprotocol/inspector python server.py
```

L'Inspector s'ouvrira dans votre navigateur. Essayez :

1. Cliquez sur **"Tools"** pour voir vos trois outils
2. Cliquez sur `list_categories` → **"Run tool"** → voyez les catégories
3. Cliquez sur `search_products` → remplissez `keyword: "tent"` → **"Run tool"**

!!! success "Vous devriez voir la Camping Tent dans les résultats"

### Étape 5 : Exécuter en tant que serveur HTTP/SSE (pour les agents distants)

Pour les agents hébergés dans le cloud comme Microsoft Foundry, nous avons besoin du transport HTTP/SSE. Ajoutez l'option de démarrage :

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

Exécutez en mode HTTP :
```bash
python server.py --http
```

Vous verrez :
```
INFO:     Uvicorn running on http://0.0.0.0:8000
```

Testez avec curl :
```bash
curl http://localhost:8000/sse
```

### Étape 6 : Connecter à GitHub Copilot dans VS Code

1. Dans VS Code, créez `.vscode/mcp.json` dans votre espace de travail :

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

2. Ouvrez GitHub Copilot Chat dans VS Code
3. Tapez : `@copilot What product categories are available?`

GitHub Copilot appellera votre outil `list_categories` et inclura le résultat dans sa réponse !

!!! tip "Support MCP dans VS Code"
    Assurez-vous d'avoir l'extension **GitHub Copilot** version 1.99+ installée.  
    Vous devrez peut-être activer MCP dans les paramètres de VS Code : `"chat.mcp.enabled": true`

---

## Ajouter une ressource (Bonus)

MCP prend également en charge les **Resources** — des données que l'agent peut lire. Ajoutez une ressource qui expose le catalogue complet des produits :

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

## 📁 Fichier de démarrage

Ce lab inclut un fichier de démarrage avec des marqueurs TODO pour vous guider dans la construction du serveur :

```
lab-020/
└── outdoorgear_mcp_server_starter.py   ← 6 TODOs à compléter
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

Le fichier de démarrage contient le catalogue de produits OutdoorGear (P001–P007) déjà rempli. Vous implémentez : `list_categories`, `search_products`, `get_product_details`, et un outil de défi `compare_products`.

---

## 🏆 Défi : Ajouter un outil `compare_products`

Une fois les 3 outils de base fonctionnels, ajoutez un quatrième :

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

Testez-le dans le MCP Inspector en demandant :
> *"Comparez le TrailBlazer Tent 2P et le TrailBlazer Solo. Lequel est le plus léger ?"*

L'agent devrait appeler `compare_products(["P001", "P003"])` et retourner une comparaison structurée.

---

## Résumé

Vous avez construit un serveur MCP entièrement fonctionnel qui :

- ✅ Définit **3 outils** avec des descriptions appropriées (le LLM les utilise pour décider quand les appeler)
- ✅ S'exécute en **mode stdio** pour les outils locaux
- ✅ S'exécute en **mode HTTP/SSE** pour les agents distants
- ✅ Fonctionne avec le **MCP Inspector** pour les tests
- ✅ S'intègre avec **GitHub Copilot dans VS Code**

---

## Prochaines étapes

- **Version C# :** → [Lab 021 — Serveur MCP en C#](lab-021-mcp-server-csharp.md)
- **Connecter à Microsoft Foundry Agent Service :** → [Lab 030 — Foundry Agent Service + MCP](lab-030-foundry-agent-mcp.md)
- **Ajouter des requêtes sur une vraie base de données :** → [Lab 031 — Recherche sémantique pgvector](lab-031-pgvector-semantic-search.md)
