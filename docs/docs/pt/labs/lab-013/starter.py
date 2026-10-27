"""Lab 013 starter for Foundry Local or Ollama."""

from openai import OpenAI
import os

BASE_URL = os.environ.get("LOCAL_LLM_BASE_URL", "http://localhost:11434/v1")
MODEL = os.environ.get("LOCAL_LLM_MODEL", "phi4-mini")
client = OpenAI(base_url=BASE_URL, api_key="local")


# ─────────────────────────────────────────────────────────────────────────────
# Exercise 1: Simple chat completion
# ─────────────────────────────────────────────────────────────────────────────
def simple_chat(user_message: str) -> str:
    """Send a single message and return the response text."""
    response = client.chat.completions.create(
        model=MODEL,
        messages=[{"role": "user", "content": user_message}],
    )
    return response.choices[0].message.content or ""


# ─────────────────────────────────────────────────────────────────────────────
# Exercise 2: Chat with a system prompt (OutdoorGear assistant)
# ─────────────────────────────────────────────────────────────────────────────
SYSTEM_PROMPT = """You are an expert outdoor gear advisor for OutdoorGear Inc.
You help customers choose the right gear for their adventures.
Keep answers concise (max 3 sentences). Always ask one follow-up question.
Never recommend products you don't know exist."""


def outdoor_advisor(user_question: str) -> str:
    """Answer outdoor gear questions using the system prompt above."""
    response = client.chat.completions.create(
        model=MODEL,
        messages=[
            {"role": "system", "content": SYSTEM_PROMPT},
            {"role": "user", "content": user_question},
        ],
    )
    return response.choices[0].message.content or ""


# ─────────────────────────────────────────────────────────────────────────────
# Exercise 3: Multi-turn conversation
# ─────────────────────────────────────────────────────────────────────────────
def multi_turn_chat():
    """A simple CLI loop that maintains conversation history."""
    messages = [{"role": "system", "content": SYSTEM_PROMPT}]
    print("OutdoorGear Advisor (type 'quit' to exit)\n")

    while True:
        user_input = input("You: ").strip()
        if user_input.lower() in ("quit", "exit", "q"):
            break

        # TODO 4: Append the user message to `messages`
        # TODO 5: Call the API with the full messages list
        # TODO 6: Extract the assistant reply and print it
        # TODO 7: Append the assistant reply to `messages` for next turn
        print("TODO: implement multi_turn_chat()")
        break  # Remove this line once implemented


# ─────────────────────────────────────────────────────────────────────────────
# Exercise 4: Try different models
# ─────────────────────────────────────────────────────────────────────────────
MODELS_TO_TRY = [MODEL]

QUESTION = "What sleeping bag temperature rating do I need for winter camping at -10°C?"


def compare_models():
    """Send the same question to multiple models and compare responses."""
    for model_name in MODELS_TO_TRY:
        print(f"\n{'='*60}")
        print(f"Model: {model_name}")
        print('='*60)
        # TODO 8: Call the API with each model_name and print the response
        # Handle errors gracefully (some models may not be available)
        print(f"TODO: call {model_name}")


# ─────────────────────────────────────────────────────────────────────────────
# Main
# ─────────────────────────────────────────────────────────────────────────────
if __name__ == "__main__":
    print("=== Exercise 1: Simple Chat ===")
    # Uncomment after completing TODO 2:
    # print(simple_chat("What's a good tent for solo hiking?"))

    print("\n=== Exercise 2: Outdoor Advisor ===")
    # Uncomment after completing TODO 3:
    # print(outdoor_advisor("I need a sleeping bag for -5°C winter camping."))

    print("\n=== Exercise 3: Multi-turn Chat ===")
    # Uncomment after completing TODOs 4-7:
    # multi_turn_chat()

    print("\n=== Exercise 4: Compare Models ===")
    # Uncomment after completing TODO 8:
    # compare_models()

    print("\n✅ Complete the TODOs above and uncomment the exercises!")
