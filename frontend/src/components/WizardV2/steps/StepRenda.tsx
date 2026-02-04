'use client';

/**
 * Step 8: Renda familiar
 */

import { useState, useMemo } from 'react';
import { useWizard } from '../WizardContext';
import MoneyInput from '../inputs/MoneyInput';
import ExplanationModal, { WhyButton } from '../ExplanationModal';
import { QUESTIONS, RENDA_PRESETS } from '../../../data/questions';
import { ArrowRight, AlertCircle, CheckCircle } from 'lucide-react';

export default function StepRenda() {
  const { profile, updateProfile, nextStep } = useWizard();
  const [showExplanation, setShowExplanation] = useState(false);
  const question = QUESTIONS.renda;

  // Calculate per capita
  const perCapita = useMemo(() => {
    if (!profile.rendaFamiliarMensal || !profile.pessoasNaCasa) return 0;
    return Math.round(profile.rendaFamiliarMensal / profile.pessoasNaCasa);
  }, [profile.rendaFamiliarMensal, profile.pessoasNaCasa]);

  // Eligibility thresholds
  const thresholds = {
    extremaPobreza: 218,
    bolsaFamilia: 218,
    bpc: 379, // 1/4 salário mínimo
    cadunico: 759, // 1/2 salário mínimo
    mcmv: 2000, // Faixa 1 per capita (family up to 2830)
  };

  // Determine eligibility tier
  const getTier = () => {
    if (perCapita === 0) return null;
    if (perCapita <= thresholds.extremaPobreza) return 'extrema_pobreza';
    if (perCapita <= thresholds.bpc) return 'pobreza';
    if (perCapita <= thresholds.cadunico) return 'baixa_renda';
    if (perCapita <= thresholds.mcmv) return 'moderada';
    return 'acima';
  };

  const tier = getTier();

  const tierInfo = {
    extrema_pobreza: {
      label: 'Extrema pobreza',
      color: 'red',
      benefits: ['Bolsa Família', 'BPC (se elegível)', 'CadÚnico prioritário', 'MCMV Faixa 1'],
    },
    pobreza: {
      label: 'Pobreza',
      color: 'orange',
      benefits: ['Bolsa Família', 'BPC (se elegível)', 'CadÚnico', 'MCMV Faixa 1'],
    },
    baixa_renda: {
      label: 'Baixa renda',
      color: 'yellow',
      benefits: ['CadÚnico', 'Tarifa Social', 'MCMV Faixa 1-2', 'Farmácia Popular'],
    },
    moderada: {
      label: 'Renda moderada',
      color: 'blue',
      benefits: ['MCMV Faixa 2-3', 'Farmácia Popular'],
    },
    acima: {
      label: 'Acima dos critérios',
      color: 'gray',
      benefits: ['Alguns benefícios universais'],
    },
  };

  const handleNext = () => {
    nextStep();
  };

  return (
    <div>
      {/* Header */}
      <div className="mb-6">
        <h2 className="text-xl lg:text-2xl font-bold text-[var(--text-primary)] mb-2">
          {question.title}
        </h2>
        <p className="text-[var(--text-secondary)] text-sm">
          {question.subtitle}
        </p>
        <WhyButton onClick={() => setShowExplanation(true)} className="mt-2" />
      </div>

      {/* Money input */}
      <div className="mb-6">
        <MoneyInput
          value={profile.rendaFamiliarMensal}
          onChange={(value) => updateProfile({ rendaFamiliarMensal: value })}
          placeholder="0"
          presets={RENDA_PRESETS}
        />
      </div>

      {/* Per capita calculation */}
      {profile.rendaFamiliarMensal > 0 && profile.pessoasNaCasa > 0 && (
        <div className="mb-6 p-4 bg-[var(--bg-primary)] rounded-xl space-y-3">
          <div className="flex items-center justify-between">
            <span className="text-sm text-[var(--text-secondary)]">Renda por pessoa:</span>
            <span className="text-lg font-bold text-[var(--text-primary)]">
              R$ {perCapita.toLocaleString('pt-BR')}
            </span>
          </div>

          {tier && tierInfo[tier] && (
            <div className={`
              p-3 rounded-lg
              ${tier === 'extrema_pobreza' || tier === 'pobreza' ? 'bg-emerald-50 dark:bg-emerald-500/10' : ''}
              ${tier === 'baixa_renda' ? 'bg-yellow-50 dark:bg-yellow-500/10' : ''}
              ${tier === 'moderada' || tier === 'acima' ? 'bg-blue-50 dark:bg-blue-500/10' : ''}
            `}>
              <div className="flex items-center gap-2 mb-2">
                {tier === 'extrema_pobreza' || tier === 'pobreza' ? (
                  <CheckCircle className="w-5 h-5 text-emerald-600" />
                ) : (
                  <AlertCircle className="w-5 h-5 text-blue-600" />
                )}
                <span className={`
                  font-medium
                  ${tier === 'extrema_pobreza' || tier === 'pobreza' ? 'text-emerald-700' : ''}
                  ${tier === 'baixa_renda' ? 'text-yellow-700' : ''}
                  ${tier === 'moderada' || tier === 'acima' ? 'text-blue-700' : ''}
                `}>
                  {tierInfo[tier].label}
                </span>
              </div>
              <p className="text-xs text-[var(--text-secondary)]">
                Você pode ter direito a: {tierInfo[tier].benefits.join(', ')}
              </p>
            </div>
          )}
        </div>
      )}

      {/* Zero income note */}
      {profile.rendaFamiliarMensal === 0 && (
        <div className="mb-6 p-4 bg-amber-50 dark:bg-amber-500/10 rounded-xl">
          <p className="text-sm text-amber-700 dark:text-amber-400">
            Se sua família não tem nenhuma renda, você pode informar R$ 0.
            Famílias sem renda têm prioridade no CadÚnico.
          </p>
        </div>
      )}

      {/* Continue button */}
      <button
        onClick={handleNext}
        className="w-full py-4 rounded-xl font-semibold text-white flex items-center justify-center gap-2 transition-all bg-emerald-500 hover:bg-emerald-600"
      >
        Continuar
        <ArrowRight className="w-5 h-5" />
      </button>

      {/* Explanation modal */}
      <ExplanationModal
        isOpen={showExplanation}
        onClose={() => setShowExplanation(false)}
        title={question.explanation.title}
        explanation={question.explanation.text}
        examples={question.explanation.examples}
      />
    </div>
  );
}
