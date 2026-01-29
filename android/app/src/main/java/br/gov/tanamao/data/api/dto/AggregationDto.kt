package br.gov.tanamao.data.api.dto

import com.google.gson.annotations.SerializedName

/**
 * DTO for national aggregation response.
 */
data class NationalAggregationDto(
    val level: String,
    val population: Long,
    @SerializedName("cadunico_families") val cadUnicoFamilies: Long,
    @SerializedName("total_municipalities") val totalMunicipalities: Int,
    @SerializedName("total_states") val totalStates: Int,
    @SerializedName("program_stats") val programStats: ProgramStatsDto?
)

/**
 * DTO for states aggregation response.
 */
data class StatesAggregationDto(
    val level: String,
    val count: Int,
    val states: List<StateAggregationDto>
)

/**
 * DTO for a single state aggregation.
 */
data class StateAggregationDto(
    @SerializedName("ibge_code") val ibgeCode: String,
    val name: String,
    val abbreviation: String,
    val region: String,
    val population: Long,
    @SerializedName("municipality_count") val municipalityCount: Int,
    @SerializedName("total_beneficiaries") val totalBeneficiaries: Long?,
    @SerializedName("total_families") val totalFamilies: Long?,
    @SerializedName("cadunico_families") val cadUnicoFamilies: Long?,
    @SerializedName("total_value_brl") val totalValueBrl: Double?,
    @SerializedName("avg_coverage_rate") val avgCoverageRate: Double?
)

/**
 * DTO for state detail response.
 */
data class StateDetailDto(
    val level: String,
    val state: StateInfoDto,
    @SerializedName("municipality_count") val municipalityCount: Int,
    val municipalities: List<MunicipalityAggregationDto>
)

/**
 * DTO for state info.
 */
data class StateInfoDto(
    @SerializedName("ibge_code") val ibgeCode: String,
    val name: String,
    val abbreviation: String,
    val region: String
)

/**
 * DTO for municipality in aggregation.
 */
data class MunicipalityAggregationDto(
    @SerializedName("ibge_code") val ibgeCode: String,
    val name: String,
    val population: Int,
    @SerializedName("total_beneficiaries") val totalBeneficiaries: Int?,
    @SerializedName("total_families") val totalFamilies: Int?,
    @SerializedName("avg_coverage_rate") val avgCoverageRate: Double?
)

/**
 * DTO for regions aggregation response.
 */
data class RegionsAggregationDto(
    val level: String,
    val count: Int,
    val regions: List<RegionAggregationDto>
)

/**
 * DTO for a single region aggregation.
 */
data class RegionAggregationDto(
    val code: String,
    val name: String,
    val population: Long,
    @SerializedName("state_count") val stateCount: Int,
    @SerializedName("municipality_count") val municipalityCount: Int,
    @SerializedName("total_beneficiaries") val totalBeneficiaries: Long?,
    @SerializedName("total_families") val totalFamilies: Long?,
    @SerializedName("total_value_brl") val totalValueBrl: Double?,
    @SerializedName("avg_coverage_rate") val avgCoverageRate: Double?
)

/**
 * DTO for time series response.
 */
data class TimeSeriesDto(
    val level: String,
    val count: Int,
    val data: List<TimeSeriesPointDto>
)

/**
 * DTO for a time series data point.
 */
data class TimeSeriesPointDto(
    val date: String,
    val month: String,
    @SerializedName("total_beneficiaries") val totalBeneficiaries: Long,
    @SerializedName("total_families") val totalFamilies: Long,
    @SerializedName("total_value_brl") val totalValueBrl: Double,
    @SerializedName("avg_coverage_rate") val avgCoverageRate: Double
)

/**
 * DTO for demographics response.
 */
data class DemographicsDto(
    val level: String,
    @SerializedName("total_families") val totalFamilies: Long,
    @SerializedName("total_persons") val totalPersons: Long,
    @SerializedName("income_brackets") val incomeBrackets: IncomeBracketsDto,
    @SerializedName("age_distribution") val ageDistribution: AgeDistributionDto
)

/**
 * DTO for income brackets.
 */
data class IncomeBracketsDto(
    @SerializedName("extreme_poverty") val extremePoverty: Long,
    val poverty: Long,
    @SerializedName("low_income") val lowIncome: Long
)

/**
 * DTO for age distribution.
 */
data class AgeDistributionDto(
    @SerializedName("0_5") val age0to5: Long,
    @SerializedName("6_14") val age6to14: Long,
    @SerializedName("15_17") val age15to17: Long,
    @SerializedName("18_64") val age18to64: Long,
    @SerializedName("65_plus") val age65plus: Long
)
