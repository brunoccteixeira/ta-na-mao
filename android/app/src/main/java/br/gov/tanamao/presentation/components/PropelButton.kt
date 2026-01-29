package br.gov.tanamao.presentation.components

import androidx.compose.animation.animateColorAsState
import androidx.compose.animation.core.tween
import androidx.compose.foundation.background
import androidx.compose.foundation.border
import androidx.compose.foundation.clickable
import androidx.compose.foundation.interaction.MutableInteractionSource
import androidx.compose.foundation.interaction.collectIsPressedAsState
import androidx.compose.foundation.layout.*
import androidx.compose.foundation.shape.RoundedCornerShape
import androidx.compose.material.ripple.rememberRipple
import androidx.compose.material3.*
import androidx.compose.runtime.*
import androidx.compose.ui.Alignment
import androidx.compose.ui.Modifier
import androidx.compose.ui.draw.clip
import androidx.compose.ui.graphics.Color
import androidx.compose.ui.graphics.vector.ImageVector
import androidx.compose.ui.text.style.TextOverflow
import androidx.compose.ui.unit.Dp
import androidx.compose.ui.unit.dp
import br.gov.tanamao.presentation.theme.*
import br.gov.tanamao.presentation.theme.Success as SuccessColor
import br.gov.tanamao.presentation.theme.SuccessDark as SuccessDarkColor
import br.gov.tanamao.presentation.theme.Error as ErrorColor
import br.gov.tanamao.presentation.theme.ErrorDark as ErrorDarkColor

/**
 * Propel-styled button component
 *
 * Variants:
 * - Primary: Orange background, black text (main CTAs)
 * - Secondary: Orange outline, transparent background
 * - Ghost: Just text, no background
 * - Dark: Dark background, white text
 */
@Composable
fun PropelButton(
    text: String,
    onClick: () -> Unit,
    modifier: Modifier = Modifier,
    style: PropelButtonStyle = PropelButtonStyle.Primary,
    size: PropelButtonSize = PropelButtonSize.Large,
    leadingIcon: ImageVector? = null,
    trailingIcon: ImageVector? = null,
    enabled: Boolean = true,
    loading: Boolean = false,
    fullWidth: Boolean = false
) {
    val interactionSource = remember { MutableInteractionSource() }
    val isPressed by interactionSource.collectIsPressedAsState()

    val backgroundColor by animateColorAsState(
        targetValue = when {
            !enabled -> style.disabledBackgroundColor
            isPressed -> style.pressedBackgroundColor
            else -> style.backgroundColor
        },
        animationSpec = tween(100),
        label = "btn_bg"
    )

    val contentColor by animateColorAsState(
        targetValue = when {
            !enabled -> style.disabledContentColor
            else -> style.contentColor
        },
        animationSpec = tween(100),
        label = "btn_content"
    )

    val shape = RoundedCornerShape(size.cornerRadius)

    Box(
        modifier = modifier
            .then(if (fullWidth) Modifier.fillMaxWidth() else Modifier)
            .height(size.height)
            .clip(shape)
            .background(backgroundColor)
            .then(
                if (style.hasBorder && enabled) {
                    Modifier.border(1.5.dp, style.borderColor, shape)
                } else Modifier
            )
            .clickable(
                interactionSource = interactionSource,
                indication = rememberRipple(color = style.rippleColor),
                enabled = enabled && !loading,
                onClick = onClick
            ),
        contentAlignment = Alignment.Center
    ) {
        Row(
            modifier = Modifier.padding(horizontal = size.horizontalPadding),
            horizontalArrangement = Arrangement.spacedBy(TaNaMaoDimens.spacing2),
            verticalAlignment = Alignment.CenterVertically
        ) {
            if (loading) {
                CircularProgressIndicator(
                    modifier = Modifier.size(size.iconSize),
                    color = contentColor,
                    strokeWidth = 2.dp
                )
            } else {
                leadingIcon?.let {
                    Icon(
                        imageVector = it,
                        contentDescription = null,
                        tint = contentColor,
                        modifier = Modifier.size(size.iconSize)
                    )
                }

                Text(
                    text = text,
                    style = size.textStyle,
                    color = contentColor,
                    maxLines = 1,
                    overflow = TextOverflow.Ellipsis
                )

                trailingIcon?.let {
                    Icon(
                        imageVector = it,
                        contentDescription = null,
                        tint = contentColor,
                        modifier = Modifier.size(size.iconSize)
                    )
                }
            }
        }
    }
}

/**
 * Button style variants
 */
enum class PropelButtonStyle(
    val backgroundColor: Color,
    val pressedBackgroundColor: Color,
    val contentColor: Color,
    val disabledBackgroundColor: Color,
    val disabledContentColor: Color,
    val hasBorder: Boolean,
    val borderColor: Color,
    val rippleColor: Color
) {
    /** Primary - Orange background, black text */
    Primary(
        backgroundColor = AccentOrange,
        pressedBackgroundColor = AccentOrangeDark,
        contentColor = TextOnAccent,
        disabledBackgroundColor = BackgroundElevated,
        disabledContentColor = TextMuted,
        hasBorder = false,
        borderColor = Color.Transparent,
        rippleColor = Color.Black.copy(alpha = 0.2f)
    ),

    /** Secondary - Orange outline */
    Secondary(
        backgroundColor = Color.Transparent,
        pressedBackgroundColor = AccentOrangeSubtle,
        contentColor = AccentOrange,
        disabledBackgroundColor = Color.Transparent,
        disabledContentColor = TextMuted,
        hasBorder = true,
        borderColor = AccentOrange,
        rippleColor = AccentOrange.copy(alpha = 0.3f)
    ),

    /** Ghost - Just text */
    Ghost(
        backgroundColor = Color.Transparent,
        pressedBackgroundColor = BackgroundTertiary,
        contentColor = AccentOrange,
        disabledBackgroundColor = Color.Transparent,
        disabledContentColor = TextMuted,
        hasBorder = false,
        borderColor = Color.Transparent,
        rippleColor = AccentOrange.copy(alpha = 0.3f)
    ),

    /** Dark - Dark background, white text */
    Dark(
        backgroundColor = BackgroundElevated,
        pressedBackgroundColor = BackgroundInput,
        contentColor = TextPrimary,
        disabledBackgroundColor = BackgroundTertiary,
        disabledContentColor = TextMuted,
        hasBorder = false,
        borderColor = Color.Transparent,
        rippleColor = Color.White.copy(alpha = 0.1f)
    ),

    /** Success - Green for confirmations */
    Success(
        backgroundColor = SuccessColor,
        pressedBackgroundColor = SuccessDarkColor,
        contentColor = Color.White,
        disabledBackgroundColor = BackgroundElevated,
        disabledContentColor = TextMuted,
        hasBorder = false,
        borderColor = Color.Transparent,
        rippleColor = Color.White.copy(alpha = 0.2f)
    ),

    /** Danger - Red for destructive actions */
    Danger(
        backgroundColor = ErrorColor,
        pressedBackgroundColor = ErrorDarkColor,
        contentColor = Color.White,
        disabledBackgroundColor = BackgroundElevated,
        disabledContentColor = TextMuted,
        hasBorder = false,
        borderColor = Color.Transparent,
        rippleColor = Color.White.copy(alpha = 0.2f)
    )
}

/**
 * Button size variants
 */
enum class PropelButtonSize(
    val height: Dp,
    val horizontalPadding: Dp,
    val iconSize: Dp,
    val cornerRadius: Dp,
    val textStyle: androidx.compose.ui.text.TextStyle
) {
    Large(
        height = TaNaMaoDimens.buttonHeight,
        horizontalPadding = TaNaMaoDimens.buttonPaddingHorizontal,
        iconSize = TaNaMaoDimens.iconSizeMedium,
        cornerRadius = TaNaMaoDimens.buttonRadius,
        textStyle = TaNaMaoTextStyles.button
    ),

    Medium(
        height = TaNaMaoDimens.buttonHeightCompact,
        horizontalPadding = TaNaMaoDimens.buttonPaddingHorizontalCompact,
        iconSize = TaNaMaoDimens.iconSizeSmall,
        cornerRadius = TaNaMaoDimens.buttonRadius,
        textStyle = TaNaMaoTextStyles.buttonSmall
    ),

    Small(
        height = TaNaMaoDimens.buttonHeightSmall,
        horizontalPadding = 12.dp,
        iconSize = TaNaMaoDimens.iconSizeXSmall,
        cornerRadius = TaNaMaoDimens.cardRadiusSmall,
        textStyle = TaNaMaoTextStyles.buttonSmall
    )
}

/**
 * Icon-only button (circular)
 */
@Composable
fun PropelIconButton(
    icon: ImageVector,
    onClick: () -> Unit,
    modifier: Modifier = Modifier,
    style: PropelButtonStyle = PropelButtonStyle.Ghost,
    size: Dp = TaNaMaoDimens.minTouchTarget,
    contentDescription: String? = null,
    enabled: Boolean = true
) {
    val interactionSource = remember { MutableInteractionSource() }
    val isPressed by interactionSource.collectIsPressedAsState()

    val backgroundColor by animateColorAsState(
        targetValue = when {
            !enabled -> style.disabledBackgroundColor
            isPressed -> style.pressedBackgroundColor
            else -> style.backgroundColor
        },
        animationSpec = tween(100),
        label = "icon_btn_bg"
    )

    Box(
        modifier = modifier
            .size(size)
            .clip(RoundedCornerShape(size / 2))
            .background(backgroundColor)
            .clickable(
                interactionSource = interactionSource,
                indication = rememberRipple(bounded = true, color = style.rippleColor),
                enabled = enabled,
                onClick = onClick
            ),
        contentAlignment = Alignment.Center
    ) {
        Icon(
            imageVector = icon,
            contentDescription = contentDescription,
            tint = if (enabled) style.contentColor else style.disabledContentColor,
            modifier = Modifier.size(TaNaMaoDimens.iconSizeMedium)
        )
    }
}

/**
 * Text button (no padding, inline usage)
 */
@Composable
fun PropelTextButton(
    text: String,
    onClick: () -> Unit,
    modifier: Modifier = Modifier,
    color: Color = AccentOrange,
    enabled: Boolean = true
) {
    Text(
        text = text,
        style = TaNaMaoTextStyles.buttonSmall,
        color = if (enabled) color else TextMuted,
        modifier = modifier.clickable(enabled = enabled, onClick = onClick)
    )
}
