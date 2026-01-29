/**
 * EligibilityWizard - Wizard de triagem de elegibilidade
 *
 * Componente principal que guia o cidadão através de perguntas simples
 * para descobrir quais benefícios sociais ele pode ter direito.
 *
 * Uso:
 * ```tsx
 * import EligibilityWizard from '@/components/EligibilityWizard';
 *
 * <EligibilityWizard
 *   onComplete={(result) => console.log('Triagem completa:', result)}
 *   onGenerateCarta={(profile, result) => handleGenerateCarta(profile, result)}
 *   onFindCras={(profile) => handleFindCras(profile)}
 * />
 * ```
 */

export { default } from './EligibilityWizard';
export { default as EligibilityWizard } from './EligibilityWizard';

// Steps individuais (para uso customizado)
export { default as BasicInfoStep } from './steps/BasicInfoStep';
export { default as FamilyStep } from './steps/FamilyStep';
export { default as IncomeStep } from './steps/IncomeStep';
export { default as SpecialStep } from './steps/SpecialStep';

// Resultado
export { default as RightsWallet } from './results/RightsWallet';

// Types
export type {
  CitizenProfile,
  TriagemResult,
  EligibilityResult,
  WizardStep,
} from './types';

export {
  WIZARD_STEPS,
  STEP_TITLES,
  DEFAULT_PROFILE,
  UFS,
  FAIXAS_RENDA,
} from './types';
