---
tags: [reasoning, o3, deepseek-r1, chain-of-thought, benchmark, python]
---
# Lab 060: Modelos de Raciocínio — Chain-of-Thought com o3 e DeepSeek R1

<div class="lab-meta">
  <span><strong>Nível:</strong> <span class="level-badge level-200">L200</span></span>
  <span><strong>Caminho:</strong> Todos os caminhos</span>
  <span><strong>Tempo:</strong> ~75 min</span>
  <span><strong>💰 Custo:</strong> <span class="level-badge cost-free">Gratuito</span> — Usa conjunto de dados de benchmark (Azure OpenAI opcional)</span>
</div>

## O Que Você Vai Aprender

- Como **modelos de raciocínio** (o3, DeepSeek R1) diferem de modelos padrão (GPT-4o) — pensamento estendido, chain-of-thought
- O que é um **orçamento de pensamento** e como ele controla a profundidade do raciocínio do modelo
- Comparar **precisão, velocidade e custo de tokens** entre 3 modelos em 12 problemas de benchmark
- Identificar quais **categorias de problemas e níveis de dificuldade** mais se beneficiam do raciocínio
- Aplicar um framework de decisão: **quando usar modelos de raciocínio** vs modelos padrão
- Entender **trade-offs de custo-desempenho** para implantações em produção

---

## Introdução

LLMs padrão como GPT-4o geram respostas em uma única passagem direta — rápido, mas podem tropeçar em problemas que exigem raciocínio lógico em múltiplas etapas. **Modelos de raciocínio** como o3 e DeepSeek R1 adotam uma abordagem diferente: eles usam **pensamento estendido** (chain-of-thought) para dividir problemas complexos em etapas, verificar resultados intermediários e retroceder quando detectam erros.

O trade-off é claro: modelos de raciocínio são mais lentos e usam mais tokens, mas alcançam precisão dramaticamente maior em problemas difíceis.

### O Benchmark

Você comparará **3 modelos** em **12 problemas** em 4 categorias:

| Categoria | Fácil | Médio | Difícil |
|-----------|-------|-------|---------|
| **Matemática** | Juros compostos | Sistema de equações | Provar que √2 é irracional |
| **Código** | Inverter uma string | Busca binária | Cache LRU thread-safe |
| **Lógica** | Silogismo | Puzzle das três caixas | Lobo-cabra-repolho |
| **Planejamento** | Roteiro de caminhada | Rota de entrega | Migração de microsserviços |

---

## Pré-requisitos

```bash
pip install pandas
```

Este lab analisa resultados de benchmark pré-computados — nenhuma chave de API ou assinatura do Azure é necessária. Para executar benchmarks ao vivo, você precisaria de acesso ao GPT-4o, o3 e DeepSeek R1 via Azure OpenAI ou as respectivas APIs.

---

!!! tip "Início Rápido com GitHub Codespaces"
    [![Open in GitHub Codespaces](https://github.com/codespaces/badge.svg)](https://codespaces.new/lcarli/AI-LearningHub?quickstart=1)

    Todas as dependências estão pré-instaladas no devcontainer.


## 📦 Arquivos de Apoio

!!! note "Baixe estes arquivos antes de iniciar o lab"
    Salve todos os arquivos em uma pasta `lab-060/` no seu diretório de trabalho.

| Arquivo | Descrição | Download |
|---------|-----------|----------|
| `broken_reasoning.py` | Exercício de correção de bugs (3 bugs + autotestes) | [📥 Download](https://github.com/lcarli/AI-LearningHub/raw/main/docs/docs/en/labs/lab-060/broken_reasoning.py) |
| `reasoning_benchmark.csv` | Conjunto de dados de benchmark | [📥 Download](https://github.com/lcarli/AI-LearningHub/raw/main/docs/docs/en/labs/lab-060/reasoning_benchmark.csv) |

---

## Parte 1: Entendendo Modelos de Raciocínio

### Etapa 1: Como modelos de raciocínio funcionam

Modelos padrão geram tokens da esquerda para a direita sem pausar para "pensar". Modelos de raciocínio adicionam uma fase de deliberação interna:

```
Padrão (GPT-4o):
  Entrada → [Gerar tokens] → Saída

Raciocínio (o3 / DeepSeek R1):
  Entrada → [Pensar: dividir em etapas] → [Verificar cada etapa] → [Retroceder se necessário] → Saída
```

Conceitos-chave:

| Conceito | Descrição |
|----------|-----------|
| **Chain-of-thought** | O modelo raciocina explicitamente através de etapas intermediárias antes de responder |
| **Orçamento de pensamento** | Controla quanto raciocínio o modelo realiza (mais orçamento = mais minucioso = mais lento) |
| **Pensamento estendido** | A deliberação interna do modelo — visível em algumas APIs como "tokens de pensamento" |
| **Autovalidação** | O modelo verifica seus próprios resultados intermediários e corrige erros |

!!! info "Orçamento de Pensamento"
    O orçamento de pensamento controla quanto raciocínio o modelo realiza antes de produzir uma resposta final. Um orçamento maior permite que o modelo explore mais caminhos de solução e verifique mais minuciosamente — mas custa mais tokens e leva mais tempo. Para perguntas simples, um orçamento baixo é suficiente; para provas complexas, você quer o orçamento completo.

---

## Parte 2: Carregar Dados de Benchmark

### Etapa 2: Carregar [📥 `reasoning_benchmark.csv`](https://github.com/lcarli/AI-LearningHub/raw/main/docs/docs/en/labs/lab-060/reasoning_benchmark.csv)

O conjunto de dados de benchmark contém resultados da execução de todos os 12 problemas em cada modelo:

```python
# reasoning_analysis.py
import pandas as pd

bench = pd.read_csv("lab-060/reasoning_benchmark.csv")

# Convert boolean columns
for model in ["gpt4o", "o3", "deepseek_r1"]:
    bench[f"{model}_correct"] = bench[f"{model}_correct"].astype(str).str.lower() == "true"

print(f"Problems: {len(bench)}")
print(f"Categories: {bench['category'].unique().tolist()}")
print(f"Difficulties: {bench['difficulty'].unique().tolist()}")
print(bench[["problem_id", "category", "difficulty"]].to_string(index=False))
```

**Saída esperada:**

```
Problems: 12
Categories: ['math', 'code', 'logic', 'planning']
Difficulties: ['easy', 'medium', 'hard']

problem_id category difficulty
       P01     math       easy
       P02     math     medium
       P03     math       hard
       P04     code       easy
       P05     code     medium
       P06     code       hard
       P07    logic       easy
       P08    logic     medium
       P09    logic       hard
       P10 planning       easy
       P11 planning     medium
       P12 planning       hard
```

---

## Parte 3: Comparação Geral de Precisão

### Etapa 3: Calcular a precisão de cada modelo

```python
# Overall accuracy
for model in ["gpt4o", "o3", "deepseek_r1"]:
    correct = bench[f"{model}_correct"].sum()
    total = len(bench)
    print(f"{model:>12}: {correct}/{total} = {correct/total*100:.1f}%")
```

**Saída esperada:**

```
      gpt4o: 6/12 = 50.0%
          o3: 12/12 = 100.0%
 deepseek_r1: 11/12 = 91.7%
```

!!! warning "Descoberta Principal"
    GPT-4o acerta apenas metade dos problemas, enquanto o3 alcança pontuação perfeita. DeepSeek R1 erra apenas um problema (P12 — o problema de planejamento mais difícil). A diferença é dramática nos problemas difíceis.

```python
# Which problems does GPT-4o get wrong?
gpt4o_fails = bench[bench["gpt4o_correct"] == False]
print("GPT-4o failures:")
print(gpt4o_fails[["problem_id", "category", "difficulty", "description"]].to_string(index=False))
```

**Saída esperada:**

```
GPT-4o failures:
problem_id category difficulty                                       description
       P03     math       hard                    Prove that sqrt(2) is irrational
       P06     code       hard          Design a thread-safe LRU cache in Python
       P08    logic     medium  Three boxes puzzle: one has gold - find the optimal strategy
       P09    logic       hard  River crossing puzzle with wolf-goat-cabbage constraints
       P11 planning     medium  Optimize a delivery route for 5 stops minimizing distance
       P12 planning       hard  Design a microservices migration plan for a monolith app
```

GPT-4o falha em **todos os problemas difíceis** mais dois problemas médios (P08, P11) que exigem raciocínio em múltiplas etapas.

```python
# What does DeepSeek R1 get wrong?
r1_fails = bench[bench["deepseek_r1_correct"] == False]
print("DeepSeek R1 failures:")
print(r1_fails[["problem_id", "category", "difficulty", "description"]].to_string(index=False))
```

**Saída esperada:**

```
DeepSeek R1 failures:
problem_id  category difficulty                                          description
       P12  planning       hard  Design a microservices migration plan for a monolith app
```

DeepSeek R1 falha apenas no P12 — o problema de planejamento mais complexo que requer tanto conhecimento técnico quanto planejamento de projeto em múltiplas etapas.

---

## Parte 4: Precisão por Categoria e Dificuldade

### Etapa 4: Detalhar a precisão por categoria

```python
# Accuracy by category
for category in bench["category"].unique():
    cat_data = bench[bench["category"] == category]
    print(f"\n{category.upper()}:")
    for model in ["gpt4o", "o3", "deepseek_r1"]:
        correct = cat_data[f"{model}_correct"].sum()
        total = len(cat_data)
        print(f"  {model:>12}: {correct}/{total}")
```

**Saída esperada:**

```
MATH:
        gpt4o: 2/3
            o3: 3/3
   deepseek_r1: 3/3

CODE:
        gpt4o: 2/3
            o3: 3/3
   deepseek_r1: 3/3

LOGIC:
        gpt4o: 1/3
            o3: 3/3
   deepseek_r1: 3/3

PLANNING:
        gpt4o: 1/3
            o3: 3/3
   deepseek_r1: 2/3
```

```python
# Accuracy by difficulty
for diff in ["easy", "medium", "hard"]:
    diff_data = bench[bench["difficulty"] == diff]
    print(f"\n{diff.upper()}:")
    for model in ["gpt4o", "o3", "deepseek_r1"]:
        correct = diff_data[f"{model}_correct"].sum()
        total = len(diff_data)
        print(f"  {model:>12}: {correct}/{total} = {correct/total*100:.0f}%")
```

**Saída esperada:**

```
EASY:
        gpt4o: 4/4 = 100%
            o3: 4/4 = 100%
   deepseek_r1: 4/4 = 100%

MEDIUM:
        gpt4o: 2/4 = 50%
            o3: 4/4 = 100%
   deepseek_r1: 4/4 = 100%

HARD:
        gpt4o: 0/4 = 0%
            o3: 4/4 = 100%
   deepseek_r1: 3/4 = 75%
```

!!! info "Insight de Dificuldade"
    Todos os três modelos acertam os problemas fáceis. A diferença aparece na dificuldade média (GPT-4o cai para 50%) e se torna dramática nos problemas difíceis (GPT-4o: 0%, DeepSeek R1: 75%, o3: 100%). Modelos de raciocínio provam seu valor nos problemas difíceis.

---

## Parte 5: Trade-offs de Velocidade vs Precisão

### Etapa 5: Analisar o tempo de resposta por modelo

```python
# Average time per model
for model in ["gpt4o", "o3", "deepseek_r1"]:
    avg_time = bench[f"{model}_time_sec"].mean()
    print(f"{model:>12}: {avg_time:.1f}s average")

# Time vs accuracy scatter
print("\nProblem-level detail:")
for _, row in bench.iterrows():
    print(f"  {row['problem_id']} ({row['difficulty']:>6}): "
          f"GPT-4o={row['gpt4o_time_sec']:.1f}s "
          f"o3={row['o3_time_sec']:.1f}s "
          f"R1={row['deepseek_r1_time_sec']:.1f}s")
```

**Saída esperada:**

```
      gpt4o: 2.1s average
          o3: 7.1s average
 deepseek_r1: 5.4s average

Problem-level detail:
  P01 (  easy): GPT-4o=1.2s o3=3.5s R1=2.8s
  P02 (medium): GPT-4o=1.8s o3=4.2s R1=3.5s
  P03 (  hard): GPT-4o=2.5s o3=8.1s R1=6.5s
  ...
  P12 (  hard): GPT-4o=4.0s o3=15.0s R1=11.0s
```

!!! warning "Trade-off de Velocidade"
    o3 é **3,4× mais lento** que GPT-4o em média (7,1s vs 2,1s). No problema mais difícil (P12), o3 leva 15 segundos — aceitável para tarefas complexas, mas lento demais para chat em tempo real. Escolha seu modelo com base na complexidade do problema, não em implantação generalizada.

---

## Parte 6: Análise de Custo de Tokens

### Etapa 6: Comparar uso de tokens

```python
# Average tokens per model
for model in ["gpt4o", "o3", "deepseek_r1"]:
    avg_tokens = bench[f"{model}_tokens"].mean()
    total_tokens = bench[f"{model}_tokens"].sum()
    print(f"{model:>12}: {avg_tokens:.0f} avg tokens, {total_tokens:,} total")

# Cost ratio (relative to GPT-4o)
gpt4o_total = bench["gpt4o_tokens"].sum()
for model in ["o3", "deepseek_r1"]:
    model_total = bench[f"{model}_tokens"].sum()
    ratio = model_total / gpt4o_total
    print(f"\n{model} uses {ratio:.1f}× more tokens than GPT-4o")
```

**Saída esperada:**

```
      gpt4o: 287 avg tokens, 3,440 total
          o3: 878 avg tokens, 10,530 total
 deepseek_r1: 725 avg tokens, 8,700 total

o3 uses 3.1× more tokens than GPT-4o
deepseek_r1 uses 2.5× more tokens than GPT-4o
```

Os tokens extras vêm do raciocínio chain-of-thought — o modelo está "pensando em voz alta" internamente. Este é o custo de uma precisão mais alta.

---

## Parte 7: Quando Usar Cada Modelo

### Etapa 7: Framework de decisão

Com base nos resultados do benchmark, aqui está quando usar cada modelo:

| Cenário | Modelo Recomendado | Por quê |
|---------|-------------------|---------|
| Perguntas e respostas simples, FAQ | **GPT-4o** | 100% de precisão em problemas fáceis, 3× mais rápido, 3× mais barato |
| Raciocínio em múltiplas etapas | **o3** ou **DeepSeek R1** | GPT-4o cai para 0% em problemas difíceis |
| Produção com custo sensível | **DeepSeek R1** | 91,7% de precisão com 2,5× tokens (vs 3,1× do o3) |
| Precisão máxima necessária | **o3** | 100% de precisão, mas 3,4× mais lento e 3,1× mais caro |
| Conversa em tempo real | **GPT-4o** | 2,1s em média — modelos de raciocínio são lentos demais para chat |
| Geração de código (complexo) | **o3** | Código thread-safe e concorrente precisa de raciocínio cuidadoso |
| Provas matemáticas | **o3** ou **DeepSeek R1** | Ambos lidam com provas formais; GPT-4o não consegue |

```python
# Summary dashboard
print("""
╔══════════════════════════════════════════════════════╗
║      Reasoning Model Benchmark — Summary             ║
╠══════════════════════════════════════════════════════╣
║  Model        Accuracy   Avg Time   Avg Tokens       ║
║  ─────────    ────────   ────────   ──────────       ║
║  GPT-4o        50.0%      2.1s        287            ║
║  o3           100.0%      7.1s        878            ║
║  DeepSeek R1   91.7%      5.4s        725            ║
╠══════════════════════════════════════════════════════╣
║  Key Insight: Use GPT-4o for simple tasks,           ║
║  reasoning models for complex multi-step problems.   ║
╚══════════════════════════════════════════════════════╝
""")
```

---

## 🐛 Exercício de Correção de Bugs

O arquivo `lab-060/broken_reasoning.py` tem **3 bugs** nas funções de análise de benchmark. Execute os autotestes:

```bash
python lab-060/broken_reasoning.py
```

Você deverá ver **3 testes falhando**:

| Teste | O que verifica | Dica |
|-------|---------------|------|
| Teste 1 | Cálculo de precisão do modelo | Qual coluna representa a correção — `_correct` ou `_time_sec`? |
| Teste 2 | Encontrar o modelo mais rápido | Você deve usar `min` ou `max` para encontrar o mais rápido? |
| Teste 3 | Precisão em problemas difíceis | Para qual nível de dificuldade você está filtrando? |

Corrija todos os 3 bugs e execute novamente até ver `🎉 All 3 tests passed`.

---


## 🧠 Verificação de Conhecimento

??? question "**Q1 (Múltipla Escolha):** Quando você deve usar um modelo de raciocínio em vez de um modelo padrão como GPT-4o?"

    - A) Para todas as tarefas — modelos de raciocínio são sempre melhores
    - B) Para problemas complexos em múltiplas etapas que exigem raciocínio lógico, provas ou planejamento
    - C) Para aplicações de chat em tempo real onde velocidade é crítica
    - D) Para tarefas simples de FAQ e classificação

    ??? success "✅ Revelar Resposta"
        **Correto: B) Para problemas complexos em múltiplas etapas que exigem raciocínio lógico, provas ou planejamento**

        Modelos de raciocínio se destacam quando problemas exigem divisão em etapas, verificação de resultados intermediários ou exploração de múltiplos caminhos de solução. GPT-4o alcança 100% em problemas fáceis — modelos de raciocínio não agregam valor ali, mas custam 3× mais. Reserve modelos de raciocínio para problemas difíceis onde a abordagem de passagem única do GPT-4o falha.

??? question "**Q2 (Múltipla Escolha):** O que o 'orçamento de pensamento' controla em um modelo de raciocínio?"

    - A) O número máximo de chamadas de API por minuto
    - B) O custo total em dólares para uma única requisição
    - C) Quanto raciocínio o modelo realiza antes de produzir uma resposta final
    - D) O comprimento máximo da resposta de saída

    ??? success "✅ Revelar Resposta"
        **Correto: C) Quanto raciocínio o modelo realiza antes de produzir uma resposta final**

        O orçamento de pensamento controla a profundidade da deliberação interna do modelo. Um orçamento maior permite que o modelo explore mais caminhos de solução, verifique etapas intermediárias mais minuciosamente e retroceda quando detecta erros. Isso produz resultados mais precisos, mas consome mais tokens e leva mais tempo.

??? question "**Q3 (Execute o Lab):** Qual é a precisão do o3 no benchmark de 12 problemas?"

    Calcule `bench["o3_correct"].sum() / len(bench) * 100`.

    ??? success "✅ Revelar Resposta"
        **100% (12/12)**

        o3 resolve corretamente todos os 12 problemas em todas as categorias e níveis de dificuldade — incluindo P12 (plano de migração de microsserviços), que é o único problema que DeepSeek R1 erra. Esta pontuação perfeita tem um custo: o3 gasta em média 7,1 segundos e 878 tokens por problema.

??? question "**Q4 (Execute o Lab):** Qual é a precisão do GPT-4o no benchmark?"

    Calcule `bench["gpt4o_correct"].sum() / len(bench) * 100`.

    ??? success "✅ Revelar Resposta"
        **50% (6/12)**

        GPT-4o resolve corretamente 6 dos 12 problemas. Ele acerta todos os 4 problemas fáceis, mas falha em todos os 4 problemas difíceis (P03, P06, P09, P12) e 2 problemas médios (P08, P11). As falhas abrangem todas as categorias — matemática, código, lógica e planejamento — confirmando que o problema é a profundidade do raciocínio, não o conhecimento do domínio.

??? question "**Q5 (Execute o Lab):** Qual modelo falha apenas no problema P12?"

    Verifique qual modelo tem `_correct == False` para exatamente um problema, e esse problema é P12.

    ??? success "✅ Revelar Resposta"
        **DeepSeek R1**

        DeepSeek R1 alcança 91,7% de precisão (11/12), falhando apenas no P12 — "Projetar um plano de migração de microsserviços para um app monolítico". Este é o problema de planejamento mais difícil, exigindo tanto conhecimento técnico profundo quanto planejamento complexo de projeto em múltiplas etapas. o3 o resolve; GPT-4o falha nele e em mais 5 outros problemas.

---

## Resumo

| Tópico | O Que Você Aprendeu |
|--------|---------------------|
| Modelos de Raciocínio | Pensamento estendido via chain-of-thought para problemas complexos |
| Orçamento de Pensamento | Controla a profundidade do raciocínio — mais orçamento = mais preciso, mas mais lento |
| Precisão | GPT-4o: 50%, DeepSeek R1: 91,7%, o3: 100% no benchmark de 12 problemas |
| Trade-off de Velocidade | GPT-4o: 2,1s em média, DeepSeek R1: 5,4s, o3: 7,1s — raciocínio custa tempo |
| Custo de Tokens | Modelos de raciocínio usam 2,5–3,1× mais tokens que GPT-4o |
| Framework de Decisão | Use GPT-4o para tarefas simples; modelos de raciocínio para problemas difíceis em múltiplas etapas |

---

## Próximos Passos

- **[Lab 059](lab-059-voice-agents-realtime.md)** — Agentes de Voz com GPT Realtime API (interação em tempo real, modalidade diferente)
- **[Lab 043](lab-043-multimodal-agents.md)** — Agentes Multimodais com GPT-4o Vision (outra capacidade do GPT-4o)
- **[Lab 038](lab-038-cost-optimization.md)** — Otimização de Custos (aplicando os trade-offs de custo-desempenho deste lab)
