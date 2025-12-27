/**
 * Demographic breakdown showing income and age distribution from CadÚnico
 */

import { useState } from 'react';
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
import { useDashboardStore } from '../../stores/dashboardStore';
import { fetchDemographics } from '../../api/client';
import { formatNumber } from '../../hooks/useGeoJSON';

type ViewType = 'income' | 'age';

const INCOME_COLORS = {
  extreme_poverty: '#ef4444', // red
  poverty: '#f97316', // orange
  low_income: '#eab308', // yellow
};

const AGE_COLORS = {
  '0_5': '#8b5cf6', // purple
  '6_14': '#3b82f6', // blue
  '15_17': '#06b6d4', // cyan
  '18_64': '#10b981', // green
  '65_plus': '#f59e0b', // amber
};

export default function DemographicBreakdown() {
  const { selectedState } = useDashboardStore();
  const [viewType, setViewType] = useState<ViewType>('income');

  const { data: demographics, isLoading } = useQuery({
    queryKey: ['demographics', selectedState],
    queryFn: () => fetchDemographics(selectedState || undefined),
  });

  if (isLoading) {
    return (
      <div className="bg-slate-900/50 rounded-xl border border-slate-800 p-4">
        <div className="h-6 bg-slate-700 rounded w-1/3 mb-4 animate-pulse" />
        <div className="h-32 bg-slate-800 rounded animate-pulse" />
      </div>
    );
  }

  // Check if we have demographic data
  const hasData = demographics && (
    demographics.income_brackets.extreme_poverty > 0 ||
    demographics.income_brackets.poverty > 0 ||
    demographics.income_brackets.low_income > 0
  );

  if (!hasData) {
    return (
      <div className="bg-slate-900/50 rounded-xl border border-slate-800 p-4">
        <h3 className="font-semibold text-sm mb-3">Perfil CadÚnico</h3>
        <div className="flex items-center justify-center h-32 text-slate-500 text-sm">
          <div className="text-center">
            <div className="text-2xl mb-2">👥</div>
            <p>Dados demográficos não disponíveis</p>
            <p className="text-xs text-slate-600 mt-1">
              Aguardando ingestão de dados CadÚnico
            </p>
          </div>
        </div>
      </div>
    );
  }

  // Prepare income data
  const incomeData = [
    {
      name: 'Ext. Pobreza',
      value: demographics.income_brackets.extreme_poverty,
      color: INCOME_COLORS.extreme_poverty,
      description: '< R$105/capita',
    },
    {
      name: 'Pobreza',
      value: demographics.income_brackets.poverty,
      color: INCOME_COLORS.poverty,
      description: 'R$105-218/capita',
    },
    {
      name: 'Baixa Renda',
      value: demographics.income_brackets.low_income,
      color: INCOME_COLORS.low_income,
      description: 'até 1/2 SM',
    },
  ];

  // Prepare age data
  const ageData = [
    { name: '0-5', value: demographics.age_distribution['0_5'], color: AGE_COLORS['0_5'] },
    { name: '6-14', value: demographics.age_distribution['6_14'], color: AGE_COLORS['6_14'] },
    { name: '15-17', value: demographics.age_distribution['15_17'], color: AGE_COLORS['15_17'] },
    { name: '18-64', value: demographics.age_distribution['18_64'], color: AGE_COLORS['18_64'] },
    { name: '65+', value: demographics.age_distribution['65_plus'], color: AGE_COLORS['65_plus'] },
  ];

  const chartData = viewType === 'income' ? incomeData : ageData;

  // Format large numbers for Y axis
  const formatYAxis = (value: number) => {
    if (value >= 1000000) return `${(value / 1000000).toFixed(1)}M`;
    if (value >= 1000) return `${(value / 1000).toFixed(0)}k`;
    return value.toString();
  };

  // Custom tooltip
  const CustomTooltip = ({ active, payload }: any) => {
    if (!active || !payload || !payload.length) return null;

    const item = payload[0].payload;
    return (
      <div className="bg-slate-800 border border-slate-700 rounded-lg p-3 shadow-lg">
        <p className="text-sm font-medium text-white mb-1">{item.name}</p>
        <p className="text-xs" style={{ color: item.color }}>
          {formatNumber(item.value)} {viewType === 'income' ? 'famílias' : 'pessoas'}
        </p>
        {item.description && (
          <p className="text-xs text-slate-400 mt-1">{item.description}</p>
        )}
      </div>
    );
  };

  return (
    <div className="bg-slate-900/50 rounded-xl border border-slate-800 p-4">
      {/* Header with toggle */}
      <div className="flex items-center justify-between mb-3">
        <h3 className="font-semibold text-sm">
          Perfil CadÚnico
          {selectedState && <span className="text-slate-400 ml-1">({selectedState})</span>}
        </h3>
        <div className="flex gap-1 bg-slate-800 rounded-lg p-0.5">
          <button
            onClick={() => setViewType('income')}
            className={`px-2 py-1 text-xs rounded-md transition-colors ${
              viewType === 'income'
                ? 'bg-orange-600 text-white'
                : 'text-slate-400 hover:text-white'
            }`}
          >
            Renda
          </button>
          <button
            onClick={() => setViewType('age')}
            className={`px-2 py-1 text-xs rounded-md transition-colors ${
              viewType === 'age'
                ? 'bg-purple-600 text-white'
                : 'text-slate-400 hover:text-white'
            }`}
          >
            Idade
          </button>
        </div>
      </div>

      {/* Chart */}
      <div className="h-32">
        <ResponsiveContainer width="100%" height="100%">
          <BarChart data={chartData} margin={{ top: 5, right: 5, left: 0, bottom: 5 }}>
            <XAxis
              dataKey="name"
              tick={{ fill: '#64748b', fontSize: 9 }}
              tickLine={false}
              axisLine={{ stroke: '#334155' }}
            />
            <YAxis
              tickFormatter={formatYAxis}
              tick={{ fill: '#64748b', fontSize: 9 }}
              tickLine={false}
              axisLine={false}
              width={40}
            />
            <Tooltip content={<CustomTooltip />} />
            <Bar dataKey="value" radius={[4, 4, 0, 0]}>
              {chartData.map((entry, index) => (
                <Cell key={`cell-${index}`} fill={entry.color} />
              ))}
            </Bar>
          </BarChart>
        </ResponsiveContainer>
      </div>

      {/* Summary */}
      <div className="mt-2 pt-2 border-t border-slate-800 flex justify-between text-xs text-slate-500">
        <span>{formatNumber(demographics.total_families)} famílias</span>
        <span>{formatNumber(demographics.total_persons)} pessoas</span>
      </div>
    </div>
  );
}
