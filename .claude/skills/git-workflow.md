# Skill: Workflow Git

Automação de operações git comuns no projeto.

## Criar Nova Branch
```bash
# Feature
git checkout -b feat/nome-da-feature

# Bug fix
git checkout -b fix/descricao-do-bug

# Documentação
git checkout -b docs/o-que-documenta
```

## Commit Atômico
```bash
# Adicionar arquivos específicos (preferível)
git add backend/app/services/novo_servico.py
git add backend/tests/test_novo_servico.py

# Commit com mensagem descritiva
git commit -m "feat: Adiciona serviço de consulta de BPC

- Implementa consulta por CPF
- Adiciona cache Redis
- Inclui testes unitários"
```

## Padrões de Mensagem

| Prefixo | Uso |
|---------|-----|
| `feat:` | Nova funcionalidade |
| `fix:` | Correção de bug |
| `docs:` | Documentação |
| `refactor:` | Refatoração sem mudar comportamento |
| `test:` | Adição/correção de testes |
| `chore:` | Manutenção (deps, configs) |

## Sincronizar com Main
```bash
# Fetch das mudanças remotas
git fetch origin

# Rebase na main (preferível a merge)
git rebase origin/main

# Se houver conflitos
git status                    # Ver arquivos em conflito
# Resolver manualmente
git add <arquivos>
git rebase --continue
```

## Push e PR
```bash
# Push da branch
git push -u origin feat/nome-da-feature

# Criar PR
gh pr create --title "feat: Título" --body "Descrição"

# Ver status do PR
gh pr status
```

## Desfazer Mudanças

### Último commit (não pushado)
```bash
git reset --soft HEAD~1  # Mantém mudanças staged
git reset --hard HEAD~1  # Descarta mudanças (cuidado!)
```

### Arquivo específico
```bash
git checkout -- caminho/arquivo.py
```

### Mudanças staged
```bash
git reset HEAD caminho/arquivo.py
```

## Stash (guardar temporariamente)
```bash
# Guardar
git stash push -m "WIP: descrição"

# Listar
git stash list

# Recuperar
git stash pop
```

## Ver Histórico
```bash
# Commits recentes
git log --oneline -10

# Commits da branch atual vs main
git log origin/main..HEAD --oneline

# Mudanças de um arquivo
git log --follow -p -- caminho/arquivo.py
```

## Aliases Úteis
```bash
# Adicionar no ~/.gitconfig
[alias]
    st = status
    co = checkout
    br = branch
    cm = commit -m
    lg = log --oneline -10
```
