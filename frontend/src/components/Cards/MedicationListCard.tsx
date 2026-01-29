/**
 * MedicationListCard - Renders a list of medications
 */

import { MedicationListData } from '../../api/chatClient';

interface Props {
  data: MedicationListData;
}

export default function MedicationListCard({ data }: Props) {
  return (
    <div className="bg-slate-800/50 rounded-xl border border-slate-700 overflow-hidden">
      {/* Header */}
      <div className="bg-gradient-to-r from-blue-600 to-indigo-600 px-4 py-3">
        <h3 className="font-semibold text-white flex items-center gap-2">
          <span className="text-lg">💊</span>
          Medicamentos Identificados
        </h3>
        {data.estimated_savings && (
          <span className="text-xs text-blue-100">
            Economia estimada: {data.estimated_savings}
          </span>
        )}
      </div>

      {/* Medications */}
      <div className="p-4 space-y-3">
        {data.medications.map((med, index) => (
          <div
            key={index}
            className="flex items-center gap-3 p-3 rounded-lg bg-slate-700/30"
          >
            {/* Icon */}
            <div className={`w-10 h-10 rounded-full flex items-center justify-center ${
              med.free ? 'bg-emerald-500/20' : 'bg-slate-600'
            }`}>
              <span className="text-lg">💊</span>
            </div>

            {/* Info */}
            <div className="flex-1 min-w-0">
              <p className="font-medium text-slate-200">
                {med.name}
              </p>
              <p className="text-xs text-slate-400">
                {med.dosage}
                {med.quantity && ` • ${med.quantity} unidades`}
              </p>
            </div>

            {/* Status */}
            <div className="flex-shrink-0 text-right">
              {med.free ? (
                <span className="inline-flex items-center gap-1 px-2 py-1 rounded-full bg-emerald-500/20 text-emerald-400 text-xs font-medium">
                  <svg className="w-3 h-3" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                    <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M5 13l4 4L19 7" />
                  </svg>
                  Gratuito
                </span>
              ) : (
                <span className="inline-flex items-center gap-1 px-2 py-1 rounded-full bg-amber-500/20 text-amber-400 text-xs font-medium">
                  Com desconto
                </span>
              )}
              {med.available === false && (
                <span className="block mt-1 text-xs text-red-400">
                  Indisponível
                </span>
              )}
            </div>
          </div>
        ))}
      </div>

      {/* Footer */}
      {data.all_free && (
        <div className="px-4 py-3 bg-emerald-500/10 border-t border-emerald-500/30">
          <p className="text-sm text-emerald-400 flex items-center gap-2">
            <svg className="w-4 h-4" fill="none" viewBox="0 0 24 24" stroke="currentColor">
              <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M9 12l2 2 4-4m6 2a9 9 0 11-18 0 9 9 0 0118 0z" />
            </svg>
            Todos os medicamentos são gratuitos pelo Farmácia Popular!
          </p>
        </div>
      )}
    </div>
  );
}
