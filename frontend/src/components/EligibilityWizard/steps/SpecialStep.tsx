/**
 * SpecialStep - Coleta situações especiais (idoso, PCD, gestante)
 */

import { CitizenProfile } from '../types';

interface Props {
  profile: CitizenProfile;
  onUpdate: (updates: Partial<CitizenProfile>) => void;
  onNext: () => void;
  onBack: () => void;
  isLoading?: boolean;
}

interface ToggleOption {
  key: keyof CitizenProfile;
  icon: string;
  label: string;
  description: string;
}

const OPTIONS: ToggleOption[] = [
  {
    key: 'temIdoso65Mais',
    icon: '🧓',
    label: 'Idoso (65+ anos)',
    description: 'Alguém na casa tem 65 anos ou mais',
  },
  {
    key: 'temPcd',
    icon: '♿',
    label: 'Pessoa com deficiência',
    description: 'Alguém na casa tem alguma deficiência',
  },
  {
    key: 'temGestante',
    icon: '🤰',
    label: 'Gestante',
    description: 'Alguém na casa está grávida',
  },
  {
    key: 'cadastradoCadunico',
    icon: '📋',
    label: 'Já tem CadÚnico',
    description: 'Família já está cadastrada no CadÚnico',
  },
  {
    key: 'temCasaPropria',
    icon: '🏠',
    label: 'Casa própria',
    description: 'A família tem casa própria',
  },
];

export default function SpecialStep({ profile, onUpdate, onNext, onBack, isLoading }: Props) {
  const handleToggle = (key: keyof CitizenProfile) => {
    onUpdate({ [key]: !profile[key] });
  };

  return (
    <div className="space-y-6">
      {/* Header */}
      <div className="text-center">
        <div className="text-4xl mb-3">✨</div>
        <h2 className="text-xl font-bold text-slate-100">Situações especiais</h2>
        <p className="text-slate-400 mt-2">
          Marque o que se aplica à sua família
        </p>
      </div>

      {/* Options */}
      <div className="space-y-3">
        {OPTIONS.map((option) => (
          <button
            key={option.key}
            onClick={() => handleToggle(option.key)}
            className={`w-full p-4 rounded-xl text-left transition-all flex items-center gap-4 ${
              profile[option.key]
                ? 'bg-emerald-600/20 border-2 border-emerald-500'
                : 'bg-slate-800 border-2 border-transparent hover:bg-slate-700'
            }`}
          >
            <div className="text-3xl">{option.icon}</div>
            <div className="flex-1">
              <p className={`font-medium ${
                profile[option.key] ? 'text-emerald-300' : 'text-slate-200'
              }`}>
                {option.label}
              </p>
              <p className="text-sm text-slate-400">{option.description}</p>
            </div>
            <div className={`w-6 h-6 rounded-full border-2 flex items-center justify-center ${
              profile[option.key]
                ? 'bg-emerald-500 border-emerald-500'
                : 'border-slate-600'
            }`}>
              {profile[option.key] && (
                <svg className="w-4 h-4 text-white" fill="currentColor" viewBox="0 0 20 20">
                  <path fillRule="evenodd" d="M16.707 5.293a1 1 0 010 1.414l-8 8a1 1 0 01-1.414 0l-4-4a1 1 0 011.414-1.414L8 12.586l7.293-7.293a1 1 0 011.414 0z" clipRule="evenodd" />
                </svg>
              )}
            </div>
          </button>
        ))}
      </div>

      {/* Info */}
      <div className="p-4 rounded-xl bg-blue-500/10 border border-blue-500/30">
        <p className="text-sm text-blue-300">
          <span className="font-medium">Dica:</span> Essas informações ajudam a encontrar benefícios
          específicos para sua situação. Se nenhuma opção se aplica, pode continuar.
        </p>
      </div>

      {/* Botões */}
      <div className="flex gap-3">
        <button
          onClick={onBack}
          disabled={isLoading}
          className="flex-1 py-4 rounded-xl font-semibold bg-slate-800 text-slate-300 hover:bg-slate-700 transition-all disabled:opacity-50"
        >
          ← Voltar
        </button>
        <button
          onClick={onNext}
          disabled={isLoading}
          className="flex-1 py-4 rounded-xl font-semibold bg-emerald-600 hover:bg-emerald-500 text-white transition-all disabled:opacity-50 flex items-center justify-center gap-2"
        >
          {isLoading ? (
            <>
              <svg className="animate-spin h-5 w-5" viewBox="0 0 24 24">
                <circle className="opacity-25" cx="12" cy="12" r="10" stroke="currentColor" strokeWidth="4" fill="none" />
                <path className="opacity-75" fill="currentColor" d="M4 12a8 8 0 018-8V0C5.373 0 0 5.373 0 12h4zm2 5.291A7.962 7.962 0 014 12H0c0 3.042 1.135 5.824 3 7.938l3-2.647z" />
              </svg>
              Analisando...
            </>
          ) : (
            'Ver meus direitos →'
          )}
        </button>
      </div>
    </div>
  );
}
