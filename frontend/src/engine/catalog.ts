/**
 * Benefits Catalog Loader
 * Loads and manages the benefits catalog from JSON files
 */

import { Benefit, BenefitCatalog, BRAZILIAN_STATES } from './types';

// Import federal benefits
import federalData from '../data/benefits/federal.json';
import sectoralData from '../data/benefits/sectoral.json';

// Import state benefits - explicit imports
import stateAC from '../data/benefits/states/ac.json';
import stateAL from '../data/benefits/states/al.json';
import stateAM from '../data/benefits/states/am.json';
import stateAP from '../data/benefits/states/ap.json';
import stateBA from '../data/benefits/states/ba.json';
import stateCE from '../data/benefits/states/ce.json';
import stateDF from '../data/benefits/states/df.json';
import stateES from '../data/benefits/states/es.json';
import stateGO from '../data/benefits/states/go.json';
import stateMA from '../data/benefits/states/ma.json';
import stateMG from '../data/benefits/states/mg.json';
import stateMS from '../data/benefits/states/ms.json';
import stateMT from '../data/benefits/states/mt.json';
import statePA from '../data/benefits/states/pa.json';
import statePB from '../data/benefits/states/pb.json';
import statePE from '../data/benefits/states/pe.json';
import statePI from '../data/benefits/states/pi.json';
import statePR from '../data/benefits/states/pr.json';
import stateRJ from '../data/benefits/states/rj.json';
import stateRN from '../data/benefits/states/rn.json';
import stateRO from '../data/benefits/states/ro.json';
import stateRR from '../data/benefits/states/rr.json';
import stateRS from '../data/benefits/states/rs.json';
import stateSC from '../data/benefits/states/sc.json';
import stateSE from '../data/benefits/states/se.json';
import stateSP from '../data/benefits/states/sp.json';
import stateTO from '../data/benefits/states/to.json';

const stateModules: Record<string, { benefits: Benefit[] }> = {
  AC: stateAC as unknown as { benefits: Benefit[] },
  AL: stateAL as unknown as { benefits: Benefit[] },
  AM: stateAM as unknown as { benefits: Benefit[] },
  AP: stateAP as unknown as { benefits: Benefit[] },
  BA: stateBA as unknown as { benefits: Benefit[] },
  CE: stateCE as unknown as { benefits: Benefit[] },
  DF: stateDF as unknown as { benefits: Benefit[] },
  ES: stateES as unknown as { benefits: Benefit[] },
  GO: stateGO as unknown as { benefits: Benefit[] },
  MA: stateMA as unknown as { benefits: Benefit[] },
  MG: stateMG as unknown as { benefits: Benefit[] },
  MS: stateMS as unknown as { benefits: Benefit[] },
  MT: stateMT as unknown as { benefits: Benefit[] },
  PA: statePA as unknown as { benefits: Benefit[] },
  PB: statePB as unknown as { benefits: Benefit[] },
  PE: statePE as unknown as { benefits: Benefit[] },
  PI: statePI as unknown as { benefits: Benefit[] },
  PR: statePR as unknown as { benefits: Benefit[] },
  RJ: stateRJ as unknown as { benefits: Benefit[] },
  RN: stateRN as unknown as { benefits: Benefit[] },
  RO: stateRO as unknown as { benefits: Benefit[] },
  RR: stateRR as unknown as { benefits: Benefit[] },
  RS: stateRS as unknown as { benefits: Benefit[] },
  SC: stateSC as unknown as { benefits: Benefit[] },
  SE: stateSE as unknown as { benefits: Benefit[] },
  SP: stateSP as unknown as { benefits: Benefit[] },
  TO: stateTO as unknown as { benefits: Benefit[] },
};

// Import municipal benefits - explicit imports
import mun1100205 from '../data/benefits/municipalities/1100205.json';
import mun1302603 from '../data/benefits/municipalities/1302603.json';
import mun1500800 from '../data/benefits/municipalities/1500800.json';
import mun1501402 from '../data/benefits/municipalities/1501402.json';
import mun1600303 from '../data/benefits/municipalities/1600303.json';
import mun2111300 from '../data/benefits/municipalities/2111300.json';
import mun2211001 from '../data/benefits/municipalities/2211001.json';
import mun2304400 from '../data/benefits/municipalities/2304400.json';
import mun2408102 from '../data/benefits/municipalities/2408102.json';
import mun2507507 from '../data/benefits/municipalities/2507507.json';
import mun2611606 from '../data/benefits/municipalities/2611606.json';
import mun2704302 from '../data/benefits/municipalities/2704302.json';
import mun2800308 from '../data/benefits/municipalities/2800308.json';
import mun2910800 from '../data/benefits/municipalities/2910800.json';
import mun2927408 from '../data/benefits/municipalities/2927408.json';
import mun3106200 from '../data/benefits/municipalities/3106200.json';
import mun3118601 from '../data/benefits/municipalities/3118601.json';
import mun3136702 from '../data/benefits/municipalities/3136702.json';
import mun3170206 from '../data/benefits/municipalities/3170206.json';
import mun3301702 from '../data/benefits/municipalities/3301702.json';
import mun3303302 from '../data/benefits/municipalities/3303302.json';
import mun3304557 from '../data/benefits/municipalities/3304557.json';
import mun3304904 from '../data/benefits/municipalities/3304904.json';
import mun3509502 from '../data/benefits/municipalities/3509502.json';
import mun3518800 from '../data/benefits/municipalities/3518800.json';
import mun3534401 from '../data/benefits/municipalities/3534401.json';
import mun3543402 from '../data/benefits/municipalities/3543402.json';
import mun3547809 from '../data/benefits/municipalities/3547809.json';
import mun3548708 from '../data/benefits/municipalities/3548708.json';
import mun3550308 from '../data/benefits/municipalities/3550308.json';
import mun3552205 from '../data/benefits/municipalities/3552205.json';
import mun4106902 from '../data/benefits/municipalities/4106902.json';
import mun4113700 from '../data/benefits/municipalities/4113700.json';
import mun4209102 from '../data/benefits/municipalities/4209102.json';
import mun4314902 from '../data/benefits/municipalities/4314902.json';
import mun5002704 from '../data/benefits/municipalities/5002704.json';
import mun5103403 from '../data/benefits/municipalities/5103403.json';
import mun5201405 from '../data/benefits/municipalities/5201405.json';
import mun5208707 from '../data/benefits/municipalities/5208707.json';
import mun5300108 from '../data/benefits/municipalities/5300108.json';

const municipalModules: Record<string, { benefits: Benefit[] }> = {
  '1100205': mun1100205 as unknown as { benefits: Benefit[] },
  '1302603': mun1302603 as unknown as { benefits: Benefit[] },
  '1500800': mun1500800 as unknown as { benefits: Benefit[] },
  '1501402': mun1501402 as unknown as { benefits: Benefit[] },
  '1600303': mun1600303 as unknown as { benefits: Benefit[] },
  '2111300': mun2111300 as unknown as { benefits: Benefit[] },
  '2211001': mun2211001 as unknown as { benefits: Benefit[] },
  '2304400': mun2304400 as unknown as { benefits: Benefit[] },
  '2408102': mun2408102 as unknown as { benefits: Benefit[] },
  '2507507': mun2507507 as unknown as { benefits: Benefit[] },
  '2611606': mun2611606 as unknown as { benefits: Benefit[] },
  '2704302': mun2704302 as unknown as { benefits: Benefit[] },
  '2800308': mun2800308 as unknown as { benefits: Benefit[] },
  '2910800': mun2910800 as unknown as { benefits: Benefit[] },
  '2927408': mun2927408 as unknown as { benefits: Benefit[] },
  '3106200': mun3106200 as unknown as { benefits: Benefit[] },
  '3118601': mun3118601 as unknown as { benefits: Benefit[] },
  '3136702': mun3136702 as unknown as { benefits: Benefit[] },
  '3170206': mun3170206 as unknown as { benefits: Benefit[] },
  '3301702': mun3301702 as unknown as { benefits: Benefit[] },
  '3303302': mun3303302 as unknown as { benefits: Benefit[] },
  '3304557': mun3304557 as unknown as { benefits: Benefit[] },
  '3304904': mun3304904 as unknown as { benefits: Benefit[] },
  '3509502': mun3509502 as unknown as { benefits: Benefit[] },
  '3518800': mun3518800 as unknown as { benefits: Benefit[] },
  '3534401': mun3534401 as unknown as { benefits: Benefit[] },
  '3543402': mun3543402 as unknown as { benefits: Benefit[] },
  '3547809': mun3547809 as unknown as { benefits: Benefit[] },
  '3548708': mun3548708 as unknown as { benefits: Benefit[] },
  '3550308': mun3550308 as unknown as { benefits: Benefit[] },
  '3552205': mun3552205 as unknown as { benefits: Benefit[] },
  '4106902': mun4106902 as unknown as { benefits: Benefit[] },
  '4113700': mun4113700 as unknown as { benefits: Benefit[] },
  '4209102': mun4209102 as unknown as { benefits: Benefit[] },
  '4314902': mun4314902 as unknown as { benefits: Benefit[] },
  '5002704': mun5002704 as unknown as { benefits: Benefit[] },
  '5103403': mun5103403 as unknown as { benefits: Benefit[] },
  '5201405': mun5201405 as unknown as { benefits: Benefit[] },
  '5208707': mun5208707 as unknown as { benefits: Benefit[] },
  '5300108': mun5300108 as unknown as { benefits: Benefit[] },
};

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

  for (const [stateCode, stateData] of Object.entries(stateModules)) {
    states[stateCode] = stateData.benefits || [];
  }

  // Load municipal benefits by IBGE code
  const municipal: Record<string, Benefit[]> = {};

  for (const [ibgeCode, municipalData] of Object.entries(municipalModules)) {
    municipal[ibgeCode] = municipalData.benefits || [];
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
