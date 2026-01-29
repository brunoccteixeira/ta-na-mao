package br.gov.tanamao.presentation.theme

import androidx.compose.ui.unit.Dp
import androidx.compose.ui.unit.dp

/**
 * Tá na Mão Design System - Dimensions
 *
 * Consistent spacing and sizing across the app.
 * Based on 4dp grid system for visual harmony.
 */
object TaNaMaoDimens {

    // ==========================================================================
    // SPACING SCALE (4dp increments)
    // ==========================================================================

    val spacing0: Dp = 0.dp
    val spacing1: Dp = 4.dp      // Minimal spacing
    val spacing2: Dp = 8.dp      // Tight spacing
    val spacing3: Dp = 12.dp     // Compact spacing
    val spacing4: Dp = 16.dp     // Standard spacing
    val spacing5: Dp = 20.dp     // Medium spacing
    val spacing6: Dp = 24.dp     // Section spacing
    val spacing8: Dp = 32.dp     // Large spacing
    val spacing10: Dp = 40.dp    // Extra large
    val spacing12: Dp = 48.dp    // Hero spacing
    val spacing16: Dp = 64.dp    // Maximum spacing

    // ==========================================================================
    // SCREEN PADDING
    // ==========================================================================

    /** Horizontal padding for screen content */
    val screenPaddingHorizontal: Dp = 16.dp

    /** Vertical padding for screen content */
    val screenPaddingVertical: Dp = 16.dp

    /** Padding from bottom navigation */
    val bottomNavPadding: Dp = 80.dp

    /** Safe area for FAB */
    val fabSafeArea: Dp = 88.dp

    // ==========================================================================
    // CARD DIMENSIONS
    // ==========================================================================

    /** Internal padding for cards */
    val cardPadding: Dp = 16.dp

    /** Compact card padding */
    val cardPaddingCompact: Dp = 12.dp

    /** Card corner radius */
    val cardRadius: Dp = 12.dp

    /** Small card radius (chips, badges) */
    val cardRadiusSmall: Dp = 8.dp

    /** Large card radius (hero cards) */
    val cardRadiusLarge: Dp = 16.dp

    /** Card elevation */
    val cardElevation: Dp = 2.dp

    /** Elevated card elevation */
    val cardElevationHigh: Dp = 8.dp

    // ==========================================================================
    // BUTTON DIMENSIONS
    // ==========================================================================

    /** Standard button height */
    val buttonHeight: Dp = 52.dp

    /** Compact button height */
    val buttonHeightCompact: Dp = 44.dp

    /** Small button height (chips) */
    val buttonHeightSmall: Dp = 36.dp

    /** Button corner radius */
    val buttonRadius: Dp = 12.dp

    /** Pill button radius */
    val buttonRadiusPill: Dp = 26.dp

    /** Button horizontal padding */
    val buttonPaddingHorizontal: Dp = 24.dp

    /** Compact button padding */
    val buttonPaddingHorizontalCompact: Dp = 16.dp

    // ==========================================================================
    // ICON SIZES
    // ==========================================================================

    val iconSizeXSmall: Dp = 16.dp
    val iconSizeSmall: Dp = 20.dp
    val iconSizeMedium: Dp = 24.dp
    val iconSizeLarge: Dp = 32.dp
    val iconSizeXLarge: Dp = 48.dp
    val iconSizeHero: Dp = 64.dp

    // ==========================================================================
    // INPUT FIELDS
    // ==========================================================================

    /** Text field height */
    val inputHeight: Dp = 56.dp

    /** Compact input height */
    val inputHeightCompact: Dp = 48.dp

    /** Input corner radius */
    val inputRadius: Dp = 12.dp

    /** Input horizontal padding */
    val inputPaddingHorizontal: Dp = 16.dp

    // ==========================================================================
    // BOTTOM NAVIGATION
    // ==========================================================================

    /** Bottom nav bar height */
    val bottomNavHeight: Dp = 64.dp

    /** Bottom nav icon size */
    val bottomNavIconSize: Dp = 24.dp

    /** Bottom nav indicator height */
    val bottomNavIndicatorHeight: Dp = 3.dp

    // ==========================================================================
    // TOP APP BAR
    // ==========================================================================

    /** Standard app bar height */
    val topBarHeight: Dp = 56.dp

    /** Large app bar height (with title) */
    val topBarHeightLarge: Dp = 112.dp

    // ==========================================================================
    // LISTS AND ITEMS
    // ==========================================================================

    /** List item minimum height */
    val listItemHeight: Dp = 56.dp

    /** Compact list item height */
    val listItemHeightCompact: Dp = 48.dp

    /** List item horizontal padding */
    val listItemPadding: Dp = 16.dp

    /** Space between list items */
    val listItemSpacing: Dp = 8.dp

    // ==========================================================================
    // PROGRESS INDICATORS
    // ==========================================================================

    /** Coverage bar height */
    val progressBarHeight: Dp = 8.dp

    /** Thin progress bar */
    val progressBarHeightThin: Dp = 4.dp

    /** Thick progress bar */
    val progressBarHeightThick: Dp = 12.dp

    /** Progress bar corner radius */
    val progressBarRadius: Dp = 4.dp

    // ==========================================================================
    // AVATARS AND IMAGES
    // ==========================================================================

    val avatarSizeSmall: Dp = 32.dp
    val avatarSizeMedium: Dp = 40.dp
    val avatarSizeLarge: Dp = 56.dp
    val avatarSizeXLarge: Dp = 80.dp

    /** Program icon container size */
    val programIconContainer: Dp = 40.dp

    // ==========================================================================
    // DIVIDERS
    // ==========================================================================

    val dividerThickness: Dp = 1.dp
    val dividerThicknessBold: Dp = 2.dp

    // ==========================================================================
    // BADGES
    // ==========================================================================

    /** Notification badge size */
    val badgeSize: Dp = 20.dp

    /** Small badge size (dot) */
    val badgeSizeSmall: Dp = 8.dp

    /** Badge padding */
    val badgePadding: Dp = 4.dp

    // ==========================================================================
    // TOUCH TARGETS
    // ==========================================================================

    /** Minimum touch target size (accessibility) */
    val minTouchTarget: Dp = 48.dp

    // ==========================================================================
    // ANIMATIONS
    // ==========================================================================

    /** Standard animation duration in ms */
    const val animationDurationShort: Int = 150
    const val animationDurationMedium: Int = 300
    const val animationDurationLong: Int = 500

    // ==========================================================================
    // CHIPS
    // ==========================================================================

    /** Chip corner radius */
    val chipRadius: Dp = 20.dp

    /** Chip height */
    val chipHeight: Dp = 32.dp

    // ==========================================================================
    // SECTION SPACING
    // ==========================================================================

    /** Section spacing */
    val sectionSpacing: Dp = 24.dp

    // ==========================================================================
    // PROGRESS (aliases)
    // ==========================================================================

    /** Progress height (alias for progressBarHeight) */
    val progressHeight: Dp = 8.dp

    /** Large progress height */
    val progressHeightLarge: Dp = 12.dp

    // ==========================================================================
    // SPECIFIC COMPONENTS
    // ==========================================================================

    /** Stat card icon container */
    val statCardIconContainer: Dp = 40.dp

    /** Stat card minimum width */
    val statCardMinWidth: Dp = 140.dp

    /** Benefit card height */
    val benefitCardHeight: Dp = 120.dp

    /** Alert banner height */
    val alertBannerHeight: Dp = 72.dp

    /** Quick action button size */
    val quickActionSize: Dp = 72.dp

    /** Chat message max width (% of screen) */
    const val chatMessageMaxWidthFraction: Float = 0.8f

    /** Chat input minimum height */
    val chatInputMinHeight: Dp = 48.dp
}
