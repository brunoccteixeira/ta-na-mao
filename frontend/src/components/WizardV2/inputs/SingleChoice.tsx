'use client';

/**
 * SingleChoice - Pills/buttons for single selection
 *
 * Wizbii-style: large touch targets, clear selection state
 */

import { ReactNode } from 'react';
import { Check } from 'lucide-react';

export interface SingleChoiceOption {
  value: string;
  label: string;
  description?: string;
  icon?: ReactNode;
}

interface Props {
  options: SingleChoiceOption[];
  value: string | undefined;
  onChange: (value: string) => void;
  columns?: 1 | 2 | 3;
  size?: 'sm' | 'md' | 'lg';
  className?: string;
}

export default function SingleChoice({
  options,
  value,
  onChange,
  columns = 2,
  size = 'md',
  className = '',
}: Props) {
  const gridCols = {
    1: 'grid-cols-1',
    2: 'grid-cols-2',
    3: 'grid-cols-3',
  };

  const sizes = {
    sm: 'py-2.5 px-3 text-sm',
    md: 'py-3.5 px-4 text-base',
    lg: 'py-4 px-5 text-lg',
  };

  return (
    <div className={`grid gap-3 ${gridCols[columns]} ${className}`}>
      {options.map((option) => {
        const isSelected = value === option.value;

        return (
          <button
            key={option.value}
            type="button"
            onClick={() => onChange(option.value)}
            className={`
              relative flex items-center gap-3 ${sizes[size]} rounded-xl border-2 transition-all text-left
              ${
                isSelected
                  ? 'border-emerald-500 bg-emerald-50 dark:bg-emerald-500/10'
                  : 'border-[var(--border-color)] hover:border-emerald-300 hover:shadow-sm active:scale-[0.98] bg-[var(--bg-card)]'
              }
            `}
          >
            {/* Icon (if provided) */}
            {option.icon && (
              <span className={`flex-shrink-0 ${isSelected ? 'text-emerald-600' : 'text-[var(--text-tertiary)]'}`}>
                {option.icon}
              </span>
            )}

            {/* Label */}
            <div className="flex-1 min-w-0">
              <span
                className={`block font-medium ${
                  isSelected ? 'text-emerald-700 dark:text-emerald-400' : 'text-[var(--text-primary)]'
                }`}
              >
                {option.label}
              </span>
              {option.description && (
                <span className="block text-xs text-[var(--text-tertiary)] mt-0.5">
                  {option.description}
                </span>
              )}
            </div>

            {/* Check indicator */}
            {isSelected && (
              <div className="absolute top-2 right-2 w-5 h-5 bg-emerald-500 rounded-full flex items-center justify-center">
                <Check className="w-3 h-3 text-white" />
              </div>
            )}
          </button>
        );
      })}
    </div>
  );
}
