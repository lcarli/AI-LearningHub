---
tags: [security, apim, mcp, oauth, enterprise, governance]
---
# Lab 064: Protegendo MCP em Escala com Azure API Management

<div class="lab-meta">
  <span><strong>Nível:</strong> <span class="level-badge level-400">L400</span></span>
  <span><strong>Caminho:</strong> <a href="../paths/pro-code/">⚙️ Pro Code</a></span>
  <span><strong>Tempo:</strong> ~90 min</span>
  <span><strong>💰 Custo:</strong> <span class="level-badge cost-free">Gratuito</span> — Dados de servidor simulados (não é necessária assinatura Azure)</span>
</div>

## O Que Você Vai Aprender

- Usar **Azure API Management (APIM)** como gateway centralizado para servidores MCP
- Impor autenticação **OAuth 2.0** em todos os endpoints MCP
- Aplicar **limitação de taxa**, **políticas de DLP** e **logging** ao tráfego MCP
- Auditar a conformidade de servidores MCP entre equipes e identificar lacunas de segurança
- Analisar **taxas de erro**, **latência** e **volumes de chamadas** em uma frota de MCP

!!! abstract "Pré-requisito"
    Complete **[Lab 012: O Que É MCP?](lab-012-what-is-mcp.md)** e **[Lab 020: MCP Server (Python)](lab-020-mcp-server-python.md)** primeiro. Este lab pressupõe familiaridade com a arquitetura MCP e padrões de disponibilização de ferramentas.

## Introdução

À medida que as organizações escalam suas implantações de agentes de IA, o número de **servidores MCP** cresce rapidamente — cada equipe constrói o seu próprio, com diferentes esquemas de autenticação, limites de taxa e controles de prevenção contra perda de dados (DLP). Sem governança centralizada, você acaba com uma colcha de retalhos de políticas de segurança inconsistentes.

**Azure API Management** resolve isso posicionando-se na frente de todos os servidores MCP como um gateway unificado:

| Preocupação | Sem APIM | Com APIM |
|-------------|----------|----------|
| **Autenticação** | Cada servidor implementa a sua própria (API key, basic, OAuth…) | OAuth 2.0 centralizado com Azure AD |
| **Limitação de Taxa** | Sem limites ou limites inconsistentes por servidor | Política uniforme em todos os endpoints |
| **DLP** | Sem varredura de entradas/saídas de ferramentas | Inspeção de conteúdo e redação de PII |
| **Monitoramento** | Logs dispersos, sem visão unificada | Métricas centralizadas, alertas e dashboards |

### O Cenário

Você é um **Engenheiro de Segurança de Plataforma** em uma empresa que opera **10 servidores MCP** em **6 equipes**. A gerência quer um relatório de conformidade: quais servidores atendem à linha de base de segurança (OAuth + DLP + logging), quais não atendem e qual é a exposição ao risco.

Você tem um conjunto de dados de inventário da frota com tipos de autenticação, limites de taxa, status de DLP, status de logging, volumes de chamadas, latência e taxas de erro.

---

## Pré-requisitos

| Requisito | Por quê |
|-----------|---------|
| Python 3.10+ | Executar scripts de análise |
| `pandas` | Analisar dados da frota de servidores |

```bash
pip install pandas
```

---

!!! tip "Início Rápido com GitHub Codespaces"
    [![Open in GitHub Codespaces](https://github.com/codespaces/badge.svg)](https://codespaces.new/lcarli/AI-LearningHub?quickstart=1)

    Todas as dependências estão pré-instaladas no devcontainer.


## 📦 Arquivos de Apoio

!!! note "Baixe estes arquivos antes de iniciar o lab"
    Salve todos os arquivos em uma pasta `lab-064/` no seu diretório de trabalho.

| Arquivo | Descrição | Download |
|---------|-----------|----------|
| `broken_apim.py` | Exercício de correção de bugs (3 bugs + autotestes) | [📥 Download](https://github.com/lcarli/AI-LearningHub/raw/main/docs/docs/en/labs/lab-064/broken_apim.py) |
| `mcp_servers.csv` | Conjunto de dados | [📥 Download](https://github.com/lcarli/AI-LearningHub/raw/main/docs/docs/en/labs/lab-064/mcp_servers.csv) |

---

## Etapa 1: Entendendo o Modelo de Segurança do APIM

Quando o APIM está posicionado na frente dos servidores MCP, cada chamada de ferramenta flui através de um pipeline de políticas:

```
Agent → APIM Gateway → [Auth Policy] → [Rate Limit] → [DLP Scan] → MCP Server
                                                                        ↓
Agent ← APIM Gateway ← [Response DLP] ← [Logging] ←────────────── Response
```

Políticas-chave para MCP:

| Política | Finalidade | Exemplo |
|----------|-----------|---------|
| **validate-jwt** | Verificar tokens OAuth 2.0 | Rejeitar chamadas sem token Azure AD válido |
| **rate-limit-by-key** | Limitar por cliente/equipe | 100 RPM por agente |
| **set-body** | Inspeção de conteúdo DLP | Redigir SSN, números de cartão de crédito das saídas de ferramentas |
| **log-to-eventhub** | Logging de auditoria centralizado | Cada chamada de ferramenta → Event Hub → Log Analytics |

!!! tip "Por Que OAuth em Vez de API Keys?"
    API keys não têm identidade de usuário, não têm expiração de token e não têm controle de escopo. Se uma chave vazar, qualquer pessoa pode chamar o servidor MCP até que você a rotacione manualmente. Tokens OAuth 2.0 expiram automaticamente, carregam identidade de usuário/aplicativo e podem ser restritos a ferramentas específicas.

---

## Etapa 2: Carregar e Explorar a Frota de Servidores MCP

O conjunto de dados contém **10 servidores MCP** em **6 equipes**:

```python
import pandas as pd

servers = pd.read_csv("lab-064/mcp_servers.csv")
print(f"Total MCP servers: {len(servers)}")
print(f"Teams: {sorted(servers['team'].unique())}")
print(f"\nServers per team:")
print(servers.groupby("team")["server_name"].count().sort_values(ascending=False))
```

**Esperado:**

```
Total MCP servers: 10
Teams: ['Analytics', 'Commerce', 'Finance', 'HR', 'Logistics', 'Marketing', 'Operations', 'Support']

Commerce      2
Operations    2
Analytics     1
Finance       1
HR            1
Logistics     1
Marketing     1
Support       1
```

---

## Etapa 3: Auditoria de Conformidade

Um servidor é **conforme** se tiver todos os três: autenticação OAuth 2.0, DLP habilitado e logging habilitado. Verifique a frota:

```python
compliant = servers[servers["compliant"] == True]
non_compliant = servers[servers["compliant"] == False]

print(f"Compliant servers:     {len(compliant)}")
print(f"Non-compliant servers: {len(non_compliant)}")
print(f"\nNon-compliant details:")
print(non_compliant[["server_name", "team", "auth_type", "has_dlp", "has_logging"]].to_string(index=False))
```

**Esperado:**

```
Compliant servers:     6
Non-compliant servers: 4

Non-compliant details:
     server_name       team auth_type has_dlp has_logging
 customer-support   Support   api_key   false       true
 analytics-export Analytics   api_key   false      false
       legacy-erp Operations    basic   false      false
   maps-geocoding  Logistics   api_key   false       true
```

!!! warning "Alerta de Risco"
    4 de 10 servidores não estão em conformidade — isso é **40% da frota**. O servidor `legacy-erp` é o pior infrator: autenticação basic, sem DLP, sem logging e a maior taxa de erro.

---

## Etapa 4: Análise de Lacunas de Autenticação

Identifique servidores que **não** estão usando OAuth 2.0:

```python
non_oauth = servers[servers["auth_type"] != "oauth2"]
print(f"Servers without OAuth 2.0: {len(non_oauth)}")
print(non_oauth[["server_name", "auth_type", "monthly_calls"]].to_string(index=False))

total_non_oauth_calls = non_oauth["monthly_calls"].sum()
total_calls = servers["monthly_calls"].sum()
pct = total_non_oauth_calls / total_calls * 100
print(f"\nNon-OAuth call volume: {total_non_oauth_calls:,} / {total_calls:,} ({pct:.1f}%)")
```

**Esperado:**

```
Servers without OAuth 2.0: 4

     server_name auth_type  monthly_calls
 customer-support   api_key         28000
 analytics-export   api_key         12000
       legacy-erp     basic          8000
   maps-geocoding   api_key         22000

Non-OAuth call volume: 70,000 / 194,500 (36.0%)
```

!!! danger "36% de Todas as Chamadas MCP Usam Autenticação Fraca"
    Mais de um terço das chamadas mensais de API passam por servidores com API keys ou autenticação basic. Uma única chave vazada poderia expor dados de suporte ao cliente, exportações de analytics, registros de ERP ou serviços de geocodificação.

---

## Etapa 5: Análise de Cobertura de DLP

Verifique quais servidores não possuem varredura de prevenção contra perda de dados:

```python
no_dlp = servers[servers["has_dlp"].astype(str).str.lower() == "false"]
print(f"Servers without DLP: {len(no_dlp)}")
print(no_dlp[["server_name", "team", "monthly_calls"]].to_string(index=False))
```

**Esperado:**

```
Servers without DLP: 4

     server_name       team  monthly_calls
 customer-support   Support         28000
 analytics-export Analytics         12000
       legacy-erp Operations          8000
   maps-geocoding  Logistics         22000
```

Os 4 servidores sem DLP processam **70.000 chamadas mensais** — qualquer um deles poderia vazar PII ou dados sensíveis através das saídas de ferramentas sem detecção.

---

## Etapa 6: Análise de Taxa de Erro e Latência

Identifique servidores com as maiores taxas de erro e latência:

```python
print("Error rates (sorted):")
error_sorted = servers.sort_values("error_rate_pct", ascending=False)
print(error_sorted[["server_name", "error_rate_pct", "avg_latency_ms"]].to_string(index=False))

highest_error = error_sorted.iloc[0]
print(f"\nHighest error rate: {highest_error['server_name']} at {highest_error['error_rate_pct']}%")
print(f"Its average latency: {highest_error['avg_latency_ms']}ms")
```

**Esperado:**

```
Highest error rate: legacy-erp at 5.8%
Its average latency: 450ms
```

!!! tip "Insight"
    O servidor `legacy-erp` se destaca como o servidor de maior risco: autenticação basic, sem DLP, sem logging, maior taxa de erro (5,8%) e maior latência (450ms). Este deveria ser a prioridade máxima para integração ao APIM.

---

## Etapa 7: Volume Total de Chamadas

Calcule o total de chamadas mensais em todos os servidores MCP:

```python
total = servers["monthly_calls"].sum()
print(f"Total monthly calls across fleet: {total:,}")
```

**Esperado:**

```
Total monthly calls across fleet: 194,500
```

---

## Etapa 8: Prioridade de Migração para APIM

Crie um plano de migração priorizado com base no risco:

```python
servers["risk_score"] = (
    (servers["auth_type"] != "oauth2").astype(int) * 3 +
    (servers["has_dlp"].astype(str).str.lower() == "false").astype(int) * 2 +
    (servers["has_logging"].astype(str).str.lower() == "false").astype(int) * 1 +
    servers["error_rate_pct"] / servers["error_rate_pct"].max()
)

priority = servers.sort_values("risk_score", ascending=False)
print("Migration Priority:")
print(priority[["server_name", "auth_type", "has_dlp", "has_logging", "risk_score"]]
      .head(5).to_string(index=False))
```

Isso produz uma lista classificada por risco para guiar a sequência de integração ao APIM.

---

## 🐛 Exercício de Correção de Bugs

O arquivo `lab-064/broken_apim.py` tem **3 bugs** na forma como analisa a frota de servidores MCP:

```bash
python lab-064/broken_apim.py
```

| Teste | O que ele verifica | Dica |
|-------|-------------------|------|
| Teste 1 | Contagem de servidores não conformes | Deveria contar `compliant == False`, não `True` |
| Teste 2 | Total de chamadas mensais | Deveria ser a **soma**, não a **média** |
| Teste 3 | Servidores sem OAuth | Deveria filtrar `auth_type != "oauth2"`, não `== "oauth2"` |

---


## 🧠 Verificação de Conhecimento

??? question "**Q1 (Múltipla Escolha):** Por que o APIM é a abordagem recomendada para proteger servidores MCP em escala?"

    - A) Ele substitui o MCP por um protocolo diferente
    - B) Ele fornece autenticação centralizada, limitação de taxa e monitoramento em todos os endpoints MCP
    - C) Ele elimina a necessidade de OAuth 2.0
    - D) Ele só funciona com servidores MCP hospedados no Azure

    ??? success "✅ Revelar Resposta"
        **Correto: B) Ele fornece autenticação centralizada, limitação de taxa e monitoramento em todos os endpoints MCP**

        O APIM atua como um gateway unificado na frente de todos os servidores MCP, aplicando validação OAuth 2.0 consistente, limitação de taxa, inspeção de conteúdo DLP e logging de auditoria — independentemente de como cada servidor MCP individual foi originalmente construído. Sem o APIM, cada equipe implementa (ou ignora) esses controles de forma independente.

??? question "**Q2 (Múltipla Escolha):** Por que a autenticação por API key é insuficiente para servidores MCP em produção?"

    - A) API keys são longas demais para armazenar com segurança
    - B) API keys não fornecem identidade de usuário, expiração de token e controle de escopo
    - C) API keys só funcionam com APIs REST, não com MCP
    - D) API keys requerem Azure AD para funcionar

    ??? success "✅ Revelar Resposta"
        **Correto: B) API keys não fornecem identidade de usuário, expiração de token e controle de escopo**

        API keys são segredos estáticos: se uma vazar, qualquer pessoa pode usá-la indefinidamente até que seja rotacionada manualmente. Elas não carregam informação sobre *quem* está chamando ou *o que* é permitido fazer. Tokens OAuth 2.0 expiram automaticamente, incorporam claims de identidade de usuário/aplicativo e podem ser restritos a permissões específicas (ex.: acesso somente leitura a uma ferramenta específica).

??? question "**Q3 (Execute o Lab):** Quantos servidores MCP na frota não estão em conformidade?"

    Filtre o DataFrame de servidores por `compliant == False` e conte as linhas.

    ??? success "✅ Revelar Resposta"
        **4 servidores não conformes**

        Os servidores não conformes são: `customer-support` (api_key, sem DLP), `analytics-export` (api_key, sem DLP, sem logging), `legacy-erp` (autenticação basic, sem DLP, sem logging) e `maps-geocoding` (api_key, sem DLP). Todos os 4 não possuem OAuth e DLP; 2 também não possuem logging.

??? question "**Q4 (Execute o Lab):** Qual é o volume total de chamadas mensais em todos os 10 servidores MCP?"

    Some a coluna `monthly_calls` em todos os servidores.

    ??? success "✅ Revelar Resposta"
        **194.500 chamadas mensais no total**

        45.000 + 32.000 + 28.000 + 18.000 + 15.000 + 12.000 + 5.000 + 8.000 + 22.000 + 9.500 = **194.500**. Destas, 70.000 (36%) passam por servidores sem OAuth 2.0 — uma exposição de segurança significativa.

??? question "**Q5 (Execute o Lab):** Qual servidor MCP tem a maior taxa de erro e qual é ela?"

    Ordene os servidores por `error_rate_pct` em ordem decrescente e inspecione a primeira linha.

    ??? success "✅ Revelar Resposta"
        **legacy-erp com 5,8%**

        O servidor `legacy-erp` (equipe Operations) tem a maior taxa de erro com 5,8%, quase 3× a próxima maior (payment-gateway com 2,1%). Combinado com autenticação basic, sem DLP, sem logging e latência média de 450ms, ele é o servidor de maior risco na frota e deveria ser a prioridade máxima para integração ao APIM.

---

## Resumo

| Tópico | O Que Você Aprendeu |
|--------|---------------------|
| APIM como Gateway | Segurança centralizada, limitação de taxa e monitoramento para MCP |
| OAuth 2.0 | Autenticação baseada em token com identidade, expiração e controle de escopo |
| Políticas de DLP | Inspeção de conteúdo para prevenir vazamento de PII/dados sensíveis |
| Auditoria de Conformidade | Avaliação sistemática da postura de segurança da frota |
| Priorização de Riscos | Planejamento de migração orientado por dados baseado em autenticação, DLP e taxas de erro |

---

## Próximos Passos

- **[Lab 012](lab-012-what-is-mcp.md)** — O Que É MCP? (conceitos fundamentais de MCP)
- **[Lab 028](lab-028-deploy-mcp-azure.md)** — Implantar MCP no Azure (implantar os servidores que o APIM protege)
- **[Lab 036](lab-036-prompt-injection-security.md)** — Segurança contra Prompt Injection (camada de segurança complementar)
