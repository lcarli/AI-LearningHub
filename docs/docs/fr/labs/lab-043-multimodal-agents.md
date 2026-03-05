---
tags: [multimodal, gpt-4o, vision, python, github-models, L300]
---
# Lab 043 : Agents multimodaux avec GPT-4o Vision

<div class="lab-meta">
  <span><strong>Niveau :</strong> <span class="level-badge level-300">L300</span></span>
  <span><strong>Parcours :</strong> <a href="../paths/pro-code/">💻 Pro Code</a></span>
  <span><strong>Durée :</strong> ~50 min</span>
  <span><strong>💰 Coût :</strong> <span class="level-badge cost-free">Gratuit</span> — Le niveau gratuit de GitHub Models prend en charge GPT-4o vision</span>
</div>

## Ce que vous apprendrez

- Envoyer des **images à GPT-4o** en utilisant l'API vision d'OpenAI (méthodes base64 et URL)
- Construire un agent capable d'**analyser des photos de produits** et de répondre à des questions à leur sujet
- Combiner **vision + appel d'outils** : le modèle voit une image et appelle des outils en fonction de ce qu'il observe
- Gérer les **entrées multi-images** pour la comparaison de produits
- Appliquer la vision dans des scénarios réels : identification de produits, évaluation des dommages, estimation de taille

---

## Introduction

GPT-4o est nativement multimodal — il traite le texte et les images dans un seul modèle, et non comme un pipeline de modèles séparés. Cela permet aux agents de « voir » ce que l'utilisateur regarde et de répondre avec du contexte.

**Cas d'utilisation d'OutdoorGear pour la vision :**
- Un client télécharge une photo d'un produit → l'agent l'identifie et récupère les spécifications
- Un client montre un article endommagé → l'agent évalue les dommages et initie un retour
- Un client demande « est-ce que cette tente rentrera dans cette voiture ? » avec deux photos → l'agent estime
- Un client partage une photo de sentier → l'agent recommande de l'équipement pour ce terrain et cette météo

---

## Prérequis

```bash
pip install openai requests Pillow
export GITHUB_TOKEN=<your PAT>
```

GPT-4o avec vision est disponible sur le niveau gratuit de GitHub Models — aucun abonnement Azure n'est nécessaire.

---

## Partie 1 : Vision de base — Analyser une photo de produit

### Étape 1 : Envoyer une URL d'image à GPT-4o

```python
# vision_basics.py
import os
from openai import OpenAI

client = OpenAI(
    base_url="https://models.inference.ai.azure.com",
    api_key=os.environ["GITHUB_TOKEN"],
)

# We'll use a public photo of a tent for demo purposes
# In production, customers upload their own images
TENT_IMAGE_URL = "https://upload.wikimedia.org/wikipedia/commons/thumb/8/8e/Tent_at_sunset.jpg/320px-Tent_at_sunset.jpg"

response = client.chat.completions.create(
    model="gpt-4o",
    messages=[
        {
            "role": "user",
            "content": [
                {
                    "type": "image_url",
                    "image_url": {"url": TENT_IMAGE_URL},
                },
                {
                    "type": "text",
                    "text": "This is an OutdoorGear customer photo. "
                            "Describe the tent in this image: type, approximate size, condition, "
                            "and whether it appears to be a 3-season or 4-season design.",
                },
            ],
        }
    ],
    max_tokens=300,
)

print("=== Vision Analysis ===")
print(response.choices[0].message.content)
```

### Étape 2 : Envoyer une image locale (base64)

Lorsque les clients téléchargent des images, vous recevez des octets de fichier — envoyez-les encodés en base64 :

```python
# vision_local_image.py
import base64
import os
from openai import OpenAI

def encode_image(image_path: str) -> str:
    """Encode a local image file to base64 string."""
    with open(image_path, "rb") as f:
        return base64.b64encode(f.read()).decode("utf-8")

def analyze_product_image(image_path: str, question: str) -> str:
    """Ask GPT-4o a question about a local image file."""
    client = OpenAI(
        base_url="https://models.inference.ai.azure.com",
        api_key=os.environ["GITHUB_TOKEN"],
    )

    b64_image = encode_image(image_path)

    response = client.chat.completions.create(
        model="gpt-4o",
        messages=[
            {
                "role": "system",
                "content": "You are an OutdoorGear product expert. "
                           "Analyze customer-submitted product photos and provide helpful, accurate assessments.",
            },
            {
                "role": "user",
                "content": [
                    {
                        "type": "image_url",
                        "image_url": {
                            "url": f"data:image/jpeg;base64,{b64_image}",
                            "detail": "low",    # "low" saves tokens; "high" for detailed analysis
                        },
                    },
                    {"type": "text", "text": question},
                ],
            },
        ],
        max_tokens=400,
    )
    return response.choices[0].message.content

# Usage (provide your own image):
# result = analyze_product_image("my_tent.jpg", "Is this tent suitable for winter camping?")
# print(result)
```

---

## Partie 2 : Vision + appel d'outils

La véritable puissance des agents multimodaux : le modèle voit une image, décide quels outils appeler, et passe à l'action.

### Étape 3 : Agent d'identification de produits

```python
# vision_agent.py
import os
import json
from openai import OpenAI

client = OpenAI(
    base_url="https://models.inference.ai.azure.com",
    api_key=os.environ["GITHUB_TOKEN"],
)

# Tools the agent can call after seeing an image
TOOLS = [
    {
        "type": "function",
        "function": {
            "name": "lookup_product",
            "description": "Look up product details by name or description. "
                           "Use after identifying a product in an image.",
            "parameters": {
                "type": "object",
                "properties": {
                    "product_name": {
                        "type": "string",
                        "description": "Product name or description to look up (e.g. 'TrailBlazer Tent 2P')",
                    }
                },
                "required": ["product_name"],
            },
        },
    },
    {
        "type": "function",
        "function": {
            "name": "initiate_return",
            "description": "Initiate a product return/warranty claim. "
                           "Use when an image shows damage or defects.",
            "parameters": {
                "type": "object",
                "properties": {
                    "product_id":    {"type": "string"},
                    "damage_type":   {"type": "string", "description": "Description of the observed damage"},
                    "severity":      {"type": "string", "enum": ["minor", "moderate", "severe"]},
                },
                "required": ["product_id", "damage_type", "severity"],
            },
        },
    },
]

PRODUCTS_DB = {
    "trailblazer tent": {"id": "P001", "name": "TrailBlazer Tent 2P", "price": 249.99, "warranty": "lifetime"},
    "summit dome":      {"id": "P002", "name": "Summit Dome 4P",       "price": 549.99, "warranty": "lifetime"},
    "trailblazer solo": {"id": "P003", "name": "TrailBlazer Solo",     "price": 299.99, "warranty": "lifetime"},
    "arcticdown":       {"id": "P004", "name": "ArcticDown Bag",       "price": 389.99, "warranty": "5 years"},
}

def execute_tool(name: str, args: dict) -> str:
    if name == "lookup_product":
        query = args["product_name"].lower()
        for key, product in PRODUCTS_DB.items():
            if key in query or query in key:
                return json.dumps(product)
        return json.dumps({"error": f"Product '{args['product_name']}' not found in catalog"})

    elif name == "initiate_return":
        return json.dumps({
            "return_id": "RTN-2025-00042",
            "status": "initiated",
            "product_id": args["product_id"],
            "damage_type": args["damage_type"],
            "severity": args["severity"],
            "next_steps": "Ship the item to our returns center. Label included via email.",
        })
    return json.dumps({"error": "Unknown tool"})


def vision_agent(image_url: str, user_message: str) -> str:
    """Run a multimodal agent that sees an image and calls tools."""
    messages = [
        {
            "role": "system",
            "content": "You are an OutdoorGear customer service agent. "
                       "When a customer shares a product image: identify the product, "
                       "then use tools to look it up or handle warranty claims.",
        },
        {
            "role": "user",
            "content": [
                {"type": "image_url", "image_url": {"url": image_url}},
                {"type": "text", "text": user_message},
            ],
        },
    ]

    # Agent loop: keep running until no more tool calls
    while True:
        response = client.chat.completions.create(
            model="gpt-4o",
            messages=messages,
            tools=TOOLS,
            max_tokens=500,
        )

        assistant_msg = response.choices[0].message
        messages.append(assistant_msg)

        if not assistant_msg.tool_calls:
            return assistant_msg.content   # Done!

        # Execute tool calls
        for tool_call in assistant_msg.tool_calls:
            result = execute_tool(
                tool_call.function.name,
                json.loads(tool_call.function.arguments)
            )
            messages.append({
                "role": "tool",
                "tool_call_id": tool_call.id,
                "content": result,
            })


# Demo: Customer submits a photo and asks for product info
TENT_URL = "https://upload.wikimedia.org/wikipedia/commons/thumb/8/8e/Tent_at_sunset.jpg/320px-Tent_at_sunset.jpg"

print("=== Vision + Tool Calling Agent ===")
answer = vision_agent(
    image_url=TENT_URL,
    user_message="This is my tent from OutdoorGear. Can you tell me its warranty status?",
)
print(answer)
```

---

## Partie 3 : Comparaison multi-images

GPT-4o peut analyser plusieurs images en une seule requête :

```python
# multi_image.py
import os
from openai import OpenAI

client = OpenAI(
    base_url="https://models.inference.ai.azure.com",
    api_key=os.environ["GITHUB_TOKEN"],
)

def compare_images(image_urls: list[str], comparison_question: str) -> str:
    """Compare multiple images in a single GPT-4o call."""
    content = []
    for i, url in enumerate(image_urls, 1):
        content.append({"type": "text", "text": f"Image {i}:"})
        content.append({"type": "image_url", "image_url": {"url": url}})

    content.append({"type": "text", "text": comparison_question})

    response = client.chat.completions.create(
        model="gpt-4o",
        messages=[
            {"role": "system", "content": "You are an OutdoorGear product expert."},
            {"role": "user", "content": content},
        ],
        max_tokens=500,
    )
    return response.choices[0].message.content


# Demo: Compare two tents for suitability
TENT_1 = "https://upload.wikimedia.org/wikipedia/commons/thumb/8/8e/Tent_at_sunset.jpg/320px-Tent_at_sunset.jpg"
TENT_2 = "https://upload.wikimedia.org/wikipedia/commons/thumb/1/17/Bivouac_tent.jpg/320px-Bivouac_tent.jpg"

result = compare_images(
    [TENT_1, TENT_2],
    "Comparing these two tents: which appears more suitable for winter camping, "
    "and which is lighter/smaller for backpacking? Explain your reasoning.",
)
print("=== Multi-Image Comparison ===")
print(result)
```

---

## Partie 4 : Bonnes pratiques pour la vision

### Optimisation des tokens

```python
# Vision input token costs:
# "low" detail:  ~85 tokens per image   → use for product identification
# "high" detail: ~1000+ tokens per image → use for damage assessment, fine details

# Always specify detail level:
{
    "type": "image_url",
    "image_url": {
        "url": url,
        "detail": "low"   # or "high" — choose based on task
    }
}
```

### Recommandations de taille d'image

| Cas d'utilisation | Détail | Taille d'image maximale |
|----------|--------|---------------|
| Identification de produit | `low` | Toute taille (redimensionnée automatiquement) |
| Évaluation des dommages | `high` | 2048×2048px optimal |
| Extraction de texte (étiquettes) | `high` | Haute résolution nécessaire |
| Q&R général | `low` | Toute taille |

### Sécurité et modération

```python
def safe_vision_request(image_url: str, user_question: str) -> str:
    """Wraps the vision request with a system prompt that limits scope."""
    # Always constrain vision agents to their domain
    # Prevents misuse (e.g., asking about medical conditions in photos)
    system = (
        "You are an OutdoorGear product assistant. "
        "You ONLY analyze outdoor equipment and gear in images. "
        "If the image does not contain outdoor gear, respond: "
        "'I can only help with OutdoorGear products. This image doesn't appear to show outdoor equipment.'"
    )
    # ... rest of request
```

---

## 🧠 Quiz de connaissances

??? question "1. Quelle est la différence entre `detail: 'low'` et `detail: 'high'` dans les requêtes vision ?"
    `detail: 'low'` redimensionne l'image à 512×512 pixels et utilise **~85 tokens** — rapide et économique, adapté à l'identification générale de produits et à la compréhension de scènes. `detail: 'high'` découpe l'image en tuiles de 512×512 et traite chacune avec tous les détails, utilisant **~1000+ tokens** — nécessaire pour lire du texte petit (étiquettes, numéros de série), détecter des dommages fins ou analyser des détails complexes. Utilisez toujours `low` sauf si la tâche nécessite explicitement des détails fins.

??? question "2. Pourquoi combiner la vision avec l'appel d'outils est-il plus puissant que la vision seule ?"
    Les agents avec vision uniquement peuvent décrire ce qu'ils voient mais ne peuvent pas agir. Combiner la vision avec l'appel d'outils signifie : l'agent **voit** un sac à dos endommagé → **appelle** `lookup_product()` pour l'identifier → **appelle** `initiate_return()` pour démarrer le processus de garantie — le tout en un seul tour de conversation. L'agent devient un participant actif plutôt qu'un simple narrateur.

??? question "3. Quelle est une pratique de sécurité clé lors du déploiement d'agents multimodaux ?"
    **Restriction du périmètre via le prompt système** : indiquez explicitement au modèle quels types d'images il doit et ne doit pas traiter. Sans cela, les utilisateurs peuvent envoyer des images non pertinentes (médicales, personnelles, NSFW) et obtenir des réponses. Un prompt système ciblé comme « N'analysez que les images d'équipement outdoor — refusez tout le reste » réduit considérablement les abus. Combinez avec des API de modération de contenu (Azure Content Safety) pour les déploiements en production.

---

## Résumé

| Concept | Implémentation |
|---------|---------------|
| **Entrée image par URL** | `"type": "image_url", "image_url": {"url": "..."}` |
| **Entrée image en base64** | `"url": "data:image/jpeg;base64,<encoded>"` |
| **Contrôle des tokens** | `"detail": "low"` (~85 tokens) ou `"high"` (1000+) |
| **Vision + outils** | Même boucle d'appel d'outils que les agents texte |
| **Multi-images** | Plusieurs blocs `image_url` dans un seul tableau `content` |

---

## Prochaines étapes

- **Ajouter le streaming aux réponses vision :** → [Lab 019 — Réponses en streaming](lab-019-streaming-responses.md)
- **Contrôle des coûts pour les agents intensifs en vision :** → [Lab 038 — Optimisation des coûts IA](lab-038-cost-optimization.md)
- **Évaluer la qualité des agents multimodaux :** → [Lab 035 — Évaluation des agents](lab-035-agent-evaluation.md)
