package br.gov.tanamao.domain.model

/**
 * Domain model for a Brazilian municipality.
 */
data class Municipality(
    val ibgeCode: String,
    val name: String,
    val stateAbbreviation: String,
    val stateName: String,
    val region: Region,
    val population: Int,
    val areaKm2: Double? = null,
    val cadUnicoFamilies: Int? = null,
    val totalBeneficiaries: Int? = null,
    val totalFamilies: Int? = null,
    val totalValueBrl: Double? = null,
    val coverageRate: Double? = null
)

/**
 * Search result for municipality autocomplete.
 */
data class MunicipalitySearchResult(
    val ibgeCode: String,
    val name: String,
    val stateAbbreviation: String,
    val population: Int?
)

/**
 * Program data for a specific municipality.
 */
data class MunicipalityProgram(
    val code: ProgramCode,
    val name: String,
    val totalBeneficiaries: Int?,
    val totalFamilies: Int?,
    val totalValueBrl: Double?,
    val coverageRate: Double?,
    val referenceDate: String?
)

/**
 * Brazilian geographic regions.
 */
enum class Region(val displayName: String, val emoji: String) {
    N("Norte", "\uD83C\uDF33"),
    NE("Nordeste", "☀\uFE0F"),
    CO("Centro-Oeste", "\uD83C\uDF3E"),
    SE("Sudeste", "\uD83C\uDFD9\uFE0F"),
    S("Sul", "❄\uFE0F")
}
