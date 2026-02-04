'use client';

/**
 * SelectWithSearch - Autocomplete select for cities
 *
 * Fetches municipalities from IBGE API
 */

import { useState, useEffect, useRef, useCallback } from 'react';
import { Search, ChevronDown, X, Loader2 } from 'lucide-react';

export interface SelectOption {
  value: string;
  label: string;
  extra?: string; // e.g., IBGE code for cities
}

interface Props {
  options?: SelectOption[];
  value: string | undefined;
  onChange: (value: string, option?: SelectOption) => void;
  placeholder?: string;
  searchPlaceholder?: string;
  loading?: boolean;
  disabled?: boolean;
  className?: string;
  // For IBGE integration
  fetchOptions?: (search: string) => Promise<SelectOption[]>;
}

export default function SelectWithSearch({
  options: staticOptions = [],
  value,
  onChange,
  placeholder = 'Selecione...',
  searchPlaceholder = 'Buscar...',
  loading = false,
  disabled = false,
  className = '',
  fetchOptions,
}: Props) {
  const [isOpen, setIsOpen] = useState(false);
  const [search, setSearch] = useState('');
  const [options, setOptions] = useState<SelectOption[]>(staticOptions);
  const [isSearching, setIsSearching] = useState(false);
  const containerRef = useRef<HTMLDivElement>(null);
  const inputRef = useRef<HTMLInputElement>(null);

  // Update options when static options change
  useEffect(() => {
    if (staticOptions.length > 0) {
      setOptions(staticOptions);
    }
  }, [staticOptions]);

  // Fetch options on search (debounced)
  useEffect(() => {
    if (!fetchOptions || search.length < 2) {
      if (staticOptions.length > 0) {
        setOptions(staticOptions);
      }
      return;
    }

    const timer = setTimeout(async () => {
      setIsSearching(true);
      try {
        const results = await fetchOptions(search);
        setOptions(results);
      } catch (err) {
        console.error('Error fetching options:', err);
      } finally {
        setIsSearching(false);
      }
    }, 300);

    return () => clearTimeout(timer);
  }, [search, fetchOptions, staticOptions]);

  // Close on click outside
  useEffect(() => {
    const handleClickOutside = (e: MouseEvent) => {
      if (containerRef.current && !containerRef.current.contains(e.target as Node)) {
        setIsOpen(false);
      }
    };
    document.addEventListener('mousedown', handleClickOutside);
    return () => document.removeEventListener('mousedown', handleClickOutside);
  }, []);

  // Focus input when opening
  useEffect(() => {
    if (isOpen && inputRef.current) {
      inputRef.current.focus();
    }
  }, [isOpen]);

  const selectedOption = options.find((o) => o.value === value);

  const filteredOptions = search.length > 0 && !fetchOptions
    ? options.filter((o) =>
        o.label.toLowerCase().includes(search.toLowerCase())
      )
    : options;

  const handleSelect = useCallback((option: SelectOption) => {
    onChange(option.value, option);
    setIsOpen(false);
    setSearch('');
  }, [onChange]);

  const handleClear = useCallback((e: React.MouseEvent) => {
    e.stopPropagation();
    onChange('', undefined);
    setSearch('');
  }, [onChange]);

  return (
    <div ref={containerRef} className={`relative ${className}`}>
      {/* Trigger button */}
      <button
        type="button"
        onClick={() => !disabled && setIsOpen(!isOpen)}
        disabled={disabled}
        className={`
          w-full flex items-center justify-between py-3.5 px-4 rounded-xl border-2 transition-all text-left
          ${
            isOpen
              ? 'border-emerald-500 ring-2 ring-emerald-500/20'
              : 'border-[var(--input-border)] hover:border-emerald-300'
          }
          ${disabled ? 'opacity-50 cursor-not-allowed' : 'cursor-pointer'}
          bg-[var(--input-bg)]
        `}
      >
        <span className={selectedOption ? 'text-[var(--text-primary)] font-medium' : 'text-[var(--text-tertiary)]'}>
          {loading ? (
            <span className="flex items-center gap-2">
              <Loader2 className="w-4 h-4 animate-spin" />
              Carregando...
            </span>
          ) : (
            selectedOption?.label || placeholder
          )}
        </span>

        <div className="flex items-center gap-1">
          {value && !disabled && (
            <button
              type="button"
              onClick={handleClear}
              className="p-1 hover:bg-[var(--hover-bg)] rounded-full"
            >
              <X className="w-4 h-4 text-[var(--text-tertiary)]" />
            </button>
          )}
          <ChevronDown
            className={`w-5 h-5 text-[var(--text-tertiary)] transition-transform ${isOpen ? 'rotate-180' : ''}`}
          />
        </div>
      </button>

      {/* Dropdown */}
      {isOpen && (
        <div className="absolute z-50 mt-2 w-full bg-[var(--bg-card)] border border-[var(--border-color)] rounded-xl shadow-lg overflow-hidden animate-slideDown">
          {/* Search input */}
          <div className="p-2 border-b border-[var(--border-color)]">
            <div className="relative">
              <Search className="absolute left-3 top-1/2 -translate-y-1/2 w-4 h-4 text-[var(--text-tertiary)]" />
              <input
                ref={inputRef}
                type="text"
                value={search}
                onChange={(e) => setSearch(e.target.value)}
                placeholder={searchPlaceholder}
                className="
                  w-full py-2.5 pl-9 pr-4 text-sm text-[var(--text-primary)]
                  bg-[var(--input-bg)] border border-[var(--input-border)] rounded-lg
                  focus:border-emerald-500 focus:outline-none
                  placeholder:text-[var(--text-tertiary)]
                "
              />
              {isSearching && (
                <Loader2 className="absolute right-3 top-1/2 -translate-y-1/2 w-4 h-4 text-[var(--text-tertiary)] animate-spin" />
              )}
            </div>
          </div>

          {/* Options list */}
          <div className="max-h-60 overflow-y-auto">
            {filteredOptions.length === 0 ? (
              <div className="py-8 text-center text-[var(--text-tertiary)] text-sm">
                {search.length > 0 ? 'Nenhum resultado encontrado' : 'Digite para buscar'}
              </div>
            ) : (
              filteredOptions.map((option) => (
                <button
                  key={option.value}
                  type="button"
                  onClick={() => handleSelect(option)}
                  className={`
                    w-full flex items-center justify-between py-3 px-4 text-left transition-colors
                    ${
                      option.value === value
                        ? 'bg-emerald-50 dark:bg-emerald-500/10 text-emerald-700 dark:text-emerald-400'
                        : 'hover:bg-[var(--hover-bg)] text-[var(--text-primary)]'
                    }
                  `}
                >
                  <span className="font-medium">{option.label}</span>
                  {option.extra && (
                    <span className="text-xs text-[var(--text-tertiary)]">{option.extra}</span>
                  )}
                </button>
              ))
            )}
          </div>
        </div>
      )}
    </div>
  );
}
