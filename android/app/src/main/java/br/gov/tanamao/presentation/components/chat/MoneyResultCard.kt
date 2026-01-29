package br.gov.tanamao.presentation.components.chat

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
import br.gov.tanamao.domain.model.MoneyTypeResult
import br.gov.tanamao.presentation.components.PropelCard
import br.gov.tanamao.presentation.components.PropelCardElevation
import br.gov.tanamao.presentation.theme.TaNaMaoDimens
import br.gov.tanamao.presentation.util.formatCurrency

/**
 * Card to display money found results
 */
@Composable
fun MoneyResultCard(
    totalAmount: Double?,
    types: List<MoneyTypeResult>,
    onGuideClick: (String) -> Unit = {},
    modifier: Modifier = Modifier
) {
    PropelCard(
        elevation = PropelCardElevation.Elevated,
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
                        imageVector = Icons.Outlined.AccountBalance,
                        contentDescription = null,
                        tint = MaterialTheme.colorScheme.primary,
                        modifier = Modifier.size(28.dp)
                    )
                    Text(
                        text = "Dinheiro Encontrado!",
                        style = MaterialTheme.typography.titleLarge,
                        fontWeight = FontWeight.Bold,
                        color = MaterialTheme.colorScheme.primary
                    )
                }
            }

            // Total amount
            totalAmount?.let { amount ->
                Text(
                    text = amount.formatCurrency(),
                    style = MaterialTheme.typography.headlineMedium,
                    fontWeight = FontWeight.Bold,
                    color = MaterialTheme.colorScheme.primary
                )
            }

            // Money types
            if (types.isNotEmpty()) {
                Column(
                    verticalArrangement = Arrangement.spacedBy(TaNaMaoDimens.spacing2)
                ) {
                    Text(
                        text = "Detalhes:",
                        style = MaterialTheme.typography.labelMedium,
                        color = MaterialTheme.colorScheme.onSurfaceVariant
                    )
                    types.forEach { type ->
                        MoneyTypeRow(
                            type = type,
                            onGuideClick = { onGuideClick(type.type) }
                        )
                    }
                }
            }

            // Actions
            Row(
                modifier = Modifier.fillMaxWidth(),
                horizontalArrangement = Arrangement.spacedBy(TaNaMaoDimens.spacing2)
            ) {
                types.firstOrNull()?.let { firstType ->
                    if (firstType.hasMoney) {
                        OutlinedButton(
                            onClick = { onGuideClick(firstType.type) },
                            modifier = Modifier.weight(1f)
                        ) {
                            Icon(
                                imageVector = Icons.Outlined.Info,
                                contentDescription = null,
                                modifier = Modifier.size(18.dp)
                            )
                            Spacer(modifier = Modifier.width(TaNaMaoDimens.spacing1))
                            Text("Ver guia")
                        }
                    }
                }
            }
        }
    }
}

@Composable
private fun MoneyTypeRow(
    type: MoneyTypeResult,
    onGuideClick: () -> Unit
) {
    Surface(
        shape = RoundedCornerShape(TaNaMaoDimens.cardRadiusSmall),
        color = MaterialTheme.colorScheme.surfaceVariant
    ) {
        Row(
            modifier = Modifier
                .fillMaxWidth()
                .padding(TaNaMaoDimens.spacing2),
            horizontalArrangement = Arrangement.SpaceBetween,
            verticalAlignment = Alignment.CenterVertically
        ) {
            Column(modifier = Modifier.weight(1f)) {
                Text(
                    text = type.type.replace("_", "/"),
                    style = MaterialTheme.typography.bodyMedium,
                    fontWeight = FontWeight.Medium,
                    color = MaterialTheme.colorScheme.onSurface
                )
                type.amount?.let { amount ->
                    Text(
                        text = amount.formatCurrency(),
                        style = MaterialTheme.typography.bodySmall,
                        color = MaterialTheme.colorScheme.primary
                    )
                }
                Text(
                    text = type.status,
                    style = MaterialTheme.typography.bodySmall,
                    color = MaterialTheme.colorScheme.onSurfaceVariant
                )
            }
            if (type.hasMoney) {
                IconButton(onClick = onGuideClick) {
                    Icon(
                        imageVector = Icons.Outlined.ArrowForward,
                        contentDescription = "Ver guia",
                        tint = MaterialTheme.colorScheme.primary
                    )
                }
            }
        }
    }
}



