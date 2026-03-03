"""
Lab 013: GitHub Models — Free LLM Inference
============================================
Starter file — complete the TODOs to finish each exercise.

Prerequisites:
  pip install openai
  export GITHUB_TOKEN=your_token_here   (get from github.com → Settings → Developer Settings → Tokens)
"""

import os
from openai import OpenAI

# TODO 1: Initialize the OpenAI client pointing at GitHub Models
# Hint: base_url="https://models.inference.ai.azure.com"
#       api_key=os.environ["GITHUB_TOKEN"]
client = None  # Replace with the correct client initialization


# ─────────────────────────────────────────────────────────────────────────────
# Exercise 1: Simple chat completion
# ─────────────────────────────────────────────────────────────────────────────
def simple_chat(user_message: str) -> str:
    """Send a single message and return the response text."""
    # TODO 2: Call client.chat.completions.create() with:
    #   model="gpt-4o-mini"
    #   messages=[{"role": "user", "content": user_message}]
    # Return response.choices[0].message.content
    raise NotImplementedError("TODO 2: implement simple_chat()")


# ─────────────────────────────────────────────────────────────────────────────
# Exercise 2: Chat with a system prompt (OutdoorGear assistant)
# ─────────────────────────────────────────────────────────────────────────────
SYSTEM_PROMPT = """You are an expert outdoor gear advisor for OutdoorGear Inc.
You help customers choose the right gear for their adventures.
Keep answers concise (max 3 sentences). Always ask one follow-up question.
Never recommend products you don't know exist."""


def outdoor_advisor(user_question: str) -> str:
    """Answer outdoor gear questions using the system prompt above."""
    # TODO 3: Call client.chat.completions.create() with:
    #   model="gpt-4o-mini"
    #   messages=[system message + user message]
    # Use SYSTEM_PROMPT as the system content
    raise NotImplementedError("TODO 3: implement outdoor_advisor()")


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
MODELS_TO_TRY = [
    "gpt-4o-mini",
    "gpt-4o",
    "Phi-4",
]

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
