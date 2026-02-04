'use client';

/**
 * ResultsDashboard - Main dashboard for displaying eligibility results
 *
 * Wizbii-style: hero section with total value, categorized benefits, next steps
 */

import { useState, useMemo, useEffect } from 'react';
import { useWizard } from '../WizardContext';
import BenefitCard from './BenefitCard';
import { evaluateAllBenefits } from '../../../engine/evaluator';
import {
  Gift,
  ArrowRight,
  MapPin,
  Pill,
  Building,
  FileText,
  Share2,
  RotateCcw,
  ChevronRight,
  Wallet,
  TrendingUp,
  Shield,
  Sparkles,
} from 'lucide-react';
import type { EvaluationSummary, CitizenProfile } from '../../../engine/types';

export default function ResultsDashboard() {
  const { profile, reset } = useWizard();
  const [results, setResults] = useState<EvaluationSummary | null>(null);
  const [isLoading, setIsLoading] = useState(true);
  const [activeTab, setActiveTab] = useState<'eligible' | 'likely' | 'maybe' | 'receiving'>('eligible');

  // Run eligibility evaluation
  useEffect(() => {
    const evaluate = async () => {
      setIsLoading(true);
      try {
        // Convert WizardProfile to CitizenProfile
        const citizenProfile: CitizenProfile = {
          ...profile,
          estado: profile.estado || 'SP',
          pessoasNaCasa: profile.pessoasNaCasa || 1,
          quantidadeFilhos: profile.quantidadeFilhos || 0,
          rendaFamiliarMensal: profile.rendaFamiliarMensal || 0,
        };

        const summary = await evaluateAllBenefits(citizenProfile);
        setResults(summary);
      } catch (error) {
        console.error('Error evaluating benefits:', error);
      } finally {
        setIsLoading(false);
      }
    };

    evaluate();
  }, [profile]);

  // Calculate totals
  const totals = useMemo(() => {
    if (!results) return { monthly: 0, annual: 0, oneTime: 0, count: 0 };

    const eligibleCount = results.eligible.length + results.likelyEligible.length;

    return {
      monthly: results.totalPotentialMonthly,
      annual: results.totalPotentialAnnual,
      oneTime: results.totalPotentialOneTime,
      count: eligibleCount,
    };
  }, [results]);

  // Share result
  const handleShare = async () => {
    const text = `Descobri que posso ter direito a ${totals.count} benefícios no valor de até R$ ${(totals.monthly * 12 + totals.annual + totals.oneTime).toLocaleString('pt-BR')} por ano! Descubra os seus também em tanamaoo.com.br`;

    if (navigator.share) {
      try {
        await navigator.share({ text, url: window.location.href });
      } catch {
        // User cancelled or error
      }
    } else {
      // Fallback to clipboard
      await navigator.clipboard.writeText(text);
      alert('Link copiado!');
    }
  };

  if (isLoading) {
    return (
      <div className="min-h-screen bg-[var(--bg-primary)] flex items-center justify-center">
        <div className="text-center">
          <div className="w-16 h-16 bg-emerald-500 rounded-full flex items-center justify-center mx-auto mb-4 animate-pulse">
            <Sparkles className="w-8 h-8 text-white" />
          </div>
          <p className="text-[var(--text-primary)] font-semibold">Analisando seus benefícios...</p>
          <p className="text-[var(--text-tertiary)] text-sm mt-1">Verificando mais de 200 programas</p>
        </div>
      </div>
    );
  }

  if (!results) {
    return (
      <div className="min-h-screen bg-[var(--bg-primary)] flex items-center justify-center p-4">
        <div className="text-center">
          <p className="text-[var(--text-primary)]">Erro ao carregar resultados</p>
          <button
            onClick={reset}
            className="mt-4 px-4 py-2 bg-emerald-500 text-white rounded-lg"
          >
            Tentar novamente
          </button>
        </div>
      </div>
    );
  }

  const tabs = [
    { id: 'eligible' as const, label: 'Elegíveis', count: results.eligible.length },
    { id: 'likely' as const, label: 'Prováveis', count: results.likelyEligible.length },
    { id: 'maybe' as const, label: 'Verificar', count: results.maybe.length },
    { id: 'receiving' as const, label: 'Já recebe', count: results.alreadyReceiving.length },
  ];

  const activeResults = {
    eligible: results.eligible,
    likely: results.likelyEligible,
    maybe: results.maybe,
    receiving: results.alreadyReceiving,
  }[activeTab];

  return (
    <div className="min-h-screen bg-[var(--bg-primary)]">
      {/* Hero Section */}
      <div className="bg-gradient-to-br from-emerald-600 to-emerald-700 text-white">
        <div className="max-w-2xl mx-auto px-4 py-8 lg:py-12">
          {/* Greeting */}
          <div className="flex items-center gap-2 text-emerald-200 mb-4">
            <Gift className="w-5 h-5" />
            <span className="text-sm font-medium">Resultado da análise</span>
          </div>

          {/* Main message */}
          <h1 className="text-2xl lg:text-3xl font-bold mb-2">
            Você pode ter direito a{' '}
            <span className="text-emerald-200">{totals.count} benefícios</span>
          </h1>

          {/* Value */}
          <div className="mt-6 p-4 bg-white/10 rounded-xl backdrop-blur-sm">
            <p className="text-emerald-200 text-sm mb-1">Valor potencial por ano</p>
            <p className="text-4xl lg:text-5xl font-bold">
              R$ {(totals.monthly * 12 + totals.annual + totals.oneTime).toLocaleString('pt-BR')}
            </p>

            {/* Breakdown */}
            <div className="mt-4 grid grid-cols-3 gap-4 pt-4 border-t border-white/20">
              <div>
                <p className="text-emerald-200 text-xs">Mensal</p>
                <p className="font-semibold">R$ {totals.monthly.toLocaleString('pt-BR')}</p>
              </div>
              <div>
                <p className="text-emerald-200 text-xs">Anual</p>
                <p className="font-semibold">R$ {totals.annual.toLocaleString('pt-BR')}</p>
              </div>
              <div>
                <p className="text-emerald-200 text-xs">Pontual</p>
                <p className="font-semibold">R$ {totals.oneTime.toLocaleString('pt-BR')}</p>
              </div>
            </div>
          </div>

          {/* Actions */}
          <div className="mt-6 flex gap-3">
            <button
              onClick={handleShare}
              className="flex-1 flex items-center justify-center gap-2 py-3 bg-white text-emerald-700 rounded-xl font-semibold hover:bg-emerald-50 transition-colors"
            >
              <Share2 className="w-5 h-5" />
              Compartilhar
            </button>
            <button
              onClick={reset}
              className="flex items-center justify-center gap-2 py-3 px-4 bg-white/10 text-white rounded-xl font-medium hover:bg-white/20 transition-colors"
            >
              <RotateCcw className="w-5 h-5" />
            </button>
          </div>
        </div>
      </div>

      {/* Main Content */}
      <div className="max-w-2xl mx-auto px-4 py-6">
        {/* Quick Actions (Partners Placeholder) */}
        <div className="mb-8">
          <h2 className="text-sm font-medium text-[var(--text-tertiary)] uppercase tracking-wide mb-3">
            Ações rápidas
          </h2>
          <div className="grid grid-cols-2 gap-3">
            <QuickActionCard
              icon={<MapPin className="w-5 h-5" />}
              title="CRAS mais próximo"
              description="Encontrar unidade"
              color="blue"
            />
            <QuickActionCard
              icon={<Pill className="w-5 h-5" />}
              title="Farmácia Popular"
              description="Remédios gratuitos"
              color="pink"
            />
            <QuickActionCard
              icon={<Building className="w-5 h-5" />}
              title="Conta Digital"
              description="Em breve"
              color="purple"
              disabled
            />
            <QuickActionCard
              icon={<FileText className="w-5 h-5" />}
              title="Gerar carta"
              description="Para levar ao CRAS"
              color="emerald"
            />
          </div>
        </div>

        {/* Benefits Tabs */}
        <div className="mb-4">
          <h2 className="text-sm font-medium text-[var(--text-tertiary)] uppercase tracking-wide mb-3">
            Seus benefícios
          </h2>
          <div className="flex gap-2 overflow-x-auto pb-2">
            {tabs.map((tab) => (
              <button
                key={tab.id}
                onClick={() => setActiveTab(tab.id)}
                className={`
                  flex items-center gap-2 px-4 py-2 rounded-full text-sm font-medium whitespace-nowrap transition-all
                  ${
                    activeTab === tab.id
                      ? 'bg-emerald-500 text-white'
                      : 'bg-[var(--bg-card)] text-[var(--text-secondary)] border border-[var(--border-color)] hover:border-emerald-300'
                  }
                `}
              >
                {tab.label}
                <span className={`
                  px-1.5 py-0.5 rounded-full text-xs
                  ${activeTab === tab.id ? 'bg-white/20' : 'bg-[var(--badge-bg)]'}
                `}>
                  {tab.count}
                </span>
              </button>
            ))}
          </div>
        </div>

        {/* Benefits List */}
        <div className="space-y-4 mb-8">
          {activeResults.length === 0 ? (
            <div className="text-center py-8 text-[var(--text-tertiary)]">
              Nenhum benefício nesta categoria
            </div>
          ) : (
            activeResults.map((result) => (
              <BenefitCard
                key={result.benefit.id}
                result={result}
                variant={activeTab === 'receiving' ? 'receiving' : activeTab === 'maybe' ? 'maybe' : activeTab === 'likely' ? 'likely' : 'eligible'}
              />
            ))
          )}
        </div>

        {/* Next Steps */}
        {results.prioritySteps.length > 0 && (
          <div className="mb-8">
            <h2 className="text-sm font-medium text-[var(--text-tertiary)] uppercase tracking-wide mb-3">
              Próximos passos
            </h2>
            <div className="bg-[var(--bg-card)] rounded-xl border border-[var(--border-color)] overflow-hidden">
              {results.prioritySteps.map((step, i) => (
                <div
                  key={i}
                  className="flex items-center gap-3 p-4 border-b border-[var(--border-color)] last:border-b-0"
                >
                  <div className="w-8 h-8 bg-emerald-100 dark:bg-emerald-500/20 rounded-full flex items-center justify-center text-sm font-semibold text-emerald-700 flex-shrink-0">
                    {i + 1}
                  </div>
                  <p className="flex-1 text-sm text-[var(--text-primary)]">{step}</p>
                  <ChevronRight className="w-5 h-5 text-[var(--text-tertiary)]" />
                </div>
              ))}
            </div>
          </div>
        )}

        {/* Documents Needed */}
        {results.documentsNeeded.length > 0 && (
          <div className="mb-8">
            <h2 className="text-sm font-medium text-[var(--text-tertiary)] uppercase tracking-wide mb-3">
              Documentos necessários
            </h2>
            <div className="bg-[var(--bg-card)] rounded-xl border border-[var(--border-color)] p-4">
              <div className="grid grid-cols-2 gap-2">
                {results.documentsNeeded.map((doc, i) => (
                  <div key={i} className="flex items-center gap-2 text-sm text-[var(--text-secondary)]">
                    <FileText className="w-4 h-4 text-[var(--text-tertiary)]" />
                    {doc}
                  </div>
                ))}
              </div>
            </div>
          </div>
        )}

        {/* Stats */}
        <div className="grid grid-cols-3 gap-3 mb-8">
          <StatCard
            icon={<Wallet className="w-5 h-5" />}
            label="Analisados"
            value={results.totalAnalyzed.toString()}
          />
          <StatCard
            icon={<TrendingUp className="w-5 h-5" />}
            label="Elegíveis"
            value={totals.count.toString()}
          />
          <StatCard
            icon={<Shield className="w-5 h-5" />}
            label="Já recebe"
            value={results.alreadyReceiving.length.toString()}
          />
        </div>

        {/* Footer */}
        <div className="text-center text-xs text-[var(--text-tertiary)] py-8">
          <p>Esta análise é informativa e não garante a concessão dos benefícios.</p>
          <p className="mt-1">Procure o CRAS mais próximo para confirmação.</p>
        </div>
      </div>
    </div>
  );
}

// Quick Action Card component
function QuickActionCard({
  icon,
  title,
  description,
  color,
  disabled = false,
}: {
  icon: React.ReactNode;
  title: string;
  description: string;
  color: 'blue' | 'pink' | 'purple' | 'emerald';
  disabled?: boolean;
}) {
  const colors = {
    blue: 'bg-blue-100 dark:bg-blue-500/20 text-blue-600',
    pink: 'bg-pink-100 dark:bg-pink-500/20 text-pink-600',
    purple: 'bg-purple-100 dark:bg-purple-500/20 text-purple-600',
    emerald: 'bg-emerald-100 dark:bg-emerald-500/20 text-emerald-600',
  };

  return (
    <button
      disabled={disabled}
      className={`
        flex items-center gap-3 p-4 rounded-xl border border-[var(--border-color)] bg-[var(--bg-card)] text-left transition-all
        ${disabled ? 'opacity-50 cursor-not-allowed' : 'hover:border-emerald-300 hover:shadow-sm'}
      `}
    >
      <div className={`w-10 h-10 rounded-lg flex items-center justify-center ${colors[color]}`}>
        {icon}
      </div>
      <div className="flex-1 min-w-0">
        <p className="font-medium text-[var(--text-primary)] text-sm">{title}</p>
        <p className="text-xs text-[var(--text-tertiary)]">{description}</p>
      </div>
      {!disabled && <ArrowRight className="w-4 h-4 text-[var(--text-tertiary)]" />}
    </button>
  );
}

// Stat Card component
function StatCard({
  icon,
  label,
  value,
}: {
  icon: React.ReactNode;
  label: string;
  value: string;
}) {
  return (
    <div className="bg-[var(--bg-card)] rounded-xl border border-[var(--border-color)] p-4 text-center">
      <div className="w-8 h-8 bg-[var(--bg-primary)] rounded-lg flex items-center justify-center mx-auto mb-2 text-[var(--text-tertiary)]">
        {icon}
      </div>
      <p className="text-xl font-bold text-[var(--text-primary)]">{value}</p>
      <p className="text-xs text-[var(--text-tertiary)]">{label}</p>
    </div>
  );
}
