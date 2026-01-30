/**
 * Home - Landing page with CTA
 */

import { Link } from 'react-router-dom';
import { getBenefitsCatalog, getCatalogStats } from '../engine/catalog';

export default function Home() {
  const catalog = getBenefitsCatalog();
  const stats = getCatalogStats(catalog);

  const popularBenefits = [
    { id: 'federal-bolsa-familia', name: 'Bolsa Família', icon: '🏠', desc: 'Ajuda mensal para famílias' },
    { id: 'federal-bpc-idoso', name: 'BPC Idoso', icon: '👴', desc: 'Salário mínimo para 65+' },
    { id: 'federal-farmacia-popular', name: 'Farmácia Popular', icon: '💊', desc: 'Remédios grátis' },
    { id: 'federal-tsee', name: 'Tarifa Social Luz', icon: '💡', desc: 'Desconto na conta de luz' },
    { id: 'federal-auxilio-gas', name: 'Auxílio Gás', icon: '🔥', desc: 'Ajuda para comprar gás' },
    { id: 'federal-mcmv', name: 'Minha Casa', icon: '🏡', desc: 'Casa própria facilitada' },
  ];

  return (
    <div className="min-h-screen bg-gradient-to-b from-slate-900 via-slate-900 to-slate-950">
      {/* Header */}
      <header className="fixed top-0 left-0 right-0 bg-slate-900/95 backdrop-blur-sm border-b border-slate-800 z-50">
        <div className="max-w-5xl mx-auto px-4 py-4 flex justify-between items-center">
          <Link to="/" className="text-xl font-bold text-emerald-400">
            Tá na Mão
          </Link>
          <nav className="flex gap-4">
            <Link to="/beneficios" className="text-slate-300 hover:text-white text-sm">
              Catálogo
            </Link>
            <Link to="/sobre" className="text-slate-300 hover:text-white text-sm">
              Sobre
            </Link>
          </nav>
        </div>
      </header>

      {/* Hero */}
      <main className="pt-24 pb-16 px-4">
        <div className="max-w-2xl mx-auto text-center">
          <div className="text-5xl mb-6">🤝</div>
          <h1 className="text-3xl md:text-4xl font-bold text-white mb-4">
            Descubra seus direitos<br />em 3 minutos
          </h1>
          <p className="text-lg text-slate-400 mb-8">
            Benefícios federais, estaduais e setoriais<br />
            em um só lugar.
          </p>

          <Link
            to="/descobrir"
            className="inline-flex items-center gap-2 px-8 py-4 bg-emerald-600 hover:bg-emerald-500 text-white font-semibold text-lg rounded-2xl transition-all shadow-lg shadow-emerald-600/20 hover:shadow-emerald-500/30"
          >
            🎯 Descobrir meus direitos
          </Link>
        </div>

        {/* Como funciona */}
        <div className="max-w-3xl mx-auto mt-20">
          <h2 className="text-xl font-semibold text-white text-center mb-8">
            Como funciona
          </h2>
          <div className="grid md:grid-cols-3 gap-6">
            <div className="text-center p-6 rounded-2xl bg-slate-800/50 border border-slate-700">
              <div className="w-12 h-12 rounded-full bg-emerald-600/20 flex items-center justify-center mx-auto mb-4">
                <span className="text-2xl">📋</span>
              </div>
              <h3 className="font-medium text-white mb-2">1. Responda perguntas</h3>
              <p className="text-sm text-slate-400">
                Algumas perguntas simples sobre você e sua família
              </p>
            </div>
            <div className="text-center p-6 rounded-2xl bg-slate-800/50 border border-slate-700">
              <div className="w-12 h-12 rounded-full bg-emerald-600/20 flex items-center justify-center mx-auto mb-4">
                <span className="text-2xl">✨</span>
              </div>
              <h3 className="font-medium text-white mb-2">2. Veja os benefícios</h3>
              <p className="text-sm text-slate-400">
                Descobrimos todos os programas que você pode ter direito
              </p>
            </div>
            <div className="text-center p-6 rounded-2xl bg-slate-800/50 border border-slate-700">
              <div className="w-12 h-12 rounded-full bg-emerald-600/20 flex items-center justify-center mx-auto mb-4">
                <span className="text-2xl">📍</span>
              </div>
              <h3 className="font-medium text-white mb-2">3. Saiba como pedir</h3>
              <p className="text-sm text-slate-400">
                Te mostramos onde ir e quais documentos levar
              </p>
            </div>
          </div>
        </div>

        {/* Badges */}
        <div className="max-w-lg mx-auto mt-12 flex justify-center gap-4 flex-wrap">
          <span className="px-4 py-2 rounded-full bg-slate-800 text-slate-300 text-sm">
            ✅ Grátis
          </span>
          <span className="px-4 py-2 rounded-full bg-slate-800 text-slate-300 text-sm">
            ✅ Sem cadastro
          </span>
          <span className="px-4 py-2 rounded-full bg-slate-800 text-slate-300 text-sm">
            ✅ Sem senha Gov.br
          </span>
        </div>

        {/* Benefícios populares */}
        <div className="max-w-4xl mx-auto mt-20">
          <h2 className="text-xl font-semibold text-white text-center mb-8">
            Principais benefícios
          </h2>
          <div className="grid grid-cols-2 md:grid-cols-3 gap-4">
            {popularBenefits.map((benefit) => (
              <Link
                key={benefit.id}
                to={`/beneficios/${benefit.id}`}
                className="p-4 rounded-xl bg-slate-800/50 border border-slate-700 hover:border-emerald-500/50 hover:bg-slate-800 transition-all"
              >
                <span className="text-2xl">{benefit.icon}</span>
                <h3 className="font-medium text-white mt-2">{benefit.name}</h3>
                <p className="text-xs text-slate-400 mt-1">{benefit.desc}</p>
              </Link>
            ))}
          </div>

          <div className="text-center mt-6">
            <Link
              to="/beneficios"
              className="text-emerald-400 hover:text-emerald-300 text-sm"
            >
              Ver todos os {stats.totalBenefits} benefícios →
            </Link>
          </div>
        </div>

        {/* Cobertura */}
        <div className="max-w-2xl mx-auto mt-20 text-center">
          <h2 className="text-lg font-semibold text-white mb-6">
            📍 Cobertura nacional
          </h2>
          <div className="grid grid-cols-3 gap-4">
            <div className="p-4 rounded-xl bg-slate-800/50 border border-slate-700">
              <div className="text-2xl font-bold text-emerald-400">
                {stats.federalCount}
              </div>
              <div className="text-xs text-slate-400 mt-1">
                Benefícios federais
              </div>
            </div>
            <div className="p-4 rounded-xl bg-slate-800/50 border border-slate-700">
              <div className="text-2xl font-bold text-emerald-400">
                {stats.statesWithBenefits}
              </div>
              <div className="text-xs text-slate-400 mt-1">
                Estados cobertos
              </div>
            </div>
            <div className="p-4 rounded-xl bg-slate-800/50 border border-slate-700">
              <div className="text-2xl font-bold text-emerald-400">
                {stats.sectoralCount}
              </div>
              <div className="text-xs text-slate-400 mt-1">
                Benefícios setoriais
              </div>
            </div>
          </div>
        </div>
      </main>

      {/* Footer */}
      <footer className="border-t border-slate-800 py-8 px-4">
        <div className="max-w-4xl mx-auto text-center">
          <p className="text-slate-500 text-sm">
            Este site apenas informa sobre elegibilidade. Não entregamos benefícios diretamente.
          </p>
          <p className="text-slate-600 text-xs mt-2">
            Tá na Mão © 2024 - Feito para ajudar
          </p>
        </div>
      </footer>
    </div>
  );
}
