'use client';

/**
 * BenefitStatusTracker - Pipeline visual de 4 etapas por benefício
 * Persistência via localStorage
 */

import { useState, useEffect } from 'react';

interface Props {
  benefitId: string;
  benefitName: string;
}

interface TrackerState {
  documentsReady: boolean;
  requested: boolean;
  receiving: boolean;
}

const STORAGE_KEY = 'tnm-benefit-tracker';

function loadState(benefitId: string): TrackerState {
  try {
    const stored = localStorage.getItem(STORAGE_KEY);
    if (stored) {
      const all = JSON.parse(stored);
      return all[benefitId] || { documentsReady: false, requested: false, receiving: false };
    }
  } catch {
    // ignore parse errors
  }
  return { documentsReady: false, requested: false, receiving: false };
}

function saveState(benefitId: string, state: TrackerState) {
  try {
    const stored = localStorage.getItem(STORAGE_KEY);
    const all = stored ? JSON.parse(stored) : {};
    all[benefitId] = state;
    localStorage.setItem(STORAGE_KEY, JSON.stringify(all));
  } catch {
    // ignore storage errors
  }
}

const STEPS = [
  { key: 'discovered', label: 'Descoberto', icon: '🔍' },
  { key: 'documentsReady', label: 'Documentos', icon: '📋' },
  { key: 'requested', label: 'Solicitado', icon: '📍' },
  { key: 'receiving', label: 'Recebendo', icon: '✅' },
] as const;

export default function BenefitStatusTracker({ benefitId, benefitName }: Props) {
  const [state, setState] = useState<TrackerState>(() => loadState(benefitId));
  const [expanded, setExpanded] = useState(false);

  useEffect(() => {
    saveState(benefitId, state);
  }, [benefitId, state]);

  const toggle = (field: keyof TrackerState) => {
    setState(prev => {
      const next = { ...prev };
      next[field] = !prev[field];
      // Cascading: unchecking a step unchecks subsequent steps
      if (field === 'documentsReady' && !next.documentsReady) {
        next.requested = false;
        next.receiving = false;
      }
      if (field === 'requested' && !next.requested) {
        next.receiving = false;
      }
      return next;
    });
  };

  const completedSteps = 1 + (state.documentsReady ? 1 : 0) + (state.requested ? 1 : 0) + (state.receiving ? 1 : 0);
  const progressPercent = (completedSteps / STEPS.length) * 100;

  const isStepComplete = (key: string) => {
    if (key === 'discovered') return true;
    return state[key as keyof TrackerState];
  };

  const isStepClickable = (key: string) => {
    if (key === 'discovered') return false;
    if (key === 'documentsReady') return true;
    if (key === 'requested') return state.documentsReady;
    if (key === 'receiving') return state.requested;
    return false;
  };

  return (
    <div className="mt-2">
      <button
        onClick={() => setExpanded(!expanded)}
        className="flex items-center gap-2 text-xs text-emerald-600 hover:text-emerald-500 transition-colors"
        aria-label={`Acompanhar progresso de ${benefitName}`}
      >
        <div className="flex-1 h-1.5 bg-[var(--border-color)] rounded-full overflow-hidden w-20">
          <div
            className="h-full bg-emerald-500 transition-all duration-300"
            style={{ width: `${progressPercent}%` }}
          />
        </div>
        <span>{completedSteps}/{STEPS.length} etapas</span>
        <span className="text-[var(--text-tertiary)]">{expanded ? '▲' : '▼'}</span>
      </button>

      {expanded && (
        <div className="mt-3 p-3 rounded-lg bg-[var(--badge-bg)] border border-[var(--border-color)]">
          <div className="flex items-center justify-between gap-1">
            {STEPS.map((step, i) => {
              const complete = isStepComplete(step.key);
              const clickable = isStepClickable(step.key);

              return (
                <div key={step.key} className="flex items-center flex-1">
                  <button
                    onClick={() => clickable && toggle(step.key as keyof TrackerState)}
                    disabled={!clickable}
                    className={`flex flex-col items-center gap-1 flex-1 p-1 rounded transition-colors ${
                      clickable ? 'cursor-pointer hover:bg-[var(--hover-bg)]' : 'cursor-default'
                    }`}
                    title={clickable ? `Marcar "${step.label}" como ${complete ? 'pendente' : 'concluido'}` : step.label}
                  >
                    <div className={`w-8 h-8 rounded-full flex items-center justify-center text-sm border-2 transition-colors ${
                      complete
                        ? 'bg-emerald-500 border-emerald-500 text-white'
                        : 'bg-[var(--bg-card)] border-[var(--border-color)] text-[var(--text-tertiary)]'
                    }`}>
                      {complete ? '✓' : step.icon}
                    </div>
                    <span className={`text-[10px] text-center leading-tight ${
                      complete ? 'text-emerald-600 font-medium' : 'text-[var(--text-tertiary)]'
                    }`}>
                      {step.label}
                    </span>
                  </button>
                  {i < STEPS.length - 1 && (
                    <div className={`h-0.5 w-3 flex-shrink-0 ${
                      isStepComplete(STEPS[i + 1].key) ? 'bg-emerald-500' : 'bg-[var(--border-color)]'
                    }`} />
                  )}
                </div>
              );
            })}
          </div>
        </div>
      )}
    </div>
  );
}
