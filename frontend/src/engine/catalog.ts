/**
 * Benefits Catalog Loader
 * Loads and manages the benefits catalog from JSON files
 */

import { Benefit, BenefitCatalog, BRAZILIAN_STATES } from './types';

// Import federal benefits
import federalData from '../data/benefits/federal.json';
import sectoralData from '../data/benefits/sectoral.json';

// Import state benefits - dynamic loading
const stateModules = import.meta.glob('../data/benefits/states/*.json', { eager: true });

// Import municipal benefits - dynamic loading by IBGE code
const municipalModules = import.meta.glob('../data/benefits/municipalities/*.json', { eager: true });

/**
 * Load all benefits from the catalog
 */
export function loadBenefitsCatalog(): BenefitCatalog {
  // Load federal benefits
  const federal = (federalData as { benefits: Benefit[] }).benefits;

  // Load sectoral benefits
  const sectoral = (sectoralData as { benefits: Benefit[] }).benefits;

  // Load state benefits
  const states: Record<string, Benefit[]> = {};

  for (const [path, module] of Object.entries(stateModules)) {
    // Extract state code from path (e.g., '../data/benefits/states/sp.json' -> 'SP')
    const match = path.match(/\/([a-z]{2})\.json$/i);
    if (match) {
      const stateCode = match[1].toUpperCase();
      const stateData = module as { benefits: Benefit[] };
      states[stateCode] = stateData.benefits || [];
    }
  }

  // Load municipal benefits by IBGE code
  const municipal: Record<string, Benefit[]> = {};

  for (const [path, module] of Object.entries(municipalModules)) {
    // Extract IBGE code from path (e.g., '../data/benefits/municipalities/3550308.json' -> '3550308')
    const match = path.match(/\/(\d+)\.json$/);
    if (match) {
      const ibgeCode = match[1];
      const municipalData = module as { benefits: Benefit[] };
      municipal[ibgeCode] = municipalData.benefits || [];
    }
  }

  return {
    federal,
    states,
    sectoral,
    municipal,
  };
}

/**
 * Get all benefits as a flat array
 */
export function getAllBenefits(catalog: BenefitCatalog): Benefit[] {
  const allBenefits: Benefit[] = [
    ...catalog.federal,
    ...catalog.sectoral,
  ];

  // Add all state benefits
  for (const stateBenefits of Object.values(catalog.states)) {
    allBenefits.push(...stateBenefits);
  }

  // Add all municipal benefits
  if (catalog.municipal) {
    for (const municipalBenefits of Object.values(catalog.municipal)) {
      allBenefits.push(...municipalBenefits);
    }
  }

  return allBenefits;
}

/**
 * Get benefits relevant to a specific state
 * Returns federal + state-specific + applicable sectoral benefits
 */
export function getBenefitsForState(
  catalog: BenefitCatalog,
  stateCode: string
): Benefit[] {
  const upperState = stateCode.toUpperCase();

  const benefits: Benefit[] = [
    ...catalog.federal,
    ...(catalog.states[upperState] || []),
    ...catalog.sectoral.filter(b => !b.state || b.state === upperState),
  ];

  return benefits;
}

/**
 * Get benefits relevant to a specific municipality
 * Returns federal + state + municipal + applicable sectoral benefits
 */
export function getBenefitsForMunicipality(
  catalog: BenefitCatalog,
  stateCode: string,
  ibgeCode: string
): Benefit[] {
  const upperState = stateCode.toUpperCase();

  const benefits: Benefit[] = [
    ...catalog.federal,
    ...(catalog.states[upperState] || []),
    ...(catalog.municipal?.[ibgeCode] || []),
    ...catalog.sectoral.filter(b => !b.state || b.state === upperState),
  ];

  return benefits;
}

/**
 * Get list of municipalities that have benefits registered
 */
export function getMunicipalitiesWithBenefits(catalog: BenefitCatalog): string[] {
  if (!catalog.municipal) return [];
  return Object.keys(catalog.municipal).filter(
    ibge => catalog.municipal![ibge].length > 0
  );
}

/**
 * Get a single benefit by ID
 */
export function getBenefitById(
  catalog: BenefitCatalog,
  benefitId: string
): Benefit | undefined {
  // Search in federal
  let benefit = catalog.federal.find(b => b.id === benefitId);
  if (benefit) return benefit;

  // Search in sectoral
  benefit = catalog.sectoral.find(b => b.id === benefitId);
  if (benefit) return benefit;

  // Search in all states
  for (const stateBenefits of Object.values(catalog.states)) {
    benefit = stateBenefits.find(b => b.id === benefitId);
    if (benefit) return benefit;
  }

  // Search in all municipalities
  if (catalog.municipal) {
    for (const municipalBenefits of Object.values(catalog.municipal)) {
      benefit = municipalBenefits.find(b => b.id === benefitId);
      if (benefit) return benefit;
    }
  }

  return undefined;
}

/**
 * Get benefits by scope
 */
export function getBenefitsByScope(
  catalog: BenefitCatalog,
  scope: 'federal' | 'state' | 'municipal' | 'sectoral'
): Benefit[] {
  switch (scope) {
    case 'federal':
      return catalog.federal;
    case 'sectoral':
      return catalog.sectoral;
    case 'state':
      // Return all state benefits combined
      return Object.values(catalog.states).flat();
    case 'municipal':
      // Return all municipal benefits combined
      return catalog.municipal ? Object.values(catalog.municipal).flat() : [];
    default:
      return [];
  }
}

/**
 * Get list of states that have benefits registered
 */
export function getStatesWithBenefits(catalog: BenefitCatalog): string[] {
  return Object.keys(catalog.states).filter(
    state => catalog.states[state].length > 0
  );
}

/**
 * Get catalog statistics
 */
export function getCatalogStats(catalog: BenefitCatalog): {
  totalBenefits: number;
  federalCount: number;
  stateCount: number;
  municipalCount: number;
  sectoralCount: number;
  statesWithBenefits: number;
  municipalitiesWithBenefits: number;
  benefitsByCategory: Record<string, number>;
} {
  const allBenefits = getAllBenefits(catalog);

  const benefitsByCategory: Record<string, number> = {};
  for (const benefit of allBenefits) {
    const category = benefit.category || 'Outros';
    benefitsByCategory[category] = (benefitsByCategory[category] || 0) + 1;
  }

  return {
    totalBenefits: allBenefits.length,
    federalCount: catalog.federal.length,
    stateCount: Object.values(catalog.states).flat().length,
    municipalCount: catalog.municipal ? Object.values(catalog.municipal).flat().length : 0,
    sectoralCount: catalog.sectoral.length,
    statesWithBenefits: getStatesWithBenefits(catalog).length,
    municipalitiesWithBenefits: getMunicipalitiesWithBenefits(catalog).length,
    benefitsByCategory,
  };
}

/**
 * Format currency value in Brazilian Reais
 */
export function formatCurrency(value: number): string {
  return new Intl.NumberFormat('pt-BR', {
    style: 'currency',
    currency: 'BRL',
    minimumFractionDigits: 0,
    maximumFractionDigits: 0,
  }).format(value);
}

/**
 * Format benefit value for display
 * Accepts either a full Benefit or a partial object with estimatedValue
 */
export function formatBenefitValue(benefit: { estimatedValue?: Benefit['estimatedValue'] }): string {
  if (!benefit.estimatedValue) return 'Consultar';

  const { type, min, max, description } = benefit.estimatedValue;

  if (description) {
    // If there's a description, use it but add values if available
    if (min && max && min !== max) {
      return `${formatCurrency(min)} a ${formatCurrency(max)}`;
    }
    if (min || max) {
      return formatCurrency(min || max || 0);
    }
    return description;
  }

  const typeLabel = {
    monthly: '/mês',
    annual: '/ano',
    one_time: ' (único)',
  }[type];

  if (min && max && min !== max) {
    return `${formatCurrency(min)} a ${formatCurrency(max)}${typeLabel}`;
  }

  return `${formatCurrency(min || max || 0)}${typeLabel}`;
}

/**
 * Get state name from code
 */
export function getStateName(stateCode: string): string {
  return BRAZILIAN_STATES[stateCode.toUpperCase()] || stateCode;
}

// Singleton catalog instance
let catalogInstance: BenefitCatalog | null = null;

/**
 * Get the benefits catalog (loads once, returns cached)
 */
export function getBenefitsCatalog(): BenefitCatalog {
  if (!catalogInstance) {
    catalogInstance = loadBenefitsCatalog();
  }
  return catalogInstance;
}

/**
 * Refresh the catalog (useful for hot reloading in development)
 */
export function refreshCatalog(): BenefitCatalog {
  catalogInstance = loadBenefitsCatalog();
  return catalogInstance;
}
