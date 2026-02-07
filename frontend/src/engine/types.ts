/**
 * Types for the Eligibility Engine and Benefits Catalog
 */

// ========== BENEFIT CATALOG TYPES ==========

export type BenefitScope = 'federal' | 'state' | 'municipal' | 'sectoral';

export type BenefitStatus = 'active' | 'suspended' | 'ended';

export type ValueType = 'monthly' | 'annual' | 'one_time';

export type RuleOperator = 'lte' | 'gte' | 'lt' | 'gt' | 'eq' | 'neq' | 'in' | 'not_in' | 'has' | 'not_has';

export type LegalBasisType = 'lei' | 'decreto' | 'portaria' | 'constituicao' | 'resolucao';

export interface LegalReference {
  type: LegalBasisType;
  number: string;       // "14.601/2023"
  description: string;  // "Lei do Bolsa Família"
  url?: string;         // planalto.gov.br link
}

export interface EstimatedValue {
  type: ValueType;
  min?: number;
  max?: number;
  description?: string;
  estimated?: boolean;
  estimatedRationale?: string;
}

export interface EligibilityRule {
  field: string;
  operator: RuleOperator;
  value: unknown;
  description: string;
  legalReference?: string;  // "Art. 3º, Lei 14.601/2023"
}

export interface Benefit {
  id: string;
  name: string;
  shortDescription: string;

  // Scope
  scope: BenefitScope;
  state?: string;                // UF code if state-level
  municipalityIbge?: string;     // IBGE code if municipal
  sector?: string;               // Sector if sectoral

  // Value
  estimatedValue?: EstimatedValue;

  // Eligibility
  eligibilityRules: EligibilityRule[];

  // Practical info
  whereToApply: string;
  documentsRequired: string[];
  howToApply?: string[];

  // Legal basis
  legalBasis?: { laws: LegalReference[] };

  // Metadata
  sourceUrl?: string;
  lastUpdated: string;
  status: BenefitStatus;

  // UI
  icon?: string;
  category?: string;
}

// ========== CITIZEN PROFILE (EXPANDED) ==========

export interface CitizenProfile {
  // Location
  estado: string;
  municipioIbge?: string;
  municipioNome?: string;

  // Basic info
  idade?: number;
  cpf?: string;
  nome?: string;
  cep?: string;

  // Family
  pessoasNaCasa: number;
  quantidadeFilhos: number;
  temIdoso65Mais: boolean;
  temGestante: boolean;
  temPcd: boolean;
  temCrianca0a6: boolean;

  // Income
  rendaFamiliarMensal: number;
  trabalhoFormal: boolean;

  // Housing
  temCasaPropria: boolean;
  moradiaZonaRural: boolean;

  // CadUnico and current benefits
  cadastradoCadunico: boolean;
  nisCadunico?: string;
  recebeBolsaFamilia: boolean;
  valorBolsaFamilia?: number;
  recebeBpc: boolean;

  // Work history
  trabalhou1971_1988?: boolean;
  temCarteiraAssinada?: boolean;
  tempoCarteiraAssinada?: number; // months
  fezSaqueFgts?: boolean;

  // Sectoral
  profissao?: string;
  temMei: boolean;
  trabalhaAplicativo: boolean;
  agricultorFamiliar: boolean;
  pescadorArtesanal: boolean;
  catadorReciclavel: boolean;
  trabalhadoraDomestica: boolean;

  // Special conditions
  mulherMenstruante?: boolean;
  idadeMulher?: number;

  // Education
  estudante: boolean;
  redePublica: boolean;
}

// ========== ELIGIBILITY RESULT TYPES ==========

export type EligibilityStatus =
  | 'eligible'           // Meets all criteria
  | 'likely_eligible'    // Meets most criteria, needs verification
  | 'maybe'              // Inconclusive, needs in-person check
  | 'not_eligible'       // Does not meet criteria
  | 'not_applicable'     // Benefit doesn't apply to region/sector
  | 'already_receiving'; // Already receiving this benefit

export interface EligibilityResult {
  benefit: Benefit;
  status: EligibilityStatus;
  matchedRules: string[];
  failedRules: string[];
  inconclusiveRules: string[];
  estimatedValue?: number;
  reason?: string;
}

export interface EvaluationSummary {
  eligible: EligibilityResult[];
  likelyEligible: EligibilityResult[];
  maybe: EligibilityResult[];
  notEligible: EligibilityResult[];
  notApplicable: EligibilityResult[];
  alreadyReceiving: EligibilityResult[];

  totalAnalyzed: number;
  totalPotentialMonthly: number;
  totalPotentialAnnual: number;
  totalPotentialOneTime: number;

  prioritySteps: string[];
  documentsNeeded: string[];
}

// ========== CATALOG INDEX TYPES ==========

export interface BenefitCatalog {
  federal: Benefit[];
  states: Record<string, Benefit[]>;
  sectoral: Benefit[];
  municipal?: Record<string, Benefit[]>;
}

// ========== CONSTANTS ==========

export const BRAZILIAN_STATES: Record<string, string> = {
  AC: 'Acre',
  AL: 'Alagoas',
  AP: 'Amapá',
  AM: 'Amazonas',
  BA: 'Bahia',
  CE: 'Ceará',
  DF: 'Distrito Federal',
  ES: 'Espírito Santo',
  GO: 'Goiás',
  MA: 'Maranhão',
  MT: 'Mato Grosso',
  MS: 'Mato Grosso do Sul',
  MG: 'Minas Gerais',
  PA: 'Pará',
  PB: 'Paraíba',
  PR: 'Paraná',
  PE: 'Pernambuco',
  PI: 'Piauí',
  RJ: 'Rio de Janeiro',
  RN: 'Rio Grande do Norte',
  RS: 'Rio Grande do Sul',
  RO: 'Rondônia',
  RR: 'Roraima',
  SC: 'Santa Catarina',
  SP: 'São Paulo',
  SE: 'Sergipe',
  TO: 'Tocantins',
};

export const SECTORS = {
  pescador: 'Pescador Artesanal',
  agricultor: 'Agricultor Familiar',
  entregador: 'Entregador de Aplicativo',
  motorista_app: 'Motorista de Aplicativo',
  catador: 'Catador de Recicláveis',
  mei: 'Microempreendedor Individual',
  domestica: 'Trabalhadora Doméstica',
  autonomo: 'Trabalhador Autônomo',
  clt: 'Trabalhador CLT',
  pcd: 'Pessoa com Deficiência',
};

export const MINIMUM_WAGE_2024 = 1412;
export const MINIMUM_WAGE_2025 = 1518;
export const MINIMUM_WAGE_2026 = 1621; // Decreto 12.797/2025

// Salário mínimo atual (atualizar anualmente)
export const MINIMUM_WAGE = MINIMUM_WAGE_2026;

// Per capita income thresholds (2026)
export const INCOME_THRESHOLDS = {
  extrema_pobreza: 218,            // R$ 218 per capita (valor fixo por lei)
  pobreza: 218,                    // Same for Bolsa Família
  bpc: MINIMUM_WAGE / 4,           // 1/4 minimum wage = R$ 400
  baixa_renda: MINIMUM_WAGE / 2,   // 1/2 minimum wage = R$ 800
  cadunico: MINIMUM_WAGE * 3,      // Up to 3x minimum wage = R$ 4.800
};

export const DEFAULT_CITIZEN_PROFILE: CitizenProfile = {
  estado: '',
  pessoasNaCasa: 1,
  quantidadeFilhos: 0,
  temIdoso65Mais: false,
  temGestante: false,
  temPcd: false,
  temCrianca0a6: false,
  rendaFamiliarMensal: 0,
  trabalhoFormal: false,
  temCasaPropria: false,
  moradiaZonaRural: false,
  cadastradoCadunico: false,
  recebeBolsaFamilia: false,
  recebeBpc: false,
  temMei: false,
  trabalhaAplicativo: false,
  agricultorFamiliar: false,
  pescadorArtesanal: false,
  catadorReciclavel: false,
  trabalhadoraDomestica: false,
  temCarteiraAssinada: false,
  estudante: false,
  redePublica: false,
};
