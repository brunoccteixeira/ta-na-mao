'use client';

/**
 * Step 10: Situações especiais
 */

import { useState } from 'react';
import { useWizard } from '../WizardContext';
import YesNo from '../inputs/YesNo';
import ExplanationModal, { WhyButton } from '../ExplanationModal';
import { QUESTIONS } from '../../../data/questions';
import { ArrowRight, Accessibility, Baby, GraduationCap, Shield } from 'lucide-react';

export default function StepEspecial() {
  const { profile, updateProfile, nextStep } = useWizard();
  const [showExplanation, setShowExplanation] = useState(false);
  const question = QUESTIONS.especial;

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

      {/* PCD */}
      <div className="mb-6 p-4 bg-[var(--bg-primary)] rounded-xl">
        <div className="flex items-start gap-3 mb-3">
          <div className="w-10 h-10 bg-blue-100 dark:bg-blue-500/20 rounded-lg flex items-center justify-center flex-shrink-0">
            <Accessibility className="w-5 h-5 text-blue-600" />
          </div>
          <div>
            <label className="block text-sm font-medium text-[var(--text-primary)]">
              Alguém na casa tem deficiência?
            </label>
            <p className="text-xs text-[var(--text-tertiary)] mt-0.5">
              Física, mental, intelectual ou sensorial
            </p>
          </div>
        </div>
        <YesNo
          value={profile.temPcd}
          onChange={(value) => updateProfile({ temPcd: value ?? false })}
        />
        {profile.temPcd && (
          <p className="mt-2 text-xs text-blue-600">
            Pessoas com deficiência podem ter direito ao BPC (R$ 1.621/mês), Passe Livre e outros benefícios
          </p>
        )}
      </div>

      {/* Student */}
      <div className="mb-6 p-4 bg-[var(--bg-primary)] rounded-xl">
        <div className="flex items-start gap-3 mb-3">
          <div className="w-10 h-10 bg-purple-100 dark:bg-purple-500/20 rounded-lg flex items-center justify-center flex-shrink-0">
            <GraduationCap className="w-5 h-5 text-purple-600" />
          </div>
          <div>
            <label className="block text-sm font-medium text-[var(--text-primary)]">
              Alguém na família é estudante?
            </label>
            <p className="text-xs text-[var(--text-tertiary)] mt-0.5">
              Escola, faculdade ou curso técnico
            </p>
          </div>
        </div>
        {profile.estudante ? (
          <p className="text-sm text-purple-600 font-medium">
            Você já informou que é estudante
          </p>
        ) : (
          <YesNo
            value={profile.estudante}
            onChange={(value) => updateProfile({ estudante: value ?? false })}
          />
        )}

        {/* Public school sub-question */}
        {profile.estudante && (
          <div className="mt-4 pt-4 border-t border-[var(--border-color)]">
            <label className="block text-sm font-medium text-[var(--text-primary)] mb-3">
              Estuda em escola/faculdade pública?
            </label>
            <YesNo
              value={profile.redePublica}
              onChange={(value) => updateProfile({ redePublica: value ?? false })}
            />
            {profile.redePublica && (
              <p className="mt-2 text-xs text-purple-600">
                Estudantes de escolas públicas têm acesso ao Pé-de-Meia (poupança de R$ 3.000)
              </p>
            )}
          </div>
        )}
      </div>

      {/* Women - menstrual dignity (only if there are women in the house) */}
      <div className="mb-6 p-4 bg-[var(--bg-primary)] rounded-xl">
        <div className="flex items-start gap-3 mb-3">
          <div className="w-10 h-10 bg-pink-100 dark:bg-pink-500/20 rounded-lg flex items-center justify-center flex-shrink-0">
            <Baby className="w-5 h-5 text-pink-600" />
          </div>
          <div>
            <label className="block text-sm font-medium text-[var(--text-primary)]">
              Há mulheres de 10 a 49 anos na casa?
            </label>
            <p className="text-xs text-[var(--text-tertiary)] mt-0.5">
              Para verificar Dignidade Menstrual
            </p>
          </div>
        </div>
        <YesNo
          value={profile.mulherMenstruante}
          onChange={(value) => updateProfile({ mulherMenstruante: value ?? false })}
        />
        {profile.mulherMenstruante && (
          <p className="mt-2 text-xs text-pink-600">
            Mulheres em situação de vulnerabilidade têm direito a absorventes gratuitos pelo SUS
          </p>
        )}
      </div>

      {/* Victim of violence (important for priority) */}
      <div className="mb-6 p-4 bg-[var(--bg-primary)] rounded-xl">
        <div className="flex items-start gap-3 mb-3">
          <div className="w-10 h-10 bg-red-100 dark:bg-red-500/20 rounded-lg flex items-center justify-center flex-shrink-0">
            <Shield className="w-5 h-5 text-red-600" />
          </div>
          <div>
            <label className="block text-sm font-medium text-[var(--text-primary)]">
              Vítima de violência doméstica?
            </label>
            <p className="text-xs text-[var(--text-tertiary)] mt-0.5">
              Informação usada apenas para priorizar atendimento
            </p>
          </div>
        </div>
        <YesNo
          value={undefined}
          onChange={() => {
            // We don't store this in profile, just for priority
          }}
        />
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
