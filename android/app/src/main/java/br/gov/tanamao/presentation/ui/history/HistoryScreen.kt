package br.gov.tanamao.presentation.ui.history

import androidx.compose.foundation.background
import androidx.compose.foundation.layout.*
import androidx.compose.foundation.lazy.LazyColumn
import androidx.compose.foundation.lazy.items
import androidx.compose.foundation.shape.RoundedCornerShape
import androidx.compose.material.icons.Icons
import androidx.compose.material.icons.outlined.*
import androidx.compose.material3.*
import androidx.compose.runtime.*
import androidx.compose.ui.Alignment
import androidx.compose.ui.Modifier
import androidx.compose.ui.draw.clip
import androidx.compose.ui.text.font.FontWeight
import androidx.compose.ui.unit.dp
import androidx.hilt.navigation.compose.hiltViewModel
import br.gov.tanamao.domain.model.ConsultationHistory
import br.gov.tanamao.domain.model.ConsultationType
import br.gov.tanamao.presentation.components.*
import br.gov.tanamao.presentation.theme.TaNaMaoDimens
import br.gov.tanamao.domain.model.formatBrazilian

@Composable
fun HistoryScreen(
    onNavigateBack: () -> Unit,
    viewModel: HistoryViewModel = hiltViewModel()
) {
    val uiState by viewModel.uiState.collectAsState()

    Box(
        modifier = Modifier
            .fillMaxSize()
            .background(MaterialTheme.colorScheme.background)
    ) {
        Column(modifier = Modifier.fillMaxSize()) {
            // Top Bar
            HistoryTopBar(
                onNavigateBack = onNavigateBack,
                onFilterChange = viewModel::setFilter
            )

            // Filter Chips
            FilterChips(
                selectedFilter = uiState.selectedFilter,
                onFilterSelected = viewModel::setFilter,
                modifier = Modifier.padding(horizontal = TaNaMaoDimens.screenPaddingHorizontal)
            )

            // History List
            LazyColumn(
                modifier = Modifier.fillMaxSize(),
                contentPadding = PaddingValues(horizontal = TaNaMaoDimens.screenPaddingHorizontal),
                verticalArrangement = Arrangement.spacedBy(TaNaMaoDimens.spacing2)
            ) {
                items(
                    items = uiState.filteredHistory,
                    key = { it.id }
                ) { consultation ->
                    HistoryItemCard(consultation = consultation)
                }

                if (uiState.filteredHistory.isEmpty() && !uiState.isLoading) {
                    item {
                        EmptyHistoryMessage()
                    }
                }
            }
        }

        // Loading overlay
        if (uiState.isLoading) {
            Box(
                modifier = Modifier
                    .fillMaxSize()
                    .background(MaterialTheme.colorScheme.background.copy(alpha = 0.8f)),
                contentAlignment = Alignment.Center
            ) {
                CircularProgressIndicator(color = MaterialTheme.colorScheme.primary)
            }
        }
    }
}

@Composable
private fun HistoryTopBar(
    onNavigateBack: () -> Unit,
    onFilterChange: (HistoryFilter) -> Unit
) {
    Row(
        modifier = Modifier
            .fillMaxWidth()
            .statusBarsPadding()
            .padding(TaNaMaoDimens.screenPaddingHorizontal)
            .padding(vertical = TaNaMaoDimens.spacing3),
        horizontalArrangement = Arrangement.SpaceBetween,
        verticalAlignment = Alignment.CenterVertically
    ) {
        PropelIconButton(
            icon = Icons.Outlined.ArrowBack,
            onClick = onNavigateBack,
            style = PropelButtonStyle.Ghost
        )

        Text(
            text = "Histórico",
            style = MaterialTheme.typography.titleLarge,
            fontWeight = FontWeight.Bold,
            color = MaterialTheme.colorScheme.onBackground
        )

        Spacer(modifier = Modifier.size(48.dp))
    }
}

@Composable
private fun FilterChips(
    selectedFilter: HistoryFilter,
    onFilterSelected: (HistoryFilter) -> Unit,
    modifier: Modifier = Modifier
) {
    Row(
        modifier = modifier
            .fillMaxWidth()
            .padding(vertical = TaNaMaoDimens.spacing2),
        horizontalArrangement = Arrangement.spacedBy(TaNaMaoDimens.spacing2)
    ) {
        HistoryFilter.values().forEach { filter ->
            FilterChip(
                selected = selectedFilter == filter,
                onClick = { onFilterSelected(filter) },
                label = { Text(filter.label) }
            )
        }
    }
}

@Composable
private fun HistoryItemCard(consultation: ConsultationHistory) {
    PropelCard(
        elevation = PropelCardElevation.Standard,
        modifier = Modifier.fillMaxWidth()
    ) {
        Row(
            modifier = Modifier.fillMaxWidth(),
            horizontalArrangement = Arrangement.spacedBy(TaNaMaoDimens.spacing3),
            verticalAlignment = Alignment.CenterVertically
        ) {
            // Icon
            Box(
                modifier = Modifier
                    .size(48.dp)
                    .clip(RoundedCornerShape(8.dp))
                    .background(MaterialTheme.colorScheme.primaryContainer),
                contentAlignment = Alignment.Center
            ) {
                Icon(
                    imageVector = getIconForType(consultation.type),
                    contentDescription = null,
                    tint = MaterialTheme.colorScheme.primary,
                    modifier = Modifier.size(24.dp)
                )
            }

            // Content
            Column(modifier = Modifier.weight(1f)) {
                Text(
                    text = consultation.query.take(60) + if (consultation.query.length > 60) "..." else "",
                    style = MaterialTheme.typography.bodyMedium,
                    fontWeight = FontWeight.Medium,
                    color = MaterialTheme.colorScheme.onSurface
                )
                Text(
                    text = consultation.date.formatBrazilian(),
                    style = MaterialTheme.typography.bodySmall,
                    color = MaterialTheme.colorScheme.onSurfaceVariant
                )
                if (consultation.toolsUsed.isNotEmpty()) {
                    Text(
                        text = "Tools: ${consultation.toolsUsed.joinToString(", ")}",
                        style = MaterialTheme.typography.bodySmall,
                        color = MaterialTheme.colorScheme.onSurfaceVariant
                    )
                }
            }

            // Status
            Icon(
                imageVector = if (consultation.success) Icons.Outlined.CheckCircle else Icons.Outlined.Error,
                contentDescription = null,
                tint = if (consultation.success) MaterialTheme.colorScheme.primary else MaterialTheme.colorScheme.error,
                modifier = Modifier.size(24.dp)
            )
        }
    }
}

@Composable
private fun EmptyHistoryMessage() {
    Box(
        modifier = Modifier
            .fillMaxWidth()
            .padding(TaNaMaoDimens.spacing4),
        contentAlignment = Alignment.Center
    ) {
        Column(
            horizontalAlignment = Alignment.CenterHorizontally,
            verticalArrangement = Arrangement.spacedBy(TaNaMaoDimens.spacing2)
        ) {
            Icon(
                imageVector = Icons.Outlined.History,
                contentDescription = null,
                tint = MaterialTheme.colorScheme.onSurfaceVariant,
                modifier = Modifier.size(64.dp)
            )
            Text(
                text = "Nenhuma consulta ainda",
                style = MaterialTheme.typography.titleMedium,
                color = MaterialTheme.colorScheme.onSurfaceVariant
            )
            Text(
                text = "Suas consultas com o assistente aparecerão aqui",
                style = MaterialTheme.typography.bodySmall,
                color = MaterialTheme.colorScheme.onSurfaceVariant
            )
        }
    }
}

private fun getIconForType(type: ConsultationType): androidx.compose.ui.graphics.vector.ImageVector {
    return when (type) {
        ConsultationType.ELIGIBILITY_CHECK -> Icons.Outlined.Search
        ConsultationType.MONEY_CHECK -> Icons.Outlined.AccountBalance
        ConsultationType.DOCUMENT_GUIDANCE -> Icons.Outlined.Description
        ConsultationType.LOCATION_SEARCH -> Icons.Outlined.LocationOn
        ConsultationType.PRESCRIPTION_PROCESSING -> Icons.Outlined.Medication
        ConsultationType.GENERAL_QUESTION -> Icons.Outlined.HelpOutline
    }
}



