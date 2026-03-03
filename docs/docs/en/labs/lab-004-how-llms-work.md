---
tags: [free, beginner, no-account-needed, llm]
---
# Lab 004: How LLMs Work

<div class="lab-meta">
  <span><strong>Level:</strong> <span class="level-badge level-50">L50</span></span>
  <span><strong>Path:</strong> All paths</span>
  <span><strong>Time:</strong> ~20 min</span>
  <span><strong>💰 Cost:</strong> <span class="level-badge cost-free">Free</span> — No account needed</span>
</div>

## What You'll Learn

- What a Large Language Model (LLM) really is under the hood
- How training works: pre-training, fine-tuning, RLHF
- What tokens, context windows, and temperature mean in practice
- Why LLMs hallucinate — and how to mitigate it
- The difference between models: GPT-4o, Phi-4, Llama, Claude

---

## Introduction

You've probably used ChatGPT or GitHub Copilot. But what's actually happening when you type a message and get a response? Understanding the mechanics of LLMs makes you a dramatically better agent builder — you'll know *why* certain prompts work, *why* agents make mistakes, and *how* to design around their limitations.

---

## Part 1: What is a Large Language Model?

An LLM is a neural network trained to **predict the next token** given a sequence of tokens.

That's it. Everything else — reasoning, code generation, summarization, chat — is an emergent capability that arises from doing this *at massive scale* on *enormous amounts of text*.

### Tokens

A **token** is the basic unit an LLM processes. It's roughly ¾ of a word (about 4 characters).

```
"The quick brown fox" → ["The", " quick", " brown", " fox"]
"Hello, world!"       → ["Hello", ",", " world", "!"]
"OpenAI"              → ["Open", "AI"]
```

!!! info "Why tokens matter for agents"
    - Context windows are measured in tokens, not words
    - API costs are billed per token
    - Long documents must be chunked to fit in the context window

### The prediction loop

When you send a message, the LLM:

1. Converts your text to a sequence of token IDs
2. Passes them through billions of mathematical operations (transformer layers)
3. Outputs a probability distribution over the entire vocabulary (~100,000 tokens)
4. Samples the next token based on that distribution
5. Appends it to the sequence and repeats from step 2

```
Input: "The capital of France is"
            ↓
     [Token IDs: 464, 3361, 286, 4881, 318]
            ↓
     [Transformer: 96 layers × billions of params]
            ↓
     Probability distribution:
       "Paris"    → 94.7%
       "Lyon"     → 2.1%
       "a"        → 1.3%
       ...
            ↓
     Output: "Paris"
```

The LLM doesn't "know" facts — it has learned **statistical patterns** from text. When it says "Paris," it's because "Paris" almost always follows that phrase in its training data.

---

## Part 2: Training an LLM

### Stage 1 — Pre-training

The model reads **trillions of tokens** from the internet, books, code, and scientific papers. It learns language structure, facts, reasoning patterns, and common knowledge purely by predicting the next token.

```
Training data: Wikipedia + books + GitHub + web pages + ...
Goal: minimize prediction error across all that text
Result: a "base model" that can complete text
```

**GPT-4o, Llama 3, Phi-4** all start as base models.

### Stage 2 — Instruction Fine-tuning (SFT)

The base model is trained on **examples of conversations** — (prompt, ideal response) pairs. This teaches it to be helpful, follow instructions, and respond in a conversational way.

### Stage 3 — RLHF (Reinforcement Learning from Human Feedback)

Human raters compare pairs of responses and pick the better one. A **reward model** is trained on these preferences. The LLM is then fine-tuned to maximize the reward model's score.

This is why ChatGPT feels more polished and aligned than a raw base model.

```
Base model → SFT → RLHF → "Assistant" model
   (completes text)        (answers helpfully)
```

---

## Part 3: Key Parameters

### Context Window

The **context window** is how much text the model can "see" at once — its working memory.

| Model | Context Window |
|-------|---------------|
| GPT-4o | 128,000 tokens (~96,000 words) |
| GPT-4o-mini | 128,000 tokens |
| Phi-4 | 16,000 tokens |
| Llama 3.3 70B | 128,000 tokens |
| Claude 3.5 Sonnet | 200,000 tokens |

!!! warning "Context window ≠ unlimited memory"
    The model reads the *entire* context window on every request. Longer context = slower + more expensive. Agents use RAG and summarization to manage long conversations.

### Temperature

**Temperature** controls how random the output is.

| Temperature | Behavior | Use case |
|-------------|----------|---------|
| 0.0 | Deterministic — always picks highest probability token | Structured output, code, SQL |
| 0.3–0.7 | Balanced — creative but coherent | General chat, summaries |
| 1.0+ | Very creative/unpredictable | Creative writing, brainstorming |

```python
# Deterministic (good for structured data extraction)
response = client.chat.completions.create(
    model="gpt-4o",
    temperature=0.0,
    messages=[...]
)

# Creative (good for ideas/drafts)
response = client.chat.completions.create(
    model="gpt-4o",
    temperature=0.8,
    messages=[...]
)
```

### Top-p (nucleus sampling)

An alternative to temperature. Only sample from the smallest set of tokens whose cumulative probability exceeds `top_p`.

- `top_p=0.1` → very conservative
- `top_p=0.9` → allows diverse outputs

---

## Part 4: Why LLMs Hallucinate

Hallucination (generating confident-sounding false information) happens because:

1. **The model predicts likely text, not true text.** A plausible-sounding answer can score higher than "I don't know."
2. **Training data has gaps and noise.** If the web says something wrong often enough, the model learned it.
3. **No external memory.** The model doesn't "check" facts — it generates from patterns.

### How agents mitigate hallucination

| Technique | How it helps |
|-----------|-------------|
| **RAG** | Give the model real documents to cite instead of relying on training data |
| **Tool calling** | Let the model call APIs/databases for real-time data |
| **Low temperature** | Reduce creativity when accuracy matters |
| **System prompt rules** | "Never invent data; only use tool outputs" |
| **Structured output** | Force the model to produce JSON schema — easier to validate |
| **Evaluation** | Measure groundedness, coherence, and factuality automatically |

---

## Part 5: Choosing a Model

Not every task needs GPT-4o. Choosing the right model saves money and latency.

| Model | Best for | Speed | Cost |
|-------|---------|-------|------|
| **GPT-4o** | Complex reasoning, long context, multimodal | Medium | $$$ |
| **GPT-4o-mini** | Most everyday tasks | Fast | $ |
| **Phi-4** (Microsoft) | On-device, low cost, surprisingly capable | Very fast | Free (local) |
| **Llama 3.3 70B** | Open-source, self-host, large tasks | Medium | Free (self-host) |
| **o1 / o3** | Math, code, deep multi-step reasoning | Slow | $$$$ |

!!! tip "Start cheap, upgrade when needed"
    Begin with `gpt-4o-mini` or `Phi-4`. Only upgrade to `gpt-4o` or `o1` if the task clearly requires it.

---

## Part 6: The Transformer Architecture (simplified)

You don't need to understand the math, but knowing the key insight helps:

**Self-attention** is the magic. For each token, the model computes how much "attention" to pay to every other token in the context.

```
"The bank by the river was steep"
  ↑
When processing "bank", the model attends strongly to "river"
→ It understands "bank" means riverbank, not financial institution
```

This is why LLMs understand context so well — every word is interpreted in relation to every other word.

---

## 🧠 Knowledge Check

??? question "1. Approximately how many characters is one token?"
    Roughly **4 characters** (about ¾ of a word). "Hello world" = 2 tokens. A 1,000-word document ≈ 1,300 tokens. This matters for cost (billed per token) and context window limits.

??? question "2. Name two reasons why LLMs hallucinate."
    Any two of these:
    1. **Predicts likely text, not true text** — a plausible-sounding answer scores higher than "I don't know"
    2. **Training data has gaps and noise** — if the web said something wrong enough times, the model learned it
    3. **No external memory** — the model can't "look things up," it generates from learned patterns
    4. **Context window limits** — details from early in a long conversation can be "forgotten"

??? question "3. What is the effect of setting temperature=0 when calling an LLM?"
    The model always picks the **most probable next token** — output becomes **deterministic and reproducible**. Every run with the same input produces the same output. Use `temperature=0` when accuracy and consistency matter more than creativity (e.g., data extraction, structured output).

---

## Summary

| Concept | Key takeaway |
|---------|-------------|
| **Tokens** | ~4 chars each; context windows and costs are measured in tokens |
| **Prediction** | LLMs predict the next token — reasoning is emergent, not programmed |
| **Training** | Pre-training → fine-tuning → RLHF produces helpful assistants |
| **Temperature** | 0 = deterministic; higher = more creative |
| **Context window** | The model's working memory; doesn't persist between requests |
| **Hallucination** | Caused by pattern-matching, not fact-checking — mitigated with tools + RAG |

---

## Next Steps

→ **[Lab 005 — Prompt Engineering](lab-005-prompt-engineering.md)** — Now that you know how LLMs work, learn to write prompts that reliably get the output you want.
