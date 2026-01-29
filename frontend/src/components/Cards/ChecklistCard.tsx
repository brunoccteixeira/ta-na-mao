/**
 * ChecklistCard - Renders a document checklist
 */

import { ChecklistData } from '../../api/chatClient';

interface Props {
  data: ChecklistData;
}

export default function ChecklistCard({ data }: Props) {
  return (
    <div className="bg-slate-800/50 rounded-xl border border-slate-700 overflow-hidden">
      {/* Header */}
      <div className="bg-gradient-to-r from-teal-600 to-emerald-600 px-4 py-3">
        <h3 className="font-semibold text-white flex items-center gap-2">
          <span className="text-lg">📋</span>
          {data.title}
        </h3>
        {data.program && (
          <span className="text-xs text-teal-100 opacity-80">
            {data.program}
          </span>
        )}
      </div>

      {/* Items */}
      <div className="p-4 space-y-3">
        {data.items.map((item, index) => (
          <div
            key={index}
            className={`flex items-start gap-3 p-3 rounded-lg ${
              item.required
                ? 'bg-amber-500/10 border border-amber-500/30'
                : 'bg-slate-700/30'
            }`}
          >
            {/* Checkbox / Status */}
            <div className="flex-shrink-0 mt-0.5">
              {item.checked ? (
                <div className="w-5 h-5 rounded-full bg-emerald-500 flex items-center justify-center">
                  <svg className="w-3 h-3 text-white" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                    <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={3} d="M5 13l4 4L19 7" />
                  </svg>
                </div>
              ) : item.required ? (
                <div className="w-5 h-5 rounded-full border-2 border-amber-500 flex items-center justify-center">
                  <span className="text-amber-500 text-xs font-bold">!</span>
                </div>
              ) : (
                <div className="w-5 h-5 rounded-full border-2 border-slate-500" />
              )}
            </div>

            {/* Content */}
            <div className="flex-1 min-w-0">
              <p className={`text-sm ${item.checked ? 'text-slate-400 line-through' : 'text-slate-200'}`}>
                {item.text}
              </p>
              {item.hint && (
                <p className="text-xs text-slate-400 mt-1 flex items-center gap-1">
                  <span>💡</span>
                  {item.hint}
                </p>
              )}
            </div>

            {/* Required badge */}
            {item.required && !item.checked && (
              <span className="flex-shrink-0 text-xs px-2 py-0.5 rounded-full bg-amber-500/20 text-amber-400 font-medium">
                Obrigatório
              </span>
            )}
          </div>
        ))}
      </div>

      {/* Footer summary */}
      <div className="px-4 py-3 bg-slate-800/50 border-t border-slate-700">
        <div className="flex items-center justify-between text-xs">
          <span className="text-slate-400">
            {data.items.filter(i => i.required).length} obrigatórios
          </span>
          <span className="text-slate-400">
            {data.items.filter(i => i.checked).length}/{data.items.length} completos
          </span>
        </div>
      </div>
    </div>
  );
}
