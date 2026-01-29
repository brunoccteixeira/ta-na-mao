package br.gov.tanamao.domain.model

/**
 * Model for forgotten money (PIS/PASEP, SVR, FGTS)
 */
data class MoneyForgotten(
    val totalAvailable: Double = 42_000_000_000.0, // R$ 42 bilhões
    val pisPasep: MoneyType,
    val svr: MoneyType,
    val fgts: MoneyType
)

data class MoneyType(
    val name: String,
    val totalAvailable: Double,
    val eligiblePeople: Long,
    val deadline: String? = null,
    val description: String,
    val guideSteps: List<String> = emptyList()
)

/**
 * Result from checking forgotten money for a user
 */
data class MoneyCheckResult(
    val hasMoney: Boolean,
    val totalAmount: Double? = null,
    val types: List<MoneyTypeResult> = emptyList(),
    val message: String
)

data class MoneyTypeResult(
    val type: String, // PIS_PASEP, SVR, FGTS
    val hasMoney: Boolean,
    val amount: Double? = null,
    val status: String,
    val nextSteps: List<String> = emptyList()
)



