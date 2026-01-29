# Skills do Tá na Mão

Índice de todas as skills disponíveis para o Claude Code neste projeto.

## Skills de Domínio (Benefícios Sociais)

| Skill | Descrição |
|-------|-----------|
| [beneficio-checker](beneficio-checker.md) | Consultar benefícios por CPF |
| [dinheiro-esquecido](dinheiro-esquecido.md) | PIS/PASEP, SVR, FGTS esquecido |
| [checklist-gen](checklist-gen.md) | Gerar lista de documentos necessários |
| [farmacia-finder](farmacia-finder.md) | Encontrar Farmácias Populares |
| [cras-finder](cras-finder.md) | Encontrar CRAS próximos |

## Skills de Desenvolvimento

| Skill | Descrição |
|-------|-----------|
| [run-tests](run-tests.md) | Executar testes com workflow TDD |
| [webapp-testing](webapp-testing.md) | Testes E2E com Playwright |
| [debug-agent](debug-agent.md) | Depurar o agente com metodologia |
| [root-cause-tracing](root-cause-tracing.md) | Rastrear origem de bugs |
| [finishing-branch](finishing-branch.md) | Workflow para finalizar branches |
| [git-workflow](git-workflow.md) | Automação de operações git |
| [skill-creator](skill-creator.md) | Template para criar novas skills |

## Skills de Infraestrutura

| Skill | Descrição |
|-------|-----------|
| [deploy](deploy.md) | Deploy com Docker e verificação |
| [data-ingestion](data-ingestion.md) | Jobs de ingestão de dados |
| [api-docs](api-docs.md) | Documentação da API |

## Skills de Dados & Documentos

| Skill | Descrição |
|-------|-----------|
| [pdf](pdf.md) | Processar PDFs (laudos, comprovantes) |
| [postgres](postgres.md) | Queries SQL seguras (read-only) |
| [csv-analyzer](csv-analyzer.md) | Analisar datasets CSV |
| [xlsx](xlsx.md) | Gerar/processar planilhas Excel |

## Skills de Escrita & Pesquisa

| Skill | Descrição |
|-------|-----------|
| [linguagem-simples](linguagem-simples.md) | Escrita acessível (5ª série) |
| [deep-research](deep-research.md) | Pesquisa aprofundada |
| [brainstorming](brainstorming.md) | Design de features |

## Skills de Segurança

| Skill | Descrição |
|-------|-----------|
| [defense-in-depth](defense-in-depth.md) | Checklist de segurança multi-camada |
| [varlock](varlock.md) | Gerenciamento de secrets e .env |
| [plannotator](plannotator.md) | Revisão interativa de planos |

---

## Uso

Invocar uma skill: `/nome-da-skill`

Exemplo:
```
/run-tests
/beneficio-checker
/deep-research
```

## MCP Servers Integrados

Algumas skills utilizam MCP servers configurados em `.mcp.json`:

- **pdf.md** → MCP `pdf-ocr`
- **webapp-testing.md** → MCP `playwright`
- **farmacia-finder.md** → MCP `google-maps`
- **cras-finder.md** → MCP `google-maps`
