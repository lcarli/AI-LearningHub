---
tags: [foundry-local, local-inference, free, ollama-alternative, python]
---
# Lab 078: Foundry Local — Execute Modelos de IA Offline

<div class="lab-meta">
  <span><strong>Nível:</strong> <span class="level-badge level-100">L100</span></span>
  <span><strong>Trilha:</strong> Todas as trilhas</span>
  <span><strong>Tempo:</strong> ~45 min</span>
  <span><strong>💰 Custo:</strong> <span class="level-badge cost-free">Gratuito</span> — Executa inteiramente em hardware local</span>
</div>

## O que Você Vai Aprender

- O que é o **Foundry Local** e como ele possibilita a inferência de modelos de IA offline
- Como instalar e executar modelos com `winget` e a CLI `foundry`
- Como a **API compatível com OpenAI** torna o Foundry Local um substituto direto
- Analisar um **catálogo de modelos** com 8 modelos — comparando tamanhos, requisitos de hardware e qualidade
- Identificar o **menor modelo** e quais modelos suportam inferência **somente em CPU**

## Introdução

**Foundry Local** é o runtime de inferência local da Microsoft que permite executar modelos de IA inteiramente no seu próprio hardware — sem nuvem, sem chaves de API, sem internet. É uma alternativa gratuita ao Ollama, otimizada para Windows com aceleração GPU via DirectML.

### Instalação

```bash
winget install Microsoft.FoundryLocal
```

### Executando um Modelo

```bash
foundry model run phi-4-mini
```

Isso baixa o modelo (se necessário) e inicia um servidor local com uma **API compatível com OpenAI** em `http://localhost:5273`:

```python
from openai import OpenAI

client = OpenAI(base_url="http://localhost:5273/v1", api_key="not-needed")

response = client.chat.completions.create(
    model="phi-4-mini",
    messages=[{"role": "user", "content": "Explain quantum computing in 2 sentences."}]
)
print(response.choices[0].message.content)
```

### O Cenário

Você é um **Engenheiro DevOps** avaliando o Foundry Local para implantações em ambientes isolados (offline). Você tem um catálogo de **8 modelos** (`foundry_models.csv`) com tamanho, requisitos de hardware e benchmarks de qualidade. Sua tarefa: analisar o catálogo, encontrar o melhor modelo para diferentes perfis de hardware e construir uma recomendação de implantação.

!!! info "Dados Simulados"
    Este laboratório usa um CSV de catálogo de modelos simulado. Os nomes e tamanhos dos modelos são representativos dos modelos disponíveis no catálogo do Foundry Local no início de 2026.

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
    Salve todos os arquivos em uma pasta `lab-078/` no seu diretório de trabalho.

| Arquivo | Descrição | Download |
|---------|-----------|----------|
| `broken_foundry_local.py` | Exercício de correção de bugs (3 bugs + autotestes) | [📥 Download](https://github.com/lcarli/AI-LearningHub/raw/main/docs/docs/en/labs/lab-078/broken_foundry_local.py) |
| `foundry_models.csv` | Catálogo de 8 modelos com tamanhos, hardware e pontuações de qualidade | [📥 Download](https://github.com/lcarli/AI-LearningHub/raw/main/docs/docs/en/labs/lab-078/foundry_models.csv) |

---

## Etapa 1: Entenda o Catálogo de Modelos

Cada modelo no catálogo possui os seguintes atributos:

| Coluna | Descrição |
|--------|-----------|
| **model_name** | Identificador do modelo (ex.: `phi-4-mini`, `qwen2.5-0.5b`) |
| **size_gb** | Tamanho do download em gigabytes |
| **parameters** | Número de parâmetros do modelo (ex.: `3.8B`, `0.5B`) |
| **hardware** | Hardware necessário: `cpu_only`, `gpu_recommended` ou `gpu_required` |
| **quality_score** | Pontuação de qualidade do benchmark (0.0–1.0) |
| **use_case** | Caso de uso principal: `chat`, `coding`, `embedding` ou `general` |
| **quantization** | Nível de quantização: `q4`, `q8` ou `fp16` |

---

## Etapa 2: Carregue e Explore o Catálogo

```python
import pandas as pd

df = pd.read_csv("lab-078/foundry_models.csv")

print(f"Total models: {len(df)}")
print(f"Hardware requirements: {df['hardware'].value_counts().to_dict()}")
print(f"Use cases: {df['use_case'].value_counts().to_dict()}")
print(f"\nFull catalog:")
print(df[["model_name", "size_gb", "parameters", "hardware", "quality_score"]].to_string(index=False))
```

**Saída esperada:**

```
Total models: 8
Hardware requirements: {'gpu_recommended': 4, 'cpu_only': 2, 'gpu_required': 2}
Use cases: {'chat': 3, 'coding': 2, 'general': 2, 'embedding': 1}
```

---

## Etapa 3: Encontre o Menor Modelo

```python
smallest = df.loc[df["size_gb"].idxmin()]
largest = df.loc[df["size_gb"].idxmax()]

print(f"Smallest model: {smallest['model_name']} ({smallest['size_gb']} GB)")
print(f"  Parameters: {smallest['parameters']}")
print(f"  Hardware: {smallest['hardware']}")
print(f"  Quality: {smallest['quality_score']}")

print(f"\nLargest model: {largest['model_name']} ({largest['size_gb']} GB)")
print(f"  Parameters: {largest['parameters']}")
print(f"  Hardware: {largest['hardware']}")
print(f"  Quality: {largest['quality_score']}")

print(f"\nSize range: {smallest['size_gb']} GB – {largest['size_gb']} GB")
```

**Saída esperada:**

```
Smallest model: qwen2.5-0.5b (0.4 GB)
  Parameters: 0.5B
  Hardware: cpu_only
  Quality: 0.52
```

!!! tip "Implantação em Borda"
    **qwen2.5-0.5b** com apenas **0.4 GB** é ideal para dispositivos de borda, gateways IoT ou máquinas com armazenamento mínimo. Apesar do tamanho reduzido, ele lida com tarefas básicas de chat e sumarização razoavelmente bem.

---

## Etapa 4: Identifique os Modelos Somente CPU

Para máquinas isoladas sem GPUs:

```python
cpu_models = df[df["hardware"] == "cpu_only"]
print(f"CPU-only models: {len(cpu_models)}\n")
for _, row in cpu_models.iterrows():
    print(f"  {row['model_name']:>20s}  size={row['size_gb']}GB  quality={row['quality_score']}  use_case={row['use_case']}")
```

```python
# Compare CPU-only vs GPU models
gpu_models = df[df["hardware"] != "cpu_only"]
print(f"\nCPU-only avg quality: {cpu_models['quality_score'].mean():.2f}")
print(f"GPU models avg quality: {gpu_models['quality_score'].mean():.2f}")
print(f"Quality gap: {(gpu_models['quality_score'].mean() - cpu_models['quality_score'].mean()) * 100:.1f}pp")
```

!!! warning "Compensação de Qualidade"
    Modelos somente CPU são menores e funcionam em qualquer lugar, mas suas pontuações de qualidade são tipicamente mais baixas que as dos modelos GPU. Para casos de uso em produção que exigem alta precisão, prefira modelos com GPU recomendada e pelo menos 4 GB de VRAM.

---

## Etapa 5: Analise por Caso de Uso

```python
print("Models by use case:\n")
for use_case, group in df.groupby("use_case"):
    print(f"  {use_case.upper()} ({len(group)} models):")
    for _, row in group.iterrows():
        print(f"    {row['model_name']:>20s}  {row['size_gb']}GB  quality={row['quality_score']}")
    print()

# Best model per use case
print("Best model per use case (by quality):")
for use_case, group in df.groupby("use_case"):
    best = group.loc[group["quality_score"].idxmax()]
    print(f"  {use_case:>10s}: {best['model_name']} (quality={best['quality_score']}, size={best['size_gb']}GB)")
```

---

## Etapa 6: Construa a Recomendação de Implantação

```python
report = f"""# 📋 Foundry Local Deployment Recommendation

## Catalog Summary
| Metric | Value |
|--------|-------|
| Total Models | {len(df)} |
| CPU-Only | {len(cpu_models)} |
| GPU Recommended | {len(df[df['hardware'] == 'gpu_recommended'])} |
| GPU Required | {len(df[df['hardware'] == 'gpu_required'])} |
| Smallest | {smallest['model_name']} ({smallest['size_gb']} GB) |
| Largest | {largest['model_name']} ({largest['size_gb']} GB) |

## Hardware Profiles

### Profile A: Edge Device (CPU only, 2 GB storage)
"""

for _, row in cpu_models.iterrows():
    report += f"- **{row['model_name']}** — {row['size_gb']} GB, quality {row['quality_score']}\n"

report += f"""
### Profile B: Developer Laptop (GPU, 16 GB storage)
"""

for _, row in df[df["hardware"] == "gpu_recommended"].iterrows():
    report += f"- **{row['model_name']}** — {row['size_gb']} GB, quality {row['quality_score']}\n"

report += f"""
### Profile C: Workstation (High-end GPU, 64 GB storage)
"""

for _, row in df[df["hardware"] == "gpu_required"].iterrows():
    report += f"- **{row['model_name']}** — {row['size_gb']} GB, quality {row['quality_score']}\n"

print(report)

with open("lab-078/deployment_recommendation.md", "w") as f:
    f.write(report)
print("💾 Saved to lab-078/deployment_recommendation.md")
```

---

## 🐛 Exercício de Correção de Bugs

O arquivo `lab-078/broken_foundry_local.py` contém **3 bugs** que produzem análises de modelos incorretas. Você consegue encontrar e corrigir todos?

Execute os autotestes para ver quais falham:

```bash
python lab-078/broken_foundry_local.py
```

Você deverá ver **3 testes falhando**. Cada teste corresponde a um bug:

| Teste | O que verifica | Dica |
|-------|---------------|------|
| Teste 1 | Nome do menor modelo | Deve encontrar o mínimo de `size_gb`, não o máximo |
| Teste 2 | Contagem de modelos somente CPU | Deve filtrar `hardware == "cpu_only"`, não `"gpu_required"` |
| Teste 3 | Contagem total de modelos | Deve usar `len(df)`, não um valor fixo no código |

Corrija todos os 3 bugs e execute novamente. Quando você vir `All passed!`, está pronto!

---


## 🧠 Verificação de Conhecimento

??? question "**Q1 (Múltipla Escolha):** O que torna o Foundry Local diferente dos serviços de IA em nuvem?"

    - A) Ele suporta apenas modelos da Microsoft
    - B) Ele executa modelos de IA inteiramente em hardware local, sem necessidade de internet
    - C) Ele requer uma assinatura do Azure
    - D) Ele funciona apenas no Linux

    ??? success "✅ Revelar Resposta"
        **Correto: B) Ele executa modelos de IA inteiramente em hardware local, sem necessidade de internet**

        O Foundry Local é um runtime de inferência local — os modelos são baixados uma vez e executados inteiramente offline. Ele usa uma API compatível com OpenAI, tornando-o um substituto direto para endpoints em nuvem. Sem chaves de API, sem internet, sem custos por token.

??? question "**Q2 (Múltipla Escolha):** Por que o Foundry Local usa uma API compatível com OpenAI?"

    - A) Ele é construído pela OpenAI
    - B) Ele permite substituição direta — código existente que chama APIs da OpenAI funciona sem alterações
    - C) A OpenAI exige que todos os mecanismos de inferência usem seu formato de API
    - D) Ele executa apenas modelos da OpenAI

    ??? success "✅ Revelar Resposta"
        **Correto: B) Ele permite substituição direta — código existente que chama APIs da OpenAI funciona sem alterações**

        Ao expor o mesmo formato de endpoint `/v1/chat/completions`, o Foundry Local permite que desenvolvedores mudem da inferência em nuvem para local alterando apenas o `base_url`. Todos os SDKs, ferramentas e frameworks existentes que utilizam o formato de API da OpenAI funcionam imediatamente.

??? question "**Q3 (Execute o Laboratório):** Qual é o menor modelo no catálogo e qual o seu tamanho?"

    Execute a análise da Etapa 3 no [📥 `foundry_models.csv`](https://github.com/lcarli/AI-LearningHub/raw/main/docs/docs/en/labs/lab-078/foundry_models.csv) para encontrar o menor modelo.

    ??? success "✅ Revelar Resposta"
        **qwen2.5-0.5b com 0.4 GB**

        O menor modelo no catálogo é o **qwen2.5-0.5b** com apenas **0.4 GB** de tamanho de download e 0.5B parâmetros. Ele roda somente em CPU e atinge uma pontuação de qualidade de 0.52 — adequado para chat básico e implantações em borda.

??? question "**Q4 (Execute o Laboratório):** Quantos modelos suportam inferência somente em CPU?"

    Execute a análise da Etapa 4 para filtrar modelos com `hardware == "cpu_only"`.

    ??? success "✅ Revelar Resposta"
        **2 modelos**

        Apenas **2 modelos** suportam inferência somente em CPU. Esses são os menores modelos no catálogo, otimizados com quantização agressiva (q4) para rodar sem aceleração GPU. São ideais para dispositivos de borda e ambientes isolados.

??? question "**Q5 (Execute o Laboratório):** Quantos modelos no total estão disponíveis no catálogo do Foundry Local?"

    Carregue o CSV e verifique a contagem total de linhas.

    ??? success "✅ Revelar Resposta"
        **8 modelos**

        O catálogo do Foundry Local inclui **8 modelos** em 4 casos de uso: chat (3), coding (2), general (2) e embedding (1). Os requisitos de hardware variam de somente CPU a GPU obrigatória.

---

## Resumo

| Tópico | O que Você Aprendeu |
|--------|---------------------|
| Foundry Local | Runtime de inferência local da Microsoft — gratuito, offline, sem chaves de API |
| Instalação | `winget install Microsoft.FoundryLocal` + `foundry model run` |
| Compatibilidade OpenAI | Substituição direta via `http://localhost:5273/v1` |
| Catálogo de Modelos | 8 modelos de 0.4 GB a vários GB, de CPU a GPU obrigatória |
| Menor Modelo | qwen2.5-0.5b com 0.4 GB — roda em CPU, ideal para borda |
| Perfis de Hardware | Somente CPU (2 modelos), GPU recomendada (4), GPU obrigatória (2) |

---

## Próximos Passos

- **[Lab 074](lab-074-foundry-agent-service.md)** — Foundry Agent Service (implante agentes usando modelos Foundry)
- **[Lab 071](lab-071-context-caching.md)** — Cache de Contexto (otimize a inferência local com cache de prompts)
- **[Lab 038](lab-038-cost-optimization.md)** — Otimização de Custos de IA (compare custos de inferência local vs. nuvem)
- **[Lab 076](lab-076-microsoft-agent-framework.md)** — Microsoft Agent Framework (use o Foundry Local como backend de inferência para agentes MAF)
