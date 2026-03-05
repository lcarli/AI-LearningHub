---
tags: [graphrag, knowledge-graph, rag, python]
---
# Lab 067: GraphRAG — Grafos de Conhecimento para Recuperação Entre Documentos

<div class="lab-meta">
  <span><strong>Nível:</strong> <span class="level-badge level-300">L300</span></span>
  <span><strong>Trilha:</strong> Todas as trilhas</span>
  <span><strong>Tempo:</strong> ~90 min</span>
  <span><strong>💰 Custo:</strong> <span class="level-badge cost-free">Gratuito</span> — Dados simulados (não requer Azure OpenAI ou banco de dados de grafos)</span>
</div>

## O que Você Vai Aprender

- O que é **GraphRAG** e como ele difere do RAG tradicional baseado apenas em vetores
- Construir um **grafo de conhecimento** a partir da extração de entidades e relacionamentos
- Detectar **comunidades** usando algoritmos de agrupamento em grafos
- Executar **consultas globais** que sintetizam informações de todos os documentos
- Executar **consultas locais** que percorrem subgrafos centrados em entidades
- Avaliar a qualidade da recuperação usando **pontuação de importância** e cobertura de comunidades

!!! abstract "Pré-requisitos"
    Complete primeiro o **[Lab 009: Geração Aumentada por Recuperação](lab-009-rag-basic.md)**. Este laboratório pressupõe familiaridade com conceitos básicos de RAG, incluindo chunking, embedding e busca vetorial.

## Introdução

O RAG tradicional recupera trechos individuais por similaridade semântica. Isso funciona bem para **consultas locais** ("Qual é a política de devolução?"), mas falha para **consultas globais** que exigem a síntese de informações de vários documentos ("Quais são os principais temas nos resultados do 3º trimestre de todas as empresas do portfólio?").

O **GraphRAG** resolve isso construindo um **grafo de conhecimento** a partir de entidades e relacionamentos extraídos, e depois agrupando o grafo em **comunidades** que representam grupos temáticos:

| Abordagem | Método de Recuperação | Melhor Para | Fraqueza |
|----------|-----------------|----------|----------|
| **Vector RAG** | Similaridade por cosseno em embeddings | Consultas locais e específicas | Não consegue sintetizar entre documentos |
| **GraphRAG Local** | Percurso de subgrafo centrado em entidade | Consultas sobre entidades específicas | Perde temas globais |
| **GraphRAG Global** | Resumos de comunidade + map-reduce | Consultas amplas entre documentos | Maior latência e custo |

### O Cenário

Você está construindo um **sistema de inteligência de mercado** para uma empresa de equipamentos para atividades ao ar livre. Seu corpus contém avaliações de produtos, relatórios de fornecedores e documentos de análise de concorrentes. Você irá extrair entidades, construir um grafo de conhecimento, detectar comunidades e comparar o desempenho de consultas locais versus globais.

O grafo de conhecimento contém **15 entidades** organizadas em **8 comunidades**.

---

## Pré-requisitos

| Requisito | Por quê |
|---|---|
| Python 3.10+ | Executar scripts de análise |
| `pandas` | Analisar dados do grafo de conhecimento |

```bash
pip install pandas
```

---

!!! tip "Início Rápido com GitHub Codespaces"
    [![Open in GitHub Codespaces](https://github.com/codespaces/badge.svg)](https://codespaces.new/lcarli/AI-LearningHub?quickstart=1)

    Todas as dependências já estão pré-instaladas no devcontainer.


## 📦 Arquivos de Apoio

!!! note "Baixe estes arquivos antes de iniciar o laboratório"
    Salve todos os arquivos em uma pasta `lab-067/` no seu diretório de trabalho.

| Arquivo | Descrição | Download |
|------|-------------|----------|
| `broken_graphrag.py` | Exercício de correção de bugs (3 bugs + autotestes) | [📥 Download](https://github.com/lcarli/AI-LearningHub/raw/main/docs/docs/en/labs/lab-067/broken_graphrag.py) |
| `knowledge_graph.csv` | Conjunto de dados | [📥 Download](https://github.com/lcarli/AI-LearningHub/raw/main/docs/docs/en/labs/lab-067/knowledge_graph.csv) |

---

## Etapa 1: Entendendo a Arquitetura do GraphRAG

O GraphRAG estende o pipeline de RAG com construção de grafos e detecção de comunidades:

```
Documents → [Entity Extraction] → [Relationship Extraction] → Knowledge Graph
                                                                     ↓
Query → [Community Detection] → [Community Summaries] → [Map-Reduce Answer]
                                        ↓
                              [Local Subgraph] → [Entity-Centric Answer]
```

Conceitos-chave:

1. **Entidades** — Pessoas, organizações, produtos e conceitos extraídos do texto
2. **Relacionamentos** — Conexões entre entidades (ex.: "EmpresaA *fornece para* EmpresaB")
3. **Comunidades** — Agrupamentos de entidades densamente conectadas descobertos por algoritmos de grafos
4. **Resumos de Comunidade** — Descrições geradas por LLM sobre o tema de cada comunidade
5. **Pontuação de Importância** — Métrica de centralidade (0–1) indicando a relevância de uma entidade

!!! info "Por que as Comunidades São Importantes"
    As comunidades agrupam entidades relacionadas que frequentemente coocorrem. Uma consulta global como "Quais são as tendências do mercado?" pode ser respondida sintetizando resumos de comunidades em vez de varrer cada trecho de documento — reduzindo drasticamente o uso de tokens e melhorando a cobertura.

---

## Etapa 2: Carregar e Explorar o Grafo de Conhecimento

O conjunto de dados contém **15 entidades** com relacionamentos e atribuições de comunidade:

```python
import pandas as pd

kg = pd.read_csv("lab-067/knowledge_graph.csv")
print(f"Total entities: {len(kg)}")
print(f"Entity types: {sorted(kg['entity_type'].unique())}")
print(f"Communities: {sorted(kg['community_id'].unique())}")
print(f"Number of communities: {kg['community_id'].nunique()}")
print(f"\nEntities per community:")
print(kg.groupby("community_id")["entity_id"].count().sort_values(ascending=False))
```

**Esperado:**

```
Total entities: 15
Communities: [0, 1, 2, 3, 4, 5, 6, 7]
Number of communities: 8
```

---

## Etapa 3: Análise de Importância das Entidades

Analise as pontuações de importância das entidades para identificar os nós-chave do grafo:

```python
print("Top entities by importance score:")
top_entities = kg.sort_values("importance_score", ascending=False).head(5)
print(top_entities[["entity_id", "entity_name", "entity_type", "importance_score", "community_id"]]
      .to_string(index=False))

print(f"\nHighest importance entity: {kg.loc[kg['importance_score'].idxmax(), 'entity_name']} "
      f"({kg['importance_score'].max():.2f})")
print(f"Average importance score: {kg['importance_score'].mean():.2f}")
```

**Esperado:**

```
Highest importance entity: OutdoorGear Inc (0.98)
```

!!! tip "Centralidade e Importância"
    A pontuação de importância reflete o quão central uma entidade é no grafo de conhecimento. Entidades com pontuações altas (como OutdoorGear Inc com 0,98) conectam muitas outras entidades e comunidades. Consultas que envolvem essas entidades-hub percorrerão mais partes do grafo, fornecendo um contexto mais rico.

---

## Etapa 4: Análise da Estrutura de Comunidades

Examine a estrutura e os temas das comunidades:

```python
print(f"Total communities: {kg['community_id'].nunique()}")
print(f"\nCommunity sizes:")
community_sizes = kg.groupby("community_id").agg(
    entity_count=("entity_id", "count"),
    avg_importance=("importance_score", "mean"),
    entities=("entity_name", lambda x: ", ".join(x))
).sort_values("entity_count", ascending=False)
print(community_sizes.to_string())
```

**Esperado:**

```
Total communities: 8
```

!!! info "Detecção de Comunidades"
    As comunidades são detectadas usando o algoritmo Leiden, que identifica subgrafos densamente conectados. Cada comunidade representa um agrupamento temático — por exemplo, uma comunidade pode conter entidades relacionadas a fornecedores enquanto outra agrupa entidades de concorrentes. O número e o tamanho das comunidades dependem da estrutura de conectividade do grafo.

---

## Etapa 5: Simulação de Consultas Locais vs Globais

Simule como consultas locais e globais percorrem o grafo de maneiras diferentes:

```python
# Local query: find entities related to a specific entity
target_entity = kg.loc[kg["importance_score"].idxmax(), "entity_name"]
target_community = kg.loc[kg["importance_score"].idxmax(), "community_id"]
local_results = kg[kg["community_id"] == target_community]
print(f"Local query for '{target_entity}':")
print(f"  Community {target_community} has {len(local_results)} entities")
print(f"  Entities: {', '.join(local_results['entity_name'].tolist())}")

# Global query: summarize across all communities
print(f"\nGlobal query — all communities:")
for cid in sorted(kg["community_id"].unique()):
    community = kg[kg["community_id"] == cid]
    print(f"  Community {cid}: {len(community)} entities — "
          f"{', '.join(community['entity_name'].tolist())}")
```

---

## Etapa 6: Métricas de Qualidade do Grafo

Avalie a qualidade do grafo de conhecimento:

```python
total_entities = len(kg)
total_communities = kg["community_id"].nunique()
avg_community_size = total_entities / total_communities
max_importance = kg["importance_score"].max()
min_importance = kg["importance_score"].min()

report = f"""
╔════════════════════════════════════════════════════════╗
║     GraphRAG — Knowledge Graph Quality Report          ║
╠════════════════════════════════════════════════════════╣
║ Total Entities:              {total_entities:>5}                     ║
║ Total Communities:           {total_communities:>5}                     ║
║ Avg Community Size:          {avg_community_size:>5.1f}                     ║
║ Max Importance Score:        {max_importance:>5.2f}                     ║
║ Min Importance Score:        {min_importance:>5.2f}                     ║
║ Entity Types:                {kg['entity_type'].nunique():>5}                     ║
╚════════════════════════════════════════════════════════╝
"""
print(report)
```

---

## 🐛 Exercício de Correção de Bugs

O arquivo `lab-067/broken_graphrag.py` possui **3 bugs** em como ele processa o grafo de conhecimento:

```bash
python lab-067/broken_graphrag.py
```

| Teste | O que verifica | Dica |
|------|---------------|------|
| Teste 1 | Contagem de entidades | Deve contar todas as linhas do DataFrame, não os IDs únicos de comunidade |
| Teste 2 | Contagem de comunidades | Deve usar `nunique()` em `community_id`, não `count()` |
| Teste 3 | Entidade de maior importância | Deve usar `idxmax()` em `importance_score`, não `idxmin()` |

---


## 🧠 Verificação de Conhecimento

??? question "**Q1 (Múltipla Escolha):** Qual problema o GraphRAG resolve que o RAG vetorial tradicional não consegue?"

    - A) Geração mais rápida de embeddings
    - B) Síntese entre documentos para consultas globais usando resumos em nível de comunidade
    - C) Custos menores de armazenamento para embeddings
    - D) Melhor tokenização dos documentos de origem

    ??? success "✅ Revelar Resposta"
        **Correta: B) Síntese entre documentos para consultas globais usando resumos em nível de comunidade**

        O RAG vetorial tradicional recupera trechos individuais por similaridade, o que funciona para consultas locais mas falha quando a resposta requer sintetizar informações espalhadas por vários documentos. O GraphRAG constrói um grafo de conhecimento, detecta comunidades de entidades relacionadas e usa resumos de comunidade para responder consultas globais via map-reduce.

??? question "**Q2 (Múltipla Escolha):** O que é uma 'comunidade' no contexto do GraphRAG?"

    - A) Um grupo de usuários que compartilham o mesmo agente
    - B) Um agrupamento de entidades densamente conectadas no grafo de conhecimento que representa um grupo temático
    - C) Um tipo de partição de índice vetorial
    - D) Uma conversa com múltiplos participantes

    ??? success "✅ Revelar Resposta"
        **Correta: B) Um agrupamento de entidades densamente conectadas no grafo de conhecimento que representa um grupo temático**

        As comunidades são descobertas por algoritmos de agrupamento em grafos como o Leiden. Entidades dentro de uma comunidade são mais densamente conectadas entre si do que com entidades fora da comunidade. Cada comunidade recebe um resumo gerado por LLM que captura seu tema, permitindo respostas eficientes a consultas globais.

??? question "**Q3 (Execute o Lab):** Quantas entidades no total existem no grafo de conhecimento?"

    Carregue o CSV do grafo de conhecimento e conte o total de linhas.

    ??? success "✅ Revelar Resposta"
        **15 entidades**

        O grafo de conhecimento contém 15 entidades abrangendo vários tipos (organizações, produtos, pessoas, conceitos). Essas entidades são conectadas por meio de relacionamentos extraídos dos documentos de origem.

??? question "**Q4 (Execute o Lab):** Quantas comunidades foram detectadas no grafo de conhecimento?"

    Use `nunique()` na coluna `community_id`.

    ??? success "✅ Revelar Resposta"
        **8 comunidades**

        As 15 entidades estão organizadas em 8 comunidades pelo algoritmo de agrupamento Leiden. Cada comunidade representa um grupo temático de entidades relacionadas — por exemplo, relacionamentos com fornecedores, cenário competitivo ou categorias de produtos.

??? question "**Q5 (Execute o Lab):** Qual entidade possui a maior pontuação de importância e qual é a pontuação?"

    Ordene por `importance_score` em ordem decrescente e verifique a entidade no topo.

    ??? success "✅ Revelar Resposta"
        **OutdoorGear Inc com uma pontuação de importância de 0,98**

        OutdoorGear Inc é a entidade mais central no grafo de conhecimento, conectando-se a entidades de várias comunidades. Sua alta pontuação de importância (0,98) reflete seu papel como hub — consultas envolvendo essa entidade percorrerão mais partes do grafo e fornecerão um contexto mais rico entre documentos.

---

## Resumo

| Tópico | O que Você Aprendeu |
|-------|-----------------|
| GraphRAG | Estende o RAG com grafos de conhecimento para síntese entre documentos |
| Extração de Entidades | Identificar pessoas, organizações e conceitos a partir de documentos |
| Detecção de Comunidades | Agrupar entidades relacionadas para descobrir grupos temáticos |
| Consultas Locais | Percorrer subgrafos centrados em entidades para respostas específicas |
| Consultas Globais | Sintetizar resumos de comunidades via map-reduce para respostas amplas |
| Pontuação de Importância | Classificar entidades por centralidade no grafo para identificar nós-chave |

---

## Próximos Passos

- **[Lab 009](lab-009-rag-basic.md)** — Fundamentos de RAG (padrões básicos de recuperação)
- **[Lab 068](lab-068-hybrid-search.md)** — Busca Híbrida (estratégias complementares de recuperação)
- **[Lab 065](lab-065-purview-dspm-ai.md)** — Purview DSPM for AI (governança para pipelines de RAG)
