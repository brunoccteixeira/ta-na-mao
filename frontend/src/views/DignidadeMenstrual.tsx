/**
 * DignidadeMenstrual - Find nearby pharmacies for free menstrual products
 *
 * Uses the same pharmacy API with programa=DIGNIDADE_MENSTRUAL filter.
 * Rose/pink color theme.
 */

import { useState } from 'react';
import Link from 'next/link';
import dynamic from 'next/dynamic';
import { useNearbyFarmacias } from '../hooks/useNearbyFarmacias';
import type { PharmacyLocation } from '../hooks/useNearbyFarmacias';

const PharmacyMap = dynamic(() => import('../components/Map/PharmacyMap'), { ssr: false });

// ─── FAQ items ───
const faqItems = [
  {
    question: 'Quem pode receber absorventes grátis?',
    answer: 'Estudantes de escolas públicas, pessoas inscritas no CadÚnico com renda de até meio salário mínimo per capita, pessoas em situação de rua e adolescentes em medidas socioeducativas.',
  },
  {
    question: 'Precisa de receita médica?',
    answer: 'Não! Diferente dos medicamentos, os absorventes não precisam de receita. Basta apresentar CPF e documento com foto.',
  },
  {
    question: 'Pode ser em qualquer farmácia?',
    answer: 'Não. Precisa ser em uma farmácia credenciada no programa Farmácia Popular. Use a busca acima para encontrar uma perto de você.',
  },
  {
    question: 'Quantos absorventes posso pegar por mês?',
    answer: 'Até 2 pacotes de absorventes externos por mês, gratuitamente. Basta ir a uma farmácia credenciada com CPF e documento com foto.',
  },
  {
    question: 'Preciso ir ao CRAS primeiro?',
    answer: 'Não! Você pode ir direto na farmácia credenciada. Não precisa de encaminhamento do CRAS.',
  },
  {
    question: 'Preciso estar no CadÚnico?',
    answer: 'Depende: estudantes de escolas públicas não precisam. Para os demais grupos, é necessário estar inscrito no CadÚnico com renda de até 1/2 salário mínimo per capita.',
  },
];

export default function DignidadeMenstrual() {
  const [cepInput, setCepInput] = useState('');
  const [selectedPharmacy, setSelectedPharmacy] = useState<PharmacyLocation | null>(null);
  const [viewMode, setViewMode] = useState<'map' | 'list'>('map');
  const [openFaq, setOpenFaq] = useState<number | null>(null);

  const {
    farmacias,
    loading,
    error,
    fonte,
    userLocation,
    raio,
    requestLocationAndFetch,
    fetchByCep,
    clear,
  } = useNearbyFarmacias({ programa: 'DIGNIDADE_MENSTRUAL', raioMetros: 3000, limite: 20 });

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
              <h1 className="text-xl font-bold text-slate-900">Dignidade Menstrual</h1>
              <p className="text-sm text-slate-500">Absorventes grátis todo mês</p>
            </div>
            <span className="text-3xl">🩸</span>
          </div>
        </div>
      </header>

      <main className="max-w-4xl mx-auto px-4 py-6 space-y-6">
        {/* Banner */}
        <div className="bg-gradient-to-r from-rose-500 to-pink-500 rounded-2xl p-6 text-white">
          <h2 className="text-xl font-bold mb-2">Absorventes grátis todo mês</h2>
          <p className="text-rose-100 text-sm leading-relaxed">
            NÃO precisa ir ao CRAS. Vá direto na farmácia credenciada com CPF e documento com foto.
          </p>
        </div>

        {/* Eligibility Checklist */}
        <div className="bg-white rounded-2xl shadow-sm border border-slate-200 p-6">
          <h2 className="text-lg font-semibold text-slate-900 mb-4">Quem tem direito?</h2>
          <div className="space-y-3">
            {[
              { text: 'Estudantes de escolas públicas', detail: 'Levar comprovante de matrícula' },
              { text: 'Inscritas no CadÚnico', detail: 'Renda até 1/2 salário mínimo per capita' },
              { text: 'Pessoas em situação de rua', detail: 'Cadastro junto ao CRAS/Centro POP' },
              { text: 'Adolescentes em medidas socioeducativas', detail: 'Encaminhamento institucional' },
            ].map((item) => (
              <div key={item.text} className="flex items-start gap-3">
                <div className="w-6 h-6 rounded-full bg-rose-500 flex items-center justify-center flex-shrink-0 mt-0.5">
                  <svg className="w-3.5 h-3.5 text-white" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                    <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2.5} d="M5 13l4 4L19 7" />
                  </svg>
                </div>
                <div>
                  <p className="font-medium text-slate-800">{item.text}</p>
                  <p className="text-sm text-slate-500">{item.detail}</p>
                </div>
              </div>
            ))}
          </div>
        </div>

        {/* Search Options */}
        <div className="bg-white rounded-2xl shadow-sm border border-slate-200 p-6">
          <h2 className="text-lg font-semibold text-slate-900 mb-4">Encontre uma farmácia</h2>

          <div className="grid md:grid-cols-2 gap-4">
            {/* GPS Search */}
            <button
              onClick={requestLocationAndFetch}
              disabled={loading}
              className="flex items-center gap-4 p-4 rounded-xl border-2 border-rose-200 bg-rose-50 hover:bg-rose-100 transition-colors text-left disabled:opacity-50"
            >
              <div className="w-12 h-12 rounded-full bg-rose-500 flex items-center justify-center text-2xl flex-shrink-0">
                📍
              </div>
              <div>
                <p className="font-semibold text-rose-800">Usar minha localização</p>
                <p className="text-sm text-rose-600">Farmácias próximas a mim</p>
              </div>
            </button>

            {/* CEP Search */}
            <form onSubmit={handleCepSearch} className="flex flex-col">
              <div className="flex items-center gap-4 p-4 rounded-xl border-2 border-pink-200 bg-pink-50">
                <div className="w-12 h-12 rounded-full bg-pink-500 flex items-center justify-center text-2xl flex-shrink-0">
                  🔍
                </div>
                <div className="flex-1">
                  <label className="font-semibold text-pink-800 block mb-1">Buscar por CEP</label>
                  <div className="flex gap-2">
                    <input
                      type="text"
                      value={cepInput}
                      onChange={(e) => setCepInput(formatCep(e.target.value))}
                      placeholder="00000-000"
                      maxLength={9}
                      className="flex-1 px-3 py-2 rounded-lg border border-pink-300 bg-white text-slate-900 placeholder-slate-400 focus:outline-none focus:ring-2 focus:ring-pink-500"
                    />
                    <button
                      type="submit"
                      disabled={loading || cepInput.replace(/\D/g, '').length !== 8}
                      className="px-4 py-2 bg-pink-600 text-white rounded-lg hover:bg-pink-700 disabled:opacity-50 disabled:cursor-not-allowed transition-colors"
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
          <div className="text-center py-8">
            <div className="text-5xl mb-3">🩸</div>
            <h3 className="text-lg font-semibold text-slate-700 mb-2">
              Busque uma farmácia acima
            </h3>
            <p className="text-slate-500 max-w-md mx-auto text-sm">
              Use sua localização ou CEP para encontrar farmácias que distribuem
              absorventes gratuitos pelo programa Dignidade Menstrual.
            </p>
          </div>
        )}

        {/* FAQ Accordion */}
        <div className="bg-white rounded-2xl shadow-sm border border-slate-200 overflow-hidden">
          <div className="p-6 border-b border-slate-100">
            <h2 className="text-lg font-semibold text-slate-900">Perguntas frequentes</h2>
          </div>

          <div className="divide-y divide-slate-100">
            {faqItems.map((item, index) => (
              <div key={index}>
                <button
                  onClick={() => setOpenFaq(openFaq === index ? null : index)}
                  className="w-full flex items-center justify-between p-4 hover:bg-slate-50 transition-colors text-left"
                >
                  <span className="font-medium text-slate-800 pr-4">{item.question}</span>
                  <svg
                    className={`w-5 h-5 text-slate-400 transition-transform flex-shrink-0 ${openFaq === index ? 'rotate-180' : ''}`}
                    fill="none"
                    stroke="currentColor"
                    viewBox="0 0 24 24"
                  >
                    <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M19 9l-7 7-7-7" />
                  </svg>
                </button>

                {openFaq === index && (
                  <div className="px-4 pb-4">
                    <p className="text-sm text-slate-600 leading-relaxed">{item.answer}</p>
                  </div>
                )}
              </div>
            ))}
          </div>
        </div>

        {/* Info Cards */}
        <div className="grid md:grid-cols-3 gap-4">
          <div className="bg-rose-50 border border-rose-200 rounded-xl p-4">
            <h3 className="font-semibold text-rose-900 mb-2">📋 O que levar</h3>
            <ul className="text-sm text-rose-800 space-y-1">
              <li>• CPF</li>
              <li>• Documento com foto</li>
              <li>• Comprovante de matrícula (estudantes)</li>
            </ul>
          </div>

          <div className="bg-pink-50 border border-pink-200 rounded-xl p-4">
            <h3 className="font-semibold text-pink-900 mb-2">📞 Disque Saúde</h3>
            <p className="text-sm text-pink-800 mb-2">Dúvidas? Ligue grátis:</p>
            <a
              href="tel:136"
              className="inline-flex items-center gap-2 px-4 py-2 bg-pink-600 text-white rounded-lg hover:bg-pink-700 transition-colors"
            >
              <span>📞</span>
              <span className="font-bold">136</span>
            </a>
          </div>

          <div className="bg-purple-50 border border-purple-200 rounded-xl p-4">
            <h3 className="font-semibold text-purple-900 mb-2">📜 Base legal</h3>
            <p className="text-sm text-purple-800">
              Lei 14.214/2021 - Programa de Proteção e Promoção da Saúde Menstrual
            </p>
          </div>
        </div>
      </main>
    </div>
  );
}

// =============================================================================
// Pharmacy List Item (reused with rose theme)
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
          ? 'border-rose-500 shadow-md shadow-rose-100'
          : 'border-slate-200 hover:border-slate-300'
      }`}
    >
      <div className="flex items-start gap-4">
        <div className="w-12 h-12 rounded-full bg-rose-100 flex items-center justify-center text-2xl flex-shrink-0">
          🩸
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
          </div>
        </div>

        <div className="flex flex-col gap-2 flex-shrink-0">
          {farmacia.telefone && (
            <a
              href={`tel:${farmacia.telefone}`}
              onClick={(e) => e.stopPropagation()}
              className="flex items-center justify-center w-10 h-10 rounded-full bg-rose-100 text-rose-600 hover:bg-rose-200 transition-colors"
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
                className="flex-1 py-2 px-4 bg-rose-600 text-white text-center rounded-lg hover:bg-rose-700 transition-colors text-sm font-medium"
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
          </div>
        </div>
      )}
    </div>
  );
}
