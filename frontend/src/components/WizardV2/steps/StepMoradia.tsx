'use client';

/**
 * Step 4: Moradia
 */

import { useState } from 'react';
import { useWizard } from '../WizardContext';
import SingleChoice from '../inputs/SingleChoice';
import YesNo from '../inputs/YesNo';
import ExplanationModal, { WhyButton } from '../ExplanationModal';
import { QUESTIONS, MORADIA_OPTIONS } from '../../../data/questions';
import { ArrowRight, Home, Building, Users, AlertTriangle, MapPin } from 'lucide-react';

export default function StepMoradia() {
  const { profile, updateProfile, nextStep } = useWizard();
  const [showExplanation, setShowExplanation] = useState(false);
  const [moradia, setMoradia] = useState<string | undefined>(
    profile.temCasaPropria ? 'propria' : undefined
  );
  const question = QUESTIONS.moradia;

  const optionsWithIcons = MORADIA_OPTIONS.map((opt) => ({
    ...opt,
    icon: {
      propria: <Home className="w-5 h-5" />,
      alugada: <Building className="w-5 h-5" />,
      cedida: <Users className="w-5 h-5" />,
      irregular: <AlertTriangle className="w-5 h-5" />,
      rua: <MapPin className="w-5 h-5" />,
    }[opt.value],
  }));

  const handleMoradiaChange = (value: string) => {
    setMoradia(value);
    updateProfile({
      temCasaPropria: value === 'propria',
    });
  };

  const handleNext = () => {
    if (moradia) {
      nextStep();
    }
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

      {/* Moradia type */}
      <div className="mb-6">
        <SingleChoice
          options={optionsWithIcons}
          value={moradia}
          onChange={handleMoradiaChange}
          columns={1}
        />
      </div>

      {/* Zona rural question */}
      <div className="mb-6">
        <label className="block text-sm font-medium text-[var(--text-primary)] mb-3">
          Você mora em zona rural?
        </label>
        <YesNo
          value={profile.moradiaZonaRural}
          onChange={(value) => updateProfile({ moradiaZonaRural: value ?? false })}
        />
      </div>

      {/* Continue button */}
      <button
        onClick={handleNext}
        disabled={!moradia}
        className={`
          w-full py-4 rounded-xl font-semibold text-white flex items-center justify-center gap-2 transition-all
          ${
            moradia
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
