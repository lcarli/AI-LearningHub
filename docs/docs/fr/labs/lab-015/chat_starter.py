"""
Lab 015: Ollama — Local LLMs
=============================
Starter file — chat with Ollama running locally.
100% free, no API keys, no internet required after model download.

Prerequisites:
  1. Install Ollama: https://ollama.com
  2. Pull a model: ollama pull phi4
  3. pip install openai   (Ollama uses OpenAI-compatible API)

No environment variables needed — Ollama runs at http://localhost:11434
"""

from openai import OpenAI

# Ollama exposes an OpenAI-compatible API on port 11434
ollama_client = OpenAI(
    base_url="http://localhost:11434/v1",
    api_key="ollama",  # Required by the library but not used by Ollama
)


# ─────────────────────────────────────────────────────────────────────────────
# Exercise 1: List available models
# ─────────────────────────────────────────────────────────────────────────────
def list_local_models():
    """Print all models available in your local Ollama installation."""
    try:
        models = ollama_client.models.list()
        print("📦 Available local models:")
        for model in models.data:
            print(f"  • {model.id}")
        return [m.id for m in models.data]
    except Exception as e:
        print(f"❌ Could not connect to Ollama: {e}")
        print("   Make sure Ollama is running: ollama serve")
        return []


# ─────────────────────────────────────────────────────────────────────────────
# Exercise 2: Simple completion
# ─────────────────────────────────────────────────────────────────────────────
def ask_ollama(prompt: str, model: str = "phi4") -> str:
    """Send a prompt to a local Ollama model and return the response."""
    response = ollama_client.chat.completions.create(
        model=model,
        messages=[{"role": "user", "content": prompt}],
    )
    return response.choices[0].message.content


# ─────────────────────────────────────────────────────────────────────────────
# Exercise 3: Chat with the custom OutdoorGear model
# ─────────────────────────────────────────────────────────────────────────────
def chat_with_outdoorgear():
    """
    Chat with the custom OutdoorGear model.
    First create it: ollama create outdoorgear -f Modelfile
    """
    print("\n🏕️  OutdoorGear Advisor (local, private, free!)")
    print("   Type 'quit' to exit\n")

    history = []

    while True:
        user_input = input("You: ").strip()
        if not user_input or user_input.lower() in ("quit", "exit", "q"):
            print("Happy trails! 🥾")
            break

        history.append({"role": "user", "content": user_input})

        try:
            response = ollama_client.chat.completions.create(
                model="outdoorgear",  # Our custom model from Modelfile
                messages=history,
            )
            assistant_reply = response.choices[0].message.content
            history.append({"role": "assistant", "content": assistant_reply})
            print(f"\nGear: {assistant_reply}\n")
        except Exception as e:
            print(f"❌ Error: {e}")
            print("   Did you create the model? Run: ollama create outdoorgear -f Modelfile")
            break


# ─────────────────────────────────────────────────────────────────────────────
# Exercise 4: Compare two local models side-by-side
# ─────────────────────────────────────────────────────────────────────────────
def compare_local_models(models: list[str], question: str):
    """Compare responses from multiple local models."""
    print(f"\n📊 Question: {question}\n")

    for model in models:
        print(f"{'─'*50}")
        print(f"Model: {model}")
        print('─'*50)
        try:
            reply = ask_ollama(question, model=model)
            print(reply)
        except Exception as e:
            print(f"⚠️  Model '{model}' not available: {e}")
            print(f"   Pull it with: ollama pull {model}")
        print()


# ─────────────────────────────────────────────────────────────────────────────
# Exercise 5: Streaming responses (watch tokens appear in real-time)
# ─────────────────────────────────────────────────────────────────────────────
def streaming_chat(prompt: str, model: str = "phi4"):
    """Stream the response token by token."""
    print(f"\n🔄 Streaming from {model}:\n")

    stream = ollama_client.chat.completions.create(
        model=model,
        messages=[{"role": "user", "content": prompt}],
        stream=True,
    )

    for chunk in stream:
        delta = chunk.choices[0].delta.content
        if delta:
            print(delta, end="", flush=True)
    print("\n")  # newline after streaming


# ─────────────────────────────────────────────────────────────────────────────
# Main
# ─────────────────────────────────────────────────────────────────────────────
if __name__ == "__main__":
    # Step 1: Check what's available
    available = list_local_models()

    if not available:
        print("\n💡 Quick start:")
        print("   1. Install Ollama: https://ollama.com")
        print("   2. Run: ollama pull phi4")
        print("   3. Run this script again")
    else:
        # Step 2: Simple question
        print("\n=== Exercise 2: Simple Completion ===")
        reply = ask_ollama(
            "What's the most important piece of gear for a first-time hiker?",
            model=available[0]
        )
        print(reply)

        # Step 3: Streaming
        print("\n=== Exercise 5: Streaming ===")
        streaming_chat(
            "Explain the layering system for outdoor clothing in 3 steps.",
            model=available[0]
        )

        # Step 4: Custom OutdoorGear model (requires Modelfile setup)
        print("\n=== Exercise 3: Custom OutdoorGear Model ===")
        print("Create the model first: ollama create outdoorgear -f Modelfile")
        # Uncomment to run: chat_with_outdoorgear()

        # Step 5: Compare models (if you have multiple)
        if len(available) >= 2:
            print("\n=== Exercise 4: Compare Models ===")
            compare_local_models(
                available[:2],
                "What sleeping bag temperature rating do I need for 0°C camping?"
            )
