'use client';

/**
 * Interactive map showing pharmacy locations with markers
 * Uses Leaflet for map rendering - teal/green markers for pharmacies
 */

import { useEffect, useMemo } from 'react';
import { MapContainer, TileLayer, Marker, Popup, useMap, Circle } from 'react-leaflet';
import L from 'leaflet';
import 'leaflet/dist/leaflet.css';
import type { PharmacyLocation } from '../../hooks/useNearbyFarmacias';

interface PharmacyMapProps {
  farmacias: PharmacyLocation[];
  userLocation?: { latitude: number; longitude: number };
  raio?: number;
  height?: string;
  onPharmacySelect?: (pharmacy: PharmacyLocation) => void;
}

// Teal marker for pharmacies
const pharmacyIcon = new L.Icon({
  iconUrl: 'data:image/svg+xml;base64,' + btoa(`
    <svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 24 24" width="32" height="32">
      <path fill="#10B981" d="M12 2C8.13 2 5 5.13 5 9c0 5.25 7 13 7 13s7-7.75 7-13c0-3.87-3.13-7-7-7z"/>
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

function MapBoundsAdjuster({
  farmacias,
  userLocation,
}: {
  farmacias: PharmacyLocation[];
  userLocation?: { latitude: number; longitude: number };
}) {
  const map = useMap();

  useEffect(() => {
    if (farmacias.length === 0 && !userLocation) return;

    const points: [number, number][] = farmacias
      .filter((f) => f.latitude && f.longitude)
      .map((f) => [f.latitude, f.longitude]);

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
  }, [farmacias, userLocation, map]);

  return null;
}

export default function PharmacyMap({
  farmacias,
  userLocation,
  raio,
  height = '400px',
  onPharmacySelect,
}: PharmacyMapProps) {
  const center = useMemo<[number, number]>(() => {
    if (userLocation) {
      return [userLocation.latitude, userLocation.longitude];
    }
    if (farmacias.length > 0 && farmacias[0].latitude) {
      return [farmacias[0].latitude, farmacias[0].longitude];
    }
    return [-14.24, -51.92];
  }, [farmacias, userLocation]);

  const validFarmacias = farmacias.filter(
    (f) => f.latitude && f.longitude && !isNaN(f.latitude) && !isNaN(f.longitude)
  );

  if (validFarmacias.length === 0 && !userLocation) {
    return (
      <div
        className="flex items-center justify-center bg-slate-800 rounded-xl text-slate-400"
        style={{ height }}
      >
        <div className="text-center p-4">
          <span className="text-4xl mb-2 block">🗺️</span>
          <p>Nenhuma farmácia com coordenadas para exibir no mapa</p>
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
        <TileLayer
          url="https://{s}.basemaps.cartocdn.com/dark_all/{z}/{x}/{y}{r}.png"
          attribution='&copy; <a href="https://www.openstreetmap.org/copyright">OpenStreetMap</a>'
        />

        <MapBoundsAdjuster farmacias={validFarmacias} userLocation={userLocation} />

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

            {raio && (
              <Circle
                center={[userLocation.latitude, userLocation.longitude]}
                radius={raio}
                pathOptions={{
                  color: '#10B981',
                  fillColor: '#10B981',
                  fillOpacity: 0.1,
                  weight: 2,
                  dashArray: '5, 5',
                }}
              />
            )}
          </>
        )}

        {validFarmacias.map((farmacia, index) => (
          <Marker
            key={farmacia.id || `farmacia-${index}`}
            position={[farmacia.latitude, farmacia.longitude]}
            icon={pharmacyIcon}
            eventHandlers={{
              click: () => onPharmacySelect?.(farmacia),
            }}
          >
            <Popup>
              <div className="min-w-[200px] max-w-[280px]">
                <h3 className="font-bold text-emerald-700 text-sm mb-2">
                  💊 {farmacia.nome}
                </h3>

                <p className="text-xs text-gray-600 mb-2">
                  📍 {farmacia.endereco}
                </p>

                {/* Badges */}
                <div className="flex gap-1.5 mb-2">
                  {farmacia.aberto_agora !== undefined && (
                    <span
                      className={`px-1.5 py-0.5 text-[10px] rounded font-medium ${
                        farmacia.aberto_agora
                          ? 'bg-green-100 text-green-700'
                          : 'bg-red-100 text-red-700'
                      }`}
                    >
                      {farmacia.aberto_agora ? 'Aberto agora' : 'Fechado'}
                    </span>
                  )}
                  {farmacia.delivery && (
                    <span className="px-1.5 py-0.5 bg-blue-100 text-blue-700 text-[10px] rounded font-medium">
                      Delivery
                    </span>
                  )}
                </div>

                {farmacia.distancia && (
                  <p className="text-xs text-blue-600 mb-2">
                    🚶 {farmacia.distancia}
                  </p>
                )}

                {farmacia.telefone && (
                  <p className="text-xs mb-2">
                    📞{' '}
                    <a href={`tel:${farmacia.telefone}`} className="text-blue-600 hover:underline">
                      {farmacia.telefone}
                    </a>
                  </p>
                )}

                {farmacia.horario && (
                  <p className="text-xs text-gray-500 mb-2">
                    🕐 {farmacia.horario}
                  </p>
                )}

                <div className="mt-3 pt-2 border-t border-gray-200 flex gap-2">
                  {farmacia.telefone && (
                    <a
                      href={`tel:${farmacia.telefone}`}
                      className="flex-1 text-center py-1 bg-emerald-600 text-white text-xs rounded hover:bg-emerald-700"
                    >
                      Ligar
                    </a>
                  )}
                  <a
                    href={
                      farmacia.links?.google_maps ||
                      `https://www.google.com/maps/dir/?api=1&destination=${farmacia.latitude},${farmacia.longitude}`
                    }
                    target="_blank"
                    rel="noopener noreferrer"
                    className="flex-1 text-center py-1 bg-blue-600 text-white text-xs rounded hover:bg-blue-700"
                  >
                    Maps
                  </a>
                  {farmacia.links?.waze && (
                    <a
                      href={farmacia.links.waze}
                      target="_blank"
                      rel="noopener noreferrer"
                      className="flex-1 text-center py-1 bg-sky-500 text-white text-xs rounded hover:bg-sky-600"
                    >
                      Waze
                    </a>
                  )}
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
            <span className="w-3 h-3 rounded-full bg-emerald-500"></span>
            Farmácia
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
      <div className="absolute top-3 right-3 z-[1000] bg-emerald-600 px-3 py-1.5 rounded-full text-xs text-white font-medium">
        {validFarmacias.length} farmácia{validFarmacias.length !== 1 ? 's' : ''} encontrada{validFarmacias.length !== 1 ? 's' : ''}
      </div>
    </div>
  );
}
