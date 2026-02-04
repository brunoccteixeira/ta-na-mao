'use client';

/**
 * Export button for downloading data in CSV/JSON format
 */

import { useState } from 'react';
import { downloadExport } from '../../api/client';
import { useDashboardStore } from '../../stores/dashboardStore';

export default function ExportButton() {
  const { selectedProgram, selectedState } = useDashboardStore();
  const [isExporting, setIsExporting] = useState(false);
  const [showMenu, setShowMenu] = useState(false);

  const handleExport = async (format: 'csv' | 'json') => {
    setIsExporting(true);
    setShowMenu(false);
    try {
      await downloadExport({
        format,
        scope: selectedState ? 'state' : 'national',
        state_code: selectedState || undefined,
        program: selectedProgram || undefined,
      });
    } catch (error) {
      console.error('Export failed:', error);
      alert('Erro ao exportar dados. Tente novamente.');
    } finally {
      setIsExporting(false);
    }
  };

  return (
    <div className="relative">
      <button
        onClick={() => setShowMenu(!showMenu)}
        disabled={isExporting}
        className={`px-3 py-1.5 text-sm rounded-lg flex items-center gap-2 transition-colors ${
          isExporting
            ? 'bg-slate-700 text-slate-400 cursor-wait'
            : 'bg-emerald-600 hover:bg-emerald-500 text-white'
        }`}
      >
        {isExporting ? (
          <>
            <span className="animate-spin">...</span>
            Exportando
          </>
        ) : (
          <>
            <svg
              xmlns="http://www.w3.org/2000/svg"
              className="h-4 w-4"
              fill="none"
              viewBox="0 0 24 24"
              stroke="currentColor"
            >
              <path
                strokeLinecap="round"
                strokeLinejoin="round"
                strokeWidth={2}
                d="M4 16v1a3 3 0 003 3h10a3 3 0 003-3v-1m-4-4l-4 4m0 0l-4-4m4 4V4"
              />
            </svg>
            Exportar
          </>
        )}
      </button>

      {/* Dropdown Menu */}
      {showMenu && !isExporting && (
        <>
          {/* Backdrop */}
          <div className="fixed inset-0 z-10" onClick={() => setShowMenu(false)} />

          {/* Menu */}
          <div className="absolute right-0 mt-2 w-48 bg-slate-800 rounded-lg shadow-lg border border-slate-700 z-20">
            <div className="p-2">
              <div className="text-xs text-slate-400 px-2 py-1 mb-1">
                Escopo: {selectedState ? `Estado ${selectedState}` : 'Nacional'}
              </div>

              <button
                onClick={() => handleExport('csv')}
                className="w-full text-left px-3 py-2 text-sm rounded hover:bg-slate-700 flex items-center gap-2 transition-colors"
              >
                <span className="text-emerald-400">CSV</span>
                <span className="text-slate-400">Planilha</span>
              </button>

              <button
                onClick={() => handleExport('json')}
                className="w-full text-left px-3 py-2 text-sm rounded hover:bg-slate-700 flex items-center gap-2 transition-colors"
              >
                <span className="text-blue-400">JSON</span>
                <span className="text-slate-400">Dados estruturados</span>
              </button>
            </div>

            <div className="border-t border-slate-700 p-2">
              <div className="text-xs text-slate-500 px-2">
                {selectedProgram
                  ? `Programa: ${selectedProgram}`
                  : 'Todos os programas'}
              </div>
            </div>
          </div>
        </>
      )}
    </div>
  );
}
