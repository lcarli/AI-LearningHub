---
tags: [semantic-kernel, free, python, github-models]
---
# Lab 014 : Semantic Kernel — Hello Agent

<div class="lab-meta">
  <span><strong>Niveau :</strong> <span class="level-badge level-100">L100</span></span>
  <span><strong>Parcours :</strong> <a href="../paths/semantic-kernel/">🧠 Semantic Kernel</a></span>
  <span><strong>Durée :</strong> ~30 min</span>
  <span><strong>💰 Coût :</strong> <span class="level-badge cost-github">GitHub Free</span> — Compte GitHub gratuit, pas de carte bancaire</span>
</div>

!!! warning "Semantic Kernel → Microsoft Agent Framework"
    Semantic Kernel fait désormais partie de **Microsoft Agent Framework (MAF)**, qui unifie SK et AutoGen en un seul framework. Les concepts de ce lab (Kernel, Plugins, appel de fonctions) s'appliquent toujours — MAF s'appuie dessus. Voir **[Lab 076 : Microsoft Agent Framework](lab-076-microsoft-agent-framework.md)** pour le guide de migration.

## Ce que vous apprendrez

- Ce qu'est Semantic Kernel (SK) et ses composants clés
- Comment créer un **Kernel** SK connecté à GitHub Models (gratuit)
- Comment ajouter votre premier **Plugin** (fonction native)
- Comment activer l'**appel automatique de fonctions** pour que le LLM décide quand utiliser votre fonction

---

## Introduction

**Semantic Kernel** est le SDK open-source de Microsoft pour construire des agents et des applications IA. Il se place entre votre code et le LLM, fournissant :

- Une abstraction unifiée sur n'importe quel LLM (OpenAI, Azure OpenAI, GitHub Models, Ollama...)
- Un **système de Plugins** pour définir des fonctions que le LLM peut appeler
- L'**appel automatique de fonctions** — le LLM invoque automatiquement vos fonctions quand c'est nécessaire
- Une **mémoire vectorielle** pour le contexte à long terme (abordé dans le Lab 023)

Dans ce lab, nous construisons un agent simple qui peut répondre à des questions **et** appeler une fonction personnalisée.

---

## 📁 Fichier de démarrage

Un fichier squelette de démarrage est fourni avec des commentaires `TODO` pour chaque étape :

```bash
# From your cloned repo:
cd AI-LearningHub/docs/docs/en/labs/lab-014
pip install -r requirements.txt
python hello_agent_starter.py
```

Complétez les TODOs dans l'ordre (1–16) pour construire un agent SK complet avec des fonctions sémantiques, des plugins natifs et une boucle de conversation.

---

## Configuration des prérequis

### Python
```bash
pip install semantic-kernel openai
```

### C#
```bash
dotnet new console -n HelloSkAgent
cd HelloSkAgent
dotnet add package Microsoft.SemanticKernel
```

Assurez-vous que `GITHUB_TOKEN` est défini (voir [Lab 013](lab-013-github-models.md#prerequisites-setup)).

---

!!! tip "Démarrage rapide avec GitHub Codespaces"
    [![Open in GitHub Codespaces](https://github.com/codespaces/badge.svg)](https://codespaces.new/lcarli/AI-LearningHub?quickstart=1)

    Toutes les dépendances sont pré-installées dans le devcontainer.


## 📦 Fichiers de support

!!! note "Téléchargez ces fichiers avant de commencer le lab"
    Enregistrez tous les fichiers dans un dossier `lab-014/` dans votre répertoire de travail.

| Fichier | Description | Téléchargement |
|---------|-------------|----------------|
| `hello_agent_starter.py` | Script de démarrage avec des TODOs | [📥 Télécharger](https://github.com/lcarli/AI-LearningHub/raw/main/docs/docs/en/labs/lab-014/hello_agent_starter.py) |
| `requirements.txt` | Dépendances Python | [📥 Télécharger](https://github.com/lcarli/AI-LearningHub/raw/main/docs/docs/en/labs/lab-014/requirements.txt) |

---

## Exercice du lab

### Étape 1 : Créer un Kernel de base

Le **Kernel** est l'objet central de Semantic Kernel — il contient votre connexion LLM et tous les plugins.

=== "Python"

    Créez `hello_agent.py` :

    ```python
    import asyncio
    import os
    from semantic_kernel import Kernel
    from semantic_kernel.connectors.ai.open_ai import OpenAIChatCompletion
    from semantic_kernel.connectors.ai.function_choice_behavior import FunctionChoiceBehavior
    from semantic_kernel.contents import ChatHistory

    async def main():
        # Create the kernel
        kernel = Kernel()

        # Add GitHub Models as the LLM backend
        kernel.add_service(
            OpenAIChatCompletion(
                ai_model_id="gpt-4o-mini",
                api_key=os.environ["GITHUB_TOKEN"],
                base_url="https://models.inference.ai.azure.com",
            )
        )

        # Simple chat — no tools yet
        history = ChatHistory()
        history.add_system_message("You are a helpful assistant.")
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

    Modifiez `Program.cs` :

    ```csharp
    using Microsoft.SemanticKernel;
    using Microsoft.SemanticKernel.ChatCompletion;
    using Microsoft.SemanticKernel.Connectors.OpenAI;

    var builder = Kernel.CreateBuilder();
    builder.AddOpenAIChatCompletion(
        modelId: "gpt-4o-mini",
        apiKey: Environment.GetEnvironmentVariable("GITHUB_TOKEN")!,
        endpoint: new Uri("https://models.inference.ai.azure.com")
    );
    var kernel = builder.Build();

    var chat = kernel.GetRequiredService<IChatCompletionService>();
    var history = new ChatHistory("You are a helpful assistant.");
    history.AddUserMessage("What is Semantic Kernel?");

    var response = await chat.GetChatMessageContentAsync(history);
    Console.WriteLine(response.Content);
    ```

Exécutez-le :

=== "Python"
    ```bash
    python hello_agent.py
    ```
=== "C#"
    ```bash
    dotnet run
    ```

Vous devriez voir le LLM répondre. Ajoutons maintenant une fonction personnalisée.

---

### Étape 2 : Ajouter un Plugin (fonction native)

Un **Plugin** est une classe avec des méthodes que le LLM peut appeler. Décorez-les avec `@kernel_function` (Python) ou `[KernelFunction]` (C#).

=== "Python"

    Ajoutez cette classe avant `main()` :

    ```python
    from semantic_kernel.functions import kernel_function

    class WeatherPlugin:
        """Provides current weather information."""

        @kernel_function(
            name="get_current_weather",
            description="Get the current weather for a city",
        )
        def get_current_weather(self, city: str) -> str:
            # In a real lab this would call a weather API
            # For now, return mock data
            weather_data = {
                "Seattle": "🌧️ Rainy, 12°C",
                "New York": "☀️ Sunny, 22°C",
                "London": "⛅ Cloudy, 15°C",
            }
            return weather_data.get(city, f"Weather data not available for {city}")
    ```

    Puis enregistrez le plugin dans `main()` :
    ```python
    kernel.add_plugin(WeatherPlugin(), plugin_name="weather")
    ```

=== "C#"

    Ajoutez cette classe à votre projet :

    ```csharp
    using Microsoft.SemanticKernel;

    public class WeatherPlugin
    {
        [KernelFunction("get_current_weather")]
        [Description("Get the current weather for a city")]
        public string GetCurrentWeather(string city)
        {
            var weatherData = new Dictionary<string, string>
            {
                ["Seattle"] = "🌧️ Rainy, 12°C",
                ["New York"] = "☀️ Sunny, 22°C",
                ["London"] = "⛅ Cloudy, 15°C",
            };
            return weatherData.TryGetValue(city, out var weather)
                ? weather
                : $"Weather data not available for {city}";
        }
    }
    ```

    Enregistrez dans `Program.cs` :
    ```csharp
    kernel.Plugins.AddFromType<WeatherPlugin>("weather");
    ```

---

### Étape 3 : Activer l'appel automatique de fonctions

Avec l'appel automatique de fonctions, le LLM **décide quand appeler votre fonction** en fonction de la conversation. Vous n'avez pas besoin de le déclencher manuellement.

=== "Python"

    Mettez à jour vos paramètres pour activer l'appel automatique de fonctions :

    ```python
    from semantic_kernel.connectors.ai.open_ai import OpenAIChatPromptExecutionSettings
    from semantic_kernel.connectors.ai.function_choice_behavior import FunctionChoiceBehavior

    settings = OpenAIChatPromptExecutionSettings(
        function_choice_behavior=FunctionChoiceBehavior.Auto(),
    )

    history = ChatHistory()
    history.add_system_message("You are a helpful assistant with access to weather data.")
    history.add_user_message("What's the weather like in Seattle today?")

    result = await chat.get_chat_message_content(
        chat_history=history,
        settings=settings,
        kernel=kernel,  # pass kernel so SK can call plugins
    )
    print(result)
    ```

=== "C#"

    ```csharp
    var settings = new OpenAIPromptExecutionSettings
    {
        FunctionChoiceBehavior = FunctionChoiceBehavior.Auto()
    };

    var history = new ChatHistory("You are a helpful assistant with access to weather data.");
    history.AddUserMessage("What's the weather like in Seattle today?");

    var response = await chat.GetChatMessageContentAsync(history, settings, kernel);
    Console.WriteLine(response.Content);
    ```

Exécutez-le et demandez : `"What's the weather like in Seattle today?"`

Le LLM va :
1. Voir que `get_current_weather` est disponible
2. L'appeler avec `city = "Seattle"`
3. Intégrer le résultat dans sa réponse

!!! success "Résultat attendu"
    "The current weather in Seattle is 🌧️ Rainy, 12°C. Bring an umbrella!"

---

### Étape 4 : Construire une boucle de conversation simple

Rendons-le interactif :

=== "Python"

    ```python
    history = ChatHistory()
    history.add_system_message(
        "You are a helpful assistant with access to weather data. "
        "Use the weather plugin when the user asks about weather."
    )

    print("Weather Agent ready. Type 'exit' to quit.\n")
    while True:
        user_input = input("You: ").strip()
        if user_input.lower() == "exit":
            break

        history.add_user_message(user_input)
        result = await chat.get_chat_message_content(
            chat_history=history,
            settings=settings,
            kernel=kernel,
        )
        history.add_assistant_message(str(result))
        print(f"Agent: {result}\n")
    ```

---

## Résumé

Vous avez construit votre premier **agent Semantic Kernel** qui :

- ✅ Se connecte à un LLM (GitHub Models — gratuit)
- ✅ Possède un **Plugin** personnalisé avec une fonction native
- ✅ Utilise l'**appel automatique de fonctions** — le LLM décide quand invoquer la fonction
- ✅ Maintient un **historique de conversation** entre les tours

---

## Prochaines étapes

- **Ajouter de la mémoire et plus de plugins :** → [Lab 023 — SK Plugins, Memory & Planners](lab-023-sk-plugins-memory.md)
- **Construire un serveur MCP et le connecter à SK :** → [Lab 020 — Serveur MCP en Python](lab-020-mcp-server-python.md)
