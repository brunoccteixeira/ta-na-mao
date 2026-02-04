import type { Metadata } from 'next';
import Link from 'next/link';

export const metadata: Metadata = {
  title: 'Sobre | Ta na Mao',
  description: 'Saiba mais sobre o Ta na Mao, plataforma gratuita de acesso a beneficios sociais.',
};

export default function AboutPage() {
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
            <Link href="/descobrir" className="text-emerald-600 hover:text-emerald-500 text-sm font-medium">
              Descobrir direitos
            </Link>
          </nav>
        </div>
      </header>

      {/* Content */}
      <main className="pt-24 pb-16 px-4">
        <div className="max-w-2xl mx-auto">
          <h1 className="text-3xl font-bold text-[var(--text-primary)] mb-6">
            Sobre o Ta na Mao
          </h1>

          <div className="prose max-w-none">
            <section className="mb-10">
              <h2 className="text-xl font-semibold text-[var(--text-primary)] mb-4">
                O que e?
              </h2>
              <p className="text-[var(--text-secondary)] leading-relaxed">
                O Ta na Mao e uma plataforma gratuita que ajuda brasileiros a descobrirem
                quais beneficios sociais podem ter direito. Em apenas 3 minutos, voce
                responde algumas perguntas simples e nos mostramos todos os programas
                federais, estaduais e setoriais disponiveis para voce.
              </p>
            </section>

            <section className="mb-10">
              <h2 className="text-xl font-semibold text-[var(--text-primary)] mb-4">
                O que NAO fazemos
              </h2>
              <ul className="space-y-2 text-[var(--text-secondary)]">
                <li className="flex items-start gap-2">
                  <span className="text-red-500">✕</span>
                  <span>Nao entregamos beneficios diretamente</span>
                </li>
                <li className="flex items-start gap-2">
                  <span className="text-red-500">✕</span>
                  <span>Nao pedimos sua senha do Gov.br</span>
                </li>
                <li className="flex items-start gap-2">
                  <span className="text-red-500">✕</span>
                  <span>Nao cobramos nada</span>
                </li>
                <li className="flex items-start gap-2">
                  <span className="text-red-500">✕</span>
                  <span>Nao vendemos seus dados</span>
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
                  <span>Analisamos sua situacao com base no que voce nos conta</span>
                </li>
                <li className="flex items-start gap-2">
                  <span className="text-emerald-600">✓</span>
                  <span>Mostramos todos os beneficios que voce pode ter direito</span>
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
                  <div className="text-sm text-[var(--text-tertiary)]">Beneficios federais</div>
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
                Seguranca
              </h2>
              <p className="text-[var(--text-secondary)] leading-relaxed">
                Sua privacidade e importante para nos. As informacoes que voce fornece
                sao usadas apenas para calcular sua elegibilidade e nao sao armazenadas
                em nossos servidores. Voce nao precisa criar conta ou fornecer
                informacoes pessoais identificaveis.
              </p>
            </section>

            <section className="mb-10">
              <h2 className="text-xl font-semibold text-[var(--text-primary)] mb-4">
                Contato
              </h2>
              <p className="text-[var(--text-secondary)] leading-relaxed">
                Se voce encontrou algum erro ou quer sugerir um novo beneficio para
                incluirmos, entre em contato conosco.
              </p>
            </section>
          </div>

          {/* CTA */}
          <div className="mt-12 pt-8 border-t border-[var(--border-color)] text-center">
            <Link
              href="/descobrir"
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
