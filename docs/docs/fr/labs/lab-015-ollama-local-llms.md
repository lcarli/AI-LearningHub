---
tags: [ollama, local-llm, free, python]
---
# Lab 015 : Ollama — Exécutez des LLMs localement et gratuitement

<div class="lab-meta">
  <span><strong>Niveau :</strong> <span class="level-badge level-100">L100</span></span>
  <span><strong>Parcours :</strong> Tous les parcours</span>
  <span><strong>Durée :</strong> ~30 min</span>
  <span><strong>💰 Coût :</strong> <span class="level-badge cost-free">Gratuit</span> — S'exécute sur votre machine, pas de cloud, pas de clé API</span>
</div>

!!! tip "Essayez aussi Foundry Local"
    Microsoft **Foundry Local** est une alternative à Ollama avec une API compatible OpenAI. Consultez le **[Lab 078 : Foundry Local](lab-078-foundry-local.md)** pour un guide pratique.

## Ce que vous allez apprendre

- Installer et exécuter **Ollama** pour servir des LLMs localement
- Exécuter **Phi-4** (le puissant petit modèle de Microsoft) et **Llama 3.2** sur votre propre machine
- Générer des **embeddings de texte** localement avec `nomic-embed-text`
- Appeler Ollama depuis **Python** et **C#** en utilisant l'API compatible OpenAI
- Utiliser Ollama comme backend LLM pour **Semantic Kernel** (pas de clé API nécessaire)

---

## Introduction

**Ollama** est un outil open source qui permet d'exécuter des LLMs sur votre ordinateur portable aussi facilement que `ollama run phi4`. Pas de clé API, pas de compte cloud, pas de coûts d'utilisation — juste votre propre matériel.

Cela est utile pour :
- **Confidentialité** : les données sensibles ne quittent jamais votre machine
- **Développement hors ligne** : fonctionne sans internet
- **Contrôle des coûts** : zéro frais d'API pendant le développement
- **Apprentissage** : expérimentez librement sans vous soucier des factures

!!! info "Configuration matérielle requise"
    Ollama fonctionne sur Mac (Apple Silicon ou Intel), Windows et Linux.  
    Pour de meilleures performances : 16 Go+ de RAM. Fonctionne avec 8 Go mais plus lentement.  
    Le GPU est optionnel — les modèles fonctionnent aussi sur CPU (juste plus lentement).

---

## Configuration des prérequis

### Installer Ollama

1. Allez sur [ollama.com](https://ollama.com) et téléchargez l'installateur pour votre système d'exploitation
2. Installez et vérifiez :

```bash
ollama --version
# ollama version 0.5.x
```

Ollama s'exécute comme un service en arrière-plan sur `http://localhost:11434`.

---

!!! tip "Démarrage rapide avec GitHub Codespaces"
    [![Open in GitHub Codespaces](https://github.com/codespaces/badge.svg)](https://codespaces.new/lcarli/AI-LearningHub?quickstart=1)

    Toutes les dépendances sont pré-installées dans le devcontainer.


## 📦 Fichiers de support

!!! note "Téléchargez ces fichiers avant de commencer le lab"
    Enregistrez tous les fichiers dans un dossier `lab-015/` dans votre répertoire de travail.

| Fichier | Description | Téléchargement |
|---------|-------------|----------------|
| `Modelfile` | Configuration de modèle Ollama | [📥 Télécharger](https://github.com/lcarli/AI-LearningHub/raw/main/docs/docs/en/labs/lab-015/Modelfile) |
| `chat_starter.py` | Script de démarrage avec des TODOs | [📥 Télécharger](https://github.com/lcarli/AI-LearningHub/raw/main/docs/docs/en/labs/lab-015/chat_starter.py) |

---

## Exercice du lab

### Étape 1 : Exécuter votre premier modèle

```bash
ollama run phi4
```

Cela télécharge Phi-4 (~9 Go) lors de la première exécution, puis démarre un chat interactif.

```
>>> What are AI agents?
AI agents are autonomous systems that use LLMs as their reasoning engine...
>>> /bye
```

Autres modèles à essayer :

```bash
ollama run llama3.2        # Meta Llama 3.2 3B — rapide, petit
ollama run llama3.2:1b     # Encore plus petit, très rapide
ollama run mistral         # Mistral 7B — bon équilibre
ollama run deepseek-r1     # Modèle de raisonnement (comme o1)
ollama run phi4-mini       # Phi-4 Mini — plus rapide, moins de RAM
```

Vérifiez ce que vous avez installé :
```bash
ollama list
```

### Étape 2 : Télécharger un modèle d'embedding

```bash
ollama pull nomic-embed-text
```

Cela vous donne un modèle d'embedding local gratuit — parfait pour le RAG sans aucun coût d'API.

### Étape 3 : Appeler Ollama depuis Python

L'API d'Ollama est **100 % compatible OpenAI**, donc le même code qui appelle GitHub Models ou Azure OpenAI fonctionne ici :

```python
from openai import OpenAI

# Point to local Ollama instead of OpenAI
client = OpenAI(
    base_url="http://localhost:11434/v1",
    api_key="ollama",  # required by the client, but value doesn't matter
)

response = client.chat.completions.create(
    model="phi4",
    messages=[
        {"role": "system", "content": "You are a helpful assistant."},
        {"role": "user", "content": "Explain the difference between RAG and fine-tuning in 3 sentences."},
    ],
    temperature=0.3,
)

print(response.choices[0].message.content)
```

### Étape 4 : Générer des embeddings localement

```python
from openai import OpenAI

client = OpenAI(
    base_url="http://localhost:11434/v1",
    api_key="ollama",
)

response = client.embeddings.create(
    model="nomic-embed-text",
    input="waterproof hiking boots for mountain trails",
)

vector = response.data[0].embedding
print(f"Dimensions: {len(vector)}")   # 768
print(f"First 5:    {vector[:5]}")
```

### Étape 5 : Utiliser Ollama avec Semantic Kernel

Comme Ollama est compatible OpenAI, l'intégrer dans Semantic Kernel est trivial :

=== "Python"

    ```python
    import asyncio
    from semantic_kernel import Kernel
    from semantic_kernel.connectors.ai.open_ai import OpenAIChatCompletion

    async def main():
        kernel = Kernel()

        # Use Ollama instead of GitHub Models — just change base_url and model
        kernel.add_service(
            OpenAIChatCompletion(
                ai_model_id="phi4",
                api_key="ollama",
                base_url="http://localhost:11434/v1",
            )
        )

        # The rest of your agent code is identical!
        from semantic_kernel.contents import ChatHistory
        history = ChatHistory()
        history.add_system_message("You are a helpful AI assistant.")
        history.add_user_message("What is Semantic Kernel?")

        chat = kernel.get_service(type=OpenAIChatCompletion)
        result = await chat.get_chat_message_content(
            chat_history=history,
            settings=kernel.get_prompt_execution_settings_from_service_id("default"),
        )
        print(result)

    asyncio.run(main())
    ```

=== "C#"

    ```csharp
    using Microsoft.SemanticKernel;
    using Microsoft.SemanticKernel.ChatCompletion;

    var builder = Kernel.CreateBuilder();
    builder.AddOpenAIChatCompletion(
        modelId: "phi4",
        apiKey: "ollama",
        endpoint: new Uri("http://localhost:11434/v1")
    );
    var kernel = builder.Build();

    var chat = kernel.GetRequiredService<IChatCompletionService>();
    var history = new ChatHistory("You are a helpful AI assistant.");
    history.AddUserMessage("What is Semantic Kernel?");

    var response = await chat.GetChatMessageContentAsync(history);
    Console.WriteLine(response.Content);
    ```

### Étape 6 : Utiliser Ollama comme backend de serveur MCP

Comme Ollama est compatible OpenAI, tout serveur MCP qui appelle un LLM peut l'utiliser localement. Il suffit de changer la configuration du client :

```python
# In your MCP server's config.py
LLM_BASE_URL = "http://localhost:11434/v1"
LLM_MODEL = "phi4"
EMBED_MODEL = "nomic-embed-text"
LLM_API_KEY = "ollama"
```

Aucune autre modification de code nécessaire.

### Étape 7 : Ollama via l'API REST directement

Vous pouvez aussi appeler l'API native d'Ollama (non compatible OpenAI) :

```bash
curl http://localhost:11434/api/chat -d '{
  "model": "phi4",
  "messages": [
    {"role": "user", "content": "Why is the sky blue?"}
  ],
  "stream": false
}'
```

---

## 📁 Fichiers de démarrage

Deux fichiers sont fournis pour vous accompagner :

```bash

# Chat with any local model
python chat_starter.py

# Create the OutdoorGear custom model first:
ollama create outdoorgear -f Modelfile
ollama run outdoorgear
```

Le [📥 `Modelfile`](https://github.com/lcarli/AI-LearningHub/raw/main/docs/docs/en/labs/lab-015/Modelfile) crée un persona personnalisé **OutdoorGear Advisor** basé sur Phi-4. Le [📥 `chat_starter.py`](https://github.com/lcarli/AI-LearningHub/raw/main/docs/docs/en/labs/lab-015/chat_starter.py) contient 5 exercices couvrant la complétion de base, les modèles personnalisés, la comparaison et le streaming.

---

## Comparaison des modèles (sur un ordinateur portable typique)

| Modèle | Taille | RAM nécessaire | Vitesse | Qualité |
|--------|--------|----------------|---------|---------|
| `phi4-mini` | 2,5 Go | 4 Go | ⚡⚡⚡ Rapide | Bonne |
| `llama3.2:1b` | 1,3 Go | 4 Go | ⚡⚡⚡ Très rapide | Basique |
| `llama3.2` | 2,0 Go | 6 Go | ⚡⚡ Rapide | Bonne |
| `phi4` | 9,1 Go | 12 Go | ⚡ Modérée | Excellente |
| `mistral` | 4,1 Go | 8 Go | ⚡⚡ Rapide | Très bonne |
| `deepseek-r1` | 4,7 Go | 8 Go | ⚡ Modérée | Meilleur raisonnement |

---

## Résumé

Vous disposez maintenant d'une pile LLM entièrement locale :

- ✅ **Ollama** servant les modèles sur `localhost:11434`
- ✅ **Phi-4** (ou Llama) pour le chat/raisonnement — gratuit, privé, hors ligne
- ✅ **nomic-embed-text** pour les embeddings — gratuit, local
- ✅ Le même code fonctionne pour Ollama, GitHub Models et Azure OpenAI — il suffit de changer l'URL de base

---

## Prochaines étapes

- **Construire une application RAG avec des embeddings locaux :** → [Lab 022 — RAG avec GitHub Models + pgvector](lab-022-rag-github-models-pgvector.md)
- **Utiliser avec les plugins Semantic Kernel :** → [Lab 023 — Plugins, mémoire et planificateurs SK](lab-023-sk-plugins-memory.md)
- **IA locale en production :** → [Lab 044 — Phi-4 + Ollama en production](lab-044-phi4-ollama-production.md)
