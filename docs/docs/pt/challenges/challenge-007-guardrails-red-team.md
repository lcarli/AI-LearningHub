---
tags: [challenge, guardrails, red-team, safety, pii, python, local]
---
# Desafio 007: Red Team de Guardrails de Agentes

<div class="lab-meta">
  <span><strong>Nível:</strong> <span class="level-badge level-300">L300</span></span>
  <span><strong>Tipo:</strong> Desafio</span>
  <span><strong>Tempo:</strong> ~60 min</span>
  <span><strong>💰 Custo:</strong> <span class="level-badge cost-free">Gratuito (local)</span></span>
</div>

## Cenário

A OutdoorGear está preparando um agente de suporte voltado ao cliente. Antes do lançamento, a equipe de segurança entrega um pequeno conjunto de red team com perguntas seguras, exposição de PII, tentativas de jailbreak, pedidos perigosos e pedidos fora de escopo.

Sua tarefa é implementar uma camada local de guardrails que bloqueie, redija ou permita cada solicitação corretamente.

---

## Objetivo

Corrija `starter_guardrails.py` para que a camada de guardrails classifique cenários corretamente, redija endereços de e-mail, reporte métricas de red team e gere um código de validação.

Sua camada final deve:

- Permitir perguntas normais de suporte da OutdoorGear
- Redigir e-mails antes do processamento pelo agente
- Bloquear tentativas de jailbreak
- Bloquear pedidos perigosos de segurança física
- Bloquear pedidos de automação fora de escopo
- Evitar falsos positivos em perguntas seguras de suporte

---

## Arquivos Iniciais

Salve estes arquivos em uma pasta chamada `challenge-007/`:

| Arquivo | Finalidade | Download |
|---------|------------|----------|
| `scenarios.json` | Cenários seguros e de red team | [Download](https://github.com/lcarli/AI-LearningHub/raw/main/docs/docs/en/challenges/challenge-007/scenarios.json) |
| `starter_guardrails.py` | Camada de guardrails quebrada | [Download](https://github.com/lcarli/AI-LearningHub/raw/main/docs/docs/en/challenges/challenge-007/starter_guardrails.py) |
| `test_guardrails.py` | Testes de aceite | [Download](https://github.com/lcarli/AI-LearningHub/raw/main/docs/docs/en/challenges/challenge-007/test_guardrails.py) |
| `validate_guardrails.py` | Gera o código final de conclusão | [Download](https://github.com/lcarli/AI-LearningHub/raw/main/docs/docs/en/challenges/challenge-007/validate_guardrails.py) |

---

## Briefing do Desafio

Você recebe fixtures de cenários e uma implementação quebrada de guardrails. Não há walkthrough: decida quais sinais devem acionar bloqueio, redação ou permissão e faça as métricas de red team baterem com o comportamento esperado.

---

## Restrições

- Use apenas a biblioteca padrão do Python em `starter_guardrails.py`.
- Não hardcode comportamento por ID de cenário.
- Não bloqueie perguntas normais de produto/devolução.
- A redação deve preservar o restante da solicitação.
- Bloqueios devem ser determinísticos.

---

## Critérios de Aceite

Sua solução está completa quando:

- `python -m pytest test_guardrails.py` passa
- Perguntas seguras de produto e devolução são permitidas
- Endereços de e-mail são redigidos
- Solicitações de jailbreak, perigosas e fora de escopo são bloqueadas
- `false_positive == 0`

---

## Validação

Quando sua implementação estiver pronta, execute:

```bash
python -m pytest test_guardrails.py
python validate_guardrails.py
```

Digite o código de conclusão impresso por `validate_guardrails.py`:

<div class="challenge-validator" data-answer="CH007-452A3ED6">
  <input type="text" aria-label="Código de conclusão" placeholder="CH007-XXXXXXXX" />
  <button type="button">Validar</button>
  <p class="challenge-validator-result" aria-live="polite"></p>
</div>

---

## Dicas

??? tip "Dica 1 — Redação não é o mesmo que bloqueio"
    Um usuário pode fornecer um e-mail em uma solicitação de suporte válida.

??? tip "Dica 2 — Escopo importa"
    Uma solicitação pode ser inofensiva, mas ainda estar fora do escopo de um agente de suporte da OutdoorGear.

??? tip "Dica 3 — Padrões de segurança podem ser simples"
    Este desafio não precisa de classificação por ML. Checagens determinísticas por frases e regex são suficientes.

---

## Rubrica

| Área | Pontos | Como fica bom |
|------|:------:|---------------|
| Classificação | 35 | Decisões corretas de permitir/bloquear/redigir |
| Tratamento de PII | 20 | E-mail redigido sem perder o sentido da solicitação |
| Escopo de segurança | 20 | Pedidos perigosos e fora de escopo são bloqueados |
| Métricas | 15 | Resumo de red team é preciso |
| Simplicidade | 10 | Código pequeno e determinístico de guardrails |

---

## Labs Relacionados

- [Lab 008 — IA Responsável para Agentes](../labs/lab-008-responsible-ai.md)
- [Lab 036 — Defesa contra Injeção de Prompt e Segurança](../labs/lab-036-prompt-injection-security.md)
- [Lab 082 — Guardrails de Agentes](../labs/lab-082-agent-guardrails.md)
