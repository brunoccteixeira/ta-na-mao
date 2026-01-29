package br.gov.tanamao.presentation.components.chat

import androidx.compose.foundation.background
import androidx.compose.foundation.layout.*
import androidx.compose.foundation.shape.RoundedCornerShape
import androidx.compose.material.icons.Icons
import androidx.compose.material.icons.outlined.*
import androidx.compose.material3.*
import androidx.compose.runtime.Composable
import androidx.compose.ui.Alignment
import androidx.compose.ui.Modifier
import androidx.compose.ui.draw.clip
import androidx.compose.ui.text.font.FontWeight
import androidx.compose.ui.unit.dp
import br.gov.tanamao.domain.model.MessageMetadata
import br.gov.tanamao.domain.model.EligibilityCriterion
import br.gov.tanamao.presentation.components.PropelCard
import br.gov.tanamao.presentation.components.PropelCardElevation
import br.gov.tanamao.presentation.theme.TaNaMaoDimens
import br.gov.tanamao.presentation.util.formatCurrency

/**
 * Card to display eligibility check results
 */
@Composable
fun BenefitResultCard(
    result: MessageMetadata.EligibilityResult,
    onActionClick: (String) -> Unit = {},
    modifier: Modifier = Modifier
) {
    PropelCard(
        elevation = PropelCardElevation.Standard,
        modifier = modifier.fillMaxWidth()
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
                Row(
                    horizontalArrangement = Arrangement.spacedBy(TaNaMaoDimens.spacing2),
                    verticalAlignment = Alignment.CenterVertically
                ) {
                    Icon(
                        imageVector = if (result.isEligible) Icons.Outlined.CheckCircle else Icons.Outlined.Info,
                        contentDescription = null,
                        tint = if (result.isEligible) MaterialTheme.colorScheme.primary else MaterialTheme.colorScheme.onSurfaceVariant,
                        modifier = Modifier.size(24.dp)
                    )
                    Text(
                        text = result.programName,
                        style = MaterialTheme.typography.titleMedium,
                        fontWeight = FontWeight.Bold,
                        color = MaterialTheme.colorScheme.onSurface
                    )
                }
                
                // Score badge
                Surface(
                    shape = RoundedCornerShape(12.dp),
                    color = if (result.isEligible) MaterialTheme.colorScheme.primaryContainer else MaterialTheme.colorScheme.surfaceVariant
                ) {
                    Text(
                        text = "${(result.score * 100).toInt()}%",
                        style = MaterialTheme.typography.labelMedium,
                        fontWeight = FontWeight.Bold,
                        color = if (result.isEligible) MaterialTheme.colorScheme.onPrimaryContainer else MaterialTheme.colorScheme.onSurfaceVariant,
                        modifier = Modifier.padding(horizontal = TaNaMaoDimens.spacing2, vertical = TaNaMaoDimens.spacing1)
                    )
                }
            }

            // Status
            Text(
                text = if (result.isEligible) "✅ Você é elegível!" else "❌ Não elegível no momento",
                style = MaterialTheme.typography.bodyLarge,
                fontWeight = FontWeight.SemiBold,
                color = if (result.isEligible) MaterialTheme.colorScheme.primary else MaterialTheme.colorScheme.error
            )

            // Criteria
            if (result.criteria.isNotEmpty()) {
                Column(
                    verticalArrangement = Arrangement.spacedBy(TaNaMaoDimens.spacing2)
                ) {
                    Text(
                        text = "Critérios:",
                        style = MaterialTheme.typography.labelMedium,
                        color = MaterialTheme.colorScheme.onSurfaceVariant
                    )
                    result.criteria.take(3).forEach { criterion ->
                        Row(
                            horizontalArrangement = Arrangement.spacedBy(TaNaMaoDimens.spacing2),
                            verticalAlignment = Alignment.CenterVertically
                        ) {
                            Icon(
                                imageVector = if (criterion.isMet) Icons.Outlined.Check else Icons.Outlined.Close,
                                contentDescription = null,
                                tint = if (criterion.isMet) MaterialTheme.colorScheme.primary else MaterialTheme.colorScheme.error,
                                modifier = Modifier.size(16.dp)
                            )
                            Text(
                                text = criterion.name,
                                style = MaterialTheme.typography.bodySmall,
                                color = MaterialTheme.colorScheme.onSurface
                            )
                        }
                    }
                }
            }

            // Recommendation
            if (result.recommendation.isNotEmpty()) {
                Surface(
                    shape = RoundedCornerShape(TaNaMaoDimens.cardRadiusSmall),
                    color = MaterialTheme.colorScheme.surfaceVariant
                ) {
                    Text(
                        text = result.recommendation,
                        style = MaterialTheme.typography.bodySmall,
                        color = MaterialTheme.colorScheme.onSurface,
                        modifier = Modifier.padding(TaNaMaoDimens.spacing2)
                    )
                }
            }

            // Actions
            Row(
                modifier = Modifier.fillMaxWidth(),
                horizontalArrangement = Arrangement.spacedBy(TaNaMaoDimens.spacing2)
            ) {
                if (result.isEligible) {
                    TextButton(onClick = { onActionClick("documents_${result.programCode}") }) {
                        Icon(
                            imageVector = Icons.Outlined.Description,
                            contentDescription = null,
                            modifier = Modifier.size(18.dp)
                        )
                        Spacer(modifier = Modifier.width(TaNaMaoDimens.spacing1))
                        Text("Ver documentos")
                    }
                    TextButton(onClick = { onActionClick("apply_${result.programCode}") }) {
                        Icon(
                            imageVector = Icons.Outlined.Send,
                            contentDescription = null,
                            modifier = Modifier.size(18.dp)
                        )
                        Spacer(modifier = Modifier.width(TaNaMaoDimens.spacing1))
                        Text("Como solicitar")
                    }
                }
            }
        }
    }
}



