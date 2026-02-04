'use client';

/**
 * Penetration rates table for admin view
 * Shows detailed coverage data for all municipalities with pagination
 */

import { useState } from 'react';
import { useQuery } from '@tanstack/react-query';
import { fetchPenetrationData, PenetrationData } from '../../api/client';
import { useDashboardStore } from '../../stores/dashboardStore';

const formatNumber = (num: number): string => {
  if (num >= 1_000_000) return `${(num / 1_000_000).toFixed(1)}M`;
  if (num >= 1_000) return `${(num / 1_000).toFixed(1)}K`;
  return num.toLocaleString('pt-BR');
};

const formatCurrency = (num: number): string => {
  if (num >= 1_000_000_000) return `R$ ${(num / 1_000_000_000).toFixed(1)}B`;
  if (num >= 1_000_000) return `R$ ${(num / 1_000_000).toFixed(1)}M`;
  if (num >= 1_000) return `R$ ${(num / 1_000).toFixed(0)}K`;
  return `R$ ${num.toFixed(0)}`;
};

const getCoverageBadge = (coverage: number): { bg: string; text: string } => {
  if (coverage >= 70) return { bg: 'bg-emerald-500/20', text: 'text-emerald-400' };
  if (coverage >= 40) return { bg: 'bg-yellow-500/20', text: 'text-yellow-400' };
  if (coverage >= 20) return { bg: 'bg-orange-500/20', text: 'text-orange-400' };
  return { bg: 'bg-red-500/20', text: 'text-red-400' };
};

export default function PenetrationTable() {
  const { selectedProgram, selectedState } = useDashboardStore();
  const [page, setPage] = useState(0);
  const [orderBy, setOrderBy] = useState<string>('coverage');
  const [orderDir, setOrderDir] = useState<'asc' | 'desc'>('asc');
  const pageSize = 25;

  const { data, isLoading, error } = useQuery({
    queryKey: ['penetration', selectedProgram, selectedState, page, orderBy, orderDir],
    queryFn: () =>
      fetchPenetrationData({
        program: selectedProgram || undefined,
        state_code: selectedState || undefined,
        order_by: orderBy,
        order_dir: orderDir,
        limit: pageSize,
        offset: page * pageSize,
      }),
  });

  const handleSort = (column: string) => {
    if (orderBy === column) {
      setOrderDir(orderDir === 'asc' ? 'desc' : 'asc');
    } else {
      setOrderBy(column);
      setOrderDir(column === 'coverage' ? 'asc' : 'desc');
    }
    setPage(0);
  };

  const SortIcon = ({ column }: { column: string }) => {
    if (orderBy !== column) return <span className="text-slate-600 ml-1">-</span>;
    return <span className="ml-1">{orderDir === 'asc' ? '\u2191' : '\u2193'}</span>;
  };

  if (isLoading) {
    return (
      <div className="bg-slate-900/50 rounded-xl border border-slate-800 p-4">
        <div className="animate-pulse space-y-2">
          {[...Array(10)].map((_, i) => (
            <div key={i} className="h-8 bg-slate-800 rounded" />
          ))}
        </div>
      </div>
    );
  }

  if (error) {
    return (
      <div className="bg-slate-900/50 rounded-xl border border-slate-800 p-4 text-red-400">
        Erro ao carregar dados de penetracao
      </div>
    );
  }

  const municipalities = data?.data || [];
  const totalCount = data?.total_count || 0;
  const totalPages = Math.ceil(totalCount / pageSize);

  return (
    <div className="bg-slate-900/50 rounded-xl border border-slate-800 overflow-hidden">
      {/* Header */}
      <div className="p-4 border-b border-slate-800 flex items-center justify-between">
        <h3 className="font-semibold">Taxa de Penetracao por Municipio</h3>
        <span className="text-sm text-slate-400">
          {totalCount.toLocaleString('pt-BR')} municipios
        </span>
      </div>

      {/* Table */}
      <div className="overflow-x-auto">
        <table className="w-full text-sm">
          <thead className="bg-slate-800/50">
            <tr>
              <th className="text-left p-3 font-medium text-slate-400">
                <button onClick={() => handleSort('name')} className="flex items-center hover:text-white">
                  Municipio <SortIcon column="name" />
                </button>
              </th>
              <th className="text-left p-3 font-medium text-slate-400 w-16">UF</th>
              <th className="text-right p-3 font-medium text-slate-400">
                <button onClick={() => handleSort('population')} className="flex items-center justify-end hover:text-white">
                  Pop <SortIcon column="population" />
                </button>
              </th>
              <th className="text-right p-3 font-medium text-slate-400">
                <button onClick={() => handleSort('beneficiaries')} className="flex items-center justify-end hover:text-white">
                  Benef <SortIcon column="beneficiaries" />
                </button>
              </th>
              <th className="text-right p-3 font-medium text-slate-400">
                <button onClick={() => handleSort('coverage')} className="flex items-center justify-end hover:text-white">
                  Cobertura <SortIcon column="coverage" />
                </button>
              </th>
              <th className="text-right p-3 font-medium text-slate-400">
                <button onClick={() => handleSort('gap')} className="flex items-center justify-end hover:text-white">
                  Gap <SortIcon column="gap" />
                </button>
              </th>
              <th className="text-right p-3 font-medium text-slate-400">
                <button onClick={() => handleSort('value')} className="flex items-center justify-end hover:text-white">
                  Valor <SortIcon column="value" />
                </button>
              </th>
            </tr>
          </thead>
          <tbody className="divide-y divide-slate-800">
            {municipalities.map((mun: PenetrationData) => {
              const badge = getCoverageBadge(mun.coverage_rate);
              return (
                <tr key={mun.ibge_code} className="hover:bg-slate-800/50 transition-colors">
                  <td className="p-3">
                    <div className="flex items-center gap-2">
                      <span
                        className={`w-2 h-2 rounded-full ${
                          mun.coverage_rate < 20
                            ? 'bg-red-500'
                            : mun.coverage_rate < 40
                            ? 'bg-orange-500'
                            : mun.coverage_rate < 70
                            ? 'bg-yellow-500'
                            : 'bg-emerald-500'
                        }`}
                      />
                      <span className="truncate max-w-[200px]">{mun.municipality}</span>
                    </div>
                  </td>
                  <td className="p-3 text-slate-400">{mun.state}</td>
                  <td className="p-3 text-right">{formatNumber(mun.population)}</td>
                  <td className="p-3 text-right text-emerald-400">{formatNumber(mun.total_beneficiaries)}</td>
                  <td className="p-3 text-right">
                    <span className={`px-2 py-0.5 rounded ${badge.bg} ${badge.text}`}>
                      {mun.coverage_rate.toFixed(1)}%
                    </span>
                  </td>
                  <td className="p-3 text-right text-red-400">
                    {mun.gap > 0 ? formatNumber(mun.gap) : '-'}
                  </td>
                  <td className="p-3 text-right text-slate-400">{formatCurrency(mun.total_value_brl)}</td>
                </tr>
              );
            })}
          </tbody>
        </table>
      </div>

      {/* Pagination */}
      <div className="p-4 border-t border-slate-800 flex items-center justify-between">
        <span className="text-sm text-slate-400">
          Mostrando {page * pageSize + 1}-{Math.min((page + 1) * pageSize, totalCount)} de {totalCount}
        </span>
        <div className="flex gap-2">
          <button
            onClick={() => setPage(Math.max(0, page - 1))}
            disabled={page === 0}
            className="px-3 py-1.5 text-sm rounded bg-slate-800 hover:bg-slate-700 disabled:opacity-50 disabled:cursor-not-allowed transition-colors"
          >
            Anterior
          </button>
          <span className="px-3 py-1.5 text-sm text-slate-400">
            Pagina {page + 1} de {totalPages || 1}
          </span>
          <button
            onClick={() => setPage(Math.min(totalPages - 1, page + 1))}
            disabled={page >= totalPages - 1}
            className="px-3 py-1.5 text-sm rounded bg-slate-800 hover:bg-slate-700 disabled:opacity-50 disabled:cursor-not-allowed transition-colors"
          >
            Proximo
          </button>
        </div>
      </div>
    </div>
  );
}
