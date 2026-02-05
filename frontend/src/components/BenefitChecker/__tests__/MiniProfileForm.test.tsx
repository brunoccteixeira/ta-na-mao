import { describe, it, expect, vi } from 'vitest';
import { render, screen } from '@testing-library/react';
import userEvent from '@testing-library/user-event';
import MiniProfileForm from '../MiniProfileForm';
import { DEFAULT_CITIZEN_PROFILE } from '../../../engine/types';
import type { EligibilityRule, CitizenProfile } from '../../../engine/types';

// Helper to build a minimal rule
function makeRule(field: string): EligibilityRule {
  return { field, operator: 'eq', value: true, description: `Rule for ${field}` };
}

describe('MiniProfileForm', () => {
  it('renderiza apenas campos necessarios baseado nas rules', () => {
    const rules = [
      makeRule('rendaFamiliarMensal'),
      makeRule('cadastradoCadunico'),
    ];

    render(<MiniProfileForm rules={rules} onSubmit={vi.fn()} />);

    expect(screen.getByText('Renda da família por mês')).toBeInTheDocument();
    expect(screen.getByText('Tem Cadastro Único (CadÚnico)?')).toBeInTheDocument();
    // Should NOT render fields not in rules
    expect(screen.queryByText('Tem casa própria?')).not.toBeInTheDocument();
  });

  it('campo numerico aceita input', async () => {
    const user = userEvent.setup({ delay: null }); // Disable delay for faster tests
    const rules = [makeRule('rendaFamiliarMensal')];

    render(<MiniProfileForm rules={rules} onSubmit={vi.fn()} />);

    const input = screen.getByPlaceholderText('Ex: 800');
    await user.type(input, '1500');

    expect(input).toHaveValue(1500);
  });

  it('campo numerico vazio converte para 0 no submit', async () => {
    const user = userEvent.setup({ delay: null }); // Disable delay for faster tests
    const onSubmit = vi.fn();
    const rules = [makeRule('rendaFamiliarMensal')];

    render(<MiniProfileForm rules={rules} onSubmit={onSubmit} />);

    // Don't type anything — leave empty
    const submitBtn = screen.getByText('Verificar Agora');
    await user.click(submitBtn);

    expect(onSubmit).toHaveBeenCalledTimes(1);
    const submittedProfile = onSubmit.mock.calls[0][0] as CitizenProfile;
    expect(submittedProfile.rendaFamiliarMensal).toBe(0);
  });

  it('campo boolean: botoes Sim/Nao toggleam valor', async () => {
    const user = userEvent.setup({ delay: null }); // Disable delay for faster tests
    const rules = [makeRule('cadastradoCadunico')];

    render(<MiniProfileForm rules={rules} onSubmit={vi.fn()} />);

    const simButtons = screen.getAllByText('Sim');
    const naoButtons = screen.getAllByText('Não');

    // Click Sim
    await user.click(simButtons[0]);
    // The Sim button should have the active style (emerald)
    expect(simButtons[0].className).toContain('emerald');

    // Click Nao
    await user.click(naoButtons[0]);
    expect(naoButtons[0].className).toContain('emerald');
  }, 15000); // Increased timeout

  it('submit chama onSubmit com CitizenProfile completo (merged com DEFAULT)', async () => {
    const user = userEvent.setup({ delay: null }); // Disable delay for faster tests
    const onSubmit = vi.fn();
    const rules = [makeRule('rendaFamiliarMensal'), makeRule('cadastradoCadunico')];

    render(<MiniProfileForm rules={rules} onSubmit={onSubmit} />);

    const input = screen.getByPlaceholderText('Ex: 800');
    await user.type(input, '500');

    const simButtons = screen.getAllByText('Sim');
    await user.click(simButtons[0]);

    await user.click(screen.getByText('Verificar Agora'));

    expect(onSubmit).toHaveBeenCalledTimes(1);
    const profile = onSubmit.mock.calls[0][0] as CitizenProfile;

    // Fields from form
    expect(profile.rendaFamiliarMensal).toBe(500);
    expect(profile.cadastradoCadunico).toBe(true);

    // Fields from DEFAULT_CITIZEN_PROFILE
    expect(profile.pessoasNaCasa).toBe(DEFAULT_CITIZEN_PROFILE.pessoasNaCasa);
    expect(profile.temMei).toBe(DEFAULT_CITIZEN_PROFILE.temMei);
  }, 15000); // Increased timeout

  it('initialProfile preenche valores existentes', () => {
    const rules = [makeRule('rendaFamiliarMensal'), makeRule('cadastradoCadunico')];
    const initial: Partial<CitizenProfile> = {
      rendaFamiliarMensal: 1200,
      cadastradoCadunico: true,
    };

    render(
      <MiniProfileForm rules={rules} onSubmit={vi.fn()} initialProfile={initial} />,
    );

    const input = screen.getByPlaceholderText('Ex: 800');
    expect(input).toHaveValue(1200);
  });

  it('nenhum campo configurado retorna null', () => {
    // Rule with a field that has no FIELD_CONFIG entry
    const rules = [makeRule('campoSemConfig')];

    const { container } = render(
      <MiniProfileForm rules={rules} onSubmit={vi.fn()} />,
    );

    expect(container.innerHTML).toBe('');
  });

  it('expande rendaPerCapita para rendaFamiliarMensal + pessoasNaCasa', () => {
    const rules = [makeRule('rendaPerCapita')];

    render(<MiniProfileForm rules={rules} onSubmit={vi.fn()} />);

    expect(screen.getByText('Renda da família por mês')).toBeInTheDocument();
    expect(screen.getByText('Quantas pessoas moram na casa')).toBeInTheDocument();
  });
});
