---
tags: [evaluation, python, free, github-models]
---
# Lab 035: Avaliação de Agentes com Azure AI Eval SDK

<div class="lab-meta">
  <span><strong>Nível:</strong> <span class="level-badge level-300">L300</span></span>
  <span><strong>Trilha:</strong> <a href="../paths/pro-code/">Pro Code</a></span>
  <span><strong>Tempo:</strong> ~60 min</span>
  <span><strong>💰 Custo:</strong> <span class="level-badge cost-github">GitHub Gratuito</span> — usa GitHub Models para avaliação</span>
</div>

## O que Você Vai Aprender

- Por que a avaliação **LLM-as-judge** funciona e quando usá-la
- Medir **fundamentação**, **relevância**, **coerência** e **fluência**
- Construir um **golden dataset** para testes de regressão
- Avaliar seu agente RAG automaticamente com o SDK `azure-ai-evaluation`
- Rastrear métricas de qualidade ao longo do tempo e detectar regressões

---

## Introdução

Como você sabe se seu agente melhorou ou piorou após uma mudança? Testes manuais não escalam.

A **avaliação LLM-as-judge** usa um segundo LLM independente para pontuar as respostas do seu agente com base em critérios como:

- **Fundamentação** — A resposta é suportada pelos documentos recuperados?
- **Relevância** — A resposta aborda o que o usuário perguntou?
- **Coerência** — A resposta é logicamente estruturada?
- **Fluência** — A gramática está correta?

Este lab constrói um pipeline de avaliação automatizado para o assistente OutdoorGear.

---

## Pré-requisitos

- Python 3.11+
- `pip install azure-ai-evaluation openai`
- `GITHUB_TOKEN` configurado

---

## 📦 Arquivos de Apoio

!!! note "Baixe estes arquivos antes de iniciar o lab"
    Salve todos os arquivos em uma pasta `lab-035/` no seu diretório de trabalho.

| Arquivo | Descrição | Download |
|---------|-----------|----------|
| `eval_dataset.jsonl` | Conjunto de dados de avaliação | [📥 Download](https://github.com/lcarli/AI-LearningHub/raw/main/docs/docs/en/labs/lab-035/eval_dataset.jsonl) |

---

## Exercício do Lab

### Passo 1: Instalar o SDK de avaliação

```bash
pip install azure-ai-evaluation openai
```

### Passo 2: Criar um golden dataset

Um **golden dataset** é um conjunto de perguntas de teste com respostas corretas conhecidas. Crie [📥 `eval_dataset.jsonl`](https://github.com/lcarli/AI-LearningHub/raw/main/docs/docs/en/labs/lab-035/eval_dataset.jsonl):

```jsonl
{"query": "What is the return policy?", "response": "We offer a 60-day return window. Items must be unused in original packaging.", "context": "60-day return window. Items must be unused in original packaging. Worn footwear non-refundable unless defective."}
{"query": "Do you sell waterproof jackets?", "response": "Yes, we have the StormShell Jacket at $349 — a 3-layer Gore-Tex Pro shell.", "context": "StormShell Jacket ($349): 3-layer Gore-Tex Pro shell. 20k/20k waterproof rating."}
{"query": "How long does standard shipping take?", "response": "Standard shipping takes 3-5 business days and costs $5.99.", "context": "Standard $5.99 (3-5 days). Express $14.99 (1-2 days). Free on orders $75+."}
{"query": "What is the capital of France?", "response": "Paris is the capital of France.", "context": "OutdoorGear Inc. sells outdoor equipment including tents, boots, and apparel."}
{"query": "Tell me about the TrailBlazer X200", "response": "The TrailBlazer X200 is a waterproof hiking boot with Vibram outsole, priced at $189.99.", "context": "TrailBlazer X200 ($189.99): Waterproof Gore-Tex hiking boot. Vibram outsole. 3-season rated."}
```

Observe a 4ª entrada — o agente responde uma pergunta não relacionada à base de conhecimento. A avaliação de fundamentação deve sinalizar isso.

### Passo 3: Executar avaliadores integrados

```python
# evaluate_agent.py
import os, json
from pathlib import Path
from azure.ai.evaluation import (
    GroundednessEvaluator,
    RelevanceEvaluator,
    CoherenceEvaluator,
    FluencyEvaluator,
)

# Use GitHub Models as the judge LLM
model_config = {
    "azure_endpoint": "https://models.inference.ai.azure.com",
    "api_key": os.environ["GITHUB_TOKEN"],
    "azure_deployment": "gpt-4o",
    "api_version": "2024-02-01",
}

# Initialize evaluators
groundedness = GroundednessEvaluator(model_config=model_config)
relevance    = RelevanceEvaluator(model_config=model_config)
coherence    = CoherenceEvaluator(model_config=model_config)
fluency      = FluencyEvaluator(model_config=model_config)

# Load dataset
dataset = [
    json.loads(line)
    for line in Path("eval_dataset.jsonl").read_text().splitlines()
    if line.strip()
]

results = []
for i, item in enumerate(dataset, 1):
    query    = item["query"]
    response = item["response"]
    context  = item["context"]

    print(f"Evaluating {i}/{len(dataset)}: {query[:50]}...")

    scores = {
        "query":        query,
        "response":     response[:80] + "...",
        "groundedness": groundedness(query=query, response=response, context=context)["groundedness"],
        "relevance":    relevance(query=query,    response=response, context=context)["relevance"],
        "coherence":    coherence(query=query,    response=response)["coherence"],
        "fluency":      fluency(response=response)["fluency"],
    }
    results.append(scores)

# Print report
print("\n" + "="*80)
print(f"{'Query':<45} {'Ground':>7} {'Relev':>6} {'Coher':>6} {'Fluency':>8}")
print("-"*80)
for r in results:
    print(
        f"{r['query'][:44]:<45} "
        f"{r['groundedness']:>7.1f} "
        f"{r['relevance']:>6.1f} "
        f"{r['coherence']:>6.1f} "
        f"{r['fluency']:>8.1f}"
    )

# Summary
print("="*80)
for metric in ["groundedness", "relevance", "coherence", "fluency"]:
    avg = sum(r[metric] for r in results) / len(results)
    status = "✅" if avg >= 3.5 else "⚠️" if avg >= 2.5 else "❌"
    print(f"{status} Avg {metric:15}: {avg:.2f}/5.0")
```

```bash
python evaluate_agent.py
```

Saída esperada:
```
============================================================
Query                                         Ground  Relev  Coher  Fluency
------------------------------------------------------------
What is the return policy?                       4.0    5.0    5.0      5.0
Do you sell waterproof jackets?                  5.0    5.0    4.0      5.0
How long does standard shipping take?            5.0    5.0    5.0      5.0
What is the capital of France?                   1.0    1.0    4.0      5.0  ← sinalizado!
Tell me about the TrailBlazer X200               5.0    5.0    5.0      5.0
============================================================
✅ Avg groundedness    : 4.00/5.0
✅ Avg relevance       : 4.20/5.0
✅ Avg coherence       : 4.60/5.0
✅ Avg fluency         : 5.00/5.0
```

A pergunta sobre Paris é corretamente sinalizada com baixa fundamentação (1.0) — a resposta não é suportada pelo contexto do OutdoorGear.

### Passo 4: Construir um avaliador personalizado

Às vezes você precisa de critérios específicos do domínio. Aqui está um avaliador personalizado para **precisão de preço**:

```python
# custom_evaluator.py
from azure.ai.evaluation import PromptTemplateEvaluator

PRICE_ACCURACY_TEMPLATE = """
You are evaluating whether an AI assistant correctly stated product prices.

Query: {{query}}
Response: {{response}}
Ground truth context: {{context}}

Score the price accuracy from 1-5:
- 5: All prices mentioned are exactly correct
- 4: Prices are approximately correct (within 10%)
- 3: Some prices correct, some missing
- 2: Prices are wrong or made up
- 1: No prices when prices were relevant, or completely wrong prices

Return a JSON object: {"price_accuracy": <score>, "reason": "<brief explanation>"}
"""

price_evaluator = PromptTemplateEvaluator(
    prompt_template=PRICE_ACCURACY_TEMPLATE,
    model_config=model_config,
    result_key="price_accuracy",
)

# Test it
result = price_evaluator(
    query="How much is the TrailBlazer X200?",
    response="The TrailBlazer X200 costs $189.99.",
    context="TrailBlazer X200 ($189.99): Waterproof Gore-Tex hiking boot."
)
print(f"Price accuracy score: {result['price_accuracy']}")
```

### Passo 5: Automatizar no CI/CD

Adicione isso ao seu workflow do GitHub Actions (veja [Lab 037](lab-037-cicd-github-actions.md)):

```yaml
- name: Evaluate agent quality
  run: |
    pip install azure-ai-evaluation openai
    python evaluate_agent.py | tee eval_report.txt
    # Fail if avg groundedness < 3.5
    python -c "
    import json, sys
    results = [json.loads(l) for l in open('eval_results.jsonl')]
    avg_g = sum(r['groundedness'] for r in results) / len(results)
    print(f'Avg groundedness: {avg_g:.2f}')
    sys.exit(0 if avg_g >= 3.5 else 1)
    "
  env:
    GITHUB_TOKEN: ${{ secrets.GITHUB_TOKEN }}
```

---

## Referência de Métricas de Avaliação

| Métrica | O que mede | Pontuação boa |
|---------|-----------|---------------|
| Fundamentação | Resposta suportada pelo contexto | ≥ 4.0 |
| Relevância | Responde à pergunta do usuário | ≥ 4.0 |
| Coerência | Lógica, bem estruturada | ≥ 4.0 |
| Fluência | Gramaticalmente correta | ≥ 4.5 |

Pontuações são de 1 a 5. Abaixo de 3.0 em fundamentação geralmente indica alucinação.

---


## 🧠 Verificação de Conhecimento

??? question "**Q1 (Execute o Lab):** Carregue `lab-035/eval_dataset.jsonl` em Python. Quantos exemplos existem no conjunto de dados, e quantos estão na categoria `out_of_scope`?"

    Execute o código de carregamento da seção Arquivos de Apoio acima.

    ??? success "✅ Revelar Resposta"
        **20 exemplos no total. 1 exemplo está na categoria `out_of_scope`.**

        O conjunto de dados tem exatamente 20 linhas. Execute `sum(1 for d in dataset if d["category"] == "out_of_scope")` para confirmar que há 1 exemplo fora do escopo. Esse exemplo testa se seu agente recusa corretamente responder perguntas não relacionadas a equipamentos outdoor.

??? question "**Q2 (Execute o Lab):** Para o único exemplo `out_of_scope` em `eval_dataset.jsonl`, qual é o valor do campo `product_ids`?"

    Carregue o conjunto de dados e filtre por `category == "out_of_scope"`. Imprima o campo `product_ids`.

    ??? success "✅ Revelar Resposta"
        **`[]` (lista vazia)**

        O exemplo fora do escopo tem `"product_ids": []` porque a pergunta não é sobre nenhum produto específico — está testando se o agente recusa responder perguntas irrelevantes (como pedir receitas culinárias). Um agente bem projetado deve retornar uma mensagem de recusa em vez de alucinar uma resposta. Sua métrica de avaliação deve verificar que a pontuação de `groundedness` do agente é alta e que ele NÃO referencia nenhum ID de produto.

??? question "**Q3 (Múltipla Escolha):** Quantos exemplos em `eval_dataset.jsonl` estão na categoria `tents`?"

    - A) 3
    - B) 5
    - C) 7
    - D) 4

    ??? success "✅ Revelar Resposta"
        **Correto: B — 5 exemplos**

        A categoria `tents` tem 5 exemplos, sendo a maior categoria individual. Execute `sum(1 for d in dataset if d["category"] == "tents")` para confirmar. A distribuição completa: tents(5), backpacks(4), sleeping_bags(3), pricing(3), recommendations(3), out_of_scope(1), comparisons(1).

---

## Próximos Passos

- **CI/CD para agentes:** → [Lab 037 — GitHub Actions for AI Agents](lab-037-cicd-github-actions.md)
- **Avaliação RAG empresarial:** → [Lab 042 — Enterprise RAG with Evaluations](lab-042-enterprise-rag.md)
