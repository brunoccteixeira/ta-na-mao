'use client';

/**
 * Interactive map showing CRAS locations with markers
 * Uses Leaflet for map rendering
 */

import { useEffect, useMemo } from 'react';
import { MapContainer, TileLayer, Marker, Popup, useMap, Circle } from 'react-leaflet';
import L from 'leaflet';
import 'leaflet/dist/leaflet.css';

// =============================================================================
// Types
// =============================================================================

export interface CrasLocation {
  id?: string;
  nome: string;
  endereco: string;
  telefone?: string;
  horario?: string;
  servicos?: string[];
  latitude: number;
  longitude: number;
  distancia?: string;
  distancia_metros?: number;
}

interface CrasMapProps {
  /** List of CRAS to display on map */
  cras: CrasLocation[];
  /** User's current location (optional) */
  userLocation?: { latitude: number; longitude: number };
  /** Search radius in meters (optional, shows circle) */
  raio?: number;
  /** Map height (default: 400px) */
  height?: string;
  /** Callback when a CRAS is selected */
  onCrasSelect?: (cras: CrasLocation) => void;
}

// =============================================================================
// Custom marker icon (purple for CRAS)
// =============================================================================

const crasIcon = new L.Icon({
  iconUrl: 'data:image/svg+xml;base64,' + btoa(`
    <svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 24 24" width="32" height="32">
      <path fill="#9333EA" d="M12 2C8.13 2 5 5.13 5 9c0 5.25 7 13 7 13s7-7.75 7-13c0-3.87-3.13-7-7-7z"/>
      <circle fill="white" cx="12" cy="9" r="3"/>
    </svg>
  `),
  iconSize: [32, 32],
  iconAnchor: [16, 32],
  popupAnchor: [0, -32],
});

const userIcon = new L.Icon({
  iconUrl: 'data:image/svg+xml;base64,' + btoa(`
    <svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 24 24" width="24" height="24">
      <circle fill="#3B82F6" cx="12" cy="12" r="8" stroke="white" stroke-width="3"/>
    </svg>
  `),
  iconSize: [24, 24],
  iconAnchor: [12, 12],
  popupAnchor: [0, -12],
});

// =============================================================================
// Map bounds adjuster component
// =============================================================================

function MapBoundsAdjuster({
  cras,
  userLocation
}: {
  cras: CrasLocation[];
  userLocation?: { latitude: number; longitude: number };
}) {
  const map = useMap();

  useEffect(() => {
    if (cras.length === 0 && !userLocation) return;

    const points: [number, number][] = cras
      .filter(c => c.latitude && c.longitude)
      .map(c => [c.latitude, c.longitude]);

    if (userLocation) {
      points.push([userLocation.latitude, userLocation.longitude]);
    }

    if (points.length === 0) return;

    if (points.length === 1) {
      map.setView(points[0], 14);
    } else {
      const bounds = L.latLngBounds(points);
      map.fitBounds(bounds, { padding: [50, 50] });
    }
  }, [cras, userLocation, map]);

  return null;
}

// =============================================================================
// Main Component
// =============================================================================

export default function CrasMap({
  cras,
  userLocation,
  raio,
  height = '400px',
  onCrasSelect,
}: CrasMapProps) {
  // Calculate center point
  const center = useMemo<[number, number]>(() => {
    if (userLocation) {
      return [userLocation.latitude, userLocation.longitude];
    }
    if (cras.length > 0 && cras[0].latitude) {
      return [cras[0].latitude, cras[0].longitude];
    }
    // Default: Brazil center
    return [-14.24, -51.92];
  }, [cras, userLocation]);

  const handleCrasClick = (crasItem: CrasLocation) => {
    onCrasSelect?.(crasItem);
  };

  // Filter CRAS with valid coordinates
  const validCras = cras.filter(c =>
    c.latitude && c.longitude &&
    !isNaN(c.latitude) && !isNaN(c.longitude)
  );

  if (validCras.length === 0 && !userLocation) {
    return (
      <div
        className="flex items-center justify-center bg-slate-800 rounded-xl text-slate-400"
        style={{ height }}
      >
        <div className="text-center p-4">
          <span className="text-4xl mb-2 block">🗺️</span>
          <p>Nenhum CRAS com coordenadas para exibir no mapa</p>
        </div>
      </div>
    );
  }

  return (
    <div className="relative rounded-xl overflow-hidden" style={{ height }}>
      <MapContainer
        center={center}
        zoom={userLocation ? 13 : 4}
        className="w-full h-full"
        zoomControl={true}
        scrollWheelZoom={true}
      >
        {/* Dark tile layer matching app theme */}
        <TileLayer
          url="https://{s}.basemaps.cartocdn.com/dark_all/{z}/{x}/{y}{r}.png"
          attribution='&copy; <a href="https://www.openstreetmap.org/copyright">OpenStreetMap</a>'
        />

        {/* Auto-adjust bounds */}
        <MapBoundsAdjuster cras={validCras} userLocation={userLocation} />

        {/* User location marker */}
        {userLocation && (
          <>
            <Marker
              position={[userLocation.latitude, userLocation.longitude]}
              icon={userIcon}
            >
              <Popup>
                <div className="text-center">
                  <strong>📍 Você está aqui</strong>
                </div>
              </Popup>
            </Marker>

            {/* Search radius circle */}
            {raio && (
              <Circle
                center={[userLocation.latitude, userLocation.longitude]}
                radius={raio}
                pathOptions={{
                  color: '#3B82F6',
                  fillColor: '#3B82F6',
                  fillOpacity: 0.1,
                  weight: 2,
                  dashArray: '5, 5',
                }}
              />
            )}
          </>
        )}

        {/* CRAS markers */}
        {validCras.map((crasItem, index) => (
          <Marker
            key={crasItem.id || `cras-${index}`}
            position={[crasItem.latitude, crasItem.longitude]}
            icon={crasIcon}
            eventHandlers={{
              click: () => handleCrasClick(crasItem),
            }}
          >
            <Popup>
              <div className="min-w-[200px] max-w-[280px]">
                <h3 className="font-bold text-purple-700 text-sm mb-2">
                  🏛️ {crasItem.nome}
                </h3>

                <p className="text-xs text-gray-600 mb-2">
                  📍 {crasItem.endereco}
                </p>

                {crasItem.distancia && (
                  <p className="text-xs text-blue-600 mb-2">
                    🚶 {crasItem.distancia}
                  </p>
                )}

                {crasItem.telefone && (
                  <p className="text-xs mb-2">
                    📞{' '}
                    <a
                      href={`tel:${crasItem.telefone}`}
                      className="text-blue-600 hover:underline"
                    >
                      {crasItem.telefone}
                    </a>
                  </p>
                )}

                {crasItem.horario && (
                  <p className="text-xs text-gray-500 mb-2">
                    🕐 {crasItem.horario}
                  </p>
                )}

                {crasItem.servicos && crasItem.servicos.length > 0 && (
                  <div className="flex flex-wrap gap-1 mt-2">
                    {crasItem.servicos.slice(0, 3).map((servico, i) => (
                      <span
                        key={i}
                        className="px-1.5 py-0.5 bg-purple-100 text-purple-700 text-[10px] rounded"
                      >
                        {servico}
                      </span>
                    ))}
                  </div>
                )}

                <div className="mt-3 pt-2 border-t border-gray-200 flex gap-2">
                  {crasItem.telefone && (
                    <a
                      href={`tel:${crasItem.telefone}`}
                      className="flex-1 text-center py-1 bg-purple-600 text-white text-xs rounded hover:bg-purple-700"
                    >
                      Ligar
                    </a>
                  )}
                  <a
                    href={`https://www.google.com/maps/dir/?api=1&destination=${crasItem.latitude},${crasItem.longitude}`}
                    target="_blank"
                    rel="noopener noreferrer"
                    className="flex-1 text-center py-1 bg-blue-600 text-white text-xs rounded hover:bg-blue-700"
                  >
                    Rota
                  </a>
                </div>
              </div>
            </Popup>
          </Marker>
        ))}
      </MapContainer>

      {/* Legend */}
      <div className="absolute bottom-3 left-3 z-[1000] bg-slate-800/90 px-3 py-2 rounded-lg text-xs text-white">
        <div className="flex items-center gap-3">
          <span className="flex items-center gap-1">
            <span className="w-3 h-3 rounded-full bg-purple-600"></span>
            CRAS
          </span>
          {userLocation && (
            <span className="flex items-center gap-1">
              <span className="w-3 h-3 rounded-full bg-blue-500"></span>
              Você
            </span>
          )}
        </div>
      </div>

      {/* Count badge */}
      <div className="absolute top-3 right-3 z-[1000] bg-purple-600 px-3 py-1.5 rounded-full text-xs text-white font-medium">
        {validCras.length} CRAS encontrado{validCras.length !== 1 ? 's' : ''}
      </div>
    </div>
  );
}
