---
tags: [swe-bench, benchmarking, evaluation, coding-agents, python]
---
# Lab 073: Benchmarking de Agentes com SWE-bench

<div class="lab-meta">
  <span><strong>Nível:</strong> <span class="level-badge level-300">L300</span></span>
  <span><strong>Trilha:</strong> Todas as trilhas</span>
  <span><strong>Tempo:</strong> ~90 min</span>
  <span><strong>💰 Custo:</strong> <span class="level-badge cost-free">Gratuito</span> — Usa resultados simulados de benchmark</span>
</div>

## O que Você Vai Aprender

- O que é o **SWE-bench** e por que ele é o padrão ouro para avaliar agentes de codificação
- Como diferentes estratégias de agentes (prompt direto, cadeia de pensamento, loop agêntico) afetam as taxas de resolução
- Analisar resultados de benchmark entre modelos e estratégias para encontrar a melhor configuração de agente
- Medir o **trade-off custo-desempenho** — taxas de resolução mais altas custam mais por issue
- Construir um **relatório comparativo de benchmark** para selecionar a arquitetura de agente ideal

## Introdução

O **SWE-bench** é um benchmark para avaliar agentes de codificação com IA em issues reais do GitHub. Cada tarefa é um bug genuíno ou solicitação de funcionalidade de repositórios populares de código aberto em Python (Django, scikit-learn, sympy, etc.). O agente deve:

1. Ler a descrição da issue
2. Navegar pela base de código
3. Escrever um patch que corrija a issue
4. Passar na suíte de testes do repositório

| Variante do Benchmark | Issues | Dificuldade | Caso de Uso |
|------------------------|--------|-------------|-------------|
| **SWE-bench Full** | 2.294 | Mista | Avaliação abrangente |
| **SWE-bench Lite** | 300 | Subconjunto curado | Comparação rápida (usado neste lab) |
| **SWE-bench Verified** | 500 | Verificado por humanos | Avaliação padrão ouro |

### O Cenário

Você é um **Arquiteto de Plataforma de IA** avaliando agentes de codificação para sua equipe de engenharia. Você realizou benchmark de **8 configurações de agentes** em 3 modelos (GPT-4o, o3, Claude 3.5 Sonnet) e 4 estratégias (prompt direto, cadeia de pensamento, loop agêntico, mini SWE-agent). Seu dataset (`swe_bench_results.csv`) contém os resultados. Sua tarefa: identificar a melhor configuração de agente e entender os trade-offs de custo-desempenho.

!!! info "Dados Simulados"
    Este lab usa resultados simulados de benchmark que refletem as tendências publicadas no leaderboard do SWE-bench. Benchmarking real requer poder computacional significativo — este dataset simulado permite que você aprenda a metodologia de análise sem o custo.

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

!!! note "Baixe estes arquivos antes de iniciar o lab"
    Salve todos os arquivos em uma pasta `lab-073/` no seu diretório de trabalho.

| Arquivo | Descrição | Download |
|---------|-----------|----------|
| `broken_benchmark.py` | Exercício de correção de bugs (3 bugs + auto-testes) | [📥 Download](https://github.com/lcarli/AI-LearningHub/raw/main/docs/docs/en/labs/lab-073/broken_benchmark.py) |
| `swe_bench_results.csv` | Dataset | [📥 Download](https://github.com/lcarli/AI-LearningHub/raw/main/docs/docs/en/labs/lab-073/swe_bench_results.csv) |

---

## Etapa 1: Entender as Estratégias de Agentes

Antes de analisar os resultados, entenda as quatro estratégias sendo avaliadas:

| Estratégia | Como Funciona | Desempenho Esperado | Custo Esperado |
|------------|--------------|---------------------|----------------|
| **Direct Prompt** | Um único prompt com issue + contexto da base de código → patch | Mais baixo | Mais baixo |
| **Chain of Thought** | Prompt com etapas de raciocínio explícitas → patch | Médio | Médio |
| **Agentic Loop** | Loop multi-turno: ler código → raciocinar → editar → testar → iterar | Mais alto | Mais alto |
| **Mini SWE-agent** | Agente leve com ferramentas de navegação de arquivos e edição | Médio-Alto | Médio |

### Métricas Principais

| Métrica | Definição |
|---------|-----------|
| **Resolve Rate** | % de issues em que o patch do agente passa em todos os testes |
| **Avg Time** | Média de segundos por tentativa de issue |
| **Avg Cost** | Média de USD por tentativa de issue |

---

## Etapa 2: Carregar e Explorar os Resultados

O dataset possui **8 configurações de agentes** testadas no SWE-bench Lite (300 issues) e Verified (500 issues):

```python
import pandas as pd

df = pd.read_csv("lab-073/swe_bench_results.csv")

print(f"Total configurations: {len(df)}")
print(f"Models: {df['model'].unique().tolist()}")
print(f"Strategies: {df['strategy'].unique().tolist()}")
print(f"\nAll results:")
print(df.to_string(index=False))
```

**Saída esperada:**

```
Total configurations: 8
Models: ['gpt-4o', 'o3', 'claude-3.5-sonnet']
Strategies: ['direct_prompt', 'chain_of_thought', 'agentic_loop', 'mini_swe_agent']
```

---

## Etapa 3: Encontrar os Melhores e Piores Agentes

Classifique os agentes por taxa de resolução para encontrar os de melhor desempenho:

```python
ranked = df.sort_values("resolve_rate_pct", ascending=False)
print("Agent Ranking by Resolve Rate:")
print(ranked[["agent_name", "model", "strategy", "resolve_rate_pct", "avg_cost_usd"]].to_string(index=False))
```

**Saída esperada:**

| Posição | Agente | Modelo | Estratégia | Taxa de Resolução | Custo/Issue |
|---------|--------|--------|------------|-------------------|-------------|
| 1 | Agentic o3 | o3 | agentic_loop | 65,0% | $5,50 |
| 2 | Agentic Claude | claude-3.5-sonnet | agentic_loop | 56,0% | $3,20 |
| 3 | Agentic GPT-4o | gpt-4o | agentic_loop | 50,0% | $2,50 |
| 4 | Baseline o3 | o3 | direct_prompt | 45,0% | $3,00 |
| 5 | CoT GPT-4o | gpt-4o | chain_of_thought | 40,0% | $1,20 |
| 6 | Mini SWE-agent | gpt-4o | mini_swe_agent | 35,0% | $1,80 |
| 7 | Baseline Claude | claude-3.5-sonnet | direct_prompt | 35,0% | $0,95 |
| 8 | Baseline GPT-4o | gpt-4o | direct_prompt | 30,0% | $0,85 |

```python
best = ranked.iloc[0]
worst = ranked.iloc[-1]
print(f"\nBest agent:  {best['agent_name']} ({best['resolve_rate_pct']}%)")
print(f"Worst agent: {worst['agent_name']} ({worst['resolve_rate_pct']}%)")
```

!!! tip "Insight"
    **Agentic o3 lidera com 65%** — mas a $5,50 por issue. **Baseline GPT-4o é o mais barato** a $0,85, mas resolve apenas 30%. A estratégia de loop agêntico supera consistentemente outras estratégias para o mesmo modelo.

---

## Etapa 4: Medir a Melhoria do Loop Agêntico

Quanto a estratégia de loop agêntico melhora em relação ao baseline (prompt direto) para o mesmo modelo?

```python
lite = df[df["benchmark"] == "swe-bench-lite"]

for model in lite["model"].unique():
    model_data = lite[lite["model"] == model]
    baseline = model_data[model_data["strategy"] == "direct_prompt"]
    agentic = model_data[model_data["strategy"] == "agentic_loop"]

    if not baseline.empty and not agentic.empty:
        b_rate = baseline["resolve_rate_pct"].values[0]
        a_rate = agentic["resolve_rate_pct"].values[0]
        improvement = a_rate - b_rate
        print(f"{model:>20s}: baseline={b_rate:.0f}%  agentic={a_rate:.0f}%  improvement=+{improvement:.0f}pp")
```

**Saída esperada:**

```
              gpt-4o: baseline=30%  agentic=50%  improvement=+20pp
                  o3: baseline=45%  agentic=65%  improvement=+20pp
    claude-3.5-sonnet: baseline=35%  agentic=56%  improvement=+21pp
```

!!! tip "Insight"
    O loop agêntico adiciona **+20–21 pontos percentuais** em todos os modelos. Essa melhoria consistente sugere que a estratégia (navegação iterativa no código + testes) importa tanto quanto o modelo subjacente.

---

## Etapa 5: Analisar Trade-offs de Custo-Desempenho

Agentes mais capazes custam mais. Calcule o custo por issue resolvida para encontrar a opção mais eficiente:

```python
df["cost_per_resolved"] = df["avg_cost_usd"] * df["total_issues"] / df["resolved"]
df["cost_per_resolved"] = df["cost_per_resolved"].round(2)

efficiency = df.sort_values("cost_per_resolved")
print("Cost Efficiency Ranking:")
print(efficiency[["agent_name", "resolve_rate_pct", "avg_cost_usd", "cost_per_resolved"]].to_string(index=False))
```

```python
# Custo para resolver 100 issues com cada agente
for _, row in df.iterrows():
    issues_needed = 100 / (row["resolve_rate_pct"] / 100)
    total_cost = issues_needed * row["avg_cost_usd"]
    print(f"  {row['agent_name']:>20s}: {total_cost:>8.0f} USD to resolve 100 issues")
```

!!! warning "A Curva de Custo"
    Ir de 30% para 65% de taxa de resolução (melhoria de 2,2x) custa $5,50 vs. $0,85 por tentativa (6,5x mais caro). Os retornos decrescentes aparecem com força — avalie se a melhoria marginal na taxa de resolução justifica o custo para o seu caso de uso.

---

## Etapa 6: Construir o Relatório de Benchmark

```python
best_agent = df.loc[df["resolve_rate_pct"].idxmax()]
cheapest_agent = df.loc[df["avg_cost_usd"].idxmin()]
best_efficiency = df.loc[df["cost_per_resolved"].idxmin()]

report = f"""# 📊 SWE-bench Agent Benchmark Report

## Summary
| Metric | Value |
|--------|-------|
| Configurations Tested | {len(df)} |
| Models | {', '.join(df['model'].unique())} |
| Strategies | {', '.join(df['strategy'].unique())} |

## Top Results
| Category | Agent | Score |
|----------|-------|-------|
| Highest Resolve Rate | {best_agent['agent_name']} | {best_agent['resolve_rate_pct']:.0f}% |
| Lowest Cost/Attempt | {cheapest_agent['agent_name']} | ${cheapest_agent['avg_cost_usd']:.2f} |
| Best Cost/Resolved | {best_efficiency['agent_name']} | ${best_efficiency['cost_per_resolved']:.2f} |

## Key Finding
The **agentic loop** strategy consistently adds +20pp resolve rate over
baseline for the same model. The best agent ({best_agent['agent_name']})
achieves {best_agent['resolve_rate_pct']:.0f}% at ${best_agent['avg_cost_usd']:.2f}/attempt.

## Recommendation
- **High-value fixes:** Use {best_agent['agent_name']} (highest success rate)
- **High-volume triage:** Use {cheapest_agent['agent_name']} (lowest cost, acceptable rate)
- **Balanced workloads:** Use {best_efficiency['agent_name']} (best cost per resolved issue)
"""

print(report)

with open("lab-073/benchmark_report.md", "w") as f:
    f.write(report)
print("💾 Saved to lab-073/benchmark_report.md")
```

---

## 🐛 Exercício de Correção de Bugs

O arquivo `lab-073/broken_benchmark.py` contém **3 bugs** que produzem análises de benchmark incorretas. Você consegue encontrar e corrigir todos?

Execute os auto-testes para ver quais falham:

```bash
python lab-073/broken_benchmark.py
```

Você deverá ver **3 testes falhando**. Cada teste corresponde a um bug:

| Teste | O que verifica | Dica |
|-------|---------------|------|
| Teste 1 | Seleção do melhor agente | Deve encontrar o agente com a *maior* taxa de resolução, não a menor |
| Teste 2 | Custo médio por issue resolvida | Deve dividir pela contagem de *resolvidas*, não pelo total de issues |
| Teste 3 | Comparação agêntico vs. baseline | Deve filtrar por *modelo* antes de comparar estratégias |

Corrija todos os 3 bugs e execute novamente. Quando você vir `All passed!`, está pronto!

---


## 🧠 Verificação de Conhecimento

??? question "**Q1 (Múltipla Escolha):** O que o SWE-bench mede sobre um agente de codificação?"

    - A) Quão rápido ele consegue gerar código
    - B) Se ele consegue resolver issues reais do GitHub produzindo patches que passam nos testes
    - C) Quantas linhas de código ele consegue escrever por minuto
    - D) Se ele consegue explicar código para um humano

    ??? success "✅ Revelar Resposta"
        **Correto: B) Se ele consegue resolver issues reais do GitHub produzindo patches que passam nos testes**

        O SWE-bench avalia agentes em sua capacidade de corrigir bugs genuínos e implementar funcionalidades de repositórios reais de código aberto. O agente deve produzir um patch, e o patch deve passar na suíte de testes existente do projeto para contar como "resolvido".

??? question "**Q2 (Múltipla Escolha):** Por que a estratégia de loop agêntico supera o prompt direto?"

    - A) Ela usa uma janela de contexto maior
    - B) Ela itera: lendo código, raciocinando, editando e testando em um loop
    - C) Ela usa um modelo mais caro
    - D) Ela tem acesso à internet

    ??? success "✅ Revelar Resposta"
        **Correto: B) Ela itera: lendo código, raciocinando, editando e testando em um loop**

        O loop agêntico dá ao agente múltiplos turnos para explorar a base de código, formar hipóteses, escrever patches, executar testes e revisar. Isso espelha como desenvolvedores humanos trabalham — raramente uma tentativa única resolve um bug complexo.

??? question "**Q3 (Execute o Lab):** Qual configuração de agente tem a maior taxa de resolução?"

    Execute a análise da Etapa 3 no [📥 `swe_bench_results.csv`](https://github.com/lcarli/AI-LearningHub/raw/main/docs/docs/en/labs/lab-073/swe_bench_results.csv) e verifique o ranking.

    ??? success "✅ Revelar Resposta"
        **Agentic o3 — 65%**

        O agente AG05 ("Agentic o3") usando o modelo `o3` com a estratégia `agentic_loop` resolve 195 de 300 issues (65,0%), a maior de todas as 8 configurações.

??? question "**Q4 (Execute o Lab):** Qual configuração de agente tem a menor taxa de resolução?"

    Verifique a parte inferior do ranking da Etapa 3.

    ??? success "✅ Revelar Resposta"
        **Baseline GPT-4o — 30%**

        O agente AG01 ("Baseline GPT-4o") usando o modelo `gpt-4o` com a estratégia `direct_prompt` resolve apenas 90 de 300 issues (30,0%). O prompt direto sem iteração produz o menor desempenho.

??? question "**Q5 (Execute o Lab):** Quantos pontos percentuais o loop agêntico melhora em relação ao baseline para o mesmo modelo?"

    Execute a análise da Etapa 4 para calcular a melhoria agêntica por modelo.

    ??? success "✅ Revelar Resposta"
        **+20pp para GPT-4o (30%→50%), +20pp para o3 (45%→65%), +21pp para Claude (35%→56%)**

        O loop agêntico adiciona consistentemente 20–21 pontos percentuais de taxa de resolução sobre o baseline de prompt direto, independentemente do modelo subjacente. Isso demonstra que a arquitetura do agente importa tanto quanto a capacidade do modelo.

---

## Resumo

| Tópico | O que Você Aprendeu |
|--------|---------------------|
| SWE-bench | Benchmark padrão ouro usando issues reais do GitHub e suítes de testes |
| Taxa de Resolução | Métrica principal — % de issues em que o patch do agente passa nos testes |
| Loop Agêntico | +20pp de melhoria sobre prompt direto para qualquer modelo |
| Trade-off de Custo | 65% de taxa de resolução custa 6,5x mais por tentativa do que 30% |
| Modelo vs. Estratégia | A estratégia (loop agêntico) contribui tanto quanto a escolha do modelo |
| Análise de Benchmark | Como classificar, comparar e relatar sobre configurações de agentes |

---

## Próximos Passos

- **[Lab 035](lab-035-agent-evaluation.md)** — Avaliação de Agentes com Azure AI Eval SDK (avaliação personalizada além do SWE-bench)
- **[Lab 038](lab-038-cost-optimization.md)** — Otimização de Custos de IA (gerenciando o custo de loops agênticos)
- **[Lab 040](lab-040-autogen-multi-agent.md)** — AutoGen Multi-Agente (construindo loops agênticos com AutoGen)
- **[Lab 074](lab-074-foundry-agent-service.md)** — Foundry Agent Service (implantando agentes em produção)
