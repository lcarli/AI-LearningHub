---
tags: [free, beginner, no-account-needed, rag]
---
# Lab 006: O que é RAG?

<div class="lab-meta">
  <span><strong>Nível:</strong> <span class="level-badge level-50">L50</span></span>
  <span><strong>Trilha:</strong> <a href="../paths/rag/">📚 RAG</a></span>
  <span><strong>Tempo:</strong> ~20 min</span>
  <span><strong>💰 Custo:</strong> <span class="level-badge cost-free">Gratuito</span> — Nenhuma conta necessária</span>
</div>

## O que Você Vai Aprender

- Por que LLMs precisam de conhecimento externo (e por que os dados de treinamento sozinhos não são suficientes)
- O pipeline completo de RAG: ingestão → fragmentação → embedding → armazenamento → recuperação → geração
- A diferença entre **busca por palavras-chave**, **busca semântica** e **busca híbrida**
- Quando usar RAG vs. ajuste fino vs. apenas uma janela de contexto maior
- Arquiteturas RAG do mundo real

---

## Introdução

Imagine que você construiu um agente de IA para sua empresa. Ele responde perguntas lindamente — até que um usuário pergunte sobre um produto lançado no mês passado, ou uma política atualizada na semana passada.

O LLM não sabe. Seus dados de treinamento têm uma data de corte. E mesmo que a informação existisse nos dados de treinamento, o modelo pode não tê-la memorizado com precisão.

**RAG (Geração Aumentada por Recuperação)** resolve isso conectando o LLM ao seu próprio conhecimento atualizado no momento da consulta — sem retreinar o modelo.

![Pipeline RAG](../../assets/diagrams/rag-pipeline.svg)

---

## 📦 Arquivos de Apoio

!!! note "Baixe estes arquivos antes de iniciar o lab"
    Salve todos os arquivos em uma pasta `lab-006/` no seu diretório de trabalho.

| Arquivo | Descrição | Download |
|------|-------------|----------|
| `faq_backpacks.txt` | Arquivo de base de conhecimento FAQ | [📥 Download](https://github.com/lcarli/AI-LearningHub/raw/main/docs/docs/en/labs/lab-006/faq_backpacks.txt) |
| `faq_clothing.txt` | Arquivo de base de conhecimento FAQ | [📥 Download](https://github.com/lcarli/AI-LearningHub/raw/main/docs/docs/en/labs/lab-006/faq_clothing.txt) |
| `faq_footwear.txt` | Arquivo de base de conhecimento FAQ | [📥 Download](https://github.com/lcarli/AI-LearningHub/raw/main/docs/docs/en/labs/lab-006/faq_footwear.txt) |
| `faq_sleeping_bags.txt` | Arquivo de base de conhecimento FAQ | [📥 Download](https://github.com/lcarli/AI-LearningHub/raw/main/docs/docs/en/labs/lab-006/faq_sleeping_bags.txt) |
| `faq_tents.txt` | Arquivo de base de conhecimento FAQ | [📥 Download](https://github.com/lcarli/AI-LearningHub/raw/main/docs/docs/en/labs/lab-006/faq_tents.txt) |

---

## Parte 1: O Problema Central

LLMs têm duas limitações de conhecimento:

| Limitação | Descrição | Exemplo |
|-----------|-------------|---------|
| **Corte de treinamento** | O conhecimento para em uma data | "O que aconteceu na semana passada?" |
| **Dados privados** | Nunca viu seus documentos | "Qual é nossa política de reembolso?" |
| **Risco de alucinação** | Pode confabular quando incerto | Inventa resposta que soa plausível mas está errada |

A solução ingênua — "coloque todos os seus documentos no prompt" — não escala. Um manual de 500 páginas tem ~375.000 tokens. A maioria dos LLMs limita em 128.000 tokens, e mesmo que não limitassem, você pagaria por todos esses tokens em cada consulta individual.

**A resposta do RAG:** Recupere apenas as partes *relevantes*, exatamente quando você precisa delas.

---

## Parte 2: O Pipeline RAG

RAG tem duas fases distintas:

### Fase 1 — Ingestão (executa uma vez, ou por agendamento)

```
Your documents (PDFs, Word, web pages, databases...)
         │
         ▼
    1. LOAD       ── Read content from source
         │
         ▼
    2. CHUNK      ── Split into overlapping segments (~512 tokens each)
         │
         ▼
    3. EMBED      ── Convert each chunk to a vector (list of numbers)
         │
         ▼
    4. STORE      ── Save chunks + vectors in a vector database
                     (pgvector, Azure AI Search, Chroma, Pinecone...)
```

### Fase 2 — Recuperação + Geração (executa em cada consulta)

```
User asks: "What is the return policy for outdoor equipment?"
         │
         ▼
    5. EMBED QUERY ── Convert user question to a vector
         │
         ▼
    6. SEARCH     ── Find the most similar chunks in the vector DB
                     (cosine similarity / vector distance)
         │
         ▼
    7. AUGMENT    ── Inject retrieved chunks into the prompt:
                     "Answer based on these documents: [chunks]"
         │
         ▼
    8. GENERATE   ── LLM answers, grounded in real data
         │
         ▼
    User gets: "Our return policy for outdoor equipment allows returns
               within 30 days with original receipt..."
```

??? question "🤔 Verifique Seu Entendimento"
    No pipeline RAG, qual é a diferença entre a **fase de ingestão** e a **fase de recuperação**, e com que frequência cada uma executa?

    ??? success "Resposta"
        A **fase de ingestão** (Carregar → Fragmentar → Fazer Embedding → Armazenar) executa **uma vez** (ou por agendamento) para preparar seus documentos. A **fase de recuperação** (Fazer embedding da consulta → Buscar → Aumentar → Gerar) executa **a cada consulta do usuário** para encontrar fragmentos relevantes e gerar uma resposta. A ingestão é um processo em lote; a recuperação é em tempo real.

---

## Parte 3: Estratégias de Fragmentação

Como você divide documentos importa enormemente.

| Estratégia | Como | Melhor para |
|----------|-----|---------|
| **Tamanho fixo** | Divide a cada N tokens | Simples, rápido, funciona para a maioria dos casos |
| **Sentença/parágrafo** | Divide em limites naturais | Melhor preservação de contexto |
| **Semântica** | Divide quando o tópico muda | Melhor qualidade, mais complexo |
| **Recursiva** | Tenta parágrafo → sentença → palavra | Bom padrão para conteúdo misto |

**Sobreposição é importante.** Se você dividir exatamente em 512 tokens, informação relevante que cruza um limite se perde. Adicione 50–100 tokens de sobreposição entre fragmentos.

```
Chunk 1: tokens 1–512
Chunk 2: tokens 462–974   ← 50-token overlap
Chunk 3: tokens 924–1436  ← 50-token overlap
```

??? question "🤔 Verifique Seu Entendimento"
    Por que é importante adicionar **sobreposição** entre fragmentos ao dividir documentos?

    ??? success "Resposta"
        Sem sobreposição, informação relevante que cruza um limite de fragmento fica **dividida entre dois fragmentos** e pode se perder durante a recuperação. Adicionar 50–100 tokens de sobreposição garante que o contexto nas bordas seja preservado em ambos os fragmentos adjacentes, melhorando a qualidade da recuperação.

---

## Parte 4: Tipos de Busca

### Busca por Palavras-chave (BM25)
Busca tradicional — corresponde palavras exatas. Rápida, interpretável, mas perde sinônimos e intenção.

```
Query: "waterproof jacket"
Finds: documents containing exactly "waterproof" and "jacket"
Misses: "rain-resistant coat", "weatherproof outerwear"
```

### Busca Semântica (Vetorial)
Compara significado, não palavras. Encontra conteúdo conceitualmente similar.

```
Query: "waterproof jacket"
Finds: "rain-resistant coat", "all-weather outerwear", "waterproof jacket"
Based on: vector similarity in embedding space
```

### Busca Híbrida (BM25 + Vetorial)
O melhor dos dois mundos — combina pontuações de palavras-chave e semânticas.

```
Final score = α × keyword_score + (1-α) × semantic_score
```

A maioria dos sistemas RAG em produção usa busca híbrida porque ela lida tanto com buscas exatas ("SKU-12345") quanto com consultas semânticas ("algo para acampar na chuva").

??? question "🤔 Verifique Seu Entendimento"
    Um usuário busca por "rain-resistant coat" mas o documento contém apenas a frase "waterproof jacket." A busca por palavras-chave vai encontrá-lo? E a busca semântica? Por quê?

    ??? success "Resposta"
        **A busca por palavras-chave vai perder** — não há palavras correspondentes entre "rain-resistant coat" e "waterproof jacket." **A busca semântica vai encontrar** porque ela compara significado via similaridade vetorial, não palavras exatas. Ambas as frases têm significados muito similares e terão representações vetoriais similares. É por isso que a busca híbrida (combinando ambas) é preferida em produção.

---

## Parte 5: RAG vs. Ajuste Fino vs. Contexto Grande

Uma pergunta comum: "Por que não simplesmente ajustar finamente o modelo nos meus dados?"

| Abordagem | Custo | Atualidade | Melhor para |
|----------|------|-----------|---------|
| **RAG** | Baixo | ✅ Tempo real | Dados dinâmicos, documentos, Q&A |
| **Ajuste fino** | Alto | ❌ Estático | Tom, estilo, vocabulário de domínio |
| **Contexto grande** | Médio | ✅ Por requisição | Conjuntos de dados pequenos que cabem no contexto |
| **RAG + Ajuste fino** | Alto | ✅ Tempo real | Sistemas em produção que precisam de ambos |

**Regra prática:** Use RAG para *conhecimento* (fatos, documentos). Use ajuste fino para *comportamento* (tom, estilo, formato). Eles são complementares, não concorrentes.

---

## Parte 6: Métricas de Qualidade RAG

Um sistema RAG pode falhar em dois pontos:

| Falha | Sintoma | Correção |
|---------|---------|-----|
| **Recuperação ruim** | Fragmentos recuperados não são relevantes | Melhor fragmentação, busca híbrida, re-ranking |
| **Geração ruim** | LLM ignora ou usa mal o conteúdo recuperado | Prompt de sistema mais forte, exigência de citação |

Métricas-chave usadas no [Lab 035](lab-035-agent-evaluation.md) e [Lab 042](lab-042-enterprise-rag.md):

- **Fundamentação**: A resposta é suportada pelos documentos recuperados?
- **Relevância**: Os fragmentos recuperados são realmente relevantes para a pergunta?
- **Coerência**: A resposta é bem estruturada e legível?
- **Fidelidade**: A resposta permanece fiel ao material de origem?

---

## Arquiteturas RAG do Mundo Real

### RAG Básico
```
User → Embed query → Vector search → Augment prompt → LLM → Answer
```

### RAG Agêntico (abordado no Lab 026)
```
User → Agent decides: search? what query? how many chunks?
     → Multiple targeted searches
     → Agent synthesizes results
     → Answer with citations
```

### RAG Corretivo
```
User → Retrieve → Grade relevance → If poor: web search fallback
     → Augment → Generate → Self-check → Answer
```

---


## 🧠 Verificação de Conhecimento

??? question "**Q1 (Múltipla Escolha):** O que significa RAG, e qual problema ele resolve principalmente?"

    - A) Recursive Augmented Graph — resolve problemas de raciocínio multi-etapas
    - B) Retrieval-Augmented Generation — fundamenta respostas do LLM em dados privados ou atualizados sem retreinamento
    - C) Randomized Agent Generation — torna respostas de agentes menos determinísticas
    - D) Ranked Answer Generation — melhora o ranking de resultados de busca

    ??? success "✅ Revelar Resposta"
        **Correta: B — Retrieval-Augmented Generation**

        RAG conecta o LLM ao seu próprio conhecimento no momento da consulta. Em vez do modelo depender dos dados de treinamento (que têm uma data de corte e não incluem seus documentos privados), o RAG recupera os fragmentos mais relevantes do seu armazenamento de dados e os inclui no prompt. Sem necessidade de retreinamento.

??? question "**Q2 (Múltipla Escolha):** No pipeline de ingestão RAG, qual etapa vem imediatamente ANTES de armazenar vetores no banco de dados?"

    - A) Fragmentação
    - B) Carregamento de documentos
    - C) Geração de embeddings
    - D) Re-ranking semântico

    ??? success "✅ Revelar Resposta"
        **Correta: C — Geração de embeddings**

        A ordem de ingestão é: **Carregar → Fragmentar → Fazer Embedding → Armazenar**. Você primeiro carrega documentos brutos, divide-os em fragmentos menores (~512 tokens com sobreposição), *depois* converte cada fragmento em um embedding vetorial usando o modelo de embedding, e finalmente armazena esses vetores no banco de dados vetorial. Re-ranking semântico é uma etapa de recuperação, não de ingestão.

??? question "**Q3 (Execute o Lab):** Abra o arquivo `lab-006/faq_tents.txt`. Quantos pares de P&R ele contém, e qual é o tópico da ÚLTIMA pergunta?"

    Abra `lab-006/faq_tents.txt` e conte os pares de P&R. A última pergunta começa com "Q:".

    ??? success "✅ Revelar Resposta"
        **5 pares de P&R. A última pergunta é: "Can I use a 2-person tent solo?"**

        [📥 `faq_tents.txt`](https://github.com/lcarli/AI-LearningHub/raw/main/docs/docs/en/labs/lab-006/faq_tents.txt) contém exatamente 5 pares de P&R cobrindo: escolha de barraca para mochileiro solo, 3-estações vs 4-estações, impermeabilização, materiais de hastes e uso de barraca 2P solo. Este é o tipo de base de conhecimento que um sistema RAG ingeriria — cada par de P&R é um fragmento natural para embedding.

---

## Resumo

| Conceito | Principal aprendizado |
|---------|-------------|
| **Por que RAG** | LLMs não conhecem seus dados ou eventos recentes — RAG corrige isso |
| **Ingestão** | Carregar → Fragmentar → Fazer Embedding → Armazenar (executa uma vez) |
| **Recuperação** | Fazer embedding da consulta → Busca vetorial → Top-k fragmentos |
| **Fragmentação** | Tamanho + sobreposição importam; ~512 tokens com 50 tokens de sobreposição |
| **Busca** | Híbrida (palavras-chave + semântica) supera qualquer uma isoladamente |
| **Avaliação** | Meça fundamentação e relevância — tanto recuperação quanto geração |

---

## Próximos Passos

- **Entenda os vetores de embedding:** → [Lab 007 — O que são Embeddings?](lab-007-what-are-embeddings.md)
- **Construa um app RAG gratuitamente:** → [Lab 022 — RAG com GitHub Models + pgvector](lab-022-rag-github-models-pgvector.md)
- **RAG em produção no Azure:** → [Lab 031 — Busca Semântica pgvector no Azure](lab-031-pgvector-semantic-search.md)
