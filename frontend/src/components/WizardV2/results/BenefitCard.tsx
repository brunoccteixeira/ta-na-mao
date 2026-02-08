'use client';

/**
 * BenefitCard - Card for displaying a single benefit
 *
 * Value-first design with colored left border and smooth expand/collapse
 */

import { useState } from 'react';
import { ChevronDown, ChevronUp, ExternalLink, CheckCircle, Clock, HelpCircle, AlertTriangle, Phone } from 'lucide-react';
import type { EligibilityResult } from '../../../engine/types';

function getAlternativeChannel(category?: string): string {
  if (!category) return 'Ligue 136 (Disque Social) para orientação gratuita.';

  const cat = category.toLowerCase();
  if (cat.includes('saúde') || cat.includes('saude') || cat.includes('farmácia') || cat.includes('farmacia'))
    return 'Ligue 136 (Disque Social) ou vá à UBS mais próxima.';
  if (cat.includes('previdência') || cat.includes('previdencia') || cat.includes('aposentadoria'))
    return 'Ligue 135 (INSS) — atendimento 24h, todos os dias.';
  if (cat.includes('assistência') || cat.includes('assistencia') || cat.includes('social'))
    return 'Ligue 111 (Central SUAS) ou procure o CRAS mais próximo.';
  if (cat.includes('trabalh') || cat.includes('emprego') || cat.includes('clt'))
    return 'Ligue 158 (Alô Trabalho) ou vá ao posto do SINE.';

  return 'Ligue 136 (Disque Social) para orientação gratuita.';
}

interface Props {
  result: EligibilityResult;
  variant?: 'eligible' | 'likely' | 'maybe' | 'receiving';
}

export default function BenefitCard({ result, variant = 'eligible' }: Props) {
  const [isExpanded, setIsExpanded] = useState(false);
  const { benefit, estimatedValue, matchedRules, reason } = result;

  const variantStyles = {
    eligible: {
      borderLeft: 'border-l-emerald-500',
      border: 'border-emerald-200',
      bg: 'bg-emerald-50',
      icon: <CheckCircle className="w-5 h-5 text-emerald-600" />,
      badge: 'bg-emerald-100 text-emerald-700',
      label: 'Você tem direito',
    },
    likely: {
      borderLeft: 'border-l-blue-500',
      border: 'border-blue-200',
      bg: 'bg-blue-50',
      icon: <Clock className="w-5 h-5 text-blue-600" />,
      badge: 'bg-blue-100 text-blue-700',
      label: 'Provavelmente elegível',
    },
    maybe: {
      borderLeft: 'border-l-amber-500',
      border: 'border-amber-200',
      bg: 'bg-amber-50',
      icon: <HelpCircle className="w-5 h-5 text-amber-600" />,
      badge: 'bg-amber-100 text-amber-700',
      label: 'Verificar presencialmente',
    },
    receiving: {
      borderLeft: 'border-l-gray-400',
      border: 'border-gray-200',
      bg: 'bg-gray-50',
      icon: <CheckCircle className="w-5 h-5 text-gray-500" />,
      badge: 'bg-gray-100 text-gray-600',
      label: 'Você já recebe',
    },
  };

  const style = variantStyles[variant];

  // Format value
  const formatValue = () => {
    if (!estimatedValue) return null;

    const type = benefit.estimatedValue?.type;
    switch (type) {
      case 'monthly':
        return `R$ ${estimatedValue.toLocaleString('pt-BR')} /mês`;
      case 'annual':
        return `R$ ${estimatedValue.toLocaleString('pt-BR')} /ano`;
      case 'one_time':
        return `R$ ${estimatedValue.toLocaleString('pt-BR')} (único)`;
      default:
        return `R$ ${estimatedValue.toLocaleString('pt-BR')}`;
    }
  };

  const valueDisplay = formatValue();

  return (
    <div className={`rounded-xl border-2 border-l-4 ${style.border} ${style.borderLeft} overflow-hidden transition-all`}>
      {/* Header */}
      <div className={`p-4 ${style.bg}`}>
        <div className="flex items-start justify-between gap-3">
          <div className="flex-1 min-w-0">
            {/* Value (prominent) */}
            {valueDisplay && (
              <p className="text-2xl font-bold text-[var(--text-primary)] mb-1">
                {valueDisplay}
              </p>
            )}

            {/* Name */}
            <div className="flex items-center gap-2">
              {style.icon}
              <h3 className="font-semibold text-[var(--text-primary)]">
                {benefit.name}
              </h3>
            </div>

            {/* Badge */}
            <span className={`inline-block mt-2 px-2 py-0.5 rounded-full text-xs font-medium ${style.badge}`}>
              {style.label}
            </span>
          </div>
        </div>

        {/* Short description */}
        <p className="mt-3 text-sm text-[var(--text-secondary)]">
          {benefit.shortDescription}
        </p>
      </div>

      {/* Actions */}
      <div className="p-4 bg-[var(--bg-card)] border-t border-[var(--border-color)]">
        <div className="flex items-center gap-2">
          <button
            onClick={() => setIsExpanded(!isExpanded)}
            className="flex-1 flex items-center justify-center gap-2 py-2 px-4 rounded-lg bg-[var(--bg-primary)] hover:bg-[var(--hover-bg)] text-sm font-medium text-[var(--text-primary)] transition-colors"
          >
            {isExpanded ? (
              <>
                <ChevronUp className="w-4 h-4" />
                Menos detalhes
              </>
            ) : (
              <>
                <ChevronDown className="w-4 h-4" />
                Ver detalhes
              </>
            )}
          </button>

          {benefit.sourceUrl && (
            <a
              href={benefit.sourceUrl}
              target="_blank"
              rel="noopener noreferrer"
              className="p-2 rounded-lg bg-[var(--bg-primary)] hover:bg-[var(--hover-bg)] text-[var(--text-tertiary)] hover:text-[var(--text-primary)] transition-colors"
              title="Abrir site oficial"
            >
              <ExternalLink className="w-5 h-5" />
            </a>
          )}
        </div>
      </div>

      {/* Expanded content with smooth grid-rows transition */}
      <div className="benefit-expand" data-open={isExpanded}>
        <div>
          <div className="p-4 bg-[var(--bg-primary)] border-t border-[var(--border-color)] space-y-4">
            {/* Reason / matched rules */}
            {(reason || matchedRules.length > 0) && (
              <div>
                <h4 className="text-xs font-medium text-[var(--text-tertiary)] uppercase tracking-wide mb-2">
                  Por que você tem direito
                </h4>
                {reason && (
                  <p className="text-sm text-[var(--text-secondary)]">{reason}</p>
                )}
                {matchedRules.length > 0 && (
                  <ul className="mt-2 space-y-1">
                    {matchedRules.map((rule, i) => (
                      <li key={i} className="flex items-center gap-2 text-sm text-[var(--text-secondary)]">
                        <CheckCircle className="w-4 h-4 text-emerald-500 flex-shrink-0" />
                        {rule}
                      </li>
                    ))}
                  </ul>
                )}
              </div>
            )}

            {/* Where to apply */}
            <div>
              <h4 className="text-xs font-medium text-[var(--text-tertiary)] uppercase tracking-wide mb-2">
                Onde solicitar
              </h4>
              <p className="text-sm text-[var(--text-primary)] font-medium">
                {benefit.whereToApply}
              </p>
            </div>

            {/* Documents */}
            {benefit.documentsRequired.length > 0 && (
              <div>
                <h4 className="text-xs font-medium text-[var(--text-tertiary)] uppercase tracking-wide mb-2">
                  Documentos necessários
                </h4>
                <ul className="grid grid-cols-2 gap-1">
                  {benefit.documentsRequired.map((doc, i) => (
                    <li key={i} className="flex items-center gap-1 text-xs text-[var(--text-secondary)]">
                      <span className="w-1 h-1 bg-emerald-500 rounded-full" />
                      {doc}
                    </li>
                  ))}
                </ul>
              </div>
            )}

            {/* How to apply */}
            {benefit.howToApply && benefit.howToApply.length > 0 && (
              <div>
                <h4 className="text-xs font-medium text-[var(--text-tertiary)] uppercase tracking-wide mb-2">
                  Como solicitar
                </h4>
                <ol className="space-y-2">
                  {benefit.howToApply.map((step, i) => (
                    <li key={i} className="flex items-start gap-2 text-sm text-[var(--text-secondary)]">
                      <span className="w-5 h-5 bg-emerald-100 rounded-full flex items-center justify-center text-xs font-medium text-emerald-700 flex-shrink-0">
                        {i + 1}
                      </span>
                      {step}
                    </li>
                  ))}
                </ol>
              </div>
            )}

            {/* Legal basis */}
            {benefit.legalBasis?.laws && benefit.legalBasis.laws.length > 0 && (
              <div>
                <h4 className="text-xs font-medium text-[var(--text-tertiary)] uppercase tracking-wide mb-2">
                  Base legal
                </h4>
                <p className="text-xs text-[var(--text-tertiary)]">
                  {benefit.legalBasis.laws.map((l) => l.description).join(', ')}
                </p>
              </div>
            )}

            {/* Disclaimer */}
            {benefit.metadata?.disclaimer && (
              <div className="flex gap-2 p-3 bg-amber-50 border border-amber-200 rounded-lg">
                <AlertTriangle className="w-4 h-4 text-amber-500 flex-shrink-0 mt-0.5" />
                <p className="text-xs text-amber-800">
                  {benefit.metadata.disclaimer}
                </p>
              </div>
            )}

            {/* Armadilha (common pitfall) */}
            {benefit.metadata?.armadilha && (
              <div className="flex gap-2 p-3 bg-red-50 border border-red-200 rounded-lg">
                <AlertTriangle className="w-4 h-4 text-red-500 flex-shrink-0 mt-0.5" />
                <div>
                  <p className="text-xs font-medium text-red-800 mb-0.5">Atenção</p>
                  <p className="text-xs text-red-700">
                    {benefit.metadata.armadilha}
                  </p>
                </div>
              </div>
            )}

            {/* Alternative channel */}
            {benefit.whereToApply && (
              <div className="flex gap-2 p-3 bg-blue-50 border border-blue-200 rounded-lg">
                <Phone className="w-4 h-4 text-blue-500 flex-shrink-0 mt-0.5" />
                <div>
                  <p className="text-xs font-medium text-blue-800 mb-0.5">Sem internet?</p>
                  <p className="text-xs text-blue-700">
                    {getAlternativeChannel(benefit.category)}
                  </p>
                </div>
              </div>
            )}
          </div>
        </div>
      </div>
    </div>
  );
}
