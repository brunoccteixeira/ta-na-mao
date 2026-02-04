'use client';

/**
 * Step 6: Filhos e dependentes (conditional - only if pessoas > 1)
 */

import { useState } from 'react';
import { useWizard } from '../WizardContext';
import YesNo from '../inputs/YesNo';
import NumberGrid from '../inputs/NumberGrid';
import ExplanationModal, { WhyButton } from '../ExplanationModal';
import { QUESTIONS } from '../../../data/questions';
import { ArrowRight } from 'lucide-react';

export default function StepFilhos() {
  const { profile, updateProfile, nextStep } = useWizard();
  const [showExplanation, setShowExplanation] = useState(false);
  const [hasMinors, setHasMinors] = useState<boolean | undefined>(
    profile.quantidadeFilhos > 0 ? true : undefined
  );
  const question = QUESTIONS.filhos;

  const handleHasMinorsChange = (value: boolean | null) => {
    const boolValue = value ?? false;
    setHasMinors(boolValue);
    if (!boolValue) {
      updateProfile({
        quantidadeFilhos: 0,
        temCrianca0a6: false,
      });
    }
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

      {/* Has children under 18? */}
      <div className="mb-6">
        <label className="block text-sm font-medium text-[var(--text-primary)] mb-3">
          Tem filhos menores de 18 anos?
        </label>
        <YesNo
          value={hasMinors}
          onChange={handleHasMinorsChange}
        />
      </div>

      {/* How many children */}
      {hasMinors && (
        <div className="mb-6 animate-fadeIn">
          <label className="block text-sm font-medium text-[var(--text-primary)] mb-3">
            Quantos filhos menores de 18?
          </label>
          <NumberGrid
            value={profile.quantidadeFilhos}
            onChange={(value) => updateProfile({ quantidadeFilhos: value })}
            min={1}
            max={8}
            lastLabel="8+"
          />
        </div>
      )}

      {/* Children 0-6? */}
      {hasMinors && profile.quantidadeFilhos > 0 && (
        <div className="mb-6 animate-fadeIn">
          <label className="block text-sm font-medium text-[var(--text-primary)] mb-3">
            Algum filho tem de 0 a 6 anos?
          </label>
          <YesNo
            value={profile.temCrianca0a6}
            onChange={(value) => updateProfile({ temCrianca0a6: value ?? false })}
          />
          {profile.temCrianca0a6 && (
            <p className="mt-2 text-xs text-emerald-600">
              Crianças de 0-6 anos dão direito a adicional de R$ 150 no Bolsa Família
            </p>
          )}
        </div>
      )}

      {/* Has elderly 65+? */}
      <div className="mb-6">
        <label className="block text-sm font-medium text-[var(--text-primary)] mb-3">
          Tem alguém com 65 anos ou mais na casa?
        </label>
        <YesNo
          value={profile.temIdoso65Mais}
          onChange={(value) => updateProfile({ temIdoso65Mais: value ?? false })}
        />
        {profile.temIdoso65Mais && (
          <p className="mt-2 text-xs text-emerald-600">
            Idosos 65+ podem ter direito ao BPC/LOAS (R$ 1.518/mês)
          </p>
        )}
      </div>

      {/* Has pregnant? */}
      <div className="mb-6">
        <label className="block text-sm font-medium text-[var(--text-primary)] mb-3">
          Tem gestante na família?
        </label>
        <YesNo
          value={profile.temGestante}
          onChange={(value) => updateProfile({ temGestante: value ?? false })}
        />
        {profile.temGestante && (
          <p className="mt-2 text-xs text-emerald-600">
            Gestantes têm adicional de R$ 50 no Bolsa Família
          </p>
        )}
      </div>

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
