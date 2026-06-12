---
tags: [challenge, local-ai, agent, tools, rag, python]
---
# Desafio 008: Construa um Agente 100% Local

<div class="lab-meta">
  <span><strong>Nível:</strong> <span class="level-badge level-200">L200</span></span>
  <span><strong>Tipo:</strong> Desafio</span>
  <span><strong>Tempo:</strong> ~75 min</span>
  <span><strong>💰 Custo:</strong> <span class="level-badge cost-free">Gratuito (local)</span></span>
</div>

## Cenário

A OutdoorGear quer um pequeno agente de suporte que funcione sem Azure, GitHub Models, LLMs hospedados ou chamadas de rede. Ele deve classificar uma solicitação, usar ferramentas locais sobre dados locais e retornar uma resposta fundamentada com trace.

Sua tarefa é finalizar o agente 100% local e provar que ele lida com busca de produtos, consulta de política e recomendação de bundle sem configuração de nuvem.

---

## Objetivo

Corrija `starter_local_agent.py` para que o agente local roteie solicitações corretamente, use apenas dados locais, retorne respostas úteis, reporte nenhum uso de nuvem e gere um código de validação.

Seu agente local final deve:

- Não exigir configuração de nuvem
- Classificar três intents suportadas
- Buscar produtos localmente
- Consultar texto de política localmente
- Montar um bundle de camping dentro do orçamento
- Retornar resposta, trace, intent e `uses_cloud: False`

---

## Arquivos Iniciais

Salve estes arquivos em uma pasta chamada `challenge-008/`:

| Arquivo | Finalidade | Download |
|---------|------------|----------|
| `local_data.json` | Dados locais de produtos e políticas | [Download](https://github.com/lcarli/AI-LearningHub/raw/main/docs/docs/en/challenges/challenge-008/local_data.json) |
| `eval_requests.json` | Solicitações de avaliação | [Download](https://github.com/lcarli/AI-LearningHub/raw/main/docs/docs/en/challenges/challenge-008/eval_requests.json) |
| `starter_local_agent.py` | Agente local quebrado | [Download](https://github.com/lcarli/AI-LearningHub/raw/main/docs/docs/en/challenges/challenge-008/starter_local_agent.py) |
| `test_local_agent.py` | Testes de aceite | [Download](https://github.com/lcarli/AI-LearningHub/raw/main/docs/docs/en/challenges/challenge-008/test_local_agent.py) |
| `validate_local_agent.py` | Gera o código final de conclusão | [Download](https://github.com/lcarli/AI-LearningHub/raw/main/docs/docs/en/challenges/challenge-008/validate_local_agent.py) |

---

## Briefing do Desafio

Você recebe dados locais de produtos/políticas, solicitações de avaliação e um agente local quebrado. Não há walkthrough: decida como rotear intents, chamar ferramentas locais, compor respostas e provar que nenhuma dependência de nuvem é necessária.

---

## Restrições

- Use apenas a biblioteca padrão do Python em `starter_local_agent.py`.
- Não chame rede, modelo hospedado ou API de nuvem.
- Não hardcode respostas por ID de solicitação.
- Preserve os nomes públicos das funções usados pelos testes.
- Mantenha traces úteis para mostrar qual ferramenta local foi executada.

---

## Critérios de Aceite

Sua solução está completa quando:

- `python -m pytest test_local_agent.py` passa
- Busca de produto retorna `RainShell Pro Jacket`
- Consulta de política retorna a política de devolução de 60 dias
- Recomendação de bundle inclui os três itens esperados de camping dentro do orçamento
- O trace registra intent e execução de ferramenta
- `uses_cloud` é `False`

---

## Validação

Quando sua implementação estiver pronta, execute:

```bash
python -m pytest test_local_agent.py
python validate_local_agent.py
```

Digite o código de conclusão impresso por `validate_local_agent.py`:

<div class="challenge-validator" data-answer="CH008-A1B101A9">
  <input type="text" aria-label="Código de conclusão" placeholder="CH008-XXXXXXXX" />
  <button type="button">Validar</button>
  <p class="challenge-validator-result" aria-live="polite"></p>
</div>

---

## Dicas

??? tip "Dica 1 — Local-only é requisito"
    Um agente local ainda pode ser útil se roteamento de intent e ferramentas forem determinísticos.

??? tip "Dica 2 — Mantenha o roteamento estreito"
    As solicitações de fixture são propositalmente limitadas a busca de produto, consulta de política e recomendação de bundle.

??? tip "Dica 3 — Trace a ferramenta, não só a resposta"
    Um trace ajuda a provar que o agente tomou uma decisão e usou uma ferramenta local.

---

## Rubrica

| Área | Pontos | Como fica bom |
|------|:------:|---------------|
| Comportamento local-only | 25 | Nenhuma dependência de nuvem ou rede |
| Roteamento de intent | 25 | Três tipos de solicitação classificados corretamente |
| Saídas das ferramentas | 25 | Respostas de produto, política e bundle corretas |
| Rastreabilidade | 15 | Trace mostra intent e ferramenta local selecionada |
| Simplicidade | 10 | Implementação local determinística |

---

## Labs Relacionados

- [Lab 015 — Ollama LLMs Locais](../labs/lab-015-ollama-local-llms.md)
- [Lab 078 — Foundry Local](../labs/lab-078-foundry-local.md)
- [Lab 020 — Servidor MCP em Python](../labs/lab-020-mcp-server-python.md)
