package br.gov.tanamao.presentation.util

import java.text.NumberFormat
import java.util.Locale

private val brazilLocale = Locale("pt", "BR")
private val numberFormat = NumberFormat.getNumberInstance(brazilLocale)
private val currencyFormat = NumberFormat.getCurrencyInstance(brazilLocale)
private val percentFormat = NumberFormat.getPercentInstance(brazilLocale).apply {
    minimumFractionDigits = 1
    maximumFractionDigits = 1
}

/**
 * Formats a number with Brazilian locale (e.g., 1.234.567)
 */
fun Long.formatNumber(): String = numberFormat.format(this)

fun Int.formatNumber(): String = numberFormat.format(this)

/**
 * Formats a number in a compact way (e.g., 1.2M, 456K)
 */
fun Long.formatCompact(): String {
    return when {
        this >= 1_000_000_000 -> String.format(brazilLocale, "%.1fB", this / 1_000_000_000.0)
        this >= 1_000_000 -> String.format(brazilLocale, "%.1fM", this / 1_000_000.0)
        this >= 1_000 -> String.format(brazilLocale, "%.1fK", this / 1_000.0)
        else -> this.toString()
    }
}

fun Int.formatCompact(): String = this.toLong().formatCompact()

/**
 * Formats a value as Brazilian currency (e.g., R$ 1.234,56)
 */
fun Double.formatCurrency(): String = currencyFormat.format(this)

fun Long.formatCurrency(): String = currencyFormat.format(this)

/**
 * Formats a value as currency in compact form (e.g., R$ 1.2M)
 */
fun Double.formatCurrencyCompact(): String {
    return when {
        this >= 1_000_000_000 -> String.format(brazilLocale, "R$ %.1fB", this / 1_000_000_000.0)
        this >= 1_000_000 -> String.format(brazilLocale, "R$ %.1fM", this / 1_000_000.0)
        this >= 1_000 -> String.format(brazilLocale, "R$ %.1fK", this / 1_000.0)
        else -> currencyFormat.format(this)
    }
}

/**
 * Formats a decimal as percentage (e.g., 0.85 -> 85,0%)
 */
fun Double.formatPercent(): String = percentFormat.format(this)

fun Float.formatPercent(): String = this.toDouble().formatPercent()

/**
 * Formats a coverage rate (0-100) as percentage string
 */
fun Double.formatCoveragePercent(): String {
    return String.format(brazilLocale, "%.1f%%", this)
}

/**
 * Formats a date string from API format to display format
 * e.g., "2024-01" -> "Jan/2024"
 */
fun String.formatMonthYear(): String {
    return try {
        val parts = this.split("-")
        if (parts.size >= 2) {
            val month = parts[1].toInt()
            val monthName = when (month) {
                1 -> "Jan"
                2 -> "Fev"
                3 -> "Mar"
                4 -> "Abr"
                5 -> "Mai"
                6 -> "Jun"
                7 -> "Jul"
                8 -> "Ago"
                9 -> "Set"
                10 -> "Out"
                11 -> "Nov"
                12 -> "Dez"
                else -> "???"
            }
            "$monthName/${parts[0]}"
        } else {
            this
        }
    } catch (e: Exception) {
        this
    }
}
