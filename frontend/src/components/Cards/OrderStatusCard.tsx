/**
 * OrderStatusCard - Renders medication order status
 */

import { OrderStatusData } from '../../api/chatClient';

interface Props {
  data: OrderStatusData;
}

const STATUS_LABELS: Record<OrderStatusData['status'], { label: string; color: string }> = {
  pending: { label: 'Aguardando', color: 'text-amber-400' },
  confirmed: { label: 'Confirmado', color: 'text-blue-400' },
  preparing: { label: 'Preparando', color: 'text-purple-400' },
  ready: { label: 'Pronto!', color: 'text-emerald-400' },
  delivered: { label: 'Entregue', color: 'text-slate-400' },
};

export default function OrderStatusCard({ data }: Props) {
  const statusConfig = STATUS_LABELS[data.status];
  const completedSteps = data.steps.filter(s => s.done).length;
  const progress = (completedSteps / data.steps.length) * 100;

  return (
    <div className="bg-slate-800/50 rounded-xl border border-slate-700 overflow-hidden">
      {/* Header */}
      <div className="bg-gradient-to-r from-indigo-600 to-purple-600 px-4 py-3">
        <div className="flex items-center justify-between">
          <div>
            <h3 className="font-semibold text-white flex items-center gap-2">
              <span className="text-lg">📦</span>
              Pedido {data.order_number}
            </h3>
            <p className="text-xs text-indigo-100">{data.pharmacy}</p>
          </div>
          <span className={`px-3 py-1 rounded-full bg-white/20 text-sm font-medium ${statusConfig.color}`}>
            {statusConfig.label}
          </span>
        </div>
      </div>

      <div className="p-4">
        {/* Progress bar */}
        <div className="mb-4">
          <div className="h-2 bg-slate-700 rounded-full overflow-hidden">
            <div
              className="h-full bg-gradient-to-r from-indigo-500 to-purple-500 transition-all duration-500"
              style={{ width: `${progress}%` }}
            />
          </div>
        </div>

        {/* Steps */}
        <div className="space-y-3">
          {data.steps.map((step, index) => (
            <div key={index} className="flex items-center gap-3">
              {/* Step indicator */}
              <div className={`w-6 h-6 rounded-full flex items-center justify-center flex-shrink-0 ${
                step.done
                  ? 'bg-emerald-500'
                  : index === completedSteps
                    ? 'bg-indigo-500 animate-pulse'
                    : 'bg-slate-700'
              }`}>
                {step.done ? (
                  <svg className="w-3 h-3 text-white" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                    <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={3} d="M5 13l4 4L19 7" />
                  </svg>
                ) : (
                  <span className="w-2 h-2 rounded-full bg-slate-500" />
                )}
              </div>

              {/* Step label */}
              <span className={`text-sm ${
                step.done
                  ? 'text-slate-300'
                  : index === completedSteps
                    ? 'text-indigo-400 font-medium'
                    : 'text-slate-500'
              }`}>
                {step.label}
              </span>
            </div>
          ))}
        </div>

        {/* Estimated time */}
        {data.estimated_ready && data.status !== 'ready' && data.status !== 'delivered' && (
          <div className="mt-4 p-3 rounded-lg bg-indigo-500/10 border border-indigo-500/30">
            <p className="text-sm text-indigo-300 flex items-center gap-2">
              <span>⏱️</span>
              Previsão: <strong>{data.estimated_ready}</strong>
            </p>
          </div>
        )}

        {/* Ready message */}
        {data.status === 'ready' && (
          <div className="mt-4 p-3 rounded-lg bg-emerald-500/10 border border-emerald-500/30">
            <p className="text-sm text-emerald-300 flex items-center gap-2">
              <span>🎉</span>
              Seu pedido está pronto para retirada!
            </p>
          </div>
        )}
      </div>
    </div>
  );
}
