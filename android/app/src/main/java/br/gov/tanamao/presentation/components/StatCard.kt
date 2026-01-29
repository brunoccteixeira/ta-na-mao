package br.gov.tanamao.presentation.components

import androidx.compose.foundation.background
import androidx.compose.foundation.layout.*
import androidx.compose.foundation.shape.RoundedCornerShape
import androidx.compose.material3.*
import androidx.compose.runtime.Composable
import androidx.compose.ui.Alignment
import androidx.compose.ui.Modifier
import androidx.compose.ui.draw.clip
import androidx.compose.ui.graphics.Color
import androidx.compose.ui.graphics.vector.ImageVector
import androidx.compose.ui.text.font.FontWeight
import androidx.compose.ui.text.style.TextOverflow
import androidx.compose.ui.unit.dp
import br.gov.tanamao.presentation.theme.*

/**
 * Propel-styled stat card for displaying KPIs
 *
 * Design:
 * - Dark background with subtle elevation
 * - Icon with accent color
 * - Large bold value
 * - Smaller label
 */
@Composable
fun StatCard(
    title: String,
    value: String,
    icon: ImageVector,
    modifier: Modifier = Modifier,
    subtitle: String? = null,
    iconTint: Color = AccentOrange,
    valueColor: Color = TextPrimary,
    onClick: (() -> Unit)? = null
) {
    PropelCard(
        modifier = modifier,
        onClick = onClick,
        elevation = PropelCardElevation.Standard
    ) {
        Row(
            modifier = Modifier.fillMaxWidth(),
            horizontalArrangement = Arrangement.spacedBy(TaNaMaoDimens.spacing3),
            verticalAlignment = Alignment.CenterVertically
        ) {
            // Icon container
            Box(
                modifier = Modifier
                    .size(TaNaMaoDimens.statCardIconContainer)
                    .clip(RoundedCornerShape(TaNaMaoDimens.cardRadiusSmall))
                    .background(iconTint.copy(alpha = 0.15f)),
                contentAlignment = Alignment.Center
            ) {
                Icon(
                    imageVector = icon,
                    contentDescription = null,
                    tint = iconTint,
                    modifier = Modifier.size(TaNaMaoDimens.iconSizeMedium)
                )
            }

            // Content
            Column(modifier = Modifier.weight(1f)) {
                Text(
                    text = title,
                    style = MaterialTheme.typography.labelMedium,
                    color = TextTertiary,
                    maxLines = 1,
                    overflow = TextOverflow.Ellipsis
                )

                Spacer(modifier = Modifier.height(TaNaMaoDimens.spacing1))

                Text(
                    text = value,
                    style = TaNaMaoTextStyles.kpiValue,
                    color = valueColor,
                    maxLines = 1,
                    overflow = TextOverflow.Ellipsis
                )

                subtitle?.let {
                    Spacer(modifier = Modifier.height(TaNaMaoDimens.spacing1))
                    Text(
                        text = it,
                        style = MaterialTheme.typography.bodySmall,
                        color = TextSecondary
                    )
                }
            }
        }
    }
}

/**
 * Compact stat card for grid layouts
 * Centered design with value prominence
 */
@Composable
fun CompactStatCard(
    label: String,
    value: String,
    modifier: Modifier = Modifier,
    valueColor: Color = AccentOrange,
    onClick: (() -> Unit)? = null
) {
    PropelCard(
        modifier = modifier,
        onClick = onClick,
        elevation = PropelCardElevation.Standard,
        contentPadding = PaddingValues(TaNaMaoDimens.spacing3)
    ) {
        Column(
            modifier = Modifier.fillMaxWidth(),
            horizontalAlignment = Alignment.CenterHorizontally,
            verticalArrangement = Arrangement.Center
        ) {
            Text(
                text = value,
                style = TaNaMaoTextStyles.kpiValue,
                color = valueColor
            )
            Spacer(modifier = Modifier.height(TaNaMaoDimens.spacing1))
            Text(
                text = label,
                style = TaNaMaoTextStyles.kpiLabel,
                color = TextSecondary,
                maxLines = 1,
                overflow = TextOverflow.Ellipsis
            )
        }
    }
}

/**
 * Stat item for horizontal inline display
 * Label on left, value on right
 */
@Composable
fun StatItem(
    label: String,
    value: String,
    modifier: Modifier = Modifier,
    valueColor: Color = TextPrimary
) {
    Row(
        modifier = modifier.fillMaxWidth(),
        horizontalArrangement = Arrangement.SpaceBetween,
        verticalAlignment = Alignment.CenterVertically
    ) {
        Text(
            text = label,
            style = MaterialTheme.typography.bodyMedium,
            color = TextSecondary
        )
        Text(
            text = value,
            style = MaterialTheme.typography.bodyMedium,
            fontWeight = FontWeight.SemiBold,
            color = valueColor
        )
    }
}

/**
 * Large stat display for hero sections
 */
@Composable
fun StatHero(
    value: String,
    label: String,
    modifier: Modifier = Modifier,
    valueColor: Color = AccentOrange,
    icon: ImageVector? = null
) {
    Column(
        modifier = modifier,
        horizontalAlignment = Alignment.CenterHorizontally
    ) {
        icon?.let {
            Icon(
                imageVector = it,
                contentDescription = null,
                tint = valueColor,
                modifier = Modifier.size(TaNaMaoDimens.iconSizeLarge)
            )
            Spacer(modifier = Modifier.height(TaNaMaoDimens.spacing2))
        }

        Text(
            text = value,
            style = TaNaMaoTextStyles.moneyLarge,
            color = valueColor
        )

        Spacer(modifier = Modifier.height(TaNaMaoDimens.spacing1))

        Text(
            text = label,
            style = MaterialTheme.typography.bodyMedium,
            color = TextSecondary
        )
    }
}

/**
 * Stat row with multiple items (for dashboard summaries)
 */
@Composable
fun StatRow(
    stats: List<Pair<String, String>>,
    modifier: Modifier = Modifier
) {
    Row(
        modifier = modifier.fillMaxWidth(),
        horizontalArrangement = Arrangement.SpaceEvenly
    ) {
        stats.forEach { (value, label) ->
            Column(
                horizontalAlignment = Alignment.CenterHorizontally
            ) {
                Text(
                    text = value,
                    style = MaterialTheme.typography.headlineSmall,
                    fontWeight = FontWeight.Bold,
                    color = TextPrimary
                )
                Text(
                    text = label,
                    style = MaterialTheme.typography.labelSmall,
                    color = TextTertiary
                )
            }
        }
    }
}
