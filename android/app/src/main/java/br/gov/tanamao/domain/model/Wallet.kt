package br.gov.tanamao.domain.model

import java.time.LocalDate
import java.time.YearMonth

/**
 * Complete wallet data for a user
 */
data class Wallet(
    val summary: WalletSummary,
    val activeBenefits: List<UserBenefit>,
    val eligibleBenefits: List<UserBenefit>,
    val pendingBenefits: List<UserBenefit>,
    val paymentHistory: List<PaymentHistoryItem>
)

/**
 * Payment history item for timeline display
 */
data class PaymentHistoryItem(
    val id: String,
    val programCode: String,
    val programName: String,
    val date: LocalDate,
    val value: Double,
    val reference: YearMonth,
    val status: PaymentStatus,
    val details: String? = null
)

/**
 * Group payments by month for timeline display
 */
data class PaymentHistoryGroup(
    val yearMonth: YearMonth,
    val totalValue: Double,
    val payments: List<PaymentHistoryItem>
)

/**
 * Extension to group payments by month
 */
fun List<PaymentHistoryItem>.groupByMonth(): List<PaymentHistoryGroup> {
    return this
        .groupBy { YearMonth.from(it.date) }
        .map { (yearMonth, payments) ->
            PaymentHistoryGroup(
                yearMonth = yearMonth,
                totalValue = payments.sumOf { it.value },
                payments = payments.sortedByDescending { it.date }
            )
        }
        .sortedByDescending { it.yearMonth }
}

/**
 * Extension to format YearMonth in Brazilian format
 */
fun YearMonth.formatBrazilian(): String {
    val months = listOf(
        "Janeiro", "Fevereiro", "Março", "Abril", "Maio", "Junho",
        "Julho", "Agosto", "Setembro", "Outubro", "Novembro", "Dezembro"
    )
    return "${months[monthValue - 1]} $year"
}

/**
 * Benefit detail for expanded view
 */
data class BenefitDetail(
    val benefit: UserBenefit,
    val description: String,
    val requirements: List<String>,
    val documents: List<String>,
    val howToApply: String,
    val contacts: List<ContactInfo>,
    val faq: List<FaqItem>
)

data class ContactInfo(
    val type: ContactType,
    val value: String,
    val label: String? = null
)

enum class ContactType {
    PHONE, EMAIL, WEBSITE, ADDRESS, WHATSAPP
}

data class FaqItem(
    val question: String,
    val answer: String
)
