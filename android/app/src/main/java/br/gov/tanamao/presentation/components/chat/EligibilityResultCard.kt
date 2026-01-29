package br.gov.tanamao.presentation.components.chat

import androidx.compose.animation.*
import androidx.compose.foundation.background
import androidx.compose.foundation.layout.*
import androidx.compose.foundation.shape.CircleShape
import androidx.compose.foundation.shape.RoundedCornerShape
import androidx.compose.material.icons.Icons
import androidx.compose.material.icons.filled.*
import androidx.compose.material3.*
import androidx.compose.runtime.*
import androidx.compose.ui.Alignment
import androidx.compose.ui.Modifier
import androidx.compose.ui.draw.clip
import androidx.compose.ui.graphics.Color
import androidx.compose.ui.text.font.FontWeight
import androidx.compose.ui.unit.dp
import br.gov.tanamao.domain.model.EligibilityCriterion
import br.gov.tanamao.domain.model.MessageMetadata
import br.gov.tanamao.presentation.components.*
import br.gov.tanamao.presentation.theme.StatusActive
import br.gov.tanamao.presentation.theme.StatusEligible
import br.gov.tanamao.presentation.theme.StatusNotEligible
import br.gov.tanamao.presentation.theme.TaNaMaoColors
import br.gov.tanamao.presentation.theme.TaNaMaoDimens
import br.gov.tanamao.presentation.theme.TaNaMaoTextStyles

/**
 * Card showing eligibility assessment result
 */
@Composable
fun EligibilityResultCard(
    result: MessageMetadata.EligibilityResult,
    onAction: ((String) -> Unit)?,
    modifier: Modifier = Modifier
) {
    val programColor = TaNaMaoColors.programColor(result.programCode)
    val resultColor = if (result.isEligible) StatusEligible else StatusNotEligible

    Column(
        modifier = modifier
            .fillMaxWidth()
            .padding(
                start = 40.dp,
                top = TaNaMaoDimens.spacing2,
                bottom = TaNaMaoDimens.spacing2
            )
    ) {
        // Card
        Column(
            modifier = Modifier
                .fillMaxWidth()
                .clip(RoundedCornerShape(TaNaMaoDimens.cardRadius))
                .background(MaterialTheme.colorScheme.surfaceVariant)
                .padding(TaNaMaoDimens.cardPadding),
            verticalArrangement = Arrangement.spacedBy(TaNaMaoDimens.spacing4)
        ) {
            // Header with result
            Row(
                modifier = Modifier.fillMaxWidth(),
                horizontalArrangement = Arrangement.SpaceBetween,
                verticalAlignment = Alignment.Top
            ) {
                Row(
                    horizontalArrangement = Arrangement.spacedBy(TaNaMaoDimens.spacing3),
                    verticalAlignment = Alignment.CenterVertically
                ) {
                    Box(
                        modifier = Modifier
                            .size(48.dp)
                            .clip(RoundedCornerShape(12.dp))
                            .background(programColor.copy(alpha = 0.15f)),
                        contentAlignment = Alignment.Center
                    ) {
                        Icon(
                            imageVector = getProgramIcon(result.programCode),
                            contentDescription = null,
                            tint = programColor,
                            modifier = Modifier.size(28.dp)
                        )
                    }

                    Column {
                        Text(
                            text = result.programName,
                            style = MaterialTheme.typography.titleMedium,
                            fontWeight = FontWeight.SemiBold,
                            color = MaterialTheme.colorScheme.onSurface
                        )
                        Row(
                            horizontalArrangement = Arrangement.spacedBy(TaNaMaoDimens.spacing2),
                            verticalAlignment = Alignment.CenterVertically
                        ) {
                            Icon(
                                imageVector = if (result.isEligible) Icons.Filled.CheckCircle else Icons.Filled.Cancel,
                                contentDescription = null,
                                tint = resultColor,
                                modifier = Modifier.size(16.dp)
                            )
                            Text(
                                text = if (result.isEligible) "Elegível" else "Não elegível",
                                style = MaterialTheme.typography.labelMedium,
                                fontWeight = FontWeight.SemiBold,
                                color = resultColor
                            )
                        }
                    }
                }

                // Score circle
                EligibilityScoreCircle(
                    score = result.score,
                    isEligible = result.isEligible
                )
            }

            // Criteria list
            Column(
                modifier = Modifier
                    .fillMaxWidth()
                    .clip(RoundedCornerShape(TaNaMaoDimens.cardRadiusSmall))
                    .background(MaterialTheme.colorScheme.surface)
                    .padding(TaNaMaoDimens.spacing3),
                verticalArrangement = Arrangement.spacedBy(TaNaMaoDimens.spacing2)
            ) {
                Text(
                    text = "Critérios avaliados",
                    style = MaterialTheme.typography.labelSmall,
                    color = MaterialTheme.colorScheme.onSurfaceVariant
                )

                result.criteria.forEach { criterion ->
                    CriterionRow(criterion = criterion)
                }
            }

            // Recommendation
            Row(
                modifier = Modifier
                    .fillMaxWidth()
                    .clip(RoundedCornerShape(TaNaMaoDimens.cardRadiusSmall))
                    .background(resultColor.copy(alpha = 0.1f))
                    .padding(TaNaMaoDimens.spacing3),
                horizontalArrangement = Arrangement.spacedBy(TaNaMaoDimens.spacing2)
            ) {
                Icon(
                    imageVector = Icons.Filled.Lightbulb,
                    contentDescription = null,
                    tint = resultColor,
                    modifier = Modifier.size(20.dp)
                )
                Text(
                    text = result.recommendation,
                    style = MaterialTheme.typography.bodySmall,
                    color = MaterialTheme.colorScheme.onSurface
                )
            }

            // Action buttons
            if (result.isEligible) {
                Row(
                    modifier = Modifier.fillMaxWidth(),
                    horizontalArrangement = Arrangement.spacedBy(TaNaMaoDimens.spacing3)
                ) {
                    PropelButton(
                        text = "Ver documentos",
                        onClick = { onAction?.invoke("documents_${result.programCode}") },
                        style = PropelButtonStyle.Secondary,
                        size = PropelButtonSize.Medium,
                        modifier = Modifier.weight(1f)
                    )
                    PropelButton(
                        text = "Como solicitar",
                        onClick = { onAction?.invoke("apply_${result.programCode}") },
                        style = PropelButtonStyle.Primary,
                        size = PropelButtonSize.Medium,
                        leadingIcon = Icons.Filled.ArrowForward,
                        modifier = Modifier.weight(1f)
                    )
                }
            } else {
                PropelButton(
                    text = "Entender os critérios",
                    onClick = { onAction?.invoke("criteria_${result.programCode}") },
                    style = PropelButtonStyle.Secondary,
                    size = PropelButtonSize.Medium,
                    fullWidth = true
                )
            }
        }
    }
}

@Composable
private fun EligibilityScoreCircle(
    score: Float,
    isEligible: Boolean
) {
    val color = if (isEligible) StatusEligible else StatusNotEligible
    val percentage = (score * 100).toInt()

    Box(
        modifier = Modifier.size(56.dp),
        contentAlignment = Alignment.Center
    ) {
        CircularProgressIndicator(
            progress = { score },
            modifier = Modifier.fillMaxSize(),
            color = color,
            trackColor = color.copy(alpha = 0.2f),
            strokeWidth = 4.dp
        )

        Column(horizontalAlignment = Alignment.CenterHorizontally) {
            Text(
                text = "$percentage%",
                style = TaNaMaoTextStyles.percentage,
                fontWeight = FontWeight.Bold,
                color = color
            )
        }
    }
}

@Composable
private fun CriterionRow(criterion: EligibilityCriterion) {
    Row(
        modifier = Modifier.fillMaxWidth(),
        horizontalArrangement = Arrangement.spacedBy(TaNaMaoDimens.spacing2),
        verticalAlignment = Alignment.CenterVertically
    ) {
        Icon(
            imageVector = if (criterion.isMet) Icons.Filled.CheckCircle else Icons.Filled.Cancel,
            contentDescription = null,
            tint = if (criterion.isMet) StatusActive else StatusNotEligible,
            modifier = Modifier.size(18.dp)
        )

        Column(modifier = Modifier.weight(1f)) {
            Text(
                text = criterion.name,
                style = MaterialTheme.typography.bodyMedium,
                fontWeight = FontWeight.Medium,
                color = MaterialTheme.colorScheme.onSurface
            )
            Text(
                text = criterion.description,
                style = MaterialTheme.typography.bodySmall,
                color = MaterialTheme.colorScheme.onSurfaceVariant
            )
        }
    }
}

/**
 * Compact eligibility indicator for lists
 */
@Composable
fun EligibilityIndicator(
    score: Float,
    isEligible: Boolean,
    modifier: Modifier = Modifier
) {
    val color = if (isEligible) StatusEligible else StatusNotEligible

    Row(
        modifier = modifier
            .clip(RoundedCornerShape(TaNaMaoDimens.chipRadius))
            .background(color.copy(alpha = 0.15f))
            .padding(horizontal = TaNaMaoDimens.spacing2, vertical = TaNaMaoDimens.spacing1),
        horizontalArrangement = Arrangement.spacedBy(TaNaMaoDimens.spacing1),
        verticalAlignment = Alignment.CenterVertically
    ) {
        Icon(
            imageVector = if (isEligible) Icons.Filled.CheckCircle else Icons.Filled.Cancel,
            contentDescription = null,
            tint = color,
            modifier = Modifier.size(14.dp)
        )
        Text(
            text = "${(score * 100).toInt()}%",
            style = TaNaMaoTextStyles.badge,
            fontWeight = FontWeight.SemiBold,
            color = color
        )
    }
}
