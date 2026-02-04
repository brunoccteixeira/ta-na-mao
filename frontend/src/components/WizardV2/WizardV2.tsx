'use client';

/**
 * WizardV2 - Main wizard component
 *
 * Combines all parts: context, layout, step router
 */

import { WizardProvider, useWizard } from './WizardContext';
import WizardLayout from './WizardLayout';
import {
  StepEstado,
  StepCidade,
  StepNascimento,
  StepMoradia,
  StepFamilia,
  StepFilhos,
  StepTrabalho,
  StepRenda,
  StepBeneficios,
  StepEspecial,
  StepInteresses,
} from './steps';
import { ResultsDashboard } from './results';

// Step router component
function StepRouter() {
  const { currentStep } = useWizard();

  switch (currentStep.id) {
    case 'estado':
      return <StepEstado />;
    case 'cidade':
      return <StepCidade />;
    case 'nascimento':
      return <StepNascimento />;
    case 'moradia':
      return <StepMoradia />;
    case 'familia':
      return <StepFamilia />;
    case 'filhos':
      return <StepFilhos />;
    case 'trabalho':
      return <StepTrabalho />;
    case 'renda':
      return <StepRenda />;
    case 'beneficios':
      return <StepBeneficios />;
    case 'especial':
      return <StepEspecial />;
    case 'interesses':
      return <StepInteresses />;
    case 'resultado':
      return <ResultsDashboard />;
    default:
      return <StepEstado />;
  }
}

// Main component
export default function WizardV2() {
  return (
    <WizardProvider>
      <WizardLayout>
        <StepRouter />
      </WizardLayout>
    </WizardProvider>
  );
}
