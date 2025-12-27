/**
 * Region detail card shown when a region is selected
 */

import { useQuery } from '@tanstack/react-query';
import { useDashboardStore } from '../../stores/dashboardStore';
import { fetchRegionsAggregation, exportToCSV } from '../../api/client';
import { formatNumber, getCoverageColor } from '../../hooks/useGeoJSON';

const REGION_NAMES: Record<string, string> = {
  N: 'Norte',
  NE: 'Nordeste',
  CO: 'Centro-Oeste',
  SE: 'Sudeste',
  S: 'Sul',
};

const REGION_ICONS: Record<string, string> = {
  N: '🌳',
  NE: '☀️',
  CO: '🌾',
  SE: '🏙️',
  S: '❄️',
};

export default function RegionCard() {
  const { selectedRegion, selectedProgram, selectRegion } = useDashboardStore();

  const { data: regionsData } = useQuery({
    queryKey: ['aggregation', 'regions', selectedProgram],
    queryFn: () => fetchRegionsAggregation(selectedProgram || undefined),
  });

  if (!selectedRegion) {
    return null;
  }

  const regionData = regionsData?.regions?.find(
    (r) => r.code === selectedRegion
  );

  if (!regionData) {
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

  const coverage = regionData.avg_coverage_rate || 0;

  const handleExport = () => {
    if (regionsData?.regions) {
      const exportData = regionsData.regions.map(r => ({
        Região: REGION_NAMES[r.code] || r.code,
        Estados: r.state_count,
        Municípios: r.municipality_count,
        População: r.population,
        Beneficiários: r.total_beneficiaries,
        'Valor (R$)': r.total_value_brl,
        'Cobertura (%)': (r.avg_coverage_rate * 100).toFixed(1),
      }));
      exportToCSV(exportData, `regioes_${selectedProgram || 'todos'}`);
    }
  };

  return (
    <div className="bg-slate-900/50 rounded-xl border border-slate-800 p-4">
      {/* Header */}
      <div className="flex items-center gap-3 mb-4">
        <div
          className="w-10 h-10 rounded-lg flex items-center justify-center text-xl"
          style={{ backgroundColor: getCoverageColor(coverage) }}
        >
          {REGION_ICONS[selectedRegion] || '🗺️'}
        </div>
        <div className="flex-1">
          <h3 className="font-semibold">{REGION_NAMES[selectedRegion]}</h3>
          <p className="text-xs text-slate-400">
            {regionData.state_count} estados • {formatNumber(regionData.municipality_count)} municípios
          </p>
        </div>
        <button
          onClick={() => selectRegion(null)}
          className="text-slate-400 hover:text-white text-xl"
        >
          ×
        </button>
      </div>

      {/* Stats */}
      <div className="space-y-3">
        <div className="bg-slate-800/50 rounded-lg p-3">
          <div className="flex justify-between items-center mb-1">
            <span className="text-xs text-slate-400">População</span>
            <span className="text-sm font-medium">
              {formatNumber(regionData.population || 0)}
            </span>
          </div>
        </div>

        <div className="bg-slate-800/50 rounded-lg p-3">
          <div className="flex justify-between items-center mb-1">
            <span className="text-xs text-slate-400">Beneficiários</span>
            <span className="text-sm font-medium text-emerald-400">
              {formatNumber(regionData.total_beneficiaries || 0)}
            </span>
          </div>
        </div>

        <div className="bg-slate-800/50 rounded-lg p-3">
          <div className="flex justify-between items-center mb-1">
            <span className="text-xs text-slate-400">Valor Total</span>
            <span className="text-sm font-medium text-amber-400">
              R$ {formatNumber(regionData.total_value_brl || 0)}
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
      </div>

      {/* Export button */}
      <button
        onClick={handleExport}
        className="mt-4 w-full py-2 text-sm text-slate-400 hover:text-white hover:bg-slate-800 rounded-lg transition-colors flex items-center justify-center gap-2"
      >
        <span>📥</span>
        <span>Exportar CSV</span>
      </button>
    </div>
  );
}
