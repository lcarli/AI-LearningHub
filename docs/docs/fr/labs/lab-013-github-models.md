---
tags: [github-models, free, python, llm]
---
# Lab 013 : GitHub Models — Inférence LLM gratuite

<div class="lab-meta">
  <span><strong>Niveau :</strong> <span class="level-badge level-100">L100</span></span>
  <span><strong>Parcours :</strong> <a href="../paths/copilot/">🤖 GitHub Copilot</a> · <a href="../paths/rag/">📚 RAG</a></span>
  <span><strong>Durée :</strong> ~25 min</span>
  <span><strong>💰 Coût :</strong> <span class="level-badge cost-github">GitHub Free</span> — Compte GitHub gratuit, pas de carte bancaire</span>
</div>

## Ce que vous apprendrez

- Ce qu'est GitHub Models et quels modèles sont disponibles
- Comment utiliser le **playground** GitHub Models (navigateur, sans code)
- Comment appeler GitHub Models via l'**API REST** et le **SDK Python**
- Comment générer des **embeddings de texte** gratuitement (nécessaire pour les labs RAG)

---

## Introduction

**GitHub Models** vous donne un accès API gratuit aux LLM de pointe — GPT-4o, Llama, Phi, Mistral, et bien d'autres — en utilisant votre jeton d'accès personnel GitHub. Pas de compte Azure, pas de carte bancaire, pas d'inscription supplémentaire.

C'est le backend LLM utilisé dans tous les **labs L200** de ce hub.

---

## Configuration des prérequis

### 1. Créer un jeton d'accès personnel GitHub

1. Allez sur [github.com/settings/tokens](https://github.com/settings/tokens)
2. Cliquez sur **"Generate new token (classic)"**
3. Nom : `github-models-labs`
4. Expiration : 90 jours
5. Portées : aucune nécessaire (l'accès en lecture seule est suffisant pour l'API Models)
6. Cliquez sur **"Generate token"** — copiez et sauvegardez-le immédiatement

### 2. Stocker le jeton comme variable d'environnement

=== "Windows (PowerShell)"
    ```powershell
    $env:GITHUB_TOKEN = "ghp_your_token_here"
    ```

=== "macOS / Linux"
    ```bash
    export GITHUB_TOKEN="ghp_your_token_here"
    ```

=== "VS Code / Codespaces"
    Ajoutez dans votre fichier `.env` (ne commitez jamais ce fichier dans git !) :
    ```
    GITHUB_TOKEN=ghp_your_token_here
    ```

---

## 📦 Fichiers de support

!!! note "Téléchargez ces fichiers avant de commencer le lab"
    Enregistrez tous les fichiers dans un dossier `lab-013/` dans votre répertoire de travail.

| Fichier | Description | Téléchargement |
|---------|-------------|----------------|
| `requirements.txt` | Dépendances Python | [📥 Télécharger](https://github.com/lcarli/AI-LearningHub/raw/main/docs/docs/en/labs/lab-013/requirements.txt) |
| `starter.py` | Script de démarrage avec des TODOs | [📥 Télécharger](https://github.com/lcarli/AI-LearningHub/raw/main/docs/docs/en/labs/lab-013/starter.py) |

---

## Exercice du lab

### Étape 1 : Explorer le Playground

1. Allez sur [github.com/marketplace/models](https://github.com/marketplace/models)
2. Cliquez sur **"gpt-4o"**
3. Cliquez sur **"Playground"**
4. Tapez un message et appuyez sur Entrée

Vous discutez maintenant avec GPT-4o gratuitement, directement dans le navigateur.

Essayez différents modèles :
- `gpt-4o-mini` — plus rapide et moins cher
- `Phi-4` — le petit mais puissant modèle de Microsoft
- `Llama-3.3-70B-Instruct` — le modèle open-source de Meta

### Étape 2 : Effectuer votre premier appel API

=== "Python"

    Installez le SDK Python OpenAI (il est compatible avec GitHub Models) :
    ```bash
    pip install openai
    ```

    Créez `hello_models.py` :
    ```python
    import os
    from openai import OpenAI

    client = OpenAI(
        base_url="https://models.inference.ai.azure.com",
        api_key=os.environ["GITHUB_TOKEN"],
    )

    response = client.chat.completions.create(
        model="gpt-4o-mini",
        messages=[
            {"role": "system", "content": "You are a helpful assistant."},
            {"role": "user", "content": "What is the Model Context Protocol?"},
        ],
        max_tokens=500,
    )

    print(response.choices[0].message.content)
    ```

    Exécutez-le :
    ```bash
    python hello_models.py
    ```

=== "C#"

    Ajoutez le package NuGet :
    ```bash
    dotnet add package Azure.AI.Inference
    ```

    Créez `Program.cs` :
    ```csharp
    using Azure;
    using Azure.AI.Inference;

    var endpoint = new Uri("https://models.inference.ai.azure.com");
    var credential = new AzureKeyCredential(Environment.GetEnvironmentVariable("GITHUB_TOKEN")!);
    var client = new ChatCompletionsClient(endpoint, credential);

    var response = await client.CompleteAsync(new ChatCompletionsOptions
    {
        Model = "gpt-4o-mini",
        Messages =
        {
            new ChatRequestSystemMessage("You are a helpful assistant."),
            new ChatRequestUserMessage("What is the Model Context Protocol?"),
        },
        MaxTokens = 500,
    });

    Console.WriteLine(response.Value.Content);
    ```

=== "REST (curl)"

    ```bash
    curl https://models.inference.ai.azure.com/chat/completions \
      -H "Authorization: Bearer $GITHUB_TOKEN" \
      -H "Content-Type: application/json" \
      -d '{
        "model": "gpt-4o-mini",
        "messages": [
          {"role": "user", "content": "What is the Model Context Protocol?"}
        ]
      }'
    ```

### Étape 3 : Générer des embeddings de texte

Les embeddings sont l'ingrédient clé du RAG. Générons-en un :

=== "Python"

    ```python
    import os
    from openai import OpenAI

    client = OpenAI(
        base_url="https://models.inference.ai.azure.com",
        api_key=os.environ["GITHUB_TOKEN"],
    )

    response = client.embeddings.create(
        model="text-embedding-3-small",
        input="A waterproof outdoor camping tent",
    )

    vector = response.data[0].embedding
    print(f"Embedding dimensions: {len(vector)}")
    print(f"First 5 values: {vector[:5]}")
    ```

!!! info "Qu'est-ce qu'un embedding ?"
    Un embedding est une liste de nombres (un vecteur) qui représente la *signification* d'un morceau de texte.  
    Des textes similaires produisent des vecteurs proches dans l'espace vectoriel.  
    C'est ainsi que fonctionne la recherche sémantique : on compare le vecteur de la requête à tous les vecteurs de documents et on retourne les plus proches.

### Étape 4 : Modèles disponibles

Vérifiez quels modèles sont disponibles via l'API :

```python
import os
from openai import OpenAI

client = OpenAI(
    base_url="https://models.inference.ai.azure.com",
    api_key=os.environ["GITHUB_TOKEN"],
)

models = client.models.list()
for model in models.data:
    print(model.id)
```

---

## 📁 Fichiers de démarrage

Téléchargez le fichier de démarrage pour suivre le lab :

```bash
# From your cloned repo:
cd AI-LearningHub/docs/docs/en/labs/lab-013
pip install -r requirements.txt
python starter.py
```

Le [📥 `starter.py`](https://github.com/lcarli/AI-LearningHub/raw/main/docs/docs/en/labs/lab-013/starter.py) contient 4 exercices avec des commentaires `TODO`. Complétez chaque TODO pour construire un client GitHub Models fonctionnel.

---

## Limites de débit

GitHub Models est gratuit mais limité en débit :

| Niveau | Requêtes/min | Jetons/jour |
|--------|-------------|-------------|
| Free | ~15 | ~150 000 |
| Copilot Pro/Business | Plus élevé | Plus élevé |

Pour les besoins du lab, ces limites sont largement suffisantes. Si vous atteignez une limite, attendez 1 minute.

---

## Résumé

GitHub Models vous donne un **accès gratuit aux LLM de pointe** en utilisant simplement votre compte GitHub. Vous pouvez utiliser l'interface du playground dans le navigateur ou appeler l'API depuis Python/C#/REST. L'API est compatible OpenAI, donc tout code qui fonctionne avec OpenAI fonctionne aussi ici.

---

## Prochaines étapes

- **Construire un agent avec Semantic Kernel :** → [Lab 014 — SK Hello Agent](lab-014-sk-hello-agent.md)
- **Construire une application RAG :** → [Lab 022 — RAG avec GitHub Models + pgvector](lab-022-rag-github-models-pgvector.md)
