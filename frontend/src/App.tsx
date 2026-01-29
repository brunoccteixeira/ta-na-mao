/**
 * Main App component - Tá na Mão Dashboard & Chat
 */

import { useState } from 'react';
import { QueryClient, QueryClientProvider } from '@tanstack/react-query';
import BrazilMap from './components/Map/BrazilMap';
import ProgramSelector from './components/Dashboard/ProgramSelector';
import NationalSummary from './components/Dashboard/NationalSummary';
import StateCard from './components/Dashboard/StateCard';
import MunicipalityCard from './components/Dashboard/MunicipalityCard';
import MunicipalitySearch from './components/Dashboard/MunicipalitySearch';
import MetricSelector from './components/Dashboard/MetricSelector';
import RankingPanel from './components/Dashboard/RankingPanel';
import RegionSelector from './components/Dashboard/RegionSelector';
import RegionCard from './components/Dashboard/RegionCard';
import TrendChart from './components/Charts/TrendChart';
import DemographicBreakdown from './components/Charts/DemographicBreakdown';
import ProgramComparison from './components/Charts/ProgramComparison';
import AlertsPanel from './components/Admin/AlertsPanel';
import PenetrationTable from './components/Admin/PenetrationTable';
import ExportButton from './components/Admin/ExportButton';
import ChatPage from './components/Chat/ChatPage';
import EligibilityWizard from './components/EligibilityWizard';
import { ErrorBoundary } from './components/ErrorBoundary';
import { useDashboardStore } from './stores/dashboardStore';
import type { CitizenProfile, TriagemResult } from './components/EligibilityWizard/types';

// Create React Query client
const queryClient = new QueryClient({
  defaultOptions: {
    queries: {
      staleTime: 1000 * 60 * 5, // 5 minutes
      gcTime: 1000 * 60 * 60, // 1 hour
    },
  },
});

function Dashboard({ onOpenChat, onOpenWizard }: { onOpenChat: () => void; onOpenWizard: () => void }) {
  const { selectedState, selectedMunicipality, selectedRegion, viewLevel } = useDashboardStore();

  const REGION_NAMES: Record<string, string> = {
    N: 'Norte',
    NE: 'Nordeste',
    CO: 'Centro-Oeste',
    SE: 'Sudeste',
    S: 'Sul',
  };

  return (
    <div className="min-h-screen bg-slate-950 text-slate-100">
      {/* Header */}
      <header className="border-b border-slate-800 p-4">
        <div className="flex items-center gap-3 mb-3">
          <div className="w-10 h-10 rounded-lg bg-gradient-to-br from-teal-500 to-emerald-600 flex items-center justify-center text-xl">
            🇧🇷
          </div>
          <div>
            <h1 className="text-xl font-bold bg-gradient-to-r from-teal-400 to-emerald-400 bg-clip-text text-transparent">
              Dashboard de Benefícios - Brasil
            </h1>
            <p className="text-slate-400 text-xs">
              Tá na Mão × CAIXA | Granularidade Municipal
            </p>
          </div>
        </div>

        {/* Controls - Row 1 */}
        <div className="flex flex-wrap items-center gap-3 mb-2">
          <ProgramSelector />
          <div className="h-6 w-px bg-slate-700" />
          <MunicipalitySearch />
          <div className="h-6 w-px bg-slate-700" />
          <MetricSelector />
          <div className="flex-1" />
          <ExportButton />
        </div>

        {/* Controls - Row 2 */}
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

      {/* Main Content - Map & Sidebar */}
      <div className="grid lg:grid-cols-4 gap-4 p-4">
        {/* Map */}
        <div className="lg:col-span-3 bg-slate-900/50 rounded-xl border border-slate-800 overflow-hidden" style={{ height: '450px' }}>
          <BrazilMap />
        </div>

        {/* Sidebar */}
        <div className="lg:col-span-1 space-y-4 overflow-y-auto" style={{ maxHeight: '450px' }}>
          {/* Alerts Panel */}
          <AlertsPanel />

          {/* Selection Card */}
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

      {/* Penetration Table */}
      <div className="p-4 pt-0">
        <PenetrationTable />
      </div>

      {/* Footer */}
      <footer className="border-t border-slate-800 p-3 text-center text-xs text-slate-600">
        <p>
          Dados: IBGE, ANEEL, Ministério da Saúde, MDS |
          Atualizado automaticamente via API
        </p>
      </footer>

      {/* FAB Buttons */}
      <div className="fixed bottom-6 right-6 flex flex-col gap-3 z-40">
        {/* Wizard FAB */}
        <button
          onClick={onOpenWizard}
          className="w-16 h-16 rounded-full bg-gradient-to-br from-emerald-500 to-green-600 shadow-lg shadow-emerald-500/30 flex items-center justify-center text-2xl hover:scale-110 transition-transform"
          title="Descobrir meus direitos"
        >
          🎯
        </button>
        {/* Chat FAB */}
        <button
          onClick={onOpenChat}
          className="w-16 h-16 rounded-full bg-gradient-to-br from-teal-500 to-emerald-600 shadow-lg shadow-teal-500/30 flex items-center justify-center text-2xl hover:scale-110 transition-transform"
          title="Abrir Assistente Tá na Mão"
        >
          🤖
        </button>
      </div>
    </div>
  );
}

function WizardPage({ onBack }: { onBack: () => void }) {
  const handleComplete = (result: TriagemResult) => {
    console.log('Triagem completa:', result);
  };

  const handleGenerateCarta = (profile: CitizenProfile, result: TriagemResult) => {
    // TODO: Integrar com API de carta de encaminhamento
    console.log('Gerar carta para:', profile, result);
    alert('Funcionalidade de carta será integrada em breve!');
  };

  const handleFindCras = (profile: CitizenProfile) => {
    // TODO: Integrar com busca de CRAS
    console.log('Buscar CRAS para:', profile);
    const query = encodeURIComponent(`CRAS ${profile.municipio || ''} ${profile.uf || ''}`);
    window.open(`https://www.google.com/maps/search/${query}`, '_blank');
  };

  return (
    <div className="fixed inset-0 z-50 bg-slate-950 overflow-auto">
      {/* Header */}
      <header className="sticky top-0 z-10 bg-slate-950/95 backdrop-blur border-b border-slate-800 p-4">
        <div className="max-w-md mx-auto flex items-center gap-3">
          <button
            onClick={onBack}
            className="w-10 h-10 rounded-full bg-slate-800 hover:bg-slate-700 flex items-center justify-center transition-colors"
          >
            <svg className="w-5 h-5" fill="none" stroke="currentColor" viewBox="0 0 24 24">
              <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M15 19l-7-7 7-7" />
            </svg>
          </button>
          <div className="flex-1">
            <h1 className="font-bold text-slate-100">Descobrir Meus Direitos</h1>
            <p className="text-xs text-slate-400">Triagem de elegibilidade</p>
          </div>
          <div className="w-10 h-10 rounded-full bg-gradient-to-br from-emerald-500 to-green-600 flex items-center justify-center text-xl">
            🎯
          </div>
        </div>
      </header>

      {/* Wizard Content */}
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

export default function App() {
  const [showChat, setShowChat] = useState(false);
  const [showWizard, setShowWizard] = useState(false);

  return (
    <ErrorBoundary>
      <QueryClientProvider client={queryClient}>
        <Dashboard
          onOpenChat={() => setShowChat(true)}
          onOpenWizard={() => setShowWizard(true)}
        />
        {showChat && <ChatPage onBack={() => setShowChat(false)} />}
        {showWizard && <WizardPage onBack={() => setShowWizard(false)} />}
      </QueryClientProvider>
    </ErrorBoundary>
  );
}
