package br.gov.tanamao.domain.repository

import br.gov.tanamao.data.api.dto.BenefitDetailDto
import br.gov.tanamao.data.api.dto.BenefitSummaryDto
import br.gov.tanamao.data.api.dto.BenefitStatsResponseDto
import br.gov.tanamao.data.api.dto.BenefitsByLocationResponseDto
import br.gov.tanamao.data.api.dto.CitizenProfileDto
import br.gov.tanamao.data.api.dto.EligibilityResponseDto
import br.gov.tanamao.data.api.dto.QuickEligibilityResponseDto
import br.gov.tanamao.domain.model.Result
import kotlinx.coroutines.flow.Flow

/**
 * Repository interface for Benefits API v2.
 * Provides access to the unified benefits catalog with offline support.
 */
interface BenefitsV2Repository {

    // ========== BENEFITS CATALOG ==========

    /**
     * Get all benefits with optional refresh from API.
     * Uses cache-first strategy: returns cached data immediately,
     * then fetches from API and updates.
     *
     * @param forceRefresh Force fetch from API, ignoring cache
     */
    fun getBenefits(forceRefresh: Boolean = false): Flow<Result<List<BenefitSummaryDto>>>

    /**
     * Get benefits filtered by scope.
     */
    suspend fun getBenefitsByScope(
        scope: String,
        forceRefresh: Boolean = false
    ): Result<List<BenefitSummaryDto>>

    /**
     * Get benefits for a specific state (federal + state + sectoral).
     */
    suspend fun getBenefitsForState(
        stateCode: String,
        forceRefresh: Boolean = false
    ): Result<List<BenefitSummaryDto>>

    /**
     * Get benefits for a specific municipality (federal + state + municipal + sectoral).
     */
    suspend fun getBenefitsForMunicipality(
        stateCode: String,
        municipalityIbge: String,
        forceRefresh: Boolean = false
    ): Result<BenefitsByLocationResponseDto>

    /**
     * Get a single benefit by ID.
     */
    suspend fun getBenefitDetail(benefitId: String): Result<BenefitDetailDto>

    /**
     * Search benefits by name or description.
     */
    suspend fun searchBenefits(query: String): Result<List<BenefitSummaryDto>>

    /**
     * Get catalog statistics.
     */
    suspend fun getStats(): Result<BenefitStatsResponseDto>

    // ========== ELIGIBILITY ==========

    /**
     * Full eligibility check against all benefits.
     */
    suspend fun checkEligibility(
        profile: CitizenProfileDto,
        scope: String? = null,
        includeNotApplicable: Boolean = false
    ): Result<EligibilityResponseDto>

    /**
     * Quick eligibility count (lighter response).
     */
    suspend fun quickEligibilityCheck(
        estado: String,
        rendaFamiliarMensal: Double,
        pessoasNaCasa: Int,
        cadastradoCadunico: Boolean
    ): Result<QuickEligibilityResponseDto>

    // ========== CACHE MANAGEMENT ==========

    /**
     * Check if cache has valid data.
     */
    suspend fun hasCachedData(): Boolean

    /**
     * Clear all cached benefits.
     */
    suspend fun clearCache()

    /**
     * Sync cache with API (background operation).
     */
    suspend fun syncCache(): Result<Int>
}
