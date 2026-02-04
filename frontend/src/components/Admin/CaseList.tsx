'use client';

/**
 * CaseList - Lista de casos do sistema Anjo Social
 * Usado no painel do assessor para visualizar e gerenciar casos.
 */

import { useState } from 'react';

interface CaseNote {
  id: string;
  author: string;
  content: string;
  createdAt: string;
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
  notes: CaseNote[];
  createdAt: string;
  updatedAt: string;
  resolvedAt: string | null;
}

interface CaseListProps {
  cases: CaseData[];
  onUpdateStatus: (caseId: string, status: string) => void;
  onAddNote: (caseId: string, content: string) => void;
}

const STATUS_LABELS: Record<string, string> = {
  open: 'Aberto',
  assigned: 'Atribuído',
  in_progress: 'Em Andamento',
  resolved: 'Resolvido',
  closed: 'Encerrado',
};

const STATUS_COLORS: Record<string, string> = {
  open: 'bg-yellow-500/20 text-yellow-400',
  assigned: 'bg-blue-500/20 text-blue-400',
  in_progress: 'bg-purple-500/20 text-purple-400',
  resolved: 'bg-emerald-500/20 text-emerald-400',
  closed: 'bg-slate-500/20 text-slate-400',
};

const PRIORITY_LABELS: Record<string, string> = {
  low: 'Baixa',
  medium: 'Média',
  high: 'Alta',
  emergency: 'Emergência',
};

const PRIORITY_COLORS: Record<string, string> = {
  low: 'bg-slate-500/20 text-slate-400',
  medium: 'bg-blue-500/20 text-blue-400',
  high: 'bg-orange-500/20 text-orange-400',
  emergency: 'bg-red-500/20 text-red-400',
};

const STATUS_FLOW = ['open', 'assigned', 'in_progress', 'resolved', 'closed'];

export default function CaseList({ cases, onUpdateStatus, onAddNote }: CaseListProps) {
  const [expandedCase, setExpandedCase] = useState<string | null>(null);
  const [noteText, setNoteText] = useState('');
  const [filterStatus, setFilterStatus] = useState<string>('all');
  const [filterPriority, setFilterPriority] = useState<string>('all');

  const filtered = cases.filter((c) => {
    if (filterStatus !== 'all' && c.status !== filterStatus) return false;
    if (filterPriority !== 'all' && c.priority !== filterPriority) return false;
    return true;
  });

  const handleAddNote = (caseId: string) => {
    if (!noteText.trim()) return;
    onAddNote(caseId, noteText.trim());
    setNoteText('');
  };

  const getNextStatus = (current: string): string | null => {
    const idx = STATUS_FLOW.indexOf(current);
    if (idx < 0 || idx >= STATUS_FLOW.length - 1) return null;
    return STATUS_FLOW[idx + 1];
  };

  return (
    <div className="space-y-4">
      {/* Filters */}
      <div className="flex flex-wrap gap-3">
        <select
          value={filterStatus}
          onChange={(e) => setFilterStatus(e.target.value)}
          className="bg-slate-800 border border-slate-700 rounded-lg px-3 py-2 text-sm text-slate-200"
        >
          <option value="all">Todos os status</option>
          {Object.entries(STATUS_LABELS).map(([k, v]) => (
            <option key={k} value={k}>{v}</option>
          ))}
        </select>

        <select
          value={filterPriority}
          onChange={(e) => setFilterPriority(e.target.value)}
          className="bg-slate-800 border border-slate-700 rounded-lg px-3 py-2 text-sm text-slate-200"
        >
          <option value="all">Todas as prioridades</option>
          {Object.entries(PRIORITY_LABELS).map(([k, v]) => (
            <option key={k} value={k}>{v}</option>
          ))}
        </select>

        <span className="ml-auto text-sm text-slate-400 self-center">
          {filtered.length} caso{filtered.length !== 1 ? 's' : ''}
        </span>
      </div>

      {/* Case Cards */}
      {filtered.length === 0 ? (
        <div className="text-center py-12 text-slate-400">
          Nenhum caso encontrado com os filtros selecionados.
        </div>
      ) : (
        filtered.map((c) => {
          const isExpanded = expandedCase === c.id;
          const nextStatus = getNextStatus(c.status);

          return (
            <div
              key={c.id}
              className="bg-slate-800/50 border border-slate-700 rounded-xl overflow-hidden"
            >
              {/* Header */}
              <button
                onClick={() => setExpandedCase(isExpanded ? null : c.id)}
                className="w-full flex items-center gap-3 p-4 text-left hover:bg-slate-700/30 transition-colors"
              >
                {/* Priority indicator */}
                <div className={`w-2 h-10 rounded-full ${
                  c.priority === 'emergency' ? 'bg-red-500' :
                  c.priority === 'high' ? 'bg-orange-500' :
                  c.priority === 'medium' ? 'bg-blue-500' : 'bg-slate-500'
                }`} />

                <div className="flex-1 min-w-0">
                  <div className="flex items-center gap-2 flex-wrap">
                    <span className={`px-2 py-0.5 rounded text-xs font-medium ${STATUS_COLORS[c.status] || ''}`}>
                      {STATUS_LABELS[c.status] || c.status}
                    </span>
                    <span className={`px-2 py-0.5 rounded text-xs font-medium ${PRIORITY_COLORS[c.priority] || ''}`}>
                      {PRIORITY_LABELS[c.priority] || c.priority}
                    </span>
                    <span className="text-xs text-slate-500 font-mono">
                      #{c.id.slice(0, 8)}
                    </span>
                  </div>
                  <p className="text-sm text-slate-200 mt-1 truncate">{c.escalationReason}</p>
                </div>

                <div className="text-right shrink-0">
                  <div className="flex flex-wrap gap-1 justify-end">
                    {c.benefits.slice(0, 3).map((b) => (
                      <span key={b} className="px-1.5 py-0.5 bg-emerald-500/10 text-emerald-400 rounded text-xs">
                        {b.replace(/_/g, ' ')}
                      </span>
                    ))}
                    {c.benefits.length > 3 && (
                      <span className="text-xs text-slate-500">+{c.benefits.length - 3}</span>
                    )}
                  </div>
                  <p className="text-xs text-slate-500 mt-1">
                    {new Date(c.createdAt).toLocaleDateString('pt-BR')}
                  </p>
                </div>

                <svg
                  className={`w-5 h-5 text-slate-400 transition-transform ${isExpanded ? 'rotate-180' : ''}`}
                  fill="none"
                  stroke="currentColor"
                  viewBox="0 0 24 24"
                >
                  <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M19 9l-7 7-7-7" />
                </svg>
              </button>

              {/* Expanded Content */}
              {isExpanded && (
                <div className="border-t border-slate-700 p-4 space-y-4">
                  {/* Context */}
                  {c.citizenContext && (
                    <div className="text-sm text-slate-300">
                      <span className="text-slate-500 text-xs uppercase tracking-wide">Contexto</span>
                      <div className="mt-1 flex flex-wrap gap-2">
                        {Object.entries(c.citizenContext).map(([k, v]) => (
                          <span key={k} className="px-2 py-1 bg-slate-700/50 rounded text-xs">
                            {k}: {String(v)}
                          </span>
                        ))}
                      </div>
                    </div>
                  )}

                  {/* Notes */}
                  <div>
                    <span className="text-slate-500 text-xs uppercase tracking-wide">
                      Notas ({c.notes.length})
                    </span>
                    <div className="mt-2 space-y-2 max-h-48 overflow-y-auto">
                      {c.notes.map((n) => (
                        <div
                          key={n.id}
                          className={`p-2 rounded-lg text-sm ${
                            n.author === 'sistema'
                              ? 'bg-slate-700/30 text-slate-400 italic'
                              : 'bg-slate-700/50 text-slate-200'
                          }`}
                        >
                          <div className="flex justify-between text-xs text-slate-500 mb-1">
                            <span>{n.author}</span>
                            <span>{new Date(n.createdAt).toLocaleString('pt-BR')}</span>
                          </div>
                          {n.content}
                        </div>
                      ))}
                    </div>

                    {/* Add note */}
                    <div className="mt-3 flex gap-2">
                      <input
                        type="text"
                        value={noteText}
                        onChange={(e) => setNoteText(e.target.value)}
                        onKeyDown={(e) => e.key === 'Enter' && handleAddNote(c.id)}
                        placeholder="Adicionar nota..."
                        className="flex-1 bg-slate-700 border border-slate-600 rounded-lg px-3 py-2 text-sm text-slate-200 placeholder-slate-500"
                      />
                      <button
                        onClick={() => handleAddNote(c.id)}
                        className="px-4 py-2 bg-emerald-600 hover:bg-emerald-500 rounded-lg text-sm font-medium transition-colors"
                      >
                        Enviar
                      </button>
                    </div>
                  </div>

                  {/* Actions */}
                  <div className="flex gap-2 pt-2 border-t border-slate-700">
                    {nextStatus && (
                      <button
                        onClick={() => onUpdateStatus(c.id, nextStatus)}
                        className="px-4 py-2 bg-blue-600 hover:bg-blue-500 rounded-lg text-sm font-medium transition-colors"
                      >
                        Mover para: {STATUS_LABELS[nextStatus]}
                      </button>
                    )}
                    {c.status !== 'resolved' && c.status !== 'closed' && (
                      <button
                        onClick={() => onUpdateStatus(c.id, 'resolved')}
                        className="px-4 py-2 bg-emerald-600 hover:bg-emerald-500 rounded-lg text-sm font-medium transition-colors"
                      >
                        Marcar Resolvido
                      </button>
                    )}
                  </div>
                </div>
              )}
            </div>
          );
        })
      )}
    </div>
  );
}
