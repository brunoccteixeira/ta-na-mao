'use client';

/**
 * Step 5: Família (quantas pessoas na casa)
 */

import { useState } from 'react';
import { useWizard } from '../WizardContext';
import NumberGrid from '../inputs/NumberGrid';
import ExplanationModal, { WhyButton } from '../ExplanationModal';
import { QUESTIONS } from '../../../data/questions';
import { ArrowRight, Users } from 'lucide-react';

export default function StepFamilia() {
  const { profile, updateProfile, nextStep } = useWizard();
  const [showExplanation, setShowExplanation] = useState(false);
  const question = QUESTIONS.familia;

  const handleNext = () => {
    if (profile.pessoasNaCasa >= 1) {
      nextStep();
    }
  };

  // Calculate per capita hint if we have income
  const perCapita = profile.rendaFamiliarMensal && profile.pessoasNaCasa > 0
    ? Math.round(profile.rendaFamiliarMensal / profile.pessoasNaCasa)
    : null;

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

      {/* Visual representation */}
      <div className="mb-6 flex items-center justify-center py-6 bg-[var(--bg-primary)] rounded-xl">
        <div className="flex items-center gap-2">
          {Array.from({ length: Math.min(profile.pessoasNaCasa || 1, 8) }).map((_, i) => (
            <div
              key={i}
              className="w-10 h-10 bg-emerald-100 dark:bg-emerald-500/20 rounded-full flex items-center justify-center"
            >
              <Users className="w-5 h-5 text-emerald-600" />
            </div>
          ))}
          {(profile.pessoasNaCasa || 0) > 8 && (
            <span className="text-emerald-600 font-bold">+</span>
          )}
        </div>
      </div>

      {/* Number grid */}
      <div className="mb-6">
        <NumberGrid
          value={profile.pessoasNaCasa}
          onChange={(value) => updateProfile({ pessoasNaCasa: value })}
          min={1}
          max={9}
          lastLabel="9+"
        />
      </div>

      {/* Per capita hint */}
      {profile.pessoasNaCasa >= 1 && (
        <div className="mb-6 p-4 bg-emerald-50 dark:bg-emerald-500/10 rounded-xl">
          <p className="text-sm text-emerald-700 dark:text-emerald-400">
            <span className="font-semibold">{profile.pessoasNaCasa} pessoa{profile.pessoasNaCasa > 1 ? 's' : ''}</span> na casa
            {perCapita !== null && (
              <span className="block mt-1 text-emerald-600">
                Renda por pessoa: R$ {perCapita.toLocaleString('pt-BR')}
              </span>
            )}
          </p>
        </div>
      )}

      {/* Continue button */}
      <button
        onClick={handleNext}
        disabled={!profile.pessoasNaCasa || profile.pessoasNaCasa < 1}
        className={`
          w-full py-4 rounded-xl font-semibold text-white flex items-center justify-center gap-2 transition-all
          ${
            profile.pessoasNaCasa >= 1
              ? 'bg-emerald-500 hover:bg-emerald-600'
              : 'bg-gray-300 cursor-not-allowed'
          }
        `}
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
