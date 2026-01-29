/**
 * PharmacyCard - Renders a pharmacy location
 */

import { PharmacyCardData } from '../../api/chatClient';

interface Props {
  data: PharmacyCardData;
  selected?: boolean;
  onSelect?: () => void;
}

export default function PharmacyCard({ data, selected, onSelect }: Props) {
  return (
    <div
      className={`rounded-xl border overflow-hidden transition-all cursor-pointer ${
        selected
          ? 'bg-teal-500/10 border-teal-500'
          : 'bg-slate-800/50 border-slate-700 hover:border-slate-600'
      }`}
      onClick={onSelect}
    >
      <div className="p-4">
        {/* Header */}
        <div className="flex items-start justify-between gap-3 mb-3">
          <div className="flex items-center gap-3">
            <div className={`w-10 h-10 rounded-full flex items-center justify-center ${
              selected ? 'bg-teal-500' : 'bg-emerald-500/20'
            }`}>
              <span className="text-lg">🏪</span>
            </div>
            <div>
              <h4 className="font-medium text-slate-200">{data.name}</h4>
              {data.distance && (
                <span className="text-xs text-teal-400">{data.distance}</span>
              )}
            </div>
          </div>

          {selected && (
            <div className="w-6 h-6 rounded-full bg-teal-500 flex items-center justify-center">
              <svg className="w-4 h-4 text-white" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={3} d="M5 13l4 4L19 7" />
              </svg>
            </div>
          )}
        </div>

        {/* Address */}
        <p className="text-sm text-slate-400 mb-3">
          📍 {data.address}
        </p>

        {/* Details */}
        <div className="flex flex-wrap gap-2 text-xs">
          {data.hours && (
            <span className="px-2 py-1 rounded-full bg-slate-700 text-slate-300">
              🕐 {data.hours}
            </span>
          )}
          {data.phone && (
            <span className="px-2 py-1 rounded-full bg-slate-700 text-slate-300">
              📞 {data.phone}
            </span>
          )}
          {data.has_whatsapp && (
            <span className="px-2 py-1 rounded-full bg-green-500/20 text-green-400">
              WhatsApp
            </span>
          )}
        </div>
      </div>

      {/* Action buttons */}
      <div className="flex border-t border-slate-700">
        {data.phone && (
          <a
            href={`tel:${data.phone}`}
            className="flex-1 py-2 text-center text-xs text-slate-400 hover:text-slate-200 hover:bg-slate-700/50 transition-colors"
            onClick={(e) => e.stopPropagation()}
          >
            📞 Ligar
          </a>
        )}
        {data.has_whatsapp && data.whatsapp_number && (
          <a
            href={`https://wa.me/${data.whatsapp_number.replace(/\D/g, '')}`}
            target="_blank"
            rel="noopener noreferrer"
            className="flex-1 py-2 text-center text-xs text-green-400 hover:text-green-300 hover:bg-green-500/10 transition-colors border-l border-slate-700"
            onClick={(e) => e.stopPropagation()}
          >
            💬 WhatsApp
          </a>
        )}
        <a
          href={`https://www.google.com/maps/search/?api=1&query=${encodeURIComponent(data.address)}`}
          target="_blank"
          rel="noopener noreferrer"
          className="flex-1 py-2 text-center text-xs text-blue-400 hover:text-blue-300 hover:bg-blue-500/10 transition-colors border-l border-slate-700"
          onClick={(e) => e.stopPropagation()}
        >
          🗺️ Mapa
        </a>
      </div>
    </div>
  );
}
