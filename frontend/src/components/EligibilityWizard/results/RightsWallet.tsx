/**
 * RightsWallet - Exibe a "Carteira de Direitos" com benefícios elegíveis
 * Agrupa por categoria: Federal, Estadual, Setorial
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
    labelColor: 'text-emerald-600',
  },
  ja_recebe: {
    bg: 'bg-blue-500/10',
    border: 'border-blue-500/30',
    icon: '✅',
    label: 'Já recebe',
    labelColor: 'text-blue-600',
  },
  inelegivel: {
    bg: 'bg-[var(--badge-bg)]',
    border: 'border-[var(--border-color)]',
    icon: '❌',
    label: 'Não elegível',
    labelColor: 'text-[var(--text-tertiary)]',
  },
  inconclusivo: {
    bg: 'bg-amber-500/10',
    border: 'border-amber-500/30',
    icon: '❓',
    label: 'Verificar',
    labelColor: 'text-amber-600',
  },
};

const PROGRAM_ICONS: Record<string, string> = {
  BOLSA_FAMILIA: '👨‍👩‍👧‍👦',
  BPC: '🧓',
  BPC_IDOSO: '👴',
  BPC_PCD: '♿',
  TSEE: '💡',
  FARMACIA_POPULAR: '💊',
  AUXILIO_GAS: '🔥',
  DIGNIDADE_MENSTRUAL: '🩸',
  MCMV: '🏠',
  MCMV_REFORMAS: '🔨',
  PIS_PASEP: '💰',
  SVR: '🏦',
  FGTS: '📋',
  SEGURO_DESEMPREGO: '🛡️',
  ABONO_SALARIAL: '💵',
  TARIFA_SOCIAL_AGUA: '💧',
  ISENCAO_IPVA: '🚗',
  PASSE_LIVRE: '🚌',
};

// Categorias para agrupar benefícios
const BENEFIT_CATEGORIES: Record<string, { label: string; icon: string; color: string }> = {
  federal: {
    label: 'Benefícios Federais',
    icon: '🇧🇷',
    color: 'from-blue-600/15 to-blue-500/5 border-blue-500/30',
  },
  estadual: {
    label: 'Benefícios Estaduais',
    icon: '🏛️',
    color: 'from-purple-600/15 to-purple-500/5 border-purple-500/30',
  },
  municipal: {
    label: 'Benefícios Municipais',
    icon: '🏘️',
    color: 'from-cyan-600/15 to-cyan-500/5 border-cyan-500/30',
  },
  setorial: {
    label: 'Benefícios Setoriais',
    icon: '👷',
    color: 'from-amber-600/15 to-amber-500/5 border-amber-500/30',
  },
};

// Detecta categoria do benefício baseado no código do programa
function getBenefitCategory(programa: string): 'federal' | 'estadual' | 'municipal' | 'setorial' {
  const federalPrograms = [
    'BOLSA_FAMILIA', 'BPC', 'BPC_IDOSO', 'BPC_PCD', 'TSEE', 'FARMACIA_POPULAR',
    'AUXILIO_GAS', 'DIGNIDADE_MENSTRUAL', 'MCMV', 'PIS_PASEP', 'SVR', 'FGTS',
    'SEGURO_DESEMPREGO', 'ABONO_SALARIAL', 'TARIFA_SOCIAL_AGUA', 'ISENCAO_IPVA', 'PASSE_LIVRE'
  ];

  const setorialPrograms = [
    'SEGURO_DEFESO', 'PRONAF', 'GARANTIA_SAFRA', 'PAA', 'HABITACAO_RURAL',
    'BOLSA_RECICLAGEM', 'AUXILIO_INCLUSAO'
  ];

  if (federalPrograms.includes(programa)) return 'federal';
  if (setorialPrograms.includes(programa)) return 'setorial';

  // Check for municipal prefixes (format: uf-cidade-programa)
  const municipalPattern = /^[a-z]{2}-[a-z]+-/i;
  if (municipalPattern.test(programa)) {
    return 'municipal';
  }

  // Check for state prefixes
  if (programa.includes('_SP') || programa.includes('_RJ') || programa.includes('_MG') ||
      /^state-[a-z]{2}-/i.test(programa)) {
    return 'estadual';
  }

  return 'federal'; // Default to federal
}

function BenefitCard({ benefit }: { benefit: EligibilityResult }) {
  const config = STATUS_CONFIG[benefit.status];
  const icon = PROGRAM_ICONS[benefit.programa] || '📋';

  return (
    <div className={`rounded-xl border overflow-hidden ${config.bg} ${config.border}`}>
      <div className="p-4">
        {/* Header */}
        <div className="flex items-start gap-3">
          <div className="w-12 h-12 rounded-full bg-[var(--badge-bg)] flex items-center justify-center text-2xl flex-shrink-0">
            {icon}
          </div>
          <div className="flex-1 min-w-0">
            <h4 className="font-semibold text-[var(--text-secondary)]">{benefit.programaNome}</h4>
            <span className={`text-xs font-medium ${config.labelColor}`}>
              {config.icon} {config.label}
            </span>
          </div>
          {benefit.valorEstimado && benefit.status === 'elegivel' && (
            <div className="text-right">
              <p className="text-xs text-[var(--text-tertiary)]">até</p>
              <p className="text-lg font-bold text-emerald-600">
                R$ {benefit.valorEstimado.toFixed(0)}
              </p>
              <p className="text-xs text-[var(--text-tertiary)]">/mês</p>
            </div>
          )}
        </div>

        {/* Motivo */}
        <p className="mt-3 text-sm text-[var(--text-tertiary)] line-clamp-2">
          {benefit.motivo}
        </p>

        {/* Onde solicitar */}
        {benefit.ondeSolicitar && benefit.status === 'elegivel' && (
          <div className="mt-3 flex items-center gap-2 text-xs text-[var(--text-tertiary)]">
            <span>📍</span>
            <span>{benefit.ondeSolicitar}</span>
          </div>
        )}
      </div>
    </div>
  );
}

function CategorySection({
  category,
  benefits,
}: {
  category: keyof typeof BENEFIT_CATEGORIES;
  benefits: EligibilityResult[];
}) {
  if (benefits.length === 0) return null;

  const config = BENEFIT_CATEGORIES[category];
  const totalValue = benefits.reduce((sum, b) => sum + (b.valorEstimado || 0), 0);

  return (
    <div className="space-y-3">
      <div className={`p-3 rounded-lg bg-gradient-to-r ${config.color} border`}>
        <div className="flex items-center justify-between">
          <div className="flex items-center gap-2">
            <span className="text-xl">{config.icon}</span>
            <span className="font-medium text-[var(--text-secondary)]">{config.label}</span>
            <span className="px-2 py-0.5 rounded bg-[var(--badge-bg)] text-xs text-[var(--text-secondary)]">
              {benefits.length}
            </span>
          </div>
          {totalValue > 0 && (
            <span className="text-sm font-medium text-emerald-600">
              até R$ {totalValue.toFixed(0)}/mês
            </span>
          )}
        </div>
      </div>
      <div className="space-y-3 pl-2">
        {benefits.map((b, i) => (
          <BenefitCard key={`${category}-${i}`} benefit={b} />
        ))}
      </div>
    </div>
  );
}

export default function RightsWallet({ result, onGenerateCarta, onFindCras, onReset }: Props) {
  const totalElegiveis = result.beneficiosElegiveis.length;
  const totalJaRecebe = result.beneficiosJaRecebe.length;

  // Agrupa benefícios elegíveis por categoria
  const eligibleByCategory = {
    federal: result.beneficiosElegiveis.filter(b => getBenefitCategory(b.programa) === 'federal'),
    estadual: result.beneficiosElegiveis.filter(b => getBenefitCategory(b.programa) === 'estadual'),
    municipal: result.beneficiosElegiveis.filter(b => getBenefitCategory(b.programa) === 'municipal'),
    setorial: result.beneficiosElegiveis.filter(b => getBenefitCategory(b.programa) === 'setorial'),
  };

  const hasCategories = eligibleByCategory.estadual.length > 0 ||
                        eligibleByCategory.municipal.length > 0 ||
                        eligibleByCategory.setorial.length > 0;

  return (
    <div className="space-y-6">
      {/* Header com resumo */}
      <div className="text-center">
        {totalElegiveis > 0 ? (
          <>
            <div className="text-5xl mb-3">🎉</div>
            <h2 className="text-2xl font-bold text-[var(--text-primary)]">
              Você pode ter direito a {totalElegiveis} benefício{totalElegiveis > 1 ? 's' : ''}!
            </h2>
          </>
        ) : (
          <>
            <div className="text-5xl mb-3">📋</div>
            <h2 className="text-2xl font-bold text-[var(--text-primary)]">
              Resultado da análise
            </h2>
          </>
        )}
      </div>

      {/* Valor potencial */}
      {result.valorPotencialMensal > 0 && (
        <div className="p-5 rounded-2xl bg-gradient-to-r from-emerald-600/15 to-emerald-500/5 border border-emerald-500/30">
          <p className="text-sm text-emerald-600 mb-1">Valor potencial mensal</p>
          <p className="text-4xl font-bold text-emerald-600">
            R$ {result.valorPotencialMensal.toFixed(0)}
          </p>
          <p className="text-xs text-emerald-600/60 mt-1">
            em benefícios que você pode receber
          </p>
        </div>
      )}

      {/* Benefícios que já recebe */}
      {totalJaRecebe > 0 && (
        <div className="space-y-3">
          <h3 className="text-sm font-medium text-[var(--text-tertiary)] uppercase tracking-wider">
            Você já recebe
          </h3>
          {result.beneficiosJaRecebe.map((b, i) => (
            <BenefitCard key={`ja-${i}`} benefit={b} />
          ))}
        </div>
      )}

      {/* Benefícios elegíveis - Agrupados por categoria */}
      {totalElegiveis > 0 && (
        <div className="space-y-6">
          <h3 className="text-sm font-medium text-[var(--text-tertiary)] uppercase tracking-wider">
            Benefícios disponíveis para você
          </h3>

          {hasCategories ? (
            <>
              <CategorySection category="federal" benefits={eligibleByCategory.federal} />
              <CategorySection category="estadual" benefits={eligibleByCategory.estadual} />
              <CategorySection category="municipal" benefits={eligibleByCategory.municipal} />
              <CategorySection category="setorial" benefits={eligibleByCategory.setorial} />
            </>
          ) : (
            // Se só tem federais, mostra sem categoria
            <div className="space-y-3">
              {result.beneficiosElegiveis.map((b, i) => (
                <BenefitCard key={`el-${i}`} benefit={b} />
              ))}
            </div>
          )}
        </div>
      )}

      {/* Inconclusivos */}
      {result.beneficiosInconclusivos.length > 0 && (
        <div className="space-y-3">
          <h3 className="text-sm font-medium text-[var(--text-tertiary)] uppercase tracking-wider">
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
          <h3 className="font-medium text-blue-600 mb-3">Próximos passos</h3>
          <ol className="space-y-2">
            {result.proximosPassosPrioritarios.map((passo, i) => (
              <li key={i} className="text-sm text-[var(--text-secondary)] flex gap-2">
                <span className="text-blue-600 font-medium">{i + 1}.</span>
                <span>{passo}</span>
              </li>
            ))}
          </ol>
        </div>
      )}

      {/* Documentos necessários */}
      {result.documentosNecessarios.length > 0 && (
        <div className="p-4 rounded-xl bg-[var(--badge-bg)] border border-[var(--border-color)]">
          <h3 className="font-medium text-[var(--text-secondary)] mb-3">Documentos necessários</h3>
          <div className="flex flex-wrap gap-2">
            {result.documentosNecessarios.slice(0, 6).map((doc, i) => (
              <span key={i} className="px-3 py-1 rounded-full bg-[var(--bg-card)] border border-[var(--border-color)] text-sm text-[var(--text-secondary)]">
                📄 {doc}
              </span>
            ))}
          </div>
        </div>
      )}

      {/* Dica sobre benefícios estaduais e municipais */}
      {eligibleByCategory.estadual.length === 0 && eligibleByCategory.municipal.length === 0 && totalElegiveis > 0 && (
        <div className="p-4 rounded-xl bg-purple-500/10 border border-purple-500/30">
          <div className="flex items-start gap-3">
            <span className="text-xl">💡</span>
            <div>
              <p className="text-purple-600 font-medium text-sm">Dica</p>
              <p className="text-purple-600/70 text-sm mt-1">
                Seu estado e cidade podem ter benefícios adicionais! Informe sua localização na primeira etapa
                para vermos programas estaduais e municipais disponíveis.
              </p>
            </div>
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
          className="w-full py-3 rounded-xl font-medium bg-[var(--badge-bg)] text-[var(--text-secondary)] hover:bg-[var(--hover-bg)] transition-all"
        >
          Fazer nova consulta
        </button>
      </div>

      {/* Footer informativo */}
      <div className="text-center pt-4 border-t border-[var(--border-color)]">
        <p className="text-xs text-[var(--text-tertiary)]">
          Análise baseada nas informações fornecidas.
          Confirme presencialmente no CRAS ou órgão responsável.
        </p>
      </div>
    </div>
  );
}
