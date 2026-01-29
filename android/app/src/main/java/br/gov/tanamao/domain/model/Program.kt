package br.gov.tanamao.domain.model

import java.time.LocalDate

/**
 * Domain model for a social benefit program.
 */
data class Program(
    val code: ProgramCode,
    val name: String,
    val description: String,
    val dataSourceUrl: String,
    val updateFrequency: UpdateFrequency,
    val nationalStats: ProgramStats?
)

/**
 * Program codes for social benefit programs.
 */
enum class ProgramCode(val displayName: String, val abbreviation: String) {
    CADUNICO("Bolsa Família / CadÚnico", "BF"),
    BPC("BPC/LOAS", "BPC"),
    FARMACIA_POPULAR("Farmácia Popular", "Farm"),
    TSEE("Tarifa Social de Energia", "TSEE"),
    DIGNIDADE_MENSTRUAL("Dignidade Menstrual", "Dig")
}

/**
 * Update frequency for program data.
 */
enum class UpdateFrequency {
    MONTHLY,
    QUARTERLY,
    YEARLY
}

/**
 * Statistics for a program at national level.
 */
data class ProgramStats(
    val totalBeneficiaries: Long,
    val totalFamilies: Long,
    val totalValueBrl: Double,
    val avgCoverageRate: Double? = null,
    val municipalitiesCovered: Int? = null,
    val totalMunicipalities: Int? = null,
    val latestDataDate: LocalDate? = null
)
