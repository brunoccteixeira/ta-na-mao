/**
 * Eligibility Engine - Evaluates citizen profiles against benefit rules
 */

import {
  Benefit,
  CitizenProfile,
  EligibilityRule,
  EligibilityResult,
  EligibilityStatus,
  EvaluationSummary,
} from './types';

/**
 * Calculate per capita income
 */
export function calcularRendaPerCapita(profile: CitizenProfile): number {
  const pessoas = Math.max(profile.pessoasNaCasa, 1);
  return profile.rendaFamiliarMensal / pessoas;
}

/**
 * Get a field value from the profile, including computed fields
 */
function getFieldValue(profile: CitizenProfile, field: string): unknown {
  // Computed fields
  if (field === 'rendaPerCapita') {
    return calcularRendaPerCapita(profile);
  }

  // Direct field access
  return (profile as unknown as Record<string, unknown>)[field];
}

/**
 * Evaluate a single rule against a profile
 */
function evaluateRule(
  profile: CitizenProfile,
  rule: EligibilityRule
): { passed: boolean; inconclusive: boolean; description: string } {
  const fieldValue = getFieldValue(profile, rule.field);

  // If the field is undefined/null, mark as inconclusive
  if (fieldValue === undefined || fieldValue === null) {
    return {
      passed: false,
      inconclusive: true,
      description: rule.description,
    };
  }

  const { operator, value } = rule;
  let passed = false;

  switch (operator) {
    case 'eq':
      passed = fieldValue === value;
      break;
    case 'neq':
      passed = fieldValue !== value;
      break;
    case 'lt':
      passed = (fieldValue as number) < (value as number);
      break;
    case 'lte':
      passed = (fieldValue as number) <= (value as number);
      break;
    case 'gt':
      passed = (fieldValue as number) > (value as number);
      break;
    case 'gte':
      passed = (fieldValue as number) >= (value as number);
      break;
    case 'in':
      passed = Array.isArray(value) && value.includes(fieldValue);
      break;
    case 'not_in':
      passed = Array.isArray(value) && !value.includes(fieldValue);
      break;
    case 'has':
      // Check if field has a truthy value
      passed = Boolean(fieldValue);
      break;
    case 'not_has':
      passed = !fieldValue;
      break;
    default:
      passed = false;
  }

  return {
    passed,
    inconclusive: false,
    description: rule.description,
  };
}

/**
 * Check if benefit applies to citizen's geographic location
 */
function matchesGeography(profile: CitizenProfile, benefit: Benefit): boolean {
  // Federal benefits apply everywhere
  if (benefit.scope === 'federal') {
    return true;
  }

  // State benefits require matching state
  if (benefit.scope === 'state') {
    return benefit.state === profile.estado;
  }

  // Municipal benefits require matching municipality
  if (benefit.scope === 'municipal') {
    return benefit.municipalityIbge === profile.municipioIbge;
  }

  // Sectoral benefits may have geographic restrictions
  if (benefit.scope === 'sectoral') {
    // If no state restriction, applies everywhere
    if (!benefit.state) return true;
    return benefit.state === profile.estado;
  }

  return false;
}

/**
 * Check if benefit applies to citizen's sector/profession
 */
function matchesSector(profile: CitizenProfile, benefit: Benefit): boolean {
  if (benefit.scope !== 'sectoral' || !benefit.sector) {
    return true;
  }

  const sectorMap: Record<string, keyof CitizenProfile> = {
    pescador: 'pescadorArtesanal',
    agricultor: 'agricultorFamiliar',
    entregador: 'trabalhaAplicativo',
    motorista_app: 'trabalhaAplicativo',
    catador: 'catadorReciclavel',
    mei: 'temMei',
    autonomo: 'temMei', // MEI is a form of autonomo
    pcd: 'temPcd',
  };

  const profileField = sectorMap[benefit.sector];
  if (!profileField) return true;

  return Boolean(profile[profileField]);
}

/**
 * Calculate estimated value for a benefit based on profile
 */
function calculateEstimatedValue(
  profile: CitizenProfile,
  benefit: Benefit
): number | undefined {
  if (!benefit.estimatedValue) return undefined;

  const { min, max } = benefit.estimatedValue;

  // For benefits with variable values, try to estimate based on profile
  if (benefit.id === 'federal-bolsa-familia') {
    // Bolsa Família: R$ 142 base + R$ 150 por criança até 6 anos + R$ 50 por criança 7-18
    let valor = 142; // Benefício de Renda de Cidadania
    if (profile.temCrianca0a6) valor += 150 * Math.min(profile.quantidadeFilhos, 3);
    if (profile.quantidadeFilhos > 0) valor += 50 * profile.quantidadeFilhos;
    if (profile.temGestante) valor += 50;
    return Math.min(valor, max || 900);
  }

  if (benefit.id === 'federal-abono-salarial') {
    // Proporcional aos meses trabalhados (assume 12 meses)
    return max || 1412;
  }

  // Default to average or min
  if (min && max) {
    return Math.round((min + max) / 2);
  }

  return min || max;
}

/**
 * Check if citizen is already receiving this benefit
 */
function isAlreadyReceiving(profile: CitizenProfile, benefit: Benefit): boolean {
  if (benefit.id === 'federal-bolsa-familia' && profile.recebeBolsaFamilia) {
    return true;
  }
  if ((benefit.id === 'federal-bpc-idoso' || benefit.id === 'federal-bpc-pcd') && profile.recebeBpc) {
    return true;
  }
  return false;
}

/**
 * Evaluate a single benefit against a citizen profile
 */
export function evaluateBenefit(
  profile: CitizenProfile,
  benefit: Benefit
): EligibilityResult {
  // Check if already receiving
  if (isAlreadyReceiving(profile, benefit)) {
    return {
      benefit,
      status: 'already_receiving',
      matchedRules: [],
      failedRules: [],
      inconclusiveRules: [],
      reason: 'Você já recebe este benefício',
    };
  }

  // Check geographic scope
  if (!matchesGeography(profile, benefit)) {
    return {
      benefit,
      status: 'not_applicable',
      matchedRules: [],
      failedRules: [],
      inconclusiveRules: [],
      reason: `Não disponível em ${profile.estado || 'sua região'}`,
    };
  }

  // Check sector scope
  if (!matchesSector(profile, benefit)) {
    return {
      benefit,
      status: 'not_applicable',
      matchedRules: [],
      failedRules: [],
      inconclusiveRules: [],
      reason: 'Não se aplica à sua profissão',
    };
  }

  // Evaluate all eligibility rules
  const matchedRules: string[] = [];
  const failedRules: string[] = [];
  const inconclusiveRules: string[] = [];

  for (const rule of benefit.eligibilityRules) {
    const result = evaluateRule(profile, rule);

    if (result.inconclusive) {
      inconclusiveRules.push(result.description);
    } else if (result.passed) {
      matchedRules.push(result.description);
    } else {
      failedRules.push(result.description);
    }
  }

  // Determine status based on rule results
  let status: EligibilityStatus;
  let reason: string | undefined;

  if (failedRules.length === 0 && inconclusiveRules.length === 0) {
    status = 'eligible';
    reason = 'Você atende a todos os requisitos';
  } else if (failedRules.length === 0 && inconclusiveRules.length > 0) {
    status = 'likely_eligible';
    reason = 'Provavelmente elegível, verificar presencialmente';
  } else if (failedRules.length <= 1 && inconclusiveRules.length > 0) {
    status = 'maybe';
    reason = 'Pode ter direito, verificar no CRAS';
  } else {
    status = 'not_eligible';
    reason = failedRules[0] || 'Não atende aos requisitos';
  }

  return {
    benefit,
    status,
    matchedRules,
    failedRules,
    inconclusiveRules,
    estimatedValue: status === 'eligible' || status === 'likely_eligible'
      ? calculateEstimatedValue(profile, benefit)
      : undefined,
    reason,
  };
}

/**
 * Evaluate all benefits in a catalog against a citizen profile
 */
export function evaluateAllBenefits(
  profile: CitizenProfile,
  benefits: Benefit[]
): EvaluationSummary {
  const results = benefits.map(benefit => evaluateBenefit(profile, benefit));

  const eligible = results.filter(r => r.status === 'eligible');
  const likelyEligible = results.filter(r => r.status === 'likely_eligible');
  const maybe = results.filter(r => r.status === 'maybe');
  const notEligible = results.filter(r => r.status === 'not_eligible');
  const notApplicable = results.filter(r => r.status === 'not_applicable');
  const alreadyReceiving = results.filter(r => r.status === 'already_receiving');

  // Calculate potential values
  const calculateTotal = (
    results: EligibilityResult[],
    valueType: 'monthly' | 'annual' | 'one_time'
  ): number => {
    return results.reduce((sum, r) => {
      if (r.benefit.estimatedValue?.type === valueType && r.estimatedValue) {
        return sum + r.estimatedValue;
      }
      return sum;
    }, 0);
  };

  const eligibleAndLikely = [...eligible, ...likelyEligible];
  const totalPotentialMonthly = calculateTotal(eligibleAndLikely, 'monthly');
  const totalPotentialAnnual = calculateTotal(eligibleAndLikely, 'annual');
  const totalPotentialOneTime = calculateTotal(eligibleAndLikely, 'one_time');

  // Collect all required documents
  const documentsNeeded = new Set<string>();
  eligibleAndLikely.forEach(r => {
    r.benefit.documentsRequired.forEach(doc => documentsNeeded.add(doc));
  });

  // Generate priority steps
  const prioritySteps: string[] = [];

  if (!profile.cadastradoCadunico && eligibleAndLikely.some(r =>
    r.benefit.eligibilityRules.some(rule => rule.field === 'cadastradoCadunico')
  )) {
    prioritySteps.push('Faça ou atualize seu Cadastro Único no CRAS');
  }

  if (eligible.length > 0) {
    const topBenefit = eligible[0];
    prioritySteps.push(`Solicite o ${topBenefit.benefit.name} - ${topBenefit.benefit.whereToApply}`);
  }

  if (likelyEligible.length > 0) {
    prioritySteps.push('Vá ao CRAS para verificar outros benefícios possíveis');
  }

  return {
    eligible,
    likelyEligible,
    maybe,
    notEligible,
    notApplicable,
    alreadyReceiving,
    totalAnalyzed: results.length,
    totalPotentialMonthly,
    totalPotentialAnnual,
    totalPotentialOneTime,
    prioritySteps,
    documentsNeeded: Array.from(documentsNeeded),
  };
}

/**
 * Get benefits filtered by scope
 */
export function filterBenefitsByScope(
  benefits: Benefit[],
  scope: 'federal' | 'state' | 'municipal' | 'sectoral'
): Benefit[] {
  return benefits.filter(b => b.scope === scope);
}

/**
 * Get benefits filtered by state
 */
export function filterBenefitsByState(
  benefits: Benefit[],
  state: string
): Benefit[] {
  return benefits.filter(b =>
    b.scope === 'federal' ||
    (b.scope === 'state' && b.state === state) ||
    (b.scope === 'sectoral' && (!b.state || b.state === state))
  );
}

/**
 * Search benefits by text
 */
export function searchBenefits(
  benefits: Benefit[],
  query: string
): Benefit[] {
  const normalizedQuery = query.toLowerCase().trim();
  if (!normalizedQuery) return benefits;

  return benefits.filter(b =>
    b.name.toLowerCase().includes(normalizedQuery) ||
    b.shortDescription.toLowerCase().includes(normalizedQuery) ||
    b.category?.toLowerCase().includes(normalizedQuery)
  );
}

/**
 * Sort benefits by estimated value (highest first)
 */
export function sortBenefitsByValue(benefits: Benefit[]): Benefit[] {
  return [...benefits].sort((a, b) => {
    const aValue = a.estimatedValue?.max || a.estimatedValue?.min || 0;
    const bValue = b.estimatedValue?.max || b.estimatedValue?.min || 0;
    return bValue - aValue;
  });
}

/**
 * Group benefits by category
 */
export function groupBenefitsByCategory(
  benefits: Benefit[]
): Record<string, Benefit[]> {
  return benefits.reduce((groups, benefit) => {
    const category = benefit.category || 'Outros';
    if (!groups[category]) {
      groups[category] = [];
    }
    groups[category].push(benefit);
    return groups;
  }, {} as Record<string, Benefit[]>);
}

/**
 * Group results by scope for display
 */
export function groupResultsByScope(
  results: EligibilityResult[]
): {
  federal: EligibilityResult[];
  state: EligibilityResult[];
  municipal: EligibilityResult[];
  sectoral: EligibilityResult[];
} {
  return {
    federal: results.filter(r => r.benefit.scope === 'federal'),
    state: results.filter(r => r.benefit.scope === 'state'),
    municipal: results.filter(r => r.benefit.scope === 'municipal'),
    sectoral: results.filter(r => r.benefit.scope === 'sectoral'),
  };
}
