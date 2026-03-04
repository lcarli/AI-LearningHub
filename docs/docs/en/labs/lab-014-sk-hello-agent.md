---
tags: [semantic-kernel, free, python, github-models]
---
# Lab 014: Semantic Kernel — Hello Agent

<div class="lab-meta">
  <span><strong>Level:</strong> <span class="level-badge level-100">L100</span></span>
  <span><strong>Path:</strong> <a href="../paths/semantic-kernel/">🧠 Semantic Kernel</a></span>
  <span><strong>Time:</strong> ~30 min</span>
  <span><strong>💰 Cost:</strong> <span class="level-badge cost-github">GitHub Free</span> — Free GitHub account, no credit card</span>
</div>

## What You'll Learn

- What Semantic Kernel (SK) is and its key building blocks
- How to create an SK **Kernel** connected to GitHub Models (free)
- How to add your first **Plugin** (native function)
- How to enable **auto function calling** so the LLM decides when to use your function

---

## Introduction

**Semantic Kernel** is Microsoft's open-source SDK for building AI agents and applications. It sits between your code and the LLM, providing:

- A unified abstraction over any LLM (OpenAI, Azure OpenAI, GitHub Models, Ollama...)
- A **Plugin system** for defining functions the LLM can call
- **Auto function calling** — the LLM automatically invokes your functions when needed
- **Vector memory** for long-term context (covered in Lab 023)

In this lab, we build a simple agent that can answer questions **and** call a custom function.

---

## 📁 Starter File

A skeleton starter file is provided with `TODO` comments for each step:

```bash
# From your cloned repo:
cd AI-LearningHub/docs/docs/en/labs/lab-014
pip install -r requirements.txt
python hello_agent_starter.py
```

Complete the TODOs in order (1–16) to build a full SK agent with semantic functions, native plugins, and a chat loop.

---

## Prerequisites Setup

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

Make sure `GITHUB_TOKEN` is set (see [Lab 013](lab-013-github-models.md#prerequisites-setup)).

---

## Lab Exercise

### Step 1: Create a basic Kernel

The **Kernel** is the central object in Semantic Kernel — it holds your LLM connection and all plugins.

=== "Python"

    Create `hello_agent.py`:

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

    Edit `Program.cs`:

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

Run it:

=== "Python"
    ```bash
    python hello_agent.py
    ```
=== "C#"
    ```bash
    dotnet run
    ```

You should see the LLM respond. Now let's add a custom function.

---

### Step 2: Add a Plugin (native function)

A **Plugin** is a class with methods the LLM can call. Decorate them with `@kernel_function` (Python) or `[KernelFunction]` (C#).

=== "Python"

    Add this class before `main()`:

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

    Then register the plugin in `main()`:
    ```python
    kernel.add_plugin(WeatherPlugin(), plugin_name="weather")
    ```

=== "C#"

    Add this class to your project:

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

    Register in `Program.cs`:
    ```csharp
    kernel.Plugins.AddFromType<WeatherPlugin>("weather");
    ```

---

### Step 3: Enable auto function calling

With auto function calling, the LLM **decides when to call your function** based on the conversation. You don't need to trigger it manually.

=== "Python"

    Update your settings to enable auto function calling:

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

Run it and ask: `"What's the weather like in Seattle today?"`

The LLM will:
1. See that `get_current_weather` is available
2. Call it with `city = "Seattle"`
3. Incorporate the result into its answer

!!! success "Expected output"
    "The current weather in Seattle is 🌧️ Rainy, 12°C. Bring an umbrella!"

---

### Step 4: Build a simple conversation loop

Let's make it interactive:

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


## 📥 Download Supporting Files

- [📥 hello_agent_starter.py](https://github.com/lcarli/AI-LearningHub/raw/main/docs/docs/en/labs/lab-014/hello_agent_starter.py)
- [📥 requirements.txt](https://github.com/lcarli/AI-LearningHub/raw/main/docs/docs/en/labs/lab-014/requirements.txt)

---

## Summary

You've built your first **Semantic Kernel agent** that:

- ✅ Connects to an LLM (GitHub Models — free)
- ✅ Has a custom **Plugin** with a native function
- ✅ Uses **auto function calling** — the LLM decides when to invoke the function
- ✅ Maintains **conversation history** across turns

---

## Next Steps

- **Add memory and more plugins:** → [Lab 023 — SK Plugins, Memory & Planners](lab-023-sk-plugins-memory.md)
- **Build an MCP Server and connect it to SK:** → [Lab 020 — MCP Server in Python](lab-020-mcp-server-python.md)
