'use client';

/**
 * React Query hooks for Benefits V2 API
 * Provides caching, offline fallback, and loading states
 */

import { useQuery, useMutation, useQueryClient } from '@tanstack/react-query';
import {
  fetchBenefitsV2,
  fetchBenefitByIdV2,
  fetchBenefitsStats,
  fetchBenefitsByLocation,
  checkEligibilityV2,
  quickEligibilityCheck,
  apiToBenefit,
  type BenefitListResponse,
  type BenefitDetailAPI,
  type BenefitSummaryAPI,
  type BenefitStatsResponse,
  type BenefitsByLocationResponse,
  type EligibilityResponse,
} from '../api/benefitsV2';

import {
  getBenefitsCatalog,
  getAllBenefits,
  getBenefitById,
  getBenefitsForState,
  getBenefitsForMunicipality,
  getCatalogStats,
} from '../engine/catalog';
import type { Benefit, CitizenProfile } from '../engine/types';

// Re-export API types for convenience
export type { BenefitSummaryAPI, BenefitDetailAPI, BenefitListResponse, EligibilityResponse };

// ========== CACHE CONFIGURATION ==========

const CACHE_KEY_PREFIX = 'tnm_benefits_v2_';
const CACHE_TTL_MS = 24 * 60 * 60 * 1000; // 24 hours

interface CacheEntry<T> {
  data: T;
  timestamp: number;
  expiresAt: number;
}

// ========== LOCAL STORAGE CACHE HELPERS ==========

function getLocalCache<T>(key: string): T | null {
  try {
    const raw = localStorage.getItem(`${CACHE_KEY_PREFIX}${key}`);
    if (!raw) return null;

    const entry: CacheEntry<T> = JSON.parse(raw);
    if (Date.now() > entry.expiresAt) {
      localStorage.removeItem(`${CACHE_KEY_PREFIX}${key}`);
      return null;
    }

    return entry.data;
  } catch {
    return null;
  }
}

function setLocalCache<T>(key: string, data: T): void {
  try {
    const entry: CacheEntry<T> = {
      data,
      timestamp: Date.now(),
      expiresAt: Date.now() + CACHE_TTL_MS,
    };
    localStorage.setItem(`${CACHE_KEY_PREFIX}${key}`, JSON.stringify(entry));
  } catch {
    // localStorage might be full or disabled
    console.warn('Failed to save to localStorage cache');
  }
}

function clearBenefitsCache(): void {
  try {
    const keys = Object.keys(localStorage).filter(k => k.startsWith(CACHE_KEY_PREFIX));
    keys.forEach(k => localStorage.removeItem(k));
  } catch {
    console.warn('Failed to clear localStorage cache');
  }
}

// ========== TYPES ==========

export interface UseBenefitsListOptions {
  scope?: string;
  state?: string;
  municipalityIbge?: string;
  sector?: string;
  category?: string;
  search?: string;
  page?: number;
  limit?: number;
  enabled?: boolean;
}

// ========== QUERY KEYS ==========

export const benefitsKeys = {
  all: ['benefits', 'v2'] as const,
  lists: () => [...benefitsKeys.all, 'list'] as const,
  list: (filters: UseBenefitsListOptions) => [...benefitsKeys.lists(), filters] as const,
  details: () => [...benefitsKeys.all, 'detail'] as const,
  detail: (id: string) => [...benefitsKeys.details(), id] as const,
  stats: () => [...benefitsKeys.all, 'stats'] as const,
  byLocation: (state: string, ibge?: string) => [...benefitsKeys.all, 'location', state, ibge] as const,
  eligibility: () => [...benefitsKeys.all, 'eligibility'] as const,
};

// ========== HOOKS ==========

/**
 * Hook to fetch paginated benefits list with filters
 * Falls back to static JSON if API is unavailable
 */
export function useBenefitsList(options: UseBenefitsListOptions = {}) {
  const { enabled = true, ...filters } = options;
  const cacheKey = `list_${JSON.stringify(filters)}`;

  return useQuery({
    queryKey: benefitsKeys.list(filters),
    queryFn: async (): Promise<BenefitListResponse> => {
      try {
        const response = await fetchBenefitsV2(filters);
        setLocalCache(cacheKey, response);
        return response;
      } catch (error) {
        console.warn('API unavailable, trying cache/fallback:', error);

        // Try localStorage cache first
        const cached = getLocalCache<BenefitListResponse>(cacheKey);
        if (cached) {
          console.log('Using localStorage cache');
          return cached;
        }

        // Fallback to static JSON
        console.log('Using static JSON fallback');
        const catalog = getBenefitsCatalog();
        let benefits = getAllBenefits(catalog);

        // Apply filters locally
        if (filters.scope) {
          benefits = benefits.filter(b => b.scope === filters.scope);
        }
        if (filters.state) {
          benefits = benefits.filter(
            b => b.state === filters.state || b.scope === 'federal'
          );
        }
        if (filters.search) {
          const searchLower = filters.search.toLowerCase();
          benefits = benefits.filter(
            b =>
              b.name.toLowerCase().includes(searchLower) ||
              b.shortDescription.toLowerCase().includes(searchLower)
          );
        }
        if (filters.category) {
          benefits = benefits.filter(b => b.category === filters.category);
        }

        const items = benefits.map(b => ({
          id: b.id,
          name: b.name,
          shortDescription: b.shortDescription,
          scope: b.scope,
          state: b.state,
          municipalityIbge: b.municipalityIbge,
          estimatedValue: b.estimatedValue,
          status: b.status,
          icon: b.icon,
          category: b.category,
        }));

        return {
          items,
          total: items.length,
          page: 1,
          limit: items.length,
          pages: 1,
        };
      }
    },
    enabled,
    staleTime: 5 * 60 * 1000, // 5 minutes
    gcTime: CACHE_TTL_MS,
    retry: 1,
    retryDelay: 1000,
  });
}

/**
 * Hook to fetch a single benefit detail
 * Falls back to static JSON if API is unavailable
 */
export function useBenefitDetail(benefitId: string | undefined) {
  const cacheKey = `detail_${benefitId}`;

  return useQuery({
    queryKey: benefitsKeys.detail(benefitId || ''),
    queryFn: async (): Promise<Benefit> => {
      if (!benefitId) {
        throw new Error('Benefit ID is required');
      }

      try {
        const response = await fetchBenefitByIdV2(benefitId);
        setLocalCache(cacheKey, response);
        return apiToBenefit(response);
      } catch (error) {
        console.warn('API unavailable, trying cache/fallback:', error);

        // Try localStorage cache first
        const cached = getLocalCache<BenefitDetailAPI>(cacheKey);
        if (cached) {
          console.log('Using localStorage cache');
          return apiToBenefit(cached);
        }

        // Fallback to static JSON
        console.log('Using static JSON fallback');
        const catalog = getBenefitsCatalog();
        const benefit = getBenefitById(catalog, benefitId);

        if (!benefit) {
          throw new Error(`Benefit ${benefitId} not found`);
        }

        return benefit;
      }
    },
    enabled: !!benefitId,
    staleTime: 5 * 60 * 1000,
    gcTime: CACHE_TTL_MS,
    retry: 1,
  });
}

/**
 * Hook to fetch catalog statistics
 */
export function useBenefitsStats() {
  const cacheKey = 'stats';

  return useQuery({
    queryKey: benefitsKeys.stats(),
    queryFn: async (): Promise<BenefitStatsResponse> => {
      try {
        const response = await fetchBenefitsStats();
        setLocalCache(cacheKey, response);
        return response;
      } catch (error) {
        console.warn('API unavailable, using fallback:', error);

        // Try localStorage cache
        const cached = getLocalCache<BenefitStatsResponse>(cacheKey);
        if (cached) {
          return cached;
        }

        // Fallback to static JSON stats
        const catalog = getBenefitsCatalog();
        const stats = getCatalogStats(catalog);

        return {
          totalBenefits: stats.totalBenefits,
          byScope: {
            federal: stats.federalCount,
            state: stats.stateCount,
            municipal: stats.municipalCount,
            sectoral: stats.sectoralCount,
          },
          byCategory: stats.benefitsByCategory,
          statesCovered: stats.statesWithBenefits,
          municipalitiesCovered: stats.municipalitiesWithBenefits,
        };
      }
    },
    staleTime: 30 * 60 * 1000, // 30 minutes
    gcTime: CACHE_TTL_MS,
  });
}

/**
 * Hook to fetch benefits by geographic location
 */
export function useBenefitsByLocation(stateCode: string, municipalityIbge?: string) {
  const cacheKey = `location_${stateCode}_${municipalityIbge || 'all'}`;

  return useQuery({
    queryKey: benefitsKeys.byLocation(stateCode, municipalityIbge),
    queryFn: async (): Promise<BenefitsByLocationResponse> => {
      try {
        const response = await fetchBenefitsByLocation(stateCode, municipalityIbge);
        setLocalCache(cacheKey, response);
        return response;
      } catch (error) {
        console.warn('API unavailable, using fallback:', error);

        // Try localStorage cache
        const cached = getLocalCache<BenefitsByLocationResponse>(cacheKey);
        if (cached) {
          return cached;
        }

        // Fallback to static JSON
        const catalog = getBenefitsCatalog();
        const benefits = municipalityIbge
          ? getBenefitsForMunicipality(catalog, stateCode, municipalityIbge)
          : getBenefitsForState(catalog, stateCode);

        const toSummary = (b: Benefit) => ({
          id: b.id,
          name: b.name,
          shortDescription: b.shortDescription,
          scope: b.scope,
          state: b.state,
          municipalityIbge: b.municipalityIbge,
          estimatedValue: b.estimatedValue,
          status: b.status,
          icon: b.icon,
          category: b.category,
        });

        return {
          stateCode,
          stateName: stateCode, // Would need lookup for full name
          municipalityIbge,
          municipalityName: undefined,
          federal: benefits.filter(b => b.scope === 'federal').map(toSummary),
          state: benefits.filter(b => b.scope === 'state').map(toSummary),
          municipal: benefits.filter(b => b.scope === 'municipal').map(toSummary),
          sectoral: benefits.filter(b => b.scope === 'sectoral').map(toSummary),
          total: benefits.length,
        };
      }
    },
    enabled: !!stateCode,
    staleTime: 5 * 60 * 1000,
    gcTime: CACHE_TTL_MS,
  });
}

/**
 * Mutation hook for full eligibility check
 */
export function useEligibilityCheck() {
  const queryClient = useQueryClient();

  return useMutation({
    mutationFn: async (params: {
      profile: CitizenProfile;
      scope?: 'federal' | 'state' | 'municipal' | 'sectoral';
      includeNotApplicable?: boolean;
    }): Promise<EligibilityResponse> => {
      return checkEligibilityV2(params.profile, {
        scope: params.scope,
        includeNotApplicable: params.includeNotApplicable,
      });
    },
    onSuccess: () => {
      // Invalidate related queries if needed
      queryClient.invalidateQueries({ queryKey: benefitsKeys.eligibility() });
    },
  });
}

/**
 * Mutation hook for quick eligibility count
 */
export function useQuickEligibilityCheck() {
  return useMutation({
    mutationFn: async (params: {
      estado: string;
      rendaFamiliarMensal: number;
      pessoasNaCasa: number;
      cadastradoCadunico: boolean;
    }) => {
      return quickEligibilityCheck(
        params.estado,
        params.rendaFamiliarMensal,
        params.pessoasNaCasa,
        params.cadastradoCadunico
      );
    },
  });
}

// ========== PREFETCH HELPERS ==========

/**
 * Prefetch benefits list for faster navigation
 */
export function usePrefetchBenefitsList(queryClient: ReturnType<typeof useQueryClient>) {
  return (filters: UseBenefitsListOptions = {}) => {
    queryClient.prefetchQuery({
      queryKey: benefitsKeys.list(filters),
      queryFn: () => fetchBenefitsV2(filters),
      staleTime: 5 * 60 * 1000,
    });
  };
}

/**
 * Prefetch benefit detail for faster navigation
 */
export function usePrefetchBenefitDetail(queryClient: ReturnType<typeof useQueryClient>) {
  return (benefitId: string) => {
    queryClient.prefetchQuery({
      queryKey: benefitsKeys.detail(benefitId),
      queryFn: async () => {
        const response = await fetchBenefitByIdV2(benefitId);
        return apiToBenefit(response);
      },
      staleTime: 5 * 60 * 1000,
    });
  };
}

// ========== CACHE MANAGEMENT ==========

export { clearBenefitsCache };
