/**
 * Ranking panel showing top municipalities by coverage or gap
 */

import { useState } from 'react';
import { useQuery } from '@tanstack/react-query';
import { useDashboardStore } from '../../stores/dashboardStore';
import { fetchProgramRanking, RankingItem } from '../../api/client';
import { formatNumber, getCoverageColor } from '../../hooks/useGeoJSON';

type RankingType = 'coverage' | 'gap';

export default function RankingPanel() {
  const { selectedProgram, selectedState, selectMunicipality } = useDashboardStore();
  const [rankingType, setRankingType] = useState<RankingType>('coverage');

  // Use TSEE as default if no program selected
  const programCode = selectedProgram || 'TSEE';

  const { data: coverageRanking, isLoading: loadingCoverage } = useQuery({
    queryKey: ['ranking', programCode, 'coverage', selectedState],
    queryFn: () => fetchProgramRanking(programCode, 'coverage', selectedState || undefined, 10),
    enabled: rankingType === 'coverage',
  });

  const { data: gapRanking, isLoading: loadingGap } = useQuery({
    queryKey: ['ranking', programCode, 'beneficiaries', selectedState],
    queryFn: () => fetchProgramRanking(programCode, 'beneficiaries', selectedState || undefined, 10),
    enabled: rankingType === 'gap',
  });

  const isLoading = rankingType === 'coverage' ? loadingCoverage : loadingGap;
  const ranking = rankingType === 'coverage' ? coverageRanking?.ranking : gapRanking?.ranking;

  const handleMunicipalityClick = (ibgeCode: string) => {
    selectMunicipality(ibgeCode);
  };

  return (
    <div className="bg-slate-900/50 rounded-xl border border-slate-800 p-4">
      {/* Header with toggle */}
      <div className="flex items-center justify-between mb-3">
        <h3 className="font-semibold text-sm">
          Top 10 Municípios
          {selectedState && <span className="text-slate-400 ml-1">({selectedState})</span>}
        </h3>
        <div className="flex gap-1 bg-slate-800 rounded-lg p-0.5">
          <button
            onClick={() => setRankingType('coverage')}
            className={`px-2 py-1 text-xs rounded-md transition-colors ${
              rankingType === 'coverage'
                ? 'bg-emerald-600 text-white'
                : 'text-slate-400 hover:text-white'
            }`}
          >
            Cobertura
          </button>
          <button
            onClick={() => setRankingType('gap')}
            className={`px-2 py-1 text-xs rounded-md transition-colors ${
              rankingType === 'gap'
                ? 'bg-red-600 text-white'
                : 'text-slate-400 hover:text-white'
            }`}
          >
            Beneficiários
          </button>
        </div>
      </div>

      {/* Loading state */}
      {isLoading && (
        <div className="space-y-2">
          {[...Array(5)].map((_, i) => (
            <div key={i} className="h-8 bg-slate-800 rounded animate-pulse" />
          ))}
        </div>
      )}

      {/* Ranking list */}
      {!isLoading && ranking && (
        <div className="space-y-1.5">
          {ranking.map((item: RankingItem, idx: number) => (
            <button
              key={item.ibge_code}
              onClick={() => handleMunicipalityClick(item.ibge_code)}
              className="w-full flex items-center gap-2 p-2 rounded-lg bg-slate-800/50 hover:bg-slate-700/50 transition-colors text-left"
            >
              {/* Rank badge */}
              <div
                className={`w-6 h-6 rounded flex items-center justify-center text-xs font-bold ${
                  idx === 0
                    ? 'bg-amber-500 text-amber-950'
                    : idx === 1
                    ? 'bg-slate-400 text-slate-900'
                    : idx === 2
                    ? 'bg-amber-700 text-amber-100'
                    : 'bg-slate-700 text-slate-400'
                }`}
              >
                {idx + 1}
              </div>

              {/* Municipality name */}
              <div className="flex-1 min-w-0">
                <p className="text-sm truncate">{item.name}</p>
              </div>

              {/* Metric value */}
              {rankingType === 'coverage' ? (
                <div className="text-right">
                  <span
                    className="text-sm font-medium"
                    style={{ color: getCoverageColor(item.coverage_rate || 0) }}
                  >
                    {((item.coverage_rate || 0) * 100).toFixed(1)}%
                  </span>
                </div>
              ) : (
                <div className="text-right">
                  <span className="text-sm font-medium text-emerald-400">
                    {formatNumber(item.total_beneficiaries)}
                  </span>
                </div>
              )}
            </button>
          ))}
        </div>
      )}

      {/* Empty state */}
      {!isLoading && (!ranking || ranking.length === 0) && (
        <div className="text-center text-slate-500 text-sm py-4">
          <p>Sem dados disponíveis</p>
        </div>
      )}

      {/* Footer info */}
      <div className="mt-3 pt-2 border-t border-slate-800">
        <p className="text-xs text-slate-500 text-center">
          {rankingType === 'coverage'
            ? 'Ordenado por maior cobertura'
            : 'Ordenado por mais beneficiários'}
        </p>
      </div>
    </div>
  );
}
