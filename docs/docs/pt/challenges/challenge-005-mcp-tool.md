---
tags: [challenge, mcp, tools, schema, privacy, python, local]
---
# Desafio 005: Construa uma Ferramenta Segura no Estilo MCP

<div class="lab-meta">
  <span><strong>Nível:</strong> <span class="level-badge level-200">L200</span></span>
  <span><strong>Tipo:</strong> Desafio</span>
  <span><strong>Tempo:</strong> ~60 min</span>
  <span><strong>💰 Custo:</strong> <span class="level-badge cost-free">Gratuito (local)</span></span>
</div>

## Cenário

A OutdoorGear quer expor uma ferramenta de consulta de status de pedido para agentes por meio de um contrato no estilo MCP. A ferramenta atual vaza e-mails de clientes, aceita argumentos extras e tem um schema incompleto.

Sua tarefa é projetar um contrato local de ferramenta e um caminho de execução seguros antes que a ferramenta seja exposta a qualquer runtime de agente.

---

## Objetivo

Corrija `starter_mcp_tool.py` para que o manifesto da ferramenta seja válido, a validação de argumentos seja rígida, chamadas inválidas sejam bloqueadas, consultas de pedido redijam PII e o validador gere um código de conclusão.

Sua ferramenta final deve:

- Definir um manifesto claro de `get_order_status` com schema de entrada
- Aceitar apenas `order_id`
- Rejeitar ferramentas desconhecidas e argumentos extras
- Retornar dados seguros de status do pedido sem `customer_email`
- Reportar métricas de contrato corretamente

---

## Arquivos Iniciais

Salve estes arquivos em uma pasta chamada `challenge-005/`:

| Arquivo | Finalidade | Download |
|---------|------------|----------|
| `orders.json` | Pedidos mock da OutdoorGear | [Download](https://github.com/lcarli/AI-LearningHub/raw/main/docs/docs/en/challenges/challenge-005/orders.json) |
| `tool_requests.json` | Chamadas de ferramenta válidas e inválidas | [Download](https://github.com/lcarli/AI-LearningHub/raw/main/docs/docs/en/challenges/challenge-005/tool_requests.json) |
| `starter_mcp_tool.py` | Implementação quebrada de ferramenta estilo MCP | [Download](https://github.com/lcarli/AI-LearningHub/raw/main/docs/docs/en/challenges/challenge-005/starter_mcp_tool.py) |
| `test_mcp_tool.py` | Testes de aceite | [Download](https://github.com/lcarli/AI-LearningHub/raw/main/docs/docs/en/challenges/challenge-005/test_mcp_tool.py) |
| `validate_mcp_tool.py` | Gera o código final de conclusão | [Download](https://github.com/lcarli/AI-LearningHub/raw/main/docs/docs/en/challenges/challenge-005/validate_mcp_tool.py) |

---

## Briefing do Desafio

Você recebe pedidos mock, chamadas de ferramenta válidas e inválidas e uma implementação quebrada. Não há walkthrough: decida como descrever a ferramenta, validar argumentos, despachar execução e redigir campos sensíveis.

---

## Restrições

- Use apenas a biblioteca padrão do Python em `starter_mcp_tool.py`.
- Não exponha `customer_email` nos resultados da ferramenta.
- Não aceite argumentos extras.
- Não execute ferramentas desconhecidas.
- Preserve os nomes públicos das funções usados pelos testes.

---

## Critérios de Aceite

Sua solução está completa quando:

- `python -m pytest test_mcp_tool.py` passa
- O manifesto inclui um `inputSchema` válido
- Apenas `order_id` é aceito como entrada
- Ferramentas desconhecidas e argumentos extras com PII são bloqueados
- Chamadas bem-sucedidas retornam `delivered` e `processing`
- Resultados da ferramenta são redigidos

---

## Validação

Quando sua implementação estiver pronta, execute:

```bash
python -m pytest test_mcp_tool.py
python validate_mcp_tool.py
```

Digite o código de conclusão impresso por `validate_mcp_tool.py`:

<div class="challenge-validator" data-answer="CH005-CD4DDCBC">
  <input type="text" aria-label="Código de conclusão" placeholder="CH005-XXXXXXXX" />
  <button type="button">Validar</button>
  <p class="challenge-validator-result" aria-live="polite"></p>
</div>

---

## Dicas

??? tip "Dica 1 — O schema é uma fronteira de segurança"
    Um schema frouxo convida agentes a enviar campos que a ferramenta nunca deveria receber.

??? tip "Dica 2 — Redação pertence perto da ferramenta"
    Não dependa do agente para esconder campos sensíveis depois que a ferramenta os retorna.

??? tip "Dica 3 — Falhe fechado"
    Ferramentas desconhecidas, campos obrigatórios ausentes e argumentos extras devem gerar erro.

---

## Rubrica

| Área | Pontos | Como fica bom |
|------|:------:|---------------|
| Contrato do manifesto | 25 | Nome, descrição, schema e campos obrigatórios claros |
| Validação de argumentos | 25 | Campos ausentes e extras são rejeitados |
| Execução segura | 25 | Status correto do pedido com PII redigida |
| Tratamento de erros | 15 | Chamadas desconhecidas ou inválidas falham fechadas |
| Simplicidade | 10 | Código de ferramenta pequeno e determinístico |

---

## Labs Relacionados

- [Lab 012 — O que é MCP?](../labs/lab-012-what-is-mcp.md)
- [Lab 020 — Servidor MCP em Python](../labs/lab-020-mcp-server-python.md)
- [Lab 064 — Protegendo MCP com APIM](../labs/lab-064-securing-mcp-apim.md)
