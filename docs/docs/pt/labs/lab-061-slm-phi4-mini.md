---
tags: [slm, phi-4, onnx, privacy, local-inference, python]
---
# Lab 061: SLMs — Phi-4 Mini para Habilidades de Agentes de Baixo Custo

<div class="lab-meta">
  <span><strong>Nível:</strong> <span class="level-badge level-200">L200</span></span>
  <span><strong>Caminho:</strong> Todos os caminhos</span>
  <span><strong>Tempo:</strong> ~60 min</span>
  <span><strong>💰 Custo:</strong> <span class="level-badge cost-free">Gratuito</span> — Usa dados de benchmark simulados (nenhuma chave de API necessária)</span>
</div>

## O Que Você Vai Aprender

- Como **Small Language Models (SLMs)** como Phi-4 Mini se comparam a modelos de fronteira como GPT-4o
- Quando SLMs oferecem um melhor trade-off: **baixa latência, privacidade e custo zero na nuvem**
- Executar inferência com **ONNX Runtime** localmente para habilidades de agentes (classificar, extrair, resumir, rotear, redigir)
- Analisar um **benchmark de 15 tarefas** comparando Phi-4 Mini vs GPT-4o em precisão, latência e custo
- Identificar quais tipos de tarefas SLMs lidam bem — e onde ficam aquém
- Aplicar uma estratégia de **inferência com privacidade em primeiro lugar** para cargas de trabalho sensíveis

---

## Introdução

Modelos de fronteira como GPT-4o entregam qualidade excepcional, mas trazem trade-offs de latência, custo e privacidade. **Small Language Models (SLMs)** como Phi-4 Mini executam localmente via ONNX Runtime, oferecendo latência dramaticamente menor, custo zero na nuvem e privacidade total dos dados — seus dados nunca saem do dispositivo.

A questão não é "qual modelo é melhor" — é "quais tarefas um SLM pode lidar igualmente bem?" Este lab usa um benchmark de 15 tarefas para encontrar a resposta.

### O Benchmark

Você comparará **Phi-4 Mini (local)** vs **GPT-4o (nuvem)** em **15 tarefas** em 5 categorias:

| Categoria | Quantidade | Exemplo |
|-----------|-----------|---------|
| **Classificar** | 3 | Análise de sentimento, detecção de intenção, etiquetagem de tópicos |
| **Extrair** | 3 | Extração de entidades, parsing de chave-valor, normalização de datas |
| **Resumir** | 3 | Notas de reunião, resumo de artigo, resumo de ticket de suporte |
| **Rotear** | 3 | Roteamento de tickets, decisão de escalonamento, atribuição de fila |
| **Redigir** | 3 | Resposta de e-mail, parágrafo de relatório, descrição de produto |

---

## Pré-requisitos

```bash
pip install pandas
```

Este lab analisa resultados de benchmark pré-computados — nenhuma chave de API, GPU ou instalação do ONNX Runtime é necessária. Para executar inferência ao vivo, você precisaria do ONNX Runtime e do modelo Phi-4 Mini ONNX.

---

!!! tip "Início Rápido com GitHub Codespaces"
    [![Open in GitHub Codespaces](https://github.com/codespaces/badge.svg)](https://codespaces.new/lcarli/AI-LearningHub?quickstart=1)

    Todas as dependências estão pré-instaladas no devcontainer.


## 📦 Arquivos de Apoio

!!! note "Baixe estes arquivos antes de iniciar o lab"
    Salve todos os arquivos em uma pasta `lab-061/` no seu diretório de trabalho.

| Arquivo | Descrição | Download |
|---------|-----------|----------|
| `broken_slm.py` | Exercício de correção de bugs (3 bugs + autotestes) | [📥 Download](https://github.com/lcarli/AI-LearningHub/raw/main/docs/docs/en/labs/lab-061/broken_slm.py) |
| `slm_benchmark.csv` | Conjunto de dados de benchmark | [📥 Download](https://github.com/lcarli/AI-LearningHub/raw/main/docs/docs/en/labs/lab-061/slm_benchmark.csv) |

---

## Parte 1: Entendendo SLMs

### Etapa 1: SLMs vs modelos de fronteira

SLMs são modelos compactos (tipicamente 1–4B parâmetros) otimizados para padrões de tarefas específicos. Eles trocam abrangência por eficiência:

```
Modelo de Fronteira (GPT-4o):
  API na Nuvem → [Modelo grande] → Alta precisão, alta latência, custo por token

Small Language Model (Phi-4 Mini):
  ONNX Local → [Modelo compacto] → Boa precisão, latência muito baixa, custo zero
```

Conceitos-chave:

| Conceito | Descrição |
|----------|-----------|
| **SLM** | Small Language Model — modelo compacto otimizado para tarefas específicas |
| **ONNX Runtime** | Motor de inferência multiplataforma para executar modelos localmente |
| **Inferência com privacidade em primeiro lugar** | Dados nunca saem do dispositivo — crítico para PII, saúde, finanças |
| **Roteamento de tarefas** | Direcionar tarefas simples para SLMs e tarefas complexas para modelos de fronteira |

!!! info "Quando considerar SLMs"
    SLMs se destacam em tarefas bem definidas e restritas como classificação, extração e roteamento. Eles têm dificuldade com tarefas criativas abertas que exigem amplo conhecimento de mundo. A arquitetura ideal roteia cada tarefa para o modelo do tamanho certo.

---

## Parte 2: Carregar Dados de Benchmark

### Etapa 2: Carregar [📥 `slm_benchmark.csv`](https://github.com/lcarli/AI-LearningHub/raw/main/docs/docs/en/labs/lab-061/slm_benchmark.csv)

O conjunto de dados de benchmark contém resultados da execução de todas as 15 tarefas em ambos os modelos:

```python
# slm_analysis.py
import pandas as pd

bench = pd.read_csv("lab-061/slm_benchmark.csv")

print(f"Tasks: {len(bench)}")
print(f"Categories: {bench['category'].unique().tolist()}")
print(bench[["task_id", "category", "description"]].to_string(index=False))
```

**Saída esperada:**

```
Tasks: 15
Categories: ['classify', 'extract', 'summarize', 'route', 'draft']

task_id  category                          description
    T01  classify                   Sentiment analysis
    T02  classify                     Intent detection
    T03  classify                        Topic tagging
    T04   extract                  Entity extraction
    T05   extract                  Key-value parsing
    T06   extract                Date normalization
    T07 summarize                     Meeting notes
    T08 summarize                    Article digest
    T09 summarize            Support ticket summary
    T10     draft                       Email reply
    T11     draft                  Report paragraph
    T12     draft              Product description
    T13     route                   Ticket routing
    T14 summarize       Compliance document summary
    T15     route              Escalation decision
```

---

## Parte 3: Comparação de Precisão

### Etapa 3: Calcular a precisão de cada modelo

```python
# Overall accuracy
for model in ["phi4_mini", "gpt4o"]:
    correct = bench[f"{model}_correct"].sum()
    total = len(bench)
    print(f"{model:>10}: {correct}/{total} = {correct/total*100:.0f}%")
```

**Saída esperada:**

```
 phi4_mini: 12/15 = 80%
     gpt4o: 15/15 = 100%
```

!!! warning "Descoberta Principal"
    Phi-4 Mini alcança 80% de precisão — sólido para a maioria das tarefas de agentes. GPT-4o acerta tudo, mas com latência e custo muito maiores. As 3 tarefas que Phi-4 Mini erra revelam onde os SLMs atingem seus limites.

```python
# Which tasks does Phi-4 Mini get wrong?
phi4_fails = bench[bench["phi4_mini_correct"] == False]
print("Phi-4 Mini failures:")
print(phi4_fails[["task_id", "category", "description"]].to_string(index=False))
```

**Saída esperada:**

```
Phi-4 Mini failures:
task_id  category                    description
    T10     draft                     Email reply
    T11     draft                Report paragraph
    T14 summarize  Compliance document summary
```

Phi-4 Mini falha em **2 tarefas de redação** (T10, T11) e **1 tarefa de resumo** (T14). Tarefas de redação exigem escrita criativa e nuançada — exatamente onde SLMs têm dificuldade. T14 é um documento complexo de conformidade que excede a capacidade de contexto do modelo.

---

## Parte 4: Comparação de Latência

### Etapa 4: Comparar latência de inferência

```python
# Average latency per model
for model in ["phi4_mini", "gpt4o"]:
    avg_ms = bench[f"{model}_latency_ms"].mean()
    print(f"{model:>10}: {avg_ms:.1f}ms average")

# Speedup
phi4_avg = bench["phi4_mini_latency_ms"].mean()
gpt4o_avg = bench["gpt4o_latency_ms"].mean()
speedup = gpt4o_avg / phi4_avg
print(f"\nPhi-4 Mini is {speedup:.0f}× faster than GPT-4o")
```

**Saída esperada:**

```
 phi4_mini: 82.3ms average
     gpt4o: 996.7ms average

Phi-4 Mini is 12× faster than GPT-4o
```

!!! info "Vantagem de Latência"
    Phi-4 Mini executa localmente via ONNX Runtime com 82,3ms em média — **12× mais rápido** que o round-trip na nuvem do GPT-4o de ~1 segundo. Para habilidades de agentes executadas repetidamente (classificação, roteamento), essa diferença de latência se acumula dramaticamente.

```python
# Per-task latency comparison
print("\nPer-task latency:")
for _, row in bench.iterrows():
    print(f"  {row['task_id']} ({row['category']:>9}): "
          f"Phi-4={row['phi4_mini_latency_ms']:.0f}ms  "
          f"GPT-4o={row['gpt4o_latency_ms']:.0f}ms")
```

---

## Parte 5: Análise de Custo

### Etapa 5: Calcular custo de nuvem evitado

```python
# Total cloud cost for GPT-4o
total_cost = bench["gpt4o_cost_usd"].sum()
print(f"Total GPT-4o cloud cost: ${total_cost:.4f}")
print(f"Phi-4 Mini local cost:   $0.0000")
print(f"Cost avoided by using SLM: ${total_cost:.4f}")

# Cost per category
print("\nCost by category:")
for cat in bench["category"].unique():
    cat_cost = bench[bench["category"] == cat]["gpt4o_cost_usd"].sum()
    print(f"  {cat:>9}: ${cat_cost:.4f}")
```

**Saída esperada:**

```
Total GPT-4o cloud cost: $0.0121
Phi-4 Mini local cost:   $0.0000
Cost avoided by using SLM: $0.0121

Cost by category:
  classify: $0.0018
   extract: $0.0021
 summarize: $0.0035
     route: $0.0015
     draft: $0.0032
```

Embora $0,0121 pareça pouco para 15 tarefas, em escala (milhares de invocações de agentes por dia), a economia se acumula rapidamente — e o benefício de privacidade é inestimável para dados sensíveis.

---

## Parte 6: Estratégia de Roteamento de Tarefas

### Etapa 6: Construir uma decisão de roteamento

Com base no benchmark, a estratégia ideal roteia tarefas por categoria:

| Categoria | Modelo Recomendado | Por quê |
|-----------|-------------------|---------|
| **Classificar** | Phi-4 Mini | 100% de precisão, 12× mais rápido, custo zero |
| **Extrair** | Phi-4 Mini | 100% de precisão, 12× mais rápido, custo zero |
| **Rotear** | Phi-4 Mini | 100% de precisão, 12× mais rápido, custo zero |
| **Resumir** | Phi-4 Mini (com fallback) | 2/3 corretos; fallback para GPT-4o para documentos complexos |
| **Redigir** | GPT-4o | SLM falha em escrita criativa — use modelo de fronteira |

```python
# Summary dashboard
print("""
╔══════════════════════════════════════════════════════╗
║     SLM Benchmark — Phi-4 Mini vs GPT-4o            ║
╠══════════════════════════════════════════════════════╣
║  Metric              Phi-4 Mini     GPT-4o          ║
║  ─────────────       ──────────     ──────          ║
║  Accuracy              80%          100%            ║
║  Avg Latency           82.3ms       996.7ms         ║
║  Speedup               12×          baseline        ║
║  Cloud Cost             $0           $0.0121        ║
║  Privacy                Full         Data leaves    ║
╠══════════════════════════════════════════════════════╣
║  Route: classify/extract/route → SLM                ║
║  Route: draft → frontier model                      ║
║  Route: summarize → SLM with fallback               ║
╚══════════════════════════════════════════════════════╝
""")
```

---

## 🐛 Exercício de Correção de Bugs

O arquivo `lab-061/broken_slm.py` tem **3 bugs** nas funções de análise do SLM. Execute os autotestes:

```bash
python lab-061/broken_slm.py
```

Você deverá ver **3 testes falhando**:

| Teste | O que verifica | Dica |
|-------|---------------|------|
| Teste 1 | Cálculo de precisão | Qual coluna representa a correção — `_correct` ou `_latency_ms`? |
| Teste 2 | Cálculo de custo | Você está somando `_tokens` ou `_cost_usd`? |
| Teste 3 | Filtragem de tarefas falhadas | Você está filtrando por `category == "draft"` ou faltou o filtro? |

Corrija todos os 3 bugs e execute novamente até ver `🎉 All 3 tests passed`.

---


## 🧠 Verificação de Conhecimento

??? question "**Q1 (Múltipla Escolha):** Quais são as principais vantagens de usar um SLM como Phi-4 Mini em vez de um modelo de fronteira como GPT-4o?"

    - A) Maior precisão em todos os tipos de tarefas
    - B) Baixa latência, privacidade de dados e custo zero na nuvem
    - C) Melhor escrita criativa e resumo
    - D) Janela de contexto maior e mais parâmetros

    ??? success "✅ Revelar Resposta"
        **Correto: B) Baixa latência, privacidade de dados e custo zero na nuvem**

        SLMs executam localmente via ONNX Runtime, entregando 12× menor latência (82,3ms vs 996,7ms), mantendo todos os dados no dispositivo para privacidade total e eliminando custos por token na nuvem. Eles não superam modelos de fronteira em precisão (80% vs 100%), mas para tarefas bem definidas como classificação, extração e roteamento, a precisão é suficiente e os benefícios operacionais são significativos.

??? question "**Q2 (Múltipla Escolha):** Quando você NÃO deve usar um SLM como Phi-4 Mini?"

    - A) Para classificação de sentimento
    - B) Para extração de entidades
    - C) Para tarefas complexas de escrita criativa
    - D) Para roteamento de tickets

    ??? success "✅ Revelar Resposta"
        **Correto: C) Para tarefas complexas de escrita criativa**

        O benchmark mostra que Phi-4 Mini falha em ambas as tarefas de redação (T10: resposta de e-mail, T11: parágrafo de relatório). Escrita criativa exige geração de linguagem nuançada, amplo conhecimento de mundo e flexibilidade estilística — áreas onde SLMs carecem da capacidade dos modelos de fronteira. Tarefas de classificar, extrair e rotear são bem adequadas para SLMs.

??? question "**Q3 (Execute o Lab):** Qual é a precisão do Phi-4 Mini no benchmark de 15 tarefas?"

    Calcule `bench["phi4_mini_correct"].sum() / len(bench) * 100`.

    ??? success "✅ Revelar Resposta"
        **80% (12/15)**

        Phi-4 Mini lida corretamente com 12 das 15 tarefas. Ele alcança 100% de precisão em tarefas de classificar (3/3), extrair (3/3) e rotear (3/3), mas falha em 2 tarefas de redação (T10, T11) e 1 tarefa complexa de resumo (T14). Esta precisão de 80% é suficiente para uma arquitetura de roteamento de tarefas onde apenas tarefas apropriadas são enviadas ao SLM.

??? question "**Q4 (Execute o Lab):** Quanto mais rápido é o Phi-4 Mini comparado ao GPT-4o?"

    Calcule `bench["gpt4o_latency_ms"].mean() / bench["phi4_mini_latency_ms"].mean()`.

    ??? success "✅ Revelar Resposta"
        **~12× mais rápido**

        Phi-4 Mini tem média de 82,3ms por tarefa via inferência local com ONNX Runtime, enquanto GPT-4o tem média de 996,7ms incluindo o round-trip na nuvem. A proporção é 996,7 / 82,3 ≈ 12×. Para pipelines de agentes que executam muitas habilidades sequencialmente, essa redução de latência se acumula — um pipeline de agente com 10 etapas cai de ~10 segundos para menos de 1 segundo.

??? question "**Q5 (Execute o Lab):** Quanto de custo total de nuvem é evitado usando Phi-4 Mini para todas as 15 tarefas?"

    Calcule `bench["gpt4o_cost_usd"].sum()`.

    ??? success "✅ Revelar Resposta"
        **$0,0121**

        O custo total de nuvem do GPT-4o em todas as 15 tarefas é $0,0121. Embora pareça pouco, escala linearmente — 10.000 invocações por dia custariam ~$8/dia ou ~$240/mês. Com Phi-4 Mini executando localmente, o custo na nuvem é exatamente $0. O valor real geralmente é a privacidade e não o custo: para cargas de trabalho de saúde, finanças e jurídicas, manter os dados no dispositivo pode ser um requisito de conformidade.

---

## Resumo

| Tópico | O Que Você Aprendeu |
|--------|---------------------|
| SLMs | Modelos compactos otimizados para tarefas específicas — rápidos, privados, gratuitos |
| Phi-4 Mini | 80% de precisão no benchmark de 15 tarefas, 12× mais rápido que GPT-4o |
| ONNX Runtime | Motor de inferência local — sem dependência de nuvem |
| Roteamento de Tarefas | Rotear classificar/extrair/rotear para SLM; redigir para modelo de fronteira |
| Privacidade | Inferência SLM mantém todos os dados no dispositivo — crítico para cargas de trabalho sensíveis |
| Custo | $0,0121 de custo de nuvem evitado por 15 tarefas; se acumula em escala |

---

## Próximos Passos

- **[Lab 062](lab-062-ondevice-phi-silica.md)** — Agentes On-Device com Phi Silica (inferência on-device acelerada por NPU)
- **[Lab 060](lab-060-reasoning-models.md)** — Modelos de Raciocínio (quando você precisa de precisão máxima em vez de velocidade)
- **[Lab 044](lab-044-phi4-ollama-production.md)** — Phi-4 com Ollama em Produção (implantação local alternativa)
