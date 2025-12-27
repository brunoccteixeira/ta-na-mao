/**
 * Program comparison chart showing all programs side by side
 */

import { useQuery } from '@tanstack/react-query';
import {
  BarChart,
  Bar,
  XAxis,
  YAxis,
  Tooltip,
  ResponsiveContainer,
  Cell,
} from 'recharts';
import { fetchPrograms, exportToCSV } from '../../api/client';
import { formatNumber } from '../../hooks/useGeoJSON';

const PROGRAM_COLORS: Record<string, string> = {
  TSEE: '#10b981',
  FARMACIA_POPULAR: '#3b82f6',
  DIGNIDADE_MENSTRUAL: '#ec4899',
  BPC: '#f59e0b',
  PIS_PASEP: '#8b5cf6',
};

const PROGRAM_LABELS: Record<string, string> = {
  TSEE: 'TSEE',
  FARMACIA_POPULAR: 'Farmácia',
  DIGNIDADE_MENSTRUAL: 'Dignidade',
  BPC: 'BPC',
  PIS_PASEP: 'PIS/PASEP',
};

export default function ProgramComparison() {
  const { data: programs, isLoading } = useQuery({
    queryKey: ['programs'],
    queryFn: fetchPrograms,
  });

  if (isLoading) {
    return (
      <div className="bg-slate-900/50 rounded-xl border border-slate-800 p-4">
        <div className="h-6 bg-slate-700 rounded w-1/3 mb-4 animate-pulse" />
        <div className="h-48 bg-slate-800 rounded animate-pulse" />
      </div>
    );
  }

  // Filter programs with data and prepare chart data
  const chartData = (programs || [])
    .filter(p => p.national_stats && p.national_stats.total_beneficiaries > 0)
    .map(p => ({
      code: p.code,
      name: PROGRAM_LABELS[p.code] || p.code,
      beneficiaries: p.national_stats?.total_beneficiaries || 0,
      value: p.national_stats?.total_value_brl || 0,
      color: PROGRAM_COLORS[p.code] || '#64748b',
    }))
    .sort((a, b) => b.beneficiaries - a.beneficiaries);

  if (chartData.length === 0) {
    return (
      <div className="bg-slate-900/50 rounded-xl border border-slate-800 p-4">
        <h3 className="font-semibold text-sm mb-3">Comparativo de Programas</h3>
        <div className="flex items-center justify-center h-32 text-slate-500 text-sm">
          <p>Sem dados disponíveis</p>
        </div>
      </div>
    );
  }

  // Format large numbers for Y axis
  const formatYAxis = (value: number) => {
    if (value >= 1000000) return `${(value / 1000000).toFixed(0)}M`;
    if (value >= 1000) return `${(value / 1000).toFixed(0)}k`;
    return value.toString();
  };

  // Custom tooltip
  const CustomTooltip = ({ active, payload }: any) => {
    if (!active || !payload || !payload.length) return null;

    const item = payload[0].payload;
    return (
      <div className="bg-slate-800 border border-slate-700 rounded-lg p-3 shadow-lg">
        <p className="text-sm font-medium text-white mb-2">{item.name}</p>
        <div className="space-y-1 text-xs">
          <p className="text-emerald-400">
            Beneficiários: {formatNumber(item.beneficiaries)}
          </p>
          <p className="text-amber-400">
            Valor: R$ {formatNumber(item.value)}
          </p>
        </div>
      </div>
    );
  };

  const handleExport = () => {
    const exportData = chartData.map(p => ({
      Programa: p.name,
      Beneficiários: p.beneficiaries,
      'Valor (R$)': p.value,
    }));
    exportToCSV(exportData, 'comparativo_programas');
  };

  return (
    <div className="bg-slate-900/50 rounded-xl border border-slate-800 p-4">
      <div className="flex items-center justify-between mb-3">
        <h3 className="font-semibold text-sm">Comparativo de Programas</h3>
        <button
          onClick={handleExport}
          className="text-xs text-slate-400 hover:text-white px-2 py-1 rounded hover:bg-slate-700 transition-colors"
          title="Exportar CSV"
        >
          📥
        </button>
      </div>

      <div className="h-48">
        <ResponsiveContainer width="100%" height="100%">
          <BarChart data={chartData} layout="vertical" margin={{ top: 5, right: 5, left: 60, bottom: 5 }}>
            <XAxis
              type="number"
              tickFormatter={formatYAxis}
              tick={{ fill: '#64748b', fontSize: 10 }}
              tickLine={false}
              axisLine={{ stroke: '#334155' }}
            />
            <YAxis
              type="category"
              dataKey="name"
              tick={{ fill: '#94a3b8', fontSize: 11 }}
              tickLine={false}
              axisLine={false}
              width={55}
            />
            <Tooltip content={<CustomTooltip />} />
            <Bar dataKey="beneficiaries" radius={[0, 4, 4, 0]}>
              {chartData.map((entry, index) => (
                <Cell key={`cell-${index}`} fill={entry.color} />
              ))}
            </Bar>
          </BarChart>
        </ResponsiveContainer>
      </div>

      {/* Legend */}
      <div className="mt-3 pt-2 border-t border-slate-800 grid grid-cols-2 gap-2">
        {chartData.slice(0, 4).map((p) => (
          <div key={p.code} className="flex items-center gap-2 text-xs">
            <div
              className="w-3 h-3 rounded"
              style={{ backgroundColor: p.color }}
            />
            <span className="text-slate-400 truncate">{p.name}</span>
          </div>
        ))}
      </div>
    </div>
  );
}
