'use client';

/**
 * Step 9: Benefícios já recebidos
 */

import { useState } from 'react';
import { useWizard } from '../WizardContext';
import YesNo from '../inputs/YesNo';
import MultiChoice from '../inputs/MultiChoice';
import ExplanationModal, { WhyButton } from '../ExplanationModal';
import { QUESTIONS } from '../../../data/questions';
import { ArrowRight } from 'lucide-react';

export default function StepBeneficios() {
  const { profile, updateProfile, nextStep } = useWizard();
  const [showExplanation, setShowExplanation] = useState(false);
  const question = QUESTIONS.beneficios;

  // Track current benefits
  const [beneficiosAtuais, setBeneficiosAtuais] = useState<string[]>(() => {
    const initial: string[] = [];
    if (profile.recebeBolsaFamilia) initial.push('bolsa_familia');
    if (profile.recebeBpc) initial.push('bpc');
    if (profile.cadastradoCadunico) initial.push('cadunico');
    return initial;
  });

  const beneficiosOptions = [
    { value: 'bolsa_familia', label: 'Bolsa Família', description: 'Benefício mensal' },
    { value: 'bpc', label: 'BPC/LOAS', description: 'Benefício de Prestação Continuada' },
    { value: 'aposentadoria', label: 'Aposentadoria/Pensão', description: 'INSS' },
    { value: 'seguro_desemprego', label: 'Seguro-Desemprego', description: 'Temporário' },
    { value: 'auxilio_gas', label: 'Auxílio Gás', description: 'A cada 2 meses' },
    { value: 'tarifa_social', label: 'Tarifa Social de Energia', description: 'Desconto na luz' },
  ];

  const handleBeneficiosChange = (values: string[]) => {
    setBeneficiosAtuais(values);
    updateProfile({
      recebeBolsaFamilia: values.includes('bolsa_familia'),
      recebeBpc: values.includes('bpc'),
    });
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

      {/* CadÚnico question */}
      <div className="mb-6">
        <label className="block text-sm font-medium text-[var(--text-primary)] mb-3">
          Sua família está inscrita no CadÚnico?
        </label>
        <YesNo
          value={profile.cadastradoCadunico}
          onChange={(value) => updateProfile({ cadastradoCadunico: value ?? false })}
          showUnsure
        />
        {profile.cadastradoCadunico === false && (
          <p className="mt-2 text-xs text-amber-600">
            O CadÚnico é porta de entrada para a maioria dos benefícios sociais.
            Procure o CRAS mais próximo para se cadastrar.
          </p>
        )}
      </div>

      {/* Current benefits */}
      <div className="mb-6">
        <label className="block text-sm font-medium text-[var(--text-primary)] mb-3">
          Quais benefícios você já recebe? (se houver)
        </label>
        <MultiChoice
          options={beneficiosOptions}
          values={beneficiosAtuais}
          onChange={handleBeneficiosChange}
          columns={1}
        />
      </div>

      {/* Info about Bolsa Família value */}
      {profile.recebeBolsaFamilia && (
        <div className="mb-6 p-4 bg-emerald-50 dark:bg-emerald-500/10 rounded-xl">
          <p className="text-sm text-emerald-700 dark:text-emerald-400">
            Você recebe Bolsa Família. Vamos verificar se você tem direito a valores adicionais
            ou outros benefícios complementares.
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
