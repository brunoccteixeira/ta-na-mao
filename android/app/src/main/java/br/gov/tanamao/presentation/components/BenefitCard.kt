package br.gov.tanamao.presentation.components

import androidx.compose.foundation.background
import androidx.compose.foundation.layout.*
import androidx.compose.foundation.shape.CircleShape
import androidx.compose.foundation.shape.RoundedCornerShape
import androidx.compose.material.icons.Icons
import androidx.compose.material.icons.filled.*
import androidx.compose.material.icons.outlined.ChevronRight
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
 * Status of a benefit for a user
 */
enum class BenefitStatus(
    val color: Color,
    val label: String,
    val icon: ImageVector
) {
    /** Actively receiving the benefit */
    Active(
        color = StatusActive,
        label = "Ativo",
        icon = Icons.Filled.CheckCircle
    ),

    /** Application submitted, waiting for response */
    Pending(
        color = StatusPending,
        label = "Em análise",
        icon = Icons.Filled.Schedule
    ),

    /** Eligible but not yet applied */
    Eligible(
        color = StatusEligible,
        label = "Pode receber",
        icon = Icons.Filled.Stars
    ),

    /** Not eligible for this benefit */
    NotEligible(
        color = StatusNotEligible,
        label = "Sem direito",
        icon = Icons.Filled.Block
    ),

    /** Benefit was blocked or suspended */
    Blocked(
        color = StatusBlocked,
        label = "Bloqueado",
        icon = Icons.Filled.Warning
    )
}

/**
 * Card displaying a social benefit with status
 *
 * Used in:
 * - Home screen benefit carousel
 * - Wallet screen benefit list
 */
@Composable
fun BenefitCard(
    programName: String,
    programCode: String,
    status: BenefitStatus,
    modifier: Modifier = Modifier,
    value: String? = null,
    nextPaymentDate: String? = null,
    onClick: (() -> Unit)? = null
) {
    val programColor = TaNaMaoColors.programColor(programCode)

    PropelCard(
        modifier = modifier.fillMaxWidth(),
        onClick = onClick,
        elevation = PropelCardElevation.Standard
    ) {
        Row(
            modifier = Modifier.fillMaxWidth(),
            horizontalArrangement = Arrangement.SpaceBetween,
            verticalAlignment = Alignment.CenterVertically
        ) {
            Row(
                horizontalArrangement = Arrangement.spacedBy(TaNaMaoDimens.spacing3),
                verticalAlignment = Alignment.CenterVertically,
                modifier = Modifier.weight(1f)
            ) {
                // Program icon
                Box(
                    modifier = Modifier
                        .size(TaNaMaoDimens.programIconContainer)
                        .clip(RoundedCornerShape(TaNaMaoDimens.cardRadiusSmall))
                        .background(programColor.copy(alpha = 0.15f)),
                    contentAlignment = Alignment.Center
                ) {
                    Icon(
                        imageVector = getProgramIcon(programCode),
                        contentDescription = null,
                        tint = programColor,
                        modifier = Modifier.size(TaNaMaoDimens.iconSizeMedium)
                    )
                }

                // Info
                Column(modifier = Modifier.weight(1f)) {
                    Text(
                        text = programName,
                        style = MaterialTheme.typography.titleSmall,
                        color = MaterialTheme.colorScheme.onSurface,
                        maxLines = 1,
                        overflow = TextOverflow.Ellipsis
                    )

                    Spacer(modifier = Modifier.height(2.dp))

                    Row(
                        horizontalArrangement = Arrangement.spacedBy(TaNaMaoDimens.spacing2),
                        verticalAlignment = Alignment.CenterVertically
                    ) {
                        // Status badge
                        BenefitStatusBadge(status = status)

                        // Value if available
                        value?.let {
                            Text(
                                text = "•",
                                color = MaterialTheme.colorScheme.onSurfaceVariant
                            )
                            Text(
                                text = it,
                                style = MaterialTheme.typography.bodySmall,
                                fontWeight = FontWeight.SemiBold,
                                color = MaterialTheme.colorScheme.onSurfaceVariant
                            )
                        }
                    }

                    // Next payment date
                    nextPaymentDate?.let {
                        Spacer(modifier = Modifier.height(4.dp))
                        Text(
                            text = "Próximo: $it",
                            style = MaterialTheme.typography.bodySmall,
                            color = MaterialTheme.colorScheme.onSurfaceVariant
                        )
                    }
                }
            }

            // Chevron for navigation
            if (onClick != null) {
                Icon(
                    imageVector = Icons.Outlined.ChevronRight,
                    contentDescription = "Ver detalhes",
                    tint = MaterialTheme.colorScheme.onSurfaceVariant,
                    modifier = Modifier.size(TaNaMaoDimens.iconSizeMedium)
                )
            }
        }
    }
}

/**
 * Compact benefit card for horizontal carousel
 */
@Composable
fun BenefitCardCompact(
    programName: String,
    programCode: String,
    status: BenefitStatus,
    modifier: Modifier = Modifier,
    value: String? = null,
    onClick: (() -> Unit)? = null
) {
    val programColor = TaNaMaoColors.programColor(programCode)

    PropelCard(
        modifier = modifier.width(160.dp),
        onClick = onClick,
        elevation = PropelCardElevation.Standard
    ) {
        Column(
            modifier = Modifier.fillMaxWidth(),
            verticalArrangement = Arrangement.spacedBy(TaNaMaoDimens.spacing3)
        ) {
            Row(
                horizontalArrangement = Arrangement.SpaceBetween,
                verticalAlignment = Alignment.CenterVertically,
                modifier = Modifier.fillMaxWidth()
            ) {
                // Program icon
                Box(
                    modifier = Modifier
                        .size(32.dp)
                        .clip(RoundedCornerShape(8.dp))
                        .background(programColor.copy(alpha = 0.15f)),
                    contentAlignment = Alignment.Center
                ) {
                    Icon(
                        imageVector = getProgramIcon(programCode),
                        contentDescription = null,
                        tint = programColor,
                        modifier = Modifier.size(18.dp)
                    )
                }

                // Status dot
                Box(
                    modifier = Modifier
                        .size(8.dp)
                        .clip(CircleShape)
                        .background(status.color)
                )
            }

            Column {
                Text(
                    text = programName,
                    style = MaterialTheme.typography.titleSmall,
                    color = MaterialTheme.colorScheme.onSurface,
                    maxLines = 2,
                    overflow = TextOverflow.Ellipsis
                )

                value?.let {
                    Spacer(modifier = Modifier.height(4.dp))
                    Text(
                        text = it,
                        style = TaNaMaoTextStyles.moneyMedium,
                        color = AccentOrange
                    )
                }
            }
        }
    }
}

/**
 * Status badge component
 */
@Composable
fun BenefitStatusBadge(
    status: BenefitStatus,
    modifier: Modifier = Modifier
) {
    Row(
        modifier = modifier
            .clip(RoundedCornerShape(4.dp))
            .background(status.color.copy(alpha = 0.15f))
            .padding(horizontal = 6.dp, vertical = 2.dp),
        horizontalArrangement = Arrangement.spacedBy(4.dp),
        verticalAlignment = Alignment.CenterVertically
    ) {
        Icon(
            imageVector = status.icon,
            contentDescription = null,
            tint = status.color,
            modifier = Modifier.size(12.dp)
        )
        Text(
            text = status.label,
            style = TaNaMaoTextStyles.badge,
            color = status.color
        )
    }
}

/**
 * Large benefit summary card (for Wallet header)
 */
@Composable
fun BenefitSummaryCard(
    totalMonthlyValue: String,
    activeBenefitsCount: Int,
    eligibleBenefitsCount: Int,
    modifier: Modifier = Modifier,
    onViewAll: (() -> Unit)? = null
) {
    PropelCardAccent(
        modifier = modifier.fillMaxWidth(),
        onClick = onViewAll,
        accentColor = AccentOrange
    ) {
        Column(
            modifier = Modifier.fillMaxWidth(),
            verticalArrangement = Arrangement.spacedBy(TaNaMaoDimens.spacing4)
        ) {
            // Header
            Text(
                text = "Seus Benefícios",
                style = MaterialTheme.typography.titleMedium,
                color = MaterialTheme.colorScheme.onSurfaceVariant
            )

            // Total value
            Column {
                Text(
                    text = "Valor mensal",
                    style = MaterialTheme.typography.bodySmall,
                    color = MaterialTheme.colorScheme.onSurfaceVariant
                )
                Text(
                    text = totalMonthlyValue,
                    style = TaNaMaoTextStyles.moneyLarge,
                    color = AccentOrange
                )
            }

            // Stats row
            Row(
                modifier = Modifier.fillMaxWidth(),
                horizontalArrangement = Arrangement.SpaceEvenly
            ) {
                StatPill(
                    value = activeBenefitsCount.toString(),
                    label = "Ativos",
                    color = StatusActive
                )
                StatPill(
                    value = eligibleBenefitsCount.toString(),
                    label = "Pode receber",
                    color = StatusEligible
                )
            }
        }
    }
}

@Composable
private fun StatPill(
    value: String,
    label: String,
    color: Color
) {
    Row(
        horizontalArrangement = Arrangement.spacedBy(TaNaMaoDimens.spacing2),
        verticalAlignment = Alignment.CenterVertically
    ) {
        Text(
            text = value,
            style = MaterialTheme.typography.headlineSmall,
            fontWeight = FontWeight.Bold,
            color = color
        )
        Text(
            text = label,
            style = MaterialTheme.typography.bodySmall,
            color = MaterialTheme.colorScheme.onSurfaceVariant
        )
    }
}

/**
 * Get icon for a program code
 */
fun getProgramIcon(programCode: String): ImageVector {
    return when (programCode.uppercase()) {
        "BOLSA_FAMILIA", "BF" -> Icons.Filled.FamilyRestroom
        "BPC", "LOAS" -> Icons.Filled.Elderly
        "FARMACIA_POPULAR", "FARM" -> Icons.Filled.LocalPharmacy
        "TSEE" -> Icons.Filled.Bolt
        "DIGNIDADE_MENSTRUAL", "DIG" -> Icons.Filled.Favorite
        "PIS_PASEP", "PIS" -> Icons.Filled.AccountBalance
        "SVR" -> Icons.Filled.Savings
        else -> Icons.Filled.CardGiftcard
    }
}
