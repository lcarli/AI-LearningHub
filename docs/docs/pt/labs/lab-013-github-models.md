---
tags: [modelos-locais, foundry-local, ollama, gratis, python, llm]
lab:
  id: '013'
  level: L100
  journey: llm-foundations
  time_min: 45
  cost:
    tier: free
    requires: []
    estimate_usd: US$ 0; execução no hardware local.
    simulation: false
    cleanup: false
  status: active
  last_verified: '2026-10-27'
  languages: [en, pt, fr]
---
# Lab 013: Backends de LLM Gratuitos — Foundry Local e Ollama

<div class="lab-meta">
  <span><strong>Nível:</strong> <span class="level-badge level-100">L100</span></span>
  <span><strong>Jornada:</strong> Fundamentos de LLM</span>
  <span><strong>Tempo:</strong> ~45 min</span>
  <span><strong>💰 Custo:</strong> <span class="level-badge cost-free">Grátis</span> — execução local, sem conta ou cartão</span>
</div>

!!! info "Por que este lab mudou"
    A inferência do GitHub Models foi descontinuada em 30 de julho de 2026. Este lab agora oferece o backend gratuito compartilhado pelo hub: Foundry Local em dispositivos Windows compatíveis ou Ollama no Windows, macOS e Linux.

## O Que Você Vai Aprender

- Escolher entre Foundry Local e Ollama
- Iniciar um endpoint local compatível com OpenAI
- Chamar um modelo de chat local com Python
- Configurar as variáveis de ambiente usadas nos outros labs
- Verificar que prompts e dados não saem da sua máquina

## Escolha um Runtime

=== "Foundry Local"
    Recomendado para dispositivos Windows compatíveis e aceleração DirectML.

    ```powershell
    winget install Microsoft.FoundryLocal
    foundry model run phi-4-mini
    $env:LOCAL_LLM_BASE_URL = "http://localhost:5273/v1"
    $env:LOCAL_LLM_MODEL = "phi-4-mini"
    ```

=== "Ollama"
    Opção multiplataforma para Windows, macOS e Linux.

    1. Instale o [Ollama](https://ollama.com/download).
    2. Inicie um modelo pequeno:

    ```bash
    ollama run phi4-mini
    ```

    Configure o endpoint:

    === "PowerShell"
        ```powershell
        $env:LOCAL_LLM_BASE_URL = "http://localhost:11434/v1"
        $env:LOCAL_LLM_MODEL = "phi4-mini"
        ```

    === "macOS / Linux"
        ```bash
        export LOCAL_LLM_BASE_URL="http://localhost:11434/v1"
        export LOCAL_LLM_MODEL="phi4-mini"
        ```

## Arquivos de Apoio

| Arquivo | Descrição | Download |
|---------|-----------|----------|
| `requirements.txt` | Dependência Python | [Download](lab-013/requirements.txt) |
| `starter.py` | Exercícios com backend local | [Download](lab-013/starter.py) |

## Exercício 1 — Verifique o Endpoint

```bash
pip install -r requirements.txt
python starter.py
```

```python
import os
from openai import OpenAI

client = OpenAI(
    base_url=os.environ["LOCAL_LLM_BASE_URL"],
    api_key="local",
)

response = client.chat.completions.create(
    model=os.environ["LOCAL_LLM_MODEL"],
    messages=[{"role": "user", "content": "Explique MCP em duas frases."}],
)
print(response.choices[0].message.content)
```

## Exercício 2 — Confirme o Processamento Local

1. Desconecte a internet depois de baixar o modelo.
2. Execute `python starter.py` novamente.
3. Confirme que a resposta continua funcionando.
4. Pare o runtime e confirme que o script mostra erro de conexão em vez de trocar silenciosamente para um serviço de nuvem.

## Configuração Compartilhada

| Variável | Exemplo | Finalidade |
|----------|---------|------------|
| `LOCAL_LLM_BASE_URL` | `http://localhost:11434/v1` | Endpoint compatível com OpenAI |
| `LOCAL_LLM_MODEL` | `phi4-mini` | Modelo de chat instalado |
| `LOCAL_EMBEDDING_MODEL` | Específico do runtime | Modelo opcional de embeddings |

!!! warning "As capacidades variam por modelo"
    Tool calling, saída estruturada, embeddings e limites de contexto dependem do modelo e do runtime. Cada lab informa as capacidades necessárias.

## Verificação de Conhecimento

??? question "Por que usar variáveis de ambiente?"
    Elas permitem usar o mesmo código com Foundry Local, Ollama ou um backend pago documentado.

??? question "Usar o SDK OpenAI envia a requisição para a OpenAI?"
    Não. O SDK é apenas o cliente; `base_url` define o destino.

## Próximos Passos

- [Lab 015 — Ollama: LLMs Locais](lab-015-ollama-local-llms.md)
- [Lab 078 — Foundry Local](lab-078-foundry-local.md)
- [Lab 017 — Saída Estruturada](lab-017-structured-output.md)

## Kit de apoio

O build do site gera downloads estáveis em PDF e ZIP. O ZIP contém o guia do lab e todos os arquivos de apoio declarados para este lab.

- [Baixar PDF gerado](../downloads/kits/lab-013-kit-pt.pdf)
- [Baixar ZIP gerado](../downloads/kits/lab-013-kit-pt.zip)
