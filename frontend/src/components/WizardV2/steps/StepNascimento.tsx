'use client';

/**
 * Step 3: Data de Nascimento
 */

import { useState, useMemo } from 'react';
import { useWizard } from '../WizardContext';
import DateSelect from '../inputs/DateSelect';
import ExplanationModal, { WhyButton } from '../ExplanationModal';
import { QUESTIONS } from '../../../data/questions';
import { ArrowRight } from 'lucide-react';

export default function StepNascimento() {
  const { profile, updateProfile, nextStep } = useWizard();
  const [showExplanation, setShowExplanation] = useState(false);
  const question = QUESTIONS.nascimento;

  // Calculate age
  const age = useMemo(() => {
    const { diaNascimento, mesNascimento, anoNascimento } = profile;
    if (!diaNascimento || !mesNascimento || !anoNascimento) return null;

    const birthDate = new Date(anoNascimento, mesNascimento - 1, diaNascimento);
    const today = new Date();
    let age = today.getFullYear() - birthDate.getFullYear();
    const monthDiff = today.getMonth() - birthDate.getMonth();

    if (monthDiff < 0 || (monthDiff === 0 && today.getDate() < birthDate.getDate())) {
      age--;
    }

    return age;
  }, [profile.diaNascimento, profile.mesNascimento, profile.anoNascimento]);

  const handleNext = () => {
    if (age !== null && age >= 0) {
      updateProfile({ idade: age });
      nextStep();
    }
  };

  const isValid = age !== null && age >= 0 && age < 130;

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

      {/* Date select */}
      <div className="mb-6">
        <DateSelect
          day={profile.diaNascimento}
          month={profile.mesNascimento}
          year={profile.anoNascimento}
          onChangeDay={(day) => updateProfile({ diaNascimento: day })}
          onChangeMonth={(month) => updateProfile({ mesNascimento: month })}
          onChangeYear={(year) => updateProfile({ anoNascimento: year })}
        />
      </div>

      {/* Continue button */}
      <button
        onClick={handleNext}
        disabled={!isValid}
        className={`
          w-full py-4 rounded-xl font-semibold text-white flex items-center justify-center gap-2 transition-all
          ${
            isValid
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
