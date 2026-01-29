# Skill: Criar Nova Skill

Template e guia para criar skills no padrão do Tá na Mão.

## Estrutura de uma Skill

```markdown
# Skill: Nome da Skill

Descrição breve do que a skill faz.

## Comandos/Ações Principais
[Lista de comandos ou ações]

## Como Usar
[Exemplos práticos]

## Arquivos Relacionados
[Arquivos do projeto relevantes]

## Troubleshooting (opcional)
[Problemas comuns e soluções]
```

## Template Básico

```markdown
# Skill: [Nome]

[Descrição em 1-2 linhas]

## Comandos
\`\`\`bash
# Comando principal
comando exemplo

# Variações
comando --flag
\`\`\`

## Exemplos

### Caso de Uso 1
\`\`\`
[exemplo]
\`\`\`

### Caso de Uso 2
\`\`\`
[exemplo]
\`\`\`

## Arquivos
- `caminho/arquivo1.py` - Descrição
- `caminho/arquivo2.py` - Descrição

## Dicas
- Dica 1
- Dica 2
```

## Categorias de Skills

| Categoria | Foco | Exemplo |
|-----------|------|---------|
| Domínio | Benefícios sociais | beneficio-checker.md |
| Desenvolvimento | Código e testes | run-tests.md |
| Infraestrutura | Deploy e ops | deploy.md |
| Dados | Processamento | csv-analyzer.md |
| Escrita | Documentação | linguagem-simples.md |
| Segurança | Proteção | defense-in-depth.md |

## Boas Práticas

1. **Nome**: Use kebab-case (palavras-separadas-por-hifen)
2. **Extensão**: Sempre `.md`
3. **Localização**: `.claude/skills/`
4. **Linguagem**: Português (projeto brasileiro)
5. **Exemplos**: Sempre incluir comandos que funcionam
6. **Concisão**: Direto ao ponto, sem enrolação

## Integração com MCP

Se a skill usa um MCP server:

```markdown
## Dependência MCP

Utiliza o MCP `nome-do-mcp` configurado em `.mcp.json`.

### Ações Disponíveis
\`\`\`
mcp__nome__acao1
mcp__nome__acao2
\`\`\`
```

## Checklist Nova Skill

- [ ] Arquivo criado em `.claude/skills/`
- [ ] Nome em kebab-case
- [ ] Descrição clara
- [ ] Exemplos funcionais
- [ ] Adicionado ao README.md
- [ ] Testado manualmente
