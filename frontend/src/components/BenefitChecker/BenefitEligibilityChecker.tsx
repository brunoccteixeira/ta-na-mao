/**
 * BenefitEligibilityChecker — main container that orchestrates header,
 * summary bar, criteria sections, mini-form, and action buttons.
 */

import { useMemo } from 'react';
import { Link } from 'react-router-dom';
import { MapPin, List, ArrowRight } from 'lucide-react';
import type { Benefit, CitizenProfile, EligibilityResult } from '../../engine/types';
import { evaluateBenefit } from '../../engine/evaluator';
import { formatBenefitValue } from '../../engine/catalog';
import { groupAndEvaluateCriteria } from '../../utils/criteriaGrouping';
import CriteriaSection from './CriteriaSection';
import MiniProfileForm from './MiniProfileForm';

interface BenefitEligibilityCheckerProps {
  benefit: Benefit;
  profile: CitizenProfile | null;
  onProfileSubmit: (profile: CitizenProfile) => void;
}

// Scope badge colors
function scopeBadge(scope: string) {
  switch (scope) {
    case 'federal':
      return { label: 'Federal', cls: 'bg-blue-100 text-blue-700' };
    case 'state':
      return { label: 'Estadual', cls: 'bg-purple-100 text-purple-700' };
    case 'municipal':
      return { label: 'Municipal', cls: 'bg-amber-100 text-amber-700' };
    case 'sectoral':
      return { label: 'Setorial', cls: 'bg-teal-100 text-teal-700' };
    default:
      return { label: 'Benefício', cls: 'bg-gray-100 text-gray-700' };
  }
}

function statusSummary(result: EligibilityResult) {
  const total = result.matchedRules.length + result.failedRules.length + result.inconclusiveRules.length;
  const met = result.matchedRules.length;

  const statusMap: Record<string, { label: string; cls: string }> = {
    eligible: { label: 'Você tem direito!', cls: 'bg-emerald-100 text-emerald-700' },
    likely_eligible: { label: 'Provavelmente sim', cls: 'bg-emerald-50 text-emerald-600' },
    maybe: { label: 'Pode ter direito', cls: 'bg-amber-50 text-amber-700' },
    not_eligible: { label: 'Não atende agora', cls: 'bg-red-50 text-red-600' },
    already_receiving: { label: 'Você já recebe', cls: 'bg-blue-50 text-blue-600' },
    not_applicable: { label: 'Não se aplica', cls: 'bg-gray-100 text-gray-600' },
  };

  const info = statusMap[result.status] || statusMap.not_applicable;

  return { total, met, ...info };
}

export default function BenefitEligibilityChecker({
  benefit,
  profile,
  onProfileSubmit,
}: BenefitEligibilityCheckerProps) {
  // Evaluate if we have a profile
  const result = useMemo<EligibilityResult | null>(() => {
    if (!profile) return null;
    return evaluateBenefit(profile, benefit);
  }, [profile, benefit]);

  // Group criteria
  const groups = useMemo(
    () => groupAndEvaluateCriteria(benefit.eligibilityRules, result),
    [benefit.eligibilityRules, result],
  );

  const badge = scopeBadge(benefit.scope);
  const summary = result ? statusSummary(result) : null;

  return (
    <div className="space-y-5">
      {/* ── BenefitHeader ── */}
      <div className="p-5 bg-[var(--bg-card)] rounded-2xl border border-[var(--border-color)]">
        <div className="flex items-start gap-3 mb-3">
          <span className="text-3xl leading-none">{benefit.icon || '📋'}</span>
          <div className="flex-1 min-w-0">
            <div className="flex items-center gap-2 mb-1">
              <span className={`px-2 py-0.5 rounded-full text-xs font-medium ${badge.cls}`}>
                {badge.label}
              </span>
            </div>
            <h2 className="text-lg font-bold text-[var(--text-primary)] leading-tight">
              {benefit.name}
            </h2>
          </div>
        </div>
        <p className="text-sm text-[var(--text-secondary)] mb-3">
          {benefit.shortDescription}
        </p>
        {benefit.estimatedValue && (
          <div className="inline-flex items-center gap-1.5 px-3 py-1.5 rounded-full bg-emerald-50 text-emerald-700 text-sm font-semibold">
            {formatBenefitValue(benefit)}
            {/* Append suffix only when formatBenefitValue omits it (description branch) */}
            {benefit.estimatedValue.description && benefit.estimatedValue.type === 'monthly' && '/mês'}
            {benefit.estimatedValue.description && benefit.estimatedValue.type === 'annual' && '/ano'}
          </div>
        )}
      </div>

      {/* ── EligibilitySummaryBar ── */}
      {summary && (
        <div className={`flex items-center justify-between p-4 rounded-2xl ${summary.cls}`}>
          <div>
            <p className="text-sm font-semibold">{summary.label}</p>
            <p className="text-xs opacity-80">
              {summary.met} de {summary.total} critérios atendidos
            </p>
          </div>
          {result?.reason && (
            <p className="text-xs text-right max-w-[50%] opacity-80">
              {result.reason}
            </p>
          )}
        </div>
      )}

      {/* ── Mini form (when no profile) ── */}
      {!profile && (
        <MiniProfileForm
          rules={benefit.eligibilityRules}
          onSubmit={onProfileSubmit}
        />
      )}

      {/* ── Criteria Sections (when we have evaluation) ── */}
      {result && (
        <div>
          {groups.map(group => (
            <CriteriaSection key={group.groupKey} group={group} />
          ))}
        </div>
      )}

      {/* ── Update data (when profile exists — allow re-filling) ── */}
      {profile && (
        <details className="group">
          <summary className="cursor-pointer text-sm font-medium text-[var(--accent)] flex items-center gap-1 py-2">
            <ArrowRight className="w-4 h-4 transition-transform group-open:rotate-90" />
            Atualizar meus dados
          </summary>
          <div className="mt-3">
            <MiniProfileForm
              rules={benefit.eligibilityRules}
              onSubmit={onProfileSubmit}
              initialProfile={profile}
            />
          </div>
        </details>
      )}

      {/* ── CheckerActions ── */}
      <div className="space-y-3 pt-2">
        {result && result.status !== 'already_receiving' && result.status !== 'not_applicable' && (
          <a
            href={`https://www.google.com/maps/search/${encodeURIComponent('CRAS perto de mim')}`}
            target="_blank"
            rel="noopener noreferrer"
            className="flex items-center justify-center gap-2 w-full py-4 bg-[var(--bg-card)] border border-[var(--border-color)] text-[var(--text-primary)] font-medium rounded-full text-sm transition-colors hover:bg-gray-50 min-h-[48px]"
          >
            <MapPin className="w-5 h-5 text-[var(--accent)]" />
            Encontrar CRAS mais próximo
          </a>
        )}

        <Link
          to="/beneficios"
          className="flex items-center justify-center gap-2 w-full py-4 bg-[var(--bg-card)] border border-[var(--border-color)] text-[var(--text-secondary)] font-medium rounded-full text-sm transition-colors hover:bg-gray-50 min-h-[48px]"
        >
          <List className="w-5 h-5" />
          Ver todos os benefícios
        </Link>
      </div>
    </div>
  );
}
