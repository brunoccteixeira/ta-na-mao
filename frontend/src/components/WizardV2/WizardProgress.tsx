'use client';

/**
 * WizardProgress - Step dots with counter
 *
 * Dots: completed = emerald filled, current = emerald + ring, future = gray
 */

import { useWizard } from './WizardContext';

interface Props {
  className?: string;
}

export default function WizardProgress({ className = '' }: Props) {
  const { visibleSteps, currentStep } = useWizard();

  if (currentStep.id === 'resultado') {
    return null;
  }

  const stepsWithoutResult = visibleSteps.filter((s) => s.id !== 'resultado');
  const currentIndex = stepsWithoutResult.findIndex((s) => s.id === currentStep.id);
  const totalSteps = stepsWithoutResult.length;

  return (
    <div className={`flex items-center gap-3 ${className}`}>
      {/* Step dots */}
      <div className="flex items-center gap-1.5">
        {stepsWithoutResult.map((step, i) => {
          const isCompleted = i < currentIndex;
          const isCurrent = i === currentIndex;

          return (
            <div
              key={step.id}
              className={`
                rounded-full transition-all duration-300
                ${isCurrent ? 'w-2.5 h-2.5 bg-emerald-500 ring-2 ring-emerald-500/30' : ''}
                ${isCompleted ? 'w-2 h-2 bg-emerald-500' : ''}
                ${!isCurrent && !isCompleted ? 'w-2 h-2 bg-gray-300' : ''}
              `}
            />
          );
        })}
      </div>

      {/* Counter */}
      <span className="text-sm text-[var(--text-tertiary)] whitespace-nowrap">
        {currentIndex + 1} de {totalSteps}
      </span>
    </div>
  );
}
