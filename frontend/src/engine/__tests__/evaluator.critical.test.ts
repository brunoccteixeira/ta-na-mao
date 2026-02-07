/**
 * Critical Benefits Regression Tests
 * 30 tests (3 per benefit: eligible, not-eligible, edge case)
 * Uses REAL benefit data and REAL eligibility rules.
 */
import { describe, it, expect } from 'vitest';
import { evaluateBenefit } from '../evaluator';
import { makeProfile } from './fixtures/testProfiles';
import { findBenefit } from './testHelpers';

// ═══════════════════════════════════════════════════════════════════
// 1. BOLSA FAMÍLIA
// ═══════════════════════════════════════════════════════════════════

describe('Bolsa Família (federal-bolsa-familia)', () => {
  const getBF = () => findBenefit('federal-bolsa-familia');

  it('eligible: rendaPC=200, CadÚnico=true', () => {
    const result = evaluateBenefit(
      makeProfile({
        rendaFamiliarMensal: 800,
        pessoasNaCasa: 4, // PC = 200
        cadastradoCadunico: true,
      }),
      getBF()
    );
    expect(result.status).toBe('eligible');
    expect(result.estimatedValue).toBeGreaterThan(0);
  });

  it('not eligible: rendaPC=500 (above 218)', () => {
    const result = evaluateBenefit(
      makeProfile({
        rendaFamiliarMensal: 2000,
        pessoasNaCasa: 4, // PC = 500
        cadastradoCadunico: true,
      }),
      getBF()
    );
    expect(result.status).toBe('not_eligible');
  });

  it('edge: rendaPC=218 exactly (limit)', () => {
    const result = evaluateBenefit(
      makeProfile({
        rendaFamiliarMensal: 872,
        pessoasNaCasa: 4, // PC = 218.0
        cadastradoCadunico: true,
      }),
      getBF()
    );
    expect(result.status).toBe('eligible');
  });
});

// ═══════════════════════════════════════════════════════════════════
// 2. BPC IDOSO
// ═══════════════════════════════════════════════════════════════════

describe('BPC Idoso (federal-bpc-idoso)', () => {
  const getBPC = () => findBenefit('federal-bpc-idoso');

  it('eligible: idoso 65+, rendaPC=400', () => {
    const result = evaluateBenefit(
      makeProfile({
        temIdoso65Mais: true,
        rendaFamiliarMensal: 400,
        pessoasNaCasa: 1, // PC = 400 <= 405.25
        recebeBolsaFamilia: false,
      }),
      getBPC()
    );
    expect(result.status).toBe('eligible');
    expect(result.estimatedValue).toBe(1621); // 1 SM
  });

  it('not eligible: not idoso', () => {
    const result = evaluateBenefit(
      makeProfile({
        temIdoso65Mais: false,
        rendaFamiliarMensal: 400,
        pessoasNaCasa: 1,
      }),
      getBPC()
    );
    expect(result.status).toBe('not_eligible');
  });

  it('edge: rendaPC=405.25 exactly (1/4 SM)', () => {
    const result = evaluateBenefit(
      makeProfile({
        temIdoso65Mais: true,
        rendaFamiliarMensal: 405.25,
        pessoasNaCasa: 1, // PC = 405.25
        recebeBolsaFamilia: false,
      }),
      getBPC()
    );
    expect(result.status).toBe('eligible');
  });
});

// ═══════════════════════════════════════════════════════════════════
// 3. BPC PcD
// ═══════════════════════════════════════════════════════════════════

describe('BPC PcD (federal-bpc-pcd)', () => {
  const getBPCPCD = () => findBenefit('federal-bpc-pcd');

  it('eligible: PcD=true, rendaPC=250', () => {
    const result = evaluateBenefit(
      makeProfile({
        temPcd: true,
        rendaFamiliarMensal: 500,
        pessoasNaCasa: 2, // PC = 250
      }),
      getBPCPCD()
    );
    expect(result.status).toBe('eligible');
    expect(result.estimatedValue).toBe(1621);
  });

  it('not eligible: PcD=false', () => {
    const result = evaluateBenefit(
      makeProfile({
        temPcd: false,
        rendaFamiliarMensal: 250,
        pessoasNaCasa: 1,
      }),
      getBPCPCD()
    );
    expect(result.status).toBe('not_eligible');
  });

  it('edge: PcD + idoso (overlap — both conditions met)', () => {
    const result = evaluateBenefit(
      makeProfile({
        temPcd: true,
        temIdoso65Mais: true,
        rendaFamiliarMensal: 400,
        pessoasNaCasa: 1,
      }),
      getBPCPCD()
    );
    // BPC PcD doesn't require NOT being idoso — should still be eligible
    expect(result.status).toBe('eligible');
  });
});

// ═══════════════════════════════════════════════════════════════════
// 4. FARMÁCIA POPULAR
// ═══════════════════════════════════════════════════════════════════

describe('Farmácia Popular (federal-farmacia-popular)', () => {
  const getFP = () => findBenefit('federal-farmacia-popular');

  it('eligible: any person with age (universal)', () => {
    const result = evaluateBenefit(
      makeProfile({ idade: 40 }),
      getFP()
    );
    expect(result.status).toBe('eligible');
  });

  it('eligible: elderly person', () => {
    const result = evaluateBenefit(
      makeProfile({ idade: 70, temIdoso65Mais: true }),
      getFP()
    );
    expect(result.status).toBe('eligible');
  });

  it('edge: age 0 (newborn — eligible with prescription)', () => {
    const result = evaluateBenefit(
      makeProfile({ idade: 0 }),
      getFP()
    );
    // Rule is idade >= 0, so 0 passes
    expect(result.status).toBe('eligible');
  });
});

// ═══════════════════════════════════════════════════════════════════
// 5. ABONO SALARIAL PIS/PASEP
// ═══════════════════════════════════════════════════════════════════

describe('Abono Salarial (federal-abono-salarial)', () => {
  const getAbono = () => findBenefit('federal-abono-salarial');

  it('eligible: CLT, renda=2000, 30+ dias', () => {
    const result = evaluateBenefit(
      makeProfile({
        trabalhoFormal: true,
        rendaFamiliarMensal: 2000,
        tempoCarteiraAssinada: 36,
      }),
      getAbono()
    );
    expect(result.status).toBe('eligible');
  });

  it('not eligible: renda=3000 (above 2766)', () => {
    const result = evaluateBenefit(
      makeProfile({
        trabalhoFormal: true,
        rendaFamiliarMensal: 3000,
        tempoCarteiraAssinada: 36,
      }),
      getAbono()
    );
    expect(result.status).toBe('not_eligible');
  });

  it('edge: renda=2766 exactly (limit INPC)', () => {
    const result = evaluateBenefit(
      makeProfile({
        trabalhoFormal: true,
        rendaFamiliarMensal: 2766,
        tempoCarteiraAssinada: 36,
      }),
      getAbono()
    );
    expect(result.status).toBe('eligible');
  });
});

// ═══════════════════════════════════════════════════════════════════
// 6. MINHA CASA MINHA VIDA
// ═══════════════════════════════════════════════════════════════════

describe('MCMV (federal-mcmv)', () => {
  const getMCMV = () => findBenefit('federal-mcmv');

  it('eligible: renda=5000, sem casa', () => {
    const result = evaluateBenefit(
      makeProfile({
        rendaFamiliarMensal: 5000,
        temCasaPropria: false,
      }),
      getMCMV()
    );
    expect(result.status).toBe('eligible');
  });

  it('not eligible: tem casa própria', () => {
    const result = evaluateBenefit(
      makeProfile({
        rendaFamiliarMensal: 5000,
        temCasaPropria: true,
      }),
      getMCMV()
    );
    expect(result.status).toBe('not_eligible');
  });

  it('edge: renda=12000 exactly (limit Faixa 4)', () => {
    const result = evaluateBenefit(
      makeProfile({
        rendaFamiliarMensal: 12000,
        temCasaPropria: false,
      }),
      getMCMV()
    );
    expect(result.status).toBe('eligible');
  });
});

// ═══════════════════════════════════════════════════════════════════
// 7. SEGURO-DESEMPREGO
// ═══════════════════════════════════════════════════════════════════

describe('Seguro-Desemprego (federal-seguro-desemprego)', () => {
  const getSD = () => findBenefit('federal-seguro-desemprego');

  it('eligible: desempregado, 12+ meses anteriores', () => {
    const result = evaluateBenefit(
      makeProfile({
        trabalhoFormal: false,
        tempoCarteiraAssinada: 14,
      }),
      getSD()
    );
    expect(result.status).toBe('eligible');
  });

  it('not eligible: still employed (trabalhoFormal=true)', () => {
    const result = evaluateBenefit(
      makeProfile({
        trabalhoFormal: true,
        tempoCarteiraAssinada: 24,
      }),
      getSD()
    );
    expect(result.status).toBe('not_eligible');
  });

  it('edge: exactly 12 months (minimum)', () => {
    const result = evaluateBenefit(
      makeProfile({
        trabalhoFormal: false,
        tempoCarteiraAssinada: 12,
      }),
      getSD()
    );
    expect(result.status).toBe('eligible');
  });
});

// ═══════════════════════════════════════════════════════════════════
// 8. AUXÍLIO GÁS
// ═══════════════════════════════════════════════════════════════════

describe('Auxílio Gás (federal-auxilio-gas)', () => {
  const getGas = () => findBenefit('federal-auxilio-gas');

  it('eligible: CadÚnico, rendaPC=400', () => {
    const result = evaluateBenefit(
      makeProfile({
        cadastradoCadunico: true,
        rendaFamiliarMensal: 1600,
        pessoasNaCasa: 4, // PC = 400
      }),
      getGas()
    );
    expect(result.status).toBe('eligible');
  });

  it('not eligible: rendaPC=1000 (above meio SM)', () => {
    const result = evaluateBenefit(
      makeProfile({
        cadastradoCadunico: true,
        rendaFamiliarMensal: 2000,
        pessoasNaCasa: 2, // PC = 1000
      }),
      getGas()
    );
    expect(result.status).toBe('not_eligible');
  });

  it('edge: rendaPC=810.50 exactly (meio SM)', () => {
    const result = evaluateBenefit(
      makeProfile({
        cadastradoCadunico: true,
        rendaFamiliarMensal: 810.50,
        pessoasNaCasa: 1, // PC = 810.50
      }),
      getGas()
    );
    expect(result.status).toBe('eligible');
  });
});

// ═══════════════════════════════════════════════════════════════════
// 9. PROUNI
// ═══════════════════════════════════════════════════════════════════

describe('ProUni (federal-prouni)', () => {
  const getProUni = () => findBenefit('federal-prouni');

  it('eligible: rede pública, rendaPC=2000', () => {
    const result = evaluateBenefit(
      makeProfile({
        redePublica: true,
        rendaFamiliarMensal: 4000,
        pessoasNaCasa: 2, // PC = 2000
      }),
      getProUni()
    );
    expect(result.status).toBe('eligible');
  });

  it('not eligible: rede privada (redePublica=false)', () => {
    const result = evaluateBenefit(
      makeProfile({
        redePublica: false,
        rendaFamiliarMensal: 2000,
        pessoasNaCasa: 2,
      }),
      getProUni()
    );
    expect(result.status).toBe('not_eligible');
  });

  it('edge: rendaPC=4863 exactly (3 SM — limit parcial)', () => {
    const result = evaluateBenefit(
      makeProfile({
        redePublica: true,
        rendaFamiliarMensal: 4863,
        pessoasNaCasa: 1, // PC = 4863
      }),
      getProUni()
    );
    expect(result.status).toBe('eligible');
  });
});

// ═══════════════════════════════════════════════════════════════════
// 10. FIES
// ═══════════════════════════════════════════════════════════════════

describe('FIES (federal-fies)', () => {
  const getFIES = () => findBenefit('federal-fies');

  it('eligible: rendaPC=3000 (within 3 SM)', () => {
    const result = evaluateBenefit(
      makeProfile({
        rendaFamiliarMensal: 6000,
        pessoasNaCasa: 2, // PC = 3000
      }),
      getFIES()
    );
    expect(result.status).toBe('eligible');
  });

  it('not eligible: rendaPC=5000 (above 3 SM)', () => {
    const result = evaluateBenefit(
      makeProfile({
        rendaFamiliarMensal: 10000,
        pessoasNaCasa: 2, // PC = 5000
      }),
      getFIES()
    );
    expect(result.status).toBe('not_eligible');
  });

  it('edge: rendaPC=4863 exactly (3 SM limit)', () => {
    const result = evaluateBenefit(
      makeProfile({
        rendaFamiliarMensal: 4863,
        pessoasNaCasa: 1, // PC = 4863
      }),
      getFIES()
    );
    expect(result.status).toBe('eligible');
  });
});

// ═══════════════════════════════════════════════════════════════════
// BONUS: Already-Receiving Detection
// ═══════════════════════════════════════════════════════════════════

describe('Already-receiving detection', () => {
  it('Bolsa Família: already receiving', () => {
    const bf = findBenefit('federal-bolsa-familia');
    const result = evaluateBenefit(
      makeProfile({
        recebeBolsaFamilia: true,
        cadastradoCadunico: true,
        rendaFamiliarMensal: 400,
        pessoasNaCasa: 4,
      }),
      bf
    );
    expect(result.status).toBe('already_receiving');
  });

  it('BPC Idoso: already receiving', () => {
    const bpc = findBenefit('federal-bpc-idoso');
    const result = evaluateBenefit(
      makeProfile({
        recebeBpc: true,
        temIdoso65Mais: true,
        rendaFamiliarMensal: 400,
        pessoasNaCasa: 1,
      }),
      bpc
    );
    expect(result.status).toBe('already_receiving');
  });

  it('BPC PcD: already receiving', () => {
    const bpc = findBenefit('federal-bpc-pcd');
    const result = evaluateBenefit(
      makeProfile({
        recebeBpc: true,
        temPcd: true,
        rendaFamiliarMensal: 400,
        pessoasNaCasa: 1,
      }),
      bpc
    );
    expect(result.status).toBe('already_receiving');
  });
});
