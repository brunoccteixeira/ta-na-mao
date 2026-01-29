/**
 * BenefitCard - Renders a benefit status card
 */

import { BenefitCardData } from '../../api/chatClient';

interface Props {
  data: BenefitCardData;
}

const STATUS_CONFIG = {
  active: {
    bg: 'bg-emerald-500/10',
    border: 'border-emerald-500/30',
    icon: '✅',
    label: 'Ativo',
    labelColor: 'text-emerald-400',
  },
  eligible: {
    bg: 'bg-blue-500/10',
    border: 'border-blue-500/30',
    icon: '🎯',
    label: 'Elegível',
    labelColor: 'text-blue-400',
  },
  ineligible: {
    bg: 'bg-slate-700/50',
    border: 'border-slate-600',
    icon: '❌',
    label: 'Não elegível',
    labelColor: 'text-slate-400',
  },
  pending: {
    bg: 'bg-amber-500/10',
    border: 'border-amber-500/30',
    icon: '⏳',
    label: 'Em análise',
    labelColor: 'text-amber-400',
  },
};

const PROGRAM_ICONS: Record<string, string> = {
  bolsa_familia: '👨‍👩‍👧‍👦',
  bpc: '🧓',
  tarifa_social: '💡',
  farmacia_popular: '💊',
  auxilio_gas: '🔥',
  seguro_defeso: '🐟',
  garantia_safra: '🌾',
};

export default function BenefitCard({ data }: Props) {
  const config = STATUS_CONFIG[data.status];
  const icon = data.icon || PROGRAM_ICONS[data.code] || '📋';

  return (
    <div className={`rounded-xl border overflow-hidden ${config.bg} ${config.border}`}>
      <div className="p-4">
        {/* Header */}
        <div className="flex items-start justify-between gap-3">
          <div className="flex items-center gap-3">
            <div className="w-12 h-12 rounded-full bg-slate-800 flex items-center justify-center text-2xl">
              {icon}
            </div>
            <div>
              <h4 className="font-semibold text-slate-200">{data.name}</h4>
              <span className={`text-xs font-medium ${config.labelColor}`}>
                {config.icon} {config.label}
              </span>
            </div>
          </div>
        </div>

        {/* Value */}
        {data.value && (
          <div className="mt-4 p-3 rounded-lg bg-slate-800/50">
            <p className="text-xs text-slate-400 mb-1">Valor mensal</p>
            <p className="text-2xl font-bold text-emerald-400">{data.value}</p>
          </div>
        )}

        {/* Next payment */}
        {data.next_payment && (
          <div className="mt-3 flex items-center gap-2 text-sm text-slate-400">
            <span>📅</span>
            <span>Próximo pagamento: <strong className="text-slate-200">{data.next_payment}</strong></span>
          </div>
        )}
      </div>
    </div>
  );
}
