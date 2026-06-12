---
tags: [challenge, rag, retrieval, evaluation, python, local]
---
# Desafio 002: Corrija um Pipeline RAG Quebrado

<div class="lab-meta">
  <span><strong>Nível:</strong> <span class="level-badge level-200">L200</span></span>
  <span><strong>Tipo:</strong> Desafio</span>
  <span><strong>Tempo:</strong> ~75 min</span>
  <span><strong>💰 Custo:</strong> <span class="level-badge cost-free">Gratuito (local)</span></span>
</div>

## Cenário

A OutdoorGear tem um protótipo local de RAG para perguntas de suporte. Ele deveria recuperar a política ou guia de produto correto e responder usando apenas o contexto recuperado. O protótipo atual está quebrado: a recuperação coloca chunks ruins no topo, as respostas ignoram evidências e a avaliação reporta métricas enganosas.

Sua tarefa é corrigir o pipeline sem usar LLM, banco vetorial ou framework de RAG.

---

## Objetivo

Implemente a lógica faltante ou quebrada em `starter_rag_pipeline.py` para que o pipeline RAG recupere os documentos corretos, produza respostas fundamentadas, reporte métricas de avaliação corretas e gere um código de validação.

Seu pipeline final deve:

- Normalizar texto de consultas e documentos para recuperação
- Fragmentar documentos preservando metadados de origem
- Ranquear chunks por relevância
- Produzir respostas concisas a partir da evidência recuperada
- Avaliar acurácia top-1 de recuperação e cobertura de termos obrigatórios na resposta

---

## Arquivos Iniciais

Salve estes arquivos em uma pasta chamada `challenge-002/`:

| Arquivo | Finalidade | Download |
|---------|------------|----------|
| `documents.json` | Base de conhecimento mock da OutdoorGear | [Download](https://github.com/lcarli/AI-LearningHub/raw/main/docs/docs/en/challenges/challenge-002/documents.json) |
| `queries.json` | Consultas de avaliação e evidências esperadas | [Download](https://github.com/lcarli/AI-LearningHub/raw/main/docs/docs/en/challenges/challenge-002/queries.json) |
| `starter_rag_pipeline.py` | Pipeline RAG quebrado | [Download](https://github.com/lcarli/AI-LearningHub/raw/main/docs/docs/en/challenges/challenge-002/starter_rag_pipeline.py) |
| `test_rag_pipeline.py` | Testes de aceite | [Download](https://github.com/lcarli/AI-LearningHub/raw/main/docs/docs/en/challenges/challenge-002/test_rag_pipeline.py) |
| `validate_rag_pipeline.py` | Gera o código final de conclusão | [Download](https://github.com/lcarli/AI-LearningHub/raw/main/docs/docs/en/challenges/challenge-002/validate_rag_pipeline.py) |

---

## Briefing do Desafio

Você recebe uma base de conhecimento pequena, um conjunto de consultas de avaliação e um pipeline RAG local quebrado. Não há walkthrough: decida como fragmentar, pontuar, recuperar, responder e avaliar para que o sistema se comporte como um assistente de suporte confiável e fundamentado.

---

## Restrições

- Use apenas a biblioteca padrão do Python em `starter_rag_pipeline.py`.
- Não chame uma API de LLM.
- Não use embeddings ou banco vetorial.
- Não hardcode respostas para IDs de consulta específicos.
- Use a evidência recuperada em `answer_question()`.
- Preserve os nomes públicos das funções usados pelos testes.

---

## Critérios de Aceite

Sua solução está completa quando:

- `python -m pytest test_rag_pipeline.py` passa
- Os metadados dos chunks preservam `chunk_id`, `doc_id`, `title` e `text`
- O documento no topo para cada consulta de fixture está correto
- As respostas incluem os termos de evidência obrigatórios
- A avaliação reporta `top1_accuracy == 1.0`
- A avaliação reporta `required_coverage == 1.0`

---

## Validação

Quando sua implementação estiver pronta, execute:

```bash
python -m pytest test_rag_pipeline.py
python validate_rag_pipeline.py
```

Digite o código de conclusão impresso por `validate_rag_pipeline.py`:

<div class="challenge-validator" data-answer="CH002-3E640D5D">
  <input type="text" aria-label="Código de conclusão" placeholder="CH002-XXXXXXXX" />
  <button type="button">Validar</button>
  <p class="challenge-validator-result" aria-live="polite"></p>
</div>

---

## Dicas

??? tip "Dica 1 — Qualidade de recuperação começa na normalização"
    Pontuação, maiúsculas/minúsculas e stop words podem dominar um recuperador lexical pequeno se você não normalizar o texto.

??? tip "Dica 2 — Chunking faz parte da recuperação"
    Um chunk deve ser pequeno o suficiente para pontuar com precisão, mas ainda carregar metadados de origem suficientes para explicar de onde veio a resposta.

??? tip "Dica 3 — Responda a partir da evidência, não da consulta"
    Se um termo obrigatório não aparece no contexto recuperado, a resposta não deve inventá-lo.

??? tip "Dica 4 — Métricas precisam do denominador certo"
    Acurácia top-1 e cobertura são métricas por consulta. Confira pelo que você está dividindo.

---

## Rubrica

| Área | Pontos | Como fica bom |
|------|:------:|---------------|
| Recuperação | 35 | Documento correto no topo para cada consulta |
| Chunking | 20 | Metadados preservados e tamanhos de chunk controlados |
| Respostas fundamentadas | 20 | Respostas incluem evidência dos chunks recuperados |
| Avaliação | 15 | Métricas refletem desempenho por consulta |
| Simplicidade | 10 | Sem framework ou respostas hardcoded por consulta |

---

## Objetivos Extras

- Adicionar reciprocal rank fusion sobre pontuações de título e corpo
- Retornar citações com IDs de chunk na resposta
- Adicionar resposta "evidência insuficiente" quando a confiança de recuperação for baixa
- Adicionar uma nova consulta em `queries.json` e atualizar localmente o payload do validador

---

## Labs Relacionados

- [Lab 006 — O que é RAG?](../labs/lab-006-what-is-rag.md)
- [Lab 007 — O que são Embeddings?](../labs/lab-007-what-are-embeddings.md)
- [Lab 022 — RAG com GitHub Models + pgvector](../labs/lab-022-rag-github-models-pgvector.md)
