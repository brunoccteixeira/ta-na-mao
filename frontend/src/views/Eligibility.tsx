/**
 * Eligibility - Page wrapper for the eligibility wizard
 */

import { Link } from 'react-router-dom';
import EligibilityWizard from '../components/EligibilityWizard';

export default function Eligibility() {
  return (
    <div className="min-h-screen bg-[var(--bg-primary)]">
      {/* Header */}
      <header className="fixed top-0 left-0 right-0 bg-[var(--bg-header)] backdrop-blur-sm border-b border-[var(--border-color)] z-50">
        <div className="max-w-5xl mx-auto px-4 py-4 flex justify-between items-center">
          <Link to="/" className="text-xl font-bold text-emerald-600">
            Tá na Mão
          </Link>
          <Link
            to="/"
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
