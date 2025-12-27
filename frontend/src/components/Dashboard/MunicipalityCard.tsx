/**
 * Municipality detail card shown when a municipality is selected
 */

import { useQuery } from '@tanstack/react-query';
import { useDashboardStore } from '../../stores/dashboardStore';
import { api } from '../../api/client';
import { formatNumber, getCoverageColor } from '../../hooks/useGeoJSON';

interface MunicipalityData {
  ibge_code: string;
  name: string;
  state_abbreviation: string;
  population: number;
  total_beneficiaries: number;
  total_families: number;
  total_value_brl: number;
  cadunico_families: number;
  coverage_rate: number;
}

export default function MunicipalityCard() {
  const { selectedMunicipality, selectedProgram, selectMunicipality } = useDashboardStore();

  const { data: munData, isLoading } = useQuery({
    queryKey: ['municipality', selectedMunicipality, selectedProgram],
    queryFn: async () => {
      const params = new URLSearchParams();
      if (selectedProgram) params.append('program', selectedProgram);
      const response = await api.get(`/municipalities/${selectedMunicipality}?${params}`);
      return response.data as MunicipalityData;
    },
    enabled: !!selectedMunicipality,
  });

  if (!selectedMunicipality) {
    return null;
  }

  if (isLoading) {
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

  if (!munData) {
    return (
      <div className="bg-slate-900/50 rounded-xl border border-slate-800 p-4">
        <div className="text-center text-slate-500 text-sm">
          <p>Dados não disponíveis</p>
        </div>
      </div>
    );
  }

  const coverage = munData.coverage_rate || 0;
  const gap = (munData.cadunico_families || 0) - (munData.total_beneficiaries || 0);

  return (
    <div className="bg-slate-900/50 rounded-xl border border-slate-800 p-4">
      {/* Header */}
      <div className="flex items-center gap-3 mb-4">
        <div
          className="w-10 h-10 rounded-lg flex items-center justify-center text-sm font-bold text-white"
          style={{ backgroundColor: getCoverageColor(coverage) }}
        >
          {munData.state_abbreviation}
        </div>
        <div className="flex-1">
          <h3 className="font-semibold">{munData.name}</h3>
          <p className="text-xs text-slate-400">
            {munData.state_abbreviation} • {formatNumber(munData.population || 0)} hab
          </p>
        </div>
        <button
          onClick={() => selectMunicipality(null)}
          className="text-slate-400 hover:text-white text-xl"
        >
          ×
        </button>
      </div>

      {/* Stats */}
      <div className="space-y-3">
        <div className="bg-slate-800/50 rounded-lg p-3">
          <div className="flex justify-between items-center mb-1">
            <span className="text-xs text-slate-400">Código IBGE</span>
            <span className="text-sm font-medium font-mono">{munData.ibge_code}</span>
          </div>
        </div>

        <div className="bg-slate-800/50 rounded-lg p-3">
          <div className="flex justify-between items-center mb-1">
            <span className="text-xs text-slate-400">CadÚnico (famílias)</span>
            <span className="text-sm font-medium text-sky-400">
              {formatNumber(munData.cadunico_families || 0)}
            </span>
          </div>
        </div>

        <div className="bg-slate-800/50 rounded-lg p-3">
          <div className="flex justify-between items-center mb-1">
            <span className="text-xs text-slate-400">Beneficiários</span>
            <span className="text-sm font-medium text-emerald-400">
              {formatNumber(munData.total_beneficiaries || 0)}
            </span>
          </div>
        </div>

        <div className="bg-slate-800/50 rounded-lg p-3">
          <div className="flex justify-between items-center mb-1">
            <span className="text-xs text-slate-400">Valor Total</span>
            <span className="text-sm font-medium text-amber-400">
              R$ {formatNumber(munData.total_value_brl || 0)}
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
                width: `${Math.min(coverage * 100, 100)}%`,
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

      {/* Back button */}
      <button
        onClick={() => selectMunicipality(null)}
        className="mt-4 w-full py-2 text-sm text-slate-400 hover:text-white hover:bg-slate-800 rounded-lg transition-colors"
      >
        ← Voltar para estado
      </button>
    </div>
  );
}
