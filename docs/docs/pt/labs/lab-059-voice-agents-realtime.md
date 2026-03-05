---
tags: [voice, realtime-api, webrtc, azure-openai, multimodal, python]
---
# Lab 059: Agentes de Voz com GPT Realtime API

<div class="lab-meta">
  <span><strong>Nível:</strong> <span class="level-badge level-200">L200</span></span>
  <span><strong>Caminho:</strong> Todos os caminhos</span>
  <span><strong>Tempo:</strong> ~75 min</span>
  <span><strong>💰 Custo:</strong> <span class="level-badge cost-free">Gratuito</span> — Usa dataset de sessão (Azure OpenAI opcional)</span>
</div>

## O Que Você Vai Aprender

- Como a **GPT-4o Realtime API** permite conversas de voz full-duplex com latência de ~100 ms
- Conectar clientes via **WebRTC** para streaming de áudio de baixa latência nativo do navegador
- Lidar com **interrupções (barge-in)** — permitindo que os usuários interrompam enquanto o agente ainda está falando
- Integrar **RAG com áudio em tempo real** para que o agente recupere dados de produtos durante a conversa
- Analisar **métricas de sessão de voz**: percentis de latência, sentimento e distribuição de idiomas
- Avaliar **suporte multi-idioma** (en, es, fr) em uma única implantação de agente de voz

---

## Introdução

Agentes de voz estão mudando da tradicional alternância de turnos — onde o usuário fala, espera, e então o agente responde — para **conversa em tempo real**. A GPT-4o Realtime API processa entrada de fala e gera saída de fala simultaneamente, permitindo diálogo natural de ida e volta com latência inferior a 100 ms.

A **OutdoorGear** quer um assistente de voz para consultas sobre produtos. Os clientes ligam, perguntam sobre equipamentos, e o agente responde com detalhes do produto — tudo em tempo real. O sistema deve lidar com interrupções de forma elegante (um cliente pode dizer "espera, na verdade…" no meio de uma resposta), suportar múltiplos idiomas e buscar informações de produtos de um pipeline de RAG em tempo real.

### Visão Geral da Arquitetura

```
┌──────────┐   WebRTC    ┌────────────────────┐   REST/WS   ┌───────────┐
│  Browser  │◄──────────►│  Realtime API      │◄───────────►│  RAG      │
│  (mic +   │  audio     │  (GPT-4o-realtime) │  tool calls │  (product │
│  speaker) │  stream    │  • VAD             │             │   search) │
└──────────┘             │  • Barge-in        │             └───────────┘
                         │  • Turn detection  │
                         └────────────────────┘
```

Conceitos principais:

| Conceito | Descrição |
|---------|-------------|
| **Realtime API** | Endpoint full-duplex de fala para fala — sem pipeline separado de STT/TTS |
| **WebRTC** | Protocolo nativo do navegador para streaming de áudio/vídeo de baixa latência |
| **VAD (Voice Activity Detection)** | Detecta quando o usuário começa/para de falar |
| **Barge-in** | O usuário pode interromper o agente no meio da resposta; o agente para e escuta |
| **Detecção de turno server-side** | A API decide quando um turno do usuário está completo |

---

## Pré-requisitos

```bash
pip install pandas
```

Este lab analisa dados de sessão pré-gravados — nenhuma chave de API ou assinatura do Azure é necessária. Para construir um agente de voz ao vivo, você precisaria de um recurso Azure OpenAI com o modelo `gpt-4o-realtime-preview` implantado.

---

!!! tip "Início Rápido com GitHub Codespaces"
    [![Open in GitHub Codespaces](https://github.com/codespaces/badge.svg)](https://codespaces.new/lcarli/AI-LearningHub?quickstart=1)

    Todas as dependências estão pré-instaladas no devcontainer.


## 📦 Arquivos de Apoio

!!! note "Baixe estes arquivos antes de iniciar o lab"
    Salve todos os arquivos em uma pasta `lab-059/` no seu diretório de trabalho.

| Arquivo | Descrição | Download |
|------|-------------|----------|
| `broken_voice.py` | Exercício de correção de bugs (3 bugs + auto-testes) | [📥 Download](https://github.com/lcarli/AI-LearningHub/raw/main/docs/docs/en/labs/lab-059/broken_voice.py) |
| `voice_sessions.csv` | Dataset | [📥 Download](https://github.com/lcarli/AI-LearningHub/raw/main/docs/docs/en/labs/lab-059/voice_sessions.csv) |

---

## Parte 1: Entendendo a Arquitetura da Realtime API

### Etapa 1: Como a Realtime API difere do Chat Completions

A API padrão de Chat Completions segue um padrão de requisição-resposta: envia texto, recebe texto. A Realtime API é fundamentalmente diferente:

| Recurso | Chat Completions | Realtime API |
|---------|-----------------|--------------|
| Entrada | Texto (JSON) | Stream de áudio (PCM/WebRTC) |
| Saída | Texto (JSON) | Stream de áudio + transcrição de texto |
| Latência | 500–2000 ms | ~100 ms (P50) |
| Duplex | Half-duplex (requisição → resposta) | Full-duplex (simultâneo) |
| Interrupção | Não suportado | Barge-in suportado |
| Protocolo | HTTP REST | WebSocket / WebRTC |

A meta de latência de ~100 ms torna as conversas por voz naturais — comparável a chamadas telefônicas entre humanos.

---

## Parte 2: Carregar e Explorar Dados de Sessão de Voz

### Etapa 2: Carregar [📥 `voice_sessions.csv`](https://github.com/lcarli/AI-LearningHub/raw/main/docs/docs/en/labs/lab-059/voice_sessions.csv)

A OutdoorGear gravou **15 sessões de voz** durante um teste piloto da integração com a Realtime API. Cada sessão captura uma interação com o cliente:

```python
# voice_analysis.py
import pandas as pd

sessions = pd.read_csv("lab-059/voice_sessions.csv")
print(f"Total sessions: {len(sessions)}")
print(f"Columns: {list(sessions.columns)}")
print(sessions.head())
```

**Saída esperada:**

```
Total sessions: 15
Columns: ['session_id', 'scenario', 'duration_sec', 'latency_p50_ms',
           'latency_p95_ms', 'interruptions', 'turns', 'sentiment',
           'model', 'rag_used', 'language']
```

O dataset inclui:

| Coluna | Descrição |
|--------|-------------|
| `session_id` | Identificador único da sessão (S01–S15) |
| `scenario` | Tipo de interação: product_inquiry, order_status, complaint, return_request, faq |
| `duration_sec` | Duração total da sessão em segundos |
| `latency_p50_ms` | Latência mediana de resposta em milissegundos |
| `latency_p95_ms` | Latência de resposta no percentil 95 |
| `interruptions` | Número de vezes que o usuário interrompeu o agente |
| `turns` | Total de turnos conversacionais |
| `sentiment` | Sentimento geral da sessão: positive, neutral, negative |
| `model` | Modelo utilizado (`gpt-4o-realtime`) |
| `rag_used` | Se o RAG foi invocado durante a sessão |
| `language` | Idioma da sessão: en, es, fr |

---

## Parte 3: Análise de Latência

### Etapa 3: Medir a latência de resposta entre sessões

A latência é a métrica mais crítica para agentes de voz — qualquer coisa acima de 200 ms parece lenta.

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

**Saída esperada:**

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

!!! info "Insight de Latência"
    A média P50 de 89,3 ms está bem abaixo da meta de 100 ms. No entanto, sessões de reclamação e devolução consistentemente têm latência mais alta — provavelmente porque elas acionam buscas de RAG mais longas e raciocínio mais complexo.

---

## Parte 4: Análise de Sentimento

### Etapa 4: Analisar a distribuição de sentimento das sessões

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

**Saída esperada:**

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

!!! warning "Padrão"
    Todas as 4 sessões negativas são reclamações ou solicitações de devolução. Três das quatro têm 3+ interrupções — clientes frustrados interrompem com mais frequência.

---

## Parte 5: Padrões de Uso do RAG

### Etapa 5: Analisar quais sessões usam RAG

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

**Saída esperada:**

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

!!! info "Insight sobre RAG"
    As 3 sessões sem RAG são todas cenários de FAQ — perguntas simples que não requerem buscas no banco de dados de produtos. Sessões de FAQ também são as mais curtas (15–20 segundos) e têm a menor latência.

---

## Parte 6: Padrões de Interrupção

### Etapa 6: Analisar o comportamento de barge-in

Barge-in é quando um usuário interrompe o agente no meio de uma resposta. É uma capacidade chave da Realtime API — sem ela, agentes de voz parecem robóticos.

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
print(f"\nHigh-interruption sessions (\u22653):")
print(high_interrupt[["session_id", "scenario", "interruptions", "sentiment"]])
```

**Saída esperada:**

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

!!! info "Insight sobre Barge-in"
    Sessões negativas têm em média 3,25 interrupções vs 0,63 para sessões positivas. Contagens altas de interrupção são um forte sinal de frustração do cliente — um agente poderia detectar isso em tempo real e escalar para um agente humano.

---

## Parte 7: Suporte Multi-Idioma

### Etapa 7: Analisar a distribuição de idiomas

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

**Saída esperada:**

```
Language Distribution:
en    13
es     1
fr     1

EN: 13 sessions, avg P50=90.2ms, avg sentiment: positive
ES: 1 sessions, avg P50=82.0ms, avg sentiment: positive
FR: 1 sessions, avg P50=87.0ms, avg sentiment: positive
```

A Realtime API suporta múltiplos idiomas nativamente — o mesmo modelo lida com inglês, espanhol e francês sem implantações separadas.

---

## 🐛 Exercício de Correção de Bugs

O arquivo `lab-059/broken_voice.py` tem **3 bugs** nas funções de análise de sessão de voz. Execute os auto-testes:

```bash
python lab-059/broken_voice.py
```

Você deve ver **3 testes falhando**:

| Teste | O que verifica | Dica |
|------|---------------|------|
| Teste 1 | Cálculo da latência média P95 | Qual coluna de latência você deve usar? |
| Teste 2 | Contagem de sessões com sentimento negativo | Você está filtrando pelo valor de sentimento correto? |
| Teste 3 | Taxa de uso de RAG como porcentagem | Qual deve ser o denominador? |

Corrija todos os 3 bugs e execute novamente até ver `🎉 All 3 tests passed`.

---


## 🧠 Verificação de Conhecimento

??? question "**Q1 (Múltipla Escolha):** Qual é a latência de resposta alvo da GPT-4o Realtime API?"

    - A) ~500 ms — rápido o suficiente para a maioria das aplicações de voz
    - B) ~100 ms — comparável à latência de conversa entre humanos
    - C) ~10 ms — quase instantâneo para jogos em tempo real
    - D) ~1000 ms — aceitável para processamento de voz em lote

    ??? success "✅ Revelar Resposta"
        **Correta: B) ~100 ms**

        A Realtime API tem como meta ~100 ms de latência P50, que é comparável às pausas naturais na conversa humana. Nessa velocidade, as interações de voz parecem fluidas e naturais. Os dados da sessão confirmam isso — a média P50 em 15 sessões é 89,3 ms.

??? question "**Q2 (Múltipla Escolha):** O que significa 'barge-in' no contexto de agentes de voz?"

    - A) O agente interrompe o usuário para fornecer informações urgentes
    - B) O usuário pode interromper o agente no meio da resposta e o agente para para ouvir
    - C) Múltiplos usuários podem entrar na mesma sessão de voz simultaneamente
    - D) O agente alterna entre idiomas no meio da conversa

    ??? success "✅ Revelar Resposta"
        **Correta: B) O usuário pode interromper o agente no meio da resposta e o agente para para ouvir**

        Barge-in é um recurso crítico de conversa natural por voz. Quando um usuário diz "espera, na verdade…" enquanto o agente ainda está falando, o agente imediatamente para sua resposta atual e processa a nova entrada. Sem barge-in, os usuários precisam esperar o agente terminar — criando uma experiência frustrante e robótica.

??? question "**Q3 (Execute o Lab):** Qual é a latência média P95 em todas as 15 sessões de voz?"

    Calcule `sessions["latency_p95_ms"].mean()`.

    ??? success "✅ Revelar Resposta"
        **187,5 ms**

        Os valores P95 variam de 150 ms (S10, uma sessão de FAQ) a 255 ms (S14, uma reclamação). A média em todas as 15 sessões é (170+185+195+180+155+210+165+175+240+150+178+215+188+255+152) / 15 = **187,5 ms**. Quatro sessões excedem o limiar de 200 ms — todas são reclamações ou solicitações de devolução.

??? question "**Q4 (Execute o Lab):** Quantas sessões têm sentimento negativo?"

    Filtre `sessions[sessions["sentiment"] == "negative"]` e conte.

    ??? success "✅ Revelar Resposta"
        **4 sessões**

        As sessões S03, S06, S09 e S14 têm sentimento negativo. Todas as quatro são reclamações (S03, S09, S14) ou solicitações de devolução (S06). Essas sessões também têm a maior latência e contagens de interrupção, sugerindo uma correlação entre frustração do cliente e desempenho do sistema em cenários complexos.

??? question "**Q5 (Execute o Lab):** Qual porcentagem de sessões usa RAG?"

    Calcule `(sessões com rag_used == True) / total de sessões * 100`.

    ??? success "✅ Revelar Resposta"
        **80% (12 de 15)**

        12 de 15 sessões usam RAG. As 3 sessões sem RAG (S05, S10, S15) são todas cenários de FAQ — perguntas simples que o modelo responde a partir de seus dados de treinamento sem precisar de buscas no banco de dados de produtos. Sessões de FAQ também têm a menor latência, confirmando que o RAG adiciona um overhead de latência mensurável (mas pequeno).

---

## Resumo

| Tópico | O Que Você Aprendeu |
|-------|-----------------|
| Realtime API | Fala para fala full-duplex com ~100 ms de latência |
| WebRTC | Protocolo nativo do navegador para streaming de áudio de baixa latência |
| Barge-in | Usuários podem interromper no meio da resposta para fluxo de conversa natural |
| RAG + Voz | 80% das sessões usam RAG; sessões de FAQ pulam para menor latência |
| Sentimento | Sessões negativas correlacionam com reclamações, alta latência e interrupções |
| Multi-idioma | O mesmo modelo lida com en, es, fr sem implantações separadas |

---

## Próximos Passos

- **[Lab 043](lab-043-multimodal-agents.md)** — Agentes Multimodais com GPT-4o Vision (modalidade complementar)
- **[Lab 060](lab-060-reasoning-models.md)** — Modelos de Raciocínio: Chain-of-Thought com o3 e DeepSeek R1
- **[Lab 019](lab-019-streaming-responses.md)** — Respostas em Streaming (conceitos fundamentais de streaming)
