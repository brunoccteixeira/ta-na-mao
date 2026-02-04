/**
 * AdvisorDashboard - Painel do Assessor Social (Anjo Social)
 * Rota: /assessor
 * Dark theme consistente com admin existente.
 */

import { useState, useEffect, useCallback } from 'react';
import CaseList from '../components/Admin/CaseList';

const API_BASE = '/api/v1/advisory';

interface AdvisorStats {
  openCases: number;
  inProgressCases: number;
  resolvedThisMonth: number;
  totalResolved: number;
  avgResolutionDays: number | null;
}

interface CaseData {
  id: string;
  citizenSessionId: string;
  status: string;
  priority: string;
  benefits: string[];
  escalationReason: string;
  citizenContext: Record<string, unknown> | null;
  advisor: { name: string; role: string; organization: string } | null;
  notes: { id: string; author: string; content: string; createdAt: string }[];
  createdAt: string;
  updatedAt: string;
  resolvedAt: string | null;
}

export default function AdvisorDashboard() {
  const [cases, setCases] = useState<CaseData[]>([]);
  const [stats, setStats] = useState<AdvisorStats | null>(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);

  const fetchCases = useCallback(async () => {
    try {
      const res = await fetch(`${API_BASE}/cases/?limit=100`);
      if (!res.ok) throw new Error('Erro ao carregar casos');
      const data = await res.json();
      setCases(data.cases || []);

      // Calcula stats a partir dos casos
      const allCases = data.cases || [];
      const open = allCases.filter(
        (c: CaseData) => c.status === 'open' || c.status === 'assigned',
      ).length;
      const inProgress = allCases.filter(
        (c: CaseData) => c.status === 'in_progress',
      ).length;
      const resolved = allCases.filter(
        (c: CaseData) => c.status === 'resolved',
      );
      const now = new Date();
      const monthStart = new Date(now.getFullYear(), now.getMonth(), 1);
      const resolvedThisMonth = resolved.filter(
        (c: CaseData) => c.resolvedAt && new Date(c.resolvedAt) >= monthStart,
      ).length;

      setStats({
        openCases: open,
        inProgressCases: inProgress,
        resolvedThisMonth,
        totalResolved: resolved.length,
        avgResolutionDays: null,
      });

      setError(null);
    } catch (err) {
      setError(err instanceof Error ? err.message : 'Erro desconhecido');
    } finally {
      setLoading(false);
    }
  }, []);

  useEffect(() => {
    fetchCases();
  }, [fetchCases]);

  const handleUpdateStatus = async (caseId: string, status: string) => {
    try {
      const res = await fetch(`${API_BASE}/cases/${caseId}`, {
        method: 'PATCH',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ status }),
      });
      if (!res.ok) throw new Error('Erro ao atualizar caso');
      await fetchCases();
    } catch (err) {
      console.error('Erro ao atualizar status:', err);
    }
  };

  const handleAddNote = async (caseId: string, content: string) => {
    try {
      const res = await fetch(`${API_BASE}/cases/${caseId}/notes`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ author: 'Assessor', content }),
      });
      if (!res.ok) throw new Error('Erro ao adicionar nota');
      await fetchCases();
    } catch (err) {
      console.error('Erro ao adicionar nota:', err);
    }
  };

  return (
    <div className="min-h-screen bg-slate-950 text-slate-100">
      {/* Header */}
      <header className="border-b border-slate-800 p-4">
        <div className="max-w-6xl mx-auto flex items-center gap-3">
          <div className="w-10 h-10 rounded-lg bg-gradient-to-br from-violet-500 to-purple-600 flex items-center justify-center text-xl">
            <svg className="w-6 h-6 text-white" fill="none" stroke="currentColor" viewBox="0 0 24 24">
              <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M17 20h5v-2a3 3 0 00-5.356-1.857M17 20H7m10 0v-2c0-.656-.126-1.283-.356-1.857M7 20H2v-2a3 3 0 015.356-1.857M7 20v-2c0-.656.126-1.283.356-1.857m0 0a5.002 5.002 0 019.288 0M15 7a3 3 0 11-6 0 3 3 0 016 0zm6 3a2 2 0 11-4 0 2 2 0 014 0zM7 10a2 2 0 11-4 0 2 2 0 014 0z" />
            </svg>
          </div>
          <div>
            <h1 className="text-xl font-bold bg-gradient-to-r from-violet-400 to-purple-400 bg-clip-text text-transparent">
              Anjo Social - Painel do Assessor
            </h1>
            <p className="text-slate-400 text-xs">
              Acompanhamento de casos escalados pela IA
            </p>
          </div>
          <div className="flex-1" />
          <a
            href="/admin"
            className="px-3 py-1.5 bg-slate-800 hover:bg-slate-700 rounded-lg text-sm text-slate-300 transition-colors"
          >
            Dashboard Admin
          </a>
        </div>
      </header>

      {/* KPIs */}
      <div className="max-w-6xl mx-auto p-4">
        {stats && (
          <div className="grid grid-cols-2 md:grid-cols-4 gap-4 mb-6">
            <KPICard
              label="Casos Abertos"
              value={stats.openCases}
              color="text-yellow-400"
              bg="bg-yellow-500/10 border-yellow-500/20"
            />
            <KPICard
              label="Em Andamento"
              value={stats.inProgressCases}
              color="text-purple-400"
              bg="bg-purple-500/10 border-purple-500/20"
            />
            <KPICard
              label="Resolvidos (mes)"
              value={stats.resolvedThisMonth}
              color="text-emerald-400"
              bg="bg-emerald-500/10 border-emerald-500/20"
            />
            <KPICard
              label="Total Resolvidos"
              value={stats.totalResolved}
              color="text-blue-400"
              bg="bg-blue-500/10 border-blue-500/20"
            />
          </div>
        )}

        {/* Cases */}
        {loading ? (
          <div className="text-center py-12 text-slate-400">
            Carregando casos...
          </div>
        ) : error ? (
          <div className="text-center py-12">
            <p className="text-red-400 mb-3">{error}</p>
            <button
              onClick={fetchCases}
              className="px-4 py-2 bg-slate-800 hover:bg-slate-700 rounded-lg text-sm transition-colors"
            >
              Tentar novamente
            </button>
          </div>
        ) : cases.length === 0 ? (
          <div className="text-center py-16">
            <div className="text-4xl mb-4">
              <svg className="w-16 h-16 mx-auto text-slate-600" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={1.5} d="M9 12h6m-6 4h6m2 5H7a2 2 0 01-2-2V5a2 2 0 012-2h5.586a1 1 0 01.707.293l5.414 5.414a1 1 0 01.293.707V19a2 2 0 01-2 2z" />
              </svg>
            </div>
            <p className="text-slate-400 text-lg mb-2">Nenhum caso aberto</p>
            <p className="text-slate-500 text-sm">
              Casos escalados pela IA aparecerao aqui automaticamente.
            </p>
          </div>
        ) : (
          <CaseList
            cases={cases}
            onUpdateStatus={handleUpdateStatus}
            onAddNote={handleAddNote}
          />
        )}
      </div>
    </div>
  );
}

function KPICard({
  label,
  value,
  color,
  bg,
}: {
  label: string;
  value: number;
  color: string;
  bg: string;
}) {
  return (
    <div className={`p-4 rounded-xl border ${bg}`}>
      <p className="text-xs text-slate-400 mb-1">{label}</p>
      <p className={`text-3xl font-bold ${color}`}>{value}</p>
    </div>
  );
}
