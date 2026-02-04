'use client';

/**
 * YesNo - Toggle for yes/no questions
 *
 * Can include "Não sei" option for uncertain answers
 */

import { Check, X, HelpCircle } from 'lucide-react';

interface Props {
  value: boolean | undefined | null; // null = "não sei"
  onChange: (value: boolean | null) => void;
  showUnsure?: boolean;
  yesLabel?: string;
  noLabel?: string;
  unsureLabel?: string;
  className?: string;
}

export default function YesNo({
  value,
  onChange,
  showUnsure = false,
  yesLabel = 'Sim',
  noLabel = 'Não',
  unsureLabel = 'Não sei',
  className = '',
}: Props) {
  const options = [
    {
      key: 'yes',
      label: yesLabel,
      icon: <Check className="w-5 h-5" />,
      value: true,
      color: 'emerald',
    },
    {
      key: 'no',
      label: noLabel,
      icon: <X className="w-5 h-5" />,
      value: false,
      color: 'slate',
    },
    ...(showUnsure
      ? [
          {
            key: 'unsure',
            label: unsureLabel,
            icon: <HelpCircle className="w-5 h-5" />,
            value: null as boolean | null,
            color: 'amber',
          },
        ]
      : []),
  ];

  return (
    <div className={`flex gap-3 ${className}`}>
      {options.map((option) => {
        const isSelected = value === option.value;

        const selectedStyles = {
          emerald: 'border-emerald-500 bg-emerald-50 dark:bg-emerald-500/10 text-emerald-700 dark:text-emerald-400',
          slate: 'border-slate-400 bg-slate-50 dark:bg-slate-500/10 text-slate-700 dark:text-slate-300',
          amber: 'border-amber-500 bg-amber-50 dark:bg-amber-500/10 text-amber-700 dark:text-amber-400',
        };

        const iconStyles = {
          emerald: 'text-emerald-600',
          slate: 'text-slate-500',
          amber: 'text-amber-600',
        };

        return (
          <button
            key={option.key}
            type="button"
            onClick={() => onChange(option.value)}
            className={`
              flex-1 flex items-center justify-center gap-2 py-4 px-4 rounded-xl border-2 font-medium transition-all
              ${
                isSelected
                  ? selectedStyles[option.color as keyof typeof selectedStyles]
                  : 'border-[var(--border-color)] hover:border-emerald-300 bg-[var(--bg-card)] text-[var(--text-primary)]'
              }
            `}
          >
            <span className={isSelected ? iconStyles[option.color as keyof typeof iconStyles] : 'text-[var(--text-tertiary)]'}>
              {option.icon}
            </span>
            <span>{option.label}</span>
          </button>
        );
      })}
    </div>
  );
}
