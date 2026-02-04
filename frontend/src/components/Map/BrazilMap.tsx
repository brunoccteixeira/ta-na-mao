'use client';

/**
 * Interactive Brazil Map using Leaflet
 * Supports state and municipality level visualization
 */

import { useEffect, useRef } from 'react';
import { MapContainer, TileLayer, GeoJSON, useMap } from 'react-leaflet';
import type { GeoJSON as GeoJSONType, Layer, PathOptions } from 'leaflet';
import { useStatesGeoJSON, useMunicipalitiesGeoJSON, getMetricColor } from '../../hooks/useGeoJSON';
import { useDashboardStore, MetricType } from '../../stores/dashboardStore';
import 'leaflet/dist/leaflet.css';

// Brazil bounds
const BRAZIL_BOUNDS: [[number, number], [number, number]] = [
  [-33.75, -73.99], // Southwest
  [5.27, -28.85],   // Northeast
];

const BRAZIL_CENTER: [number, number] = [-14.24, -51.92];

interface MapLayerProps {
  stateCode: string | null;
  program: string | null;
  metric: MetricType;
  onStateClick: (stateCode: string) => void;
  onMunicipalityClick: (ibgeCode: string) => void;
}

/**
 * Component to handle map layers and interactions
 */
function MapLayers({ stateCode, program, metric, onStateClick, onMunicipalityClick }: MapLayerProps) {
  const map = useMap();
  const geoJsonRef = useRef<GeoJSONType | null>(null);

  // Fetch GeoJSON data
  const { data: statesData, isLoading: statesLoading } = useStatesGeoJSON(program || undefined);
  const { data: municipalitiesData, isLoading: municipalitiesLoading } = useMunicipalitiesGeoJSON(
    stateCode,
    program || undefined
  );

  // Style function for choropleth based on selected metric
  const getStyle = (feature: any): PathOptions => {
    const props = feature?.properties || {};
    return {
      fillColor: getMetricColor(metric, props),
      weight: 1,
      opacity: 1,
      color: '#0f172a',
      fillOpacity: 0.7,
    };
  };

  // Highlight on hover
  const onEachFeature = (feature: any, layer: Layer) => {
    const props = feature.properties;
    const isState = props.abbreviation !== undefined;

    // Tooltip content
    const tooltipContent = isState
      ? `<strong>${props.name} (${props.abbreviation})</strong><br/>
         Beneficiários: ${props.beneficiaries?.toLocaleString('pt-BR') || 'N/A'}<br/>
         Cobertura: ${props.coverage ? (props.coverage * 100).toFixed(1) + '%' : 'N/A'}`
      : `<strong>${props.name}</strong><br/>
         População: ${props.population?.toLocaleString('pt-BR') || 'N/A'}<br/>
         Beneficiários: ${props.beneficiaries?.toLocaleString('pt-BR') || 'N/A'}`;

    layer.bindTooltip(tooltipContent, { sticky: true });

    // Click handler
    layer.on('click', () => {
      if (isState) {
        onStateClick(props.abbreviation);
      } else {
        onMunicipalityClick(props.ibge_code);
      }
    });

    // Hover effects
    layer.on('mouseover', (e) => {
      const target = e.target;
      target.setStyle({
        weight: 2,
        color: '#fff',
        fillOpacity: 0.9,
      });
      target.bringToFront();
    });

    layer.on('mouseout', (e) => {
      if (geoJsonRef.current) {
        geoJsonRef.current.resetStyle(e.target);
      }
    });
  };

  // Fit bounds when state is selected/deselected
  useEffect(() => {
    if (stateCode && municipalitiesData && municipalitiesData.features?.length > 0) {
      // Calculate bounds from municipalities GeoJSON
      try {
        const bounds = municipalitiesData.features.reduce(
          (acc: [[number, number], [number, number]], feature: any) => {
            if (feature.geometry?.coordinates) {
              const coords = feature.geometry.type === 'MultiPolygon'
                ? feature.geometry.coordinates.flat(2)
                : feature.geometry.coordinates.flat(1);
              coords.forEach((coord: [number, number]) => {
                if (Array.isArray(coord) && coord.length >= 2) {
                  acc[0][0] = Math.min(acc[0][0], coord[1]); // min lat
                  acc[0][1] = Math.min(acc[0][1], coord[0]); // min lng
                  acc[1][0] = Math.max(acc[1][0], coord[1]); // max lat
                  acc[1][1] = Math.max(acc[1][1], coord[0]); // max lng
                }
              });
            }
            return acc;
          },
          [[90, 180], [-90, -180]] as [[number, number], [number, number]]
        );
        map.fitBounds(bounds, { padding: [20, 20] });
      } catch (e) {
        // Fallback to default zoom
        map.setZoom(6);
      }
    } else if (!stateCode) {
      map.fitBounds(BRAZIL_BOUNDS);
    }
  }, [stateCode, municipalitiesData, map]);

  const isLoading = statesLoading || (stateCode && municipalitiesLoading);

  if (isLoading) {
    return (
      <div className="absolute inset-0 flex items-center justify-center bg-slate-900/50 z-[1000]">
        <div className="text-white">Carregando mapa...</div>
      </div>
    );
  }

  // Show municipalities if state is selected, otherwise show states
  const dataToRender = stateCode && municipalitiesData ? municipalitiesData : statesData;

  return dataToRender ? (
    <GeoJSON
      ref={geoJsonRef}
      key={`${stateCode || 'states'}-${metric}`} // Force re-render when switching state or metric
      data={dataToRender}
      style={getStyle}
      onEachFeature={onEachFeature}
    />
  ) : null;
}

/**
 * Main Brazil Map component
 */
// Legend config by metric
const LEGEND_CONFIG: Record<MetricType, { title: string; labels: string[] }> = {
  coverage: {
    title: 'Cobertura',
    labels: ['≥80%', '60-79%', '40-59%', '20-39%', '<20%'],
  },
  beneficiaries: {
    title: 'Beneficiários',
    labels: ['Muito alto', 'Alto', 'Médio', 'Baixo', 'Muito baixo'],
  },
  gap: {
    title: 'Gap',
    labels: ['Muito alto', 'Alto', 'Médio', 'Baixo', 'Sem gap'],
  },
  value: {
    title: 'Valor (R$)',
    labels: ['Muito alto', 'Alto', 'Médio', 'Baixo', 'Muito baixo'],
  },
};

export default function BrazilMap() {
  const {
    selectedState,
    selectedProgram,
    selectedMetric,
    selectState,
    selectMunicipality,
  } = useDashboardStore();

  return (
    <div className="relative w-full h-full">
      <MapContainer
        center={BRAZIL_CENTER}
        zoom={4}
        minZoom={3}
        maxZoom={12}
        bounds={BRAZIL_BOUNDS}
        className="w-full h-full bg-slate-950"
        zoomControl={true}
        scrollWheelZoom={true}
      >
        {/* Dark tile layer */}
        <TileLayer
          url="https://{s}.basemaps.cartocdn.com/dark_all/{z}/{x}/{y}{r}.png"
          attribution='&copy; <a href="https://www.openstreetmap.org/copyright">OpenStreetMap</a> contributors &copy; <a href="https://carto.com/attributions">CARTO</a>'
        />

        {/* Map layers */}
        <MapLayers
          stateCode={selectedState}
          program={selectedProgram}
          metric={selectedMetric}
          onStateClick={selectState}
          onMunicipalityClick={selectMunicipality}
        />
      </MapContainer>

      {/* Back button when viewing a state */}
      {selectedState && (
        <button
          onClick={() => selectState(null)}
          className="absolute top-4 left-4 z-[1000] px-3 py-2 bg-slate-800 text-white rounded-lg hover:bg-slate-700 transition-colors"
        >
          ← Voltar para Brasil
        </button>
      )}

      {/* Legend */}
      <div className="absolute bottom-4 right-4 z-[1000] bg-slate-800/90 p-3 rounded-lg text-xs text-white">
        <div className="font-semibold mb-2">{LEGEND_CONFIG[selectedMetric].title}</div>
        <div className="flex flex-col gap-1">
          {['#10B981', '#22C55E', '#EAB308', '#F97316', '#EF4444'].map((color, i) => (
            <div key={color} className="flex items-center gap-2">
              <div className="w-4 h-3 rounded" style={{ backgroundColor: color }}></div>
              <span>{LEGEND_CONFIG[selectedMetric].labels[i]}</span>
            </div>
          ))}
        </div>
      </div>
    </div>
  );
}
