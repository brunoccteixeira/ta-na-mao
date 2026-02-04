/**
 * Empowerment - Hub de Empoderamento
 * Rota: /empoderamento
 * Agregador de serviços: emprego, capacitação, comparador, economia solidária.
 * Cada seção direciona ao chat com mensagem pré-preenchida.
 */

import { useNavigate } from 'react-router-dom';
import ServiceCard from '../components/Cards/ServiceCard';

const SERVICES = [
  {
    id: 'emprego',
    icon: (
      <svg className="w-7 h-7 text-white" fill="none" stroke="currentColor" viewBox="0 0 24 24">
        <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M21 13.255A23.931 23.931 0 0112 15c-3.183 0-6.22-.62-9-1.745M16 6V4a2 2 0 00-2-2h-4a2 2 0 00-2 2v2m4 6h.01M5 20h14a2 2 0 002-2V8a2 2 0 00-2-2H5a2 2 0 00-2 2v10a2 2 0 002 2z" />
      </svg>
    ),
    title: 'Emprego',
    description:
      'Encontre vagas de emprego perto de voce. Priorizamos vagas para quem esta no CadUnico, primeiro emprego e sem experiencia.',
    ctaText: 'Buscar vagas',
    color: 'bg-gradient-to-br from-blue-500 to-blue-600',
    chatMessage: 'Quero encontrar vagas de emprego perto de mim',
  },
  {
    id: 'capacitacao',
    icon: (
      <svg className="w-7 h-7 text-white" fill="none" stroke="currentColor" viewBox="0 0 24 24">
        <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M12 6.253v13m0-13C10.832 5.477 9.246 5 7.5 5S4.168 5.477 3 6.253v13C4.168 18.477 5.754 18 7.5 18s3.332.477 4.5 1.253m0-13C13.168 5.477 14.754 5 16.5 5c1.747 0 3.332.477 4.5 1.253v13C19.832 18.477 18.247 18 16.5 18c-1.746 0-3.332.477-4.5 1.253" />
      </svg>
    ),
    title: 'Capacitacao',
    description:
      'Cursos gratuitos do SENAI, SENAC, SEBRAE e Pronatec para crescer na carreira. Quem esta no CadUnico tem prioridade!',
    ctaText: 'Ver cursos gratis',
    color: 'bg-gradient-to-br from-purple-500 to-purple-600',
    chatMessage: 'Quero ver cursos gratuitos de capacitacao',
  },
  {
    id: 'comparador',
    icon: (
      <svg className="w-7 h-7 text-white" fill="none" stroke="currentColor" viewBox="0 0 24 24">
        <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M9 7h6m0 10v-3m-3 3h.01M9 17h.01M9 14h.01M12 14h.01M15 11h.01M12 11h.01M9 11h.01M7 21h10a2 2 0 002-2V5a2 2 0 00-2-2H7a2 2 0 00-2 2v14a2 2 0 002 2z" />
      </svg>
    ),
    title: 'Comparador',
    description:
      'Compare planos de celular, contas bancarias e veja como economizar na conta de luz com a Tarifa Social.',
    ctaText: 'Comparar servicos',
    color: 'bg-gradient-to-br from-amber-500 to-orange-600',
    chatMessage: 'Quero comparar servicos e economizar',
  },
  {
    id: 'economia-solidaria',
    icon: (
      <svg className="w-7 h-7 text-white" fill="none" stroke="currentColor" viewBox="0 0 24 24">
        <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M17 20h5v-2a3 3 0 00-5.356-1.857M17 20H7m10 0v-2c0-.656-.126-1.283-.356-1.857M7 20H2v-2a3 3 0 015.356-1.857M7 20v-2c0-.656.126-1.283.356-1.857m0 0a5.002 5.002 0 019.288 0M15 7a3 3 0 11-6 0 3 3 0 016 0zm6 3a2 2 0 11-4 0 2 2 0 014 0zM7 10a2 2 0 11-4 0 2 2 0 014 0z" />
      </svg>
    ),
    title: 'Economia Solidaria',
    description:
      'Feiras, cooperativas e grupos de economia solidaria perto de voce. Compre direto de quem produz e apoie sua comunidade.',
    ctaText: 'Encontrar feiras',
    color: 'bg-gradient-to-br from-emerald-500 to-green-600',
    chatMessage: 'Quero encontrar feiras e cooperativas perto de mim',
  },
];

export default function Empowerment() {
  const navigate = useNavigate();

  const handleServiceAction = (chatMessage: string) => {
    // Navega para descobrir com mensagem pré-preenchida no chat
    // Em produção, abriria o chat com a mensagem
    const encoded = encodeURIComponent(chatMessage);
    navigate(`/descobrir?chat=${encoded}`);
  };

  return (
    <div className="min-h-screen bg-[var(--bg-primary)]">
      {/* Header */}
      <header className="bg-[var(--bg-header)] border-b border-[var(--border-color)]">
        <div className="max-w-4xl mx-auto px-4 py-6">
          <nav className="flex items-center gap-3 mb-6">
            <a
              href="/"
              className="text-sm text-[var(--text-tertiary)] hover:text-[var(--text-primary)] transition-colors"
            >
              Inicio
            </a>
            <span className="text-[var(--text-tertiary)]">/</span>
            <span className="text-sm text-[var(--text-primary)] font-medium">Empoderamento</span>
          </nav>

          <div className="flex items-center gap-4">
            <div className="w-14 h-14 rounded-2xl bg-gradient-to-br from-emerald-500 to-green-600 flex items-center justify-center">
              <svg className="w-8 h-8 text-white" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M13 10V3L4 14h7v7l9-11h-7z" />
              </svg>
            </div>
            <div>
              <h1 className="text-2xl font-bold text-[var(--text-primary)]">
                Empoderamento
              </h1>
              <p className="text-[var(--text-secondary)]">
                Ferramentas para crescer alem dos beneficios
              </p>
            </div>
          </div>
        </div>
      </header>

      {/* Services Grid */}
      <main className="max-w-4xl mx-auto px-4 py-8">
        <p className="text-[var(--text-secondary)] mb-8 max-w-2xl">
          Beneficios sociais sao um direito seu e te ajudam agora. Mas voce
          tambem pode usar essas ferramentas para conquistar mais
          independencia: emprego, capacitacao, economia e apoio da comunidade.
        </p>

        <div className="grid sm:grid-cols-2 gap-6">
          {SERVICES.map((service) => (
            <ServiceCard
              key={service.id}
              icon={service.icon}
              title={service.title}
              description={service.description}
              ctaText={service.ctaText}
              color={service.color}
              onAction={() => handleServiceAction(service.chatMessage)}
            />
          ))}
        </div>

        {/* Microcredito Section */}
        <div className="mt-12 p-6 rounded-2xl bg-gradient-to-br from-emerald-600/10 via-emerald-500/5 to-transparent border border-emerald-500/20">
          <div className="flex items-start gap-4">
            <div className="w-12 h-12 rounded-xl bg-gradient-to-br from-emerald-500 to-teal-600 flex items-center justify-center shrink-0">
              <svg className="w-7 h-7 text-white" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M12 8c-1.657 0-3 .895-3 2s1.343 2 3 2 3 .895 3 2-1.343 2-3 2m0-8c1.11 0 2.08.402 2.599 1M12 8V7m0 1v8m0 0v1m0-1c-1.11 0-2.08-.402-2.599-1M21 12a9 9 0 11-18 0 9 9 0 0118 0z" />
              </svg>
            </div>
            <div>
              <h3 className="text-lg font-bold text-[var(--text-primary)] mb-2">
                Microcredito Produtivo
              </h3>
              <p className="text-sm text-[var(--text-secondary)] mb-4">
                Quer abrir um negocio ou investir no seu trabalho? O governo oferece
                emprestimos com juros muito baixos para empreendedores de baixa renda.
                CrediAmigo, Pronaf e PNMPO — sem burocracia.
              </p>
              <button
                onClick={() => handleServiceAction('Quero saber sobre microcredito para abrir um negocio')}
                className="px-5 py-2.5 rounded-lg bg-emerald-600 hover:bg-emerald-500 text-white text-sm font-medium transition-colors"
              >
                Simular microcredito
              </button>
            </div>
          </div>
        </div>
      </main>

      {/* Footer CTA */}
      <div className="max-w-4xl mx-auto px-4 py-8 text-center">
        <p className="text-[var(--text-tertiary)] text-sm mb-3">
          Nao sabe por onde comecar?
        </p>
        <a
          href="/descobrir"
          className="inline-flex items-center gap-2 px-6 py-3 rounded-xl bg-emerald-600 hover:bg-emerald-500 text-white font-medium transition-colors"
        >
          <svg className="w-5 h-5" fill="none" stroke="currentColor" viewBox="0 0 24 24">
            <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M8 12h.01M12 12h.01M16 12h.01M21 12c0 4.418-4.03 8-9 8a9.863 9.863 0 01-4.255-.949L3 20l1.395-3.72C3.512 15.042 3 13.574 3 12c0-4.418 4.03-8 9-8s9 3.582 9 8z" />
          </svg>
          Fale com nosso assistente
        </a>
      </div>
    </div>
  );
}
