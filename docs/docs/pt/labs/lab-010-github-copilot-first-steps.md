---
tags: [github-copilot, free, foundations]
---
# Lab 010: GitHub Copilot — Primeiros Passos

<div class="lab-meta">
  <span><strong>Nível:</strong> <span class="level-badge level-100">L100</span></span>
  <span><strong>Trilha:</strong> <a href="../paths/copilot/">🤖 GitHub Copilot</a></span>
  <span><strong>Tempo:</strong> ~45 min</span>
  <span><strong>💰 Custo:</strong> <span class="level-badge cost-github">GitHub Free</span> — Plano gratuito (2.000 completações + 50 chats/mês)</span>
</div>

## O Que Você Vai Aprender

- Usar **completação de código inline** para escrever código a partir de comentários
- Usar **Copilot Chat `/fix`** para encontrar e entender bugs reais
- Usar **Copilot Edits** para refatorar um arquivo inteiro com linguagem natural
- Usar **chat inline** para estender código sem sair do editor
- Escrever prompts que geram melhores resultados

Este laboratório usa **exercícios práticos** — você abrirá arquivos com bugs reais e código incompleto, e então usará o Copilot para corrigir e estendê-los.

---

## Pré-requisitos

### 1. Ativar o GitHub Copilot Free

1. Acesse [github.com/features/copilot](https://github.com/features/copilot) → **"Start for free"**
2. Faça login e siga o assistente de configuração

!!! tip "Estudantes recebem o Copilot Pro gratuitamente"
    → [GitHub Student Developer Pack](https://education.github.com/pack)

### 2. Instalar o VS Code + extensão do Copilot

1. Instale o [VS Code](https://code.visualstudio.com)
2. Extensões (`Ctrl+Shift+X`) → pesquise **"GitHub Copilot"** → Instale ambos:
   - **GitHub Copilot** (completações)
   - **GitHub Copilot Chat** (painel de chat)
3. Faça login quando solicitado — você verá o ícone do Copilot na barra de status

### 3. Baixar os arquivos de exercício

Clone ou baixe os arquivos de exercício para este laboratório:

```bash
git clone https://github.com/lcarli/AI-LearningHub.git
cd AI-LearningHub/docs/docs/en/labs/lab-010
```

Ou copie cada arquivo diretamente das seções abaixo.

---

!!! tip "Início Rápido com GitHub Codespaces"
    [![Open in GitHub Codespaces](https://github.com/codespaces/badge.svg)](https://codespaces.new/lcarli/AI-LearningHub?quickstart=1)

    Todas as dependências estão pré-instaladas no devcontainer.


## 📦 Arquivos de Apoio

!!! note "Baixe estes arquivos antes de iniciar o laboratório"
    Salve todos os arquivos em uma pasta `lab-010/` no seu diretório de trabalho.

| Arquivo | Descrição | Download |
|---------|-----------|----------|
| `exercise1_fibonacci.py` | Script de exercício interativo | [📥 Download](https://github.com/lcarli/AI-LearningHub/raw/main/docs/docs/en/labs/lab-010/exercise1_fibonacci.py) |
| `exercise2_shopping_cart.py` | Script de exercício interativo | [📥 Download](https://github.com/lcarli/AI-LearningHub/raw/main/docs/docs/en/labs/lab-010/exercise2_shopping_cart.py) |
| `exercise3_product_search.py` | Script de exercício interativo | [📥 Download](https://github.com/lcarli/AI-LearningHub/raw/main/docs/docs/en/labs/lab-010/exercise3_product_search.py) |
| `exercise4_refactor_me.py` | Script de exercício interativo | [📥 Download](https://github.com/lcarli/AI-LearningHub/raw/main/docs/docs/en/labs/lab-010/exercise4_refactor_me.py) |

---

## Exercício 1 — Completação Inline: Escreva Código a Partir de Comentários

**Objetivo:** Aprender como o Copilot completa código enquanto você digita.

Crie um novo arquivo `practice.py` e digite cada comentário abaixo. Após cada comentário, **pare de digitar** e aguarde a sugestão do Copilot. Pressione `Tab` para aceitar, você pode continuar pressionando tab até o Copilot parar de sugerir mais completações.

!!! tip "Não vamos executar este código, então não se preocupe com erros de sintaxe ou imports faltando — apenas foque nas sugestões que o Copilot oferece com base nos comentários."

```python
# Function that takes a list of prices and returns the average:

# Function that reads a CSV file and returns rows as a list of dicts:

# Async function that fetches JSON from a URL using httpx:

# Class OutdoorProduct with name, price, category attributes and a discount() method:
```

!!! tip "Atalhos de teclado"
    | Tecla | Ação |
    |-------|------|
    | `Tab` | Aceitar sugestão |
    | `Esc` | Descartar |
    | `Alt+]` / `Alt+[` | Próxima / sugestão anterior |
    | `Ctrl+Enter` | Abrir painel com todas as sugestões |

**Experimente prompts melhores e piores:**

| ❌ Vago | ✅ Específico |
|---------|-------------|
| `# sort this` | `# Sort list of dicts by 'price' descending, then 'name' ascending` |
| `# connect to db` | `# Connect to PostgreSQL using asyncpg, return a connection pool` |
| `# handle error` | `# Retry 3 times with exponential backoff if requests.Timeout is raised` |

---

## Exercício 2 — Copilot `/fix`: Caça aos Bugs 🐛

**Objetivo:** Usar o Copilot Chat para encontrar, entender e corrigir bugs reais.

### Arquivo: [📥 `exercise1_fibonacci.py`](https://github.com/lcarli/AI-LearningHub/raw/main/docs/docs/en/labs/lab-010/exercise1_fibonacci.py)

```python title="exercise1_fibonacci.py — 3 bugs escondidos"
--8<-- "labs/lab-010/exercise1_fibonacci.py"
```

**Passos:**

1. Copie o código acima em um novo arquivo (ou abra-o dos exercícios baixados)
2. Abra o **Copilot Chat** (`Ctrl+Shift+I`)
3. Selecione **todo o código** (`Ctrl+A`)
4. Digite: `/fix`

O Copilot deve identificar todos os 3 bugs e explicar cada um. Antes de aceitar, **leia a explicação** — entender *por que* o código estava errado é o objetivo.

**Saída esperada após a correção:**
```python
fibonacci(0)  # → []
fibonacci(1)  # → [0]
fibonacci(8)  # → [0, 1, 1, 2, 3, 5, 8, 13]
```

Execute `python exercise1_fibonacci.py` — você deverá ver: `✅ All tests passed!`

---

### Arquivo: [📥 `exercise2_shopping_cart.py`](https://github.com/lcarli/AI-LearningHub/raw/main/docs/docs/en/labs/lab-010/exercise2_shopping_cart.py)

```python title="exercise2_shopping_cart.py — 4 bugs escondidos"
--8<-- "labs/lab-010/exercise2_shopping_cart.py"
```

Este arquivo tem **4 bugs** na classe `ShoppingCart`. Desta vez, antes de usar `/fix`:

1. **Tente identificar os bugs primeiro** — gaste 2 minutos lendo o código
2. Depois use o Copilot Chat: selecione tudo → `/fix`
3. O Copilot encontrou bugs que você não percebeu?

**Peça ao Copilot para explicar um bug em detalhes:**
```
Why is iterating with "for item in self.items" wrong here? What does it actually iterate over?
```

**Saída esperada após a correção:**
```
TrailBlazer X200 x2 @ $189.99 = $379.98
Summit Pro Tent x1 @ $349.00 = $349.00

Total: $656.08
Unique items: 2
✅ All tests passed!
```

---

## Exercício 3 — Chat Inline: Corrigir + Estender

**Objetivo:** Corrigir bugs E adicionar uma nova funcionalidade usando o chat inline (`Ctrl+I`).

### Arquivo: [📥 `exercise3_product_search.py`](https://github.com/lcarli/AI-LearningHub/raw/main/docs/docs/en/labs/lab-010/exercise3_product_search.py)

```python title="exercise3_product_search.py — 2 bugs + 1 funcionalidade faltando"
--8<-- "labs/lab-010/exercise3_product_search.py"
```

**Parte A — Corrigir (2 bugs):**

1. Abra o arquivo no VS Code
2. Selecione tudo (`Ctrl+A`) → Copilot Chat → `/fix`
3. Verifique: `python exercise3_product_search.py` — os testes 1–4 devem passar

**Parte B — Estender (1 funcionalidade faltando):**

O arquivo menciona uma função `sort_by_price()` que ainda não existe.

1. Posicione o cursor no final do arquivo (antes da seção de testes)
2. Pressione `Ctrl+I` (chat inline)
3. Digite exatamente:
   ```
   Add a sort_by_price(products, ascending=True) function that returns
   the products list sorted by price
   ```
4. Revise a sugestão e pressione **Aceitar** (`Ctrl+Enter`)
5. Execute os testes novamente — todos os 5 devem passar agora

---

## Exercício 4 — Copilot Edits: Refatorar um Arquivo Inteiro

**Objetivo:** Usar o Copilot Edits para melhorar a qualidade do código com instruções em linguagem natural — sem alterar o comportamento.

### Arquivo: [📥 `exercise4_refactor_me.py`](https://github.com/lcarli/AI-LearningHub/raw/main/docs/docs/en/labs/lab-010/exercise4_refactor_me.py)

```python title="exercise4_refactor_me.py — funciona, mas precisa de melhorias"
--8<-- "labs/lab-010/exercise4_refactor_me.py"
```

Este código **funciona corretamente** mas é difícil de ler e manter. Use o **Copilot Edits** para melhorá-lo passo a passo:

1. Abra o painel do Copilot Edits: `Ctrl+Shift+I` → clique em **"Open Copilot Edits"** (ícone de lápis)
2. Clique em **"Add Files"** e adicione `exercise4_refactor_me.py`
3. Execute cada um destes prompts **um de cada vez**, revisando as alterações antes de prosseguir:

**Prompt 1:**
```
Add type hints to all function parameters and return values
```

**Prompt 2:**
```
Add docstrings following Google style to every function
```

**Prompt 3:**
```
Refactor calculate_shipping to use early return instead of nested if/else
```

**Prompt 4:**
```
Add input validation: raise ValueError if price or quantity is negative
```

Após cada prompt, verifique se o teste no final ainda passa:
```bash
python exercise4_refactor_me.py
# Deve continuar exibindo: ✅ Refactoring complete — behavior unchanged!
```

!!! warning "Não aceite tudo cegamente"
    Às vezes o Copilot adiciona complexidade extra. Se uma sugestão tornar o código mais difícil de ler, pressione **Descartar** (`Ctrl+Backspace`) e reformule.

---

## Bônus: Peça ao Copilot para explicar, não apenas corrigir

Use estes prompts em qualquer um dos arquivos de exercício para aprofundar seu entendimento:

```
/explain
```
```
What tests should I write for this function? Generate them.
```
```
What edge cases does this code not handle?
```
```
Is there a more Pythonic way to write this?
```

---

## O Que Você Praticou

| Funcionalidade do Copilot | Exercício | Caso de uso |
|---------------------------|-----------|-------------|
| Completação inline | Exercício 1 | Escrever código novo a partir de comentários |
| Chat `/fix` | Exercício 2 | Entender e corrigir bugs |
| Chat inline `Ctrl+I` | Exercício 3 | Corrigir + estender no local |
| Copilot Edits | Exercício 4 | Refatorar arquivos inteiros |

---

## Próximos Passos

- **Construa um agente no-code para o Teams:** → [Lab 011 — Copilot Studio](lab-011-copilot-studio-first-agent.md)
- **Use o Agent Mode para construir uma funcionalidade completa:** → [Lab 016 — Copilot Agent Mode](lab-016-copilot-agent-mode.md)
- **Use LLMs gratuitos no seu código:** → [Lab 013 — GitHub Models](lab-013-github-models.md)