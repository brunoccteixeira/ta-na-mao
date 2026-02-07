'use client';

import { useState, useEffect, useCallback, useRef } from 'react';
import Link from 'next/link';
import { useRouter } from 'next/navigation';
import { useBenefitDetail } from '../../../../../src/hooks/useBenefitsAPI';
import { getDocumentHint } from '../../../../../src/utils/documentHints';

// --- localStorage persistence ---

const STORAGE_KEY = 'tnm-doc-checklist';

function loadChecked(benefitId: string): boolean[] {
  if (typeof window === 'undefined') return [];
  try {
    const raw = localStorage.getItem(STORAGE_KEY);
    if (!raw) return [];
    const all = JSON.parse(raw) as Record<string, boolean[]>;
    return all[benefitId] || [];
  } catch {
    return [];
  }
}

function saveChecked(benefitId: string, checked: boolean[]) {
  if (typeof window === 'undefined') return;
  try {
    const raw = localStorage.getItem(STORAGE_KEY);
    const all = raw ? (JSON.parse(raw) as Record<string, boolean[]>) : {};
    all[benefitId] = checked;
    localStorage.setItem(STORAGE_KEY, JSON.stringify(all));
  } catch {
    // localStorage may be disabled
  }
}

// --- Component ---

export default function DocumentsClient({ id }: { id: string }) {
  const router = useRouter();
  const { data: benefit, isLoading, isError, error } = useBenefitDetail(id);
  const [checked, setChecked] = useState<boolean[]>([]);
  const progressRef = useRef<HTMLSpanElement>(null);

  // Load saved state
  useEffect(() => {
    setChecked(loadChecked(id));
  }, [id]);

  const toggle = useCallback(
    (idx: number) => {
      setChecked((prev) => {
        const next = [...prev];
        next[idx] = !next[idx];
        saveChecked(id, next);
        return next;
      });
    },
    [id]
  );

  // --- Loading ---
  if (isLoading) {
    return (
      <div className="min-h-screen bg-[var(--bg-primary)] flex items-center justify-center">
        <div className="flex items-center gap-3 text-[var(--text-tertiary)]">
          <div className="w-5 h-5 border-2 border-emerald-500 border-t-transparent rounded-full animate-spin" />
          <span>Carregando documentos...</span>
        </div>
      </div>
    );
  }

  // --- Error ---
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

  const docs = benefit.documentsRequired;
  const checkedCount = checked.filter(Boolean).length;
  const total = docs.length;
  const allDone = total > 0 && checkedCount === total;
  const progressPct = total > 0 ? (checkedCount / total) * 100 : 0;

  return (
    <div className="min-h-screen bg-[var(--bg-primary)]">
      {/* Header — hidden on print */}
      <header className="fixed top-0 left-0 right-0 bg-[var(--bg-header)] backdrop-blur-sm border-b border-[var(--border-color)] z-50 print:hidden">
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

      {/* Print-only header */}
      <div className="hidden print:block mb-6 pb-4 border-b-2 border-black">
        <p className="text-lg font-bold">Ta na Mao - Lista de Documentos</p>
        <p className="text-sm">{benefit.name}</p>
        <p className="text-xs text-gray-600">
          Impresso em {new Date().toLocaleDateString('pt-BR')}
        </p>
      </div>

      {/* Content */}
      <main className="pt-24 pb-16 px-4 print:pt-0 print:pb-0">
        <div className="max-w-2xl mx-auto">
          {/* Breadcrumb */}
          <div className="mb-6 print:hidden">
            <Link
              href={`/beneficios/${benefit.id}`}
              className="text-sm text-emerald-600 hover:text-emerald-500"
            >
              ← {benefit.name}
            </Link>
            <h1 className="text-2xl font-bold text-[var(--text-primary)] mt-2 flex items-center gap-2">
              <span>📄</span> Documentos necessarios
            </h1>
          </div>

          {/* Progress bar — hidden on print */}
          <div className="mb-6 print:hidden">
            <div className="flex items-center gap-3">
              <div className="flex-1 h-2 rounded-full bg-[var(--border-color)] overflow-hidden">
                <div
                  className="h-full bg-emerald-500 rounded-full transition-all duration-500"
                  style={{ width: `${progressPct}%` }}
                />
              </div>
              <span
                ref={progressRef}
                className="text-sm font-medium text-[var(--text-secondary)]"
                aria-live="polite"
              >
                {checkedCount}/{total}
              </span>
            </div>
            {checkedCount > 0 && !allDone && (
              <p className="text-xs text-[var(--text-tertiary)] mt-1">
                Faltam {total - checkedCount} documento{total - checkedCount !== 1 ? 's' : ''}
              </p>
            )}
          </div>

          {/* Celebration banner */}
          {allDone && (
            <div className="mb-6 p-4 rounded-xl bg-emerald-500/15 border border-emerald-500/30 print:hidden">
              <div className="flex items-center gap-3">
                <span className="text-2xl">🎉</span>
                <div>
                  <p className="font-semibold text-emerald-700">Tudo pronto!</p>
                  <p className="text-sm text-emerald-600/70">
                    Agora e so levar ao {benefit.whereToApply || 'posto de atendimento'}.
                  </p>
                </div>
              </div>
            </div>
          )}

          {/* Document checklist */}
          <div className="space-y-3">
            {docs.map((doc, idx) => {
              const isChecked = checked[idx] || false;
              const hint = getDocumentHint(doc);
              const inputId = `doc-${idx}`;

              return (
                <label
                  key={idx}
                  htmlFor={inputId}
                  className={`block p-4 rounded-xl border cursor-pointer transition-colors focus-within:ring-2 focus-within:ring-emerald-500 ${
                    isChecked
                      ? 'bg-emerald-500/10 border-emerald-500/30'
                      : 'bg-[var(--bg-card)] border-[var(--border-color)] hover:bg-[var(--hover-bg)]'
                  } print:bg-white print:border-black print:p-3`}
                >
                  <div className="flex items-start gap-3">
                    {/* Custom checkbox visual */}
                    <div
                      className={`w-6 h-6 rounded-md border-2 flex items-center justify-center flex-shrink-0 mt-0.5 transition-colors ${
                        isChecked
                          ? 'bg-emerald-500 border-emerald-500'
                          : 'border-gray-300 print:border-black'
                      }`}
                    >
                      {isChecked && (
                        <svg className="w-4 h-4 text-white print:text-black" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                          <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={3} d="M5 13l4 4L19 7" />
                        </svg>
                      )}
                    </div>

                    <input
                      id={inputId}
                      type="checkbox"
                      checked={isChecked}
                      onChange={() => toggle(idx)}
                      className="sr-only"
                    />

                    <div className="flex-1 min-w-0">
                      <span
                        className={`text-[var(--text-primary)] print:text-black ${
                          isChecked ? 'line-through text-[var(--text-tertiary)]' : ''
                        }`}
                      >
                        {doc}
                      </span>
                      {hint && (
                        <p className="text-xs text-[var(--text-tertiary)] mt-1 print:text-gray-600">
                          💡 {hint}
                        </p>
                      )}
                    </div>
                  </div>
                </label>
              );
            })}
          </div>

          {/* Onde levar */}
          {benefit.whereToApply && (
            <section className="mt-8 print:mt-6">
              <h2 className="text-lg font-semibold text-[var(--text-primary)] mb-3 flex items-center gap-2 print:text-black">
                <span>📍</span> Onde levar esses documentos
              </h2>
              <div className="p-4 rounded-xl bg-[var(--bg-card)] border border-[var(--border-color)] print:bg-white print:border-black print:p-3">
                <p className="text-[var(--text-secondary)] print:text-black">
                  {benefit.whereToApply}
                </p>
              </div>
            </section>
          )}

          {/* Print button — hidden on print */}
          <div className="mt-8 print:hidden">
            <button
              onClick={() => window.print()}
              className="w-full py-3 bg-[var(--bg-card)] border border-[var(--border-color)] hover:bg-[var(--hover-bg)] text-[var(--text-secondary)] font-medium rounded-xl transition-colors text-sm flex items-center justify-center gap-2"
            >
              <svg className="w-4 h-4" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M17 17h2a2 2 0 002-2v-4a2 2 0 00-2-2H5a2 2 0 00-2 2v4a2 2 0 002 2h2m2 4h6a2 2 0 002-2v-4a2 2 0 00-2-2H9a2 2 0 00-2 2v4a2 2 0 002 2zm8-12V5a2 2 0 00-2-2H9a2 2 0 00-2 2v4h10z" />
              </svg>
              Imprimir lista
            </button>
          </div>

          {/* Bottom CTAs — hidden on print */}
          <div className="mt-6 pt-6 border-t border-[var(--border-color)] space-y-3 print:hidden">
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
