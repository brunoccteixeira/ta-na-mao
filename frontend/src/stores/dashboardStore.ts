/**
 * Dashboard state management with Zustand
 */

import { create } from 'zustand';

export type ProgramCode =
  | 'TSEE'
  | 'FARMACIA_POPULAR'
  | 'DIGNIDADE_MENSTRUAL'
  | 'PIS_PASEP'
  | 'BPC'
  | 'CADUNICO'
  | 'BOLSA_FAMILIA'
  | 'AUXILIO_GAS'
  | 'SEGURO_DEFESO'
  | 'AUXILIO_INCLUSAO'
  | 'GARANTIA_SAFRA'
  | 'PNAE'
  | null;
export type MetricType = 'beneficiaries' | 'coverage' | 'gap' | 'value';
export type ViewLevel = 'national' | 'region' | 'state' | 'municipality';
export type RegionCode = 'N' | 'NE' | 'CO' | 'SE' | 'S' | null;
export type ViewMode = 'citizen' | 'admin';

interface DashboardState {
  // Selection state
  selectedProgram: ProgramCode;
  selectedMetric: MetricType;
  selectedRegion: RegionCode;
  selectedState: string | null;
  selectedMunicipality: string | null;
  viewLevel: ViewLevel;

  // UI state
  isSidebarOpen: boolean;
  isLoading: boolean;
  viewMode: ViewMode;

  // Actions
  setProgram: (program: ProgramCode) => void;
  setMetric: (metric: MetricType) => void;
  selectRegion: (region: RegionCode) => void;
  selectState: (stateCode: string | null) => void;
  selectMunicipality: (ibgeCode: string | null) => void;
  setViewLevel: (level: ViewLevel) => void;
  toggleSidebar: () => void;
  setLoading: (loading: boolean) => void;
  resetSelection: () => void;
  setViewMode: (mode: ViewMode) => void;
}

export const useDashboardStore = create<DashboardState>((set) => ({
  // Initial state
  selectedProgram: null,
  selectedMetric: 'beneficiaries',
  selectedRegion: null,
  selectedState: null,
  selectedMunicipality: null,
  viewLevel: 'national',
  isSidebarOpen: true,
  isLoading: false,
  viewMode: 'citizen',

  // Actions
  setProgram: (program) => set({ selectedProgram: program }),

  setMetric: (metric) => set({ selectedMetric: metric }),

  selectRegion: (region) =>
    set({
      selectedRegion: region,
      selectedState: null,
      selectedMunicipality: null,
      viewLevel: region ? 'region' : 'national',
    }),

  selectState: (stateCode) =>
    set({
      selectedState: stateCode,
      selectedMunicipality: null,
      viewLevel: stateCode ? 'state' : 'national',
    }),

  selectMunicipality: (ibgeCode) =>
    set({
      selectedMunicipality: ibgeCode,
      viewLevel: ibgeCode ? 'municipality' : 'state',
    }),

  setViewLevel: (level) => set({ viewLevel: level }),

  toggleSidebar: () => set((state) => ({ isSidebarOpen: !state.isSidebarOpen })),

  setLoading: (loading) => set({ isLoading: loading }),

  resetSelection: () =>
    set({
      selectedRegion: null,
      selectedState: null,
      selectedMunicipality: null,
      viewLevel: 'national',
    }),

  setViewMode: (mode) => set({ viewMode: mode }),
}));
