---
tags: [python, free, github-models, streaming]
---
# Lab 019 : Réponses en streaming dans les agents

<div class="lab-meta">
  <span><strong>Niveau :</strong> <span class="level-badge level-100">L100</span></span>
  <span><strong>Parcours :</strong> <a href="../paths/pro-code/">⚙️ Pro Code Agents</a></span>
  <span><strong>Durée :</strong> ~25 min</span>
  <span><strong>💰 Coût :</strong> <span class="level-badge cost-github">GitHub Free</span> — Compte GitHub gratuit, pas de carte bancaire</span>
</div>

## Ce que vous apprendrez

- Pourquoi le streaming est important pour l'expérience utilisateur des agents IA
- Comment utiliser `stream=True` avec le SDK Python OpenAI
- Comment gérer les appels d'outils en streaming (délicat — différent du streaming classique)
- Comment renvoyer des tokens en streaming depuis un endpoint FastAPI
- Comment streamer depuis Semantic Kernel

---

## Introduction

Sans streaming, les utilisateurs fixent un écran vide pendant 3 à 10 secondes pendant que le modèle génère une longue réponse. Avec le streaming, le texte apparaît **token par token** au fur et à mesure de la génération — exactement comme ChatGPT.

Pour les agents, le streaming est particulièrement important car les appels d'outils peuvent ajouter une latence significative. Afficher des résultats intermédiaires ("Recherche de produits... 3 résultats trouvés. Génération de la réponse...") rend l'attente beaucoup plus courte.

---

## Étape 1 : Streaming basique

```bash
pip install openai
export GITHUB_TOKEN=your_github_token
```

```python
import os
from openai import OpenAI

client = OpenAI(
    base_url="https://models.inference.ai.azure.com",
    api_key=os.environ["GITHUB_TOKEN"],
)

print("Streaming response:\n")

# stream=True returns a generator instead of a complete response
stream = client.chat.completions.create(
    model="gpt-4o-mini",
    messages=[
        {"role": "system", "content": "You are an outdoor gear advisor."},
        {"role": "user", "content": "Explain the three-layer clothing system for outdoor activities in detail."}
    ],
    stream=True,
)

# Iterate over chunks as they arrive
for chunk in stream:
    delta = chunk.choices[0].delta
    if delta.content:
        print(delta.content, end="", flush=True)

print("\n\n✅ Done!")
```

Le `flush=True` est essentiel — sans lui, Python met en mémoire tampon la sortie et vous perdez l'effet de streaming.

---

## Étape 2 : Collecter la réponse complète pendant le streaming

Parfois, vous souhaitez afficher la sortie en streaming ET disposer du texte complet pour un traitement ultérieur :

```python
full_response = []

stream = client.chat.completions.create(
    model="gpt-4o-mini",
    messages=[{"role": "user", "content": "List 5 essential items for day hiking."}],
    stream=True,
)

for chunk in stream:
    delta = chunk.choices[0].delta
    if delta.content:
        print(delta.content, end="", flush=True)
        full_response.append(delta.content)

full_text = "".join(full_response)
print(f"\n\nFull response ({len(full_text)} chars):\n{full_text}")
```

---

## Étape 3 : Streaming avec appels d'outils

Le streaming combiné aux appels d'outils nécessite un traitement attentif. L'appel d'outil est transmis sur plusieurs fragments :

```python
import json

def stream_with_tools(user_message: str, tools: list):
    """Stream a response that may include tool calls."""
    messages = [
        {"role": "system", "content": "You are an OutdoorGear advisor. Use tools when needed."},
        {"role": "user", "content": user_message}
    ]

    # Accumulators for the streaming tool call
    current_tool_calls = {}
    full_content = []

    stream = client.chat.completions.create(
        model="gpt-4o-mini",
        messages=messages,
        tools=tools,
        tool_choice="auto",
        stream=True,
    )

    finish_reason = None

    for chunk in stream:
        choice = chunk.choices[0]
        delta = choice.delta
        finish_reason = choice.finish_reason

        # Handle regular text content
        if delta.content:
            print(delta.content, end="", flush=True)
            full_content.append(delta.content)

        # Handle tool call chunks — they come piece by piece
        if delta.tool_calls:
            for tc in delta.tool_calls:
                idx = tc.index

                if idx not in current_tool_calls:
                    current_tool_calls[idx] = {
                        "id": tc.id or "",
                        "type": "function",
                        "function": {"name": "", "arguments": ""}
                    }

                if tc.id:
                    current_tool_calls[idx]["id"] = tc.id
                if tc.function.name:
                    current_tool_calls[idx]["function"]["name"] += tc.function.name
                if tc.function.arguments:
                    current_tool_calls[idx]["function"]["arguments"] += tc.function.arguments

    # After streaming, handle any tool calls
    if finish_reason == "tool_calls":
        print(f"\n  🔧 Tool calls requested: {len(current_tool_calls)}")
        for idx, tc in current_tool_calls.items():
            print(f"     → {tc['function']['name']}({tc['function']['arguments']})")
        # Execute tools and continue (same as non-streaming pattern from Lab 018)

    return "".join(full_content), current_tool_calls
```

!!! tip "Le streaming + les outils est complexe"
    La plupart du code en production utilise le mode non-streaming pour la phase d'appel d'outils et ne streame que la génération de la réponse finale. C'est plus simple et généralement suffisant.

---

## Étape 4 : Streaming dans un endpoint FastAPI

Voici le pattern pour les applications web réelles :

```python
# pip install fastapi uvicorn openai
from fastapi import FastAPI
from fastapi.responses import StreamingResponse
import os
from openai import OpenAI

app = FastAPI()
client = OpenAI(
    base_url="https://models.inference.ai.azure.com",
    api_key=os.environ["GITHUB_TOKEN"],
)


async def generate_stream(user_message: str):
    """Async generator that yields SSE-formatted chunks."""
    stream = client.chat.completions.create(
        model="gpt-4o-mini",
        messages=[
            {"role": "system", "content": "You are an outdoor gear advisor."},
            {"role": "user", "content": user_message}
        ],
        stream=True,
    )

    for chunk in stream:
        delta = chunk.choices[0].delta
        if delta.content:
            # Server-Sent Events format: data: <content>\n\n
            yield f"data: {delta.content}\n\n"

    yield "data: [DONE]\n\n"


@app.get("/stream")
async def stream_endpoint(question: str = "What gear do I need for a weekend hike?"):
    return StreamingResponse(
        generate_stream(question),
        media_type="text/event-stream",
        headers={"Cache-Control": "no-cache", "X-Accel-Buffering": "no"}
    )
```

Démarrez le serveur :
```bash
uvicorn main:app --reload
```

Testez avec curl :
```bash
curl "http://localhost:8000/stream?question=What+tent+is+best+for+winter+camping"
```

Ou consommez en JavaScript (navigateur) :
```javascript
const source = new EventSource('/stream?question=What+boots+for+hiking%3F');
source.onmessage = (event) => {
    if (event.data === '[DONE]') { source.close(); return; }
    document.getElementById('response').innerText += event.data;
};
```

---

## Étape 5 : Streaming dans Semantic Kernel

```python
import asyncio
import os
from semantic_kernel import Kernel
from semantic_kernel.connectors.ai.open_ai import OpenAIChatCompletion
from semantic_kernel.contents import ChatHistory

async def stream_sk_response():
    kernel = Kernel()
    kernel.add_service(
        OpenAIChatCompletion(
            ai_model_id="gpt-4o-mini",
            api_key=os.environ["GITHUB_TOKEN"],
            base_url="https://models.inference.ai.azure.com",
        )
    )

    chat = kernel.get_service(type=OpenAIChatCompletion)
    history = ChatHistory()
    history.add_system_message("You are a friendly outdoor gear advisor.")
    history.add_user_message("What are the key features to look for in a hiking backpack?")

    print("Streaming SK response:\n")

    # SK streaming uses get_streaming_chat_message_content
    async for chunk in chat.get_streaming_chat_message_content(
        chat_history=history,
        settings=None,
        kernel=kernel,
    ):
        if chunk.content:
            print(chunk.content, end="", flush=True)

    print("\n")


asyncio.run(stream_sk_response())
```

---

## Étape 6 : Afficher la progression pendant les appels d'outils

Pour une meilleure expérience utilisateur, montrez aux utilisateurs ce qui se passe pendant l'exécution des outils :

```python
import time

def run_agent_with_progress(user_message: str) -> str:
    messages = [
        {"role": "system", "content": "You are an OutdoorGear advisor. Use tools to answer accurately."},
        {"role": "user", "content": user_message}
    ]

    step = 0
    while True:
        step += 1
        response = client.chat.completions.create(
            model="gpt-4o-mini",
            messages=messages,
            tools=TOOLS,  # from Lab 018
            tool_choice="auto",
        )

        message = response.choices[0].message
        messages.append(message)

        if response.choices[0].finish_reason == "tool_calls":
            for tc in message.tool_calls:
                # Show progress to user
                print(f"  ⏳ Looking up: {tc.function.name}...", end="", flush=True)
                
                # Execute tool
                args = json.loads(tc.function.arguments)
                result = TOOL_FUNCTIONS[tc.function.name](**args)
                
                print(f" ✅")  # Done
                
                messages.append({
                    "role": "tool",
                    "tool_call_id": tc.id,
                    "content": json.dumps(result),
                })
        else:
            # Stream the final answer
            print("\n")
            stream = client.chat.completions.create(
                model="gpt-4o-mini",
                messages=messages,
                stream=True,
            )
            result_text = []
            for chunk in stream:
                if chunk.choices[0].delta.content:
                    content = chunk.choices[0].delta.content
                    print(content, end="", flush=True)
                    result_text.append(content)
            print("\n")
            return "".join(result_text)
```

Ce pattern est utilisé dans les agents en production : les appels d'outils s'exécutent sans streaming (pour un code plus simple), et seule la réponse finale du LLM est streamée.

---

## 🧠 Vérification des connaissances

??? question "1. Pourquoi flush=True est-il important lors de l'affichage des tokens en streaming ?"
    Python met en mémoire tampon stdout par défaut. Sans `flush=True`, le texte s'accumule dans le tampon et s'affiche d'un seul coup à la fin — ce qui annule l'intérêt du streaming. `flush=True` force l'écriture immédiate du tampon à chaque appel `print()`.

??? question "2. Pourquoi le streaming avec appels d'outils nécessite-t-il un code plus complexe que le streaming basique ?"
    Les données d'appel d'outil arrivent **sur plusieurs fragments** — chaque fragment contient une petite partie du nom de la fonction, de l'identifiant et des arguments. Vous devez accumuler ces morceaux et reconstruire l'objet d'appel d'outil complet avant de pouvoir l'exécuter. Le streaming de texte classique est plus simple car chaque fragment est déjà du texte complet que vous pouvez afficher immédiatement.

??? question "3. Qu'est-ce que les Server-Sent Events (SSE) et pourquoi sont-ils utilisés pour le streaming IA dans les applications web ?"
    SSE est un standard web où le serveur envoie un flux d'événements via une seule connexion HTTP, formaté comme `data: <contenu>\n\n`. C'est plus simple que les WebSockets pour le streaming unidirectionnel serveur→client. Les navigateurs disposent d'un support natif via l'API `EventSource`, et cela fonctionne mieux à travers les proxys et les répartiteurs de charge que les WebSockets. La plupart des interfaces de chat IA (ChatGPT, Copilot) utilisent SSE pour les réponses en streaming.

---

## Résumé

| Approche | Quand l'utiliser |
|----------|-----------------|
| `stream=True` basique | Outils en ligne de commande, scripts simples |
| Collecter pendant le streaming | Besoin du streaming UX + texte complet pour le traitement |
| FastAPI + SSE | Applications web, interfaces de chat |
| SK `get_streaming_...` | Agents SK en production |
| Messages de progression | Quand les appels d'outils ajoutent une latence significative |

---

## Prochaines étapes

- **Approfondissement des appels d'outils :** → [Lab 018 — Appel de fonctions et utilisation d'outils](lab-018-function-calling.md)
- **Construire une interface web pour votre agent :** → [Lab 041 — Extension GitHub Copilot personnalisée](lab-041-copilot-extension.md)
- **Streaming en production avec Foundry :** → [Lab 030 — Foundry Agent Service](lab-030-foundry-agent-mcp.md)
