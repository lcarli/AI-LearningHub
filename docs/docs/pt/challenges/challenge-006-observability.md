---
tags: [challenge, observability, incident, tracing, python, local]
---
# Desafio 006: Investigue um Incidente de Observabilidade de Agente

<div class="lab-meta">
  <span><strong>Nível:</strong> <span class="level-badge level-300">L300</span></span>
  <span><strong>Tipo:</strong> Desafio</span>
  <span><strong>Tempo:</strong> ~60 min</span>
  <span><strong>💰 Custo:</strong> <span class="level-badge cost-free">Gratuito (local)</span></span>
</div>

## Cenário

O agente de suporte da OutdoorGear teve um pico de latência e uma requisição falhou. Você recebe uma pequena exportação de traces com spans raiz do agente e spans filhos de ferramentas/LLM. O analisador atual calcula métricas sobre os spans errados e reporta a causa raiz errada.

Sua tarefa é corrigir o analisador para que um engenheiro de plantão identifique o trace com falha, a dependência causadora, a taxa de erro e a latência p95.

---

## Objetivo

Corrija `starter_observability.py` para que ele resuma o incidente corretamente e gere um código de validação.

Seu analisador final deve:

- Isolar spans raiz de requisições do agente
- Calcular taxa de erro apenas sobre requisições raiz
- Calcular p95 por nearest-rank sobre requisições raiz
- Identificar o trace raiz com falha
- Atribuir causa raiz ao span de dependência com falha

---

## Arquivos Iniciais

Salve estes arquivos em uma pasta chamada `challenge-006/`:

| Arquivo | Finalidade | Download |
|---------|------------|----------|
| `traces.json` | Exportação mock de traces do agente | [Download](https://github.com/lcarli/AI-LearningHub/raw/main/docs/docs/en/challenges/challenge-006/traces.json) |
| `starter_observability.py` | Analisador de incidente quebrado | [Download](https://github.com/lcarli/AI-LearningHub/raw/main/docs/docs/en/challenges/challenge-006/starter_observability.py) |
| `test_observability.py` | Testes de aceite | [Download](https://github.com/lcarli/AI-LearningHub/raw/main/docs/docs/en/challenges/challenge-006/test_observability.py) |
| `validate_observability.py` | Gera o código final de conclusão | [Download](https://github.com/lcarli/AI-LearningHub/raw/main/docs/docs/en/challenges/challenge-006/validate_observability.py) |

---

## Briefing do Desafio

Você recebe spans de trace e um analisador quebrado. Não há walkthrough: decida quais spans contam como requisições, como calcular métricas de SRE e como atribuir o incidente à dependência filha correta.

---

## Restrições

- Use apenas a biblioteca padrão do Python em `starter_observability.py`.
- Não hardcode o dicionário final de resumo.
- Métricas devem ser calculadas a partir dos spans.
- Spans filhos podem explicar causa raiz, mas não devem inflar contagens de requisições.

---

## Critérios de Aceite

Sua solução está completa quando:

- `python -m pytest test_observability.py` passa
- As requisições raiz são `tr-001`, `tr-002`, `tr-003` e `tr-004`
- A taxa de erro é `25.0`
- A latência p95 é `2200`
- O trace do incidente é `tr-003`
- A causa raiz é `inventory_api_timeout`

---

## Validação

Quando sua implementação estiver pronta, execute:

```bash
python -m pytest test_observability.py
python validate_observability.py
```

Digite o código de conclusão impresso por `validate_observability.py`:

<div class="challenge-validator" data-answer="CH006-FC7D7B5F">
  <input type="text" aria-label="Código de conclusão" placeholder="CH006-XXXXXXXX" />
  <button type="button">Validar</button>
  <p class="challenge-validator-result" aria-live="polite"></p>
</div>

---

## Dicas

??? tip "Dica 1 — Separe spans de requisição de spans filhos"
    Métricas de requisições raiz não devem contar cada ferramenta ou span de LLM.

??? tip "Dica 2 — A causa raiz geralmente está abaixo da raiz"
    O span do agente diz que a requisição falhou; a dependência filha normalmente diz por quê.

??? tip "Dica 3 — p95 tem uma definição"
    Use p95 por nearest-rank neste desafio.

---

## Rubrica

| Área | Pontos | Como fica bom |
|------|:------:|---------------|
| Filtragem de spans | 25 | Requisições raiz do agente são isoladas corretamente |
| Métricas | 30 | Taxa de erro e p95 usam o denominador certo |
| Causa raiz | 25 | Falha de dependência é identificada corretamente |
| Resumo do incidente | 10 | Saída concisa e acionável |
| Simplicidade | 10 | Análise local determinística |

---

## Labs Relacionados

- [Lab 033 — Observabilidade de Agentes com App Insights](../labs/lab-033-agent-observability.md)
- [Lab 049 — Rastreamento de Agentes no Foundry IQ](../labs/lab-049-foundry-iq-agent-tracing.md)
- [Lab 050 — Observabilidade Multi-Agente](../labs/lab-050-multi-agent-observability.md)
