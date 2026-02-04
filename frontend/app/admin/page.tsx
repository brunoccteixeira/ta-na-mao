'use client';

import { useState } from 'react';
import dynamic from 'next/dynamic';
import ChatPage from '../../src/components/Chat/ChatPage';

const EligibilityWizard = dynamic(
  () => import('../../src/components/EligibilityWizard'),
  { ssr: false }
);
import ProgramSelector from '../../src/components/Dashboard/ProgramSelector';
import NationalSummary from '../../src/components/Dashboard/NationalSummary';
import StateCard from '../../src/components/Dashboard/StateCard';
import MunicipalityCard from '../../src/components/Dashboard/MunicipalityCard';
import MunicipalitySearch from '../../src/components/Dashboard/MunicipalitySearch';
import MetricSelector from '../../src/components/Dashboard/MetricSelector';
import RankingPanel from '../../src/components/Dashboard/RankingPanel';
import RegionSelector from '../../src/components/Dashboard/RegionSelector';
import RegionCard from '../../src/components/Dashboard/RegionCard';
import TrendChart from '../../src/components/Charts/TrendChart';
import DemographicBreakdown from '../../src/components/Charts/DemographicBreakdown';
import ProgramComparison from '../../src/components/Charts/ProgramComparison';
import AlertsPanel from '../../src/components/Admin/AlertsPanel';
import PenetrationTable from '../../src/components/Admin/PenetrationTable';
import ExportButton from '../../src/components/Admin/ExportButton';
import { useDashboardStore } from '../../src/stores/dashboardStore';
import type { CitizenProfile, TriagemResult } from '../../src/components/EligibilityWizard/types';
import { generateCarta } from '../../src/utils/generateCarta';

// Leaflet requires dynamic import with ssr: false
const BrazilMap = dynamic(
  () => import('../../src/components/Map/BrazilMap'),
  { ssr: false }
);

const REGION_NAMES: Record<string, string> = {
  N: 'Norte',
  NE: 'Nordeste',
  CO: 'Centro-Oeste',
  SE: 'Sudeste',
  S: 'Sul',
};

function WizardOverlay({ onBack }: { onBack: () => void }) {
  const handleComplete = (result: TriagemResult) => {
    console.log('Triagem completa:', result);
  };

  const handleGenerateCarta = async (profile: CitizenProfile, result: TriagemResult) => {
    try {
      await generateCarta(profile, result);
    } catch (err) {
      console.error('Erro ao gerar carta:', err);
      alert('Erro ao gerar carta. Tente novamente.');
    }
  };

  const handleFindCras = (profile: CitizenProfile) => {
    const query = encodeURIComponent(`CRAS ${profile.municipio || ''} ${profile.uf || ''}`);
    window.open(`https://www.google.com/maps/search/${query}`, '_blank');
  };

  return (
    <div className="theme-dark fixed inset-0 z-50 bg-[var(--bg-primary)] overflow-auto">
      <header className="sticky top-0 z-10 bg-[var(--bg-header)] backdrop-blur border-b border-[var(--border-color)] p-4">
        <div className="max-w-md mx-auto flex items-center gap-3">
          <button
            onClick={onBack}
            className="w-10 h-10 rounded-full bg-[var(--bg-card)] hover:bg-[var(--hover-bg)] flex items-center justify-center transition-colors"
          >
            <svg className="w-5 h-5" fill="none" stroke="currentColor" viewBox="0 0 24 24">
              <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M15 19l-7-7 7-7" />
            </svg>
          </button>
          <div className="flex-1">
            <h1 className="font-bold text-[var(--text-primary)]">Descobrir Meus Direitos</h1>
            <p className="text-xs text-[var(--text-tertiary)]">Triagem de elegibilidade</p>
          </div>
          <div className="w-10 h-10 rounded-full bg-gradient-to-br from-emerald-500 to-green-600 flex items-center justify-center text-xl">
            🎯
          </div>
        </div>
      </header>
      <main className="p-4 pb-8">
        <EligibilityWizard
          onComplete={handleComplete}
          onGenerateCarta={handleGenerateCarta}
          onFindCras={handleFindCras}
        />
      </main>
    </div>
  );
}

export default function AdminPage() {
  const [showChat, setShowChat] = useState(false);
  const [showWizard, setShowWizard] = useState(false);
  const { selectedState, selectedMunicipality, selectedRegion, viewLevel } = useDashboardStore();

  return (
    <>
      <div className="min-h-screen bg-slate-950 text-slate-100">
        {/* Header */}
        <header className="border-b border-slate-800 p-4">
          <div className="flex items-center gap-3 mb-3">
            <div className="w-10 h-10 rounded-lg bg-gradient-to-br from-teal-500 to-emerald-600 flex items-center justify-center text-xl">
              🇧🇷
            </div>
            <div>
              <h1 className="text-xl font-bold bg-gradient-to-r from-teal-400 to-emerald-400 bg-clip-text text-transparent">
                Dashboard de Beneficios - Brasil
              </h1>
              <p className="text-slate-400 text-xs">
                Ta na Mao × CAIXA | Granularidade Municipal
              </p>
            </div>
          </div>

          <div className="flex flex-wrap items-center gap-3 mb-2">
            <ProgramSelector />
            <div className="h-6 w-px bg-slate-700" />
            <MunicipalitySearch />
            <div className="h-6 w-px bg-slate-700" />
            <MetricSelector />
            <div className="flex-1" />
            <ExportButton />
          </div>

          <div className="flex flex-wrap items-center gap-3">
            <RegionSelector />
            <div className="flex-1" />
            <div className="flex items-center gap-2 text-xs text-slate-500">
              <span className="px-2 py-1 bg-blue-500/20 text-blue-400 rounded font-medium">
                Painel Admin
              </span>
              <span className="px-2 py-1 bg-slate-800 rounded">
                {viewLevel === 'national' && 'Brasil'}
                {viewLevel === 'region' && `${selectedRegion ? REGION_NAMES[selectedRegion] : ''}`}
                {viewLevel === 'state' && `${selectedState}`}
                {viewLevel === 'municipality' && 'Municipio'}
              </span>
              <span className="px-2 py-1 bg-emerald-500/20 text-emerald-400 rounded">
                ~5.570 municipios
              </span>
            </div>
          </div>
        </header>

        {/* KPIs */}
        <div className="p-4 border-b border-slate-800">
          <NationalSummary />
        </div>

        {/* Main Content */}
        <div className="grid lg:grid-cols-4 gap-4 p-4">
          <div className="lg:col-span-3 bg-slate-900/50 rounded-xl border border-slate-800 overflow-hidden" style={{ height: '450px' }}>
            <BrazilMap />
          </div>

          <div className="lg:col-span-1 space-y-4 overflow-y-auto" style={{ maxHeight: '450px' }}>
            <AlertsPanel />
            {selectedMunicipality ? (
              <MunicipalityCard />
            ) : selectedRegion ? (
              <RegionCard />
            ) : (
              <StateCard />
            )}
            <ProgramComparison />
            <TrendChart />
            <DemographicBreakdown />
            <RankingPanel />
          </div>
        </div>

        <div className="p-4 pt-0">
          <PenetrationTable />
        </div>

        <footer className="border-t border-slate-800 p-3 text-center text-xs text-slate-600">
          <p>
            Dados: IBGE, ANEEL, Ministerio da Saude, MDS |
            Atualizado automaticamente via API
          </p>
        </footer>

        {/* FAB Buttons */}
        <div className="fixed bottom-6 right-6 flex flex-col gap-3 z-40">
          <button
            onClick={() => setShowWizard(true)}
            className="w-16 h-16 rounded-full bg-gradient-to-br from-emerald-500 to-green-600 shadow-lg shadow-emerald-500/30 flex items-center justify-center text-2xl hover:scale-110 transition-transform"
            title="Descobrir meus direitos"
          >
            🎯
          </button>
          <button
            onClick={() => setShowChat(true)}
            className="w-16 h-16 rounded-full bg-gradient-to-br from-teal-500 to-emerald-600 shadow-lg shadow-teal-500/30 flex items-center justify-center text-2xl hover:scale-110 transition-transform"
            title="Abrir Assistente Ta na Mao"
          >
            🤖
          </button>
        </div>
      </div>

      {showChat && <ChatPage onBack={() => setShowChat(false)} />}
      {showWizard && <WizardOverlay onBack={() => setShowWizard(false)} />}
    </>
  );
}
