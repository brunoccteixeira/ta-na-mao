'use client';

import Link from 'next/link';
import dynamic from 'next/dynamic';

// WizardV2 - New Wizbii-style eligibility wizard
const WizardV2 = dynamic(
  () => import('../../../src/components/WizardV2'),
  { ssr: false }
);

export default function DiscoverPage() {
  return (
    <div className="theme-light">
      {/* Header */}
      <header className="fixed top-0 left-0 right-0 bg-[var(--bg-header)] backdrop-blur-sm border-b border-[var(--border-color)] z-50">
        <div className="max-w-5xl mx-auto px-4 py-3 flex justify-between items-center">
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

      {/* Wizard Content - Full height, handles its own padding */}
      <main className="pt-14">
        <WizardV2 />
      </main>
    </div>
  );
}
