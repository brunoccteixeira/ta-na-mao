/**
 * Eligibility - Page wrapper for the eligibility wizard
 */

import { Link } from 'react-router-dom';
import EligibilityWizard from '../components/EligibilityWizard';

export default function Eligibility() {
  return (
    <div className="min-h-screen bg-gradient-to-b from-slate-900 via-slate-900 to-slate-950">
      {/* Header */}
      <header className="fixed top-0 left-0 right-0 bg-slate-900/95 backdrop-blur-sm border-b border-slate-800 z-50">
        <div className="max-w-5xl mx-auto px-4 py-4 flex justify-between items-center">
          <Link to="/" className="text-xl font-bold text-emerald-400">
            Tá na Mão
          </Link>
          <Link
            to="/"
            className="text-slate-400 hover:text-white text-sm"
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
