---
tags: [github-copilot, free, vscode]
---
# Lab 016: GitHub Copilot Agent Mode

<div class="lab-meta">
  <span><strong>Nível:</strong> <span class="level-badge level-100">L100</span></span>
  <span><strong>Trilha:</strong> <a href="../paths/copilot/">🤖 GitHub Copilot</a></span>
  <span><strong>Tempo:</strong> ~30 min</span>
  <span><strong>💰 Custo:</strong> <span class="level-badge cost-github">GitHub Free</span> — Conta GitHub gratuita (o plano gratuito inclui o agent mode)</span>
</div>

## O que você vai aprender

- O que torna o **agent mode** diferente do Copilot Chat convencional
- Como ativar e usar o agent mode no VS Code
- Como o agente lê sua base de código, planeja e executa tarefas em múltiplas etapas
- Como conectar **servidores MCP** para expandir as capacidades do agente
- Boas práticas e limitações

---

## Introdução

O GitHub Copilot no VS Code possui três modos:

| Modo | O que faz |
|------|-----------|
| **Ask** | Responde perguntas sobre código; somente leitura |
| **Edit** | Faz alterações nos arquivos que você especificar |
| **Agent** ⭐ | Explora autonomamente sua base de código, executa comandos, usa ferramentas e conclui tarefas em múltiplas etapas |

O **Agent mode** é o mais novo e mais poderoso. Você descreve um objetivo, e o Copilot age como um desenvolvedor júnior: ele lê arquivos, escreve código, executa testes e itera até concluir — pedindo sua aprovação em pontos-chave de decisão.

!!! info "Disponível no VS Code 1.99+"
    O Agent mode requer VS Code 1.99 ou posterior e a extensão GitHub Copilot. Verifique se há atualizações caso você não veja o seletor de modo.

---

## Configuração de Pré-requisitos

1. **VS Code 1.99+** com a extensão GitHub Copilot instalada
2. **Conta GitHub gratuita** com Copilot habilitado ([github.com/features/copilot](https://github.com/features/copilot))
3. Um projeto para trabalhar (usaremos um projeto Python simples)

---

!!! tip "Início Rápido com GitHub Codespaces"
    [![Open in GitHub Codespaces](https://github.com/codespaces/badge.svg)](https://codespaces.new/lcarli/AI-LearningHub?quickstart=1)

    Todas as dependências já estão pré-instaladas no devcontainer.


## 📦 Arquivos de Apoio

!!! note "Baixe estes arquivos antes de iniciar o laboratório"
    Salve todos os arquivos em uma pasta `lab-016/` no seu diretório de trabalho.

| Arquivo | Descrição | Download |
|---------|-----------|----------|
| `outdoorgear_api.py` | Script Python | [📥 Download](https://github.com/lcarli/AI-LearningHub/raw/main/docs/docs/en/labs/lab-016/outdoorgear_api.py) |

---

## Exercício do Laboratório

### Etapa 1: Ativar o agent mode

1. Abra o painel do Copilot Chat (`Ctrl+Shift+I`)
2. Procure o seletor de modo na parte superior da entrada do chat
3. Selecione **"Agent"**

Você vai notar que a entrada muda — agora é possível descrever objetivos, não apenas fazer perguntas.

---

### Etapa 2: O Projeto Quebrado — Corrija com Agent Mode 🐛

Este exercício oferece um **projeto Python realmente quebrado** para corrigir usando o agent mode. O objetivo é ver como o agente lê arquivos, identifica problemas e os corrige — passo a passo.

**Baixe o projeto:**
```bash
cd AI-LearningHub/docs/docs/en/labs/lab-016
```

Ou copie o arquivo [📥 `outdoorgear_api.py`](https://github.com/lcarli/AI-LearningHub/raw/main/docs/docs/en/labs/lab-016/outdoorgear_api.py) abaixo:

```python title="lab-016/outdoorgear_api.py — 5 bugs, 1 funcionalidade ausente, sem testes"
--8<-- "labs/lab-016/outdoorgear_api.py"
```

**Abra a pasta no VS Code** (importante — o agente precisa ver o projeto inteiro):
```bash
code docs/docs/en/labs/lab-016/
```

---

### Fase 1: Deixe o agente encontrar e corrigir os bugs

Mude para o **Agent mode** e digite exatamente isto:

```
Fix all the bugs in outdoorgear_api.py so that the basic tests 
at the bottom of the file pass when I run: python outdoorgear_api.py

Don't fix the "Test 7" failure yet — that requires a missing function.
```

Observe o que o agente faz:

1. 🔍 Ele **lê o arquivo** sem que você precise colar nada
2. 🐛 Ele **identifica cada bug** e explica por que está errado
3. ✏️ Ele **propõe correções** e pede sua aprovação
4. ▶️ Ele **executa o arquivo** para verificar se a correção funcionou

Após aceitar, execute a verificação:
```bash
python outdoorgear_api.py
```
Os testes 1–6 devem passar. O teste 7 vai falhar (isso é esperado — a função está ausente).

!!! tip "Se o agente travar"
    Tente ser mais específico: "Run python outdoorgear_api.py and show me the error output, then fix the remaining bug"

---

### Fase 2: Adicionar a funcionalidade ausente

Agora peça ao agente para implementar a função `search_by_price_range` que está faltando:

```
Implement the search_by_price_range(min_price, max_price) function 
that is referenced in Test 7. 
It should return active products in that price range, sorted by price ascending.
Then run python outdoorgear_api.py to verify all 7 tests pass.
```

O agente deve:
1. Ler o código existente para entender as estruturas de dados
2. Implementar a função
3. Executar os testes para verificar

---

### Fase 3: Escrever um conjunto de testes

Agora peça ao agente para criar testes adequados:

```
Create a tests/ folder with a file test_outdoorgear_api.py.
Write pytest tests that cover:
- get_all_products() with include_inactive=True and False
- get_product_by_id() for valid and invalid IDs
- add_to_cart() including the stock check
- calculate_cart_total() with multiple items
- apply_promo_code() with valid and invalid codes
- place_order() end-to-end

Run pytest to make sure all tests pass.
```

Observe o agente:
- Criar a pasta `tests/`
- Escrever testes abrangentes usando fixtures do pytest
- Executar `pytest` no terminal
- Corrigir quaisquer falhas de teste encontradas

---

### Fase 4: Melhorar a qualidade do código

```
Add type hints to all public functions in outdoorgear_api.py.
Add Google-style docstrings to each function.
Don't change any logic.
```

---

### Etapa 3: Exploração da base de código

Tente pedir ao agente para analisar o que ele acabou de criar:

```
Give me a summary of the outdoorgear_api.py module:
1. What it does
2. All public functions and their signatures
3. Any edge cases not currently handled
```

O agente lê toda a base de código e sintetiza uma resposta coerente — sem que você precise colar nenhum código.

---

### Etapa 4: Conectar um servidor MCP (bônus)

O Agent mode suporta servidores MCP. Configure o VS Code para usar o servidor MCP do [Lab 020](lab-020-mcp-server-python.md):

**`.vscode/mcp.json`:**
```json
{
  "servers": {
    "outdoorgear-products": {
      "type": "stdio",
      "command": "python",
      "args": ["server.py"],
      "cwd": "${workspaceFolder}"
    }
  }
}
```

Em seguida, pergunte no agent mode:
```
What camping products do we have in stock? Use the outdoorgear-products MCP tool.
```

### Etapa 5: Instruções personalizadas

Crie `.github/copilot-instructions.md` para fazer o agente sempre seguir as convenções do seu projeto:

```markdown
# Copilot Instructions

## Project
Python API project for OutdoorGear Inc.

## Code Style
- Use type hints on all functions
- Docstrings follow Google style  
- Tests use pytest with fixtures, no unittest
- All prices rounded to 2 decimal places

## Never
- Use print() for logging
- Hardcode product data outside CATALOG
- Skip ValueError validation on public functions
```

---

## Agent Mode vs. Edit Mode: Quando Usar Cada Um

| Use o Edit mode quando | Use o Agent mode quando |
|------------------------|-------------------------|
| Você sabe exatamente o que mudar | Você tem um objetivo, mas não um plano |
| Edições simples e direcionadas | Tarefas em múltiplos arquivos e múltiplas etapas |
| Você quer controle total de cada edição | Você quer que o agente descubra sozinho |
| Correções rápidas, refatorações | Depuração, adição de funcionalidades, escrita de testes |

---

## O que o Agente Fez (Por Trás dos Bastidores)

```
Your request: "Fix all bugs"
        │
        ▼
[read_file] outdoorgear_api.py        ← agent reads without you pasting
        │
        ▼
[analysis] Found 5 bugs:
  Bug 1: line 45 — = instead of ==
  Bug 2: line 57 — =+ instead of +=
  ...
        │
        ▼
[replace_in_file] × 5 targeted fixes  ← surgical edits, not rewriting whole file
        │
        ▼
[run_terminal] python outdoorgear_api.py
        │
        ▼
✅ All 6 tests pass
```

---

## Resumo

- ✅ **Lê sua base de código** — sem copiar/colar código no chat
- ✅ **Execução em múltiplas etapas** — planeja e conclui tarefas complexas
- ✅ **Acesso ao terminal** — executa testes, verifica correções
- ✅ **Integração com MCP** — conecte ferramentas personalizadas
- ✅ **Aprovações a cada etapa** — você mantém o controle

---

## Próximos Passos

- **Construa um servidor MCP para estender o agent mode:** → [Lab 020 — MCP Server in Python](lab-020-mcp-server-python.md)
- **Construa um Chat Participant do VS Code (@agent personalizado):** → [Lab 025 — VS Code Chat Participant](lab-025-vscode-chat-participant.md)
