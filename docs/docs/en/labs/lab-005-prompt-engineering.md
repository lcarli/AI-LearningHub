---
tags: [free, beginner, no-account-needed, prompt-engineering, persona-student, persona-developer, persona-analyst]
---
# Lab 005: Prompt Engineering

<div class="lab-meta">
  <span><strong>Level:</strong> <span class="level-badge level-50">L50</span></span>
  <span><strong>Path:</strong> All paths</span>
  <span><strong>Time:</strong> ~25 min</span>
  <span><strong>💰 Cost:</strong> <span class="level-badge cost-free">Free</span> — No account needed (examples use GitHub Models playground)</span>
</div>

## What You'll Learn

- The anatomy of a prompt: system, user, assistant messages
- Core techniques: zero-shot, few-shot, chain-of-thought, role prompting
- How to write effective **system prompts** for AI agents
- Common failure patterns — and how to fix them
- Practical templates you can use immediately

---

## Introduction

Prompt engineering is the practice of designing inputs to LLMs that reliably produce the outputs you want. It's part art, part science — and the single most impactful skill for building good AI agents.

A well-crafted prompt can turn a mediocre response into an excellent one without changing the model. A poorly designed system prompt will cause your agent to misbehave no matter how powerful the model is.

!!! tip "Try these examples live"
    Open the [GitHub Models Playground](https://github.com/marketplace/models) in a browser tab and test each example as you read. It's free with a GitHub account.

---

## 📦 Supporting Files

!!! note "Download these files before starting the lab"
    Save all files to a `lab-005/` folder in your working directory.

| File | Description | Download |
|------|-------------|----------|
| `prompt_challenges.py` | Interactive exercise script | [📥 Download](https://github.com/lcarli/AI-LearningHub/raw/main/docs/docs/en/labs/lab-005/prompt_challenges.py) |

---

## Part 1: Anatomy of a Prompt

Every LLM API call has up to three message types:

```
┌──────────────────────────────────────────────┐
│  SYSTEM MESSAGE                              │
│  "You are a helpful assistant for Zava,      │
│   a DIY retail company..."                   │
│  (Persistent instructions — defines behavior)│
├──────────────────────────────────────────────┤
│  USER MESSAGE                                │
│  "What are your top-selling products         │
│   in the camping category?"                  │
│  (The human's input)                         │
├──────────────────────────────────────────────┤
│  ASSISTANT MESSAGE (optional)                │
│  "The top-selling camping products are..."   │
│  (Prior model responses — for few-shot or    │
│   continued conversations)                   │
└──────────────────────────────────────────────┘
```

### The System Message

The system message is the most important part of agent design. It:

- Defines the agent's **persona and role**
- Sets **behavioral rules** ("never invent data")
- Specifies **output format** (Markdown, JSON, tables)
- Provides **domain context** the model wouldn't otherwise have
- Handles **edge cases** ("if asked out-of-scope questions, say...")

??? question "🤔 Check Your Understanding"
    What are the three message roles in an LLM API call, and which one is invisible to the end user?

    ??? success "Answer"
        The three roles are **system**, **user**, and **assistant**. The **system message** is invisible to end users — it's set by the developer and defines the agent's persona, rules, scope, and behavior. The user sees their own messages and the assistant's responses.

---

## Part 2: Core Techniques

### Zero-Shot

Ask directly with no examples. Works for simple, well-defined tasks.

```
Classify this customer review as Positive, Neutral, or Negative.

Review: "The tent arrived on time but the zipper broke after one use."
```

**When to use:** Simple classification, extraction, summarization.

---

### Few-Shot

Provide examples before your actual question. Dramatically improves consistency.

```
Classify customer reviews as Positive, Neutral, or Negative.

Review: "Great quality, arrived fast!" → Positive
Review: "It's okay, nothing special." → Neutral
Review: "Completely broken on arrival." → Negative

Review: "The tent arrived on time but the zipper broke after one use." →
```

**When to use:** Any task where you want a specific format, tone, or classification scheme.

!!! tip "Rule of thumb"
    2–5 examples is usually enough. More than 10 rarely helps and costs more tokens.

---

### Chain-of-Thought (CoT)

Ask the model to think step-by-step before giving the final answer. Improves accuracy on reasoning tasks.

**Without CoT:**
```
Q: A store sells 3 tents for $249 each and gives a 15% group discount.
   What is the total?
A: $635.55
```
*(May be wrong — rushed calculation)*

**With CoT:**
```
Q: A store sells 3 tents for $249 each and gives a 15% group discount.
   What is the total? Think step by step.

A: 
Step 1: 3 tents × $249 = $747
Step 2: 15% discount = $747 × 0.15 = $112.05
Step 3: Total = $747 - $112.05 = $634.95
Final answer: $634.95
```

**How to trigger CoT:**
- "Think step by step"
- "Let's work through this"
- "Explain your reasoning before answering"

**When to use:** Math, logic, multi-step reasoning, debugging, complex decisions.

??? question "🤔 Check Your Understanding"
    Why does adding "Think step by step" to a math prompt improve accuracy, even though the model has the same knowledge either way?

    ??? success "Answer"
        Chain-of-thought prompting forces the model to **generate intermediate reasoning steps** before producing a final answer. This reduces errors because the model can catch mistakes in earlier steps. Without CoT, the model may "rush" to a final answer and skip critical calculations.

??? question "🤔 Check Your Understanding"
    When would you choose few-shot prompting over zero-shot prompting?

    ??? success "Answer"
        Use **few-shot** when you need a **specific format, tone, or classification scheme** that the model might not infer from instructions alone. Providing 2–5 examples dramatically improves consistency. Zero-shot works for simple, well-defined tasks where the model can infer the expected output format.

---

### Role Prompting

Give the model a persona to adopt. Changes tone, vocabulary, and depth.

```
You are a senior PostgreSQL database engineer with 15 years of experience.
Review this query for performance issues and suggest improvements:

SELECT * FROM sales WHERE store_id = 5 ORDER BY sale_date;
```

vs.

```
Review this query for performance issues:

SELECT * FROM sales WHERE store_id = 5 ORDER BY sale_date;
```

The role prompt produces more detailed, expert-level feedback.

---

### Structured Output

Force the model to respond in a specific format — JSON, Markdown table, bullet list.

```
Extract the product details from this text and return as JSON.
Do not include any explanation — return only the JSON object.

Text: "The ProTrek X200 hiking boots are available in sizes 7-13,
       priced at $189.99, and come in black and brown."

Expected format:
{
  "name": string,
  "sizes": [number],
  "price": number,
  "colors": [string]
}
```

!!! tip "Use JSON mode when available"
    Most APIs support `response_format: { type: "json_object" }` which forces valid JSON output and eliminates parsing errors.

---

### Prompt Chaining

Break complex tasks into a sequence of smaller prompts. Each output feeds the next.

```
Step 1: Extract key facts from the sales report → JSON
Step 2: Feed JSON to "write an executive summary" prompt → Text
Step 3: Feed summary to "translate to Spanish" prompt → Final output
```

This is more reliable than asking one prompt to do everything.

---

## Part 3: Writing Agent System Prompts

For AI agents (used in all labs from L100+), the system prompt is the **agent's constitution**. Here's a proven structure:

```markdown
## Role
You are [name], a [role] for [company/context].
Your tone is [professional/friendly/technical].

## Capabilities
You can:
- [capability 1]
- [capability 2]
Use ONLY the tools provided to you. Never invent data.

## Rules
- [Rule 1: always do X]
- [Rule 2: never do Y]
- [Rule 3: when Z happens, respond with...]

## Output Format
- Default: Markdown tables
- Charts: only when explicitly requested
- Language: respond in the same language the user writes in

## Scope
Only answer questions about [domain].
For out-of-scope questions, say: "I can only help with [domain]."
```

### Real example: Zava Sales Agent (from this repo's workshop)

```markdown
You are Zava, a sales analysis agent for Zava DIY Retail (Washington State).
Your tone is professional and friendly. Use emojis sparingly.

## Data Rules
- Always fetch table schemas before querying (get_multiple_table_schemas())
- Apply LIMIT 20 to all SELECT queries
- Use exact table and column names from the schema
- Never invent, estimate, or assume data

## Financial Calendar
- Financial year (FY) starts July 1
- Q1=Jul–Sep, Q2=Oct–Dec, Q3=Jan–Mar, Q4=Apr–Jun

## Visualizations
- Generate charts ONLY when user uses words: "chart", "graph", "visualize", "show as"
- Always save as PNG and provide download link

## Scope
Only answer questions about Zava sales data.
If asked about anything else, say you're specialized for Zava sales analysis.
```

---

## Part 4: Common Failure Patterns — and Fixes

### ❌ The Vague Prompt

```
# Bad
"Summarize this."

# Good
"Summarize this sales report in 3 bullet points.
 Each bullet should be ≤20 words.
 Focus on: total revenue, top product, and key trend."
```

**Rule:** Be explicit about format, length, and focus.

---

### ❌ The Contradictory Prompt

```
# Bad (contradicts itself)
"Be concise but include all the details."

# Good
"Summarize in 100 words. Prioritize: revenue numbers and top-performing stores."
```

**Rule:** When space is limited, tell the model what to prioritize.

---

### ❌ No Negative Examples

```
# Bad (doesn't stop hallucination)
"Answer questions about our product catalog."

# Good
"Answer questions about our product catalog.
 If you don't have a product in your data, say 'I don't have that product in the catalog.'
 Never guess or suggest alternatives you haven't verified."
```

**Rule:** Always define what the agent should do when it *can't* answer.

---

### ❌ Instruction Overload

```
# Bad (27 rules, contradictory, hard to follow)
"Be helpful. Be concise. Be detailed. Use tables. Use bullet points.
 Always explain. Never explain. Answer in English. Answer in Portuguese..."

# Good
"Use Markdown tables for data. Use bullet points for lists.
 Default to the user's language."
```

**Rule:** 5–10 clear rules outperform 30 vague ones.

---

### ❌ Forgetting the Edge Cases

Always ask: "What happens if the user asks something out of scope? What if data is missing? What if the question is ambiguous?"

Build rules for those cases explicitly.

---

## Part 5: Quick Reference Templates

### Extraction Prompt

```
Extract the following fields from the text below.
Return as JSON. If a field is not found, use null.

Fields: name, price, category, availability

Text:
"""
{text}
"""
```

### Classification Prompt

```
Classify the following support ticket into one of these categories:
[Billing, Shipping, Returns, Technical, Other]

Return only the category name. No explanation.

Ticket: "{ticket_text}"
```

### Summarization Prompt

```
Summarize the following in {n} bullet points.
Each bullet: one key insight, ≤15 words.
Audience: {audience}

Text:
"""
{text}
"""
```

### Agent System Prompt Template

```
## Role
You are {agent_name}, a {role} for {company}.
Tone: {tone}.

## Capabilities
You have access to these tools: {tools}
Only use verified tool outputs. Never invent data.

## Rules
- {rule_1}
- {rule_2}

## Output Format
{format_instructions}

## Scope
{scope_definition}
For out-of-scope questions: "{out_of_scope_response}"
```

??? question "🤔 Check Your Understanding"
    Why is it important for an agent's system prompt to define what the agent should do when it *can't* answer a question?

    ??? success "Answer"
        Without an explicit fallback instruction, the LLM will try to answer anyway — often **hallucinating** a plausible-sounding but incorrect response. Defining out-of-scope behavior (e.g., "say 'I can only help with X'") prevents the agent from inventing data and sets clear user expectations.

---

## Part 6: 🧪 Interactive Challenges — Fix the Prompts

Reading about prompts is good. **Writing and running them** is better.

These 4 challenges give you **broken or vague prompts** that produce bad results. Your task: improve them until the output matches the target.

### Setup (5 minutes, free)

```bash
pip install openai
export GITHUB_TOKEN=your_github_token   # github.com → Settings → Developer Settings → Tokens
```

Download the challenge file:
```bash
# From the cloned repo:
cd AI-LearningHub/docs/docs/en/labs/lab-005
python prompt_challenges.py
```

Or copy it from below:

```python title="lab-005/prompt_challenges.py"
--8<-- "labs/lab-005/prompt_challenges.py"
```

### What each challenge tests

| # | What's broken | Technique to apply |
|---|---------------|--------------------|
| **1** | Vague user prompt, no format instruction | Specific output format |
| **2** | No structure, likely prose instead of JSON | Structured output |
| **3** | Direct question without reasoning steps | Chain-of-thought |
| **4** | No scope guardrails → hallucinated products | Scope control |

### How to work through each challenge

1. Run `python prompt_challenges.py` and read the **❌ BAD PROMPT result**
2. Edit the `IMPROVED_SYSTEM_*` or `IMPROVED_USER_*` variables at the bottom of each challenge
3. Re-run and compare with the **Target** description in the comments
4. Keep iterating until your output matches

!!! tip "There's no single right answer"
    The goal is to get output that meets the target spec. How you phrase the prompt is up to you — compare approaches with a colleague!

---

## 🧠 Knowledge Check

??? question "**Q1 (Multiple Choice):** You are building an agent that needs to solve a multi-step math problem. Which prompting technique will most improve accuracy?"

    - A) Zero-shot prompting
    - B) Role prompting (e.g., "You are a mathematician")
    - C) Chain-of-thought prompting (e.g., "Think step by step")
    - D) Structured output prompting

    ??? success "✅ Reveal Answer"
        **Correct: C — Chain-of-thought prompting**

        Chain-of-thought (CoT) forces the model to reason through intermediate steps before producing a final answer. This dramatically reduces errors on math, logic, and multi-step problems. "Think step by step" or showing few-shot examples with explicit reasoning both trigger CoT. Zero-shot works for simple tasks; role prompting helps with tone/expertise; structured output helps with formatting.

??? question "**Q2 (Multiple Choice):** Which of the three conversation roles does the USER never directly see when interacting with an agent?"

    - A) user
    - B) assistant
    - C) system
    - D) function

    ??? success "✅ Reveal Answer"
        **Correct: C — system**

        The `system` message is the agent's "constitution" — it sets the persona, rules, scope, and behavior. It's set by the developer and not visible to end users in the chat interface. The `user` role holds the human's inputs. The `assistant` role holds the model's previous responses (included in subsequent API calls to maintain context).

??? question "**Q3 (Multiple Choice):** Your OutdoorGear agent keeps saying things like 'The TrailBlazer Tent probably weighs around 1.5kg' even though the exact weight is in the database. Which system prompt rule is the best fix?"

    - A) "You are a helpful OutdoorGear assistant."
    - B) "Never invent, estimate, or assume data. Only use outputs from the tools provided to you. If the product is not found, say: 'I don't have that information in our catalog.'"
    - C) "Think step by step before answering."
    - D) "Always respond in JSON format."

    ??? success "✅ Reveal Answer"
        **Correct: B**

        The key is two instructions working together: (1) the prohibition on inventing/estimating data, and (2) an explicit fallback phrase for when data is unavailable. Without the fallback, the model will invent an answer rather than say nothing. Grounding rules + fallback behavior together prevent hallucination in tool-using agents.

---

## Summary

| Technique | Best for |
|-----------|---------|
| **Zero-shot** | Simple, clear tasks |
| **Few-shot** | Consistent format or classification |
| **Chain-of-thought** | Reasoning, math, multi-step problems |
| **Role prompting** | Expert-level responses |
| **Structured output** | JSON, tables, parseable data |
| **Prompt chaining** | Complex multi-step workflows |

**The golden rule:** Be specific about *what you want*, *what format*, and *what to do when things go wrong*.

---

## Next Steps

You're now ready to build your first hands-on lab:

→ **[Lab 010 — GitHub Copilot First Steps](lab-010-github-copilot-first-steps.md)** — Apply prompt skills in VS Code  
→ **[Lab 013 — GitHub Models](lab-013-github-models.md)** — Run your own prompts via API for free  
→ **[Lab 014 — SK Hello Agent](lab-014-sk-hello-agent.md)** — Write a system prompt for a Semantic Kernel agent
