/**
 * Catalog - Browse all benefits
 * Uses API v2 with fallback to static JSON
 */

import { useState, useMemo, useEffect } from 'react';
import { Link } from 'react-router-dom';
import { useBenefitsList, type BenefitSummaryAPI } from '../hooks/useBenefitsAPI';
import { formatBenefitValue } from '../engine/catalog';
import { BRAZILIAN_STATES } from '../engine/types';

type FilterScope = 'all' | 'federal' | 'state' | 'municipal' | 'sectoral';

// Mapeamento de códigos IBGE para nomes de municípios
const MUNICIPALITIES: Record<string, { name: string; state: string }> = {
  // Top 10
  '3550308': { name: 'São Paulo', state: 'SP' },
  '3304557': { name: 'Rio de Janeiro', state: 'RJ' },
  '5300108': { name: 'Brasília', state: 'DF' },
  '2927408': { name: 'Salvador', state: 'BA' },
  '2304400': { name: 'Fortaleza', state: 'CE' },
  '3106200': { name: 'Belo Horizonte', state: 'MG' },
  '1302603': { name: 'Manaus', state: 'AM' },
  '4106902': { name: 'Curitiba', state: 'PR' },
  '2611606': { name: 'Recife', state: 'PE' },
  '4314902': { name: 'Porto Alegre', state: 'RS' },
  // 11-20
  '5208707': { name: 'Goiânia', state: 'GO' },
  '1501402': { name: 'Belém', state: 'PA' },
  '3518800': { name: 'Guarulhos', state: 'SP' },
  '3509502': { name: 'Campinas', state: 'SP' },
  '2111300': { name: 'São Luís', state: 'MA' },
  '3304904': { name: 'São Gonçalo', state: 'RJ' },
  '2704302': { name: 'Maceió', state: 'AL' },
  '3301702': { name: 'Duque de Caxias', state: 'RJ' },
  '5002704': { name: 'Campo Grande', state: 'MS' },
  '2408102': { name: 'Natal', state: 'RN' },
  // 21-30
  '2211001': { name: 'Teresina', state: 'PI' },
  '3548708': { name: 'São Bernardo do Campo', state: 'SP' },
  '2507507': { name: 'João Pessoa', state: 'PB' },
  '3534401': { name: 'Osasco', state: 'SP' },
  '3547809': { name: 'Santo André', state: 'SP' },
  '3543402': { name: 'Ribeirão Preto', state: 'SP' },
  '3170206': { name: 'Uberlândia', state: 'MG' },
  '3118601': { name: 'Contagem', state: 'MG' },
  '3552205': { name: 'Sorocaba', state: 'SP' },
  '2800308': { name: 'Aracaju', state: 'SE' },
  // 31-40
  '5103403': { name: 'Cuiabá', state: 'MT' },
  '2910800': { name: 'Feira de Santana', state: 'BA' },
  '4209102': { name: 'Joinville', state: 'SC' },
  '5201405': { name: 'Aparecida de Goiânia', state: 'GO' },
  '4113700': { name: 'Londrina', state: 'PR' },
  '3136702': { name: 'Juiz de Fora', state: 'MG' },
  '1500800': { name: 'Ananindeua', state: 'PA' },
  '1100205': { name: 'Porto Velho', state: 'RO' },
  '3303302': { name: 'Niterói', state: 'RJ' },
  '1600303': { name: 'Macapá', state: 'AP' },
};

export default function Catalog() {
  const [searchQuery, setSearchQuery] = useState('');
  const [scopeFilter, setScopeFilter] = useState<FilterScope>('all');
  const [stateFilter, setStateFilter] = useState<string>('');
  const [debouncedSearch, setDebouncedSearch] = useState('');

  // Debounce search input
  useEffect(() => {
    const timer = setTimeout(() => {
      setDebouncedSearch(searchQuery);
    }, 300);
    return () => clearTimeout(timer);
  }, [searchQuery]);

  // Fetch benefits from API with filters
  const {
    data: benefitsData,
    isLoading,
    isError,
    error,
  } = useBenefitsList({
    scope: scopeFilter !== 'all' ? scopeFilter : undefined,
    state: stateFilter || undefined,
    search: debouncedSearch || undefined,
    limit: 500, // Get all for now
  });

  const allBenefits = useMemo(() => {
    return benefitsData?.items || [];
  }, [benefitsData]);

  // The API already handles filtering, but we do local filtering for the municipality name search
  const filteredBenefits = useMemo(() => {
    let results = allBenefits;

    // Additional local filtering for municipality name search (API can't do this)
    if (debouncedSearch.trim()) {
      const query = debouncedSearch.toLowerCase();
      // Check if the API search missed any matches on municipality name
      results = results.filter(b =>
        b.name.toLowerCase().includes(query) ||
        b.shortDescription.toLowerCase().includes(query) ||
        b.category?.toLowerCase().includes(query) ||
        (b.municipalityIbge && MUNICIPALITIES[b.municipalityIbge]?.name.toLowerCase().includes(query))
      );
    }

    return results;
  }, [allBenefits, debouncedSearch]);

  // Group by category
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
    <div className="min-h-screen bg-gradient-to-b from-slate-900 via-slate-900 to-slate-950">
      {/* Header */}
      <header className="fixed top-0 left-0 right-0 bg-slate-900/95 backdrop-blur-sm border-b border-slate-800 z-50">
        <div className="max-w-5xl mx-auto px-4 py-4 flex justify-between items-center">
          <Link to="/" className="text-xl font-bold text-emerald-400">
            Tá na Mão
          </Link>
          <nav className="flex gap-4">
            <Link to="/descobrir" className="text-emerald-400 hover:text-emerald-300 text-sm font-medium">
              Descobrir meus direitos
            </Link>
          </nav>
        </div>
      </header>

      {/* Content */}
      <main className="pt-24 pb-16 px-4">
        <div className="max-w-4xl mx-auto">
          <h1 className="text-2xl font-bold text-white mb-2">
            Catálogo de Benefícios
          </h1>
          <p className="text-slate-400 mb-8">
            {allBenefits.length} benefícios disponíveis em todo o Brasil
          </p>

          {/* Filters */}
          <div className="mb-8 space-y-4">
            {/* Search */}
            <div className="relative">
              <input
                type="text"
                value={searchQuery}
                onChange={(e) => setSearchQuery(e.target.value)}
                placeholder="Buscar benefício..."
                className="w-full px-4 py-3 pl-10 rounded-xl bg-slate-800 border border-slate-700 text-white placeholder-slate-500 focus:outline-none focus:ring-2 focus:ring-emerald-500"
              />
              <span className="absolute left-3 top-1/2 -translate-y-1/2 text-slate-500">
                🔍
              </span>
            </div>

            {/* Filter buttons */}
            <div className="flex flex-wrap gap-2">
              {(['all', 'federal', 'state', 'municipal', 'sectoral'] as FilterScope[]).map((scope) => (
                <button
                  key={scope}
                  onClick={() => setScopeFilter(scope)}
                  className={`px-4 py-2 rounded-lg text-sm transition-colors ${
                    scopeFilter === scope
                      ? 'bg-emerald-600 text-white'
                      : 'bg-slate-800 text-slate-300 hover:bg-slate-700'
                  }`}
                >
                  {scope === 'all' ? 'Todos' : scopeLabel(scope)}
                </button>
              ))}

              {/* State filter */}
              <select
                value={stateFilter}
                onChange={(e) => setStateFilter(e.target.value)}
                className="px-4 py-2 rounded-lg bg-slate-800 text-slate-300 border border-slate-700 focus:outline-none focus:ring-2 focus:ring-emerald-500"
              >
                <option value="">Todos os estados</option>
                {Object.entries(BRAZILIAN_STATES).map(([code, name]) => (
                  <option key={code} value={code}>{name}</option>
                ))}
              </select>
            </div>
          </div>

          {/* Loading state */}
          {isLoading && (
            <div className="flex items-center justify-center py-12">
              <div className="flex items-center gap-3 text-slate-400">
                <div className="w-5 h-5 border-2 border-emerald-500 border-t-transparent rounded-full animate-spin" />
                <span>Carregando benefícios...</span>
              </div>
            </div>
          )}

          {/* Error state */}
          {isError && (
            <div className="bg-red-500/10 border border-red-500/30 rounded-xl p-4 mb-6">
              <p className="text-red-400 text-sm">
                {error instanceof Error ? error.message : 'Erro ao carregar benefícios. Usando dados locais.'}
              </p>
            </div>
          )}

          {/* Results count */}
          {!isLoading && (
            <p className="text-sm text-slate-500 mb-4">
              {filteredBenefits.length} benefício{filteredBenefits.length !== 1 && 's'} encontrado{filteredBenefits.length !== 1 && 's'}
              {benefitsData?.total && benefitsData.total > filteredBenefits.length && (
                <span className="text-slate-600"> (de {benefitsData.total} total)</span>
              )}
            </p>
          )}

          {/* Benefits grid by category */}
          {!isLoading && Object.entries(groupedBenefits).map(([category, benefits]) => (
            <div key={category} className="mb-8">
              <h2 className="text-lg font-semibold text-white mb-4">
                {category}
              </h2>
              <div className="grid md:grid-cols-2 gap-4">
                {benefits.map((benefit) => (
                  <Link
                    key={benefit.id}
                    to={`/beneficios/${benefit.id}`}
                    className="p-4 rounded-xl bg-slate-800/50 border border-slate-700 hover:border-emerald-500/50 hover:bg-slate-800 transition-all"
                  >
                    <div className="flex items-start gap-3">
                      <span className="text-2xl">{benefit.icon || '📋'}</span>
                      <div className="flex-1 min-w-0">
                        <div className="flex items-center gap-2">
                          <h3 className="font-medium text-white truncate">
                            {benefit.name}
                          </h3>
                          <span className={`px-2 py-0.5 rounded text-xs ${
                            benefit.scope === 'federal' ? 'bg-blue-500/20 text-blue-300' :
                            benefit.scope === 'state' ? 'bg-purple-500/20 text-purple-300' :
                            benefit.scope === 'municipal' ? 'bg-cyan-500/20 text-cyan-300' :
                            'bg-amber-500/20 text-amber-300'
                          }`}>
                            {benefit.scope === 'state' ? benefit.state :
                             benefit.scope === 'municipal' ? getMunicipalityName(benefit.municipalityIbge) :
                             scopeLabel(benefit.scope)}
                          </span>
                        </div>
                        <p className="text-sm text-slate-400 mt-1 line-clamp-2">
                          {benefit.shortDescription}
                        </p>
                        {benefit.estimatedValue && (
                          <p className="text-sm text-emerald-400 mt-2 font-medium">
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
              <p className="text-slate-500">Nenhum benefício encontrado</p>
              <button
                onClick={() => {
                  setSearchQuery('');
                  setScopeFilter('all');
                  setStateFilter('');
                }}
                className="mt-4 text-emerald-400 hover:text-emerald-300"
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
