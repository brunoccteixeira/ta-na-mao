/**
 * CrasFinder - Find nearby CRAS locations
 *
 * Allows users to search for CRAS by:
 * - Current GPS location
 * - CEP (postal code)
 *
 * Displays results on an interactive map and as a list.
 */

import { useState } from 'react';
import Link from 'next/link';
import dynamic from 'next/dynamic';
import { useNearbyCras } from '../hooks/useNearbyCras';
import type { CrasLocation } from '../components/Map/CrasMap';

const CrasMap = dynamic(() => import('../components/Map/CrasMap'), { ssr: false });

export default function CrasFinder() {
  const [cepInput, setCepInput] = useState('');
  const [selectedCras, setSelectedCras] = useState<CrasLocation | null>(null);
  const [viewMode, setViewMode] = useState<'map' | 'list'>('map');

  const {
    cras,
    loading,
    error,
    fonte,
    userLocation,
    raio,
    requestLocationAndFetch,
    fetchByCep,
    clear,
  } = useNearbyCras({ raioMetros: 10000, limite: 20 });

  const handleCepSearch = async (e: React.FormEvent) => {
    e.preventDefault();
    if (cepInput.trim()) {
      await fetchByCep(cepInput);
    }
  };

  const handleLocationSearch = async () => {
    await requestLocationAndFetch();
  };

  const formatCep = (value: string) => {
    const digits = value.replace(/\D/g, '');
    if (digits.length <= 5) return digits;
    return `${digits.slice(0, 5)}-${digits.slice(5, 8)}`;
  };

  return (
    <div className="min-h-screen bg-gradient-to-b from-slate-50 to-white">
      {/* Header */}
      <header className="bg-white border-b border-slate-200 sticky top-0 z-50">
        <div className="max-w-4xl mx-auto px-4 py-4">
          <div className="flex items-center gap-4">
            <Link
              href="/"
              className="w-10 h-10 rounded-full bg-slate-100 hover:bg-slate-200 flex items-center justify-center transition-colors"
            >
              <svg className="w-5 h-5 text-slate-600" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M15 19l-7-7 7-7" />
              </svg>
            </Link>
            <div className="flex-1">
              <h1 className="text-xl font-bold text-slate-900">Encontrar CRAS</h1>
              <p className="text-sm text-slate-500">Centro de Referência de Assistência Social</p>
            </div>
            <span className="text-3xl">🏛️</span>
          </div>
        </div>
      </header>

      <main className="max-w-4xl mx-auto px-4 py-6 space-y-6">
        {/* Search Options */}
        <div className="bg-white rounded-2xl shadow-sm border border-slate-200 p-6">
          <h2 className="text-lg font-semibold text-slate-900 mb-4">Como você quer buscar?</h2>

          <div className="grid md:grid-cols-2 gap-4">
            {/* GPS Search */}
            <button
              onClick={handleLocationSearch}
              disabled={loading}
              className="flex items-center gap-4 p-4 rounded-xl border-2 border-emerald-200 bg-emerald-50 hover:bg-emerald-100 transition-colors text-left disabled:opacity-50"
            >
              <div className="w-12 h-12 rounded-full bg-emerald-500 flex items-center justify-center text-2xl flex-shrink-0">
                📍
              </div>
              <div>
                <p className="font-semibold text-emerald-800">Usar minha localização</p>
                <p className="text-sm text-emerald-600">Encontrar CRAS próximos a mim</p>
              </div>
            </button>

            {/* CEP Search */}
            <form onSubmit={handleCepSearch} className="flex flex-col">
              <div className="flex items-center gap-4 p-4 rounded-xl border-2 border-purple-200 bg-purple-50">
                <div className="w-12 h-12 rounded-full bg-purple-500 flex items-center justify-center text-2xl flex-shrink-0">
                  🔍
                </div>
                <div className="flex-1">
                  <label className="font-semibold text-purple-800 block mb-1">Buscar por CEP</label>
                  <div className="flex gap-2">
                    <input
                      type="text"
                      value={cepInput}
                      onChange={(e) => setCepInput(formatCep(e.target.value))}
                      placeholder="00000-000"
                      maxLength={9}
                      className="flex-1 px-3 py-2 rounded-lg border border-purple-300 bg-white text-slate-900 placeholder-slate-400 focus:outline-none focus:ring-2 focus:ring-purple-500"
                    />
                    <button
                      type="submit"
                      disabled={loading || cepInput.replace(/\D/g, '').length !== 8}
                      className="px-4 py-2 bg-purple-600 text-white rounded-lg hover:bg-purple-700 disabled:opacity-50 disabled:cursor-not-allowed transition-colors"
                    >
                      Buscar
                    </button>
                  </div>
                </div>
              </div>
            </form>
          </div>

          {/* Loading State */}
          {loading && (
            <div className="mt-4 flex items-center justify-center gap-3 text-slate-600">
              <svg className="w-5 h-5 animate-spin" fill="none" viewBox="0 0 24 24">
                <circle className="opacity-25" cx="12" cy="12" r="10" stroke="currentColor" strokeWidth="4"></circle>
                <path className="opacity-75" fill="currentColor" d="M4 12a8 8 0 018-8V0C5.373 0 0 5.373 0 12h4z"></path>
              </svg>
              <span>Buscando CRAS próximos...</span>
            </div>
          )}

          {/* Error State */}
          {error && (
            <div className="mt-4 p-4 bg-red-50 border border-red-200 rounded-xl">
              <p className="text-red-700 flex items-center gap-2">
                <span>⚠️</span>
                {error}
              </p>
            </div>
          )}
        </div>

        {/* Results */}
        {cras.length > 0 && (
          <>
            {/* Results Header */}
            <div className="flex items-center justify-between">
              <div>
                <h2 className="text-lg font-semibold text-slate-900">
                  {cras.length} CRAS encontrado{cras.length !== 1 ? 's' : ''}
                </h2>
                <p className="text-sm text-slate-500">
                  {fonte === 'coordenadas' ? 'Próximos à sua localização' : 'Na sua região'}
                </p>
              </div>

              {/* View Toggle */}
              <div className="flex rounded-lg bg-slate-100 p-1">
                <button
                  onClick={() => setViewMode('map')}
                  className={`px-3 py-1.5 rounded-md text-sm font-medium transition-colors ${
                    viewMode === 'map'
                      ? 'bg-white text-slate-900 shadow-sm'
                      : 'text-slate-600 hover:text-slate-900'
                  }`}
                >
                  🗺️ Mapa
                </button>
                <button
                  onClick={() => setViewMode('list')}
                  className={`px-3 py-1.5 rounded-md text-sm font-medium transition-colors ${
                    viewMode === 'list'
                      ? 'bg-white text-slate-900 shadow-sm'
                      : 'text-slate-600 hover:text-slate-900'
                  }`}
                >
                  📋 Lista
                </button>
              </div>
            </div>

            {/* Map View */}
            {viewMode === 'map' && (
              <div className="rounded-2xl overflow-hidden shadow-sm border border-slate-200">
                <CrasMap
                  cras={cras}
                  userLocation={userLocation || undefined}
                  raio={fonte === 'coordenadas' ? raio : undefined}
                  height="450px"
                  onCrasSelect={setSelectedCras}
                />
              </div>
            )}

            {/* List View */}
            {viewMode === 'list' && (
              <div className="space-y-3">
                {cras.map((crasItem, index) => (
                  <CrasListItem
                    key={crasItem.id || index}
                    cras={crasItem}
                    isSelected={selectedCras?.id === crasItem.id}
                    onClick={() => setSelectedCras(crasItem)}
                  />
                ))}
              </div>
            )}

            {/* Clear Button */}
            <div className="text-center">
              <button
                onClick={clear}
                className="text-sm text-slate-500 hover:text-slate-700 underline"
              >
                Limpar resultados e buscar novamente
              </button>
            </div>
          </>
        )}

        {/* Empty State (no search yet) */}
        {cras.length === 0 && !loading && !error && (
          <div className="text-center py-12">
            <div className="text-6xl mb-4">🏛️</div>
            <h3 className="text-lg font-semibold text-slate-700 mb-2">
              O CRAS é a porta de entrada para benefícios sociais
            </h3>
            <p className="text-slate-500 max-w-md mx-auto">
              No CRAS você pode se cadastrar no CadÚnico, solicitar Bolsa Família,
              BPC, Tarifa Social de Energia e muitos outros benefícios.
            </p>
          </div>
        )}

        {/* Info Cards */}
        <div className="grid md:grid-cols-2 gap-4">
          <div className="bg-blue-50 border border-blue-200 rounded-xl p-4">
            <h3 className="font-semibold text-blue-900 mb-2">📋 O que levar ao CRAS</h3>
            <ul className="text-sm text-blue-800 space-y-1">
              <li>• Documento de identidade (RG ou CNH)</li>
              <li>• CPF de todos da família</li>
              <li>• Comprovante de residência</li>
              <li>• Comprovante de renda (se houver)</li>
            </ul>
          </div>

          <div className="bg-emerald-50 border border-emerald-200 rounded-xl p-4">
            <h3 className="font-semibold text-emerald-900 mb-2">📞 Disque Social</h3>
            <p className="text-sm text-emerald-800 mb-2">
              Não encontrou CRAS na sua região? Ligue gratuitamente:
            </p>
            <a
              href="tel:121"
              className="inline-flex items-center gap-2 px-4 py-2 bg-emerald-600 text-white rounded-lg hover:bg-emerald-700 transition-colors"
            >
              <span>📞</span>
              <span className="font-bold">121</span>
            </a>
          </div>
        </div>
      </main>
    </div>
  );
}

// =============================================================================
// CRAS List Item Component
// =============================================================================

interface CrasListItemProps {
  cras: CrasLocation;
  isSelected: boolean;
  onClick: () => void;
}

function CrasListItem({ cras, isSelected, onClick }: CrasListItemProps) {
  return (
    <div
      onClick={onClick}
      className={`bg-white rounded-xl border-2 p-4 cursor-pointer transition-all ${
        isSelected
          ? 'border-purple-500 shadow-md shadow-purple-100'
          : 'border-slate-200 hover:border-slate-300'
      }`}
    >
      <div className="flex items-start gap-4">
        <div className="w-12 h-12 rounded-full bg-purple-100 flex items-center justify-center text-2xl flex-shrink-0">
          🏛️
        </div>

        <div className="flex-1 min-w-0">
          <h3 className="font-semibold text-slate-900 truncate">{cras.nome}</h3>
          <p className="text-sm text-slate-600 mt-0.5">{cras.endereco}</p>

          {cras.distancia && (
            <span className="inline-flex items-center gap-1 mt-2 px-2 py-0.5 bg-blue-100 text-blue-700 text-xs rounded-full">
              📍 {cras.distancia}
            </span>
          )}

          {cras.servicos && cras.servicos.length > 0 && (
            <div className="flex flex-wrap gap-1 mt-2">
              {cras.servicos.slice(0, 4).map((servico, i) => (
                <span
                  key={i}
                  className="px-2 py-0.5 bg-slate-100 text-slate-600 text-xs rounded"
                >
                  {servico}
                </span>
              ))}
            </div>
          )}
        </div>

        <div className="flex flex-col gap-2 flex-shrink-0">
          {cras.telefone && (
            <a
              href={`tel:${cras.telefone}`}
              onClick={(e) => e.stopPropagation()}
              className="flex items-center justify-center w-10 h-10 rounded-full bg-emerald-100 text-emerald-600 hover:bg-emerald-200 transition-colors"
              title="Ligar"
            >
              📞
            </a>
          )}
          {cras.latitude && cras.longitude && (
            <a
              href={`https://www.google.com/maps/dir/?api=1&destination=${cras.latitude},${cras.longitude}`}
              target="_blank"
              rel="noopener noreferrer"
              onClick={(e) => e.stopPropagation()}
              className="flex items-center justify-center w-10 h-10 rounded-full bg-blue-100 text-blue-600 hover:bg-blue-200 transition-colors"
              title="Como chegar"
            >
              🗺️
            </a>
          )}
        </div>
      </div>

      {/* Expanded Details */}
      {isSelected && (
        <div className="mt-4 pt-4 border-t border-slate-200 space-y-3">
          {cras.horario && (
            <div className="flex items-center gap-2 text-sm">
              <span>🕐</span>
              <span className="text-slate-600">{cras.horario}</span>
            </div>
          )}

          {cras.telefone && (
            <div className="flex items-center gap-2 text-sm">
              <span>📞</span>
              <a href={`tel:${cras.telefone}`} className="text-blue-600 hover:underline">
                {cras.telefone}
              </a>
            </div>
          )}

          <div className="flex gap-2 mt-3">
            {cras.telefone && (
              <a
                href={`tel:${cras.telefone}`}
                className="flex-1 py-2 px-4 bg-emerald-600 text-white text-center rounded-lg hover:bg-emerald-700 transition-colors text-sm font-medium"
              >
                📞 Ligar agora
              </a>
            )}
            {cras.latitude && cras.longitude && (
              <a
                href={`https://www.google.com/maps/dir/?api=1&destination=${cras.latitude},${cras.longitude}`}
                target="_blank"
                rel="noopener noreferrer"
                className="flex-1 py-2 px-4 bg-blue-600 text-white text-center rounded-lg hover:bg-blue-700 transition-colors text-sm font-medium"
              >
                🗺️ Traçar rota
              </a>
            )}
          </div>
        </div>
      )}
    </div>
  );
}
