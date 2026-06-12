---
tags: [challenge, security, prompt-injection, rag, python, local]
---
# Desafio 003: Defenda um Agente contra Prompt Injection

<div class="lab-meta">
  <span><strong>Nível:</strong> <span class="level-badge level-200">L200</span></span>
  <span><strong>Tipo:</strong> Desafio</span>
  <span><strong>Tempo:</strong> ~60 min</span>
  <span><strong>💰 Custo:</strong> <span class="level-badge cost-free">Gratuito (local)</span></span>
</div>

## Cenário

A OutdoorGear importou avaliações de clientes para a base de conhecimento de um agente de suporte. Uma avaliação importada contém instruções maliciosas que tentam sobrescrever a política do agente, revelar instruções ocultas e afirmar que devoluções são ilimitadas.

Sua tarefa é fortalecer um helper local de suporte estilo RAG para bloquear tentativas de prompt injection, excluir contexto inseguro e responder perguntas seguras usando apenas documentos de política confiáveis.

---

## Objetivo

Corrija `starter_prompt_defense.py` para que a suíte de defesa bloqueie ataques, permita solicitações seguras, remova contexto malicioso, evite vazar texto do atacante e gere um código de validação.

Sua defesa final deve:

- Normalizar texto antes das verificações de política
- Detectar padrões comuns de prompt injection
- Remover contexto não confiável ou malicioso dos documentos recuperados
- Bloquear solicitações maliciosas de usuários
- Responder solicitações seguras usando apenas contexto confiável
- Reportar métricas de defesa corretamente

---

## Arquivos Iniciais

Salve estes arquivos em uma pasta chamada `challenge-003/`:

| Arquivo | Finalidade | Download |
|---------|------------|----------|
| `documents.json` | Contexto de suporte confiável e não confiável | [Download](https://github.com/lcarli/AI-LearningHub/raw/main/docs/docs/en/challenges/challenge-003/documents.json) |
| `requests.json` | Solicitações seguras e maliciosas | [Download](https://github.com/lcarli/AI-LearningHub/raw/main/docs/docs/en/challenges/challenge-003/requests.json) |
| `starter_prompt_defense.py` | Implementação de defesa quebrada | [Download](https://github.com/lcarli/AI-LearningHub/raw/main/docs/docs/en/challenges/challenge-003/starter_prompt_defense.py) |
| `test_prompt_defense.py` | Testes de aceite | [Download](https://github.com/lcarli/AI-LearningHub/raw/main/docs/docs/en/challenges/challenge-003/test_prompt_defense.py) |
| `validate_prompt_defense.py` | Gera o código final de conclusão | [Download](https://github.com/lcarli/AI-LearningHub/raw/main/docs/docs/en/challenges/challenge-003/validate_prompt_defense.py) |

---

## Briefing do Desafio

Você recebe documentos com níveis mistos de confiança, solicitações seguras, solicitações de ataque e uma camada de defesa quebrada. Não há walkthrough: decida como detectar intenção de ataque, filtrar contexto, responder com segurança e avaliar se o agente vazou instruções controladas pelo atacante.

---

## Restrições

- Use apenas a biblioteca padrão do Python em `starter_prompt_defense.py`.
- Não chame uma API de LLM.
- Não hardcode comportamento por ID de solicitação.
- Não responda a partir de conteúdo não confiável de avaliações de clientes.
- Solicitações seguras ainda devem ser respondidas.
- Texto de ataque não pode aparecer em respostas seguras.

---

## Critérios de Aceite

Sua solução está completa quando:

- `python -m pytest test_prompt_defense.py` passa
- As três solicitações de ataque são bloqueadas
- As duas solicitações seguras são permitidas
- A avaliação maliciosa é excluída do contexto seguro
- Respostas seguras citam fatos da política oficial
- `leakage_count == 0`

---

## Validação

Quando sua implementação estiver pronta, execute:

```bash
python -m pytest test_prompt_defense.py
python validate_prompt_defense.py
```

Digite o código de conclusão impresso por `validate_prompt_defense.py`:

<div class="challenge-validator" data-answer="CH003-EF57BB85">
  <input type="text" aria-label="Código de conclusão" placeholder="CH003-XXXXXXXX" />
  <button type="button">Validar</button>
  <p class="challenge-validator-result" aria-live="polite"></p>
</div>

---

## Dicas

??? tip "Dica 1 — Trate entrada do usuário e contexto recuperado separadamente"
    Uma solicitação do usuário pode ser maliciosa, mas documentos recuperados também podem conter instruções maliciosas.

??? tip "Dica 2 — Metadados de confiança importam"
    O fixture inclui um campo `trusted`. Use-o, mas não dependa apenas dos metadados.

??? tip "Dica 3 — Procure intenção, não só frases exatas"
    Atacantes podem dizer "ignore", "bypass", "admin_override" ou "system prompt" com variações de maiúsculas/minúsculas.

??? tip "Dica 4 — Respostas seguras devem ser entediantes"
    Uma resposta segura de política deve citar fatos da política. Ela não deve mencionar prompts ocultos, overrides ou devoluções ilimitadas.

---

## Rubrica

| Área | Pontos | Como fica bom |
|------|:------:|---------------|
| Detecção de ataques | 30 | Bloqueia padrões variados de prompt injection |
| Filtragem de contexto | 25 | Remove contexto inseguro e preserva documentos confiáveis |
| Resposta segura | 20 | Responde solicitações seguras a partir de evidência oficial |
| Prevenção de vazamento | 15 | Nenhuma string controlada pelo atacante aparece nas respostas |
| Simplicidade | 10 | Checagens locais determinísticas, sem over-engineering |

---

## Objetivos Extras

- Adicionar níveis de severidade para ataques
- Retornar uma mensagem segura de recusa para solicitações bloqueadas
- Adicionar motivos de exclusão por documento
- Adicionar uma nova variante de ataque e atualizar localmente o payload do validador

---

## Labs Relacionados

- [Lab 008 — IA Responsável para Agentes](../labs/lab-008-responsible-ai.md)
- [Lab 036 — Defesa contra Injeção de Prompt e Segurança](../labs/lab-036-prompt-injection-security.md)
- [Lab 082 — Guardrails de Agentes](../labs/lab-082-agent-guardrails.md)
