/**
 * Criteria grouping utility — groups eligibility rules by category
 * and maps each rule to its evaluation status.
 */

import type { EligibilityRule, EligibilityResult } from '../engine/types';

export type CriterionStatus = 'met' | 'not_met' | 'inconclusive' | 'pending';

export interface EvaluatedRule {
  rule: EligibilityRule;
  status: CriterionStatus;
}

export interface GroupedCriteria {
  groupKey: string;
  label: string;
  lucideIcon: string;
  rules: EvaluatedRule[];
}

// Field → group mapping
const FIELD_TO_GROUP: Record<string, string> = {
  cadastradoCadunico: 'documentacao',
  cpf: 'documentacao',
  nisCadunico: 'documentacao',

  rendaPerCapita: 'renda',
  rendaFamiliarMensal: 'renda',
  trabalhoFormal: 'renda',

  temIdoso65Mais: 'familia',
  temCrianca0a6: 'familia',
  pessoasNaCasa: 'familia',
  quantidadeFilhos: 'familia',
  temGestante: 'familia',
  temPcd: 'familia',
  idade: 'familia',

  profissao: 'trabalho',
  temMei: 'trabalho',
  trabalhaAplicativo: 'trabalho',
  agricultorFamiliar: 'trabalho',
  pescadorArtesanal: 'trabalho',
  catadorReciclavel: 'trabalho',
  temCarteiraAssinada: 'trabalho',
  tempoCarteiraAssinada: 'trabalho',

  temCasaPropria: 'moradia',
  moradiaZonaRural: 'moradia',

  recebeBolsaFamilia: 'documentacao',
  recebeBpc: 'documentacao',
  estudante: 'familia',
  redePublica: 'familia',
};

interface GroupMeta {
  label: string;
  lucideIcon: string;
  order: number;
}

const GROUP_META: Record<string, GroupMeta> = {
  documentacao: { label: 'Documentos e cadastros', lucideIcon: 'FileText', order: 0 },
  renda: { label: 'Sobre sua renda', lucideIcon: 'DollarSign', order: 1 },
  familia: { label: 'Sobre sua família', lucideIcon: 'Users', order: 2 },
  trabalho: { label: 'Sobre seu trabalho', lucideIcon: 'Briefcase', order: 3 },
  moradia: { label: 'Sobre sua casa', lucideIcon: 'Home', order: 4 },
  outros: { label: 'Outras condições', lucideIcon: 'ClipboardList', order: 5 },
};

/**
 * Determine the status of a single rule based on the evaluation result.
 * If `result` is null (no evaluation yet), all rules are 'pending'.
 */
function getRuleStatus(
  rule: EligibilityRule,
  result: EligibilityResult | null,
): CriterionStatus {
  if (!result) return 'pending';

  const desc = rule.description;

  if (result.matchedRules.includes(desc)) return 'met';
  if (result.failedRules.includes(desc)) return 'not_met';
  if (result.inconclusiveRules.includes(desc)) return 'inconclusive';

  return 'pending';
}

/**
 * Group a benefit's eligibility rules by category and attach evaluation status.
 */
export function groupAndEvaluateCriteria(
  rules: EligibilityRule[],
  result: EligibilityResult | null,
): GroupedCriteria[] {
  const groups: Record<string, EvaluatedRule[]> = {};

  for (const rule of rules) {
    const groupKey = FIELD_TO_GROUP[rule.field] || 'outros';

    if (!groups[groupKey]) {
      groups[groupKey] = [];
    }

    groups[groupKey].push({
      rule,
      status: getRuleStatus(rule, result),
    });
  }

  return Object.entries(groups)
    .map(([groupKey, evaluatedRules]) => {
      const meta = GROUP_META[groupKey] || GROUP_META.outros;
      return {
        groupKey,
        label: meta.label,
        lucideIcon: meta.lucideIcon,
        rules: evaluatedRules,
      };
    })
    .sort((a, b) => {
      const orderA = GROUP_META[a.groupKey]?.order ?? 99;
      const orderB = GROUP_META[b.groupKey]?.order ?? 99;
      return orderA - orderB;
    });
}

/**
 * Derive which profile fields are needed from a set of eligibility rules.
 * Expands computed fields (e.g. rendaPerCapita → rendaFamiliarMensal + pessoasNaCasa).
 */
export function getRequiredFields(rules: EligibilityRule[]): string[] {
  const fields = new Set<string>();

  for (const rule of rules) {
    if (rule.field === 'rendaPerCapita') {
      fields.add('rendaFamiliarMensal');
      fields.add('pessoasNaCasa');
    } else {
      fields.add(rule.field);
    }
  }

  return Array.from(fields);
}
