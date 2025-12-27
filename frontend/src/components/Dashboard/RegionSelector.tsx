/**
 * Region selector component for filtering by Brazilian regions
 */

import { useDashboardStore, RegionCode } from '../../stores/dashboardStore';

const REGIONS = [
  { code: null as RegionCode, label: 'Brasil', icon: '🇧🇷' },
  { code: 'N' as RegionCode, label: 'Norte', icon: '🌳' },
  { code: 'NE' as RegionCode, label: 'Nordeste', icon: '☀️' },
  { code: 'CO' as RegionCode, label: 'Centro-Oeste', icon: '🌾' },
  { code: 'SE' as RegionCode, label: 'Sudeste', icon: '🏙️' },
  { code: 'S' as RegionCode, label: 'Sul', icon: '❄️' },
];

export default function RegionSelector() {
  const { selectedRegion, selectRegion } = useDashboardStore();

  return (
    <div className="flex flex-wrap gap-1">
      {REGIONS.map((region) => (
        <button
          key={region.code || 'all'}
          onClick={() => selectRegion(region.code)}
          className={`px-2 py-1 text-xs rounded-md transition-colors flex items-center gap-1 ${
            selectedRegion === region.code
              ? 'bg-indigo-600 text-white'
              : 'text-slate-400 hover:text-white hover:bg-slate-700'
          }`}
          title={region.label}
        >
          <span>{region.icon}</span>
          <span className="hidden sm:inline">{region.label}</span>
        </button>
      ))}
    </div>
  );
}
