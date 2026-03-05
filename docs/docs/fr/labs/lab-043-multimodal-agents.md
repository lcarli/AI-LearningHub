---
tags: [multimodal, gpt-4o, vision, python, github-models, L300]
---
# Lab 043: Multimodal Agents with GPT-4o Vision

<div class="lab-meta">
  <span><strong>Level:</strong> <span class="level-badge level-300">L300</span></span>
  <span><strong>Path:</strong> <a href="../paths/pro-code/">💻 Pro Code</a></span>
  <span><strong>Time:</strong> ~50 min</span>
  <span><strong>💰 Cost:</strong> <span class="level-badge cost-free">Free</span> — GitHub Models free tier supports GPT-4o vision</span>
</div>

!!! info "Traduction en cours"
    Ce lab est en cours de traduction. Le contenu ci-dessous est en anglais.



## What You'll Learn

- Send **images to GPT-4o** using the OpenAI vision API (base64 and URL methods)
- Build an agent that can **analyze product photos** and answer questions about them
- Combine **vision + tool calling**: the model sees an image and calls tools based on what it observes
- Handle **multi-image inputs** for product comparison
- Apply vision in real scenarios: product identification, damage assessment, size estimation

---

## Introduction

GPT-4o is natively multimodal — it processes text and images in a single model, not as a pipeline of separate models. This enables agents that can "see" what the user is looking at and respond with context.

**OutdoorGear use cases for vision:**
- Customer uploads a photo of a product → agent identifies it and retrieves specs
- Customer shows a damaged item → agent assesses damage and initiates return
- Customer asks "will this tent fit in this car?" with two photos → agent estimates
- Customer shares a trail photo → agent recommends gear for that terrain and weather

---

## Prerequisites

```bash
pip install openai requests Pillow
export GITHUB_TOKEN=<your PAT>
```

GPT-4o with vision is available on the GitHub Models free tier — no Azure subscription needed.

---

## Part 1: Basic Vision — Analyze a Product Photo

### Step 1: Send an image URL to GPT-4o

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

### Step 2: Send a local image (base64)

When customers upload images, you receive file bytes — send them base64-encoded:

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

## Part 2: Vision + Tool Calling

The real power of multimodal agents: the model sees an image, decides what tools to call, and takes action.

### Step 3: Product identification agent

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

## Part 3: Multi-Image Comparison

GPT-4o can analyze multiple images in one request:

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

## Part 4: Vision Best Practices

### Token optimization

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

### Image size guidelines

| Use case | Detail | Max image size |
|----------|--------|---------------|
| Product identification | `low` | Any (down-sampled automatically) |
| Damage assessment | `high` | 2048×2048px optimal |
| Text extraction (labels) | `high` | High resolution needed |
| General Q&A | `low` | Any |

### Safety and moderation

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

## 🧠 Knowledge Check

??? question "1. What is the difference between `detail: 'low'` and `detail: 'high'` in vision requests?"
    `detail: 'low'` resizes the image to 512×512 pixels and uses **~85 tokens** — fast and cheap, suitable for general product identification and scene understanding. `detail: 'high'` tiles the image into 512×512 chunks and processes each one with full detail, using **~1000+ tokens** — necessary for reading small text (labels, serial numbers), detecting fine damage, or analyzing intricate details. Always use `low` unless the task explicitly requires fine detail.

??? question "2. Why is combining vision with tool calling more powerful than vision alone?"
    Vision-only agents can describe what they see but cannot take action. Combining vision with tool calling means: the agent **sees** a damaged backpack → **calls** `lookup_product()` to identify it → **calls** `initiate_return()` to start the warranty process — all in one conversation turn. The agent becomes an active participant rather than just a narrator.

??? question "3. What is a key safety practice when deploying multimodal agents?"
    **Scope restriction via system prompt**: explicitly tell the model what types of images it should and should not process. Without this, users can send unrelated images (medical, personal, NSFW) and extract responses. A scoped system prompt like "Only analyze outdoor gear images — refuse anything else" significantly reduces misuse. Combine with content moderation APIs (Azure Content Safety) for production deployments.

---

## Summary

| Concept | Implementation |
|---------|---------------|
| **URL image input** | `"type": "image_url", "image_url": {"url": "..."}` |
| **Base64 image input** | `"url": "data:image/jpeg;base64,<encoded>"` |
| **Token control** | `"detail": "low"` (~85 tokens) or `"high"` (1000+) |
| **Vision + tools** | Same tool-calling loop as text agents |
| **Multi-image** | Multiple `image_url` blocks in one `content` array |

---

## Next Steps

- **Add streaming to vision responses:** → [Lab 019 — Streaming Responses](lab-019-streaming-responses.md)
- **Cost control for vision-heavy agents:** → [Lab 038 — AI Cost Optimization](lab-038-cost-optimization.md)
- **Evaluate multimodal agent quality:** → [Lab 035 — Agent Evaluation](lab-035-agent-evaluation.md)
