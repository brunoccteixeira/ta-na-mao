/**
 * API client for Tá na Mão backend
 */

import axios from 'axios';

const API_BASE_URL = process.env.NEXT_PUBLIC_API_URL || '/api/v1';

export const api = axios.create({
  baseURL: API_BASE_URL,
  headers: {
    'Content-Type': 'application/json',
  },
});

// Types
export interface State {
  ibge_code: string;
  name: string;
  abbreviation: string;
  region: string;
  population?: number;
  beneficiaries?: number;
  coverage?: number;
}

export interface Municipality {
  ibge_code: string;
  name: string;
  state_id: number;
  population?: number;
  area_km2?: number;
  beneficiaries?: number;
  families?: number;
  coverage?: number;
}

export interface Program {
  code: string;
  name: string;
  description?: string;
  national_stats?: {
    total_beneficiaries: number;
    total_families: number;
    total_value_brl: number;
    avg_coverage_rate: number;
    latest_data_date?: string;
  };
}

export interface GeoJSONFeatureCollection {
  type: 'FeatureCollection';
  features: GeoJSONFeature[];
  metadata?: Record<string, any>;
}

export interface GeoJSONFeature {
  type: 'Feature';
  properties: Record<string, any>;
  geometry: any;
}

// API functions
export const fetchStatesGeoJSON = async (program?: string): Promise<GeoJSONFeatureCollection> => {
  const params = new URLSearchParams({ simplified: 'true' });
  if (program) params.append('program', program);
  const response = await api.get(`/geo/states?${params}`);
  return response.data;
};

export const fetchMunicipalitiesGeoJSON = async (
  stateCode: string,
  program?: string
): Promise<GeoJSONFeatureCollection> => {
  const params = new URLSearchParams({ state_code: stateCode, simplified: 'true' });
  if (program) params.append('program', program);
  const response = await api.get(`/geo/municipalities?${params}`);
  return response.data;
};

export const fetchPrograms = async (): Promise<Program[]> => {
  const response = await api.get('/programs');
  return response.data;
};

export const fetchNationalAggregation = async (program?: string) => {
  const params = program ? `?program=${program}` : '';
  const response = await api.get(`/aggregations/national${params}`);
  return response.data;
};

export const fetchStatesAggregation = async (program?: string) => {
  const params = program ? `?program=${program}` : '';
  const response = await api.get(`/aggregations/states${params}`);
  return response.data;
};

export const searchMunicipalities = async (query: string): Promise<Municipality[]> => {
  const response = await api.get(`/municipalities/search?q=${encodeURIComponent(query)}`);
  return response.data;
};

export interface RankingItem {
  rank: number;
  ibge_code: string;
  name: string;
  total_beneficiaries: number;
  total_families: number;
  coverage_rate: number | null;
  total_value_brl: number | null;
}

export interface ProgramRanking {
  program_code: string;
  program_name: string;
  order_by: string;
  ranking: RankingItem[];
}

export const fetchProgramRanking = async (
  programCode: string,
  orderBy: 'beneficiaries' | 'coverage' | 'value' = 'coverage',
  stateCode?: string,
  limit: number = 10
): Promise<ProgramRanking> => {
  const params = new URLSearchParams({ order_by: orderBy, limit: limit.toString() });
  if (stateCode) params.append('state_code', stateCode);
  const response = await api.get(`/programs/${programCode}/ranking?${params}`);
  return response.data;
};

export interface TimeSeriesPoint {
  date: string;
  month: string;
  total_beneficiaries: number;
  total_families: number;
  total_value_brl: number;
  avg_coverage_rate: number;
}

export interface TimeSeriesData {
  level: string;
  count: number;
  data: TimeSeriesPoint[];
}

export const fetchTimeSeries = async (
  program?: string,
  stateCode?: string
): Promise<TimeSeriesData> => {
  const params = new URLSearchParams();
  if (program) params.append('program', program);
  if (stateCode) params.append('state_code', stateCode);
  const response = await api.get(`/aggregations/time-series?${params}`);
  return response.data;
};

export interface DemographicsData {
  level: string;
  total_families: number;
  total_persons: number;
  income_brackets: {
    extreme_poverty: number;
    poverty: number;
    low_income: number;
  };
  age_distribution: {
    '0_5': number;
    '6_14': number;
    '15_17': number;
    '18_64': number;
    '65_plus': number;
  };
}

export const fetchDemographics = async (stateCode?: string): Promise<DemographicsData> => {
  const params = stateCode ? `?state_code=${stateCode}` : '';
  const response = await api.get(`/aggregations/demographics${params}`);
  return response.data;
};

export interface RegionStats {
  code: string;
  name: string;
  population: number;
  state_count: number;
  municipality_count: number;
  total_beneficiaries: number;
  total_families: number;
  total_value_brl: number;
  avg_coverage_rate: number;
}

export interface RegionsData {
  level: string;
  count: number;
  regions: RegionStats[];
}

export const fetchRegionsAggregation = async (program?: string): Promise<RegionsData> => {
  const params = program ? `?program=${program}` : '';
  const response = await api.get(`/aggregations/regions${params}`);
  return response.data;
};

export const exportToCSV = (data: any[], filename: string) => {
  if (!data || data.length === 0) return;

  const headers = Object.keys(data[0]);
  const csvContent = [
    headers.join(','),
    ...data.map(row =>
      headers.map(h => {
        const val = row[h];
        // Escape commas and quotes
        if (typeof val === 'string' && (val.includes(',') || val.includes('"'))) {
          return `"${val.replace(/"/g, '""')}"`;
        }
        return val;
      }).join(',')
    )
  ].join('\n');

  const blob = new Blob([csvContent], { type: 'text/csv;charset=utf-8;' });
  const link = document.createElement('a');
  link.href = URL.createObjectURL(blob);
  link.download = `${filename}.csv`;
  link.click();
};

// Admin API types and functions
export interface PenetrationData {
  ibge_code: string;
  municipality: string;
  state: string;
  region: string;
  population: number;
  cadunico_families: number;
  total_beneficiaries: number;
  total_families: number;
  total_value_brl: number;
  coverage_rate: number;
  gap: number;
}

export interface PenetrationResponse {
  level: string;
  total_count: number;
  page_size: number;
  offset: number;
  filters: {
    state: string | null;
    program: string | null;
    min_population: number | null;
    max_population: number | null;
    min_coverage: number | null;
    max_coverage: number | null;
  };
  data: PenetrationData[];
}

export interface AdminAlert {
  type: 'critical' | 'warning' | 'info';
  ibge_code: string;
  municipality: string;
  state: string;
  population: number;
  coverage_rate: number;
  total_beneficiaries: number;
  message: string;
}

export interface AlertsResponse {
  summary: {
    critical_count: number;
    warning_count: number;
    thresholds: {
      critical: number;
      warning: number;
    };
    biggest_gap: {
      municipality: string;
      state: string;
      gap: number;
    } | null;
  };
  alerts: AdminAlert[];
}

export interface AdminSummary {
  total_municipalities: number;
  total_states: number;
  total_population: number;
  total_beneficiaries: number;
  total_value_brl: number;
  avg_coverage_rate: number;
  critical_municipalities: number;
  programs_tracked: number;
}

export const fetchPenetrationData = async (params: {
  state_code?: string;
  program?: string;
  min_population?: number;
  max_population?: number;
  min_coverage?: number;
  max_coverage?: number;
  order_by?: string;
  order_dir?: string;
  limit?: number;
  offset?: number;
}): Promise<PenetrationResponse> => {
  const searchParams = new URLSearchParams();
  Object.entries(params).forEach(([key, value]) => {
    if (value !== undefined && value !== null) {
      searchParams.append(key, String(value));
    }
  });
  const response = await api.get(`/admin/penetration?${searchParams}`);
  return response.data;
};

export const fetchAlerts = async (params?: {
  threshold_critical?: number;
  threshold_warning?: number;
  program?: string;
  state_code?: string;
  limit?: number;
}): Promise<AlertsResponse> => {
  const searchParams = new URLSearchParams();
  if (params) {
    Object.entries(params).forEach(([key, value]) => {
      if (value !== undefined && value !== null) {
        searchParams.append(key, String(value));
      }
    });
  }
  const response = await api.get(`/admin/alerts?${searchParams}`);
  return response.data;
};

export const fetchAdminSummary = async (): Promise<AdminSummary> => {
  const response = await api.get('/admin/summary');
  return response.data;
};

export const downloadExport = async (params: {
  format?: 'csv' | 'json';
  scope?: 'national' | 'state';
  state_code?: string;
  program?: string;
}): Promise<void> => {
  const searchParams = new URLSearchParams();
  Object.entries(params).forEach(([key, value]) => {
    if (value !== undefined && value !== null) {
      searchParams.append(key, String(value));
    }
  });

  // For CSV, we need to handle as blob
  if (params.format === 'csv' || !params.format) {
    const response = await api.get(`/admin/export?${searchParams}`, {
      responseType: 'blob',
    });
    const blob = new Blob([response.data], { type: 'text/csv' });
    const url = window.URL.createObjectURL(blob);
    const link = document.createElement('a');
    link.href = url;
    link.download = `tanamao_export_${params.scope || 'national'}_${new Date().toISOString().split('T')[0]}.csv`;
    link.click();
    window.URL.revokeObjectURL(url);
  } else {
    const response = await api.get(`/admin/export?${searchParams}`);
    const blob = new Blob([JSON.stringify(response.data, null, 2)], { type: 'application/json' });
    const url = window.URL.createObjectURL(blob);
    const link = document.createElement('a');
    link.href = url;
    link.download = `tanamao_export_${params.scope || 'national'}_${new Date().toISOString().split('T')[0]}.json`;
    link.click();
    window.URL.revokeObjectURL(url);
  }
};
