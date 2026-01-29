# Guia de Deployment - Tá na Mão

Este guia descreve como fazer deploy do Tá na Mão em produção.

## Pré-requisitos

- Docker e Docker Compose instalados
- Acesso ao servidor de produção
- Variáveis de ambiente configuradas
- Domínio configurado (opcional)

## Variáveis de Ambiente

Crie um arquivo `.env` na raiz do projeto com as seguintes variáveis:

```env
# Database
POSTGRES_USER=tanamao
POSTGRES_PASSWORD=<senha-forte>
POSTGRES_DB=tanamao
DATABASE_URL=postgresql://tanamao:<senha>@db:5432/tanamao

# Redis
REDIS_URL=redis://redis:6379/0

# Application
ENVIRONMENT=production
CORS_ORIGINS=https://seu-dominio.com,https://www.seu-dominio.com

# APIs Externas
GOOGLE_API_KEY=<sua-chave-gemini>
TWILIO_ACCOUNT_SID=<sua-conta-twilio>
TWILIO_AUTH_TOKEN=<seu-token-twilio>
TWILIO_WEBHOOK_URL=https://seu-dominio.com/api/v1/webhook/twilio

# Security
SECRET_KEY=<chave-secreta-aleatoria>
```

## Deploy com Docker Compose

### 1. Preparar o Ambiente

```bash
cd backend
cp .env.example .env
# Editar .env com valores de produção
```

### 2. Iniciar Serviços

```bash
docker-compose -f docker-compose.prod.yml up -d
```

### 3. Executar Migrações

```bash
docker-compose -f docker-compose.prod.yml exec api alembic upgrade head
```

### 4. Verificar Status

```bash
docker-compose -f docker-compose.prod.yml ps
docker-compose -f docker-compose.prod.yml logs -f api
```

## Deploy Manual (sem Docker)

### 1. Instalar Dependências

```bash
cd backend
python -m venv venv
source venv/bin/activate
pip install -r requirements.txt
```

### 2. Configurar Banco de Dados

```bash
# Criar banco de dados
createdb tanamao

# Executar migrações
alembic upgrade head
```

### 3. Iniciar Aplicação

```bash
# Com uvicorn
uvicorn app.main:app --host 0.0.0.0 --port 8000

# Com gunicorn (recomendado para produção)
gunicorn app.main:app -w 4 -k uvicorn.workers.UvicornWorker --bind 0.0.0.0:8000
```

## Nginx Reverse Proxy

Exemplo de configuração Nginx:

```nginx
server {
    listen 80;
    server_name api.tanamao.gov.br;

    location / {
        proxy_pass http://localhost:8000;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
        proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Proto $scheme;
    }
}
```

## Monitoramento

### Health Check

```bash
curl http://localhost:8000/health
```

### Métricas Prometheus

```bash
curl http://localhost:8000/metrics
```

## Backup do Banco de Dados

```bash
# Backup
docker-compose -f docker-compose.prod.yml exec db pg_dump -U tanamao tanamao > backup.sql

# Restore
docker-compose -f docker-compose.prod.yml exec -T db psql -U tanamao tanamao < backup.sql
```

## Atualização

```bash
# Pull latest code
git pull

# Rebuild containers
docker-compose -f docker-compose.prod.yml build

# Restart services
docker-compose -f docker-compose.prod.yml up -d

# Run migrations
docker-compose -f docker-compose.prod.yml exec api alembic upgrade head
```

## Troubleshooting

### Verificar Logs

```bash
docker-compose -f docker-compose.prod.yml logs -f api
docker-compose -f docker-compose.prod.yml logs -f db
```

### Reiniciar Serviços

```bash
docker-compose -f docker-compose.prod.yml restart api
```

### Limpar e Recriar

```bash
docker-compose -f docker-compose.prod.yml down
docker-compose -f docker-compose.prod.yml up -d
```






