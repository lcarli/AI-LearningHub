---
tags: [enterprise, work-iq, copilot-analytics, python, power-bi, viva-insights, roi]
---
# Lab 048: Work IQ — Análise de Impacto do Copilot e Power BI

<div class="lab-meta">
  <span><strong>Nível:</strong> <span class="level-badge level-300">L300</span></span>
  <span><strong>Trilha:</strong> Todas as trilhas</span>
  <span><strong>Tempo:</strong> ~90 min</span>
  <span><strong>💰 Custo:</strong> <span class="level-badge cost-free">Gratuito</span> — Usa conjuntos de dados mock incluídos (Viva Insights ao vivo requer licença M365 Copilot)</span>
</div>

## O que Você Vai Aprender

- Como a **atribuição de impacto** funciona — conectando o uso do Copilot a resultados de negócios
- Calcular o **valor em dólares do tempo economizado** (ROI) a partir de dados de adoção do Copilot
- Usar **correlação de Pearson** para medir a relação entre uso e KPIs
- Analisar **tendências de adoção mês a mês** para identificar padrões de crescimento
- Escrever uma **narrativa executiva de impacto** que conta uma história baseada em dados
- Entender como essas análises se mapeiam para dashboards do **Power BI** e Relatórios Avançados do Viva Insights

!!! abstract "Pré-requisito"
    Complete o **[Lab 047: Work IQ — Análise de Adoção do Copilot](lab-047-work-iq-copilot-analytics.md)** primeiro. Este lab se baseia nos conceitos de análise de adoção e no cenário da OutdoorGear Inc. do Lab 047.

## Introdução

![Modelo de Atribuição de Impacto](../../assets/diagrams/impact-attribution-model.svg)

No Lab 047, você respondeu _"Quem está usando o Copilot?"_. Agora os executivos querem a pergunta mais difícil respondida: _"Que valor o Copilot está gerando?"_

A **atribuição de impacto** conecta o uso de ferramentas de IA a resultados reais de negócios — crescimento de receita, tempos de resposta mais rápidos, satisfação dos funcionários e entrega de projetos. Esta é a análise que garante o investimento contínuo em IA.

### O Cenário

Três meses se passaram desde que a OutdoorGear Inc. implantou o M365 Copilot. Agora você tem:

1. **Dados de uso do Copilot** — 3 meses de métricas agregadas por departamento (usuários ativos, uso de recursos, tempo economizado)
2. **KPIs de resultados de negócios** — mudança na receita, taxas de resolução de tickets, tempos de resposta, pontuações de satisfação, entrega de projetos

Sua missão: **provar (ou refutar) que o Copilot está impulsionando melhorias mensuráveis nos negócios** — e apresentar suas descobertas ao conselho.

!!! warning "Correlação ≠ Causalidade"
    Este lab ensina você a encontrar **correlações** entre uso e resultados. Correlação NÃO prova que o Copilot *causou* a melhoria — outros fatores (novas contratações, mudanças de processo, sazonalidade) podem contribuir. Sempre apresente as descobertas como "departamentos com maior uso do Copilot *tendem a* mostrar melhores resultados" em vez de "o Copilot *causou* a melhoria."

---

## 📦 Arquivos de Suporte

!!! note "Baixe estes arquivos antes de iniciar o lab"
    Salve todos os arquivos em uma pasta `lab-048/` no seu diretório de trabalho.

| Arquivo | Descrição | Download |
|------|-------------|----------|
| `broken_roi_calculator.py` | Exercício de correção de bugs (3 bugs + autotestes) | [📥 Download](https://github.com/lcarli/AI-LearningHub/raw/main/docs/docs/en/labs/lab-048/broken_roi_calculator.py) |
| `business_outcomes.csv` | Conjunto de dados | [📥 Download](https://github.com/lcarli/AI-LearningHub/raw/main/docs/docs/en/labs/lab-048/business_outcomes.csv) |
| `copilot_quarterly_summary.csv` | Conjunto de dados | [📥 Download](https://github.com/lcarli/AI-LearningHub/raw/main/docs/docs/en/labs/lab-048/copilot_quarterly_summary.csv) |
| `impact_analyzer.py` | Script inicial com TODOs | [📥 Download](https://github.com/lcarli/AI-LearningHub/raw/main/docs/docs/en/labs/lab-048/impact_analyzer.py) |

---

## Passo 1: Entender a Análise de Impacto

Antes de programar, entenda os três pilares da análise de impacto:

| Pilar | O Que Ele Mede | Exemplo |
|--------|-----------------|---------|
| **ROI (Retorno sobre Investimento)** | Valor em dólares do tempo economizado vs. custo da licença | 188 horas economizadas × $50/h = $9.400 |
| **Correlação** | Relação estatística entre uso e resultados | r = 0,97 entre dias ativos e satisfação |
| **Análise de Tendência** | Como a adoção e os resultados mudam ao longo do tempo | 60% de crescimento em usuários ativos em 3 meses |

### Relatórios Avançados do Viva Insights

Em um ambiente M365 ao vivo, os Relatórios Avançados do Viva Insights fornecem:

- **100+ métricas do Copilot** segmentadas por departamento, função, gestor e localização
- **Importação de dados organizacionais** para adicionar atributos personalizados (centro de custo, data de contratação, etc.)
- **Controles de privacidade**: tamanho mínimo de grupo de 5, agregação de dados, acesso baseado em função
- **Modelos Power BI** para dashboards pré-construídos

Neste lab, simulamos essas capacidades com Python e exportações CSV.

!!! tip "Conexão com Power BI"
    Se você tem o Power BI Desktop instalado, pode carregar ambos os CSVs diretamente no Power BI para criar dashboards interativos. Toda a análise que fazemos em Python se mapeia 1:1 para visuais do Power BI: tabelas → matriz, correlações → gráficos de dispersão, tendências → gráficos de linha.

---

## Passo 2: Carregar e Mesclar os Conjuntos de Dados

Você tem dois conjuntos de dados para trabalhar:

**[📥 `copilot_quarterly_summary.csv`](https://github.com/lcarli/AI-LearningHub/raw/main/docs/docs/en/labs/lab-048/copilot_quarterly_summary.csv)** — Dados de uso agregados (21 linhas: 7 departamentos × 3 meses)

| Coluna | Descrição |
|--------|-------------|
| `department` | Nome do departamento |
| `month` | Mês (2026-01, 2026-02, 2026-03) |
| `licensed` / `enabled` / `active_users` | Contagens de usuários |
| `avg_active_days` | Média de dias ativos entre usuários ativos |
| `total_meetings` / `total_emails` / `total_docs` / `total_chats` | Totais por recurso |
| `total_time_saved_min` | Minutos estimados economizados |

**[📥 `business_outcomes.csv`](https://github.com/lcarli/AI-LearningHub/raw/main/docs/docs/en/labs/lab-048/business_outcomes.csv)** — KPIs por departamento (21 linhas: 7 departamentos × 3 meses)

| Coluna | Descrição |
|--------|-------------|
| `revenue_change_pct` | Mudança na receita vs. ano anterior (%) |
| `tickets_resolved_per_person` | Tickets de suporte resolvidos por pessoa |
| `avg_response_hours` | Tempo médio de resposta (horas) |
| `employee_satisfaction` | Pontuação de satisfação (0-100) |
| `projects_on_time_pct` | Projetos entregues no prazo (%) |

Carregue e mescle-os:

```python
import pandas as pd

usage = pd.read_csv("lab-048/copilot_quarterly_summary.csv")
outcomes = pd.read_csv("lab-048/business_outcomes.csv")

# Merge on department + month
merged = pd.merge(usage, outcomes, on=["department", "month"])
print(f"Merged: {len(merged)} rows × {len(merged.columns)} columns")
print(merged.head())
```

**Esperado:** 21 linhas × 17 colunas.

---

## Passo 3: Calcular o ROI — Valor em Dólares do Tempo Economizado

A métrica de ROI mais simples: **quanto vale o tempo economizado?**

```python
HOURLY_RATE = 50  # Average fully-loaded cost per employee-hour

total_minutes = usage["total_time_saved_min"].sum()
total_hours = total_minutes / 60
dollar_value = total_hours * HOURLY_RATE

print(f"Total time saved: {total_minutes:,} minutes")
print(f"                = {total_hours:.1f} hours")
print(f"Dollar value:    = ${dollar_value:,.0f} (at ${HOURLY_RATE}/hr)")
```

**Saída esperada:**

```
Total time saved: 11,280 minutes
                = 188.0 hours
Dollar value:    = $9,400 (at $50/hr)
```

### Detalhamento de ROI por Departamento

```python
dept_roi = usage.groupby("department")["total_time_saved_min"].sum().reset_index()
dept_roi["hours"] = dept_roi["total_time_saved_min"] / 60
dept_roi["dollar_value"] = dept_roi["hours"] * HOURLY_RATE
dept_roi = dept_roi.sort_values("dollar_value", ascending=False)
print(dept_roi[["department", "hours", "dollar_value"]].to_string(index=False))
```

**Saída esperada:**

| Departamento | Horas | Valor em Dólares |
|------------|-------|-------------|
| Engineering | 65,2 | $3.262 |
| Finance | 45,9 | $2.296 |
| Marketing | 34,3 | $1.713 |
| Operations | 19,6 | $979 |
| Sales | 15,5 | $775 |
| HR | 6,4 | $321 |
| Legal | 1,1 | $54 |

!!! tip "Insight"
    Engineering gera o maior valor absoluto ($3.262) porque tem mais usuários. Mas **Finance tem o maior ROI por usuário** — 6 usuários gerando $2.296 vs. 12 usuários de Engineering gerando $3.262. O valor por usuário de Finance é **$383** vs. **$272** de Engineering.

---

## Passo 4: Correlacionar Uso com Resultados de Negócios

Agora a pergunta crítica: **maior uso do Copilot se correlaciona com melhores resultados de negócios?**

```python
# Pearson correlation between average active days and employee satisfaction
correlation = merged["avg_active_days"].corr(merged["employee_satisfaction"])
print(f"Correlation (active_days ↔ satisfaction): {correlation:.3f}")
```

**Saída esperada:**

```
Correlation (active_days ↔ satisfaction): 0.970
```

Uma correlação de **0,970** é extremamente forte. Departamentos com maior média de dias ativos consistentemente apresentam maior satisfação dos funcionários.

### Matriz de Correlação

Verifique múltiplas métricas de resultado de uma vez:

```python
usage_cols = ["avg_active_days", "active_users"]
outcome_cols = ["employee_satisfaction", "revenue_change_pct",
                "projects_on_time_pct", "avg_response_hours"]

corr_matrix = merged[usage_cols + outcome_cols].corr()
print("\nCorrelation with avg_active_days:")
for col in outcome_cols:
    r = corr_matrix.loc["avg_active_days", col]
    direction = "↑ positive" if r > 0 else "↓ negative"
    print(f"  {col:>30s}: r = {r:+.3f}  ({direction})")
```

Você deve ver:

- **employee_satisfaction**: positiva forte (~0,97)
- **revenue_change_pct**: positiva forte
- **projects_on_time_pct**: positiva forte
- **avg_response_hours**: **negativa** forte (maior uso → *menor* tempo de resposta = mais rápido)

!!! warning "Lembre-se: Correlação ≠ Causalidade"
    Uma correlação de 0,97 é impressionante, mas não prova que o Copilot *causou* o aumento de satisfação. Departamentos de alto desempenho podem ter adotado o Copilot mais rapidamente *porque* já eram eficientes. Apresente isso como evidência de uma **relação**, não prova de causalidade.

---

## Passo 5: Análise de Tendência — Crescimento Mês a Mês

Acompanhe como a adoção está crescendo ao longo do tempo:

```python
monthly = usage.groupby("month")["active_users"].sum().reset_index()
monthly.columns = ["Month", "Active Users"]
print(monthly.to_string(index=False))

jan = monthly[monthly["Month"] == "2026-01"]["Active Users"].values[0]
mar = monthly[monthly["Month"] == "2026-03"]["Active Users"].values[0]
growth = (mar - jan) / jan * 100
print(f"\nGrowth (Jan → Mar): {jan} → {mar} = {growth:.1f}%")
```

**Saída esperada:**

```
   Month  Active Users
 2026-01            20
 2026-02            28
 2026-03            32

Growth (Jan → Mar): 20 → 32 = 60.0%
```

### Tendências por Departamento

```python
print("\nDepartment-level growth (Jan → Mar):")
for dept in usage["department"].unique():
    d = usage[usage["department"] == dept]
    j = d[d["month"] == "2026-01"]["active_users"].values[0]
    m = d[d["month"] == "2026-03"]["active_users"].values[0]
    g = ((m - j) / j * 100) if j > 0 else float("inf")
    arrow = "📈" if g > 50 else "📊" if g > 0 else "⚠️"
    print(f"  {arrow} {dept}: {j} → {m} ({g:+.0f}%)")
```

### Melhoria de Satisfação por Departamento

```python
print("\nSatisfaction improvement (Jan → Mar):")
for dept in outcomes["department"].unique():
    d = outcomes[outcomes["department"] == dept]
    j = d[d["month"] == "2026-01"]["employee_satisfaction"].values[0]
    m = d[d["month"] == "2026-03"]["employee_satisfaction"].values[0]
    delta = m - j
    print(f"  {dept:>15s}: {j} → {m}  (Δ = {delta:+d})")
```

**Saída esperada:**

| Departamento | Jan | Mar | Δ |
|------------|-----|-----|---|
| Finance | 75 | 88 | **+13** ← maior |
| Engineering | 72 | 84 | +12 |
| Marketing | 70 | 80 | +10 |
| Operations | 68 | 76 | +8 |
| HR | 62 | 68 | +6 |
| Sales | 65 | 70 | +5 |
| Legal | 58 | 62 | +4 ← menor |

!!! tip "A História Se Escreve Sozinha"
    **Finance** (maior adoção do Copilot com 100%) mostra a **maior melhoria na satisfação (+13)**. **Legal** (menor adoção com 50%) mostra a **menor melhoria (+4)**. Esta é a história de correlação que você apresentará ao conselho.

---

## Passo 6: Construir a Narrativa de Impacto

Combine todas as descobertas em um documento pronto para executivos:

```python
narrative = f"""# 📋 OutdoorGear Inc. — Copilot Impact Report
## Q1 2026 (January – March)

### Executive Summary

Over Q1 2026, Microsoft 365 Copilot adoption at OutdoorGear Inc. grew
**{growth:.0f}%** (from {jan} to {mar} active users). The estimated value of
time saved is **${dollar_value:,.0f}** ({total_hours:.0f} hours at $50/hr).

There is a **strong positive correlation (r = {correlation:.2f})** between
Copilot usage intensity and employee satisfaction — departments with higher
average active days consistently report higher satisfaction scores.

### Key Metrics

| Metric | Value |
|--------|-------|
| Active Users (March) | {mar} of 52 employees |
| Adoption Growth (Q1) | {growth:.0f}% |
| Total Time Saved | {total_hours:.0f} hours |
| Estimated ROI | ${dollar_value:,.0f} |
| Usage ↔ Satisfaction Correlation | r = {correlation:.2f} |

### Department Spotlight: Finance 🏆

Finance achieved **100% adoption** with all 6 employees actively using Copilot
an average of 20.5 days/month. They show the **largest satisfaction improvement
(+13 points)** and the **highest per-user ROI ($383/user)**.

### Top 3 Recommendations

1. **Enable the 7 users in the licensing gap** — Sales has 3 licensed users
   not yet enabled. This is the fastest path to increasing adoption.
2. **Replicate Finance's playbook** — interview the Finance team to understand
   what drove their 100% adoption and apply those practices org-wide.
3. **Targeted training for Legal and HR** — lowest adoption departments
   need hands-on enablement sessions, not just license assignment.
"""

print(narrative)

with open("lab-048/impact_narrative.md", "w") as f:
    f.write(narrative)
print("💾 Saved to lab-048/impact_narrative.md")
```

---

## Passo 7: Dashboard Power BI (Opcional)

Se você tem o **Power BI Desktop** instalado, pode criar uma versão interativa desta análise:

1. **Abra o Power BI Desktop** → Obter Dados → Texto/CSV
2. Carregue `copilot_quarterly_summary.csv` e `business_outcomes.csv`
3. Na visualização de **Modelo**, crie um relacionamento em `department` + `month`
4. Crie estes visuais:

| Tipo de Visual | Eixo X | Eixo Y | Propósito |
|-------------|--------|--------|---------|
| Barras Agrupadas | Department | active_users | Adoção por departamento |
| Gráfico de Linha | Month | active_users | Tendência de adoção |
| Gráfico de Dispersão | avg_active_days | employee_satisfaction | Visualização de correlação |
| Cartão | — | dollar_value | Destaque de ROI |
| Matriz | Department × Month | Todos os KPIs | Detalhamento completo |

!!! info "Sem Power BI? Sem problema"
    A análise em Python acima produz insights idênticos. O Power BI adiciona interatividade (filtragem, drill-down, compartilhamento), mas os dados e fórmulas subjacentes são os mesmos. Se você tem o **matplotlib** instalado, também pode criar gráficos em Python:

    ```python
    # pip install matplotlib
    import matplotlib.pyplot as plt

    fig, axes = plt.subplots(1, 2, figsize=(14, 5))

    # Chart 1: Adoption trend
    monthly.plot(x="Month", y="Active Users", kind="bar", ax=axes[0], color="#3b82f6")
    axes[0].set_title("Copilot Adoption Growth")
    axes[0].set_ylabel("Active Users")

    # Chart 2: Correlation scatter
    axes[1].scatter(merged["avg_active_days"], merged["employee_satisfaction"],
                    c="#8b5cf6", s=60, alpha=0.7)
    axes[1].set_xlabel("Avg Active Days")
    axes[1].set_ylabel("Employee Satisfaction")
    axes[1].set_title(f"Usage vs Satisfaction (r = {correlation:.2f})")

    plt.tight_layout()
    plt.savefig("lab-048/impact_charts.png", dpi=150)
    plt.show()
    print("📊 Charts saved to lab-048/impact_charts.png")
    ```

---

## 🐛 Exercício de Correção de Bugs

O arquivo `lab-048/broken_roi_calculator.py` contém **3 bugs** que produzem análises de impacto incorretas. Execute os autotestes:

```bash
python lab-048/broken_roi_calculator.py
```

Você deve ver **3 testes falhando**:

| Teste | O que ele verifica | Dica |
|------|---------------|------|
| Teste 1 | Cálculo de ROI | Verifique a conversão de unidades (minutos → horas) |
| Teste 2 | Coluna de correlação | Qual coluna realmente mede *uso*? |
| Teste 3 | Base da taxa de crescimento | Qual mês é o *ponto de partida*? |

Corrija os 3 bugs e execute novamente até ver `🎉 All 3 tests passed`.

---


## 🧠 Verificação de Conhecimento

??? question "**Q1 (Múltipla Escolha):** O que significa 'atribuição de impacto' no contexto do Work IQ?"

    - A) Contar quantos usuários têm uma licença Copilot
    - B) Conectar o uso de ferramentas de IA a resultados de negócios mensuráveis
    - C) Rastrear qual departamento tem mais usuários ativos
    - D) Medir o custo total das licenças de IA

    ??? success "✅ Revelar Resposta"
        **Correto: B) Conectar o uso de ferramentas de IA a resultados de negócios mensuráveis**

        A atribuição de impacto vai além das métricas de adoção (quem está usando o Copilot?) para responder à pergunta de ROI: o uso do Copilot está correlacionado com melhores resultados de negócios como crescimento de receita, tempos de resposta mais rápidos e maior satisfação dos funcionários?

??? question "**Q2 (Múltipla Escolha):** Por que o princípio 'correlação ≠ causalidade' é crítico ao apresentar o ROI do Copilot para a liderança?"

    - A) Porque correlações são sempre não confiáveis
    - B) Porque outros fatores podem explicar as melhorias de negócios
    - C) Porque os dados de uso do Copilot não são precisos
    - D) Porque a liderança não entende estatística

    ??? success "✅ Revelar Resposta"
        **Correto: B) Porque outros fatores podem explicar as melhorias de negócios**

        Departamentos de alto desempenho podem adotar ferramentas de IA mais rapidamente porque já são bem gerenciados — a melhoria pode ser devida à qualidade da liderança, contratações, mudanças de processo ou tendências sazonais. Sempre apresente as descobertas como "departamentos com maior uso *tendem a* mostrar melhores resultados" em vez de afirmar causalidade direta.

??? question "**Q3 (Execute o Lab):** Qual é o valor total estimado em dólares do tempo economizado em todos os departamentos durante o Q1 2026 (a $50/h)?"

    Calcule: some todos os valores de `total_time_saved_min`, converta para horas, multiplique por $50.

    ??? success "✅ Revelar Resposta"
        **$9.400**

        Tempo total economizado: 11.280 minutos ÷ 60 = 188,0 horas × $50/h = **$9.400**. Engineering contribui com o maior valor absoluto ($3.262), mas Finance tem o maior ROI por usuário ($383/usuário).

??? question "**Q4 (Execute o Lab):** Qual departamento mostra a maior melhoria na satisfação dos funcionários de janeiro a março de 2026?"

    Compare as pontuações de `employee_satisfaction` de janeiro e março de cada departamento.

    ??? success "✅ Revelar Resposta"
        **Finance (+13 pontos: 75 → 88)**

        Finance melhorou de 75 para 88, um delta de +13. Isso se alinha com Finance tendo a maior taxa de adoção do Copilot (100%). Engineering é o segundo com +12 (72 → 84). Legal mostra a menor melhoria (+4), correspondendo à sua baixa adoção.

??? question "**Q5 (Execute o Lab):** Qual é a taxa geral de crescimento de adoção de janeiro a março de 2026?"

    Some `active_users` para janeiro e março em todos os departamentos, e então calcule o crescimento percentual.

    ??? success "✅ Revelar Resposta"
        **60,0%**

        Janeiro: 6+4+2+1+4+0+3 = **20** usuários ativos. Março: 9+6+4+2+6+1+4 = **32** usuários ativos. Crescimento = (32 − 20) ÷ 20 × 100 = **60,0%**.

---

## Resumo

| Tópico | O Que Você Aprendeu |
|-------|-----------------|
| Atribuição de Impacto | Conectando dados de uso a KPIs de negócios |
| Cálculo de ROI | Tempo economizado → horas → valor em dólares |
| Correlação de Pearson | Medindo relações estatísticas (r = 0,97) |
| Análise de Tendência | Crescimento de adoção mês a mês (60%) |
| Narrativa de Impacto | Storytelling pronto para executivos com dados |
| Mapeamento Power BI | Como a análise Python se mapeia para visuais do Power BI |

---

## Próximos Passos

- **[Lab 033](lab-033-agent-observability.md)** — Observabilidade de Agentes com Application Insights (monitorando agentes personalizados da mesma forma que o Viva monitora o Copilot)
- **[Lab 038](lab-038-cost-optimization.md)** — Otimização de Custos de IA (o lado financeiro do ROI para implantações personalizadas de IA)
- **[Lab 035](lab-035-agent-evaluation.md)** — Avaliação de Agentes com Azure AI Eval SDK (métricas de qualidade, não apenas adoção)
