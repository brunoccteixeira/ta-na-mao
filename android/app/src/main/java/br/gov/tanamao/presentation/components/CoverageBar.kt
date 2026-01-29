package br.gov.tanamao.presentation.components

import androidx.compose.animation.core.animateFloatAsState
import androidx.compose.animation.core.tween
import androidx.compose.foundation.background
import androidx.compose.foundation.layout.*
import androidx.compose.foundation.shape.RoundedCornerShape
import androidx.compose.material3.MaterialTheme
import androidx.compose.material3.Text
import androidx.compose.runtime.*
import androidx.compose.ui.Alignment
import androidx.compose.ui.Modifier
import androidx.compose.ui.draw.clip
import androidx.compose.ui.graphics.Color
import androidx.compose.ui.text.font.FontWeight
import androidx.compose.ui.unit.Dp
import androidx.compose.ui.unit.dp
import br.gov.tanamao.presentation.theme.*

/**
 * Propel-styled coverage bar with animated fill
 *
 * Design:
 * - Dark track background
 * - Color-coded fill based on percentage
 * - Optional label with percentage
 * - Smooth entrance animation
 */
@Composable
fun CoverageBar(
    coverage: Float,
    modifier: Modifier = Modifier,
    showLabel: Boolean = true,
    label: String = "Cobertura",
    height: Dp = TaNaMaoDimens.progressHeight,
    animationDuration: Int = 500,
    trackColor: Color = BackgroundElevated
) {
    val normalizedCoverage = (coverage / 100f).coerceIn(0f, 1f)
    val barColor = TaNaMaoColors.coverageColor(coverage)

    var animationPlayed by remember { mutableStateOf(false) }
    val animatedProgress by animateFloatAsState(
        targetValue = if (animationPlayed) normalizedCoverage else 0f,
        animationSpec = tween(durationMillis = animationDuration),
        label = "coverage_animation"
    )

    LaunchedEffect(Unit) {
        animationPlayed = true
    }

    Column(modifier = modifier) {
        if (showLabel) {
            Row(
                modifier = Modifier.fillMaxWidth(),
                horizontalArrangement = Arrangement.SpaceBetween,
                verticalAlignment = Alignment.CenterVertically
            ) {
                Text(
                    text = label,
                    style = MaterialTheme.typography.labelSmall,
                    color = TextTertiary
                )
                Text(
                    text = String.format("%.1f%%", coverage),
                    style = TaNaMaoTextStyles.percentage,
                    color = barColor
                )
            }
            Spacer(modifier = Modifier.height(TaNaMaoDimens.spacing2))
        }

        // Track
        Box(
            modifier = Modifier
                .fillMaxWidth()
                .height(height)
                .clip(RoundedCornerShape(height / 2))
                .background(trackColor)
        ) {
            // Fill
            Box(
                modifier = Modifier
                    .fillMaxWidth(animatedProgress)
                    .fillMaxHeight()
                    .clip(RoundedCornerShape(height / 2))
                    .background(barColor)
            )
        }
    }
}

/**
 * Compact coverage badge showing percentage with colored background
 */
@Composable
fun CoverageBadge(
    coverage: Float,
    modifier: Modifier = Modifier
) {
    val backgroundColor = TaNaMaoColors.coverageColor(coverage)
    val textColor = if (coverage >= 40) TextOnAccent else TextPrimary

    Box(
        modifier = modifier
            .clip(RoundedCornerShape(TaNaMaoDimens.cardRadiusSmall))
            .background(backgroundColor)
            .padding(horizontal = TaNaMaoDimens.spacing2, vertical = TaNaMaoDimens.spacing1),
        contentAlignment = Alignment.Center
    ) {
        Text(
            text = String.format("%.1f%%", coverage),
            style = TaNaMaoTextStyles.badge,
            fontWeight = FontWeight.Bold,
            color = textColor
        )
    }
}

/**
 * Large circular coverage indicator for dashboards
 */
@Composable
fun CoverageCircle(
    coverage: Float,
    modifier: Modifier = Modifier,
    size: Dp = 80.dp,
    strokeWidth: Dp = 8.dp,
    showLabel: Boolean = true
) {
    val normalizedCoverage = (coverage / 100f).coerceIn(0f, 1f)
    val coverageColor = TaNaMaoColors.coverageColor(coverage)

    var animationPlayed by remember { mutableStateOf(false) }
    val animatedProgress by animateFloatAsState(
        targetValue = if (animationPlayed) normalizedCoverage else 0f,
        animationSpec = tween(durationMillis = 800),
        label = "circle_animation"
    )

    LaunchedEffect(Unit) {
        animationPlayed = true
    }

    Box(
        modifier = modifier.size(size),
        contentAlignment = Alignment.Center
    ) {
        // Background circle
        androidx.compose.foundation.Canvas(
            modifier = Modifier.fillMaxSize()
        ) {
            drawArc(
                color = BackgroundElevated,
                startAngle = -90f,
                sweepAngle = 360f,
                useCenter = false,
                style = androidx.compose.ui.graphics.drawscope.Stroke(
                    width = strokeWidth.toPx()
                )
            )

            // Progress arc
            drawArc(
                color = coverageColor,
                startAngle = -90f,
                sweepAngle = 360f * animatedProgress,
                useCenter = false,
                style = androidx.compose.ui.graphics.drawscope.Stroke(
                    width = strokeWidth.toPx(),
                    cap = androidx.compose.ui.graphics.StrokeCap.Round
                )
            )
        }

        // Center text
        if (showLabel) {
            Text(
                text = String.format("%.0f%%", coverage),
                style = TaNaMaoTextStyles.percentage,
                color = coverageColor
            )
        }
    }
}

/**
 * Coverage summary card with bar and stats
 */
@Composable
fun CoverageSummaryCard(
    title: String,
    coverage: Float,
    modifier: Modifier = Modifier,
    subtitle: String? = null,
    onClick: (() -> Unit)? = null
) {
    PropelCard(
        modifier = modifier.fillMaxWidth(),
        onClick = onClick,
        elevation = PropelCardElevation.Standard
    ) {
        Column(
            modifier = Modifier.fillMaxWidth(),
            verticalArrangement = Arrangement.spacedBy(TaNaMaoDimens.spacing3)
        ) {
            // Header
            Row(
                modifier = Modifier.fillMaxWidth(),
                horizontalArrangement = Arrangement.SpaceBetween,
                verticalAlignment = Alignment.CenterVertically
            ) {
                Column(modifier = Modifier.weight(1f)) {
                    Text(
                        text = title,
                        style = MaterialTheme.typography.titleSmall,
                        color = TextPrimary
                    )
                    subtitle?.let {
                        Text(
                            text = it,
                            style = MaterialTheme.typography.bodySmall,
                            color = TextSecondary
                        )
                    }
                }

                CoverageBadge(coverage = coverage)
            }

            // Bar
            CoverageBar(
                coverage = coverage,
                showLabel = false,
                height = TaNaMaoDimens.progressHeightLarge
            )
        }
    }
}

/**
 * Compact coverage row for lists
 */
@Composable
fun CoverageRow(
    label: String,
    coverage: Float,
    modifier: Modifier = Modifier
) {
    Row(
        modifier = modifier.fillMaxWidth(),
        horizontalArrangement = Arrangement.SpaceBetween,
        verticalAlignment = Alignment.CenterVertically
    ) {
        Text(
            text = label,
            style = MaterialTheme.typography.bodyMedium,
            color = TextSecondary,
            modifier = Modifier.weight(1f)
        )

        Spacer(modifier = Modifier.width(TaNaMaoDimens.spacing3))

        CoverageBar(
            coverage = coverage,
            showLabel = false,
            height = 6.dp,
            modifier = Modifier.weight(1f)
        )

        Spacer(modifier = Modifier.width(TaNaMaoDimens.spacing2))

        Text(
            text = String.format("%.1f%%", coverage),
            style = TaNaMaoTextStyles.percentage,
            color = TaNaMaoColors.coverageColor(coverage)
        )
    }
}
