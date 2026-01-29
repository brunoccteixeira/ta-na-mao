package br.gov.tanamao.presentation.theme

import androidx.compose.ui.graphics.Color

// =============================================================================
// PROPEL-INSPIRED COLOR PALETTE
// =============================================================================

// Primary Accent - Orange (Call-to-actions, highlights)
val AccentOrange = Color(0xFFF99500)
val AccentOrangeLight = Color(0xFFFFAB33)
val AccentOrangeDark = Color(0xFFCC7A00)
val AccentOrangeSubtle = Color(0x33F99500) // 20% opacity for backgrounds

// Background Colors (Dark Theme - Default)
val BackgroundPrimary = Color(0xFF000000)      // Pure black - main background
val BackgroundSecondary = Color(0xFF0A0A0A)    // Slightly lighter
val BackgroundTertiary = Color(0xFF141414)     // Cards and surfaces
val BackgroundElevated = Color(0xFF1F1F1F)     // Elevated cards, modals
val BackgroundInput = Color(0xFF262626)        // Text fields, search bars

// Background Colors (Light Theme - Alternative)
val BackgroundLightPrimary = Color(0xFFFFFFFF)
val BackgroundLightSecondary = Color(0xFFF5F5F5)
val BackgroundLightTertiary = Color(0xFFEEEEEE)

// Text Colors (Dark Theme)
val TextPrimary = Color(0xFFFFFFFF)            // White - main text
val TextSecondary = Color(0xFFB3B3B3)          // Light gray - secondary text
val TextTertiary = Color(0xFF808080)           // Medium gray - hints
val TextMuted = Color(0xFF4D4D4D)              // Dark gray - disabled
val TextOnAccent = Color(0xFF000000)           // Black - text on orange buttons

// Text Colors (Light Theme)
val TextLightPrimary = Color(0xFF000000)
val TextLightSecondary = Color(0xFF666666)
val TextLightTertiary = Color(0xFF999999)

// Semantic Colors
val Success = Color(0xFF22C55E)         // Green 500
val SuccessLight = Color(0xFF4ADE80)    // Green 400
val SuccessDark = Color(0xFF16A34A)     // Green 600

val Warning = Color(0xFFF59E0B)         // Amber 500
val WarningLight = Color(0xFFFBBF24)    // Amber 400
val WarningDark = Color(0xFFD97706)     // Amber 600

val Error = Color(0xFFEF4444)           // Red 500
val ErrorLight = Color(0xFFF87171)      // Red 400
val ErrorDark = Color(0xFFDC2626)       // Red 600

val Info = Color(0xFF3B82F6)            // Blue 500
val InfoLight = Color(0xFF60A5FA)       // Blue 400
val InfoDark = Color(0xFF2563EB)        // Blue 600

// =============================================================================
// COVERAGE SCALE COLORS (5 levels)
// =============================================================================

val CoverageExcellent = Color(0xFF166534)   // Green 800 - 80%+
val CoverageGood = Color(0xFF22C55E)        // Green 500 - 60-80%
val CoverageRegular = Color(0xFFEAB308)     // Yellow 500 - 40-60%
val CoverageLow = Color(0xFFF97316)         // Orange 500 - 20-40%
val CoverageCritical = Color(0xFFDC2626)    // Red 600 - <20%

// Coverage bar colors (gradient-friendly)
val CoverageHigh = Color(0xFF22C55E)        // 80%+
val CoverageMediumHigh = Color(0xFF84CC16)  // 60-80%
val CoverageMedium = Color(0xFFEAB308)      // 40-60%
val CoverageMediumLow = Color(0xFFF97316)   // 20-40%

// =============================================================================
// PROGRAM BRAND COLORS
// =============================================================================

val ColorBolsaFamilia = Color(0xFF3B82F6)   // Blue
val ColorBPC = Color(0xFF8B5CF6)            // Purple
val ColorFarmacia = Color(0xFF06B6D4)       // Cyan
val ColorTSEE = Color(0xFF22C55E)           // Green
val ColorDignidade = Color(0xFFEC4899)      // Pink
val ColorPISPASEP = Color(0xFFF59E0B)       // Amber
val ColorSVR = Color(0xFF6366F1)            // Indigo

// =============================================================================
// BENEFIT STATUS COLORS
// =============================================================================

val StatusActive = Color(0xFF22C55E)        // Green - receiving benefit
val StatusPending = Color(0xFFF59E0B)       // Amber - processing
val StatusEligible = Color(0xFFF99500)      // Orange - can apply (CTA)
val StatusNotEligible = Color(0xFF4D4D4D)   // Gray - not eligible
val StatusBlocked = Color(0xFFEF4444)       // Red - blocked/suspended

// =============================================================================
// UTILITY COLORS
// =============================================================================

val Divider = Color(0xFF262626)             // Subtle dividers
val DividerLight = Color(0xFFE5E5E5)
val Overlay = Color(0x99000000)             // 60% black overlay
val Shimmer = Color(0xFF2A2A2A)             // Skeleton loading
val ShimmerHighlight = Color(0xFF3A3A3A)

// Border colors
val BorderDefault = Color(0xFF333333)
val BorderFocused = Color(0xFFF99500)       // Orange when focused
val BorderError = Color(0xFFEF4444)
