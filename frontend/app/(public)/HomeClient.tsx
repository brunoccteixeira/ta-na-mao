'use client';

import Link from 'next/link';
import SocialProof from '../../src/components/SocialProof';

interface HomeClientProps {
  totalBenefits: number;
  federalCount: number;
  statesCovered: number;
  sectoralCount: number;
}

const popularBenefits = [
  { id: 'federal-bolsa-familia', name: 'Bolsa Familia', icon: '🏠', desc: 'Ajuda mensal para familias' },
  { id: 'federal-bpc-idoso', name: 'BPC Idoso', icon: '👴', desc: 'Salario minimo para 65+' },
  { id: 'federal-farmacia-popular', name: 'Farmacia Popular', icon: '💊', desc: 'Remedios gratis' },
  { id: 'federal-tsee', name: 'Tarifa Social Luz', icon: '💡', desc: 'Desconto na conta de luz' },
  { id: 'federal-auxilio-gas', name: 'Auxilio Gas', icon: '🔥', desc: 'Ajuda para comprar gas' },
  { id: 'federal-mcmv', name: 'Minha Casa', icon: '🏡', desc: 'Casa propria facilitada' },
];

export default function HomeClient({ totalBenefits, federalCount, statesCovered, sectoralCount }: HomeClientProps) {
  return (
    <div className="min-h-screen bg-[var(--bg-primary)]">
      {/* Header */}
      <header className="fixed top-0 left-0 right-0 bg-[var(--bg-header)] backdrop-blur-sm border-b border-[var(--border-color)] z-50">
        <div className="max-w-5xl mx-auto px-4 py-4 flex justify-between items-center">
          <Link href="/" className="text-xl font-bold text-emerald-600">
            Ta na Mao
          </Link>
          <nav className="flex gap-4">
            <Link href="/beneficios" className="text-[var(--text-secondary)] hover:text-[var(--text-primary)] text-sm">
              Catalogo
            </Link>
            <Link href="/sobre" className="text-[var(--text-secondary)] hover:text-[var(--text-primary)] text-sm">
              Sobre
            </Link>
          </nav>
        </div>
      </header>

      {/* Hero */}
      <main className="pt-24 pb-16 px-4">
        <div className="max-w-2xl mx-auto text-center">
          <div className="text-5xl mb-6">🤝</div>
          <h1 className="text-3xl md:text-4xl font-bold text-[var(--text-primary)] mb-4">
            Descubra seus direitos<br />em 3 minutos
          </h1>
          <p className="text-lg text-[var(--text-tertiary)] mb-8">
            Beneficios federais, estaduais e setoriais<br />
            em um so lugar.
          </p>

          <Link
            href="/descobrir"
            className="inline-flex items-center gap-2 px-8 py-4 bg-emerald-600 hover:bg-emerald-500 text-white font-semibold text-lg rounded-2xl transition-all shadow-lg shadow-emerald-600/20 hover:shadow-emerald-500/30"
          >
            🎯 Descobrir meus direitos
          </Link>
        </div>

        {/* Social Proof */}
        <div className="max-w-4xl mx-auto mt-20">
          <SocialProof />
        </div>

        {/* Como funciona */}
        <div className="max-w-3xl mx-auto mt-20">
          <h2 className="text-xl font-semibold text-[var(--text-primary)] text-center mb-8">
            Como funciona
          </h2>
          <div className="grid md:grid-cols-3 gap-6">
            <div className="text-center p-6 rounded-2xl bg-[var(--bg-card)] border border-[var(--border-color)]">
              <div className="w-12 h-12 rounded-full bg-emerald-600/10 flex items-center justify-center mx-auto mb-4">
                <span className="text-2xl">📋</span>
              </div>
              <h3 className="font-medium text-[var(--text-primary)] mb-2">1. Responda perguntas</h3>
              <p className="text-sm text-[var(--text-tertiary)]">
                Algumas perguntas simples sobre voce e sua familia
              </p>
            </div>
            <div className="text-center p-6 rounded-2xl bg-[var(--bg-card)] border border-[var(--border-color)]">
              <div className="w-12 h-12 rounded-full bg-emerald-600/10 flex items-center justify-center mx-auto mb-4">
                <span className="text-2xl">✨</span>
              </div>
              <h3 className="font-medium text-[var(--text-primary)] mb-2">2. Veja os beneficios</h3>
              <p className="text-sm text-[var(--text-tertiary)]">
                Descobrimos todos os programas que voce pode ter direito
              </p>
            </div>
            <div className="text-center p-6 rounded-2xl bg-[var(--bg-card)] border border-[var(--border-color)]">
              <div className="w-12 h-12 rounded-full bg-emerald-600/10 flex items-center justify-center mx-auto mb-4">
                <span className="text-2xl">📍</span>
              </div>
              <h3 className="font-medium text-[var(--text-primary)] mb-2">3. Saiba como pedir</h3>
              <p className="text-sm text-[var(--text-tertiary)]">
                Te mostramos onde ir e quais documentos levar
              </p>
            </div>
          </div>
        </div>

        {/* Badges */}
        <div className="max-w-lg mx-auto mt-12 flex justify-center gap-4 flex-wrap">
          <span className="px-4 py-2 rounded-full bg-[var(--badge-bg)] text-[var(--text-secondary)] text-sm">
            ✅ Gratis
          </span>
          <span className="px-4 py-2 rounded-full bg-[var(--badge-bg)] text-[var(--text-secondary)] text-sm">
            ✅ Sem cadastro
          </span>
          <span className="px-4 py-2 rounded-full bg-[var(--badge-bg)] text-[var(--text-secondary)] text-sm">
            ✅ Sem senha Gov.br
          </span>
        </div>

        {/* Beneficios populares */}
        <div className="max-w-4xl mx-auto mt-20">
          <h2 className="text-xl font-semibold text-[var(--text-primary)] text-center mb-8">
            Principais beneficios
          </h2>
          <div className="grid grid-cols-2 md:grid-cols-3 gap-4">
            {popularBenefits.map((benefit) => (
              <Link
                key={benefit.id}
                href={`/beneficios/${benefit.id}`}
                className="p-4 rounded-xl bg-[var(--bg-card)] border border-[var(--border-color)] hover:border-emerald-500/50 hover:bg-[var(--hover-bg)] transition-all"
              >
                <span className="text-2xl">{benefit.icon}</span>
                <h3 className="font-medium text-[var(--text-primary)] mt-2">{benefit.name}</h3>
                <p className="text-xs text-[var(--text-tertiary)] mt-1">{benefit.desc}</p>
              </Link>
            ))}
          </div>

          <div className="text-center mt-6">
            <Link
              href="/beneficios"
              className="text-emerald-600 hover:text-emerald-500 text-sm"
            >
              Ver todos os {totalBenefits} beneficios →
            </Link>
          </div>
        </div>

        {/* Cobertura */}
        <div className="max-w-2xl mx-auto mt-20 text-center">
          <h2 className="text-lg font-semibold text-[var(--text-primary)] mb-6">
            📍 Cobertura nacional
          </h2>
          <div className="grid grid-cols-3 gap-4">
            <div className="p-4 rounded-xl bg-[var(--bg-card)] border border-[var(--border-color)]">
              <div className="text-2xl font-bold text-emerald-600">
                {federalCount}
              </div>
              <div className="text-xs text-[var(--text-tertiary)] mt-1">
                Beneficios federais
              </div>
            </div>
            <div className="p-4 rounded-xl bg-[var(--bg-card)] border border-[var(--border-color)]">
              <div className="text-2xl font-bold text-emerald-600">
                {statesCovered}
              </div>
              <div className="text-xs text-[var(--text-tertiary)] mt-1">
                Estados cobertos
              </div>
            </div>
            <div className="p-4 rounded-xl bg-[var(--bg-card)] border border-[var(--border-color)]">
              <div className="text-2xl font-bold text-emerald-600">
                {sectoralCount}
              </div>
              <div className="text-xs text-[var(--text-tertiary)] mt-1">
                Beneficios setoriais
              </div>
            </div>
          </div>
        </div>
      </main>

      {/* Footer */}
      <footer className="border-t border-[var(--border-color)] py-8 px-4">
        <div className="max-w-4xl mx-auto text-center">
          <p className="text-[var(--text-tertiary)] text-sm">
            Este site apenas informa sobre elegibilidade. Nao entregamos beneficios diretamente.
          </p>
          <p className="text-[var(--text-tertiary)] text-xs mt-2 opacity-60">
            Ta na Mao &copy; 2024 - Feito para ajudar
          </p>
        </div>
      </footer>
    </div>
  );
}
