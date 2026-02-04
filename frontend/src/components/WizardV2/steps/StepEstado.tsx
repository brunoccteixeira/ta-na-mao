'use client';

/**
 * Step 1: Estado (UF)
 */

import { useState } from 'react';
import { useWizard } from '../WizardContext';
import SingleChoice from '../inputs/SingleChoice';
import ExplanationModal, { WhyButton } from '../ExplanationModal';
import { QUESTIONS, ESTADO_OPTIONS } from '../../../data/questions';
import { ArrowRight } from 'lucide-react';

export default function StepEstado() {
  const { profile, updateProfile, nextStep } = useWizard();
  const [showExplanation, setShowExplanation] = useState(false);
  const question = QUESTIONS.estado;

  const handleNext = () => {
    if (profile.estado) {
      nextStep();
    }
  };

  // Group states by region for better UX
  const regions = {
    Norte: ['AC', 'AP', 'AM', 'PA', 'RO', 'RR', 'TO'],
    Nordeste: ['AL', 'BA', 'CE', 'MA', 'PB', 'PE', 'PI', 'RN', 'SE'],
    'Centro-Oeste': ['DF', 'GO', 'MT', 'MS'],
    Sudeste: ['ES', 'MG', 'RJ', 'SP'],
    Sul: ['PR', 'RS', 'SC'],
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

      {/* Options by region */}
      <div className="space-y-4 mb-6">
        {Object.entries(regions).map(([region, ufs]) => (
          <div key={region}>
            <p className="text-xs text-[var(--text-tertiary)] font-medium mb-2 uppercase tracking-wide">
              {region}
            </p>
            <SingleChoice
              options={ESTADO_OPTIONS.filter((o) => ufs.includes(o.value))}
              value={profile.estado}
              onChange={(value) => updateProfile({ estado: value })}
              columns={3}
              size="sm"
            />
          </div>
        ))}
      </div>

      {/* Continue button */}
      <button
        onClick={handleNext}
        disabled={!profile.estado}
        className={`
          w-full py-4 rounded-xl font-semibold text-white flex items-center justify-center gap-2 transition-all
          ${
            profile.estado
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
