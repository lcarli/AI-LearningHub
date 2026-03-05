---
tags: [free, beginner, no-account-needed, awareness]
---
# Lab 001: O que são Agentes de IA?

<div class="lab-meta">
  <span><strong>Nível:</strong> <span class="level-badge level-50">L50</span></span>
  <span><strong>Trilha:</strong> Todas as trilhas</span>
  <span><strong>Tempo:</strong> ~15 min</span>
  <span><strong>💰 Custo:</strong> <span class="level-badge cost-free">Gratuito</span> — Nenhuma conta necessária</span>
</div>

## O que Você Vai Aprender

- O que é (e o que não é) um agente de IA
- As quatro propriedades fundamentais de um agente: **percepção, memória, raciocínio, ação**
- Como os agentes diferem de chatbots simples e de software tradicional
- Exemplos reais de agentes de IA

---

## Introdução

A palavra "agente" está em todo lugar na IA atualmente — mas o que ela realmente significa?

Um **agente de IA** é um software que usa um Modelo de Linguagem Grande (LLM) como motor de raciocínio para **perseguir um objetivo de forma autônoma**, decidindo *o que fazer* e *quais ferramentas chamar* a cada passo — sem que você precise pré-programar todos os caminhos possíveis.

A palavra-chave é **autônomo**: o agente não apenas responde a uma pergunta. Ele planeja, age, observa o resultado e se ajusta.

---

## As Quatro Propriedades de um Agente

### 1. 🔍 Percepção
O agente recebe entrada — uma mensagem do usuário, um arquivo, uma resposta de API, um evento.

### 2. 🧠 Memória
O agente armazena informações entre turnos:
- **Curto prazo (janela de contexto):** a conversa atual
- **Longo prazo (banco vetorial / BD):** fatos, histórico, documentos recuperados

### 3. 💡 Raciocínio
O LLM decide *o que fazer em seguida*: responder diretamente, chamar uma ferramenta, fazer uma pergunta de esclarecimento ou dividir o objetivo em sub-etapas.

### 4. ⚡ Ação
O agente *faz algo*: chama uma API, consulta um banco de dados, escreve um arquivo, envia um e-mail, aciona outro agente.

![Ciclo do Agente de IA — Perceber, Raciocinar, Agir, Observar](../../assets/diagrams/agent-loop-cycle.svg)

??? question "🤔 Verifique Seu Entendimento"
    No ciclo do agente, o que acontece depois que o agente **age** (por exemplo, chama uma API)?

    ??? success "Resposta"
        O agente **observa** o resultado — a saída da ferramenta é alimentada de volta no contexto para que o LLM possa raciocinar sobre a nova informação e decidir o próximo passo. Isso fecha o ciclo: perceber → raciocinar → agir → observar → raciocinar novamente.

---

## Agente vs. Chatbot vs. Software Tradicional

| | Software Tradicional | Chatbot | Agente de IA |
|---|---|---|---|
| **Lógica definida por** | Desenvolvedor | Desenvolvedor | LLM (em tempo de execução) |
| **Lida com novas situações** | ❌ Apenas o que foi codificado | ⚠️ Dentro dos padrões treinados | ✅ Adapta-se dinamicamente |
| **Usa ferramentas** | ✅ Codificado fixo | ⚠️ Limitado | ✅ Descobre e chama ferramentas |
| **Raciocínio multi-etapas** | ❌ | ❌ | ✅ |
| **Previsibilidade** | ✅ Muito previsível | ✅ Majoritariamente previsível | ⚠️ Menos previsível |

!!! tip "Quando NÃO usar um agente"
    Agentes são poderosos, mas complexos. Use uma **chamada simples ao LLM** para perguntas e respostas de turno único. Use um **agente** apenas quando a tarefa exigir raciocínio multi-etapas, uso de ferramentas ou tomada de decisão dinâmica.

??? question "🤔 Verifique Seu Entendimento"
    Um chatbot tradicional segue uma árvore de decisão pré-programada. Como um agente de IA difere quando encontra uma situação que o desenvolvedor não antecipou?

    ??? success "Resposta"
        Um agente de IA usa o LLM para **se adaptar dinamicamente em tempo de execução** — ele raciocina sobre a nova situação e decide o que fazer, mesmo que aquele cenário exato nunca tenha sido codificado. Um chatbot tradicional só pode lidar com o que foi explicitamente programado.

??? question "🤔 Verifique Seu Entendimento"
    Quando você deve usar uma chamada simples ao LLM em vez de construir um agente de IA completo?

    ??? success "Resposta"
        Use uma chamada simples ao LLM para tarefas de **perguntas e respostas de turno único** que não exigem raciocínio multi-etapas, uso de ferramentas ou tomada de decisão dinâmica. Agentes adicionam complexidade e devem ser usados apenas quando a tarefa realmente necessita de autonomia.

---

## Exemplos do Mundo Real

| Agente | O que faz |
|-------|-------------|
| **GitHub Copilot** | Lê seu código, sugere complementos, conversa, executa comandos |
| **Zava Sales Agent** *(workshop deste repositório)* | Consulta PostgreSQL, gera gráficos, interpreta tendências de vendas |
| **Microsoft 365 Copilot** | Lê e-mails, calendário, arquivos, redige respostas, resume reuniões |
| **Agente de pesquisa AutoGen** | Cria sub-agentes para pesquisar, sintetizar e escrever um relatório |

??? question "🤔 Verifique Seu Entendimento"
    Qual das quatro propriedades fundamentais do agente (percepção, memória, raciocínio, ação) é principalmente responsável por o agente decidir *o que fazer em seguida*?

    ??? success "Resposta"
        **Raciocínio.** O LLM usa o raciocínio para decidir o próximo passo — seja responder diretamente, chamar uma ferramenta, fazer uma pergunta de esclarecimento ou dividir o objetivo em sub-etapas. A percepção lida com a entrada, a memória armazena o contexto e a ação executa a decisão.

---

## Termos-Chave

| Termo | Definição |
|------|-----------|
| **LLM** | Modelo de Linguagem Grande — o cérebro de IA (ex.: GPT-4o, Phi-4) |
| **Ferramenta / Função** | Uma função que o LLM pode chamar (ex.: `search_database`, `send_email`) |
| **Janela de contexto** | A "memória de trabalho" do LLM — tudo que ele pode ver de uma vez |
| **Prompt** | As instruções + contexto enviados ao LLM |
| **Token** | A unidade que os LLMs processam — aproximadamente ¾ de uma palavra |
| **Grounding** | Conectar as respostas do agente a dados reais e verificados |

---

## 🧠 Verificação de Conhecimento

??? question "**Q1 (Múltipla Escolha):** Qual das alternativas a seguir melhor descreve um agente de IA?"

    - A) Um chatbot que segue uma árvore de decisão pré-programada
    - B) Um modelo de aprendizado de máquina ajustado finamente nos dados da sua empresa
    - C) Software que usa um LLM para perseguir um objetivo de forma autônoma, decidindo o que fazer e quais ferramentas chamar a cada passo
    - D) Um sistema baseado em regras de correspondência de palavras-chave que direciona usuários para FAQs

    ??? success "✅ Revelar Resposta"
        **Correta: C**

        Um agente de IA usa um LLM como seu *motor de raciocínio* para decidir autonomamente o que fazer a cada passo — incluindo quais ferramentas chamar, quando repetir e quando parar. A opção A descreve um chatbot tradicional. A opção B é ajuste fino (muda o comportamento do modelo, não a estrutura do agente). A opção D é um sistema clássico de roteamento NLP.

??? question "**Q2 (Múltipla Escolha):** No ciclo perceber → raciocinar → agir → observar, qual é o propósito da etapa 'observar'?"

    - A) O agente reformula a consulta original do usuário antes de raciocinar
    - B) O agente recebe o resultado de uma ação e o adiciona de volta ao contexto para a próxima etapa de raciocínio
    - C) O agente chama o LLM para gerar uma resposta final
    - D) O agente salva a conversa na memória de longo prazo

    ??? success "✅ Revelar Resposta"
        **Correta: B**

        Depois que o agente *age* (chama uma ferramenta, executa código, consulta um banco de dados), ele *observa* o resultado — a saída da ferramenta é adicionada de volta ao histórico de mensagens. Isso fecha o ciclo: o LLM agora tem novas informações para raciocinar na próxima etapa. O ciclo continua até que o agente decida que tem informações suficientes para responder.

??? question "**Q3 (Múltipla Escolha):** Qual das alternativas a seguir NÃO é uma das quatro propriedades fundamentais de um agente de IA?"

    - A) Percepção
    - B) Compilação
    - C) Memória
    - D) Ação

    ??? success "✅ Revelar Resposta"
        **Correta: B — Compilação não é uma propriedade fundamental do agente**

        As quatro propriedades fundamentais são **Percepção** (recebe entradas), **Memória** (retém contexto), **Raciocínio** (usa o LLM para decidir o próximo passo) e **Ação** (chama ferramentas/APIs/código). Compilação é um conceito de linguagem de programação, não faz parte da arquitetura do agente.

---

## Resumo

Um agente de IA é um sistema alimentado por LLM que **percebe, lembra, raciocina e age** para alcançar um objetivo. Ele difere do software tradicional porque a lógica não é codificada fixamente — o LLM decide em tempo de execução. Essa flexibilidade é poderosa, mas requer design cuidadoso de instruções e ferramentas.

---

## Próximos Passos

→ **[Lab 002: Panorama dos Agentes de IA 2025](lab-002-agent-landscape.md)** — Compare todas as ferramentas e plataformas disponíveis hoje.
