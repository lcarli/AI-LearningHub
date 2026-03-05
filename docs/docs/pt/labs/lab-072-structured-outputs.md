---
tags: [structured-outputs, json-schema, pydantic, reliability, python]
---
# Lab 072: Structured Outputs — JSON Garantido para Agentes

<div class="lab-meta">
  <span><strong>Nível:</strong> <span class="level-badge level-100">L100</span></span>
  <span><strong>Trilha:</strong> Todas as trilhas</span>
  <span><strong>Tempo:</strong> ~45 min</span>
  <span><strong>💰 Custo:</strong> <span class="level-badge cost-free">Gratuito</span> — Usa dados simulados de extração</span>
</div>

## O que Você Vai Aprender

- O que são **Structured Outputs** e por que agentes precisam de JSON garantido
- Como a imposição de JSON Schema difere de prompts genéricos do tipo "por favor, retorne JSON"
- Analisar resultados de testes de extração comparando saídas com e sem imposição de schema
- Medir **taxas de validade de schema** e **precisão de campos** em diferentes tipos de entrada
- Criar um **relatório de confiabilidade** provando que structured outputs eliminam falhas de parsing

## Introdução

Quando um agente extrai informações de texto não estruturado — e-mails, faturas, currículos, chamados de suporte — ele precisa retornar **dados estruturados** que sistemas downstream possam interpretar de forma confiável. Sem imposição de schema, até os melhores modelos ocasionalmente retornam JSON malformado, campos ausentes ou tipos inesperados.

**Structured Outputs** resolvem isso ao restringir a saída do modelo a um JSON Schema no momento da decodificação. O modelo literalmente *não consegue* produzir JSON inválido.

| Abordagem | Garantia de Validade | Precisão de Campos | Falhas de Parsing |
|----------|-------------------|----------------|-----------------|
| Prompt genérico ("retorne JSON") | ❌ Sem garantia | Variável | Comuns |
| Modo JSON | ✅ JSON válido | Variável | Raras |
| **Structured Outputs (JSON Schema)** | ✅ Válido + compatível com schema | Alta | **Zero** |

### O Cenário

Você é um **Engenheiro de Dados** construindo um pipeline de extração para uma seguradora. O pipeline processa 5 tipos de documentos: e-mails, faturas, currículos, chamados de suporte e avaliações de produtos. Você executou **15 testes de extração** — 10 com imposição de schema e 5 sem — e precisa provar que structured outputs estão prontos para produção.

Seu dataset (`structured_outputs.csv`) contém os resultados. Seu trabalho: analisar taxas de validade, precisão de campos e construir o caso para imposição de schema.

!!! info "Dados Simulados"
    Este lab utiliza um CSV com resultados de testes simulados. Os padrões refletem o comportamento do mundo real: saídas com imposição de schema alcançam precisão quase perfeita, enquanto saídas genéricas são inconsistentes.

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

    Todas as dependências já estão pré-instaladas no devcontainer.


## 📦 Arquivos de Apoio

!!! note "Baixe estes arquivos antes de iniciar o lab"
    Salve todos os arquivos em uma pasta `lab-072/` no seu diretório de trabalho.

| Arquivo | Descrição | Download |
|------|-------------|----------|
| `broken_structured.py` | Exercício de correção de bugs (3 bugs + autotestes) | [📥 Download](https://github.com/lcarli/AI-LearningHub/raw/main/docs/docs/en/labs/lab-072/broken_structured.py) |
| `structured_outputs.csv` | Dataset | [📥 Download](https://github.com/lcarli/AI-LearningHub/raw/main/docs/docs/en/labs/lab-072/structured_outputs.csv) |

---

## Etapa 1: Entender Structured Outputs

Structured Outputs funcionam fornecendo um **JSON Schema** junto com seu prompt. O decodificador do modelo é restringido a produzir apenas tokens que resultem em JSON válido compatível com o schema.

### Exemplo de Schema (Pydantic)

```python
from pydantic import BaseModel
from typing import List

class EmailExtraction(BaseModel):
    name: str
    email: str
    subject: str
    urgency: str  # "low", "medium", "high"

class InvoiceExtraction(BaseModel):
    vendor: str
    amount: float
    date: str
    line_items: List[str]
```

### Como Funciona

1. Você define um JSON Schema (ou modelo Pydantic)
2. Você o passa para a API junto com seu prompt
3. A amostragem de tokens do modelo é restringida para corresponder ao schema
4. A saída tem **garantia** de ser JSON válido correspondente ao seu schema — todo campo presente, todo tipo correto

!!! tip "Integração com Pydantic"
    O SDK Python da OpenAI pode aceitar um modelo Pydantic diretamente via `response_format=EmailExtraction`. O SDK lida com a conversão do schema automaticamente.

---

## Etapa 2: Carregar e Explorar os Resultados dos Testes

O dataset possui **15 testes de extração** — 10 com imposição de schema (`gpt-4o`) e 5 sem (`gpt-4o-no-schema`):

```python
import pandas as pd

df = pd.read_csv("lab-072/structured_outputs.csv")

# Convert string booleans
for col in ["structured_output_valid", "json_parse_success"]:
    df[col] = df[col].astype(str).str.strip().str.lower() == "true"

print(f"Total tests: {len(df)}")
print(f"Models: {df['model'].unique().tolist()}")
print(f"Input types: {df['input_type'].unique().tolist()}")
print(f"\nFirst 5 rows:\n{df.head()}")
```

**Saída esperada:**

```
Total tests: 15
Models: ['gpt-4o', 'gpt-4o-no-schema']
Input types: ['email', 'invoice', 'resume', 'support_ticket', 'product_review']
```

---

## Etapa 3: Comparar Taxas de Validade de Schema

A coluna `structured_output_valid` indica se a saída correspondeu ao schema esperado (todos os campos presentes, tipos corretos):

```python
schema_rows = df[df["model"] == "gpt-4o"]
no_schema_rows = df[df["model"] == "gpt-4o-no-schema"]

schema_valid_rate = schema_rows["structured_output_valid"].mean() * 100
no_schema_valid_rate = no_schema_rows["structured_output_valid"].mean() * 100

print(f"Schema-enforced validity rate:  {schema_valid_rate:.0f}%")
print(f"No-schema validity rate:        {no_schema_valid_rate:.0f}%")
```

**Saída esperada:**

```
Schema-enforced validity rate:  100%
No-schema validity rate:        0%
```

!!! tip "Insight"
    **100% vs. 0%** — este é o argumento completo a favor de structured outputs. Com imposição de schema, cada extração passa na validação. Sem ela, *nenhuma* passa (algumas podem ser interpretadas como JSON, mas campos estão ausentes ou tipos estão errados).

---

## Etapa 4: Analisar Precisão de Campos

Mesmo quando o JSON é válido, os *valores* extraídos podem não ser precisos. A coluna `field_accuracy_pct` mede quantos campos tiveram o valor correto:

```python
schema_accuracy = schema_rows["field_accuracy_pct"].mean()
no_schema_accuracy = no_schema_rows["field_accuracy_pct"].mean()

print(f"Avg field accuracy (with schema):    {schema_accuracy:.0f}%")
print(f"Avg field accuracy (without schema): {no_schema_accuracy:.0f}%")
```

**Saída esperada:**

```
Avg field accuracy (with schema):    98%
Avg field accuracy (without schema): 68%
```

Detalhamento por tipo de entrada:

```python
accuracy_by_type = df.groupby(["input_type", "model"])["field_accuracy_pct"].mean().unstack()
print(accuracy_by_type.round(1))
```

```python
# Which input types show the biggest accuracy gap?
for input_type in df["input_type"].unique():
    schema_acc = df[(df["input_type"] == input_type) & (df["model"] == "gpt-4o")]["field_accuracy_pct"].mean()
    no_schema_acc = df[(df["input_type"] == input_type) & (df["model"] == "gpt-4o-no-schema")]["field_accuracy_pct"].mean()
    gap = schema_acc - no_schema_acc if not pd.isna(no_schema_acc) else 0
    print(f"  {input_type:>20s}: schema={schema_acc:.0f}%  no-schema={no_schema_acc:.0f}%  gap={gap:.0f}pp")
```

---

## Etapa 5: Medir Latência e Uso de Tokens

A imposição de schema tem um pequeno overhead — o modelo precisa se conformar às restrições durante a decodificação:

```python
for model in df["model"].unique():
    subset = df[df["model"] == model]
    avg_time = subset["time_ms"].mean()
    avg_tokens = subset["tokens"].mean()
    print(f"{model:>20s}: avg_time={avg_time:.0f}ms  avg_tokens={avg_tokens:.0f}")
```

**Saída esperada:**

```
           gpt-4o: avg_time=915ms  avg_tokens=139
  gpt-4o-no-schema: avg_time=660ms  avg_tokens=121
```

!!! warning "Compensação de Latência"
    Saídas com imposição de schema são ~38% mais lentas em média. Isso é esperado — a decodificação restringida requer processamento adicional. Para a maioria dos fluxos de trabalho de agentes, a garantia de confiabilidade compensa amplamente o custo de latência.

---

## Etapa 6: Criar o Relatório de Confiabilidade

```python
report = f"""# 📊 Structured Outputs Reliability Report

## Test Summary
| Metric | With Schema | Without Schema |
|--------|-------------|----------------|
| Tests Run | {len(schema_rows)} | {len(no_schema_rows)} |
| Schema Valid | {schema_valid_rate:.0f}% | {no_schema_valid_rate:.0f}% |
| Avg Field Accuracy | {schema_accuracy:.0f}% | {no_schema_accuracy:.0f}% |
| Avg Latency | {schema_rows['time_ms'].mean():.0f}ms | {no_schema_rows['time_ms'].mean():.0f}ms |
| Avg Tokens | {schema_rows['tokens'].mean():.0f} | {no_schema_rows['tokens'].mean():.0f} |

## Conclusion
Structured Outputs deliver **{schema_valid_rate:.0f}% schema validity** vs. {no_schema_valid_rate:.0f}%
without enforcement. Field accuracy improves from {no_schema_accuracy:.0f}% to {schema_accuracy:.0f}%.

**Recommendation:** Enable Structured Outputs for all extraction pipelines.
The ~38% latency overhead is justified by zero parsing failures in production.
"""

print(report)

with open("lab-072/reliability_report.md", "w") as f:
    f.write(report)
print("💾 Saved to lab-072/reliability_report.md")
```

---

## 🐛 Exercício de Correção de Bugs

O arquivo `lab-072/broken_structured.py` contém **3 bugs** que produzem métricas incorretas. Você consegue encontrar e corrigir todos?

Execute os autotestes para ver quais falham:

```bash
python lab-072/broken_structured.py
```

Você deve ver **3 testes falhando**. Cada teste corresponde a um bug:

| Teste | O que verifica | Dica |
|------|---------------|------|
| Teste 1 | Métrica de taxa de sucesso do schema | Deve verificar `structured_output_valid`, não `json_parse_success` |
| Teste 2 | Precisão sem schema | Deve filtrar pelo modelo sem schema, não pelo modelo com schema |
| Teste 3 | Média de tokens por modelo | Deve filtrar por modelo antes de calcular a média |

Corrija todos os 3 bugs e execute novamente. Quando você vir `All passed!`, está feito!

---


## 🧠 Verificação de Conhecimento

??? question "**Q1 (Múltipla Escolha):** O que distingue Structured Outputs do modo JSON comum?"

    - A) Structured Outputs são mais rápidos que o modo JSON
    - B) Structured Outputs garantem que a saída corresponda a um JSON Schema específico, não apenas JSON válido
    - C) Structured Outputs funcionam sem uma chave de API
    - D) Structured Outputs usam uma arquitetura de modelo diferente

    ??? success "✅ Revelar Resposta"
        **Correta: B) Structured Outputs garantem que a saída corresponda a um JSON Schema específico, não apenas JSON válido**

        O modo JSON garante sintaxe JSON válida (colchetes, aspas, etc. corretos), mas a *estrutura* — quais campos existem, seus tipos, aninhamento — não é imposta. Structured Outputs restringem o decodificador para corresponder a um schema específico, garantindo que cada campo esteja presente com o tipo correto.

??? question "**Q2 (Múltipla Escolha):** Qual biblioteca Python se integra mais facilmente com Structured Outputs da OpenAI para definição de schemas?"

    - A) dataclasses
    - B) marshmallow
    - C) Pydantic
    - D) attrs

    ??? success "✅ Revelar Resposta"
        **Correta: C) Pydantic**

        O SDK Python da OpenAI aceita diretamente subclasses de `BaseModel` do Pydantic via parâmetro `response_format`. O SDK converte o modelo Pydantic para um JSON Schema automaticamente, tornando a definição de schema tão simples quanto escrever uma classe Python.

??? question "**Q3 (Execute o Lab):** Qual é a taxa de validade de schema para os testes de extração com imposição de schema?"

    Execute a análise da Etapa 3 em [📥 `structured_outputs.csv`](https://github.com/lcarli/AI-LearningHub/raw/main/docs/docs/en/labs/lab-072/structured_outputs.csv) e confira os resultados.

    ??? success "✅ Revelar Resposta"
        **100%**

        Todos os 10 testes com imposição de schema (`model=gpt-4o`) possuem `structured_output_valid=true`. O decodificador restringido garante que cada saída corresponda ao JSON Schema definido — zero falhas de parsing ou validação.

??? question "**Q4 (Execute o Lab):** Qual é a taxa de validade de schema para os testes **sem** imposição de schema?"

    Execute a análise da Etapa 3 para comparar.

    ??? success "✅ Revelar Resposta"
        **0%**

        Todos os 5 testes sem schema (`model=gpt-4o-no-schema`) possuem `structured_output_valid=false`. Mesmo que alguns produzam JSON interpretável (`json_parse_success=true`), eles falham na validação de schema porque campos estão ausentes, possuem tipos errados ou usam nomes de chave inesperados.

??? question "**Q5 (Execute o Lab):** Qual é a precisão média de campos para os testes com imposição de schema (linhas gpt-4o)?"

    Execute a análise da Etapa 4 para calcular.

    ??? success "✅ Revelar Resposta"
        **98%**

        Os 10 testes com imposição de schema possuem precisões de campo de 100, 100, 100, 95, 100, 90, 100, 100, 100 e 95. A média é (100+100+100+95+100+90+100+100+100+95) ÷ 10 = **98%**.

---

## Resumo

| Tópico | O que Você Aprendeu |
|-------|-----------------|
| Structured Outputs | Decodificação restringida por JSON Schema que garante saída válida |
| Validade de Schema | 100% com imposição vs. 0% sem — elimina falhas de parsing |
| Precisão de Campos | 98% com schema vs. 68% sem — a estrutura melhora a precisão do conteúdo |
| Integração com Pydantic | Defina schemas como classes Python para integração perfeita com a API |
| Compensação de Latência | ~38% de overhead é justificado pela confiabilidade em produção |
| Prontidão para Produção | Zero falhas de parsing torna structured outputs essenciais para pipelines |

---

## Próximos Passos

- **[Lab 018](lab-018-function-calling.md)** — Function Calling (a base para agentes que usam ferramentas)
- **[Lab 017](lab-017-structured-output.md)** — Structured Output em profundidade (teoria complementar)
- **[Lab 071](lab-071-context-caching.md)** — Context Caching (otimização de custos para fluxos com muitos schemas)
- **[Lab 073](lab-073-swe-bench.md)** — Benchmarking de Agentes com SWE-bench (avalie a qualidade do agente)
