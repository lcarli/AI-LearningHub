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

Faça todos os testes passarem implementando as funções faltantes em `starter_agent_loop.py`.

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

---

## Configuração

```bash
cd challenge-001
python -m pip install pytest
python -m pytest test_agent_loop.py
```

Os testes devem falhar no início. Sua tarefa é fazê-los passar.

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

## Dicas

??? tip "Dica 1 — Comece pelas ferramentas"
    Implemente `search_products`, `get_product_details` e `recommend_bundle` antes de mexer no loop. Um loop de agente só é útil se as ferramentas forem confiáveis.

??? tip "Dica 2 — Mantenha o parsing simples"
    Você não precisa de NLP avançado. Checagens simples de palavras como `jacket`, `camping`, `under` e `SKU` são suficientes para este desafio.

??? tip "Dica 3 — Use observações como memória"
    `state.observations` é a memória de curto prazo do loop. Depois que uma ferramenta roda, a resposta final deve se basear na observação mais recente, não no catálogo original.

??? tip "Dica 4 — Decida de forma determinística"
    Se ainda não há observações, escolha uma ferramenta. Se já existe pelo menos uma observação útil, escolha `final`.

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
