---
tags: [challenge, agent-loop, tools, python, local]
---
# Desafio 001: Construa um Loop de Agente do Zero

<div class="lab-meta">
  <span><strong>Nível:</strong> <span class="level-badge level-100">L100</span></span>
  <span><strong>Tipo:</strong> Desafio</span>
  <span><strong>Tempo:</strong> ~60 min</span>
  <span><strong>💰 Custo:</strong> <span class="level-badge cost-free">Gratuito (local)</span></span>
</div>

## Cenário

A OutdoorGear quer um pequeno agente assistente de produtos que raciocine sobre um catálogo local. A equipe **não** quer usar Semantic Kernel, LangGraph, AutoGen ou qualquer LLM hospedado ainda. Primeiro, ela quer provar que você entende o loop central:

> perceber → decidir → agir → observar → responder

Sua tarefa é finalizar um pequeno loop de agente em Python que escolhe ferramentas, executa essas ferramentas, armazena observações e produz uma resposta final fundamentada.

---

## Objetivo

Implemente a lógica faltante em `starter_agent_loop.py` para que o assistente local de produtos conclua as duas solicitações-alvo e gere um código de validação.

Ao final, seu agente deve conseguir:

- Buscar produtos usando categoria, palavras de consulta, orçamento e filtro de estoque
- Consultar detalhes de produto por SKU
- Recomendar um pequeno bundle de camping em estoque dentro de um orçamento
- Executar um loop que chama exatamente uma ferramenta antes de responder para requisições suportadas
- Retornar um trace mostrando o que o agente fez

---

## Arquivos Iniciais

Salve estes arquivos em uma pasta chamada `challenge-001/`:

| Arquivo | Finalidade | Download |
|---------|------------|----------|
| `products.json` | Catálogo mock da OutdoorGear | [Download](https://github.com/lcarli/AI-LearningHub/raw/main/docs/docs/en/challenges/challenge-001/products.json) |
| `starter_agent_loop.py` | Implementação inicial com TODOs | [Download](https://github.com/lcarli/AI-LearningHub/raw/main/docs/docs/en/challenges/challenge-001/starter_agent_loop.py) |
| `test_agent_loop.py` | Testes de aceite | [Download](https://github.com/lcarli/AI-LearningHub/raw/main/docs/docs/en/challenges/challenge-001/test_agent_loop.py) |
| `validate_agent_loop.py` | Gera o código final de conclusão | [Download](https://github.com/lcarli/AI-LearningHub/raw/main/docs/docs/en/challenges/challenge-001/validate_agent_loop.py) |

---

## Briefing do Desafio

Você recebe um catálogo de produtos, uma implementação inicial e testes. Não há walkthrough: decida como interpretar a solicitação, escolher uma ferramenta, executá-la, armazenar a observação e produzir a resposta final.

---

## Restrições

- Use apenas a biblioteca padrão do Python em `starter_agent_loop.py`.
- Não chame uma API de LLM.
- Não use um framework de agentes.
- Mantenha o loop legível: o objetivo é entender o fluxo de controle.
- Preserve o formato de retorno de `run_agent()`:

```python
{
    "final_answer": "...",
    "trace": [
        {"step": 1, "type": "tool", "tool": "...", "arguments": {...}},
        {"step": 2, "type": "final"}
    ]
}
```

---

## Critérios de Aceite

Sua solução está completa quando:

- `python -m pytest test_agent_loop.py` passa
- A solicitação de jaqueta chama `search_products` antes de responder
- A solicitação de bundle de camping chama `recommend_bundle` antes de responder
- A resposta final inclui nomes de produtos, preços e uma justificativa curta
- Produtos fora de estoque não são recomendados
- O loop para com uma resposta final antes de `max_steps`

---

## Validação

Quando sua implementação estiver pronta, execute:

```bash
python -m pytest test_agent_loop.py
python validate_agent_loop.py
```

Digite o código de conclusão impresso por `validate_agent_loop.py`:

<div class="challenge-validator" data-answer="CH001-4707D4F5">
  <input type="text" aria-label="Código de conclusão" placeholder="CH001-XXXXXXXX" />
  <button type="button">Validar</button>
  <p class="challenge-validator-result" aria-live="polite"></p>
</div>

---

## Dicas

??? tip "Dica 1 — Comece pelas ferramentas"
    O loop fica mais fácil de raciocinar quando cada ferramenta tem contrato claro e saída determinística.

??? tip "Dica 2 — Mantenha o parsing simples"
    Você não precisa de NLP avançado. As solicitações-alvo são propositalmente estreitas.

??? tip "Dica 3 — Use observações como memória"
    `state.observations` é a memória de curto prazo do loop. Depois que uma ferramenta roda, a resposta final deve se basear na observação mais recente, não no catálogo original.

??? tip "Dica 4 — Decida de forma determinística"
    Uma boa solução toma a mesma decisão toda vez para o mesmo estado.

---

## Rubrica

| Área | Pontos | Como fica bom |
|------|:------:|---------------|
| Correção das ferramentas | 30 | Filtros, consulta por SKU e seleção de bundle estão corretos |
| Loop de agente | 30 | Fluxo claro perceber → decidir → agir → observar → responder |
| Resposta fundamentada | 20 | A resposta usa observações das ferramentas e cita produtos concretos |
| Rastreabilidade | 10 | O trace mostra chamada de ferramenta e etapa final |
| Simplicidade | 10 | Sem framework, API ou over-engineering desnecessários |

---

## Objetivos Extras

- Adicionar suporte para "comparar dois SKUs"
- Adicionar uma resposta de erro quando nenhum produto corresponder
- Adicionar uma segunda chamada de ferramenta antes da resposta final para pedidos ambíguos
- Criar um parser de `max_price` que aceite `$150`, `150 dollars` e `under 150`

---

## Labs Relacionados

- [Lab 001 — O que são Agentes de IA?](../labs/lab-001-what-are-ai-agents.md)
- [Lab 018 — Chamada de Funções e Uso de Ferramentas](../labs/lab-018-function-calling.md)
- [Lab 020 — Servidor MCP em Python](../labs/lab-020-mcp-server-python.md)
