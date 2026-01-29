/**
 * Types for the Eligibility Wizard
 */

export interface CitizenProfile {
  // Identificação
  cpf?: string;
  nome?: string;

  // Localização
  municipio?: string;
  uf?: string;
  cep?: string;

  // Composição familiar
  pessoasNaCasa: number;
  temFilhosMenores: boolean;
  quantidadeFilhos: number;
  temIdoso65Mais: boolean;
  temGestante: boolean;
  temPcd: boolean;

  // Renda
  rendaFamiliarMensal: number;

  // Benefícios atuais (se conhecidos)
  recebeBolsaFamilia: boolean;
  valorBolsaFamilia: number;
  recebeBpc: boolean;
  cadastradoCadunico: boolean;

  // Habitação
  temCasaPropria: boolean;

  // Trabalho histórico
  trabalhou1971_1988?: boolean;
}

export interface EligibilityResult {
  programa: string;
  programaNome: string;
  status: 'elegivel' | 'ja_recebe' | 'inelegivel' | 'inconclusivo';
  motivo: string;
  valorEstimado?: number;
  proximosPassos?: string[];
  documentosNecessarios?: string[];
  ondeSolicitar?: string;
  observacoes?: string;
}

export interface TriagemResult {
  beneficiosElegiveis: EligibilityResult[];
  beneficiosJaRecebe: EligibilityResult[];
  beneficiosInelegiveis: EligibilityResult[];
  beneficiosInconclusivos: EligibilityResult[];
  totalProgramasAnalisados: number;
  valorPotencialMensal: number;
  valorJaRecebeMensal: number;
  proximosPassosPrioritarios: string[];
  documentosNecessarios: string[];
}

export type WizardStep = 'basic' | 'family' | 'income' | 'special' | 'result';

export const WIZARD_STEPS: WizardStep[] = ['basic', 'family', 'income', 'special', 'result'];

export const STEP_TITLES: Record<WizardStep, string> = {
  basic: 'Dados Básicos',
  family: 'Família',
  income: 'Renda',
  special: 'Situação Especial',
  result: 'Seus Direitos',
};

export const DEFAULT_PROFILE: CitizenProfile = {
  pessoasNaCasa: 1,
  temFilhosMenores: false,
  quantidadeFilhos: 0,
  temIdoso65Mais: false,
  temGestante: false,
  temPcd: false,
  rendaFamiliarMensal: 0,
  recebeBolsaFamilia: false,
  valorBolsaFamilia: 0,
  recebeBpc: false,
  cadastradoCadunico: false,
  temCasaPropria: false,
};

// UFs brasileiras
export const UFS = [
  'AC', 'AL', 'AP', 'AM', 'BA', 'CE', 'DF', 'ES', 'GO', 'MA',
  'MT', 'MS', 'MG', 'PA', 'PB', 'PR', 'PE', 'PI', 'RJ', 'RN',
  'RS', 'RO', 'RR', 'SC', 'SP', 'SE', 'TO',
];

// Faixas de renda para seleção
export const FAIXAS_RENDA = [
  { label: 'Até R$ 300', value: 300 },
  { label: 'R$ 300 a R$ 600', value: 600 },
  { label: 'R$ 600 a R$ 1.200', value: 1200 },
  { label: 'R$ 1.200 a R$ 2.000', value: 2000 },
  { label: 'R$ 2.000 a R$ 3.000', value: 3000 },
  { label: 'Mais de R$ 3.000', value: 4000 },
];
