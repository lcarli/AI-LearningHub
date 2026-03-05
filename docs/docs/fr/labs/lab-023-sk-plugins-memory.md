---
tags: [semantic-kernel, python, free, github-models]
---
# Lab 023 : Semantic Kernel — Plugins, mémoire & planificateurs

<div class="lab-meta">
  <span><strong>Niveau :</strong> <span class="level-badge level-200">L200</span></span>
  <span><strong>Parcours :</strong> <a href="../paths/semantic-kernel/">Semantic Kernel</a></span>
  <span><strong>Durée :</strong> ~45 min</span>
  <span><strong>💰 Coût :</strong> <span class="level-badge cost-github">GitHub Free</span></span>
</div>
!!! warning "Semantic Kernel -> Microsoft Agent Framework"
    Semantic Kernel fait désormais partie de **Microsoft Agent Framework (MAF)**, qui unifie SK et AutoGen en un seul framework. Les concepts de ce lab restent valables — MAF s'appuie dessus. Voir **[Lab 076 : Microsoft Agent Framework](lab-076-microsoft-agent-framework.md)** pour le guide de migration.



## Ce que vous apprendrez

- Créer des **plugins à fonctions natives** en Python et C#
- Utiliser **KernelArguments** pour passer des données typées entre plugins
- Ajouter un **magasin de vecteurs en mémoire** pour la mémoire sémantique
- Utiliser l'**appel automatique de fonctions** pour laisser le LLM orchestrer les plugins
- Comprendre le fonctionnement des planificateurs SK

---

## Introduction

Le [Lab 014](lab-014-sk-hello-agent.md) a construit un agent SK minimal. Ce lab va plus loin : plusieurs plugins fonctionnant ensemble, la mémoire sémantique, et laisser le noyau décider quels outils appeler.

---

## Prérequis

=== "Python"
    ```bash
    pip install semantic-kernel openai
    ```

=== "C#"
    ```bash
    dotnet add package Microsoft.SemanticKernel
    dotnet add package Microsoft.SemanticKernel.Connectors.InMemory --prerelease
    ```

Configurez `GITHUB_TOKEN`.

---

!!! tip "Démarrage rapide avec GitHub Codespaces"
    [![Open in GitHub Codespaces](https://github.com/codespaces/badge.svg)](https://codespaces.new/lcarli/AI-LearningHub?quickstart=1)

    Toutes les dépendances sont pré-installées dans le devcontainer.


## 📦 Fichiers d'accompagnement

!!! note "Téléchargez ces fichiers avant de commencer le lab"
    Enregistrez tous les fichiers dans un dossier `lab-023/` dans votre répertoire de travail.

| Fichier | Description | Téléchargement |
|---------|-------------|----------------|
| `broken_plugin.py` | Exercice de correction de bugs (3 bugs + auto-tests) | [📥 Télécharger](https://github.com/lcarli/AI-LearningHub/raw/main/docs/docs/en/labs/lab-023/broken_plugin.py) |

---

## Exercice du lab

### Étape 1 : Créer un agent multi-plugins

=== "Python"

    ```python
    import os, asyncio
    from semantic_kernel import Kernel
    from semantic_kernel.connectors.ai.open_ai import OpenAIChatCompletion
    from semantic_kernel.functions import kernel_function
    from semantic_kernel.connectors.ai.open_ai import OpenAIChatPromptExecutionSettings
    from semantic_kernel.connectors.ai.function_choice_behavior import FunctionChoiceBehavior

    # --- Plugin 1: Products ---
    class ProductPlugin:
        @kernel_function(description="Search products by keyword")
        def search_products(self, query: str) -> str:
            catalog = [
                {"id": "P001", "name": "TrailBlazer X200", "price": 189.99, "category": "footwear"},
                {"id": "P002", "name": "Summit Pro Tent",  "price": 349.00, "category": "camping"},
                {"id": "P003", "name": "ClimbTech Harness","price": 129.99, "category": "climbing"},
            ]
            results = [p for p in catalog if query.lower() in p["name"].lower() or query.lower() in p["category"].lower()]
            return str(results) if results else "No products found."

        @kernel_function(description="Get the current shopping cart total")
        def get_cart_total(self) -> str:
            return "Current cart: 1x TrailBlazer X200 ($189.99). Total: $189.99"

    # --- Plugin 2: Weather (for trip planning) ---
    class WeatherPlugin:
        @kernel_function(description="Get trail conditions for a location")
        def get_trail_conditions(self, location: str) -> str:
            conditions = {
                "olympic": "Muddy, 45°F, light rain. Waterproof boots recommended.",
                "rainier": "Snow above 5000ft. Crampons required above treeline.",
                "cascades": "Clear, 62°F. Ideal conditions.",
            }
            for key, val in conditions.items():
                if key in location.lower():
                    return val
            return f"No trail data for {location}. Check local ranger station."

    # --- Plugin 3: Math/Utilities ---
    class UtilityPlugin:
        @kernel_function(description="Calculate total price with tax")
        def calculate_with_tax(self, subtotal: float, tax_rate: float = 0.098) -> str:
            total = subtotal * (1 + tax_rate)
            return f"${subtotal:.2f} + {tax_rate*100:.1f}% tax = ${total:.2f}"

    async def main():
        kernel = Kernel()
        kernel.add_service(OpenAIChatCompletion(
            ai_model_id="gpt-4o-mini",
            api_key=os.environ["GITHUB_TOKEN"],
            base_url="https://models.inference.ai.azure.com/openai",
        ))

        # Register all plugins
        kernel.add_plugin(ProductPlugin(), plugin_name="Products")
        kernel.add_plugin(WeatherPlugin(), plugin_name="Weather")
        kernel.add_plugin(UtilityPlugin(), plugin_name="Utils")

        # Auto function calling — kernel decides which tools to use
        settings = OpenAIChatPromptExecutionSettings(
            function_choice_behavior=FunctionChoiceBehavior.Auto()
        )

        questions = [
            "What camping gear do you have, and what's the total with Washington state tax?",
            "I'm planning a hike on Mount Rainier — what gear and conditions should I expect?",
        ]

        for question in questions:
            print(f"\n❓ {question}")
            result = await kernel.invoke_prompt(
                question,
                execution_settings=settings,
            )
            print(f"💬 {result}")

    asyncio.run(main())
    ```

### Étape 2 : Ajouter la mémoire sémantique

La mémoire sémantique vous permet de stocker des faits et de les récupérer par signification (et non par mot-clé).

=== "Python"

    ```python
    import os, asyncio
    from semantic_kernel import Kernel
    from semantic_kernel.connectors.ai.open_ai import OpenAIChatCompletion, OpenAITextEmbedding
    from semantic_kernel.memory import SemanticTextMemory, VolatileMemoryStore

    async def demo_memory():
        kernel = Kernel()
        kernel.add_service(OpenAIChatCompletion(
            ai_model_id="gpt-4o-mini",
            api_key=os.environ["GITHUB_TOKEN"],
            base_url="https://models.inference.ai.azure.com/openai",
        ))
        embedding_service = OpenAITextEmbedding(
            ai_model_id="text-embedding-3-small",
            api_key=os.environ["GITHUB_TOKEN"],
            base_url="https://models.inference.ai.azure.com/openai",
        )

        memory = SemanticTextMemory(
            storage=VolatileMemoryStore(),
            embeddings_generator=embedding_service,
        )

        # Store facts
        facts = [
            ("boot-care",    "Clean boots after each use. Apply waterproofing spray every 3 months."),
            ("tent-setup",   "Always stake tent before raising poles in wind."),
            ("harness-check","Inspect harness stitching and buckles before every climb."),
            ("layering",     "Base layer wicks moisture. Mid layer insulates. Shell blocks wind/rain."),
        ]

        collection = "outdoor-tips"
        for key, fact in facts:
            await memory.save_information(collection, id=key, text=fact)

        # Retrieve by meaning
        queries = ["how do I maintain my footwear?", "safety check before climbing"]
        for q in queries:
            results = await memory.search(collection, q, limit=2, min_relevance_score=0.7)
            print(f"\n🔍 '{q}'")
            for r in results:
                print(f"  [{r.relevance:.2f}] {r.text}")

    asyncio.run(demo_memory())
    ```

### Étape 3 : Combiner plugins et mémoire

```python
from semantic_kernel.core_plugins.text_memory_plugin import TextMemoryPlugin

async def agent_with_memory():
    kernel = Kernel()
    # ... (add services as above) ...

    memory = SemanticTextMemory(
        storage=VolatileMemoryStore(),
        embeddings_generator=embedding_service,
    )

    # TextMemoryPlugin exposes memory as a kernel function
    kernel.add_plugin(TextMemoryPlugin(memory), plugin_name="Memory")
    kernel.add_plugin(ProductPlugin(), plugin_name="Products")

    # Now the agent can use memory AND product search together
    settings = OpenAIChatPromptExecutionSettings(
        function_choice_behavior=FunctionChoiceBehavior.Auto()
    )

    result = await kernel.invoke_prompt(
        "I'm going hiking in wet weather — what should I remember about gear maintenance?",
        execution_settings=settings,
    )
    print(result)
```

### Étape 4 : Comprendre les planificateurs

Les planificateurs SK décomposent un objectif en étapes. L'approche moderne est l'**appel automatique de fonctions** (comme utilisé ci-dessus) — le LLM génère un plan et l'exécute en une seule boucle.

Pour l'explicabilité, vous pouvez journaliser chaque appel de fonction :

```python
from semantic_kernel.filters import FunctionInvocationContext

async def log_function_calls(context: FunctionInvocationContext, next):
    print(f"  📞 Calling: {context.function.plugin_name}.{context.function.name}")
    print(f"     Args: {context.arguments}")
    await next(context)
    print(f"     Result: {str(context.result)[:100]}")

kernel.add_filter("function_invocation", log_function_calls)
```

---

## Résumé des concepts clés

| Concept | Rôle |
|---------|------|
| **Plugin** | Regroupe des méthodes `@kernel_function` liées |
| **KernelArguments** | Dictionnaire typé passé entre les fonctions |
| **Appel automatique de fonctions** | Le LLM décide quels plugins appeler |
| **Mémoire sémantique** | Magasin de vecteurs pour la récupération par signification |
| **TextMemoryPlugin** | Connecte le magasin de mémoire au système de plugins |
| **Filtre** | Middleware — journaliser, authentifier ou modifier les appels de fonctions |

---

## 🐛 Exercice de correction de bugs : Réparer le plugin SK cassé

Ce lab inclut un plugin Semantic Kernel volontairement cassé. Trouvez et corrigez 3 bugs !

```
lab-023/
└── broken_plugin.py    ← 3 bugs intentionnels à trouver et corriger
```

**Configuration :**
```bash
pip install semantic-kernel openai

# Run the test suite to see which tests fail
python lab-023/broken_plugin.py
```

**Les 3 bugs :**

| # | Fonction | Symptôme | Type |
|---|----------|----------|------|
| 1 | `search_products` | SK ne découvre pas la fonction | Décorateur `@kernel_function` manquant |
| 2 | `get_cart_total` | Retourne `$2.00` au lieu de `$339.98` | Accumule la quantité et non le prix |
| 3 | `calculate_price_with_tax` | Retourne `$291.59` au lieu de `$269.99` | Taxe appliquée deux fois |

**Vérifiez vos corrections :** Le testeur intégré vérifie chaque fonction :
```bash
python lab-023/broken_plugin.py
# Expected output:
# ✅ Passed — found 3 tents
# ✅ Passed — cart total = $339.98
# ✅ Passed — price with tax = $269.99
# 🎉 All tests passed! Your plugin is bug-free.
```

---

## 🧠 Quiz de connaissances

??? question "**Q1 (Exécutez le lab) :** Après avoir corrigé le bug #2, que retourne `get_cart_total()` quand le panier contient P001 (×1) à $249.99 et P007 (×1) à $89.99 ?"

    Corrigez le bug #2 dans [📥 `broken_plugin.py`](https://github.com/lcarli/AI-LearningHub/raw/main/docs/docs/en/labs/lab-023/broken_plugin.py) et exécutez-le, ou calculez manuellement : prix P001 × 1 + prix P007 × 1.

    ??? success "✅ Révéler la réponse"
        **$339.98**

        Le panier contient 1× P001 (TrailBlazer Tent 2P, $249.99) et 1× P007 (DayHiker 22L, $89.99). `total = 249.99 + 89.99 = $339.98`. Le bug #2 accumulait la *quantité* de l'article au lieu de `prix * quantité`, donc les paniers à article unique retournaient le nombre de quantité (par ex. `$1.00`, `$2.00`) au lieu du prix.

??? question "**Q2 (Exécutez le lab) :** Après avoir corrigé LES 3 bugs, exécutez `python lab-023/broken_plugin.py`. Combien de fonctions SK le testeur découvre-t-il dans OutdoorGearPlugin ?"

    Après toutes les corrections, exécutez le script. Cherchez la ligne « SK discovers N functions » dans la sortie.

    ??? success "✅ Révéler la réponse"
        **3 fonctions : `search_products`, `get_cart_total` et `calculate_price_with_tax`**

        Avant la correction du bug #1 (décorateur `@kernel_function` manquant), SK ne pouvait découvrir que 2 fonctions. Après avoir ajouté le décorateur à `search_products`, les 3 sont visibles par le planificateur SK. C'est pourquoi les décorateurs sont importants — sans `@kernel_function`, SK ignore simplement la fonction.

??? question "**Q3 (Choix multiple) :** Le bug #3 faisait que `calculate_price_with_tax(249.99, tax_rate=0.08)` retournait ~$291.59 au lieu de $269.99. Quelle était la cause racine ?"

    - A) Le prix de base était doublé avant l'application de la taxe
    - B) La taxe était appliquée au résultat d'un calcul de taxe précédent (appliquée deux fois)
    - C) La fonction utilisait la mauvaise variable de taux de taxe
    - D) La taxe était soustraite au lieu d'être ajoutée

    ??? success "✅ Révéler la réponse"
        **Correct : B — La taxe était appliquée deux fois**

        Le code buggé calculait d'abord `price_with_tax = price * (1 + tax_rate)` → $269.99, puis appliquait la taxe *à nouveau* sur ce résultat : `$269.99 * 1.08 = $291.59`. La correction : calculer et retourner en une seule étape — `return round(price * (1 + tax_rate), 2)`.

---

## Prochaines étapes

- **Orchestration multi-agents avec SK :** → [Lab 034 — Systèmes multi-agents SK](lab-034-multi-agent-sk.md)
- **Pipeline RAG avec SK :** → [Lab 022 — RAG avec pgvector](lab-022-rag-github-models-pgvector.md)
