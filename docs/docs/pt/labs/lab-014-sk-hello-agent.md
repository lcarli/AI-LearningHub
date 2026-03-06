---
tags: [semantic-kernel, free, python, github-models]
---
# Lab 014: Semantic Kernel — Hello Agent

<div class="lab-meta">
  <span><strong>Nível:</strong> <span class="level-badge level-100">L100</span></span>
  <span><strong>Trilha:</strong> <a href="../paths/semantic-kernel/">🧠 Semantic Kernel</a></span>
  <span><strong>Tempo:</strong> ~30 min</span>
  <span><strong>💰 Custo:</strong> <span class="level-badge cost-github">GitHub Free</span> — Conta gratuita no GitHub, sem cartão de crédito</span>
</div>

!!! warning "Semantic Kernel → Microsoft Agent Framework"
    O Semantic Kernel agora faz parte do **Microsoft Agent Framework (MAF)**, que unifica o SK e o AutoGen em um único framework. Os conceitos deste laboratório (Kernel, Plugins, chamada de funções) ainda se aplicam — o MAF é construído sobre eles. Consulte o **[Lab 076: Microsoft Agent Framework](lab-076-microsoft-agent-framework.md)** para o guia de migração.

## O Que Você Vai Aprender

- O que é o Semantic Kernel (SK) e seus principais componentes
- Como criar um **Kernel** do SK conectado ao GitHub Models (gratuito)
- Como adicionar seu primeiro **Plugin** (função nativa)
- Como habilitar a **chamada automática de funções** para que o LLM decida quando usar sua função

---

## Introdução

O **Semantic Kernel** é o SDK de código aberto da Microsoft para construir agentes e aplicações de IA. Ele fica entre o seu código e o LLM, fornecendo:

- Uma abstração unificada sobre qualquer LLM (OpenAI, Azure OpenAI, GitHub Models, Ollama...)
- Um **sistema de Plugins** para definir funções que o LLM pode chamar
- **Chamada automática de funções** — o LLM invoca automaticamente suas funções quando necessário
- **Memória vetorial** para contexto de longo prazo (abordado no Lab 023)

Neste laboratório, construímos um agente simples que pode responder perguntas **e** chamar uma função personalizada.

---

## 📁 Arquivo Inicial

Um arquivo inicial com estrutura básica é fornecido com comentários `TODO` para cada etapa:

```bash
pip install -r requirements.txt
python hello_agent_starter.py
```

Complete os TODOs em ordem (1–16) para construir um agente SK completo com funções semânticas, plugins nativos e um loop de chat.

---

## Configuração de Pré-requisitos

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

Certifique-se de que `GITHUB_TOKEN` está configurado (veja [Lab 013](lab-013-github-models.md#prerequisites-setup)).

---

!!! tip "Início Rápido com GitHub Codespaces"
    [![Open in GitHub Codespaces](https://github.com/codespaces/badge.svg)](https://codespaces.new/lcarli/AI-LearningHub?quickstart=1)

    Todas as dependências já estão pré-instaladas no devcontainer.


## 📦 Arquivos de Apoio

!!! note "Baixe estes arquivos antes de iniciar o laboratório"
    Salve todos os arquivos em uma pasta `lab-014/` no seu diretório de trabalho.

| Arquivo | Descrição | Download |
|---------|-----------|----------|
| `hello_agent_starter.py` | Script inicial com TODOs | [📥 Download](https://github.com/lcarli/AI-LearningHub/raw/main/docs/docs/en/labs/lab-014/hello_agent_starter.py) |
| `requirements.txt` | Dependências do Python | [📥 Download](https://github.com/lcarli/AI-LearningHub/raw/main/docs/docs/en/labs/lab-014/requirements.txt) |

---

## Exercício do Laboratório

### Etapa 1: Criar um Kernel básico

O **Kernel** é o objeto central no Semantic Kernel — ele mantém sua conexão com o LLM e todos os plugins.

=== "Python"

    Crie `hello_agent.py`:

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

    Edite `Program.cs`:

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

Execute:

=== "Python"
    ```bash
    python hello_agent.py
    ```
=== "C#"
    ```bash
    dotnet run
    ```

Você deverá ver o LLM respondendo. Agora vamos adicionar uma função personalizada.

---

### Etapa 2: Adicionar um Plugin (função nativa)

Um **Plugin** é uma classe com métodos que o LLM pode chamar. Decore-os com `@kernel_function` (Python) ou `[KernelFunction]` (C#).

=== "Python"

    Adicione esta classe antes de `main()`:

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

    Em seguida, registre o plugin em `main()`:
    ```python
    kernel.add_plugin(WeatherPlugin(), plugin_name="weather")
    ```

=== "C#"

    Adicione esta classe ao seu projeto:

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

    Registre em `Program.cs`:
    ```csharp
    kernel.Plugins.AddFromType<WeatherPlugin>("weather");
    ```

---

### Etapa 3: Habilitar a chamada automática de funções

Com a chamada automática de funções, o LLM **decide quando chamar sua função** com base na conversa. Você não precisa acioná-la manualmente.

=== "Python"

    Atualize suas configurações para habilitar a chamada automática de funções:

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

Execute e pergunte: `"What's the weather like in Seattle today?"`

O LLM irá:
1. Ver que `get_current_weather` está disponível
2. Chamá-la com `city = "Seattle"`
3. Incorporar o resultado na sua resposta

!!! success "Saída esperada"
    "The current weather in Seattle is 🌧️ Rainy, 12°C. Bring an umbrella!"

---

### Etapa 4: Construir um loop de conversa simples

Vamos torná-lo interativo:

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

## Resumo

Você construiu seu primeiro **agente Semantic Kernel** que:

- ✅ Conecta-se a um LLM (GitHub Models — gratuito)
- ✅ Possui um **Plugin** personalizado com uma função nativa
- ✅ Usa **chamada automática de funções** — o LLM decide quando invocar a função
- ✅ Mantém o **histórico de conversa** entre as interações

---

## Próximos Passos

- **Adicionar memória e mais plugins:** → [Lab 023 — SK Plugins, Memory & Planners](lab-023-sk-plugins-memory.md)
- **Construir um MCP Server e conectá-lo ao SK:** → [Lab 020 — MCP Server in Python](lab-020-mcp-server-python.md)
