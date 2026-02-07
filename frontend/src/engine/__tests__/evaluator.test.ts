/**
 * Evaluator Engine Tests — Operators, Computed Fields, Geography, Sectors
 * Uses REAL benefit data from JSON files, not mocks.
 */
import { describe, it, expect } from 'vitest';
import {
  evaluateBenefit,
  evaluateAllBenefits,
  calcularRendaPerCapita,
  filterBenefitsByScope,
  filterBenefitsByState,
  searchBenefits,
} from '../evaluator';

import { makeProfile } from './fixtures/testProfiles';
import {
  federalBenefits,
  sectoralBenefits,
  spBenefits,
  maBenefits,
  findBenefit,
  findBySector,
} from './testHelpers';

// ═══════════════════════════════════════════════════════════════════
// A. OPERATOR TESTS (10)
// ═══════════════════════════════════════════════════════════════════

describe('Operators — using real benefit rules', () => {
  // Bolsa Família uses "lte" on rendaPerCapita
  it('lte: rendaPerCapita 200 <= 218 passes (Bolsa Família)', () => {
    const bf = findBenefit('federal-bolsa-familia');
    const profile = makeProfile({
      rendaFamiliarMensal: 800,
      pessoasNaCasa: 4, // PC = 200
      cadastradoCadunico: true,
    });
    const result = evaluateBenefit(profile, bf);
    expect(result.status).toBe('eligible');
  });

  it('lte: rendaPerCapita 250 > 218 fails (Bolsa Família)', () => {
    const bf = findBenefit('federal-bolsa-familia');
    const profile = makeProfile({
      rendaFamiliarMensal: 1000,
      pessoasNaCasa: 4, // PC = 250
      cadastradoCadunico: true,
    });
    const result = evaluateBenefit(profile, bf);
    expect(result.status).toBe('not_eligible');
  });

  // BPC Idoso uses "eq" on temIdoso65Mais
  it('eq: temIdoso65Mais === true passes (BPC Idoso)', () => {
    const bpc = findBenefit('federal-bpc-idoso');
    const profile = makeProfile({
      temIdoso65Mais: true,
      rendaFamiliarMensal: 400,
      pessoasNaCasa: 1, // PC = 400 <= 405.25
      recebeBolsaFamilia: false,
    });
    const result = evaluateBenefit(profile, bpc);
    expect(result.status).toBe('eligible');
  });

  it('eq: temIdoso65Mais === false fails (BPC Idoso)', () => {
    const bpc = findBenefit('federal-bpc-idoso');
    const profile = makeProfile({
      temIdoso65Mais: false,
      rendaFamiliarMensal: 400,
      pessoasNaCasa: 1,
    });
    const result = evaluateBenefit(profile, bpc);
    expect(result.status).toBe('not_eligible');
  });

  // Seguro-Desemprego uses "eq" false (trabalhoFormal === false) and "gte" on tempoCarteiraAssinada
  it('gte: tempoCarteiraAssinada >= 12 passes (Seguro-Desemprego)', () => {
    const sd = findBenefit('federal-seguro-desemprego');
    const profile = makeProfile({
      trabalhoFormal: false,
      tempoCarteiraAssinada: 12,
    });
    const result = evaluateBenefit(profile, sd);
    expect(result.status).toBe('eligible');
  });

  it('gte: tempoCarteiraAssinada = 6 < 12 fails (Seguro-Desemprego)', () => {
    const sd = findBenefit('federal-seguro-desemprego');
    const profile = makeProfile({
      trabalhoFormal: false,
      tempoCarteiraAssinada: 6,
    });
    const result = evaluateBenefit(profile, sd);
    expect(result.status).toBe('not_eligible');
  });

  // SVR uses "has" on cpf
  it('has: cpf with value passes (SVR)', () => {
    const svr = findBenefit('federal-svr');
    const profile = makeProfile({
      cpf: '12345678900',
    });
    const result = evaluateBenefit(profile, svr);
    expect(result.status).toBe('eligible');
  });

  it('has: cpf undefined is inconclusive (SVR)', () => {
    const svr = findBenefit('federal-svr');
    const profile = makeProfile({});
    // cpf is undefined by default
    const result = evaluateBenefit(profile, svr);
    // Field is undefined → inconclusive → likely_eligible
    expect(result.inconclusiveRules.length).toBeGreaterThan(0);
  });

  // Farmácia Popular uses "gte" with value 0 on idade (universal)
  it('gte: idade >= 0 passes for any age (Farmácia Popular)', () => {
    const fp = findBenefit('federal-farmacia-popular');
    const profile = makeProfile({ idade: 25 });
    const result = evaluateBenefit(profile, fp);
    // idade is optional; if present, >= 0 should pass
    expect(result.status).toBe('eligible');
  });

  // neq: BPC Idoso requires recebeBolsaFamilia === false (eq false acts as neq true)
  it('eq false: recebeBolsaFamilia === false passes (BPC Idoso rule)', () => {
    const bpc = findBenefit('federal-bpc-idoso');
    const profile = makeProfile({
      temIdoso65Mais: true,
      rendaFamiliarMensal: 400,
      pessoasNaCasa: 1,
      recebeBolsaFamilia: false,
    });
    const result = evaluateBenefit(profile, bpc);
    expect(result.failedRules).not.toContain(
      expect.stringContaining('Bolsa Família')
    );
  });
});

// ═══════════════════════════════════════════════════════════════════
// B. COMPUTED FIELDS (5)
// ═══════════════════════════════════════════════════════════════════

describe('Computed fields — rendaPerCapita', () => {
  it('calculates correctly: 800 / 4 = 200', () => {
    const profile = makeProfile({
      rendaFamiliarMensal: 800,
      pessoasNaCasa: 4,
    });
    expect(calcularRendaPerCapita(profile)).toBe(200);
  });

  it('handles renda zero: 0 / 3 = 0', () => {
    const profile = makeProfile({
      rendaFamiliarMensal: 0,
      pessoasNaCasa: 3,
    });
    expect(calcularRendaPerCapita(profile)).toBe(0);
  });

  it('handles 1 person: 1500 / 1 = 1500', () => {
    const profile = makeProfile({
      rendaFamiliarMensal: 1500,
      pessoasNaCasa: 1,
    });
    expect(calcularRendaPerCapita(profile)).toBe(1500);
  });

  it('handles large family: 1200 / 6 = 200', () => {
    const profile = makeProfile({
      rendaFamiliarMensal: 1200,
      pessoasNaCasa: 6,
    });
    expect(calcularRendaPerCapita(profile)).toBe(200);
  });

  it('edge: limit value 218 per capita with Bolsa Família', () => {
    const bf = findBenefit('federal-bolsa-familia');
    // 872 / 4 = 218 exactly
    const profile = makeProfile({
      rendaFamiliarMensal: 872,
      pessoasNaCasa: 4,
      cadastradoCadunico: true,
    });
    const result = evaluateBenefit(profile, bf);
    expect(result.status).toBe('eligible');
  });
});

// ═══════════════════════════════════════════════════════════════════
// C. GEOGRAPHY TESTS (8)
// ═══════════════════════════════════════════════════════════════════

describe('Geography matching', () => {
  it('federal benefit matches any state', () => {
    const bf = findBenefit('federal-bolsa-familia');
    const profileAC = makeProfile({
      estado: 'AC',
      rendaFamiliarMensal: 200,
      pessoasNaCasa: 1,
      cadastradoCadunico: true,
    });
    const result = evaluateBenefit(profileAC, bf);
    expect(result.status).not.toBe('not_applicable');
  });

  it('SP state benefit matches SP resident', () => {
    const spBenefit = spBenefits[0]; // First SP benefit
    const profile = makeProfile({
      estado: 'SP',
      rendaFamiliarMensal: 500,
      pessoasNaCasa: 1,
      cadastradoCadunico: true,
    });
    const result = evaluateBenefit(profile, spBenefit);
    expect(result.status).not.toBe('not_applicable');
  });

  it('SP state benefit does NOT match RJ resident', () => {
    const spBenefit = spBenefits[0];
    const profile = makeProfile({
      estado: 'RJ',
      rendaFamiliarMensal: 500,
      pessoasNaCasa: 1,
    });
    const result = evaluateBenefit(profile, spBenefit);
    expect(result.status).toBe('not_applicable');
  });

  it('MA state benefit matches MA resident', () => {
    const maBenefit = maBenefits[0];
    const profile = makeProfile({
      estado: 'MA',
      rendaFamiliarMensal: 500,
      pessoasNaCasa: 1,
      cadastradoCadunico: true,
    });
    const result = evaluateBenefit(profile, maBenefit);
    expect(result.status).not.toBe('not_applicable');
  });

  it('MA state benefit does NOT match SP resident', () => {
    const maBenefit = maBenefits[0];
    const profile = makeProfile({ estado: 'SP' });
    const result = evaluateBenefit(profile, maBenefit);
    expect(result.status).toBe('not_applicable');
  });

  it('sectoral benefit without state restriction matches any state', () => {
    // Seguro-Defeso is sectoral without state restriction
    const seguroDefeso = findBenefit('sectoral-seguro-defeso');
    const profile = makeProfile({
      estado: 'PA',
      pescadorArtesanal: true,
      cadastradoCadunico: true,
    });
    const result = evaluateBenefit(profile, seguroDefeso);
    expect(result.status).not.toBe('not_applicable');
  });

  it('evaluateAllBenefits excludes out-of-state benefits', () => {
    const profile = makeProfile({
      estado: 'RJ',
      rendaFamiliarMensal: 500,
      pessoasNaCasa: 1,
      cadastradoCadunico: true,
    });
    const summary = evaluateAllBenefits(profile, spBenefits);
    // All SP benefits should be not_applicable for RJ resident
    expect(summary.notApplicable.length).toBe(spBenefits.length);
  });

  it('filterBenefitsByState returns federal + matching state', () => {
    const allBenefits = [...federalBenefits, ...spBenefits, ...maBenefits];
    const filtered = filterBenefitsByState(allBenefits, 'SP');
    // Should include federal + SP, not MA
    const hasMA = filtered.some(b => b.scope === 'state' && b.state === 'MA');
    const hasSP = filtered.some(b => b.scope === 'state' && b.state === 'SP');
    const hasFederal = filtered.some(b => b.scope === 'federal');
    expect(hasMA).toBe(false);
    expect(hasSP).toBe(true);
    expect(hasFederal).toBe(true);
  });
});

// ═══════════════════════════════════════════════════════════════════
// D. SECTOR TESTS (10)
// ═══════════════════════════════════════════════════════════════════

describe('Sector matching', () => {
  it('pescador sector matches pescadorArtesanal=true', () => {
    const seguroDefeso = findBenefit('sectoral-seguro-defeso');
    const profile = makeProfile({
      pescadorArtesanal: true,
      cadastradoCadunico: true,
    });
    const result = evaluateBenefit(profile, seguroDefeso);
    expect(result.status).not.toBe('not_applicable');
  });

  it('pescador sector rejects non-pescador', () => {
    const seguroDefeso = findBenefit('sectoral-seguro-defeso');
    const profile = makeProfile({
      pescadorArtesanal: false,
    });
    const result = evaluateBenefit(profile, seguroDefeso);
    expect(result.status).toBe('not_applicable');
  });

  it('agricultor sector matches agricultorFamiliar=true', () => {
    const pronaf = findBenefit('sectoral-pronaf');
    const profile = makeProfile({
      agricultorFamiliar: true,
      moradiaZonaRural: true,
    });
    const result = evaluateBenefit(profile, pronaf);
    expect(result.status).not.toBe('not_applicable');
  });

  it('agricultor sector rejects non-agricultor', () => {
    const pronaf = findBenefit('sectoral-pronaf');
    const profile = makeProfile({ agricultorFamiliar: false });
    const result = evaluateBenefit(profile, pronaf);
    expect(result.status).toBe('not_applicable');
  });

  it('mei sector matches temMei=true', () => {
    const meiBenefits = findBySector('mei');
    expect(meiBenefits.length).toBeGreaterThan(0);
    const profile = makeProfile({ temMei: true });
    const result = evaluateBenefit(profile, meiBenefits[0]);
    expect(result.status).not.toBe('not_applicable');
  });

  it('mei sector rejects non-MEI', () => {
    const meiBenefits = findBySector('mei');
    const profile = makeProfile({ temMei: false });
    const result = evaluateBenefit(profile, meiBenefits[0]);
    expect(result.status).toBe('not_applicable');
  });

  it('domestica sector matches trabalhadoraDomestica=true', () => {
    const domesticaBenefits = findBySector('domestica');
    expect(domesticaBenefits.length).toBeGreaterThan(0);
    const profile = makeProfile({ trabalhadoraDomestica: true });
    const result = evaluateBenefit(profile, domesticaBenefits[0]);
    expect(result.status).not.toBe('not_applicable');
  });

  it('entregador sector matches trabalhaAplicativo=true', () => {
    const entregadorBenefits = findBySector('entregador');
    expect(entregadorBenefits.length).toBeGreaterThan(0);
    const profile = makeProfile({ trabalhaAplicativo: true });
    const result = evaluateBenefit(profile, entregadorBenefits[0]);
    expect(result.status).not.toBe('not_applicable');
  });

  it('pcd sector matches temPcd=true', () => {
    const pcdBenefits = findBySector('pcd');
    expect(pcdBenefits.length).toBeGreaterThan(0);
    const profile = makeProfile({ temPcd: true });
    const result = evaluateBenefit(profile, pcdBenefits[0]);
    expect(result.status).not.toBe('not_applicable');
  });

  it('clt sector matches trabalhoFormal=true', () => {
    const cltBenefits = findBySector('clt');
    expect(cltBenefits.length).toBeGreaterThan(0);
    const profile = makeProfile({ trabalhoFormal: true });
    const result = evaluateBenefit(profile, cltBenefits[0]);
    expect(result.status).not.toBe('not_applicable');
  });
});

// ═══════════════════════════════════════════════════════════════════
// E. UTILITY FUNCTIONS (5)
// ═══════════════════════════════════════════════════════════════════

describe('Utility functions', () => {
  it('filterBenefitsByScope returns only federal', () => {
    const all = [...federalBenefits, ...sectoralBenefits, ...spBenefits];
    const result = filterBenefitsByScope(all, 'federal');
    expect(result.every(b => b.scope === 'federal')).toBe(true);
    expect(result.length).toBe(federalBenefits.length);
  });

  it('searchBenefits finds by name', () => {
    const result = searchBenefits(federalBenefits, 'Bolsa Família');
    expect(result.length).toBeGreaterThanOrEqual(1);
    expect(result[0].id).toBe('federal-bolsa-familia');
  });

  it('searchBenefits finds by category', () => {
    const result = searchBenefits(federalBenefits, 'Moradia');
    expect(result.some(b => b.id === 'federal-mcmv')).toBe(true);
  });

  it('searchBenefits returns all for empty query', () => {
    const result = searchBenefits(federalBenefits, '');
    expect(result.length).toBe(federalBenefits.length);
  });

  it('evaluateAllBenefits returns correct totalAnalyzed', () => {
    const profile = makeProfile({
      estado: 'SP',
      rendaFamiliarMensal: 500,
      pessoasNaCasa: 1,
      cadastradoCadunico: true,
    });
    const summary = evaluateAllBenefits(profile, federalBenefits);
    expect(summary.totalAnalyzed).toBe(federalBenefits.length);
    // Sum of all categories = totalAnalyzed
    const total =
      summary.eligible.length +
      summary.likelyEligible.length +
      summary.maybe.length +
      summary.notEligible.length +
      summary.notApplicable.length +
      summary.alreadyReceiving.length;
    expect(total).toBe(summary.totalAnalyzed);
  });
});
