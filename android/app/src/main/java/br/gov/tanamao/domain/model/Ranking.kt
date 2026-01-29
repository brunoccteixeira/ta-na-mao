package br.gov.tanamao.domain.model

/**
 * Ranking item for municipality rankings.
 */
data class RankingItem(
    val rank: Int,
    val ibgeCode: String,
    val name: String,
    val stateAbbreviation: String? = null,
    val totalBeneficiaries: Int,
    val totalFamilies: Int,
    val coverageRate: Double,
    val totalValueBrl: Double,
    val referenceDate: String
)

/**
 * Order criteria for rankings.
 */
enum class RankingOrderBy(val value: String) {
    BENEFICIARIES("beneficiaries"),
    COVERAGE("coverage"),
    VALUE("value")
}
