'use client';

/**
 * WizardContext - State management for the eligibility wizard
 *
 * Provides:
 * - Profile data (all 20 questions)
 * - Navigation between steps
 * - Progress tracking
 * - Persistence (localStorage)
 */

import React, { createContext, useContext, useReducer, useCallback, useEffect, ReactNode } from 'react';
import { CitizenProfile, DEFAULT_CITIZEN_PROFILE } from '../../engine/types';

// Extended profile with wizard-specific fields
export interface WizardProfile extends CitizenProfile {
  // Additional fields for interests (partner placeholders)
  interesseTarifaSocial?: boolean;
  usaMedicamentoContinuo?: boolean;
  interesseHabitacao?: boolean;
  // Contact for follow-up (optional)
  telefone?: string;
  // Date of birth components
  diaNascimento?: number;
  mesNascimento?: number;
  anoNascimento?: number;
}

export const DEFAULT_WIZARD_PROFILE: WizardProfile = {
  ...DEFAULT_CITIZEN_PROFILE,
  interesseTarifaSocial: undefined,
  usaMedicamentoContinuo: undefined,
  interesseHabitacao: undefined,
  telefone: undefined,
};

// Steps definition
export type WizardStepId =
  | 'estado'
  | 'cidade'
  | 'nascimento'
  | 'moradia'
  | 'familia'
  | 'filhos'
  | 'trabalho'
  | 'renda'
  | 'beneficios'
  | 'especial'
  | 'interesses'
  | 'resultado';

export interface WizardStep {
  id: WizardStepId;
  title: string;
  shortTitle: string;
  isConditional?: boolean;
  shouldShow?: (profile: WizardProfile) => boolean;
}

export const WIZARD_STEPS: WizardStep[] = [
  { id: 'estado', title: 'Em qual estado você mora?', shortTitle: 'Estado' },
  { id: 'cidade', title: 'Em qual cidade você mora?', shortTitle: 'Cidade' },
  { id: 'nascimento', title: 'Qual sua data de nascimento?', shortTitle: 'Nascimento' },
  { id: 'moradia', title: 'Como é sua moradia?', shortTitle: 'Moradia' },
  { id: 'familia', title: 'Quantas pessoas moram na sua casa?', shortTitle: 'Família' },
  {
    id: 'filhos',
    title: 'Sobre crianças e idosos na família',
    shortTitle: 'Dependentes',
    isConditional: true,
    shouldShow: (p) => p.pessoasNaCasa > 1,
  },
  { id: 'trabalho', title: 'Qual sua situação de trabalho?', shortTitle: 'Trabalho' },
  { id: 'renda', title: 'Qual a renda total da família?', shortTitle: 'Renda' },
  { id: 'beneficios', title: 'Você já recebe algum benefício?', shortTitle: 'Benefícios' },
  { id: 'especial', title: 'Situações especiais', shortTitle: 'Especial' },
  { id: 'interesses', title: 'O que mais você precisa?', shortTitle: 'Interesses' },
  { id: 'resultado', title: 'Seus direitos', shortTitle: 'Resultado' },
];

// State
interface WizardState {
  profile: WizardProfile;
  currentStepIndex: number;
  visitedSteps: Set<WizardStepId>;
  isSubmitting: boolean;
  error: string | null;
}

// Actions
type WizardAction =
  | { type: 'UPDATE_PROFILE'; payload: Partial<WizardProfile> }
  | { type: 'GO_TO_STEP'; payload: number }
  | { type: 'NEXT_STEP' }
  | { type: 'PREV_STEP' }
  | { type: 'SET_SUBMITTING'; payload: boolean }
  | { type: 'SET_ERROR'; payload: string | null }
  | { type: 'RESET' }
  | { type: 'RESTORE'; payload: WizardState };

// Reducer
function wizardReducer(state: WizardState, action: WizardAction): WizardState {
  switch (action.type) {
    case 'UPDATE_PROFILE': {
      const updatedProfile = { ...state.profile, ...action.payload };
      // Clear dependent fields when pessoasNaCasa drops to 1 (no dependents possible)
      if (action.payload.pessoasNaCasa === 1) {
        updatedProfile.quantidadeFilhos = 0;
        updatedProfile.temIdoso65Mais = false;
        updatedProfile.temGestante = false;
        updatedProfile.temCrianca0a6 = false;
      }
      return {
        ...state,
        profile: updatedProfile,
      };
    }

    case 'GO_TO_STEP': {
      const newVisited = new Set(state.visitedSteps);
      newVisited.add(WIZARD_STEPS[action.payload].id);
      return {
        ...state,
        currentStepIndex: action.payload,
        visitedSteps: newVisited,
        error: null,
      };
    }

    case 'NEXT_STEP': {
      const visibleSteps = getVisibleSteps(state.profile);
      const currentVisibleIndex = visibleSteps.findIndex(
        (s) => s.id === WIZARD_STEPS[state.currentStepIndex].id
      );
      const nextVisible = visibleSteps[currentVisibleIndex + 1];
      if (nextVisible) {
        const nextIndex = WIZARD_STEPS.findIndex((s) => s.id === nextVisible.id);
        const newVisited = new Set(state.visitedSteps);
        newVisited.add(nextVisible.id);
        return {
          ...state,
          currentStepIndex: nextIndex,
          visitedSteps: newVisited,
          error: null,
        };
      }
      return state;
    }

    case 'PREV_STEP': {
      const visibleSteps = getVisibleSteps(state.profile);
      const currentVisibleIndex = visibleSteps.findIndex(
        (s) => s.id === WIZARD_STEPS[state.currentStepIndex].id
      );
      const prevVisible = visibleSteps[currentVisibleIndex - 1];
      if (prevVisible) {
        const prevIndex = WIZARD_STEPS.findIndex((s) => s.id === prevVisible.id);
        return {
          ...state,
          currentStepIndex: prevIndex,
          error: null,
        };
      }
      return state;
    }

    case 'SET_SUBMITTING':
      return { ...state, isSubmitting: action.payload };

    case 'SET_ERROR':
      return { ...state, error: action.payload };

    case 'RESET':
      return initialState;

    case 'RESTORE':
      return action.payload;

    default:
      return state;
  }
}

// Helper to get visible steps based on profile
export function getVisibleSteps(profile: WizardProfile): WizardStep[] {
  return WIZARD_STEPS.filter((step) => {
    if (step.isConditional && step.shouldShow) {
      return step.shouldShow(profile);
    }
    return true;
  });
}

// Initial state
const initialState: WizardState = {
  profile: DEFAULT_WIZARD_PROFILE,
  currentStepIndex: 0,
  visitedSteps: new Set(['estado']),
  isSubmitting: false,
  error: null,
};

// Context
interface WizardContextValue {
  // State
  profile: WizardProfile;
  currentStep: WizardStep;
  currentStepIndex: number;
  visibleSteps: WizardStep[];
  progress: number;
  isFirstStep: boolean;
  isLastStep: boolean;
  isResultStep: boolean;
  isSubmitting: boolean;
  error: string | null;

  // Actions
  updateProfile: (updates: Partial<WizardProfile>) => void;
  goToStep: (index: number) => void;
  nextStep: () => void;
  prevStep: () => void;
  setSubmitting: (value: boolean) => void;
  setError: (error: string | null) => void;
  reset: () => void;
}

const WizardContext = createContext<WizardContextValue | null>(null);

// Storage key
const STORAGE_KEY = 'tanamaoo_wizard_v2';

// Provider
interface WizardProviderProps {
  children: ReactNode;
}

export function WizardProvider({ children }: WizardProviderProps) {
  const [state, dispatch] = useReducer(wizardReducer, initialState);

  // Restore from localStorage on mount
  useEffect(() => {
    try {
      const saved = localStorage.getItem(STORAGE_KEY);
      if (saved) {
        const parsed = JSON.parse(saved);
        dispatch({
          type: 'RESTORE',
          payload: {
            ...parsed,
            visitedSteps: new Set(parsed.visitedSteps || ['estado']),
          },
        });
      }
    } catch {
      // Ignore errors
    }
  }, []);

  // Save to localStorage on changes
  useEffect(() => {
    try {
      const toSave = {
        ...state,
        visitedSteps: Array.from(state.visitedSteps),
      };
      localStorage.setItem(STORAGE_KEY, JSON.stringify(toSave));
    } catch {
      // Ignore errors
    }
  }, [state]);

  const visibleSteps = getVisibleSteps(state.profile);
  const currentStep = WIZARD_STEPS[state.currentStepIndex];
  const currentVisibleIndex = visibleSteps.findIndex((s) => s.id === currentStep.id);

  const updateProfile = useCallback((updates: Partial<WizardProfile>) => {
    dispatch({ type: 'UPDATE_PROFILE', payload: updates });
  }, []);

  const goToStep = useCallback((index: number) => {
    dispatch({ type: 'GO_TO_STEP', payload: index });
  }, []);

  const nextStep = useCallback(() => {
    dispatch({ type: 'NEXT_STEP' });
  }, []);

  const prevStep = useCallback(() => {
    dispatch({ type: 'PREV_STEP' });
  }, []);

  const setSubmitting = useCallback((value: boolean) => {
    dispatch({ type: 'SET_SUBMITTING', payload: value });
  }, []);

  const setError = useCallback((error: string | null) => {
    dispatch({ type: 'SET_ERROR', payload: error });
  }, []);

  const reset = useCallback(() => {
    localStorage.removeItem(STORAGE_KEY);
    dispatch({ type: 'RESET' });
  }, []);

  // Progress calculation (excluding result step)
  const stepsForProgress = visibleSteps.filter((s) => s.id !== 'resultado');
  const progress = Math.round(((currentVisibleIndex) / stepsForProgress.length) * 100);

  const value: WizardContextValue = {
    profile: state.profile,
    currentStep,
    currentStepIndex: state.currentStepIndex,
    visibleSteps,
    progress: Math.min(progress, 100),
    isFirstStep: currentVisibleIndex === 0,
    isLastStep: currentStep.id === 'interesses',
    isResultStep: currentStep.id === 'resultado',
    isSubmitting: state.isSubmitting,
    error: state.error,
    updateProfile,
    goToStep,
    nextStep,
    prevStep,
    setSubmitting,
    setError,
    reset,
  };

  return <WizardContext.Provider value={value}>{children}</WizardContext.Provider>;
}

// Hook
export function useWizard(): WizardContextValue {
  const context = useContext(WizardContext);
  if (!context) {
    throw new Error('useWizard must be used within a WizardProvider');
  }
  return context;
}
