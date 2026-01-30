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
      <div className="min-h-screen bg-slate-900 flex items-center justify-center">
        <div className="flex items-center gap-3 text-slate-400">
          <div className="w-5 h-5 border-2 border-emerald-500 border-t-transparent rounded-full animate-spin" />
          <span>Carregando benefício...</span>
        </div>
      </div>
    );
  }

  // Error/Not found state
  if (isError || !benefit) {
    return (
      <div className="min-h-screen bg-slate-900 flex items-center justify-center">
        <div className="text-center">
          <p className="text-slate-400 mb-4">
            {error instanceof Error ? error.message : 'Benefício não encontrado'}
          </p>
          <Link to="/beneficios" className="text-emerald-400 hover:text-emerald-300">
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
    <div className="min-h-screen bg-gradient-to-b from-slate-900 via-slate-900 to-slate-950">
      {/* Header */}
      <header className="fixed top-0 left-0 right-0 bg-slate-900/95 backdrop-blur-sm border-b border-slate-800 z-50">
        <div className="max-w-5xl mx-auto px-4 py-4 flex justify-between items-center">
          <Link to="/" className="text-xl font-bold text-emerald-400">
            Tá na Mão
          </Link>
          <button
            onClick={() => navigate(-1)}
            className="text-slate-400 hover:text-white text-sm"
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
                  benefit.scope === 'federal' ? 'bg-blue-500/20 text-blue-300' :
                  benefit.scope === 'state' ? 'bg-purple-500/20 text-purple-300' :
                  'bg-amber-500/20 text-amber-300'
                }`}>
                  {scopeLabel()}
                </span>
              </div>
            </div>
            <h1 className="text-2xl font-bold text-white mb-3">
              {benefit.name}
            </h1>
            <p className="text-lg text-slate-300">
              {benefit.shortDescription}
            </p>
          </div>

          {/* Value */}
          {benefit.estimatedValue && (
            <div className="p-4 rounded-xl bg-emerald-500/10 border border-emerald-500/30 mb-6">
              <div className="flex items-center gap-2 text-emerald-400">
                <span className="text-xl">💰</span>
                <span className="font-semibold text-lg">
                  {formatBenefitValue(benefit)}
                </span>
              </div>
              {benefit.estimatedValue.description && (
                <p className="text-sm text-emerald-400/80 mt-1 ml-7">
                  {benefit.estimatedValue.description}
                </p>
              )}
            </div>
          )}

          {/* Quem pode receber */}
          <section className="mb-8">
            <h2 className="text-lg font-semibold text-white mb-4 flex items-center gap-2">
              <span>✅</span> Quem pode receber
            </h2>
            <div className="space-y-3">
              {benefit.eligibilityRules.map((rule, idx) => (
                <div
                  key={idx}
                  className="p-3 rounded-lg bg-slate-800/50 border border-slate-700"
                >
                  <p className="text-slate-300">{rule.description}</p>
                </div>
              ))}
            </div>
          </section>

          {/* Onde pedir */}
          <section className="mb-8">
            <h2 className="text-lg font-semibold text-white mb-4 flex items-center gap-2">
              <span>📍</span> Onde pedir
            </h2>
            <div className="p-4 rounded-xl bg-slate-800/50 border border-slate-700">
              <p className="text-slate-200">{benefit.whereToApply}</p>
            </div>
          </section>

          {/* Documentos necessários */}
          <section className="mb-8">
            <h2 className="text-lg font-semibold text-white mb-4 flex items-center gap-2">
              <span>📄</span> Documentos necessários
            </h2>
            <ul className="space-y-2">
              {benefit.documentsRequired.map((doc, idx) => (
                <li
                  key={idx}
                  className="flex items-center gap-3 p-3 rounded-lg bg-slate-800/50 border border-slate-700"
                >
                  <span className="text-emerald-400">•</span>
                  <span className="text-slate-300">{doc}</span>
                </li>
              ))}
            </ul>
          </section>

          {/* Como pedir */}
          {benefit.howToApply && (
            <section className="mb-8">
              <h2 className="text-lg font-semibold text-white mb-4 flex items-center gap-2">
                <span>📋</span> Como pedir
              </h2>
              <div className="space-y-3">
                {benefit.howToApply.map((step, idx) => (
                  <div
                    key={idx}
                    className="flex items-start gap-3 p-3 rounded-lg bg-slate-800/50 border border-slate-700"
                  >
                    <span className="w-6 h-6 rounded-full bg-emerald-600 text-white text-sm flex items-center justify-center flex-shrink-0">
                      {idx + 1}
                    </span>
                    <p className="text-slate-300">{step}</p>
                  </div>
                ))}
              </div>
            </section>
          )}

          {/* Source */}
          {benefit.sourceUrl && (
            <div className="mt-8 pt-6 border-t border-slate-800">
              <a
                href={benefit.sourceUrl}
                target="_blank"
                rel="noopener noreferrer"
                className="text-sm text-slate-500 hover:text-slate-400"
              >
                Fonte oficial: {benefit.sourceUrl}
              </a>
            </div>
          )}

          {/* CTA */}
          <div className="mt-8 pt-6 border-t border-slate-800">
            <Link
              to="/descobrir"
              className="block w-full py-4 bg-emerald-600 hover:bg-emerald-500 text-white font-semibold text-center rounded-xl transition-colors"
            >
              Verificar se tenho direito a este e outros benefícios
            </Link>
          </div>
        </div>
      </main>
    </div>
  );
}
