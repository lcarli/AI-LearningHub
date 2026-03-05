---
tags: [multimodal, rag, images, tables, gpt4o-vision, python]
---
# Lab 083: RAG Multi-Modal — Imagens, Tabelas e Gráficos em Documentos

<div class="lab-meta">
  <span><strong>Nível:</strong> <span class="level-badge level-300">L300</span></span>
  <span><strong>Trilha:</strong> Todas as trilhas</span>
  <span><strong>Tempo:</strong> ~90 min</span>
  <span><strong>💰 Custo:</strong> <span class="level-badge cost-free">Gratuito</span></span>
</div>

## O que Você Vai Aprender

- O que é **RAG multi-modal** — geração aumentada por recuperação que lida com imagens, tabelas e gráficos junto com texto
- Como o **GPT-4o vision** permite a compreensão de conteúdo visual dentro de documentos para uma recuperação mais rica
- Comparar pontuações de **recuperação somente texto vs multi-modal** para quantificar a melhoria da compreensão visual
- Analisar **tipos de chunks** (texto, imagem, tabela) e seu impacto na qualidade da recuperação
- Depurar um script de análise de RAG multi-modal quebrado corrigindo 3 bugs

## Introdução

Pipelines tradicionais de RAG funcionam bem com texto — eles dividem documentos em chunks, fazem embedding dos chunks e recuperam os mais relevantes para uma consulta. Mas documentos empresariais não são apenas texto. Eles contêm **gráficos de barras**, **gráficos de pizza**, **fotos de produtos**, **diagramas de arquitetura**, **tabelas de dados** e **fluxogramas** que carregam informações críticas.

Um pipeline de RAG somente texto perde essas informações completamente. Quando um usuário pergunta "Qual foi a receita do Q1 por região?", a resposta pode estar em um **gráfico de barras** — que o embedding somente texto pontua em 0.15 (quase inútil) enquanto uma abordagem multi-modal pontua 0.82 (altamente relevante).

| Abordagem | Lida com Texto | Lida com Imagens | Lida com Tabelas | Caso de Uso Típico |
|----------|:---:|:---:|:---:|---|
| **RAG somente texto** | ✅ | ❌ | ⚠️ (somente texto) | P&R simples sobre documentos de texto |
| **RAG multi-modal** | ✅ | ✅ | ✅ | Documentos com gráficos, fotos, diagramas |

### O Cenário

Você está construindo um **sistema de inteligência de documentos** para a OutdoorGear Inc. O corpus inclui relatórios trimestrais com gráficos, catálogos de produtos com fotos, manuais de treinamento com diagramas, apresentações para investidores com visualizações e planilhas de vendas. Você analisará **15 chunks de documentos** para comparar o desempenho de recuperação somente texto e multi-modal.

!!! info "API do GPT-4o Não Necessária"
    Este laboratório analisa um **conjunto de dados de benchmark pré-gravado** de pontuações de recuperação. Você não precisa de uma chave de API da OpenAI — toda a análise é feita localmente com pandas. O conjunto de dados simula pontuações reais de recuperação de um pipeline de RAG multi-modal.

## Pré-requisitos

| Requisito | Por quê |
|---|---|
| Python 3.10+ | Executar scripts de análise |
| Biblioteca `pandas` | Operações com DataFrame |

```bash
pip install pandas
```

---

!!! tip "Início Rápido com GitHub Codespaces"
    [![Open in GitHub Codespaces](https://github.com/codespaces/badge.svg)](https://codespaces.new/lcarli/AI-LearningHub?quickstart=1)

    Todas as dependências estão pré-instaladas no devcontainer.


## 📦 Arquivos de Apoio

!!! note "Baixe estes arquivos antes de iniciar o laboratório"
    Salve todos os arquivos em uma pasta `lab-083/` no seu diretório de trabalho.

| Arquivo | Descrição | Download |
|------|-------------|----------|
| `broken_multimodal.py` | Exercício de correção de bugs (3 bugs + auto-testes) | [📥 Download](https://github.com/lcarli/AI-LearningHub/raw/main/docs/docs/en/labs/lab-083/broken_multimodal.py) |
| `multimodal_chunks.csv` | Conjunto de dados — 15 chunks de documentos com pontuações de recuperação | [📥 Download](https://github.com/lcarli/AI-LearningHub/raw/main/docs/docs/en/labs/lab-083/multimodal_chunks.csv) |

---

## Etapa 1: Entendendo o RAG Multi-Modal

Um pipeline de RAG multi-modal estende o RAG tradicional com compreensão visual:

```
┌──────────────┐     ┌──────────────┐     ┌──────────────┐
│  Document    │────▶│  Chunker     │────▶│  Chunks      │
│  (PDF/DOCX)  │     │  (text +     │     │  (text,      │
│              │     │   visual)    │     │   image,     │
└──────────────┘     └──────────────┘     │   table)     │
                                          └──────┬───────┘
                                                 │
                     ┌──────────────┐     ┌──────▼───────┐
                     │  Query       │────▶│  Retrieval   │
                     │              │     │  (text +     │
                     │              │     │   vision)    │
                     └──────────────┘     └──────┬───────┘
                                                 │
                                          ┌──────▼───────┐
                                          │  LLM + GPT-4o│
                                          │  (generate)  │
                                          └──────────────┘
```

### Como os Chunks Visuais São Processados

| Tipo de Chunk | Pipeline Somente Texto | Pipeline Multi-Modal |
|-----------|-------------------|---------------------|
| **Texto** | Embedding do texto → recuperação por similaridade de cosseno | Igual ao somente texto |
| **Tabela** | Embedding do texto serializado da tabela | Embedding do texto + compreensão da estrutura |
| **Imagem** | ❌ Pular ou usar texto alternativo (baixa qualidade) | GPT-4o descreve a imagem → embedding da descrição + características visuais |

O insight principal: **imagens carregam informações que o texto não consegue capturar**. Um gráfico de barras, foto de produto ou diagrama de arquitetura transmite significado que se perde quando a imagem é simplesmente ignorada ou descrita apenas pelo texto alternativo.

---

## Etapa 2: Carregar o Conjunto de Dados de Chunks

O conjunto de dados contém **15 chunks** de 5 documentos, cada um com pontuações de recuperação somente texto e multi-modal:

```python
import pandas as pd

chunks = pd.read_csv("lab-083/multimodal_chunks.csv")
chunks["has_image"] = chunks["has_image"].astype(str).str.lower() == "true"
chunks["has_table"] = chunks["has_table"].astype(str).str.lower() == "true"

print(f"Total chunks: {len(chunks)}")
print(f"Chunk types: {chunks['chunk_type'].value_counts().to_dict()}")
print(f"Documents: {sorted(chunks['document'].unique())}")
print(f"\nDataset preview:")
print(chunks[["chunk_id", "document", "chunk_type", "has_image", "retrieval_score_text_only",
              "retrieval_score_multimodal"]].to_string(index=False))
```

**Saída esperada:**

```
Total chunks: 15
Chunk types: {'text': 5, 'image': 6, 'table': 4}
Documents: ['investor_deck.pptx', 'product_catalog.docx', 'quarterly_report.pdf', 'sales_data.xlsx', 'training_manual.pdf']
```

| chunk_id | document | chunk_type | has_image | text_only | multimodal |
|----------|---------|-----------|-----------|-----------|------------|
| C01 | quarterly_report.pdf | text | False | 0.85 | 0.85 |
| C03 | quarterly_report.pdf | image | True | 0.15 | 0.82 |
| C05 | product_catalog.docx | image | True | 0.10 | 0.91 |
| ... | ... | ... | ... | ... | ... |

---

## Etapa 3: Comparar Pontuações Somente Texto vs Multi-Modal

Analise como a recuperação multi-modal melhora em relação ao somente texto:

```python
print("Average retrieval scores by chunk type:")
for ctype in ["text", "table", "image"]:
    subset = chunks[chunks["chunk_type"] == ctype]
    text_avg = subset["retrieval_score_text_only"].mean()
    mm_avg = subset["retrieval_score_multimodal"].mean()
    improvement = mm_avg - text_avg
    print(f"  {ctype:>5}: text={text_avg:.3f}  multimodal={mm_avg:.3f}  "
          f"improvement={improvement:+.3f}")
```

**Saída esperada:**

```
Average retrieval scores by chunk type:
   text: text=0.806  multimodal=0.806  improvement=+0.000
  table: text=0.780  multimodal=0.898  improvement=+0.117
  image: text=0.138  multimodal=0.853  improvement=+0.715
```

!!! tip "Insight"
    **Chunks de texto** não apresentam melhoria — já são bem atendidos por embeddings de texto. **Chunks de tabela** ganham +0.117 com a compreensão estrutural. **Chunks de imagem** apresentam uma melhoria massiva de +0.715 — a recuperação somente texto pontua apenas 0.138 em média para imagens, enquanto a multi-modal pontua 0.853. Esta é a principal proposta de valor do RAG multi-modal.

---

## Etapa 4: Analisar Chunks de Imagem

Análise aprofundada dos chunks com imagens:

```python
image_chunks = chunks[chunks["has_image"] == True]
print(f"Image chunks: {len(image_chunks)}/{len(chunks)}")

print(f"\nImage chunk details:")
for _, c in image_chunks.iterrows():
    improvement = c["retrieval_score_multimodal"] - c["retrieval_score_text_only"]
    print(f"  {c['chunk_id']} ({c['document']}):")
    print(f"    Description: {c['image_description']}")
    print(f"    Text-only: {c['retrieval_score_text_only']:.2f} → Multimodal: {c['retrieval_score_multimodal']:.2f} "
          f"(+{improvement:.2f})")
```

**Saída esperada:**

```
Image chunks: 6/15

Image chunk details:
  C03 (quarterly_report.pdf):
    Description: Bar chart showing Q1 revenue by region
    Text-only: 0.15 → Multimodal: 0.82 (+0.67)
  C05 (product_catalog.docx):
    Description: Photo of Alpine Explorer Tent with dimensions
    Text-only: 0.10 → Multimodal: 0.91 (+0.81)
  C08 (training_manual.pdf):
    Description: Diagram of tent assembly steps 1-5
    Text-only: 0.12 → Multimodal: 0.85 (+0.73)
  C09 (training_manual.pdf):
    Description: Photo showing correct stake placement
    Text-only: 0.08 → Multimodal: 0.79 (+0.71)
  C11 (investor_deck.pptx):
    Description: Pie chart of market share by competitor
    Text-only: 0.18 → Multimodal: 0.87 (+0.69)
  C15 (quarterly_report.pdf):
    Description: Line graph of monthly active users trend
    Text-only: 0.20 → Multimodal: 0.88 (+0.68)
```

---

## Etapa 5: Calcular Métricas de Melhoria

Calcule a melhoria média para chunks de imagem:

```python
image_text_avg = image_chunks["retrieval_score_text_only"].mean()
image_mm_avg = image_chunks["retrieval_score_multimodal"].mean()
avg_improvement = image_mm_avg - image_text_avg

print(f"Image chunks — average scores:")
print(f"  Text-only:    {image_text_avg:.3f}")
print(f"  Multi-modal:  {image_mm_avg:.3f}")
print(f"  Improvement:  +{avg_improvement:.3f}")
print(f"  Multiplier:   {image_mm_avg/image_text_avg:.1f}x better")
```

**Saída esperada:**

```
Image chunks — average scores:
  Text-only:    0.138
  Multi-modal:  0.853
  Improvement:  +0.715
  Multiplier:   6.2x better
```

```python
overall_text = chunks["retrieval_score_text_only"].mean()
overall_mm = chunks["retrieval_score_multimodal"].mean()
print(f"\nOverall retrieval scores:")
print(f"  Text-only:    {overall_text:.3f}")
print(f"  Multi-modal:  {overall_mm:.3f}")
print(f"  Improvement:  +{overall_mm - overall_text:.3f}")
```

!!! tip "Insight"
    A recuperação multi-modal é **6.2x melhor** que a somente texto para chunks de imagem. Mesmo considerando todos os 15 chunks (incluindo os somente texto), a pontuação geral de recuperação melhora significativamente porque 40% dos chunks (6/15) contêm imagens.

---

## Etapa 6: Análise por Documento

Compare o impacto multi-modal por documento:

```python
print("Retrieval improvement by document:")
for doc in sorted(chunks["document"].unique()):
    subset = chunks[chunks["document"] == doc]
    text_avg = subset["retrieval_score_text_only"].mean()
    mm_avg = subset["retrieval_score_multimodal"].mean()
    has_images = subset["has_image"].any()
    print(f"  {doc:>30}: text={text_avg:.3f}  mm={mm_avg:.3f}  "
          f"Δ={mm_avg-text_avg:+.3f}  images={'Yes' if has_images else 'No'}")
```

**Saída esperada:**

```
Retrieval improvement by document:
            investor_deck.pptx: text=0.577  mm=0.840  Δ=+0.263  images=Yes
          product_catalog.docx: text=0.608  mm=0.838  Δ=+0.230  images=Yes
        quarterly_report.pdf: text=0.513  mm=0.850  Δ=+0.337  images=Yes
             sales_data.xlsx: text=0.820  mm=0.920  Δ=+0.100  images=No
           training_manual.pdf: text=0.427  mm=0.840  Δ=+0.413  images=Yes
```

!!! tip "Insight"
    Documentos com imagens apresentam as maiores melhorias. O **manual de treinamento** é o mais beneficiado (+0.413) porque contém diagramas de montagem e fotos que são essenciais para responder perguntas do tipo "como fazer". A **planilha de vendas** (sem imagens) ainda se beneficia da compreensão aprimorada de tabelas (+0.100).

---

## 🐛 Exercício de Correção de Bugs

O arquivo `lab-083/broken_multimodal.py` tem **3 bugs** nas funções de análise. Você consegue encontrar e corrigir todos?

Execute os auto-testes para ver quais falham:

```bash
python lab-083/broken_multimodal.py
```

Você deve ver **3 testes com falha**. Cada teste corresponde a um bug:

| Teste | O que verifica | Dica |
|------|---------------|------|
| Teste 1 | Cálculo de melhoria multi-modal | Deve calcular a melhoria usando chunks de imagem para ambas as pontuações, não mistas |
| Teste 2 | Contagem de chunks de imagem | Deve verificar `has_image`, não `has_table` |
| Teste 3 | Pontuação média multi-modal | Deve usar `retrieval_score_multimodal`, não `retrieval_score_text_only` |

Corrija todos os 3 bugs e execute novamente. Quando você ver `All passed!`, está pronto!

---

## 🧠 Verificação de Conhecimento

??? question "**Q1 (Múltipla Escolha):** Por que chunks de imagem pontuam mal com recuperação somente texto?"

    - A) Porque as imagens são sempre de baixa qualidade
    - B) Porque embeddings de texto não conseguem capturar informações visuais — gráficos, fotos e diagramas têm texto extraível mínimo
    - C) Porque arquivos de imagem são grandes demais para fazer embedding
    - D) Porque modelos somente texto se recusam a processar imagens

    ??? success "✅ Revelar Resposta"
        **Correto: B) Porque embeddings de texto não conseguem capturar informações visuais — gráficos, fotos e diagramas têm texto extraível mínimo**

        Um gráfico de barras mostrando "receita do Q1 por região" tem muito pouco texto extraível (talvez rótulos dos eixos), então seu embedding de texto tem quase nenhuma sobreposição semântica com uma consulta sobre receita. O RAG multi-modal usa GPT-4o vision para *compreender* o conteúdo do gráfico e gerar uma descrição rica, produzindo um embedding que representa com precisão as informações do gráfico.

??? question "**Q2 (Múltipla Escolha):** Qual é o papel do GPT-4o vision em um pipeline de RAG multi-modal?"

    - A) Ele gera a resposta final para a consulta do usuário
    - B) Ele converte imagens em descrições de texto que podem ser incorporadas junto com o texto do documento
    - C) Ele substitui completamente o banco de dados vetorial
    - D) Ele lida apenas com OCR para documentos digitalizados

    ??? success "✅ Revelar Resposta"
        **Correto: B) Ele converte imagens em descrições de texto que podem ser incorporadas junto com o texto do documento**

        O GPT-4o vision analisa cada chunk de imagem — gráficos, fotos, diagramas — e produz uma descrição detalhada em texto do que a imagem contém. Essa descrição é então incorporada junto com o texto do documento, permitindo que o sistema de recuperação encontre imagens relevantes quando um usuário faz uma pergunta. A descrição serve como ponte entre o conteúdo visual e a recuperação baseada em texto.

??? question "**Q3 (Execute o Laboratório):** Quantos chunks contêm imagens (`has_image == True`)?"

    Carregue [📥 `multimodal_chunks.csv`](https://github.com/lcarli/AI-LearningHub/raw/main/docs/docs/en/labs/lab-083/multimodal_chunks.csv) e conte as linhas onde `has_image == True`.

    ??? success "✅ Revelar Resposta"
        **6**

        6 de 15 chunks contêm imagens: C03 (gráfico de barras), C05 (foto do produto), C08 (diagrama de montagem), C09 (foto de posicionamento de estacas), C11 (gráfico de pizza) e C15 (gráfico de linhas). Eles representam 40% do corpus.

??? question "**Q4 (Execute o Laboratório):** Qual é a melhoria média da pontuação multi-modal para chunks de imagem em comparação com suas pontuações somente texto?"

    Para chunks onde `has_image == True`, calcule `retrieval_score_multimodal.mean() - retrieval_score_text_only.mean()`.

    ??? success "✅ Revelar Resposta"
        **+0.715**

        Pontuação média somente texto dos chunks de imagem: (0.15 + 0.10 + 0.12 + 0.08 + 0.18 + 0.20) ÷ 6 = **0.138**. Pontuação média multi-modal: (0.82 + 0.91 + 0.85 + 0.79 + 0.87 + 0.88) ÷ 6 = **0.853**. Melhoria = 0.853 − 0.138 = **+0.715**.

??? question "**Q5 (Execute o Laboratório):** Quantos chunks totais existem no conjunto de dados?"

    Conte todas as linhas no conjunto de dados.

    ??? success "✅ Revelar Resposta"
        **15**

        O conjunto de dados contém 15 chunks em 5 documentos: quarterly_report.pdf (3), product_catalog.docx (3), training_manual.pdf (2), investor_deck.pptx (3), sales_data.xlsx (1), product_catalog.docx (1), quarterly_report.pdf (1) e sales_data.xlsx (1) — totalizando 15 chunks.

---

## Resumo

| Tópico | O que Você Aprendeu |
|-------|-----------------|
| RAG Multi-Modal | Estende o RAG de texto com compreensão visual de imagens, gráficos e diagramas |
| GPT-4o Vision | Converte imagens em descrições de texto ricas para embedding e recuperação |
| Chunks de Imagem | 6 de 15 chunks contêm imagens — 40% do corpus |
| Melhoria de Pontuação | Chunks de imagem melhoram de 0.138 (somente texto) para 0.853 (multi-modal) — ganho de +0.715 |
| Chunks de Texto | Nenhuma melhoria necessária — já são bem atendidos por embeddings de texto |
| Chunks de Tabela | Melhoria moderada (+0.117) com compreensão estrutural |
| Impacto Geral | A recuperação multi-modal melhora significativamente a qualidade para documentos visualmente ricos |

---

## Próximos Passos

- Explore o [Azure AI Document Intelligence](https://learn.microsoft.com/azure/ai-services/document-intelligence/) para análise de documentos em nível de produção
- Tente construir um pipeline de RAG multi-modal com o [suporte multi-modal do LangChain](https://python.langchain.com/docs/how_to/multimodal_inputs/)
- Revise o **[Lab 080](lab-080-markitdown-mcp.md)** para conversão de documento para Markdown como etapa de pré-processamento
