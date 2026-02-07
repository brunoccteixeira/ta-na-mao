/**
 * Types for the Eligibility Wizard
 */

export interface CitizenProfile {
  // Identificação
  cpf?: string;
  nome?: string;

  // Localização
  municipio?: string;
  municipioIbge?: string;
  uf?: string;
  cep?: string;

  // Dados básicos
  idade?: number;

  // Composição familiar
  pessoasNaCasa: number;
  temFilhosMenores: boolean;
  quantidadeFilhos: number;
  temIdoso65Mais: boolean;
  temGestante: boolean;
  temPcd: boolean;
  temCrianca0a6: boolean;

  // Renda
  rendaFamiliarMensal: number;
  trabalhoFormal: boolean;

  // Benefícios atuais (se conhecidos)
  recebeBolsaFamilia: boolean;
  valorBolsaFamilia: number;
  recebeBpc: boolean;
  cadastradoCadunico: boolean;

  // Habitação
  temCasaPropria: boolean;
  moradiaZonaRural: boolean;

  // Trabalho histórico
  trabalhou1971_1988?: boolean;
  temCarteiraAssinada?: boolean;
  tempoCarteiraAssinada?: number;

  // Setorial/Profissão
  profissao?: string;
  temMei: boolean;
  trabalhaAplicativo: boolean;
  agricultorFamiliar: boolean;
  pescadorArtesanal: boolean;
  catadorReciclavel: boolean;
  trabalhadoraDomestica: boolean;

  // Especial
  mulherMenstruante?: boolean;
  estudante: boolean;
  redePublica: boolean;
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

export type WizardStep = 'basic' | 'family' | 'income' | 'work' | 'special' | 'result';

export const WIZARD_STEPS: WizardStep[] = ['basic', 'family', 'income', 'work', 'special', 'result'];

export const STEP_TITLES: Record<WizardStep, string> = {
  basic: 'Dados Básicos',
  family: 'Família',
  income: 'Renda',
  work: 'Trabalho',
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
  temCrianca0a6: false,
  rendaFamiliarMensal: 0,
  trabalhoFormal: false,
  recebeBolsaFamilia: false,
  valorBolsaFamilia: 0,
  recebeBpc: false,
  cadastradoCadunico: false,
  temCasaPropria: false,
  moradiaZonaRural: false,
  temMei: false,
  trabalhaAplicativo: false,
  agricultorFamiliar: false,
  pescadorArtesanal: false,
  catadorReciclavel: false,
  trabalhadoraDomestica: false,
  estudante: false,
  redePublica: false,
};

// Profissões disponíveis para seleção
export const PROFISSOES = [
  { value: '', label: 'Selecione...' },
  { value: 'empregado_formal', label: 'Empregado com carteira assinada' },
  { value: 'autonomo', label: 'Autônomo / Bico / Informal' },
  { value: 'mei', label: 'MEI - Microempreendedor Individual' },
  { value: 'pescador', label: 'Pescador artesanal' },
  { value: 'agricultor', label: 'Agricultor familiar' },
  { value: 'entregador', label: 'Entregador de aplicativo' },
  { value: 'motorista_app', label: 'Motorista de aplicativo' },
  { value: 'catador', label: 'Catador de recicláveis' },
  { value: 'domestica', label: 'Trabalhador(a) doméstico(a)' },
  { value: 'desempregado', label: 'Desempregado / Procurando emprego' },
  { value: 'aposentado', label: 'Aposentado / Pensionista' },
  { value: 'estudante', label: 'Estudante' },
  { value: 'do_lar', label: 'Do lar / Cuida da família' },
  { value: 'outro', label: 'Outro' },
];

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
