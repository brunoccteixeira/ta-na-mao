'use client';

import Link from 'next/link';
import { useRouter } from 'next/navigation';
import { useBenefitDetail } from '../../../../../src/hooks/useBenefitsAPI';
import JourneyFlow from '../../../../../src/components/Journey/JourneyFlow';
import type { Journey } from '../../../../../src/components/Journey/JourneyFlow';
import journeysData from '../../../../../src/data/journeys.json';

export default function JourneyClient({ id }: { id: string }) {
  const router = useRouter();
  const { data: benefit, isLoading, isError, error } = useBenefitDetail(id);

  const journey = (journeysData.journeys as Journey[]).find((j) => j.benefitId === id) || null;

  if (isLoading) {
    return (
      <div className="min-h-screen bg-[var(--bg-primary)] flex items-center justify-center">
        <div className="flex items-center gap-3 text-[var(--text-tertiary)]">
          <div className="w-5 h-5 border-2 border-emerald-500 border-t-transparent rounded-full animate-spin" />
          <span>Carregando jornada...</span>
        </div>
      </div>
    );
  }

  if (isError || !benefit) {
    return (
      <div className="min-h-screen bg-[var(--bg-primary)] flex items-center justify-center">
        <div className="text-center">
          <p className="text-[var(--text-tertiary)] mb-4">
            {error instanceof Error ? error.message : 'Beneficio nao encontrado'}
          </p>
          <Link href="/beneficios" className="text-emerald-600 hover:text-emerald-500">
            ← Voltar ao catalogo
          </Link>
        </div>
      </div>
    );
  }

  if (!journey) {
    return (
      <div className="min-h-screen bg-[var(--bg-primary)] flex items-center justify-center">
        <div className="text-center">
          <p className="text-4xl mb-4">🗺️</p>
          <p className="text-[var(--text-secondary)] mb-2 font-medium">
            Jornada ainda nao mapeada
          </p>
          <p className="text-sm text-[var(--text-tertiary)] mb-6">
            Estamos preparando o passo a passo para o {benefit.name}
          </p>
          <Link
            href={`/beneficios/${benefit.id}`}
            className="text-emerald-600 hover:text-emerald-500"
          >
            ← Voltar para o beneficio
          </Link>
        </div>
      </div>
    );
  }

  return (
    <div className="min-h-screen bg-[var(--bg-primary)]">
      {/* Header */}
      <header className="fixed top-0 left-0 right-0 bg-[var(--bg-header)] backdrop-blur-sm border-b border-[var(--border-color)] z-50">
        <div className="max-w-5xl mx-auto px-4 py-4 flex justify-between items-center">
          <Link href="/" className="text-xl font-bold text-emerald-600">
            Ta na Mao
          </Link>
          <button
            onClick={() => router.back()}
            className="text-[var(--text-tertiary)] hover:text-[var(--text-primary)] text-sm"
          >
            ← Voltar
          </button>
        </div>
      </header>

      {/* Content */}
      <main className="pt-24 pb-16 px-4">
        <div className="max-w-2xl mx-auto">
          {/* Benefit name */}
          <div className="mb-6">
            <Link
              href={`/beneficios/${benefit.id}`}
              className="text-sm text-emerald-600 hover:text-emerald-500"
            >
              ← {benefit.name}
            </Link>
            <h1 className="text-2xl font-bold text-[var(--text-primary)] mt-2">
              🗺️ Como conseguir
            </h1>
          </div>

          <JourneyFlow journey={journey} />

          {/* Bottom CTA */}
          <div className="mt-10 pt-6 border-t border-[var(--border-color)] space-y-3">
            <Link
              href={`/beneficios/${benefit.id}/verificar`}
              className="block w-full py-4 bg-emerald-600 hover:bg-emerald-500 text-white font-semibold text-center rounded-xl transition-colors"
            >
              Verificar se tenho direito
            </Link>
            <Link
              href={`/beneficios/${benefit.id}`}
              className="block w-full py-3 bg-[var(--badge-bg)] hover:bg-[var(--hover-bg)] text-[var(--text-secondary)] font-medium text-center rounded-xl transition-colors text-sm"
            >
              Voltar para detalhes do beneficio
            </Link>
          </div>
        </div>
      </main>
    </div>
  );
}
