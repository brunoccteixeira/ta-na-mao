/**
 * MiniProfileForm — lightweight inline form that asks only the fields
 * needed to evaluate a specific benefit's eligibility rules.
 */

import { useState } from 'react';
import { Search } from 'lucide-react';
import type { CitizenProfile, EligibilityRule } from '../../engine/types';
import { DEFAULT_CITIZEN_PROFILE } from '../../engine/types';
import { getRequiredFields } from '../../utils/criteriaGrouping';

interface MiniProfileFormProps {
  rules: EligibilityRule[];
  onSubmit: (profile: CitizenProfile) => void;
  initialProfile?: Partial<CitizenProfile>;
}

// Metadata for renderable profile fields
interface FieldConfig {
  key: string;
  label: string;
  type: 'number' | 'boolean' | 'text';
  placeholder?: string;
  hint?: string;
}

const FIELD_CONFIGS: Record<string, FieldConfig> = {
  rendaFamiliarMensal: {
    key: 'rendaFamiliarMensal',
    label: 'Renda da família por mês',
    type: 'number',
    placeholder: 'Ex: 800',
    hint: 'Some tudo que entra na casa (salário, bicos, ajuda)',
  },
  pessoasNaCasa: {
    key: 'pessoasNaCasa',
    label: 'Quantas pessoas moram na casa',
    type: 'number',
    placeholder: 'Ex: 4',
  },
  cadastradoCadunico: {
    key: 'cadastradoCadunico',
    label: 'Tem Cadastro Único (CadÚnico)?',
    type: 'boolean',
  },
  temIdoso65Mais: {
    key: 'temIdoso65Mais',
    label: 'Tem alguém com 65 anos ou mais em casa?',
    type: 'boolean',
  },
  temCrianca0a6: {
    key: 'temCrianca0a6',
    label: 'Tem criança de 0 a 6 anos?',
    type: 'boolean',
  },
  quantidadeFilhos: {
    key: 'quantidadeFilhos',
    label: 'Quantos filhos?',
    type: 'number',
    placeholder: 'Ex: 2',
  },
  temGestante: {
    key: 'temGestante',
    label: 'Tem gestante na família?',
    type: 'boolean',
  },
  temPcd: {
    key: 'temPcd',
    label: 'Alguém tem deficiência?',
    type: 'boolean',
  },
  trabalhoFormal: {
    key: 'trabalhoFormal',
    label: 'Trabalha com carteira assinada?',
    type: 'boolean',
  },
  recebeBolsaFamilia: {
    key: 'recebeBolsaFamilia',
    label: 'Já recebe Bolsa Família?',
    type: 'boolean',
  },
  recebeBpc: {
    key: 'recebeBpc',
    label: 'Já recebe BPC?',
    type: 'boolean',
  },
  temMei: {
    key: 'temMei',
    label: 'Tem MEI?',
    type: 'boolean',
  },
  trabalhaAplicativo: {
    key: 'trabalhaAplicativo',
    label: 'Trabalha com aplicativo (Uber, iFood...)?',
    type: 'boolean',
  },
  agricultorFamiliar: {
    key: 'agricultorFamiliar',
    label: 'É agricultor familiar?',
    type: 'boolean',
  },
  pescadorArtesanal: {
    key: 'pescadorArtesanal',
    label: 'É pescador artesanal?',
    type: 'boolean',
  },
  temCasaPropria: {
    key: 'temCasaPropria',
    label: 'Tem casa própria?',
    type: 'boolean',
  },
  moradiaZonaRural: {
    key: 'moradiaZonaRural',
    label: 'Mora na zona rural?',
    type: 'boolean',
  },
  estudante: {
    key: 'estudante',
    label: 'É estudante?',
    type: 'boolean',
  },
  redePublica: {
    key: 'redePublica',
    label: 'Estuda em escola pública?',
    type: 'boolean',
  },
  idade: {
    key: 'idade',
    label: 'Idade',
    type: 'number',
    placeholder: 'Ex: 35',
  },
  temCarteiraAssinada: {
    key: 'temCarteiraAssinada',
    label: 'Tem carteira assinada?',
    type: 'boolean',
  },
  tempoCarteiraAssinada: {
    key: 'tempoCarteiraAssinada',
    label: 'Meses com carteira assinada',
    type: 'number',
    placeholder: 'Ex: 12',
  },
  catadorReciclavel: {
    key: 'catadorReciclavel',
    label: 'É catador de recicláveis?',
    type: 'boolean',
  },
};

export default function MiniProfileForm({ rules, onSubmit, initialProfile }: MiniProfileFormProps) {
  const requiredFields = getRequiredFields(rules);

  // Build initial state from saved profile or empty for fresh form
  const buildInitial = (): Record<string, unknown> => {
    const base: Record<string, unknown> = { ...DEFAULT_CITIZEN_PROFILE, ...initialProfile };
    const partial: Record<string, unknown> = {};
    for (const field of requiredFields) {
      const config = FIELD_CONFIGS[field];
      const saved = base[field as keyof CitizenProfile];

      if (initialProfile) {
        // Re-editing: use the saved value
        partial[field] = saved ?? '';
      } else if (config?.type === 'number') {
        // Fresh form: leave number fields empty so user must fill them
        partial[field] = '';
      } else {
        // Booleans default from DEFAULT_CITIZEN_PROFILE
        partial[field] = saved ?? '';
      }
    }
    return partial;
  };

  const [values, setValues] = useState<Record<string, unknown>>(buildInitial);

  const handleChange = (key: string, value: unknown) => {
    setValues(prev => ({ ...prev, [key]: value }));
  };

  const handleSubmit = (e: React.FormEvent) => {
    e.preventDefault();
    // Coerce empty strings to 0 for numeric fields before sending to engine
    const coerced: Record<string, unknown> = {};
    for (const [key, val] of Object.entries(values)) {
      coerced[key] = val === '' && FIELD_CONFIGS[key]?.type === 'number' ? 0 : val;
    }
    const profile: CitizenProfile = {
      ...DEFAULT_CITIZEN_PROFILE,
      ...initialProfile,
      ...coerced,
    } as CitizenProfile;
    onSubmit(profile);
  };

  // Only render fields we have configs for
  const fieldsToRender = requiredFields
    .filter(f => FIELD_CONFIGS[f])
    .map(f => FIELD_CONFIGS[f]);

  if (fieldsToRender.length === 0) return null;

  return (
    <form onSubmit={handleSubmit} className="space-y-4">
      <div className="p-5 bg-[var(--bg-card)] rounded-2xl border border-[var(--border-color)]">
        <h3 className="text-base font-semibold text-[var(--text-primary)] mb-1">
          Precisamos de algumas informações
        </h3>
        <p className="text-sm text-[var(--text-secondary)] mb-5">
          Responda só o que souber. Seus dados ficam só no seu celular.
        </p>

        <div className="space-y-4">
          {fieldsToRender.map(config => (
            <div key={config.key}>
              <label className="block text-sm font-medium text-[var(--text-primary)] mb-1.5">
                {config.label}
              </label>

              {config.type === 'boolean' ? (
                <div className="flex gap-2">
                  {[
                    { label: 'Sim', value: true },
                    { label: 'Não', value: false },
                  ].map(opt => (
                    <button
                      key={String(opt.value)}
                      type="button"
                      onClick={() => handleChange(config.key, opt.value)}
                      className={`flex-1 py-3 rounded-xl text-sm font-medium border transition-colors min-h-[48px] ${
                        values[config.key] === opt.value
                          ? 'bg-emerald-50 border-emerald-300 text-emerald-700'
                          : 'bg-[var(--bg-primary)] border-[var(--border-color)] text-[var(--text-secondary)]'
                      }`}
                    >
                      {opt.label}
                    </button>
                  ))}
                </div>
              ) : (
                <input
                  type="number"
                  inputMode="numeric"
                  placeholder={config.placeholder}
                  value={values[config.key] as string | number}
                  onChange={e => handleChange(config.key, e.target.value === '' ? '' : Number(e.target.value))}
                  className="w-full px-4 py-3 rounded-xl border border-[var(--border-color)] bg-[var(--bg-primary)] text-[var(--text-primary)] placeholder-[var(--text-tertiary)] text-sm min-h-[48px] focus:outline-none focus:ring-2 focus:ring-emerald-400 focus:border-transparent"
                />
              )}

              {config.hint && (
                <p className="text-xs text-[var(--text-tertiary)] mt-1">{config.hint}</p>
              )}
            </div>
          ))}
        </div>
      </div>

      <button
        type="submit"
        className="w-full flex items-center justify-center gap-2 py-4 bg-emerald-500 hover:bg-emerald-600 text-white font-semibold rounded-full text-base transition-colors min-h-[48px]"
      >
        <Search className="w-5 h-5" />
        Verificar Agora
      </button>
    </form>
  );
}
