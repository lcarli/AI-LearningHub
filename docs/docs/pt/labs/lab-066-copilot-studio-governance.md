---
tags: [copilot-studio, governance, dlp, power-platform, enterprise]
---
# Lab 066: Governança Corporativa do Copilot Studio

<div class="lab-meta">
  <span><strong>Nível:</strong> <span class="level-badge level-300">L300</span></span>
  <span><strong>Trilha:</strong> Todas as trilhas</span>
  <span><strong>Tempo:</strong> ~75 min</span>
  <span><strong>💰 Custo:</strong> <span class="level-badge cost-free">Gratuito</span> — Dados simulados (não requer licença do Copilot Studio)</span>
</div>

## O que Você Vai Aprender

- Como **auditar agentes do Copilot Studio** em um locatário do Power Platform
- Aplicar **políticas de DLP** em conectores e fluxos de dados dos agentes
- Detectar **agentes não governados** criados fora de ambientes gerenciados pela TI
- Aplicar **segurança em nível de ambiente** para isolar agentes de produção
- Identificar **lacunas de conformidade** entre agentes desenvolvidos por cidadãos e gerenciados pela TI
- Construir um **painel de governança** resumindo a postura dos agentes

!!! abstract "Pré-requisitos"
    Complete primeiro o **[Lab 065: Purview DSPM for AI](lab-065-purview-dspm-ai.md)**. Este lab pressupõe familiaridade com conceitos de governança de dados e fundamentos de políticas de DLP.

## Introdução

À medida que as organizações adotam o **Microsoft Copilot Studio**, desenvolvedores cidadãos e desenvolvedores profissionais criam agentes no Power Platform. Sem governança adequada, os agentes proliferam sem controle — conectando-se a fontes de dados sensíveis, contornando políticas de DLP e operando sem trilhas de auditoria.

A **Governança Corporativa do Copilot Studio** aborda esses desafios:

- Quais agentes existem e quem os criou?
- Os agentes estão em conformidade com as **políticas de DLP** organizacionais?
- Os agentes estão operando em **ambientes gerenciados** ou sandboxes pessoais?
- Quais agentes **falharam nas verificações de segurança**?

| Capacidade de Governança | O que Faz | Exemplo |
|--------------------------|-----------|---------|
| **Inventário de Agentes** | Cataloga todos os agentes no locatário | 12 agentes em 4 ambientes |
| **Aplicação de DLP** | Avalia o uso de conectores em relação às regras de DLP | Bloquear agentes usando APIs externas não aprovadas |
| **Verificação de Segurança** | Detecta configurações incorretas e vulnerabilidades | Agente expondo KB interna sem autenticação |
| **Isolamento de Ambiente** | Separa agentes de dev/teste/produção | Agentes de produção restritos a ambientes gerenciados pela TI |
| **Governança de Criadores** | Rastreia agentes criados por cidadãos vs TI | Sinalizar agentes desenvolvidos por cidadãos não revisados |

### O Cenário

Você é um **Administrador do Power Platform** encarregado de auditar todos os agentes do Copilot Studio no seu locatário. A organização tem **12 agentes** construídos por diferentes equipes. Alguns foram criados pela TI, outros por desenvolvedores cidadãos. Sua tarefa: identificar agentes não governados, sinalizar violações de DLP e produzir um relatório de governança.

---

## Pré-requisitos

| Requisito | Motivo |
|---|---|
| Python 3.10+ | Executar scripts de análise |
| `pandas` | Analisar dados de inventário de agentes |

```bash
pip install pandas
```

---

!!! tip "Início Rápido com GitHub Codespaces"
    [![Open in GitHub Codespaces](https://github.com/codespaces/badge.svg)](https://codespaces.new/lcarli/AI-LearningHub?quickstart=1)

    Todas as dependências estão pré-instaladas no devcontainer.


## 📦 Arquivos de Apoio

!!! note "Baixe estes arquivos antes de iniciar o lab"
    Salve todos os arquivos em uma pasta `lab-066/` no seu diretório de trabalho.

| Arquivo | Descrição | Download |
|---------|-----------|----------|
| `broken_governance.py` | Exercício de correção de bugs (3 bugs + autotestes) | [📥 Download](https://github.com/lcarli/AI-LearningHub/raw/main/docs/docs/en/labs/lab-066/broken_governance.py) |
| `studio_agents.csv` | Conjunto de dados | [📥 Download](https://github.com/lcarli/AI-LearningHub/raw/main/docs/docs/en/labs/lab-066/studio_agents.csv) |

---

## Etapa 1: Entendendo a Governança do Copilot Studio

A governança do Copilot Studio opera por meio de múltiplas camadas:

```
Tenant Admin Center → Environment Management → DLP Policies → Agent Inventory
                                                                     ↓
Governance Report ← Security Scan ← Connector Audit ←──────── Agent Config
```

Cada agente é avaliado em relação a:

1. **Classificação do ambiente** — O agente está em um ambiente gerenciado ou padrão?
2. **Conformidade com política de DLP** — O agente usa apenas conectores aprovados?
3. **Status da verificação de segurança** — O agente passou nas verificações de segurança automatizadas?
4. **Tipo de criador** — Foi construído pela TI ou por um desenvolvedor cidadão?

!!! info "Agentes Cidadãos vs Gerenciados pela TI"
    Agentes desenvolvidos por cidadãos são criados por usuários de negócios usando ferramentas low-code. Embora acelerem a inovação, frequentemente carecem de revisões de segurança, tratamento adequado de erros e controles de conformidade. A governança garante que esses agentes atendam aos mesmos padrões dos gerenciados pela TI.

---

## Etapa 2: Carregar e Explorar o Inventário de Agentes

O conjunto de dados contém **12 agentes do Copilot Studio** no locatário:

```python
import pandas as pd

agents = pd.read_csv("lab-066/studio_agents.csv")
print(f"Total agents: {len(agents)}")
print(f"Environments: {sorted(agents['environment'].unique())}")
print(f"Creator types: {sorted(agents['creator_type'].unique())}")
print(f"\nAgents per environment:")
print(agents.groupby("environment")["agent_id"].count().sort_values(ascending=False))
```

**Esperado:**

```
Total agents: 12
Environments: ['Default', 'Development', 'Production', 'Sandbox']
Creator types: ['citizen', 'it_managed']
```

---

## Etapa 3: Verificação de Conformidade com Política de DLP

Identifique agentes que violam as políticas de DLP:

```python
dlp_violations = agents[agents["dlp_compliant"] == False]
print(f"DLP non-compliant agents: {len(dlp_violations)}")
print(dlp_violations[["agent_id", "agent_name", "environment", "creator_type", "connector_count"]]
      .to_string(index=False))
```

**Esperado:**

```
DLP non-compliant agents: 4
```

!!! warning "Risco de Conectores"
    Agentes não conformes normalmente usam conectores que acessam APIs externas ou fontes de dados fora da lista aprovada da organização. Cada conector não aprovado representa um caminho potencial de exfiltração de dados.

---

## Etapa 4: Análise de Verificação de Segurança

Verifique quais agentes falharam nas verificações de segurança:

```python
failed_scans = agents[agents["security_scan"] == "failed"]
print(f"Failed security scans: {len(failed_scans)}")
print(failed_scans[["agent_id", "agent_name", "creator_type", "environment"]].to_string(index=False))

unprotected = agents[agents["authentication"] == "none"]
print(f"\nAgents without authentication: {len(unprotected)}")
print(unprotected[["agent_id", "agent_name", "environment"]].to_string(index=False))
```

**Esperado:**

```
Failed security scans: 3

Agents without authentication: 3
```

!!! danger "Agentes Desprotegidos"
    Agentes sem autenticação são acessíveis publicamente. Qualquer usuário — ou atacante externo — pode interagir com eles. Esses agentes devem ser imediatamente protegidos ou desativados.

---

## Etapa 5: Governança de Desenvolvedores Cidadãos

Analise a divisão entre agentes desenvolvidos por cidadãos e gerenciados pela TI:

```python
citizen = agents[agents["creator_type"] == "citizen"]
it_managed = agents[agents["creator_type"] == "it_managed"]
print(f"Citizen-created agents: {len(citizen)}")
print(f"IT-managed agents: {len(it_managed)}")
print(f"\nCitizen agents by environment:")
print(citizen.groupby("environment")["agent_id"].count().sort_values(ascending=False))

citizen_noncompliant = citizen[citizen["dlp_compliant"] == False]
print(f"\nCitizen agents violating DLP: {len(citizen_noncompliant)}")
```

**Esperado:**

```
Citizen-created agents: 8
IT-managed agents: 4
```

!!! tip "Insight de Governança"
    Desenvolvedores cidadãos criaram 8 dos 12 agentes (67%). Embora isso demonstre forte adoção, agentes cidadãos têm maior probabilidade de apresentar violações de DLP e falhas em verificações de segurança. Considere implementar fluxos de revisão obrigatórios para agentes criados por cidadãos antes que cheguem à produção.

---

## Etapa 6: Painel de Governança

Combine todas as descobertas em um resumo de governança:

```python
dashboard = f"""
╔════════════════════════════════════════════════════════╗
║     Copilot Studio Governance Report                   ║
╠════════════════════════════════════════════════════════╣
║ Total Agents:                {len(agents):>5}                     ║
║ Citizen-Created:             {len(citizen):>5}                     ║
║ IT-Managed:                  {len(it_managed):>5}                     ║
║ DLP Non-Compliant:           {len(dlp_violations):>5}                     ║
║ Failed Security Scans:       {len(failed_scans):>5}                     ║
║ No Authentication:           {len(unprotected):>5}                     ║
║ Production Agents:           {len(agents[agents['environment'] == 'Production']):>5}                     ║
╚════════════════════════════════════════════════════════╝
"""
print(dashboard)
```

---

## 🐛 Exercício de Correção de Bugs

O arquivo `lab-066/broken_governance.py` tem **3 bugs** na forma como analisa os dados de governança:

```bash
python lab-066/broken_governance.py
```

| Teste | O que verifica | Dica |
|-------|---------------|------|
| Teste 1 | Contagem de violações de DLP | Deve filtrar `dlp_compliant == False`, não `True` |
| Teste 2 | Contagem de agentes cidadãos | Deve filtrar `creator_type == "citizen"`, não `"it_managed"` |
| Teste 3 | Percentual de verificações com falha | Deve filtrar `security_scan == "failed"`, não `"passed"` |

---


## 🧠 Verificação de Conhecimento

??? question "**Q1 (Múltipla Escolha):** Qual é o principal risco de agentes do Copilot Studio não governados?"

    - A) Eles consomem muito poder computacional
    - B) Eles podem acessar dados sensíveis sem controles de DLP, autenticação ou trilhas de auditoria
    - C) Eles tornam o Power Platform mais lento
    - D) Eles impedem a TI de criar novos agentes

    ??? success "✅ Revelar Resposta"
        **Correta: B) Eles podem acessar dados sensíveis sem controles de DLP, autenticação ou trilhas de auditoria**

        Agentes não governados contornam as políticas de segurança organizacionais. Eles podem se conectar a fontes de dados sensíveis usando conectores não aprovados, operar sem autenticação e não possuir registro de auditoria — criando lacunas de conformidade e riscos de exfiltração de dados.

??? question "**Q2 (Múltipla Escolha):** Por que o isolamento de ambiente é importante para a governança do Copilot Studio?"

    - A) Faz os agentes executarem mais rápido
    - B) Separa agentes de desenvolvimento, teste e produção para aplicar diferentes políticas de segurança por estágio do ciclo de vida
    - C) Reduz custos de licenciamento
    - D) É necessário apenas para agentes de código personalizado

    ??? success "✅ Revelar Resposta"
        **Correta: B) Separa agentes de desenvolvimento, teste e produção para aplicar diferentes políticas de segurança por estágio do ciclo de vida**

        O isolamento de ambiente garante que agentes experimentais em ambientes sandbox não possam acessar dados de produção, e que agentes de produção atendam a requisitos mais rigorosos de DLP, autenticação e revisão. Sem isolamento, o protótipo de um desenvolvedor cidadão poderia acidentalmente se conectar a bancos de dados de produção.

??? question "**Q3 (Execute o Lab):** Quantos agentes falharam nas verificações de segurança?"

    Filtre o DataFrame de agentes para `security_scan == "failed"` e conte as linhas.

    ??? success "✅ Revelar Resposta"
        **3 agentes falharam nas verificações de segurança**

        Esses agentes apresentavam configurações incorretas, como autenticação ausente, bases de conhecimento internas expostas ou uso de conectores não aprovados. Falhas nas verificações exigem correção imediata antes que os agentes possam ser promovidos para produção.

??? question "**Q4 (Execute o Lab):** Quantos agentes não têm autenticação configurada?"

    Filtre por `authentication == "none"` e conte.

    ??? success "✅ Revelar Resposta"
        **3 agentes não têm autenticação**

        Agentes sem autenticação são acessíveis publicamente, o que significa que qualquer pessoa com a URL do endpoint pode interagir com eles. Esta é uma lacuna crítica de segurança que deve ser resolvida configurando Azure AD ou outros provedores de identidade.

??? question "**Q5 (Execute o Lab):** Quantos agentes foram criados por desenvolvedores cidadãos?"

    Filtre por `creator_type == "citizen"` e conte.

    ??? success "✅ Revelar Resposta"
        **8 agentes foram criados por desenvolvedores cidadãos**

        Desenvolvedores cidadãos criaram 8 dos 12 agentes totais (67%). Embora o desenvolvimento cidadão acelere a inovação, esses agentes requerem revisão de governança adicional para garantir conformidade com DLP, autenticação adequada e aprovação em verificações de segurança antes da implantação em produção.

---

## Resumo

| Tópico | O que Você Aprendeu |
|--------|---------------------|
| Inventário de Agentes | Catalogar e auditar todos os agentes do Copilot Studio no locatário |
| Aplicação de DLP | Detectar agentes usando conectores e fontes de dados não aprovados |
| Verificação de Segurança | Identificar agentes com verificações de segurança com falha e configurações incorretas |
| Isolamento de Ambiente | Separar dev/teste/produção para aplicar políticas apropriadas ao ciclo de vida |
| Governança de Criadores | Rastrear taxas de criação e conformidade de agentes cidadãos vs gerenciados pela TI |
| Painéis de Governança | Construir relatórios resumidos para partes interessadas executivas e de conformidade |

---

## Próximos Passos

- **[Lab 065](lab-065-purview-dspm-ai.md)** — Purview DSPM for AI (governança de dados complementar)
- **[Lab 064](lab-064-securing-mcp-apim.md)** — Securing MCP with APIM (segurança em nível de infraestrutura)
- **[Lab 008](lab-008-responsible-ai.md)** — Responsible AI (princípios fundamentais de governança)
