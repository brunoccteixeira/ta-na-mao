'use client';

/**
 * NumberGrid - Grid of number buttons (0-8+)
 *
 * For selecting quantities like number of people in household.
 * When lastLabel (e.g. "8+") is selected, shows a text input for exact value.
 */

import { useState, useRef, useEffect } from 'react';

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
  const [showCustomInput, setShowCustomInput] = useState(
    lastLabel ? (value !== undefined && value > max) : false
  );
  const [customValue, setCustomValue] = useState(
    value !== undefined && value > max ? value.toString() : ''
  );
  const inputRef = useRef<HTMLInputElement>(null);

  useEffect(() => {
    if (showCustomInput && inputRef.current) {
      inputRef.current.focus();
    }
  }, [showCustomInput]);

  const handleLastClick = () => {
    setShowCustomInput(true);
    setCustomValue('');
    onChange(max);
  };

  const handleCustomChange = (e: React.ChangeEvent<HTMLInputElement>) => {
    const raw = e.target.value.replace(/\D/g, '');
    setCustomValue(raw);
    const num = parseInt(raw, 10);
    if (num >= max) {
      onChange(num);
    }
  };

  const isCustomActive = lastLabel && (showCustomInput || (value !== undefined && value > max));

  return (
    <div className={className}>
      <div className="grid grid-cols-5 gap-2">
        {numbers.map((num, index) => {
          const isLast = index === numbers.length - 1 && lastLabel;
          const isSelected = isLast
            ? isCustomActive
            : value === num && !isCustomActive;
          const displayLabel = isLast ? lastLabel : num.toString();

          return (
            <button
              key={num}
              type="button"
              onClick={() => {
                if (isLast) {
                  handleLastClick();
                } else {
                  setShowCustomInput(false);
                  setCustomValue('');
                  onChange(num);
                }
              }}
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

      {/* Custom input for exact value when N+ is selected */}
      {isCustomActive && (
        <div className="mt-3 animate-fadeIn">
          <label className="block text-xs text-[var(--text-tertiary)] mb-1.5">
            Informe o número exato:
          </label>
          <input
            ref={inputRef}
            type="text"
            inputMode="numeric"
            value={customValue}
            onChange={handleCustomChange}
            placeholder={`${max} ou mais`}
            className="
              w-32 py-2 px-3 text-lg font-semibold text-[var(--text-primary)]
              bg-[var(--input-bg)] border-2 border-emerald-500 rounded-xl
              focus:outline-none transition-colors
            "
          />
        </div>
      )}
    </div>
  );
}
