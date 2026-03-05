---
tags: [security, entra-id, obo, identity, oauth, enterprise]
---
# Lab 063: Agent Identity — Entra OBO Flow & Least Privilege

<div class="lab-meta">
  <span><strong>Nível:</strong> <span class="level-badge level-300">L300</span></span>
  <span><strong>Caminho:</strong> Todos os caminhos</span>
  <span><strong>Tempo:</strong> ~75 min</span>
  <span><strong>💰 Custo:</strong> <span class="level-badge cost-free">Gratuito</span> — Usa dados de cenário simulados (não é necessário um tenant Entra)</span>
</div>

## O Que Você Vai Aprender

- Como o **fluxo OAuth 2.0 On-Behalf-Of (OBO)** passa a identidade do usuário através de uma cadeia de agentes
- A diferença entre **permissões delegadas** (agir como usuário) e **permissões de aplicativo** (agir como aplicativo)
- Identificar **violações de conformidade** nas configurações de permissões de agentes
- Aplicar **princípios de menor privilégio** ao design de identidade de agentes
- Implementar **portões de aprovação humana (human-in-the-loop)** para ações de agentes de alto risco
- Analisar um **conjunto de dados de 15 cenários** em 4 agentes para postura de segurança

---

## Introdução

Quando agentes acessam recursos empresariais — lendo e-mails, consultando bancos de dados, modificando SharePoint — eles precisam de uma identidade. **Como** eles se autenticam determina a postura de segurança de todo o seu sistema.

O **fluxo On-Behalf-Of (OBO)** garante que os agentes ajam com a identidade e permissões do usuário, mantendo o princípio do menor privilégio. A alternativa — **client_credentials** (permissões de aplicativo) — dá ao agente sua própria identidade com acesso potencialmente amplo, contornando a autorização em nível de usuário.

Este lab analisa 15 cenários do mundo real para mostrar por que OBO é a escolha padrão e quando client_credentials cria riscos de conformidade.

### Os Cenários

Você examinará **15 cenários** em **4 agentes**, cada um com diferentes configurações de permissões:

| Agente | Descrição | Cenários |
|--------|-----------|----------|
| **MailAgent** | Lê e envia e-mails em nome dos usuários | 4 |
| **FileAgent** | Acessa arquivos do SharePoint e OneDrive | 4 |
| **CalendarAgent** | Gerencia eventos de calendário e agendamentos | 4 |
| **AdminAgent** | Realiza operações de diretório e conformidade | 3 |

---

## Pré-requisitos

```bash
pip install pandas
```

Este lab analisa dados de cenários pré-computados — não é necessário tenant Entra ID, assinatura Azure ou registro de aplicativo. Para implementar fluxos OBO em produção, você precisaria de um tenant Entra ID com registros de aplicativos.

---

!!! tip "Início Rápido com GitHub Codespaces"
    [![Open in GitHub Codespaces](https://github.com/codespaces/badge.svg)](https://codespaces.new/lcarli/AI-LearningHub?quickstart=1)

    Todas as dependências estão pré-instaladas no devcontainer.


## 📦 Arquivos de Apoio

!!! note "Baixe estes arquivos antes de iniciar o lab"
    Salve todos os arquivos em uma pasta `lab-063/` no seu diretório de trabalho.

| Arquivo | Descrição | Download |
|---------|-----------|----------|
| `broken_identity.py` | Exercício de correção de bugs (3 bugs + autotestes) | [📥 Download](https://github.com/lcarli/AI-LearningHub/raw/main/docs/docs/en/labs/lab-063/broken_identity.py) |
| `identity_scenarios.csv` | Conjunto de dados | [📥 Download](https://github.com/lcarli/AI-LearningHub/raw/main/docs/docs/en/labs/lab-063/identity_scenarios.csv) |

---

## Parte 1: Entendendo o Fluxo OBO

### Etapa 1: OBO vs client_credentials

Os dois principais fluxos de autenticação para agentes:

```
OBO Flow (Delegated — Recommended):
  User → [Auth] → Agent → [OBO token exchange] → Resource API
  Agent acts AS the user — user's permissions apply

Client Credentials (Application — Use with caution):
  Agent → [App secret/cert] → Resource API
  Agent acts AS ITSELF — app permissions apply (often broader)
```

Conceitos-chave:

| Conceito | Descrição |
|----------|-----------|
| **OBO (On-Behalf-Of)** | O agente troca o token do usuário por um token de API downstream, preservando a identidade do usuário |
| **Permissões delegadas** | O agente age como o usuário autenticado — limitado ao acesso do próprio usuário |
| **Permissões de aplicativo** | O agente age como ele mesmo — pode acessar dados de todos os usuários (ex.: ler TODAS as caixas de correio) |
| **Menor privilégio** | Conceder apenas as permissões mínimas necessárias para a tarefa |
| **Human-in-the-loop** | Exigir aprovação explícita do usuário para ações de alto risco |

!!! warning "Por Que o OBO É Importante"
    Com client_credentials, um MailAgent poderia ler o e-mail de **todos os usuários** — não apenas o do usuário solicitante. O OBO garante que o agente só pode acessar o que o próprio usuário pode acessar. Esta é a diferença entre uma ferramenta controlada e uma vulnerabilidade de segurança.

---

## Parte 2: Carregar Dados de Cenários

### Etapa 2: Carregar [📥 `identity_scenarios.csv`](https://github.com/lcarli/AI-LearningHub/raw/main/docs/docs/en/labs/lab-063/identity_scenarios.csv)

O conjunto de dados de cenários contém 15 configurações de identidade em 4 agentes:

```python
# identity_analysis.py
import pandas as pd

scenarios = pd.read_csv("lab-063/identity_scenarios.csv")

print(f"Scenarios: {len(scenarios)}")
print(f"Agents: {scenarios['agent'].unique().tolist()}")
print(f"Auth flows: {scenarios['auth_flow'].unique().tolist()}")
print(scenarios[["scenario_id", "agent", "auth_flow", "risk_level", "compliant"]].to_string(index=False))
```

**Saída esperada:**

```
Scenarios: 15
Agents: ['MailAgent', 'FileAgent', 'CalendarAgent', 'AdminAgent']
Auth flows: ['obo', 'client_credentials']

scenario_id          agent          auth_flow risk_level  compliant
        S01      MailAgent                obo        low       True
        S02      MailAgent                obo        low       True
        S03      MailAgent                obo     medium       True
        S04      MailAgent                obo     medium       True
        S05      MailAgent  client_credentials   critical      False
        S06      FileAgent                obo        low       True
        S07      FileAgent  client_credentials   critical      False
        S08      FileAgent                obo     medium       True
        S09      FileAgent                obo        low       True
        S10   CalendarAgent  client_credentials   critical      False
        S11   CalendarAgent                obo        low       True
        S12   CalendarAgent                obo     medium       True
        S13      AdminAgent                obo       high       True
        S14      AdminAgent  client_credentials       high      False
        S15      AdminAgent                obo     medium       True
```

---

## Parte 3: Análise de Conformidade

### Etapa 3: Identificar violações de conformidade

```python
# Compliance violations
violations = scenarios[scenarios["compliant"] == False]
print(f"Compliance violations: {len(violations)}/{len(scenarios)}")
print("\nViolation details:")
print(violations[["scenario_id", "agent", "auth_flow", "risk_level", "description"]].to_string(index=False))
```

**Saída esperada:**

```
Compliance violations: 4/15

Violation details:
scenario_id          agent          auth_flow risk_level                                          description
        S05      MailAgent  client_credentials   critical  Read all users' mail with app-level permissions
        S07      FileAgent  client_credentials   critical  Access all SharePoint sites without user context
        S10   CalendarAgent  client_credentials   critical  Modify any user's calendar without delegation
        S14      AdminAgent  client_credentials       high  Directory read with app permissions instead of OBO
```

!!! warning "Descoberta Crítica"
    Todas as 4 violações de conformidade usam **client_credentials** — não OBO. Três são de risco crítico (S05, S07, S10) porque concedem acesso amplo aos dados de todos os usuários. O padrão é claro: client_credentials sem escopo cria violações de conformidade.

```python
# Verify: do all violations use client_credentials?
violation_flows = violations["auth_flow"].unique().tolist()
print(f"\nAuth flows in violations: {violation_flows}")
print(f"All violations use client_credentials: {violation_flows == ['client_credentials']}")
```

**Saída esperada:**

```
Auth flows in violations: ['client_credentials']
All violations use client_credentials: True
```

---

## Parte 4: Análise de Nível de Risco

### Etapa 4: Analisar a distribuição de riscos

```python
# Risk level distribution
print("Risk level distribution:")
for level in ["low", "medium", "high", "critical"]:
    count = len(scenarios[scenarios["risk_level"] == level])
    if count > 0:
        print(f"  {level:>8}: {count}")

# Critical-risk scenarios
critical = scenarios[scenarios["risk_level"] == "critical"]
print(f"\nCritical-risk scenarios: {len(critical)}")
print(critical[["scenario_id", "agent", "auth_flow", "description"]].to_string(index=False))
```

**Saída esperada:**

```
Risk level distribution:
      low: 5
   medium: 4
     high: 3
 critical: 3

Critical-risk scenarios: 3
scenario_id          agent          auth_flow                                          description
        S05      MailAgent  client_credentials  Read all users' mail with app-level permissions
        S07      FileAgent  client_credentials  Access all SharePoint sites without user context
        S10   CalendarAgent  client_credentials  Modify any user's calendar without delegation
```

!!! info "Padrão de Risco"
    Todos os 3 cenários de risco crítico envolvem agentes com **client_credentials acessando dados de usuários** (e-mail, arquivos, calendário) sem contexto de usuário. O cenário de client_credentials do AdminAgent (S14) é de alto risco, mas não crítico, porque leituras de diretório são menos sensíveis do que acessar dados individuais dos usuários.

---

## Parte 5: Análise do Fluxo OBO

### Etapa 5: Taxa de adoção do OBO

```python
# OBO vs client_credentials
obo_count = len(scenarios[scenarios["auth_flow"] == "obo"])
total = len(scenarios)
obo_pct = obo_count / total * 100

print(f"OBO flow: {obo_count}/{total} = {obo_pct:.1f}%")
print(f"Client credentials: {total - obo_count}/{total} = {(total - obo_count)/total*100:.1f}%")

# OBO by agent
print("\nOBO usage by agent:")
for agent in scenarios["agent"].unique():
    agent_data = scenarios[scenarios["agent"] == agent]
    agent_obo = len(agent_data[agent_data["auth_flow"] == "obo"])
    agent_total = len(agent_data)
    print(f"  {agent:>15}: {agent_obo}/{agent_total} OBO")
```

**Saída esperada:**

```
OBO flow: 11/15 = 73.3%
Client credentials: 4/15 = 26.7%

OBO usage by agent:
      MailAgent: 4/5 OBO
      FileAgent: 3/4 OBO
  CalendarAgent: 2/4 OBO
     AdminAgent: 2/3 OBO
```

73,3% dos cenários usam OBO — bom, mas os 26,7% usando client_credentials são responsáveis por **todas** as violações de conformidade. Cada agente tem pelo menos um cenário de client_credentials que deveria ser revisado.

---

## Parte 6: Estratégia de Remediação

### Etapa 6: Corrigir violações de conformidade

Para cada violação, a remediação é mudar de client_credentials para OBO:

| Cenário | Atual | Correção | Observações |
|---------|-------|----------|-------------|
| S05 | App lê todos os e-mails | OBO — ler apenas o e-mail do usuário solicitante | Elimina acesso cruzado de dados entre usuários |
| S07 | App acessa todo o SharePoint | OBO — acessar apenas os sites autorizados do usuário | Respeita as permissões do site |
| S10 | App modifica qualquer calendário | OBO — modificar apenas o calendário do próprio usuário | Impede modificação cruzada entre usuários |
| S14 | App lê diretório | OBO — leitura de diretório como usuário | Limita o escopo à visão de diretório do usuário |

```python
# Compliance improvement after remediation
compliant_count = scenarios["compliant"].sum()
total = len(scenarios)
print(f"Current compliance: {compliant_count}/{total} = {compliant_count/total*100:.1f}%")
print(f"After remediation:  {total}/{total} = 100.0%")
print(f"\nAction: Convert {total - compliant_count} client_credentials scenarios to OBO")
```

### Etapa 7: Human-in-the-loop para ações de alto risco

Mesmo com OBO, algumas ações exigem aprovação explícita do usuário:

```python
# High-risk + medium scenarios that should have human-in-the-loop
hitl_candidates = scenarios[scenarios["risk_level"].isin(["high", "critical", "medium"])]
print(f"Scenarios needing human-in-the-loop review: {len(hitl_candidates)}")
print(hitl_candidates[["scenario_id", "agent", "risk_level", "description"]].to_string(index=False))
```

!!! info "Defesa em Profundidade"
    OBO + menor privilégio + human-in-the-loop formam três camadas de defesa. O OBO garante a identidade correta. O menor privilégio limita o que essa identidade pode fazer. O human-in-the-loop adiciona uma etapa de confirmação para ações sensíveis — mesmo que o agente tenha permissão, o usuário aprova explicitamente.

---

## 🐛 Exercício de Correção de Bugs

O arquivo `lab-063/broken_identity.py` tem **3 bugs** nas funções de análise de identidade. Execute os autotestes:

```bash
python lab-063/broken_identity.py
```

Você deverá ver **3 testes falhando**:

| Teste | O que ele verifica | Dica |
|-------|-------------------|------|
| Teste 1 | Contagem de violações de conformidade | Você está contando `compliant == True` em vez de `compliant == False`? |
| Teste 2 | Contagem de risco crítico | Você está filtrando por `risk_level == "high"` em vez de `risk_level == "critical"`? |
| Teste 3 | Percentual de OBO | Você está filtrando por `auth_flow == "client_credentials"` em vez de `auth_flow == "obo"`? |

Corrija todos os 3 bugs e execute novamente até ver `🎉 All 3 tests passed`.

---


## 🧠 Verificação de Conhecimento

??? question "**Q1 (Múltipla Escolha):** Qual é o propósito do fluxo OAuth 2.0 On-Behalf-Of (OBO)?"

    - A) Dar aos agentes sua própria identidade independente com acesso total de administrador
    - B) Passar a identidade do usuário através da cadeia de agentes para que o agente aja como o usuário
    - C) Ignorar a autenticação completamente para execução mais rápida do agente
    - D) Criar uma nova conta de usuário para cada instância de agente

    ??? success "✅ Revelar Resposta"
        **Correto: B) Passar a identidade do usuário através da cadeia de agentes para que o agente aja como o usuário**

        O fluxo OBO troca o token do usuário por um token de API downstream, preservando a identidade e as permissões do usuário. O agente age **como** o usuário — ele só pode acessar o que o usuário pode acessar. Esta é a base da identidade de agente com menor privilégio: o agente herda o escopo de autorização do usuário, não um escopo amplo de nível de aplicativo.

??? question "**Q2 (Múltipla Escolha):** Qual é a diferença principal entre permissões delegadas e de aplicativo?"

    - A) Delegada é mais rápida; aplicativo é mais preciso
    - B) Delegada age como o usuário autenticado; aplicativo age como o próprio aplicativo
    - C) Delegada não requer autenticação; aplicativo requer OAuth
    - D) Não há diferença prática — são intercambiáveis

    ??? success "✅ Revelar Resposta"
        **Correto: B) Delegada age como o usuário autenticado; aplicativo age como o próprio aplicativo**

        Com **permissões delegadas** (OBO), o agente age como o usuário — pode ler o e-mail do próprio usuário, mas não o de outros usuários. Com **permissões de aplicativo** (client_credentials), o agente age como ele mesmo com acesso em nível de aplicativo — poderia ler o e-mail de TODOS os usuários. Esta distinção é crítica: todas as 4 violações de conformidade no benchmark usam permissões de aplicativo onde permissões delegadas deveriam ter sido usadas.

??? question "**Q3 (Execute o Lab):** Quantas violações de conformidade existem nos 15 cenários?"

    Calcule `(scenarios["compliant"] == False).sum()`.

    ??? success "✅ Revelar Resposta"
        **4 violações (S05, S07, S10, S14)**

        Quatro cenários não estão em conformidade: S05 (MailAgent lê e-mails de todos os usuários), S07 (FileAgent acessa todo o SharePoint), S10 (CalendarAgent modifica qualquer calendário) e S14 (AdminAgent leitura de diretório com permissões de aplicativo). Todos os quatro usam client_credentials em vez de OBO, concedendo acesso mais amplo do que o necessário.

??? question "**Q4 (Execute o Lab):** Quantos cenários são classificados como risco crítico?"

    Calcule `(scenarios["risk_level"] == "critical").sum()`.

    ??? success "✅ Revelar Resposta"
        **3 cenários (S05, S07, S10)**

        Três cenários são de risco crítico: S05 (MailAgent), S07 (FileAgent) e S10 (CalendarAgent). Todos os três envolvem agentes usando client_credentials para acessar dados de usuários (e-mail, arquivos, calendário) sem contexto de usuário. S14 (AdminAgent) é de alto risco, mas não crítico, porque leituras de diretório são menos sensíveis do que acessar dados pessoais individuais dos usuários.

??? question "**Q5 (Execute o Lab):** Qual percentual dos cenários usa o fluxo OBO?"

    Calcule `(scenarios["auth_flow"] == "obo").sum() / len(scenarios) * 100`.

    ??? success "✅ Revelar Resposta"
        **73,3% (11/15)**

        11 de 15 cenários usam OBO — uma maioria sólida, mas os 4 restantes (26,7%) usando client_credentials são responsáveis por todas as violações de conformidade. O caminho de remediação é claro: converter todos os 4 cenários de client_credentials para OBO, elevando a conformidade de 73,3% para 100%. Cada agente (MailAgent, FileAgent, CalendarAgent, AdminAgent) tem pelo menos um cenário que precisa de conversão.

---

## Resumo

| Tópico | O Que Você Aprendeu |
|--------|---------------------|
| Fluxo OBO | Passa a identidade do usuário pela cadeia de agentes — o agente age como usuário |
| Delegada vs Aplicativo | Delegada = escopo do usuário; Aplicativo = escopo de todo o aplicativo |
| Conformidade | 4/15 violações — todas de client_credentials, não de OBO |
| Níveis de Risco | 3 cenários de risco crítico — todos client_credentials acessando dados de usuários |
| Adoção do OBO | 73,3% OBO — os 26,7% de client_credentials causam todas as violações |
| Remediação | Converter client_credentials para OBO; adicionar human-in-the-loop para alto risco |

---

## Próximos Passos

- **[Lab 062](lab-062-ondevice-phi-silica.md)** — Agentes On-Device com Phi Silica (privacidade através de inferência no dispositivo)
- **[Lab 061](lab-061-slm-phi4-mini.md)** — SLMs com Phi-4 Mini (outra abordagem para IA com privacidade em primeiro lugar)
- **[Lab 042](lab-042-enterprise-rag.md)** — Enterprise RAG (aplicando controles de identidade à recuperação de dados)
