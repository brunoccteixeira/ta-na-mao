/**
 * Program selector component with freshness indicators
 */

import { useQuery } from '@tanstack/react-query';
import { useDashboardStore, ProgramCode } from '../../stores/dashboardStore';
import { fetchPrograms } from '../../api/client';

const PROGRAMS = [
  { code: null, label: 'Todos', icon: '📊' },
  { code: 'TSEE', label: 'TSEE', icon: '⚡' },
  { code: 'FARMACIA_POPULAR', label: 'Farmácia', icon: '💊' },
  { code: 'DIGNIDADE_MENSTRUAL', label: 'Dignidade', icon: '🩺' },
  { code: 'PIS_PASEP', label: 'PIS/PASEP', icon: '💰' },
] as const;

function getDaysAgo(dateStr: string | null | undefined): string | null {
  if (!dateStr) return null;
  const date = new Date(dateStr);
  const now = new Date();
  const diffTime = Math.abs(now.getTime() - date.getTime());
  const diffDays = Math.ceil(diffTime / (1000 * 60 * 60 * 24));

  if (diffDays === 0) return 'hoje';
  if (diffDays === 1) return '1 dia';
  if (diffDays < 30) return `${diffDays} dias`;
  if (diffDays < 60) return '1 mês';
  return `${Math.floor(diffDays / 30)} meses`;
}

export default function ProgramSelector() {
  const { selectedProgram, setProgram } = useDashboardStore();

  const { data: programsData } = useQuery({
    queryKey: ['programs'],
    queryFn: fetchPrograms,
    staleTime: 1000 * 60 * 60, // 1 hour
  });

  // Create a map of program freshness
  const freshnessMap: Record<string, string | null> = {};
  if (programsData) {
    for (const p of programsData) {
      const latestDate = p.national_stats?.latest_data_date;
      freshnessMap[p.code] = getDaysAgo(latestDate);
    }
  }

  return (
    <div className="flex flex-wrap gap-1 p-1 bg-slate-800 rounded-lg">
      {PROGRAMS.map((program) => {
        const freshness = program.code ? freshnessMap[program.code] : null;
        const hasData = program.code ? !!freshnessMap[program.code] : true;

        return (
          <button
            key={program.code || 'all'}
            onClick={() => setProgram(program.code as ProgramCode)}
            className={`px-3 py-1.5 text-xs rounded-md transition-colors flex items-center gap-1 ${
              selectedProgram === program.code
                ? 'bg-teal-600 text-white'
                : hasData
                  ? 'text-slate-400 hover:text-white hover:bg-slate-700'
                  : 'text-slate-600 hover:text-slate-400 hover:bg-slate-700/50'
            }`}
            title={freshness ? `Atualizado há ${freshness}` : program.code ? 'Sem dados' : 'Todos os programas'}
          >
            <span>{program.icon}</span>
            <span>{program.label}</span>
            {selectedProgram === program.code && freshness && (
              <span className="ml-1 px-1.5 py-0.5 bg-teal-700 rounded text-[10px]">
                {freshness}
              </span>
            )}
          </button>
        );
      })}
    </div>
  );
}
