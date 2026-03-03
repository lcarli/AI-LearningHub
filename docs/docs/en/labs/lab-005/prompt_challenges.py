# prompt_challenges.py
# 🧪 PROMPT ENGINEERING — Interactive Challenges
#
# SETUP:
#   pip install openai
#   export GITHUB_TOKEN=your_token_here
#
# This script runs "bad" prompts against the GitHub Models API
# and shows you the results. Your job: improve each prompt until
# the output matches the target.
#
# HOW TO USE:
#   1. Run: python prompt_challenges.py
#   2. See what each bad prompt produces
#   3. Edit the IMPROVED_PROMPT variable in each challenge
#   4. Re-run and compare
#   5. Check against the TARGET description below each challenge

import os
from openai import OpenAI

client = OpenAI(
    base_url="https://models.inference.ai.azure.com",
    api_key=os.environ.get("GITHUB_TOKEN", ""),
)

def ask(system: str, user: str, model: str = "gpt-4o-mini") -> str:
    response = client.chat.completions.create(
        model=model,
        temperature=0.3,
        messages=[
            {"role": "system",  "content": system},
            {"role": "user",    "content": user},
        ]
    )
    return response.choices[0].message.content


# ============================================================
# CHALLENGE 1 — Vague vs. Specific
# ============================================================
print("\n" + "="*60)
print("CHALLENGE 1: Make the summary useful")
print("="*60)

BAD_SYSTEM_1 = "You are a helpful assistant."
BAD_USER_1 = "Summarize this."
PRODUCT_TEXT = """
The TrailBlazer X200 is a waterproof Gore-Tex hiking boot featuring a
Vibram outsole for superior grip. Rated for 3-season use, it includes
a cushioned midsole and comes in sizes 7-13. Retails at $189.99.
Colors available: midnight black, earth brown, slate grey.
"""

print("\n❌ BAD PROMPT result:")
bad_result_1 = ask(BAD_SYSTEM_1, BAD_USER_1 + "\n\n" + PRODUCT_TEXT)
print(bad_result_1)

# ✏️  YOUR TASK: Edit IMPROVED_SYSTEM_1 and IMPROVED_USER_1 so the output is:
# - Exactly 2 bullet points
# - One bullet = key feature, one bullet = price + colors
# - No introduction sentence, no conclusion

IMPROVED_SYSTEM_1 = "You are a helpful assistant."  # ← edit me
IMPROVED_USER_1 = "Summarize this."                 # ← edit me

print("\n✅ YOUR IMPROVED PROMPT result:")
improved_result_1 = ask(IMPROVED_SYSTEM_1, IMPROVED_USER_1 + "\n\n" + PRODUCT_TEXT)
print(improved_result_1)


# ============================================================
# CHALLENGE 2 — Add Structure (JSON output)
# ============================================================
print("\n" + "="*60)
print("CHALLENGE 2: Get structured JSON output")
print("="*60)

BAD_SYSTEM_2 = "Extract the product info."
BAD_USER_2 = PRODUCT_TEXT

print("\n❌ BAD PROMPT result (probably not valid JSON):")
bad_result_2 = ask(BAD_SYSTEM_2, BAD_USER_2)
print(bad_result_2)

# ✏️  YOUR TASK: Make the output be ONLY valid JSON with this exact shape:
# {
#   "name": string,
#   "price": number,
#   "sizes": [number, number, ...],
#   "colors": [string, ...],
#   "waterproof": boolean
# }

IMPROVED_SYSTEM_2 = "Extract the product info."   # ← edit me
IMPROVED_USER_2 = PRODUCT_TEXT                    # ← edit me

print("\n✅ YOUR IMPROVED PROMPT result:")
improved_result_2 = ask(IMPROVED_SYSTEM_2, IMPROVED_USER_2)
print(improved_result_2)

# Bonus: try to parse it as JSON
import json
try:
    parsed = json.loads(improved_result_2.strip().strip("```json").strip("```"))
    print(f"\n  ✅ Valid JSON! Keys: {list(parsed.keys())}")
except:
    print("\n  ❌ Still not valid JSON — keep improving the prompt!")


# ============================================================
# CHALLENGE 3 — Chain of Thought
# ============================================================
print("\n" + "="*60)
print("CHALLENGE 3: Get the right math answer")
print("="*60)

MATH_QUESTION = """
A customer buys:
- 2x TrailBlazer X200 boots at $189.99 each
- 1x Summit Pro Tent at $349.00
They get a 15% loyalty discount on orders over $500.
What is the final total?
"""

BAD_SYSTEM_3 = "Answer math questions."
print("\n❌ BAD PROMPT result (may skip steps or be wrong):")
bad_result_3 = ask(BAD_SYSTEM_3, MATH_QUESTION)
print(bad_result_3)

# ✏️  YOUR TASK: Add a chain-of-thought instruction that makes the model:
# 1. Calculate the subtotal first
# 2. Check if discount applies
# 3. Calculate the final total
# Expected answer: subtotal = $728.98, discount = $109.35, total = $619.63

IMPROVED_SYSTEM_3 = "Answer math questions."    # ← edit me
IMPROVED_USER_3 = MATH_QUESTION                 # ← edit me

print("\n✅ YOUR IMPROVED PROMPT result:")
improved_result_3 = ask(IMPROVED_SYSTEM_3, IMPROVED_USER_3)
print(improved_result_3)


# ============================================================
# CHALLENGE 4 — Scope Control (stop hallucination)
# ============================================================
print("\n" + "="*60)
print("CHALLENGE 4: Stop the agent from making things up")
print("="*60)

BAD_SYSTEM_4 = "You are a customer service agent for OutdoorGear Inc."

OUT_OF_SCOPE_QUESTION = "Do you sell ski equipment? I need skis for Whistler."

print("\n❌ BAD PROMPT result (likely hallucinating products we don't sell):")
bad_result_4 = ask(BAD_SYSTEM_4, OUT_OF_SCOPE_QUESTION)
print(bad_result_4)

# ✏️  YOUR TASK: Fix the system prompt so the agent:
# 1. Politely says we don't sell ski equipment
# 2. Mentions what we DO sell (boots, tents, packs, jackets, climbing gear)
# 3. Does NOT invent products or refer users to competitors
# The response should be 2-3 sentences max.

IMPROVED_SYSTEM_4 = "You are a customer service agent for OutdoorGear Inc."  # ← edit me

print("\n✅ YOUR IMPROVED PROMPT result:")
improved_result_4 = ask(IMPROVED_SYSTEM_4, OUT_OF_SCOPE_QUESTION)
print(improved_result_4)

print("\n" + "="*60)
print("All 4 challenges complete! Review your improvements above.")
print("="*60)
