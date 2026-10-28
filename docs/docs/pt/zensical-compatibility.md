# Relatório de Compatibilidade com Zensical — Fase 3

**Decisão:** manter o build atual de produção até existir suporte sem regressão para i18n trilíngue por pastas.

A migração foi reavaliada com a documentação oficial atual de instalação, migração de MkDocs e compatibilidade de plugins do Zensical. O site exige rotas EN/PT/FR por `mkdocs-static-i18n`, além de busca, tags, glightbox, JavaScript, CSS, catálogo JSON, quizzes, progresso e kits. A compatibilidade documentada ainda não fornece caminho equivalente suportado para esse contrato por pastas.

Trocar o mecanismo degradaria o site e violaria a Fase 3. A CI mantém o build estrito do MkDocs e o conteúdo continua pronto para migração.

## Gate para novo teste

Migrar somente quando um build limpo provar contagem e rotas EN/PT/FR idênticas, navegação, busca, tags, glightbox, JS/CSS, quizzes, progresso, catálogos e links internos estritos.

## Referências oficiais

- [Zensical: primeiros passos](https://zensical.org/docs/get-started/)
- [Migração do MkDocs](https://zensical.org/docs/compatibility/mkdocs/migration/)
- [Plugins compatíveis](https://zensical.org/docs/compatibility/mkdocs/plugins/)
