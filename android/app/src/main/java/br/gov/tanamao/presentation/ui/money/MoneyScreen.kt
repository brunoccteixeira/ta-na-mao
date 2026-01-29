package br.gov.tanamao.presentation.ui.money

import androidx.compose.animation.*
import androidx.compose.foundation.background
import androidx.compose.foundation.clickable
import androidx.compose.foundation.layout.*
import androidx.compose.foundation.lazy.LazyColumn
import androidx.compose.foundation.lazy.items
import androidx.compose.foundation.shape.RoundedCornerShape
import androidx.compose.material.icons.Icons
import androidx.compose.material.icons.filled.*
import androidx.compose.material.icons.outlined.*
import androidx.compose.material3.*
import androidx.compose.runtime.*
import androidx.compose.ui.Alignment
import androidx.compose.ui.Modifier
import androidx.compose.ui.draw.clip
import androidx.compose.ui.graphics.Color
import androidx.compose.ui.text.font.FontWeight
import androidx.compose.ui.unit.dp
import androidx.hilt.navigation.compose.hiltViewModel
import br.gov.tanamao.domain.model.MoneyType
import br.gov.tanamao.presentation.components.*
import br.gov.tanamao.presentation.theme.TaNaMaoDimens
import br.gov.tanamao.presentation.theme.TaNaMaoTextStyles
import br.gov.tanamao.presentation.util.formatCurrencyCompact
import br.gov.tanamao.presentation.util.formatNumber

@OptIn(ExperimentalMaterial3Api::class)
@Composable
fun MoneyScreen(
    onNavigateBack: () -> Unit,
    onNavigateToChat: (String) -> Unit = {},
    viewModel: MoneyViewModel = hiltViewModel()
) {
    val uiState by viewModel.uiState.collectAsState()

    // Handle navigation to guide
    LaunchedEffect(uiState.navigateToGuide) {
        uiState.navigateToGuide?.let { type ->
            val message = when (type) {
                "PIS_PASEP" -> "guia PIS PASEP"
                "SVR" -> "guia SVR"
                "FGTS" -> "guia FGTS"
                else -> "guia dinheiro esquecido"
            }
            onNavigateToChat(message)
            viewModel.clearNavigation()
        }
    }

    Box(
        modifier = Modifier
            .fillMaxSize()
            .background(MaterialTheme.colorScheme.background)
    ) {
        Column(modifier = Modifier.fillMaxSize()) {
            // Top Bar
            MoneyTopBar(
                onNavigateBack = onNavigateBack,
                onRefresh = viewModel::refresh
            )

            LazyColumn(
                modifier = Modifier.fillMaxSize(),
                contentPadding = PaddingValues(horizontal = TaNaMaoDimens.screenPaddingHorizontal),
                verticalArrangement = Arrangement.spacedBy(TaNaMaoDimens.spacing4)
            ) {
                // Header Card
                item {
                    uiState.overview?.let { overview ->
                        MoneyHeaderCard(
                            totalAvailable = overview.totalAvailable,
                            onCheckClick = { viewModel.checkMyMoney() }
                        )
                    }
                }

                // Check Result
                item {
                    uiState.checkResult?.let { result ->
                        MoneyCheckResultCard(
                            result = result,
                            onDismiss = { viewModel.checkMyMoney(null) }
                        )
                    }
                }

                // Error
                item {
                    uiState.error?.let { error ->
                        ErrorCard(message = error)
                    }
                }

                // Money Type Cards
                item {
                    uiState.overview?.let { overview ->
                        Column(
                            verticalArrangement = Arrangement.spacedBy(TaNaMaoDimens.spacing3)
                        ) {
                            MoneyTypeCard(
                                type = overview.pisPasep,
                                color = MaterialTheme.colorScheme.primary,
                                onGuideClick = { viewModel.navigateToGuide("PIS_PASEP") },
                                onCheckClick = { viewModel.checkMyMoney() }
                            )
                            
                            MoneyTypeCard(
                                type = overview.svr,
                                color = Color(0xFF2196F3), // Blue
                                onGuideClick = { viewModel.navigateToGuide("SVR") },
                                onCheckClick = { viewModel.checkMyMoney() }
                            )
                            
                            MoneyTypeCard(
                                type = overview.fgts,
                                color = Color(0xFF4CAF50), // Green
                                onGuideClick = { viewModel.navigateToGuide("FGTS") },
                                onCheckClick = { viewModel.checkMyMoney() },
                                hasDeadline = true
                            )
                        }
                    }
                }

                // Loading indicator
                if (uiState.isLoading) {
                    item {
                        Box(
                            modifier = Modifier
                                .fillMaxWidth()
                                .padding(TaNaMaoDimens.spacing4),
                            contentAlignment = Alignment.Center
                        ) {
                            CircularProgressIndicator(color = MaterialTheme.colorScheme.primary)
                        }
                    }
                }
            }
        }

        // Checking overlay
        if (uiState.isChecking) {
            Box(
                modifier = Modifier
                    .fillMaxSize()
                    .background(MaterialTheme.colorScheme.background.copy(alpha = 0.8f)),
                contentAlignment = Alignment.Center
            ) {
                Column(
                    horizontalAlignment = Alignment.CenterHorizontally,
                    verticalArrangement = Arrangement.spacedBy(TaNaMaoDimens.spacing3)
                ) {
                    CircularProgressIndicator(color = MaterialTheme.colorScheme.primary)
                    Text(
                        text = "Verificando seu dinheiro...",
                        style = MaterialTheme.typography.bodyMedium,
                        color = MaterialTheme.colorScheme.onBackground
                    )
                }
            }
        }
    }
}

@Composable
private fun MoneyTopBar(
    onNavigateBack: () -> Unit,
    onRefresh: () -> Unit
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
            text = "Dinheiro Esquecido",
            style = MaterialTheme.typography.titleLarge,
            fontWeight = FontWeight.Bold,
            color = MaterialTheme.colorScheme.onBackground
        )

        PropelIconButton(
            icon = Icons.Outlined.Refresh,
            onClick = onRefresh,
            style = PropelButtonStyle.Ghost
        )
    }
}

@Composable
private fun MoneyHeaderCard(
    totalAvailable: Double,
    onCheckClick: () -> Unit
) {
    PropelCardAccent(
        elevation = PropelCardElevation.Elevated,
        modifier = Modifier.fillMaxWidth()
    ) {
        Column(
            modifier = Modifier.fillMaxWidth(),
            verticalArrangement = Arrangement.spacedBy(TaNaMaoDimens.spacing4)
        ) {
            Column {
                Text(
                    text = "Total disponível",
                    style = MaterialTheme.typography.bodyMedium,
                    color = MaterialTheme.colorScheme.onSurfaceVariant
                )
                Text(
                    text = totalAvailable.formatCurrencyCompact(),
                    style = TaNaMaoTextStyles.moneyLarge,
                    color = MaterialTheme.colorScheme.primary
                )
                Text(
                    text = "em dinheiro esquecido pelos brasileiros",
                    style = MaterialTheme.typography.bodySmall,
                    color = MaterialTheme.colorScheme.onSurfaceVariant,
                    modifier = Modifier.padding(top = TaNaMaoDimens.spacing1)
                )
            }

            PropelButton(
                text = "Verificar meu dinheiro",
                leadingIcon = Icons.Outlined.Search,
                onClick = onCheckClick,
                style = PropelButtonStyle.Primary,
                modifier = Modifier.fillMaxWidth()
            )
        }
    }
}

@Composable
private fun MoneyTypeCard(
    type: MoneyType,
    color: Color,
    onGuideClick: () -> Unit,
    onCheckClick: () -> Unit,
    hasDeadline: Boolean = false
) {
    PropelCard(
        elevation = PropelCardElevation.Standard,
        modifier = Modifier.fillMaxWidth()
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
                        text = type.name,
                        style = MaterialTheme.typography.titleMedium,
                        fontWeight = FontWeight.Bold,
                        color = MaterialTheme.colorScheme.onSurface
                    )
                    Text(
                        text = type.description,
                        style = MaterialTheme.typography.bodySmall,
                        color = MaterialTheme.colorScheme.onSurfaceVariant,
                        modifier = Modifier.padding(top = TaNaMaoDimens.spacing1)
                    )
                }
                Box(
                    modifier = Modifier
                        .size(48.dp)
                        .clip(RoundedCornerShape(8.dp))
                        .background(color.copy(alpha = 0.2f)),
                    contentAlignment = Alignment.Center
                ) {
                    Icon(
                        imageVector = Icons.Outlined.AccountBalance,
                        contentDescription = null,
                        tint = color,
                        modifier = Modifier.size(24.dp)
                    )
                }
            }

            // Value
            Text(
                text = type.totalAvailable.formatCurrencyCompact(),
                style = TaNaMaoTextStyles.moneyMedium,
                color = color
            )

            // Eligible people
            if (type.eligiblePeople > 0) {
                Text(
                    text = "${type.eligiblePeople.formatNumber()} pessoas elegíveis",
                    style = MaterialTheme.typography.bodySmall,
                    color = MaterialTheme.colorScheme.onSurfaceVariant
                )
            }

            // Deadline alert
            if (hasDeadline && type.deadline != null) {
                Row(
                    modifier = Modifier
                        .fillMaxWidth()
                        .clip(RoundedCornerShape(TaNaMaoDimens.cardRadiusSmall))
                        .background(MaterialTheme.colorScheme.errorContainer)
                        .padding(TaNaMaoDimens.spacing2),
                    horizontalArrangement = Arrangement.spacedBy(TaNaMaoDimens.spacing2),
                    verticalAlignment = Alignment.CenterVertically
                ) {
                    Icon(
                        imageVector = Icons.Outlined.Warning,
                        contentDescription = null,
                        tint = MaterialTheme.colorScheme.onErrorContainer,
                        modifier = Modifier.size(18.dp)
                    )
                    Text(
                        text = "Prazo: até ${type.deadline}",
                        style = MaterialTheme.typography.labelMedium,
                        color = MaterialTheme.colorScheme.onErrorContainer,
                        fontWeight = FontWeight.Bold
                    )
                }
            }

            // Actions
            Row(
                modifier = Modifier.fillMaxWidth(),
                horizontalArrangement = Arrangement.spacedBy(TaNaMaoDimens.spacing2)
            ) {
                PropelButton(
                    text = "Ver guia",
                    leadingIcon = Icons.Outlined.Info,
                    onClick = onGuideClick,
                    style = PropelButtonStyle.Secondary,
                    modifier = Modifier.weight(1f)
                )
                PropelButton(
                    text = "Verificar",
                    leadingIcon = Icons.Outlined.Search,
                    onClick = onCheckClick,
                    style = PropelButtonStyle.Primary,
                    modifier = Modifier.weight(1f)
                )
            }
        }
    }
}

@Composable
private fun MoneyCheckResultCard(
    result: br.gov.tanamao.domain.model.MoneyCheckResult,
    onDismiss: () -> Unit
) {
    PropelCard(
        elevation = PropelCardElevation.Standard,
        modifier = Modifier.fillMaxWidth()
    ) {
        Column(
            modifier = Modifier.fillMaxWidth(),
            verticalArrangement = Arrangement.spacedBy(TaNaMaoDimens.spacing2)
        ) {
            Row(
                modifier = Modifier.fillMaxWidth(),
                horizontalArrangement = Arrangement.SpaceBetween,
                verticalAlignment = Alignment.CenterVertically
            ) {
                Text(
                    text = if (result.hasMoney) "Dinheiro encontrado!" else "Nenhum dinheiro encontrado",
                    style = MaterialTheme.typography.titleMedium,
                    fontWeight = FontWeight.Bold,
                    color = MaterialTheme.colorScheme.onSurface
                )
                IconButton(onClick = onDismiss) {
                    Icon(
                        imageVector = Icons.Outlined.Close,
                        contentDescription = "Fechar",
                        tint = MaterialTheme.colorScheme.onSurfaceVariant
                    )
                }
            }

            if (result.totalAmount != null) {
                Text(
                    text = result.totalAmount.formatCurrencyCompact(),
                    style = TaNaMaoTextStyles.moneyMedium,
                    color = MaterialTheme.colorScheme.primary
                )
            }

            Text(
                text = result.message,
                style = MaterialTheme.typography.bodyMedium,
                color = MaterialTheme.colorScheme.onSurface
            )
        }
    }
}

@Composable
private fun ErrorCard(message: String) {
    PropelCard(
        elevation = PropelCardElevation.Standard,
        modifier = Modifier.fillMaxWidth()
    ) {
        Row(
            modifier = Modifier.fillMaxWidth(),
            horizontalArrangement = Arrangement.spacedBy(TaNaMaoDimens.spacing2),
            verticalAlignment = Alignment.CenterVertically
        ) {
            Icon(
                imageVector = Icons.Outlined.Error,
                contentDescription = null,
                tint = MaterialTheme.colorScheme.error,
                modifier = Modifier.size(24.dp)
            )
            Text(
                text = message,
                style = MaterialTheme.typography.bodyMedium,
                color = MaterialTheme.colorScheme.error
            )
        }
    }
}



