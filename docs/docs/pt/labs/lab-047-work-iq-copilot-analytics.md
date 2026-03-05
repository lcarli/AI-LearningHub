---
tags: [enterprise, work-iq, copilot-analytics, python, viva-insights, m365]
---
# Lab 047: Work IQ — Análise de Adoção do Copilot

<div class="lab-meta">
  <span><strong>Nível:</strong> <span class="level-badge level-200">L200</span></span>
  <span><strong>Trilha:</strong> Todas as trilhas</span>
  <span><strong>Tempo:</strong> ~45 min</span>
  <span><strong>💰 Custo:</strong> <span class="level-badge cost-free">Gratuito</span> — Usa conjunto de dados mock incluído (Viva Insights ao vivo requer licença M365 Copilot)</span>
</div>

## O que Você Vai Aprender

- O que é **Work IQ** e por que a análise de adoção é importante para implantações de IA
- Como ler e interpretar dados de uso do Copilot do Viva Insights e do Centro de Administração do M365
- Analisar taxas de adoção por departamento usando Python e pandas
- Identificar **bloqueadores de adoção**: lacunas de licenciamento, lacunas de habilitação e baixo engajamento
- Construir um **scorecard de implantação** que transforma dados brutos em um resumo executivo

## Introdução

![Work IQ Analytics Flow](../../assets/diagrams/work-iq-analytics-flow.svg)

**Work IQ** é o framework da Microsoft para medir e otimizar a adoção de IA em uma organização. À medida que as empresas passam de *implantar* o Microsoft 365 Copilot para *provar o ROI*, a capacidade de analisar dados de adoção se torna uma habilidade crítica.

Em 2025-2026, a pergunta mudou de _"Implantamos o Copilot?"_ para _"Ele está realmente sendo usado? Por quem? Para quê? E que valor está criando?"_

### O Cenário

Você é o **Líder de Adoção de IA** na OutdoorGear Inc. A empresa implantou o M365 Copilot para 52 funcionários em 7 departamentos há três meses. A liderança quer respostas:

1. Quais departamentos estão realmente usando o Copilot?
2. Onde as licenças estão sendo desperdiçadas — e por quê?
3. Quais recursos as pessoas mais usam?
4. Quanto tempo o Copilot economizou para a organização?

Você tem uma **exportação de dados de uso** (semelhante ao que o Viva Insights e o Centro de Administração do M365 fornecem). Seu trabalho: transformar dados brutos em um **scorecard de adoção** acionável.

!!! info "Dados Reais vs. Mock"
    Este lab usa um **conjunto de dados mock** (`copilot_usage_data.csv`) para que qualquer pessoa possa acompanhar sem uma licença M365 Copilot. A estrutura dos dados espelha o que você veria nas exportações do Viva Insights. Se você tiver um ambiente M365 ativo, pode substituir com seus próprios dados.

## Pré-requisitos

| Requisito | Por quê |
|---|---|
| Python 3.10+ | Executar os scripts de análise |
| Biblioteca `pandas` | Manipulação de dados |
| (Opcional) Licença M365 Copilot + Viva Insights | Para dados reais em vez de mock |

```bash
pip install pandas
```

---

!!! tip "Início Rápido com GitHub Codespaces"
    [![Open in GitHub Codespaces](https://github.com/codespaces/badge.svg)](https://codespaces.new/lcarli/AI-LearningHub?quickstart=1)

    Todas as dependências estão pré-instaladas no devcontainer.


## 📦 Arquivos de Suporte

!!! note "Baixe estes arquivos antes de iniciar o lab"
    Salve todos os arquivos em uma pasta `lab-047/` no seu diretório de trabalho.

| Arquivo | Descrição | Download |
|------|-------------|----------|
| `broken_scorecard.py` | Exercício de correção de bugs (3 bugs + autotestes) | [📥 Download](https://github.com/lcarli/AI-LearningHub/raw/main/docs/docs/en/labs/lab-047/broken_scorecard.py) |
| `copilot_usage_data.csv` | Conjunto de dados | [📥 Download](https://github.com/lcarli/AI-LearningHub/raw/main/docs/docs/en/labs/lab-047/copilot_usage_data.csv) |
| `scorecard_builder.py` | Script inicial com TODOs | [📥 Download](https://github.com/lcarli/AI-LearningHub/raw/main/docs/docs/en/labs/lab-047/scorecard_builder.py) |

---

## Passo 1: Entenda as Métricas Principais

Antes de mexer nos dados, você precisa entender o que o Work IQ mede. Estas são as mesmas métricas rastreadas pelo Viva Insights e pelo Centro de Administração do M365:

| Métrica | O que Mede | Por que Importa |
|--------|-----------------|----------------|
| **Licensed** | Usuário tem uma licença M365 Copilot atribuída | Licença ≠ uso; rastreia alocação de investimento |
| **Enabled** | Admin ativou o Copilot para o usuário | Lacuna entre licenciado e habilitado = gasto desperdiçado |
| **Active Days** | Dias em que o usuário interagiu com qualquer recurso do Copilot | Mede profundidade de engajamento, não apenas teste único |
| **Meetings Assisted** | Reuniões onde o Copilot gerou resumos/ações | Caso de uso de alto valor para gerentes |
| **Emails Drafted** | E-mails compostos ou refinados com ajuda do Copilot | Mede produtividade de escrita |
| **Docs Summarized** | Documentos resumidos ou analisados pelo Copilot | Mede eficiência no trabalho de conhecimento |
| **Chats** | Interações do Copilot Chat (perguntas, brainstorming) | Mede exploração e utilidade diária |
| **Time Saved (min)** | Minutos estimados economizados pelo Copilot | A métrica definitiva de ROI |

### Fórmulas Principais

```
Adoption Rate = (Active Users ÷ Enabled Users) × 100

Enablement Gap = Licensed Users − Enabled Users
    → Users with a paid license that admins haven't turned on

Licensing Gap = Total Users − Licensed Users
    → Users without any Copilot license at all
```

!!! warning "Privacidade do Viva Insights"
    No Viva Insights em produção, um **tamanho mínimo de grupo de 5 usuários** é aplicado para todos os relatórios. Você não pode detalhar departamentos menores que 5. Nossos dados mock ignoram isso para fins de aprendizado, mas tenha isso em mente para implantações reais.

---

## Passo 2: Carregue e Explore o Conjunto de Dados

O conjunto de dados tem **52 registros de usuários** em 7 departamentos. Comece carregando-o em Python:

```python
import pandas as pd

df = pd.read_csv("lab-047/copilot_usage_data.csv")

# Convert string booleans to Python booleans
for col in ["licensed", "enabled"]:
    df[col] = df[col].astype(str).str.strip().str.lower() == "true"

print(f"Total records: {len(df)}")
print(f"Departments: {df['department'].nunique()}")
print(f"\nColumn types:\n{df.dtypes}")
print(f"\nFirst 5 rows:\n{df.head()}")
```

**Saída esperada:**

```
Total records: 52
Departments: 7
```

Reserve um momento para explorar:

```python
# Quick summary by department
summary = df.groupby("department").agg(
    total=("user_id", "count"),
    licensed=("licensed", "sum"),
    enabled=("enabled", "sum"),
).reset_index()
print(summary)
```

??? question "**🤔 Antes de continuar:** Qual departamento você *prevê* que terá a maior taxa de adoção?"

    Pense nisso — depois continue para o Passo 3 para descobrir se você acertou!

---

## Passo 3: Calcule as Taxas de Adoção por Departamento

Agora calcule a taxa de adoção para cada departamento. Lembre-se: **taxa de adoção = usuários ativos ÷ usuários habilitados × 100**.

Um usuário "ativo" é qualquer pessoa com `active_days > 0` (usou o Copilot pelo menos uma vez durante o mês).

```python
results = []
for dept, group in df.groupby("department"):
    total = len(group)
    licensed = group["licensed"].sum()
    enabled = group["enabled"].sum()
    active = len(group[(group["enabled"] == True) & (group["active_days"] > 0)])
    rate = (active / enabled * 100) if enabled > 0 else 0

    results.append({
        "Department": dept,
        "Total": total,
        "Licensed": licensed,
        "Enabled": enabled,
        "Active": active,
        "Adoption %": round(rate, 1),
    })

adoption_df = pd.DataFrame(results).sort_values("Adoption %", ascending=False)
print(adoption_df.to_string(index=False))
```

**Saída esperada:**

| Department | Total | Licensed | Enabled | Active | Adoption % |
|------------|-------|----------|---------|--------|------------|
| Finance | 6 | 6 | 6 | 6 | 100.0 |
| Engineering | 12 | 11 | 10 | 9 | 90.0 |
| Marketing | 8 | 8 | 7 | 6 | 85.7 |
| Operations | 7 | 6 | 5 | 4 | 80.0 |
| Sales | 10 | 8 | 5 | 4 | 80.0 |
| HR | 5 | 3 | 3 | 2 | 66.7 |
| Legal | 4 | 3 | 2 | 1 | 50.0 |

!!! tip "Insight"
    **Finance lidera com 100%** — cada usuário habilitado está ativo. **Legal está em 50%** — apenas 1 de 2 usuários habilitados já abriu o Copilot. Mas observe que Legal também tem o menor número de usuários habilitados (2). Tamanhos de amostra pequenos podem ser enganosos — é por isso que o Viva Insights aplica um tamanho mínimo de grupo de 5.

---

## Passo 4: Identifique os Bloqueadores de Adoção

Três tipos de bloqueadores impedem a adoção do Copilot:

### 4a — Lacuna de Habilitação (Licenciado mas NÃO Habilitado)

```python
gap = df[(df["licensed"] == True) & (df["enabled"] == False)]
print(f"Enablement gap: {len(gap)} users\n")
print(gap[["department", "user_id"]].to_string(index=False))
```

**Saída esperada:**

```
Enablement gap: 7 users

  department user_id
 Engineering ENG-011
   Marketing MKT-008
       Sales SLS-004
       Sales SLS-005
       Sales SLS-006
       Legal LEG-003
  Operations OPS-006
```

!!! warning "O Problema de Sales"
    **Sales tem 3 usuários licenciados presos na lacuna de habilitação** — isso é 37,5% dos seus usuários licenciados! Provavelmente é um descuido administrativo. Um ticket para TI poderia desbloquear mais 3 usuários ativos.

### 4b — Lacuna de Licenciamento (Sem Licença)

```python
unlicensed = df[df["licensed"] == False]
print(f"Unlicensed users: {len(unlicensed)}")
print(unlicensed.groupby("department")["user_id"].count())
```

### 4c — Usuários com Zero Uso (Habilitados mas Nunca Usaram)

```python
zero_usage = df[(df["enabled"] == True) & (df["active_days"] == 0)]
print(f"Enabled but never used: {len(zero_usage)} users")
print(zero_usage[["department", "user_id"]].to_string(index=False))
```

Esses usuários têm o Copilot disponível mas não o utilizaram. Eles podem precisar de treinamento, campanhas de conscientização ou um incentivo do gerente.

---

## Passo 5: Análise de Uso de Recursos

Quais recursos do Copilot geram mais valor na OutdoorGear?

```python
active = df[df["active_days"] > 0]

features = {
    "Meetings Assisted": active["meetings_assisted"].sum(),
    "Emails Drafted": active["emails_drafted"].sum(),
    "Docs Summarized": active["docs_summarized"].sum(),
    "Chats": active["chats"].sum(),
}

print("Feature Usage (total interactions among active users):")
for feat, count in sorted(features.items(), key=lambda x: x[1], reverse=True):
    pct = count / sum(features.values()) * 100
    print(f"  {feat:>20s}: {count:>5d}  ({pct:.1f}%)")
```

**Saída esperada:**

| Recurso | Total | Participação |
|---------|-------|-------|
| Chats | 400 | 32,8% |
| Meetings Assisted | 303 | 24,8% |
| Emails Drafted | 260 | 21,3% |
| Docs Summarized | 257 | 21,1% |

!!! tip "Insight"
    **Chats dominam** com 32,8% — os usuários estão usando o Copilot principalmente para perguntas e respostas, brainstorming e consultas rápidas. Reuniões são o segundo recurso mais usado, impulsionado por Finance e Engineering, onde gerentes dependem de resumos de reuniões.

---

## Passo 6: Construa o Scorecard

Agora combine toda a sua análise em um único **Scorecard de Adoção** para a liderança:

```python
total_time = int(active["time_saved_min"].sum())

scorecard = f"""# 📊 OutdoorGear Inc. — Copilot Adoption Scorecard

**Reporting Period:** March 2026 (1-month snapshot)

## Overall Metrics
| Metric | Value |
|--------|-------|
| Total Users | {len(df)} |
| Licensed | {df['licensed'].sum()} |
| Enabled | {df['enabled'].sum()} |
| Active | {len(active)} |
| Overall Adoption Rate | {len(active) / df['enabled'].sum() * 100:.1f}% |
| Time Saved | {total_time} min ({total_time / 60:.1f} hours) |
| Enablement Gap | {len(gap)} users |

## Department Ranking
{adoption_df.to_markdown(index=False)}

## Top Actions
1. **Close the Sales enablement gap** — 3 licensed users not yet enabled
2. **Investigate Legal adoption** — only 1 of 2 enabled users is active
3. **Scale Finance's success** — 100% adoption; learn what they're doing right
4. **Run training for zero-usage users** — {len(zero_usage)} enabled users never opened Copilot
"""

print(scorecard)

with open("lab-047/scorecard_report.md", "w") as f:
    f.write(scorecard)
print("💾 Saved to lab-047/scorecard_report.md")
```

---

## 🐛 Exercício de Correção de Bugs

O arquivo `lab-047/broken_scorecard.py` contém **3 bugs** que produzem métricas de adoção incorretas. Você consegue encontrar e corrigir todos?

Execute os autotestes para ver quais falham:

```bash
python lab-047/broken_scorecard.py
```

Você deve ver **3 testes falhando**. Cada teste corresponde a um bug:

| Teste | O que verifica | Dica |
|------|---------------|------|
| Teste 1 | Denominador da taxa de adoção | Deve usar usuários habilitados, não total de usuários |
| Teste 2 | Lógica do filtro da lacuna de habilitação | Verifique as condições booleanas |
| Teste 3 | Fator de conversão de tempo | Conversão de minutos → horas |

Corrija todos os 3 bugs e execute novamente. Quando você vir `🎉 All 3 tests passed`, está pronto!

---


## 🧠 Verificação de Conhecimento

??? question "**Q1 (Múltipla Escolha):** No Microsoft Viva Insights, qual é o tamanho mínimo padrão de grupo para proteger a privacidade dos funcionários?"

    - A) 3 usuários
    - B) 5 usuários
    - C) 10 usuários
    - D) 25 usuários

    ??? success "✅ Revelar Resposta"
        **Correto: B) 5 usuários**

        O Viva Insights aplica um tamanho mínimo de grupo de **5** por padrão. Relatórios para grupos menores que 5 são suprimidos para evitar a identificação de padrões de uso individuais. Administradores podem aumentar (mas não diminuir) esse limite.

??? question "**Q2 (Múltipla Escolha):** Qual métrica melhor indica que os usuários estão usando o Copilot *consistentemente* ao longo do tempo, em vez de apenas experimentá-lo uma vez?"

    - A) Total de e-mails redigidos
    - B) Número de usuários licenciados
    - C) Média mensal de dias ativos
    - D) Tempo economizado em minutos

    ??? success "✅ Revelar Resposta"
        **Correto: C) Média mensal de dias ativos**

        Uma contagem alta de dias ativos significa que o usuário retorna ao Copilot dia após dia — isso mede **aderência** e **formação de hábito**, não apenas um teste único. Total de e-mails ou tempo economizado pode ser inflado por um único dia de uso intenso.

??? question "**Q3 (Execute o Lab):** Qual departamento tem a maior taxa de adoção do Copilot (ativos ÷ habilitados × 100)?"

    Execute a análise do Passo 3 em [📥 `copilot_usage_data.csv`](https://github.com/lcarli/AI-LearningHub/raw/main/docs/docs/en/labs/lab-047/copilot_usage_data.csv) e verifique os resultados.

    ??? success "✅ Revelar Resposta"
        **Finance — 100,0%**

        Finance tem 6 licenciados, 6 habilitados e 6 usuários ativos — cada usuário habilitado está usando o Copilot ativamente. Isso torna Finance o departamento modelo para escalar as melhores práticas de adoção para outras equipes.

??? question "**Q4 (Execute o Lab):** Quantos usuários em toda a organização estão na 'lacuna de habilitação' (licensed = true, enabled = false)?"

    Execute a análise do Passo 4a para descobrir.

    ??? success "✅ Revelar Resposta"
        **7 usuários**

        Os 7 usuários na lacuna de habilitação são: ENG-011, MKT-008, SLS-004, SLS-005, SLS-006, LEG-003 e OPS-006. Sales sozinho representa 3 deles — a vitória mais rápida para melhorar a adoção geral é habilitar esses usuários.

??? question "**Q5 (Execute o Lab):** Quantos 'power users' existem (funcionários com `active_days >= 20`)?"

    Filtre o conjunto de dados para usuários com 20+ dias ativos e conte-os.

    ??? success "✅ Revelar Resposta"
        **10 power users**

        - Engineering: ENG-001 (22), ENG-002 (20), ENG-004 (21), ENG-007 (23), ENG-009 (20) → 5
        - Marketing: MKT-003 (20) → 1
        - Finance: FIN-001 (22), FIN-002 (21), FIN-003 (20), FIN-005 (23) → 4
        - **Total: 10 power users** em Engineering, Marketing e Finance

---

## Resumo

| Tópico | O que Você Aprendeu |
|-------|-----------------|
| Work IQ | Framework para medir adoção de IA e provar ROI |
| Taxa de Adoção | ativos ÷ habilitados × 100 — a principal métrica de saúde |
| Lacuna de Habilitação | Licenciado mas não habilitado — a correção mais rápida para baixa adoção |
| Mix de Recursos | Quais recursos do Copilot geram mais valor |
| Tempo Economizado | Converter minutos em impacto de negócios para a liderança |
| Scorecard | Combinar métricas em um relatório pronto para executivos |

---

## Próximos Passos

- **[Lab 048](lab-048-work-iq-power-bi.md)** *(em breve)* — Construa dashboards avançados no Power BI com Relatórios Avançados do Viva Insights
- **[Lab 033](lab-033-agent-observability.md)** — Observabilidade de Agentes com Application Insights (mentalidade de análise similar para agentes personalizados)
- **[Lab 035](lab-035-agent-evaluation.md)** — Avaliação de Agentes com Azure AI Eval SDK (medindo qualidade do agente, não apenas adoção)
- **[Lab 038](lab-038-cost-optimization.md)** — Otimização de Custos de IA (o lado financeiro do ROI)
