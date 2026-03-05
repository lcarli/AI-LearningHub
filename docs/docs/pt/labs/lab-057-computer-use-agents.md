---
tags: [computer-use, automation, anthropic, desktop, python, safety]
---
# Lab 057: Agentes de Uso de Computador — Automação de Desktop

<div class="lab-meta">
  <span><strong>Nível:</strong> <span class="level-badge level-300">L300</span></span>
  <span><strong>Caminho:</strong> <a href="../paths/pro-code/">⚙️ Pro Code</a></span>
  <span><strong>Tempo:</strong> ~90 min</span>
  <span><strong>💰 Custo:</strong> <span class="level-badge cost-free">Gratuito</span> — Usa dataset de benchmark; API da Anthropic opcional</span>
</div>

## O Que Você Vai Aprender

- O que são **agentes de uso de computador** — IA que interage com um desktop da mesma forma que um humano (captura de tela → raciocínio → clicar/digitar)
- O **loop captura de tela–ação**: o agente captura uma tela, identifica elementos da interface e executa ações de mouse/teclado
- Como executar agentes em um **sandbox Docker** para isolá-los do sistema host
- Projetar **proteções de segurança** — listas de domínios permitidos, prompts de confirmação de ação e limites de taxa
- Analisar **benchmarks de automação de desktop** para entender onde os agentes de uso de computador acertam e erram

## Introdução

A automação tradicional depende de APIs, scripts ou bots de RPA que interagem com interfaces estruturadas. Mas o que acontece quando a aplicação **não tem API**? Aplicações desktop legadas, terminais de mainframe e softwares thick-client frequentemente expõem nada além de uma interface gráfica.

**Agentes de uso de computador** resolvem isso operando o computador como um humano faria. O agente captura uma **tela** da tela atual, envia para um modelo de visão-linguagem (como a ferramenta `computer_20251124` da Anthropic), recebe uma ação estruturada (mover mouse, clicar, digitar texto), executa e repete. Este loop captura de tela→ação permite que o agente interaja com *qualquer* aplicação que tenha uma interface visual.

### O Cenário

Você é um **Engenheiro de Automação** na OutdoorGear Inc. A empresa depende de um sistema legado de gestão de inventário — uma aplicação thick-client Windows sem API e sem planos de modernização. A gerência quer automatizar tarefas repetitivas como preencher formulários de despesas, gerar relatórios e navegar pelo sistema ERP.

Seu trabalho é avaliar se agentes de uso de computador podem lidar com essas tarefas de forma confiável e segura, usando um dataset de benchmark de **10 tarefas de desktop e navegador**.

!!! info "Agente ao Vivo Não Necessário"
    Este lab analisa um **dataset de benchmark pré-gravado** de resultados de tarefas de uso de computador. Você não precisa de uma chave de API da Anthropic ou de um agente em execução — toda a análise é feita localmente com pandas. Se você tiver acesso à API, pode opcionalmente estender o lab para executar tarefas ao vivo.

## Pré-requisitos

| Requisito | Por quê |
|---|---|
| Python 3.10+ | Executar scripts de análise |
| Biblioteca `pandas` | Operações com DataFrame |
| (Opcional) Chave de API da Anthropic | Para experimentos ao vivo de uso de computador |

```bash
pip install pandas
```

---

!!! tip "Início Rápido com GitHub Codespaces"
    [![Open in GitHub Codespaces](https://github.com/codespaces/badge.svg)](https://codespaces.new/lcarli/AI-LearningHub?quickstart=1)

    Todas as dependências estão pré-instaladas no devcontainer.


## 📦 Arquivos de Apoio

!!! note "Baixe estes arquivos antes de iniciar o lab"
    Salve todos os arquivos em uma pasta `lab-057/` no seu diretório de trabalho.

| Arquivo | Descrição | Download |
|------|-------------|----------|
| `broken_safety.py` | Exercício de correção de bugs (3 bugs + auto-testes) | [📥 Download](https://github.com/lcarli/AI-LearningHub/raw/main/docs/docs/en/labs/lab-057/broken_safety.py) |
| `desktop_tasks.csv` | Dataset | [📥 Download](https://github.com/lcarli/AI-LearningHub/raw/main/docs/docs/en/labs/lab-057/desktop_tasks.csv) |

---

## Etapa 1: Entendendo o Uso de Computador

Agentes de uso de computador seguem um loop simples, mas poderoso:

```
┌─────────────┐     ┌──────────────┐     ┌──────────────┐
│  Screenshot  │────▶│  Vision LLM  │────▶│   Action     │
│  (pixels)    │     │  (reason)    │     │  (click/type)│
└─────────────┘     └──────────────┘     └──────────────┘
       ▲                                        │
       └────────────────────────────────────────┘
                    repeat until done
```

Os componentes principais:

| Componente | Descrição |
|-----------|-------------|
| **Captura de tela** | Captura a tela atual como uma imagem (PNG) |
| **Modelo de visão** | Analisa a captura de tela para identificar elementos da interface e decidir a próxima ação |
| **Executor de ações** | Traduz a saída do modelo em eventos de mouse/teclado no nível do SO |
| **Sandbox** | Container Docker ou VM que isola o agente do host |

A ferramenta `computer_20251124` da Anthropic fornece três capacidades:

1. **Captura de tela** — tira uma foto da tela atual
2. **Controle do mouse** — mover, clicar, duplo clique, arrastar
3. **Entrada de teclado** — digitar texto, pressionar combinações de teclas

!!! tip "Por Que Capturas de Tela?"
    Diferente do web scraping tradicional (que lê HTML/DOM), agentes de uso de computador veem a tela como *pixels*. Isso significa que eles podem interagir com qualquer interface visual — aplicações desktop, desktops remotos, emuladores de terminal, até jogos — sem precisar de acesso ao código subjacente ou ao DOM.

---

## Etapa 2: Carregar o Dataset de Benchmark

O dataset contém **10 tarefas** que um agente de uso de computador tentou, cobrindo cenários de desktop e navegador:

```python
import pandas as pd

tasks = pd.read_csv("lab-057/desktop_tasks.csv")
print(f"Total tasks: {len(tasks)}")
print(f"Task types: {sorted(tasks['app_type'].unique())}")
print(f"Difficulty levels: {sorted(tasks['difficulty'].unique())}")
print(f"\nDataset preview:")
print(tasks[["task_id", "task_description", "app_type", "completed", "safety_risk"]].to_string(index=False))
```

**Saída esperada:**

```
Total tasks: 10
Task types: ['browser', 'desktop']
Difficulty levels: ['easy', 'hard', 'medium']
```

| task_id | task_description | app_type | completed | safety_risk |
|---------|-----------------|----------|-----------|-------------|
| T01 | Abrir calculadora e calcular 15 × 23 | desktop | True | low |
| T02 | Criar um novo arquivo de texto no desktop | desktop | True | low |
| T03 | Abrir navegador e pesquisar botas de trilha | browser | True | low |
| ... | ... | ... | ... | ... |
| T10 | Navegar por um processo de checkout multi-etapas | browser | False | high |

---

## Etapa 3: Analisar Taxas de Conclusão

Calcule as taxas de conclusão geral e por dificuldade:

```python
completed = tasks["completed"].sum()
total = len(tasks)
rate = (completed / total) * 100
print(f"Completed: {completed}/{total}")
print(f"Completion rate: {rate:.0f}%")

print(f"\nBy difficulty:")
for diff in ["easy", "medium", "hard"]:
    subset = tasks[tasks["difficulty"] == diff]
    diff_rate = (subset["completed"].sum() / len(subset)) * 100
    print(f"  {diff}: {subset['completed'].sum()}/{len(subset)} = {diff_rate:.0f}%")
```

**Saída esperada:**

```
Completed: 7/10
Completion rate: 70%

By difficulty:
  easy: 2/2 = 100%
  medium: 4/4 = 100%
  hard: 1/4 = 25%
```

!!! tip "Insight"
    O agente lida com tarefas **fáceis e médias** de forma confiável (100%), mas tem dificuldade com **tarefas difíceis** (25%). Tarefas difíceis envolvem fluxos de trabalho multi-etapas, conteúdo dinâmico ou operações sensíveis à segurança — todos desafiadores para navegação baseada em capturas de tela.

---

## Etapa 4: Análise de Risco de Segurança

Identifique tarefas com alto risco de segurança:

```python
print("Safety risk distribution:")
print(tasks["safety_risk"].value_counts().sort_index())

high_risk = tasks[tasks["safety_risk"] == "high"]
print(f"\nHigh-risk tasks: {len(high_risk)}")
print(high_risk[["task_id", "task_description", "completed"]].to_string(index=False))
```

**Saída esperada:**

```
Safety risk distribution:
high      2
low       6
medium    2

High-risk tasks: 2
```

| task_id | task_description | completed |
|---------|-----------------|-----------|
| T08 | Fazer login em uma aplicação web usando credenciais | False |
| T10 | Navegar por um processo de checkout multi-etapas | False |

Ambas as tarefas de alto risco **falharam**, o que na verdade é um bom resultado — significa que o agente não executou com sucesso ações potencialmente perigosas sem proteções adequadas.

!!! warning "Por Que Estas São de Alto Risco"
    - **T08 (Login com credenciais)**: O agente precisaria ler senhas de um gerenciador de senhas — um risco de segurança significativo se o agente for comprometido ou o sandbox for violado.
    - **T10 (Processo de checkout)**: Completar uma compra com informações reais de pagamento poderia ter consequências financeiras se o agente cometer erros.

---

## Etapa 5: Comparação de Tarefas Desktop vs Navegador

Compare como o agente se sai em tarefas de desktop vs navegador:

```python
print("Performance by app type:")
for app in ["desktop", "browser"]:
    subset = tasks[tasks["app_type"] == app]
    rate = (subset["completed"].sum() / len(subset)) * 100
    avg_time = subset[subset["completed"] == True]["time_sec"].mean()
    avg_actions = subset[subset["completed"] == True]["actions"].mean()
    print(f"\n  {app.upper()}:")
    print(f"    Tasks: {len(subset)}")
    print(f"    Completed: {subset['completed'].sum()}/{len(subset)} ({rate:.0f}%)")
    print(f"    Avg time (completed): {avg_time:.1f}s")
    print(f"    Avg actions (completed): {avg_actions:.1f}")
```

**Saída esperada:**

```
Performance by app type:

  DESKTOP:
    Tasks: 5
    Completed: 4/5 (80%)
    Avg time (completed): 20.5s
    Avg actions (completed): 8.0

  BROWSER:
    Tasks: 5
    Completed: 3/5 (60%)
    Avg time (completed): 26.0s
    Avg actions (completed): 10.7
```

!!! tip "Insight"
    Tarefas de desktop têm uma taxa de sucesso maior (80% vs 60%) e requerem menos ações em média. Tarefas de navegador tendem a envolver mais conteúdo dinâmico e navegação complexa, tornando-as mais difíceis para agentes baseados em capturas de tela.

---

## Etapa 6: Projeto de Proteções de Segurança

Com base na análise de benchmark, projete proteções para implantação em produção:

### Proteções Recomendadas

| Proteção | Propósito | Implementação |
|-----------|---------|----------------|
| **Lista de domínios permitidos** | Restringir quais aplicações/sites o agente pode acessar | Arquivo de configuração listando nomes de apps e URLs aprovados |
| **Confirmação de ação** | Exigir aprovação humana para ações de alto risco | Prompt antes de cliques em botões como "Enviar", "Comprar", "Excluir" |
| **Limite de tempo da sessão** | Evitar agentes descontrolados | Encerrar o agente após N minutos de inatividade |
| **Registro de capturas de tela** | Trilha de auditoria de cada ação | Salvar cada captura de tela com timestamp e ação executada |
| **Isolamento de credenciais** | Nunca expor senhas ao agente | Usar variáveis de ambiente ou referências de cofre, nunca senhas visíveis na tela |

### Matriz de Decisão de Proteções

```python
print("Guardrail recommendations by risk level:")
for _, task in tasks.iterrows():
    guardrails = []
    if task["safety_risk"] == "high":
        guardrails = ["domain_allowlist", "action_confirmation", "human_review"]
    elif task["safety_risk"] == "medium":
        guardrails = ["domain_allowlist", "screenshot_logging"]
    else:
        guardrails = ["screenshot_logging"]
    print(f"  {task['task_id']} ({task['safety_risk']}): {', '.join(guardrails)}")
```

!!! warning "Sandbox Docker é Essencial"
    **Nunca execute um agente de uso de computador na sua máquina host.** Sempre use um container Docker ou VM. Se o agente interpretar mal uma captura de tela e clicar em "Excluir Tudo" em vez de "Selecionar Tudo", o dano fica contido no sandbox. A implementação de referência da Anthropic usa um container Docker com um display virtual (Xvfb) especificamente por esse motivo.

---

## 🐛 Exercício de Correção de Bugs

O arquivo `lab-057/broken_safety.py` tem **3 bugs** nas funções de análise de segurança. Você consegue encontrar e corrigir todos?

Execute os auto-testes para ver quais falham:

```bash
python lab-057/broken_safety.py
```

Você deve ver **3 testes falhando**. Cada teste corresponde a um bug:

| Teste | O que verifica | Dica |
|------|---------------|------|
| Teste 1 | Cálculo da taxa de conclusão | O denominador deve ser o total de tarefas, não as tarefas concluídas |
| Teste 2 | Contagem de tarefas de alto risco | Deve verificar `"high"`, não `"medium"` |
| Teste 3 | Tempo médio para tarefas concluídas | Deve filtrar para tarefas concluídas antes de calcular a média |

Corrija todos os 3 bugs e execute novamente. Quando você vir `🎉 All 3 tests passed`, está pronto!

---


## 🧠 Verificação de Conhecimento

??? question "**Q1 (Múltipla Escolha):** Quais capacidades a ferramenta `computer_20251124` da Anthropic fornece?"

    - A) Apenas entrada de teclado para digitar comandos
    - B) Captura de tela, controle do mouse e entrada de teclado
    - C) Acesso direto ao DOM e análise de HTML
    - D) Integração de API com aplicações desktop

    ??? success "✅ Revelar Resposta"
        **Correta: B) Captura de tela, controle do mouse e entrada de teclado**

        A ferramenta `computer_20251124` fornece três capacidades principais: (1) captura de telas da tela atual, (2) controle do mouse (mover, clicar, arrastar) e (3) envio de entrada de teclado (digitar texto, pressionar combinações de teclas). Ela *não* acessa o DOM ou APIs de aplicações — opera puramente através da interface visual.

??? question "**Q2 (Múltipla Escolha):** Qual é o principal propósito de executar um agente de uso de computador dentro de um sandbox Docker?"

    - A) Melhorar a resolução das capturas de tela do agente
    - B) Reduzir custos de API agrupando requisições
    - C) Isolar o agente do sistema host e conter danos potenciais
    - D) Permitir que o agente execute múltiplas tarefas em paralelo

    ??? success "✅ Revelar Resposta"
        **Correta: C) Isolar o agente do sistema host e conter danos potenciais**

        Um sandbox Docker (ou VM) cria uma barreira entre o agente e seu sistema real. Se o agente interpretar mal uma captura de tela e executar uma ação não intencional — como excluir arquivos ou clicar no botão errado — o dano fica contido dentro do sandbox e não afeta sua máquina host, arquivos ou contas.

??? question "**Q3 (Execute o Lab):** Qual é a taxa geral de conclusão de tarefas?"

    Carregue [📥 `desktop_tasks.csv`](https://github.com/lcarli/AI-LearningHub/raw/main/docs/docs/en/labs/lab-057/desktop_tasks.csv) e calcule `completed.sum() / total`.

    ??? success "✅ Revelar Resposta"
        **70%**

        7 de 10 tarefas foram concluídas com sucesso. As 3 tarefas que falharam (T07, T08, T10) eram todas de dificuldade **difícil** — o agente teve dificuldade com fluxos de trabalho multi-etapas complexos e operações sensíveis à segurança.

??? question "**Q4 (Execute o Lab):** Quantas tarefas de alto risco existem no dataset?"

    Filtre tarefas onde `safety_risk == "high"` e conte-as.

    ??? success "✅ Revelar Resposta"
        **2**

        As tarefas T08 (Fazer login em uma aplicação web usando credenciais de um gerenciador de senhas) e T10 (Navegar por um processo de checkout multi-etapas em um site de e-commerce) são classificadas como alto risco. Ambas envolvem operações sensíveis — manuseio de credenciais e transações financeiras — onde erros do agente poderiam ter consequências sérias.

??? question "**Q5 (Execute o Lab):** Qual é o número médio de ações apenas para tarefas concluídas?"

    Filtre para `completed == True`, depois calcule `actions.mean()`.

    ??? success "✅ Revelar Resposta"
        **≈ 9.1**

        Tarefas concluídas: T01(5) + T02(7) + T03(6) + T04(12) + T05(9) + T06(14) + T09(11) = **64 ações** em **7 tarefas**. Média = 64 ÷ 7 ≈ **9,14 ações por tarefa concluída**.

---

## Resumo

| Tópico | O Que Você Aprendeu |
|-------|-----------------|
| Conceito de Uso de Computador | Loop captura de tela→ação: capturar tela, raciocinar com LLM de visão, executar mouse/teclado |
| Análise de Benchmark | 70% de taxa de conclusão; tarefas fáceis/médias confiáveis, tarefas difíceis desafiadoras |
| Riscos de Segurança | Tarefas de alto risco (credenciais, pagamentos) requerem proteções extras |
| Desktop vs Navegador | Tarefas de desktop tiveram maior sucesso (80%) que tarefas de navegador (60%) |
| Projeto de Proteções | Listas de domínios permitidos, confirmação de ação, sandbox Docker, isolamento de credenciais |
| Sandbox Docker | Camada de isolamento essencial — nunca execute agentes de uso de computador no seu host |

---

## Próximos Passos

- **[Lab 058](lab-058-browser-automation-cua.md)** — Agentes de Automação de Navegador com OpenAI CUA
- Explore a [implementação de referência de uso de computador](https://docs.anthropic.com/en/docs/agents-and-tools/computer-use) da Anthropic para configuração de agente ao vivo
