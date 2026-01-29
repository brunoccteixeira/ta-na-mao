package br.gov.tanamao.domain.model

import java.time.LocalDate

/**
 * Statistics about user's profile and benefits
 */
data class ProfileStats(
    val totalReceived: Double = 0.0,
    val totalReceivedThisYear: Double = 0.0,
    val activeBenefitsCount: Int = 0,
    val totalMonthlyValue: Double = 0.0,
    val consultationsCount: Int = 0,
    val lastConsultationDate: LocalDate? = null,
    val benefitsDiscovered: Int = 0,
    val moneyFound: Double? = null
)

/**
 * History of user consultations with the agent
 */
data class ConsultationHistory(
    val id: String,
    val date: LocalDate,
    val type: ConsultationType,
    val query: String,
    val result: String? = null,
    val toolsUsed: List<String> = emptyList(),
    val success: Boolean = true
)

enum class ConsultationType {
    ELIGIBILITY_CHECK,
    MONEY_CHECK,
    DOCUMENT_GUIDANCE,
    LOCATION_SEARCH,
    PRESCRIPTION_PROCESSING,
    GENERAL_QUESTION
}



