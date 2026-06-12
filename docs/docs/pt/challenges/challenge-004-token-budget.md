---
tags: [challenge, token-budget, cost, context, python, local]
---
# Desafio 004: Otimize um Orçamento de Tokens

<div class="lab-meta">
  <span><strong>Nível:</strong> <span class="level-badge level-200">L200</span></span>
  <span><strong>Tipo:</strong> Desafio</span>
  <span><strong>Tempo:</strong> ~60 min</span>
  <span><strong>💰 Custo:</strong> <span class="level-badge cost-free">Gratuito (local)</span></span>
</div>

## Cenário

A OutdoorGear tem um assistente de suporte que envia contexto demais para o modelo. Ele inclui texto jurídico longo e conteúdo de história da marca mesmo quando um resumo curto de política responderia à pergunta. A equipe quer prompts menores sem perder qualidade de resposta.

Sua tarefa é corrigir um otimizador local de orçamento de prompt que seleciona contexto compacto e relevante e mantém cada prompt abaixo de um limite rígido de tokens.

---

## Objetivo

Corrija `starter_token_budget.py` para que o otimizador selecione o documento de contexto certo para cada solicitação, evite contexto irrelevante, construa prompts compactos, reporte conformidade de orçamento e gere um código de validação.

Seu otimizador final deve:

- Estimar tokens de prompt de forma determinística
- Normalizar palavras-chave para correspondência lexical
- Preferir resumos concisos e relevantes a documentos longos e ruidosos
- Selecionar contexto dentro de um orçamento de tokens de contexto
- Construir prompts abaixo do orçamento total de cada solicitação
- Reportar documentos selecionados e conformidade de orçamento

---

## Arquivos Iniciais

Salve estes arquivos em uma pasta chamada `challenge-004/`:

| Arquivo | Finalidade | Download |
|---------|------------|----------|
| `context_docs.json` | Contexto de suporte compacto e verboso | [Download](https://github.com/lcarli/AI-LearningHub/raw/main/docs/docs/en/challenges/challenge-004/context_docs.json) |
| `requests.json` | Solicitações de suporte com orçamento | [Download](https://github.com/lcarli/AI-LearningHub/raw/main/docs/docs/en/challenges/challenge-004/requests.json) |
| `starter_token_budget.py` | Otimizador de orçamento quebrado | [Download](https://github.com/lcarli/AI-LearningHub/raw/main/docs/docs/en/challenges/challenge-004/starter_token_budget.py) |
| `test_token_budget.py` | Testes de aceite | [Download](https://github.com/lcarli/AI-LearningHub/raw/main/docs/docs/en/challenges/challenge-004/test_token_budget.py) |
| `validate_token_budget.py` | Gera o código final de conclusão | [Download](https://github.com/lcarli/AI-LearningHub/raw/main/docs/docs/en/challenges/challenge-004/validate_token_budget.py) |

---

## Briefing do Desafio

Você recebe documentos compactos, documentos verbosos, solicitações com orçamento e um otimizador quebrado. Não há walkthrough: decida como estimar tokens, ranquear contexto, selecionar evidência e construir prompts que fiquem dentro do orçamento.

---

## Restrições

- Use apenas a biblioteca padrão do Python em `starter_token_budget.py`.
- Não chame uma API de LLM.
- Não hardcode comportamento por ID de solicitação.
- Não inclua documentos irrelevantes só porque ainda há espaço.
- Mantenha a estrutura do prompt curta e fundamentada.

---

## Critérios de Aceite

Sua solução está completa quando:

- `python -m pytest test_token_budget.py` passa
- O documento conciso esperado é selecionado para cada solicitação
- Documentos verbosos ou irrelevantes não superam correspondências concisas
- Todo prompt fica dentro de `max_prompt_tokens`
- A avaliação reporta `within_budget is True`
- A avaliação reporta `all_prompts_under_budget is True`

---

## Validação

Quando sua implementação estiver pronta, execute:

```bash
python -m pytest test_token_budget.py
python validate_token_budget.py
```

Digite o código de conclusão impresso por `validate_token_budget.py`:

<div class="challenge-validator" data-answer="CH004-67CBEAD0">
  <input type="text" aria-label="Código de conclusão" placeholder="CH004-XXXXXXXX" />
  <button type="button">Validar</button>
  <p class="challenge-validator-result" aria-live="polite"></p>
</div>

---

## Dicas

??? tip "Dica 1 — A estimativa de tokens não precisa ser perfeita"
    Ela só precisa ser determinística e boa o suficiente para comparar tamanhos de prompt.

??? tip "Dica 2 — Relevância não basta"
    Um documento longo com as palavras certas pode ser menos útil que um resumo conciso com a mesma evidência.

??? tip "Dica 3 — Faça orçamento na seleção"
    É mais fácil ficar dentro do orçamento se você rejeitar contexto antes de construir o prompt final.

??? tip "Dica 4 — O template do prompt importa"
    Um template de instruções verboso pode consumir o orçamento que você está tentando economizar.

---

## Rubrica

| Área | Pontos | Como fica bom |
|------|:------:|---------------|
| Estimativa de tokens | 20 | Determinística, parecida com palavras e útil para orçamento |
| Ranking de contexto | 30 | Seleciona documentos concisos e relevantes |
| Construção do prompt | 25 | Fica fundamentado e dentro do orçamento |
| Avaliação | 15 | Reporta documentos selecionados e conformidade corretamente |
| Simplicidade | 10 | Lógica local determinística, sem over-engineering |

---

## Objetivos Extras

- Adicionar orçamentos separados para prompt de sistema, contexto e resposta
- Reportar economia de tokens versus baseline verboso
- Adicionar fallback quando nenhum documento cabe no orçamento
- Adicionar uma nova solicitação com orçamento mais apertado e atualizar localmente o payload do validador

---

## Labs Relacionados

- [Lab 038 — Otimização de Custos de IA](../labs/lab-038-cost-optimization.md)
- [Lab 071 — Cache de Contexto](../labs/lab-071-context-caching.md)
- [Lab 072 — Benchmark de Confiabilidade de Saídas Estruturadas](../labs/lab-072-structured-outputs.md)
