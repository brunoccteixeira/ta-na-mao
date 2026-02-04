/**
 * About - About the project
 */

import { Link } from 'react-router-dom';

export default function About() {
  return (
    <div className="min-h-screen bg-[var(--bg-primary)]">
      {/* Header */}
      <header className="fixed top-0 left-0 right-0 bg-[var(--bg-header)] backdrop-blur-sm border-b border-[var(--border-color)] z-50">
        <div className="max-w-5xl mx-auto px-4 py-4 flex justify-between items-center">
          <Link to="/" className="text-xl font-bold text-emerald-600">
            Tá na Mão
          </Link>
          <nav className="flex gap-4">
            <Link to="/beneficios" className="text-[var(--text-secondary)] hover:text-[var(--text-primary)] text-sm">
              Catálogo
            </Link>
            <Link to="/descobrir" className="text-emerald-600 hover:text-emerald-500 text-sm font-medium">
              Descobrir direitos
            </Link>
          </nav>
        </div>
      </header>

      {/* Content */}
      <main className="pt-24 pb-16 px-4">
        <div className="max-w-2xl mx-auto">
          <h1 className="text-3xl font-bold text-[var(--text-primary)] mb-6">
            Sobre o Tá na Mão
          </h1>

          <div className="prose max-w-none">
            <section className="mb-10">
              <h2 className="text-xl font-semibold text-[var(--text-primary)] mb-4">
                O que é?
              </h2>
              <p className="text-[var(--text-secondary)] leading-relaxed">
                O Tá na Mão é uma plataforma gratuita que ajuda brasileiros a descobrirem
                quais benefícios sociais podem ter direito. Em apenas 3 minutos, você
                responde algumas perguntas simples e nós mostramos todos os programas
                federais, estaduais e setoriais disponíveis para você.
              </p>
            </section>

            <section className="mb-10">
              <h2 className="text-xl font-semibold text-[var(--text-primary)] mb-4">
                O que NÃO fazemos
              </h2>
              <ul className="space-y-2 text-[var(--text-secondary)]">
                <li className="flex items-start gap-2">
                  <span className="text-red-500">✕</span>
                  <span>Não entregamos benefícios diretamente</span>
                </li>
                <li className="flex items-start gap-2">
                  <span className="text-red-500">✕</span>
                  <span>Não pedimos sua senha do Gov.br</span>
                </li>
                <li className="flex items-start gap-2">
                  <span className="text-red-500">✕</span>
                  <span>Não cobramos nada</span>
                </li>
                <li className="flex items-start gap-2">
                  <span className="text-red-500">✕</span>
                  <span>Não vendemos seus dados</span>
                </li>
              </ul>
            </section>

            <section className="mb-10">
              <h2 className="text-xl font-semibold text-[var(--text-primary)] mb-4">
                O que fazemos
              </h2>
              <ul className="space-y-2 text-[var(--text-secondary)]">
                <li className="flex items-start gap-2">
                  <span className="text-emerald-600">✓</span>
                  <span>Analisamos sua situação com base no que você nos conta</span>
                </li>
                <li className="flex items-start gap-2">
                  <span className="text-emerald-600">✓</span>
                  <span>Mostramos todos os benefícios que você pode ter direito</span>
                </li>
                <li className="flex items-start gap-2">
                  <span className="text-emerald-600">✓</span>
                  <span>Explicamos onde ir e quais documentos levar</span>
                </li>
                <li className="flex items-start gap-2">
                  <span className="text-emerald-600">✓</span>
                  <span>Usamos linguagem simples que todo mundo entende</span>
                </li>
              </ul>
            </section>

            <section className="mb-10">
              <h2 className="text-xl font-semibold text-[var(--text-primary)] mb-4">
                Nossa cobertura
              </h2>
              <div className="grid grid-cols-2 gap-4">
                <div className="p-4 rounded-xl bg-[var(--bg-card)] border border-[var(--border-color)]">
                  <div className="text-2xl font-bold text-emerald-600">15+</div>
                  <div className="text-sm text-[var(--text-tertiary)]">Benefícios federais</div>
                </div>
                <div className="p-4 rounded-xl bg-[var(--bg-card)] border border-[var(--border-color)]">
                  <div className="text-2xl font-bold text-emerald-600">27</div>
                  <div className="text-sm text-[var(--text-tertiary)]">Estados cobertos</div>
                </div>
                <div className="p-4 rounded-xl bg-[var(--bg-card)] border border-[var(--border-color)]">
                  <div className="text-2xl font-bold text-emerald-600">80+</div>
                  <div className="text-sm text-[var(--text-tertiary)]">Programas no total</div>
                </div>
                <div className="p-4 rounded-xl bg-[var(--bg-card)] border border-[var(--border-color)]">
                  <div className="text-2xl font-bold text-emerald-600">10+</div>
                  <div className="text-sm text-[var(--text-tertiary)]">Setores profissionais</div>
                </div>
              </div>
            </section>

            <section className="mb-10">
              <h2 className="text-xl font-semibold text-[var(--text-primary)] mb-4">
                Segurança
              </h2>
              <p className="text-[var(--text-secondary)] leading-relaxed">
                Sua privacidade é importante para nós. As informações que você fornece
                são usadas apenas para calcular sua elegibilidade e não são armazenadas
                em nossos servidores. Você não precisa criar conta ou fornecer
                informações pessoais identificáveis.
              </p>
            </section>

            <section className="mb-10">
              <h2 className="text-xl font-semibold text-[var(--text-primary)] mb-4">
                Contato
              </h2>
              <p className="text-[var(--text-secondary)] leading-relaxed">
                Se você encontrou algum erro ou quer sugerir um novo benefício para
                incluirmos, entre em contato conosco.
              </p>
            </section>
          </div>

          {/* CTA */}
          <div className="mt-12 pt-8 border-t border-[var(--border-color)] text-center">
            <Link
              to="/descobrir"
              className="inline-flex items-center gap-2 px-8 py-4 bg-emerald-600 hover:bg-emerald-500 text-white font-semibold rounded-xl transition-all"
            >
              Descobrir meus direitos
            </Link>
          </div>
        </div>
      </main>
    </div>
  );
}
