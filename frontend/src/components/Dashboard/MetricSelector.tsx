/**
 * Metric selector for map choropleth coloring
 */

import { useDashboardStore, MetricType } from '../../stores/dashboardStore';

const METRICS = [
  { code: 'coverage' as MetricType, label: 'Cobertura', icon: '📊' },
  { code: 'beneficiaries' as MetricType, label: 'Beneficiários', icon: '👥' },
  { code: 'gap' as MetricType, label: 'Gap', icon: '📉' },
  { code: 'value' as MetricType, label: 'Valor (R$)', icon: '💰' },
];

export default function MetricSelector() {
  const { selectedMetric, setMetric } = useDashboardStore();

  return (
    <div className="flex items-center gap-1 text-xs">
      <span className="text-slate-500 mr-1">Métrica:</span>
      {METRICS.map((metric) => (
        <button
          key={metric.code}
          onClick={() => setMetric(metric.code)}
          className={`px-2 py-1 rounded transition-colors ${
            selectedMetric === metric.code
              ? 'bg-slate-700 text-white'
              : 'text-slate-400 hover:text-white hover:bg-slate-800'
          }`}
          title={metric.label}
        >
          <span className="mr-1">{metric.icon}</span>
          <span className="hidden sm:inline">{metric.label}</span>
        </button>
      ))}
    </div>
  );
}
