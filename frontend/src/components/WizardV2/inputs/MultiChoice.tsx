'use client';

/**
 * MultiChoice - Checkboxes in grid layout
 *
 * For selecting multiple options at once
 */

import { ReactNode } from 'react';
import { Check } from 'lucide-react';

export interface MultiChoiceOption {
  value: string;
  label: string;
  description?: string;
  icon?: ReactNode;
}

interface Props {
  options: MultiChoiceOption[];
  values: string[];
  onChange: (values: string[]) => void;
  columns?: 1 | 2;
  className?: string;
}

export default function MultiChoice({
  options,
  values,
  onChange,
  columns = 1,
  className = '',
}: Props) {
  const toggleOption = (optionValue: string) => {
    if (values.includes(optionValue)) {
      onChange(values.filter((v) => v !== optionValue));
    } else {
      onChange([...values, optionValue]);
    }
  };

  const gridCols = columns === 1 ? 'grid-cols-1' : 'grid-cols-2';

  return (
    <div className={`grid gap-3 ${gridCols} ${className}`}>
      {options.map((option) => {
        const isSelected = values.includes(option.value);

        return (
          <button
            key={option.value}
            type="button"
            onClick={() => toggleOption(option.value)}
            className={`
              flex items-center gap-3 py-3.5 px-4 rounded-xl border-2 transition-all text-left
              ${
                isSelected
                  ? 'border-emerald-500 bg-emerald-50 dark:bg-emerald-500/10'
                  : 'border-[var(--border-color)] hover:border-emerald-300 bg-[var(--bg-card)]'
              }
            `}
          >
            {/* Checkbox */}
            <div
              className={`
                w-5 h-5 rounded flex-shrink-0 flex items-center justify-center border-2 transition-all
                ${
                  isSelected
                    ? 'bg-emerald-500 border-emerald-500'
                    : 'border-[var(--border-color)] bg-[var(--bg-card)]'
                }
              `}
            >
              {isSelected && <Check className="w-3 h-3 text-white" />}
            </div>

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
          </button>
        );
      })}
    </div>
  );
}
