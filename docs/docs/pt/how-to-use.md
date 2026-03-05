# Como Usar Este Hub

Esta página explica como o Hub de Aprendizado de Agentes de IA está estruturado para que você possa navegá-lo de forma eficaz e aproveitar ao máximo cada laboratório.

---

## 📊 O Sistema de Níveis

Cada laboratório é marcado com um nível de **50 a 400**, inspirado na numeração de sessões de conferências da Microsoft (um sinal amplamente compreendido de profundidade).

| Nível | Badge | Nome | O que esperar | Conta necessária |
|-------|-------|------|---------------|------------------|
| 50 | <span class="level-badge level-50">L50</span> | Conscientização | Leitura e conceitos. Sem ferramentas, sem conta. | ❌ Nenhuma |
| 100 | <span class="level-badge level-100">L100</span> | Fundamentos | Primeiros laboratórios práticos. Configuração mínima. | ✅ GitHub gratuito |
| 200 | <span class="level-badge level-200">L200</span> | Intermediário | Código + nuvem gratuita (GitHub Models). | ✅ GitHub gratuito |
| 300 | <span class="level-badge level-300">L300</span> | Avançado | Serviços em nuvem, padrões de integração. | ✅ Assinatura do Azure |
| 400 | <span class="level-badge level-400">L400</span> | Especialista | Arquitetura de produção, avaliações, custos. | ✅ Azure pago |

!!! tip "Comece no nível certo"
    Não pule L50/L100 mesmo se você for um desenvolvedor experiente — o enquadramento conceitual ajuda você a tomar melhores decisões depois.

---

## 🗺️ Caminhos de Aprendizado

Os laboratórios são agrupados em **8 Caminhos de Aprendizado**, cada um focado em uma ferramenta ou tecnologia:

| Caminho | Melhor para | Ponto de entrada |
|---------|-------------|------------------|
| 🤖 GitHub Copilot | Usuários do GitHub, desenvolvedores | L100 |
| 🏭 Microsoft Foundry | Desenvolvedores Azure, engenheiros de ML | L200 |
| 🔌 MCP | Qualquer pessoa construindo integrações de agentes | L100 |
| 🧠 Semantic Kernel | Desenvolvedores Python / C# | L100 |
| 📚 RAG | Desenvolvedores trabalhando com documentos/dados | L100 |
| 👥 Agent Builder — Teams | Desenvolvedores M365 | L100 |
| 💻 Agent Builder — VS Code | Desenvolvedores de extensões | L100 |
| ⚙️ Pro Code Agents | Engenheiros seniores, arquitetos | L200 |

Cada caminho tem uma **página índice** com a lista completa de laboratórios, uma ordem recomendada e uma breve visão geral do que você vai construir.

---

## 💡 Rotas de Aprendizado Sugeridas

### Rota A — "Do Zero ao Agente" (Sem necessidade de conta para começar)
```
Lab 001 → Lab 002 → Lab 003 → Lab 012 → Lab 020 (Python or C#)
```
Vá do conhecimento zero até executar seu próprio servidor MCP localmente, sem necessidade de conta na nuvem.

### Rota B — "Apenas GitHub" (Apenas conta gratuita do GitHub)
```
Lab 010 → Lab 013 → Lab 014 → Lab 022 → Lab 023
```
Use GitHub Copilot, GitHub Models e Semantic Kernel — tudo gratuito, sem cartão de crédito.

### Rota C — "Stack Completa do Azure"
```
Lab 013 → Lab 020 → Lab 030 → Lab 031 → Lab 032 → Lab 033
```
Requer assinatura do Azure. Construa um Foundry Agent completo com MCP, pgvector, RLS e observabilidade.

### Rota D — "Desenvolvedor Teams"
```
Lab 001 → Lab 011 → Lab 024
```
Construa agentes do Copilot Studio e bots do Teams passo a passo.

---

## 🔖 Lendo uma Página de Laboratório

Cada página de laboratório segue esta estrutura padrão:

```
# Lab XXX: [Title]

[Info box: Level · Path · Time · Cost]

## What You'll Learn
## Introduction
## Prerequisites Setup
## Lab Exercise
  ### Step 1 ...
  ### Step 2 ...
## Summary
## Next Steps
```

- **Caixa de informações** no topo mostra tudo de relance: nível, tempo estimado e requisitos de custo/conta.
- **Configuração de Pré-requisitos** informa exatamente o que instalar ou configurar — com links diretos para inscrições de teste gratuito.
- **Exercício do Laboratório** é o passo a passo guiado.
- **Próximos Passos** linka para a continuação natural do laboratório.

---

## 💰 Gratuito vs. Pago — Nosso Compromisso

Acreditamos que os melhores recursos de aprendizado são acessíveis. Nossos objetivos:

- ✅ **L50 e L100**: Custo zero, sem cartão de crédito, apenas uma conta gratuita do GitHub
- ✅ **L200**: Use [GitHub Models](https://github.com/marketplace/models) — inferência gratuita, sem cartão de crédito
- ⚠️ **L300**: Nível gratuito do Azure quando possível; claramente marcado quando uma assinatura do Azure é necessária
- ⚠️ **L400**: Recursos pagos do Azure necessários — custos estimados indicados em cada laboratório

→ Veja [Pré-requisitos e Contas](prerequisites.md) para o guia completo de configuração.
