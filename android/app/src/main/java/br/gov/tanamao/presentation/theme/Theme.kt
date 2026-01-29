package br.gov.tanamao.presentation.theme

import android.app.Activity
import android.os.Build
import androidx.compose.foundation.isSystemInDarkTheme
import androidx.compose.material3.MaterialTheme
import androidx.compose.material3.darkColorScheme
import androidx.compose.material3.lightColorScheme
import androidx.compose.runtime.Composable
import androidx.compose.runtime.SideEffect
import androidx.compose.ui.graphics.Color
import androidx.compose.ui.graphics.toArgb
import androidx.compose.ui.platform.LocalView
import androidx.core.view.WindowCompat

/**
 * Propel-inspired Dark Color Scheme
 * Primary: Orange accent on dark backgrounds
 * Design: Minimal, high contrast, accessibility-focused
 */
private val PropelDarkColorScheme = darkColorScheme(
    // Primary - Orange accent for CTAs and highlights
    primary = AccentOrange,
    onPrimary = TextOnAccent,
    primaryContainer = AccentOrangeDark,
    onPrimaryContainer = Color.White,

    // Secondary - Lighter orange for secondary actions
    secondary = AccentOrangeLight,
    onSecondary = TextOnAccent,
    secondaryContainer = AccentOrangeSubtle,
    onSecondaryContainer = AccentOrange,

    // Tertiary - Success green for positive feedback
    tertiary = Success,
    onTertiary = Color.White,
    tertiaryContainer = SuccessDark,
    onTertiaryContainer = Color.White,

    // Background - Pure black for OLED optimization
    background = BackgroundPrimary,
    onBackground = TextPrimary,

    // Surfaces - Graduated dark grays
    surface = BackgroundTertiary,
    onSurface = TextPrimary,
    surfaceVariant = BackgroundElevated,
    onSurfaceVariant = TextSecondary,

    // Inverse (for snackbars, etc.)
    inverseSurface = Color.White,
    inverseOnSurface = BackgroundPrimary,
    inversePrimary = AccentOrangeDark,

    // Error states
    error = Error,
    onError = Color.White,
    errorContainer = ErrorDark,
    onErrorContainer = Color.White,

    // Outlines
    outline = BorderDefault,
    outlineVariant = Divider,

    // Scrim for modals
    scrim = Overlay
)

/**
 * Light Color Scheme (alternative mode)
 */
private val PropelLightColorScheme = lightColorScheme(
    primary = AccentOrangeDark,
    onPrimary = Color.White,
    primaryContainer = AccentOrangeLight,
    onPrimaryContainer = TextOnAccent,

    secondary = AccentOrange,
    onSecondary = Color.White,
    secondaryContainer = AccentOrangeSubtle,
    onSecondaryContainer = AccentOrangeDark,

    tertiary = SuccessDark,
    onTertiary = Color.White,

    background = BackgroundLightPrimary,
    onBackground = TextLightPrimary,

    surface = BackgroundLightSecondary,
    onSurface = TextLightPrimary,
    surfaceVariant = BackgroundLightTertiary,
    onSurfaceVariant = TextLightSecondary,

    error = Error,
    onError = Color.White,

    outline = DividerLight,
    outlineVariant = DividerLight
)

/**
 * Tá na Mão Theme - Propel-inspired design
 *
 * @param darkTheme Use dark theme (default: follows system setting)
 * @param dynamicColor Use Material You dynamic colors (default: false to maintain brand)
 * @param content Composable content
 */
@Composable
fun TaNaMaoTheme(
    darkTheme: Boolean = isSystemInDarkTheme(), // Follow system preference
    dynamicColor: Boolean = false, // Keep brand colors
    content: @Composable () -> Unit
) {
    val colorScheme = when {
        // Dynamic color only on Android 12+ and if explicitly enabled
        dynamicColor && Build.VERSION.SDK_INT >= Build.VERSION_CODES.S -> {
            // Not recommended for brand consistency
            if (darkTheme) PropelDarkColorScheme else PropelLightColorScheme
        }
        darkTheme -> PropelDarkColorScheme
        else -> PropelLightColorScheme
    }

    val view = LocalView.current
    if (!view.isInEditMode) {
        SideEffect {
            val window = (view.context as Activity).window

            // Set status bar to match background
            window.statusBarColor = colorScheme.background.toArgb()

            // Navigation bar color (Android 8+)
            window.navigationBarColor = colorScheme.background.toArgb()

            // Status bar icons: light icons on dark theme
            val insetsController = WindowCompat.getInsetsController(window, view)
            insetsController.isAppearanceLightStatusBars = !darkTheme
            insetsController.isAppearanceLightNavigationBars = !darkTheme
        }
    }

    MaterialTheme(
        colorScheme = colorScheme,
        typography = TaNaMaoTypography,
        content = content
    )
}

/**
 * Extended color accessors for non-Material colors
 * Use these for custom components that need Propel-specific colors
 */
object TaNaMaoColors {
    // Accents
    val accent = AccentOrange
    val accentLight = AccentOrangeLight
    val accentDark = AccentOrangeDark

    // Semantic
    val success = Success
    val warning = Warning
    val error = Error
    val info = Info

    // Status
    val statusActive = StatusActive
    val statusPending = StatusPending
    val statusEligible = StatusEligible
    val statusNotEligible = StatusNotEligible
    val statusBlocked = StatusBlocked

    // Coverage
    fun coverageColor(percentage: Float): Color = when {
        percentage >= 0.8f -> CoverageExcellent
        percentage >= 0.6f -> CoverageGood
        percentage >= 0.4f -> CoverageRegular
        percentage >= 0.2f -> CoverageLow
        else -> CoverageCritical
    }

    // Program colors
    fun programColor(code: String): Color = when (code.uppercase()) {
        "BOLSA_FAMILIA", "BF" -> ColorBolsaFamilia
        "BPC", "LOAS" -> ColorBPC
        "FARMACIA_POPULAR", "FARM" -> ColorFarmacia
        "TSEE" -> ColorTSEE
        "DIGNIDADE_MENSTRUAL", "DIG" -> ColorDignidade
        "PIS_PASEP", "PIS" -> ColorPISPASEP
        "SVR" -> ColorSVR
        else -> AccentOrange
    }
}

/**
 * Theme-aware color provider
 * Returns appropriate colors based on current theme
 */
data class TaNaMaoColorScheme(
    val isDark: Boolean,
    val backgroundPrimary: Color,
    val backgroundSecondary: Color,
    val backgroundTertiary: Color,
    val backgroundElevated: Color,
    val backgroundInput: Color,
    val textPrimary: Color,
    val textSecondary: Color,
    val textTertiary: Color,
    val textMuted: Color,
    val divider: Color
)

val DarkColorScheme = TaNaMaoColorScheme(
    isDark = true,
    backgroundPrimary = BackgroundPrimary,
    backgroundSecondary = BackgroundSecondary,
    backgroundTertiary = BackgroundTertiary,
    backgroundElevated = BackgroundElevated,
    backgroundInput = BackgroundInput,
    textPrimary = TextPrimary,
    textSecondary = TextSecondary,
    textTertiary = TextTertiary,
    textMuted = TextMuted,
    divider = Divider
)

val LightColorScheme = TaNaMaoColorScheme(
    isDark = false,
    backgroundPrimary = BackgroundLightPrimary,
    backgroundSecondary = BackgroundLightSecondary,
    backgroundTertiary = BackgroundLightTertiary,
    backgroundElevated = Color.White,
    backgroundInput = Color(0xFFF0F0F0),
    textPrimary = TextLightPrimary,
    textSecondary = TextLightSecondary,
    textTertiary = TextLightTertiary,
    textMuted = Color(0xFFAAAAAA),
    divider = DividerLight
)

/**
 * Get theme-aware colors in composables
 */
@Composable
fun taNaMaoColors(): TaNaMaoColorScheme {
    return if (isSystemInDarkTheme()) DarkColorScheme else LightColorScheme
}
