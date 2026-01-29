# Guia de Contribuição - Tá na Mão

Obrigado pelo interesse em contribuir com o projeto Tá na Mão! Este guia descreve as práticas e convenções do projeto.

## Índice

- [Código de Conduta](#código-de-conduta)
- [Como Contribuir](#como-contribuir)
- [Estrutura do Projeto](#estrutura-do-projeto)
- [Padrões de Código](#padrões-de-código)
- [Fluxo de Trabalho Git](#fluxo-de-trabalho-git)
- [Pull Requests](#pull-requests)
- [Issues](#issues)

---

## Código de Conduta

Este projeto adota um código de conduta baseado no [Contributor Covenant](https://www.contributor-covenant.org/). Esperamos que todos os contribuidores:

- Sejam respeitosos e inclusivos
- Aceitem críticas construtivas
- Foquem no que é melhor para a comunidade
- Demonstrem empatia com outros membros

---

## Como Contribuir

### 1. Configure o Ambiente

Siga o guia [GETTING_STARTED.md](./GETTING_STARTED.md) para configurar seu ambiente de desenvolvimento.

### 2. Encontre uma Issue

- Procure issues com label `good first issue` para começar
- Issues com `help wanted` precisam de contribuidores
- Comente na issue antes de começar para evitar trabalho duplicado

### 3. Crie uma Branch

```bash
# Atualize a main
git checkout main
git pull origin main

# Crie sua branch
git checkout -b tipo/descricao-curta
```

**Tipos de branch:**
| Prefixo | Uso |
|---------|-----|
| `feat/` | Nova funcionalidade |
| `fix/` | Correção de bug |
| `docs/` | Documentação |
| `refactor/` | Refatoração |
| `test/` | Testes |
| `chore/` | Tarefas de manutenção |

**Exemplos:**
```bash
git checkout -b feat/adicionar-filtro-regiao
git checkout -b fix/corrigir-calculo-cobertura
git checkout -b docs/atualizar-api-docs
```

### 4. Desenvolva

- Faça commits pequenos e frequentes
- Escreva testes para novas funcionalidades
- Atualize a documentação se necessário

### 5. Abra um Pull Request

- Preencha o template do PR
- Vincule a issue relacionada
- Aguarde a revisão

---

## Estrutura do Projeto

```
Ta na Mao/
├── backend/                 # API FastAPI + PostgreSQL
│   ├── app/
│   │   ├── models/          # Modelos SQLAlchemy
│   │   ├── schemas/         # Schemas Pydantic
│   │   ├── routers/         # Endpoints da API
│   │   └── jobs/            # Scripts de ingestão
│   ├── alembic/             # Migrações do banco
│   └── docs/                # Documentação técnica
│
├── frontend/                # Dashboard React + Vite
│   ├── src/
│   │   ├── api/             # Cliente HTTP
│   │   ├── components/      # Componentes React
│   │   ├── hooks/           # Hooks customizados
│   │   └── stores/          # Estado (Zustand)
│   └── docs/                # Documentação técnica
│
├── android/                 # App Android (Kotlin)
│   ├── app/src/main/
│   │   ├── java/.../        # Código Kotlin
│   │   └── res/             # Recursos (layouts, strings)
│   └── docs/                # Documentação técnica
│
├── GETTING_STARTED.md       # Guia de setup
├── CONTRIBUTING.md          # Este arquivo
├── DOCUMENTO_EXECUTIVO.md   # Documento consolidado
└── CONCEITO_COMPLETO.md     # Conceito para público geral
```

---

## Padrões de Código

### Python (Backend)

**Estilo:**
- PEP 8
- Docstrings no formato Google
- Type hints obrigatórios

**Ferramentas:**
```bash
# Formatação
black app/

# Ordenação de imports
isort app/

# Linting
flake8 app/

# Type checking
mypy app/
```

**Exemplo:**
```python
from typing import Optional
from sqlalchemy.orm import Session

from app.models.municipality import Municipality
from app.schemas.municipality import MunicipalityResponse


def get_municipality(
    db: Session,
    ibge_code: str,
    program: Optional[str] = None
) -> MunicipalityResponse:
    """Busca um município pelo código IBGE.

    Args:
        db: Sessão do banco de dados
        ibge_code: Código IBGE do município (7 dígitos)
        program: Código do programa para filtrar dados

    Returns:
        Dados do município com estatísticas

    Raises:
        HTTPException: Se município não encontrado
    """
    municipality = db.query(Municipality).filter(
        Municipality.ibge_code == ibge_code
    ).first()

    if not municipality:
        raise HTTPException(status_code=404, detail="Município não encontrado")

    return MunicipalityResponse.from_orm(municipality)
```

### TypeScript (Frontend)

**Estilo:**
- ESLint + Prettier
- Componentes funcionais com hooks
- Props tipadas com interfaces

**Ferramentas:**
```bash
# Lint
npm run lint

# Formatação (se configurado)
npm run format
```

**Exemplo:**
```typescript
import { useQuery } from '@tanstack/react-query';
import { getMunicipality } from '@/api/client';

interface MunicipalityCardProps {
  ibgeCode: string;
  program?: string;
}

export function MunicipalityCard({ ibgeCode, program }: MunicipalityCardProps) {
  const { data, isLoading, error } = useQuery({
    queryKey: ['municipality', ibgeCode, program],
    queryFn: () => getMunicipality(ibgeCode, program),
  });

  if (isLoading) return <Skeleton />;
  if (error) return <ErrorCard message="Erro ao carregar" />;

  return (
    <div className="bg-white rounded-lg shadow p-4">
      <h2 className="text-lg font-bold">{data.name}</h2>
      {/* ... */}
    </div>
  );
}
```

### Kotlin (Android)

**Estilo:**
- [Kotlin Coding Conventions](https://kotlinlang.org/docs/coding-conventions.html)
- Jetpack Compose para UI
- Clean Architecture (Data → Domain → Presentation)

**Exemplo:**
```kotlin
@Composable
fun MunicipalityCard(
    municipality: Municipality,
    onSelect: (String) -> Unit,
    modifier: Modifier = Modifier
) {
    Card(
        modifier = modifier
            .fillMaxWidth()
            .clickable { onSelect(municipality.ibgeCode) },
        elevation = CardDefaults.cardElevation(defaultElevation = 2.dp)
    ) {
        Column(modifier = Modifier.padding(16.dp)) {
            Text(
                text = municipality.name,
                style = MaterialTheme.typography.titleMedium
            )
            Text(
                text = "${municipality.stateName} - ${municipality.region}",
                style = MaterialTheme.typography.bodyMedium,
                color = MaterialTheme.colorScheme.onSurfaceVariant
            )
        }
    }
}
```

---

## Fluxo de Trabalho Git

### Commits

**Formato:**
```
tipo(escopo): descrição curta

Corpo opcional com mais detalhes.

Closes #123
```

**Tipos:**
| Tipo | Descrição |
|------|-----------|
| `feat` | Nova funcionalidade |
| `fix` | Correção de bug |
| `docs` | Documentação |
| `style` | Formatação (não altera código) |
| `refactor` | Refatoração |
| `test` | Testes |
| `chore` | Manutenção |

**Exemplos:**
```bash
git commit -m "feat(api): adicionar endpoint de ranking de municípios"
git commit -m "fix(map): corrigir zoom no click do estado"
git commit -m "docs(readme): atualizar instruções de setup"
```

### Branches

```
main
 └── feat/nova-funcionalidade
 └── fix/bug-critico
 └── docs/atualizar-api
```

**Regras:**
- `main` é protegida (requer PR aprovado)
- Branches de feature partem de `main`
- Merge via PR com squash

---

## Pull Requests

### Template

```markdown
## Descrição

Breve descrição das mudanças.

## Tipo de Mudança

- [ ] Bug fix
- [ ] Nova feature
- [ ] Breaking change
- [ ] Documentação

## Checklist

- [ ] Testes passando
- [ ] Documentação atualizada
- [ ] Código segue padrões do projeto

## Screenshots (se aplicável)

Antes | Depois
--- | ---
img | img

## Issues Relacionadas

Closes #123
```

### Processo de Review

1. **Autor** abre PR e solicita review
2. **Revisor** analisa código e deixa comentários
3. **Autor** faz ajustes necessários
4. **Revisor** aprova
5. **Autor** faz merge (squash)

### Critérios de Aprovação

- Testes passando
- Cobertura de testes mantida ou aumentada
- Sem warnings de lint
- Documentação atualizada
- Aprovação de pelo menos 1 revisor

---

## Issues

### Como Reportar Bugs

Use o template de bug report:

```markdown
**Descrição**
Descrição clara do bug.

**Passos para Reproduzir**
1. Ir para '...'
2. Clicar em '...'
3. Ver erro

**Comportamento Esperado**
O que deveria acontecer.

**Comportamento Atual**
O que está acontecendo.

**Screenshots**
Se aplicável.

**Ambiente**
- OS: [ex: macOS 14.0]
- Browser: [ex: Chrome 120]
- Versão: [ex: commit abc123]
```

### Como Sugerir Features

Use o template de feature request:

```markdown
**Problema**
Qual problema esta feature resolve?

**Solução Proposta**
Descrição da solução.

**Alternativas Consideradas**
Outras abordagens pensadas.

**Contexto Adicional**
Screenshots, mockups, etc.
```

### Labels

| Label | Descrição |
|-------|-----------|
| `bug` | Algo não está funcionando |
| `enhancement` | Nova funcionalidade |
| `documentation` | Melhorias na documentação |
| `good first issue` | Boa para iniciantes |
| `help wanted` | Precisa de ajuda |
| `priority: high` | Urgente |
| `priority: low` | Pode esperar |

---

## Dúvidas?

- Abra uma issue com a label `question`
- Entre em contato com os mantenedores

---

Obrigado por contribuir! 🎉
