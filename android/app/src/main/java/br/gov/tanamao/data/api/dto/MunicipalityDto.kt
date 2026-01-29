package br.gov.tanamao.data.api.dto

import com.google.gson.annotations.SerializedName

/**
 * DTO for municipality in list response.
 */
data class MunicipalityDto(
    @SerializedName("ibge_code") val ibgeCode: String,
    val name: String,
    @SerializedName("state_id") val stateId: Int,
    val population: Int?,
    @SerializedName("area_km2") val areaKm2: Double?
)

/**
 * DTO for municipality search result.
 */
data class MunicipalitySearchDto(
    @SerializedName("ibge_code") val ibgeCode: String,
    val name: String,
    @SerializedName("state_id") val stateId: Int,
    val population: Int?
)

/**
 * DTO for municipality detail response.
 */
data class MunicipalityDetailDto(
    @SerializedName("ibge_code") val ibgeCode: String,
    val name: String,
    @SerializedName("state_abbreviation") val stateAbbreviation: String,
    @SerializedName("state_name") val stateName: String,
    val region: String,
    val population: Int,
    @SerializedName("area_km2") val areaKm2: Double?,
    @SerializedName("cadunico_families") val cadUnicoFamilies: Int?,
    @SerializedName("total_beneficiaries") val totalBeneficiaries: Int?,
    @SerializedName("total_families") val totalFamilies: Int?,
    @SerializedName("total_value_brl") val totalValueBrl: Double?,
    @SerializedName("coverage_rate") val coverageRate: Double?
)

/**
 * DTO for municipality programs response.
 */
data class MunicipalityProgramsDto(
    @SerializedName("ibge_code") val ibgeCode: String,
    val name: String,
    val programs: List<MunicipalityProgramDto>
)

/**
 * DTO for a program in a municipality.
 */
data class MunicipalityProgramDto(
    val code: String,
    val name: String,
    @SerializedName("total_beneficiaries") val totalBeneficiaries: Int?,
    @SerializedName("total_families") val totalFamilies: Int?,
    @SerializedName("total_value_brl") val totalValueBrl: Double?,
    @SerializedName("coverage_rate") val coverageRate: Double?,
    @SerializedName("reference_date") val referenceDate: String?
)

/**
 * Generic paginated response.
 */
data class PaginatedResponseDto<T>(
    val items: List<T>,
    val total: Int,
    val page: Int,
    val limit: Int,
    val pages: Int
)
