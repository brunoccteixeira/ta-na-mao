# Skill: Finalizar Branch

Workflow para fechar uma branch de feature/fix corretamente.

## Checklist Pré-Merge

### 1. Verificar Testes
```bash
# Backend
pytest backend/tests/ -v

# Frontend
cd frontend && npm test
```

### 2. Verificar Linting
```bash
# Backend (se configurado)
cd backend && ruff check .

# Frontend
cd frontend && npm run lint
```

### 3. Atualizar com Main
```bash
git fetch origin
git rebase origin/main
# Resolver conflitos se houver
```

### 4. Revisar Mudanças
```bash
# Ver todos os commits da branch
git log origin/main..HEAD --oneline

# Ver diff completo
git diff origin/main...HEAD
```

## Criar Pull Request
```bash
# Push da branch
git push -u origin nome-da-branch

# Criar PR via gh CLI
gh pr create --title "feat: Descrição curta" --body "## Resumo
- O que foi feito

## Testes
- Como testar

## Checklist
- [ ] Testes passando
- [ ] Código revisado"
```

## Após Aprovação

### Merge (squash recomendado)
```bash
gh pr merge --squash
```

### Limpar Branch Local
```bash
git checkout main
git pull origin main
git branch -d nome-da-branch
```

## Padrões de Commit

```
feat: Adiciona consulta de BPC
fix: Corrige timeout na API do agente
docs: Atualiza README com instruções de deploy
refactor: Simplifica lógica de validação de CPF
test: Adiciona testes para farmácia finder
```

## Resolução de Conflitos

```bash
# Durante rebase
git status                    # Ver arquivos em conflito
# Editar arquivos manualmente
git add <arquivo>
git rebase --continue

# Se precisar abortar
git rebase --abort
```

## Rollback de Merge
```bash
# Identificar commit do merge
git log --oneline -10

# Reverter
git revert -m 1 <commit-hash>
git push origin main
```
