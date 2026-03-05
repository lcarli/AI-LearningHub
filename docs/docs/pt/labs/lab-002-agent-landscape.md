---
tags: [free, beginner, no-account-needed, awareness]
---
# Lab 002: Panorama dos Agentes de IA 2025

<div class="lab-meta">
  <span><strong>Nível:</strong> <span class="level-badge level-50">L50</span></span>
  <span><strong>Trilha:</strong> Todas as trilhas</span>
  <span><strong>Tempo:</strong> ~20 min</span>
  <span><strong>💰 Custo:</strong> <span class="level-badge cost-free">Gratuito</span> — Nenhuma conta necessária</span>
</div>

## O que Você Vai Aprender

- O ecossistema de agentes de IA da Microsoft em um relance
- Quando usar cada plataforma: Copilot Studio, Microsoft Foundry, Semantic Kernel, Teams AI Library, AutoGen
- Como o MCP se encaixa em todos eles
- O espectro de no-code a pro-code

---

## Introdução

O ecossistema Microsoft oferece múltiplas formas sobrepostas de construir agentes de IA. Isso pode ser confuso — devo usar Copilot Studio ou Foundry? Semantic Kernel ou LangChain? MCP ou chamadas diretas de API?

Este lab oferece um **mapa do panorama** para que você possa fazer escolhas informadas.

---

## O Espectro: No-Code → Pro-Code

![Espectro No-Code a Pro-Code](../../assets/diagrams/nocode-procode-spectrum.svg)

Não existe lado "melhor" — depende do seu caso de uso, habilidades da equipe e requisitos de governança.

---

## Comparação de Plataformas

### 🤖 GitHub Copilot

| | |
|---|---|
| **O que é** | Assistente de codificação com IA integrado ao seu IDE e GitHub |
| **Melhor para** | Desenvolvedores individuais, produtividade em codificação |
| **Capacidade de agente** | Copilot Chat, GitHub Models, Copilot Extensions |
| **Habilidade necessária** | Baixa (chat) a Alta (extensões) |
| **Custo** | Nível gratuito disponível |

### 🎨 Copilot Studio (Low-Code)

| | |
|---|---|
| **O que é** | Construtor de agentes no-code/low-code da Microsoft |
| **Melhor para** | Analistas de negócios, usuários M365, agentes Teams |
| **Capacidade de agente** | Fluxos de tópicos, conectores, ações customizadas, Azure OpenAI |
| **Habilidade necessária** | Baixa — nenhuma codificação necessária |
| **Custo** | Incluído em muitas licenças M365; avaliação gratuita disponível |

### 🏭 Microsoft Foundry Agent Service

| | |
|---|---|
| **O que é** | Runtime gerenciado de agentes no Azure |
| **Melhor para** | Agentes em produção, escala empresarial |
| **Capacidade de agente** | Chamada de ferramentas, Code Interpreter, servidores MCP, avaliação |
| **Habilidade necessária** | Média — SDK Python ou C# |
| **Custo** | Assinatura Azure (nível gratuito para prototipagem) |

### 🧠 Semantic Kernel

| | |
|---|---|
| **O que é** | SDK de agentes open-source (Python / C# / Java) |
| **Melhor para** | Desenvolvedores que querem controle de código com a stack Microsoft |
| **Capacidade de agente** | Plugins, memória vetorial, planejadores, multi-agente |
| **Habilidade necessária** | Média — experiência em Python ou C# |
| **Custo** | Gratuito (open-source); custos de LLM dependem do backend |

### ⚙️ AutoGen

| | |
|---|---|
| **O que é** | Framework open-source multi-agente da Microsoft Research |
| **Melhor para** | Fluxos de trabalho multi-agente complexos, pesquisa, orquestração |
| **Capacidade de agente** | Conversas aninhadas, humano no loop, execução de código |
| **Habilidade necessária** | Alta — Python, conceitos avançados de agentes |
| **Custo** | Gratuito (open-source); custos de LLM |

### 👥 Teams AI Library

| | |
|---|---|
| **O que é** | SDK para construir bots com IA no Teams |
| **Melhor para** | Apps nativos do Teams, colaboração empresarial |
| **Capacidade de agente** | IA conversacional dentro de canais do Teams, acesso a dados M365 |
| **Habilidade necessária** | Média — Node.js ou C# |
| **Custo** | SDK gratuito; requer tenant M365 |

??? question "🤔 Verifique Seu Entendimento"
    Qual é a diferença principal entre Copilot Studio e Semantic Kernel em termos de quem deve usá-los?

    ??? success "Resposta"
        **Copilot Studio** é projetado para **desenvolvedores cidadãos e analistas de negócios** que precisam de construção de agentes no-code/low-code. **Semantic Kernel** é projetado para **desenvolvedores profissionais** (Python/C#) que querem controle total de código sobre a lógica do agente, plugins e memória.

---

## Onde o MCP se Encaixa?

**Model Context Protocol (MCP)** não é uma plataforma — é um **padrão de conector**. Pense nele como o USB-C das ferramentas de IA: uma interface padrão única que qualquer agente pode usar para se conectar a qualquer fonte de dados ou ferramenta.

![Onde o MCP se Encaixa](../../assets/diagrams/mcp-fit-overview.svg)

O MCP funciona com **todas as plataformas acima** — e também com Claude Desktop, OpenAI e qualquer outro host compatível com MCP.

??? question "🤔 Verifique Seu Entendimento"
    O MCP é descrito como "USB-C para ferramentas de IA." Qual problema específico essa analogia destaca que o MCP resolve?

    ??? success "Resposta"
        O MCP resolve o **problema de integração N×M**. Sem o MCP, conectar 5 agentes a 5 ferramentas requer 25 integrações personalizadas. Com o MCP como padrão universal, cada ferramenta publica um servidor MCP e todo agente compatível com MCP pode se conectar — reduzindo as integrações para N+M.

---

## Guia Rápido de Decisão

| Situação | Ferramenta recomendada |
|-----------|-----------------|
| "Quero um agente no Teams para minha equipe, sem codificação" | Copilot Studio |
| "Quero adicionar IA à minha extensão do VS Code" | VS Code Chat Participant API |
| "Quero um agente em produção apoiado pelo Azure, com monitoramento" | Microsoft Foundry Agent Service |
| "Quero escrever código Python/C# para construir um agente sofisticado" | Semantic Kernel |
| "Quero múltiplos agentes de IA colaborando em tarefas complexas" | AutoGen |
| "Quero conectar minha ferramenta/API existente a qualquer agente de IA" | Construir um Servidor MCP |
| "Só quero experimentar LLMs gratuitamente" | GitHub Models |

??? question "🤔 Verifique Seu Entendimento"
    Um desenvolvedor quer construir um sistema onde um agente "pesquisador", um agente "escritor" e um agente "revisor" colaboram na produção de um relatório. Qual ferramenta da Microsoft é mais adequada para isso?

    ??? success "Resposta"
        **AutoGen.** Ele é especificamente projetado para orquestrar **múltiplos agentes especializados** que colaboram em tarefas complexas através de conversas aninhadas. Semantic Kernel se destaca na construção de agentes individuais sofisticados, enquanto AutoGen se destaca na coordenação multi-agente.

---

## 🧠 Verificação de Conhecimento

??? question "**Q1 (Múltipla Escolha):** Você é um desenvolvedor cidadão sem experiência em codificação. Precisa construir um chatbot no Teams que responda perguntas sobre políticas de RH do SharePoint. Qual ferramenta você deve escolher?"

    - A) AutoGen
    - B) Semantic Kernel
    - C) Copilot Studio
    - D) Microsoft Foundry Agent Service

    ??? success "✅ Revelar Resposta"
        **Correta: C — Copilot Studio**

        Copilot Studio é a opção **no-code/low-code** projetada para desenvolvedores cidadãos e profissionais de TI. Ele se integra nativamente ao Teams e Microsoft 365, pode apontar para o SharePoint como fonte de conhecimento e não requer nenhum código. AutoGen e Semantic Kernel exigem habilidades de desenvolvimento em Python/C#. Foundry é para desenvolvedores construindo backends personalizados.

??? question "**Q2 (Múltipla Escolha):** O que o MCP (Model Context Protocol) resolve no ecossistema de agentes de IA?"

    - A) Fornece um construtor visual para agentes sem codificação
    - B) Otimiza o uso de tokens do LLM para reduzir custos de API
    - C) Define um padrão universal para que qualquer agente possa se conectar a qualquer ferramenta/fonte de dados através de uma interface comum
    - D) Gerencia autenticação e controle de acesso baseado em funções para agentes

    ??? success "✅ Revelar Resposta"
        **Correta: C**

        O MCP é descrito como "USB-C para ferramentas de IA" — um padrão universal de conexão. Sem o MCP, conectar 5 agentes a 5 ferramentas requer 25 integrações personalizadas. Com o MCP, cada ferramenta publica um servidor MCP e todo agente compatível com MCP pode usá-lo. Ele resolve o problema de integração N×M em todo o ecossistema.

??? question "**Q3 (Múltipla Escolha):** Qual é a diferença principal entre Semantic Kernel e AutoGen?"

    - A) Semantic Kernel é open-source; AutoGen é proprietário da Microsoft
    - B) Semantic Kernel constrói agentes individuais sofisticados com plugins; AutoGen orquestra múltiplos agentes especializados colaborando em tarefas complexas
    - C) AutoGen só funciona com GPT-4o; Semantic Kernel suporta qualquer LLM
    - D) Semantic Kernel é apenas para Python; AutoGen suporta Python e C#

    ??? success "✅ Revelar Resposta"
        **Correta: B**

        **Semantic Kernel** se destaca na construção de um agente profundamente capaz — com plugins, memória, planejadores e uso estruturado de ferramentas. **AutoGen** se destaca na orquestração de *múltiplos* agentes — um agente pesquisador, um agente escritor, um agente revisor — cada um fazendo uma subtarefa especializada e passando resultados entre si. Ambos são open-source e suportam múltiplos LLMs.

---

## Resumo

O ecossistema Microsoft tem ferramentas para **todos os níveis de habilidade e casos de uso** — desde Copilot Studio no-code até AutoGen pro-code. O MCP é o conector universal que funciona em todos eles. No próximo lab, ajudaremos você a escolher a ferramenta certa para sua situação específica.

---

## Próximos Passos

→ **[Lab 003: Escolhendo a Ferramenta Certa](lab-003-choosing-the-right-tool.md)**
