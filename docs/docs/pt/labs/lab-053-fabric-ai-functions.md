---
tags: [fabric, ai-functions, batch-enrichment, etl, python, pandas]
---
# Lab 053: Fabric IQ — Enriquecimento em Lote com AI Functions

<div class="lab-meta">
  <span><strong>Nível:</strong> <span class="level-badge level-300">L300</span></span>
  <span><strong>Caminho:</strong> Todos os caminhos</span>
  <span><strong>Tempo:</strong> ~90 min</span>
  <span><strong>💰 Custo:</strong> <span class="level-badge cost-free">Gratuito</span> — Usa funções de IA simuladas localmente (capacidade do Fabric opcional)</span>
</div>

## O Que Você Vai Aprender

- O que são as **Fabric AI Functions** e como elas integram IA em fluxos de trabalho Spark/pandas (`ai.classify`, `ai.summarize`, `ai.extract`, `ai.embed`)
- Projetar **pipelines de AI ETL** que enriquecem dados tabulares com transformações alimentadas por LLM
- Processar dados em **lote** — aplicando classificação, sumarização e extração de entidades a DataFrames inteiros
- Construir e testar com **funções de IA simuladas** localmente, depois trocar para chamadas reais `ai.*()` do Fabric em produção

## Introdução

![Pipeline AI ETL](../../assets/diagrams/fabric-ai-etl.svg)

Pipelines ETL tradicionais movem e transformam dados estruturados — limpar, filtrar, juntar, agregar. **AI Functions** adicionam uma nova dimensão: permitem chamar um LLM em cada linha de um DataFrame, tratando classificação, sumarização e extração como operações nativas de coluna.

No Microsoft Fabric, as funções `ai.*()` rodam diretamente dentro de notebooks Spark. Você escreve `df["sentiment"] = ai.classify(df["text"], ["positive", "neutral", "negative"])` e o Fabric cuida do agrupamento em lotes, limitação de taxa e roteamento de modelo nos bastidores.

### O Cenário

Você é um **Engenheiro de Dados** na OutdoorGear Inc. A equipe de produto coletou **20 avaliações de clientes** para equipamentos outdoor e quer que você construa um pipeline de enriquecimento que:

1. **Classifica** o sentimento de cada avaliação (positivo / neutro / negativo)
2. **Sumariza** cada avaliação em um snippet curto
3. **Extrai** entidades-chave (prós e contras) do texto da avaliação
4. **Gera embeddings** do texto da avaliação para busca semântica downstream *(discutido conceitualmente)*

Como você está desenvolvendo localmente, usará **funções de IA simuladas** que imitam o comportamento das chamadas `ai.*()` do Fabric. Uma vez que o pipeline esteja validado, trocar para modelos reais requer alterar apenas as implementações das funções.

!!! info "Funções de IA Simuladas vs. Reais"
    Este lab usa funções simuladas (baseadas em regras, sem necessidade de LLM) para que qualquer pessoa possa acompanhar sem uma capacidade do Fabric. As funções simuladas produzem resultados determinísticos que correspondem às saídas esperadas. No Fabric em produção, você substituiria essas simulações por `ai.classify()`, `ai.summarize()`, etc.

## Pré-requisitos

| Requisito | Por quê |
|---|---|
| Python 3.10+ | Executar o pipeline de enriquecimento |
| Biblioteca `pandas` | Operações com DataFrame |
| (Opcional) Capacidade do Microsoft Fabric | Para funções `ai.*()` reais |

```bash
pip install pandas
```

---

!!! tip "Início Rápido com GitHub Codespaces"
    [![Abrir no GitHub Codespaces](https://github.com/codespaces/badge.svg)](https://codespaces.new/lcarli/AI-LearningHub?quickstart=1)

    Todas as dependências estão pré-instaladas no devcontainer.


## 📦 Arquivos de Apoio

!!! note "Baixe estes arquivos antes de iniciar o lab"
    Salve todos os arquivos em uma pasta `lab-053/` no seu diretório de trabalho.

| Arquivo | Descrição | Download |
|------|-------------|----------|
| `broken_pipeline.py` | Exercício de correção de bugs (3 bugs + auto-testes) | [📥 Download](https://github.com/lcarli/AI-LearningHub/raw/main/docs/docs/en/labs/lab-053/broken_pipeline.py) |
| `product_reviews.csv` | Conjunto de dados | [📥 Download](https://github.com/lcarli/AI-LearningHub/raw/main/docs/docs/en/labs/lab-053/product_reviews.csv) |

---

## Etapa 1: Entendendo as Fabric AI Functions

As Fabric AI Functions são operações nativas que aplicam capacidades de LLM a colunas de DataFrame. Elas abstraem a engenharia de prompts, agrupamento em lotes e gerenciamento de API:

| Função | Assinatura | Descrição |
|----------|-----------|-------------|
| `ai.classify()` | `ai.classify(column, categories)` | Classifica texto em uma das categorias fornecidas usando um LLM |
| `ai.summarize()` | `ai.summarize(column, max_length=None)` | Gera um resumo conciso de cada valor de texto |
| `ai.extract()` | `ai.extract(column, fields)` | Extrai campos estruturados (entidades, palavras-chave) do texto |
| `ai.embed()` | `ai.embed(column, model=None)` | Gera embeddings vetoriais para busca de similaridade downstream |

### Como Elas Funcionam no Fabric

Em um notebook Spark real do Fabric, você escreveria:

```python
from synapse.ml.fabric import ai

# Classify sentiment in one line
df["sentiment"] = ai.classify(df["review_text"], ["positive", "neutral", "negative"])

# Summarize reviews
df["summary"] = ai.summarize(df["review_text"], max_length=50)
```

O Fabric cuida de:

- **Agrupamento em lotes** — agrupa linhas em tamanhos ótimos de lote para o endpoint do modelo
- **Limitação de taxa** — respeita limites de tokens por minuto automaticamente
- **Tratamento de erros** — repete falhas transientes com backoff exponencial
- **Roteamento de modelo** — usa o modelo padrão do workspace ou um especificado

!!! tip "Por Que Simular Primeiro?"
    Construir com simulações permite validar a lógica do pipeline, tipos de dados e consumidores downstream *antes* de gastar computação em chamadas reais de LLM. Esta é uma melhor prática para qualquer pipeline de AI ETL.

---

## Etapa 2: Carregar o Conjunto de Dados de Avaliações

O conjunto de dados contém **20 avaliações de produtos** para produtos OutdoorGear:

```python
import pandas as pd

reviews = pd.read_csv("lab-053/product_reviews.csv")
print(f"Total reviews: {len(reviews)}")
print(f"Unique products: {reviews['product_name'].nunique()}")
print(f"Rating range: {reviews['rating'].min()} – {reviews['rating'].max()}")
print(f"Average rating: {reviews['rating'].mean():.2f}")
print(f"\nReviews per product:")
print(reviews.groupby("product_name").size().sort_values(ascending=False))
```

**Saída esperada:**

```
Total reviews: 20
Unique products: 7
Rating range: 1 – 5
Average rating: 3.70

Reviews per product:
product_name
Alpine Explorer Tent       5
Peak Performer Boots       3
Explorer Pro Backpack      3
TrailMaster X4 Tent        3
CozyNights Sleeping Bag    2
DayTripper Pack            2
Summit Water Bottle        2
```

Reserve um momento para explorar os dados:

```python
print(reviews[["review_id", "product_name", "rating", "review_text"]].head(5).to_string(index=False))
```

---

## Etapa 3: Implementar Funções de IA Simuladas

Em vez de chamar um LLM real, criamos funções simuladas determinísticas que imitam o comportamento das `ai.*()` do Fabric:

### 3a — `mock_classify(rating)`

Classifica o sentimento com base na nota numérica:

```python
def mock_classify(rating: int) -> str:
    """Mock ai.classify() — maps rating to sentiment."""
    if rating >= 4:
        return "positive"
    elif rating == 3:
        return "neutral"
    else:
        return "negative"
```

- Rating ≥ 4 → `"positive"`
- Rating = 3 → `"neutral"`
- Rating ≤ 2 → `"negative"`

### 3b — `mock_summarize(text)`

Retorna uma versão truncada do texto da avaliação:

```python
def mock_summarize(text: str) -> str:
    """Mock ai.summarize() — returns first 50 characters."""
    if len(text) <= 50:
        return text
    return text[:50] + "..."
```

### 3c — `mock_extract(text)`

Extrai palavras-chave simples procurando por palavras indicadoras positivas/negativas:

```python
POSITIVE_WORDS = {"amazing", "great", "best", "perfect", "incredible", "love",
                  "good", "solid", "comfortable", "warm", "durable"}
NEGATIVE_WORDS = {"broke", "terrible", "disappointed", "cheap", "thin",
                  "cramped", "snags", "cracked"}

def mock_extract(text: str) -> dict:
    """Mock ai.extract() — finds pros and cons keywords."""
    words = set(text.lower().split())
    pros = sorted(words & POSITIVE_WORDS)
    cons = sorted(words & NEGATIVE_WORDS)
    return {"pros": pros, "cons": cons}
```

!!! tip "Real vs. Simulado"
    No Fabric em produção, `ai.classify()` envia o texto da avaliação para um LLM com os rótulos candidatos — ele entende contexto, sarcasmo e nuances. Nossa simulação usa a nota como proxy, o que é uma heurística razoável para este conjunto de dados, mas não generalizaria para texto sem rótulos.

---

## Etapa 4: Executar o Pipeline de Enriquecimento

Aplique as funções simuladas a cada linha do DataFrame:

```python
# Classify sentiment
reviews["sentiment"] = reviews["rating"].apply(mock_classify)

# Summarize reviews
reviews["summary"] = reviews["review_text"].apply(mock_summarize)

# Extract entities
reviews["entities"] = reviews["review_text"].apply(mock_extract)

print("Enriched DataFrame columns:", list(reviews.columns))
print(f"\nSentiment distribution:")
print(reviews["sentiment"].value_counts())
```

**Saída esperada:**

```
Enriched DataFrame columns: ['review_id', 'product_id', 'product_name', 'category',
                              'rating', 'review_text', 'sentiment', 'summary', 'entities']

Sentiment distribution:
positive    13
neutral      4
negative     3
```

### Verificar os Resultados

```python
# Show a sample of enriched data
sample_cols = ["review_id", "product_name", "rating", "sentiment", "summary"]
print(reviews[sample_cols].head(6).to_string(index=False))
```

**Esperado:**

| review_id | product_name | rating | sentiment | summary |
|-----------|-------------|--------|-----------|---------|
| R001 | Alpine Explorer Tent | 5 | positive | Amazing tent! Held up perfectly in heavy rain. Se... |
| R002 | Alpine Explorer Tent | 4 | positive | Solid tent but a bit heavy for long hikes. Great ... |
| R003 | Alpine Explorer Tent | 5 | positive | Best tent I've ever owned. Worth every penny. |
| R004 | Alpine Explorer Tent | 3 | neutral | Decent tent but nothing special at this price poi... |
| R005 | Alpine Explorer Tent | 4 | positive | Good quality materials. Survived a storm with no ... |
| R006 | TrailMaster X4 Tent | 4 | positive | Great ventilation and the zipper is smooth. Sligh... |

### Distribuição de Sentimento

| Sentimento | Contagem | Notas |
|-----------|-------|---------|
| Positivo (rating ≥ 4) | 13 | Notas 4 e 5 |
| Neutro (rating = 3) | 4 | Nota 3 |
| Negativo (rating ≤ 2) | 3 | Notas 1 e 2 |

---

## Etapa 5: Analisar Dados Enriquecidos

Agora que as avaliações estão enriquecidas, analise-as para extrair insights de negócios:

### 5a — Nota Média por Sentimento

```python
print("Average rating by sentiment:")
print(reviews.groupby("sentiment")["rating"].mean().to_string())
```

**Esperado:**

```
negative    1.666667
neutral     3.000000
positive    4.384615
```

### 5b — Análise por Produto

```python
product_stats = reviews.groupby("product_name").agg(
    review_count=("review_id", "count"),
    avg_rating=("rating", "mean"),
).sort_values("review_count", ascending=False)

print(f"Overall average rating: {reviews['rating'].mean():.2f}")
print(f"\nMost reviewed product: {product_stats.index[0]} ({product_stats.iloc[0]['review_count']:.0f} reviews)")
print(f"\nProduct statistics:")
print(product_stats.to_string())
```

**Esperado:**

```
Overall average rating: 3.70

Most reviewed product: Alpine Explorer Tent (5 reviews)

Product statistics:
                         review_count  avg_rating
product_name
Alpine Explorer Tent                5    4.200000
Explorer Pro Backpack               3    3.666667
Peak Performer Boots                3    4.000000
TrailMaster X4 Tent                 3    3.333333
CozyNights Sleeping Bag             2    4.000000
DayTripper Pack                     2    3.500000
Summit Water Bottle                 2    2.500000
```

### 5c — Produto com Melhor Nota (2+ avaliações)

```python
multi_review = product_stats[product_stats["review_count"] >= 2]
best = multi_review.sort_values("avg_rating", ascending=False).iloc[0]
print(f"Highest-rated product (2+ reviews): {multi_review.sort_values('avg_rating', ascending=False).index[0]}")
print(f"  Average rating: {best['avg_rating']:.2f}")
```

**Esperado:**

```
Highest-rated product (2+ reviews): Alpine Explorer Tent
  Average rating: 4.20
```

### 5d — Sentimento por Categoria

```python
print("Sentiment distribution by category:")
print(pd.crosstab(reviews["category"], reviews["sentiment"]))
```

---

## Etapa 6: Considerações de Produção

Ao migrar de simulações para Fabric AI Functions reais, considere estes fatores:

### Tamanho do Lote

| Tamanho do Lote | Compensação |
|------------|-----------|
| Pequeno (1–10 linhas) | Maior latência por linha; mais fácil de depurar |
| Médio (50–100 linhas) | Bom equilíbrio entre throughput e custo |
| Grande (500+ linhas) | Throughput máximo; risco de timeouts e limites de taxa |

As funções `ai.*()` do Fabric lidam com agrupamento em lotes automaticamente, mas você pode ajustar:

```python
# In Fabric, control batch behavior via configuration
spark.conf.set("spark.synapse.ml.ai.batchSize", 50)
```

### Troca Simulado → Real

A principal vantagem da nossa abordagem de simulação primeiro: trocar para funções reais requer alterar apenas as implementações das funções:

```python
# ── Mock (local development) ────────────────────
reviews["sentiment"] = reviews["rating"].apply(mock_classify)

# ── Real Fabric (production) ────────────────────
# from synapse.ml.fabric import ai
# reviews["sentiment"] = ai.classify(reviews["review_text"],
#                                    ["positive", "neutral", "negative"])
```

### Conscientização de Custos

| Fator | Impacto |
|--------|--------|
| Contagem de tokens | Cada avaliação consome tokens de entrada; avaliações mais longas custam mais |
| Escolha do modelo | GPT-4o vs. GPT-4o-mini — diferença de custo de 10× |
| Chamadas redundantes | Faça cache dos resultados para evitar reprocessamento de linhas inalteradas |
| Contagem de colunas | Cada chamada `ai.*()` é uma invocação separada de LLM por linha |

!!! warning "Dica de Custo"
    Para 20 avaliações, o custo é insignificante. Para 200.000 avaliações, uma única coluna `ai.classify()` pode custar $50+ com GPT-4o. Sempre faça protótipos com uma amostra, valide os resultados e depois escale.

---

## 🐛 Exercício de Correção de Bugs

O arquivo `lab-053/broken_pipeline.py` tem **3 bugs** nas funções de enriquecimento de IA. Você consegue encontrar e corrigir todos?

Execute os auto-testes para ver quais falham:

```bash
python lab-053/broken_pipeline.py
```

Você deverá ver **3 testes falhando**. Cada teste corresponde a um bug:

| Teste | O que verifica | Dica |
|------|---------------|------|
| Teste 1 | Limites de classificação de sentimento | Rating 3 deve ser neutro, não positivo |
| Teste 2 | Agrupamento de avaliações por produto | Deve agrupar por `product_name`, não por `review_id` |
| Teste 3 | Nota média filtrada por sentimento | Deve filtrar o DataFrame antes de calcular a média |

Corrija todos os 3 bugs e execute novamente. Quando você ver `🎉 All 3 tests passed`, está feito!

---


## 🧠 Verificação de Conhecimento

??? question "**Q1 (Múltipla Escolha):** O que `ai.classify()` faz nas Fabric AI Functions?"

    - A) Divide texto em sentenças para processamento de NLP
    - B) Classifica texto em categorias predefinidas usando um LLM
    - C) Treina um modelo de classificação personalizado nos seus dados
    - D) Converte texto em vetores de características numéricas

    ??? success "✅ Revelar Resposta"
        **Correto: B) Classifica texto em categorias predefinidas usando um LLM**

        `ai.classify()` envia cada valor de texto para um LLM junto com os rótulos candidatos que você fornece (ex.: `["positive", "neutral", "negative"]`). O LLM retorna o rótulo que melhor corresponde. Ele não treina um modelo — usa o conhecimento existente do LLM via aprendizado em contexto.

??? question "**Q2 (Múltipla Escolha):** Por que o tamanho do lote é importante ao usar AI Functions em escala?"

    - A) Lotes maiores sempre produzem resultados mais precisos
    - B) O tamanho do lote determina qual modelo de LLM é usado
    - C) Equilibra throughput, custo e conformidade com limites de taxa
    - D) Lotes menores usam menos tokens por linha

    ??? success "✅ Revelar Resposta"
        **Correto: C) Equilibra throughput, custo e conformidade com limites de taxa**

        O tamanho do lote afeta quantas linhas são enviadas ao endpoint do LLM por requisição. Muito pequeno = alta sobrecarga de latência; muito grande = risco de erros de limite de taxa e timeouts. O tamanho ótimo de lote equilibra throughput (linhas/segundo), custo (tokens/requisição) e limites de taxa da API.

??? question "**Q3 (Execute o Lab):** Quantas avaliações têm sentimento positivo (rating ≥ 4)?"

    Aplique `mock_classify()` à coluna de rating e conte os valores `"positive"`.

    ??? success "✅ Revelar Resposta"
        **13**

        Ratings de 4 ou 5 mapeiam para `"positive"`. Há 9 avaliações com rating 4 e 4 avaliações com rating 5, totalizando **13 avaliações positivas** de 20.

??? question "**Q4 (Execute o Lab):** Qual produto tem mais avaliações?"

    Agrupe por `product_name` e conte as linhas.

    ??? success "✅ Revelar Resposta"
        **Alpine Explorer Tent — 5 avaliações**

        Alpine Explorer Tent (P001) tem avaliações R001–R005, tornando-o o produto mais avaliado. Os próximos produtos mais avaliados (Peak Performer Boots, Explorer Pro Backpack, TrailMaster X4 Tent) têm 3 avaliações cada.

??? question "**Q5 (Execute o Lab):** Qual é a nota média de todas as 20 avaliações?"

    Calcule `reviews["rating"].mean()`.

    ??? success "✅ Revelar Resposta"
        **3,70**

        Soma de todas as notas: 5+4+5+3+4+4+2+4+5+4+3+5+4+2+4+3+5+3+4+1 = 74. Média = 74 ÷ 20 = **3,70**.

---

## Resumo

| Tópico | O Que Você Aprendeu |
|-------|-----------------|
| AI Functions | `ai.classify`, `ai.summarize`, `ai.extract`, `ai.embed` como operações de DataFrame |
| Desenvolvimento com Simulação Primeiro | Construir e validar a lógica do pipeline antes de usar chamadas reais de LLM |
| Enriquecimento em Lote | Aplicar transformações de IA a cada linha de um conjunto de dados |
| Análise de Sentimento | Classificação baseada em nota: positivo (≥4), neutro (3), negativo (≤2) |
| Análise de Produtos | Análise de agrupamento em dados enriquecidos para insights de negócios |
| Prontidão para Produção | Tamanho do lote, custo, cache e padrões de troca simulação para real |

---

## Próximos Passos

- **[Lab 051](lab-051-fabric-iq-event-streams.md)** *(em breve)* — Fabric IQ — Processamento de Event Stream em Tempo Real
- **[Lab 052](lab-052-fabric-iq-nl-to-sql.md)** *(em breve)* — Fabric IQ — Linguagem Natural para SQL com IA