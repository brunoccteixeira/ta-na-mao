# API Client - Frontend Tá na Mão

## Configuração

### Axios Setup

```typescript
// src/api/client.ts
import axios from 'axios';

const api = axios.create({
  baseURL: import.meta.env.VITE_API_URL || 'http://localhost:8000/api/v1',
  timeout: 30000,
  headers: {
    'Content-Type': 'application/json',
  },
});

// Interceptor de erro
api.interceptors.response.use(
  (response) => response,
  (error) => {
    if (error.response?.status === 404) {
      console.error('Recurso não encontrado:', error.config.url);
    }
    return Promise.reject(error);
  }
);

export default api;
```

### Variáveis de Ambiente

```bash
# .env.local (desenvolvimento)
VITE_API_URL=http://localhost:8000/api/v1

# .env.production
VITE_API_URL=https://api.tanamao.gov.br/api/v1
```

---

## Endpoints Consumidos

### Programs

```typescript
// Listar programas
export const getPrograms = () =>
  api.get<Program[]>('/programs/');

// Detalhes de programa
export const getProgram = (code: string) =>
  api.get<ProgramDetail>(`/programs/${code}`);

// Ranking de municípios
export const getProgramRanking = (
  code: string,
  params?: {
    state_code?: string;
    order_by?: 'coverage' | 'beneficiaries';
    limit?: number;
  }
) => api.get<RankingResponse>(`/programs/${code}/ranking`, { params });
```

### Aggregations

```typescript
// Nacional
export const getNational = (program?: string) =>
  api.get<NationalAggregation>('/aggregations/national', {
    params: { program }
  });

// Estados
export const getStates = (program?: string) =>
  api.get<StatesAggregation>('/aggregations/states', {
    params: { program }
  });

// Detalhes de estado
export const getStateDetail = (stateCode: string, program?: string) =>
  api.get<StateDetail>(`/aggregations/states/${stateCode}`, {
    params: { program }
  });

// Regiões
export const getRegions = (program?: string) =>
  api.get<RegionsAggregation>('/aggregations/regions', {
    params: { program }
  });

// Série temporal
export const getTimeSeries = (program?: string, stateCode?: string) =>
  api.get<TimeSeriesResponse>('/aggregations/time-series', {
    params: { program, state_code: stateCode }
  });

// Demografia
export const getDemographics = (stateCode?: string) =>
  api.get<Demographics>('/aggregations/demographics', {
    params: { state_code: stateCode }
  });
```

### Municipalities

```typescript
// Listar municípios
export const getMunicipalities = (params?: {
  state_code?: string;
  search?: string;
  page?: number;
  limit?: number;
}) => api.get<PaginatedResponse<Municipality>>('/municipalities/', { params });

// Buscar municípios
export const searchMunicipalities = (q: string, limit = 20) =>
  api.get<MunicipalitySearch[]>('/municipalities/search', {
    params: { q, limit }
  });

// Detalhes de município
export const getMunicipality = (ibgeCode: string, program?: string) =>
  api.get<MunicipalityDetail>(`/municipalities/${ibgeCode}`, {
    params: { program }
  });

// Programas do município
export const getMunicipalityPrograms = (ibgeCode: string) =>
  api.get<MunicipalityPrograms>(`/municipalities/${ibgeCode}/programs`);
```

### GeoJSON

```typescript
// GeoJSON dos estados
export const getStatesGeoJSON = (params?: {
  simplified?: boolean;
  program?: string;
  metric?: string;
}) => api.get<GeoJSONResponse>('/geo/states', { params });

// GeoJSON dos municípios (por estado)
export const getMunicipalitiesGeoJSON = (
  stateCode: string,
  params?: {
    simplified?: boolean;
    program?: string;
  }
) => api.get<GeoJSONResponse>('/geo/municipalities', {
  params: { state_code: stateCode, ...params }
});

// Bounding box
export const getBounds = (stateCode?: string) =>
  api.get<Bounds>('/geo/bounds', {
    params: { state_code: stateCode }
  });
```

---

## Tipos TypeScript

```typescript
// src/types/api.ts

// Programas
interface Program {
  code: string;
  name: string;
  description: string;
  data_source_url: string;
  update_frequency: 'daily' | 'weekly' | 'monthly';
  national_stats: ProgramStats | null;
}

interface ProgramStats {
  total_beneficiaries: number;
  total_families: number;
  total_value_brl: number;
  latest_data_date: string | null;
}

// Municípios
interface Municipality {
  ibge_code: string;
  name: string;
  state_id: number;
  population: number | null;
  area_km2: number | null;
}

interface MunicipalityDetail extends Municipality {
  state_abbreviation: string;
  state_name: string;
  region: string;
  cadunico_families: number | null;
  total_beneficiaries: number | null;
  total_families: number | null;
  total_value_brl: number | null;
  coverage_rate: number | null;
}

// Agregações
interface NationalAggregation {
  level: string;
  population: number;
  cadunico_families: number;
  total_municipalities: number;
  total_states: number;
  program_stats: ProgramStats | null;
}

interface StateAggregation {
  ibge_code: string;
  name: string;
  abbreviation: string;
  region: string;
  population: number;
  municipality_count: number;
  total_beneficiaries: number | null;
  total_families: number | null;
  cadunico_families: number | null;
  total_value_brl: number | null;
  avg_coverage_rate: number | null;
}

// Série temporal
interface TimeSeriesPoint {
  date: string;
  month: string;
  total_beneficiaries: number;
  total_families: number;
  total_value_brl: number;
  avg_coverage_rate: number;
}

// GeoJSON
interface GeoJSONResponse {
  type: 'FeatureCollection';
  features: GeoJSONFeature[];
  metadata?: {
    count: number;
    state_id?: number;
    simplified: boolean;
  };
}

interface GeoJSONFeature {
  type: 'Feature';
  properties: {
    ibge_code: string;
    name: string;
    abbreviation?: string;
    region?: string;
    beneficiaries?: number;
    families?: number;
    coverage?: number;
  };
  geometry: {
    type: 'MultiPolygon' | 'Polygon';
    coordinates: number[][][][];
  };
}
```

---

## TanStack Query Hooks

### usePrograms

```typescript
import { useQuery } from '@tanstack/react-query';
import { getPrograms } from '@/api/client';

export function usePrograms() {
  return useQuery({
    queryKey: ['programs'],
    queryFn: async () => {
      const { data } = await getPrograms();
      return data;
    },
    staleTime: 24 * 60 * 60 * 1000, // 24 horas
  });
}
```

### useNational

```typescript
export function useNational(program?: string) {
  return useQuery({
    queryKey: ['national', program],
    queryFn: async () => {
      const { data } = await getNational(program);
      return data;
    },
    staleTime: 5 * 60 * 1000, // 5 minutos
  });
}
```

### useStates

```typescript
export function useStates(program?: string) {
  return useQuery({
    queryKey: ['states', program],
    queryFn: async () => {
      const { data } = await getStates(program);
      return data.states;
    },
    staleTime: 5 * 60 * 1000,
  });
}
```

### useGeoJSON

```typescript
export function useGeoJSON(stateCode?: string, program?: string) {
  return useQuery({
    queryKey: ['geojson', stateCode, program],
    queryFn: async () => {
      if (stateCode) {
        const { data } = await getMunicipalitiesGeoJSON(stateCode, {
          simplified: true,
          program,
        });
        return data;
      }
      const { data } = await getStatesGeoJSON({
        simplified: true,
        program,
      });
      return data;
    },
    staleTime: 30 * 60 * 1000, // 30 minutos
  });
}
```

### useTimeSeries

```typescript
export function useTimeSeries(program?: string, stateCode?: string) {
  return useQuery({
    queryKey: ['timeSeries', program, stateCode],
    queryFn: async () => {
      const { data } = await getTimeSeries(program, stateCode);
      return data.data;
    },
    staleTime: 60 * 60 * 1000, // 1 hora
    enabled: !!program, // Só busca se programa selecionado
  });
}
```

### useMunicipalitySearch

```typescript
export function useMunicipalitySearch(query: string) {
  return useQuery({
    queryKey: ['municipalitySearch', query],
    queryFn: async () => {
      const { data } = await searchMunicipalities(query);
      return data;
    },
    enabled: query.length >= 2,
    staleTime: 10 * 60 * 1000, // 10 minutos
  });
}
```

---

## API v2 - Catálogo Unificado de Benefícios

### useBenefitsList

Hook para listar benefícios com filtros e paginação. Usa cache localStorage com fallback para JSON estático.

```typescript
import { useBenefitsList } from '@/hooks/useBenefitsAPI';

function BenefitsCatalog() {
  const {
    data,
    isLoading,
    isError,
    error
  } = useBenefitsList({
    scope: 'federal',        // 'federal' | 'state' | 'municipal' | 'sectoral'
    state: 'SP',             // Código UF
    search: 'bolsa',         // Busca por nome/descrição
    limit: 50,               // Itens por página
  });

  if (isLoading) return <Spinner />;
  if (isError) return <Error message={error.message} />;

  return (
    <div>
      <p>{data.total} benefícios encontrados</p>
      {data.items.map(benefit => (
        <BenefitCard key={benefit.id} benefit={benefit} />
      ))}
    </div>
  );
}
```

### useBenefitDetail

Hook para detalhes de um benefício específico.

```typescript
import { useBenefitDetail } from '@/hooks/useBenefitsAPI';

function BenefitPage({ benefitId }: { benefitId: string }) {
  const { data: benefit, isLoading, isError } = useBenefitDetail(benefitId);

  if (isLoading) return <Spinner />;
  if (isError || !benefit) return <NotFound />;

  return (
    <div>
      <h1>{benefit.name}</h1>
      <p>{benefit.shortDescription}</p>
      <h2>Quem pode receber</h2>
      <ul>
        {benefit.eligibilityRules.map((rule, i) => (
          <li key={i}>{rule.description}</li>
        ))}
      </ul>
    </div>
  );
}
```

### useBenefitsByLocation

Hook para benefícios por localização geográfica.

```typescript
import { useBenefitsByLocation } from '@/hooks/useBenefitsAPI';

function LocationBenefits({ state, ibge }: { state: string; ibge?: string }) {
  const { data, isLoading } = useBenefitsByLocation(state, ibge);

  if (isLoading) return <Spinner />;

  return (
    <div>
      <h2>Federais ({data.federal.length})</h2>
      <h2>Estaduais ({data.state.length})</h2>
      <h2>Municipais ({data.municipal.length})</h2>
      <h2>Setoriais ({data.sectoral.length})</h2>
    </div>
  );
}
```

### useEligibilityCheck

Mutation para verificação de elegibilidade completa.

```typescript
import { useEligibilityCheck } from '@/hooks/useBenefitsAPI';

function EligibilityWizard() {
  const eligibilityMutation = useEligibilityCheck();

  const handleCheck = async (profile: CitizenProfile) => {
    try {
      const result = await eligibilityMutation.mutateAsync({ profile });

      console.log('Elegíveis:', result.summary.eligible);
      console.log('Valor potencial:', result.summary.totalPotentialMonthly);
      console.log('Próximos passos:', result.summary.prioritySteps);
    } catch (error) {
      console.error('Erro na verificação:', error);
    }
  };

  return (
    <form onSubmit={(e) => { e.preventDefault(); handleCheck(profile); }}>
      {/* ... campos do formulário ... */}
      <button
        type="submit"
        disabled={eligibilityMutation.isPending}
      >
        {eligibilityMutation.isPending ? 'Verificando...' : 'Verificar elegibilidade'}
      </button>
    </form>
  );
}
```

### useBenefitsStats

Hook para estatísticas do catálogo.

```typescript
import { useBenefitsStats } from '@/hooks/useBenefitsAPI';

function CatalogStats() {
  const { data: stats, isLoading } = useBenefitsStats();

  if (isLoading) return null;

  return (
    <div>
      <p>{stats.totalBenefits} benefícios no catálogo</p>
      <p>{stats.byScope.federal} federais</p>
      <p>{stats.byScope.state} estaduais</p>
      <p>{stats.byScope.municipal} municipais</p>
      <p>{stats.statesCovered} estados cobertos</p>
    </div>
  );
}
```

### Cache e Fallback

Os hooks v2 implementam cache em três níveis:

1. **React Query Cache**: Cache em memória (5 min stale time)
2. **localStorage Cache**: Persistente por 24 horas
3. **JSON Fallback**: Se API e cache falham, usa dados estáticos do bundle

```typescript
// Limpar cache manualmente
import { clearBenefitsCache } from '@/hooks/useBenefitsAPI';

clearBenefitsCache(); // Remove cache localStorage
```

---

## Tratamento de Erros

```typescript
// src/api/errors.ts

export class ApiError extends Error {
  constructor(
    message: string,
    public status?: number,
    public code?: string
  ) {
    super(message);
    this.name = 'ApiError';
  }
}

export function handleApiError(error: unknown): ApiError {
  if (axios.isAxiosError(error)) {
    const status = error.response?.status;
    const message = error.response?.data?.detail || error.message;

    switch (status) {
      case 404:
        return new ApiError('Recurso não encontrado', 404, 'NOT_FOUND');
      case 422:
        return new ApiError('Dados inválidos', 422, 'VALIDATION_ERROR');
      case 500:
        return new ApiError('Erro no servidor', 500, 'SERVER_ERROR');
      default:
        return new ApiError(message, status);
    }
  }

  return new ApiError('Erro desconhecido');
}

// Uso nos componentes
function StateCard({ stateCode }: { stateCode: string }) {
  const { data, error, isLoading } = useQuery({
    queryKey: ['state', stateCode],
    queryFn: () => getStateDetail(stateCode),
  });

  if (error) {
    const apiError = handleApiError(error);
    return <ErrorCard message={apiError.message} code={apiError.code} />;
  }

  // ...
}
```

---

## Exportação de Dados

```typescript
// src/utils/export.ts

export function exportToCSV(data: any[], filename: string) {
  const headers = Object.keys(data[0]);
  const csvContent = [
    headers.join(','),
    ...data.map(row =>
      headers.map(header => {
        const value = row[header];
        // Escape valores com vírgula
        if (typeof value === 'string' && value.includes(',')) {
          return `"${value}"`;
        }
        return value;
      }).join(',')
    )
  ].join('\n');

  const blob = new Blob([csvContent], { type: 'text/csv;charset=utf-8;' });
  const link = document.createElement('a');
  link.href = URL.createObjectURL(blob);
  link.download = `${filename}.csv`;
  link.click();
}

// Uso
const handleExport = () => {
  const data = states.map(s => ({
    estado: s.name,
    sigla: s.abbreviation,
    beneficiarios: s.total_beneficiaries,
    cobertura: `${(s.avg_coverage_rate * 100).toFixed(1)}%`,
  }));

  exportToCSV(data, 'estados-beneficios');
};
```
