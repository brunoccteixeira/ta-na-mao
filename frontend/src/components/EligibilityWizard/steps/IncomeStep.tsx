/**
 * IncomeStep - Coleta renda familiar
 */

import { useState } from 'react';
import { CitizenProfile, FAIXAS_RENDA } from '../types';

interface Props {
  profile: CitizenProfile;
  onUpdate: (updates: Partial<CitizenProfile>) => void;
  onNext: () => void;
  onBack: () => void;
}

export default function IncomeStep({ profile, onUpdate, onNext, onBack }: Props) {
  const [inputMode, setInputMode] = useState<'faixa' | 'valor'>('faixa');
  const [valorManual, setValorManual] = useState(
    profile.rendaFamiliarMensal > 0 ? String(profile.rendaFamiliarMensal) : ''
  );

  const rendaPerCapita = profile.pessoasNaCasa > 0
    ? profile.rendaFamiliarMensal / profile.pessoasNaCasa
    : 0;

  const handleFaixaSelect = (valor: number) => {
    onUpdate({ rendaFamiliarMensal: valor });
  };

  const handleValorChange = (e: React.ChangeEvent<HTMLInputElement>) => {
    const value = e.target.value.replace(/\D/g, '');
    setValorManual(value);
    onUpdate({ rendaFamiliarMensal: parseInt(value) || 0 });
  };

  const formatCurrency = (value: number) => {
    return new Intl.NumberFormat('pt-BR', {
      style: 'currency',
      currency: 'BRL',
    }).format(value);
  };

  return (
    <div className="space-y-6">
      {/* Header */}
      <div className="text-center">
        <div className="text-4xl mb-3">💰</div>
        <h2 className="text-xl font-bold text-[var(--text-primary)]">Renda da família</h2>
        <p className="text-[var(--text-tertiary)] mt-2">
          Quanto a família ganha por mês? (somando tudo)
        </p>
      </div>

      {/* Toggle modo */}
      <div className="flex bg-[var(--badge-bg)] rounded-xl p-1">
        <button
          onClick={() => setInputMode('faixa')}
          className={`flex-1 py-2 rounded-lg text-sm font-medium transition-all ${
            inputMode === 'faixa'
              ? 'bg-emerald-600 text-white'
              : 'text-[var(--text-tertiary)] hover:text-[var(--text-secondary)]'
          }`}
        >
          Escolher faixa
        </button>
        <button
          onClick={() => setInputMode('valor')}
          className={`flex-1 py-2 rounded-lg text-sm font-medium transition-all ${
            inputMode === 'valor'
              ? 'bg-emerald-600 text-white'
              : 'text-[var(--text-tertiary)] hover:text-[var(--text-secondary)]'
          }`}
        >
          Digitar valor
        </button>
      </div>

      {/* Seleção por faixa */}
      {inputMode === 'faixa' && (
        <div className="space-y-2">
          {FAIXAS_RENDA.map((faixa) => (
            <button
              key={faixa.value}
              onClick={() => handleFaixaSelect(faixa.value)}
              className={`w-full py-4 px-4 rounded-xl text-left transition-all ${
                profile.rendaFamiliarMensal === faixa.value
                  ? 'bg-emerald-600/15 border-2 border-emerald-500 text-emerald-600'
                  : 'bg-[var(--input-bg)] border-2 border-transparent text-[var(--text-secondary)] hover:bg-[var(--hover-bg)]'
              }`}
            >
              <span className="font-medium">{faixa.label}</span>
            </button>
          ))}
        </div>
      )}

      {/* Input manual */}
      {inputMode === 'valor' && (
        <div className="space-y-3">
          <div className="relative">
            <span className="absolute left-4 top-1/2 -translate-y-1/2 text-[var(--text-tertiary)] text-lg">
              R$
            </span>
            <input
              type="text"
              value={valorManual}
              onChange={handleValorChange}
              placeholder="0"
              className="w-full pl-12 pr-4 py-4 rounded-xl bg-[var(--input-bg)] border border-[var(--input-border)] text-[var(--text-primary)] text-2xl text-center font-bold focus:outline-none focus:ring-2 focus:ring-emerald-500 focus:border-transparent"
            />
          </div>
          <p className="text-center text-sm text-[var(--text-tertiary)]">
            Digite o valor total que a família recebe por mês
          </p>
        </div>
      )}

      {/* Resumo */}
      {profile.rendaFamiliarMensal > 0 && (
        <div className="p-4 rounded-xl bg-[var(--badge-bg)] border border-[var(--border-color)] space-y-2">
          <div className="flex justify-between items-center">
            <span className="text-[var(--text-tertiary)]">Renda familiar:</span>
            <span className="text-lg font-bold text-[var(--text-secondary)]">
              {formatCurrency(profile.rendaFamiliarMensal)}
            </span>
          </div>
          <div className="flex justify-between items-center">
            <span className="text-[var(--text-tertiary)]">Renda por pessoa:</span>
            <span className={`text-lg font-bold ${
              rendaPerCapita <= 218 ? 'text-emerald-600' :
              rendaPerCapita <= 706 ? 'text-amber-500' : 'text-[var(--text-secondary)]'
            }`}>
              {formatCurrency(rendaPerCapita)}
            </span>
          </div>
          {rendaPerCapita <= 218 && (
            <p className="text-xs text-emerald-600 mt-2">
              Renda dentro do limite para Bolsa Família
            </p>
          )}
        </div>
      )}

      {/* Botões */}
      <div className="flex gap-3">
        <button
          onClick={onBack}
          className="flex-1 py-4 rounded-xl font-semibold bg-[var(--badge-bg)] text-[var(--text-secondary)] hover:bg-[var(--hover-bg)] transition-all"
        >
          ← Voltar
        </button>
        <button
          onClick={onNext}
          disabled={profile.rendaFamiliarMensal === 0}
          className={`flex-1 py-4 rounded-xl font-semibold transition-all ${
            profile.rendaFamiliarMensal > 0
              ? 'bg-emerald-600 hover:bg-emerald-500 text-white'
              : 'bg-[var(--border-color)] text-[var(--text-tertiary)] cursor-not-allowed'
          }`}
        >
          Continuar →
        </button>
      </div>
    </div>
  );
}
