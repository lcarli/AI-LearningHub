---
tags: [azure, foundry, free, python, llm, azure-required]
---
# Lab 009 : Démarrage rapide avec Azure OpenAI Service

<div class="lab-meta">
  <span><strong>Niveau :</strong> <span class="level-badge level-100">L100</span></span>
  <span><strong>Parcours :</strong> <a href="../paths/foundry/">🏭 Microsoft Foundry</a></span>
  <span><strong>Durée :</strong> ~30 min</span>
  <span><strong>💰 Coût :</strong> <span class="level-badge cost-azure-free">Azure Free</span> — Compte Azure gratuit, utilisation minimale</span>
</div>

## Ce que vous apprendrez

- Ce qu'est Azure OpenAI Service et en quoi il diffère d'OpenAI et de GitHub Models
- Comment créer une ressource Azure OpenAI et déployer un modèle
- Comment appeler Azure OpenAI via le SDK Python et l'API REST
- L'authentification par clé API vs. Microsoft Entra ID (identité managée)
- Quand utiliser Azure OpenAI vs. GitHub Models vs. Ollama

---

## Introduction

**Azure OpenAI Service** fournit l'accès aux modèles d'OpenAI (GPT-4o, GPT-4o-mini, o1 et embeddings) via l'infrastructure Azure. Cela signifie :

- **Conformité entreprise** : Les données restent dans votre tenant Azure, régies par vos politiques
- **Réseau privé** : Déploiement derrière un VNet, sans exposition à Internet public
- **Intégrations Azure** : Fonctionne nativement avec Azure AI Search, Azure AI Foundry, Key Vault, et plus encore
- **SLA** : Garanties de disponibilité de niveau entreprise

!!! info "Azure OpenAI vs. GitHub Models vs. OpenAI"
    | | GitHub Models | OpenAI (direct) | Azure OpenAI |
    |--|--------------|-----------------|--------------|
    | **Coût** | Niveau gratuit | Paiement par token | Paiement par token |
    | **Authentification** | GitHub PAT | Clé API | Clé API ou identité managée |
    | **Résidence des données** | GitHub/Azure | OpenAI US | Votre région Azure |
    | **Fonctionnalités entreprise** | ❌ | Limitées | ✅ Complètes |
    | **Limites de débit** | Faibles (dev uniquement) | Standard | Configurables |
    | **Idéal pour** | Apprentissage, dev | Applications grand public | Production entreprise |

Pour tous les **labs L200+ de ce hub**, vous pouvez utiliser GitHub Models (gratuit). Azure OpenAI est le parcours recommandé pour passer en production.

---

## Configuration des prérequis

### Créer un compte Azure

→ [Compte Azure gratuit](https://azure.microsoft.com/free/) — 200 $ de crédit, 12 mois de services gratuits

!!! warning "Limitations du niveau gratuit"
    Azure OpenAI dans le niveau gratuit dispose d'un quota très limité. Pour ces exercices, quelques appels API suffisent.

### Demander l'accès à Azure OpenAI

Azure OpenAI nécessite une demande :
1. Rendez-vous sur [aka.ms/oai/access](https://aka.ms/oai/access)
2. Remplissez le formulaire avec votre cas d'utilisation
3. Attendez l'approbation (généralement quelques heures à 1 jour)

!!! tip "En attendant l'approbation"
    Complétez les sections conceptuelles de ce lab et utilisez [GitHub Models](lab-013-github-models.md) pour les exercices pratiques — le code est identique.

---

## Étape 1 : Créer une ressource Azure OpenAI

1. Dans le [Portail Azure](https://portal.azure.com), recherchez **Azure OpenAI**
2. Cliquez sur **+ Créer**
3. Remplissez :
   - **Abonnement** : votre abonnement
   - **Groupe de ressources** : créer nouveau → `rg-learning-hub`
   - **Région** : `East US 2` (meilleure disponibilité des modèles)
   - **Nom** : `aoai-learning-hub-[votrenom]` (doit être unique à l'échelle mondiale)
   - **Niveau tarifaire** : Standard S0
4. Cliquez sur **Vérifier + Créer** → **Créer**

---

## Étape 2 : Déployer un modèle

1. Ouvrez votre ressource Azure OpenAI
2. Cliquez sur **"Accéder à Azure OpenAI Studio"** → [oai.azure.com](https://oai.azure.com)
3. Cliquez sur **Déploiements** → **+ Créer un nouveau déploiement**
4. Configurez :
   - **Modèle** : `gpt-4o-mini`
   - **Nom du déploiement** : `gpt-4o-mini` (même nom que le modèle, plus facile à retenir)
   - **Tokens par minute** : 10K (suffisant pour les labs)
5. Cliquez sur **Déployer**

Déployez également un modèle d'embedding :
- **Modèle** : `text-embedding-3-small`
- **Nom du déploiement** : `text-embedding-3-small`

---

## Étape 3 : Obtenir votre point de terminaison et vos clés

Depuis votre ressource Azure OpenAI :
1. Cliquez sur **Clés et point de terminaison** dans le menu de gauche
2. Copiez la **CLÉ 1** et l'URL du **Point de terminaison**

Stockez-les comme variables d'environnement :

=== "Windows (PowerShell)"
    ```powershell
    $env:AZURE_OPENAI_API_KEY = "your_key_here"
    $env:AZURE_OPENAI_ENDPOINT = "https://your-resource.openai.azure.com/"
    $env:AZURE_OPENAI_DEPLOYMENT = "gpt-4o-mini"
    ```

=== "macOS / Linux"
    ```bash
    export AZURE_OPENAI_API_KEY="your_key_here"
    export AZURE_OPENAI_ENDPOINT="https://your-resource.openai.azure.com/"
    export AZURE_OPENAI_DEPLOYMENT="gpt-4o-mini"
    ```

!!! danger "Ne commitez jamais de clés API"
    Utilisez des variables d'environnement, Azure Key Vault ou des fichiers `.env` (ajoutez `.env` à `.gitignore`). Ne codez jamais de clés API en dur dans le code source.

---

## Étape 4 : Votre première complétion de chat

```bash
pip install openai
```

```python
import os
from openai import AzureOpenAI

# Azure OpenAI uses AzureOpenAI, not OpenAI
client = AzureOpenAI(
    api_key=os.environ["AZURE_OPENAI_API_KEY"],
    azure_endpoint=os.environ["AZURE_OPENAI_ENDPOINT"],
    api_version="2024-02-01",  # Check latest: aka.ms/oai/docs
)

response = client.chat.completions.create(
    model=os.environ["AZURE_OPENAI_DEPLOYMENT"],  # deployment name, not model name
    messages=[
        {"role": "system", "content": "You are an expert outdoor gear advisor."},
        {"role": "user", "content": "What's the best sleeping bag for winter camping at -10°C?"}
    ],
    max_tokens=300,
    temperature=0.7,
)

print(response.choices[0].message.content)
print(f"\nTokens used: {response.usage.total_tokens}")
```

!!! tip "Même API, client différent"
    Le code est identique à OpenAI — il suffit d'utiliser `AzureOpenAI` au lieu de `OpenAI`, d'ajouter `azure_endpoint` et `api_version`. C'est tout.

---

## Étape 5 : Embeddings avec Azure OpenAI

```python
import os
from openai import AzureOpenAI

client = AzureOpenAI(
    api_key=os.environ["AZURE_OPENAI_API_KEY"],
    azure_endpoint=os.environ["AZURE_OPENAI_ENDPOINT"],
    api_version="2024-02-01",
)

texts = [
    "waterproof hiking jacket",
    "rain-resistant outdoor coat",
    "dry sleeping bag liner",
]

response = client.embeddings.create(
    input=texts,
    model="text-embedding-3-small",  # your deployment name
)

for i, embedding in enumerate(response.data):
    print(f"'{texts[i]}': {len(embedding.embedding)} dimensions")
    print(f"  First 5 values: {embedding.embedding[:5]}")
```

---

## Étape 6 : Basculer entre les backends avec une seule variable

Ce pattern vous permet d'écrire le code une seule fois et de l'exécuter avec GitHub Models (gratuit) en développement et Azure OpenAI en production :

```python
import os
from openai import AzureOpenAI, OpenAI


def get_client():
    """Return the appropriate client based on environment."""
    backend = os.environ.get("LLM_BACKEND", "github")  # default to free

    if backend == "azure":
        return AzureOpenAI(
            api_key=os.environ["AZURE_OPENAI_API_KEY"],
            azure_endpoint=os.environ["AZURE_OPENAI_ENDPOINT"],
            api_version="2024-02-01",
        ), os.environ.get("AZURE_OPENAI_DEPLOYMENT", "gpt-4o-mini")
    else:
        # GitHub Models (free)
        return OpenAI(
            base_url="https://models.inference.ai.azure.com",
            api_key=os.environ["GITHUB_TOKEN"],
        ), "gpt-4o-mini"


client, model = get_client()

response = client.chat.completions.create(
    model=model,
    messages=[{"role": "user", "content": "Hello!"}]
)
print(response.choices[0].message.content)
```

Utilisation :
```bash
# Development (free):
LLM_BACKEND=github python app.py

# Production (Azure):
LLM_BACKEND=azure python app.py
```

---

## Étape 7 : Identité managée (bonne pratique de production)

En production, **n'utilisez jamais de clés API**. Utilisez plutôt l'identité managée :

```python
from azure.identity import DefaultAzureCredential, get_bearer_token_provider
from openai import AzureOpenAI

# Works in Azure App Service, Functions, Container Apps, AKS — anywhere with managed identity
token_provider = get_bearer_token_provider(
    DefaultAzureCredential(),
    "https://cognitiveservices.azure.com/.default"
)

client = AzureOpenAI(
    azure_endpoint=os.environ["AZURE_OPENAI_ENDPOINT"],
    azure_ad_token_provider=token_provider,
    api_version="2024-02-01",
)
# No api_key needed — credentials come from the managed identity
```

```bash
pip install azure-identity
```

Attribuez à votre application le rôle **Cognitive Services OpenAI User** dans Azure RBAC.

---

## Azure OpenAI dans Azure AI Foundry

Azure AI Foundry fournit un portail unifié pour gérer Azure OpenAI et d'autres services d'IA :

1. Rendez-vous sur [ai.azure.com](https://ai.azure.com)
2. Créez un **Hub** (une fois par organisation) et un **Projet** (une fois par application)
3. Déployez des modèles via le **Catalogue de modèles**
4. Utilisez le **Playground** pour tester de manière interactive
5. Accédez aux outils d'**Évaluation** et de **Surveillance**

→ Consultez le [Lab 030 — Foundry Agent Service + MCP](lab-030-foundry-agent-mcp.md) pour un guide complet de Foundry.

---

## 🧠 Vérification des connaissances

??? question "1. Quelle est la différence de code principale entre l'utilisation directe d'OpenAI et Azure OpenAI ?"
    Utilisez `AzureOpenAI` au lieu de `OpenAI`, et fournissez `azure_endpoint` et `api_version`. Le paramètre `model` prend le **nom de votre déploiement**, pas le nom du modèle. Tout le reste (messages, temperature, etc.) est identique.

??? question "2. Pourquoi devriez-vous utiliser l'identité managée plutôt que les clés API en production ?"
    Les clés API sont des secrets statiques qui peuvent être divulgués, volés ou accidentellement commitées dans le contrôle de source. L'identité managée utilise le système d'identité intégré d'Azure — aucun secret n'est jamais stocké dans le code ou les fichiers de configuration. L'accès est contrôlé via Azure RBAC, est automatiquement renouvelé et laisse des traces d'audit.

??? question "3. Quand choisiriez-vous GitHub Models plutôt qu'Azure OpenAI ?"
    **GitHub Models** est idéal pour le développement, l'apprentissage et le prototypage — c'est gratuit avec juste un compte GitHub, sans abonnement Azure nécessaire, sans déploiement à configurer. Choisissez **Azure OpenAI** quand vous avez besoin de : exigences de résidence des données, réseau privé, SLA entreprise, intégration avec Azure AI Search ou Foundry, ou fiabilité de niveau production.

---

## Résumé

| Concept | Point clé |
|---------|-----------|
| **Client AzureOpenAI** | Même API qu'OpenAI, juste des paramètres de constructeur différents |
| **Nom du déploiement** | Vous déployez un modèle avec un nom — utilisez ce nom, pas le nom du modèle |
| **Version de l'API** | Paramètre obligatoire — vérifiez la dernière version sur aka.ms/oai/docs |
| **Identité managée** | À utiliser en production — pas de secrets statiques |
| **Foundry** | Le portail qui englobe Azure OpenAI avec des outils d'évaluation, de surveillance et d'agents |

---

## Prochaines étapes

- **Construire un agent complet avec Foundry :** → [Lab 030 — Foundry Agent Service + MCP](lab-030-foundry-agent-mcp.md)
- **Ajouter le RAG à votre application Azure OpenAI :** → [Lab 031 — Recherche sémantique pgvector sur Azure](lab-031-pgvector-semantic-search.md)
- **Alternative gratuite pour les labs :** → [Lab 013 — GitHub Models](lab-013-github-models.md)
