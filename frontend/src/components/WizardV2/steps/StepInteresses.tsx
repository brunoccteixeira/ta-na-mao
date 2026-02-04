'use client';

/**
 * Step 11: Interesses (para parceiros futuros)
 *
 * This is the last step before results
 */

import { useState } from 'react';
import { useWizard, WIZARD_STEPS } from '../WizardContext';
import MultiChoice from '../inputs/MultiChoice';
import ExplanationModal, { WhyButton } from '../ExplanationModal';
import { QUESTIONS, INTERESSES_OPTIONS } from '../../../data/questions';
import { Loader2, Sparkles, Zap, Pill, Home, Briefcase, BookOpen } from 'lucide-react';

export default function StepInteresses() {
  const { profile, updateProfile, goToStep, setSubmitting, isSubmitting } = useWizard();
  const [showExplanation, setShowExplanation] = useState(false);
  const [interesses, setInteresses] = useState<string[]>([]);
  const question = QUESTIONS.interesses;

  const icons: Record<string, React.ReactNode> = {
    luz: <Zap className="w-5 h-5" />,
    remedio: <Pill className="w-5 h-5" />,
    moradia: <Home className="w-5 h-5" />,
    emprego: <Briefcase className="w-5 h-5" />,
    capacitacao: <BookOpen className="w-5 h-5" />,
  };

  const optionsWithIcons = INTERESSES_OPTIONS.map((opt) => ({
    ...opt,
    icon: icons[opt.value],
  }));

  const handleInteressesChange = (values: string[]) => {
    setInteresses(values);
    updateProfile({
      interesseTarifaSocial: values.includes('luz'),
      usaMedicamentoContinuo: values.includes('remedio'),
      interesseHabitacao: values.includes('moradia'),
    });
  };

  const handleSubmit = async () => {
    setSubmitting(true);

    // Simulate processing time for UX
    await new Promise((resolve) => setTimeout(resolve, 1500));

    // Navigate to results
    const resultStepIndex = WIZARD_STEPS.findIndex((s) => s.id === 'resultado');
    goToStep(resultStepIndex);
    setSubmitting(false);
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

      {/* Interests options */}
      <div className="mb-6">
        <MultiChoice
          options={optionsWithIcons}
          values={interesses}
          onChange={handleInteressesChange}
          columns={1}
        />
      </div>

      {/* Summary before submit */}
      <div className="mb-6 p-4 bg-gradient-to-r from-emerald-50 to-teal-50 dark:from-emerald-500/10 dark:to-teal-500/10 rounded-xl border border-emerald-100 dark:border-emerald-500/20">
        <div className="flex items-center gap-3 mb-3">
          <div className="w-10 h-10 bg-emerald-500 rounded-full flex items-center justify-center">
            <Sparkles className="w-5 h-5 text-white" />
          </div>
          <div>
            <p className="font-semibold text-emerald-700 dark:text-emerald-400">
              Estamos quase lá!
            </p>
            <p className="text-xs text-emerald-600 dark:text-emerald-500">
              Vamos analisar mais de 200 benefícios para você
            </p>
          </div>
        </div>

        <div className="grid grid-cols-2 gap-2 text-xs">
          <div className="bg-white/50 dark:bg-white/5 rounded-lg p-2">
            <span className="text-[var(--text-tertiary)]">Estado:</span>{' '}
            <span className="font-medium text-[var(--text-primary)]">{profile.estado}</span>
          </div>
          <div className="bg-white/50 dark:bg-white/5 rounded-lg p-2">
            <span className="text-[var(--text-tertiary)]">Pessoas:</span>{' '}
            <span className="font-medium text-[var(--text-primary)]">{profile.pessoasNaCasa}</span>
          </div>
          <div className="bg-white/50 dark:bg-white/5 rounded-lg p-2">
            <span className="text-[var(--text-tertiary)]">Renda:</span>{' '}
            <span className="font-medium text-[var(--text-primary)]">
              R$ {profile.rendaFamiliarMensal?.toLocaleString('pt-BR') || '0'}
            </span>
          </div>
          <div className="bg-white/50 dark:bg-white/5 rounded-lg p-2">
            <span className="text-[var(--text-tertiary)]">Per capita:</span>{' '}
            <span className="font-medium text-[var(--text-primary)]">
              R$ {profile.pessoasNaCasa > 0
                ? Math.round(profile.rendaFamiliarMensal / profile.pessoasNaCasa).toLocaleString('pt-BR')
                : '0'
              }
            </span>
          </div>
        </div>
      </div>

      {/* Submit button */}
      <button
        onClick={handleSubmit}
        disabled={isSubmitting}
        className={`
          w-full py-4 rounded-xl font-semibold text-white flex items-center justify-center gap-2 transition-all
          ${
            isSubmitting
              ? 'bg-emerald-400 cursor-not-allowed'
              : 'bg-emerald-500 hover:bg-emerald-600'
          }
        `}
      >
        {isSubmitting ? (
          <>
            <Loader2 className="w-5 h-5 animate-spin" />
            Analisando benefícios...
          </>
        ) : (
          <>
            <Sparkles className="w-5 h-5" />
            Ver meus benefícios
          </>
        )}
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
