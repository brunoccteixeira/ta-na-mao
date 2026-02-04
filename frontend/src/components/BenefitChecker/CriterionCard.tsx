/**
 * CriterionCard — individual eligibility rule card with colored status indicator.
 */

import { Check, ChevronRight, X, HelpCircle } from 'lucide-react';
import type { CriterionStatus, EvaluatedRule } from '../../utils/criteriaGrouping';

interface CriterionCardProps {
  evaluatedRule: EvaluatedRule;
}

const STATUS_CONFIG: Record<CriterionStatus, {
  border: string;
  iconBg: string;
  icon: React.ReactNode;
  label: string;
}> = {
  met: {
    border: 'border-l-emerald-500',
    iconBg: 'bg-emerald-100 text-emerald-600',
    icon: <Check className="w-5 h-5" />,
    label: 'Atende',
  },
  not_met: {
    border: 'border-l-red-400',
    iconBg: 'bg-red-100 text-red-600',
    icon: <X className="w-5 h-5" />,
    label: 'Não atende',
  },
  inconclusive: {
    border: 'border-l-amber-400',
    iconBg: 'bg-amber-100 text-amber-600',
    icon: <HelpCircle className="w-5 h-5" />,
    label: 'A verificar',
  },
  pending: {
    border: 'border-l-gray-300',
    iconBg: 'bg-gray-100 text-gray-400',
    icon: <ChevronRight className="w-5 h-5" />,
    label: 'Pendente',
  },
};

export default function CriterionCard({ evaluatedRule }: CriterionCardProps) {
  const { rule, status } = evaluatedRule;
  const config = STATUS_CONFIG[status];

  return (
    <div
      className={`flex items-center gap-3 p-4 bg-[var(--bg-card)] rounded-xl border border-[var(--border-color)] border-l-4 ${config.border}`}
      role="listitem"
      aria-label={`${rule.description}: ${config.label}`}
    >
      {/* Status icon — 48×48 touch target */}
      <div
        className={`w-12 h-12 min-w-[48px] min-h-[48px] rounded-xl flex items-center justify-center ${config.iconBg}`}
      >
        {config.icon}
      </div>

      {/* Rule description + optional legal reference */}
      <div className="flex-1">
        <p className="text-sm text-[var(--text-primary)] leading-snug">
          {rule.description}
        </p>
        {rule.legalReference && (
          <details className="mt-1">
            <summary className="text-xs text-[var(--text-tertiary)] cursor-pointer flex items-center gap-1 hover:text-[var(--text-secondary)]">
              <svg className="w-3 h-3 inline" fill="none" stroke="currentColor" viewBox="0 0 24 24"><path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M3 6l3 1m0 0l-3 9a5.002 5.002 0 006.001 0M6 7l3 9M6 7l6-2m6 2l3-1m-3 1l-3 9a5.002 5.002 0 006.001 0M18 7l3 9m-3-9l-6-2m0-2v2m0 16V5m0 16H9m3 0h3" /></svg>
              Base legal
            </summary>
            <p className="text-xs text-[var(--text-tertiary)] mt-1 pl-4">
              {rule.legalReference}
            </p>
          </details>
        )}
      </div>

      {/* Textual status label (accessibility — not just color) */}
      <span className="text-xs font-medium text-[var(--text-tertiary)] whitespace-nowrap">
        {config.label}
      </span>
    </div>
  );
}
