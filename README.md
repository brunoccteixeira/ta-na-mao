# Tá na Mão

Plataforma de acesso a benefícios sociais brasileiros com app mobile, dashboard analítico e agente IA.

> **Novo aqui?** Leia primeiro o [MANIFESTO.md](MANIFESTO.md) para entender a visão estratégica do projeto.

## Visão Geral

O **Tá na Mão** conecta cidadãos brasileiros aos benefícios sociais a que têm direito. Este documento foca nos aspectos técnicos — para a visão estratégica completa, consulte o [MANIFESTO.md](MANIFESTO.md).

### Componentes

| Componente | Descrição | Stack |
|------------|-----------|-------|
| **Android App** | App de acesso a benefícios com chat IA | Kotlin, Jetpack Compose, Hilt |
| **Backend API** | API REST + Agente IA com 13 ferramentas | Python, FastAPI, Gemini 2.0 |
| **Website MVP** | Catálogo de benefícios + Wizard de elegibilidade | React, TypeScript, Tailwind |
| **Dashboard** | Visualização de cobertura por município | React, Leaflet, TypeScript |

## Catálogo de Benefícios

| Escopo | Quantidade | Descrição |
|--------|------------|-----------|
| Federal | 16 | Bolsa Família, BPC, TSEE, Farmácia Popular, etc. |
| Estadual | 106 | Todos os 27 estados brasileiros |
| Municipal | 97 | 40 maiores municípios |
| Setorial | 10 | Pescadores, agricultores, entregadores, etc. |
| **Total** | **229** | Benefícios mapeados |

**Cobertura geográfica:**
- 5.570 municípios com geometrias geoespaciais
- 27 estados com programas estaduais
- 40 municípios com programas locais (capitais + grandes cidades)

## Quick Start

### 1. Backend

```bash
cd backend
docker-compose up -d          # PostgreSQL + PostGIS + Redis
python -m venv venv && source venv/bin/activate
pip install -r requirements.txt
alembic upgrade head
uvicorn app.main:app --reload  # http://localhost:8000
```

**Nota:** O backend usa **SQLAlchemy async** para melhor performance. Veja [backend/docs/ASYNC_MIGRATION.md](backend/docs/ASYNC_MIGRATION.md) para detalhes.

### 2. Android

**Pré-requisito**: Java 17 (veja [android/SETUP_JAVA.md](android/SETUP_JAVA.md))

```bash
cd android
export JAVA_HOME=/usr/local/opt/openjdk@17  # macOS com Homebrew
./gradlew assembleDebug
# APK em: app/build/outputs/apk/debug/app-debug.apk
```

**Testar o app**: Veja [android/COMO_TESTAR.md](android/COMO_TESTAR.md) para opções simples de teste.

### 3. Website MVP (Catálogo + Elegibilidade)

```bash
cd frontend
npm install && npm run dev    # http://localhost:3000
```

**Rotas principais:**
- `/` - Landing page
- `/descobrir` - Wizard de elegibilidade
- `/beneficios` - Catálogo navegável (229 benefícios)
- `/beneficios/:id` - Detalhe do benefício

## Qualidade e Testes

O projeto possui testes automatizados em todas as plataformas:

- **Backend**: pytest com cobertura completa (programs, aggregations, agent)
- **Frontend**: Vitest + React Testing Library
- **Android**: JUnit + MockK + Turbine para ViewModels

Execute os testes:
```bash
# Backend
cd backend && pytest

# Frontend
cd frontend && npm test

# Android
cd android && ./gradlew test
```

**CI/CD**: GitHub Actions configurados para lint, test e build em todas as plataformas.

## Arquitetura

```
┌─────────────────┐     ┌─────────────────────────┐
│   Android App   │────▶│      FastAPI Backend    │
│  Kotlin/Compose │     │  + Gemini 2.0 Agent     │
└─────────────────┘     │  + PostgreSQL/PostGIS   │
                        └───────────┬─────────────┘
                                    │
┌─────────────────┐                 │
│  React Dashboard│─────────────────┘
│  Leaflet Maps   │
└─────────────────┘
```

## Funcionalidades

### Website MVP (Novo!)
- **Catálogo de 229 benefícios**: federais, estaduais, municipais e setoriais
- **Filtros por escopo**: Federal, Estadual, Municipal, Setorial
- **Filtro por estado**: Todos os 27 estados brasileiros
- **Busca por texto**: Nome do benefício, descrição ou categoria
- **Motor de elegibilidade**: Avaliação automática baseada no perfil
- **PWA**: Instalável como app no celular

### Wizard de Triagem de Elegibilidade
- **Formulário visual de 5 etapas**: localização, dados básicos, família, renda, profissão
- **Carteira de Direitos**: resultado visual agrupado por categoria
  - 🇧🇷 Benefícios Federais
  - 🏛️ Benefícios Estaduais
  - 🏘️ Benefícios Municipais
  - 👷 Benefícios Setoriais
- **Carta de Encaminhamento**: PDF pré-preenchido com QR Code para validação no CRAS
- Botão FAB 🎯 "Descobrir Direitos" integrado ao app
- Reduz tempo de atendimento CRAS de 2h para 30min

### Chat com Agente IA
- Verificação de elegibilidade para benefícios
- Geração de checklist de documentos
- Busca de CRAS e farmácias próximas
- Consulta de dinheiro esquecido (PIS/PASEP, SVR, FGTS)
- Visão consolidada de dados do usuário (meus dados)

### Perfil do Usuário
- Estatísticas de benefícios e consultas
- **Dinheiro Esquecido**: Verificação automática de PIS/PASEP, SVR e FGTS
  - Visualização de valores disponíveis
  - Breakdown por tipo de dinheiro
  - Navegação para detalhes e resgate
- Histórico de consultas realizadas
- Benefícios ativos resumidos

### Privacidade e LGPD
- **Exportação de Dados**: Exportação completa de dados pessoais
  - Relatório formatado com todas as informações
  - Compartilhamento via apps instalados
  - Conformidade com LGPD
- Configurações granulares de privacidade
- Exclusão de dados pessoais

### Mapa Inline
- Quando o usuário busca um local (CRAS/farmácia), o chat exibe:
  - Mapa do Google Maps com pin
  - Endereço e telefone
  - Botões para abrir no Maps/Waze ou ligar

### Upload de Receita Médica
- Captura via câmera ou galeria
- Processamento por Gemini Vision
- Identificação de medicamentos elegíveis

## Estrutura do Projeto

```
Ta na Mao/
├── android/              # App Android (Kotlin/Compose)
│   ├── app/src/main/java/br/gov/tanamao/
│   │   ├── data/         # API, DTOs, Repositories
│   │   ├── domain/       # Models, Interfaces
│   │   ├── di/           # Hilt modules
│   │   └── presentation/ # UI, ViewModels, Components
│   └── docs/             # Documentação Android
│
├── backend/              # API Python/FastAPI
│   ├── app/
│   │   ├── routers/      # Endpoints REST
│   │   ├── models/       # SQLAlchemy models
│   │   ├── services/     # Agent, tools
│   │   └── jobs/         # Scripts de ingestão
│   └── docs/             # Documentação Backend
│
├── frontend/             # Website MVP + Dashboard
│   └── src/
│       ├── components/   # EligibilityWizard, Catalog, Map
│       ├── pages/        # Home, Eligibility, Catalog, BenefitDetail
│       ├── engine/       # Motor de elegibilidade
│       ├── data/benefits/# Catálogo JSON
│       │   ├── federal.json
│       │   ├── sectoral.json
│       │   ├── states/   # 27 arquivos (um por UF)
│       │   └── municipalities/ # 40 arquivos (código IBGE)
│       └── api/          # API client
│
├── docs/                 # Documentação geral
│   ├── estrategia/       # Docs estratégicos (conceito, visão)
│   ├── tecnico/          # Docs técnicos (arquitetura, deploy)
│   ├── apresentacoes/    # PPTs e PDFs de pitch
│   ├── specs/            # Especificações técnicas
│   └── data/             # Planilhas de referência
│
└── releases/             # APKs e builds
```

## Documentação

### Documentação Geral
| Documento | Descrição |
|-----------|-----------|
| [GETTING_STARTED.md](GETTING_STARTED.md) | Guia de instalação completo |
| [CONTRIBUTING.md](CONTRIBUTING.md) | Guia de contribuição |
| [CHANGELOG.md](CHANGELOG.md) | Histórico de mudanças e melhorias |
| [docs/tecnico/ARCHITECTURE.md](docs/tecnico/ARCHITECTURE.md) | Arquitetura do sistema |
| [docs/tecnico/DEPLOYMENT.md](docs/tecnico/DEPLOYMENT.md) | Guia de deployment |
| [docs/tecnico/TROUBLESHOOTING.md](docs/tecnico/TROUBLESHOOTING.md) | Troubleshooting comum |

### Backend
| Documento | Descrição |
|-----------|-----------|
| [backend/README.md](backend/README.md) | Visão geral do backend |
| [backend/docs/API.md](backend/docs/API.md) | Documentação da API REST |
| [backend/docs/AGENT.md](backend/docs/AGENT.md) | Documentação do Agente IA |
| [backend/docs/ASYNC_MIGRATION.md](backend/docs/ASYNC_MIGRATION.md) | Migração para async SQLAlchemy |

### Android
| Documento | Descrição |
|-----------|-----------|
| [android/README.md](android/README.md) | Visão geral do app Android |
| [android/docs/README.md](android/docs/README.md) | Documentação detalhada |

## API Endpoints Principais

### Agente IA
- `POST /api/v1/agent/start` - Iniciar sessão
- `POST /api/v1/agent/chat` - Enviar mensagem
- `GET /api/v1/agent/status` - Status do agente

### Dados
- `GET /api/v1/municipalities/search?q=` - Buscar município
- `GET /api/v1/geo/states` - GeoJSON dos estados
- `GET /api/v1/aggregations/national` - Totais nacionais

## Configuração

### Android (`local.properties`)
```properties
MAPS_API_KEY=sua_chave_google_maps
```

### Backend (`.env`)
Copie `.env.example` para `.env` e configure:

```env
DATABASE_URL=postgresql://postgres:postgres@localhost:5432/tanamao
GOOGLE_API_KEY=sua_chave_gemini
REDIS_URL=redis://localhost:6379/0
ENVIRONMENT=development
```

Veja `backend/.env.example` para todas as variáveis disponíveis.

## Melhorias e Performance

### Backend Async
- ✅ **100% async SQLAlchemy** - Melhor concorrência e performance
- ✅ **Cache Redis** - Redução de carga no banco
- ✅ **Índices otimizados** - Queries mais rápidas

### Observabilidade
- ✅ **Logging estruturado** (structlog) - Logs mais fáceis de analisar
- ✅ **Métricas Prometheus** - Monitoramento de performance
- ✅ **Health checks** - Status detalhado (DB, Redis, app)

### Qualidade de Código
- ✅ **Testes automatizados** - Backend, Frontend e Android
- ✅ **CI/CD** - GitHub Actions para todas as plataformas
- ✅ **Pre-commit hooks** - Validação automática (black, ruff, mypy, eslint, ktlint)

## Releases

APKs disponíveis:
- **`TaNaMao-release-v1.0.0.apk`** - Build de produção assinado (3.6 MB)
- `TaNaMao-debug.apk` - Build de desenvolvimento

### Build Release

```bash
cd android
./gradlew assembleRelease
# APK em: app/build/outputs/apk/release/app-release.apk
```

**Requisitos para release:**
- Keystore configurado em `local.properties`
- Variáveis: `KEYSTORE_PATH`, `KEYSTORE_PASSWORD`, `KEY_ALIAS`, `KEY_PASSWORD`

## Licença

MIT License - Dados públicos do Governo Federal do Brasil.
