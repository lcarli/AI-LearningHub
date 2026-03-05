---
tags: [markitdown, mcp, document-ingestion, pdf, python]
---
# Lab 080: MarkItDown + MCP — Ingestão de Documentos para Agentes

<div class="lab-meta">
  <span><strong>Nível:</strong> <span class="level-badge level-200">L200</span></span>
  <span><strong>Trilha:</strong> Todas as trilhas</span>
  <span><strong>Tempo:</strong> ~60 min</span>
  <span><strong>💰 Custo:</strong> <span class="level-badge cost-free">Gratuito</span></span>
</div>

## O que Você Vai Aprender

- O que é o **Microsoft MarkItDown** — uma biblioteca que converte PDF, Word, Excel, PowerPoint, HTML e imagens em Markdown limpo para consumo por LLMs
- Como o **servidor MCP** do MarkItDown expõe a conversão de documentos como uma ferramenta que qualquer agente compatível com MCP pode chamar
- Analisar a **qualidade de conversão** em diferentes tipos de arquivo para entender pontos fortes e limitações
- Medir a **velocidade de conversão** e identificar quais formatos são mais rápidos de processar
- Depurar um script de análise do MarkItDown com falhas corrigindo 3 bugs

## Introdução

Modelos de Linguagem de Grande Escala funcionam melhor com **texto puro**, mas documentos empresariais vêm em dezenas de formatos — PDFs com tabelas, documentos Word com imagens incorporadas, planilhas Excel, apresentações PowerPoint e páginas HTML. Converter manualmente esses arquivos para texto perde a estrutura, e abordagens baseadas em OCR são lentas e propensas a erros.

O **Microsoft MarkItDown** resolve isso convertendo documentos ricos em **Markdown bem estruturado** que preserva tabelas, títulos, listas e referências de imagens. Ele suporta PDF, DOCX, XLSX, PPTX, HTML, CSV, JSON e até imagens (via OCR/legendagem). Quando combinado com seu **servidor MCP**, qualquer agente pode chamar `convert_to_markdown` como uma ferramenta — possibilitando fluxos de trabalho de ingestão de documentos de forma transparente.

### O Cenário

Você é um **Engenheiro de Plataforma** na OutdoorGear Inc. A empresa possui um corpus de documentos crescente — relatórios trimestrais, catálogos de produtos, manuais de treinamento e contratos — que os agentes precisam pesquisar e raciocinar sobre. Você avaliará a qualidade de conversão do MarkItDown em **12 conversões de arquivos** cobrindo 7 tipos de arquivo diferentes.

!!! info "Instalação do MarkItDown Não Necessária"
    Este laboratório analisa um **conjunto de dados de benchmark pré-gravado** de resultados de conversão. Você não precisa instalar o MarkItDown — toda a análise é feita localmente com pandas. Se você quiser executar conversões ao vivo, instale com `pip install markitdown`.

## Pré-requisitos

| Requisito | Por quê |
|---|---|
| Python 3.10+ | Executar scripts de análise |
| Biblioteca `pandas` | Operações com DataFrame |
| (Opcional) `markitdown` | Para conversões de documentos ao vivo |

```bash
pip install pandas
```

---

!!! tip "Início Rápido com GitHub Codespaces"
    [![Open in GitHub Codespaces](https://github.com/codespaces/badge.svg)](https://codespaces.new/lcarli/AI-LearningHub?quickstart=1)

    Todas as dependências estão pré-instaladas no devcontainer.


## 📦 Arquivos de Apoio

!!! note "Baixe estes arquivos antes de iniciar o laboratório"
    Salve todos os arquivos em uma pasta `lab-080/` no seu diretório de trabalho.

| Arquivo | Descrição | Download |
|---------|-----------|----------|
| `broken_markitdown.py` | Exercício de correção de bugs (3 bugs + autotestes) | [📥 Download](https://github.com/lcarli/AI-LearningHub/raw/main/docs/docs/en/labs/lab-080/broken_markitdown.py) |
| `conversion_results.csv` | Dataset — 12 conversões de arquivos em 7 formatos | [📥 Download](https://github.com/lcarli/AI-LearningHub/raw/main/docs/docs/en/labs/lab-080/conversion_results.csv) |

---

## Etapa 1: Entendendo o MarkItDown

O MarkItDown segue um pipeline simples — detecta o tipo de arquivo, aplica o conversor apropriado e produz Markdown estruturado:

```
┌──────────────┐     ┌──────────────┐     ┌──────────────┐
│  Arquivo de  │────▶│  Conversor   │────▶│  Markdown    │
│  Entrada     │     │  (por tipo)  │     │  (estrutur.) │
│  (PDF/DOCX…) │     │              │     │              │
└──────────────┘     └──────────────┘     └──────────────┘
```

Conversores suportados:

| Formato | Conversor | Preserva |
|---------|-----------|----------|
| **PDF** | `pdfminer` | Texto, títulos, tabelas (limitado) |
| **DOCX** | `python-docx` | Títulos, tabelas, listas, estilos |
| **XLSX** | `openpyxl` | Dados de planilha como tabelas Markdown |
| **PPTX** | `python-pptx` | Texto de slides, notas do apresentador, imagens |
| **HTML** | `BeautifulSoup` | Estrutura, links, tabelas |
| **CSV/JSON** | Integrado | Dados tabulares |
| **Imagens** | OCR / legendagem por LLM | Texto extraído ou descrições |

### Integração com Servidor MCP

O MarkItDown vem com um **servidor MCP** que expõe a conversão como uma ferramenta:

```json
{
  "tools": [
    {
      "name": "convert_to_markdown",
      "description": "Convert a document file to Markdown",
      "inputSchema": {
        "type": "object",
        "properties": {
          "uri": { "type": "string", "description": "File path or URL" }
        }
      }
    }
  ]
}
```

Qualquer agente compatível com MCP (GitHub Copilot, Claude Desktop, agentes personalizados) pode chamar esta ferramenta para ingerir documentos em tempo real.

---

## Etapa 2: Carregar os Resultados de Conversão

O dataset contém **12 conversões de arquivos** em 7 formatos diferentes:

```python
import pandas as pd

results = pd.read_csv("lab-080/conversion_results.csv")
print(f"Total conversions: {len(results)}")
print(f"File types: {sorted(results['file_type'].unique())}")
print(f"\nDataset preview:")
print(results[["test_id", "input_file", "file_type", "conversion_success", "quality_score"]].to_string(index=False))
```

**Saída esperada:**

```
Total conversions: 12
File types: ['csv', 'docx', 'html', 'image', 'json', 'pdf', 'pptx', 'xlsx']
```

| test_id | input_file | file_type | conversion_success | quality_score |
|---------|-----------|-----------|-------------------|---------------|
| D01 | quarterly_report.pdf | pdf | True | 0.92 |
| D02 | product_catalog.docx | docx | True | 0.95 |
| ... | ... | ... | ... | ... |
| D11 | corrupted_file.pdf | pdf | False | 0.00 |
| D12 | scanned_receipt.png | image | True | 0.72 |

---

## Etapa 3: Analisar o Sucesso da Conversão

Calcule a taxa geral de sucesso e identifique falhas:

```python
successful = results[results["conversion_success"] == True]
failed = results[results["conversion_success"] == False]

print(f"Successful conversions: {len(successful)}/{len(results)}")
print(f"Success rate: {len(successful)/len(results)*100:.0f}%")

if len(failed) > 0:
    print(f"\nFailed conversions:")
    print(failed[["test_id", "input_file", "file_type"]].to_string(index=False))
```

**Saída esperada:**

```
Successful conversions: 11/12
Success rate: 92%

Failed conversions:
 test_id      input_file file_type
     D11 corrupted_file.pdf       pdf
```

!!! tip "Insight"
    A única falha é um **PDF corrompido** (D11, file_size_kb = 0). O MarkItDown lida com todos os 7 formatos suportados com sucesso quando o arquivo de entrada é válido.

---

## Etapa 4: Analisar a Qualidade da Conversão

Compare as pontuações de qualidade entre os tipos de arquivo:

```python
print("Quality scores by file type (successful only):")
quality = successful.groupby("file_type")["quality_score"].agg(["mean", "count"])
quality.columns = ["avg_quality", "count"]
print(quality.sort_values("avg_quality", ascending=False).to_string())

avg_quality = successful["quality_score"].mean()
print(f"\nOverall average quality: {avg_quality:.3f}")
```

**Saída esperada:**

```
Quality scores by file type (successful only):
           avg_quality  count
csv              0.990      1
json             0.980      1
xlsx             0.980      1
html             0.970      1
docx             0.955      2
pdf              0.893      3
pptx             0.850      1
image            0.720      1

Overall average quality: ≈ 0.916
```

!!! tip "Insight"
    Formatos estruturados (CSV, JSON, XLSX) alcançam qualidade quase perfeita (≥0.98), enquanto **imagens** têm a menor qualidade (0.72) — OCR/legendagem é inerentemente com perdas. PDFs variam com base na complexidade; o manual de treinamento grande (D10, 12 MB) obteve 0.82.

---

## Etapa 5: Analisar a Velocidade de Conversão

Meça os tempos de conversão e identifique gargalos:

```python
print("Conversion time by file type (successful only):")
for _, row in successful.sort_values("conversion_time_ms", ascending=False).iterrows():
    print(f"  {row['test_id']} ({row['file_type']:>5}): {row['conversion_time_ms']:,}ms "
          f"({row['file_size_kb']:,} KB)")
```

**Saída esperada:**

```
  D10 (  pdf): 4,500ms (12,000 KB)
  D12 (image): 2,200ms (450 KB)
  D04 ( pptx): 1,800ms (5,200 KB)
  D01 (  pdf): 1,200ms (2,450 KB)
  ...
  D08 (  csv):    30ms (45 KB)
```

```python
total_tables = successful["tables_found"].sum()
total_images = successful["images_found"].sum()
total_headings = successful["headings_found"].sum()

print(f"\nExtracted elements (successful conversions):")
print(f"  Tables found:   {total_tables}")
print(f"  Images found:   {total_images}")
print(f"  Headings found: {total_headings}")
```

**Saída esperada:**

```
Extracted elements (successful conversions):
  Tables found:   31
  Images found:   62
  Headings found: 103
```

!!! tip "Insight"
    PDFs grandes e imagens são os mais lentos para converter. O **manual de treinamento** (D10, 12 MB) levou 4,5 segundos, mas extraiu 15 tabelas, 28 imagens e 32 títulos — um documento rico que seria extremamente tedioso de processar manualmente.

---

## Etapa 6: Arquitetura do Servidor MCP

Quando o MarkItDown roda como um servidor MCP, agentes podem converter documentos sob demanda:

```
┌──────────────┐     ┌──────────────┐     ┌──────────────┐
│   Agente     │────▶│  Servidor    │────▶│  MarkItDown  │
│  (Copilot,   │     │  MCP         │     │  (conversor) │
│   Claude)    │◀────│  (stdio/SSE) │◀────│              │
└──────────────┘     └──────────────┘     └──────────────┘
     requisição           rota              converter
     markdown             retorno           para .md
```

Para iniciar o servidor MCP localmente:

```bash
# Install MarkItDown with MCP support
pip install 'markitdown[mcp]'

# Start the MCP server (stdio transport)
markitdown --mcp
```

Em seguida, adicione-o à configuração do seu cliente MCP:

```json
{
  "mcpServers": {
    "markitdown": {
      "command": "markitdown",
      "args": ["--mcp"]
    }
  }
}
```

---

## 🐛 Exercício de Correção de Bugs

O arquivo `lab-080/broken_markitdown.py` tem **3 bugs** nas funções de análise. Você consegue encontrar e corrigir todos?

Execute os autotestes para ver quais falham:

```bash
python lab-080/broken_markitdown.py
```

Você deverá ver **3 testes falhando**. Cada teste corresponde a um bug:

| Teste | O que verifica | Dica |
|-------|---------------|------|
| Teste 1 | Cálculo da taxa de sucesso | Deve contar `True`, não `False` |
| Teste 2 | Cálculo da qualidade média | Deve filtrar apenas conversões bem-sucedidas primeiro |
| Teste 3 | Total de tabelas encontradas | Deve somar `tables_found`, não `images_found` |

Corrija todos os 3 bugs e execute novamente. Quando você vir `All passed!`, está feito!

---

## 🧠 Verificação de Conhecimento

??? question "**Q1 (Múltipla Escolha):** Quais formatos o MarkItDown suporta para conversão em Markdown?"

    - A) Apenas documentos PDF e Word
    - B) PDF, DOCX, XLSX, PPTX, HTML, CSV, JSON e imagens
    - C) Apenas formatos baseados em texto como HTML e CSV
    - D) Qualquer formato, incluindo arquivos de vídeo e áudio

    ??? success "✅ Revelar Resposta"
        **Correto: B) PDF, DOCX, XLSX, PPTX, HTML, CSV, JSON e imagens**

        O MarkItDown suporta uma ampla variedade de formatos de documentos incluindo PDF (via pdfminer), documentos Word (python-docx), planilhas Excel (openpyxl), apresentações PowerPoint (python-pptx), HTML (BeautifulSoup), CSV, JSON e imagens (via OCR ou legendagem por LLM). Ele não suporta arquivos de áudio ou vídeo.

??? question "**Q2 (Múltipla Escolha):** Como o servidor MCP do MarkItDown possibilita a ingestão de documentos baseada em agentes?"

    - A) Ele converte documentos diretamente em embeddings
    - B) Ele expõe uma ferramenta `convert_to_markdown` que qualquer agente compatível com MCP pode chamar
    - C) Ele exige que os agentes baixem e analisem os arquivos por conta própria
    - D) Ele armazena documentos convertidos em um banco de dados vetorial automaticamente

    ??? success "✅ Revelar Resposta"
        **Correto: B) Ele expõe uma ferramenta `convert_to_markdown` que qualquer agente compatível com MCP pode chamar**

        O servidor MCP do MarkItDown funciona como um servidor de ferramentas MCP padrão (via transporte stdio ou SSE). Ele expõe uma ferramenta `convert_to_markdown` que aceita um URI de arquivo e retorna o Markdown convertido. Qualquer cliente compatível com MCP — GitHub Copilot, Claude Desktop ou agentes personalizados — pode chamar essa ferramenta para ingerir documentos em tempo real sem nenhum código de integração personalizado.

??? question "**Q3 (Execute o Laboratório):** Quantas das 12 conversões de arquivos foram bem-sucedidas?"

    Carregue [📥 `conversion_results.csv`](https://github.com/lcarli/AI-LearningHub/raw/main/docs/docs/en/labs/lab-080/conversion_results.csv) e conte as linhas onde `conversion_success == True`.

    ??? success "✅ Revelar Resposta"
        **11 de 12**

        Todas as conversões foram bem-sucedidas exceto D11 (`corrupted_file.pdf`), que era um PDF corrompido com tamanho de arquivo de 0 KB. O MarkItDown lida de forma confiável com arquivos válidos em todos os 7 formatos testados.

??? question "**Q4 (Execute o Laboratório):** Qual é o número total de tabelas encontradas em todas as conversões bem-sucedidas?"

    Filtre para conversões bem-sucedidas e calcule `tables_found.sum()`.

    ??? success "✅ Revelar Resposta"
        **31**

        Soma de `tables_found` nas 11 conversões bem-sucedidas: D01(6) + D02(2) + D03(5) + D04(1) + D05(0) + D06(0) + D07(1) + D08(1) + D09(0) + D10(15) + D12(0) = **31 tabelas**.

??? question "**Q5 (Execute o Laboratório):** Qual é a pontuação média de qualidade para conversões bem-sucedidas?"

    Filtre para `conversion_success == True`, depois calcule `quality_score.mean()`.

    ??? success "✅ Revelar Resposta"
        **≈ 0,916**

        Pontuações de qualidade para as 11 conversões bem-sucedidas: 0,92 + 0,95 + 0,98 + 0,85 + 0,97 + 0,94 + 0,96 + 0,99 + 0,98 + 0,82 + 0,72 = **10,08**. Média = 10,08 ÷ 11 ≈ **0,916**.

---

## Resumo

| Tópico | O que Você Aprendeu |
|--------|---------------------|
| MarkItDown | Converte PDF, DOCX, XLSX, PPTX, HTML, CSV, JSON e imagens em Markdown estruturado |
| Integração MCP | O servidor MCP expõe a ferramenta `convert_to_markdown` para qualquer agente compatível |
| Análise de Qualidade | Formatos estruturados (CSV, JSON, XLSX) alcançam qualidade ≥0,98; imagens com a menor em 0,72 |
| Análise de Velocidade | PDFs grandes e imagens são os mais lentos; CSV/JSON convertem em menos de 50ms |
| Taxa de Sucesso | 11/12 conversões bem-sucedidas — apenas arquivos corrompidos falham |
| Extração de Elementos | 31 tabelas, 62 imagens, 103 títulos extraídos nas conversões bem-sucedidas |

---

## Próximos Passos

- **[Lab 081](lab-081-agentic-coding-tools.md)** — Ferramentas de Codificação Agêntica: Claude Code vs Copilot CLI
- Explore o [repositório do MarkItDown no GitHub](https://github.com/microsoft/markitdown) para configuração avançada e conversores personalizados
