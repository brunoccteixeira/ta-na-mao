package br.gov.tanamao.domain.model

import java.time.LocalDate
import java.time.YearMonth

/**
 * Represents a social benefit that a user is receiving or eligible for
 */
data class UserBenefit(
    val id: String,
    val programCode: String,
    val programName: String,
    val status: BenefitStatus,
    val monthlyValue: Double? = null,
    val lastPaymentDate: LocalDate? = null,
    val nextPaymentDate: LocalDate? = null,
    val paymentHistory: List<PaymentRecord> = emptyList(),
    val eligibilityDetails: EligibilityDetails? = null
)

/**
 * Status of a benefit for a user
 */
enum class BenefitStatus {
    /** Actively receiving the benefit */
    ACTIVE,
    /** Application submitted, waiting for response */
    PENDING,
    /** Eligible but not yet applied */
    ELIGIBLE,
    /** Not eligible for this benefit */
    NOT_ELIGIBLE,
    /** Benefit was blocked or suspended */
    BLOCKED
}

/**
 * Record of a benefit payment
 */
data class PaymentRecord(
    val id: String,
    val date: LocalDate,
    val value: Double,
    val reference: YearMonth,
    val status: PaymentStatus
)

enum class PaymentStatus {
    PAID,
    PENDING,
    FAILED,
    RETURNED
}

/**
 * Details about eligibility assessment
 */
data class EligibilityDetails(
    val criteria: List<EligibilityCriterion>,
    val assessmentDate: LocalDate,
    val overallScore: Float,
    val recommendation: String? = null
)

data class EligibilityCriterion(
    val name: String,
    val description: String,
    val isMet: Boolean,
    val details: String? = null
)

/**
 * Alert/notification for the user
 */
data class UserAlert(
    val id: String,
    val type: AlertCategory,
    val title: String,
    val message: String,
    val actionLabel: String? = null,
    val actionRoute: String? = null,
    val createdAt: LocalDate,
    val isRead: Boolean = false,
    val priority: AlertPriority = AlertPriority.NORMAL
)

enum class AlertCategory {
    /** New benefit the user may be eligible for */
    NEW_BENEFIT,
    /** Action required (documents, recertification) */
    ACTION_REQUIRED,
    /** Payment received or scheduled */
    PAYMENT,
    /** Deadline approaching */
    DEADLINE,
    /** General information */
    INFO,
    /** Warning about potential issues */
    WARNING
}

enum class AlertPriority {
    LOW,
    NORMAL,
    HIGH,
    URGENT
}

/**
 * User's benefit wallet summary
 */
data class WalletSummary(
    val totalMonthlyValue: Double,
    val activeBenefitsCount: Int,
    val eligibleBenefitsCount: Int,
    val pendingBenefitsCount: Int,
    val nextPaymentDate: LocalDate? = null,
    val nextPaymentValue: Double? = null
)

/**
 * Extension to format monetary values
 */
fun Double.formatAsCurrency(): String {
    return "R$ %.2f".format(this).replace(".", ",")
}

/**
 * Extension to format dates in Brazilian format
 */
fun LocalDate.formatBrazilian(): String {
    return "%02d/%02d/%d".format(dayOfMonth, monthValue, year)
}

