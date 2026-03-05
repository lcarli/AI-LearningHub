---
tags: [declarative-agents, m365-copilot, teams, manifest, low-code]
---
# Lab 069: Declarative Agents para Microsoft 365 Copilot

<div class="lab-meta">
  <span><strong>Nível:</strong> <span class="level-badge level-100">L100</span></span>
  <span><strong>Trilha:</strong> Todas as trilhas</span>
  <span><strong>Tempo:</strong> ~60 min</span>
  <span><strong>💰 Custo:</strong> <span class="level-badge cost-free">Gratuito</span> — Manifesto simulado (licença do M365 Copilot não necessária)</span>
</div>

## O que Você Vai Aprender

- O que são **declarative agents** e como eles estendem o Microsoft 365 Copilot
- Definir o comportamento do agente por meio de um **manifesto JSON** sem escrever código
- Configurar **fontes de conhecimento** (SharePoint, conectores do Graph, arquivos)
- Adicionar **plugins de API** para dar ao seu agente capacidades personalizadas
- Configurar **iniciadores de conversa** para interações guiadas com o usuário
- Validar e solucionar problemas de configurações de manifesto

!!! abstract "Pré-requisitos"
    Familiaridade com os conceitos do **Microsoft 365 Copilot** é recomendada. Nenhuma experiência em programação é necessária — declarative agents são configurados inteiramente por meio de manifestos JSON.

## Introdução

**Declarative agents** permitem personalizar o comportamento do Microsoft 365 Copilot sem escrever código. Em vez de construir um agente personalizado do zero, você define um manifesto JSON que especifica:

- **Instruções** — Prompt de sistema que molda a persona e o comportamento do agente
- **Fontes de conhecimento** — De onde o agente recupera informações (sites do SharePoint, conectores do Graph, arquivos enviados)
- **Plugins de API** — APIs externas que o agente pode chamar para executar ações
- **Iniciadores de conversa** — Prompts pré-definidos que guiam os usuários em direção às capacidades do agente

| Componente | Finalidade | Exemplo |
|-----------|---------|---------|
| **Instruções** | Definir persona, tom e limites | "Você é um assistente de RH. Responda apenas perguntas relacionadas a RH." |
| **Fontes de Conhecimento** | Fundamentar respostas em dados organizacionais | Site do SharePoint com políticas da empresa |
| **Plugins de API** | Habilitar ações além do chat | Enviar solicitações de folga via API de RH |
| **Iniciadores de Conversa** | Guiar usuários para interações produtivas | "Qual é a política de licenças da empresa?" |

### O Cenário

Você está construindo um **assistente de RH da empresa** como um declarative agent para o Microsoft 365 Copilot. O agente deve responder perguntas sobre políticas da empresa, ajudar funcionários a enviar solicitações de folga e fornecer orientação de integração. Você irá examinar um arquivo de manifesto, entender cada componente e validar a configuração.

---

## Pré-requisitos

| Requisito | Por quê |
|---|---|
| Python 3.10+ | Executar scripts de validação |
| `json` (embutido) | Analisar arquivos de manifesto |

Nenhum pacote adicional é necessário — o módulo `json` está incluído no Python.

---

!!! tip "Início Rápido com GitHub Codespaces"
    [![Open in GitHub Codespaces](https://github.com/codespaces/badge.svg)](https://codespaces.new/lcarli/AI-LearningHub?quickstart=1)

    Todas as dependências estão pré-instaladas no devcontainer.


## 📦 Arquivos de Apoio

!!! note "Baixe estes arquivos antes de iniciar o lab"
    Salve todos os arquivos em uma pasta `lab-069/` no seu diretório de trabalho.

| Arquivo | Descrição | Download |
|------|-------------|----------|
| `broken_manifest.py` | Exercício de correção de bugs (3 bugs + autotestes) | [📥 Download](https://github.com/lcarli/AI-LearningHub/raw/main/docs/docs/en/labs/lab-069/broken_manifest.py) |
| `declarative_agent.json` | Arquivo de configuração / dados | [📥 Download](https://github.com/lcarli/AI-LearningHub/raw/main/docs/docs/en/labs/lab-069/declarative_agent.json) |

---

## Etapa 1: Entendendo a Arquitetura de Declarative Agents

Declarative agents ficam entre o usuário e o Microsoft 365 Copilot, personalizando seu comportamento:

```
User → [Teams / M365 App] → [Declarative Agent Manifest]
                                      ↓
                             [Instructions] → Persona + Boundaries
                             [Knowledge]    → SharePoint, Graph, Files
                             [Plugins]      → API Actions
                             [Starters]     → Guided Conversations
                                      ↓
                            Microsoft 365 Copilot → Response
```

Princípios fundamentais:

1. **Sem código necessário** — Toda a configuração está em JSON
2. **Conhecimento com escopo definido** — O agente acessa apenas fontes especificadas
3. **Ações via plugins** — O agente pode chamar APIs para executar tarefas
4. **Proteções** — As instruções definem o que o agente deve e não deve fazer

!!! info "Declarative vs Agentes Personalizados"
    Declarative agents estendem o Copilot — eles herdam suas capacidades de raciocínio, segurança e fundamentação. Agentes personalizados (construídos com Bot Framework ou Copilot Studio) são independentes e exigem mais esforço de desenvolvimento, mas oferecem maior flexibilidade para fluxos de trabalho complexos.

---

## Etapa 2: Carregar e Explorar o Manifesto

Carregue o manifesto do declarative agent e examine sua estrutura:

```python
import json

with open("lab-069/declarative_agent.json", "r") as f:
    manifest = json.load(f)

print(f"Agent Name: {manifest['name']}")
print(f"Description: {manifest['description']}")
print(f"\nTop-level keys: {list(manifest.keys())}")
print(f"Instructions length: {len(manifest['instructions'])} characters")
```

**Esperado:**

```
Agent Name: HR Assistant
Description: A declarative agent for answering HR policy questions and managing time-off requests.
```

---

## Etapa 3: Análise das Fontes de Conhecimento

Examine as fontes de conhecimento configuradas para o agente:

```python
knowledge = manifest["knowledge_sources"]
print(f"Number of knowledge sources: {len(knowledge)}")
for i, source in enumerate(knowledge):
    print(f"\n  Source {i+1}:")
    print(f"    Type: {source['type']}")
    print(f"    Name: {source['name']}")
    print(f"    Description: {source['description']}")
```

**Esperado:**

```
Number of knowledge sources: 3
```

!!! tip "Conhecimento com Escopo Definido"
    Cada fonte de conhecimento limita o que o agente pode acessar. Ao especificar exatamente 3 fontes (por exemplo, site do SharePoint para políticas, conector do Graph para dados organizacionais, arquivo enviado para guia de benefícios), o agente é fundamentado em informações organizacionais verificadas e não pode acessar dados fora de seu escopo.

---

## Etapa 4: Configuração de Plugins de API

Examine os plugins de API disponíveis para o agente:

```python
plugins = manifest["api_plugins"]
print(f"Number of API plugins: {len(plugins)}")
for plugin in plugins:
    print(f"\n  Plugin: {plugin['name']}")
    print(f"  Description: {plugin['description']}")
    print(f"  Endpoint: {plugin['endpoint']}")
    print(f"  Operations: {[op['name'] for op in plugin['operations']]}")
```

**Esperado:**

```
Number of API plugins: 1
```

!!! warning "Segurança de Plugins"
    Plugins de API permitem que o agente execute ações — enviar solicitações, atualizar registros ou consultar sistemas externos. Cada plugin deve usar autenticação OAuth 2.0 e ser restrito às permissões mínimas necessárias. Sempre valide se os endpoints dos plugins são internos e confiáveis.

---

## Etapa 5: Iniciadores de Conversa

Examine os iniciadores de conversa que guiam os usuários:

```python
starters = manifest["conversation_starters"]
print(f"Number of conversation starters: {len(starters)}")
for i, starter in enumerate(starters):
    print(f"\n  Starter {i+1}: {starter['text']}")
    print(f"    Category: {starter.get('category', 'general')}")
```

**Esperado:**

```
Number of conversation starters: 4
```

Os iniciadores de conversa aparecem como sugestões clicáveis quando os usuários interagem pela primeira vez com o agente. Eles guiam os usuários em direção às capacidades principais do agente e reduzem o problema do "prompt em branco".

---

## Etapa 6: Validação do Manifesto

Valide o manifesto quanto à completude e problemas comuns:

```python
required_fields = ["name", "description", "instructions", "knowledge_sources",
                   "api_plugins", "conversation_starters"]
missing = [f for f in required_fields if f not in manifest]
print(f"Missing required fields: {missing if missing else 'None'}")

# Validation checks
checks = {
    "Has name": bool(manifest.get("name")),
    "Has description": bool(manifest.get("description")),
    "Has instructions": len(manifest.get("instructions", "")) > 50,
    "Knowledge sources > 0": len(manifest.get("knowledge_sources", [])) > 0,
    "Conversation starters > 0": len(manifest.get("conversation_starters", [])) > 0,
}

print("\nValidation Results:")
for check, passed in checks.items():
    status = "✅ PASS" if passed else "❌ FAIL"
    print(f"  {status} — {check}")

print(f"\nOverall: {'All checks passed' if all(checks.values()) else 'Some checks failed'}")
```

---

## 🐛 Exercício de Correção de Bugs

O arquivo `lab-069/broken_manifest.py` tem **3 bugs** na forma como valida o manifesto:

```bash
python lab-069/broken_manifest.py
```

| Teste | O que verifica | Dica |
|------|---------------|------|
| Teste 1 | Contagem de fontes de conhecimento | Deve ler de `knowledge_sources`, não de `data_sources` |
| Teste 2 | Validação de plugins | Deve verificar `api_plugins`, não `extensions` |
| Teste 3 | Extração do texto do iniciador | Deve acessar `starter['text']`, não `starter['prompt']` |

---


## 🧠 Verificação de Conhecimento

??? question "**Q1 (Múltipla Escolha):** Qual é a principal vantagem dos declarative agents em relação aos agentes personalizados?"

    - A) Eles são mais rápidos na inferência
    - B) Eles não requerem código — toda a configuração é definida em um manifesto JSON
    - C) Eles podem acessar qualquer fonte de dados sem restrições
    - D) Eles funcionam apenas localmente

    ??? success "✅ Revelar Resposta"
        **Correta: B) Eles não requerem código — toda a configuração é definida em um manifesto JSON**

        Declarative agents estendem o Microsoft 365 Copilot configurando o comportamento por meio de um manifesto JSON. Isso inclui instruções (prompt de sistema), fontes de conhecimento, plugins de API e iniciadores de conversa. Nenhuma programação é necessária, tornando-os acessíveis a não-desenvolvedores e ainda fornecendo capacidades de agente com escopo e governança definidos.

??? question "**Q2 (Múltipla Escolha):** Por que fontes de conhecimento com escopo definido são importantes para declarative agents?"

    - A) Elas fazem o agente responder mais rápido
    - B) Elas garantem que o agente acesse apenas dados verificados e autorizados — prevenindo alucinação de fontes não fundamentadas
    - C) Elas são exigidas pela loja de aplicativos do Teams
    - D) Elas reduzem o tamanho do arquivo de manifesto

    ??? success "✅ Revelar Resposta"
        **Correta: B) Elas garantem que o agente acesse apenas dados verificados e autorizados — prevenindo alucinação de fontes não fundamentadas**

        Ao listar explicitamente as fontes de conhecimento (sites do SharePoint, conectores do Graph, arquivos), o agente é fundamentado em dados organizacionais. Ele não pode acessar dados fora de seu escopo, reduzindo o risco de alucinação e garantindo conformidade com as políticas de acesso a dados. Esta é uma vantagem-chave de governança dos declarative agents.

??? question "**Q3 (Execute o Lab):** Quantas fontes de conhecimento estão configuradas no manifesto?"

    Carregue o JSON do manifesto e verifique `len(manifest['knowledge_sources'])`.

    ??? success "✅ Revelar Resposta"
        **3 fontes de conhecimento**

        O agente HR Assistant tem 3 fontes de conhecimento configuradas, fornecendo acesso com escopo definido a políticas da empresa, dados organizacionais e informações de benefícios dos funcionários. Cada fonte é declarada explicitamente no manifesto.

??? question "**Q4 (Execute o Lab):** Quantos plugins de API estão configurados?"

    Verifique `len(manifest['api_plugins'])`.

    ??? success "✅ Revelar Resposta"
        **1 plugin de API**

        O agente tem 1 plugin de API configurado, permitindo que ele execute ações como enviar solicitações de folga por meio de uma API de RH. Plugins de API permitem que declarative agents vão além do chat e executem ações reais em nome dos usuários.

??? question "**Q5 (Execute o Lab):** Quantos iniciadores de conversa estão definidos?"

    Verifique `len(manifest['conversation_starters'])`.

    ??? success "✅ Revelar Resposta"
        **4 iniciadores de conversa**

        O manifesto define 4 iniciadores de conversa que aparecem como sugestões clicáveis quando os usuários interagem pela primeira vez com o agente. Eles guiam os usuários em direção às capacidades principais do agente — perguntar sobre políticas de licença, enviar solicitações de folga, verificar benefícios e obter ajuda de integração.

---

## Resumo

| Tópico | O que Você Aprendeu |
|-------|-----------------|
| Declarative Agents | Estendem o M365 Copilot por meio de configuração de manifesto JSON |
| Instruções | Definem persona, tom e limites de comportamento |
| Fontes de Conhecimento | Definem o escopo de acesso do agente a dados organizacionais verificados |
| Plugins de API | Permitem que agentes executem ações via APIs externas |
| Iniciadores de Conversa | Guiam usuários em direção a interações produtivas |
| Validação de Manifesto | Verificam completude e correção da configuração do agente |

---

## Próximos Passos

- **[Lab 070](lab-070-agent-ux-patterns.md)** — Padrões de UX para Agentes (projetar interações eficazes com agentes)
- **[Lab 066](lab-066-copilot-studio-governance.md)** — Governança do Copilot Studio (governar implantações de agentes)
- **[Lab 008](lab-008-responsible-ai.md)** — IA Responsável (princípios fundamentais de governança)
