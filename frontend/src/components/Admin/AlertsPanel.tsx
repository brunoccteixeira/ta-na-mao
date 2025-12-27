/**
 * Coverage alerts panel for admin view
 * Shows municipalities with low coverage rates
 */

import { useQuery } from '@tanstack/react-query';
import { fetchAlerts } from '../../api/client';
import { useDashboardStore } from '../../stores/dashboardStore';

const formatNumber = (num: number): string => {
  if (num >= 1_000_000) return `${(num / 1_000_000).toFixed(1)}M`;
  if (num >= 1_000) return `${(num / 1_000).toFixed(1)}K`;
  return num.toLocaleString('pt-BR');
};

export default function AlertsPanel() {
  const { selectedProgram, selectedState } = useDashboardStore();

  const { data, isLoading, error } = useQuery({
    queryKey: ['alerts', selectedProgram, selectedState],
    queryFn: () =>
      fetchAlerts({
        program: selectedProgram || undefined,
        state_code: selectedState || undefined,
        limit: 50,
      }),
    refetchInterval: 60000, // Refresh every minute
  });

  if (isLoading) {
    return (
      <div className="bg-slate-900/50 rounded-xl border border-slate-800 p-4">
        <div className="animate-pulse space-y-2">
          {[...Array(3)].map((_, i) => (
            <div key={i} className="h-12 bg-slate-800 rounded" />
          ))}
        </div>
      </div>
    );
  }

  if (error) {
    return (
      <div className="bg-slate-900/50 rounded-xl border border-slate-800 p-4 text-red-400 text-sm">
        Erro ao carregar alertas
      </div>
    );
  }

  const summary = data?.summary;
  const alerts = data?.alerts || [];
  const criticalAlerts = alerts.filter((a) => a.type === 'critical');
  const warningAlerts = alerts.filter((a) => a.type === 'warning');

  return (
    <div className="bg-slate-900/50 rounded-xl border border-slate-800 overflow-hidden">
      {/* Header */}
      <div className="p-4 border-b border-slate-800">
        <h3 className="font-semibold flex items-center gap-2">
          <span className="w-2 h-2 rounded-full bg-red-500 animate-pulse" />
          Alertas de Cobertura
        </h3>
      </div>

      {/* Summary Stats */}
      <div className="grid grid-cols-2 gap-2 p-4 border-b border-slate-800">
        <div className="bg-red-500/10 rounded-lg p-3 text-center">
          <div className="text-2xl font-bold text-red-400">{summary?.critical_count || 0}</div>
          <div className="text-xs text-red-400/70">Criticos (&lt;{summary?.thresholds?.critical || 20}%)</div>
        </div>
        <div className="bg-orange-500/10 rounded-lg p-3 text-center">
          <div className="text-2xl font-bold text-orange-400">{summary?.warning_count || 0}</div>
          <div className="text-xs text-orange-400/70">Alertas ({summary?.thresholds?.critical || 20}-{summary?.thresholds?.warning || 40}%)</div>
        </div>
      </div>

      {/* Biggest Gap */}
      {summary?.biggest_gap && (
        <div className="p-4 border-b border-slate-800 bg-slate-800/30">
          <div className="text-xs text-slate-400 mb-1">Maior Gap</div>
          <div className="flex items-center justify-between">
            <span className="font-medium">
              {summary.biggest_gap.municipality} ({summary.biggest_gap.state})
            </span>
            <span className="text-red-400 font-bold">{formatNumber(summary.biggest_gap.gap)}</span>
          </div>
        </div>
      )}

      {/* Critical Alerts List */}
      {criticalAlerts.length > 0 && (
        <div className="p-4 border-b border-slate-800">
          <div className="text-xs text-red-400 mb-2 font-medium uppercase">Criticos</div>
          <div className="space-y-2 max-h-[200px] overflow-y-auto">
            {criticalAlerts.slice(0, 10).map((alert) => (
              <div
                key={alert.ibge_code}
                className="flex items-center justify-between p-2 bg-red-500/10 rounded-lg text-sm"
              >
                <div className="flex items-center gap-2">
                  <span className="w-2 h-2 rounded-full bg-red-500" />
                  <span className="truncate max-w-[150px]">
                    {alert.municipality} ({alert.state})
                  </span>
                </div>
                <span className="text-red-400 font-medium">{alert.coverage_rate.toFixed(1)}%</span>
              </div>
            ))}
          </div>
        </div>
      )}

      {/* Warning Alerts List */}
      {warningAlerts.length > 0 && (
        <div className="p-4">
          <div className="text-xs text-orange-400 mb-2 font-medium uppercase">Alertas</div>
          <div className="space-y-2 max-h-[150px] overflow-y-auto">
            {warningAlerts.slice(0, 5).map((alert) => (
              <div
                key={alert.ibge_code}
                className="flex items-center justify-between p-2 bg-orange-500/10 rounded-lg text-sm"
              >
                <div className="flex items-center gap-2">
                  <span className="w-2 h-2 rounded-full bg-orange-500" />
                  <span className="truncate max-w-[150px]">
                    {alert.municipality} ({alert.state})
                  </span>
                </div>
                <span className="text-orange-400 font-medium">{alert.coverage_rate.toFixed(1)}%</span>
              </div>
            ))}
          </div>
          {warningAlerts.length > 5 && (
            <div className="text-xs text-slate-500 text-center mt-2">
              +{warningAlerts.length - 5} outros alertas
            </div>
          )}
        </div>
      )}

      {/* No Alerts */}
      {alerts.length === 0 && (
        <div className="p-8 text-center text-slate-500">
          <div className="text-3xl mb-2">OK</div>
          <div className="text-sm">Sem alertas criticos</div>
        </div>
      )}
    </div>
  );
}
