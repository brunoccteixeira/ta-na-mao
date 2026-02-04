'use client';

/**
 * WizardProgress - Horizontal progress bar with step indicators
 *
 * Wizbii-style: clean progress bar with percentage
 */

import { useWizard } from './WizardContext';

interface Props {
  className?: string;
}

export default function WizardProgress({ className = '' }: Props) {
  const { progress, visibleSteps, currentStep } = useWizard();

  // Don't show on result step
  if (currentStep.id === 'resultado') {
    return null;
  }

  const currentIndex = visibleSteps.findIndex((s) => s.id === currentStep.id);
  const totalSteps = visibleSteps.filter((s) => s.id !== 'resultado').length;

  return (
    <div className={`w-full ${className}`}>
      {/* Step counter */}
      <div className="flex justify-between items-center mb-2 text-sm">
        <span className="text-[var(--text-secondary)] font-medium">
          {currentStep.shortTitle}
        </span>
        <span className="text-[var(--text-tertiary)]">
          {currentIndex + 1} de {totalSteps}
        </span>
      </div>

      {/* Progress bar */}
      <div className="h-2 bg-[var(--border-color)] rounded-full overflow-hidden">
        <div
          className="h-full bg-emerald-500 transition-all duration-500 ease-out rounded-full"
          style={{ width: `${Math.max(progress, 5)}%` }}
        />
      </div>
    </div>
  );
}
