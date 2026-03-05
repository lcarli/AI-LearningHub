---
tags: [browser-automation, cua, openai, playwright, python, safety]
---
# Lab 058: Agentes de Automação de Navegador com OpenAI CUA

<div class="lab-meta">
  <span><strong>Nível:</strong> <span class="level-badge level-300">L300</span></span>
  <span><strong>Caminho:</strong> <a href="../paths/pro-code/">⚙️ Pro Code</a></span>
  <span><strong>Tempo:</strong> ~90 min</span>
  <span><strong>💰 Custo:</strong> <span class="level-badge cost-free">Gratuito</span> — Usa dataset de benchmark; API da OpenAI opcional</span>
</div>

## O Que Você Vai Aprender

- O que é o **OpenAI CUA** (Computer-Using Agent) — GPT-4o vision controlando um navegador real na nuvem via capturas de tela
- A diferença arquitetural entre **CUA** (baseado em capturas de tela) e **Playwright** (seletores baseados em código)
- Quando usar CUA vs Playwright — sites dinâmicos sem seletores estáveis vs páginas estruturadas e conhecidas
- Projetar **limites de segurança** — listas de URLs permitidas, limites de tempo de sessão e confirmação de ação
- Analisar **benchmarks de automação web** comparando CUA e Playwright em diferentes níveis de dificuldade

## Introdução

O **OpenAI CUA** opera um navegador real através de capturas de tela. O agente vê a página renderizada como uma imagem, raciocina sobre o que fazer em seguida e envia ações estruturadas (coordenadas de clique, digitar texto, rolar). Isso é fundamentalmente diferente do **Playwright**, que interage com a página através de código — seletores CSS, consultas XPath e chamadas de API programáticas.

| Abordagem | Como "Vê" a Página | Método de Interação | Fragilidade |
|----------|----------------------|-------------------|-------------|
| **CUA** | Capturas de tela (pixels) | Coordenadas de clique, entrada de teclado | Resiliente a mudanças no DOM; tem dificuldade com SPAs dinâmicas |
| **Playwright** | DOM / estrutura HTML | Seletores CSS, XPath, chamadas de API | Quebra quando os seletores mudam; rápido e preciso |

### O Cenário

Você é um **Engenheiro de Automação Web** na OutdoorGear Inc. A equipe precisa automatizar tarefas em várias propriedades web — a loja de e-commerce, parceiros de reserva de viagens, portal de suporte e dashboards de análise internos. Alguns sites têm HTML estável e bem estruturado; outros são aplicações de página única dinâmicas com seletores em constante mudança.

Seu trabalho é avaliar **CUA vs Playwright** usando um dataset de benchmark de **10 tarefas** tentadas por ambos os métodos, e recomendar qual abordagem usar para cada cenário.

!!! info "Agente ao Vivo Não Necessário"
    Este lab analisa um **dataset de benchmark pré-gravado** comparando resultados de CUA e Playwright. Você não precisa de uma chave de API da OpenAI ou instalação do Playwright — toda a análise é feita localmente com pandas. Se você tiver acesso à API, pode opcionalmente estender o lab para executar tarefas CUA ao vivo.

## Pré-requisitos

| Requisito | Por quê |
|---|---|
| Python 3.10+ | Executar scripts de análise |
| Biblioteca `pandas` | Operações com DataFrame |
| (Opcional) Chave de API da OpenAI | Para experimentos ao vivo com CUA |
| (Opcional) Playwright | Para comparação ao vivo de automação de navegador |

```bash
pip install pandas
```

---

!!! tip "Início Rápido com GitHub Codespaces"
    [![Open in GitHub Codespaces](https://github.com/codespaces/badge.svg)](https://codespaces.new/lcarli/AI-LearningHub?quickstart=1)

    Todas as dependências estão pré-instaladas no devcontainer.


## 📦 Arquivos de Apoio

!!! note "Baixe estes arquivos antes de iniciar o lab"
    Salve todos os arquivos em uma pasta `lab-058/` no seu diretório de trabalho.

| Arquivo | Descrição | Download |
|------|-------------|----------|
| `broken_cua.py` | Exercício de correção de bugs (3 bugs + auto-testes) | [📥 Download](https://github.com/lcarli/AI-LearningHub/raw/main/docs/docs/en/labs/lab-058/broken_cua.py) |
| `browser_tasks.csv` | Dataset | [📥 Download](https://github.com/lcarli/AI-LearningHub/raw/main/docs/docs/en/labs/lab-058/browser_tasks.csv) |

---

## Etapa 1: Entendendo CUA vs Playwright

### Arquitetura do CUA

```
┌─────────────┐     ┌──────────────┐     ┌──────────────┐
│  Browser     │────▶│  GPT-4o      │────▶│  Browser     │
│  Screenshot  │     │  Vision      │     │  Action      │
│  (pixels)    │     │  (reason)    │     │  (click/type)│
└─────────────┘     └──────────────┘     └──────────────┘
       ▲                                        │
       └────────────────────────────────────────┘
                    repeat until done
```

O CUA envia capturas de tela para o GPT-4o, que retorna ações estruturadas. O navegador executa a ação, tira uma nova captura de tela, e o loop continua até que a tarefa seja concluída.

### Arquitetura do Playwright

```
┌─────────────┐     ┌──────────────┐     ┌──────────────┐
│  Test Script │────▶│  Browser     │────▶│  DOM / HTML  │
│  (code)      │     │  Engine      │     │  (selectors) │
└─────────────┘     └──────────────┘     └──────────────┘
```

O Playwright executa código pré-escrito que direciona elementos HTML específicos usando seletores CSS, XPath ou roles ARIA. É rápido, preciso e determinístico — mas quebra quando a estrutura da página muda.

### Quando Usar Cada Um

| Cenário | Melhor Abordagem | Por quê |
|----------|--------------|-----|
| Site estável e bem estruturado | **Playwright** | Seletores são confiáveis; mais rápido e mais barato |
| SPA dinâmica com seletores mutáveis | **CUA** | Baseado em visão; não depende da estrutura do DOM |
| Páginas protegidas por CAPTCHA | **CUA** | Pode "ver" e raciocinar sobre CAPTCHAs |
| Tarefas repetitivas de alto volume | **Playwright** | Execução mais rápida; sem custo de API por ação |
| Exploração de site desconhecido/novo | **CUA** | Não precisa de seletores pré-escritos |

!!! tip "Diferença Principal"
    O CUA usa **visão e capturas de tela** para entender a página — como um humano olhando para uma tela. O Playwright usa **código e seletores** — como um desenvolvedor inspecionando o código-fonte HTML. O CUA é mais flexível; o Playwright é mais confiável em páginas conhecidas.

---

## Etapa 2: Carregar o Dataset de Benchmark

O dataset contém **10 tarefas**, cada uma tentada tanto pelo CUA quanto pelo Playwright:

```python
import pandas as pd

tasks = pd.read_csv("lab-058/browser_tasks.csv")
print(f"Total rows: {len(tasks)}")
print(f"Unique tasks: {tasks['task_id'].nunique()}")
print(f"Website types: {sorted(tasks['website_type'].unique())}")
print(f"Difficulty levels: {sorted(tasks['difficulty'].unique())}")
print(f"\nDataset preview:")
print(tasks[["task_id", "task_description", "difficulty",
             "cua_completed", "playwright_completed"]].to_string(index=False))
```

**Saída esperada:**

```
Total rows: 10
Unique tasks: 10
Website types: ['auth', 'data', 'e-commerce', 'support', 'travel', 'webapp']
Difficulty levels: ['easy', 'hard', 'medium']
```

| task_id | task_description | difficulty | cua | playwright |
|---------|-----------------|------------|-----|------------|
| T01 | Pesquisar botas de trilha e filtrar por preço | easy | ✓ | ✓ |
| T02 | Adicionar um produto ao carrinho e ver o total | easy | ✓ | ✓ |
| T03 | Preencher um formulário de endereço de entrega | medium | ✓ | ✓ |
| ... | ... | ... | ... | ... |
| T10 | Navegar em uma SPA dinâmica com roteamento client-side | hard | ✗ | ✓ |

---

## Etapa 3: Comparar Taxas de Sucesso CUA vs Playwright

Calcule e compare as taxas de conclusão de ambos os métodos:

```python
cua_completed = tasks["cua_completed"].sum()
pw_completed = tasks["playwright_completed"].sum()
total = len(tasks)

cua_rate = (cua_completed / total) * 100
pw_rate = (pw_completed / total) * 100

print(f"CUA:        {cua_completed}/{total} = {cua_rate:.0f}%")
print(f"Playwright: {pw_completed}/{total} = {pw_rate:.0f}%")
print(f"Difference: {pw_rate - cua_rate:.0f} percentage points in Playwright\'s favor")
```

**Saída esperada:**

```
CUA:        7/10 = 70%
Playwright: 8/10 = 80%
Difference: 10 percentage points in Playwright's favor
```

### Onde Cada Método se Destaca

```python
# Tasks where CUA succeeded but Playwright failed
cua_only = tasks[(tasks["cua_completed"] == True) & (tasks["playwright_completed"] == False)]
print(f"CUA succeeded, Playwright failed ({len(cua_only)}):")
print(cua_only[["task_id", "task_description"]].to_string(index=False))

# Tasks where Playwright succeeded but CUA failed
pw_only = tasks[(tasks["playwright_completed"] == True) & (tasks["cua_completed"] == False)]
print(f"\nPlaywright succeeded, CUA failed ({len(pw_only)}):")
print(pw_only[["task_id", "task_description"]].to_string(index=False))
```

**Esperado:**

- **Apenas CUA**: T07 (Enviar um ticket de suporte com anexo de captura de tela) — formulário dinâmico com upload de arquivo que é difícil de automatizar com seletores
- **Apenas Playwright**: T06 (Comparar preços de hotéis em 3 abas), T10 (Navegar em uma SPA dinâmica) — tarefas estruturadas onde navegação baseada em código é mais confiável

!!! tip "Insight"
    O Playwright tem uma taxa de sucesso geral mais alta (80% vs 70%), mas o CUA vence em tarefas que envolvem **conteúdo dinâmico** ou **raciocínio visual** (como anexar capturas de tela a tickets de suporte). O Playwright se destaca em fluxos de trabalho **estruturados e multi-abas** onde é necessária navegação precisa baseada em seletores.

---

## Etapa 4: Analisar por Dificuldade

Divida as taxas de sucesso por nível de dificuldade:

```python
print("Success rates by difficulty:\n")
for diff in ["easy", "medium", "hard"]:
    subset = tasks[tasks["difficulty"] == diff]
    cua_r = (subset["cua_completed"].sum() / len(subset)) * 100
    pw_r = (subset["playwright_completed"].sum() / len(subset)) * 100
    print(f"  {diff.upper()} ({len(subset)} tasks):")
    print(f"    CUA:        {subset['cua_completed'].sum()}/{len(subset)} = {cua_r:.0f}%")
    print(f"    Playwright: {subset['playwright_completed'].sum()}/{len(subset)} = {pw_r:.0f}%")
    print()
```

**Saída esperada:**

```
Success rates by difficulty:

  EASY (2 tasks):
    CUA:        2/2 = 100%
    Playwright: 2/2 = 100%

  MEDIUM (3 tasks):
    CUA:        3/3 = 100%
    Playwright: 3/3 = 100%

  HARD (5 tasks):
    CUA:        2/5 = 40%
    Playwright: 3/5 = 60%
```

!!! tip "Insight"
    Ambos os métodos lidam com tarefas **fáceis e médias** perfeitamente (100%). A diferença aparece nas **tarefas difíceis** onde a abordagem baseada em seletores do Playwright tem uma leve vantagem (60% vs 40%). No entanto, as tarefas onde o CUA vence (T07) são precisamente aquelas onde os seletores do Playwright não conseguem lidar com conteúdo dinâmico e visual.

---

## Etapa 5: Análise de Capturas de Tela

O CUA tira capturas de tela a cada etapa — mais capturas geralmente significam uma tarefa mais difícil ou mais longa:

```python
total_screenshots = tasks["cua_screenshots"].sum()
print(f"Total CUA screenshots across all tasks: {total_screenshots}")

print(f"\nScreenshots per task:")
print(tasks[["task_id", "task_description", "difficulty",
             "cua_screenshots", "cua_completed"]].to_string(index=False))

avg_by_diff = tasks.groupby("difficulty")["cua_screenshots"].mean()
print(f"\nAverage screenshots by difficulty:")
print(avg_by_diff.to_string())
```

**Saída esperada:**

```
Total CUA screenshots across all tasks: 122
```

| task_id | difficulty | screenshots | completed |
|---------|-----------|-------------|-----------|
| T01 | easy | 3 | True |
| T02 | easy | 5 | True |
| T03 | medium | 8 | True |
| T04 | medium | 6 | True |
| T05 | medium | 10 | True |
| T06 | hard | 18 | False |
| T07 | hard | 14 | True |
| T08 | hard | 16 | False |
| T09 | hard | 22 | True |
| T10 | hard | 20 | False |

```
Average screenshots by difficulty:
easy       4.0
medium     8.0
hard      18.0
```

!!! tip "Custo de Capturas de Tela"
    Cada captura de tela é enviada ao GPT-4o como um token de imagem — a ~765 tokens por captura de tela (página web típica), 122 capturas ≈ 93.000 tokens. Com os preços do GPT-4o, isso é aproximadamente **$0,47 em tokens de entrada** para toda a execução do benchmark. O CUA é econômico para cargas de trabalho moderadas, mas pode acumular custos para tarefas de alto volume.

---

## Etapa 6: Considerações de Segurança

### Lista de URLs Permitidas

Restrinja o CUA a domínios aprovados:

```python
# Analyze domain patterns in the dataset
print("URL patterns in tasks:")
print(tasks["url_pattern"].value_counts().to_string())

internal = tasks[tasks["url_pattern"] != "external"]
external = tasks[tasks["url_pattern"] == "external"]
print(f"\nInternal domains: {len(internal)} tasks")
print(f"External domains: {len(external)} tasks")

high_risk = tasks[tasks["safety_risk"] == "high"]
print(f"\nHigh-risk tasks: {len(high_risk)}")
print(high_risk[["task_id", "task_description", "safety_risk", "url_pattern"]].to_string(index=False))
```

### Limites de Segurança Recomendados

| Limite | Propósito | Implementação |
|----------|---------|----------------|
| **Lista de URLs permitidas** | Restringir quais sites o CUA pode visitar | `allowed_domains = ["*.outdoorgear.com"]` |
| **Limite de tempo da sessão** | Evitar agentes descontrolados | Encerrar sessão após 5 minutos de inatividade |
| **Confirmação de ação** | Aprovação humana para ações arriscadas | Prompt antes de envios de formulário em páginas de pagamento |
| **Retenção de capturas de tela** | Trilha de auditoria | Salvar todas as capturas de tela com timestamps para revisão |
| **Tratamento de credenciais** | Nunca expor senhas em capturas de tela | Usar preenchimento automático do navegador; manter senhas fora de campos visíveis |

!!! warning "Sites Externos"
    A tarefa T10 tem como alvo um domínio externo (`external`). Em produção, o CUA **nunca** deve ser direcionado a sites externos sem lista de permissões explícita. Um agente sem restrições poderia navegar para sites de phishing, baixar malware ou vazar dados sensíveis através de envios de formulário em domínios não confiáveis.

---

## 🐛 Exercício de Correção de Bugs

O arquivo `lab-058/broken_cua.py` tem **3 bugs** nas funções de análise do CUA. Você consegue encontrar e corrigir todos?

Execute os auto-testes para ver quais falham:

```bash
python lab-058/broken_cua.py
```

Você deve ver **3 testes falhando**. Cada teste corresponde a um bug:

| Teste | O que verifica | Dica |
|------|---------------|------|
| Teste 1 | Taxa de sucesso do CUA | Deve usar a coluna `cua_completed`, não `playwright_completed` |
| Teste 2 | Total de capturas de tela do CUA | Deve usar `sum()`, não `max()` |
| Teste 3 | Taxa de sucesso do CUA por dificuldade | Deve filtrar pelo parâmetro `difficulty` antes de calcular a taxa |

Corrija todos os 3 bugs e execute novamente. Quando você vir `🎉 All 3 tests passed`, está pronto!

---


## 🧠 Verificação de Conhecimento

??? question "**Q1 (Múltipla Escolha):** Qual é a principal diferença entre CUA e Playwright para automação de navegador?"

    - A) O CUA é mais rápido porque pula a renderização da página
    - B) O CUA usa visão/capturas de tela para entender páginas, enquanto o Playwright usa seletores CSS baseados em código
    - C) O Playwright pode lidar com CAPTCHAs, mas o CUA não
    - D) O CUA requer acesso ao código-fonte HTML da página

    ??? success "✅ Revelar Resposta"
        **Correta: B) O CUA usa visão/capturas de tela para entender páginas, enquanto o Playwright usa seletores CSS baseados em código**

        O CUA envia capturas de tela para um modelo de visão-linguagem (GPT-4o) e recebe ações de clicar/digitar baseadas no que ele "vê" — assim como um humano olhando para uma tela. O Playwright interage com o DOM diretamente usando seletores CSS, XPath ou roles ARIA. Essa diferença fundamental significa que o CUA é mais flexível (funciona em qualquer interface visual) enquanto o Playwright é mais preciso (acesso direto ao DOM).

??? question "**Q2 (Múltipla Escolha):** Quando o CUA é uma escolha melhor que o Playwright?"

    - A) Para tarefas repetitivas de alto volume em páginas estáveis
    - B) Para sites dinâmicos sem seletores CSS estáveis
    - C) Quando você precisa de resultados de teste determinísticos e reproduzíveis
    - D) Quando a página tem uma API bem documentada

    ??? success "✅ Revelar Resposta"
        **Correta: B) Para sites dinâmicos sem seletores CSS estáveis**

        O CUA se destaca em sites onde a estrutura do DOM muda frequentemente — SPAs dinâmicas, sites com testes A/B ou páginas com IDs de elementos aleatórios. Como o CUA "vê" a página visualmente, ele não depende de seletores CSS que podem quebrar a cada implantação. O Playwright é melhor para sites estáveis e bem estruturados onde os seletores são confiáveis.

??? question "**Q3 (Execute o Lab):** Qual é a taxa de sucesso do CUA?"

    Conte tarefas onde `cua_completed == True` e divida pelo total de tarefas.

    ??? success "✅ Revelar Resposta"
        **70%**

        7 de 10 tarefas foram concluídas com sucesso pelo CUA. As 3 falhas (T06, T08, T10) eram todas tarefas de dificuldade **difícil** envolvendo comparação multi-abas, tratamento de CAPTCHA e navegação de SPA dinâmica.

??? question "**Q4 (Execute o Lab):** Qual é a taxa de sucesso do Playwright?"

    Conte tarefas onde `playwright_completed == True` e divida pelo total de tarefas.

    ??? success "✅ Revelar Resposta"
        **80%**

        8 de 10 tarefas foram concluídas com sucesso pelo Playwright. As 2 falhas (T07, T08) envolveram um upload de anexo de captura de tela (que requer raciocínio visual além de seletores) e um formulário protegido por CAPTCHA (que nenhum dos métodos conseguiu resolver).

??? question "**Q5 (Execute o Lab):** Qual é o número total de capturas de tela do CUA em todas as tarefas?"

    Calcule `tasks["cua_screenshots"].sum()`.

    ??? success "✅ Revelar Resposta"
        **122**

        Soma de todas as capturas de tela: 3 + 5 + 8 + 6 + 10 + 18 + 14 + 16 + 22 + 20 = **122 capturas de tela**. Tarefas difíceis exigiram significativamente mais capturas (média de 18) comparado com tarefas fáceis (média de 4), refletindo as etapas adicionais de raciocínio necessárias para fluxos de trabalho complexos.

---

## Resumo

| Tópico | O Que Você Aprendeu |
|-------|-----------------|
| Arquitetura do CUA | GPT-4o vision controla um navegador na nuvem via loop captura de tela→ação |
| Arquitetura do Playwright | Seletores baseados em código interagem diretamente com o DOM |
| CUA vs Playwright | CUA: 70% de sucesso, flexível; Playwright: 80% de sucesso, preciso |
| Impacto da Dificuldade | Ambos os métodos acertam fácil/médio; tarefas difíceis revelam suas diferenças |
| Overhead de Capturas de Tela | 122 capturas no total; tarefas difíceis requerem 4× mais que as fáceis |
| Design de Segurança | Listas de URLs permitidas, limites de sessão, isolamento de credenciais, trilhas de auditoria |

---

## Próximos Passos

- **[Lab 057](lab-057-computer-use-agents.md)** — Agentes de Uso de Computador para Automação de Desktop
- Explore a [documentação do CUA](https://platform.openai.com/docs/guides/computer-using-agent) da OpenAI para configuração de agente ao vivo
- Experimente o [Playwright](https://playwright.dev/) para automação de navegador baseada em código
