'use client';

/**
 * WizardLayout - Compact centered layout with step transitions
 *
 * Desktop: emerald header bar (logo + dots + counter) + centered max-w-xl card
 * Mobile: progress dots + compact banner + content
 */

import { ReactNode } from 'react';
import { useWizard } from './WizardContext';
import WizardProgress from './WizardProgress';
import { Gift, ChevronLeft } from 'lucide-react';

interface Props {
  children: ReactNode;
}

export default function WizardLayout({ children }: Props) {
  const { isResultStep, prevStep, isFirstStep, currentStep, direction } = useWizard();

  // Result page has its own layout
  if (isResultStep) {
    return (
      <div className="min-h-screen bg-[var(--bg-primary)]">
        {children}
      </div>
    );
  }

  const animationClass = direction === 'forward' ? 'step-forward' : 'step-back';

  return (
    <div className="min-h-screen bg-[var(--bg-primary)] flex flex-col">
      {/* Desktop Header Bar */}
      <div className="hidden lg:block bg-gradient-to-r from-emerald-600 to-emerald-500">
        <div className="max-w-3xl mx-auto px-6 py-4 flex items-center justify-between">
          {/* Left: logo + tagline */}
          <div className="flex items-center gap-3">
            <div className="w-8 h-8 bg-white/20 rounded-lg flex items-center justify-center flex-shrink-0">
              <Gift className="w-4 h-4 text-white" />
            </div>
            <div className="text-white">
              <p className="text-sm font-semibold leading-none">Descubra seus benefícios</p>
              <p className="text-xs text-emerald-100 mt-0.5">5 min &bull; +1.300 programas &bull; 100% gratuito</p>
            </div>
          </div>

          {/* Right: step dots */}
          <WizardProgress className="text-white [&_span]:text-emerald-100" />
        </div>
      </div>

      {/* Mobile: progress + banner */}
      <div className="lg:hidden">
        <div className="px-4 pt-4 pb-2">
          <WizardProgress />
        </div>

        {/* Compact value prop banner */}
        <div className="px-4 pb-3">
          <div className="flex items-center gap-3 px-4 py-3 bg-gradient-to-r from-emerald-600 to-emerald-500 rounded-xl text-white">
            <Gift className="w-5 h-5 flex-shrink-0" />
            <div className="flex items-center gap-2 text-sm">
              <span className="font-semibold">5 min</span>
              <span className="text-emerald-200">&bull;</span>
              <span>+1.300 benefícios</span>
              <span className="text-emerald-200">&bull;</span>
              <span>Gratuito</span>
            </div>
          </div>
        </div>
      </div>

      {/* Content Area */}
      <div className="flex-1 flex flex-col justify-center px-4 py-6 lg:px-8 lg:py-12">
        <div className="w-full max-w-xl mx-auto">
          {/* Back button */}
          {!isFirstStep && (
            <button
              onClick={prevStep}
              className="flex items-center gap-1 text-[var(--text-tertiary)] hover:text-[var(--text-primary)] mb-4 -ml-1 transition-colors"
            >
              <ChevronLeft className="w-5 h-5" />
              <span className="text-sm">Voltar</span>
            </button>
          )}

          {/* Step content with transition */}
          <div
            key={currentStep.id}
            className={`bg-[var(--bg-card)] rounded-2xl p-6 lg:p-8 border border-[var(--border-color)] shadow-sm ${animationClass}`}
          >
            {children}
          </div>
        </div>
      </div>
    </div>
  );
}
