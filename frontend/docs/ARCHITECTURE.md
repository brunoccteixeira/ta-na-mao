# Arquitetura do Frontend

## Visão Geral

```
┌─────────────────────────────────────────────────────────────┐
│                         App.tsx                              │
│  ┌─────────────────────────────────────────────────────────┐│
│  │  QueryClientProvider (TanStack Query)                   ││
│  │  ┌─────────────────────────────────────────────────────┐││
│  │  │                    Layout                           │││
│  │  │  ┌─────────────┐ ┌─────────────┐ ┌───────────────┐ │││
│  │  │  │  Sidebar    │ │   Map       │ │   Details     │ │││
│  │  │  │  (Filters)  │ │  (Leaflet)  │ │   (Cards)     │ │││
│  │  │  └─────────────┘ └─────────────┘ └───────────────┘ │││
│  │  └─────────────────────────────────────────────────────┘││
│  └─────────────────────────────────────────────────────────┘│
└─────────────────────────────────────────────────────────────┘
```

## Camadas da Aplicação

### 1. Data Layer (API)

```
src/api/
└── client.ts
```

Configuração do Axios e definição de endpoints.

```typescript
// Exemplo de uso
const api = axios.create({
  baseURL: import.meta.env.VITE_API_URL
});

export const getPrograms = () => api.get('/programs/');
export const getNational = (program?: string) =>
  api.get('/aggregations/national', { params: { program } });
export const getStates = (program?: string) =>
  api.get('/aggregations/states', { params: { program } });
```

### 2. State Management (Zustand)

```
src/stores/
└── dashboardStore.ts
```

Estado global do dashboard.

```typescript
interface DashboardState {
  // Filtros ativos
  selectedProgram: ProgramCode | null;
  selectedMetric: 'coverage' | 'beneficiaries' | 'gap' | 'value';
  selectedState: string | null;
  selectedMunicipality: string | null;

  // Ações
  setProgram: (code: ProgramCode | null) => void;
  setMetric: (metric: MetricType) => void;
  setState: (code: string | null) => void;
  setMunicipality: (code: string | null) => void;
  reset: () => void;
}
```

### 3. Data Fetching (TanStack Query)

Hooks para busca de dados com cache automático.

```typescript
// Exemplo de uso nos componentes
function NationalSummary() {
  const { selectedProgram } = useDashboardStore();

  const { data, isLoading, error } = useQuery({
    queryKey: ['national', selectedProgram],
    queryFn: () => getNational(selectedProgram),
    staleTime: 5 * 60 * 1000, // 5 minutos
  });

  if (isLoading) return <Skeleton />;
  if (error) return <Error />;

  return <StatCards data={data} />;
}
```

### 4. Hooks Customizados

```
src/hooks/
└── useGeoJSON.ts
```

Hook para carregar e processar dados GeoJSON.

```typescript
function useGeoJSON(stateCode?: string, program?: string) {
  return useQuery({
    queryKey: ['geojson', stateCode, program],
    queryFn: async () => {
      if (stateCode) {
        return api.get('/geo/municipalities', {
          params: { state_code: stateCode, program }
        });
      }
      return api.get('/geo/states', { params: { program } });
    },
    staleTime: 30 * 60 * 1000, // 30 minutos (geometrias mudam pouco)
  });
}
```

### 5. Components (UI)

```
src/components/
├── Charts/       # Visualizações de dados
├── Dashboard/    # Componentes do painel
└── Map/          # Mapa interativo
```

---

## Fluxo de Dados

```
┌──────────────┐     ┌──────────────┐     ┌──────────────┐
│   User       │────▶│  Zustand     │────▶│  Components  │
│   Action     │     │  Store       │     │  Re-render   │
└──────────────┘     └──────────────┘     └──────────────┘
                            │
                            ▼
                     ┌──────────────┐
                     │  TanStack    │
                     │  Query       │
                     └──────────────┘
                            │
                            ▼
                     ┌──────────────┐
                     │  API Client  │
                     │  (Axios)     │
                     └──────────────┘
                            │
                            ▼
                     ┌──────────────┐
                     │  Backend     │
                     │  FastAPI     │
                     └──────────────┘
```

1. **Usuário interage** (seleciona programa, clica em estado)
2. **Zustand atualiza** o estado global
3. **Componentes re-renderizam** com novos filtros
4. **TanStack Query** verifica cache ou busca dados
5. **Axios** faz requisição HTTP
6. **Backend** retorna dados
7. **Cache é atualizado** e componentes exibem dados

---

## Padrões de Código

### Componentes

- Componentes funcionais com TypeScript
- Props tipadas com interfaces
- Desestruturação de props
- Composição sobre herança

```typescript
interface StatCardProps {
  title: string;
  value: number;
  unit?: string;
  trend?: 'up' | 'down' | 'stable';
  loading?: boolean;
}

export function StatCard({
  title,
  value,
  unit = '',
  trend,
  loading = false
}: StatCardProps) {
  if (loading) return <StatCardSkeleton />;

  return (
    <div className="bg-white rounded-lg shadow p-4">
      <h3 className="text-sm text-gray-500">{title}</h3>
      <p className="text-2xl font-bold">
        {formatNumber(value)}{unit}
      </p>
      {trend && <TrendIndicator trend={trend} />}
    </div>
  );
}
```

### Queries

- Query keys organizadas por domínio
- Stale time apropriado por tipo de dado
- Error boundaries para fallback

```typescript
// Query keys
const queryKeys = {
  programs: ['programs'],
  national: (program?: string) => ['national', program],
  states: (program?: string) => ['states', program],
  municipalities: (stateCode: string) => ['municipalities', stateCode],
  geojson: {
    states: (program?: string) => ['geojson', 'states', program],
    municipalities: (stateCode: string, program?: string) =>
      ['geojson', 'municipalities', stateCode, program],
  },
};
```

### Styling

- Tailwind CSS para estilização
- Classes utilitárias
- Responsividade mobile-first

```typescript
// Exemplo de classes responsivas
<div className="
  grid
  grid-cols-1
  md:grid-cols-2
  lg:grid-cols-4
  gap-4
">
  {stats.map(stat => <StatCard key={stat.id} {...stat} />)}
</div>
```

---

## Estratégia de Cache

| Dado | Stale Time | Cache Time | Justificativa |
|------|------------|------------|---------------|
| Programas | 24h | 7 dias | Lista fixa |
| Nacional | 5 min | 1 hora | Atualização frequente |
| Estados | 5 min | 1 hora | Atualização frequente |
| Municípios | 5 min | 1 hora | Atualização frequente |
| GeoJSON | 30 min | 24 horas | Geometrias estáveis |
| Time Series | 1 hora | 24 horas | Dados históricos |

---

## Performance

### Otimizações Implementadas

1. **GeoJSON Simplificado**: Geometrias reduzidas para renderização rápida
2. **Lazy Loading**: Municípios carregados sob demanda (por estado)
3. **Query Cache**: Evita requisições duplicadas
4. **Debounce**: Busca de municípios com delay de 300ms
5. **Memoização**: Componentes pesados com `React.memo`

### Métricas Alvo

| Métrica | Alvo | Atual |
|---------|------|-------|
| FCP (First Contentful Paint) | < 1.5s | ~1.2s |
| LCP (Largest Contentful Paint) | < 2.5s | ~2.0s |
| TTI (Time to Interactive) | < 3.5s | ~3.0s |
| Bundle Size (gzip) | < 200KB | ~180KB |
