/**
 * CrasCard - Renders CRAS (Social Assistance Center) information
 */

import { CrasCardData } from '../../api/chatClient';

interface Props {
  data: CrasCardData;
}

export default function CrasCard({ data }: Props) {
  return (
    <div className="bg-slate-800/50 rounded-xl border border-slate-700 overflow-hidden">
      {/* Header */}
      <div className="bg-gradient-to-r from-purple-600 to-pink-600 px-4 py-3">
        <h3 className="font-semibold text-white flex items-center gap-2">
          <span className="text-lg">🏛️</span>
          {data.name}
        </h3>
        {data.distance && (
          <span className="text-xs text-purple-100">
            📍 {data.distance} de você
          </span>
        )}
      </div>

      <div className="p-4 space-y-3">
        {/* Address */}
        <div className="flex items-start gap-3">
          <span className="text-slate-400">📍</span>
          <div>
            <p className="text-sm text-slate-200">{data.address}</p>
            <a
              href={`https://www.google.com/maps/search/?api=1&query=${encodeURIComponent(data.address)}`}
              target="_blank"
              rel="noopener noreferrer"
              className="text-xs text-blue-400 hover:text-blue-300"
            >
              Ver no mapa →
            </a>
          </div>
        </div>

        {/* Phone */}
        {data.phone && (
          <div className="flex items-center gap-3">
            <span className="text-slate-400">📞</span>
            <a
              href={`tel:${data.phone}`}
              className="text-sm text-slate-200 hover:text-teal-400"
            >
              {data.phone}
            </a>
          </div>
        )}

        {/* Hours */}
        {data.hours && (
          <div className="flex items-center gap-3">
            <span className="text-slate-400">🕐</span>
            <p className="text-sm text-slate-200">{data.hours}</p>
          </div>
        )}

        {/* Services */}
        {data.services && data.services.length > 0 && (
          <div className="pt-2 border-t border-slate-700">
            <p className="text-xs text-slate-400 mb-2">Serviços disponíveis:</p>
            <div className="flex flex-wrap gap-1">
              {data.services.map((service, index) => (
                <span
                  key={index}
                  className="px-2 py-0.5 rounded-full bg-purple-500/20 text-purple-300 text-xs"
                >
                  {service}
                </span>
              ))}
            </div>
          </div>
        )}
      </div>

      {/* Actions */}
      <div className="flex border-t border-slate-700">
        {data.phone && (
          <a
            href={`tel:${data.phone}`}
            className="flex-1 py-3 text-center text-sm text-slate-400 hover:text-slate-200 hover:bg-slate-700/50 transition-colors"
          >
            📞 Ligar
          </a>
        )}
        <a
          href={`https://www.google.com/maps/search/?api=1&query=${encodeURIComponent(data.address)}`}
          target="_blank"
          rel="noopener noreferrer"
          className="flex-1 py-3 text-center text-sm text-blue-400 hover:text-blue-300 hover:bg-blue-500/10 transition-colors border-l border-slate-700"
        >
          🗺️ Como chegar
        </a>
      </div>
    </div>
  );
}
