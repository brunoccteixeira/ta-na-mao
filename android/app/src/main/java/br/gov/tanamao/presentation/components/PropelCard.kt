package br.gov.tanamao.presentation.components

import androidx.compose.animation.animateColorAsState
import androidx.compose.animation.core.tween
import androidx.compose.foundation.background
import androidx.compose.foundation.border
import androidx.compose.foundation.clickable
import androidx.compose.foundation.interaction.MutableInteractionSource
import androidx.compose.foundation.interaction.collectIsPressedAsState
import androidx.compose.foundation.isSystemInDarkTheme
import androidx.compose.foundation.layout.*
import androidx.compose.foundation.shape.RoundedCornerShape
import androidx.compose.material.ripple.rememberRipple
import androidx.compose.material3.MaterialTheme
import androidx.compose.runtime.*
import androidx.compose.ui.Modifier
import androidx.compose.ui.draw.clip
import androidx.compose.ui.graphics.Color
import androidx.compose.ui.unit.Dp
import androidx.compose.ui.unit.dp
import br.gov.tanamao.presentation.theme.*

/**
 * Propel-styled card component
 *
 * Design principles:
 * - Theme-aware backgrounds (dark/light)
 * - Subtle borders
 * - Smooth press feedback
 * - Consistent corner radius (12dp)
 */
@Composable
fun PropelCard(
    modifier: Modifier = Modifier,
    onClick: (() -> Unit)? = null,
    elevation: PropelCardElevation = PropelCardElevation.Standard,
    borderColor: Color? = null,
    cornerRadius: Dp = TaNaMaoDimens.cardRadius,
    contentPadding: PaddingValues = PaddingValues(TaNaMaoDimens.cardPadding),
    content: @Composable ColumnScope.() -> Unit
) {
    val interactionSource = remember { MutableInteractionSource() }
    val isPressed by interactionSource.collectIsPressedAsState()
    val isDark = isSystemInDarkTheme()

    val backgroundColor by animateColorAsState(
        targetValue = when {
            isPressed -> elevation.getPressedColor(isDark)
            else -> elevation.getBackgroundColor(isDark)
        },
        animationSpec = tween(durationMillis = 100),
        label = "card_bg"
    )

    val shape = RoundedCornerShape(cornerRadius)

    Box(
        modifier = modifier
            .clip(shape)
            .background(backgroundColor)
            .then(
                if (borderColor != null) {
                    Modifier.border(1.dp, borderColor, shape)
                } else Modifier
            )
            .then(
                if (onClick != null) {
                    Modifier.clickable(
                        interactionSource = interactionSource,
                        indication = rememberRipple(color = AccentOrange.copy(alpha = 0.3f)),
                        onClick = onClick
                    )
                } else Modifier
            )
    ) {
        Column(
            modifier = Modifier.padding(contentPadding),
            content = content
        )
    }
}

/**
 * Card elevation variants - now theme-aware
 */
enum class PropelCardElevation {
    /** Flat - same as background, minimal visual distinction */
    Flat,

    /** Standard - default card elevation */
    Standard,

    /** Elevated - modals, highlighted cards */
    Elevated;

    fun getBackgroundColor(isDark: Boolean): Color = when (this) {
        Flat -> if (isDark) BackgroundSecondary else Color(0xFFF8F8F8)
        Standard -> if (isDark) BackgroundTertiary else Color.White
        Elevated -> if (isDark) BackgroundElevated else Color.White
    }

    fun getPressedColor(isDark: Boolean): Color = when (this) {
        Flat -> if (isDark) BackgroundTertiary else Color(0xFFEEEEEE)
        Standard -> if (isDark) BackgroundElevated else Color(0xFFF5F5F5)
        Elevated -> if (isDark) BackgroundInput else Color(0xFFEEEEEE)
    }
}

/**
 * PropelCard with accent border - for highlighted/selected states
 */
@Composable
fun PropelCardAccent(
    modifier: Modifier = Modifier,
    onClick: (() -> Unit)? = null,
    elevation: PropelCardElevation = PropelCardElevation.Standard,
    accentColor: Color = AccentOrange,
    content: @Composable ColumnScope.() -> Unit
) {
    PropelCard(
        modifier = modifier,
        onClick = onClick,
        elevation = elevation,
        borderColor = accentColor.copy(alpha = 0.5f),
        content = content
    )
}

/**
 * PropelCard with status indicator - for benefit/status cards
 */
@Composable
fun PropelCardWithStatus(
    modifier: Modifier = Modifier,
    onClick: (() -> Unit)? = null,
    statusColor: Color,
    statusPosition: StatusPosition = StatusPosition.Left,
    content: @Composable ColumnScope.() -> Unit
) {
    val shape = RoundedCornerShape(TaNaMaoDimens.cardRadius)
    val isDark = isSystemInDarkTheme()
    val bgColor = if (isDark) BackgroundTertiary else Color.White

    Row(
        modifier = modifier
            .clip(shape)
            .background(bgColor)
            .then(
                if (onClick != null) {
                    Modifier.clickable(onClick = onClick)
                } else Modifier
            )
    ) {
        if (statusPosition == StatusPosition.Left) {
            Box(
                modifier = Modifier
                    .width(4.dp)
                    .fillMaxHeight()
                    .background(statusColor)
            )
        }

        Column(
            modifier = Modifier
                .weight(1f)
                .padding(TaNaMaoDimens.cardPadding),
            content = content
        )

        if (statusPosition == StatusPosition.Right) {
            Box(
                modifier = Modifier
                    .width(4.dp)
                    .fillMaxHeight()
                    .background(statusColor)
            )
        }
    }
}

enum class StatusPosition {
    Left, Right
}

/**
 * Section card with header and divider
 */
@Composable
fun PropelSectionCard(
    title: String,
    modifier: Modifier = Modifier,
    subtitle: String? = null,
    action: (@Composable () -> Unit)? = null,
    content: @Composable ColumnScope.() -> Unit
) {
    val isDark = isSystemInDarkTheme()
    val dividerColor = if (isDark) Divider else DividerLight

    PropelCard(
        modifier = modifier,
        contentPadding = PaddingValues(0.dp)
    ) {
        // Header
        Row(
            modifier = Modifier
                .fillMaxWidth()
                .padding(
                    start = TaNaMaoDimens.cardPadding,
                    end = TaNaMaoDimens.cardPadding,
                    top = TaNaMaoDimens.cardPadding,
                    bottom = TaNaMaoDimens.spacing3
                ),
            horizontalArrangement = Arrangement.SpaceBetween,
            verticalAlignment = androidx.compose.ui.Alignment.CenterVertically
        ) {
            Column(modifier = Modifier.weight(1f)) {
                androidx.compose.material3.Text(
                    text = title,
                    style = MaterialTheme.typography.titleMedium,
                    color = MaterialTheme.colorScheme.onSurface
                )
                subtitle?.let {
                    Spacer(modifier = Modifier.height(2.dp))
                    androidx.compose.material3.Text(
                        text = it,
                        style = MaterialTheme.typography.bodySmall,
                        color = MaterialTheme.colorScheme.onSurfaceVariant
                    )
                }
            }
            action?.invoke()
        }

        // Divider
        Box(
            modifier = Modifier
                .fillMaxWidth()
                .height(1.dp)
                .background(dividerColor)
        )

        // Content
        Column(
            modifier = Modifier.padding(TaNaMaoDimens.cardPadding),
            content = content
        )
    }
}
