'use client';

/**
 * Step 7: Trabalho
 */

import { useState } from 'react';
import { useWizard } from '../WizardContext';
import SingleChoice from '../inputs/SingleChoice';
import MultiChoice from '../inputs/MultiChoice';
import ExplanationModal, { WhyButton } from '../ExplanationModal';
import { QUESTIONS, TRABALHO_OPTIONS, SETORIAL_OPTIONS } from '../../../data/questions';
import { ArrowRight, Briefcase, Store, Wrench, Car, UserX, Heart, Home, GraduationCap } from 'lucide-react';

export default function StepTrabalho() {
  const { updateProfile, nextStep } = useWizard();
  const [showExplanation, setShowExplanation] = useState(false);
  const [trabalho, setTrabalho] = useState<string | undefined>();
  const [setorial, setSetorial] = useState<string[]>([]);
  const question = QUESTIONS.trabalho;

  const icons: Record<string, React.ReactNode> = {
    clt: <Briefcase className="w-5 h-5" />,
    mei: <Store className="w-5 h-5" />,
    autonomo: <Wrench className="w-5 h-5" />,
    app: <Car className="w-5 h-5" />,
    desempregado: <UserX className="w-5 h-5" />,
    aposentado: <Heart className="w-5 h-5" />,
    do_lar: <Home className="w-5 h-5" />,
    estudante: <GraduationCap className="w-5 h-5" />,
  };

  const optionsWithIcons = TRABALHO_OPTIONS.map((opt) => ({
    ...opt,
    icon: icons[opt.value],
  }));

  const handleTrabalhoChange = (value: string) => {
    setTrabalho(value);

    // Map to profile fields
    updateProfile({
      trabalhoFormal: value === 'clt',
      temMei: value === 'mei',
      trabalhaAplicativo: value === 'app',
      estudante: value === 'estudante',
    });
  };

  const handleSetorialChange = (values: string[]) => {
    setSetorial(values);
    updateProfile({
      agricultorFamiliar: values.includes('agricultor'),
      pescadorArtesanal: values.includes('pescador'),
      catadorReciclavel: values.includes('catador'),
    });
  };

  const handleNext = () => {
    if (trabalho) {
      nextStep();
    }
  };

  // Show sectoral options for certain work types
  const showSetorial = trabalho && ['autonomo', 'desempregado', 'do_lar'].includes(trabalho);

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

      {/* Work type */}
      <div className="mb-6">
        <SingleChoice
          options={optionsWithIcons}
          value={trabalho}
          onChange={handleTrabalhoChange}
          columns={2}
        />
      </div>

      {/* Sectoral options (conditional) */}
      {showSetorial && (
        <div className="mb-6 animate-fadeIn">
          <label className="block text-sm font-medium text-[var(--text-primary)] mb-3">
            Você também trabalha com alguma dessas atividades? (opcional)
          </label>
          <MultiChoice
            options={SETORIAL_OPTIONS}
            values={setorial}
            onChange={handleSetorialChange}
            columns={1}
          />
        </div>
      )}

      {/* Hints based on selection */}
      {trabalho && (
        <div className="mb-6 p-4 bg-emerald-50 dark:bg-emerald-500/10 rounded-xl">
          <p className="text-sm text-emerald-700 dark:text-emerald-400">
            {trabalho === 'clt' && 'Você pode ter direito ao abono salarial PIS/PASEP e FGTS'}
            {trabalho === 'mei' && 'MEIs podem receber Bolsa Família se a renda for baixa'}
            {trabalho === 'autonomo' && 'Trabalhadores informais podem se cadastrar no CadÚnico'}
            {trabalho === 'app' && 'Motoristas e entregadores de app têm direitos trabalhistas específicos'}
            {trabalho === 'desempregado' && 'Você pode ter direito ao seguro-desemprego ou Bolsa Família'}
            {trabalho === 'aposentado' && 'Verifique se você tem direito ao BPC ou outros benefícios'}
            {trabalho === 'do_lar' && 'Pessoas que cuidam da casa podem se cadastrar no CadÚnico'}
            {trabalho === 'estudante' && 'Estudantes podem ter acesso a bolsas e auxílios'}
          </p>
        </div>
      )}

      {/* Continue button */}
      <button
        onClick={handleNext}
        disabled={!trabalho}
        className={`
          w-full py-4 rounded-xl font-semibold text-white flex items-center justify-center gap-2 transition-all
          ${
            trabalho
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
