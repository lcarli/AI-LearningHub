---
tags: [free, beginner, no-account-needed, llm]
---
# Lab 004: Como LLMs Funcionam

<div class="lab-meta">
  <span><strong>Nível:</strong> <span class="level-badge level-50">L50</span></span>
  <span><strong>Trilha:</strong> Todas as trilhas</span>
  <span><strong>Tempo:</strong> ~20 min</span>
  <span><strong>💰 Custo:</strong> <span class="level-badge cost-free">Gratuito</span> — Nenhuma conta necessária</span>
</div>

## O que Você Vai Aprender

- O que realmente é um Modelo de Linguagem Grande (LLM) por baixo dos panos
- Como o treinamento funciona: pré-treinamento, ajuste fino, RLHF
- O que tokens, janelas de contexto e temperatura significam na prática
- Por que LLMs alucinam — e como mitigar isso
- A diferença entre modelos: GPT-4o, Phi-4, Llama, Claude

---

## Introdução

Você provavelmente já usou ChatGPT ou GitHub Copilot. Mas o que realmente acontece quando você digita uma mensagem e recebe uma resposta? Entender a mecânica dos LLMs torna você um construtor de agentes dramaticamente melhor — você saberá *por que* certos prompts funcionam, *por que* agentes cometem erros e *como* projetar contornando suas limitações.

---

## Parte 1: O que é um Modelo de Linguagem Grande?

Um LLM é uma rede neural treinada para **prever o próximo token** dada uma sequência de tokens.

Só isso. Todo o resto — raciocínio, geração de código, sumarização, chat — é uma capacidade emergente que surge de fazer isso em *escala massiva* com *enormes quantidades de texto*.

### Tokens

Um **token** é a unidade básica que um LLM processa. É aproximadamente ¾ de uma palavra (cerca de 4 caracteres).

![Tokenização](../../assets/diagrams/tokenization.svg)

!!! info "Por que tokens importam para agentes"
    - Janelas de contexto são medidas em tokens, não em palavras
    - Custos de API são cobrados por token
    - Documentos longos precisam ser divididos em pedaços para caber na janela de contexto

### O ciclo de predição

Quando você envia uma mensagem, o LLM:

1. Converte seu texto em uma sequência de IDs de tokens
2. Passa-os através de bilhões de operações matemáticas (camadas transformer)
3. Produz uma distribuição de probabilidade sobre todo o vocabulário (~100.000 tokens)
4. Amostra o próximo token com base nessa distribuição
5. Anexa-o à sequência e repete a partir do passo 2

![Ciclo de Predição do LLM](../../assets/diagrams/llm-prediction-loop.svg)

O LLM não "sabe" fatos — ele aprendeu **padrões estatísticos** de texto. Quando ele diz "Paris", é porque "Paris" quase sempre segue aquela frase nos seus dados de treinamento.

??? question "🤔 Verifique Seu Entendimento"
    Um LLM responde corretamente "A capital da França é Paris." O modelo *sabe* esse fato da mesma forma que um humano?

    ??? success "Resposta"
        Não. O LLM aprendeu **padrões estatísticos** dos seus dados de treinamento — "Paris" quase sempre segue "A capital da França é" no texto em que ele foi treinado. Ele prevê o próximo token mais provável, não fatos verificados. É por isso que LLMs também podem produzir respostas erradas com confiança (alucinações).

---

## Parte 2: Treinando um LLM

### Estágio 1 — Pré-treinamento

O modelo lê **trilhões de tokens** da internet, livros, código e artigos científicos. Ele aprende estrutura da linguagem, fatos, padrões de raciocínio e conhecimento geral puramente prevendo o próximo token.

```
Training data: Wikipedia + books + GitHub + web pages + ...
Goal: minimize prediction error across all that text
Result: a "base model" that can complete text
```

**GPT-4o, Llama 3, Phi-4** todos começam como modelos base.

### Estágio 2 — Ajuste Fino por Instrução (SFT)

O modelo base é treinado com **exemplos de conversas** — pares (prompt, resposta ideal). Isso o ensina a ser útil, seguir instruções e responder de forma conversacional.

### Estágio 3 — RLHF (Aprendizado por Reforço com Feedback Humano)

Avaliadores humanos comparam pares de respostas e escolhem a melhor. Um **modelo de recompensa** é treinado com essas preferências. O LLM é então ajustado para maximizar a pontuação do modelo de recompensa.

É por isso que o ChatGPT parece mais polido e alinhado do que um modelo base bruto.

![Pipeline de Treinamento do LLM](../../assets/diagrams/llm-training-pipeline.svg)

??? question "🤔 Verifique Seu Entendimento"
    Qual é o propósito do RLHF (Aprendizado por Reforço com Feedback Humano) no treinamento de LLMs, e por que o pré-treinamento sozinho não consegue alcançar o mesmo resultado?

    ??? success "Resposta"
        O RLHF alinha o modelo com **preferências humanas** — tornando as respostas mais úteis, seguras e conversacionais. O pré-treinamento apenas ensina o modelo a prever o próximo token a partir de padrões de texto. Sem o RLHF, o modelo pode produzir respostas tecnicamente corretas mas inúteis, inseguras ou com formatação estranha.

---

## Parte 3: Parâmetros-Chave

### Janela de Contexto

A **janela de contexto** é quanto texto o modelo pode "ver" de uma vez — sua memória de trabalho.

| Modelo | Janela de Contexto |
|-------|---------------|
| GPT-4o | 128.000 tokens (~96.000 palavras) |
| GPT-4o-mini | 128.000 tokens |
| Phi-4 | 16.000 tokens |
| Llama 3.3 70B | 128.000 tokens |
| Claude 3.5 Sonnet | 200.000 tokens |

![Comparação de Janela de Contexto](../../assets/diagrams/context-window.svg)

!!! warning "Janela de contexto ≠ memória ilimitada"
    O modelo lê a janela de contexto *inteira* a cada requisição. Contexto mais longo = mais lento + mais caro. Agentes usam RAG e sumarização para gerenciar conversas longas.

### Temperatura

**Temperatura** controla o quão aleatória é a saída.

![Comparação de Temperatura](../../assets/diagrams/temperature-comparison.svg)

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

### Top-p (amostragem por núcleo)

Uma alternativa à temperatura. Amostra apenas do menor conjunto de tokens cuja probabilidade cumulativa excede `top_p`.

- `top_p=0.1` → muito conservador
- `top_p=0.9` → permite saídas diversas

??? question "🤔 Verifique Seu Entendimento"
    Você está construindo um agente que gera consultas SQL a partir de linguagem natural. Deve usar temperatura alta ou baixa, e por quê?

    ??? success "Resposta"
        Use **temperatura baixa (0.0)**. Consultas SQL precisam ser determinísticas e sintaticamente corretas. Temperatura alta introduz aleatoriedade que pode produzir SQL inválido ou inconsistente. Para tarefas de saída estruturada como geração de código, extração de dados e SQL, sempre prefira temperature=0.

---

## Parte 4: Por que LLMs Alucinam

![Causas e Soluções de Alucinação](../../assets/diagrams/hallucination-causes.svg)

Alucinação (gerar informação falsa que soa confiante) acontece porque:

1. **O modelo prevê texto provável, não texto verdadeiro.** Uma resposta que parece plausível pode ter pontuação mais alta do que "Eu não sei."
2. **Os dados de treinamento têm lacunas e ruído.** Se a web diz algo errado com frequência suficiente, o modelo aprendeu isso.
3. **Sem memória externa.** O modelo não "verifica" fatos — ele gera a partir de padrões.

### Como agentes mitigam alucinação

| Técnica | Como ajuda |
|-----------|-------------|
| **RAG** | Dá ao modelo documentos reais para citar em vez de depender dos dados de treinamento |
| **Chamada de ferramentas** | Permite que o modelo chame APIs/bancos de dados para dados em tempo real |
| **Temperatura baixa** | Reduz criatividade quando precisão importa |
| **Regras no prompt de sistema** | "Nunca invente dados; use apenas saídas de ferramentas" |
| **Saída estruturada** | Força o modelo a produzir esquema JSON — mais fácil de validar |
| **Avaliação** | Mede fundamentação, coerência e factualidade automaticamente |

---

## Parte 5: Escolhendo um Modelo

Nem toda tarefa precisa do GPT-4o. Escolher o modelo certo economiza dinheiro e latência.

| Modelo | Melhor para | Velocidade | Custo |
|-------|---------|-------|------|
| **GPT-4o** | Raciocínio complexo, contexto longo, multimodal | Média | $$$ |
| **GPT-4o-mini** | Maioria das tarefas do dia a dia | Rápida | $ |
| **Phi-4** (Microsoft) | No dispositivo, baixo custo, surpreendentemente capaz | Muito rápida | Gratuito (local) |
| **Llama 3.3 70B** | Open-source, auto-hospedagem, tarefas grandes | Média | Gratuito (auto-hospedagem) |
| **o1 / o3** | Matemática, código, raciocínio profundo multi-etapas | Lenta | $$$$ |

!!! tip "Comece barato, escale quando necessário"
    Comece com `gpt-4o-mini` ou `Phi-4`. Só atualize para `gpt-4o` ou `o1` se a tarefa claramente exigir.

---

## Parte 6: A Arquitetura Transformer (simplificada)

Você não precisa entender a matemática, mas conhecer o insight principal ajuda:

**Auto-atenção** é a mágica. Para cada token, o modelo calcula quanta "atenção" prestar a cada outro token no contexto.

![Mecanismo de Auto-Atenção](../../assets/diagrams/self-attention.svg)

É por isso que LLMs entendem contexto tão bem — cada palavra é interpretada em relação a todas as outras palavras.

??? question "🤔 Verifique Seu Entendimento"
    Na frase "O banco perto do rio era íngreme," como o mecanismo de auto-atenção ajuda o modelo a entender que "banco" significa uma margem de rio e não uma instituição financeira?

    ??? success "Resposta"
        A auto-atenção calcula quanta "atenção" cada token deve prestar a cada outro token. Ao processar "banco," o modelo presta forte atenção a "rio" — a relação contextual entre essas palavras muda a interpretação para **margem de rio** em vez de instituição financeira. Cada palavra é interpretada em relação a todas as outras palavras no contexto.

---

## 🧠 Verificação de Conhecimento

??? question "**Q1 (Múltipla Escolha):** Aproximadamente quantos tokens tem a frase *'Hello world'*?"

    - A) 1 token
    - B) 2 tokens
    - C) 6 tokens
    - D) 10 tokens

    ??? success "✅ Revelar Resposta"
        **Correta: B — 2 tokens**

        "Hello" é 1 token e "world" é 1 token. Como regra geral, 1 token ≈ 4 caracteres ≈ ¾ de uma palavra. Um documento de 1.000 palavras tem aproximadamente 1.300 tokens. Isso importa tanto para custo (APIs cobram por token) quanto para limites da janela de contexto (GPT-4o tem uma janela de contexto de 128K tokens).

??? question "**Q2 (Múltipla Escolha):** Você está chamando um LLM para extração de dados estruturados (por exemplo, extraindo JSON de um e-mail de cliente). Qual configuração de temperatura é mais apropriada?"

    - A) temperature = 1.5 (alta criatividade)
    - B) temperature = 0.8 (criatividade moderada)
    - C) temperature = 0.0 (determinístico)
    - D) temperature = 2.0 (aleatoriedade máxima)

    ??? success "✅ Revelar Resposta"
        **Correta: C — temperature = 0.0**

        Quando precisão e reprodutibilidade importam mais do que criatividade, use `temperature=0`. Isso faz o modelo sempre escolher o próximo token mais provável — então a mesma entrada sempre produz a mesma saída. Para escrita criativa: use 0.7–1.0. Para extração de dados, geração de SQL ou formatação de argumentos de ferramentas: use 0.

??? question "**Q3 (Múltipla Escolha):** Um LLM afirma com confiança que uma cidade fictícia no Brasil tem uma população de 2,3 milhões. Esta cidade não existe. Qual é a causa principal?"

    - A) A janela de contexto do modelo era muito pequena
    - B) A temperatura estava configurada muito alta
    - C) O modelo prevê texto com aparência provável em vez de fatos verificados — ele fez correspondência de padrões com cidades reais similares
    - D) O prompt de sistema estava faltando

    ??? success "✅ Revelar Resposta"
        **Correta: C — LLMs preveem texto provável, não texto factual**

        LLMs são treinados para prever o próximo token que é *estatisticamente provável* dado o contexto. Uma cidade inventada que se assemelha a cidades reais no padrão ("São Paulo tem 12M, Rio tem 6M...") leva o modelo a gerar uma resposta que soa plausível mas é fabricada. Isso é alucinação. A solução é RAG ou chamada de ferramentas — forçar o modelo a consultar fatos em vez de prevê-los.

---

## Resumo

| Conceito | Principal aprendizado |
|---------|-------------|
| **Tokens** | ~4 caracteres cada; janelas de contexto e custos são medidos em tokens |
| **Predição** | LLMs preveem o próximo token — raciocínio é emergente, não programado |
| **Treinamento** | Pré-treinamento → ajuste fino → RLHF produz assistentes úteis |
| **Temperatura** | 0 = determinístico; maior = mais criativo |
| **Janela de contexto** | A memória de trabalho do modelo; não persiste entre requisições |
| **Alucinação** | Causada por correspondência de padrões, não verificação de fatos — mitigada com ferramentas + RAG |

---

## Próximos Passos

→ **[Lab 005 — Engenharia de Prompt](lab-005-prompt-engineering.md)** — Agora que você sabe como LLMs funcionam, aprenda a escrever prompts que obtêm de forma confiável a saída desejada.
