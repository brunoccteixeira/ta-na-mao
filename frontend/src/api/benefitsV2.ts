/**
 * API client for Benefits V2 endpoints
 * Provides typed access to the unified benefits catalog API
 */

import { api } from './client';
import type { CitizenProfile, Benefit, EligibilityRule, EstimatedValue } from '../engine/types';

// ========== API RESPONSE TYPES ==========

export interface BenefitSummaryAPI {
  id: string;
  name: string;
  shortDescription: string;
  scope: 'federal' | 'state' | 'municipal' | 'sectoral';
  state?: string;
  municipalityIbge?: string;
  estimatedValue?: EstimatedValue;
  status: string;
  icon?: string;
  category?: string;
}

export interface BenefitDetailAPI extends BenefitSummaryAPI {
  sector?: string;
  eligibilityRules: EligibilityRule[];
  whereToApply: string;
  documentsRequired: string[];
  howToApply?: string[];
  sourceUrl?: string;
  lastUpdated: string;
}

export interface BenefitListResponse {
  items: BenefitSummaryAPI[];
  total: number;
  page: number;
  limit: number;
  pages: number;
}

export interface BenefitStatsResponse {
  totalBenefits: number;
  byScope: Record<string, number>;
  byCategory: Record<string, number>;
  statesCovered: number;
  municipalitiesCovered: number;
}

export interface BenefitsByLocationResponse {
  stateCode: string;
  stateName: string;
  municipalityIbge?: string;
  municipalityName?: string;
  federal: BenefitSummaryAPI[];
  state: BenefitSummaryAPI[];
  municipal: BenefitSummaryAPI[];
  sectoral: BenefitSummaryAPI[];
  total: number;
}

// ========== ELIGIBILITY TYPES ==========

export interface RuleEvaluationResult {
  ruleDescription: string;
  passed: boolean;
  inconclusive: boolean;
  field: string;
  expectedValue: unknown;
  actualValue?: unknown;
}

export interface BenefitEligibilityResult {
  benefit: BenefitSummaryAPI;
  status: 'eligible' | 'likely_eligible' | 'maybe' | 'not_eligible' | 'not_applicable' | 'already_receiving';
  matchedRules: string[];
  failedRules: string[];
  inconclusiveRules: string[];
  estimatedValue?: number;
  reason?: string;
  ruleDetails?: RuleEvaluationResult[];
}

export interface EligibilitySummary {
  eligible: BenefitEligibilityResult[];
  likelyEligible: BenefitEligibilityResult[];
  maybe: BenefitEligibilityResult[];
  notEligible: BenefitEligibilityResult[];
  notApplicable: BenefitEligibilityResult[];
  alreadyReceiving: BenefitEligibilityResult[];
  totalAnalyzed: number;
  totalPotentialMonthly: number;
  totalPotentialAnnual: number;
  totalPotentialOneTime: number;
  prioritySteps: string[];
  documentsNeeded: string[];
}

export interface EligibilityResponse {
  profileSummary: Record<string, unknown>;
  summary: EligibilitySummary;
  evaluatedAt: string;
}

export interface EligibilityRequest {
  profile: CitizenProfile;
  scope?: 'federal' | 'state' | 'municipal' | 'sectoral';
  includeNotApplicable?: boolean;
}

// ========== API v2 BASE URL ==========

const V2_BASE = '/v2/benefits';

// ========== BENEFITS ENDPOINTS ==========

/**
 * Fetch paginated list of benefits with optional filters
 */
export async function fetchBenefitsV2(params?: {
  scope?: string;
  state?: string;
  municipalityIbge?: string;
  sector?: string;
  category?: string;
  status?: string;
  search?: string;
  page?: number;
  limit?: number;
}): Promise<BenefitListResponse> {
  const queryParams = new URLSearchParams();

  if (params) {
    Object.entries(params).forEach(([key, value]) => {
      if (value !== undefined && value !== null && value !== '') {
        // Convert camelCase to snake_case for API
        const snakeKey = key.replace(/([A-Z])/g, '_$1').toLowerCase();
        queryParams.append(snakeKey, String(value));
      }
    });
  }

  const queryString = queryParams.toString();
  const url = queryString ? `${V2_BASE}/?${queryString}` : `${V2_BASE}/`;

  const response = await api.get(url);
  return response.data;
}

/**
 * Fetch a single benefit by ID
 */
export async function fetchBenefitByIdV2(benefitId: string): Promise<BenefitDetailAPI> {
  const response = await api.get(`${V2_BASE}/${benefitId}`);
  return response.data;
}

/**
 * Fetch benefits statistics
 */
export async function fetchBenefitsStats(): Promise<BenefitStatsResponse> {
  const response = await api.get(`${V2_BASE}/stats`);
  return response.data;
}

/**
 * Fetch benefits by geographic location
 */
export async function fetchBenefitsByLocation(
  stateCode: string,
  municipalityIbge?: string
): Promise<BenefitsByLocationResponse> {
  const queryParams = municipalityIbge
    ? `?municipality_ibge=${municipalityIbge}`
    : '';

  const response = await api.get(`${V2_BASE}/by-location/${stateCode}${queryParams}`);
  return response.data;
}

// ========== ELIGIBILITY ENDPOINTS ==========

/**
 * Full eligibility check against all benefits
 */
export async function checkEligibilityV2(
  profile: CitizenProfile,
  options?: {
    scope?: 'federal' | 'state' | 'municipal' | 'sectoral';
    includeNotApplicable?: boolean;
  }
): Promise<EligibilityResponse> {
  const request: EligibilityRequest = {
    profile,
    scope: options?.scope,
    includeNotApplicable: options?.includeNotApplicable ?? false,
  };

  const response = await api.post(`${V2_BASE}/eligibility/check`, request);
  return response.data;
}

/**
 * Quick eligibility count (lighter response)
 */
export async function quickEligibilityCheck(
  estado: string,
  rendaFamiliarMensal: number,
  pessoasNaCasa: number,
  cadastradoCadunico: boolean
): Promise<{
  eligibleCount: number;
  maybeCount: number;
  totalPotentialMonthly: number;
  topBenefits: Array<{ name: string; value?: number }>;
}> {
  const params = new URLSearchParams({
    estado,
    renda_familiar_mensal: String(rendaFamiliarMensal),
    pessoas_na_casa: String(pessoasNaCasa),
    cadastrado_cadunico: String(cadastradoCadunico),
  });

  const response = await api.get(`${V2_BASE}/eligibility/quick?${params}`);
  return response.data;
}

// ========== HELPER: CONVERT API TO ENGINE FORMAT ==========

/**
 * Convert API benefit summary to engine Benefit format
 */
export function apiToBenefit(apiBenefit: BenefitDetailAPI): Benefit {
  return {
    id: apiBenefit.id,
    name: apiBenefit.name,
    shortDescription: apiBenefit.shortDescription,
    scope: apiBenefit.scope,
    state: apiBenefit.state,
    municipalityIbge: apiBenefit.municipalityIbge,
    sector: apiBenefit.sector,
    estimatedValue: apiBenefit.estimatedValue,
    eligibilityRules: apiBenefit.eligibilityRules,
    whereToApply: apiBenefit.whereToApply,
    documentsRequired: apiBenefit.documentsRequired,
    howToApply: apiBenefit.howToApply,
    sourceUrl: apiBenefit.sourceUrl,
    lastUpdated: apiBenefit.lastUpdated,
    status: apiBenefit.status as Benefit['status'],
    icon: apiBenefit.icon,
    category: apiBenefit.category,
  };
}

/**
 * Convert API summary to minimal Benefit format (for list views)
 */
export function apiSummaryToBenefit(summary: BenefitSummaryAPI): Partial<Benefit> {
  return {
    id: summary.id,
    name: summary.name,
    shortDescription: summary.shortDescription,
    scope: summary.scope,
    state: summary.state,
    municipalityIbge: summary.municipalityIbge,
    estimatedValue: summary.estimatedValue,
    status: summary.status as Benefit['status'],
    icon: summary.icon,
    category: summary.category,
  };
}
