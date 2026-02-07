'use client';

/**
 * WizardLayout - Split-screen layout inspired by Wizbii Money
 *
 * Desktop: Left sidebar with value prop + Right form area
 * Mobile: Stacked layout with condensed header
 */

import { ReactNode } from 'react';
import { useWizard } from './WizardContext';
import WizardProgress from './WizardProgress';
import { Gift, Clock, Shield, ChevronLeft } from 'lucide-react';

interface Props {
  children: ReactNode;
}

export default function WizardLayout({ children }: Props) {
  const { isResultStep, prevStep, isFirstStep } = useWizard();

  // Result page has a different layout
  if (isResultStep) {
    return (
      <div className="min-h-screen bg-[var(--bg-primary)]">
        {children}
      </div>
    );
  }

  return (
    <div className="min-h-screen bg-[var(--bg-primary)]">
      {/* Mobile Header */}
      <div className="lg:hidden">
        <div className="px-4 pt-4 pb-2">
          <WizardProgress />
        </div>

        {/* Value prop banner (mobile) */}
        <div className="px-4 py-4 bg-gradient-to-r from-emerald-600 to-emerald-500 mx-4 rounded-xl mb-4">
          <div className="flex items-center gap-3 text-white">
            <div className="w-10 h-10 bg-white/20 rounded-full flex items-center justify-center flex-shrink-0">
              <Gift className="w-5 h-5" />
            </div>
            <div>
              <p className="text-sm opacity-90">5 minutos para descobrir</p>
              <p className="text-lg font-bold">+1.300 benefícios</p>
            </div>
          </div>
        </div>
      </div>

      {/* Desktop Split Layout */}
      <div className="lg:flex lg:min-h-screen">
        {/* Left Sidebar (desktop only) */}
        <div className="hidden lg:flex lg:w-[400px] lg:flex-shrink-0 bg-gradient-to-br from-emerald-600 to-emerald-700 text-white p-8 flex-col">
          <div className="flex-1 flex flex-col justify-center max-w-sm mx-auto">
            {/* Main value prop */}
            <div className="mb-12">
              <p className="text-emerald-200 text-lg mb-2">Em apenas</p>
              <h2 className="text-5xl font-bold mb-4">5 minutos</h2>
              <p className="text-xl text-emerald-100">
                descubra todos os benefícios que você pode receber
              </p>
            </div>

            {/* Stats */}
            <div className="space-y-6">
              <StatItem
                icon={<Gift className="w-6 h-6" />}
                value="+1.300"
                label="benefícios mapeados"
              />
              <StatItem
                icon={<Clock className="w-6 h-6" />}
                value="20"
                label="perguntas simples"
              />
              <StatItem
                icon={<Shield className="w-6 h-6" />}
                value="100%"
                label="gratuito e seguro"
              />
            </div>

            {/* Trust badges */}
            <div className="mt-12 pt-8 border-t border-emerald-500/30">
              <p className="text-emerald-200 text-sm mb-3">Seus dados estão seguros</p>
              <p className="text-emerald-100/70 text-xs">
                Não armazenamos CPF ou dados sensíveis. A análise é feita localmente no seu dispositivo.
              </p>
            </div>
          </div>
        </div>

        {/* Right Content Area */}
        <div className="flex-1 flex flex-col">
          {/* Desktop Progress */}
          <div className="hidden lg:block px-8 pt-8">
            <WizardProgress />
          </div>

          {/* Form Area */}
          <div className="flex-1 flex flex-col justify-center px-4 py-6 lg:px-8 lg:py-12">
            <div className="w-full max-w-xl mx-auto">
              {/* Back button (mobile) */}
              {!isFirstStep && (
                <button
                  onClick={prevStep}
                  className="lg:hidden flex items-center gap-1 text-[var(--text-tertiary)] hover:text-[var(--text-primary)] mb-4 -ml-1"
                >
                  <ChevronLeft className="w-5 h-5" />
                  <span className="text-sm">Voltar</span>
                </button>
              )}

              {/* Step content */}
              <div className="bg-[var(--bg-card)] rounded-2xl p-6 lg:p-8 border border-[var(--border-color)] shadow-sm">
                {children}
              </div>
            </div>
          </div>

          {/* Desktop Back Button */}
          {!isFirstStep && (
            <div className="hidden lg:block px-8 pb-8">
              <button
                onClick={prevStep}
                className="flex items-center gap-1 text-[var(--text-tertiary)] hover:text-[var(--text-primary)]"
              >
                <ChevronLeft className="w-5 h-5" />
                <span className="text-sm">Voltar</span>
              </button>
            </div>
          )}
        </div>
      </div>
    </div>
  );
}

// Stat item component for sidebar
function StatItem({
  icon,
  value,
  label,
}: {
  icon: ReactNode;
  value: string;
  label: string;
}) {
  return (
    <div className="flex items-center gap-4">
      <div className="w-12 h-12 bg-white/10 rounded-xl flex items-center justify-center flex-shrink-0">
        {icon}
      </div>
      <div>
        <p className="text-2xl font-bold">{value}</p>
        <p className="text-emerald-200 text-sm">{label}</p>
      </div>
    </div>
  );
}
