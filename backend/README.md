# Tá na Mão - Backend API

Sistema de monitoramento de benefícios sociais brasileiros com granularidade municipal.

## Visão Geral

O **Tá na Mão** é uma plataforma que consolida dados de programas sociais do governo brasileiro, permitindo visualizar a cobertura e alcance desses programas nos 5.570 municípios do país.

### Programas Rastreados

| Programa | Fonte | Dados Disponíveis |
|----------|-------|-------------------|
| **Bolsa Família** | Portal da Transparência | ~21M famílias/mês |
| **CadÚnico** | Múltiplas fontes | ~85M pessoas cadastradas |
| **BPC/LOAS** | Portal da Transparência | ~6.2M beneficiários |
| **Farmácia Popular** | OpenDataSUS | 2016-2025 (10 anos) - 12.4M/mês |
| **TSEE** | ANEEL | ~14.3M beneficiários |
| **Dignidade Menstrual** | OpenDataSUS | ~358k beneficiários |
| **PIS/PASEP** | Caixa/BB | R$ 26.3bi não resgatados |

### Canais de Distribuição (Roadmap)

| Canal | Status | Descrição |
|-------|--------|-----------|
| **App Tá na Mão** | MVP | App Android nativo |
| **WhatsApp Bot** | Em Desenvolvimento | Assistente via WhatsApp (Twilio) |
| **API para Caixa Tem** | Fase 2 | Integração com apps Caixa |
| **API para App FGTS** | Fase 3 | Notificações de direitos |

## Requisitos

- Python 3.11+
- PostgreSQL 15+ com PostGIS
- Docker e Docker Compose (recomendado)

## Instalação

### 1. Clonar e configurar ambiente

```bash
cd backend
python -m venv venv
source venv/bin/activate  # Linux/Mac
pip install -r requirements.txt
```

### 2. Configurar variáveis de ambiente

```bash
cp .env.example .env
# Editar .env com suas configurações
```

### 3. Iniciar banco de dados

```bash
docker-compose up -d
```

### 4. Executar migrações

```bash
alembic upgrade head
```

### 5. Carregar dados geográficos

```bash
python -m app.jobs.ingest_ibge
python -m app.jobs.ingest_population
```

### 6. Ingerir dados de programas

```bash
# BPC/LOAS (Portal da Transparência)
python -m app.jobs.ingest_bpc_real 2024 10

# Farmácia Popular (OpenDataSUS - inclui histórico)
python -m app.jobs.ingest_farmacia_real

# TSEE (ANEEL)
python -m app.jobs.ingest_tsee

# Dignidade Menstrual (OpenDataSUS)
python -m app.jobs.ingest_dignidade

# Dados históricos (10 anos Farmácia Popular)
python -m app.jobs.ingest_historical
```

### 7. Iniciar API

```bash
uvicorn app.main:app --reload --host 0.0.0.0 --port 8000
```

**Nota:** O backend usa **SQLAlchemy async** para melhor performance e concorrência. Todas as queries são assíncronas. Veja [docs/ASYNC_MIGRATION.md](docs/ASYNC_MIGRATION.md) para detalhes técnicos.

## Modelos de Dados

### Entidades Principais

| Modelo | Tabela | Descrição |
|--------|--------|-----------|
| `State` | states | 27 estados brasileiros |
| `Municipality` | municipalities | 5.570 municípios com geometria |
| `Program` | programs | Programas sociais rastreados |
| `BeneficiaryData` | beneficiary_data | Dados por município/programa/mês |
| `CadUnicoData` | cadunico_data | Dados demográficos do CadÚnico |

### Relacionamentos

```
State (1) ─────────────── (N) Municipality
                              │
                              │
Municipality (1) ────────── (N) BeneficiaryData
                              │
                              └── program_code (FK)
                              └── reference_date
                              └── total_beneficiaries
                              └── total_value_brl

Municipality (1) ────────── (N) CadUnicoData
                              └── families_extreme_poverty
                              └── families_poverty
                              └── families_low_income
```

### Campos Geoespaciais (PostGIS)

- `Municipality.geometry`: MultiPolygon para renderização de mapas
- `Municipality.geometry_simplified`: Versão simplificada para performance

## Agente Conversacional (V2)

O Tá na Mão utiliza uma **arquitetura multi-agente** com orquestrador e sub-agentes especializados:

```
┌─────────────────────────────────────────────────────────────┐
│                    ORQUESTRADOR PRINCIPAL                    │
│         (Classifica intenção, roteia para sub-agente)       │
└─────────────────────────────────────────────────────────────┘
                              │
        ┌─────────────────────┼─────────────────────┐
        ▼                     ▼                     ▼
┌───────────────┐    ┌───────────────┐    ┌───────────────────┐
│  SUB-AGENT    │    │  SUB-AGENT    │    │    SUB-AGENT      │
│  Benefícios   │    │   Farmácia    │    │  Documentação     │
└───────────────┘    └───────────────┘    └───────────────────┘
```

### Funcionalidades

- Gera checklist de documentos automaticamente
- Busca CRAS ou farmácias próximas (Google Places API)
- Processa receitas médicas (foto ou texto)
- Envia pedidos de medicamentos para farmácias via WhatsApp
- **Respostas estruturadas (A2UI)** com cards e botões renderizáveis

### Fluxo de Pedido de Medicamentos (estilo iFood)

```
Cidadão pede → Agente processa receita → Busca farmácia
     ↓
Cidadão escolhe → Agente envia WhatsApp → Farmácia prepara
     ↓
Farmácia confirma → Cidadão recebe "PRONTO!" → Retira
```

Veja [docs/AGENT.md](docs/AGENT.md) para documentação completa.

## Estrutura do Projeto

```
backend/
├── app/
│   ├── agent/              # Agente conversacional V2
│   │   ├── agent.py        # Classe TaNaMaoAgent (Gemini)
│   │   ├── orchestrator.py # Orquestrador principal (roteia para sub-agentes)
│   │   ├── context.py      # ConversationContext e CitizenProfile
│   │   ├── response_types.py  # AgentResponse, UIComponent, Action (A2UI)
│   │   ├── intent_classifier.py  # Classificador de intenção
│   │   ├── whatsapp_formatter.py # Converte A2UI para TwiML
│   │   ├── session_redis.py      # Sessões persistentes (Redis)
│   │   ├── prompts.py      # System prompts
│   │   ├── mcp/            # MCP Wrappers (Model Context Protocol)
│   │   │   ├── __init__.py      # Exports: init_mcp, mcp_manager
│   │   │   ├── base.py          # MCPClient, MCPManager
│   │   │   ├── brasil_api.py    # BrasilAPIMCP (CEP, CNPJ)
│   │   │   ├── google_maps.py   # GoogleMapsMCP (Places)
│   │   │   └── pdf_ocr.py       # PDFOcrMCP (OCR receitas)
│   │   ├── subagents/      # Sub-agentes especializados
│   │   │   ├── __init__.py
│   │   │   ├── farmacia_agent.py    # Fluxo de pedido de medicamentos
│   │   │   ├── beneficio_agent.py   # Consulta de benefícios
│   │   │   └── documentacao_agent.py # Checklist e busca CRAS
│   │   └── tools/          # 15+ tools disponíveis
│   │       ├── validar_cpf.py
│   │       ├── buscar_cep.py          # MCP + Fallback ViaCEP
│   │       ├── checklist.py
│   │       ├── buscar_cras.py
│   │       ├── buscar_farmacia.py     # MCP + Fallback Google Places
│   │       ├── processar_receita.py   # MCP + Fallback Gemini Vision
│   │       ├── enviar_whatsapp.py     # Twilio
│   │       └── preparar_pedido.py
│   ├── jobs/               # Scripts de ingestão de dados
│   │   ├── ingest_bolsa_familia.py
│   │   ├── ingest_bpc_real.py
│   │   ├── ingest_farmacia_real.py
│   │   ├── ingest_dignidade.py
│   │   ├── ingest_tsee.py
│   │   └── ingest_historical.py
│   ├── models/             # Modelos SQLAlchemy
│   │   ├── state.py
│   │   ├── municipality.py
│   │   ├── program.py
│   │   ├── beneficiary_data.py
│   │   └── pedido.py       # Pedidos de medicamentos
│   ├── routers/            # Endpoints da API
│   │   ├── programs.py
│   │   ├── aggregations.py
│   │   ├── municipalities.py
│   │   ├── geo.py
│   │   ├── agent.py        # POST /agent/v2/chat, /agent/v2/start
│   │   └── webhook.py      # Webhook Twilio WhatsApp + /whatsapp/chat
│   ├── schemas/
│   │   └── agent.py        # ChatResponseV2, UIComponent, Action
│   ├── database.py
│   ├── config.py
│   └── main.py
├── tests/                  # Testes automatizados
│   ├── __init__.py
│   ├── conftest.py         # Fixtures compartilhadas
│   ├── test_orchestrator.py # Testes do orquestrador
│   └── test_subagents.py   # Testes dos sub-agentes
├── data/
│   ├── medicamentos_farmacia_popular.json
│   ├── documentos_por_beneficio.json
│   ├── cras_exemplo.json
│   └── farmacias_exemplo.json
├── docs/
│   ├── API.md              # Referência da API REST (inclui V2)
│   ├── AGENT.md            # Documentação do Agente V2
│   ├── DATA_SOURCES.md     # Fontes de dados oficiais
│   └── INGESTION.md        # Guia de ingestão
├── alembic/
├── docker-compose.yml
├── requirements.txt
└── README.md
```

## API

A API está disponível em `http://localhost:8000` com documentação interativa em `/docs`.

### Endpoints Principais

| Endpoint | Descrição |
|----------|-----------|
| `GET /api/v1/programs/` | Lista todos os programas |
| `GET /api/v1/aggregations/time-series` | Série histórica |
| `GET /api/v1/aggregations/states` | Dados por estado |
| `GET /api/v1/aggregations/regions` | Dados por região |
| `GET /api/v1/programs/{code}/ranking` | Ranking de municípios |
| **`POST /api/v1/agent/v2/start`** | Iniciar sessão de chat |
| **`POST /api/v1/agent/v2/chat`** | Enviar mensagem ao agente |
| **`POST /api/v1/webhook/whatsapp/chat`** | Chat via WhatsApp (Twilio) |

### Exemplos

```bash
# Série histórica da Farmácia Popular
curl "http://localhost:8000/api/v1/aggregations/time-series?program=FARMACIA_POPULAR"

# Dados por estado
curl "http://localhost:8000/api/v1/aggregations/states?program=BPC"

# Ranking de municípios
curl "http://localhost:8000/api/v1/programs/FARMACIA_POPULAR/ranking?limit=10"

# Chat com o agente (V2)
curl -X POST "http://localhost:8000/api/v1/agent/v2/chat" \
  -H "Content-Type: application/json" \
  -d '{"message": "quero ver meus benefícios", "session_id": "test-123"}'
```

## Testes

O backend possui uma suíte completa de testes usando pytest com suporte assíncrono.

### Executar Testes

```bash
# Rodar todos os testes
pytest tests/ -v

# Testes específicos
pytest tests/test_programs.py -v
pytest tests/test_aggregations.py -v
pytest tests/test_agent.py -v

# Com cobertura
pytest tests/ --cov=app --cov-report=html

# Usando Makefile
make test
```

### Estrutura de Testes

| Arquivo | Descrição |
|---------|-----------|
| `tests/conftest.py` | Fixtures compartilhadas (client async, DB async) |
| `tests/test_programs.py` | Testes dos endpoints `/api/v1/programs/*` |
| `tests/test_aggregations.py` | Testes dos endpoints `/api/v1/aggregations/*` |
| `tests/test_agent.py` | Testes do agente IA |

### Características dos Testes

- **Async/await**: Todos os testes usam `pytest-asyncio` e `httpx.AsyncClient`
- **DB isolado**: SQLite em memória para testes rápidos
- **Mocks**: APIs externas (Google, Twilio) são mockadas
- **Fixtures**: Database e client HTTP reutilizáveis

### Cobertura

Atualmente com testes para:
- ✅ Endpoints de programas
- ✅ Endpoints de agregações
- ✅ Agente IA (estrutura criada)
- ✅ Health checks

## Performance e Observabilidade

### Performance

- **SQLAlchemy Async**: 100% dos routers convertidos para async
  - Melhor concorrência (2-3x mais requisições simultâneas)
  - Não bloqueia event loop
  - Veja [docs/ASYNC_MIGRATION.md](docs/ASYNC_MIGRATION.md) para detalhes

- **Cache Redis**: Redução de carga no banco para queries frequentes

- **Índices**: Índices otimizados em colunas frequentemente consultadas

### Observabilidade

- **Logging Estruturado**: Usa `structlog` para logs JSON facilmente analisáveis
- **Métricas Prometheus**: Endpoint `/metrics` para monitoramento
- **Health Checks**: Endpoint `/health` com status de DB, Redis e aplicação

```bash
# Health check
curl http://localhost:8000/health

# Métricas Prometheus
curl http://localhost:8000/metrics
```

## CI/CD

O projeto possui GitHub Actions configurados para:

- **Lint**: ruff, mypy, black (backend) | eslint (frontend) | ktlint (Android)
- **Testes**: pytest (backend) | vitest (frontend) | JUnit (Android)
- **Build**: Verificação de builds em todas as plataformas

Veja `.github/workflows/` para detalhes.

## Developer Experience

### Makefile

Comandos úteis disponíveis:

```bash
make test      # Rodar testes
make lint      # Verificar linting
make format    # Formatar código (black, ruff)
make run       # Rodar servidor local
```

### Pre-commit Hooks

Hooks configurados para validação automática antes de commits:

- black (formatação Python)
- ruff (linting Python)
- mypy (type checking Python)
- eslint (linting JavaScript/TypeScript)
- ktlint (linting Kotlin)

Instalar: `pre-commit install`

## Integração MCP (Model Context Protocol)

O Tá na Mão utiliza MCPs para integração padronizada com serviços externos:

| MCP Server | Uso | Tool Integrada |
|------------|-----|----------------|
| **Brasil API** | CEP, CNPJ, DDD | `buscar_cep.py` |
| **Google Maps** | Places, Geocoding | `buscar_farmacia.py` |
| **PDF/OCR** | OCR de receitas | `processar_receita.py` |

### Características

- **Fallback Automático**: Se MCP falhar, usa API direta (HTTP)
- **Configurável**: MCPs podem ser desabilitados via `MCP_ENABLED=false`
- **Inicialização no Startup**: MCPs são carregados automaticamente em `main.py`

### Configuração

```bash
# .env
MCP_ENABLED=true
MCP_CONFIG_PATH=.mcp.json
MCP_TIMEOUT=30000
```

Veja [MCP_SETUP.md](../docs/MCP_SETUP.md) para documentação completa.

## Documentação Adicional

- [Documentação da API](docs/API.md) - Referência completa dos endpoints REST
- [Agente Conversacional](docs/AGENT.md) - Agente de IA, tools e fluxo de pedidos
- [Configuração MCP](../docs/MCP_SETUP.md) - Model Context Protocol setup e integração
- [Fontes de Dados](docs/DATA_SOURCES.md) - Detalhes sobre as fontes oficiais
- [Guia de Ingestão](docs/INGESTION.md) - Como executar os scripts de dados
- [Migração Async](docs/ASYNC_MIGRATION.md) - Detalhes técnicos da migração para async

## Licença

MIT License
