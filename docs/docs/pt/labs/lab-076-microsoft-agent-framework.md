---
tags: [agent-framework, semantic-kernel, autogen, migration, python, dotnet]
---
# Lab 076: Microsoft Agent Framework — De SK para MAF

<div class="lab-meta">
  <span><strong>Nível:</strong> <span class="level-badge level-200">L200</span></span>
  <span><strong>Trilha:</strong> Todas as trilhas</span>
  <span><strong>Tempo:</strong> ~75 min</span>
  <span><strong>💰 Custo:</strong> <span class="level-badge cost-free">Gratuito</span> — Usa dados simulados de migração</span>
</div>

## O que Você Vai Aprender

- Como **Semantic Kernel** e **AutoGen** são unificados no **Microsoft Agent Framework (MAF)**
- O que são **Agent Skills** (pacotes portáteis de habilidades em `.md`) e como eles permitem reutilização
- Como **Graph Workflows** (DAG com checkpointing) substituem pipelines lineares
- Analisar uma **matriz de migração** comparando 15 funcionalidades entre SK, AutoGen e MAF
- Identificar níveis de esforço de migração e capacidades exclusivas do MAF

## Introdução

O **Microsoft Agent Framework (MAF)** unifica Semantic Kernel e AutoGen em uma única plataforma coesa para construção de agentes de IA. Lançado como **Release Candidate em fevereiro de 2026**, o MAF reúne o melhor dos dois mundos:

- O sistema de plugins, planejadores e conectores empresariais do **Semantic Kernel**
- As conversas multi-agente, execução de código e padrões de chat em grupo do **AutoGen**

### Instalação

```bash
pip install agent-framework
```

### Conceitos-Chave

| Conceito | Descrição |
|----------|-----------|
| **Agent Skills** | Pacotes portáteis de habilidades em `.md` que definem capacidades do agente, entradas, saídas e dependências — compartilháveis entre equipes e projetos |
| **Graph Workflows** | Orquestração baseada em DAG com checkpointing, retry e ramificação — substituindo pipelines lineares |
| **DevUI** | Interface de desenvolvimento integrada para depuração de conversas de agentes, inspeção de execução de habilidades e visualização de workflows |
| **API Unificada** | Superfície de API única que substitui o `Kernel` do SK e o `AssistantAgent` do AutoGen por uma classe `Agent` comum |

### O Cenário

Você é um **Engenheiro de Plataforma** em uma empresa que construiu agentes usando tanto Semantic Kernel quanto AutoGen. A liderança decidiu migrar para o MAF. Você tem uma **matriz de migração** (`migration_matrix.csv`) que mapeia 15 funcionalidades nos três frameworks — rastreando disponibilidade, esforço de migração e funcionalidades exclusivas do MAF.

Seu trabalho: analisar a matriz, identificar ganhos rápidos, sinalizar desafios e construir um plano de migração.

!!! info "Dados Simulados"
    Este laboratório usa um CSV de matriz de migração simulado. Os dados refletem o mapeamento real de funcionalidades entre Semantic Kernel, AutoGen e MAF conforme documentado nos guias de migração.

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
    Salve todos os arquivos em uma pasta `lab-076/` no seu diretório de trabalho.

| Arquivo | Descrição | Download |
|---------|-----------|----------|
| `broken_migration.py` | Exercício de correção de bugs (3 bugs + autotestes) | [📥 Download](https://github.com/lcarli/AI-LearningHub/raw/main/docs/docs/en/labs/lab-076/broken_migration.py) |
| `migration_matrix.csv` | Comparação de 15 funcionalidades: SK vs AutoGen vs MAF | [📥 Download](https://github.com/lcarli/AI-LearningHub/raw/main/docs/docs/en/labs/lab-076/migration_matrix.csv) |

---

## Etapa 1: Entenda a Matriz de Migração

A matriz de migração mapeia 15 funcionalidades em três frameworks. Cada linha representa uma capacidade:

| Coluna | Descrição |
|--------|-----------|
| **feature** | A capacidade sendo comparada (ex.: `plugins`, `multi_agent_chat`) |
| **sk_support** | Se Semantic Kernel suporta esta funcionalidade: `yes`, `partial` ou `no` |
| **autogen_support** | Se AutoGen suporta esta funcionalidade: `yes`, `partial` ou `no` |
| **maf_support** | Se MAF suporta esta funcionalidade: `yes`, `partial` ou `no` |
| **migration_effort** | Esforço para migrar de SK/AutoGen para MAF: `low`, `medium` ou `high` |
| **category** | Categoria da funcionalidade: `core`, `orchestration`, `tooling` ou `integration` |

---

## Etapa 2: Carregue e Explore a Matriz

```python
import pandas as pd

df = pd.read_csv("lab-076/migration_matrix.csv")

print(f"Total features: {len(df)}")
print(f"Categories: {df['category'].value_counts().to_dict()}")
print(f"Migration effort: {df['migration_effort'].value_counts().to_dict()}")
print(f"\nFull matrix:")
print(df[["feature", "sk_support", "autogen_support", "maf_support", "migration_effort"]].to_string(index=False))
```

**Saída esperada:**

```
Total features: 15
Categories: {'core': 5, 'orchestration': 4, 'tooling': 3, 'integration': 3}
Migration effort: {'low': 7, 'medium': 5, 'high': 3}
```

---

## Etapa 3: Identifique Ganhos Rápidos (Baixo Esforço de Migração)

Funcionalidades com esforço de migração `low` são seus ganhos rápidos — comece por aqui:

```python
low_effort = df[df["migration_effort"] == "low"]
print(f"Quick wins (low effort): {len(low_effort)} features\n")
for _, row in low_effort.iterrows():
    print(f"  {row['feature']:>25s}  SK={row['sk_support']:<8s} AutoGen={row['autogen_support']:<8s} MAF={row['maf_support']}")
```

!!! tip "Estratégia de Migração"
    **Comece pelas funcionalidades de baixo esforço** para construir a confiança da equipe e demonstrar a API unificada do MAF. Estas geralmente possuem equivalentes diretos no SK ou AutoGen, tornando a migração simples.

---

## Etapa 4: Encontre Funcionalidades Exclusivas do MAF

Quais funcionalidades existem no MAF mas não no Semantic Kernel?

```python
maf_only_vs_sk = df[(df["maf_support"] == "yes") & (df["sk_support"] == "no")]
print(f"Features in MAF but NOT in SK: {len(maf_only_vs_sk)}\n")
for _, row in maf_only_vs_sk.iterrows():
    print(f"  {row['feature']:>25s}  category={row['category']}")
```

```python
# Features exclusive to MAF (not in SK AND not in AutoGen)
maf_exclusive = df[(df["maf_support"] == "yes") & (df["sk_support"] == "no") & (df["autogen_support"] == "no")]
print(f"\nMAF-exclusive features (not in SK or AutoGen): {len(maf_exclusive)}")
for _, row in maf_exclusive.iterrows():
    print(f"  {row['feature']}: {row['category']}")
```

---

## Etapa 5: Analise as Migrações de Alto Esforço

Estas funcionalidades precisam de mais planejamento:

```python
high_effort = df[df["migration_effort"] == "high"]
print(f"High-effort migrations: {len(high_effort)}\n")
for _, row in high_effort.iterrows():
    print(f"  {row['feature']}")
    print(f"    SK: {row['sk_support']}, AutoGen: {row['autogen_support']}, MAF: {row['maf_support']}")
    print(f"    Category: {row['category']}")
    print()
```

!!! warning "Risco de Migração"
    Funcionalidades de alto esforço frequentemente envolvem **mudanças arquiteturais** — por exemplo, substituir orquestração customizada por Graph Workflows ou converter plugins proprietários em Agent Skills. Planeje de 2 a 4 semanas por funcionalidade de alto esforço.

---

## Etapa 6: Construa o Plano de Migração

```python
report = f"""# 📋 MAF Migration Plan

## Matrix Summary
| Metric | Value |
|--------|-------|
| Total Features | {len(df)} |
| Low Effort | {len(df[df['migration_effort'] == 'low'])} |
| Medium Effort | {len(df[df['migration_effort'] == 'medium'])} |
| High Effort | {len(df[df['migration_effort'] == 'high'])} |
| MAF-only (vs SK) | {len(maf_only_vs_sk)} |

## Phase 1: Quick Wins (Weeks 1–2)
Migrate {len(low_effort)} low-effort features:
"""
for _, row in low_effort.iterrows():
    report += f"- {row['feature']} ({row['category']})\n"

report += f"""
## Phase 2: Medium Effort (Weeks 3–5)
Migrate {len(df[df['migration_effort'] == 'medium'])} medium-effort features with dedicated sprint time.

## Phase 3: High Effort (Weeks 6–10)
Migrate {len(high_effort)} high-effort features requiring architectural changes.

## New Capabilities Unlocked
MAF-exclusive features not available in SK or AutoGen:
"""
for _, row in maf_exclusive.iterrows():
    report += f"- **{row['feature']}** ({row['category']})\n"

print(report)

with open("lab-076/migration_plan.md", "w") as f:
    f.write(report)
print("💾 Saved to lab-076/migration_plan.md")
```

---

## 🐛 Exercício de Correção de Bugs

O arquivo `lab-076/broken_migration.py` contém **3 bugs** que produzem análise de migração incorreta. Você consegue encontrar e corrigir todos?

Execute os autotestes para ver quais falham:

```bash
python lab-076/broken_migration.py
```

Você deverá ver **3 testes falhando**. Cada teste corresponde a um bug:

| Teste | O que verifica | Dica |
|-------|---------------|------|
| Teste 1 | Contagem de funcionalidades de baixo esforço | Deve filtrar `migration_effort == "low"`, não `"high"` |
| Teste 2 | Contagem de MAF-only vs SK | Deve verificar `sk_support == "no"`, não `"yes"` |
| Teste 3 | Contagem total de funcionalidades | Deve usar `len(df)`, não `len(df.columns)` |

Corrija todos os 3 bugs e execute novamente. Quando você ver `All passed!`, está pronto!

---


## 🧠 Verificação de Conhecimento

??? question "**Q1 (Múltipla Escolha):** O que é o Microsoft Agent Framework (MAF)?"

    - A) Uma nova versão do AutoGen com um nome diferente
    - B) Um framework unificado que combina Semantic Kernel e AutoGen em uma única plataforma
    - C) Um serviço exclusivo de nuvem para executar agentes no Azure
    - D) Um substituto para o LangChain

    ??? success "✅ Revelar Resposta"
        **Correto: B) Um framework unificado que combina Semantic Kernel e AutoGen em uma única plataforma**

        O MAF une os pontos fortes de ambos os frameworks: o sistema de plugins empresariais e planejadores do SK com as conversas multi-agente e execução de código do AutoGen. Ele fornece uma única classe `Agent`, Agent Skills portáteis e Graph Workflows baseados em DAG.

??? question "**Q2 (Múltipla Escolha):** O que são Agent Skills no MAF?"

    - A) Funções Python decoradas com `@skill`
    - B) Pacotes portáteis de habilidades em `.md` que definem capacidades, entradas, saídas e dependências
    - C) Pesos de modelo pré-treinados para tarefas específicas
    - D) Azure Functions que os agentes podem chamar

    ??? success "✅ Revelar Resposta"
        **Correto: B) Pacotes portáteis de habilidades em `.md` que definem capacidades, entradas, saídas e dependências**

        Agent Skills são pacotes baseados em markdown que descrevem o que um agente pode fazer, quais entradas ele precisa, quais saídas ele produz e quais dependências são necessárias. Eles são compartilháveis entre equipes e projetos, permitindo um marketplace de capacidades reutilizáveis de agentes.

??? question "**Q3 (Execute o Laboratório):** Quantas funcionalidades têm esforço de migração 'low'?"

    Execute a análise da Etapa 3 no [📥 `migration_matrix.csv`](https://github.com/lcarli/AI-LearningHub/raw/main/docs/docs/en/labs/lab-076/migration_matrix.csv) e conte as funcionalidades de baixo esforço.

    ??? success "✅ Revelar Resposta"
        **7 funcionalidades**

        Das 15 funcionalidades na matriz de migração, **7 têm `migration_effort = "low"`**. Estes são os ganhos rápidos para a Fase 1 da migração — geralmente funcionalidades com equivalentes diretos entre SK/AutoGen e MAF.

??? question "**Q4 (Execute o Laboratório):** Quantas funcionalidades estão disponíveis no MAF mas NÃO no Semantic Kernel?"

    Execute a análise da Etapa 4 para encontrar funcionalidades onde `maf_support = "yes"` e `sk_support = "no"`.

    ??? success "✅ Revelar Resposta"
        **A contagem de funcionalidades onde MAF tem suporte `yes` mas SK tem suporte `no`.**

        Estas representam capacidades que as equipes ganham ao migrar do SK para o MAF — como padrões de chat multi-agente, sandboxes de execução de código e outras funcionalidades que originaram no AutoGen e agora estão disponíveis no framework unificado.

??? question "**Q5 (Execute o Laboratório):** Quantas funcionalidades no total são rastreadas na matriz de migração?"

    Carregue o CSV e verifique a contagem total de linhas.

    ??? success "✅ Revelar Resposta"
        **15 funcionalidades**

        A matriz de migração rastreia **15 funcionalidades** em 4 categorias: core (5), orchestration (4), tooling (3) e integration (3). Cada funcionalidade é avaliada quanto ao suporte em SK, AutoGen e MAF, junto com o esforço de migração.

---

## Resumo

| Tópico | O que Você Aprendeu |
|--------|---------------------|
| Microsoft Agent Framework | Plataforma unificada que une Semantic Kernel e AutoGen (RC Fev 2026) |
| Agent Skills | Pacotes portáteis de habilidades em `.md` para capacidades reutilizáveis de agentes |
| Graph Workflows | Orquestração baseada em DAG com checkpointing, substituindo pipelines lineares |
| Matriz de Migração | 15 funcionalidades comparadas entre SK, AutoGen e MAF |
| Estratégia de Migração | Comece pelo baixo esforço (7 funcionalidades), planeje para alto esforço (3 funcionalidades) |
| DevUI | Interface de desenvolvimento integrada para depuração e visualização de workflows de agentes |

---

## Próximos Passos

- **[Lab 034](lab-034-multi-agent-sk.md)** — Multi-Agente com Semantic Kernel (entenda de onde você está migrando)
- **[Lab 036](lab-036-autogen-basics.md)** — Fundamentos do AutoGen (entenda os padrões do AutoGen antes do MAF)
- **[Lab 074](lab-074-foundry-agent-service.md)** — Foundry Agent Service (implante agentes MAF em produção)
- **[Lab 073](lab-073-swe-bench.md)** — SWE-Bench (avalie agentes MAF em tarefas de codificação do mundo real)
