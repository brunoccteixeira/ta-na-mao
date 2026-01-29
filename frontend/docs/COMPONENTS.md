# Componentes - Frontend Tá na Mão

## Hierarquia de Componentes

```
App
├── Header
│   └── Logo, Navigation
├── Sidebar
│   ├── ProgramSelector
│   ├── MetricSelector
│   ├── RegionSelector
│   └── MunicipalitySearch
├── MainContent
│   ├── NationalSummary
│   │   └── StatCard (x4)
│   ├── BrazilMap
│   │   └── GeoJSON Layers
│   └── DetailPanel
│       ├── StateCard / MunicipalityCard
│       └── Charts
│           ├── TrendChart
│           ├── DemographicBreakdown
│           └── ProgramComparison
└── Footer
    └── DataSources, LastUpdate
```

---

## Componentes do Dashboard

### NationalSummary

Exibe os KPIs nacionais em cards.

**Arquivo**: `src/components/Dashboard/NationalSummary.tsx`

**Props**: Nenhuma (usa dados do TanStack Query)

**Dados exibidos**:
- População total
- Famílias no CadÚnico
- Total de beneficiários
- Taxa de cobertura média

```tsx
<NationalSummary />

// Renderiza:
// ┌─────────────┐ ┌─────────────┐ ┌─────────────┐ ┌─────────────┐
// │  População  │ │  CadÚnico   │ │ Beneficiár. │ │  Cobertura  │
// │    215M     │ │   20.6M     │ │   12.4M     │ │    42%      │
// └─────────────┘ └─────────────┘ └─────────────┘ └─────────────┘
```

---

### ProgramSelector

Chips para seleção do programa social ativo.

**Arquivo**: `src/components/Dashboard/ProgramSelector.tsx`

**Props**:
```typescript
interface ProgramSelectorProps {
  selected: ProgramCode | null;
  onChange: (code: ProgramCode | null) => void;
}
```

**Programas disponíveis**:
- Todos (null)
- Bolsa Família
- BPC/LOAS
- Farmácia Popular
- TSEE
- Dignidade Menstrual

---

### MetricSelector

Seletor da métrica para coloração do mapa.

**Arquivo**: `src/components/Dashboard/MetricSelector.tsx`

**Props**:
```typescript
interface MetricSelectorProps {
  selected: MetricType;
  onChange: (metric: MetricType) => void;
}

type MetricType = 'coverage' | 'beneficiaries' | 'gap' | 'value';
```

**Métricas**:
| Código | Label | Descrição |
|--------|-------|-----------|
| `coverage` | Cobertura | % de famílias atendidas |
| `beneficiaries` | Beneficiários | Número absoluto |
| `gap` | Gap | Famílias não atendidas |
| `value` | Valor (R$) | Total em reais |

---

### RegionSelector

Filtro por região do Brasil.

**Arquivo**: `src/components/Dashboard/RegionSelector.tsx`

**Regiões**:
- Norte (N)
- Nordeste (NE)
- Centro-Oeste (CO)
- Sudeste (SE)
- Sul (S)

---

### MunicipalitySearch

Campo de busca com autocomplete.

**Arquivo**: `src/components/Dashboard/MunicipalitySearch.tsx`

**Comportamento**:
1. Usuário digita (mínimo 2 caracteres)
2. Debounce de 300ms
3. Busca via API `/municipalities/search`
4. Exibe dropdown com resultados
5. Clique seleciona município

---

### StateCard

Card com informações de um estado.

**Arquivo**: `src/components/Dashboard/StateCard.tsx`

**Props**:
```typescript
interface StateCardProps {
  state: StateData;
  program?: ProgramCode;
  onSelect?: () => void;
}
```

**Exibe**:
- Nome e sigla do estado
- População
- Número de municípios
- Beneficiários (total e %)
- Comparação com média nacional

---

### MunicipalityCard

Card com informações de um município.

**Arquivo**: `src/components/Dashboard/MunicipalityCard.tsx`

**Props**:
```typescript
interface MunicipalityCardProps {
  municipality: MunicipalityData;
  programs: MunicipalityProgram[];
}
```

**Exibe**:
- Nome, estado, região
- População e área
- Lista de programas com:
  - Beneficiários
  - Valor (R$)
  - Taxa de cobertura (progress bar)
  - Data de referência

---

### RankingPanel

Painel com ranking de municípios.

**Arquivo**: `src/components/Dashboard/RankingPanel.tsx`

**Props**:
```typescript
interface RankingPanelProps {
  program: ProgramCode;
  stateCode?: string;
  orderBy?: 'coverage' | 'beneficiaries';
  limit?: number;
}
```

**Exibe**:
- Top N municípios
- Medalhas para top 3
- Barra de cobertura
- Clique navega para detalhes

---

## Componentes de Mapa

### BrazilMap

Mapa interativo do Brasil usando Leaflet.

**Arquivo**: `src/components/Map/BrazilMap.tsx`

**Props**:
```typescript
interface BrazilMapProps {
  level: 'states' | 'municipalities';
  stateCode?: string;
  program?: ProgramCode;
  metric?: MetricType;
  onStateClick?: (stateCode: string) => void;
  onMunicipalityClick?: (ibgeCode: string) => void;
}
```

**Comportamento**:
1. **Nível estados**: Exibe todos os 27 estados
2. **Clique em estado**: Zoom para municípios
3. **Coloração**: Baseada na métrica selecionada
4. **Tooltip**: Exibe dados ao hover
5. **Legenda**: Escala de cores dinâmica

**Escala de Cores (Cobertura)**:
| Faixa | Cor | Classe Tailwind |
|-------|-----|-----------------|
| 80%+ | Verde escuro | `bg-green-700` |
| 60-79% | Verde | `bg-green-500` |
| 40-59% | Amarelo | `bg-yellow-500` |
| 20-39% | Laranja | `bg-orange-500` |
| <20% | Vermelho | `bg-red-500` |

---

## Componentes de Gráficos

### TrendChart

Gráfico de linha com série temporal.

**Arquivo**: `src/components/Charts/TrendChart.tsx`

**Props**:
```typescript
interface TrendChartProps {
  data: TimeSeriesPoint[];
  metric?: 'beneficiaries' | 'families' | 'value';
  height?: number;
}
```

**Usa**: Recharts `<LineChart>`

**Período**: Até 120 meses (10 anos para Farmácia Popular)

---

### DemographicBreakdown

Gráfico de barras com distribuição demográfica.

**Arquivo**: `src/components/Charts/DemographicBreakdown.tsx`

**Props**:
```typescript
interface DemographicBreakdownProps {
  data: Demographics;
  type?: 'income' | 'age';
}
```

**Visualizações**:
1. **Por renda**: Extrema pobreza, Pobreza, Baixa renda
2. **Por idade**: 0-5, 6-14, 15-17, 18-64, 65+

**Usa**: Recharts `<BarChart>`

---

### ProgramComparison

Comparativo entre programas sociais.

**Arquivo**: `src/components/Charts/ProgramComparison.tsx`

**Props**:
```typescript
interface ProgramComparisonProps {
  programs: ProgramStats[];
  metric?: 'beneficiaries' | 'coverage' | 'value';
}
```

**Usa**: Recharts `<BarChart>` horizontal

---

## Componentes Utilitários

### StatCard

Card genérico para estatísticas.

```typescript
interface StatCardProps {
  title: string;
  value: number | string;
  unit?: string;
  icon?: LucideIcon;
  trend?: {
    value: number;
    direction: 'up' | 'down';
  };
  loading?: boolean;
}
```

### CoverageBar

Barra de progresso para taxa de cobertura.

```typescript
interface CoverageBarProps {
  value: number; // 0-100
  showLabel?: boolean;
  size?: 'sm' | 'md' | 'lg';
}
```

### Skeleton

Placeholder durante carregamento.

```typescript
interface SkeletonProps {
  width?: string | number;
  height?: string | number;
  className?: string;
}
```

### ErrorBoundary

Fallback para erros de renderização.

```typescript
interface ErrorBoundaryProps {
  fallback?: ReactNode;
  onError?: (error: Error) => void;
  children: ReactNode;
}
```

---

## Padrões de Uso

### Composição de Componentes

```tsx
// Página principal
function Dashboard() {
  return (
    <div className="flex h-screen">
      {/* Sidebar */}
      <aside className="w-64 bg-white shadow">
        <ProgramSelector />
        <MetricSelector />
        <MunicipalitySearch />
      </aside>

      {/* Main content */}
      <main className="flex-1 p-4">
        <NationalSummary />

        <div className="grid grid-cols-2 gap-4 mt-4">
          <BrazilMap />
          <div>
            <StateCard />
            <TrendChart />
          </div>
        </div>
      </main>
    </div>
  );
}
```

### Tratamento de Loading

```tsx
function StateCard({ stateCode }: { stateCode: string }) {
  const { data, isLoading, error } = useQuery({
    queryKey: ['state', stateCode],
    queryFn: () => getStateDetail(stateCode),
  });

  if (isLoading) {
    return (
      <div className="bg-white rounded-lg p-4">
        <Skeleton height={24} width="60%" />
        <Skeleton height={48} className="mt-2" />
        <Skeleton height={16} width="80%" className="mt-2" />
      </div>
    );
  }

  if (error) {
    return <ErrorCard message="Erro ao carregar estado" />;
  }

  return (
    <div className="bg-white rounded-lg p-4">
      <h2>{data.name}</h2>
      {/* ... */}
    </div>
  );
}
```
