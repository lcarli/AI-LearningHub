---
tags: [deep-research, multi-agent, synthesis, citations, python]
---
# Lab 079: Deep Research Agents — Síntese de Conhecimento em Múltiplas Etapas

<div class="lab-meta">
  <span><strong>Nível:</strong> <span class="level-badge level-300">L300</span></span>
  <span><strong>Trilha:</strong> Todas as trilhas</span>
  <span><strong>Tempo:</strong> ~90 min</span>
  <span><strong>💰 Custo:</strong> <span class="level-badge cost-free">Gratuito</span> — Usa dados simulados de rastreamento de pesquisa</span>
</div>

## O que Você Vai Aprender

- Como **Deep Research Agents** usam um pipeline multi-agente para síntese de conhecimento
- A arquitetura **Planner → Researcher → Writer → Reviewer** e as responsabilidades de cada papel
- Como o **rastreamento de citações** garante que cada afirmação seja mapeada de volta a uma fonte
- Analisar um **rastreamento de pesquisa de 14 etapas** com papéis de agentes, uso de tokens e pontuações de qualidade
- Identificar gargalos, distribuição de tokens e padrões de qualidade ao longo do pipeline

## Introdução

**Deep Research Agents** implementam um pipeline de múltiplas etapas para produzir relatórios de pesquisa abrangentes e bem referenciados. Em vez de um único LLM gerar um relatório inteiro, o trabalho é dividido entre agentes especializados:

### O Pipeline

```
  ┌──────────┐     ┌────────────┐     ┌──────────┐     ┌──────────┐
  │ Planner  │────►│ Researcher │────►│  Writer  │────►│ Reviewer │
  └──────────┘     └────────────┘     └──────────┘     └──────────┘
       │                 │                  │                │
  Decompõe          Coleta info        Sintetiza        Revisa &
  consulta em       das fontes         descobertas      fornece
  sub-perguntas     com citações       em relatório     feedback
```

| Agente | Papel | Saída Principal |
|--------|-------|----------------|
| **Planner** | Decompõe a pergunta de pesquisa em sub-perguntas e cria um plano de pesquisa | Sub-perguntas, estratégia de busca |
| **Researcher** | Executa buscas, lê fontes, extrai descobertas principais com citações | Descobertas com citações de fontes |
| **Writer** | Sintetiza descobertas em um relatório coerente e bem estruturado | Rascunho do relatório com citações inline |
| **Reviewer** | Revisa o rascunho quanto à precisão, completude e qualidade das citações | Feedback, pontuação de qualidade, aprovação/revisão |

### Rastreamento de Citações

Cada afirmação no relatório final deve ser rastreável até uma fonte. O pipeline rastreia:

- **sources_cited**: Número de fontes únicas citadas em cada etapa
- **quality_score**: Autoavaliação de qualidade da saída pelo agente (0.0–1.0)

### O Cenário

Você é um **Líder de Equipe de Pesquisa** avaliando um sistema de agentes de pesquisa profunda. Você tem um **rastreamento de pesquisa de 14 etapas** (`research_trace.csv`) de uma execução de pesquisa concluída. Sua tarefa: analisar o rastreamento para entender o comportamento dos agentes, uso de tokens, padrões de qualidade e identificar oportunidades de otimização.

!!! info "Dados Simulados"
    Este laboratório usa um CSV de rastreamento de pesquisa simulado. Os dados representam uma execução realista de pesquisa profunda com 14 etapas em 4 papéis de agentes, incluindo planejamento, pesquisa multi-fonte, escrita e revisão iterativa.

## Pré-requisitos

| Requisito | Por quê |
|---|---|
| Python 3.10+ | Executar os scripts de análise |
| Biblioteca `pandas` | Manipulação de dados |

```bash
pip install pandas
```

---

!!! tip "Início Rápido com GitHub Codespaces"
    [![Open in GitHub Codespaces](https://github.com/codespaces/badge.svg)](https://codespaces.new/lcarli/AI-LearningHub?quickstart=1)

    Todas as dependências estão pré-instaladas no devcontainer.


## 📦 Arquivos de Apoio

!!! note "Baixe estes arquivos antes de iniciar o laboratório"
    Salve todos os arquivos em uma pasta `lab-079/` no seu diretório de trabalho.

| Arquivo | Descrição | Download |
|---------|-----------|----------|
| `broken_research.py` | Exercício de correção de bugs (3 bugs + autotestes) | [📥 Download](https://github.com/lcarli/AI-LearningHub/raw/main/docs/docs/en/labs/lab-079/broken_research.py) |
| `research_trace.csv` | Rastreamento de pesquisa de 14 etapas com papéis de agentes, tokens e qualidade | [📥 Download](https://github.com/lcarli/AI-LearningHub/raw/main/docs/docs/en/labs/lab-079/research_trace.csv) |

---

## Etapa 1: Entenda o Formato do Rastreamento

Cada linha no rastreamento representa uma etapa no pipeline de pesquisa:

| Coluna | Descrição |
|--------|-----------|
| **step_id** | Número sequencial da etapa (1–14) |
| **agent_role** | Qual agente executou esta etapa: `planner`, `researcher`, `writer`, `reviewer` |
| **action** | O que o agente fez (ex.: `decompose_query`, `search_sources`, `write_section`) |
| **tokens_used** | Número de tokens consumidos nesta etapa |
| **sources_cited** | Número de fontes citadas na saída desta etapa |
| **quality_score** | Avaliação de qualidade da saída desta etapa (0.0–1.0) |
| **duration_sec** | Tempo gasto nesta etapa em segundos |

---

## Etapa 2: Carregue e Explore o Rastreamento

```python
import pandas as pd

df = pd.read_csv("lab-079/research_trace.csv")

print(f"Total steps: {len(df)}")
print(f"Agent roles: {df['agent_role'].value_counts().to_dict()}")
print(f"Total tokens: {df['tokens_used'].sum():,}")
print(f"Total sources cited: {df['sources_cited'].sum()}")
print(f"\nFull trace:")
print(df[["step_id", "agent_role", "action", "tokens_used", "sources_cited", "quality_score"]].to_string(index=False))
```

**Saída esperada:**

```
Total steps: 14
Agent roles: {'researcher': 6, 'writer': 4, 'reviewer': 2, 'planner': 2}
Total tokens: varies
Total sources cited: 10
```

---

## Etapa 3: Analise o Uso de Tokens por Agente

```python
print("Token usage by agent role:\n")
for role, group in df.groupby("agent_role"):
    total_tokens = group["tokens_used"].sum()
    avg_tokens = group["tokens_used"].mean()
    steps = len(group)
    print(f"  {role:>12s}: {total_tokens:>7,} tokens across {steps} steps (avg {avg_tokens:,.0f}/step)")

print(f"\nTotal tokens: {df['tokens_used'].sum():,}")
```

```python
# Token share by agent
total_tokens = df["tokens_used"].sum()
print("\nToken distribution:")
for role, group in df.groupby("agent_role"):
    share = group["tokens_used"].sum() / total_tokens * 100
    bar = "█" * int(share / 2)
    print(f"  {role:>12s}: {share:>5.1f}% {bar}")
```

!!! tip "Insight de Otimização"
    O **Researcher** normalmente consome a maior quantidade de tokens porque processa múltiplas fontes por sub-pergunta. Para reduzir custos, considere armazenar em cache as extrações de fontes e limitar o número de fontes por sub-pergunta.

---

## Etapa 4: Analise o Fluxo de Citações

```python
print("Citation flow through the pipeline:\n")
for _, row in df.iterrows():
    cited = "📚" * row["sources_cited"] if row["sources_cited"] > 0 else "—"
    print(f"  Step {row['step_id']:>2}: [{row['agent_role']:>10s}] {row['action']:<25s} sources={row['sources_cited']}  {cited}")

total_sources = df["sources_cited"].sum()
print(f"\nTotal sources cited across all steps: {total_sources}")

# Sources by agent role
print("\nSources cited by role:")
for role, group in df.groupby("agent_role"):
    print(f"  {role:>12s}: {group['sources_cited'].sum()} sources")
```

---

## Etapa 5: Análise de Qualidade

```python
print("Quality scores by agent role:\n")
for role, group in df.groupby("agent_role"):
    avg_q = group["quality_score"].mean()
    min_q = group["quality_score"].min()
    max_q = group["quality_score"].max()
    print(f"  {role:>12s}: avg={avg_q:.2f}  min={min_q:.2f}  max={max_q:.2f}")

# Find the lowest-quality step
worst_step = df.loc[df["quality_score"].idxmin()]
print(f"\nLowest quality step:")
print(f"  Step {worst_step['step_id']}: [{worst_step['agent_role']}] {worst_step['action']}")
print(f"  Quality: {worst_step['quality_score']}")
print(f"  Tokens: {worst_step['tokens_used']}")

# Find the highest-quality step
best_step = df.loc[df["quality_score"].idxmax()]
print(f"\nHighest quality step:")
print(f"  Step {best_step['step_id']}: [{best_step['agent_role']}] {best_step['action']}")
print(f"  Quality: {best_step['quality_score']}")
```

!!! warning "Variância de Qualidade"
    Fique atento a **quedas de qualidade nas etapas posteriores do Researcher** — isso frequentemente indica esgotamento de fontes (o agente está encontrando fontes de menor qualidade para sub-perguntas mais difíceis). Considere adicionar um limiar de qualidade que acione uma nova busca com consultas alternativas.

---

## Etapa 6: Construa o Relatório de Análise da Pesquisa

```python
writer_tokens = df[df["agent_role"] == "writer"]["tokens_used"].sum()
researcher_steps = len(df[df["agent_role"] == "researcher"])
total_duration = df["duration_sec"].sum()

report = f"""# 📋 Deep Research Trace Analysis

## Pipeline Summary
| Metric | Value |
|--------|-------|
| Total Steps | {len(df)} |
| Total Tokens | {df['tokens_used'].sum():,} |
| Total Sources Cited | {total_sources} |
| Total Duration | {total_duration:.0f}s ({total_duration/60:.1f} min) |
| Avg Quality | {df['quality_score'].mean():.2f} |

## Agent Breakdown
| Role | Steps | Tokens | Sources | Avg Quality |
|------|-------|--------|---------|-------------|
"""

for role in ["planner", "researcher", "writer", "reviewer"]:
    group = df[df["agent_role"] == role]
    report += f"| {role} | {len(group)} | {group['tokens_used'].sum():,} | {group['sources_cited'].sum()} | {group['quality_score'].mean():.2f} |\n"

report += f"""
## Key Findings
- **Researcher** executed {researcher_steps} steps — the most of any agent role
- **Writer** consumed {writer_tokens:,} tokens for synthesis
- **Total sources cited**: {total_sources} across the pipeline
- **Quality** {'improved' if df.iloc[-1]['quality_score'] > df.iloc[0]['quality_score'] else 'varied'} through the pipeline

## Optimization Recommendations
1. **Cache source extractions** to reduce Researcher token usage
2. **Parallelize sub-question research** — steps are independent
3. **Add quality gates** between pipeline stages
4. **Limit sources per sub-question** to top-3 most relevant
"""

print(report)

with open("lab-079/research_analysis.md", "w") as f:
    f.write(report)
print("💾 Saved to lab-079/research_analysis.md")
```

---

## 🐛 Exercício de Correção de Bugs

O arquivo `lab-079/broken_research.py` contém **3 bugs** que produzem análises de pesquisa incorretas. Você consegue encontrar e corrigir todos?

Execute os autotestes para ver quais falham:

```bash
python lab-079/broken_research.py
```

Você deve ver **3 testes com falha**. Cada teste corresponde a um bug:

| Teste | O que verifica | Dica |
|-------|---------------|------|
| Teste 1 | Total de fontes citadas | Deve somar `sources_cited`, não contar linhas |
| Teste 2 | Contagem de tokens do Writer | Deve filtrar `agent_role == "writer"`, não `"researcher"` |
| Teste 3 | Contagem de etapas do Researcher | Deve contar linhas onde `agent_role == "researcher"`, não somar tokens |

Corrija todos os 3 bugs e execute novamente. Quando você vir `All passed!`, está pronto!

---


## 🧠 Verificação de Conhecimento

??? question "**Q1 (Múltipla Escolha):** Qual é a principal vantagem de um pipeline multi-agente em relação a uma abordagem de LLM único para pesquisa?"

    - A) Usa menos tokens no total
    - B) Cada agente se especializa em uma tarefa, permitindo melhor qualidade e rastreabilidade
    - C) Requer apenas uma implantação de modelo
    - D) Elimina a necessidade de citações

    ??? success "✅ Revelar Resposta"
        **Correto: B) Cada agente se especializa em uma tarefa, permitindo melhor qualidade e rastreabilidade**

        Ao dividir a pesquisa em planejamento, busca, escrita e revisão, cada agente pode ser otimizado para sua tarefa específica. O Researcher pode focar na qualidade das fontes, o Writer na coerência da prosa e o Reviewer na precisão factual. Essa especialização normalmente produz saídas de maior qualidade do que uma geração única de ponta a ponta.

??? question "**Q2 (Múltipla Escolha):** Por que o rastreamento de citações é importante em agentes de pesquisa profunda?"

    - A) Reduz o uso de tokens
    - B) Garante que cada afirmação seja mapeada de volta a uma fonte, permitindo verificação e confiança
    - C) Torna o relatório mais longo
    - D) É exigido pelos termos de serviço do LLM

    ??? success "✅ Revelar Resposta"
        **Correto: B) Garante que cada afirmação seja mapeada de volta a uma fonte, permitindo verificação e confiança**

        O rastreamento de citações cria uma cadeia auditável de cada afirmação no relatório final até sua fonte. Isso permite que revisores verifiquem a precisão factual, que usuários explorem fontes primárias e que organizações mantenham a integridade da pesquisa — crítico para aplicações de alto risco como pesquisa jurídica, médica ou financeira.

??? question "**Q3 (Execute o Laboratório):** Qual é o número total de fontes citadas em todas as etapas?"

    Execute a análise da Etapa 4 em [📥 `research_trace.csv`](https://github.com/lcarli/AI-LearningHub/raw/main/docs/docs/en/labs/lab-079/research_trace.csv) e some a coluna `sources_cited`.

    ??? success "✅ Revelar Resposta"
        **10 fontes**

        A soma de todos os valores de `sources_cited` nas 14 etapas é igual a **10**. A maioria das fontes é citada durante as etapas do Researcher, com algumas citações adicionais incluídas durante a síntese do Writer.

??? question "**Q4 (Execute o Laboratório):** Quantos tokens no total o agente Writer consumiu?"

    Execute a análise da Etapa 3 e encontre o total de tokens para o papel `writer`.

    ??? success "✅ Revelar Resposta"
        **Soma de `tokens_used` onde `agent_role == "writer"`**

        A contagem total de tokens do Writer inclui todas as etapas de escrita e síntese. Filtre o rastreamento por `agent_role == "writer"` e some a coluna `tokens_used` para obter o valor exato.

??? question "**Q5 (Execute o Laboratório):** Quantas etapas o agente Researcher executou?"

    Conte as linhas onde `agent_role == "researcher"`.

    ??? success "✅ Revelar Resposta"
        **6 etapas**

        O Researcher executou **6 etapas** — o maior número de qualquer papel de agente. Isso faz sentido porque o Researcher lida com múltiplas sub-perguntas do Planner, com cada sub-pergunta potencialmente exigindo múltiplas etapas de busca e extração.

---

## Resumo

| Tópico | O que Você Aprendeu |
|--------|---------------------|
| Deep Research Agents | Pipeline multi-agente para síntese de conhecimento com rastreamento de citações |
| Arquitetura do Pipeline | Planner → Researcher → Writer → Reviewer com papéis especializados |
| Rastreamento de Citações | Cada afirmação é mapeada de volta a uma fonte ao longo do pipeline |
| Distribuição de Tokens | Researcher usa mais tokens; Writer sintetiza; Reviewer valida |
| Padrões de Qualidade | A qualidade varia por etapa — etapas de pesquisa posteriores podem mostrar esgotamento de fontes |
| Otimização | Armazenar fontes em cache, paralelizar pesquisa, adicionar portões de qualidade |

---

## Próximos Passos

- **[Lab 034](lab-034-multi-agent-sk.md)** — Multi-Agent com Semantic Kernel (construa os agentes)
- **[Lab 067](lab-067-graphrag.md)** — GraphRAG (aprimore a pesquisa com recuperação por grafo de conhecimento)
- **[Lab 033](lab-033-agent-observability.md)** — Observabilidade de Agentes (monitore pipelines de pesquisa profunda em produção)
- **[Lab 076](lab-076-microsoft-agent-framework.md)** — Microsoft Agent Framework (implemente pipelines com MAF Graph Workflows)
