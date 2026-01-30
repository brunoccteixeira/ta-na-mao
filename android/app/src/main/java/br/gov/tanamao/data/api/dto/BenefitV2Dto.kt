package br.gov.tanamao.data.api.dto

import com.google.gson.annotations.SerializedName

/**
 * DTOs for Benefits API v2 - unified benefits catalog
 */

// ========== BENEFIT LIST ==========

/**
 * Paginated list of benefits response.
 */
data class BenefitListResponseDto(
    val items: List<BenefitSummaryDto>,
    val total: Int,
    val page: Int,
    val limit: Int,
    val pages: Int
)

/**
 * Summary of a benefit for list views.
 */
data class BenefitSummaryDto(
    val id: String,
    val name: String,
    @SerializedName("short_description") val shortDescription: String,
    val scope: String, // "federal", "state", "municipal", "sectoral"
    val state: String?,
    @SerializedName("municipality_ibge") val municipalityIbge: String?,
    @SerializedName("estimated_value") val estimatedValue: EstimatedValueDto?,
    val status: String, // "active", "suspended", "ended"
    val icon: String?,
    val category: String?
)

/**
 * Estimated value for a benefit.
 */
data class EstimatedValueDto(
    val type: String, // "monthly", "annual", "one_time"
    val min: Double?,
    val max: Double?,
    val description: String?
)

// ========== BENEFIT DETAIL ==========

/**
 * Full benefit detail response.
 */
data class BenefitDetailDto(
    val id: String,
    val name: String,
    @SerializedName("short_description") val shortDescription: String,
    val scope: String,
    val state: String?,
    @SerializedName("municipality_ibge") val municipalityIbge: String?,
    val sector: String?,
    @SerializedName("estimated_value") val estimatedValue: EstimatedValueDto?,
    @SerializedName("eligibility_rules") val eligibilityRules: List<EligibilityRuleDto>,
    @SerializedName("where_to_apply") val whereToApply: String,
    @SerializedName("documents_required") val documentsRequired: List<String>,
    @SerializedName("how_to_apply") val howToApply: List<String>?,
    @SerializedName("source_url") val sourceUrl: String?,
    @SerializedName("last_updated") val lastUpdated: String,
    val status: String,
    val icon: String?,
    val category: String?
)

/**
 * Single eligibility rule for a benefit.
 */
data class EligibilityRuleDto(
    val field: String,
    val operator: String, // "lte", "gte", "eq", "in", etc.
    val value: Any,
    val description: String
)

// ========== BENEFIT STATS ==========

/**
 * Statistics about the benefits catalog.
 */
data class BenefitStatsResponseDto(
    @SerializedName("total_benefits") val totalBenefits: Int,
    @SerializedName("by_scope") val byScope: Map<String, Int>,
    @SerializedName("by_category") val byCategory: Map<String, Int>,
    @SerializedName("states_covered") val statesCovered: Int,
    @SerializedName("municipalities_covered") val municipalitiesCovered: Int
)

// ========== BENEFITS BY LOCATION ==========

/**
 * Benefits grouped by location (federal + state + municipal + sectoral).
 */
data class BenefitsByLocationResponseDto(
    @SerializedName("state_code") val stateCode: String,
    @SerializedName("state_name") val stateName: String,
    @SerializedName("municipality_ibge") val municipalityIbge: String?,
    @SerializedName("municipality_name") val municipalityName: String?,
    val federal: List<BenefitSummaryDto>,
    val state: List<BenefitSummaryDto>,
    val municipal: List<BenefitSummaryDto>,
    val sectoral: List<BenefitSummaryDto>,
    val total: Int
)
