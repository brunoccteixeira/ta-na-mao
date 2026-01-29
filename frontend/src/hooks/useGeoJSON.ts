/**
 * React Query hooks for fetching and caching GeoJSON data
 */

import { useQuery } from '@tanstack/react-query';
import { fetchStatesGeoJSON, fetchMunicipalitiesGeoJSON } from '../api/client';

/**
 * Hook to fetch states GeoJSON with caching
 * GeoJSON is cached indefinitely since geometry doesn't change
 */
export function useStatesGeoJSON(program?: string) {
  return useQuery({
    queryKey: ['geojson', 'states', program],
    queryFn: () => fetchStatesGeoJSON(program || undefined),
    staleTime: Infinity, // Geometry doesn't change
    gcTime: 1000 * 60 * 60 * 24, // Keep in cache for 24 hours
  });
}

/**
 * Hook to fetch municipalities GeoJSON for a specific state
 * Only fetches when stateCode is provided
 */
export function useMunicipalitiesGeoJSON(stateCode: string | null, program?: string) {
  return useQuery({
    queryKey: ['geojson', 'municipalities', stateCode, program],
    queryFn: () => fetchMunicipalitiesGeoJSON(stateCode!, program || undefined),
    enabled: !!stateCode, // Only fetch when state is selected
    staleTime: Infinity,
    gcTime: 1000 * 60 * 60 * 24,
  });
}

/**
 * Get color based on coverage rate (0-1 scale)
 */
export function getCoverageColor(coverage: number | undefined): string {
  if (coverage === undefined || coverage === null) return '#1e293b';

  if (coverage >= 0.8) return '#10B981'; // Green - 80%+
  if (coverage >= 0.6) return '#22C55E'; // Light green - 60-79%
  if (coverage >= 0.4) return '#EAB308'; // Yellow - 40-59%
  if (coverage >= 0.2) return '#F97316'; // Orange - 20-39%
  return '#EF4444'; // Red - <20%
}

/**
 * Get color based on gap (inverse of coverage - higher gap = worse)
 */
export function getGapColor(gap: number | undefined, maxGap: number = 100000): string {
  if (gap === undefined || gap === null || gap <= 0) return '#10B981'; // Green - no gap

  const normalized = Math.min(gap / maxGap, 1);
  if (normalized >= 0.8) return '#EF4444'; // Red - very high gap
  if (normalized >= 0.6) return '#F97316'; // Orange
  if (normalized >= 0.4) return '#EAB308'; // Yellow
  if (normalized >= 0.2) return '#22C55E'; // Light green
  return '#10B981'; // Green - low gap
}

/**
 * Get color based on beneficiaries count
 */
export function getBeneficiariesColor(beneficiaries: number | undefined, maxBen: number = 1000000): string {
  if (beneficiaries === undefined || beneficiaries === null) return '#1e293b';

  const normalized = Math.min(beneficiaries / maxBen, 1);
  if (normalized >= 0.8) return '#10B981'; // Green - many beneficiaries
  if (normalized >= 0.6) return '#22C55E';
  if (normalized >= 0.4) return '#EAB308';
  if (normalized >= 0.2) return '#F97316';
  return '#EF4444'; // Red - few beneficiaries
}

/**
 * Get color based on value (R$)
 */
export function getValueColor(value: number | undefined, maxValue: number = 100000000): string {
  if (value === undefined || value === null) return '#1e293b';

  const normalized = Math.min(value / maxValue, 1);
  if (normalized >= 0.8) return '#10B981';
  if (normalized >= 0.6) return '#22C55E';
  if (normalized >= 0.4) return '#EAB308';
  if (normalized >= 0.2) return '#F97316';
  return '#EF4444';
}

export type MetricType = 'coverage' | 'beneficiaries' | 'gap' | 'value';

/**
 * Get color for a feature based on selected metric
 */
export function getMetricColor(
  metric: MetricType,
  properties: Record<string, any>,
  maxValues?: { beneficiaries?: number; gap?: number; value?: number }
): string {
  switch (metric) {
    case 'coverage':
      return getCoverageColor(properties.coverage);
    case 'beneficiaries':
      return getBeneficiariesColor(properties.beneficiaries, maxValues?.beneficiaries);
    case 'gap': {
      const gap = (properties.cadunico_families || 0) - (properties.beneficiaries || 0);
      return getGapColor(gap, maxValues?.gap);
    }
    case 'value':
      return getValueColor(properties.total_value_brl, maxValues?.value);
    default:
      return getCoverageColor(properties.coverage);
  }
}

/**
 * Format large numbers for display
 */
export function formatNumber(num: number): string {
  if (num >= 1_000_000) return (num / 1_000_000).toFixed(1) + 'M';
  if (num >= 1_000) return (num / 1_000).toFixed(0) + 'k';
  return num.toLocaleString('pt-BR');
}
