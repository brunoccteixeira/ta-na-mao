# Getting Started - Tá na Mão

Guia completo para configurar o ambiente de desenvolvimento do projeto Tá na Mão.

## Pré-requisitos

### Obrigatórios

| Ferramenta | Versão | Download |
|------------|--------|----------|
| **Docker Desktop** | 4.0+ | [docker.com](https://www.docker.com/products/docker-desktop) |
| **Python** | 3.11+ | [python.org](https://www.python.org/downloads/) |
| **Node.js** | 18+ | [nodejs.org](https://nodejs.org/) |
| **Git** | 2.0+ | [git-scm.com](https://git-scm.com/) |

### Opcionais (para desenvolvimento mobile)

| Ferramenta | Versão | Download |
|------------|--------|----------|
| **Android Studio** | Hedgehog+ | [developer.android.com](https://developer.android.com/studio) |
| **JDK** | 17 | Incluído no Android Studio |

---

## 1. Clone do Repositório

```bash
git clone https://github.com/seu-org/ta-na-mao.git
cd ta-na-mao
```

---

## 2. Backend (FastAPI + PostgreSQL)

### 2.1 Iniciar Containers

```bash
cd backend

# Iniciar PostgreSQL + PostGIS + Redis
docker-compose up -d

# Verificar se estão rodando
docker-compose ps
```

**Containers criados:**
| Container | Porta | Descrição |
|-----------|-------|-----------|
| `tanamao-postgres` | 5432 | PostgreSQL 15 + PostGIS |
| `tanamao-redis` | 6379 | Redis (cache) |

### 2.2 Ambiente Virtual Python

```bash
# Criar ambiente virtual
python -m venv venv

# Ativar (Linux/Mac)
source venv/bin/activate

# Ativar (Windows)
venv\Scripts\activate

# Instalar dependências
pip install -r requirements.txt
```

### 2.3 Variáveis de Ambiente

Crie o arquivo `.env` na pasta `backend/`:

```bash
# backend/.env
DATABASE_URL=postgresql://tanamao:tanamao@localhost:5432/tanamao
REDIS_URL=redis://localhost:6379
SECRET_KEY=dev-secret-key-change-in-production
DEBUG=true
```

### 2.4 Migrações do Banco

```bash
# Aplicar migrações
alembic upgrade head
```

### 2.5 Carga de Dados Inicial

Execute os scripts na ordem correta:

```bash
# 1. Estados e municípios (IBGE)
python -m app.jobs.ingest_ibge

# 2. População
python -m app.jobs.ingest_population

# 3. Geometrias dos municípios (PostGIS)
python -m app.jobs.ingest_mun_geometries

# 4. Dados TSEE
python -m app.jobs.ingest_tsee

# 5. Dados Farmácia Popular
python -m app.jobs.ingest_farmacia_real

# 6. Dados Dignidade Menstrual
python -m app.jobs.ingest_dignidade

# 7. Dados BPC
python -m app.jobs.ingest_bpc_real

# 8. Atualizar taxas de cobertura
python -m app.jobs.update_coverage
```

**Tempo estimado:** ~15-20 minutos (dependendo da conexão)

### 2.6 Iniciar API

```bash
uvicorn app.main:app --reload --host 0.0.0.0 --port 8000
```

**Endpoints disponíveis:**
| URL | Descrição |
|-----|-----------|
| http://localhost:8000 | API base |
| http://localhost:8000/docs | Swagger UI |
| http://localhost:8000/redoc | ReDoc |
| http://localhost:8000/health | Health check |

### 2.7 Verificar Instalação

```bash
# Testar endpoint
curl http://localhost:8000/api/v1/programs/

# Esperado: lista de programas sociais
```

---

## 3. Frontend (React + Vite)

### 3.1 Instalar Dependências

```bash
cd frontend

npm install
```

### 3.2 Variáveis de Ambiente

Crie o arquivo `.env.local` na pasta `frontend/`:

```bash
# frontend/.env.local
VITE_API_URL=http://localhost:8000/api/v1
```

### 3.3 Iniciar Dev Server

```bash
npm run dev
```

**Dashboard disponível em:** http://localhost:5173

### 3.4 Build de Produção

```bash
# Compilar para produção
npm run build

# Preview local da build
npm run preview
```

---

## 4. Android (Kotlin + Jetpack Compose)

### 4.1 Abrir no Android Studio

1. Abra o Android Studio
2. File → Open → Selecione a pasta `android/`
3. Aguarde o Gradle sync completar

### 4.2 Configurar API Key (Google Maps)

> ⚠️ **Nota:** O mapa está em desenvolvimento. Enquanto isso, a tela de mapa mostra um placeholder.

Para habilitar o mapa real:

1. Obtenha uma API Key no [Google Cloud Console](https://console.cloud.google.com/)
2. Habilite "Maps SDK for Android"
3. Adicione ao `local.properties`:

```properties
# android/local.properties
MAPS_API_KEY=sua_chave_aqui
```

### 4.3 Configurar URL da API

Edite `app/src/main/java/com/tanamao/app/data/api/TaNaMaoApi.kt`:

```kotlin
// Para emulador (padrão)
private const val BASE_URL = "http://10.0.2.2:8000/api/v1/"

// Para dispositivo físico na mesma rede
// private const val BASE_URL = "http://SEU_IP_LOCAL:8000/api/v1/"
```

### 4.4 Executar

1. Conecte um dispositivo ou inicie um emulador
2. Clique em **Run** (▶️) no Android Studio
3. Aguarde a instalação

**Telas implementadas:**
- Home (Dashboard)
- Pesquisa (Estados/Municípios)
- Detalhe do Município

---

## 5. Verificação Completa

### Checklist de Funcionamento

| Componente | URL | Status Esperado |
|------------|-----|-----------------|
| Backend API | http://localhost:8000/health | `{"status": "healthy"}` |
| Swagger Docs | http://localhost:8000/docs | Página de documentação |
| Frontend | http://localhost:5173 | Dashboard com mapa |
| Android | N/A | App rodando no emulador |

### Teste de Integração

```bash
# Backend: listar programas
curl http://localhost:8000/api/v1/programs/

# Backend: dados nacionais
curl http://localhost:8000/api/v1/aggregations/national

# Backend: estados
curl http://localhost:8000/api/v1/aggregations/states
```

---

## 6. Troubleshooting

### Backend

**Erro: "Connection refused" ao conectar PostgreSQL**
```bash
# Verificar se container está rodando
docker-compose ps

# Reiniciar containers
docker-compose down
docker-compose up -d
```

**Erro: "ModuleNotFoundError"**
```bash
# Verificar se venv está ativado
which python  # Deve apontar para venv/bin/python

# Reinstalar dependências
pip install -r requirements.txt
```

**Erro: "relation does not exist"**
```bash
# Rodar migrações novamente
alembic upgrade head
```

### Frontend

**Erro: "ENOENT: no such file or directory"**
```bash
# Limpar cache e reinstalar
rm -rf node_modules package-lock.json
npm install
```

**Erro: "Network Error" ao buscar dados**
```bash
# Verificar se backend está rodando
curl http://localhost:8000/health

# Verificar variável de ambiente
cat .env.local
```

### Android

**Erro: "Could not resolve com.google.android.gms:play-services-maps"**
```bash
# Sincronizar Gradle
./gradlew --refresh-dependencies
```

**Erro: "Connection refused" no emulador**
```
# Use 10.0.2.2 em vez de localhost para o emulador
# Verifique se o backend está escutando em 0.0.0.0
uvicorn app.main:app --host 0.0.0.0 --port 8000
```

---

## 7. Próximos Passos

Após configurar o ambiente:

1. **Explore a API**: http://localhost:8000/docs
2. **Leia a documentação técnica**:
   - [Backend Docs](./backend/docs/README.md)
   - [Frontend Docs](./frontend/docs/README.md)
   - [Android Docs](./android/docs/README.md)
3. **Contribua**: Veja [CONTRIBUTING.md](./CONTRIBUTING.md)

---

## 8. Comandos Úteis

### Backend

```bash
# Iniciar API
uvicorn app.main:app --reload

# Rodar migrações
alembic upgrade head

# Criar nova migração
alembic revision --autogenerate -m "descrição"

# Logs do PostgreSQL
docker-compose logs -f postgres
```

### Frontend

```bash
# Dev server
npm run dev

# Build produção
npm run build

# Lint
npm run lint

# Preview build
npm run preview
```

### Docker

```bash
# Subir containers
docker-compose up -d

# Parar containers
docker-compose down

# Limpar tudo (CUIDADO: apaga dados)
docker-compose down -v

# Ver logs
docker-compose logs -f
```

---

**Dúvidas?** Abra uma issue no repositório ou consulte a documentação técnica.
