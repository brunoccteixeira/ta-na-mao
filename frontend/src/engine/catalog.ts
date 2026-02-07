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

// Import municipal benefits by state — 5573 municipalities (auto-generated)
// Using per-state barrel files to avoid TypeScript OOM with individual imports
import munStateAC from '../data/benefits/municipalities/by-state/AC.json';
import munStateAL from '../data/benefits/municipalities/by-state/AL.json';
import munStateAM from '../data/benefits/municipalities/by-state/AM.json';
import munStateAP from '../data/benefits/municipalities/by-state/AP.json';
import munStateBA from '../data/benefits/municipalities/by-state/BA.json';
import munStateCE from '../data/benefits/municipalities/by-state/CE.json';
import munStateDF from '../data/benefits/municipalities/by-state/DF.json';
import munStateES from '../data/benefits/municipalities/by-state/ES.json';
import munStateGO from '../data/benefits/municipalities/by-state/GO.json';
import munStateMA from '../data/benefits/municipalities/by-state/MA.json';
import munStateMG from '../data/benefits/municipalities/by-state/MG.json';
import munStateMS from '../data/benefits/municipalities/by-state/MS.json';
import munStateMT from '../data/benefits/municipalities/by-state/MT.json';
import munStatePA from '../data/benefits/municipalities/by-state/PA.json';
import munStatePB from '../data/benefits/municipalities/by-state/PB.json';
import munStatePE from '../data/benefits/municipalities/by-state/PE.json';
import munStatePI from '../data/benefits/municipalities/by-state/PI.json';
import munStatePR from '../data/benefits/municipalities/by-state/PR.json';
import munStateRJ from '../data/benefits/municipalities/by-state/RJ.json';
import munStateRN from '../data/benefits/municipalities/by-state/RN.json';
import munStateRO from '../data/benefits/municipalities/by-state/RO.json';
import munStateRR from '../data/benefits/municipalities/by-state/RR.json';
import munStateRS from '../data/benefits/municipalities/by-state/RS.json';
import munStateSC from '../data/benefits/municipalities/by-state/SC.json';
import munStateSE from '../data/benefits/municipalities/by-state/SE.json';
import munStateSP from '../data/benefits/municipalities/by-state/SP.json';
import munStateTO from '../data/benefits/municipalities/by-state/TO.json';

// Build municipalModules from state barrels
type MunicipalBarrel = { municipalities: Record<string, Benefit[]> };
const municipalModules: Record<string, Benefit[]> = {};

for (const [ibge, benefits] of Object.entries((munStateAC as unknown as MunicipalBarrel).municipalities)) {
  municipalModules[ibge] = benefits;
}
for (const [ibge, benefits] of Object.entries((munStateAL as unknown as MunicipalBarrel).municipalities)) {
  municipalModules[ibge] = benefits;
}
for (const [ibge, benefits] of Object.entries((munStateAM as unknown as MunicipalBarrel).municipalities)) {
  municipalModules[ibge] = benefits;
}
for (const [ibge, benefits] of Object.entries((munStateAP as unknown as MunicipalBarrel).municipalities)) {
  municipalModules[ibge] = benefits;
}
for (const [ibge, benefits] of Object.entries((munStateBA as unknown as MunicipalBarrel).municipalities)) {
  municipalModules[ibge] = benefits;
}
for (const [ibge, benefits] of Object.entries((munStateCE as unknown as MunicipalBarrel).municipalities)) {
  municipalModules[ibge] = benefits;
}
for (const [ibge, benefits] of Object.entries((munStateDF as unknown as MunicipalBarrel).municipalities)) {
  municipalModules[ibge] = benefits;
}
for (const [ibge, benefits] of Object.entries((munStateES as unknown as MunicipalBarrel).municipalities)) {
  municipalModules[ibge] = benefits;
}
for (const [ibge, benefits] of Object.entries((munStateGO as unknown as MunicipalBarrel).municipalities)) {
  municipalModules[ibge] = benefits;
}
for (const [ibge, benefits] of Object.entries((munStateMA as unknown as MunicipalBarrel).municipalities)) {
  municipalModules[ibge] = benefits;
}
for (const [ibge, benefits] of Object.entries((munStateMG as unknown as MunicipalBarrel).municipalities)) {
  municipalModules[ibge] = benefits;
}
for (const [ibge, benefits] of Object.entries((munStateMS as unknown as MunicipalBarrel).municipalities)) {
  municipalModules[ibge] = benefits;
}
for (const [ibge, benefits] of Object.entries((munStateMT as unknown as MunicipalBarrel).municipalities)) {
  municipalModules[ibge] = benefits;
}
for (const [ibge, benefits] of Object.entries((munStatePA as unknown as MunicipalBarrel).municipalities)) {
  municipalModules[ibge] = benefits;
}
for (const [ibge, benefits] of Object.entries((munStatePB as unknown as MunicipalBarrel).municipalities)) {
  municipalModules[ibge] = benefits;
}
for (const [ibge, benefits] of Object.entries((munStatePE as unknown as MunicipalBarrel).municipalities)) {
  municipalModules[ibge] = benefits;
}
for (const [ibge, benefits] of Object.entries((munStatePI as unknown as MunicipalBarrel).municipalities)) {
  municipalModules[ibge] = benefits;
}
for (const [ibge, benefits] of Object.entries((munStatePR as unknown as MunicipalBarrel).municipalities)) {
  municipalModules[ibge] = benefits;
}
for (const [ibge, benefits] of Object.entries((munStateRJ as unknown as MunicipalBarrel).municipalities)) {
  municipalModules[ibge] = benefits;
}
for (const [ibge, benefits] of Object.entries((munStateRN as unknown as MunicipalBarrel).municipalities)) {
  municipalModules[ibge] = benefits;
}
for (const [ibge, benefits] of Object.entries((munStateRO as unknown as MunicipalBarrel).municipalities)) {
  municipalModules[ibge] = benefits;
}
for (const [ibge, benefits] of Object.entries((munStateRR as unknown as MunicipalBarrel).municipalities)) {
  municipalModules[ibge] = benefits;
}
for (const [ibge, benefits] of Object.entries((munStateRS as unknown as MunicipalBarrel).municipalities)) {
  municipalModules[ibge] = benefits;
}
for (const [ibge, benefits] of Object.entries((munStateSC as unknown as MunicipalBarrel).municipalities)) {
  municipalModules[ibge] = benefits;
}
for (const [ibge, benefits] of Object.entries((munStateSE as unknown as MunicipalBarrel).municipalities)) {
  municipalModules[ibge] = benefits;
}
for (const [ibge, benefits] of Object.entries((munStateSP as unknown as MunicipalBarrel).municipalities)) {
  municipalModules[ibge] = benefits;
}
for (const [ibge, benefits] of Object.entries((munStateTO as unknown as MunicipalBarrel).municipalities)) {
  municipalModules[ibge] = benefits;
}

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

  for (const [ibgeCode, benefits] of Object.entries(municipalModules)) {
    municipal[ibgeCode] = benefits || [];
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
