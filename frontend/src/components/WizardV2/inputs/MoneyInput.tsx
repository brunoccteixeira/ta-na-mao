'use client';

/**
 * MoneyInput - Currency input with R$ prefix
 *
 * Formats as user types and handles edge cases
 */

import { useState, useEffect, useRef } from 'react';

interface Props {
  value: number | undefined;
  onChange: (value: number) => void;
  placeholder?: string;
  className?: string;
  presets?: number[];
}

export default function MoneyInput({
  value,
  onChange,
  placeholder = '0',
  className = '',
  presets,
}: Props) {
  const [displayValue, setDisplayValue] = useState('');
  const [showMaxWarning, setShowMaxWarning] = useState(false);
  const inputRef = useRef<HTMLInputElement>(null);

  // Sync display value with prop
  useEffect(() => {
    if (value !== undefined && value > 0) {
      setDisplayValue(formatNumber(value));
    } else {
      setDisplayValue('');
    }
  }, [value]);

  const formatNumber = (num: number): string => {
    return num.toLocaleString('pt-BR');
  };

  const parseNumber = (str: string): number => {
    // Remove all non-digits
    const digits = str.replace(/\D/g, '');
    return parseInt(digits, 10) || 0;
  };

  const handleChange = (e: React.ChangeEvent<HTMLInputElement>) => {
    const raw = e.target.value;
    const num = parseNumber(raw);

    // Limit to reasonable max (R$ 999.999)
    if (num > 999999) {
      setShowMaxWarning(true);
      return;
    }

    setShowMaxWarning(false);
    setDisplayValue(num > 0 ? formatNumber(num) : '');
    onChange(num);
  };

  const handlePreset = (preset: number) => {
    setDisplayValue(formatNumber(preset));
    onChange(preset);
    inputRef.current?.focus();
  };

  return (
    <div className={className}>
      {/* Main input */}
      <div className="relative">
        <span className="absolute left-4 top-1/2 -translate-y-1/2 text-[var(--text-tertiary)] font-medium text-lg">
          R$
        </span>
        <input
          ref={inputRef}
          type="text"
          inputMode="numeric"
          value={displayValue}
          onChange={handleChange}
          placeholder={placeholder}
          className="
            w-full py-4 pl-12 pr-4 text-2xl font-semibold text-[var(--text-primary)]
            bg-[var(--input-bg)] border-2 border-[var(--input-border)] rounded-xl
            focus:border-emerald-500 focus:outline-none transition-colors
            placeholder:text-[var(--text-tertiary)] placeholder:font-normal
          "
        />
      </div>

      {/* Max value warning */}
      {showMaxWarning && (
        <p className="mt-1 text-xs text-amber-600">Valor máximo: R$ 999.999</p>
      )}

      {/* Quick presets */}
      {presets && presets.length > 0 && (
        <div className="mt-3">
          <p className="text-xs text-[var(--text-tertiary)] mb-2">Selecione uma faixa:</p>
          <div className="flex flex-wrap gap-2">
            {presets.map((preset) => {
              const isSelected = value === preset;
              return (
                <button
                  key={preset}
                  type="button"
                  onClick={() => handlePreset(preset)}
                  className={`
                    py-2 px-3 rounded-lg text-sm font-medium transition-all
                    ${
                      isSelected
                        ? 'bg-emerald-500 text-white'
                        : 'bg-[var(--badge-bg)] text-[var(--text-secondary)] hover:bg-emerald-100 hover:text-emerald-700'
                    }
                  `}
                >
                  R$ {formatNumber(preset)}
                </button>
              );
            })}
          </div>
        </div>
      )}

      {/* Helper text */}
      {value !== undefined && value > 0 && (
        <p className="mt-2 text-sm text-[var(--text-tertiary)]">
          {value <= 300 && 'Renda muito baixa - você pode ter direito a vários benefícios'}
          {value > 300 && value <= 1000 && 'Renda baixa - verifique benefícios disponíveis'}
          {value > 1000 && value <= 3000 && 'Alguns benefícios podem estar disponíveis'}
          {value > 3000 && 'Benefícios como MCMV podem estar disponíveis'}
        </p>
      )}
    </div>
  );
}
