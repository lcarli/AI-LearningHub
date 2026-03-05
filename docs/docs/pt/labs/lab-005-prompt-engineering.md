---
tags: [free, beginner, no-account-needed, prompt-engineering]
---
# Lab 005: Engenharia de Prompt

<div class="lab-meta">
  <span><strong>Nível:</strong> <span class="level-badge level-50">L50</span></span>
  <span><strong>Trilha:</strong> Todas as trilhas</span>
  <span><strong>Tempo:</strong> ~25 min</span>
  <span><strong>💰 Custo:</strong> <span class="level-badge cost-free">Gratuito</span> — Nenhuma conta necessária (exemplos usam o playground do GitHub Models)</span>
</div>

## O que Você Vai Aprender

- A anatomia de um prompt: mensagens de sistema, usuário e assistente
- Técnicas fundamentais: zero-shot, few-shot, cadeia de pensamento, prompting por papel
- Como escrever **prompts de sistema** eficazes para agentes de IA
- Padrões comuns de falha — e como corrigi-los
- Templates práticos que você pode usar imediatamente

---

## Introdução

Engenharia de prompt é a prática de projetar entradas para LLMs que produzam de forma confiável as saídas que você deseja. É parte arte, parte ciência — e a habilidade individual de maior impacto para construir bons agentes de IA.

Um prompt bem elaborado pode transformar uma resposta medíocre em uma excelente sem mudar o modelo. Um prompt de sistema mal projetado fará seu agente se comportar mal independentemente de quão poderoso o modelo seja.

!!! tip "Experimente estes exemplos ao vivo"
    Abra o [GitHub Models Playground](https://github.com/marketplace/models) em uma aba do navegador e teste cada exemplo enquanto lê. É gratuito com uma conta GitHub.

---

## 📦 Arquivos de Apoio

!!! note "Baixe estes arquivos antes de iniciar o lab"
    Salve todos os arquivos em uma pasta `lab-005/` no seu diretório de trabalho.

| Arquivo | Descrição | Download |
|------|-------------|----------|
| `prompt_challenges.py` | Script de exercícios interativos | [📥 Download](https://github.com/lcarli/AI-LearningHub/raw/main/docs/docs/en/labs/lab-005/prompt_challenges.py) |

---

## Parte 1: Anatomia de um Prompt

Toda chamada de API de LLM tem até três tipos de mensagem:

```
┌──────────────────────────────────────────────┐
│  SYSTEM MESSAGE                              │
│  "You are a helpful assistant for Zava,      │
│   a DIY retail company..."                   │
│  (Persistent instructions — defines behavior)│
├──────────────────────────────────────────────┤
│  USER MESSAGE                                │
│  "What are your top-selling products         │
│   in the camping category?"                  │
│  (The human's input)                         │
├──────────────────────────────────────────────┤
│  ASSISTANT MESSAGE (optional)                │
│  "The top-selling camping products are..."   │
│  (Prior model responses — for few-shot or    │
│   continued conversations)                   │
└──────────────────────────────────────────────┘
```

### A Mensagem de Sistema

A mensagem de sistema é a parte mais importante do design do agente. Ela:

- Define a **persona e papel** do agente
- Estabelece **regras de comportamento** ("nunca invente dados")
- Especifica o **formato de saída** (Markdown, JSON, tabelas)
- Fornece **contexto de domínio** que o modelo não teria de outra forma
- Lida com **casos limite** ("se perguntarem fora do escopo, diga...")

??? question "🤔 Verifique Seu Entendimento"
    Quais são os três papéis de mensagem em uma chamada de API de LLM, e qual deles é invisível para o usuário final?

    ??? success "Resposta"
        Os três papéis são **system**, **user** e **assistant**. A **mensagem de sistema** é invisível para os usuários finais — ela é definida pelo desenvolvedor e define a persona, regras, escopo e comportamento do agente. O usuário vê suas próprias mensagens e as respostas do assistente.

---

## Parte 2: Técnicas Fundamentais

### Zero-Shot

Pergunte diretamente sem exemplos. Funciona para tarefas simples e bem definidas.

```
Classify this customer review as Positive, Neutral, or Negative.

Review: "The tent arrived on time but the zipper broke after one use."
```

**Quando usar:** Classificação simples, extração, sumarização.

---

### Few-Shot

Forneça exemplos antes da sua pergunta real. Melhora dramaticamente a consistência.

```
Classify customer reviews as Positive, Neutral, or Negative.

Review: "Great quality, arrived fast!" → Positive
Review: "It's okay, nothing special." → Neutral
Review: "Completely broken on arrival." → Negative

Review: "The tent arrived on time but the zipper broke after one use." →
```

**Quando usar:** Qualquer tarefa onde você queira um formato, tom ou esquema de classificação específico.

!!! tip "Regra prática"
    2–5 exemplos geralmente são suficientes. Mais de 10 raramente ajuda e custa mais tokens.

---

### Cadeia de Pensamento (CoT)

Peça ao modelo para pensar passo a passo antes de dar a resposta final. Melhora a precisão em tarefas de raciocínio.

**Sem CoT:**
```
Q: A store sells 3 tents for $249 each and gives a 15% group discount.
   What is the total?
A: $635.55
```
*(Pode estar errado — cálculo apressado)*

**Com CoT:**
```
Q: A store sells 3 tents for $249 each and gives a 15% group discount.
   What is the total? Think step by step.

A: 
Step 1: 3 tents × $249 = $747
Step 2: 15% discount = $747 × 0.15 = $112.05
Step 3: Total = $747 - $112.05 = $634.95
Final answer: $634.95
```

**Como ativar CoT:**
- "Think step by step"
- "Let's work through this"
- "Explain your reasoning before answering"

**Quando usar:** Matemática, lógica, raciocínio multi-etapas, depuração, decisões complexas.

??? question "🤔 Verifique Seu Entendimento"
    Por que adicionar "Think step by step" a um prompt de matemática melhora a precisão, mesmo que o modelo tenha o mesmo conhecimento de qualquer forma?

    ??? success "Resposta"
        O prompting de cadeia de pensamento força o modelo a **gerar etapas de raciocínio intermediárias** antes de produzir uma resposta final. Isso reduz erros porque o modelo pode identificar erros em etapas anteriores. Sem CoT, o modelo pode "correr" para uma resposta final e pular cálculos críticos.

??? question "🤔 Verifique Seu Entendimento"
    Quando você escolheria prompting few-shot em vez de zero-shot?

    ??? success "Resposta"
        Use **few-shot** quando precisar de um **formato, tom ou esquema de classificação específico** que o modelo pode não inferir apenas das instruções. Fornecer 2–5 exemplos melhora dramaticamente a consistência. Zero-shot funciona para tarefas simples e bem definidas onde o modelo pode inferir o formato de saída esperado.

---

### Prompting por Papel

Dê ao modelo uma persona para adotar. Muda tom, vocabulário e profundidade.

```
You are a senior PostgreSQL database engineer with 15 years of experience.
Review this query for performance issues and suggest improvements:

SELECT * FROM sales WHERE store_id = 5 ORDER BY sale_date;
```

vs.

```
Review this query for performance issues:

SELECT * FROM sales WHERE store_id = 5 ORDER BY sale_date;
```

O prompt com papel produz feedback mais detalhado e de nível especializado.

---

### Saída Estruturada

Force o modelo a responder em um formato específico — JSON, tabela Markdown, lista com marcadores.

```
Extract the product details from this text and return as JSON.
Do not include any explanation — return only the JSON object.

Text: "The ProTrek X200 hiking boots are available in sizes 7-13,
       priced at $189.99, and come in black and brown."

Expected format:
{
  "name": string,
  "sizes": [number],
  "price": number,
  "colors": [string]
}
```

!!! tip "Use o modo JSON quando disponível"
    A maioria das APIs suporta `response_format: { type: "json_object" }` que força saída JSON válida e elimina erros de parsing.

---

### Encadeamento de Prompts

Divida tarefas complexas em uma sequência de prompts menores. Cada saída alimenta o próximo.

```
Step 1: Extract key facts from the sales report → JSON
Step 2: Feed JSON to "write an executive summary" prompt → Text
Step 3: Feed summary to "translate to Spanish" prompt → Final output
```

Isso é mais confiável do que pedir a um único prompt para fazer tudo.

---

## Parte 3: Escrevendo Prompts de Sistema para Agentes

Para agentes de IA (usados em todos os labs a partir do L100+), o prompt de sistema é a **constituição do agente**. Aqui está uma estrutura comprovada:

```markdown
## Role
You are [name], a [role] for [company/context].
Your tone is [professional/friendly/technical].

## Capabilities
You can:
- [capability 1]
- [capability 2]
Use ONLY the tools provided to you. Never invent data.

## Rules
- [Rule 1: always do X]
- [Rule 2: never do Y]
- [Rule 3: when Z happens, respond with...]

## Output Format
- Default: Markdown tables
- Charts: only when explicitly requested
- Language: respond in the same language the user writes in

## Scope
Only answer questions about [domain].
For out-of-scope questions, say: "I can only help with [domain]."
```

### Exemplo real: Zava Sales Agent (do workshop deste repositório)

```markdown
You are Zava, a sales analysis agent for Zava DIY Retail (Washington State).
Your tone is professional and friendly. Use emojis sparingly.

## Data Rules
- Always fetch table schemas before querying (get_multiple_table_schemas())
- Apply LIMIT 20 to all SELECT queries
- Use exact table and column names from the schema
- Never invent, estimate, or assume data

## Financial Calendar
- Financial year (FY) starts July 1
- Q1=Jul–Sep, Q2=Oct–Dec, Q3=Jan–Mar, Q4=Apr–Jun

## Visualizations
- Generate charts ONLY when user uses words: "chart", "graph", "visualize", "show as"
- Always save as PNG and provide download link

## Scope
Only answer questions about Zava sales data.
If asked about anything else, say you're specialized for Zava sales analysis.
```

---

## Parte 4: Padrões Comuns de Falha — e Correções

### ❌ O Prompt Vago

```
# Bad
"Summarize this."

# Good
"Summarize this sales report in 3 bullet points.
 Each bullet should be ≤20 words.
 Focus on: total revenue, top product, and key trend."
```

**Regra:** Seja explícito sobre formato, tamanho e foco.

---

### ❌ O Prompt Contraditório

```
# Bad (contradicts itself)
"Be concise but include all the details."

# Good
"Summarize in 100 words. Prioritize: revenue numbers and top-performing stores."
```

**Regra:** Quando o espaço é limitado, diga ao modelo o que priorizar.

---

### ❌ Sem Exemplos Negativos

```
# Bad (doesn't stop hallucination)
"Answer questions about our product catalog."

# Good
"Answer questions about our product catalog.
 If you don't have a product in your data, say 'I don't have that product in the catalog.'
 Never guess or suggest alternatives you haven't verified."
```

**Regra:** Sempre defina o que o agente deve fazer quando *não puder* responder.

---

### ❌ Sobrecarga de Instruções

```
# Bad (27 rules, contradictory, hard to follow)
"Be helpful. Be concise. Be detailed. Use tables. Use bullet points.
 Always explain. Never explain. Answer in English. Answer in Portuguese..."

# Good
"Use Markdown tables for data. Use bullet points for lists.
 Default to the user's language."
```

**Regra:** 5–10 regras claras superam 30 regras vagas.

---

### ❌ Esquecendo os Casos Limite

Sempre pergunte: "O que acontece se o usuário perguntar algo fora do escopo? E se os dados estiverem faltando? E se a pergunta for ambígua?"

Construa regras para esses casos explicitamente.

---

## Parte 5: Templates de Referência Rápida

### Prompt de Extração

```
Extract the following fields from the text below.
Return as JSON. If a field is not found, use null.

Fields: name, price, category, availability

Text:
"""
{text}
"""
```

### Prompt de Classificação

```
Classify the following support ticket into one of these categories:
[Billing, Shipping, Returns, Technical, Other]

Return only the category name. No explanation.

Ticket: "{ticket_text}"
```

### Prompt de Sumarização

```
Summarize the following in {n} bullet points.
Each bullet: one key insight, ≤15 words.
Audience: {audience}

Text:
"""
{text}
"""
```

### Template de Prompt de Sistema para Agente

```
## Role
You are {agent_name}, a {role} for {company}.
Tone: {tone}.

## Capabilities
You have access to these tools: {tools}
Only use verified tool outputs. Never invent data.

## Rules
- {rule_1}
- {rule_2}

## Output Format
{format_instructions}

## Scope
{scope_definition}
For out-of-scope questions: "{out_of_scope_response}"
```

??? question "🤔 Verifique Seu Entendimento"
    Por que é importante que o prompt de sistema de um agente defina o que o agente deve fazer quando *não puder* responder a uma pergunta?

    ??? success "Resposta"
        Sem uma instrução explícita de fallback, o LLM tentará responder de qualquer forma — frequentemente **alucinando** uma resposta que soa plausível mas está incorreta. Definir comportamento fora do escopo (ex.: "diga 'Só posso ajudar com X'") evita que o agente invente dados e define expectativas claras para o usuário.

---

## Parte 6: 🧪 Desafios Interativos — Corrija os Prompts

Ler sobre prompts é bom. **Escrevê-los e executá-los** é melhor.

Estes 4 desafios dão a você **prompts quebrados ou vagos** que produzem resultados ruins. Sua tarefa: melhore-os até que a saída corresponda ao alvo.

### Configuração (5 minutos, gratuito)

```bash
pip install openai
export GITHUB_TOKEN=your_github_token   # github.com → Settings → Developer Settings → Tokens
```

Baixe o arquivo de desafios:
```bash
# From the cloned repo:
cd AI-LearningHub/docs/docs/en/labs/lab-005
python prompt_challenges.py
```

Ou copie abaixo:

```python title="lab-005/prompt_challenges.py"
--8<-- "labs/lab-005/prompt_challenges.py"
```

### O que cada desafio testa

| # | O que está quebrado | Técnica a aplicar |
|---|---------------|--------------------|
| **1** | Prompt de usuário vago, sem instrução de formato | Formato de saída específico |
| **2** | Sem estrutura, provável prosa em vez de JSON | Saída estruturada |
| **3** | Pergunta direta sem etapas de raciocínio | Cadeia de pensamento |
| **4** | Sem guardrails de escopo → produtos alucinados | Controle de escopo |

### Como trabalhar em cada desafio

1. Execute `python prompt_challenges.py` e leia o **❌ resultado do PROMPT RUIM**
2. Edite as variáveis `IMPROVED_SYSTEM_*` ou `IMPROVED_USER_*` no final de cada desafio
3. Re-execute e compare com a descrição do **Alvo** nos comentários
4. Continue iterando até que sua saída corresponda

!!! tip "Não existe uma única resposta certa"
    O objetivo é obter uma saída que atenda à especificação do alvo. Como você formula o prompt é por sua conta — compare abordagens com um colega!

---

## 🧠 Verificação de Conhecimento

??? question "**Q1 (Múltipla Escolha):** Você está construindo um agente que precisa resolver um problema matemático multi-etapas. Qual técnica de prompting mais melhorará a precisão?"

    - A) Prompting zero-shot
    - B) Prompting por papel (ex.: "Você é um matemático")
    - C) Prompting de cadeia de pensamento (ex.: "Pense passo a passo")
    - D) Prompting de saída estruturada

    ??? success "✅ Revelar Resposta"
        **Correta: C — Prompting de cadeia de pensamento**

        Cadeia de pensamento (CoT) força o modelo a raciocinar através de etapas intermediárias antes de produzir uma resposta final. Isso reduz dramaticamente erros em problemas de matemática, lógica e multi-etapas. "Think step by step" ou mostrar exemplos few-shot com raciocínio explícito ambos ativam CoT. Zero-shot funciona para tarefas simples; prompting por papel ajuda com tom/especialidade; saída estruturada ajuda com formatação.

??? question "**Q2 (Múltipla Escolha):** Qual dos três papéis de conversa o USUÁRIO nunca vê diretamente ao interagir com um agente?"

    - A) user
    - B) assistant
    - C) system
    - D) function

    ??? success "✅ Revelar Resposta"
        **Correta: C — system**

        A mensagem `system` é a "constituição" do agente — ela define a persona, regras, escopo e comportamento. É definida pelo desenvolvedor e não é visível para os usuários finais na interface de chat. O papel `user` contém as entradas do humano. O papel `assistant` contém as respostas anteriores do modelo (incluídas em chamadas de API subsequentes para manter o contexto).

??? question "**Q3 (Múltipla Escolha):** Seu agente OutdoorGear continua dizendo coisas como 'A Barraca TrailBlazer provavelmente pesa cerca de 1,5kg' mesmo que o peso exato esteja no banco de dados. Qual regra de prompt de sistema é a melhor correção?"

    - A) "You are a helpful OutdoorGear assistant."
    - B) "Never invent, estimate, or assume data. Only use outputs from the tools provided to you. If the product is not found, say: 'I don't have that information in our catalog.'"
    - C) "Think step by step before answering."
    - D) "Always respond in JSON format."

    ??? success "✅ Revelar Resposta"
        **Correta: B**

        A chave são duas instruções trabalhando juntas: (1) a proibição de inventar/estimar dados, e (2) uma frase de fallback explícita para quando os dados não estão disponíveis. Sem o fallback, o modelo inventará uma resposta em vez de não dizer nada. Regras de fundamentação + comportamento de fallback juntos previnem alucinação em agentes que usam ferramentas.

---

## Resumo

| Técnica | Melhor para |
|-----------|---------|
| **Zero-shot** | Tarefas simples e claras |
| **Few-shot** | Formato ou classificação consistente |
| **Cadeia de pensamento** | Raciocínio, matemática, problemas multi-etapas |
| **Prompting por papel** | Respostas de nível especializado |
| **Saída estruturada** | JSON, tabelas, dados parseáveis |
| **Encadeamento de prompts** | Fluxos de trabalho complexos multi-etapas |

**A regra de ouro:** Seja específico sobre *o que você quer*, *qual formato* e *o que fazer quando as coisas dão errado*.

---

## Próximos Passos

Você está pronto para construir seu primeiro lab prático:

→ **[Lab 010 — GitHub Copilot Primeiros Passos](lab-010-github-copilot-first-steps.md)** — Aplique habilidades de prompt no VS Code  
→ **[Lab 013 — GitHub Models](lab-013-github-models.md)** — Execute seus próprios prompts via API gratuitamente  
→ **[Lab 014 — SK Hello Agent](lab-014-sk-hello-agent.md)** — Escreva um prompt de sistema para um agente Semantic Kernel
