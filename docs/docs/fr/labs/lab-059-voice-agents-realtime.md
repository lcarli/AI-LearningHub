---
tags: [voice, realtime-api, webrtc, azure-openai, multimodal, python]
---
# Lab 059: Voice Agents with GPT Realtime API

<div class="lab-meta">
  <span><strong>Level:</strong> <span class="level-badge level-200">L200</span></span>
  <span><strong>Path:</strong> All paths</span>
  <span><strong>Time:</strong> ~75 min</span>
  <span><strong>💰 Cost:</strong> <span class="level-badge cost-free">Free</span> — Uses session dataset (Azure OpenAI optional)</span>
</div>

!!! info "Traduction en cours"
    Ce lab est en cours de traduction. Le contenu ci-dessous est en anglais.



## What You'll Learn

- How the **GPT-4o Realtime API** enables full-duplex voice conversations with ~100 ms latency
- Connect clients via **WebRTC** for low-latency, browser-native audio streaming
- Handle **interruptions (barge-in)** — letting users cut in while the agent is still speaking
- Integrate **RAG with real-time audio** so the agent retrieves product data mid-conversation
- Analyze **voice session metrics**: latency percentiles, sentiment, and language distribution
- Evaluate **multi-language support** (en, es, fr) in a single voice agent deployment

---

## Introduction

Voice agents are shifting from traditional turn-taking — where the user speaks, waits, then the agent responds — to **real-time conversation**. The GPT-4o Realtime API processes speech input and generates speech output simultaneously, enabling natural back-and-forth dialogue with sub-100 ms latency.

**OutdoorGear** wants a voice assistant for product inquiries. Customers call in, ask about gear, and the agent responds with product details — all in real time. The system must handle interruptions gracefully (a customer can say "wait, actually…" mid-response), support multiple languages, and pull product information from a RAG pipeline on the fly.

### Architecture Overview

```
┌──────────┐   WebRTC    ┌────────────────────┐   REST/WS   ┌───────────┐
│  Browser  │◄──────────►│  Realtime API      │◄───────────►│  RAG      │
│  (mic +   │  audio     │  (GPT-4o-realtime) │  tool calls │  (product │
│  speaker) │  stream    │  • VAD             │             │   search) │
└──────────┘             │  • Barge-in        │             └───────────┘
                         │  • Turn detection  │
                         └────────────────────┘
```

Key concepts:

| Concept | Description |
|---------|-------------|
| **Realtime API** | Full-duplex speech-to-speech endpoint — no separate STT/TTS pipeline |
| **WebRTC** | Browser-native protocol for low-latency audio/video streaming |
| **VAD (Voice Activity Detection)** | Detects when the user starts/stops speaking |
| **Barge-in** | User can interrupt the agent mid-response; the agent stops and listens |
| **Server-side turn detection** | The API decides when a user turn is complete |

---

## Prerequisites

```bash
pip install pandas
```

This lab analyzes pre-recorded session data — no API key or Azure subscription required. To build a live voice agent, you would need an Azure OpenAI resource with the `gpt-4o-realtime-preview` model deployed.

---

!!! tip "Quick Start with GitHub Codespaces"
    [![Open in GitHub Codespaces](https://github.com/codespaces/badge.svg)](https://codespaces.new/lcarli/AI-LearningHub?quickstart=1)

    All dependencies are pre-installed in the devcontainer.


## 📦 Supporting Files

!!! note "Download these files before starting the lab"
    Save all files to a `lab-059/` folder in your working directory.

| File | Description | Download |
|------|-------------|----------|
| `broken_voice.py` | Bug-fix exercise (3 bugs + self-tests) | [📥 Download](https://github.com/lcarli/AI-LearningHub/raw/main/docs/docs/en/labs/lab-059/broken_voice.py) |
| `voice_sessions.csv` | Dataset | [📥 Download](https://github.com/lcarli/AI-LearningHub/raw/main/docs/docs/en/labs/lab-059/voice_sessions.csv) |

---

## Part 1: Understanding Realtime API Architecture

### Step 1: How the Realtime API differs from Chat Completions

The standard Chat Completions API follows a request-response pattern: send text, receive text. The Realtime API is fundamentally different:

| Feature | Chat Completions | Realtime API |
|---------|-----------------|--------------|
| Input | Text (JSON) | Audio stream (PCM/WebRTC) |
| Output | Text (JSON) | Audio stream + text transcript |
| Latency | 500–2000 ms | ~100 ms (P50) |
| Duplex | Half-duplex (request → response) | Full-duplex (simultaneous) |
| Interruption | Not supported | Barge-in supported |
| Protocol | HTTP REST | WebSocket / WebRTC |

The ~100 ms target latency makes voice conversations feel natural — comparable to human-to-human phone calls.

---

## Part 2: Load and Explore Voice Session Data

### Step 2: Load [📥 `voice_sessions.csv`](https://github.com/lcarli/AI-LearningHub/raw/main/docs/docs/en/labs/lab-059/voice_sessions.csv)

OutdoorGear recorded **15 voice sessions** during a pilot test of their Realtime API integration. Each session captures a customer interaction:

```python
# voice_analysis.py
import pandas as pd

sessions = pd.read_csv("lab-059/voice_sessions.csv")
print(f"Total sessions: {len(sessions)}")
print(f"Columns: {list(sessions.columns)}")
print(sessions.head())
```

**Expected output:**

```
Total sessions: 15
Columns: ['session_id', 'scenario', 'duration_sec', 'latency_p50_ms',
           'latency_p95_ms', 'interruptions', 'turns', 'sentiment',
           'model', 'rag_used', 'language']
```

The dataset includes:

| Column | Description |
|--------|-------------|
| `session_id` | Unique session identifier (S01–S15) |
| `scenario` | Type of interaction: product_inquiry, order_status, complaint, return_request, faq |
| `duration_sec` | Total session duration in seconds |
| `latency_p50_ms` | Median response latency in milliseconds |
| `latency_p95_ms` | 95th percentile response latency |
| `interruptions` | Number of times the user interrupted the agent |
| `turns` | Total conversational turns |
| `sentiment` | Overall session sentiment: positive, neutral, negative |
| `model` | Model used (`gpt-4o-realtime`) |
| `rag_used` | Whether RAG was invoked during the session |
| `language` | Session language: en, es, fr |

---

## Part 3: Latency Analysis

### Step 3: Measure response latency across sessions

Latency is the most critical metric for voice agents — anything above 200 ms feels laggy.

```python
# Latency statistics
avg_p50 = sessions["latency_p50_ms"].mean()
avg_p95 = sessions["latency_p95_ms"].mean()

print(f"Average P50 latency: {avg_p50:.1f} ms")
print(f"Average P95 latency: {avg_p95:.1f} ms")
print(f"Min P50: {sessions['latency_p50_ms'].min()} ms")
print(f"Max P50: {sessions['latency_p50_ms'].max()} ms")

# Sessions exceeding 200ms at P95
slow = sessions[sessions["latency_p95_ms"] > 200]
print(f"\nSessions with P95 > 200ms: {len(slow)}")
print(slow[["session_id", "scenario", "latency_p95_ms"]])
```

**Expected output:**

```
Average P50 latency: 89.3 ms
Average P95 latency: 187.5 ms
Min P50: 75 ms
Max P50: 110 ms

Sessions with P95 > 200ms: 4
  session_id       scenario  latency_p95_ms
       S06  return_request             210
       S09       complaint             240
       S12  return_request             215
       S14       complaint             255
```

!!! info "Latency Insight"
    The average P50 of 89.3 ms is well below the 100 ms target. However, complaint and return sessions consistently have higher latency — likely because they trigger longer RAG lookups and more complex reasoning.

---

## Part 4: Sentiment Analysis

### Step 4: Analyze session sentiment distribution

```python
# Sentiment breakdown
sentiment_counts = sessions["sentiment"].value_counts()
print("Sentiment Distribution:")
print(sentiment_counts)
print(f"\nPositive: {sentiment_counts.get('positive', 0)} sessions")
print(f"Neutral:  {sentiment_counts.get('neutral', 0)} sessions")
print(f"Negative: {sentiment_counts.get('negative', 0)} sessions")

# Which sessions are negative?
negative = sessions[sessions["sentiment"] == "negative"]
print(f"\nNegative sessions:")
print(negative[["session_id", "scenario", "duration_sec", "interruptions"]])
```

**Expected output:**

```
Sentiment Distribution:
positive    8
negative    4
neutral     3

Positive: 8 sessions (S01, S04, S05, S07, S10, S11, S13, S15)
Neutral:  3 sessions (S02, S08, S12)
Negative: 4 sessions (S03, S06, S09, S14)

Negative sessions:
  session_id       scenario  duration_sec  interruptions
       S03       complaint           120              3
       S06  return_request            65              1
       S09       complaint            90              4
       S14       complaint           105              5
```

!!! warning "Pattern"
    All 4 negative sessions are either complaints or return requests. Three of the four have 3+ interruptions — frustrated customers interrupt more frequently.

---

## Part 5: RAG Usage Patterns

### Step 5: Analyze which sessions use RAG

```python
# RAG usage
rag_used = sessions[sessions["rag_used"] == True]
rag_not_used = sessions[sessions["rag_used"] == False]

print(f"RAG used: {len(rag_used)}/{len(sessions)} sessions ({len(rag_used)/len(sessions)*100:.0f}%)")
print(f"RAG not used: {len(rag_not_used)} sessions")
print(f"\nSessions without RAG:")
print(rag_not_used[["session_id", "scenario", "sentiment"]])

# Compare latency: RAG vs no-RAG
print(f"\nAvg P50 with RAG:    {rag_used['latency_p50_ms'].mean():.1f} ms")
print(f"Avg P50 without RAG: {rag_not_used['latency_p50_ms'].mean():.1f} ms")
```

**Expected output:**

```
RAG used: 12/15 sessions (80%)
RAG not used: 3 sessions

Sessions without RAG:
  session_id scenario sentiment
       S05      faq  positive
       S10      faq  positive
       S15      faq  positive

Avg P50 with RAG:    92.6 ms
Avg P50 without RAG: 76.3 ms
```

!!! info "RAG Insight"
    The 3 sessions without RAG are all FAQ scenarios — simple questions that don't require product database lookups. FAQ sessions are also the shortest (15–20 seconds) and have the lowest latency.

---

## Part 6: Interruption Patterns

### Step 6: Analyze barge-in behavior

Barge-in is when a user interrupts the agent mid-response. It's a key capability of the Realtime API — without it, voice agents feel robotic.

```python
# Interruption analysis
print("Interruptions per session:")
print(sessions[["session_id", "scenario", "interruptions", "sentiment"]].to_string(index=False))

# Correlation between interruptions and sentiment
avg_interruptions = sessions.groupby("sentiment")["interruptions"].mean()
print(f"\nAvg interruptions by sentiment:")
print(avg_interruptions)

# Sessions with most interruptions
high_interrupt = sessions[sessions["interruptions"] >= 3]
print(f"\nHigh-interruption sessions (≥3):")
print(high_interrupt[["session_id", "scenario", "interruptions", "sentiment"]])
```

**Expected output:**

```
Avg interruptions by sentiment:
negative    3.25
neutral     0.67
positive    0.63

High-interruption sessions (≥3):
  session_id   scenario  interruptions sentiment
       S03  complaint              3  negative
       S09  complaint              4  negative
       S14  complaint              5  negative
```

!!! info "Barge-in Insight"
    Negative sessions average 3.25 interruptions vs 0.63 for positive sessions. High interruption counts are a strong signal of customer frustration — an agent could detect this in real time and escalate to a human agent.

---

## Part 7: Multi-Language Support

### Step 7: Analyze language distribution

```python
# Language breakdown
lang_counts = sessions["language"].value_counts()
print("Language Distribution:")
print(lang_counts)

# Performance by language
for lang in sessions["language"].unique():
    lang_sessions = sessions[sessions["language"] == lang]
    print(f"\n{lang.upper()}: {len(lang_sessions)} sessions, "
          f"avg P50={lang_sessions['latency_p50_ms'].mean():.1f}ms, "
          f"avg sentiment: {lang_sessions['sentiment'].mode().iloc[0]}")
```

**Expected output:**

```
Language Distribution:
en    13
es     1
fr     1

EN: 13 sessions, avg P50=90.2ms, avg sentiment: positive
ES: 1 sessions, avg P50=82.0ms, avg sentiment: positive
FR: 1 sessions, avg P50=87.0ms, avg sentiment: positive
```

The Realtime API supports multiple languages natively — the same model handles English, Spanish, and French without separate deployments.

---

## 🐛 Bug-Fix Exercise

The file `lab-059/broken_voice.py` has **3 bugs** in the voice session analysis functions. Run the self-tests:

```bash
python lab-059/broken_voice.py
```

You should see **3 failed tests**:

| Test | What it checks | Hint |
|------|---------------|------|
| Test 1 | Average P95 latency calculation | Which latency column should you use? |
| Test 2 | Count of negative sentiment sessions | Are you filtering for the right sentiment value? |
| Test 3 | RAG usage rate as a percentage | What should the denominator be? |

Fix all 3 bugs and re-run until you see `🎉 All 3 tests passed`.

---


## 🧠 Knowledge Check

??? question "**Q1 (Multiple Choice):** What is the target response latency for the GPT-4o Realtime API?"

    - A) ~500 ms — fast enough for most voice applications
    - B) ~100 ms — comparable to human-to-human conversation latency
    - C) ~10 ms — near-instantaneous for real-time gaming
    - D) ~1000 ms — acceptable for batch voice processing

    ??? success "✅ Reveal Answer"
        **Correct: B) ~100 ms**

        The Realtime API targets ~100 ms P50 latency, which is comparable to the natural pauses in human conversation. At this speed, voice interactions feel fluid and natural. The session data confirms this — the average P50 across 15 sessions is 89.3 ms.

??? question "**Q2 (Multiple Choice):** What does 'barge-in' mean in the context of voice agents?"

    - A) The agent interrupts the user to provide urgent information
    - B) The user can interrupt the agent mid-response and the agent stops to listen
    - C) Multiple users can join the same voice session simultaneously
    - D) The agent switches between languages mid-conversation

    ??? success "✅ Reveal Answer"
        **Correct: B) The user can interrupt the agent mid-response and the agent stops to listen**

        Barge-in is a critical feature of natural voice conversation. When a user says "wait, actually…" while the agent is still speaking, the agent immediately stops its current response and processes the new input. Without barge-in, users must wait for the agent to finish — creating a frustrating, robotic experience.

??? question "**Q3 (Run the Lab):** What is the average P95 latency across all 15 voice sessions?"

    Calculate `sessions["latency_p95_ms"].mean()`.

    ??? success "✅ Reveal Answer"
        **187.5 ms**

        The P95 values range from 150 ms (S10, an FAQ session) to 255 ms (S14, a complaint). The mean across all 15 sessions is (170+185+195+180+155+210+165+175+240+150+178+215+188+255+152) / 15 = **187.5 ms**. Four sessions exceed the 200 ms threshold — all are complaints or return requests.

??? question "**Q4 (Run the Lab):** How many sessions have negative sentiment?"

    Filter `sessions[sessions["sentiment"] == "negative"]` and count.

    ??? success "✅ Reveal Answer"
        **4 sessions**

        Sessions S03, S06, S09, and S14 have negative sentiment. All four are either complaints (S03, S09, S14) or return requests (S06). These sessions also have the highest latency and interruption counts, suggesting a correlation between customer frustration and system performance under complex scenarios.

??? question "**Q5 (Run the Lab):** What percentage of sessions use RAG?"

    Calculate `(sessions with rag_used == True) / total sessions * 100`.

    ??? success "✅ Reveal Answer"
        **80% (12 out of 15)**

        12 of 15 sessions use RAG. The 3 sessions without RAG (S05, S10, S15) are all FAQ scenarios — simple questions that the model answers from its training data without needing product database lookups. FAQ sessions also have the lowest latency, confirming that RAG adds a measurable (but small) latency overhead.

---

## Summary

| Topic | What You Learned |
|-------|-----------------|
| Realtime API | Full-duplex speech-to-speech with ~100 ms latency |
| WebRTC | Browser-native protocol for low-latency audio streaming |
| Barge-in | Users can interrupt mid-response for natural conversation flow |
| RAG + Voice | 80% of sessions use RAG; FAQ sessions skip it for lower latency |
| Sentiment | Negative sessions correlate with complaints, high latency, and interruptions |
| Multi-language | Same model handles en, es, fr without separate deployments |

---

## Next Steps

- **[Lab 043](lab-043-multimodal-agents.md)** — Multimodal Agents with GPT-4o Vision (complementary modality)
- **[Lab 060](lab-060-reasoning-models.md)** — Reasoning Models: Chain-of-Thought with o3 and DeepSeek R1
- **[Lab 019](lab-019-streaming-responses.md)** — Streaming Responses (foundational streaming concepts)
