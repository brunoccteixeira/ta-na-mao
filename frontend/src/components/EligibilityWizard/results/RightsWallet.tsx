/**
 * RightsWallet - Exibe a "Carteira de Direitos" com benefícios elegíveis
 */

import { TriagemResult, EligibilityResult } from '../types';

interface Props {
  result: TriagemResult;
  onGenerateCarta: () => void;
  onFindCras: () => void;
  onReset: () => void;
}

const STATUS_CONFIG = {
  elegivel: {
    bg: 'bg-emerald-500/10',
    border: 'border-emerald-500/30',
    icon: '🎯',
    label: 'Pode ter direito',
    labelColor: 'text-emerald-400',
  },
  ja_recebe: {
    bg: 'bg-blue-500/10',
    border: 'border-blue-500/30',
    icon: '✅',
    label: 'Já recebe',
    labelColor: 'text-blue-400',
  },
  inelegivel: {
    bg: 'bg-slate-700/50',
    border: 'border-slate-600',
    icon: '❌',
    label: 'Não elegível',
    labelColor: 'text-slate-400',
  },
  inconclusivo: {
    bg: 'bg-amber-500/10',
    border: 'border-amber-500/30',
    icon: '❓',
    label: 'Verificar',
    labelColor: 'text-amber-400',
  },
};

const PROGRAM_ICONS: Record<string, string> = {
  BOLSA_FAMILIA: '👨‍👩‍👧‍👦',
  BPC: '🧓',
  TSEE: '💡',
  FARMACIA_POPULAR: '💊',
  AUXILIO_GAS: '🔥',
  DIGNIDADE_MENSTRUAL: '🩸',
  MCMV: '🏠',
  MCMV_REFORMAS: '🔨',
  PIS_PASEP: '💰',
};

function BenefitCard({ benefit }: { benefit: EligibilityResult }) {
  const config = STATUS_CONFIG[benefit.status];
  const icon = PROGRAM_ICONS[benefit.programa] || '📋';

  return (
    <div className={`rounded-xl border overflow-hidden ${config.bg} ${config.border}`}>
      <div className="p-4">
        {/* Header */}
        <div className="flex items-start gap-3">
          <div className="w-12 h-12 rounded-full bg-slate-800 flex items-center justify-center text-2xl flex-shrink-0">
            {icon}
          </div>
          <div className="flex-1 min-w-0">
            <h4 className="font-semibold text-slate-200">{benefit.programaNome}</h4>
            <span className={`text-xs font-medium ${config.labelColor}`}>
              {config.icon} {config.label}
            </span>
          </div>
          {benefit.valorEstimado && benefit.status === 'elegivel' && (
            <div className="text-right">
              <p className="text-xs text-slate-400">até</p>
              <p className="text-lg font-bold text-emerald-400">
                R$ {benefit.valorEstimado.toFixed(0)}
              </p>
              <p className="text-xs text-slate-400">/mês</p>
            </div>
          )}
        </div>

        {/* Motivo */}
        <p className="mt-3 text-sm text-slate-400 line-clamp-2">
          {benefit.motivo}
        </p>

        {/* Onde solicitar */}
        {benefit.ondeSolicitar && benefit.status === 'elegivel' && (
          <div className="mt-3 flex items-center gap-2 text-xs text-slate-500">
            <span>📍</span>
            <span>{benefit.ondeSolicitar}</span>
          </div>
        )}
      </div>
    </div>
  );
}

export default function RightsWallet({ result, onGenerateCarta, onFindCras, onReset }: Props) {
  const totalElegiveis = result.beneficiosElegiveis.length;
  const totalJaRecebe = result.beneficiosJaRecebe.length;

  return (
    <div className="space-y-6">
      {/* Header com resumo */}
      <div className="text-center">
        {totalElegiveis > 0 ? (
          <>
            <div className="text-5xl mb-3">🎉</div>
            <h2 className="text-2xl font-bold text-slate-100">
              Você pode ter direito a {totalElegiveis} benefício{totalElegiveis > 1 ? 's' : ''}!
            </h2>
          </>
        ) : (
          <>
            <div className="text-5xl mb-3">📋</div>
            <h2 className="text-2xl font-bold text-slate-100">
              Resultado da análise
            </h2>
          </>
        )}
      </div>

      {/* Valor potencial */}
      {result.valorPotencialMensal > 0 && (
        <div className="p-5 rounded-2xl bg-gradient-to-r from-emerald-600/20 to-emerald-500/10 border border-emerald-500/30">
          <p className="text-sm text-emerald-300 mb-1">Valor potencial mensal</p>
          <p className="text-4xl font-bold text-emerald-400">
            R$ {result.valorPotencialMensal.toFixed(0)}
          </p>
          <p className="text-xs text-emerald-300/70 mt-1">
            em benefícios que você pode receber
          </p>
        </div>
      )}

      {/* Benefícios que já recebe */}
      {totalJaRecebe > 0 && (
        <div className="space-y-3">
          <h3 className="text-sm font-medium text-slate-400 uppercase tracking-wider">
            Você já recebe
          </h3>
          {result.beneficiosJaRecebe.map((b, i) => (
            <BenefitCard key={`ja-${i}`} benefit={b} />
          ))}
        </div>
      )}

      {/* Benefícios elegíveis */}
      {totalElegiveis > 0 && (
        <div className="space-y-3">
          <h3 className="text-sm font-medium text-slate-400 uppercase tracking-wider">
            Benefícios disponíveis para você
          </h3>
          {result.beneficiosElegiveis.map((b, i) => (
            <BenefitCard key={`el-${i}`} benefit={b} />
          ))}
        </div>
      )}

      {/* Inconclusivos */}
      {result.beneficiosInconclusivos.length > 0 && (
        <div className="space-y-3">
          <h3 className="text-sm font-medium text-slate-400 uppercase tracking-wider">
            Verificar presencialmente
          </h3>
          {result.beneficiosInconclusivos.map((b, i) => (
            <BenefitCard key={`inc-${i}`} benefit={b} />
          ))}
        </div>
      )}

      {/* Próximos passos */}
      {result.proximosPassosPrioritarios.length > 0 && (
        <div className="p-4 rounded-xl bg-blue-500/10 border border-blue-500/30">
          <h3 className="font-medium text-blue-300 mb-3">Próximos passos</h3>
          <ol className="space-y-2">
            {result.proximosPassosPrioritarios.map((passo, i) => (
              <li key={i} className="text-sm text-slate-300 flex gap-2">
                <span className="text-blue-400 font-medium">{i + 1}.</span>
                <span>{passo}</span>
              </li>
            ))}
          </ol>
        </div>
      )}

      {/* Documentos necessários */}
      {result.documentosNecessarios.length > 0 && (
        <div className="p-4 rounded-xl bg-slate-800/50 border border-slate-700">
          <h3 className="font-medium text-slate-300 mb-3">Documentos necessários</h3>
          <div className="flex flex-wrap gap-2">
            {result.documentosNecessarios.slice(0, 6).map((doc, i) => (
              <span key={i} className="px-3 py-1 rounded-full bg-slate-700 text-sm text-slate-300">
                📄 {doc}
              </span>
            ))}
          </div>
        </div>
      )}

      {/* Ações */}
      <div className="space-y-3">
        {totalElegiveis > 0 && (
          <>
            <button
              onClick={onGenerateCarta}
              className="w-full py-4 rounded-xl font-semibold bg-emerald-600 hover:bg-emerald-500 text-white transition-all flex items-center justify-center gap-2"
            >
              <span>📄</span>
              Gerar Carta para o CRAS
            </button>
            <button
              onClick={onFindCras}
              className="w-full py-4 rounded-xl font-semibold bg-blue-600 hover:bg-blue-500 text-white transition-all flex items-center justify-center gap-2"
            >
              <span>📍</span>
              Encontrar CRAS mais perto
            </button>
          </>
        )}
        <button
          onClick={onReset}
          className="w-full py-3 rounded-xl font-medium bg-slate-800 text-slate-300 hover:bg-slate-700 transition-all"
        >
          Fazer nova consulta
        </button>
      </div>
    </div>
  );
}
