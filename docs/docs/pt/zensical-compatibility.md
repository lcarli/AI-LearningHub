# Relatório de Compatibilidade com Zensical — Fase 2

**Decisão:** não migrar o site de produção na Fase 2.

## Teste isolado

A árvore `docs/` foi copiada para uma pasta temporária da sessão e um ambiente virtual limpo foi criado. Dois caminhos de instalação foram tentados:

1. o feed Python configurado solicitou o wheel Windows ARM64 e retornou HTTP 404;
2. o PyPI direto encontrou Zensical 0.0.73, mas o host falhou no handshake TLS com `files.pythonhosted.org`.

O Docker também foi verificado, porém o mecanismo do Docker Desktop não estava ativo. Nenhum arquivo do repositório ou configuração de produção foi alterado.

## Bloqueio acionável de compatibilidade

O repositório depende de `mkdocs-static-i18n` com `docs_structure: folder` para compilar EN, PT e FR em uma configuração. A lista oficial de plugins compatíveis do Zensical ainda não inclui esse plugin e a documentação trata i18n nativo como trabalho futuro. Uma troca agora poderia remover ou rotear incorretamente dois idiomas.

## Superfícies compatíveis

- Zensical lê `mkdocs.yml` e permite migração gradual.
- Search, tags e glightbox possuem caminhos documentados de compatibilidade.
- O repositório não usa a configuração MkDocs `hooks`, não suportada.

## Resultado

O critério da Fase 2 é atendido por um relatório explícito e reproduzível: **i18n trilíngue é o bloqueio de produto**. Repetir o teste quando houver i18n nativo por pastas ou compatibilidade verificada com `mkdocs-static-i18n`. Manter MkDocs Material em produção até que navegação, contagem de páginas, rotas de idiomas, busca, tags e links estritos sejam equivalentes.

## Procedimento para novo teste

```powershell
python -m venv .zensical-test
.zensical-test\Scripts\python -m pip install zensical
Copy-Item -Recurse docs .zensical-test\docs-copy
Push-Location .zensical-test\docs-copy
..\Scripts\zensical build
Pop-Location
```

Compare a saída com `python -m mkdocs build --strict`, incluindo todas as rotas EN/PT/FR.

## Referências oficiais

- [Zensical: primeiros passos](https://zensical.org/docs/get-started/)
- [Zensical: migrar do MkDocs](https://zensical.org/docs/compatibility/mkdocs/migration/)
- [Zensical: plugins MkDocs compatíveis](https://zensical.org/docs/compatibility/mkdocs/plugins/)
