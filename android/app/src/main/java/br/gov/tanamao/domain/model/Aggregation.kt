package br.gov.tanamao.domain.model

import java.time.LocalDate

/**
 * National-level aggregation statistics.
 */
data class NationalStats(
    val population: Long,
    val cadUnicoFamilies: Long,
    val totalMunicipalities: Int,
    val totalStates: Int,
    val totalBeneficiaries: Long? = null,
    val totalFamilies: Long? = null,
    val totalValueBrl: Double? = null,
    val avgCoverageRate: Double? = null
)

/**
 * State-level aggregation statistics.
 */
data class StateStats(
    val ibgeCode: String,
    val name: String,
    val abbreviation: String,
    val region: Region,
    val population: Long,
    val municipalityCount: Int,
    val totalBeneficiaries: Long?,
    val totalFamilies: Long?,
    val cadUnicoFamilies: Long?,
    val totalValueBrl: Double?,
    val avgCoverageRate: Double?
)

/**
 * Region-level aggregation statistics.
 */
data class RegionStats(
    val code: Region,
    val name: String,
    val population: Long,
    val stateCount: Int,
    val municipalityCount: Int,
    val totalBeneficiaries: Long?,
    val totalFamilies: Long?,
    val totalValueBrl: Double?,
    val avgCoverageRate: Double?
)

/**
 * Time series data point for trend analysis.
 */
data class TimeSeriesPoint(
    val date: LocalDate,
    val monthLabel: String,
    val totalBeneficiaries: Long,
    val totalFamilies: Long,
    val totalValueBrl: Double,
    val avgCoverageRate: Double
)

/**
 * Demographics data from CadÚnico.
 */
data class Demographics(
    val totalFamilies: Long,
    val totalPersons: Long,
    val incomeBrackets: IncomeBrackets,
    val ageDistribution: AgeDistribution
)

/**
 * Income bracket distribution.
 */
data class IncomeBrackets(
    val extremePoverty: Long,  // < R$ 105/capita
    val poverty: Long,          // R$ 105 - R$ 218/capita
    val lowIncome: Long         // up to 1/2 min wage
)

/**
 * Age distribution of registered persons.
 */
data class AgeDistribution(
    val age0to5: Long,
    val age6to14: Long,
    val age15to17: Long,
    val age18to64: Long,
    val age65plus: Long
)
