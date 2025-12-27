/**
 * State detail card shown when a state is selected
 */

import { useQuery } from '@tanstack/react-query';
import { useDashboardStore } from '../../stores/dashboardStore';
import { fetchStatesAggregation } from '../../api/client';
import { formatNumber, getCoverageColor } from '../../hooks/useGeoJSON';

export default function StateCard() {
  const { selectedState, selectedProgram, selectState } = useDashboardStore();

  const { data: statesData } = useQuery({
    queryKey: ['aggregation', 'states', selectedProgram],
    queryFn: () => fetchStatesAggregation(selectedProgram || undefined),
  });

  if (!selectedState) {
    return (
      <div className="bg-slate-900/50 rounded-xl border border-slate-800 p-4 h-full flex items-center justify-center">
        <div className="text-center text-slate-500 text-sm">
          <div className="text-3xl mb-2">👆</div>
          <p>Clique em um estado<br/>para ver detalhes</p>
        </div>
      </div>
    );
  }

  const stateData = statesData?.states?.find(
    (s: any) => s.abbreviation === selectedState
  );

  if (!stateData) {
    return (
      <div className="bg-slate-900/50 rounded-xl border border-slate-800 p-4">
        <div className="animate-pulse">
          <div className="h-8 bg-slate-700 rounded w-1/3 mb-4"></div>
          <div className="space-y-2">
            {[...Array(4)].map((_, i) => (
              <div key={i} className="h-16 bg-slate-700 rounded"></div>
            ))}
          </div>
        </div>
      </div>
    );
  }

  const coverage = stateData.avg_coverage_rate || 0;
  const cadunicoFamilies = stateData.cadunico_families || 0;
  const gap = cadunicoFamilies - (stateData.total_beneficiaries || 0);

  return (
    <div className="bg-slate-900/50 rounded-xl border border-slate-800 p-4">
      {/* Header */}
      <div className="flex items-center gap-3 mb-4">
        <div
          className="w-10 h-10 rounded-lg flex items-center justify-center text-sm font-bold"
          style={{ backgroundColor: getCoverageColor(coverage) }}
        >
          {stateData.abbreviation}
        </div>
        <div className="flex-1">
          <h3 className="font-semibold">{stateData.name}</h3>
          <p className="text-xs text-slate-400">
            {stateData.region} • {formatNumber(stateData.population || 0)} hab
          </p>
        </div>
        <button
          onClick={() => selectState(null)}
          className="text-slate-400 hover:text-white text-xl"
        >
          ×
        </button>
      </div>

      {/* Stats */}
      <div className="space-y-3">
        <div className="bg-slate-800/50 rounded-lg p-3">
          <div className="flex justify-between items-center mb-1">
            <span className="text-xs text-slate-400">Municípios</span>
            <span className="text-sm font-medium">{stateData.municipality_count || 0}</span>
          </div>
        </div>

        <div className="bg-slate-800/50 rounded-lg p-3">
          <div className="flex justify-between items-center mb-1">
            <span className="text-xs text-slate-400">Beneficiários</span>
            <span className="text-sm font-medium text-emerald-400">
              {formatNumber(stateData.total_beneficiaries || 0)}
            </span>
          </div>
        </div>

        <div className="bg-slate-800/50 rounded-lg p-3">
          <div className="flex justify-between items-center mb-1">
            <span className="text-xs text-slate-400">Valor Total</span>
            <span className="text-sm font-medium text-amber-400">
              R$ {formatNumber(stateData.total_value_brl || 0)}
            </span>
          </div>
        </div>

        <div className="bg-slate-800/50 rounded-lg p-3">
          <div className="flex justify-between items-center mb-1">
            <span className="text-xs text-slate-400">Cobertura</span>
            <span className="text-sm font-medium" style={{ color: getCoverageColor(coverage) }}>
              {(coverage * 100).toFixed(1)}%
            </span>
          </div>
          <div className="h-1.5 bg-slate-700 rounded-full overflow-hidden">
            <div
              className="h-full rounded-full"
              style={{
                width: `${coverage * 100}%`,
                backgroundColor: getCoverageColor(coverage),
              }}
            />
          </div>
        </div>

        <div className="bg-red-500/10 border border-red-500/30 rounded-lg p-3">
          <div className="text-red-400 text-xs font-medium">Gap</div>
          <div className="text-xl font-bold text-red-400">{formatNumber(gap > 0 ? gap : 0)}</div>
        </div>
      </div>
    </div>
  );
}
