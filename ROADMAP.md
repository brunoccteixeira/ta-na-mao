# Roadmap - Tá na Mão

Plano de desenvolvimento da plataforma de acesso a benefícios sociais brasileiros.

---

## Visão Geral

**Objetivo**: Criar uma plataforma que ajuda cidadãos brasileiros a descobrir e acessar benefícios sociais aos quais têm direito.

**Público-alvo**: Cidadãos de baixa renda/escolaridade (linguagem simples, mobile-first).

**Premissas do MVP**:
- Só elegibilidade (não entrega o benefício, apenas informa)
- Sem autenticação (usuário não precisa criar conta)
- Sem Gov.br (não pedimos senha de nenhum sistema)
- Mobile-first (86% do público usa celular)
- Linguagem simples (acessível para 5ª série)

---

## Status Atual

| Componente | Status | Cobertura |
|------------|--------|-----------|
| **Backend API** | ✅ Produção | 15+ endpoints |
| **Frontend Web** | ✅ MVP | PWA completo |
| **Android App** | ✅ MVP | Play Store ready |
| **Catálogo de Benefícios** | ✅ Completo | 229 benefícios |
| **API v2 Unificada** | ✅ Implementado | Pronto para migração |

### Catálogo de Benefícios

| Escopo | Quantidade | Status |
|--------|------------|--------|
| Federais | 16 | ✅ Completo |
| Estaduais | 106 (27 UFs) | ✅ Completo |
| Municipais | 97 (40 cidades) | ✅ Completo |
| Setoriais | 10 | ✅ Completo |
| **Total** | **229** | ✅ |

---

## Sprints Concluídos

### Sprint 1-6: Fundação ✅

- [x] Estrutura de dados JSON para catálogo
- [x] Motor de elegibilidade básico
- [x] Rotas do website
- [x] Landing page
- [x] 16 benefícios federais
- [x] 106 benefícios estaduais (27 UFs)
- [x] 10 benefícios setoriais
- [x] Catálogo navegável com filtros
- [x] PWA manifest + service worker + SEO

### Sprint 7: Benefícios Municipais ✅

- [x] Criar pasta `municipalities/`
- [x] 40 municípios cobertos (27 capitais + 13 grandes cidades)
- [x] 97 benefícios municipais
- [x] Filtro por município no Catalog
- [x] Categoria municipal no RightsWallet

### Sprint 8: Unificação da Base de Dados ✅

- [x] Migration Alembic para tabela `benefits`
- [x] Model SQLAlchemy `Benefit`
- [x] Schema Pydantic `CitizenProfile`
- [x] Serviço de elegibilidade no backend
- [x] API v2 endpoints (`/api/v2/benefits/`)
- [x] Script de migração JSON → PostgreSQL
- [x] Documentação API v2

---

## Próximos Sprints

### Sprint 9: Integração Frontend/Android com API v2

**Objetivo**: Fazer Frontend e Android consumirem a API v2 como fonte única.

- [ ] Frontend: Hook `useBenefitsAPI()` para consumir Backend
- [ ] Frontend: Cache localStorage (TTL 24h)
- [ ] Frontend: Fallback para JSON local se API offline
- [ ] Android: Atualizar DTOs para novo schema
- [ ] Android: Cache Room/SQLite
- [ ] Android: Sync periódico em background
- [ ] Testar modo offline em ambas plataformas

### Sprint 10: Expansão Municipal

**Objetivo**: Ampliar cobertura municipal para cidades >100k habitantes.

- [ ] Pesquisar benefícios de cidades com >500k habitantes
- [ ] Adicionar mais 50 municípios ao catálogo
- [ ] Meta: 200+ benefícios municipais

### Sprint 11: Integrações Externas

**Objetivo**: Conectar com APIs governamentais para dados em tempo real.

- [ ] Integração consulta CadÚnico (se API disponível)
- [ ] Integração consulta Valores a Receber (BCB)
- [ ] Push notifications (FCM) no Android
- [ ] Alertas de novos benefícios/atualizações

### Sprint 12: Gov.br e Autenticação

**Objetivo**: Permitir login opcional via Gov.br para features avançadas.

- [ ] Login Gov.br (OAuth)
- [ ] Consulta automática de benefícios ativos
- [ ] Histórico de consultas salvo
- [ ] Perfil persistente

---

## Backlog (Futuro)

### Features Técnicas
- [ ] Analytics unificado (GA4 + eventos customizados)
- [ ] A/B testing framework
- [ ] Cache Redis para catálogo (TTL 1h)
- [ ] Rate limiting por IP
- [ ] Monitoramento Sentry

### Features de Produto
- [ ] Widget Android
- [ ] Deep links
- [ ] Instant App
- [ ] Wear OS support
- [ ] Biometria/PIN para dados sensíveis
- [ ] Onboarding flow interativo

### Expansão de Conteúdo
- [ ] Motor Vivo (monitoramento de legislação)
- [ ] Alertas de mudanças em benefícios
- [ ] Calculadora de benefícios
- [ ] Simulador de CadÚnico
- [ ] FAQ por benefício
- [ ] Vídeos explicativos

### Parcerias
- [ ] Integração com CRAS (agendamento)
- [ ] Integração com farmácias credenciadas
- [ ] Dashboard para gestores públicos
- [ ] API para terceiros

---

## Arquitetura Atual

```
┌─────────────────────────────────────────────────────────────────┐
│                    FONTE ÚNICA (Backend)                        │
│  ┌─────────────────────────────────────────────────────────┐   │
│  │              PostgreSQL + Redis Cache                    │   │
│  │  ┌──────────┐ ┌──────────┐ ┌──────────┐ ┌──────────┐   │   │
│  │  │ benefits │ │ rules    │ │ documents│ │ updates  │   │   │
│  │  │ (229+)   │ │ (elegib.)│ │ (PDF/img)│ │ (audit)  │   │   │
│  │  └──────────┘ └──────────┘ └──────────┘ └──────────┘   │   │
│  └─────────────────────────────────────────────────────────┘   │
│                              │                                  │
│                              ▼                                  │
│  ┌─────────────────────────────────────────────────────────┐   │
│  │                    API REST v2                           │   │
│  │  GET /benefits                    # Catálogo completo    │   │
│  │  GET /benefits/{id}               # Detalhes             │   │
│  │  POST /eligibility/check          # Avaliação            │   │
│  │  GET /benefits/by-location/{ibge} # Por município        │   │
│  └─────────────────────────────────────────────────────────┘   │
└─────────────────────────────────────────────────────────────────┘
                    │                     │
        ┌───────────┘                     └───────────┐
        ▼                                             ▼
┌───────────────────┐                    ┌───────────────────┐
│   Website MVP     │                    │   Android App     │
│   (React)         │                    │   (Kotlin)        │
│                   │                    │                   │
│ • Cache local 24h │                    │ • Cache SQLite    │
│ • Fallback JSON   │                    │ • Offline básico  │
│ • PWA offline     │                    │ • Sync periódico  │
└───────────────────┘                    └───────────────────┘
```

---

## Comandos Úteis

### Backend

```bash
cd backend

# Aplicar migrations
alembic upgrade head

# Migrar benefícios do frontend para PostgreSQL
python scripts/migrate_benefits.py

# Rodar servidor
uvicorn app.main:app --reload

# Testar API v2
curl http://localhost:8000/api/v2/benefits/stats
```

### Frontend

```bash
cd frontend

# Desenvolvimento
npm run dev

# Build
npm run build

# Preview
npm run preview
```

### Android

```bash
cd android

# Build debug
./gradlew assembleDebug

# Instalar no dispositivo
./gradlew installDebug

# Testes
./gradlew test
```

---

## Métricas de Sucesso

| Métrica | Meta | Atual |
|---------|------|-------|
| Benefícios no catálogo | 300+ | 229 |
| Estados cobertos | 27 | 27 ✅ |
| Municípios cobertos | 100+ | 40 |
| Taxa de conclusão do wizard | >70% | TBD |
| NPS | >50 | TBD |

---

## Links Úteis

- [README Principal](README.md)
- [MANIFESTO](MANIFESTO.md)
- [Guia de Contribuição](CONTRIBUTING.md)
- [Documentação da API](backend/docs/API.md)
- [Arquitetura do Agente](backend/docs/AGENT.md)

---

*Última atualização: Janeiro 2026*
