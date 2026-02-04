'use client';

/**
 * HomeClient - Landing page inspirada no Wizbii Money
 * Proposta de valor: Descubra → Acompanhe → Receba
 */

import Link from 'next/link';
import { useState, useEffect, useRef } from 'react';

interface HomeClientProps {
  totalBenefits: number;
  federalCount: number;
  statesCovered: number;
  sectoralCount: number;
}

function useCountUp(target: number, duration: number = 2000) {
  const [count, setCount] = useState(0);
  const [started, setStarted] = useState(false);
  const ref = useRef<HTMLDivElement>(null);

  useEffect(() => {
    if (typeof IntersectionObserver === 'undefined') {
      setStarted(true);
      return;
    }
    const observer = new IntersectionObserver(
      ([entry]) => { if (entry.isIntersecting && !started) setStarted(true); },
      { threshold: 0.3 }
    );
    if (ref.current) observer.observe(ref.current);
    return () => observer.disconnect();
  }, [started]);

  useEffect(() => {
    if (!started) return;
    const steps = 60;
    const increment = target / steps;
    const stepDuration = duration / steps;
    let current = 0;
    const timer = setInterval(() => {
      current += increment;
      if (current >= target) { setCount(target); clearInterval(timer); }
      else setCount(Math.floor(current));
    }, stepDuration);
    return () => clearInterval(timer);
  }, [started, target, duration]);

  return { count, ref };
}

function StatCard({ value, suffix, label }: { value: number; suffix: string; label: string }) {
  const { count, ref } = useCountUp(value);
  const formatted = suffix === ' bi' ? `R$ ${count}` : count.toLocaleString('pt-BR');
  return (
    <div ref={ref} className="text-center">
      <div className="text-3xl md:text-4xl font-bold text-emerald-600">
        {formatted}{suffix}
      </div>
      <div className="text-sm text-[var(--text-tertiary)] mt-1">{label}</div>
    </div>
  );
}

const popularBenefits = [
  { id: 'federal-bolsa-familia', name: 'Bolsa Família', icon: '🏠', desc: 'Ajuda mensal para famílias', value: 'Até R$ 900/mês' },
  { id: 'federal-bpc-idoso', name: 'BPC Idoso', icon: '👴', desc: 'Salário mínimo para 65+', value: 'R$ 1.412/mês' },
  { id: 'federal-farmacia-popular', name: 'Farmácia Popular', icon: '💊', desc: 'Remédios grátis', value: '100% grátis' },
  { id: 'federal-tsee', name: 'Tarifa Social Luz', icon: '💡', desc: 'Desconto na conta de luz', value: 'Até 65% off' },
  { id: 'federal-auxilio-gas', name: 'Auxílio Gás', icon: '🔥', desc: 'Ajuda para comprar gás', value: 'R$ 104/bimestre' },
  { id: 'federal-mcmv', name: 'Minha Casa', icon: '🏡', desc: 'Casa própria facilitada', value: 'Subsídio até R$ 55 mil' },
];

export default function HomeClient({ totalBenefits, federalCount, statesCovered, sectoralCount }: HomeClientProps) {
  return (
    <div className="min-h-screen bg-[var(--bg-primary)]">
      {/* Header */}
      <header className="fixed top-0 left-0 right-0 bg-[var(--bg-header)] backdrop-blur-sm border-b border-[var(--border-color)] z-50">
        <div className="max-w-6xl mx-auto px-4 py-4 flex justify-between items-center">
          <Link href="/" className="text-xl font-bold text-emerald-600">
            Tá na Mão
          </Link>
          <nav className="flex items-center gap-4">
            <Link href="/beneficios" className="text-[var(--text-secondary)] hover:text-[var(--text-primary)] text-sm hidden sm:inline">
              Catálogo
            </Link>
            <Link href="/sobre" className="text-[var(--text-secondary)] hover:text-[var(--text-primary)] text-sm hidden sm:inline">
              Sobre
            </Link>
            <Link
              href="/descobrir"
              className="px-5 py-2 bg-emerald-600 hover:bg-emerald-500 text-white text-sm font-semibold rounded-full transition-all"
            >
              Descobrir meus direitos
            </Link>
          </nav>
        </div>
      </header>

      <main>
        {/* ─── HERO ─── */}
        <section className="pt-28 pb-16 px-4 md:pt-32 md:pb-24">
          <div className="max-w-6xl mx-auto flex flex-col md:flex-row items-center gap-12">
            {/* Left: Text */}
            <div className="flex-1 text-center md:text-left">
              <h1 className="text-3xl md:text-5xl font-extrabold text-[var(--text-primary)] leading-tight">
                Não deixe passar<br />
                seus direitos!
              </h1>
              <p className="text-[var(--text-secondary)] mt-4 text-lg">
                Tá na Mão, seu guia de benefícios sociais:
              </p>

              <ul className="mt-6 space-y-3 text-left inline-block">
                <li className="flex items-center gap-3">
                  <span className="w-6 h-6 rounded-full bg-emerald-500 flex items-center justify-center text-white text-xs font-bold">→</span>
                  <span className="text-[var(--text-primary)] font-semibold">Simulação rápida</span>
                </li>
                <li className="flex items-center gap-3">
                  <span className="w-6 h-6 rounded-full bg-emerald-500 flex items-center justify-center text-white text-xs font-bold">→</span>
                  <span className="text-[var(--text-primary)] font-semibold">Acompanhamento gratuito</span>
                </li>
                <li className="flex items-center gap-3">
                  <span className="w-6 h-6 rounded-full bg-emerald-500 flex items-center justify-center text-white text-xs font-bold">→</span>
                  <span className="text-[var(--text-primary)] font-semibold">100% grátis</span>
                </li>
              </ul>

              <div className="mt-8">
                <Link
                  href="/descobrir"
                  className="inline-flex items-center gap-2 px-8 py-4 bg-emerald-600 hover:bg-emerald-500 text-white font-semibold text-lg rounded-2xl transition-all shadow-lg shadow-emerald-600/20 hover:shadow-emerald-500/30"
                >
                  Descobrir meus direitos →
                </Link>
                <p className="text-[var(--text-tertiary)] text-sm mt-3">
                  Simulação rápida e sem cadastro
                </p>
              </div>
            </div>

            {/* Right: Floating benefit cards */}
            <div className="flex-1 relative hidden md:block">
              <div className="relative w-full max-w-md mx-auto h-80">
                {/* Background circle */}
                <div className="absolute inset-0 m-auto w-72 h-72 rounded-full bg-emerald-50" />

                {/* Floating cards */}
                <div className="absolute top-4 right-0 bg-white rounded-xl shadow-lg p-3 border border-gray-100" style={{ animation: 'float 3s ease-in-out infinite' }}>
                  <p className="text-xs text-gray-500">Bolsa Família</p>
                  <p className="text-emerald-600 font-bold">R$ 600,00<span className="text-xs font-normal text-gray-400"> /mês</span></p>
                </div>

                <div className="absolute top-28 -left-4 bg-white rounded-xl shadow-lg p-3 border border-gray-100" style={{ animation: 'float 3s ease-in-out infinite 0.5s' }}>
                  <p className="text-xs text-gray-500">Farmácia Popular</p>
                  <p className="text-emerald-600 font-bold">100% grátis</p>
                </div>

                <div className="absolute bottom-8 right-4 bg-white rounded-xl shadow-lg p-3 border border-gray-100" style={{ animation: 'float 3s ease-in-out infinite 1s' }}>
                  <p className="text-xs text-gray-500">Tarifa Social Luz</p>
                  <p className="text-emerald-600 font-bold">-65%<span className="text-xs font-normal text-gray-400"> na conta</span></p>
                </div>

                {/* Eligibility badge */}
                <div className="absolute -top-2 right-0 bg-slate-800 text-white rounded-xl px-4 py-2 shadow-lg">
                  <p className="text-xs opacity-80">Benefícios elegíveis:</p>
                  <p className="text-emerald-400 font-bold text-lg">R$ 8.640<span className="text-xs font-normal opacity-80"> /ano</span></p>
                </div>

                {/* Status badges */}
                <div className="absolute bottom-0 -left-2 flex flex-col gap-2">
                  <span className="inline-flex items-center gap-1.5 bg-emerald-500 text-white text-xs font-medium px-3 py-1.5 rounded-full shadow">
                    <svg className="w-3.5 h-3.5" fill="none" viewBox="0 0 24 24" stroke="currentColor"><path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M5 13l4 4L19 7" /></svg>
                    Simulação concluída
                  </span>
                  <span className="inline-flex items-center gap-1.5 bg-emerald-500 text-white text-xs font-medium px-3 py-1.5 rounded-full shadow">
                    <svg className="w-3.5 h-3.5" fill="none" viewBox="0 0 24 24" stroke="currentColor"><path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M5 13l4 4L19 7" /></svg>
                    Documentos enviados
                  </span>
                </div>
              </div>
            </div>
          </div>
        </section>

        {/* ─── DARK SECTION: "SABIA QUE?" ─── */}
        <section className="bg-slate-900 text-white py-16 px-4">
          <div className="max-w-6xl mx-auto flex flex-col md:flex-row items-center gap-12">
            <div className="flex-1">
              <h2 className="text-2xl md:text-4xl font-extrabold leading-tight">
                Ninguém deveria deixar<br />
                de receber seus direitos!
              </h2>
              <p className="text-slate-300 mt-4">
                Para usar nosso serviço você só precisa:
              </p>
              <ul className="mt-4 space-y-2">
                <li className="flex items-center gap-3">
                  <span className="text-emerald-400 font-bold">→</span>
                  <span className="font-semibold">Morar no Brasil</span>
                </li>
                <li className="flex items-center gap-3">
                  <span className="text-emerald-400 font-bold">→</span>
                  <span className="font-semibold">Ter CPF</span>
                </li>
              </ul>

              <div className="mt-8 bg-slate-800 rounded-xl p-5 border border-slate-700">
                <p className="text-emerald-400 font-bold text-sm">Sabia que?</p>
                <p className="text-amber-400 font-bold text-lg mt-1">
                  R$ 42 bilhões em benefícios não são resgatados no Brasil!
                </p>
              </div>

              <div className="mt-6">
                <Link
                  href="/descobrir"
                  className="inline-flex items-center gap-2 px-8 py-4 bg-emerald-500 hover:bg-emerald-400 text-white font-semibold text-lg rounded-2xl transition-all"
                >
                  Descobrir meus direitos →
                </Link>
              </div>
            </div>

            {/* Right: Benefit categories checklist */}
            <div className="flex-1 flex justify-center">
              <div className="bg-white rounded-2xl p-6 shadow-xl max-w-sm w-full">
                <ul className="space-y-4">
                  {[
                    'Benefícios para famílias',
                    'Saúde e medicamentos',
                    'Moradia e habitação',
                    'Trabalho e renda',
                    'Educação e capacitação',
                  ].map((item) => (
                    <li key={item} className="flex items-center gap-3">
                      <div className="w-6 h-6 rounded-full bg-emerald-500 flex items-center justify-center flex-shrink-0">
                        <svg className="w-3.5 h-3.5 text-white" fill="none" viewBox="0 0 24 24" stroke="currentColor"><path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2.5} d="M5 13l4 4L19 7" /></svg>
                      </div>
                      <span className="text-slate-800 font-medium">{item}</span>
                    </li>
                  ))}
                </ul>
              </div>
            </div>
          </div>
        </section>

        {/* ─── 3-STEP VALUE PROPOSITION ─── */}
        <section className="py-20 px-4">
          <div className="max-w-3xl mx-auto">
            {/* Step 1 */}
            <div className="flex gap-6 items-start">
              <div className="flex flex-col items-center flex-shrink-0">
                <div className="w-10 h-10 rounded-full bg-emerald-500 text-white flex items-center justify-center font-bold text-lg">1</div>
                <div className="w-0.5 h-24 bg-emerald-200 mt-2" />
              </div>
              <div className="pb-12">
                <h3 className="text-xl font-bold text-[var(--text-primary)]">
                  Descubra quanto você pode receber
                </h3>
                <p className="text-[var(--text-secondary)] mt-2">
                  {totalBenefits}+ benefícios mapeados em todo o Brasil.
                  Seus dados ficam 100% protegidos.
                </p>
              </div>
            </div>

            {/* Step 2 */}
            <div className="flex gap-6 items-start">
              <div className="flex flex-col items-center flex-shrink-0">
                <div className="w-10 h-10 rounded-full bg-emerald-500 text-white flex items-center justify-center font-bold text-lg">2</div>
                <div className="w-0.5 h-24 bg-emerald-200 mt-2" />
              </div>
              <div className="pb-12">
                <h3 className="text-xl font-bold text-[var(--text-primary)]">
                  Você não está sozinho(a)
                </h3>
                <p className="text-[var(--text-secondary)] mt-2">
                  Acompanhamento até conseguir o benefício.
                  Te mostramos onde ir, o que levar e como dar entrada.
                </p>
              </div>
            </div>

            {/* Step 3 */}
            <div className="flex gap-6 items-start">
              <div className="flex flex-col items-center flex-shrink-0">
                <div className="w-10 h-10 rounded-full bg-emerald-500 text-white flex items-center justify-center font-bold text-lg">3</div>
              </div>
              <div>
                <h3 className="text-xl font-bold text-[var(--text-primary)]">
                  Receba seus benefícios
                </h3>
                <p className="text-[var(--text-secondary)] mt-2">
                  Te ajudamos a acompanhar o processo até a aprovação.
                  Chega de burocracia!
                </p>
              </div>
            </div>

            <div className="text-center mt-10">
              <Link
                href="/descobrir"
                className="inline-flex items-center gap-2 px-8 py-4 bg-emerald-600 hover:bg-emerald-500 text-white font-semibold text-lg rounded-2xl transition-all shadow-lg shadow-emerald-600/20"
              >
                Começar simulação gratuita →
              </Link>
            </div>
          </div>
        </section>

        {/* ─── NÚMEROS + FONTES DE DADOS ─── */}
        <section className="bg-[var(--bg-card)] border-y border-[var(--border-color)] py-16 px-4">
          <div className="max-w-4xl mx-auto">
            {/* Stats */}
            <div className="grid grid-cols-2 md:grid-cols-4 gap-8 mb-12">
              <StatCard value={totalBenefits} suffix="+" label="Benefícios mapeados" />
              <StatCard value={statesCovered} suffix="" label="Estados cobertos" />
              <StatCard value={5570} suffix="" label="Municípios" />
              <StatCard value={42} suffix=" bi" label="Não resgatados no Brasil" />
            </div>

            {/* Trust: Data sources */}
            <div className="text-center">
              <p className="text-[var(--text-tertiary)] text-sm mb-4">Dados oficiais de:</p>
              <div className="flex flex-wrap justify-center gap-6 items-center">
                {[
                  { name: 'Gov.br', color: 'text-blue-600' },
                  { name: 'MDS', color: 'text-orange-600' },
                  { name: 'IBGE', color: 'text-green-700' },
                  { name: 'DataSUS', color: 'text-red-600' },
                  { name: 'Caixa', color: 'text-blue-800' },
                  { name: 'INSS', color: 'text-indigo-600' },
                ].map((source) => (
                  <span
                    key={source.name}
                    className={`${source.color} font-bold text-lg opacity-60 hover:opacity-100 transition-opacity`}
                  >
                    {source.name}
                  </span>
                ))}
              </div>
            </div>
          </div>
        </section>

        {/* ─── BENEFÍCIOS POPULARES ─── */}
        <section className="py-16 px-4">
          <div className="max-w-4xl mx-auto">
            <h2 className="text-2xl font-bold text-[var(--text-primary)] text-center mb-3">
              Principais benefícios
            </h2>
            <p className="text-[var(--text-tertiary)] text-center mb-8">
              Conheça alguns dos {totalBenefits}+ programas que mapeamos
            </p>
            <div className="grid grid-cols-1 sm:grid-cols-2 md:grid-cols-3 gap-4">
              {popularBenefits.map((benefit) => (
                <Link
                  key={benefit.id}
                  href={`/beneficios/${benefit.id}`}
                  className="p-5 rounded-xl bg-[var(--bg-card)] border border-[var(--border-color)] hover:border-emerald-500/50 hover:shadow-md transition-all group"
                >
                  <div className="flex items-start justify-between">
                    <span className="text-2xl">{benefit.icon}</span>
                    <span className="text-xs font-semibold text-emerald-600 bg-emerald-50 px-2 py-1 rounded-full">
                      {benefit.value}
                    </span>
                  </div>
                  <h3 className="font-semibold text-[var(--text-primary)] mt-3 group-hover:text-emerald-600 transition-colors">
                    {benefit.name}
                  </h3>
                  <p className="text-sm text-[var(--text-tertiary)] mt-1">{benefit.desc}</p>
                </Link>
              ))}
            </div>

            <div className="text-center mt-8">
              <Link
                href="/beneficios"
                className="text-emerald-600 hover:text-emerald-500 font-medium"
              >
                Ver todos os {totalBenefits} benefícios →
              </Link>
            </div>
          </div>
        </section>

        {/* ─── CTA FINAL ─── */}
        <section className="bg-slate-900 text-white py-16 px-4">
          <div className="max-w-2xl mx-auto text-center">
            <h2 className="text-2xl md:text-3xl font-bold">
              Descubra seus direitos agora
            </h2>
            <p className="text-slate-300 mt-3">
              Simulação gratuita, sem cadastro, sem senha Gov.br
            </p>
            <div className="mt-8">
              <Link
                href="/descobrir"
                className="inline-flex items-center gap-2 px-10 py-4 bg-emerald-500 hover:bg-emerald-400 text-white font-semibold text-lg rounded-2xl transition-all"
              >
                Fazer minha simulação →
              </Link>
            </div>
          </div>
        </section>
      </main>

      {/* Footer */}
      <footer className="border-t border-[var(--border-color)] py-8 px-4">
        <div className="max-w-4xl mx-auto text-center">
          <p className="text-[var(--text-tertiary)] text-sm">
            Este site apenas informa sobre elegibilidade. Não entregamos benefícios diretamente.
          </p>
          <p className="text-[var(--text-tertiary)] text-xs mt-2 opacity-60">
            Tá na Mão &copy; 2025 - Feito para ajudar
          </p>
        </div>
      </footer>
    </div>
  );
}
