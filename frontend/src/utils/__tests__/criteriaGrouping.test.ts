import { describe, it, expect } from 'vitest';
import { groupAndEvaluateCriteria, getRequiredFields } from '../criteriaGrouping';
import type { EligibilityRule, EligibilityResult, Benefit } from '../../engine/types';

// Helper to build a minimal rule
function makeRule(field: string, description: string): EligibilityRule {
  return { field, operator: 'eq', value: true, description };
}

// Helper to build a minimal EligibilityResult
function makeResult(
  matched: string[] = [],
  failed: string[] = [],
  inconclusive: string[] = [],
): EligibilityResult {
  return {
    benefit: {} as Benefit,
    status: 'eligible',
    matchedRules: matched,
    failedRules: failed,
    inconclusiveRules: inconclusive,
  };
}

// ─── groupAndEvaluateCriteria ───

describe('groupAndEvaluateCriteria', () => {
  it('agrupa regras por categoria corretamente', () => {
    const rules = [
      makeRule('rendaFamiliarMensal', 'Renda familiar'),
      makeRule('pessoasNaCasa', 'Pessoas na casa'),
      makeRule('cadastradoCadunico', 'CadUnico'),
    ];

    const groups = groupAndEvaluateCriteria(rules, null);

    const keys = groups.map(g => g.groupKey);
    expect(keys).toContain('renda');
    expect(keys).toContain('familia');
    expect(keys).toContain('documentacao');
  });

  it('ordena grupos pela ordem definida em GROUP_META', () => {
    const rules = [
      makeRule('temCasaPropria', 'Casa propria'),      // moradia (order 4)
      makeRule('cadastradoCadunico', 'CadUnico'),      // documentacao (order 0)
      makeRule('rendaFamiliarMensal', 'Renda'),        // renda (order 1)
      makeRule('pessoasNaCasa', 'Familia'),             // familia (order 2)
      makeRule('profissao', 'Profissao'),               // trabalho (order 3)
    ];

    const groups = groupAndEvaluateCriteria(rules, null);
    const keys = groups.map(g => g.groupKey);

    expect(keys).toEqual(['documentacao', 'renda', 'familia', 'trabalho', 'moradia']);
  });

  it('mapeia campo desconhecido para grupo "outros"', () => {
    const rules = [makeRule('campoInventado', 'Campo inventado')];

    const groups = groupAndEvaluateCriteria(rules, null);

    expect(groups).toHaveLength(1);
    expect(groups[0].groupKey).toBe('outros');
    expect(groups[0].label).toBe('Outras condições');
  });

  it('regras sem result retornam todas como "pending"', () => {
    const rules = [
      makeRule('rendaFamiliarMensal', 'Renda'),
      makeRule('cadastradoCadunico', 'CadUnico'),
    ];

    const groups = groupAndEvaluateCriteria(rules, null);
    const allStatuses = groups.flatMap(g => g.rules.map(r => r.status));

    expect(allStatuses.every(s => s === 'pending')).toBe(true);
  });

  it('regras com result mapeiam met/not_met/inconclusive corretamente', () => {
    const rules = [
      makeRule('rendaFamiliarMensal', 'Renda baixa'),
      makeRule('cadastradoCadunico', 'Tem CadUnico'),
      makeRule('temIdoso65Mais', 'Tem idoso'),
    ];

    const result = makeResult(
      ['Renda baixa'],
      ['Tem CadUnico'],
      ['Tem idoso'],
    );

    const groups = groupAndEvaluateCriteria(rules, result);
    const allRules = groups.flatMap(g => g.rules);

    const rendaRule = allRules.find(r => r.rule.description === 'Renda baixa');
    const cadRule = allRules.find(r => r.rule.description === 'Tem CadUnico');
    const idosoRule = allRules.find(r => r.rule.description === 'Tem idoso');

    expect(rendaRule?.status).toBe('met');
    expect(cadRule?.status).toBe('not_met');
    expect(idosoRule?.status).toBe('inconclusive');
  });

  it('array vazio retorna array vazio', () => {
    const groups = groupAndEvaluateCriteria([], null);
    expect(groups).toEqual([]);
  });

  it('regra com descricao nao listada em nenhum resultado fica "pending"', () => {
    const rules = [makeRule('rendaFamiliarMensal', 'Regra nao avaliada')];
    const result = makeResult(['Outra regra'], ['Mais outra'], []);

    const groups = groupAndEvaluateCriteria(rules, result);
    expect(groups[0].rules[0].status).toBe('pending');
  });
});

// ─── getRequiredFields ───

describe('getRequiredFields', () => {
  it('extrai campos simples', () => {
    const rules = [
      makeRule('cadastradoCadunico', 'CadUnico'),
      makeRule('temIdoso65Mais', 'Idoso'),
    ];

    const fields = getRequiredFields(rules);
    expect(fields).toContain('cadastradoCadunico');
    expect(fields).toContain('temIdoso65Mais');
  });

  it('expande rendaPerCapita em rendaFamiliarMensal + pessoasNaCasa', () => {
    const rules = [makeRule('rendaPerCapita', 'Renda per capita')];

    const fields = getRequiredFields(rules);
    expect(fields).toContain('rendaFamiliarMensal');
    expect(fields).toContain('pessoasNaCasa');
    expect(fields).not.toContain('rendaPerCapita');
  });

  it('remove duplicatas', () => {
    const rules = [
      makeRule('rendaPerCapita', 'Renda per capita'),
      makeRule('pessoasNaCasa', 'Pessoas'),
    ];

    const fields = getRequiredFields(rules);
    const pessoasCount = fields.filter(f => f === 'pessoasNaCasa').length;
    expect(pessoasCount).toBe(1);
  });

  it('array vazio retorna array vazio', () => {
    expect(getRequiredFields([])).toEqual([]);
  });
});
