/**
 * FamilyStep - Coleta composição familiar
 */

import { CitizenProfile } from '../types';

interface Props {
  profile: CitizenProfile;
  onUpdate: (updates: Partial<CitizenProfile>) => void;
  onNext: () => void;
  onBack: () => void;
}

export default function FamilyStep({ profile, onUpdate, onNext, onBack }: Props) {
  const handlePessoasChange = (quantidade: number) => {
    onUpdate({
      pessoasNaCasa: quantidade,
      // Reset filhos se só tem 1 pessoa
      temFilhosMenores: quantidade === 1 ? false : profile.temFilhosMenores,
      quantidadeFilhos: quantidade === 1 ? 0 : profile.quantidadeFilhos,
    });
  };

  return (
    <div className="space-y-6">
      {/* Header */}
      <div className="text-center">
        <div className="text-4xl mb-3">👨‍👩‍👧‍👦</div>
        <h2 className="text-xl font-bold text-slate-100">Sua família</h2>
        <p className="text-slate-400 mt-2">Quantas pessoas moram com você?</p>
      </div>

      {/* Quantidade de pessoas */}
      <div className="space-y-3">
        <label className="block text-sm font-medium text-slate-300">
          Pessoas na casa (incluindo você)
        </label>
        <div className="flex gap-2 flex-wrap justify-center">
          {[1, 2, 3, 4, 5, 6, 7, 8].map((num) => (
            <button
              key={num}
              onClick={() => handlePessoasChange(num)}
              className={`w-14 h-14 rounded-xl font-bold text-lg transition-all ${
                profile.pessoasNaCasa === num
                  ? 'bg-emerald-600 text-white'
                  : 'bg-slate-800 text-slate-300 hover:bg-slate-700'
              }`}
            >
              {num === 8 ? '8+' : num}
            </button>
          ))}
        </div>
      </div>

      {/* Filhos menores */}
      {profile.pessoasNaCasa > 1 && (
        <div className="space-y-3">
          <label className="block text-sm font-medium text-slate-300">
            Tem filhos menores de 18 anos?
          </label>
          <div className="flex gap-3">
            <button
              onClick={() => onUpdate({ temFilhosMenores: true })}
              className={`flex-1 py-3 rounded-xl font-medium transition-all ${
                profile.temFilhosMenores
                  ? 'bg-emerald-600 text-white'
                  : 'bg-slate-800 text-slate-300 hover:bg-slate-700'
              }`}
            >
              Sim
            </button>
            <button
              onClick={() => onUpdate({ temFilhosMenores: false, quantidadeFilhos: 0 })}
              className={`flex-1 py-3 rounded-xl font-medium transition-all ${
                !profile.temFilhosMenores
                  ? 'bg-emerald-600 text-white'
                  : 'bg-slate-800 text-slate-300 hover:bg-slate-700'
              }`}
            >
              Não
            </button>
          </div>
        </div>
      )}

      {/* Quantidade de filhos */}
      {profile.temFilhosMenores && (
        <div className="space-y-3">
          <label className="block text-sm font-medium text-slate-300">
            Quantos filhos menores de 18?
          </label>
          <div className="flex gap-2 justify-center">
            {[1, 2, 3, 4, 5].map((num) => (
              <button
                key={num}
                onClick={() => onUpdate({ quantidadeFilhos: num })}
                className={`w-12 h-12 rounded-xl font-bold transition-all ${
                  profile.quantidadeFilhos === num
                    ? 'bg-blue-600 text-white'
                    : 'bg-slate-800 text-slate-300 hover:bg-slate-700'
                }`}
              >
                {num === 5 ? '5+' : num}
              </button>
            ))}
          </div>
        </div>
      )}

      {/* Summary */}
      <div className="p-4 rounded-xl bg-slate-800/50 border border-slate-700">
        <p className="text-sm text-slate-400">
          {profile.pessoasNaCasa === 1
            ? 'Você mora sozinho(a)'
            : `${profile.pessoasNaCasa} pessoas na casa`}
          {profile.temFilhosMenores && profile.quantidadeFilhos > 0 &&
            `, ${profile.quantidadeFilhos} filho(s) menor(es)`}
        </p>
      </div>

      {/* Botões */}
      <div className="flex gap-3">
        <button
          onClick={onBack}
          className="flex-1 py-4 rounded-xl font-semibold bg-slate-800 text-slate-300 hover:bg-slate-700 transition-all"
        >
          ← Voltar
        </button>
        <button
          onClick={onNext}
          className="flex-1 py-4 rounded-xl font-semibold bg-emerald-600 hover:bg-emerald-500 text-white transition-all"
        >
          Continuar →
        </button>
      </div>
    </div>
  );
}
