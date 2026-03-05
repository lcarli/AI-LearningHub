---
tags: [ux, adaptive-cards, teams, proactive, accessibility, python]
---
# Lab 070: Padrões de UX para Agentes — Chat, Adaptive Cards e Notificações Proativas

<div class="lab-meta">
  <span><strong>Nível:</strong> <span class="level-badge level-100">L100</span></span>
  <span><strong>Trilha:</strong> Todas as trilhas</span>
  <span><strong>Tempo:</strong> ~60 min</span>
  <span><strong>💰 Custo:</strong> <span class="level-badge cost-free">Gratuito</span> — Dados de interação simulados (não requer Teams ou Azure Bot Service)</span>
</div>

## O que Você Vai Aprender

- **Padrões de UX** essenciais para interações de agentes de IA em ambientes corporativos
- Projetar **interfaces de chat** eficazes com indicadores de digitação e citações de fontes
- Construir **Adaptive Cards** para exibição de dados estruturados e entrada do usuário
- Implementar padrões de **notificação proativa** para mensagens iniciadas pelo agente
- Aplicar boas práticas de **acessibilidade** à UX de agentes
- Medir a qualidade da UX usando métricas de **satisfação do usuário**

!!! abstract "Pré-requisitos"
    Familiaridade com conceitos de **chatbot** é recomendada. Nenhuma experiência com desenvolvimento front-end é necessária — este lab analisa padrões de UX usando dados de interação simulados.

## Introdução

A inteligência de um agente de IA é tão eficaz quanto a sua **experiência do usuário**. Uma UX ruim — indicadores de digitação ausentes, sem citações de fontes, Adaptive Cards inacessíveis — mina a confiança e a adoção pelos usuários. Uma boa UX de agente segue padrões estabelecidos:

| Padrão de UX | Finalidade | Impacto |
|-----------|---------|--------|
| **Indicador de Digitação** | Mostra que o agente está processando | Reduz a latência percebida |
| **Citação de Fonte** | Vincula respostas a documentos de origem | Constrói confiança e verificabilidade |
| **Adaptive Cards** | Exibição estruturada com ações | Permite interações ricas |
| **Notificações Proativas** | Mensagens iniciadas pelo agente | Mantém os usuários informados |
| **Mensagens de Erro** | Estados de erro claros e acionáveis | Reduz a frustração |
| **Acessibilidade** | Suporte a leitores de tela, navegação por teclado | Garante acesso inclusivo |

### O Cenário

Você é um **Designer de UX** auditando os padrões de interação de um agente corporativo. Você tem dados sobre **12 padrões de UX** usados em toda a organização, incluindo pontuações de satisfação, status de implementação e conformidade de acessibilidade. Sua tarefa: identificar padrões de alto impacto, encontrar lacunas e recomendar melhorias.

---

## Pré-requisitos

| Requisito | Por quê |
|---|---|
| Python 3.10+ | Executar scripts de análise |
| `pandas` | Analisar dados de padrões de UX |

```bash
pip install pandas
```

---

!!! tip "Início Rápido com GitHub Codespaces"
    [![Open in GitHub Codespaces](https://github.com/codespaces/badge.svg)](https://codespaces.new/lcarli/AI-LearningHub?quickstart=1)

    Todas as dependências estão pré-instaladas no devcontainer.


## 📦 Arquivos de Apoio

!!! note "Baixe estes arquivos antes de iniciar o lab"
    Salve todos os arquivos em uma pasta `lab-070/` no seu diretório de trabalho.

| Arquivo | Descrição | Download |
|------|-------------|----------|
| `broken_ux.py` | Exercício de correção de bugs (3 bugs + autotestes) | [📥 Download](https://github.com/lcarli/AI-LearningHub/raw/main/docs/docs/en/labs/lab-070/broken_ux.py) |
| `ux_patterns.csv` | Conjunto de dados | [📥 Download](https://github.com/lcarli/AI-LearningHub/raw/main/docs/docs/en/labs/lab-070/ux_patterns.csv) |

---

## Etapa 1: Entendendo os Princípios de UX para Agentes

Uma UX eficaz para agentes segue uma abordagem em camadas:

```
User Input → [Typing Indicator] → Agent Processing → [Response Formatting]
                                                            ↓
                                                   ┌── Plain Text Chat
                                                   ├── Adaptive Card
                                                   ├── Source Citation
                                                   └── Error Message
                                                            ↓
                                              [Accessibility Check] → User
```

Princípios fundamentais:

1. **Responsividade** — Sempre reconheça a entrada do usuário imediatamente (indicadores de digitação)
2. **Transparência** — Cite fontes e explique os níveis de confiança
3. **Estrutura** — Use Adaptive Cards para dados complexos, texto simples para respostas simples
4. **Proatividade** — Notifique os usuários sobre eventos importantes sem exigir uma solicitação
5. **Acessibilidade** — Garanta que todas as interações funcionem com leitores de tela e navegação por teclado

!!! info "Por que a UX é Importante para a Adoção de Agentes"
    Pesquisas mostram que agentes com padrões de UX adequados (citações de fontes, indicadores de digitação, erros claros) têm 2-3x maior retenção de usuários do que agentes com respostas em texto puro. Os usuários confiam mais em agentes quando podem verificar as respostas e entender o estado do agente.

---

## Etapa 2: Carregar e Explorar os Padrões de UX

O conjunto de dados contém **12 padrões de UX** com pontuações de satisfação e dados de implementação:

```python
import pandas as pd

patterns = pd.read_csv("lab-070/ux_patterns.csv")
print(f"Total patterns: {len(patterns)}")
print(f"Categories: {sorted(patterns['category'].unique())}")
print(f"\nAll patterns:")
print(patterns[["pattern_id", "pattern_name", "category", "satisfaction_score"]]
      .to_string(index=False))
```

**Esperado:**

```
Total patterns: 12
```

---

## Etapa 3: Análise de Satisfação

Identifique os padrões com maior e menor satisfação:

```python
print("Patterns ranked by satisfaction score:")
ranked = patterns.sort_values("satisfaction_score", ascending=False)
print(ranked[["pattern_name", "category", "satisfaction_score"]].to_string(index=False))

highest = patterns.loc[patterns["satisfaction_score"].idxmax()]
print(f"\nHighest satisfaction: {highest['pattern_name']} ({highest['satisfaction_score']})")
print(f"Average satisfaction: {patterns['satisfaction_score'].mean():.2f}")
```

**Esperado:**

```
Highest satisfaction: Source Citation (4.8)
Average satisfaction: 4.17
```

!!! tip "Citações de Fontes Vencem"
    Source Citation tem a maior pontuação de satisfação (4.8 de 5.0). Os usuários preferem fortemente agentes que vinculam respostas a fontes verificáveis — isso constrói confiança e permite que os usuários se aprofundem. Esse padrão deve ser implementado em todo agente corporativo.

---

## Etapa 4: Análise por Categoria

Analise os padrões por categoria:

```python
print("Average satisfaction by category:")
cat_stats = patterns.groupby("category").agg(
    count=("pattern_id", "count"),
    avg_satisfaction=("satisfaction_score", "mean")
).sort_values("avg_satisfaction", ascending=False)
print(cat_stats.to_string())
```

As categorias agrupam padrões relacionados (por exemplo, padrões de "confiança" como citações de fontes e indicadores de confiança, padrões de "responsividade" como indicadores de digitação e streaming).

---

## Etapa 5: Verificação de Conformidade de Acessibilidade

Verifique quais padrões atendem aos padrões de acessibilidade:

```python
accessible = patterns[patterns["accessible"] == True]
not_accessible = patterns[patterns["accessible"] == False]
print(f"Accessible patterns: {len(accessible)} / {len(patterns)}")
print(f"Non-accessible patterns: {len(not_accessible)}")

if len(not_accessible) > 0:
    print(f"\nPatterns needing accessibility fixes:")
    print(not_accessible[["pattern_name", "category", "satisfaction_score"]].to_string(index=False))
```

!!! warning "Lacunas de Acessibilidade"
    Qualquer padrão não acessível é um risco de conformidade e exclui usuários que dependem de tecnologias assistivas. Adaptive Cards devem incluir `altText` para imagens, `label` para entradas e propriedades `speak` adequadas para leitores de tela.

---

## Etapa 6: Painel de Qualidade de UX

Construa um relatório abrangente de qualidade de UX:

```python
total = len(patterns)
avg_sat = patterns["satisfaction_score"].mean()
highest_name = patterns.loc[patterns["satisfaction_score"].idxmax(), "pattern_name"]
highest_score = patterns["satisfaction_score"].max()
accessible_count = (patterns["accessible"] == True).sum()

dashboard = f"""
╔════════════════════════════════════════════════════════╗
║     Agent UX Patterns — Quality Report                 ║
╠════════════════════════════════════════════════════════╣
║ Total Patterns:              {total:>5}                     ║
║ Average Satisfaction:        {avg_sat:>5.2f}                     ║
║ Highest Satisfaction:  {highest_name:>12} ({highest_score})           ║
║ Accessible Patterns:         {accessible_count:>5} / {total}                ║
║ Categories:                  {patterns['category'].nunique():>5}                     ║
╚════════════════════════════════════════════════════════╝
"""
print(dashboard)
```

---

## 🐛 Exercício de Correção de Bugs

O arquivo `lab-070/broken_ux.py` tem **3 bugs** na forma como analisa dados de padrões de UX:

```bash
python lab-070/broken_ux.py
```

| Teste | O que verifica | Dica |
|------|---------------|------|
| Teste 1 | Contagem de padrões | Deve contar todas as linhas com `len()`, não categorias únicas |
| Teste 2 | Padrão com maior satisfação | Deve usar `idxmax()`, não `idxmin()` |
| Teste 3 | Satisfação média | Deve usar `mean()`, não `median()` |

---


## 🧠 Verificação de Conhecimento

??? question "**Q1 (Múltipla Escolha):** Por que os indicadores de digitação são importantes para a UX de agentes de IA?"

    - A) Eles tornam o agente mais inteligente
    - B) Eles reduzem a latência percebida e sinalizam que o agente está processando ativamente a solicitação
    - C) Eles são exigidos pelo Microsoft Teams
    - D) Eles melhoram a precisão das respostas do agente

    ??? success "✅ Revelar Resposta"
        **Correta: B) Eles reduzem a latência percebida e sinalizam que o agente está processando ativamente a solicitação**

        Indicadores de digitação fornecem feedback visual imediato de que o agente recebeu a mensagem do usuário e está trabalhando em uma resposta. Sem eles, os usuários podem pensar que o agente está quebrado ou sem resposta, especialmente durante tempos de processamento mais longos. Esse padrão simples melhora significativamente a responsividade percebida e a confiança do usuário.

??? question "**Q2 (Múltipla Escolha):** Qual é o principal benefício das Adaptive Cards em relação às respostas em texto simples?"

    - A) Elas são mais rápidas de renderizar
    - B) Elas permitem a exibição de dados estruturados com elementos interativos como botões, entradas e layouts formatados
    - C) Elas funcionam sem internet
    - D) Elas são mais simples de implementar

    ??? success "✅ Revelar Resposta"
        **Correta: B) Elas permitem a exibição de dados estruturados com elementos interativos como botões, entradas e layouts formatados**

        Adaptive Cards transformam as respostas do agente de texto simples em experiências ricas e interativas. Elas podem exibir tabelas, imagens, botões de ação, formulários de entrada e texto formatado — permitindo que os usuários interajam com os dados diretamente em vez de digitar consultas de acompanhamento. São particularmente eficazes para fluxos de aprovação, resumos de dados e processos com múltiplas etapas.

??? question "**Q3 (Execute o Lab):** Qual padrão de UX tem a maior pontuação de satisfação do usuário?"

    Ordene os padrões por `satisfaction_score` de forma decrescente e verifique a primeira entrada.

    ??? success "✅ Revelar Resposta"
        **Source Citation com uma pontuação de satisfação de 4.8**

        Source Citation é o padrão de UX com a maior avaliação (4.8 de 5.0). Os usuários preferem fortemente agentes que vinculam respostas a documentos de origem verificáveis, pois isso constrói confiança e permite que eles verifiquem as informações. Esse padrão deve ser um padrão em todo agente corporativo.

??? question "**Q4 (Execute o Lab):** Qual é a pontuação média de satisfação em todos os padrões?"

    Calcule `patterns['satisfaction_score'].mean()`.

    ??? success "✅ Revelar Resposta"
        **4.17 de satisfação média**

        A pontuação média de satisfação em todos os 12 padrões de UX é 4.17 de 5.0, indicando recepção geralmente positiva pelos usuários. No entanto, a variância entre a maior (4.8) e as menores pontuações sugere que alguns padrões precisam de melhorias para igualar a qualidade dos melhores.

??? question "**Q5 (Execute o Lab):** Quantos padrões de UX estão no conjunto de dados?"

    Verifique `len(patterns)`.

    ??? success "✅ Revelar Resposta"
        **12 padrões**

        O conjunto de dados contém 12 padrões de UX abrangendo categorias como confiança (citações de fontes, indicadores de confiança), responsividade (indicadores de digitação, streaming), estrutura (Adaptive Cards, carrosséis), proatividade (notificações, sugestões) e acessibilidade (suporte a leitores de tela, navegação por teclado).

---

## Resumo

| Tópico | O que Você Aprendeu |
|-------|-----------------|
| UX de Chat | Projetar chat responsivo com indicadores de digitação e streaming |
| Citações de Fontes | Construir confiança vinculando respostas a fontes verificáveis |
| Adaptive Cards | Exibir dados estruturados com elementos interativos |
| Notificações Proativas | Habilitar mensagens iniciadas pelo agente para atualizações oportunas |
| Acessibilidade | Garantir UX inclusiva com suporte a leitores de tela e teclado |
| Métricas de Satisfação | Medir e comparar a eficácia dos padrões de UX |

---

## Próximos Passos

- **[Lab 069](lab-069-declarative-agents.md)** — Agentes Declarativos (configurar comportamento do agente via manifestos)
- **[Lab 066](lab-066-copilot-studio-governance.md)** — Governança do Copilot Studio (governar implantações de agentes)
- **[Lab 008](lab-008-responsible-ai.md)** — IA Responsável (princípios fundamentais de UX e segurança)
