package br.gov.tanamao.presentation.components

import androidx.compose.animation.*
import androidx.compose.foundation.background
import androidx.compose.foundation.layout.*
import androidx.compose.foundation.shape.RoundedCornerShape
import androidx.compose.material.icons.Icons
import androidx.compose.material.icons.filled.*
import androidx.compose.material.icons.outlined.Close
import androidx.compose.material3.*
import androidx.compose.runtime.*
import androidx.compose.ui.Alignment
import androidx.compose.ui.Modifier
import androidx.compose.ui.draw.clip
import androidx.compose.ui.graphics.Color
import androidx.compose.ui.graphics.vector.ImageVector
import androidx.compose.ui.text.font.FontWeight
import androidx.compose.ui.text.style.TextOverflow
import androidx.compose.ui.unit.dp
import br.gov.tanamao.presentation.theme.*
import br.gov.tanamao.presentation.theme.Success as SuccessColor
import br.gov.tanamao.presentation.theme.Warning as WarningColor
import br.gov.tanamao.presentation.theme.Error as ErrorColor

/**
 * Alert types with associated styling
 */
enum class AlertType(
    val backgroundColor: Color,
    val borderColor: Color,
    val iconColor: Color,
    val icon: ImageVector
) {
    /** New benefit available */
    NewBenefit(
        backgroundColor = AccentOrangeSubtle,
        borderColor = AccentOrange,
        iconColor = AccentOrange,
        icon = Icons.Filled.CardGiftcard
    ),

    /** Important information/action required */
    Action(
        backgroundColor = Info.copy(alpha = 0.15f),
        borderColor = Info,
        iconColor = Info,
        icon = Icons.Filled.Info
    ),

    /** Warning about deadline or issue */
    Warning(
        backgroundColor = WarningColor.copy(alpha = 0.15f),
        borderColor = WarningColor,
        iconColor = WarningColor,
        icon = Icons.Filled.Warning
    ),

    /** Success confirmation */
    Success(
        backgroundColor = SuccessColor.copy(alpha = 0.15f),
        borderColor = SuccessColor,
        iconColor = SuccessColor,
        icon = Icons.Filled.CheckCircle
    ),

    /** Error or failure */
    Error(
        backgroundColor = ErrorColor.copy(alpha = 0.15f),
        borderColor = ErrorColor,
        iconColor = ErrorColor,
        icon = Icons.Filled.Error
    )
}

/**
 * Alert banner for important notifications
 *
 * Used at the top of screens to highlight:
 * - New benefits available
 * - Action required
 * - Deadlines approaching
 * - Success/Error messages
 */
@Composable
fun AlertBanner(
    title: String,
    message: String,
    type: AlertType,
    modifier: Modifier = Modifier,
    action: String? = null,
    onAction: (() -> Unit)? = null,
    onDismiss: (() -> Unit)? = null,
    visible: Boolean = true
) {
    AnimatedVisibility(
        visible = visible,
        enter = expandVertically() + fadeIn(),
        exit = shrinkVertically() + fadeOut()
    ) {
        Box(
            modifier = modifier
                .fillMaxWidth()
                .clip(RoundedCornerShape(TaNaMaoDimens.cardRadius))
                .background(type.backgroundColor)
                .padding(1.dp)
        ) {
            Row(
                modifier = Modifier
                    .fillMaxWidth()
                    .clip(RoundedCornerShape(TaNaMaoDimens.cardRadius - 1.dp))
                    .background(type.backgroundColor)
                    .padding(TaNaMaoDimens.cardPadding),
                horizontalArrangement = Arrangement.spacedBy(TaNaMaoDimens.spacing3)
            ) {
                // Icon
                Box(
                    modifier = Modifier
                        .size(40.dp)
                        .clip(RoundedCornerShape(8.dp))
                        .background(type.iconColor.copy(alpha = 0.2f)),
                    contentAlignment = Alignment.Center
                ) {
                    Icon(
                        imageVector = type.icon,
                        contentDescription = null,
                        tint = type.iconColor,
                        modifier = Modifier.size(24.dp)
                    )
                }

                // Content
                Column(
                    modifier = Modifier.weight(1f),
                    verticalArrangement = Arrangement.spacedBy(4.dp)
                ) {
                    Text(
                        text = title,
                        style = MaterialTheme.typography.titleSmall,
                        fontWeight = FontWeight.SemiBold,
                        color = MaterialTheme.colorScheme.onSurface,
                        maxLines = 1,
                        overflow = TextOverflow.Ellipsis
                    )

                    Text(
                        text = message,
                        style = MaterialTheme.typography.bodySmall,
                        color = MaterialTheme.colorScheme.onSurfaceVariant,
                        maxLines = 2,
                        overflow = TextOverflow.Ellipsis
                    )

                    // Action button
                    action?.let {
                        Spacer(modifier = Modifier.height(4.dp))
                        PropelTextButton(
                            text = it,
                            onClick = onAction ?: {},
                            color = type.iconColor
                        )
                    }
                }

                // Dismiss button
                onDismiss?.let {
                    PropelIconButton(
                        icon = Icons.Outlined.Close,
                        onClick = it,
                        style = PropelButtonStyle.Ghost,
                        size = 32.dp,
                        contentDescription = "Fechar"
                    )
                }
            }
        }
    }
}

/**
 * Compact inline alert (for form validation, etc.)
 */
@Composable
fun AlertInline(
    message: String,
    type: AlertType,
    modifier: Modifier = Modifier
) {
    Row(
        modifier = modifier
            .fillMaxWidth()
            .clip(RoundedCornerShape(8.dp))
            .background(type.backgroundColor)
            .padding(TaNaMaoDimens.spacing3),
        horizontalArrangement = Arrangement.spacedBy(TaNaMaoDimens.spacing2),
        verticalAlignment = Alignment.CenterVertically
    ) {
        Icon(
            imageVector = type.icon,
            contentDescription = null,
            tint = type.iconColor,
            modifier = Modifier.size(16.dp)
        )
        Text(
            text = message,
            style = MaterialTheme.typography.bodySmall,
            color = type.iconColor
        )
    }
}

/**
 * Toast-style notification (for bottom of screen)
 */
@Composable
fun AlertToast(
    message: String,
    type: AlertType,
    modifier: Modifier = Modifier,
    action: String? = null,
    onAction: (() -> Unit)? = null,
    onDismiss: (() -> Unit)? = null,
    visible: Boolean = true
) {
    AnimatedVisibility(
        visible = visible,
        enter = slideInVertically(initialOffsetY = { it }) + fadeIn(),
        exit = slideOutVertically(targetOffsetY = { it }) + fadeOut()
    ) {
        Box(
            modifier = modifier
                .fillMaxWidth()
                .padding(TaNaMaoDimens.screenPaddingHorizontal)
        ) {
            Row(
                modifier = Modifier
                    .fillMaxWidth()
                    .clip(RoundedCornerShape(TaNaMaoDimens.cardRadius))
                    .background(MaterialTheme.colorScheme.surfaceVariant)
                    .padding(TaNaMaoDimens.cardPadding),
                horizontalArrangement = Arrangement.spacedBy(TaNaMaoDimens.spacing3),
                verticalAlignment = Alignment.CenterVertically
            ) {
                // Icon
                Icon(
                    imageVector = type.icon,
                    contentDescription = null,
                    tint = type.iconColor,
                    modifier = Modifier.size(24.dp)
                )

                // Message
                Text(
                    text = message,
                    style = MaterialTheme.typography.bodyMedium,
                    color = MaterialTheme.colorScheme.onSurface,
                    modifier = Modifier.weight(1f),
                    maxLines = 2,
                    overflow = TextOverflow.Ellipsis
                )

                // Action or dismiss
                if (action != null && onAction != null) {
                    PropelButton(
                        text = action,
                        onClick = onAction,
                        style = PropelButtonStyle.Ghost,
                        size = PropelButtonSize.Small
                    )
                } else if (onDismiss != null) {
                    PropelIconButton(
                        icon = Icons.Outlined.Close,
                        onClick = onDismiss,
                        size = 32.dp
                    )
                }
            }
        }
    }
}

/**
 * Promotional banner (for home screen highlights)
 */
@Composable
fun PromoBanner(
    title: String,
    subtitle: String,
    modifier: Modifier = Modifier,
    icon: ImageVector = Icons.Filled.Lightbulb,
    actionLabel: String = "Saiba mais",
    onAction: () -> Unit
) {
    PropelCardAccent(
        modifier = modifier.fillMaxWidth(),
        onClick = onAction,
        accentColor = AccentOrange
    ) {
        Row(
            modifier = Modifier.fillMaxWidth(),
            horizontalArrangement = Arrangement.spacedBy(TaNaMaoDimens.spacing4),
            verticalAlignment = Alignment.CenterVertically
        ) {
            // Icon
            Box(
                modifier = Modifier
                    .size(48.dp)
                    .clip(RoundedCornerShape(12.dp))
                    .background(AccentOrangeSubtle),
                contentAlignment = Alignment.Center
            ) {
                Icon(
                    imageVector = icon,
                    contentDescription = null,
                    tint = AccentOrange,
                    modifier = Modifier.size(28.dp)
                )
            }

            // Content
            Column(modifier = Modifier.weight(1f)) {
                Text(
                    text = title,
                    style = MaterialTheme.typography.titleSmall,
                    fontWeight = FontWeight.Bold,
                    color = MaterialTheme.colorScheme.onSurface
                )
                Text(
                    text = subtitle,
                    style = MaterialTheme.typography.bodySmall,
                    color = MaterialTheme.colorScheme.onSurfaceVariant
                )
            }

            // Action indicator
            Icon(
                imageVector = Icons.Filled.ArrowForward,
                contentDescription = null,
                tint = AccentOrange,
                modifier = Modifier.size(20.dp)
            )
        }
    }
}
