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
| [cadunico-api](cadunico-api.md) | API CadÚnico via Conecta Gov.br |
| [rede-protecao](rede-protecao.md) | Rede de proteção social + encaminhamento de urgência |
| [rede-suas](rede-suas.md) | Navegação na rede SUAS (CRAS/CREAS/CAPS/Centro POP) |
| [direitos-trabalhistas](direitos-trabalhistas.md) | Guia de direitos por tipo de vínculo + calculadoras |
| [mei-simplificado](mei-simplificado.md) | Guia MEI com simulador de impacto nos benefícios |

## Skills de Gestão Pública & Governo Digital

| Skill | Descrição |
|-------|-----------|
| [govbr-integrator](govbr-integrator.md) | Integração Gov.br (Login Único + APIs Conecta) |
| [orcamento-participativo](orcamento-participativo.md) | Orçamento participativo digital |
| [painel-gestor](painel-gestor.md) | Dashboard para gestores municipais |
| [monitor-legislacao](monitor-legislacao.md) | Monitor de mudanças legislativas |
| [dados-abertos](dados-abertos.md) | Pipeline de dados abertos governamentais |
| [indicadores-sociais](indicadores-sociais.md) | Painel de indicadores sociais (IBGE/IPEA/MDS) |
| [mapa-social](mapa-social.md) | Mapeamento social territorial + desertos de assistência |

## Skills de Inclusão & Acessibilidade

| Skill | Descrição |
|-------|-----------|
| [linguagem-simples](linguagem-simples.md) | Escrita acessível (5ª série) |
| [acompanhante-digital](acompanhante-digital.md) | Modo acompanhante para agentes comunitários/familiares |
| [voz-acessivel](voz-acessivel.md) | Interface por voz (speech-to-text + text-to-speech) |
| [pwa-offline](pwa-offline.md) | Modo offline / PWA para áreas sem internet |
| [whatsapp-flows](whatsapp-flows.md) | Fluxos conversacionais WhatsApp |
| [a11y-auditor](a11y-auditor.md) | Auditor de acessibilidade WCAG 2.1 AA |

## Skills de Economia & Negócios

| Skill | Descrição |
|-------|-----------|
| [educacao-financeira](educacao-financeira.md) | Micro-lições financeiras + alerta de golpes |
| [economia-solidaria](economia-solidaria.md) | Diretório de cooperativas e economia solidária |
| [impacto-esg](impacto-esg.md) | Relatórios de impacto social (ESG/ODS) |
| [vulnerabilidade-preditiva](vulnerabilidade-preditiva.md) | Score de risco social + recomendações proativas |

## Skills de Pesquisa & Dados

| Skill | Descrição |
|-------|-----------|
| [deep-research](deep-research.md) | Pesquisa aprofundada |
| [brainstorming](brainstorming.md) | Design de features |
| [pesquisa-campo](pesquisa-campo.md) | Pesquisa de campo digital (questionários + análise) |
| [pdf](pdf.md) | Processar PDFs (laudos, comprovantes) |
| [postgres](postgres.md) | Queries SQL seguras (read-only) |
| [csv-analyzer](csv-analyzer.md) | Analisar datasets CSV |
| [xlsx](xlsx.md) | Gerar/processar planilhas Excel |

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
| [changelog](changelog.md) | Manter o CHANGELOG do projeto |

## Skills de Infraestrutura

| Skill | Descrição |
|-------|-----------|
| [deploy](deploy.md) | Deploy com Docker e verificação |
| [data-ingestion](data-ingestion.md) | Jobs de ingestão de dados |
| [api-docs](api-docs.md) | Documentação da API |

## Skills de Segurança

| Skill | Descrição |
|-------|-----------|
| [defense-in-depth](defense-in-depth.md) | Checklist de segurança multi-camada |
| [varlock](varlock.md) | Gerenciamento de secrets e .env |
| [plannotator](plannotator.md) | Revisão interativa de planos |
| [seguranca-cidada](seguranca-cidada.md) | Proteção de dados do cidadão (LGPD+) |

---

## Resumo

| Categoria | Skills | Novas |
|-----------|--------|-------|
| Domínio (Benefícios) | 10 | +5 |
| Gestão Pública | 7 | +7 |
| Inclusão & Acessibilidade | 6 | +5 |
| Economia & Negócios | 4 | +4 |
| Pesquisa & Dados | 7 | +1 |
| Desenvolvimento | 8 | +1 |
| Infraestrutura | 3 | — |
| Segurança | 4 | +1 |
| **Total** | **49** | **+24** |

## Uso

Invocar uma skill: `/nome-da-skill`

Exemplo:
```
/run-tests
/beneficio-checker
/deep-research
/cadunico-api
/rede-protecao
```

## MCP Servers Integrados

Algumas skills utilizam MCP servers configurados em `.mcp.json`:

- **pdf.md** → MCP `pdf-ocr`
- **webapp-testing.md** → MCP `playwright`
- **farmacia-finder.md** → MCP `google-maps`
- **cras-finder.md** → MCP `google-maps`
