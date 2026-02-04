import { describe, it, expect, vi, beforeEach } from 'vitest';
import { render, screen } from '@testing-library/react';
import type { Benefit, CitizenProfile, EligibilityResult } from '../../../engine/types';
import { DEFAULT_CITIZEN_PROFILE } from '../../../engine/types';

// ── Mocks ──

vi.mock('react-router-dom', () => ({
  Link: ({ children, to, ...props }: { children: React.ReactNode; to: string; [k: string]: unknown }) => (
    <a href={to} {...props}>{children}</a>
  ),
  useParams: () => ({ id: 'federal-bolsa-familia' }),
}));

const mockEvaluateBenefit = vi.fn();
vi.mock('../../../engine/evaluator', () => ({
  evaluateBenefit: (...args: unknown[]) => mockEvaluateBenefit(...args),
}));

const mockFormatBenefitValue = vi.fn();
vi.mock('../../../engine/catalog', () => ({
  formatBenefitValue: (...args: unknown[]) => mockFormatBenefitValue(...args),
}));

// Import AFTER mocks
import BenefitEligibilityChecker from '../BenefitEligibilityChecker';

// ── Fixtures ──

const baseBenefit: Benefit = {
  id: 'federal-bolsa-familia',
  name: 'Bolsa Família',
  shortDescription: 'Programa de transferência de renda',
  scope: 'federal',
  eligibilityRules: [
    { field: 'rendaPerCapita', operator: 'lte', value: 218, description: 'Renda per capita até R$ 218' },
    { field: 'cadastradoCadunico', operator: 'eq', value: true, description: 'Cadastrado no CadÚnico' },
  ],
  whereToApply: 'CRAS',
  documentsRequired: ['CPF', 'RG'],
  lastUpdated: '2025-01-01',
  status: 'active',
  icon: '💰',
};

const baseProfile: CitizenProfile = {
  ...DEFAULT_CITIZEN_PROFILE,
  estado: 'SP',
  rendaFamiliarMensal: 500,
  pessoasNaCasa: 4,
  cadastradoCadunico: true,
};

const eligibleResult: EligibilityResult = {
  benefit: baseBenefit,
  status: 'eligible',
  matchedRules: ['Renda per capita até R$ 218', 'Cadastrado no CadÚnico'],
  failedRules: [],
  inconclusiveRules: [],
  estimatedValue: 600,
  reason: 'Você atende a todos os requisitos',
};

const notEligibleResult: EligibilityResult = {
  benefit: baseBenefit,
  status: 'not_eligible',
  matchedRules: [],
  failedRules: ['Renda per capita até R$ 218'],
  inconclusiveRules: ['Cadastrado no CadÚnico'],
  reason: 'Renda per capita até R$ 218',
};

// ── Tests ──

describe('BenefitEligibilityChecker', () => {
  beforeEach(() => {
    vi.clearAllMocks();
    mockFormatBenefitValue.mockReturnValue('R$ 600/mês');
  });

  it('sem profile renderiza MiniProfileForm', () => {
    render(
      <BenefitEligibilityChecker
        benefit={baseBenefit}
        profile={null}
        onProfileSubmit={vi.fn()}
      />,
    );

    expect(screen.getByText('Precisamos de algumas informações')).toBeInTheDocument();
    // Summary bar should NOT appear without profile
    expect(screen.queryByText(/critérios atendidos/)).not.toBeInTheDocument();
  });

  it('com profile renderiza summary bar e criteria sections', () => {
    mockEvaluateBenefit.mockReturnValue(eligibleResult);

    render(
      <BenefitEligibilityChecker
        benefit={baseBenefit}
        profile={baseProfile}
        onProfileSubmit={vi.fn()}
      />,
    );

    // Summary bar
    expect(screen.getByText('Você tem direito!')).toBeInTheDocument();
    expect(screen.getByText(/critérios atendidos/)).toBeInTheDocument();
  });

  it('beneficio com estimatedValue mostra valor formatado', () => {
    mockEvaluateBenefit.mockReturnValue(eligibleResult);
    mockFormatBenefitValue.mockReturnValue('R$ 600');

    const benefitWithValue: Benefit = {
      ...baseBenefit,
      estimatedValue: { type: 'monthly', min: 600, max: 600 },
    };

    render(
      <BenefitEligibilityChecker
        benefit={benefitWithValue}
        profile={baseProfile}
        onProfileSubmit={vi.fn()}
      />,
    );

    expect(mockFormatBenefitValue).toHaveBeenCalledWith(benefitWithValue);
    expect(screen.getByText('R$ 600')).toBeInTheDocument();
  });

  it('renderiza scope badge federal com texto correto', () => {
    mockEvaluateBenefit.mockReturnValue(eligibleResult);

    render(
      <BenefitEligibilityChecker
        benefit={baseBenefit}
        profile={baseProfile}
        onProfileSubmit={vi.fn()}
      />,
    );

    expect(screen.getByText('Federal')).toBeInTheDocument();
  });

  it('scope badge estadual para benefit state', () => {
    mockEvaluateBenefit.mockReturnValue(eligibleResult);

    const stateBenefit: Benefit = {
      ...baseBenefit,
      scope: 'state',
      state: 'SP',
    };

    render(
      <BenefitEligibilityChecker
        benefit={stateBenefit}
        profile={baseProfile}
        onProfileSubmit={vi.fn()}
      />,
    );

    expect(screen.getByText('Estadual')).toBeInTheDocument();
  });

  it('not_eligible mostra mensagem "Não atende agora"', () => {
    mockEvaluateBenefit.mockReturnValue(notEligibleResult);

    render(
      <BenefitEligibilityChecker
        benefit={baseBenefit}
        profile={baseProfile}
        onProfileSubmit={vi.fn()}
      />,
    );

    expect(screen.getByText('Não atende agora')).toBeInTheDocument();
  });

  it('renderiza link "Ver todos os benefícios" sempre', () => {
    render(
      <BenefitEligibilityChecker
        benefit={baseBenefit}
        profile={null}
        onProfileSubmit={vi.fn()}
      />,
    );

    const link = screen.getByText('Ver todos os benefícios');
    expect(link).toBeInTheDocument();
    expect(link.closest('a')).toHaveAttribute('href', '/beneficios');
  });

  it('mostra botao "Atualizar meus dados" quando profile existe', () => {
    mockEvaluateBenefit.mockReturnValue(eligibleResult);

    render(
      <BenefitEligibilityChecker
        benefit={baseBenefit}
        profile={baseProfile}
        onProfileSubmit={vi.fn()}
      />,
    );

    expect(screen.getByText('Atualizar meus dados')).toBeInTheDocument();
  });
});
