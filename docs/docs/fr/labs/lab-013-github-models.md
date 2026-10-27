---
tags: [modeles-locaux, foundry-local, ollama, gratuit, python, llm]
lab:
  id: '013'
  level: L100
  journey: llm-foundations
  time_min: 45
  cost:
    tier: free
    requires: []
    estimate_usd: 0 USD ; exécution sur le matériel local.
    simulation: false
    cleanup: false
  status: active
  last_verified: '2026-10-27'
  languages: [en, pt, fr]
---
# Lab 013 : Backends LLM Gratuits — Foundry Local et Ollama

<div class="lab-meta">
  <span><strong>Niveau :</strong> <span class="level-badge level-100">L100</span></span>
  <span><strong>Parcours :</strong> Fondamentaux des LLM</span>
  <span><strong>Durée :</strong> ~45 min</span>
  <span><strong>💰 Coût :</strong> <span class="level-badge cost-free">Gratuit</span> — exécution locale, sans compte ni carte bancaire</span>
</div>

!!! info "Pourquoi ce lab a changé"
    L'inférence GitHub Models a été retirée le 30 juillet 2026. Ce lab fournit maintenant le backend gratuit commun au hub : Foundry Local sur les appareils Windows compatibles ou Ollama sur Windows, macOS et Linux.

## Ce Que Vous Allez Apprendre

- Choisir entre Foundry Local et Ollama
- Démarrer un endpoint local compatible OpenAI
- Appeler un modèle de chat local avec Python
- Configurer les variables d'environnement utilisées par les autres labs
- Vérifier que les prompts et les données restent sur votre machine

## Choisissez un Runtime

=== "Foundry Local"
    Recommandé pour les appareils Windows compatibles et l'accélération DirectML.

    ```powershell
    winget install Microsoft.FoundryLocal
    foundry model run phi-4-mini
    $env:LOCAL_LLM_BASE_URL = "http://localhost:5273/v1"
    $env:LOCAL_LLM_MODEL = "phi-4-mini"
    ```

=== "Ollama"
    Option multiplateforme pour Windows, macOS et Linux.

    1. Installez [Ollama](https://ollama.com/download).
    2. Démarrez un petit modèle :

    ```bash
    ollama run phi4-mini
    ```

    Configurez l'endpoint :

    === "PowerShell"
        ```powershell
        $env:LOCAL_LLM_BASE_URL = "http://localhost:11434/v1"
        $env:LOCAL_LLM_MODEL = "phi4-mini"
        ```

    === "macOS / Linux"
        ```bash
        export LOCAL_LLM_BASE_URL="http://localhost:11434/v1"
        export LOCAL_LLM_MODEL="phi4-mini"
        ```

## Fichiers d'Accompagnement

| Fichier | Description | Téléchargement |
|---------|-------------|----------------|
| `requirements.txt` | Dépendance Python | [Télécharger](https://github.com/lcarli/AI-LearningHub/raw/main/docs/docs/en/labs/lab-013/requirements.txt) |
| `starter.py` | Exercices avec backend local | [Télécharger](https://github.com/lcarli/AI-LearningHub/raw/main/docs/docs/en/labs/lab-013/starter.py) |

## Exercice 1 — Vérifiez l'Endpoint

```bash
pip install -r requirements.txt
python starter.py
```

```python
import os
from openai import OpenAI

client = OpenAI(
    base_url=os.environ["LOCAL_LLM_BASE_URL"],
    api_key="local",
)

response = client.chat.completions.create(
    model=os.environ["LOCAL_LLM_MODEL"],
    messages=[{"role": "user", "content": "Expliquez MCP en deux phrases."}],
)
print(response.choices[0].message.content)
```

## Exercice 2 — Confirmez le Traitement Local

1. Déconnectez Internet après le téléchargement du modèle.
2. Exécutez de nouveau `python starter.py`.
3. Confirmez que la réponse fonctionne toujours.
4. Arrêtez le runtime et vérifiez que le script affiche une erreur de connexion au lieu de basculer silencieusement vers un service cloud.

## Configuration Commune

| Variable | Exemple | Objectif |
|----------|---------|----------|
| `LOCAL_LLM_BASE_URL` | `http://localhost:11434/v1` | Endpoint compatible OpenAI |
| `LOCAL_LLM_MODEL` | `phi4-mini` | Modèle de chat installé |
| `LOCAL_EMBEDDING_MODEL` | Spécifique au runtime | Modèle d'embeddings facultatif |

!!! warning "Les capacités varient selon le modèle"
    Tool calling, sorties structurées, embeddings et limites de contexte dépendent du modèle et du runtime. Chaque lab indique les capacités requises.

## Vérification des Connaissances

??? question "Pourquoi utiliser des variables d'environnement ?"
    Elles permettent d'utiliser le même code avec Foundry Local, Ollama ou un backend payant documenté.

??? question "Le SDK OpenAI envoie-t-il la requête à OpenAI ?"
    Non. Le SDK n'est que le client ; `base_url` définit la destination.

## Étapes Suivantes

- [Lab 015 — Ollama : LLM Locaux](lab-015-ollama-local-llms.md)
- [Lab 078 — Foundry Local](lab-078-foundry-local.md)
- [Lab 017 — Sorties Structurées](lab-017-structured-output.md)
