/**
 * WorkStep - Coleta informações sobre trabalho e profissão
 * Importante para identificar benefícios setoriais
 */

import { CitizenProfile, PROFISSOES } from '../types';

interface Props {
  profile: CitizenProfile;
  onUpdate: (updates: Partial<CitizenProfile>) => void;
  onNext: () => void;
  onBack: () => void;
}

export default function WorkStep({ profile, onUpdate, onNext, onBack }: Props) {

  const handleProfissaoChange = (profissao: string) => {
    // Atualiza profissão e campos relacionados
    const updates: Partial<CitizenProfile> = {
      profissao,
      temMei: profissao === 'mei',
      trabalhaAplicativo: profissao === 'entregador' || profissao === 'motorista_app',
      agricultorFamiliar: profissao === 'agricultor',
      pescadorArtesanal: profissao === 'pescador',
      catadorReciclavel: profissao === 'catador',
      trabalhoFormal: profissao === 'empregado_formal',
      estudante: profissao === 'estudante',
    };
    onUpdate(updates);
  };

  const isSetorial = ['pescador', 'agricultor', 'entregador', 'motorista_app', 'catador'].includes(profile.profissao || '');

  return (
    <div className="space-y-6">
      {/* Header */}
      <div className="text-center">
        <div className="text-4xl mb-3">💼</div>
        <h2 className="text-xl font-bold text-[var(--text-primary)]">Sobre seu trabalho</h2>
        <p className="text-[var(--text-tertiary)] mt-2">
          Alguns benefícios são específicos para certas profissões
        </p>
      </div>

      {/* Profissão */}
      <div className="space-y-3">
        <label className="block text-sm font-medium text-[var(--text-secondary)]">
          Qual é a sua principal ocupação?
        </label>
        <select
          value={profile.profissao || ''}
          onChange={(e) => handleProfissaoChange(e.target.value)}
          className="w-full px-4 py-3 rounded-xl bg-[var(--input-bg)] border border-[var(--input-border)] text-[var(--text-primary)] focus:outline-none focus:ring-2 focus:ring-emerald-500 focus:border-transparent"
        >
          {PROFISSOES.map((prof) => (
            <option key={prof.value} value={prof.value}>
              {prof.label}
            </option>
          ))}
        </select>
      </div>

      {/* Info sobre benefícios setoriais */}
      {isSetorial && (
        <div className="p-4 rounded-xl bg-emerald-500/10 border border-emerald-500/30">
          <div className="flex items-start gap-3">
            <span className="text-2xl">✨</span>
            <div>
              <p className="text-emerald-600 font-medium">
                Boa notícia!
              </p>
              <p className="text-emerald-600/70 text-sm mt-1">
                {profile.profissao === 'pescador' &&
                  'Pescadores artesanais podem ter direito ao Seguro-Defeso e crédito especial.'}
                {profile.profissao === 'agricultor' &&
                  'Agricultores familiares podem acessar PRONAF, Garantia-Safra e outros programas.'}
                {(profile.profissao === 'entregador' || profile.profissao === 'motorista_app') &&
                  'Vamos verificar programas disponíveis para trabalhadores de aplicativo na sua região.'}
                {profile.profissao === 'catador' &&
                  'Catadores organizados em cooperativas podem ter direito à Bolsa Reciclagem.'}
              </p>
            </div>
          </div>
        </div>
      )}

      {/* Perguntas adicionais para trabalhadores */}
      {profile.profissao && profile.profissao !== 'desempregado' && profile.profissao !== 'do_lar' && (
        <div className="space-y-4">
          {/* Zona rural */}
          <div className="p-4 rounded-xl bg-[var(--badge-bg)] border border-[var(--border-color)]">
            <label className="flex items-center gap-3 cursor-pointer">
              <input
                type="checkbox"
                checked={profile.moradiaZonaRural}
                onChange={(e) => onUpdate({ moradiaZonaRural: e.target.checked })}
                className="w-5 h-5 rounded border-[var(--input-border)] text-emerald-500 focus:ring-emerald-500"
              />
              <div>
                <span className="text-[var(--text-secondary)]">Moro ou trabalho na zona rural</span>
                <p className="text-sm text-[var(--text-tertiary)] mt-0.5">
                  Agricultores e trabalhadores rurais têm benefícios específicos
                </p>
              </div>
            </label>
          </div>

          {/* Carteira assinada recente */}
          {profile.profissao === 'desempregado' && (
            <div className="p-4 rounded-xl bg-[var(--badge-bg)] border border-[var(--border-color)]">
              <label className="flex items-center gap-3 cursor-pointer">
                <input
                  type="checkbox"
                  checked={profile.temCarteiraAssinada}
                  onChange={(e) => onUpdate({ temCarteiraAssinada: e.target.checked })}
                  className="w-5 h-5 rounded border-[var(--input-border)] text-emerald-500 focus:ring-emerald-500"
                />
                <div>
                  <span className="text-[var(--text-secondary)]">Trabalhei com carteira nos últimos 2 anos</span>
                  <p className="text-sm text-[var(--text-tertiary)] mt-0.5">
                    Pode dar direito a Seguro-Desemprego e FGTS
                  </p>
                </div>
              </label>
            </div>
          )}
        </div>
      )}

      {/* Desempregado - perguntas específicas */}
      {profile.profissao === 'desempregado' && (
        <div className="space-y-4">
          <div className="p-4 rounded-xl bg-amber-500/10 border border-amber-500/30">
            <div className="flex items-start gap-3">
              <span className="text-xl">💡</span>
              <div className="text-sm">
                <p className="text-amber-600 font-medium">Você sabia?</p>
                <p className="text-amber-600/70 mt-1">
                  Se você foi demitido sem justa causa e trabalhou pelo menos 12 meses,
                  pode ter direito ao Seguro-Desemprego.
                </p>
              </div>
            </div>
          </div>

          <div className="p-4 rounded-xl bg-[var(--badge-bg)] border border-[var(--border-color)]">
            <label className="flex items-center gap-3 cursor-pointer">
              <input
                type="checkbox"
                checked={profile.temCarteiraAssinada}
                onChange={(e) => onUpdate({ temCarteiraAssinada: e.target.checked })}
                className="w-5 h-5 rounded border-[var(--input-border)] text-emerald-500 focus:ring-emerald-500"
              />
              <div>
                <span className="text-[var(--text-secondary)]">Trabalhei com carteira assinada recentemente</span>
                <p className="text-sm text-[var(--text-tertiary)] mt-0.5">
                  Nos últimos 18 meses
                </p>
              </div>
            </label>
          </div>
        </div>
      )}

      {/* Estudante - perguntas específicas */}
      {profile.profissao === 'estudante' && (
        <div className="p-4 rounded-xl bg-[var(--badge-bg)] border border-[var(--border-color)]">
          <label className="flex items-center gap-3 cursor-pointer">
            <input
              type="checkbox"
              checked={profile.redePublica}
              onChange={(e) => onUpdate({ redePublica: e.target.checked })}
              className="w-5 h-5 rounded border-[var(--input-border)] text-emerald-500 focus:ring-emerald-500"
            />
            <div>
              <span className="text-[var(--text-secondary)]">Estudo em escola/faculdade pública</span>
              <p className="text-sm text-[var(--text-tertiary)] mt-0.5">
                Estudantes de escolas públicas têm acesso a mais benefícios
              </p>
            </div>
          </label>
        </div>
      )}

      {/* Trabalho histórico (PIS/PASEP) */}
      <div className="p-4 rounded-xl bg-[var(--badge-bg)] border border-[var(--border-color)]">
        <label className="flex items-center gap-3 cursor-pointer">
          <input
            type="checkbox"
            checked={profile.trabalhou1971_1988 || false}
            onChange={(e) => onUpdate({ trabalhou1971_1988: e.target.checked })}
            className="w-5 h-5 rounded border-[var(--input-border)] text-emerald-500 focus:ring-emerald-500"
          />
          <div>
            <span className="text-[var(--text-secondary)]">Trabalhei com carteira entre 1971 e 1988</span>
            <p className="text-sm text-[var(--text-tertiary)] mt-0.5">
              Pode ter PIS/PASEP esquecido para sacar
            </p>
          </div>
        </label>
      </div>

      {/* Botões de navegação */}
      <div className="flex gap-3">
        <button
          onClick={onBack}
          className="flex-1 py-3 px-4 rounded-xl font-medium text-[var(--text-secondary)] bg-[var(--badge-bg)] hover:bg-[var(--hover-bg)] transition-colors"
        >
          ← Voltar
        </button>
        <button
          onClick={onNext}
          className="flex-1 py-3 px-4 rounded-xl font-semibold text-white bg-emerald-600 hover:bg-emerald-500 transition-colors"
        >
          Continuar →
        </button>
      </div>
    </div>
  );
}
