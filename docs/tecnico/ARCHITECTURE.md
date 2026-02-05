# Arquitetura do Sistema - Tá na Mão

## Visão Geral

O Tá na Mão é uma plataforma multi-camadas que integra dados de benefícios sociais brasileiros com um agente de IA conversacional.

## Diagrama de Arquitetura

```mermaid
graph TB
    subgraph "Frontend Layer"
        Web[React Dashboard]
        Mobile[Android App]
    end

    subgraph "API Layer"
        API[FastAPI Backend]
        Agent[Gemini Agent]
    end

    subgraph "ETL Layer"
        Scheduler[APScheduler]
        Jobs[Ingestion Jobs]
        Geocoding[Geocoding Service]
    end

    subgraph "Data Layer"
        PG[(PostgreSQL + PostGIS)]
        Redis[(Redis Cache)]
    end

    subgraph "External Services"
        IBGE[IBGE API]
        Gemini[Google Gemini]
        Twilio[Twilio WhatsApp]
        MDS[MDS/Censo SUAS]
        OpenDataSUS[OpenDataSUS]
        Nominatim[Nominatim/OSM]
    end

    Web --> API
    Mobile --> API
    API --> Agent
    API --> PG
    API --> Redis
    Agent --> Gemini
    API --> IBGE
    Agent --> Twilio

    Scheduler --> Jobs
    Jobs --> PG
    Jobs --> Geocoding
    Geocoding --> Nominatim
    Jobs --> MDS
    Jobs --> OpenDataSUS
```

## Componentes Principais

### Backend (FastAPI)

**Responsabilidades:**
- API REST para dados de benefícios
- Agregações e análises
- Integração com agente IA
- Gerenciamento de sessões

**Estrutura:**
```
backend/
├── app/
│   ├── core/          # Logging estruturado, exceptions, utilities
│   ├── models/        # SQLAlchemy models (async)
│   ├── routers/       # API endpoints (100% async)
│   ├── agent/         # IA agent implementation
│   ├── jobs/          # Data ingestion scripts
│   └── middleware/    # Metrics (Prometheus), auth, etc.
├── alembic/           # Database migrations
└── tests/             # Test suite (pytest, async)
```

**Características:**
- **SQLAlchemy Async**: Todas as queries são assíncronas para melhor performance
- **Cache Redis**: Cache distribuído para queries frequentes
- **Logging Estruturado**: Logs JSON com structlog
- **Métricas**: Prometheus metrics middleware

### Frontend (React + TypeScript)

**Responsabilidades:**
- Dashboard interativo
- Visualização de mapas
- Gráficos e estatísticas
- Interface de chat

**Tecnologias:**
- React 18
- TypeScript
- Vite
- TailwindCSS
- Leaflet (mapas)
- Recharts (gráficos)
- React Query (data fetching)

### Android App (Kotlin)

**Responsabilidades:**
- Interface mobile nativa
- Chat com agente IA
- Notificações push
- Cache offline

**Arquitetura:**
- MVVM + Clean Architecture
- Jetpack Compose
- Hilt (DI)
- Room (cache local)

## Fluxo de Dados

### 1. Ingestão de Dados (ETL Pipeline)

```
Fontes Externas → Scheduler → Jobs → Geocoding → PostgreSQL
```

**Arquitetura ETL:**
```
backend/app/jobs/
├── dados_abertos/
│   ├── orquestrador.py    # APScheduler + coordenação
│   ├── extrator.py        # Download de dados
│   ├── transformador.py   # Validação e normalização
│   └── carregador.py      # Upsert no banco
├── ingest_cras.py         # CRAS locations (~8.300)
├── ingest_farmacia_real.py # Farmácias (~31.000)
└── ingest_population.py   # População IBGE
```

**Scheduler (APScheduler):**
| Job | Dia do Mês | Hora | Fonte |
|-----|------------|------|-------|
| Bolsa Família | 5 | 03:00 | Portal Transparência |
| BPC/LOAS | 6 | 03:00 | Portal Transparência |
| Farmácia Popular | 7 | 04:00 | OpenDataSUS |
| TSEE | 8 | 04:00 | ANEEL |
| Auxílio Gás | 9 | 04:00 | Portal Transparência |
| Seguro Defeso | 10 | 04:00 | Portal Transparência |
| CRAS Locations | 11 | 04:00 | Censo SUAS/MDS |

**Geocodificação:**
- Serviço: `app/services/geocoding_service.py`
- Estratégia: Nominatim (gratuito) → Google API (fallback pago)
- Cobertura: ~80% automático, resto manual

**Fontes de Dados:**
- Portal da Transparência (benefícios federais)
- OpenDataSUS (Farmácia Popular)
- Censo SUAS/MDS (CRAS locations)
- ANEEL (Tarifa Social)
- IBGE (população, municípios)

### 2. Consulta de Dados

```
Cliente → API → Cache (Redis) → PostgreSQL → Resposta
```

### 3. Chat com Agente

```
Usuário → API → Gemini Agent → Tools → Resposta
```

**Tools disponíveis:**
- Validação de CPF
- Busca de CEP
- Consulta de benefícios
- Geração de checklist
- Busca de CRAS/Farmácias
- Processamento de receitas

## Banco de Dados

### Modelos Principais

- **State**: Estados brasileiros
- **Municipality**: Municípios (com geometria PostGIS)
- **Program**: Programas sociais
- **BeneficiaryData**: Dados agregados por município/programa/mês
- **CadUnicoData**: Dados demográficos do CadÚnico
- **CrasLocation**: Localizações de CRAS (~8.300 registros)
- **Pedido**: Pedidos de medicamentos
- **Beneficiario**: Beneficiários (com hash de CPF)
- **Benefit**: Catálogo de benefícios (229 benefícios)
- **Partner**: Parceiros e conversões
- **Advisor/Case**: Sistema Anjo Social

### Índices

- `municipalities.ibge_code` (único)
- `beneficiary_data(municipality_id, program_id, reference_date)`
- `municipalities.geometry` (GIST para PostGIS)
- `cras_locations.ibge_code` (busca por município)
- `cras_locations(latitude, longitude)` (busca por coordenadas)

## Cache Strategy

**Redis é usado para:**
- GeoJSON de estados/municípios (TTL: 24h)
- Agregações nacionais (TTL: 1h)
- Buscas de municípios (TTL: 30min)
- Sessões do agente IA

## Segurança

### Autenticação
- JWT para endpoints admin (planejado)
- Rate limiting em endpoints públicos

### Privacidade
- CPFs são hasheados (SHA-256)
- Dados pessoais não são armazenados em texto plano
- LGPD compliant

## Monitoramento

### Métricas (Prometheus)
- Requisições HTTP (total, duração)
- Queries de banco de dados
- Requisições ativas
- Health checks

### Logging
- Estruturado (JSON em produção)
- Contexto de requisição (request ID)
- Níveis: DEBUG, INFO, WARNING, ERROR

### Health Checks
- `/health`: Status geral
- `/metrics`: Métricas Prometheus

## Escalabilidade

### Horizontal Scaling
- API stateless (pode rodar múltiplas instâncias)
- Redis compartilhado
- PostgreSQL com replicação (planejado)

### Otimizações
- Cache agressivo
- Índices de banco de dados
- Queries otimizadas
- Connection pooling

## Deploy

### Desenvolvimento
- Docker Compose local
- Hot reload habilitado
- Logs em console

### Produção
- Docker Compose ou Kubernetes
- Multi-stage builds
- Health checks
- Logs centralizados
- Métricas Prometheus

## Roadmap Técnico

### Fase 1 (Completa)
- ✅ Estrutura básica
- ✅ Ingestão de dados
- ✅ API REST
- ✅ Dashboard web
- ✅ App Android MVP
- ✅ Async SQLAlchemy (100% routers migrados)
- ✅ Testes em todas as plataformas
- ✅ CI/CD completo (GitHub Actions)
- ✅ Logging estruturado e métricas
- ✅ ETL Scheduler (APScheduler)
- ✅ CRAS Database (~8.300 localizações)
- ✅ Geocodificação automática (Nominatim + Google)
- ✅ APIs Gov.br (SERPRO, Transparência)

### Fase 2 (Próxima)
- [ ] Autenticação JWT para endpoints admin
- [ ] Rate limiting
- [ ] Aumentar cobertura de testes (>70%)
- [ ] OpenTelemetry tracing
- [ ] Ingestão completa Censo SUAS

### Fase 3 (Futura)
- [ ] Kubernetes deployment
- [ ] Replicação de banco
- [ ] CDN para assets
- [ ] WebSockets para chat em tempo real
- [ ] PWA para frontend


