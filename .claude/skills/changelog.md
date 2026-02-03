# Skill: Manter o CHANGELOG

Documentação de todas as mudanças relevantes do projeto no formato Keep a Changelog.

## Formato

Baseado em [Keep a Changelog](https://keepachangelog.com/pt-BR/1.1.0/) + [Semantic Versioning](https://semver.org/).

### Estrutura de uma Entrada
```markdown
## [versão] - AAAA-MM-DD

### Added (Adicionado)
- Funcionalidades novas

### Changed (Modificado)
- Mudanças em funcionalidades existentes

### Fixed (Corrigido)
- Correções de bugs

### Removed (Removido)
- Funcionalidades removidas

### Security (Segurança)
- Correções de vulnerabilidades

### Deprecated (Descontinuado)
- Funcionalidades que serão removidas no futuro
```

## Regras

1. **Sempre atualizar** o CHANGELOG ao fazer merge de feature/fix
2. **Linguagem simples** — descrever o que mudou para quem usa, não para quem codou
3. **Agrupar por tipo** — Added, Changed, Fixed, etc.
4. **Unreleased** no topo — mudanças que ainda não viraram release
5. **Data no formato ISO** — AAAA-MM-DD
6. **Link para PR/commit** quando relevante
7. **Nunca apagar entradas antigas** — CHANGELOG é histórico permanente

## Versionamento

```
MAJOR.MINOR.PATCH

MAJOR: Mudança incompatível (nova arquitetura, breaking change)
MINOR: Nova funcionalidade compatível (novo benefício, nova skill, novo módulo)
PATCH: Correção de bug, ajuste de texto, fix pontual
```

### Exemplos para o Tá na Mão
```
1.0.0 → MVP inicial (backend + frontend + agente)
1.1.0 → Adicionar módulo PIS/PASEP e Dinheiro Esquecido
1.2.0 → Adicionar 97 benefícios municipais
1.3.0 → API v2 unificada de benefícios
1.4.0 → Integrar Frontend e Android com API v2
1.5.0 → Adicionar 23 novas skills
2.0.0 → Integração Gov.br (Login Único) — breaking: autenticação muda
```

## Quando Atualizar

| Evento | Seção | Exemplo |
|--------|-------|---------|
| Novo benefício adicionado | Added | "Adicionado Auxílio Gás ao catálogo" |
| Novo módulo/feature | Added | "Adicionado módulo de Dinheiro Esquecido" |
| Correção de cálculo | Fixed | "Corrigido cálculo de renda per capita no BPC" |
| Mudança de API | Changed | "API de benefícios migrada para v2" |
| Dependência atualizada | Changed | "Atualizado Gemini de 1.5 para 2.0 Flash" |
| Skill nova | Added | "Adicionada skill de integração Gov.br" |
| Remoção de feature | Removed | "Removido endpoint legado /api/v1/benefits" |
| Vulnerabilidade corrigida | Security | "Corrigida exposição de CPF em logs" |

## Como Escrever Boas Entradas

### Bom
```
- Adicionado catálogo com 97 benefícios municipais para as 40 maiores cidades
- Corrigido bug que impedia consulta de BPC para idosos acima de 80 anos
- Adicionado alerta quando CadÚnico está próximo de vencer
```

### Ruim
```
- Fix bug                          (vago demais)
- Refatorado service layer         (irrelevante pro usuário)
- Atualizado dependencies          (genérico demais)
- Merged PR #42                    (sem significado)
```

## Arquivo
```
Localização: /CHANGELOG.md (raiz do projeto)
```

## Checklist por Release
- [ ] CHANGELOG atualizado com todas as mudanças
- [ ] Versão incrementada corretamente (MAJOR/MINOR/PATCH)
- [ ] Data da release adicionada
- [ ] [Unreleased] movido para nova versão
- [ ] Novo [Unreleased] vazio adicionado no topo
- [ ] Commit com tag de versão: `git tag v1.5.0`
