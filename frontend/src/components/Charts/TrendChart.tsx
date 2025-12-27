/**
 * Time-series trend chart showing beneficiaries over time
 */

import { useQuery } from '@tanstack/react-query';
import {
  AreaChart,
  Area,
  XAxis,
  YAxis,
  CartesianGrid,
  Tooltip,
  ResponsiveContainer,
} from 'recharts';
import { useDashboardStore } from '../../stores/dashboardStore';
import { fetchTimeSeries } from '../../api/client';
import { formatNumber } from '../../hooks/useGeoJSON';

export default function TrendChart() {
  const { selectedProgram, selectedState } = useDashboardStore();

  const { data: timeSeriesData, isLoading } = useQuery({
    queryKey: ['timeSeries', selectedProgram, selectedState],
    queryFn: () => fetchTimeSeries(selectedProgram || undefined, selectedState || undefined),
  });

  if (isLoading) {
    return (
      <div className="bg-slate-900/50 rounded-xl border border-slate-800 p-4">
        <div className="h-6 bg-slate-700 rounded w-1/3 mb-4 animate-pulse" />
        <div className="h-40 bg-slate-800 rounded animate-pulse" />
      </div>
    );
  }

  const data = timeSeriesData?.data || [];

  // If no data or only one point, show a message
  if (data.length < 2) {
    return (
      <div className="bg-slate-900/50 rounded-xl border border-slate-800 p-4">
        <h3 className="font-semibold text-sm mb-3">Tendência Temporal</h3>
        <div className="flex items-center justify-center h-40 text-slate-500 text-sm">
          <div className="text-center">
            <div className="text-2xl mb-2">📈</div>
            <p>Dados históricos insuficientes</p>
            <p className="text-xs text-slate-600 mt-1">
              {data.length === 1
                ? `Apenas ${data[0].month} disponível`
                : 'Aguardando ingestão de dados históricos'}
            </p>
          </div>
        </div>
      </div>
    );
  }

  // Format large numbers for Y axis
  const formatYAxis = (value: number) => {
    if (value >= 1000000) return `${(value / 1000000).toFixed(1)}M`;
    if (value >= 1000) return `${(value / 1000).toFixed(0)}k`;
    return value.toString();
  };

  // Custom tooltip
  const CustomTooltip = ({ active, payload }: any) => {
    if (!active || !payload || !payload.length) return null;

    const point = payload[0].payload;
    return (
      <div className="bg-slate-800 border border-slate-700 rounded-lg p-3 shadow-lg">
        <p className="text-sm font-medium text-white mb-2">{point.month}</p>
        <div className="space-y-1 text-xs">
          <p className="text-emerald-400">
            Beneficiários: {formatNumber(point.total_beneficiaries)}
          </p>
          <p className="text-amber-400">
            Valor: R$ {formatNumber(point.total_value_brl)}
          </p>
          <p className="text-sky-400">
            Cobertura: {(point.avg_coverage_rate * 100).toFixed(1)}%
          </p>
        </div>
      </div>
    );
  };

  return (
    <div className="bg-slate-900/50 rounded-xl border border-slate-800 p-4">
      <div className="flex items-center justify-between mb-3">
        <h3 className="font-semibold text-sm">Tendência Temporal</h3>
        <span className="text-xs text-slate-500">{data.length} meses</span>
      </div>

      <div className="h-40">
        <ResponsiveContainer width="100%" height="100%">
          <AreaChart data={data} margin={{ top: 5, right: 5, left: 0, bottom: 5 }}>
            <defs>
              <linearGradient id="beneficiariesGradient" x1="0" y1="0" x2="0" y2="1">
                <stop offset="5%" stopColor="#10b981" stopOpacity={0.3} />
                <stop offset="95%" stopColor="#10b981" stopOpacity={0} />
              </linearGradient>
            </defs>
            <CartesianGrid strokeDasharray="3 3" stroke="#334155" vertical={false} />
            <XAxis
              dataKey="month"
              tick={{ fill: '#64748b', fontSize: 10 }}
              tickLine={false}
              axisLine={{ stroke: '#334155' }}
            />
            <YAxis
              tickFormatter={formatYAxis}
              tick={{ fill: '#64748b', fontSize: 10 }}
              tickLine={false}
              axisLine={false}
              width={45}
            />
            <Tooltip content={<CustomTooltip />} />
            <Area
              type="monotone"
              dataKey="total_beneficiaries"
              stroke="#10b981"
              strokeWidth={2}
              fill="url(#beneficiariesGradient)"
            />
          </AreaChart>
        </ResponsiveContainer>
      </div>
    </div>
  );
}
