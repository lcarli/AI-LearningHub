---
tags: [free, beginner, no-account-needed, embeddings, rag]
---
# Lab 007: O que são Embeddings?

<div class="lab-meta">
  <span><strong>Nível:</strong> <span class="level-badge level-50">L50</span></span>
  <span><strong>Trilha:</strong> <a href="../paths/rag/">&#128218; RAG</a> &middot; <a href="../paths/semantic-kernel/">&#129504; Semantic Kernel</a></span>
  <span><strong>Tempo:</strong> ~15 min</span>
  <span><strong>&#128176; Custo:</strong> <span class="level-badge cost-free">Gratuito</span> &mdash; Nenhuma conta necessária</span>
</div>

## O que Você Vai Aprender

- O que é um embedding (um vetor / lista de números)
- Como texto é mapeado para um espaço de alta dimensão
- O que **similaridade cosseno** significa e por que importa
- Por que embeddings alimentam busca semântica, RAG e memória de agentes
- Quais modelos de embedding usar e quando

---

## Introdução

Embeddings são o motor por trás da busca semântica, RAG e memoria vetorial em agentes de IA. Uma vez que você entende o que sao, muita "mágica" em sistemas de IA se torna óbvia.

A ideia central é simples: **converter qualquer pedaco de texto em uma lista de números (um vetor) de forma que textos similares produzam vetores similares.**

---

## &#128230; Arquivos de Apoio

!!! note "Baixe estes arquivos antes de iniciar o lab"
    Salve todos os arquivos em uma pasta `lab-007/` no seu diretório de trabalho.

| Arquivo | Descrição | Download |
|------|-------------|----------|
| `embedding_explorer.py` | Script de exercícios interativos | [&#128229; Download](https://github.com/lcarli/AI-LearningHub/raw/main/docs/docs/en/labs/lab-007/embedding_explorer.py) |

---

## Parte 1: Texto como um Ponto no Espaço

Imagine um mapa 2D onde cada palavra é posicionada com base no seu significado:

![Espaço de Embedding 2D](../../assets/diagrams/embedding-space-2d.svg)

Palavras com significados similares se agrupam. "Dog" está perto de "Cat" e "Pet". "Python" se agrupa perto de "Code" e "Programming" -- não perto de "Snake" (em um corpus focado em codigo).

Modelos de embedding reais não usam 2 dimensões -- eles usam **1.536** (OpenAI) ou **3.072** dimensões. Mas o princípio é o mesmo: significado similar = ponto próximo no espaço.

??? question "&#129300; Verifique Seu Entendimento"
    Por que modelos de embedding usam 1.536 dimensões em vez de apenas 2 ou 3?

    ??? success "Resposta"
        A linguagem humana tem enorme complexidade -- sinônimos, contexto, tom, significado específico de domínio. Duas ou tres dimensoes não conseguem capturar todas essas nuances. **Dimensões mais altas** permitem que o modelo codifique muitos aspectos diferentes de significado simultaneamente, para que distinções sutis (como "Python a linguagem" vs. "python a cobra") possam ser representadas como direções diferentes no espaço vetorial.

---

## Parte 2: Como um Embedding Realmente É

Quando você faz o embedding do texto `"waterproof hiking boots"`, você recebe de volta algo como:

```python
[0.023, -0.157, 0.842, 0.001, -0.334, 0.711, ..., 0.089]
# ^ 1,536 numbers for text-embedding-3-small
```

Cada numero codifica algum aspecto do significado -- mas não há interpretação legível por humanos de dimensoes individuais. O significado vive nas *relações* entre vetores.

---

## Parte 3: Medindo Similaridade -- Distância Cosseno

Para comparar dois vetores, usamos **similaridade cosseno**: o ângulo entre eles.

```
Vector A ("waterproof hiking boots")
      /

Vector B ("weatherproof trekking shoes")  <- small angle -> very similar
      / (almost same direction)

Vector C ("chocolate birthday cake")      <- large angle -> very different
->  (completely different direction)
```

A similaridade cosseno varia de **-1 a 1**:
- `1.0` = significado idêntico
- `0.0` = sem relação
- `-1.0` = significado oposto

Na pratica, a maioria dos documentos similares tem pontuação entre **0,7 e 0,95**.

??? question "&#129300; Verifique Seu Entendimento"
    Dois textos tem uma similaridade cosseno de 0,05. O que isso diz sobre a relação deles?

    ??? success "Resposta"
        Uma similaridade cosseno de 0,05 significa que os textos sao **essencialmente sem relação** -- seus vetores apontam em direções quase perpendiculares. Na escala de -1 a 1, uma pontuacao proxima de 0 indica nenhuma conexão semântica significativa. Documentos similares tipicamente pontuam entre 0,7 e 0,95.

---

```python
# Simplified cosine similarity
import numpy as np

def cosine_similarity(a, b):
    return np.dot(a, b) / (np.linalg.norm(a) * np.linalg.norm(b))

# "king" - "man" + "woman" ~ "queen"  (the famous word2vec example)
similarity = cosine_similarity(embed("king"), embed("queen"))
# -> ~0.89 (very similar)

similarity = cosine_similarity(embed("king"), embed("pizza"))
# -> ~0.12 (unrelated)
```

---

## Parte 4: Onde Embeddings São Usados em Sistemas de Agentes

### 1. Busca Semântica (RAG)
```
User query: "something to keep rain out while hiking"
         | embed
[0.023, -0.157, ...]
         | compare with all document vectors
Matches: "waterproof hiking jacket" (0.91)
         "rain-resistant trekking gear" (0.88)
         "chocolate cake recipe" (0.08) <- filtered out
```

### 2. Memória do Agente (Semantic Kernel / LangChain)
A memória de longo prazo do agente armazena interações passadas como embeddings. Quando o usuário menciona um tópico, o agente recupera memórias semanticamente relevantes:

```
User: "Let's continue our discussion about the camping budget"
         | embed query
Retrieves: previous conversation about camping (0.87 similarity)
Not: unrelated conversation about software (0.12 similarity)
```

### 3. Detecção de Duplicatas
```
"How do I return a product?" (0.94 similarity)
"What's your return policy?"
-> Detected as duplicates -> merge/deduplicate FAQs
```

### 4. Clusterização / Categorização
Agrupe documentos automaticamente por significado sem categorias predefinidas.

---

## Parte 5: Modelos de Embedding

| Modelo | Dimensões | Contexto | Custo | Melhor para |
|-------|-----------|---------|------|---------|
| `text-embedding-3-small` (OpenAI) | 1.536 | 8.191 tokens | Baixo | Maioria dos casos de uso |
| `text-embedding-3-large` (OpenAI) | 3.072 | 8.191 tokens | Mais alto | Maior precisão |
| `text-embedding-ada-002` (OpenAI) | 1.536 | 8.191 tokens | Baixo | Legado |
| `nomic-embed-text` (Ollama) | 768 | 8.192 tokens | **Gratuito (local)** | Offline/privado |
| `mxbai-embed-large` (Ollama) | 1.024 | 512 tokens | **Gratuito (local)** | Produção local |

??? question "&#129300; Verifique Seu Entendimento"
    Seu sistema RAG ingeriu todos os documentos usando `text-embedding-3-small`. Voce depois muda para `text-embedding-3-large` para consultas. O sistema ainda funcionará corretamente?

    ??? success "Resposta"
        **Não.** Vetores de modelos de embedding diferentes sao **incompatíveis** -- eles mapeiam para espaços vetoriais diferentes com dimensões diferentes (1.536 vs. 3.072). Compara-los produziria pontuações de similaridade sem significado. Voce deve **sempre usar o mesmo modelo** tanto para ingestao quanto para consulta, ou refazer o embedding de todos os documentos com o novo modelo.

!!! tip "Use text-embedding-3-small via GitHub Models (gratuito)"
    Nos labs L200 deste hub, usamos `text-embedding-3-small` via a API do GitHub Models -- gratuito, sem cartão de crédito, mesma qualidade do Azure OpenAI pago.

---

## Parte 6: Propriedades-Chave e Armadilhas

### Embeddings capturam significado entre idiomas
```
embed("waterproof jacket") ~ embed("veste impermeable")  # French
```
Modelos multilingues funcionam entre idiomas -- consultas em um idioma podem encontrar documentos em outro.

### Embeddings sao específicos do modelo
Vetores de `text-embedding-3-small` **não são comparáveis** com vetores de `nomic-embed-text`. Nunca misture modelos no mesmo banco vetorial.

### Embeddings nao capturam correspondências exatas bem
```
embed("SKU-12345") may not match embed("product SKU-12345")
```
Para IDs exatos, códigos ou palavras-chave, use busca por palavras-chave/BM25 junto com embeddings (busca híbrida).

### Texto longo perde detalhes
Fazer embedding de um documento de 10 páginas em um vetor único perde significado detalhado. E por isso que **fragmentamos** primeiro, depois fazemos embedding de cada fragmento separadamente.

---

## Prática: Explorador de Embeddings

Este lab inclui um script Python que permite **ver embeddings em acao** usando o nível gratuito do GitHub Models.

```
lab-007/
 embedding_explorer.py   <- Cosine similarity demo with OutdoorGear products
```

**Pré-requisitos:** Python 3.9+ e um token GitHub (gratuito)

```bash
# Install dependencies
pip install openai

# Set your GitHub token
export GITHUB_TOKEN=<your_PAT>    # Linux/macOS
set GITHUB_TOKEN=<your_PAT>       # Windows

# Run the explorer
python lab-007/embedding_explorer.py
```

**O que você verá:**

1. **Busca semantica:** Encontre produtos correspondendo "lightweight tent for solo hiking" sem correspondência de palavras-chave
2. **Semantico vs. palavras-chave:** Compare como a busca por palavras-chave perde "something to sleep in the cold" enquanto a busca semântica encontra o saco de dormir
3. **Matriz de similaridade:** Veja que duas descrições de barracas têm pontuação de similaridade mais alta entre si do que uma barraca vs. um saco de dormir

Isso ilustra diretamente por que RAG funciona: o embedding de uma *pergunta* e o embedding do seu *documento de resposta* ficam proximos no espaco vetorial.

---

## &#129504; Verificação de Conhecimento

??? question "**Q1 (Múltipla Escolha):** Duas descrições de produtos têm uma similaridade cosseno de 0,95. O que isso significa?"

    - A) Sao produtos completamente sem relação
    - B) Compartilham 95% das mesmas palavras
    - C) Sao semanticamente muito similares -- suas representações vetoriais apontam em direções quase iguais
    - D) Um documento e 95% mais longo que o outro

    ??? success "Revelar Resposta"
        **Correta: C**

        Similaridade cosseno mede o *ângulo* entre dois vetores, nao sobreposição de palavras. Uma pontuacao de 0,95 significa que os vetores apontam em direções quase iguais -- os textos sao semanticamente muito similares. Na pratica: produtos da mesma categoria como duas barracas pontuam ~0,90-0,96; produtos sem relação (barraca vs mochila) pontuam ~0,70-0,82; texto completamente sem relação pontua < 0,5.

??? question "**Q2 (Múltipla Escolha):** Seu sistema RAG usa `text-embedding-3-small` para ingestao de documentos mas `text-embedding-3-large` para embedding de consultas. O que vai acontecer?"

    - A) Consultas serao mais lentas mas mais precisas
    - B) Pontuacoes de similaridade serao sem significado — você está comparando vetores de espacos diferentes
    - C) O sistema normalizara automaticamente os vetores para serem compatíveis
    - D) O desempenho melhora porque o modelo maior fornece compreensão mais rica da consulta

    ??? success "Revelar Resposta"
        **Correta: B -- Vetores de modelos diferentes sao incompatíveis**

        Cada modelo de embedding mapeia texto para seu proprio espaço de alta dimensão único. `text-embedding-3-small` produz vetores de 1.536 dimensoes; `text-embedding-3-large` produz vetores de 3.072 dimensoes. Mesmo se voce forçasse as mesmas dimensões, os significados numéricos são completamente diferentes. Voce obteria pontuações de similaridade aleatorias. **Sempre use o mesmo modelo tanto para ingestao quanto para consulta.**

??? question "**Q3 (Execute o Lab):** Execute `python lab-007/embedding_explorer.py`. Na saida da matriz de similaridade, quais dois produtos (além de um produto comparado consigo mesmo) têm a MAIOR pontuação de similaridade cosseno entre si?"

    Execute o script e observe a seção da matriz de similaridade no final da saída.

    ??? success "Revelar Resposta"
        **P001 (TrailBlazer Tent 2P) e P003 (TrailBlazer Solo)**

        Ambas sao barracas de mochileiro de 3 estações com descrições muito similares -- mesma categoria, mesma estacao, mesmos materiais de construção. Suas descrições compartilham a maior sobreposição semântica no catálogo. Pontuação típica: **~0,93-0,97**. Em contraste, uma barraca vs. um saco de dormir pontua muito mais baixo (~0,75-0,85) porque servem a propósitos diferentes apesar de ambos serem equipamento de camping.

---

## Resumo

| Conceito | Principal aprendizado |
|---------|-------------|
| **Embedding** | Uma lista de ~1.536 números representando significado de texto |
| **Similaridade cosseno** | Mede ângulo entre vetores; mais próximo = mais similar |
| **Busca semantica** | Encontra conteúdo relevante por significado, nao palavras exatas |
| **Específico do modelo** | Nunca misture vetores de modelos de embedding diferentes |
| **Fragmentar primeiro** | Faça embedding de fragmentos, nao documentos inteiros |
| **Opção gratuita** | `text-embedding-3-small` via GitHub Models ou `nomic-embed-text` via Ollama |

---

## Próximos Passos

- **Veja embeddings em um app RAG:** -> [Lab 022 -- RAG com GitHub Models + pgvector](lab-022-rag-github-models-pgvector.md)
- **Execute embeddings localmente de graça:** -> [Lab 015 -- Ollama LLMs Locais](lab-015-ollama-local-llms.md)
- **Use embeddings no Semantic Kernel:** -> [Lab 023 -- SK Plugins, Memória e Planejadores](lab-023-sk-plugins-memory.md)
