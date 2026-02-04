'use client';

import { useState, useMemo, useEffect } from 'react';
import Link from 'next/link';
import { useBenefitsList, type BenefitSummaryAPI } from '../../../src/hooks/useBenefitsAPI';
import { formatBenefitValue } from '../../../src/engine/catalog';
import { BRAZILIAN_STATES } from '../../../src/engine/types';

type FilterScope = 'all' | 'federal' | 'state' | 'municipal' | 'sectoral';

const MUNICIPALITIES: Record<string, { name: string; state: string }> = {
  '3550308': { name: 'Sao Paulo', state: 'SP' },
  '3304557': { name: 'Rio de Janeiro', state: 'RJ' },
  '5300108': { name: 'Brasilia', state: 'DF' },
  '2927408': { name: 'Salvador', state: 'BA' },
  '2304400': { name: 'Fortaleza', state: 'CE' },
  '3106200': { name: 'Belo Horizonte', state: 'MG' },
  '1302603': { name: 'Manaus', state: 'AM' },
  '4106902': { name: 'Curitiba', state: 'PR' },
  '2611606': { name: 'Recife', state: 'PE' },
  '4314902': { name: 'Porto Alegre', state: 'RS' },
  '5208707': { name: 'Goiania', state: 'GO' },
  '1501402': { name: 'Belem', state: 'PA' },
  '3518800': { name: 'Guarulhos', state: 'SP' },
  '3509502': { name: 'Campinas', state: 'SP' },
  '2111300': { name: 'Sao Luis', state: 'MA' },
  '3304904': { name: 'Sao Goncalo', state: 'RJ' },
  '2704302': { name: 'Maceio', state: 'AL' },
  '3301702': { name: 'Duque de Caxias', state: 'RJ' },
  '5002704': { name: 'Campo Grande', state: 'MS' },
  '2408102': { name: 'Natal', state: 'RN' },
  '2211001': { name: 'Teresina', state: 'PI' },
  '3548708': { name: 'Sao Bernardo do Campo', state: 'SP' },
  '2507507': { name: 'Joao Pessoa', state: 'PB' },
  '3534401': { name: 'Osasco', state: 'SP' },
  '3547809': { name: 'Santo Andre', state: 'SP' },
  '3543402': { name: 'Ribeirao Preto', state: 'SP' },
  '3170206': { name: 'Uberlandia', state: 'MG' },
  '3118601': { name: 'Contagem', state: 'MG' },
  '3552205': { name: 'Sorocaba', state: 'SP' },
  '2800308': { name: 'Aracaju', state: 'SE' },
  '5103403': { name: 'Cuiaba', state: 'MT' },
  '2910800': { name: 'Feira de Santana', state: 'BA' },
  '4209102': { name: 'Joinville', state: 'SC' },
  '5201405': { name: 'Aparecida de Goiania', state: 'GO' },
  '4113700': { name: 'Londrina', state: 'PR' },
  '3136702': { name: 'Juiz de Fora', state: 'MG' },
  '1500800': { name: 'Ananindeua', state: 'PA' },
  '1100205': { name: 'Porto Velho', state: 'RO' },
  '3303302': { name: 'Niteroi', state: 'RJ' },
  '1600303': { name: 'Macapa', state: 'AP' },
};

export default function CatalogPage() {
  const [searchQuery, setSearchQuery] = useState('');
  const [scopeFilter, setScopeFilter] = useState<FilterScope>('all');
  const [stateFilter, setStateFilter] = useState<string>('');
  const [debouncedSearch, setDebouncedSearch] = useState('');

  useEffect(() => {
    const timer = setTimeout(() => {
      setDebouncedSearch(searchQuery);
    }, 300);
    return () => clearTimeout(timer);
  }, [searchQuery]);

  const {
    data: benefitsData,
    isLoading,
    isError,
    error,
  } = useBenefitsList({
    scope: scopeFilter !== 'all' ? scopeFilter : undefined,
    state: stateFilter || undefined,
    search: debouncedSearch || undefined,
    limit: 500,
  });

  const allBenefits = useMemo(() => {
    return benefitsData?.items || [];
  }, [benefitsData]);

  const filteredBenefits = useMemo(() => {
    let results = allBenefits;

    if (debouncedSearch.trim()) {
      const query = debouncedSearch.toLowerCase();
      results = results.filter(b =>
        b.name.toLowerCase().includes(query) ||
        b.shortDescription.toLowerCase().includes(query) ||
        b.category?.toLowerCase().includes(query) ||
        (b.municipalityIbge && MUNICIPALITIES[b.municipalityIbge]?.name.toLowerCase().includes(query))
      );
    }

    return results;
  }, [allBenefits, debouncedSearch]);

  const groupedBenefits = useMemo(() => {
    const groups: Record<string, BenefitSummaryAPI[]> = {};
    filteredBenefits.forEach(b => {
      const cat = b.category || 'Outros';
      if (!groups[cat]) groups[cat] = [];
      groups[cat].push(b);
    });
    return groups;
  }, [filteredBenefits]);

  const scopeLabel = (scope: string) => {
    switch (scope) {
      case 'federal': return 'Federal';
      case 'state': return 'Estadual';
      case 'municipal': return 'Municipal';
      case 'sectoral': return 'Setorial';
      default: return scope;
    }
  };

  const getMunicipalityName = (ibgeCode?: string) => {
    if (!ibgeCode) return '';
    return MUNICIPALITIES[ibgeCode]?.name || ibgeCode;
  };

  return (
    <div className="min-h-screen bg-[var(--bg-primary)]">
      {/* Header */}
      <header className="fixed top-0 left-0 right-0 bg-[var(--bg-header)] backdrop-blur-sm border-b border-[var(--border-color)] z-50">
        <div className="max-w-5xl mx-auto px-4 py-4 flex justify-between items-center">
          <Link href="/" className="text-xl font-bold text-emerald-600">
            Ta na Mao
          </Link>
          <nav className="flex gap-4">
            <Link href="/descobrir" className="text-emerald-600 hover:text-emerald-500 text-sm font-medium">
              Descobrir meus direitos
            </Link>
          </nav>
        </div>
      </header>

      {/* Content */}
      <main className="pt-24 pb-16 px-4">
        <div className="max-w-4xl mx-auto">
          <h1 className="text-2xl font-bold text-[var(--text-primary)] mb-2">
            Catalogo de Beneficios
          </h1>
          <p className="text-[var(--text-tertiary)] mb-8">
            {allBenefits.length} beneficios disponiveis em todo o Brasil
          </p>

          {/* Filters */}
          <div className="mb-8 space-y-4">
            <div className="relative">
              <input
                type="text"
                value={searchQuery}
                onChange={(e) => setSearchQuery(e.target.value)}
                placeholder="Buscar beneficio..."
                className="w-full px-4 py-3 pl-10 rounded-xl bg-[var(--input-bg)] border border-[var(--input-border)] text-[var(--text-primary)] placeholder-[var(--text-tertiary)] focus:outline-none focus:ring-2 focus:ring-emerald-500"
              />
              <span className="absolute left-3 top-1/2 -translate-y-1/2 text-[var(--text-tertiary)]">
                🔍
              </span>
            </div>

            <div className="flex flex-wrap gap-2">
              {(['all', 'federal', 'state', 'municipal', 'sectoral'] as FilterScope[]).map((scope) => (
                <button
                  key={scope}
                  onClick={() => setScopeFilter(scope)}
                  className={`px-4 py-2 rounded-lg text-sm transition-colors ${
                    scopeFilter === scope
                      ? 'bg-emerald-600 text-white'
                      : 'bg-[var(--badge-bg)] text-[var(--text-secondary)] hover:bg-[var(--hover-bg)]'
                  }`}
                >
                  {scope === 'all' ? 'Todos' : scopeLabel(scope)}
                </button>
              ))}

              <select
                value={stateFilter}
                onChange={(e) => setStateFilter(e.target.value)}
                className="px-4 py-2 rounded-lg bg-[var(--input-bg)] text-[var(--text-secondary)] border border-[var(--input-border)] focus:outline-none focus:ring-2 focus:ring-emerald-500"
              >
                <option value="">Todos os estados</option>
                {Object.entries(BRAZILIAN_STATES).map(([code, name]) => (
                  <option key={code} value={code}>{name}</option>
                ))}
              </select>
            </div>
          </div>

          {/* Loading */}
          {isLoading && (
            <div className="flex items-center justify-center py-12">
              <div className="flex items-center gap-3 text-[var(--text-tertiary)]">
                <div className="w-5 h-5 border-2 border-emerald-500 border-t-transparent rounded-full animate-spin" />
                <span>Carregando beneficios...</span>
              </div>
            </div>
          )}

          {/* Error */}
          {isError && (
            <div className="bg-red-500/10 border border-red-500/30 rounded-xl p-4 mb-6">
              <p className="text-red-500 text-sm">
                {error instanceof Error ? error.message : 'Erro ao carregar beneficios. Usando dados locais.'}
              </p>
            </div>
          )}

          {/* Results count */}
          {!isLoading && (
            <p className="text-sm text-[var(--text-tertiary)] mb-4">
              {filteredBenefits.length} beneficio{filteredBenefits.length !== 1 && 's'} encontrado{filteredBenefits.length !== 1 && 's'}
              {benefitsData?.total && benefitsData.total > filteredBenefits.length && (
                <span className="opacity-60"> (de {benefitsData.total} total)</span>
              )}
            </p>
          )}

          {/* Benefits grid by category */}
          {!isLoading && Object.entries(groupedBenefits).map(([category, benefits]) => (
            <div key={category} className="mb-8">
              <h2 className="text-lg font-semibold text-[var(--text-primary)] mb-4">
                {category}
              </h2>
              <div className="grid md:grid-cols-2 gap-4">
                {benefits.map((benefit) => (
                  <Link
                    key={benefit.id}
                    href={`/beneficios/${benefit.id}`}
                    className="p-4 rounded-xl bg-[var(--bg-card)] border border-[var(--border-color)] hover:border-emerald-500/50 hover:bg-[var(--hover-bg)] transition-all"
                  >
                    <div className="flex items-start gap-3">
                      <span className="text-2xl">{benefit.icon || '📋'}</span>
                      <div className="flex-1 min-w-0">
                        <div className="flex items-center gap-2">
                          <h3 className="font-medium text-[var(--text-primary)] truncate">
                            {benefit.name}
                          </h3>
                          <span className={`px-2 py-0.5 rounded text-xs ${
                            benefit.scope === 'federal' ? 'bg-blue-500/20 text-blue-600' :
                            benefit.scope === 'state' ? 'bg-purple-500/20 text-purple-600' :
                            benefit.scope === 'municipal' ? 'bg-cyan-500/20 text-cyan-600' :
                            'bg-amber-500/20 text-amber-600'
                          }`}>
                            {benefit.scope === 'state' ? benefit.state :
                             benefit.scope === 'municipal' ? getMunicipalityName(benefit.municipalityIbge) :
                             scopeLabel(benefit.scope)}
                          </span>
                        </div>
                        <p className="text-sm text-[var(--text-tertiary)] mt-1 line-clamp-2">
                          {benefit.shortDescription}
                        </p>
                        {benefit.estimatedValue && (
                          <p className="text-sm text-emerald-600 mt-2 font-medium">
                            {formatBenefitValue(benefit)}
                          </p>
                        )}
                      </div>
                    </div>
                  </Link>
                ))}
              </div>
            </div>
          ))}

          {!isLoading && filteredBenefits.length === 0 && (
            <div className="text-center py-12">
              <p className="text-[var(--text-tertiary)]">Nenhum beneficio encontrado</p>
              <button
                onClick={() => {
                  setSearchQuery('');
                  setScopeFilter('all');
                  setStateFilter('');
                }}
                className="mt-4 text-emerald-600 hover:text-emerald-500"
              >
                Limpar filtros
              </button>
            </div>
          )}
        </div>
      </main>
    </div>
  );
}
