/**
 * BenefitDetail - Single benefit page
 * Uses API v2 with fallback to static JSON
 */

import { useParams, Link, useNavigate } from 'react-router-dom';
import { useBenefitDetail } from '../hooks/useBenefitsAPI';
import { formatBenefitValue, getStateName } from '../engine/catalog';

export default function BenefitDetail() {
  const { id } = useParams<{ id: string }>();
  const navigate = useNavigate();

  const { data: benefit, isLoading, isError, error } = useBenefitDetail(id);

  // Loading state
  if (isLoading) {
    return (
      <div className="min-h-screen bg-[var(--bg-primary)] flex items-center justify-center">
        <div className="flex items-center gap-3 text-[var(--text-tertiary)]">
          <div className="w-5 h-5 border-2 border-emerald-500 border-t-transparent rounded-full animate-spin" />
          <span>Carregando benefício...</span>
        </div>
      </div>
    );
  }

  // Error/Not found state
  if (isError || !benefit) {
    return (
      <div className="min-h-screen bg-[var(--bg-primary)] flex items-center justify-center">
        <div className="text-center">
          <p className="text-[var(--text-tertiary)] mb-4">
            {error instanceof Error ? error.message : 'Benefício não encontrado'}
          </p>
          <Link to="/beneficios" className="text-emerald-600 hover:text-emerald-500">
            ← Voltar ao catálogo
          </Link>
        </div>
      </div>
    );
  }

  const scopeLabel = () => {
    switch (benefit.scope) {
      case 'federal': return 'Benefício Federal';
      case 'state': return `Benefício Estadual - ${getStateName(benefit.state || '')}`;
      case 'sectoral': return 'Benefício Setorial';
      case 'municipal': return 'Benefício Municipal';
      default: return 'Benefício';
    }
  };

  return (
    <div className="min-h-screen bg-[var(--bg-primary)]">
      {/* Header */}
      <header className="fixed top-0 left-0 right-0 bg-[var(--bg-header)] backdrop-blur-sm border-b border-[var(--border-color)] z-50">
        <div className="max-w-5xl mx-auto px-4 py-4 flex justify-between items-center">
          <Link to="/" className="text-xl font-bold text-emerald-600">
            Tá na Mão
          </Link>
          <button
            onClick={() => navigate(-1)}
            className="text-[var(--text-tertiary)] hover:text-[var(--text-primary)] text-sm"
          >
            ← Voltar
          </button>
        </div>
      </header>

      {/* Content */}
      <main className="pt-24 pb-16 px-4">
        <div className="max-w-2xl mx-auto">
          {/* Header */}
          <div className="mb-8">
            <div className="flex items-center gap-3 mb-4">
              <span className="text-4xl">{benefit.icon || '📋'}</span>
              <div>
                <span className={`px-2 py-1 rounded text-xs ${
                  benefit.scope === 'federal' ? 'bg-blue-500/15 text-blue-600' :
                  benefit.scope === 'state' ? 'bg-purple-500/15 text-purple-600' :
                  'bg-amber-500/15 text-amber-600'
                }`}>
                  {scopeLabel()}
                </span>
              </div>
            </div>
            <h1 className="text-2xl font-bold text-[var(--text-primary)] mb-3">
              {benefit.name}
            </h1>
            <p className="text-lg text-[var(--text-secondary)]">
              {benefit.shortDescription}
            </p>
          </div>

          {/* Value */}
          {benefit.estimatedValue && (
            <div className="p-4 rounded-xl bg-emerald-500/10 border border-emerald-500/30 mb-6">
              <div className="flex items-center gap-2 text-emerald-600">
                <span className="text-xl">💰</span>
                <span className="font-semibold text-lg">
                  {formatBenefitValue(benefit)}
                </span>
              </div>
              {benefit.estimatedValue.description && (
                <p className="text-sm text-emerald-600/70 mt-1 ml-7">
                  {benefit.estimatedValue.description}
                </p>
              )}
            </div>
          )}

          {/* Quem pode receber */}
          <section className="mb-8">
            <h2 className="text-lg font-semibold text-[var(--text-primary)] mb-4 flex items-center gap-2">
              <span>✅</span> Quem pode receber
            </h2>
            <div className="space-y-3">
              {benefit.eligibilityRules.map((rule, idx) => (
                <div
                  key={idx}
                  className="p-3 rounded-lg bg-[var(--bg-card)] border border-[var(--border-color)]"
                >
                  <p className="text-[var(--text-secondary)]">{rule.description}</p>
                  {rule.legalReference && (
                    <p className="text-xs text-[var(--text-tertiary)] mt-1 flex items-center gap-1">
                      <svg className="w-3 h-3" fill="none" stroke="currentColor" viewBox="0 0 24 24"><path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M3 6l3 1m0 0l-3 9a5.002 5.002 0 006.001 0M6 7l3 9M6 7l6-2m6 2l3-1m-3 1l-3 9a5.002 5.002 0 006.001 0M18 7l3 9m-3-9l-6-2m0-2v2m0 16V5m0 16H9m3 0h3" /></svg>
                      {rule.legalReference}
                    </p>
                  )}
                </div>
              ))}
            </div>
          </section>

          {/* Onde pedir */}
          <section className="mb-8">
            <h2 className="text-lg font-semibold text-[var(--text-primary)] mb-4 flex items-center gap-2">
              <span>📍</span> Onde pedir
            </h2>
            <div className="p-4 rounded-xl bg-[var(--bg-card)] border border-[var(--border-color)]">
              <p className="text-[var(--text-secondary)]">{benefit.whereToApply}</p>
            </div>
          </section>

          {/* Documentos necessários */}
          <section className="mb-8">
            <h2 className="text-lg font-semibold text-[var(--text-primary)] mb-4 flex items-center gap-2">
              <span>📄</span> Documentos necessários
            </h2>
            <ul className="space-y-2">
              {benefit.documentsRequired.map((doc, idx) => (
                <li
                  key={idx}
                  className="flex items-center gap-3 p-3 rounded-lg bg-[var(--bg-card)] border border-[var(--border-color)]"
                >
                  <span className="text-emerald-600">•</span>
                  <span className="text-[var(--text-secondary)]">{doc}</span>
                </li>
              ))}
            </ul>
          </section>

          {/* Como pedir */}
          {benefit.howToApply && (
            <section className="mb-8">
              <h2 className="text-lg font-semibold text-[var(--text-primary)] mb-4 flex items-center gap-2">
                <span>📋</span> Como pedir
              </h2>
              <div className="space-y-3">
                {benefit.howToApply.map((step, idx) => (
                  <div
                    key={idx}
                    className="flex items-start gap-3 p-3 rounded-lg bg-[var(--bg-card)] border border-[var(--border-color)]"
                  >
                    <span className="w-6 h-6 rounded-full bg-emerald-600 text-white text-sm flex items-center justify-center flex-shrink-0">
                      {idx + 1}
                    </span>
                    <p className="text-[var(--text-secondary)]">{step}</p>
                  </div>
                ))}
              </div>
            </section>
          )}

          {/* Base Legal */}
          {benefit.legalBasis && benefit.legalBasis.laws.length > 0 && (
            <section className="mb-8">
              <h2 className="text-lg font-semibold text-[var(--text-primary)] mb-4 flex items-center gap-2">
                <svg className="w-5 h-5" fill="none" stroke="currentColor" viewBox="0 0 24 24"><path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M12 6.253v13m0-13C10.832 5.477 9.246 5 7.5 5S4.168 5.477 3 6.253v13C4.168 18.477 5.754 18 7.5 18s3.332.477 4.5 1.253m0-13C13.168 5.477 14.754 5 16.5 5c1.747 0 3.332.477 4.5 1.253v13C19.832 18.477 18.247 18 16.5 18c-1.746 0-3.332.477-4.5 1.253" /></svg>
                Base legal
              </h2>
              <div className="space-y-3">
                {benefit.legalBasis.laws.map((law, idx) => (
                  <div
                    key={idx}
                    className="p-4 rounded-xl bg-[var(--bg-card)] border border-[var(--border-color)]"
                  >
                    <div className="flex items-start gap-3">
                      <div className="flex-1">
                        <div className="flex items-center gap-2 mb-1">
                          <span className={`px-2 py-0.5 rounded text-xs font-medium ${
                            law.type === 'constituicao' ? 'bg-amber-500/15 text-amber-600' :
                            law.type === 'lei' ? 'bg-blue-500/15 text-blue-600' :
                            law.type === 'decreto' ? 'bg-purple-500/15 text-purple-600' :
                            law.type === 'portaria' ? 'bg-cyan-500/15 text-cyan-600' :
                            'bg-gray-500/15 text-gray-600'
                          }`}>
                            {law.type === 'constituicao' ? 'Constituição' :
                             law.type === 'lei' ? 'Lei' :
                             law.type === 'decreto' ? 'Decreto' :
                             law.type === 'portaria' ? 'Portaria' :
                             'Resolução'}
                          </span>
                          <span className="text-sm font-medium text-[var(--text-primary)]">
                            {law.number}
                          </span>
                        </div>
                        <p className="text-sm text-[var(--text-secondary)]">
                          {law.description}
                        </p>
                      </div>
                      {law.url && (
                        <a
                          href={law.url}
                          target="_blank"
                          rel="noopener noreferrer"
                          className="text-xs text-emerald-600 hover:text-emerald-500 whitespace-nowrap flex items-center gap-1 mt-1"
                        >
                          Ver texto
                          <svg className="w-3 h-3" fill="none" stroke="currentColor" viewBox="0 0 24 24"><path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M10 6H6a2 2 0 00-2 2v10a2 2 0 002 2h10a2 2 0 002-2v-4M14 4h6m0 0v6m0-6L10 14" /></svg>
                        </a>
                      )}
                    </div>
                  </div>
                ))}
              </div>
            </section>
          )}

          {/* Source */}
          {benefit.sourceUrl && (
            <div className="mt-8 pt-6 border-t border-[var(--border-color)]">
              <a
                href={benefit.sourceUrl}
                target="_blank"
                rel="noopener noreferrer"
                className="text-sm text-[var(--text-tertiary)] hover:text-[var(--text-secondary)]"
              >
                Fonte oficial: {benefit.sourceUrl}
              </a>
            </div>
          )}

          {/* CTA */}
          <div className="mt-8 pt-6 border-t border-[var(--border-color)] space-y-3">
            <Link
              to={`/beneficios/${benefit.id}/verificar`}
              className="block w-full py-4 bg-emerald-600 hover:bg-emerald-500 text-white font-semibold text-center rounded-xl transition-colors"
            >
              Verificar se tenho direito
            </Link>
            <Link
              to="/descobrir"
              className="block w-full py-3 bg-[var(--badge-bg)] hover:bg-[var(--hover-bg)] text-[var(--text-secondary)] font-medium text-center rounded-xl transition-colors text-sm"
            >
              Ver todos os benefícios que posso receber
            </Link>
          </div>
        </div>
      </main>
    </div>
  );
}
