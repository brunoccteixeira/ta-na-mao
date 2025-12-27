/**
 * Municipality search with autocomplete
 * Allows quick navigation to any municipality
 */

import { useState, useRef, useEffect } from 'react';
import { useQuery } from '@tanstack/react-query';
import { useDashboardStore } from '../../stores/dashboardStore';
import { searchMunicipalities } from '../../api/client';

interface SearchResult {
  ibge_code: string;
  name: string;
  state_id: number;
  population?: number;
}

// Debounce hook
function useDebounce<T>(value: T, delay: number): T {
  const [debouncedValue, setDebouncedValue] = useState<T>(value);

  useEffect(() => {
    const timer = setTimeout(() => setDebouncedValue(value), delay);
    return () => clearTimeout(timer);
  }, [value, delay]);

  return debouncedValue;
}

export default function MunicipalitySearch() {
  const [query, setQuery] = useState('');
  const [isOpen, setIsOpen] = useState(false);
  const inputRef = useRef<HTMLInputElement>(null);
  const dropdownRef = useRef<HTMLDivElement>(null);

  const { selectMunicipality } = useDashboardStore();

  const debouncedQuery = useDebounce(query, 300);

  const { data: results, isLoading } = useQuery({
    queryKey: ['municipalitySearch', debouncedQuery],
    queryFn: () => searchMunicipalities(debouncedQuery),
    enabled: debouncedQuery.length >= 2,
  });

  // Close dropdown when clicking outside
  useEffect(() => {
    const handleClickOutside = (event: MouseEvent) => {
      if (
        dropdownRef.current &&
        !dropdownRef.current.contains(event.target as Node) &&
        !inputRef.current?.contains(event.target as Node)
      ) {
        setIsOpen(false);
      }
    };

    document.addEventListener('mousedown', handleClickOutside);
    return () => document.removeEventListener('mousedown', handleClickOutside);
  }, []);

  const handleSelect = (result: SearchResult) => {
    // Get state abbreviation from state_id (we'll need to map this)
    // For now, navigate directly to municipality
    selectMunicipality(result.ibge_code);
    setQuery('');
    setIsOpen(false);
  };

  const formatPopulation = (pop?: number) => {
    if (!pop) return '';
    if (pop >= 1_000_000) return `${(pop / 1_000_000).toFixed(1)}M hab`;
    if (pop >= 1_000) return `${(pop / 1_000).toFixed(0)}k hab`;
    return `${pop} hab`;
  };

  return (
    <div className="relative">
      <div className="relative">
        <input
          ref={inputRef}
          type="text"
          value={query}
          onChange={(e) => {
            setQuery(e.target.value);
            setIsOpen(true);
          }}
          onFocus={() => setIsOpen(true)}
          placeholder="Buscar município..."
          className="w-48 lg:w-64 px-3 py-1.5 pl-8 text-sm bg-slate-800 border border-slate-700 rounded-lg text-white placeholder-slate-500 focus:outline-none focus:border-teal-500 focus:ring-1 focus:ring-teal-500"
        />
        <svg
          className="absolute left-2.5 top-1/2 -translate-y-1/2 w-4 h-4 text-slate-500"
          fill="none"
          stroke="currentColor"
          viewBox="0 0 24 24"
        >
          <path
            strokeLinecap="round"
            strokeLinejoin="round"
            strokeWidth={2}
            d="M21 21l-6-6m2-5a7 7 0 11-14 0 7 7 0 0114 0z"
          />
        </svg>
        {query && (
          <button
            onClick={() => {
              setQuery('');
              setIsOpen(false);
            }}
            className="absolute right-2 top-1/2 -translate-y-1/2 text-slate-500 hover:text-white"
          >
            <svg className="w-4 h-4" fill="none" stroke="currentColor" viewBox="0 0 24 24">
              <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M6 18L18 6M6 6l12 12" />
            </svg>
          </button>
        )}
      </div>

      {/* Dropdown */}
      {isOpen && query.length >= 2 && (
        <div
          ref={dropdownRef}
          className="absolute z-50 mt-1 w-full bg-slate-800 border border-slate-700 rounded-lg shadow-xl max-h-64 overflow-y-auto"
        >
          {isLoading ? (
            <div className="px-3 py-2 text-sm text-slate-400">Buscando...</div>
          ) : results && results.length > 0 ? (
            results.map((result: SearchResult) => (
              <button
                key={result.ibge_code}
                onClick={() => handleSelect(result)}
                className="w-full px-3 py-2 text-left hover:bg-slate-700 transition-colors border-b border-slate-700 last:border-b-0"
              >
                <div className="text-sm font-medium text-white">{result.name}</div>
                <div className="text-xs text-slate-400 flex items-center gap-2">
                  <span className="font-mono">{result.ibge_code}</span>
                  {result.population && (
                    <>
                      <span>•</span>
                      <span>{formatPopulation(result.population)}</span>
                    </>
                  )}
                </div>
              </button>
            ))
          ) : (
            <div className="px-3 py-2 text-sm text-slate-400">
              Nenhum município encontrado
            </div>
          )}
        </div>
      )}
    </div>
  );
}
