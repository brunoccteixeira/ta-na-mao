package br.gov.tanamao.data.api.dto

import com.google.gson.annotations.SerializedName

/**
 * DTO for program list response.
 */
data class ProgramDto(
    val code: String,
    val name: String,
    val description: String,
    @SerializedName("data_source_url") val dataSourceUrl: String,
    @SerializedName("update_frequency") val updateFrequency: String,
    @SerializedName("national_stats") val nationalStats: ProgramStatsDto?
)

/**
 * DTO for program statistics.
 */
data class ProgramStatsDto(
    @SerializedName("total_beneficiaries") val totalBeneficiaries: Long,
    @SerializedName("total_families") val totalFamilies: Long,
    @SerializedName("total_value_brl") val totalValueBrl: Double,
    @SerializedName("latest_data_date") val latestDataDate: String?
)

/**
 * DTO for program detail response.
 */
data class ProgramDetailDto(
    val code: String,
    val name: String,
    val description: String,
    @SerializedName("data_source_url") val dataSourceUrl: String,
    @SerializedName("update_frequency") val updateFrequency: String,
    @SerializedName("national_stats") val nationalStats: ProgramDetailStatsDto?
)

/**
 * DTO for detailed program statistics.
 */
data class ProgramDetailStatsDto(
    @SerializedName("total_beneficiaries") val totalBeneficiaries: Long,
    @SerializedName("total_families") val totalFamilies: Long,
    @SerializedName("total_value_brl") val totalValueBrl: Double,
    @SerializedName("avg_coverage_rate") val avgCoverageRate: Double?,
    @SerializedName("municipalities_covered") val municipalitiesCovered: Int?,
    @SerializedName("total_municipalities") val totalMunicipalities: Int?,
    @SerializedName("coverage_percentage") val coveragePercentage: Double?
)

/**
 * DTO for ranking response.
 */
data class RankingResponseDto(
    @SerializedName("program_code") val programCode: String,
    @SerializedName("program_name") val programName: String,
    @SerializedName("order_by") val orderBy: String,
    val ranking: List<RankingItemDto>
)

/**
 * DTO for ranking item.
 */
data class RankingItemDto(
    val rank: Int,
    @SerializedName("ibge_code") val ibgeCode: String,
    val name: String,
    @SerializedName("total_beneficiaries") val totalBeneficiaries: Int,
    @SerializedName("total_families") val totalFamilies: Int,
    @SerializedName("coverage_rate") val coverageRate: Double,
    @SerializedName("total_value_brl") val totalValueBrl: Double,
    @SerializedName("reference_date") val referenceDate: String
)
