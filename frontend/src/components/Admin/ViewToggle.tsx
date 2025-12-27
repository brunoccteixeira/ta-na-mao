/**
 * Toggle between Citizen and Admin view modes
 */

import { useDashboardStore } from '../../stores/dashboardStore';

export default function ViewToggle() {
  const { viewMode, setViewMode } = useDashboardStore();

  return (
    <div className="flex items-center gap-1 bg-slate-800 rounded-lg p-0.5">
      <button
        onClick={() => setViewMode('citizen')}
        className={`px-3 py-1.5 text-sm rounded-md transition-colors flex items-center gap-1.5 ${
          viewMode === 'citizen'
            ? 'bg-emerald-600 text-white'
            : 'text-slate-400 hover:text-white'
        }`}
      >
        <span>Cidadao</span>
      </button>
      <button
        onClick={() => setViewMode('admin')}
        className={`px-3 py-1.5 text-sm rounded-md transition-colors flex items-center gap-1.5 ${
          viewMode === 'admin'
            ? 'bg-blue-600 text-white'
            : 'text-slate-400 hover:text-white'
        }`}
      >
        <span>Admin</span>
      </button>
    </div>
  );
}
