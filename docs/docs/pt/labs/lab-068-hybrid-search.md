---
tags: [search, rag, bm25, vector, semantic-ranker, python]
---
# Lab 068: Hybrid Search — Vector + BM25 + Semantic Ranker

<div class="lab-meta">
  <span><strong>Nível:</strong> <span class="level-badge level-200">L200</span></span>
  <span><strong>Trilha:</strong> Todas as trilhas</span>
  <span><strong>Tempo:</strong> ~60 min</span>
  <span><strong>💰 Custo:</strong> <span class="level-badge cost-free">Gratuito</span> — Resultados de busca pré-computados (não requer Azure AI Search)</span>
</div>

## O que Você Vai Aprender

- As diferenças entre busca **BM25** (por palavras-chave), **vector** (semântica) e **hybrid** (híbrida)
- Como o **Reciprocal Rank Fusion (RRF)** combina pontuações de BM25 e vetores
- Como um **semantic ranker** (reranqueador cross-encoder) melhora a precisão
- Medir a qualidade da recuperação com métricas de **recall** e **precision**
- Comparar estratégias de busca usando um **dataset de benchmark**
- Identificar quais tipos de consulta mais se beneficiam da busca híbrida + reranqueamento

!!! abstract "Pré-requisito"
    Complete primeiro o **[Lab 009: Retrieval-Augmented Generation](lab-009-rag-basic.md)**. Este lab pressupõe familiaridade com recuperação baseada em embeddings e conceitos básicos de busca.

## Introdução

Pipelines de RAG dependem da qualidade da recuperação — se você recuperar os trechos errados, até o melhor LLM produzirá respostas incorretas. A busca moderna combina múltiplas estratégias para maximizar recall e precisão:

| Estratégia | Como Funciona | Pontos Fortes | Pontos Fracos |
|----------|-------------|-----------|------------|
| **BM25** | Correspondência de palavras-chave por TF-IDF | Correspondências exatas, termos raros | Sem compreensão semântica |
| **Vector** | Similaridade de cosseno em embeddings | Similaridade semântica, sinônimos | Perde palavras-chave exatas |
| **Hybrid (RRF)** | Combina BM25 + vector via fusão de rankings | O melhor dos dois mundos | Maior latência |
| **Hybrid + Rerank** | Híbrido + reranqueamento com cross-encoder | Resultados de maior qualidade | Maior latência e custo |

### O Cenário

Você tem **20 consultas de busca** com documentos relevantes conhecidos (ground truth). Cada consulta foi executada contra todas as quatro estratégias, com recall e precisão registrados. Sua tarefa: analisar qual estratégia entrega a melhor qualidade de recuperação e entender quando cada abordagem se destaca.

---

## Pré-requisitos

| Requisito | Por quê |
|---|---|
| Python 3.10+ | Executar scripts de análise |
| `pandas` | Analisar dados de comparação de busca |

```bash
pip install pandas
```

---

!!! tip "Início Rápido com GitHub Codespaces"
    [![Open in GitHub Codespaces](https://github.com/codespaces/badge.svg)](https://codespaces.new/lcarli/AI-LearningHub?quickstart=1)

    Todas as dependências estão pré-instaladas no devcontainer.


## 📦 Arquivos de Apoio

!!! note "Baixe estes arquivos antes de iniciar o lab"
    Salve todos os arquivos em uma pasta `lab-068/` no seu diretório de trabalho.

| Arquivo | Descrição | Download |
|------|-------------|----------|
| `broken_search.py` | Exercício de correção de bugs (3 bugs + autotestes) | [📥 Download](https://github.com/lcarli/AI-LearningHub/raw/main/docs/docs/en/labs/lab-068/broken_search.py) |
| `search_comparison.csv` | Dataset | [📥 Download](https://github.com/lcarli/AI-LearningHub/raw/main/docs/docs/en/labs/lab-068/search_comparison.csv) |

---

## Etapa 1: Entendendo as Estratégias de Busca

Cada estratégia de busca processa consultas de forma diferente:

```
Query → ┬─ [BM25 Index]      → keyword matches   ─┐
        │                                          ├─ [RRF Fusion] → Hybrid Results
        └─ [Vector Index]     → semantic matches   ─┘                      ↓
                                                                  [Semantic Ranker]
                                                                         ↓
                                                               Hybrid + Rerank Results
```

Métricas principais:

1. **Recall** — Qual fração dos documentos relevantes foi recuperada? (maior = menos omissões)
2. **Precision** — Qual fração dos documentos recuperados é relevante? (maior = menos ruído)
3. **RRF Score** — Reciprocal Rank Fusion combina rankings: `1/(k + rank)` somado entre estratégias
4. **Rerank Score** — Pontuação de relevância do cross-encoder aplicada aos resultados híbridos

!!! info "Por que a Busca Híbrida Supera Ambas"
    BM25 se destaca em correspondências exatas de palavras-chave ("error code 0x8004") enquanto a busca vetorial se destaca em significado semântico ("application crashes on startup"). A busca híbrida funde ambas — capturando correspondências exatas que a busca vetorial perde E correspondências semânticas que o BM25 perde. O semantic ranker então reordena os resultados usando um modelo cross-encoder mais caro, porém mais preciso.

---

## Etapa 2: Carregar e Explorar Resultados de Busca

O dataset contém **20 consultas** com resultados de todas as quatro estratégias:

```python
import pandas as pd

results = pd.read_csv("lab-068/search_comparison.csv")
print(f"Total queries: {len(results)}")
print(f"Search strategies: {sorted(results.columns)}")
print(f"\nFirst 5 queries:")
print(results[["query_id", "query_text", "bm25_recall", "vector_recall",
               "hybrid_recall", "hybrid_rerank_recall"]].head().to_string(index=False))
```

**Esperado:**

```
Total queries: 20
```

---

## Etapa 3: Comparação de Recall

Compare o recall entre todas as quatro estratégias:

```python
print("Average Recall by Strategy:")
print(f"  BM25:            {results['bm25_recall'].mean():.2f}")
print(f"  Vector:          {results['vector_recall'].mean():.2f}")
print(f"  Hybrid:          {results['hybrid_recall'].mean():.2f}")
print(f"  Hybrid + Rerank: {results['hybrid_rerank_recall'].mean():.2f}")

perfect_recall = results[results["hybrid_rerank_recall"] == 1.0]
print(f"\nQueries with perfect hybrid+rerank recall: {len(perfect_recall)} / {len(results)}")
```

**Esperado:**

```
Average Recall by Strategy:
  BM25:            0.47
  Vector:          0.62
  Hybrid:          0.85
  Hybrid + Rerank: 1.00
```

!!! tip "Insight Principal"
    Hybrid + Rerank alcança recall perfeito (1.00) — todo documento relevante é recuperado para cada consulta. BM25 sozinho recupera menos da metade dos documentos relevantes em média. Isso demonstra por que pipelines modernos de RAG devem usar busca híbrida com reranqueamento sempre que possível.

---

## Etapa 4: Análise de Precisão

Recall sem precisão significa recuperar muito ruído. Analise a precisão:

```python
print("Average Precision by Strategy:")
print(f"  BM25:            {results['bm25_precision'].mean():.2f}")
print(f"  Vector:          {results['vector_precision'].mean():.2f}")
print(f"  Hybrid:          {results['hybrid_precision'].mean():.2f}")
print(f"  Hybrid + Rerank: {results['hybrid_rerank_precision'].mean():.2f}")
```

**Esperado:**

```
Average Precision by Strategy:
  BM25:            0.40
  Vector:          0.48
  Hybrid:          0.52
  Hybrid + Rerank: 0.57
```

!!! warning "Trade-off entre Precisão e Recall"
    Mesmo hybrid + rerank alcança apenas 0.57 de precisão média — significando que 43% dos documentos recuperados não são relevantes. Alto recall garante que nenhum documento relevante seja perdido, mas o LLM precisa filtrar o ruído do contexto. Considere usar um limiar de reranqueamento mais rigoroso para melhorar a precisão ao custo de algum recall.

---

## Etapa 5: Análise por Consulta

Identifique quais consultas mais se beneficiam da busca híbrida:

```python
results["hybrid_lift"] = results["hybrid_rerank_recall"] - results["bm25_recall"]
biggest_lift = results.sort_values("hybrid_lift", ascending=False).head(5)
print("Queries with biggest recall lift (hybrid+rerank vs BM25):")
print(biggest_lift[["query_id", "query_text", "bm25_recall", "hybrid_rerank_recall", "hybrid_lift"]]
      .to_string(index=False))
```

As consultas com maior ganho são tipicamente de natureza semântica — paráfrases, sinônimos ou consultas conceituais onde a correspondência por palavras-chave do BM25 falha, mas a similaridade vetorial tem sucesso.

---

## Etapa 6: Motor de Recomendação de Estratégia de Busca

Construa uma recomendação com base na análise:

```python
summary = f"""
╔════════════════════════════════════════════════════════╗
║     Hybrid Search — Strategy Comparison Report         ║
╠════════════════════════════════════════════════════════╣
║ Queries Evaluated:           {len(results):>5}                     ║
║ BM25 Avg Recall:             {results['bm25_recall'].mean():>5.2f}                     ║
║ Vector Avg Recall:           {results['vector_recall'].mean():>5.2f}                     ║
║ Hybrid Avg Recall:           {results['hybrid_recall'].mean():>5.2f}                     ║
║ Hybrid+Rerank Avg Recall:    {results['hybrid_rerank_recall'].mean():>5.2f}                     ║
║ Hybrid+Rerank Avg Precision: {results['hybrid_rerank_precision'].mean():>5.2f}                     ║
╚════════════════════════════════════════════════════════╝
"""
print(summary)
```

---

## 🐛 Exercício de Correção de Bugs

O arquivo `lab-068/broken_search.py` tem **3 bugs** na forma como calcula métricas de busca:

```bash
python lab-068/broken_search.py
```

| Teste | O que verifica | Dica |
|------|---------------|------|
| Teste 1 | Cálculo de recall médio | Deve usar `mean()`, não `sum()` |
| Teste 2 | Nome da coluna de precisão | Deve usar `hybrid_rerank_precision`, não `hybrid_precision` |
| Teste 3 | Comparação de recall | Deve comparar `hybrid_rerank_recall >= bm25_recall`, não `<=` |

---


## 🧠 Verificação de Conhecimento

??? question "**Q1 (Múltipla Escolha):** O que o Reciprocal Rank Fusion (RRF) faz na busca híbrida?"

    - A) Substitui o índice vetorial por um índice de palavras-chave
    - B) Combina rankings de múltiplas estratégias de busca em um único ranking unificado
    - C) Treina um novo modelo de embedding na consulta
    - D) Reduz o número de documentos no índice

    ??? success "✅ Revelar Resposta"
        **Correto: B) Combina rankings de múltiplas estratégias de busca em um único ranking unificado**

        O RRF mescla rankings de resultados de BM25 e busca vetorial usando a fórmula `1/(k + rank)` somada entre estratégias. Documentos bem classificados por ambas as estratégias recebem impulso, enquanto documentos bem classificados por apenas uma estratégia ainda aparecem. Isso produz um ranking unificado que captura tanto relevância por palavras-chave quanto semântica.

??? question "**Q2 (Múltipla Escolha):** Por que um semantic ranker (cross-encoder) melhora os resultados em relação à busca híbrida sozinha?"

    - A) É mais rápido que o BM25
    - B) Ele re-pontua cada candidato codificando conjuntamente a consulta e o documento, capturando sinais de relevância mais profundos
    - C) Remove todos os documentos irrelevantes perfeitamente
    - D) Gera novos documentos para preencher lacunas

    ??? success "✅ Revelar Resposta"
        **Correto: B) Ele re-pontua cada candidato codificando conjuntamente a consulta e o documento, capturando sinais de relevância mais profundos**

        Um cross-encoder recebe tanto a consulta quanto um documento candidato como entrada e produz uma pontuação de relevância. Diferente dos bi-encoders (usados para busca vetorial), cross-encoders capturam interações refinadas entre tokens da consulta e do documento. Isso é mais preciso, porém caro demais para aplicar ao índice inteiro — por isso é usado como reranqueador nos top-N resultados híbridos.

??? question "**Q3 (Execute o Lab):** Qual é o recall médio da estratégia hybrid + rerank?"

    Calcule `results['hybrid_rerank_recall'].mean()`.

    ??? success "✅ Revelar Resposta"
        **1.00 (recall perfeito)**

        Hybrid + rerank alcança recall perfeito em todas as 20 consultas, significando que todo documento relevante é recuperado para cada consulta. Isso é uma melhoria significativa em relação ao BM25 sozinho (0.47) e demonstra o valor de combinar busca por palavras-chave e semântica com reranqueamento por cross-encoder.

??? question "**Q4 (Execute o Lab):** Qual é o recall médio da busca BM25 sozinha?"

    Calcule `results['bm25_recall'].mean()`.

    ??? success "✅ Revelar Resposta"
        **0.47 de recall médio**

        BM25 recupera menos da metade dos documentos relevantes em média. Isso ocorre porque BM25 depende de correspondência por palavras-chave e não consegue lidar com sinônimos, paráfrases ou consultas conceituais. Por exemplo, uma consulta sobre "application crashes" perderia documentos que discutem "software failures" ou "system instability."

??? question "**Q5 (Execute o Lab):** Qual é a precisão média da estratégia hybrid + rerank?"

    Calcule `results['hybrid_rerank_precision'].mean()`.

    ??? success "✅ Revelar Resposta"
        **0.57 de precisão média**

        Embora hybrid + rerank alcance recall perfeito, sua precisão é 0.57 — significando que 43% dos documentos recuperados não são relevantes. Este é o trade-off entre recall e precisão: maximizar o recall garante que nenhum documento relevante seja perdido, mas inclui algum ruído. O LLM deve ser robusto o suficiente para ignorar contexto irrelevante ao gerar respostas.

---

## Resumo

| Tópico | O que Você Aprendeu |
|-------|-----------------|
| BM25 Search | Recuperação baseada em palavras-chave usando pontuação TF-IDF |
| Vector Search | Recuperação semântica usando similaridade de cosseno em embeddings |
| Hybrid Search | Combinação de BM25 + vector via Reciprocal Rank Fusion |
| Semantic Ranker | Reranqueamento com cross-encoder para ordenação de resultados de maior qualidade |
| Recall & Precision | Medição da qualidade de recuperação com métricas complementares |
| Seleção de Estratégia | Escolha da estratégia de busca adequada com base nas características da consulta |

---

## Próximos Passos

- **[Lab 009](lab-009-rag-basic.md)** — Fundamentos de RAG (padrões fundamentais de recuperação)
- **[Lab 067](lab-067-graphrag.md)** — GraphRAG (síntese entre documentos com grafos de conhecimento)
- **[Lab 065](lab-065-purview-dspm-ai.md)** — Purview DSPM for AI (governança para pipelines de busca)
