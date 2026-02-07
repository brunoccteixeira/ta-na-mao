/**
 * Benefit Relations Map — declarative rules for exclusions, cascades, and suggestions.
 *
 * Base legal das relações:
 * - LOAS (Lei 8.742/1993, Art. 20) — BPC
 * - Lei 14.601/2023 — permite acumulação BPC + Bolsa Família
 * - Decreto 12.534/2025 — BPC incompatível com Seguro-Desemprego
 * - Lei 7.998/1990 — Abono Salarial × Seguro-Desemprego
 * - Regulamentos MEC — ProUni integral × FIES
 */

export type RelationType =
  | 'excludes'      // X exclui Y (não pode ter os 2)
  | 'unlocks'       // Ter X dá acesso automático a Y
  | 'suggests'      // Ter X indica que deve pedir Y
  | 'choose_best';  // Deve escolher entre X e Y (pegar o maior)

export interface BenefitRelation {
  from: string;
  to: string;
  type: RelationType;
  description: string;
  legalBasis?: string;
  bidirectional?: boolean;
}

// Padrão de aposentadorias para exclusão com BPC
const APOSENTADORIA_IDS = [
  'federal-aposentadoria-rural',
  'federal-aposentadoria-idade',
  'federal-aposentadoria-tempo',
  'federal-aposentadoria-invalidez',
  'federal-aposentadoria-especial',
  'federal-aposentadoria-hibrida',
  'federal-aposentadoria-professor',
];

const BPC_IDS = ['federal-bpc-idoso', 'federal-bpc-pcd'];

// ─── Exclusões mútuas ───

const exclusions: BenefitRelation[] = [
  // BPC Idoso × BPC PcD (mesma pessoa não pode ter os dois)
  {
    from: 'federal-bpc-idoso',
    to: 'federal-bpc-pcd',
    type: 'excludes',
    description: 'BPC Idoso e BPC PcD: você pode receber apenas um. Recomendamos o de maior valor.',
    legalBasis: 'LOAS Art. 20, Lei 8.742/1993',
    bidirectional: true,
  },

  // BPC × Aposentadorias INSS
  ...BPC_IDS.flatMap(bpc =>
    APOSENTADORIA_IDS.map(apos => ({
      from: bpc,
      to: apos,
      type: 'excludes' as const,
      description: `${bpc.includes('idoso') ? 'BPC Idoso' : 'BPC PcD'} e Aposentadoria INSS são incompatíveis. Escolha o de maior valor.`,
      legalBasis: 'LOAS Art. 20, §4º',
      bidirectional: true,
    }))
  ),

  // BPC × Seguro-Desemprego
  ...BPC_IDS.map(bpc => ({
    from: bpc,
    to: 'federal-seguro-desemprego',
    type: 'excludes' as const,
    description: `${bpc.includes('idoso') ? 'BPC Idoso' : 'BPC PcD'} e Seguro-Desemprego são incompatíveis.`,
    legalBasis: 'Decreto 12.534/2025',
    bidirectional: true,
  })),

  // Abono Salarial × Seguro-Desemprego
  {
    from: 'federal-abono-salarial',
    to: 'federal-seguro-desemprego',
    type: 'excludes',
    description: 'Abono Salarial e Seguro-Desemprego não podem ser recebidos ao mesmo tempo.',
    legalBasis: 'Lei 7.998/1990',
    bidirectional: true,
  },

  // ProUni integral × FIES
  {
    from: 'federal-prouni',
    to: 'federal-fies',
    type: 'excludes',
    description: 'ProUni com bolsa integral não pode ser acumulado com FIES.',
    legalBasis: 'Regulamentos MEC',
    bidirectional: true,
  },
];

// ─── Cascatas (ter X → já tem Y automaticamente) ───

const cascades: BenefitRelation[] = [
  // Bolsa Família → Tarifa Social de Energia (cruzamento CadÚnico mensal)
  {
    from: 'federal-bolsa-familia',
    to: 'federal-tsee',
    type: 'unlocks',
    description: 'Quem recebe Bolsa Família já tem Tarifa Social de Energia automaticamente.',
    legalBasis: 'Lei 12.212/2010, Art. 2º',
  },
  // Bolsa Família → Tarifa Social de Água
  {
    from: 'federal-bolsa-familia',
    to: 'federal-tarifa-social-agua',
    type: 'unlocks',
    description: 'Quem recebe Bolsa Família já tem Tarifa Social de Água automaticamente.',
    legalBasis: 'Decreto 7.217/2010',
  },
  // Bolsa Família → Auxílio Gás (SAGICAD automático)
  {
    from: 'federal-bolsa-familia',
    to: 'federal-auxilio-gas',
    type: 'unlocks',
    description: 'Quem recebe Bolsa Família já tem Auxílio Gás automaticamente via SAGICAD.',
    legalBasis: 'Lei 14.237/2021',
  },
  // Bolsa Família → Farmácia Popular 100% grátis
  {
    from: 'federal-bolsa-familia',
    to: 'federal-farmacia-popular',
    type: 'unlocks',
    description: 'Quem recebe Bolsa Família tem 100% de gratuidade na Farmácia Popular (não só 50%).',
    legalBasis: 'Decreto 5.090/2004',
  },

  // BPC → Tarifa Social de Energia
  ...BPC_IDS.map(bpc => ({
    from: bpc,
    to: 'federal-tsee',
    type: 'unlocks' as const,
    description: 'Quem recebe BPC já tem Tarifa Social de Energia automaticamente.',
    legalBasis: 'Lei 12.212/2010, Art. 2º',
  })),
  // BPC → Tarifa Social de Água
  ...BPC_IDS.map(bpc => ({
    from: bpc,
    to: 'federal-tarifa-social-agua',
    type: 'unlocks' as const,
    description: 'Quem recebe BPC já tem Tarifa Social de Água automaticamente.',
    legalBasis: 'Decreto 7.217/2010',
  })),
  // BPC PcD → Passe Livre
  {
    from: 'federal-bpc-pcd',
    to: 'federal-passe-livre',
    type: 'unlocks',
    description: 'Quem recebe BPC PcD tem direito ao Passe Livre Interestadual.',
    legalBasis: 'Lei 8.899/1994',
  },

  // CadÚnico → ID Jovem (15-29 anos, verificado pelo evaluator)
  {
    from: 'federal-bolsa-familia',
    to: 'federal-id-jovem',
    type: 'suggests',
    description: 'Com CadÚnico/Bolsa Família, jovens de 15 a 29 anos podem solicitar a ID Jovem.',
    legalBasis: 'Decreto 9.306/2018',
  },
  // CadÚnico → Carteira do Idoso (60+)
  {
    from: 'federal-bolsa-familia',
    to: 'federal-carteira-idoso',
    type: 'suggests',
    description: 'Com CadÚnico/Bolsa Família, idosos de 60+ podem solicitar a Carteira do Idoso.',
    legalBasis: 'Estatuto do Idoso, Lei 10.741/2003',
  },
  // CadÚnico → Isenção de Taxa de Concurso
  {
    from: 'federal-bolsa-familia',
    to: 'federal-isencao-taxa-concurso',
    type: 'suggests',
    description: 'Com CadÚnico/Bolsa Família, você pode pedir isenção de taxa em concursos públicos.',
    legalBasis: 'Lei 13.656/2018',
  },
];

// ─── Sugestões e escolhas ───

const suggestions: BenefitRelation[] = [
  // BPC Idoso + BF → PODEM acumular (informativo)
  {
    from: 'federal-bpc-idoso',
    to: 'federal-bolsa-familia',
    type: 'suggests',
    description: 'BPC Idoso e Bolsa Família podem ser acumulados desde 2023. Você pode ter os dois!',
    legalBasis: 'Lei 14.601/2023',
    bidirectional: true,
  },
  // Aposentadoria Rural vs BPC Idoso
  {
    from: 'federal-aposentadoria-rural',
    to: 'federal-bpc-idoso',
    type: 'choose_best',
    description: 'Aposentadoria Rural e BPC Idoso: compare os valores e escolha o melhor para você.',
    legalBasis: 'LOAS Art. 20, §4º',
    bidirectional: true,
  },
  // Cascata agrícola: PRONAF → PAA + Garantia-Safra
  {
    from: 'sectoral-pronaf',
    to: 'sectoral-paa',
    type: 'suggests',
    description: 'Quem tem PRONAF/DAP geralmente pode acessar o PAA (Programa de Aquisição de Alimentos).',
  },
  {
    from: 'sectoral-pronaf',
    to: 'sectoral-garantia-safra',
    type: 'suggests',
    description: 'Quem tem PRONAF/DAP pode aderir ao Garantia-Safra para proteção contra seca.',
  },
];

/** All benefit relations */
export const BENEFIT_RELATIONS: BenefitRelation[] = [
  ...exclusions,
  ...cascades,
  ...suggestions,
];

/**
 * Find all relations where a given benefit is involved (as from or to).
 */
export function getRelationsForBenefit(benefitId: string): BenefitRelation[] {
  return BENEFIT_RELATIONS.filter(
    r => r.from === benefitId || r.to === benefitId ||
      (r.bidirectional && (r.from === benefitId || r.to === benefitId))
  );
}

/**
 * Find exclusion pairs — returns the "other" benefit ID that conflicts.
 */
export function getExclusions(benefitId: string): string[] {
  return BENEFIT_RELATIONS
    .filter(r => r.type === 'excludes' && (r.from === benefitId || (r.bidirectional && r.to === benefitId)))
    .map(r => r.from === benefitId ? r.to : r.from);
}

/**
 * Find benefits unlocked by a given benefit.
 */
export function getUnlocked(benefitId: string): BenefitRelation[] {
  return BENEFIT_RELATIONS.filter(
    r => (r.type === 'unlocks' || r.type === 'suggests') && r.from === benefitId
  );
}
