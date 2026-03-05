---
tags: [power-bi, copilot, fabric, dax, analytics, low-code]
---
# Lab 075: Power BI Copilot — Análise Autônoma e Storytelling com Dados

<div class="lab-meta">
  <span><strong>Nível:</strong> <span class="level-badge level-100">L100</span></span>
  <span><strong>Trilha:</strong> Todas as trilhas</span>
  <span><strong>Tempo:</strong> ~45 min</span>
  <span><strong>💰 Custo:</strong> <span class="level-badge cost-free">Gratuito</span> — Usa dados fictícios de relatório</span>
</div>

## O que Você Vai Aprender

- O que é o **Power BI Copilot** e como ele transforma a criação de relatórios com linguagem natural
- Como relatórios assistidos e gerados pelo Copilot se comparam à criação manual
- Analisar um conjunto de dados de relatórios para medir **economia de tempo**, **precisão** e **adoção** entre departamentos
- Entender como a geração de medidas DAX funciona com o Copilot
- Construir um **relatório de impacto** quantificando o valor do Copilot para a equipe de análise

## Introdução

O **Power BI Copilot** traz IA generativa diretamente para a experiência do Power BI dentro do Microsoft Fabric. Analistas e usuários de negócio podem:

- **Criar relatórios** descrevendo o que desejam em linguagem natural
- **Gerar medidas DAX** sem memorizar sintaxe complexa
- **Construir narrativas** que resumem automaticamente os principais insights
- **Fazer perguntas** sobre seus dados usando consultas conversacionais

### Métodos de Criação

| Método | Quem | Como Funciona | Tempo Típico |
|--------|------|---------------|--------------|
| **Manual** | Analista | Constrói cada visual manualmente, escreve DAX à mão | 2–4 horas |
| **Assistido pelo Copilot** | Analista | Analista inicia; Copilot sugere visuais, gera DAX | 1–2 horas |
| **Gerado pelo Copilot** | Usuário de Negócio | Descreve o relatório em linguagem natural; Copilot o constrói | 15–30 min |

### O Cenário

Você é um **Líder da Equipe de BI** em uma empresa de médio porte. Sua equipe vem testando o Power BI Copilot há 3 meses. Você tem **10 relatórios** em 4 departamentos — alguns manuais, alguns assistidos pelo Copilot e alguns totalmente gerados pelo Copilot. A liderança quer saber: _"O Copilot está realmente economizando tempo? A qualidade é aceitável?"_

Seu conjunto de dados (`powerbi_reports.csv`) tem as respostas. Seu trabalho: analisar os dados e construir um relatório de impacto convincente.

!!! info "Dados Fictícios"
    Este laboratório usa um conjunto de dados fictício de relatórios. Os dados refletem padrões do mundo real: relatórios gerados pelo Copilot são mais rápidos, mas ligeiramente menos precisos; relatórios assistidos pelo Copilot combinam velocidade com qualidade de nível analista.

## Pré-requisitos

| Requisito | Por quê |
|---|---|
| Python 3.10+ | Executar os scripts de análise |
| Biblioteca `pandas` | Manipulação de dados |

```bash
pip install pandas
```

---

!!! tip "Início Rápido com GitHub Codespaces"
    [![Open in GitHub Codespaces](https://github.com/codespaces/badge.svg)](https://codespaces.new/lcarli/AI-LearningHub?quickstart=1)

    Todas as dependências estão pré-instaladas no devcontainer.


## 📦 Arquivos de Apoio

!!! note "Baixe estes arquivos antes de iniciar o laboratório"
    Salve todos os arquivos em uma pasta `lab-075/` no seu diretório de trabalho.

| Arquivo | Descrição | Download |
|---------|-----------|----------|
| `broken_powerbi.py` | Exercício de correção de bugs (3 bugs + autotestes) | [📥 Download](https://github.com/lcarli/AI-LearningHub/raw/main/docs/docs/en/labs/lab-075/broken_powerbi.py) |
| `powerbi_reports.csv` | Conjunto de dados | [📥 Download](https://github.com/lcarli/AI-LearningHub/raw/main/docs/docs/en/labs/lab-075/powerbi_reports.csv) |

---

## Etapa 1: Entenda as Métricas

Antes de analisar, entenda o que cada coluna no conjunto de dados mede:

| Coluna | Descrição |
|--------|-----------|
| **created_by** | `analyst` ou `business_user` — quem construiu o relatório |
| **creation_method** | `manual`, `copilot_assisted` ou `copilot_generated` |
| **pages** | Número de páginas do relatório |
| **visuals** | Total de elementos visuais (gráficos, tabelas, cartões) |
| **dax_measures** | Número de medidas DAX no modelo de dados |
| **copilot_queries** | Número de interações com o Copilot usadas durante a criação |
| **time_saved_min** | Minutos estimados economizados em comparação com a criação totalmente manual |
| **accuracy_score** | Pontuação de qualidade (0.0–1.0) baseada em revisão de precisão dos dados |

### Fórmulas Principais

```
Taxa de Adoção do Copilot = (Relatórios com Copilot ÷ Total de relatórios) × 100

Tempo Médio Economizado = Soma(time_saved_min para relatórios com copilot) ÷ Contagem(relatórios com copilot)

Diferença de Qualidade = Precisão média(manual) − Precisão média(copilot_generated)
```

---

## Etapa 2: Carregue e Explore o Conjunto de Dados

O conjunto de dados tem **10 relatórios** em 4 departamentos:

```python
import pandas as pd

df = pd.read_csv("lab-075/powerbi_reports.csv")

print(f"Total reports: {len(df)}")
print(f"Creation methods: {df['creation_method'].value_counts().to_dict()}")
print(f"Departments: {df['department'].unique().tolist()}")
print(f"\nAll reports:")
print(df[["report_id", "report_name", "creation_method", "time_saved_min", "accuracy_score"]].to_string(index=False))
```

**Saída esperada:**

```
Total reports: 10
Creation methods: {'copilot_assisted': 4, 'copilot_generated': 4, 'manual': 2}
Departments: ['Sales', 'Marketing', 'Operations', 'HR', 'Finance']
```

---

## Etapa 3: Meça a Adoção do Copilot

Quantos relatórios usaram o Copilot de alguma forma?

```python
copilot_reports = df[df["creation_method"].isin(["copilot_assisted", "copilot_generated"])]
manual_reports = df[df["creation_method"] == "manual"]

copilot_count = len(copilot_reports)
total = len(df)
adoption_rate = copilot_count / total * 100

print(f"Copilot-assisted/generated reports: {copilot_count}")
print(f"Manual reports:                     {len(manual_reports)}")
print(f"Copilot adoption rate:              {adoption_rate:.0f}%")
```

**Saída esperada:**

```
Copilot-assisted/generated reports: 8
Manual reports:                     2
Copilot adoption rate:              80%
```

Detalhamento por método de criação:

```python
for method, group in df.groupby("creation_method"):
    print(f"\n{method}:")
    print(f"  Reports: {len(group)}")
    print(f"  Avg pages: {group['pages'].mean():.1f}")
    print(f"  Avg visuals: {group['visuals'].mean():.1f}")
    print(f"  Avg DAX measures: {group['dax_measures'].mean():.1f}")
```

!!! tip "Insight"
    **80% dos relatórios** agora usam o Copilot — um forte sinal de adoção. Relatórios manuais tendem a ter mais páginas e visuais, sugerindo que dashboards complexos ainda são construídos manualmente. Relatórios gerados pelo Copilot são menores, mas criados por usuários de negócio que não conseguiriam criá-los de outra forma.

---

## Etapa 4: Calcule a Economia de Tempo

A coluna `time_saved_min` estima quanto tempo o Copilot economizou em comparação com a criação totalmente manual:

```python
total_time_saved = df["time_saved_min"].sum()
copilot_time_saved = copilot_reports["time_saved_min"].sum()
avg_time_saved = copilot_reports["time_saved_min"].mean()

print(f"Total time saved (all reports):      {total_time_saved} min")
print(f"Total time saved (copilot reports):  {copilot_time_saved} min")
print(f"Avg time saved per copilot report:   {avg_time_saved:.1f} min")
print(f"Total hours saved:                   {total_time_saved / 60:.1f} hours")
```

**Saída esperada:**

```
Total time saved (all reports):      395 min
Total time saved (copilot reports):  395 min
Avg time saved per copilot report:   49.4 min
Total hours saved:                   6.6 hours
```

Detalhamento por método:

```python
for method in ["copilot_assisted", "copilot_generated"]:
    subset = df[df["creation_method"] == method]
    print(f"\n{method}:")
    print(f"  Total saved: {subset['time_saved_min'].sum()} min")
    print(f"  Avg saved:   {subset['time_saved_min'].mean():.1f} min")
```

---

## Etapa 5: Avalie a Qualidade e Precisão

Economia de tempo não tem sentido se a qualidade for prejudicada. Compare as pontuações de precisão:

```python
for method in df["creation_method"].unique():
    subset = df[df["creation_method"] == method]
    avg_acc = subset["accuracy_score"].mean()
    print(f"  {method:>20s}: avg accuracy = {avg_acc:.2f}")
```

**Saída esperada:**

```
              manual: avg accuracy = 0.96
    copilot_assisted: avg accuracy = 0.94
   copilot_generated: avg accuracy = 0.85
```

```python
# Quality gap analysis
manual_acc = manual_reports["accuracy_score"].mean()
assisted_acc = df[df["creation_method"] == "copilot_assisted"]["accuracy_score"].mean()
generated_acc = df[df["creation_method"] == "copilot_generated"]["accuracy_score"].mean()

print(f"\nQuality gap (manual vs. assisted):  {(manual_acc - assisted_acc) * 100:.1f}pp")
print(f"Quality gap (manual vs. generated): {(manual_acc - generated_acc) * 100:.1f}pp")
```

!!! warning "Compensação de Qualidade"
    **Relatórios assistidos pelo Copilot** (analista + Copilot) alcançam **0.94 de precisão** — apenas 2pp abaixo do manual. **Relatórios gerados pelo Copilot** (usuário de negócio + Copilot) pontuam **0.85** — aceitável para exploração, mas pode necessitar de revisão do analista antes da distribuição executiva.

---

## Etapa 6: Construa o Relatório de Impacto

```python
total_copilot_queries = copilot_reports["copilot_queries"].sum()

report = f"""# 📊 Power BI Copilot Impact Report

## Adoption Summary
| Metric | Value |
|--------|-------|
| Total Reports | {len(df)} |
| Copilot Reports | {copilot_count} ({adoption_rate:.0f}%) |
| Manual Reports | {len(manual_reports)} |
| Total Copilot Queries | {total_copilot_queries} |

## Time Savings
| Metric | Value |
|--------|-------|
| Total Time Saved | {total_time_saved} min ({total_time_saved / 60:.1f} hours) |
| Avg per Copilot Report | {avg_time_saved:.1f} min |
| Copilot-Assisted Avg | {df[df['creation_method']=='copilot_assisted']['time_saved_min'].mean():.1f} min |
| Copilot-Generated Avg | {df[df['creation_method']=='copilot_generated']['time_saved_min'].mean():.1f} min |

## Quality Assessment
| Method | Avg Accuracy | Rating |
|--------|-------------|--------|
| Manual | {manual_acc:.2f} | ⭐⭐⭐ Gold standard |
| Copilot-Assisted | {assisted_acc:.2f} | ⭐⭐⭐ Production-ready |
| Copilot-Generated | {generated_acc:.2f} | ⭐⭐ Review recommended |

## Recommendations
1. **Encourage Copilot-assisted** for analyst-built reports — saves ~41 min with near-manual quality
2. **Use Copilot-generated** for exploratory/departmental reports — saves ~58 min, good for self-service
3. **Add review step** for Copilot-generated reports going to executives — accuracy gap of {(manual_acc - generated_acc) * 100:.0f}pp
4. **Track DAX measure accuracy** — Copilot-generated DAX may need validation for complex calculations
"""

print(report)

with open("lab-075/impact_report.md", "w") as f:
    f.write(report)
print("💾 Saved to lab-075/impact_report.md")
```

---

## 🐛 Exercício de Correção de Bugs

O arquivo `lab-075/broken_powerbi.py` contém **3 bugs** que produzem métricas incorretas do Power BI. Você consegue encontrar e corrigir todos?

Execute os autotestes para ver quais falham:

```bash
python lab-075/broken_powerbi.py
```

Você deve ver **3 testes com falha**. Cada teste corresponde a um bug:

| Teste | O que verifica | Dica |
|-------|---------------|------|
| Teste 1 | Contagem de relatórios do Copilot | Deve contar métodos do copilot, não `manual` |
| Teste 2 | Tempo total economizado | Deve somar `time_saved_min`, não calcular a média |
| Teste 3 | Precisão média por método | Deve filtrar por método antes de calcular a média |

Corrija todos os 3 bugs e execute novamente. Quando você vir `All passed!`, está feito!

---


## 🧠 Verificação de Conhecimento

??? question "**Q1 (Múltipla Escolha):** Qual é a principal diferença entre a criação de relatórios 'copilot_assisted' e 'copilot_generated'?"

    - A) Copilot-assisted usa um modelo diferente do copilot-generated
    - B) Copilot-assisted é iniciado por um analista que usa o Copilot como auxílio; copilot-generated é criado inteiramente a partir de uma descrição em linguagem natural
    - C) Relatórios copilot-generated são sempre mais precisos
    - D) Relatórios copilot-assisted não podem incluir medidas DAX

    ??? success "✅ Revelar Resposta"
        **Correta: B) Copilot-assisted é iniciado por um analista que usa o Copilot como auxílio; copilot-generated é criado inteiramente a partir de uma descrição em linguagem natural**

        No modo copilot-assisted, um analista conduz o processo e usa o Copilot para sugerir visuais, gerar DAX ou criar resumos narrativos. No modo copilot-generated, um usuário de negócio descreve o relatório desejado em linguagem natural e o Copilot o constrói do zero — mais rápido, mas com menos supervisão humana.

??? question "**Q2 (Múltipla Escolha):** Por que relatórios copilot-generated podem precisar de uma etapa de revisão antes da distribuição executiva?"

    - A) Eles usam visuais demais
    - B) Eles têm pontuações de precisão mais baixas devido à menor supervisão humana durante a criação
    - C) Eles são gerados rápido demais
    - D) Eles não podem incluir medidas DAX

    ??? success "✅ Revelar Resposta"
        **Correta: B) Eles têm pontuações de precisão mais baixas devido à menor supervisão humana durante a criação**

        Relatórios copilot-generated têm em média ~0.85 de precisão comparado a ~0.96 para relatórios manuais. Sem um analista validando mapeamentos de dados, lógica de filtros e cálculos DAX, há um risco maior de erros sutis — especialmente para métricas de negócio complexas.

??? question "**Q3 (Execute o Lab):** Quantos relatórios foram criados usando o Copilot (assistido ou gerado)?"

    Execute a análise da Etapa 3 no [📥 `powerbi_reports.csv`](https://github.com/lcarli/AI-LearningHub/raw/main/docs/docs/en/labs/lab-075/powerbi_reports.csv) e conte os relatórios do Copilot.

    ??? success "✅ Revelar Resposta"
        **8 relatórios**

        Dos 10 relatórios no conjunto de dados, 4 são `copilot_assisted` (R02, R04, R07, R09) e 4 são `copilot_generated` (R03, R05, R08, R10). Apenas 2 são `manual` (R01, R06). Total de relatórios com Copilot = **8**.

??? question "**Q4 (Execute o Lab):** Qual é o tempo total economizado em todos os relatórios?"

    Execute a análise da Etapa 4 para calcular o tempo total economizado.

    ??? success "✅ Revelar Resposta"
        **395 minutos**

        Soma de todos os valores de `time_saved_min`: 0 + 45 + 60 + 30 + 50 + 0 + 55 + 65 + 35 + 55 = **395 minutos** (6,6 horas). Relatórios manuais (R01, R06) têm 0 de tempo economizado, pois são a linha de base.

??? question "**Q5 (Execute o Lab):** Qual é o tempo médio economizado por relatório do Copilot?"

    Divida o tempo total economizado pelo Copilot pelo número de relatórios do Copilot.

    ??? success "✅ Revelar Resposta"
        **49,4 minutos**

        Tempo total economizado pelos relatórios do Copilot = 45 + 60 + 30 + 50 + 55 + 65 + 35 + 55 = 395 min. Número de relatórios do Copilot = 8. Média = 395 ÷ 8 = **49,4 minutos** por relatório.

---

## Resumo

| Tópico | O que Você Aprendeu |
|--------|---------------------|
| Power BI Copilot | Criação de relatórios com IA, geração de DAX e narrativas de dados |
| Métodos de Criação | Manual, Assistido pelo Copilot (analista+IA), Gerado pelo Copilot (usuário de negócio+IA) |
| Economia de Tempo | 49,4 min em média por relatório do Copilot; 395 min no total durante o piloto |
| Compensação de Qualidade | Assistido=0,94 de precisão (próximo do manual); Gerado=0,85 (necessita revisão) |
| Adoção | 80% dos relatórios usaram o Copilot — forte sinal de adoção no piloto |
| BI de Autoatendimento | Copilot-generated permite que usuários de negócio criem seus próprios relatórios |

---

## Próximos Passos

- **[Lab 048](lab-048-work-iq-power-bi.md)** — Dashboards Work IQ Power BI (análises avançadas com Viva Insights)
- **[Lab 047](lab-047-work-iq-copilot-analytics.md)** — Work IQ Copilot Adoption Analytics (medindo o uso do Copilot no M365)
- **[Lab 074](lab-074-foundry-agent-service.md)** — Foundry Agent Service (implantando agentes de IA que alimentam dados para o Power BI)
- **[Lab 038](lab-038-cost-optimization.md)** — Otimização de Custos de IA (gerenciando custos do Copilot e IA)
