/**
 * BasicInfoStep - Coleta CPF (opcional) e cidade
 */

import { useState } from 'react';
import { CitizenProfile, UFS } from '../types';

interface Props {
  profile: CitizenProfile;
  onUpdate: (updates: Partial<CitizenProfile>) => void;
  onNext: () => void;
}

export default function BasicInfoStep({ profile, onUpdate, onNext }: Props) {
  const [cpfInput, setCpfInput] = useState(profile.cpf || '');
  const [semCpf, setSemCpf] = useState(false);

  const formatCpf = (value: string) => {
    const numbers = value.replace(/\D/g, '').slice(0, 11);
    if (numbers.length <= 3) return numbers;
    if (numbers.length <= 6) return `${numbers.slice(0, 3)}.${numbers.slice(3)}`;
    if (numbers.length <= 9) return `${numbers.slice(0, 3)}.${numbers.slice(3, 6)}.${numbers.slice(6)}`;
    return `${numbers.slice(0, 3)}.${numbers.slice(3, 6)}.${numbers.slice(6, 9)}-${numbers.slice(9)}`;
  };

  const handleCpfChange = (e: React.ChangeEvent<HTMLInputElement>) => {
    const formatted = formatCpf(e.target.value);
    setCpfInput(formatted);
    const numbers = formatted.replace(/\D/g, '');
    if (numbers.length === 11) {
      onUpdate({ cpf: numbers });
    }
  };

  const handleSemCpf = () => {
    setSemCpf(true);
    setCpfInput('');
    onUpdate({ cpf: undefined });
  };

  const canProceed = (profile.municipio && profile.uf) || semCpf;

  return (
    <div className="space-y-6">
      {/* Header */}
      <div className="text-center">
        <div className="text-4xl mb-3">🔍</div>
        <h2 className="text-xl font-bold text-[var(--text-primary)]">Vamos descobrir seus direitos!</h2>
        <p className="text-[var(--text-tertiary)] mt-2">Me conta um pouco sobre você</p>
      </div>

      {/* CPF Input */}
      <div className="space-y-3">
        <label className="block text-sm font-medium text-[var(--text-secondary)]">
          CPF (opcional - ajuda a encontrar benefícios)
        </label>

        {!semCpf ? (
          <div className="space-y-2">
            <input
              type="text"
              value={cpfInput}
              onChange={handleCpfChange}
              placeholder="000.000.000-00"
              className="w-full px-4 py-3 rounded-xl bg-[var(--input-bg)] border border-[var(--input-border)] text-[var(--text-primary)] placeholder-[var(--text-tertiary)] focus:outline-none focus:ring-2 focus:ring-emerald-500 focus:border-transparent text-center text-lg tracking-wider"
              maxLength={14}
            />
            <button
              onClick={handleSemCpf}
              className="w-full text-sm text-[var(--text-tertiary)] hover:text-[var(--text-secondary)] py-2"
            >
              Não tenho CPF ou prefiro não informar
            </button>
          </div>
        ) : (
          <div className="p-3 rounded-xl bg-[var(--badge-bg)] border border-[var(--border-color)] text-center">
            <span className="text-[var(--text-tertiary)]">Continuando sem CPF</span>
            <button
              onClick={() => setSemCpf(false)}
              className="ml-2 text-emerald-600 hover:text-emerald-500"
            >
              Informar CPF
            </button>
          </div>
        )}
      </div>

      {/* Cidade e UF */}
      <div className="grid grid-cols-3 gap-3">
        <div className="col-span-2">
          <label className="block text-sm font-medium text-[var(--text-secondary)] mb-2">
            Cidade
          </label>
          <input
            type="text"
            value={profile.municipio || ''}
            onChange={(e) => onUpdate({ municipio: e.target.value })}
            placeholder="Sua cidade"
            className="w-full px-4 py-3 rounded-xl bg-[var(--input-bg)] border border-[var(--input-border)] text-[var(--text-primary)] placeholder-[var(--text-tertiary)] focus:outline-none focus:ring-2 focus:ring-emerald-500 focus:border-transparent"
          />
        </div>
        <div>
          <label className="block text-sm font-medium text-[var(--text-secondary)] mb-2">
            Estado
          </label>
          <select
            value={profile.uf || ''}
            onChange={(e) => onUpdate({ uf: e.target.value })}
            className="w-full px-4 py-3 rounded-xl bg-[var(--input-bg)] border border-[var(--input-border)] text-[var(--text-primary)] focus:outline-none focus:ring-2 focus:ring-emerald-500 focus:border-transparent"
          >
            <option value="">UF</option>
            {UFS.map((uf) => (
              <option key={uf} value={uf}>{uf}</option>
            ))}
          </select>
        </div>
      </div>

      {/* Botão Continuar */}
      <button
        onClick={onNext}
        disabled={!canProceed}
        className={`w-full py-4 rounded-xl font-semibold text-lg transition-all ${
          canProceed
            ? 'bg-emerald-600 hover:bg-emerald-500 text-white'
            : 'bg-[var(--border-color)] text-[var(--text-tertiary)] cursor-not-allowed'
        }`}
      >
        Continuar →
      </button>
    </div>
  );
}
