/**
 * PharmacyFinder - Find nearby Farmácia Popular locations
 *
 * Allows users to search by GPS or CEP.
 * Shows results on map + list, plus medication categories and info cards.
 */

import { useState } from 'react';
import Link from 'next/link';
import dynamic from 'next/dynamic';
import { useNearbyFarmacias } from '../hooks/useNearbyFarmacias';
import type { PharmacyLocation } from '../hooks/useNearbyFarmacias';

const PharmacyMap = dynamic(() => import('../components/Map/PharmacyMap'), { ssr: false });

// ─── Medication categories (Farmácia Popular - 100% grátis) ───
const medicationCategories = [
  {
    name: 'Hipertensão',
    icon: '❤️',
    meds: ['Losartana', 'Captopril', 'Atenolol', 'Hidroclorotiazida', 'Enalapril', 'Propranolol', 'Anlodipino', 'Espironolactona', 'Furosemida'],
  },
  {
    name: 'Diabetes',
    icon: '🩸',
    meds: ['Metformina', 'Glibenclamida', 'Insulina NPH', 'Insulina Regular', 'Dapagliflozina'],
  },
  {
    name: 'Asma',
    icon: '🫁',
    meds: ['Salbutamol (Aerolin)', 'Beclometasona', 'Ipratrópio'],
  },
  {
    name: 'Anticoncepcionais',
    icon: '💜',
    meds: ['Etinilestradiol + Levonorgestrel', 'Noretisterona + Etinilestradiol', 'Medroxiprogesterona'],
  },
  {
    name: 'Osteoporose',
    icon: '🦴',
    meds: ['Alendronato de Sódio'],
  },
  {
    name: 'Parkinson',
    icon: '🧠',
    meds: ['Levodopa + Carbidopa', 'Levodopa + Benserazida'],
  },
  {
    name: 'Glaucoma',
    icon: '👁️',
    meds: ['Timolol'],
  },
  {
    name: 'Dislipidemia',
    icon: '🫀',
    meds: ['Sinvastatina'],
  },
  {
    name: 'Rinite',
    icon: '👃',
    meds: ['Budesonida'],
  },
];

// Itens com desconto (NÃO são 100% grátis)
const discountedItems = [
  {
    name: 'Incontinência',
    icon: '🩹',
    items: [{ name: 'Fralda Geriátrica', discount: '40% de desconto' }],
  },
];

export default function PharmacyFinder() {
  const [cepInput, setCepInput] = useState('');
  const [selectedPharmacy, setSelectedPharmacy] = useState<PharmacyLocation | null>(null);
  const [viewMode, setViewMode] = useState<'map' | 'list'>('map');
  const [openCategory, setOpenCategory] = useState<number | null>(null);

  const {
    farmacias,
    redesNacionais,
    loading,
    error,
    fonte,
    userLocation,
    raio,
    requestLocationAndFetch,
    fetchByCep,
    clear,
  } = useNearbyFarmacias({ raioMetros: 3000, limite: 20 });

  const handleCepSearch = async (e: React.FormEvent) => {
    e.preventDefault();
    if (cepInput.trim()) {
      await fetchByCep(cepInput);
    }
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
              <h1 className="text-xl font-bold text-slate-900">Farmácia Popular</h1>
              <p className="text-sm text-slate-500">Medicamentos 100% grátis</p>
            </div>
            <span className="text-3xl">💊</span>
          </div>
        </div>
      </header>

      <main className="max-w-4xl mx-auto px-4 py-6 space-y-6">
        {/* Search Options */}
        <div className="bg-white rounded-2xl shadow-sm border border-slate-200 p-6">
          <h2 className="text-lg font-semibold text-slate-900 mb-4">Encontre uma farmácia credenciada</h2>

          <div className="grid md:grid-cols-2 gap-4">
            {/* GPS Search */}
            <button
              onClick={requestLocationAndFetch}
              disabled={loading}
              className="flex items-center gap-4 p-4 rounded-xl border-2 border-teal-200 bg-teal-50 hover:bg-teal-100 transition-colors text-left disabled:opacity-50"
            >
              <div className="w-12 h-12 rounded-full bg-teal-500 flex items-center justify-center text-2xl flex-shrink-0">
                📍
              </div>
              <div>
                <p className="font-semibold text-teal-800">Usar minha localização</p>
                <p className="text-sm text-teal-600">Farmácias próximas a mim</p>
              </div>
            </button>

            {/* CEP Search */}
            <form onSubmit={handleCepSearch} className="flex flex-col">
              <div className="flex items-center gap-4 p-4 rounded-xl border-2 border-emerald-200 bg-emerald-50">
                <div className="w-12 h-12 rounded-full bg-emerald-500 flex items-center justify-center text-2xl flex-shrink-0">
                  🔍
                </div>
                <div className="flex-1">
                  <label className="font-semibold text-emerald-800 block mb-1">Buscar por CEP</label>
                  <div className="flex gap-2">
                    <input
                      type="text"
                      value={cepInput}
                      onChange={(e) => setCepInput(formatCep(e.target.value))}
                      placeholder="00000-000"
                      maxLength={9}
                      className="flex-1 px-3 py-2 rounded-lg border border-emerald-300 bg-white text-slate-900 placeholder-slate-400 focus:outline-none focus:ring-2 focus:ring-emerald-500"
                    />
                    <button
                      type="submit"
                      disabled={loading || cepInput.replace(/\D/g, '').length !== 8}
                      className="px-4 py-2 bg-emerald-600 text-white rounded-lg hover:bg-emerald-700 disabled:opacity-50 disabled:cursor-not-allowed transition-colors"
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
              <span>Buscando farmácias próximas...</span>
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
        {farmacias.length > 0 && (
          <>
            <div className="flex items-center justify-between">
              <div>
                <h2 className="text-lg font-semibold text-slate-900">
                  {farmacias.length} farmácia{farmacias.length !== 1 ? 's' : ''} encontrada{farmacias.length !== 1 ? 's' : ''}
                </h2>
                <p className="text-sm text-slate-500">
                  {fonte === 'coordenadas' ? 'Próximas à sua localização' : 'Na sua região'}
                </p>
              </div>

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

            {viewMode === 'map' && (
              <div className="rounded-2xl overflow-hidden shadow-sm border border-slate-200">
                <PharmacyMap
                  farmacias={farmacias}
                  userLocation={userLocation || undefined}
                  raio={fonte === 'coordenadas' ? raio : undefined}
                  height="450px"
                  onPharmacySelect={setSelectedPharmacy}
                />
              </div>
            )}

            {viewMode === 'list' && (
              <div className="space-y-3">
                {farmacias.map((farmacia, index) => (
                  <PharmacyListItem
                    key={farmacia.id || index}
                    farmacia={farmacia}
                    isSelected={selectedPharmacy?.id === farmacia.id}
                    onClick={() => setSelectedPharmacy(farmacia)}
                  />
                ))}
              </div>
            )}

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

        {/* Empty State */}
        {farmacias.length === 0 && !loading && !error && (
          <div className="text-center py-12">
            <div className="text-6xl mb-4">💊</div>
            <h3 className="text-lg font-semibold text-slate-700 mb-2">
              Remédios grátis pelo Farmácia Popular
            </h3>
            <p className="text-slate-500 max-w-md mx-auto">
              O programa Farmácia Popular oferece medicamentos 100% gratuitos para
              hipertensão, diabetes, asma e muito mais. Basta ter receita médica e CPF.
            </p>
          </div>
        )}

        {/* Medications Accordion */}
        <div className="bg-white rounded-2xl shadow-sm border border-slate-200 overflow-hidden">
          <div className="p-6 border-b border-slate-100">
            <h2 className="text-lg font-semibold text-slate-900">Medicamentos 100% grátis</h2>
            <p className="text-sm text-slate-500 mt-1">Toque em uma categoria para ver os remédios disponíveis</p>
          </div>

          <div className="divide-y divide-slate-100">
            {medicationCategories.map((category, index) => (
              <div key={category.name}>
                <button
                  onClick={() => setOpenCategory(openCategory === index ? null : index)}
                  className="w-full flex items-center justify-between p-4 hover:bg-slate-50 transition-colors text-left"
                >
                  <div className="flex items-center gap-3">
                    <span className="text-xl">{category.icon}</span>
                    <span className="font-medium text-slate-800">{category.name}</span>
                    <span className="text-xs text-slate-400 bg-slate-100 px-2 py-0.5 rounded-full">
                      {category.meds.length}
                    </span>
                  </div>
                  <svg
                    className={`w-5 h-5 text-slate-400 transition-transform ${openCategory === index ? 'rotate-180' : ''}`}
                    fill="none"
                    stroke="currentColor"
                    viewBox="0 0 24 24"
                  >
                    <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M19 9l-7 7-7-7" />
                  </svg>
                </button>

                {openCategory === index && (
                  <div className="px-4 pb-4">
                    <div className="flex flex-wrap gap-2 ml-9">
                      {category.meds.map((med) => (
                        <span
                          key={med}
                          className="px-3 py-1.5 bg-emerald-50 text-emerald-700 text-sm rounded-lg border border-emerald-200"
                        >
                          {med}
                        </span>
                      ))}
                    </div>
                  </div>
                )}
              </div>
            ))}
          </div>
        </div>

        {/* Items with discount (not 100% free) */}
        <div className="bg-amber-50 border border-amber-200 rounded-2xl p-6">
          <h3 className="font-semibold text-amber-900 mb-1">Com desconto (não são 100% grátis)</h3>
          <p className="text-sm text-amber-700 mb-3">
            Estes itens têm desconto pelo programa, mas não são gratuitos.
          </p>
          {discountedItems.map((cat) => (
            <div key={cat.name} className="flex items-center gap-3">
              <span className="text-xl">{cat.icon}</span>
              {cat.items.map((item) => (
                <div key={item.name} className="flex items-center gap-2">
                  <span className="font-medium text-amber-900">{item.name}</span>
                  <span className="px-2 py-0.5 bg-amber-200 text-amber-800 text-xs rounded-full font-medium">
                    {item.discount}
                  </span>
                </div>
              ))}
            </div>
          ))}
        </div>

        {/* Info Cards */}
        <div className="grid md:grid-cols-2 gap-4">
          <div className="bg-teal-50 border border-teal-200 rounded-xl p-4">
            <h3 className="font-semibold text-teal-900 mb-2">📋 O que levar na farmácia</h3>
            <ul className="text-sm text-teal-800 space-y-1">
              <li>• CPF</li>
              <li>• Receita médica (validade 120 dias)</li>
              <li>• Documento com foto (RG ou CNH)</li>
            </ul>
          </div>

          <div className="bg-emerald-50 border border-emerald-200 rounded-xl p-4">
            <h3 className="font-semibold text-emerald-900 mb-2">📞 Disque Saúde</h3>
            <p className="text-sm text-emerald-800 mb-2">
              Dúvidas sobre o programa? Ligue gratuitamente:
            </p>
            <a
              href="tel:136"
              className="inline-flex items-center gap-2 px-4 py-2 bg-emerald-600 text-white rounded-lg hover:bg-emerald-700 transition-colors"
            >
              <span>📞</span>
              <span className="font-bold">136</span>
            </a>
          </div>
        </div>

        {/* National chains */}
        <div className="bg-white rounded-2xl shadow-sm border border-slate-200 p-6">
          <h3 className="font-semibold text-slate-900 mb-3">🏪 Redes credenciadas em todo o Brasil</h3>
          <p className="text-sm text-slate-500 mb-4">
            Estas redes participam do programa. Confirme disponibilidade na unidade mais próxima.
          </p>
          <div className="flex flex-wrap gap-2">
            {(redesNacionais.length > 0
              ? redesNacionais
              : ['Drogasil', 'Droga Raia', 'Pague Menos', 'Drogaria São Paulo', 'Panvel', 'Ultrafarma']
            ).map((rede) => (
              <span
                key={rede}
                className="px-4 py-2 bg-slate-100 text-slate-700 rounded-lg text-sm font-medium"
              >
                {rede}
              </span>
            ))}
          </div>
        </div>
      </main>
    </div>
  );
}

// =============================================================================
// Pharmacy List Item
// =============================================================================

interface PharmacyListItemProps {
  farmacia: PharmacyLocation;
  isSelected: boolean;
  onClick: () => void;
}

function PharmacyListItem({ farmacia, isSelected, onClick }: PharmacyListItemProps) {
  return (
    <div
      onClick={onClick}
      className={`bg-white rounded-xl border-2 p-4 cursor-pointer transition-all ${
        isSelected
          ? 'border-emerald-500 shadow-md shadow-emerald-100'
          : 'border-slate-200 hover:border-slate-300'
      }`}
    >
      <div className="flex items-start gap-4">
        <div className="w-12 h-12 rounded-full bg-emerald-100 flex items-center justify-center text-2xl flex-shrink-0">
          💊
        </div>

        <div className="flex-1 min-w-0">
          <h3 className="font-semibold text-slate-900 truncate">{farmacia.nome}</h3>
          <p className="text-sm text-slate-600 mt-0.5">{farmacia.endereco}</p>

          <div className="flex flex-wrap gap-1.5 mt-2">
            {farmacia.distancia && (
              <span className="inline-flex items-center gap-1 px-2 py-0.5 bg-blue-100 text-blue-700 text-xs rounded-full">
                📍 {farmacia.distancia}
              </span>
            )}
            {farmacia.aberto_agora !== undefined && (
              <span
                className={`px-2 py-0.5 text-xs rounded-full font-medium ${
                  farmacia.aberto_agora
                    ? 'bg-green-100 text-green-700'
                    : 'bg-red-100 text-red-700'
                }`}
              >
                {farmacia.aberto_agora ? '🟢 Aberto' : '🔴 Fechado'}
              </span>
            )}
            {farmacia.delivery && (
              <span className="px-2 py-0.5 bg-sky-100 text-sky-700 text-xs rounded-full">
                🚚 Delivery
              </span>
            )}
          </div>
        </div>

        <div className="flex flex-col gap-2 flex-shrink-0">
          {farmacia.telefone && (
            <a
              href={`tel:${farmacia.telefone}`}
              onClick={(e) => e.stopPropagation()}
              className="flex items-center justify-center w-10 h-10 rounded-full bg-emerald-100 text-emerald-600 hover:bg-emerald-200 transition-colors"
              title="Ligar"
            >
              📞
            </a>
          )}
          <a
            href={
              farmacia.links?.google_maps ||
              `https://www.google.com/maps/dir/?api=1&destination=${farmacia.latitude},${farmacia.longitude}`
            }
            target="_blank"
            rel="noopener noreferrer"
            onClick={(e) => e.stopPropagation()}
            className="flex items-center justify-center w-10 h-10 rounded-full bg-blue-100 text-blue-600 hover:bg-blue-200 transition-colors"
            title="Como chegar"
          >
            🗺️
          </a>
        </div>
      </div>

      {/* Expanded Details */}
      {isSelected && (
        <div className="mt-4 pt-4 border-t border-slate-200 space-y-3">
          {farmacia.horario && (
            <div className="flex items-center gap-2 text-sm">
              <span>🕐</span>
              <span className="text-slate-600">{farmacia.horario}</span>
            </div>
          )}

          {farmacia.telefone && (
            <div className="flex items-center gap-2 text-sm">
              <span>📞</span>
              <a href={`tel:${farmacia.telefone}`} className="text-blue-600 hover:underline">
                {farmacia.telefone}
              </a>
            </div>
          )}

          <div className="flex gap-2 mt-3">
            {farmacia.telefone && (
              <a
                href={`tel:${farmacia.telefone}`}
                className="flex-1 py-2 px-4 bg-emerald-600 text-white text-center rounded-lg hover:bg-emerald-700 transition-colors text-sm font-medium"
              >
                📞 Ligar agora
              </a>
            )}
            <a
              href={
                farmacia.links?.google_maps ||
                `https://www.google.com/maps/dir/?api=1&destination=${farmacia.latitude},${farmacia.longitude}`
              }
              target="_blank"
              rel="noopener noreferrer"
              className="flex-1 py-2 px-4 bg-blue-600 text-white text-center rounded-lg hover:bg-blue-700 transition-colors text-sm font-medium"
            >
              🗺️ Google Maps
            </a>
            {farmacia.links?.waze && (
              <a
                href={farmacia.links.waze}
                target="_blank"
                rel="noopener noreferrer"
                className="flex-1 py-2 px-4 bg-sky-500 text-white text-center rounded-lg hover:bg-sky-600 transition-colors text-sm font-medium"
              >
                🗺️ Waze
              </a>
            )}
            {farmacia.links?.whatsapp && (
              <a
                href={farmacia.links.whatsapp}
                target="_blank"
                rel="noopener noreferrer"
                className="flex-1 py-2 px-4 bg-green-600 text-white text-center rounded-lg hover:bg-green-700 transition-colors text-sm font-medium"
              >
                💬 WhatsApp
              </a>
            )}
          </div>
        </div>
      )}
    </div>
  );
}
