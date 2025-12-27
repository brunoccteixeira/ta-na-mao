/**
 * National summary KPI cards
 */

import { useQuery } from '@tanstack/react-query';
import { fetchNationalAggregation } from '../../api/client';
import { useDashboardStore } from '../../stores/dashboardStore';
import { formatNumber } from '../../hooks/useGeoJSON';

export default function NationalSummary() {
  const { selectedProgram } = useDashboardStore();

  const { data, isLoading } = useQuery({
    queryKey: ['aggregation', 'national', selectedProgram],
    queryFn: () => fetchNationalAggregation(selectedProgram || undefined),
  });

  if (isLoading) {
    return (
      <div className="grid grid-cols-5 gap-2">
        {[...Array(5)].map((_, i) => (
          <div key={i} className="bg-slate-900/50 rounded-lg p-3 border border-slate-800 animate-pulse">
            <div className="h-3 bg-slate-700 rounded w-1/2 mb-2"></div>
            <div className="h-6 bg-slate-700 rounded w-3/4"></div>
          </div>
        ))}
      </div>
    );
  }

  const stats = data?.program_stats || {};
  const avgCoverage = stats.avg_coverage_rate ? (stats.avg_coverage_rate * 100).toFixed(0) : '0';
  const gap = stats.total_beneficiaries && data?.cadunico_families
    ? data.cadunico_families - stats.total_beneficiaries
    : 0;

  return (
    <div className="grid grid-cols-5 gap-2">
      <div className="bg-slate-900/50 rounded-lg p-3 border border-slate-800">
        <div className="text-slate-400 text-xs">🇧🇷 População</div>
        <div className="text-lg font-bold">{formatNumber(data?.population || 0)}</div>
      </div>
      <div className="bg-slate-900/50 rounded-lg p-3 border border-slate-800">
        <div className="text-slate-400 text-xs">📋 CadÚnico</div>
        <div className="text-lg font-bold text-blue-400">
          {formatNumber(data?.cadunico_families || 0)}
        </div>
      </div>
      <div className="bg-slate-900/50 rounded-lg p-3 border border-slate-800">
        <div className="text-slate-400 text-xs">👥 Beneficiários</div>
        <div className="text-lg font-bold text-emerald-400">
          {formatNumber(stats.total_beneficiaries || 0)}
        </div>
      </div>
      <div className="bg-slate-900/50 rounded-lg p-3 border border-slate-800">
        <div className="text-slate-400 text-xs">📈 Cobertura</div>
        <div className="text-lg font-bold text-yellow-400">{avgCoverage}%</div>
      </div>
      <div className="bg-slate-900/50 rounded-lg p-3 border border-slate-800">
        <div className="text-slate-400 text-xs">🎯 Gap</div>
        <div className="text-lg font-bold text-red-400">{formatNumber(gap)}</div>
      </div>
    </div>
  );
}
