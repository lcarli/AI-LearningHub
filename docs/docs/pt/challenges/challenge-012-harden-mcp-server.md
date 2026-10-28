---
tags: [challenge, phase-3, mcp, security, owasp, local-validator]
---
# Challenge 012: Blinde um Servidor MCP

<div class="lab-meta">
  <span><strong>Level:</strong> L300</span>
  <span><strong>Time:</strong> ~90 min</span>
  <span><strong>Cost:</strong> Free</span>
</div>

## Scenario

Ataque um servidor local deliberadamente fraco, defenda-o com controles explícitos e mapeie cada achado para OWASP.

```mermaid
flowchart LR
  A[Attack fixture] --> W[Weak server]
  W --> F[Finding]
  F --> D[Defense]
  D --> T[Regression test]
  T --> O[OWASP mapping]
```

## Task

1. Executar fixtures de ataque
2. Implementar controles de esquema, autorização, taxa e saída
3. Provar casos negativos
4. Mapear evidência para OWASP

## Acceptance criteria

- [ ] Todos os testes locais passam
- [ ] Cada ataque tem controle nomeado
- [ ] Nenhum segredo ou rede é necessário
- [ ] O relatório mapeia ataque → defesa → OWASP

## Local validation

```bash
cd docs/docs/pt/challenges/challenge-012
python -m unittest -v
python validate.py
```

<div class="challenge-validator" data-answer="CH012-HARDENMCP">
  <input type="text" aria-label="Completion code" placeholder="CH012-XXXXXXXX" />
  <button type="button">Validate</button>
  <p class="challenge-validator-result" aria-live="polite"></p>
</div>

## Official sources

- [OWASP Top 10 for Agentic Applications](https://genai.owasp.org/)
- [MCP 2026-07-28 authorization](https://modelcontextprotocol.io/specification/2026-07-28/basic/authorization)
