/**
 * Test helpers for evaluator tests.
 * Loads REAL benefit data from JSON files.
 */
import { Benefit } from '../types';

import federalData from '../../data/benefits/federal.json';
import sectoralData from '../../data/benefits/sectoral.json';
import spData from '../../data/benefits/states/sp.json';
import maData from '../../data/benefits/states/ma.json';
import rjData from '../../data/benefits/states/rj.json';
import baData from '../../data/benefits/states/ba.json';

// Cast JSON imports to Benefit arrays
export const federalBenefits: Benefit[] = federalData.benefits as unknown as Benefit[];
export const sectoralBenefits: Benefit[] = sectoralData.benefits as unknown as Benefit[];
export const spBenefits: Benefit[] = (spData as { benefits: unknown[] }).benefits as unknown as Benefit[];
export const maBenefits: Benefit[] = (maData as { benefits: unknown[] }).benefits as unknown as Benefit[];
export const rjBenefits: Benefit[] = (rjData as { benefits: unknown[] }).benefits as unknown as Benefit[];
export const baBenefits: Benefit[] = (baData as { benefits: unknown[] }).benefits as unknown as Benefit[];

/** Find a benefit by ID from any scope */
export function findBenefit(id: string): Benefit {
  const allBenefits = [
    ...federalBenefits,
    ...sectoralBenefits,
    ...spBenefits,
    ...maBenefits,
    ...rjBenefits,
    ...baBenefits,
  ];
  const found = allBenefits.find(b => b.id === id);
  if (!found) throw new Error(`Benefit not found: ${id}`);
  return found;
}

/** Find all benefits with a given scope */
export function findByScope(scope: string): Benefit[] {
  const allBenefits = [
    ...federalBenefits,
    ...sectoralBenefits,
    ...spBenefits,
    ...maBenefits,
    ...rjBenefits,
    ...baBenefits,
  ];
  return allBenefits.filter(b => b.scope === scope);
}

/** Find sectoral benefits by sector */
export function findBySector(sector: string): Benefit[] {
  return sectoralBenefits.filter(b => b.sector === sector);
}
