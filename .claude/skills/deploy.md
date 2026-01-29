# Skill: Deploy

## Comandos
```bash
# Desenvolvimento local
docker compose up -d

# Produção
docker compose -f docker-compose.prod.yml up -d

# Rebuild após mudanças
docker compose up -d --build
```

## Health Checks

### Verificar Serviços
```bash
# API Backend
curl http://localhost:8000/health

# PostgreSQL
docker compose exec db pg_isready

# Redis
docker compose exec redis redis-cli PING
```

### Verificar Logs
```bash
# Todos os serviços
docker compose logs -f

# Serviço específico
docker compose logs -f backend
docker compose logs -f db
docker compose logs -f redis
```

## Rollback

### Voltar para versão anterior
```bash
# Parar serviços
docker compose down

# Voltar código
git checkout HEAD~1

# Reiniciar
docker compose up -d --build
```

### Backup do banco antes de deploy
```bash
docker compose exec db pg_dump -U postgres tanamao > backup_$(date +%Y%m%d).sql
```

## Troubleshooting

| Problema | Causa Provável | Solução |
|----------|----------------|---------|
| Container não inicia | Porta ocupada | `lsof -i :8000` e matar processo |
| DB connection refused | PostgreSQL não pronto | Aguardar ou `docker compose restart db` |
| Redis timeout | Redis não iniciou | `docker compose restart redis` |
| Build falha | Cache corrompido | `docker compose build --no-cache` |
| .env não carrega | Arquivo ausente | Copiar de `.env.example` |

## Checklist Pré-Deploy

- [ ] Testes passando (`pytest backend/tests/`)
- [ ] Variáveis de ambiente configuradas
- [ ] Migrations aplicadas (`alembic upgrade head`)
- [ ] Backup do banco realizado
- [ ] Health check OK após deploy

## Arquivos
- `backend/Dockerfile`
- `backend/docker-compose.yml` (dev)
- `backend/docker-compose.prod.yml` (prod)
- `backend/.env` (não commitar)
- `backend/.env.example` (template)
