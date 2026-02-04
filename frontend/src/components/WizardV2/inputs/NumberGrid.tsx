'use client';

/**
 * NumberGrid - Grid of number buttons (0-8+)
 *
 * For selecting quantities like number of people in household
 */

interface Props {
  value: number | undefined;
  onChange: (value: number) => void;
  min?: number;
  max?: number;
  lastLabel?: string; // e.g., "8+" for open-ended
  className?: string;
}

export default function NumberGrid({
  value,
  onChange,
  min = 0,
  max = 8,
  lastLabel,
  className = '',
}: Props) {
  const numbers = Array.from({ length: max - min + 1 }, (_, i) => min + i);

  return (
    <div className={`grid grid-cols-5 gap-2 ${className}`}>
      {numbers.map((num, index) => {
        const isSelected = value === num;
        const isLast = index === numbers.length - 1 && lastLabel;
        const displayLabel = isLast ? lastLabel : num.toString();

        return (
          <button
            key={num}
            type="button"
            onClick={() => onChange(num)}
            className={`
              py-3 px-2 rounded-xl border-2 font-semibold text-lg transition-all
              ${
                isSelected
                  ? 'border-emerald-500 bg-emerald-500 text-white'
                  : 'border-[var(--border-color)] hover:border-emerald-300 bg-[var(--bg-card)] text-[var(--text-primary)]'
              }
            `}
          >
            {displayLabel}
          </button>
        );
      })}
    </div>
  );
}
