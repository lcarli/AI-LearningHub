---
tags: [copilot-studio, teams, free-trial, no-code]
---
# Lab 011: Copilot Studio — Primeiro Agente

<div class="lab-meta">
  <span><strong>Nível:</strong> <span class="level-badge level-100">L100</span></span>
  <span><strong>Trilha:</strong> <a href="../paths/agent-builder-teams/">Agent Builder — Teams</a></span>
  <span><strong>Tempo:</strong> ~30 min</span>
  <span><strong>💰 Custo:</strong> <span class="level-badge cost-free">Avaliação Gratuita</span> — Avaliação gratuita do Microsoft Copilot Studio (sem cartão de crédito nos primeiros 30 dias)</span>
</div>

## O Que Você Vai Aprender

- Navegar pelo canvas do **Copilot Studio** (construtor de agentes sem código/low-code)
- Criar um agente de perguntas e respostas a partir de uma fonte de conhecimento (documento de FAQ)
- Testar seu agente no painel de teste de chat integrado
- Publicar o agente no **Microsoft Teams**
- Entender tópicos, gatilhos e comportamento de fallback

---

## Introdução

O Microsoft Copilot Studio é uma plataforma gráfica e low-code para construir agentes de IA conversacional sem escrever código. Você define **tópicos** (fluxos de conversa), conecta **fontes de conhecimento** e publica no Teams, sites ou outros canais em minutos.

Este laboratório constrói um agente de atendimento ao cliente para a empresa fictícia **OutdoorGear Inc.**, baseado em um FAQ de produtos.

---

## Pré-requisitos

- Conta Microsoft (gratuita em account.microsoft.com)
- Avaliação do Copilot Studio: [copilotstudio.microsoft.com](https://copilotstudio.microsoft.com) → Iniciar avaliação gratuita
- Microsoft Teams (a edição pessoal gratuita funciona)

!!! tip "Não é necessário cartão de crédito"
    A avaliação gratuita do Copilot Studio dura 30 dias e não requer dados de pagamento.

---

## Exercício do Laboratório

### Etapa 1: Criar um novo Copilot

1. Acesse [copilotstudio.microsoft.com](https://copilotstudio.microsoft.com)
2. Faça login com sua conta Microsoft
3. Clique em **Create** → **New agent**
4. Preencha:
   - **Name:** `OutdoorGear Assistant`
   - **Description:** `Customer service agent for OutdoorGear Inc. — answers product and policy questions`
   - **Instructions:** `You are a friendly customer service agent for OutdoorGear Inc. Answer questions about products, return policies, shipping, and warranties. Be concise and helpful.`
5. Clique em **Create**

### Etapa 2: Adicionar uma fonte de conhecimento

1. No painel esquerdo, clique em **Knowledge**
2. Clique em **Add knowledge** → **Public website or file**
3. Insira esta URL (nosso FAQ de exemplo):
   ```
   https://raw.githubusercontent.com/lcarli/AI-LearningHub/main/data/knowledge-base.json
   ```
   Ou clique em **Upload file** e cole este conteúdo em um arquivo `.txt` primeiro.

!!! tip "Usando o knowledge-base.json"
    O arquivo `data/knowledge-base.json` contém 42 documentos incluindo guias de produtos, políticas de devolução, FAQs e informações de envio — todos pré-formatados para RAG.

### Etapa 3: Testar o conhecimento integrado

1. Clique em **Test** no canto superior direito
2. No painel de chat, experimente estas perguntas:
   - `What is your return policy?`
   - `Do you have waterproof boots?`
   - `How long does shipping take?`
3. O agente deve responder a partir da fonte de conhecimento e citar onde encontrou a resposta

### Etapa 4: Criar um tópico personalizado

Tópicos personalizados permitem substituir respostas de IA por fluxos determinísticos para intenções específicas.

1. Clique em **Topics** no painel esquerdo
2. Clique em **Add a topic** → **From blank**
3. Nomeie como: `Order Status`
4. Em **Trigger phrases**, adicione:
   - `Where is my order`
   - `Track my order`
   - `Order status`
   - `What happened to my order`
5. Adicione um nó de **Message**:
   ```
   To check your order status, please visit our order portal at outdoorgear.com/orders or call 1-800-OUTDOOR. Have your order number ready!
   ```
6. Adicione um nó de **End conversation**
7. Clique em **Save**

### Etapa 5: Testar o tópico personalizado

No painel de teste, digite: `Where is my order?`

O agente deve usar o fluxo do seu tópico personalizado, não o fallback de IA. Observe como tópicos determinísticos têm prioridade sobre respostas generativas de IA.

### Etapa 6: Publicar no Teams

1. Clique em **Publish** no painel esquerdo
2. Clique em **Publish** para colocar o agente no ar
3. Clique em **Channels** → **Microsoft Teams**
4. Clique em **Turn on Teams**
5. Clique em **Open agent** — isso abre um link direto
6. No Teams, clique em **Add** para instalar o agente como um aplicativo
7. Comece a conversar com seu OutdoorGear Assistant no Teams!

---

## Arquitetura do Copilot Studio

```
┌─────────────────────────────────────────┐
│          Copilot Studio                 │
│                                         │
│  ┌─────────────┐   ┌─────────────────┐  │
│  │   Topics    │   │  Generative AI  │  │
│  │ (no-code    │   │  (knowledge +   │  │
│  │  flows)     │   │   LLM fallback) │  │
│  └──────┬──────┘   └────────┬────────┘  │
│         │   Topic match?    │           │
│         │ ◄─────────────────┘           │
│         ▼                               │
│     User message                        │
└─────────────────────────────────────────┘
         │
         ▼
  Channels: Teams, Web, Slack, ...
```

**Ordem de prioridade:**
1. Tópicos personalizados (correspondência exata de gatilho) → determinístico
2. Tópicos do sistema integrados (escalonamento, fallback)
3. Respostas generativas de IA a partir de fontes de conhecimento

---

## Quando usar Copilot Studio vs Código Profissional

| Copilot Studio | Código Profissional (SK/MCP) |
|----------------|-------------------|
| Usuários de negócio, sem código | Desenvolvedores |
| Prototipagem rápida | Lógica complexa |
| Integração com Teams/SharePoint | Integrações personalizadas |
| Fluxos baseados em interface gráfica | Controle programático |
| Personalização limitada | Flexibilidade total |

---

## Próximos Passos

- **Teams AI Library (bot de Teams code-first):** → [Lab 024 — Teams AI Library](lab-024-teams-ai-library.md)
- **Adicionar ferramentas MCP ao Copilot Studio:** → [Lab 012 — O que é MCP?](lab-012-what-is-mcp.md)
