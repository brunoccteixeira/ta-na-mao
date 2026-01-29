# Frontend - Tá na Mão Dashboard

Dashboard web para visualização de dados de programas sociais brasileiros com granularidade municipal.

## Stack Tecnológico

| Tecnologia | Versão | Propósito |
|------------|--------|-----------|
| **React** | 18.2 | UI Library |
| **TypeScript** | 5.2 | Type Safety |
| **Vite** | 5.0 | Build Tool |
| **TanStack Query** | 5.17 | Data Fetching & Cache |
| **Zustand** | 4.4 | State Management |
| **Leaflet** | 1.9 | Mapas Interativos |
| **Recharts** | 2.10 | Gráficos |
| **Tailwind CSS** | 3.4 | Styling |
| **Axios** | 1.6 | HTTP Client |
| **Lucide React** | 0.303 | Ícones |

## Quick Start

```bash
# Instalar dependências
cd frontend
npm install

# Iniciar dev server
npm run dev

# Build para produção
npm run build

# Preview da build
npm run preview
```

## Estrutura do Projeto

```
frontend/
├── src/
│   ├── api/
│   │   └── client.ts           # Configuração Axios + endpoints
│   ├── components/
│   │   ├── Charts/             # Gráficos (Recharts)
│   │   │   ├── TrendChart.tsx
│   │   │   ├── DemographicBreakdown.tsx
│   │   │   └── ProgramComparison.tsx
│   │   ├── Dashboard/          # Componentes do dashboard
│   │   │   ├── NationalSummary.tsx
│   │   │   ├── ProgramSelector.tsx
│   │   │   ├── MetricSelector.tsx
│   │   │   ├── RegionSelector.tsx
│   │   │   ├── StateCard.tsx
│   │   │   ├── RegionCard.tsx
│   │   │   ├── MunicipalityCard.tsx
│   │   │   ├── MunicipalitySearch.tsx
│   │   │   └── RankingPanel.tsx
│   │   └── Map/
│   │       └── BrazilMap.tsx   # Mapa choropleth
│   ├── hooks/
│   │   └── useGeoJSON.ts       # Hook para dados geográficos
│   ├── stores/
│   │   └── dashboardStore.ts   # Zustand store
│   ├── App.tsx                 # Componente raiz
│   ├── main.tsx                # Entry point
│   └── vite-env.d.ts           # Type declarations
├── public/
├── docs/                       # Documentação
├── package.json
├── tailwind.config.js
├── tsconfig.json
└── vite.config.ts
```

## Funcionalidades

### Implementadas

- [x] Dashboard com KPIs nacionais
- [x] Mapa choropleth do Brasil (estados e municípios)
- [x] Seletor de programas sociais
- [x] Seletor de métricas (cobertura, beneficiários, gap)
- [x] Busca de municípios com autocomplete
- [x] Cards de estado com estatísticas
- [x] Ranking de municípios
- [x] Gráfico de tendência histórica (10 anos)
- [x] Breakdown demográfico (faixas de renda/idade)
- [x] Comparativo entre programas
- [x] Exportação de dados (CSV)

### Planejadas

- [ ] Modo escuro
- [ ] PWA (offline support)
- [ ] Filtros avançados
- [ ] Dashboard compartilhável (deep links)

## Documentação Adicional

- [Arquitetura](./ARCHITECTURE.md) - Estrutura de componentes e padrões
- [Componentes](./COMPONENTS.md) - Design system e componentes
- [API Client](./API_CLIENT.md) - Integração com backend

## Variáveis de Ambiente

```bash
# .env.local
VITE_API_URL=http://localhost:8000/api/v1
```

## Scripts

| Comando | Descrição |
|---------|-----------|
| `npm run dev` | Inicia servidor de desenvolvimento (porta 5173) |
| `npm run build` | Compila para produção |
| `npm run preview` | Preview da build de produção |
| `npm run lint` | Executa ESLint |
