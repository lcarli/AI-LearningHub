---
tags: [claude-code, copilot-cli, coding-tools, developer-experience, comparison]
---
# Lab 081: Ferramentas de Codificação Agênticas — Claude Code vs Copilot CLI

<div class="lab-meta">
  <span><strong>Nível:</strong> <span class="level-badge level-100">L100</span></span>
  <span><strong>Trilha:</strong> Todas as trilhas</span>
  <span><strong>Tempo:</strong> ~45 min</span>
  <span><strong>💰 Custo:</strong> <span class="level-badge cost-free">Gratuito</span></span>
</div>

## O que Você Vai Aprender

- O que são **ferramentas de codificação agênticas** — assistentes de IA que operam diretamente no seu terminal com contexto completo da base de código
- Comparar **Claude Code** e **GitHub Copilot CLI** em 10 tarefas reais de desenvolvimento
- Entender como cada ferramenta lida com **compreensão de código**, **geração**, **depuração** e **fluxos de trabalho git**
- Medir a **economia de tempo** em comparação com abordagens manuais para tarefas comuns de desenvolvimento
- Depurar um script de análise comparativa quebrado corrigindo 3 bugs

## Introdução

Uma nova categoria de ferramentas para desenvolvedores surgiu: **assistentes de codificação agênticos** que rodam no seu terminal, leem toda a sua base de código e executam tarefas de múltiplas etapas de forma autônoma. Diferente dos copilots baseados em IDE que sugerem linhas ou blocos individuais, essas ferramentas podem pesquisar bases de código, escrever testes, criar commits, refatorar módulos e depurar pipelines com falhas — tudo a partir de um único prompt em linguagem natural.

Duas ferramentas líderes neste espaço são:

| Ferramenta | Fornecedor | Como Funciona |
|------------|-----------|---------------|
| **Claude Code** | Anthropic | Agente de terminal que lê sua base de código, executa comandos e edita arquivos diretamente |
| **GitHub Copilot CLI** | GitHub | Agente de terminal integrado ao ecossistema GitHub, executa comandos e edita arquivos |

Ambas as ferramentas compartilham um padrão comum: aceitam uma tarefa em linguagem natural, analisam sua base de código para contexto, planejam uma abordagem e a executam — frequentemente em uma única interação.

### O Cenário

Você é um **Tech Lead** na OutdoorGear Inc. avaliando assistentes de codificação baseados em terminal para sua equipe de engenharia. Você fez benchmark de ambas as ferramentas em **10 tarefas representativas de desenvolvimento** e agora precisa analisar os resultados para fazer uma recomendação.

!!! info "Não é Necessário Instalar Ferramentas"
    Este laboratório analisa um **dataset de benchmark pré-gravado** comparando tempos de conclusão de tarefas e taxas de sucesso. Você não precisa ter Claude Code ou Copilot CLI instalados — toda a análise é feita localmente com pandas.

## Pré-requisitos

| Requisito | Por quê |
|-----------|---------|
| Python 3.10+ | Executar scripts de análise |
| Biblioteca `pandas` | Operações com DataFrame |

```bash
pip install pandas
```

---

!!! tip "Início Rápido com GitHub Codespaces"
    [![Open in GitHub Codespaces](https://github.com/codespaces/badge.svg)](https://codespaces.new/lcarli/AI-LearningHub?quickstart=1)

    Todas as dependências estão pré-instaladas no devcontainer.


## 📦 Arquivos de Apoio

!!! note "Baixe estes arquivos antes de iniciar o laboratório"
    Salve todos os arquivos em uma pasta `lab-081/` no seu diretório de trabalho.

| Arquivo | Descrição | Download |
|---------|-----------|----------|
| `broken_tools.py` | Exercício de correção de bugs (3 bugs + auto-testes) | [📥 Download](https://github.com/lcarli/AI-LearningHub/raw/main/docs/docs/en/labs/lab-081/broken_tools.py) |
| `coding_tools_comparison.csv` | Dataset — 10 tarefas comparadas entre ferramentas | [📥 Download](https://github.com/lcarli/AI-LearningHub/raw/main/docs/docs/en/labs/lab-081/coding_tools_comparison.csv) |

---

## Etapa 1: Entendendo Ferramentas de Codificação Agênticas

Tanto Claude Code quanto Copilot CLI seguem um loop de agente similar:

```
┌──────────────┐     ┌──────────────┐     ┌──────────────┐
│  User Prompt │────▶│  Codebase    │────▶│  Plan &      │
│  (terminal)  │     │  Analysis    │     │  Execute     │
└──────────────┘     └──────────────┘     └──────────────┘
                                                │
                     ┌──────────────┐            │
                     │  Edit files, │◀───────────┘
                     │  run commands│
                     └──────────────┘
```

Capacidades principais compartilhadas por ambas as ferramentas:

| Capacidade | Descrição |
|-----------|-----------|
| **Compreensão de base de código** | Ler e raciocinar sobre estrutura do projeto, dependências e padrões |
| **Geração de código** | Escrever novo código (funções, testes, módulos) alinhado com as convenções do projeto |
| **Depuração** | Analisar erros, rastrear problemas e aplicar correções |
| **Fluxos de trabalho git** | Preparar alterações, criar commits com mensagens convencionais, gerenciar branches |
| **Refatoração** | Reestruturar código preservando o comportamento |
| **Revisão de código** | Revisar alterações e sugerir melhorias |

---

## Etapa 2: Carregar o Dataset de Benchmark

O dataset contém **10 tarefas** com benchmark em ambas as ferramentas e conclusão manual:

```python
import pandas as pd

tasks = pd.read_csv("lab-081/coding_tools_comparison.csv")
print(f"Total tasks: {len(tasks)}")
print(f"Categories: {sorted(tasks['category'].unique())}")
print(f"\nDataset preview:")
print(tasks[["task_id", "task_description", "category"]].to_string(index=False))
```

**Saída esperada:**

```
Total tasks: 10
Categories: ['code_generation', 'code_review', 'code_understanding', 'codebase_search', 'debugging', 'devops', 'git_workflow', 'migration', 'refactoring', 'scaffolding']
```

| task_id | task_description | category |
|---------|-----------------|----------|
| T01 | Explain a complex function in the codebase | code_understanding |
| T02 | Find all API endpoints in the project | codebase_search |
| ... | ... | ... |
| T10 | Debug a failing CI pipeline | devops |

---

## Etapa 3: Comparar Taxas de Sucesso

Calcule as taxas de sucesso para cada ferramenta:

```python
for col in ["claude_code_success", "copilot_cli_success"]:
    tasks[col] = tasks[col].astype(str).str.lower() == "true"

cc_success = tasks["claude_code_success"].sum()
cp_success = tasks["copilot_cli_success"].sum()
total = len(tasks)

print(f"Claude Code:  {cc_success}/{total} = {cc_success/total*100:.0f}%")
print(f"Copilot CLI:  {cp_success}/{total} = {cp_success/total*100:.0f}%")

failed_cp = tasks[tasks["copilot_cli_success"] == False]
if len(failed_cp) > 0:
    print(f"\nCopilot CLI failures:")
    print(failed_cp[["task_id", "task_description", "category"]].to_string(index=False))
```

**Saída esperada:**

```
Claude Code:  10/10 = 100%
Copilot CLI:   9/10 =  90%

Copilot CLI failures:
 task_id                  task_description category
     T10 Debug a failing CI pipeline   devops
```

!!! tip "Insight"
    Claude Code completou todas as 10 tarefas com sucesso (100%). Copilot CLI completou 9 de 10 (90%), falhando apenas na T10 — depurar um pipeline de CI com falha, que requer contexto profundo sobre configuração de CI, variáveis de ambiente e sistemas de build.

---

## Etapa 4: Comparar Tempos de Conclusão

Analise a velocidade de conclusão de cada ferramenta:

```python
cc_avg = tasks["claude_code_time_sec"].mean()
cp_avg = tasks["copilot_cli_time_sec"].mean()
manual_avg = tasks["manual_time_sec"].mean()

print(f"Average completion time:")
print(f"  Claude Code:  {cc_avg:.1f}s")
print(f"  Copilot CLI:  {cp_avg:.1f}s")
print(f"  Manual:       {manual_avg:.1f}s")

print(f"\nSpeedup over manual:")
print(f"  Claude Code:  {manual_avg/cc_avg:.0f}x faster")
print(f"  Copilot CLI:  {manual_avg/cp_avg:.0f}x faster")
```

**Saída esperada:**

```
Average completion time:
  Claude Code:  20.5s
  Copilot CLI:  24.5s
  Manual:       1005.0s

Speedup over manual:
  Claude Code:  49x faster
  Copilot CLI:  41x faster
```

```python
print("\nPer-task comparison:")
for _, t in tasks.iterrows():
    faster = "Claude Code" if t["claude_code_time_sec"] < t["copilot_cli_time_sec"] else "Copilot CLI"
    print(f"  {t['task_id']} ({t['category']:>20}): CC={t['claude_code_time_sec']:>3}s  "
          f"CP={t['copilot_cli_time_sec']:>3}s  → {faster}")
```

!!! tip "Insight"
    Claude Code é mais rápido em média (20.5s vs 24.5s). A única tarefa onde Copilot CLI foi mais rápido é **T06 (git workflow)** — criar uma mensagem de commit convencional — provavelmente devido à integração mais próxima com o GitHub.

---

## Etapa 5: Analisar por Categoria de Tarefa

Compare o desempenho das ferramentas em diferentes tipos de tarefa:

```python
print("Performance by category:")
for _, row in tasks.iterrows():
    cc_status = "✅" if row["claude_code_success"] else "❌"
    cp_status = "✅" if row["copilot_cli_success"] else "❌"
    print(f"  {row['category']:>20}: CC {cc_status} ({row['claude_code_time_sec']:>3}s)  "
          f"CP {cp_status} ({row['copilot_cli_time_sec']:>3}s)  "
          f"Advantage: {row['tool_advantage']}")
```

**Saída esperada:**

```
  code_understanding: CC ✅ ( 8s)  CP ✅ (12s)  Advantage: 10x faster
     codebase_search: CC ✅ ( 5s)  CP ✅ ( 8s)  Advantage: 40x faster
     code_generation: CC ✅ (25s)  CP ✅ (30s)  Advantage: 20x faster
          debugging: CC ✅ (18s)  CP ✅ (22s)  Advantage: 45x faster
        refactoring: CC ✅ (35s)  CP ✅ (40s)  Advantage: 30x faster
       git_workflow: CC ✅ ( 4s)  CP ✅ ( 3s)  Advantage: 8x faster
        code_review: CC ✅ (15s)  CP ✅ (20s)  Advantage: 35x faster
        scaffolding: CC ✅ (45s)  CP ✅ (50s)  Advantage: 75x faster
          migration: CC ✅ (30s)  CP ✅ (35s)  Advantage: 55x faster
             devops: CC ✅ (20s)  CP ❌ (25s)  Advantage: 45x faster
```

Ambas as ferramentas fornecem **ganhos massivos de velocidade** em relação ao trabalho manual (8x a 75x mais rápido), com os maiores ganhos em tarefas de scaffolding e busca na base de código.

---

## Etapa 6: Fazendo uma Recomendação

Resuma a comparação:

```python
print("=== Tool Comparison Summary ===\n")
print(f"{'Metric':<30} {'Claude Code':>12} {'Copilot CLI':>12}")
print("-" * 56)
print(f"{'Success Rate':<30} {'100%':>12} {'90%':>12}")
print(f"{'Avg Time (s)':<30} {cc_avg:>12.1f} {cp_avg:>12.1f}")
print(f"{'Tasks Won (speed)':<30} {'9':>12} {'1':>12}")
print(f"{'Manual Speedup':<30} {f'{manual_avg/cc_avg:.0f}x':>12} {f'{manual_avg/cp_avg:.0f}x':>12}")
```

!!! tip "Recomendação"
    Ambas as ferramentas entregam ganhos excepcionais de produtividade. **Claude Code** se destaca neste benchmark com taxa de sucesso perfeita e tempos médios mais rápidos. **Copilot CLI** se sobressai em fluxos de trabalho git e oferece integração mais próxima com o GitHub. Para equipes já no ecossistema GitHub, Copilot CLI é uma escolha natural; para máxima confiabilidade em tarefas diversas, Claude Code é a opção mais forte.

---

## 🐛 Exercício de Correção de Bugs

O arquivo `lab-081/broken_tools.py` tem **3 bugs** nas funções de análise. Você consegue encontrar e corrigir todos?

Execute os auto-testes para ver quais falham:

```bash
python lab-081/broken_tools.py
```

Você deve ver **3 testes com falha**. Cada teste corresponde a um bug:

| Teste | O que verifica | Dica |
|-------|---------------|------|
| Teste 1 | Cálculo de speedup médio | Deve calcular o speedup a partir dos tempos do Claude Code, não do Copilot CLI |
| Teste 2 | Taxa de sucesso de ambas as ferramentas | Deve usar AND (`&`) e não OR (`|`) para "ambas tiveram sucesso" |
| Teste 3 | Detecção da ferramenta mais rápida | O operador de comparação está invertido |

Corrija todos os 3 bugs e execute novamente. Quando você ver `All passed!`, está pronto!

---

## 🧠 Verificação de Conhecimento

??? question "**Q1 (Múltipla Escolha):** O que distingue ferramentas de codificação agênticas dos copilots tradicionais baseados em IDE?"

    - A) Elas só funcionam com código Python
    - B) Elas operam no terminal, leem bases de código inteiras e executam tarefas de múltiplas etapas de forma autônoma
    - C) Elas requerem uma GPU para rodar localmente
    - D) Elas só sugerem completamentos de uma única linha

    ??? success "✅ Revelar Resposta"
        **Correto: B) Elas operam no terminal, leem bases de código inteiras e executam tarefas de múltiplas etapas de forma autônoma**

        Diferente dos copilots baseados em IDE que sugerem completamentos de código dentro de um editor, ferramentas de codificação agênticas como Claude Code e Copilot CLI rodam no terminal, analisam a estrutura completa do seu projeto e podem realizar tarefas complexas de múltiplas etapas — pesquisar bases de código, escrever testes, criar commits e depurar pipelines — tudo a partir de um único prompt em linguagem natural.

??? question "**Q2 (Múltipla Escolha):** Qual é a principal vantagem das ferramentas de codificação agênticas sobre o desenvolvimento manual?"

    - A) Elas produzem código sem bugs todas as vezes
    - B) Elas eliminam a necessidade de revisão de código
    - C) Elas reduzem drasticamente o tempo para tarefas comuns (frequentemente 10x–75x mais rápido)
    - D) Elas substituem a necessidade de controle de versão

    ??? success "✅ Revelar Resposta"
        **Correto: C) Elas reduzem drasticamente o tempo para tarefas comuns (frequentemente 10x–75x mais rápido)**

        O benchmark mostra acelerações variando de 8x (fluxos de trabalho git) a 75x (scaffolding) em comparação com a conclusão manual. Embora as ferramentas não produzam código perfeito todas as vezes e a revisão de código continue importante, a economia de tempo para tarefas rotineiras é substancial.

??? question "**Q3 (Execute o Laboratório):** Qual é a taxa de sucesso do Claude Code em todas as 10 tarefas?"

    Carregue [📥 `coding_tools_comparison.csv`](https://github.com/lcarli/AI-LearningHub/raw/main/docs/docs/en/labs/lab-081/coding_tools_comparison.csv) e conte `claude_code_success == True`.

    ??? success "✅ Revelar Resposta"
        **100% (10/10)**

        Claude Code completou com sucesso todas as 10 tarefas no benchmark, incluindo compreensão de código, geração, depuração, refatoração, fluxos de trabalho git, revisão de código, scaffolding, migração e tarefas de DevOps.

??? question "**Q4 (Execute o Laboratório):** Qual é a taxa de sucesso do Copilot CLI, e em qual tarefa ele falhou?"

    Conte `copilot_cli_success == True` e identifique a tarefa que falhou.

    ??? success "✅ Revelar Resposta"
        **90% (9/10) — falhou na T10 (Depurar um pipeline de CI com falha)**

        Copilot CLI teve sucesso em 9 de 10 tarefas. A única falha foi na T10 — depurar um pipeline de CI com falha — que requer contexto profundo sobre configuração de CI, variáveis de ambiente e interações do sistema de build.

??? question "**Q5 (Execute o Laboratório):** Qual ferramenta é a mais rápida no geral com base no tempo médio de conclusão?"

    Calcule `claude_code_time_sec.mean()` e `copilot_cli_time_sec.mean()`.

    ??? success "✅ Revelar Resposta"
        **Claude Code (20.5s média vs 24.5s média)**

        O tempo médio de conclusão do Claude Code é 20.5 segundos comparado com 24.5 segundos do Copilot CLI. Claude Code foi mais rápido em 9 de 10 tarefas; Copilot CLI foi mais rápido apenas na T06 (git workflow, 3s vs 4s).

---

## Resumo

| Tópico | O que Você Aprendeu |
|--------|---------------------|
| Ferramentas de Codificação Agênticas | Assistentes de IA baseados em terminal que leem bases de código e executam tarefas de múltiplas etapas |
| Claude Code | 100% de taxa de sucesso, 20.5s em média, mais forte em tarefas complexas |
| Copilot CLI | 90% de taxa de sucesso, 24.5s em média, se destaca em fluxos de trabalho git |
| Economia de Tempo | Ambas as ferramentas fornecem aceleração de 8x–75x sobre o desenvolvimento manual |
| Categorias de Tarefas | Ambas lidam bem com compreensão, geração, revisão e refatoração de código |
| Recomendação | Claude Code para confiabilidade; Copilot CLI para integração com GitHub |

---

## Próximos Passos

- **[Lab 082](lab-082-agent-guardrails.md)** — Agent Guardrails: NeMo & Azure Content Safety
- Experimente ambas as ferramentas na sua própria base de código para ver qual se adapta melhor ao seu fluxo de trabalho
