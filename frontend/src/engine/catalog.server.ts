/**
 * Benefits Catalog Loader — Server-side (Next.js)
 * Uses fs to read JSON files instead of import.meta.glob
 */

import fs from 'fs';
import path from 'path';
import type { Benefit, BenefitCatalog } from './types';

const DATA_DIR = path.join(process.cwd(), 'src', 'data', 'benefits');

function readJsonSync<T>(filePath: string): T {
  const raw = fs.readFileSync(filePath, 'utf-8');
  return JSON.parse(raw) as T;
}

/**
 * Load the full benefits catalog from disk (server-only)
 */
export function loadBenefitsCatalogServer(): BenefitCatalog {
  // Federal
  const federalPath = path.join(DATA_DIR, 'federal.json');
  const federal = readJsonSync<{ benefits: Benefit[] }>(federalPath).benefits;

  // Sectoral
  const sectoralPath = path.join(DATA_DIR, 'sectoral.json');
  const sectoral = readJsonSync<{ benefits: Benefit[] }>(sectoralPath).benefits;

  // States
  const statesDir = path.join(DATA_DIR, 'states');
  const states: Record<string, Benefit[]> = {};

  if (fs.existsSync(statesDir)) {
    for (const file of fs.readdirSync(statesDir)) {
      const match = file.match(/^([a-z]{2})\.json$/i);
      if (match) {
        const stateCode = match[1].toUpperCase();
        const stateData = readJsonSync<{ benefits: Benefit[] }>(
          path.join(statesDir, file)
        );
        states[stateCode] = stateData.benefits || [];
      }
    }
  }

  // Municipalities
  const municipalDir = path.join(DATA_DIR, 'municipalities');
  const municipal: Record<string, Benefit[]> = {};

  if (fs.existsSync(municipalDir)) {
    for (const file of fs.readdirSync(municipalDir)) {
      const match = file.match(/^(\d+)\.json$/);
      if (match) {
        const ibgeCode = match[1];
        const municipalData = readJsonSync<{ benefits: Benefit[] }>(
          path.join(municipalDir, file)
        );
        municipal[ibgeCode] = municipalData.benefits || [];
      }
    }
  }

  return { federal, states, sectoral, municipal };
}

/**
 * Get all benefits as a flat array (server-only)
 */
export function getAllBenefitsServer(catalog: BenefitCatalog): Benefit[] {
  const allBenefits: Benefit[] = [
    ...catalog.federal,
    ...catalog.sectoral,
  ];

  for (const stateBenefits of Object.values(catalog.states)) {
    allBenefits.push(...stateBenefits);
  }

  if (catalog.municipal) {
    for (const municipalBenefits of Object.values(catalog.municipal)) {
      allBenefits.push(...municipalBenefits);
    }
  }

  return allBenefits;
}

/**
 * Get a single benefit by ID (server-only)
 */
export function getBenefitByIdServer(
  catalog: BenefitCatalog,
  benefitId: string
): Benefit | undefined {
  let benefit = catalog.federal.find(b => b.id === benefitId);
  if (benefit) return benefit;

  benefit = catalog.sectoral.find(b => b.id === benefitId);
  if (benefit) return benefit;

  for (const stateBenefits of Object.values(catalog.states)) {
    benefit = stateBenefits.find(b => b.id === benefitId);
    if (benefit) return benefit;
  }

  if (catalog.municipal) {
    for (const municipalBenefits of Object.values(catalog.municipal)) {
      benefit = municipalBenefits.find(b => b.id === benefitId);
      if (benefit) return benefit;
    }
  }

  return undefined;
}

/**
 * Get list of states that have benefits (server-only)
 */
export function getStatesWithBenefitsServer(catalog: BenefitCatalog): string[] {
  return Object.keys(catalog.states).filter(
    state => catalog.states[state].length > 0
  );
}
