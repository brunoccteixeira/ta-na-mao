'use client';

import Link from 'next/link';
import dynamic from 'next/dynamic';

const EligibilityWizard = dynamic(
  () => import('../../../src/components/EligibilityWizard'),
  { ssr: false }
);

export default function DiscoverPage() {
  return (
    <div className="min-h-screen bg-[var(--bg-primary)]">
      {/* Header */}
      <header className="fixed top-0 left-0 right-0 bg-[var(--bg-header)] backdrop-blur-sm border-b border-[var(--border-color)] z-50">
        <div className="max-w-5xl mx-auto px-4 py-4 flex justify-between items-center">
          <Link href="/" className="text-xl font-bold text-emerald-600">
            Ta na Mao
          </Link>
          <Link
            href="/"
            className="text-[var(--text-tertiary)] hover:text-[var(--text-primary)] text-sm"
          >
            ← Voltar
          </Link>
        </div>
      </header>

      {/* Content */}
      <main className="pt-24 pb-16 px-4">
        <EligibilityWizard />
      </main>
    </div>
  );
}
