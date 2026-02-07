'use client';

import { useState, useEffect, useCallback } from 'react';

// --- Types ---

interface JourneyStage {
  stage: number;
  name: string;
  description: string;
  actions: string[];
  timeEstimate: string;
}

interface SupportChannel {
  type: 'phone' | 'app' | 'website';
  name: string;
  contact: string;
}

export interface Journey {
  benefitId: string;
  benefitName: string;
  totalTimeEstimate: string;
  stages: JourneyStage[];
  pitfalls: string[];
  supportChannels: SupportChannel[];
}

interface JourneyProgress {
  completedActions: Record<number, boolean[]>;
}

const STORAGE_KEY = 'tnm-journey-progress';

function loadProgress(benefitId: string): JourneyProgress {
  if (typeof window === 'undefined') return { completedActions: {} };
  try {
    const raw = localStorage.getItem(STORAGE_KEY);
    if (!raw) return { completedActions: {} };
    const all = JSON.parse(raw) as Record<string, JourneyProgress>;
    return all[benefitId] || { completedActions: {} };
  } catch {
    return { completedActions: {} };
  }
}

function saveProgress(benefitId: string, progress: JourneyProgress) {
  if (typeof window === 'undefined') return;
  try {
    const raw = localStorage.getItem(STORAGE_KEY);
    const all = raw ? (JSON.parse(raw) as Record<string, JourneyProgress>) : {};
    all[benefitId] = progress;
    localStorage.setItem(STORAGE_KEY, JSON.stringify(all));
  } catch {
    // localStorage may be disabled
  }
}

// --- Sub-components ---

function StageCard({
  stage,
  isCompleted,
  isCurrent,
  isLast,
  isExpanded,
  onToggle,
  completedActions,
  onToggleAction,
}: {
  stage: JourneyStage;
  isCompleted: boolean;
  isCurrent: boolean;
  isLast: boolean;
  isExpanded: boolean;
  onToggle: () => void;
  completedActions: boolean[];
  onToggleAction: (actionIdx: number) => void;
}) {
  const panelId = `stage-panel-${stage.stage}`;
  const headerId = `stage-header-${stage.stage}`;

  return (
    <div className="flex gap-3">
      {/* Timeline column */}
      <div className="flex flex-col items-center">
        {/* Circle */}
        <button
          onClick={onToggle}
          className={`w-10 h-10 rounded-full flex items-center justify-center flex-shrink-0 font-semibold text-sm transition-colors focus:outline-none focus:ring-2 focus:ring-emerald-500 focus:ring-offset-2 ${
            isCompleted
              ? 'bg-emerald-500 text-white'
              : isCurrent
              ? 'border-2 border-emerald-500 bg-emerald-50 text-emerald-700'
              : 'border-2 border-[var(--border-color)] text-[var(--text-tertiary)]'
          }`}
          aria-label={`Etapa ${stage.stage}: ${stage.name}`}
        >
          {isCompleted ? (
            <svg className="w-5 h-5" fill="none" stroke="currentColor" viewBox="0 0 24 24">
              <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2.5} d="M5 13l4 4L19 7" />
            </svg>
          ) : (
            stage.stage
          )}
        </button>
        {/* Vertical line */}
        {!isLast && (
          <div className={`w-0.5 flex-1 min-h-[24px] ${isCompleted ? 'bg-emerald-500' : 'bg-[var(--border-color)]'}`} />
        )}
      </div>

      {/* Content column */}
      <div className="flex-1 pb-6">
        <button
          id={headerId}
          onClick={onToggle}
          aria-expanded={isExpanded}
          aria-controls={panelId}
          className="w-full text-left focus:outline-none focus:ring-2 focus:ring-emerald-500 focus:ring-offset-2 rounded-lg -ml-1 pl-1"
        >
          <div className="flex items-center justify-between gap-2">
            <h3
              className={`font-semibold ${
                isCurrent ? 'text-[var(--text-primary)]' : 'text-[var(--text-secondary)]'
              }`}
              style={isCurrent ? { backgroundImage: 'linear-gradient(transparent 55%, #6ee7b7 55%)', display: 'inline' } : undefined}
            >
              {stage.name}
            </h3>
            <span className="px-2 py-0.5 rounded-full bg-blue-500/10 text-blue-600 text-xs whitespace-nowrap flex-shrink-0">
              {stage.timeEstimate}
            </span>
          </div>
        </button>

        {isExpanded && (
          <div
            id={panelId}
            role="region"
            aria-labelledby={headerId}
            className="mt-3 space-y-3"
          >
            <p className="text-sm text-[var(--text-secondary)]">{stage.description}</p>

            {stage.actions.length > 0 && (
              <div className="space-y-2">
                <p className="text-xs font-medium text-[var(--text-tertiary)] uppercase tracking-wide">O que fazer:</p>
                {stage.actions.map((action, idx) => (
                  <label
                    key={idx}
                    className="flex items-start gap-3 p-2 rounded-lg hover:bg-[var(--hover-bg)] cursor-pointer transition-colors"
                  >
                    <input
                      type="checkbox"
                      checked={completedActions[idx] || false}
                      onChange={() => onToggleAction(idx)}
                      className="mt-0.5 w-4 h-4 rounded border-gray-300 text-emerald-600 focus:ring-emerald-500 accent-emerald-600"
                    />
                    <span className={`text-sm ${completedActions[idx] ? 'line-through text-[var(--text-tertiary)]' : 'text-[var(--text-secondary)]'}`}>
                      {action}
                    </span>
                  </label>
                ))}
              </div>
            )}
          </div>
        )}
      </div>
    </div>
  );
}

function PitfallsSection({ pitfalls }: { pitfalls: string[] }) {
  if (pitfalls.length === 0) return null;

  return (
    <section className="mt-8">
      <h2 className="text-lg font-semibold text-[var(--text-primary)] mb-4 flex items-center gap-2">
        <span>⚠️</span> Cuidado!
      </h2>
      <div className="space-y-2">
        {pitfalls.map((pitfall, idx) => (
          <div
            key={idx}
            className="p-3 rounded-lg bg-amber-500/10 border border-amber-500/30 text-sm text-amber-800 dark:text-amber-300"
          >
            {pitfall}
          </div>
        ))}
      </div>
    </section>
  );
}

function SupportSection({ channels }: { channels: SupportChannel[] }) {
  if (channels.length === 0) return null;

  const getHref = (channel: SupportChannel) => {
    if (channel.type === 'phone') {
      const digits = channel.contact.replace(/\D/g, '');
      return `tel:${digits}`;
    }
    if (channel.contact.startsWith('http')) return channel.contact;
    return `https://${channel.contact}`;
  };

  const getIcon = (type: string) => {
    switch (type) {
      case 'phone': return '📞';
      case 'app': return '📱';
      case 'website': return '🌐';
      default: return '💬';
    }
  };

  return (
    <section className="mt-8">
      <h2 className="text-lg font-semibold text-[var(--text-primary)] mb-4 flex items-center gap-2">
        <span>🆘</span> Precisa de ajuda?
      </h2>
      <div className="space-y-2">
        {channels.map((channel, idx) => (
          <a
            key={idx}
            href={getHref(channel)}
            target={channel.type !== 'phone' ? '_blank' : undefined}
            rel={channel.type !== 'phone' ? 'noopener noreferrer' : undefined}
            className="flex items-center gap-3 p-3 rounded-lg bg-[var(--bg-card)] border border-[var(--border-color)] hover:bg-[var(--hover-bg)] transition-colors"
          >
            <span className="text-lg">{getIcon(channel.type)}</span>
            <div>
              <p className="text-sm font-medium text-[var(--text-primary)]">{channel.name}</p>
              <p className="text-xs text-[var(--text-tertiary)]">{channel.contact}</p>
            </div>
          </a>
        ))}
      </div>
    </section>
  );
}

// --- Main component ---

export default function JourneyFlow({ journey }: { journey: Journey }) {
  const [expandedStage, setExpandedStage] = useState<number | null>(1);
  const [progress, setProgress] = useState<JourneyProgress>({ completedActions: {} });

  useEffect(() => {
    setProgress(loadProgress(journey.benefitId));
  }, [journey.benefitId]);

  const completedStagesCount = journey.stages.filter((s) => {
    const actions = progress.completedActions[s.stage];
    return actions && s.actions.length > 0 && actions.every(Boolean) && actions.filter(Boolean).length === s.actions.length;
  }).length;

  const isStageCompleted = (stage: JourneyStage) => {
    const actions = progress.completedActions[stage.stage];
    return actions && stage.actions.length > 0 && actions.every(Boolean) && actions.filter(Boolean).length === stage.actions.length;
  };

  const getCurrentStage = () => {
    for (const stage of journey.stages) {
      if (!isStageCompleted(stage)) return stage.stage;
    }
    return journey.stages.length + 1; // all completed
  };

  const toggleAction = useCallback(
    (stageNum: number, actionIdx: number) => {
      setProgress((prev) => {
        const stageActions = [...(prev.completedActions[stageNum] || [])];
        stageActions[actionIdx] = !stageActions[actionIdx];
        const next = {
          completedActions: { ...prev.completedActions, [stageNum]: stageActions },
        };
        saveProgress(journey.benefitId, next);
        return next;
      });
    },
    [journey.benefitId]
  );

  const currentStage = getCurrentStage();

  return (
    <div>
      {/* Header */}
      <div className="mb-8">
        <div className="flex items-center justify-between mb-2">
          <h2 className="text-xl font-bold text-[var(--text-primary)]">
            Passo a passo
          </h2>
          <span className="px-2 py-0.5 rounded-full bg-blue-500/10 text-blue-600 text-xs">
            {journey.totalTimeEstimate}
          </span>
        </div>
        {/* Progress bar */}
        <div className="flex items-center gap-3">
          <div className="flex-1 h-2 rounded-full bg-[var(--border-color)] overflow-hidden">
            <div
              className="h-full bg-emerald-500 rounded-full transition-all duration-500"
              style={{ width: `${(completedStagesCount / journey.stages.length) * 100}%` }}
            />
          </div>
          <span
            className="text-sm font-medium text-[var(--text-secondary)]"
            aria-live="polite"
          >
            {completedStagesCount}/{journey.stages.length}
          </span>
        </div>
      </div>

      {/* Timeline */}
      <div>
        {journey.stages.map((stage, idx) => (
          <StageCard
            key={stage.stage}
            stage={stage}
            isCompleted={isStageCompleted(stage)}
            isCurrent={stage.stage === currentStage}
            isLast={idx === journey.stages.length - 1}
            isExpanded={expandedStage === stage.stage}
            onToggle={() => setExpandedStage(expandedStage === stage.stage ? null : stage.stage)}
            completedActions={progress.completedActions[stage.stage] || []}
            onToggleAction={(actionIdx) => toggleAction(stage.stage, actionIdx)}
          />
        ))}
      </div>

      {/* Pitfalls */}
      <PitfallsSection pitfalls={journey.pitfalls} />

      {/* Support */}
      <SupportSection channels={journey.supportChannels} />
    </div>
  );
}
