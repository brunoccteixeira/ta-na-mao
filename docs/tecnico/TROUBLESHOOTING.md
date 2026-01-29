# Guia de Troubleshooting - Tá na Mão

Este guia ajuda a resolver problemas comuns no projeto Tá na Mão.

## Backend

### Erro: "Connection refused" ao conectar PostgreSQL

**Sintomas:**
```
sqlalchemy.exc.OperationalError: could not connect to server
```

**Soluções:**
1. Verificar se o container está rodando:
   ```bash
   docker-compose ps
   ```

2. Reiniciar containers:
   ```bash
   docker-compose down
   docker-compose up -d
   ```

3. Verificar logs:
   ```bash
   docker-compose logs db
   ```

4. Verificar variável DATABASE_URL no .env

### Erro: "ModuleNotFoundError"

**Sintomas:**
```
ModuleNotFoundError: No module named 'app'
```

**Soluções:**
1. Verificar se o venv está ativado:
   ```bash
   which python  # Deve apontar para venv/bin/python
   ```

2. Reinstalar dependências:
   ```bash
   pip install -r requirements.txt
   ```

3. Verificar PYTHONPATH:
   ```bash
   export PYTHONPATH="${PYTHONPATH}:$(pwd)"
   ```

### Erro: "relation does not exist"

**Sintomas:**
```
sqlalchemy.exc.ProgrammingError: relation "programs" does not exist
```

**Soluções:**
1. Executar migrações:
   ```bash
   alembic upgrade head
   ```

2. Verificar se o banco foi criado:
   ```bash
   docker-compose exec db psql -U tanamao -d tanamao -c "\dt"
   ```

### Erro: "Validation error" no startup

**Sintomas:**
```
ValueError: Configuration errors: DATABASE_URL must be a valid PostgreSQL connection string
```

**Soluções:**
1. Verificar arquivo .env existe
2. Verificar formato da DATABASE_URL:
   ```
   postgresql://user:password@host:port/database
   ```
3. Verificar variáveis obrigatórias para produção

### Performance: Queries lentas

**Sintomas:**
- Endpoints demorando > 1 segundo
- Timeout em agregações

**Soluções:**
1. Verificar índices:
   ```sql
   SELECT * FROM pg_indexes WHERE tablename = 'beneficiary_data';
   ```

2. Analisar query lenta:
   ```sql
   EXPLAIN ANALYZE SELECT ...;
   ```

3. Verificar cache Redis:
   ```bash
   docker-compose exec redis redis-cli KEYS *
   ```

## Frontend

### Erro: "Network Error" ao buscar dados

**Sintomas:**
```
AxiosError: Network Error
```

**Soluções:**
1. Verificar se backend está rodando:
   ```bash
   curl http://localhost:8000/health
   ```

2. Verificar variável VITE_API_URL:
   ```bash
   cat frontend/.env.local
   ```

3. Verificar CORS no backend:
   - Adicionar origem do frontend em CORS_ORIGINS

### Erro: "Cannot find module"

**Sintomas:**
```
Error: Cannot find module '@/components/...'
```

**Soluções:**
1. Verificar tsconfig.json ou vite.config.ts tem alias configurado
2. Reinstalar dependências:
   ```bash
   rm -rf node_modules package-lock.json
   npm install
   ```

### Build falha

**Sintomas:**
```
Error during build: ...
```

**Soluções:**
1. Limpar cache:
   ```bash
   rm -rf node_modules .vite dist
   npm install
   ```

2. Verificar versão do Node:
   ```bash
   node --version  # Deve ser 18+
   ```

## Android

### Erro: "Connection refused" no emulador

**Sintomas:**
- App não consegue conectar ao backend

**Soluções:**
1. Usar `10.0.2.2` em vez de `localhost` no emulador
2. Verificar se backend está escutando em `0.0.0.0`:
   ```bash
   uvicorn app.main:app --host 0.0.0.0 --port 8000
   ```

### Erro: "Could not resolve com.google.android.gms"

**Sintomas:**
```
Could not resolve: com.google.android.gms:play-services-maps
```

**Soluções:**
1. Sincronizar Gradle:
   ```bash
   ./gradlew --refresh-dependencies
   ```

2. Verificar versão do Google Play Services no build.gradle

### Build falha com "OutOfMemoryError"

**Sintomas:**
```
java.lang.OutOfMemoryError: Java heap space
```

**Soluções:**
1. Aumentar memória do Gradle:
   ```properties
   # gradle.properties
   org.gradle.jvmargs=-Xmx4096m -XX:MaxPermSize=512m
   ```

## Docker

### Container não inicia

**Sintomas:**
```
Container exited with code 1
```

**Soluções:**
1. Verificar logs:
   ```bash
   docker-compose logs api
   ```

2. Verificar variáveis de ambiente:
   ```bash
   docker-compose config
   ```

3. Rebuild imagem:
   ```bash
   docker-compose build --no-cache api
   ```

### Volume permissions

**Sintomas:**
```
Permission denied: /var/lib/postgresql/data
```

**Soluções:**
1. Ajustar permissões:
   ```bash
   sudo chown -R 999:999 postgres_data/
   ```

## Agente IA

### Erro: "Invalid API key"

**Sintomas:**
```
google.generativeai.types.BlockedPromptException
```

**Soluções:**
1. Verificar GOOGLE_API_KEY no .env
2. Verificar se a chave está ativa no Google AI Studio
3. Verificar limites de quota

### Agente não responde

**Sintomas:**
- Timeout nas requisições
- Respostas vazias

**Soluções:**
1. Verificar logs:
   ```bash
   docker-compose logs -f api | grep agent
   ```

2. Verificar conectividade com Gemini API
3. Verificar rate limits

## Performance Geral

### API lenta

**Diagnóstico:**
1. Verificar métricas:
   ```bash
   curl http://localhost:8000/metrics
   ```

2. Verificar logs de performance
3. Analisar queries de banco

**Soluções:**
1. Aumentar cache Redis
2. Adicionar índices no banco
3. Otimizar queries
4. Escalar horizontalmente

### Frontend lento

**Diagnóstico:**
1. Verificar bundle size:
   ```bash
   npm run build
   # Verificar tamanho dos arquivos em dist/
   ```

2. Verificar Network tab no DevTools

**Soluções:**
1. Code splitting
2. Lazy loading de componentes
3. Otimizar imagens
4. Usar CDN

## Logs e Debugging

### Ver logs estruturados

```bash
# Backend
docker-compose logs -f api | jq

# Ou sem jq
docker-compose logs -f api
```

### Debug mode

```bash
# Backend
ENVIRONMENT=development DEBUG=true uvicorn app.main:app --reload

# Frontend
VITE_ENVIRONMENT=development npm run dev
```

## Contato e Suporte

Para problemas não resolvidos:
1. Verificar issues no GitHub
2. Consultar documentação técnica
3. Abrir nova issue com:
   - Descrição do problema
   - Passos para reproduzir
   - Logs relevantes
   - Ambiente (OS, versões, etc.)






