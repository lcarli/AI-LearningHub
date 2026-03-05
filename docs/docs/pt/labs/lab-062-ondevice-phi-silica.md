---
tags: [on-device, phi-silica, windows-ai, npu, edge-ai, csharp]
---
# Lab 062: Agentes On-Device com Phi Silica — Windows AI APIs

<div class="lab-meta">
  <span><strong>Nível:</strong> <span class="level-badge level-300">L300</span></span>
  <span><strong>Caminho:</strong> Todos os caminhos</span>
  <span><strong>Tempo:</strong> ~90 min</span>
  <span><strong>💰 Custo:</strong> <span class="level-badge cost-free">Gratuito</span> — Usa dados de benchmark simulados (nenhum hardware NPU necessário)</span>
</div>

## O Que Você Vai Aprender

- Como **Windows AI APIs** permitem inferência on-device usando a Neural Processing Unit (NPU)
- O que é **Phi Silica** — um modelo otimizado para hardware NPU do Windows
- Comparar latência **NPU vs nuvem** para habilidades de agentes (resumir, classificar, reescrever, texto_para_tabela)
- Lidar com **indisponibilidade do NPU** de forma elegante com estratégias de fallback para a nuvem
- Medir **taxas de correspondência de qualidade** entre inferência on-device e na nuvem
- Construir agentes que funcionam **offline-first** com degradação inteligente

---

## Introdução

IA baseada em nuvem é poderosa, mas requer conectividade com a internet, introduz latência e envia dados para fora do dispositivo. **Windows AI APIs** com **Phi Silica** trazem a inferência diretamente para o NPU (Neural Processing Unit) — um acelerador de IA dedicado integrado em dispositivos Windows modernos.

Inferência on-device significa: zero latência de rede, privacidade total dos dados, capacidade offline e sem custo por token. O trade-off é que nem toda tarefa pode ser executada no NPU, e a qualidade pode diferir dos modelos na nuvem. Este lab mede exatamente onde a inferência on-device se destaca e onde você precisa de fallback para a nuvem.

### O Benchmark

Você analisará **15 tarefas** em 4 categorias, comparando NPU (Phi Silica) vs inferência na nuvem:

| Categoria | Quantidade | Exemplo |
|-----------|-----------|---------|
| **Resumir** | 4 | Transcrição de reunião, artigo, thread de e-mail, documento de política |
| **Classificar** | 4 | Sentimento, intenção, prioridade, detecção de idioma |
| **Reescrever** | 4 | Ajuste de tom, simplificação, formalização, tradução |
| **Texto-para-tabela** | 3 | Extrair dados estruturados de texto não estruturado |

---

## Pré-requisitos

```bash
pip install pandas
```

Este lab analisa resultados de benchmark pré-computados — nenhum hardware NPU, Windows AI SDK ou toolchain C# é necessário. Para executar inferência on-device ao vivo, você precisaria de um Copilot+ PC com NPU e as Windows AI APIs.

---

!!! tip "Início Rápido com GitHub Codespaces"
    [![Open in GitHub Codespaces](https://github.com/codespaces/badge.svg)](https://codespaces.new/lcarli/AI-LearningHub?quickstart=1)

    Todas as dependências estão pré-instaladas no devcontainer.


## 📦 Arquivos de Apoio

!!! note "Baixe estes arquivos antes de iniciar o lab"
    Salve todos os arquivos em uma pasta `lab-062/` no seu diretório de trabalho.

| Arquivo | Descrição | Download |
|---------|-----------|----------|
| `broken_ondevice.py` | Exercício de correção de bugs (3 bugs + autotestes) | [📥 Download](https://github.com/lcarli/AI-LearningHub/raw/main/docs/docs/en/labs/lab-062/broken_ondevice.py) |
| `ondevice_tasks.csv` | Conjunto de dados | [📥 Download](https://github.com/lcarli/AI-LearningHub/raw/main/docs/docs/en/labs/lab-062/ondevice_tasks.csv) |

---

## Parte 1: Entendendo Inferência On-Device

### Etapa 1: Arquitetura NPU

A Neural Processing Unit (NPU) é um acelerador de IA dedicado projetado para operações eficientes de matrizes:

```
Inferência na Nuvem:
  App → [Rede] → [GPU na Nuvem] → [Rede] → Resposta
  Latência: ~800-1200ms

Inferência NPU (Phi Silica):
  App → [NPU Local] → Resposta
  Latência: ~50-120ms
```

Conceitos-chave:

| Conceito | Descrição |
|----------|-----------|
| **NPU** | Neural Processing Unit — hardware de IA dedicado em CPUs modernas |
| **Phi Silica** | Modelo da Microsoft otimizado para execução no NPU do Windows |
| **Windows AI APIs** | APIs de nível de sistema para inferência de IA on-device |
| **Verificação de disponibilidade** | API para verificar disponibilidade do NPU antes de tentar inferência |
| **Fallback elegante** | Estratégia de fallback para a nuvem quando o NPU não está disponível |

!!! info "Phi Silica vs Phi-4 Mini"
    Phi Silica é especificamente otimizado para hardware NPU do Windows — não é apenas um modelo menor, mas um projetado para a arquitetura do NPU. Phi-4 Mini (Lab 061) executa via ONNX Runtime em CPU/GPU. Ambos oferecem inferência on-device, mas visam caminhos de hardware diferentes.

---

## Parte 2: Carregar Dados de Benchmark

### Etapa 2: Carregar [📥 `ondevice_tasks.csv`](https://github.com/lcarli/AI-LearningHub/raw/main/docs/docs/en/labs/lab-062/ondevice_tasks.csv)

O conjunto de dados de benchmark contém resultados da execução de 15 tarefas através de inferência NPU e nuvem:

```python
# ondevice_analysis.py
import pandas as pd

bench = pd.read_csv("lab-062/ondevice_tasks.csv")

print(f"Tasks: {len(bench)}")
print(f"Categories: {bench['category'].unique().tolist()}")
print(bench[["task_id", "category", "description", "npu_available"]].to_string(index=False))
```

**Saída esperada:**

```
Tasks: 15
Categories: ['summarize', 'classify', 'rewrite', 'text_to_table']

task_id      category                      description  npu_available
    T01     summarize          Meeting transcript summary           True
    T02     summarize                    Article digest           True
    T03     summarize              Email thread summary           True
    T04     summarize                Policy doc summary           True
    T05      classify              Sentiment analysis           True
    T06      classify                Intent detection           True
    T07      classify              Priority assignment           True
    T08      classify             Language detection           True
    T09       rewrite                 Tone adjustment           True
    T10       rewrite                  Simplification           True
    T11       rewrite                  Formalization           True
    T12       rewrite    Translation (EN→ES snippet)          False
    T13 text_to_table      Invoice data extraction           True
    T14 text_to_table      Resume parsing to table           True
    T15 text_to_table  Schedule extraction to table           True
```

---

## Parte 3: Disponibilidade do NPU

### Etapa 3: Verificar disponibilidade do NPU nas tarefas

```python
# NPU availability
available = bench["npu_available"].sum()
unavailable = len(bench) - available
print(f"NPU available: {available}/{len(bench)}")
print(f"NPU unavailable: {unavailable}")

# Which tasks have no NPU support?
no_npu = bench[bench["npu_available"] == False]
print("\nTasks without NPU support:")
print(no_npu[["task_id", "category", "description"]].to_string(index=False))
```

**Saída esperada:**

```
NPU available: 14/15
NPU unavailable: 1

Tasks without NPU support:
task_id category                   description
    T12  rewrite  Translation (EN→ES snippet)
```

!!! warning "Limitação do NPU"
    Tradução (T12) não está disponível no NPU — Phi Silica é otimizado para tarefas em inglês e não suporta tradução entre idiomas on-device. Seu agente deve detectar isso e fazer fallback para inferência na nuvem.

---

## Parte 4: Análise de Correspondência de Qualidade

### Etapa 4: Comparar qualidade NPU vs nuvem

```python
# Quality match for NPU-available tasks only
npu_tasks = bench[bench["npu_available"] == True]
quality_match = npu_tasks["quality_match"].sum()
total_available = len(npu_tasks)
match_rate = quality_match / total_available * 100

print(f"Quality match (NPU-available tasks): {quality_match}/{total_available} = {match_rate:.0f}%")

# Which NPU-available tasks have quality mismatch?
mismatches = npu_tasks[npu_tasks["quality_match"] == False]
print("\nQuality mismatches (NPU available but lower quality):")
print(mismatches[["task_id", "category", "description"]].to_string(index=False))
```

**Saída esperada:**

```
Quality match (NPU-available tasks): 13/14 = 93%

Quality mismatches (NPU available but lower quality):
task_id      category              description
    T04     summarize  Policy doc summary
```

!!! info "Insight de Qualidade"
    93% das tarefas disponíveis no NPU correspondem à qualidade da nuvem. A única incompatibilidade é T04 (resumo de documento de política) — um documento complexo que ultrapassa os limites de contexto do modelo on-device. Para 13 das 14 tarefas disponíveis, a qualidade do NPU é indistinguível da nuvem.

```python
# Quality by category (NPU-available tasks only)
print("\nQuality match by category:")
for cat in npu_tasks["category"].unique():
    cat_data = npu_tasks[npu_tasks["category"] == cat]
    matches = cat_data["quality_match"].sum()
    total = len(cat_data)
    print(f"  {cat:>13}: {matches}/{total}")
```

**Saída esperada:**

```
Quality match by category:
      summarize: 3/4
       classify: 4/4
        rewrite: 3/3
  text_to_table: 3/3
```

---

## Parte 5: Comparação de Latência

### Etapa 5: Latência NPU vs nuvem

```python
# Average NPU latency (available tasks only)
npu_tasks = bench[bench["npu_available"] == True]
npu_avg = npu_tasks["npu_latency_ms"].mean()
cloud_avg = npu_tasks["cloud_latency_ms"].mean()
speedup = cloud_avg / npu_avg

print(f"NPU avg latency:   {npu_avg:.1f}ms")
print(f"Cloud avg latency: {cloud_avg:.1f}ms")
print(f"Speedup:           {speedup:.0f}×")
```

**Saída esperada:**

```
NPU avg latency:   83.1ms
Cloud avg latency: 874.3ms
Speedup:           10×
```

```python
# Per-task latency comparison
print("\nPer-task latency (NPU-available only):")
for _, row in npu_tasks.iterrows():
    print(f"  {row['task_id']} ({row['category']:>13}): "
          f"NPU={row['npu_latency_ms']:.0f}ms  "
          f"Cloud={row['cloud_latency_ms']:.0f}ms")
```

!!! info "Vantagem de Latência"
    Inferência NPU tem média de 83,1ms — mais de **10× mais rápido** que a nuvem com 874,3ms. Isso é ainda mais rápido que ONNX Runtime baseado em CPU (82,3ms do Lab 061) porque o NPU é construído especificamente para cargas de trabalho de IA. Para experiências de agentes em tempo real, esta latência abaixo de 100ms permite interações verdadeiramente responsivas.

---

## Parte 6: Estratégia de Fallback Elegante

### Etapa 6: Implementar lógica de fallback

O padrão correto para agentes on-device é: **verificar disponibilidade → tentar NPU → fazer fallback para a nuvem**:

```csharp
// C# — Windows AI API pattern
async Task<string> RunAgentSkill(string input, SkillType skill)
{
    // 1. Check NPU readiness for this skill
    var readiness = await PhiSilicaModel.CheckReadinessAsync(skill);

    if (readiness == AIReadiness.Available)
    {
        // 2. Run on NPU
        return await PhiSilicaModel.InferAsync(input, skill);
    }
    else
    {
        // 3. Fall back to cloud
        Console.WriteLine($"NPU unavailable for {skill}, falling back to cloud");
        return await CloudModel.InferAsync(input, skill);
    }
}
```

!!! warning "Anti-padrão: Sem Verificação de Disponibilidade"
    Nunca assuma que o NPU está disponível. Sempre chame `CheckReadinessAsync()` primeiro. Algumas tarefas (como tradução) não são suportadas on-device, e a disponibilidade do NPU pode mudar com base no hardware e no estado do driver.

```python
# Simulate fallback strategy
print("Fallback strategy simulation:")
for _, row in bench.iterrows():
    if row["npu_available"]:
        engine = "NPU"
        latency = row["npu_latency_ms"]
    else:
        engine = "CLOUD (fallback)"
        latency = row["cloud_latency_ms"]
    print(f"  {row['task_id']}: {engine:>20} → {latency:.0f}ms")
```

---

## Parte 7: Framework de Decisão

### Etapa 7: Quando usar inferência on-device

| Cenário | Recomendado | Por quê |
|---------|------------|---------|
| **Operação offline** | NPU | Sem necessidade de internet |
| **Dados sensíveis à privacidade** | NPU | Dados nunca saem do dispositivo |
| **UX de agente em tempo real** | NPU | Latência abaixo de 100ms |
| **Tradução** | Nuvem | NPU não suporta tradução entre idiomas |
| **Documentos complexos** | Nuvem (ou NPU com fallback) | NPU pode ter lacunas de qualidade em entradas complexas |
| **Processamento em lote** | NPU | Zero custo por token em escala |

```python
# Summary dashboard
print("""
╔══════════════════════════════════════════════════════╗
║   On-Device Benchmark — Phi Silica (NPU) vs Cloud   ║
╠══════════════════════════════════════════════════════╣
║  Metric                    NPU         Cloud        ║
║  ─────────────────         ───         ─────        ║
║  Tasks supported           14/15       15/15        ║
║  Quality match (avail.)    93%         baseline     ║
║  Avg latency               83.1ms      874.3ms     ║
║  Speedup                   10×+        baseline     ║
║  Privacy                   Full        Data sent    ║
║  Offline capable           Yes         No           ║
╠══════════════════════════════════════════════════════╣
║  Strategy: NPU-first with cloud fallback            ║
║  Check readiness → attempt NPU → fall back if needed║
╚══════════════════════════════════════════════════════╝
""")
```

---

## 🐛 Exercício de Correção de Bugs

O arquivo `lab-062/broken_ondevice.py` tem **3 bugs** nas funções de análise on-device. Execute os autotestes:

```bash
python lab-062/broken_ondevice.py
```

Você deverá ver **3 testes falhando**:

| Teste | O que verifica | Dica |
|-------|---------------|------|
| Teste 1 | Contagem de disponibilidade do NPU | Qual coluna representa disponibilidade — `npu_available` ou `quality_match`? |
| Teste 2 | Cálculo de speedup | A proporção é `npu / cloud` ou `cloud / npu`? |
| Teste 3 | Filtro de correspondência de qualidade | Você está filtrando por `npu_available == True` antes de verificar a qualidade? |

Corrija todos os 3 bugs e execute novamente até ver `🎉 All 3 tests passed`.

---


## 🧠 Verificação de Conhecimento

??? question "**Q1 (Múltipla Escolha):** Qual é a principal vantagem da inferência baseada em NPU com Phi Silica?"

    - A) Maior precisão que todos os modelos na nuvem
    - B) Inferência rápida sem conectividade com a internet
    - C) Suporte para todos os idiomas e modalidades
    - D) Tamanho ilimitado da janela de contexto

    ??? success "✅ Revelar Resposta"
        **Correto: B) Inferência rápida sem conectividade com a internet**

        O NPU permite inferência on-device com ~83ms em média — sem round-trip de rede, sem dependência de internet e privacidade total dos dados. Não afirma ter maior precisão que modelos na nuvem (correspondência de qualidade é 93%), e tem limitações (ex.: sem suporte a tradução). A vantagem principal é a combinação de velocidade, privacidade e capacidade offline.

??? question "**Q2 (Múltipla Escolha):** Qual é o padrão correto para lidar com indisponibilidade do NPU em um agente de produção?"

    - A) Falhar com uma mensagem de erro dizendo ao usuário para atualizar o hardware
    - B) Sempre usar inferência na nuvem para evitar problemas com NPU
    - C) Verificar a disponibilidade do NPU primeiro, depois fazer fallback para a nuvem se indisponível
    - D) Tentar inferência no NPU 10 vezes antes de desistir

    ??? success "✅ Revelar Resposta"
        **Correto: C) Verificar a disponibilidade do NPU primeiro, depois fazer fallback para a nuvem se indisponível**

        O padrão correto é: verificar disponibilidade → tentar NPU → fazer fallback para a nuvem. Isso garante que o agente funcione em todas as configurações de hardware e para todos os tipos de tarefas. Algumas tarefas (como tradução) nunca estão disponíveis no NPU, e a disponibilidade de hardware pode variar. Um fallback elegante proporciona a melhor experiência do usuário — rápido on-device quando possível, nuvem confiável quando necessário.

??? question "**Q3 (Execute o Lab):** Quantas tarefas têm NPU indisponível?"

    Calcule `(bench["npu_available"] == False).sum()`.

    ??? success "✅ Revelar Resposta"
        **1 tarefa (T12 — Tradução)**

        Apenas T12 (Tradução EN→ES snippet) não tem suporte NPU. Todas as outras 14 tarefas — resumir, classificar, reescrever e texto_para_tabela — podem ser executadas no NPU via Phi Silica. Isso significa que 93% das tarefas do benchmark podem ser executadas inteiramente on-device.

??? question "**Q4 (Execute o Lab):** Qual é a taxa de correspondência de qualidade para tarefas disponíveis no NPU?"

    Filtre por `npu_available == True`, depois calcule `quality_match.sum() / len(filtered) * 100`.

    ??? success "✅ Revelar Resposta"
        **93% (13/14)**

        Das 14 tarefas onde o NPU está disponível, 13 produzem qualidade que corresponde à inferência na nuvem — uma taxa de correspondência de 93%. A única incompatibilidade é T04 (resumo de documento de política), onde o documento complexo excede a capacidade efetiva de contexto do modelo on-device. Para a grande maioria das tarefas, a qualidade on-device é indistinguível da nuvem.

??? question "**Q5 (Execute o Lab):** Qual é a latência média do NPU para tarefas disponíveis?"

    Filtre por `npu_available == True`, depois calcule `npu_latency_ms.mean()`.

    ??? success "✅ Revelar Resposta"
        **83,1ms**

        A latência média do NPU em 14 tarefas disponíveis é 83,1ms. Comparado à média da nuvem de 874,3ms, isso representa um speedup de 10×+. Latência abaixo de 100ms permite interações de agentes em tempo real — o usuário percebe a resposta como instantânea. Esta vantagem de latência é o argumento mais forte para inferência on-device em experiências interativas de agentes.

---

## Resumo

| Tópico | O Que Você Aprendeu |
|--------|---------------------|
| Windows AI APIs | APIs de nível de sistema para inferência NPU on-device |
| Phi Silica | Modelo otimizado para hardware NPU do Windows |
| Disponibilidade do NPU | 14/15 tarefas suportadas; tradução requer fallback para a nuvem |
| Correspondência de Qualidade | 93% das tarefas disponíveis no NPU correspondem à qualidade da nuvem |
| Latência | NPU média 83,1ms vs nuvem 874,3ms — 10×+ mais rápido |
| Padrão de Fallback | Verificar disponibilidade → NPU → fallback para a nuvem |

---

## Próximos Passos

- **[Lab 061](lab-061-slm-phi4-mini.md)** — SLMs com Phi-4 Mini (inferência local baseada em CPU/GPU via ONNX Runtime)
- **[Lab 063](lab-063-agent-identity-entra.md)** — Identidade de Agente com Entra (protegendo agentes que acessam recursos na nuvem)
- **[Lab 043](lab-043-multimodal-agents.md)** — Agentes Multimodais (estendendo capacidades de agentes além de texto)
