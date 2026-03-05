# Lab 017: Saída Estruturada e Modo JSON

<div class="lab-meta">
  <span><strong>Nível:</strong> <span class="level-badge level-100">L100</span></span>
  <span><strong>Caminho:</strong> Todos os caminhos</span>
  <span><strong>Tempo:</strong> ~25 min</span>
  <span><strong>💰 Custo:</strong> <span class="level-badge cost-github">GitHub Free</span> — Conta gratuita do GitHub, sem cartão de crédito</span>
</div>

## O que Você Vai Aprender

- Por que a saída não estruturada de LLMs é frágil em sistemas de agentes
- Como usar o **modo JSON** para forçar uma saída JSON válida
- Como definir **schemas** com Pydantic (Python) e classes C#
- Como usar **saída estruturada** com a API do OpenAI
- Padrões práticos: extração, classificação, saída de funções

---

## Introdução

Em sistemas de agentes em produção, você raramente exibe o texto do LLM diretamente para os usuários. Você o analisa, armazena em bancos de dados, passa para outros serviços ou aciona ações com base nele.

O problema: LLMs são prolixos. Peça JSON e você pode receber:

```
Sure! Here's the JSON you asked for:
```json
{"name": "hiking boots", "price": 129.99}
```
I hope that helps!
```

Agora seu parser JSON quebra por causa do texto extra. Este é um problema real que a saída estruturada resolve completamente.

---

## Configuração dos Pré-requisitos

```bash
pip install openai pydantic
```

Configure `GITHUB_TOKEN` a partir do [Lab 013](lab-013-github-models.md).

---

## Exercício do Lab

### Etapa 1: O problema — analisar saída não estruturada

=== "Python"

    ```python
    import os, json
    from openai import OpenAI

    client = OpenAI(
        base_url="https://models.inference.ai.azure.com",
        api_key=os.environ["GITHUB_TOKEN"],
    )

    # BAD approach - asking for JSON in the prompt
    response = client.chat.completions.create(
        model="gpt-4o-mini",
        messages=[{
            "role": "user",
            "content": "Extract the product info as JSON: 'The ProTrek X200 hiking boots cost $189.99 and come in black.'"
        }],
    )

    text = response.choices[0].message.content
    print(text)  # May include "Sure! Here's the JSON: ```json ... ```"

    # This will often FAIL:
    try:
        data = json.loads(text)
    except json.JSONDecodeError:
        print("Parse failed! LLM added extra text.")
    ```

### Etapa 2: Modo JSON — JSON válido garantido

O modo JSON força o modelo a produzir apenas JSON válido, nada mais.

=== "Python"

    ```python
    response = client.chat.completions.create(
        model="gpt-4o-mini",
        response_format={"type": "json_object"},  # ← Habilitar modo JSON
        messages=[
            {
                "role": "system",
                "content": "You are a data extractor. Always respond with valid JSON only."
            },
            {
                "role": "user",
                "content": "Extract product info from: 'The ProTrek X200 hiking boots cost $189.99 and come in black.'"
            }
        ],
    )

    text = response.choices[0].message.content
    data = json.loads(text)  # Always succeeds now
    print(data)
    # {"name": "ProTrek X200", "type": "hiking boots", "price": 189.99, "colors": ["black"]}
    ```

!!! warning "Requisito do modo JSON"
    Ao usar o modo `json_object`, sua mensagem de sistema ou de usuário **deve** mencionar a palavra "JSON" — caso contrário, a API retorna um erro.

### Etapa 3: Saída estruturada com schema Pydantic

O modo JSON fornece JSON válido, mas não necessariamente o *formato* que você deseja. A **saída estruturada** com um schema impõe os campos e tipos exatos.

=== "Python"

    ```python
    from pydantic import BaseModel
    from openai import OpenAI
    import os

    client = OpenAI(
        base_url="https://models.inference.ai.azure.com",
        api_key=os.environ["GITHUB_TOKEN"],
    )

    # Define the schema
    class ProductInfo(BaseModel):
        name: str
        category: str
        price: float
        colors: list[str]
        in_stock: bool

    # Parse with structured output
    response = client.beta.chat.completions.parse(
        model="gpt-4o-mini",
        messages=[
            {"role": "system", "content": "Extract product information accurately."},
            {"role": "user", "content": "The ProTrek X200 hiking boots cost $189.99, come in black and brown, and are currently available."},
        ],
        response_format=ProductInfo,  # ← Pass the Pydantic model
    )

    product = response.choices[0].message.parsed  # Already a ProductInfo object!
    print(product.name)      # "ProTrek X200"
    print(product.price)     # 189.99
    print(product.colors)    # ["black", "brown"]
    print(product.in_stock)  # True
    ```

=== "C#"

    ```csharp
    using OpenAI.Chat;
    using System.Text.Json;

    // Define the schema as a C# class
    public class ProductInfo
    {
        public string Name { get; set; } = "";
        public string Category { get; set; } = "";
        public decimal Price { get; set; }
        public List<string> Colors { get; set; } = new();
        public bool InStock { get; set; }
    }

    // Use JSON mode + deserialize
    var client = new ChatClient(
        model: "gpt-4o-mini",
        apiKey: Environment.GetEnvironmentVariable("GITHUB_TOKEN"),
        options: new OpenAIClientOptions { Endpoint = new Uri("https://models.inference.ai.azure.com") }
    );

    var completion = await client.CompleteChatAsync(
        new SystemChatMessage("Extract product information. Respond with JSON only."),
        new UserChatMessage("The ProTrek X200 hiking boots cost $189.99, come in black and brown, and are available.")
    );

    var product = JsonSerializer.Deserialize<ProductInfo>(completion.Value.Content[0].Text);
    Console.WriteLine($"{product.Name}: ${product.Price}");
    ```

### Etapa 4: Padrões práticos

#### Padrão 1 — Classificação

```python
from pydantic import BaseModel
from typing import Literal

class SupportTicket(BaseModel):
    category: Literal["billing", "shipping", "returns", "technical", "other"]
    priority: Literal["low", "medium", "high", "urgent"]
    summary: str
    requires_human: bool

response = client.beta.chat.completions.parse(
    model="gpt-4o-mini",
    messages=[
        {"role": "system", "content": "Classify support tickets accurately."},
        {"role": "user", "content": "My order arrived broken and I need a replacement ASAP for my daughter's birthday tomorrow."},
    ],
    response_format=SupportTicket,
)

ticket = response.choices[0].message.parsed
print(f"Category: {ticket.category}")       # "shipping" ou "returns"
print(f"Priority: {ticket.priority}")       # "urgent"
print(f"Human needed: {ticket.requires_human}")  # True
```

#### Padrão 2 — Extração com objetos aninhados

```python
from pydantic import BaseModel

class Address(BaseModel):
    street: str
    city: str
    state: str
    zip_code: str

class OrderDetails(BaseModel):
    order_id: str
    customer_name: str
    shipping_address: Address
    items: list[str]
    total: float

# Extract structured data from unstructured text
text = """
Hi, I'm John Smith, order #ORD-2024-1234.
I ordered a tent and sleeping bag. Total was $289.98.
Ship to 123 Main St, Seattle, WA 98101.
"""
```

#### Padrão 3 — Saída de ferramenta de agente

Use saída estruturada para valores de retorno de ferramentas MCP para tornar a análise confiável:

```python
class SearchResult(BaseModel):
    products: list[dict]
    total_found: int
    has_more: bool
    suggested_query: str | None = None

@mcp.tool()
def search_products(query: str) -> dict:
    """Search the product catalog."""
    # ... do the search ...
    result = SearchResult(
        products=found_products,
        total_found=len(all_matches),
        has_more=len(all_matches) > 10,
    )
    return result.model_dump()  # Pydantic → dict → JSON
```

### Etapa 5: Temperature = 0 para tarefas estruturadas

Ao extrair dados estruturados, sempre use `temperature=0`:

```python
response = client.beta.chat.completions.parse(
    model="gpt-4o-mini",
    temperature=0,          # ← Determinístico para extração
    messages=[...],
    response_format=MySchema,
)
```

Extração é uma tarefa factual — você quer a mesma resposta todas as vezes, não uma variação criativa.

---

## Resumo

| Abordagem | Quando usar | Python |
|-----------|------------|--------|
| **Somente prompt** | Nunca para produção | ❌ Frágil |
| **Modo JSON** | JSON simples, sem schema rígido | `response_format={"type": "json_object"}` |
| **Saída estruturada** | Schema exato necessário | `response_format=MyPydanticModel` |

A regra de ouro: **qualquer saída de LLM que seu código vai analisar deve usar saída estruturada.**

---

## Próximos Passos

- **Use saída estruturada em uma ferramenta MCP:** → [Lab 020 — MCP Server in Python](lab-020-mcp-server-python.md)
- **Use com resultados de funções do Semantic Kernel:** → [Lab 023 — SK Plugins, Memory & Planners](lab-023-sk-plugins-memory.md)
