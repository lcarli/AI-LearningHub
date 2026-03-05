---
tags: [semantic-kernel, python, free, github-models]
---
# Lab 023: Semantic Kernel — Plugins, Memória e Planners

<div class="lab-meta">
  <span><strong>Nível:</strong> <span class="level-badge level-200">L200</span></span>
  <span><strong>Trilha:</strong> <a href="../paths/semantic-kernel/">Semantic Kernel</a></span>
  <span><strong>Tempo:</strong> ~45 min</span>
  <span><strong>💰 Custo:</strong> <span class="level-badge cost-github">GitHub Gratuito</span></span>
</div>
!!! warning "Semantic Kernel -> Microsoft Agent Framework"
    O Semantic Kernel agora faz parte do **Microsoft Agent Framework (MAF)**, que unifica o SK e o AutoGen em um único framework. Os conceitos deste lab ainda se aplicam — o MAF é construído sobre eles. Veja **[Lab 076: Microsoft Agent Framework](lab-076-microsoft-agent-framework.md)** para o guia de migração.



## O que Você Vai Aprender

- Criar **plugins de funções nativas** em Python e C#
- Usar **KernelArguments** para passar dados tipados entre plugins
- Adicionar **armazenamento vetorial em memória** para memória semântica
- Usar **chamada automática de funções** para permitir que o LLM orquestre plugins
- Entender como funcionam os planners do SK

---

## Introdução

O [Lab 014](lab-014-sk-hello-agent.md) construiu um agente SK mínimo. Este lab vai mais fundo: múltiplos plugins trabalhando juntos, memória semântica e deixando o kernel decidir quais ferramentas chamar.

---

## Pré-requisitos

=== "Python"
    ```bash
    pip install semantic-kernel openai
    ```

=== "C#"
    ```bash
    dotnet add package Microsoft.SemanticKernel
    dotnet add package Microsoft.SemanticKernel.Connectors.InMemory --prerelease
    ```

Configure o `GITHUB_TOKEN`.

---

!!! tip "Início Rápido com GitHub Codespaces"
    [![Open in GitHub Codespaces](https://github.com/codespaces/badge.svg)](https://codespaces.new/lcarli/AI-LearningHub?quickstart=1)

    Todas as dependências estão pré-instaladas no devcontainer.


## 📦 Arquivos de Apoio

!!! note "Baixe estes arquivos antes de iniciar o lab"
    Salve todos os arquivos em uma pasta `lab-023/` no seu diretório de trabalho.

| Arquivo | Descrição | Download |
|------|-------------|----------|
| `broken_plugin.py` | Exercício de correção de bugs (3 bugs + auto-testes) | [📥 Download](https://github.com/lcarli/AI-LearningHub/raw/main/docs/docs/en/labs/lab-023/broken_plugin.py) |

---

## Exercício do Lab

### Passo 1: Criar um agente multi-plugin

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
            print(f"
❓ {question}")
            result = await kernel.invoke_prompt(
                question,
                execution_settings=settings,
            )
            print(f"💬 {result}")

    asyncio.run(main())
    ```

### Passo 2: Adicionar memória semântica

A memória semântica permite armazenar fatos e recuperá-los por significado (não por palavra-chave).

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
            print(f"
🔍 '{q}'")
            for r in results:
                print(f"  [{r.relevance:.2f}] {r.text}")

    asyncio.run(demo_memory())
    ```

### Passo 3: Combinando plugins com memória

```python
from semantic_kernel.core_plugins.text_memory_plugin import TextMemoryPlugin

async def agent_with_memory():
    kernel = Kernel()
    # ... (adicione os serviços como acima) ...

    memory = SemanticTextMemory(
        storage=VolatileMemoryStore(),
        embeddings_generator=embedding_service,
    )

    # TextMemoryPlugin expõe a memória como uma função do kernel
    kernel.add_plugin(TextMemoryPlugin(memory), plugin_name="Memory")
    kernel.add_plugin(ProductPlugin(), plugin_name="Products")

    # Agora o agente pode usar memória E busca de produtos juntos
    settings = OpenAIChatPromptExecutionSettings(
        function_choice_behavior=FunctionChoiceBehavior.Auto()
    )

    result = await kernel.invoke_prompt(
        "I'm going hiking in wet weather — what should I remember about gear maintenance?",
        execution_settings=settings,
    )
    print(result)
```

### Passo 4: Entendendo os planners

Os planners do SK decompõem um objetivo em etapas. A abordagem moderna é a **chamada automática de funções** (conforme usada acima) — o LLM gera um plano e o executa em um único loop.

Para rastreabilidade, você pode registrar cada chamada de função:

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

## Resumo dos Conceitos-Chave

| Conceito | O que faz |
|---------|-------------|
| **Plugin** | Agrupa métodos `@kernel_function` relacionados |
| **KernelArguments** | Dict tipado passado entre funções |
| **Chamada Automática de Funções** | O LLM decide quais plugins chamar |
| **Memória Semântica** | Armazenamento vetorial para recuperação baseada em significado |
| **TextMemoryPlugin** | Conecta o armazenamento de memória ao sistema de plugins |
| **Filter** | Middleware — registrar, autenticar ou modificar chamadas de função |

---

## 🐛 Exercício de Correção de Bugs: Corrija o Plugin SK Quebrado

Este lab inclui um plugin Semantic Kernel deliberadamente quebrado. Encontre e corrija 3 bugs!

```
lab-023/
└── broken_plugin.py    ← 3 bugs intencionais para encontrar e corrigir
```

**Configuração:**
```bash
pip install semantic-kernel openai

# Execute a suíte de testes para ver quais testes falham
python lab-023/broken_plugin.py
```

**Os 3 bugs:**

| # | Função | Sintoma | Tipo |
|---|----------|---------|------|
| 1 | `search_products` | O SK não descobre a função | Decorator `@kernel_function` ausente |
| 2 | `get_cart_total` | Retorna `$2.00` em vez de `$339.98` | Acumula quantidade em vez de preço |
| 3 | `calculate_price_with_tax` | Retorna `$291.59` em vez de `$269.99` | Imposto aplicado duas vezes |

**Verifique suas correções:** O executor de testes integrado verifica cada função:
```bash
python lab-023/broken_plugin.py
# Saída esperada:
# ✅ Passed — found 3 tents
# ✅ Passed — cart total = $339.98
# ✅ Passed — price with tax = $269.99
# 🎉 All tests passed! Your plugin is bug-free.
```

---

## 🧠 Verificação de Conhecimento

??? question "**Q1 (Execute o Lab):** Após corrigir o bug #2, o que `get_cart_total()` retorna quando o carrinho contém P001 (×1) a $249.99 e P007 (×1) a $89.99?"

    Corrija o bug #2 em [📥 `broken_plugin.py`](https://github.com/lcarli/AI-LearningHub/raw/main/docs/docs/en/labs/lab-023/broken_plugin.py) e execute-o, ou calcule manualmente: preço P001 × 1 + preço P007 × 1.

    ??? success "✅ Revelar Resposta"
        **$339.98**

        O carrinho contém 1× P001 (TrailBlazer Tent 2P, $249.99) e 1× P007 (DayHiker 22L, $89.99). `total = 249.99 + 89.99 = $339.98`. O bug #2 estava acumulando a *quantidade* do item em vez de `preço * quantidade`, então carrinhos com um único item retornavam o número da quantidade (ex.: `$1.00`, `$2.00`) em vez do preço.

??? question "**Q2 (Execute o Lab):** Após corrigir TODOS os 3 bugs, execute `python lab-023/broken_plugin.py`. Quantas funções SK o executor de testes descobre no OutdoorGearPlugin?"

    Após todas as correções, execute o script. Procure pela linha "SK discovers N functions" na saída.

    ??? success "✅ Revelar Resposta"
        **3 funções: `search_products`, `get_cart_total` e `calculate_price_with_tax`**

        Antes de corrigir o bug #1 (decorator `@kernel_function` ausente), o SK conseguia descobrir apenas 2 funções. Após adicionar o decorator de volta ao `search_products`, todas as 3 ficam visíveis para o planner do SK. É por isso que decorators importam — sem `@kernel_function`, o SK simplesmente ignora a função.

??? question "**Q3 (Múltipla Escolha):** O bug #3 fazia com que `calculate_price_with_tax(249.99, tax_rate=0.08)` retornasse ~$291.59 em vez de $269.99. Qual foi a causa raiz?"

    - A) O preço base foi dobrado antes da aplicação do imposto
    - B) O imposto foi aplicado ao resultado de um cálculo de imposto anterior (aplicado duas vezes)
    - C) A função usou a variável de taxa de imposto errada
    - D) O imposto foi subtraído em vez de adicionado

    ??? success "✅ Revelar Resposta"
        **Correto: B — O imposto foi aplicado duas vezes**

        O código com bug primeiro computava `price_with_tax = price * (1 + tax_rate)` → $269.99, depois aplicava o imposto *novamente* nesse resultado: `$269.99 * 1.08 = $291.59`. A correção: computar e retornar em uma única etapa — `return round(price * (1 + tax_rate), 2)`.

---

## Próximos Passos

- **Orquestração multi-agente com SK:** → [Lab 034 — Sistemas Multi-Agente do SK](lab-034-multi-agent-sk.md)
- **Pipeline RAG com SK:** → [Lab 022 — RAG com pgvector](lab-022-rag-github-models-pgvector.md)
