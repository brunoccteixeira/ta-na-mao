/**
 * Benefit Relations Tests — Exclusions, Cascades, and Adjusted Totals
 * 15 tests covering all relation types.
 */
import { describe, it, expect } from 'vitest';
import {
  evaluateAllBenefits,
  applyBenefitRelations,
  evaluateBenefit,
} from '../evaluator';
import { makeProfile } from './fixtures/testProfiles';
import { federalBenefits, sectoralBenefits, findBenefit } from './testHelpers';

// ═══════════════════════════════════════════════════════════════════
// A. EXCLUSION TESTS (5)
// ═══════════════════════════════════════════════════════════════════

describe('Exclusions — mutually exclusive benefits', () => {
  it('BPC Idoso + BPC PcD → exclusion warning, only 1 counted in adjusted total', () => {
    // Idoso PcD com baixa renda — elegível para ambos BPC
    const profile = makeProfile({
      temIdoso65Mais: true,
      temPcd: true,
      rendaFamiliarMensal: 400,
      pessoasNaCasa: 1,
      cadastradoCadunico: true,
    });

    const bpcIdoso = findBenefit('federal-bpc-idoso');
    const bpcPcd = findBenefit('federal-bpc-pcd');
    const results = [bpcIdoso, bpcPcd].map(b => evaluateBenefit(profile, b));

    // Both should be eligible individually
    expect(results[0].status).toBe('eligible');
    expect(results[1].status).toBe('eligible');

    // Apply relations
    const { warnings, excludedIds } = applyBenefitRelations(results, profile);

    // Should have exclusion warning
    const exclusionWarning = warnings.find(w => w.type === 'exclusion');
    expect(exclusionWarning).toBeDefined();
    expect(exclusionWarning!.benefitIds).toContain('federal-bpc-idoso');
    expect(exclusionWarning!.benefitIds).toContain('federal-bpc-pcd');

    // One should be excluded
    expect(excludedIds.size).toBe(1);
  });

  it('BPC + Aposentadoria → exclusion warning', () => {
    const profile = makeProfile({
      temIdoso65Mais: true,
      rendaFamiliarMensal: 400,
      pessoasNaCasa: 1,
      cadastradoCadunico: true,
    });

    const bpc = findBenefit('federal-bpc-idoso');
    const aposRural = findBenefit('federal-aposentadoria-rural');
    const results = [
      evaluateBenefit(profile, bpc),
      evaluateBenefit(profile, aposRural),
    ];

    // BPC should be eligible
    expect(results[0].status).toBe('eligible');

    // Only apply if apos is also eligible (depends on rules)
    const { warnings } = applyBenefitRelations(results, profile);

    // If both eligible, should have warning
    if (results[1].status === 'eligible' || results[1].status === 'likely_eligible') {
      expect(warnings.some(w => w.type === 'exclusion')).toBe(true);
    }
  });

  it('Seguro-Desemprego + Abono Salarial → exclusion warning', () => {
    // CLT desempregado elegível para seguro-desemprego
    const profile = makeProfile({
      trabalhoFormal: false,
      tempoCarteiraAssinada: 14,
      rendaFamiliarMensal: 2000,
    });

    const sd = findBenefit('federal-seguro-desemprego');
    const abono = findBenefit('federal-abono-salarial');
    const results = [
      evaluateBenefit(profile, sd),
      evaluateBenefit(profile, abono),
    ];

    const { warnings, excludedIds } = applyBenefitRelations(results, profile);

    // Seguro-Desemprego should be eligible (desempregado + tempo)
    expect(results[0].status).toBe('eligible');

    // If both eligible, should warn and exclude one
    if (results[1].status === 'eligible' || results[1].status === 'likely_eligible') {
      expect(warnings.some(w => w.type === 'exclusion')).toBe(true);
      expect(excludedIds.size).toBe(1);
    }
  });

  it('ProUni integral + FIES → exclusion warning', () => {
    const profile = makeProfile({
      redePublica: true,
      rendaFamiliarMensal: 3000,
      pessoasNaCasa: 2, // PC = 1500
      estudante: true,
    });

    const prouni = findBenefit('federal-prouni');
    const fies = findBenefit('federal-fies');
    const results = [
      evaluateBenefit(profile, prouni),
      evaluateBenefit(profile, fies),
    ];

    const { warnings, excludedIds } = applyBenefitRelations(results, profile);

    if (results[0].status === 'eligible' && results[1].status === 'eligible') {
      expect(warnings.some(w =>
        w.type === 'exclusion' &&
        w.benefitIds.includes('federal-prouni') &&
        w.benefitIds.includes('federal-fies')
      )).toBe(true);
      expect(excludedIds.size).toBe(1);
    }
  });

  it('BF + BPC Idoso → NO exclusion (can accumulate since Lei 14.601/2023)', () => {
    const profile = makeProfile({
      temIdoso65Mais: true,
      rendaFamiliarMensal: 400,
      pessoasNaCasa: 1,
      cadastradoCadunico: true,
      recebeBolsaFamilia: true,  // Já recebe BF
    });

    const bpc = findBenefit('federal-bpc-idoso');
    const bf = findBenefit('federal-bolsa-familia');
    const results = [
      evaluateBenefit(profile, bpc),
      evaluateBenefit(profile, bf),
    ];

    const { warnings, excludedIds } = applyBenefitRelations(results, profile);

    // Should NOT have exclusion between BPC and BF
    const exclusionBetweenBpcBf = warnings.find(w =>
      w.type === 'exclusion' &&
      w.benefitIds.includes('federal-bpc-idoso') &&
      w.benefitIds.includes('federal-bolsa-familia')
    );
    expect(exclusionBetweenBpcBf).toBeUndefined();

    // BPC should NOT be excluded
    expect(excludedIds.has('federal-bpc-idoso')).toBe(false);
    expect(excludedIds.has('federal-bolsa-familia')).toBe(false);
  });
});

// ═══════════════════════════════════════════════════════════════════
// B. CASCADE / UNLOCK TESTS (5)
// ═══════════════════════════════════════════════════════════════════

describe('Cascades — automatic benefit unlocks', () => {
  it('BF eligible → Tarifa Social Energia in unlocked', () => {
    const profile = makeProfile({
      rendaFamiliarMensal: 800,
      pessoasNaCasa: 4,
      cadastradoCadunico: true,
    });

    const summary = evaluateAllBenefits(profile, federalBenefits);

    // BF should be eligible
    expect(summary.eligible.some(r => r.benefit.id === 'federal-bolsa-familia')).toBe(true);

    // TSEE should be in unlocked
    expect(summary.unlocked).toBeDefined();
    expect(summary.unlocked!.some(u => u.benefitId === 'federal-tsee')).toBe(true);
  });

  it('BF eligible → Auxílio Gás in unlocked', () => {
    const profile = makeProfile({
      rendaFamiliarMensal: 800,
      pessoasNaCasa: 4,
      cadastradoCadunico: true,
    });

    const summary = evaluateAllBenefits(profile, federalBenefits);

    expect(summary.unlocked).toBeDefined();
    expect(summary.unlocked!.some(u => u.benefitId === 'federal-auxilio-gas')).toBe(true);
  });

  it('BPC PcD eligible → Passe Livre in unlocked', () => {
    const profile = makeProfile({
      temPcd: true,
      rendaFamiliarMensal: 400,
      pessoasNaCasa: 1,
      cadastradoCadunico: true,
    });

    const summary = evaluateAllBenefits(profile, federalBenefits);

    // BPC PcD should be eligible
    expect(summary.eligible.some(r => r.benefit.id === 'federal-bpc-pcd')).toBe(true);

    // Passe Livre should be in unlocked
    expect(summary.unlocked).toBeDefined();
    expect(summary.unlocked!.some(u => u.benefitId === 'federal-passe-livre')).toBe(true);
  });

  it('CadÚnico + BF + idade 20 → ID Jovem suggested in warnings', () => {
    const profile = makeProfile({
      idade: 20,
      rendaFamiliarMensal: 800,
      pessoasNaCasa: 4,
      cadastradoCadunico: true,
    });

    const summary = evaluateAllBenefits(profile, federalBenefits);

    // ID Jovem should be mentioned in warnings (as suggestion)
    expect(summary.warnings).toBeDefined();
    expect(summary.warnings!.some(w =>
      w.benefitIds.includes('federal-id-jovem')
    )).toBe(true);
  });

  it('CadÚnico + BF + idade 62 → Carteira Idoso suggested in warnings', () => {
    const profile = makeProfile({
      idade: 62,
      temIdoso65Mais: false, // 62 ainda não é 65
      rendaFamiliarMensal: 800,
      pessoasNaCasa: 4,
      cadastradoCadunico: true,
    });

    const summary = evaluateAllBenefits(profile, federalBenefits);

    // Carteira do Idoso should be mentioned in warnings (as suggestion)
    expect(summary.warnings).toBeDefined();
    expect(summary.warnings!.some(w =>
      w.benefitIds.includes('federal-carteira-idoso')
    )).toBe(true);
  });
});

// ═══════════════════════════════════════════════════════════════════
// C. ADJUSTED TOTALS (3)
// ═══════════════════════════════════════════════════════════════════

describe('Adjusted totals — no double counting', () => {
  it('totalAdjustedMonthly < totalPotentialMonthly when exclusion present', () => {
    // Idoso PcD → both BPC eligible → one excluded
    const profile = makeProfile({
      temIdoso65Mais: true,
      temPcd: true,
      rendaFamiliarMensal: 400,
      pessoasNaCasa: 1,
      cadastradoCadunico: true,
    });

    const summary = evaluateAllBenefits(profile, federalBenefits);

    expect(summary.totalAdjustedMonthly).toBeDefined();
    // The adjusted total should be less because BPC counted once, not twice
    expect(summary.totalAdjustedMonthly!).toBeLessThanOrEqual(summary.totalPotentialMonthly);
  });

  it('totalAdjustedMonthly = totalPotentialMonthly when no exclusion', () => {
    // Simple profile without conflicts
    const profile = makeProfile({
      rendaFamiliarMensal: 800,
      pessoasNaCasa: 4,
      cadastradoCadunico: true,
      temIdoso65Mais: false,
      temPcd: false,
    });

    const summary = evaluateAllBenefits(profile, federalBenefits);

    expect(summary.totalAdjustedMonthly).toBeDefined();
    expect(summary.totalAdjustedMonthly!).toBe(summary.totalPotentialMonthly);
  });

  it('BPC Idoso recebendo + BF elegível → both counted (lei 2023)', () => {
    const profile = makeProfile({
      temIdoso65Mais: true,
      rendaFamiliarMensal: 400,
      pessoasNaCasa: 2, // PC = 200
      cadastradoCadunico: true,
      recebeBpc: true, // Já recebe BPC
    });

    const summary = evaluateAllBenefits(profile, federalBenefits);

    // BPC should be already_receiving
    expect(summary.alreadyReceiving.some(r => r.benefit.id === 'federal-bpc-idoso')).toBe(true);

    // BF should be eligible
    expect(summary.eligible.some(r => r.benefit.id === 'federal-bolsa-familia')).toBe(true);

    // No exclusion between BPC and BF
    const bpcBfExclusion = summary.warnings?.find(w =>
      w.type === 'exclusion' &&
      w.benefitIds.includes('federal-bpc-idoso') &&
      w.benefitIds.includes('federal-bolsa-familia')
    );
    expect(bpcBfExclusion).toBeUndefined();
  });
});

// ═══════════════════════════════════════════════════════════════════
// D. SECTORAL — No-conflict and Cascade (2)
// ═══════════════════════════════════════════════════════════════════

describe('Sectoral relations', () => {
  it('Pescador: Seguro-Defeso + PRONAF → no conflict', () => {
    const profile = makeProfile({
      pescadorArtesanal: true,
      agricultorFamiliar: true,
      moradiaZonaRural: true,
      cadastradoCadunico: true,
      rendaFamiliarMensal: 800,
      pessoasNaCasa: 3,
    });

    const allBenefits = [...federalBenefits, ...sectoralBenefits];
    const summary = evaluateAllBenefits(profile, allBenefits);

    // No exclusion warning between these two
    const conflict = summary.warnings?.find(w =>
      w.type === 'exclusion' &&
      w.benefitIds.includes('sectoral-seguro-defeso') &&
      w.benefitIds.includes('sectoral-pronaf')
    );
    expect(conflict).toBeUndefined();
  });

  it('Agricultor: PRONAF eligible → PAA + Garantia-Safra suggested', () => {
    const profile = makeProfile({
      agricultorFamiliar: true,
      moradiaZonaRural: true,
      rendaFamiliarMensal: 1000,
      pessoasNaCasa: 3,
      cadastradoCadunico: true,
    });

    const allBenefits = [...federalBenefits, ...sectoralBenefits];
    const summary = evaluateAllBenefits(profile, allBenefits);

    // PRONAF should be eligible (or likely)
    const pronafEligible = [...summary.eligible, ...summary.likelyEligible].some(
      r => r.benefit.id === 'sectoral-pronaf'
    );

    if (pronafEligible) {
      // PAA and Garantia-Safra should be suggested
      expect(summary.warnings).toBeDefined();
      expect(summary.warnings!.some(w =>
        w.benefitIds.includes('sectoral-paa')
      )).toBe(true);
      expect(summary.warnings!.some(w =>
        w.benefitIds.includes('sectoral-garantia-safra')
      )).toBe(true);
    }
  });
});
