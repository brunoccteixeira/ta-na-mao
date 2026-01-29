package br.gov.tanamao.presentation.ui.profile

import androidx.compose.animation.*
import androidx.compose.foundation.background
import androidx.compose.foundation.clickable
import androidx.compose.foundation.layout.*
import androidx.compose.foundation.lazy.LazyColumn
import androidx.compose.foundation.lazy.items
import androidx.compose.foundation.shape.CircleShape
import androidx.compose.foundation.shape.RoundedCornerShape
import androidx.compose.material.icons.Icons
import androidx.compose.material.icons.filled.*
import androidx.compose.material.icons.outlined.*
import androidx.compose.material3.*
import androidx.compose.runtime.*
import androidx.compose.ui.Alignment
import androidx.compose.ui.Modifier
import androidx.compose.ui.draw.clip
import androidx.compose.ui.graphics.vector.ImageVector
import androidx.compose.ui.text.font.FontWeight
import androidx.compose.ui.unit.dp
import androidx.hilt.navigation.compose.hiltViewModel
import br.gov.tanamao.domain.model.*
import br.gov.tanamao.presentation.components.*
import br.gov.tanamao.presentation.theme.TaNaMaoDimens
import br.gov.tanamao.presentation.theme.TaNaMaoTextStyles
import br.gov.tanamao.presentation.util.formatCurrency
import br.gov.tanamao.presentation.util.formatNumber
import br.gov.tanamao.domain.model.formatBrazilian
import br.gov.tanamao.presentation.navigation.Screen
import br.gov.tanamao.presentation.ui.profile.ForgottenMoneyInfo

@Composable
fun ProfileScreen(
    onNavigateToSettings: () -> Unit = {},
    onNavigateToPrivacy: () -> Unit = {},
    onNavigateToWallet: () -> Unit = {},
    onNavigateToHistory: () -> Unit,
    onNavigateToChat: (String) -> Unit = {},
    onNavigateToMoney: () -> Unit = {},
    viewModel: ProfileViewModel = hiltViewModel()
) {
    val uiState by viewModel.uiState.collectAsState()
    
    // Load forgotten money when screen is first displayed
    LaunchedEffect(Unit) {
        if (uiState.forgottenMoney == null && !uiState.isLoading) {
            viewModel.checkForgottenMoney()
        }
    }

    Box(
        modifier = Modifier
            .fillMaxSize()
            .background(MaterialTheme.colorScheme.background)
    ) {
        LazyColumn(
            modifier = Modifier.fillMaxSize(),
            contentPadding = PaddingValues(bottom = TaNaMaoDimens.spacing4)
        ) {
            // Profile Header
            item {
                ProfileHeader(
                    userName = uiState.userName ?: "Usuário",
                    onSettingsClick = onNavigateToSettings,
                    modifier = Modifier.padding(horizontal = TaNaMaoDimens.screenPaddingHorizontal)
                )
            }

            // Stats Cards
            item {
                uiState.stats?.let { stats ->
                    ProfileStatsSection(
                        stats = stats,
                        modifier = Modifier.padding(horizontal = TaNaMaoDimens.screenPaddingHorizontal)
                    )
                }
            }

            // Forgotten Money Section
            item {
                ForgottenMoneySection(
                    forgottenMoney = uiState.forgottenMoney,
                    isLoading = uiState.isLoading,
                    onCheckMoney = { viewModel.checkForgottenMoney() },
                    onNavigateToMoney = onNavigateToMoney,
                    modifier = Modifier.padding(horizontal = TaNaMaoDimens.screenPaddingHorizontal)
                )
            }

            // Active Benefits Summary
            item {
                if (uiState.benefits.isNotEmpty()) {
                    ActiveBenefitsSummary(
                        benefits = uiState.benefits.filter { it.status == br.gov.tanamao.domain.model.BenefitStatus.ACTIVE },
                        onViewAll = onNavigateToWallet,
                        modifier = Modifier.padding(horizontal = TaNaMaoDimens.screenPaddingHorizontal)
                    )
                }
            }

            // Quick Actions
            item {
                QuickActionsSection(
                    onNavigateToChat = onNavigateToChat,
                    modifier = Modifier.padding(horizontal = TaNaMaoDimens.screenPaddingHorizontal)
                )
            }

            // Recent Consultations
            item {
                if (uiState.consultationHistory.isNotEmpty()) {
                    RecentConsultationsSection(
                        consultations = uiState.consultationHistory.take(5),
                        onViewAll = onNavigateToHistory,
                        modifier = Modifier.padding(horizontal = TaNaMaoDimens.screenPaddingHorizontal)
                    )
                }
            }

            // Settings Section
            item {
                SettingsSection(
                    onPrivacyClick = onNavigateToPrivacy,
                    onSettingsClick = onNavigateToSettings,
                    modifier = Modifier.padding(horizontal = TaNaMaoDimens.screenPaddingHorizontal)
                )
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

        // Error message
        uiState.error?.let { error ->
            Box(
                modifier = Modifier
                    .fillMaxSize()
                    .padding(TaNaMaoDimens.screenPaddingHorizontal),
                contentAlignment = Alignment.BottomCenter
            ) {
                Snackbar(
                    action = {
                        TextButton(onClick = { viewModel.refresh() }) {
                            Text("Tentar novamente")
                        }
                    }
                ) {
                    Text(error)
                }
            }
        }
    }
}

@Composable
private fun ProfileHeader(
    userName: String,
    onSettingsClick: () -> Unit,
    modifier: Modifier = Modifier
) {
    Column(
        modifier = modifier
            .fillMaxWidth()
            .padding(vertical = TaNaMaoDimens.spacing4),
        verticalArrangement = Arrangement.spacedBy(TaNaMaoDimens.spacing3)
    ) {
        Row(
            modifier = Modifier.fillMaxWidth(),
            horizontalArrangement = Arrangement.SpaceBetween,
            verticalAlignment = Alignment.CenterVertically
        ) {
            Row(
                horizontalArrangement = Arrangement.spacedBy(TaNaMaoDimens.spacing3),
                verticalAlignment = Alignment.CenterVertically
            ) {
                // Avatar
                Box(
                    modifier = Modifier
                        .size(64.dp)
                        .clip(CircleShape)
                        .background(MaterialTheme.colorScheme.primaryContainer),
                    contentAlignment = Alignment.Center
                ) {
                    Text(
                        text = userName.take(1).uppercase(),
                        style = MaterialTheme.typography.headlineMedium,
                        fontWeight = FontWeight.Bold,
                        color = MaterialTheme.colorScheme.primary
                    )
                }

                Column {
                    Text(
                        text = "Olá, $userName",
                        style = MaterialTheme.typography.headlineSmall,
                        fontWeight = FontWeight.Bold,
                        color = MaterialTheme.colorScheme.onBackground
                    )
                    Text(
                        text = "Seu perfil e benefícios",
                        style = MaterialTheme.typography.bodyMedium,
                        color = MaterialTheme.colorScheme.onSurfaceVariant
                    )
                }
            }

            IconButton(onClick = onSettingsClick) {
                Icon(
                    imageVector = Icons.Outlined.Settings,
                    contentDescription = "Configurações",
                    tint = MaterialTheme.colorScheme.onSurface
                )
            }
        }
    }
}

@Composable
private fun ProfileStatsSection(
    stats: ProfileStats,
    modifier: Modifier = Modifier
) {
    Column(
        modifier = modifier
            .fillMaxWidth()
            .padding(vertical = TaNaMaoDimens.spacing2),
        verticalArrangement = Arrangement.spacedBy(TaNaMaoDimens.spacing3)
    ) {
        Text(
            text = "Estatísticas",
            style = MaterialTheme.typography.titleMedium,
            fontWeight = FontWeight.SemiBold,
            color = MaterialTheme.colorScheme.onSurface
        )

        Row(
            modifier = Modifier.fillMaxWidth(),
            horizontalArrangement = Arrangement.spacedBy(TaNaMaoDimens.spacing3)
        ) {
            StatCard(
                title = "Total recebido",
                value = stats.totalReceived.formatCurrency(),
                icon = Icons.Outlined.AccountBalance,
                modifier = Modifier.weight(1f)
            )
            StatCard(
                title = "Benefícios ativos",
                value = stats.activeBenefitsCount.toString(),
                icon = Icons.Outlined.CheckCircle,
                modifier = Modifier.weight(1f)
            )
        }

        Row(
            modifier = Modifier.fillMaxWidth(),
            horizontalArrangement = Arrangement.spacedBy(TaNaMaoDimens.spacing3)
        ) {
            StatCard(
                title = "Consultas",
                value = stats.consultationsCount.toString(),
                icon = Icons.Outlined.History,
                modifier = Modifier.weight(1f)
            )
            StatCard(
                title = "Valor mensal",
                value = stats.totalMonthlyValue.formatCurrency(),
                icon = Icons.Outlined.Payments,
                modifier = Modifier.weight(1f)
            )
        }
    }
}

@Composable
private fun StatCard(
    title: String,
    value: String,
    icon: ImageVector,
    modifier: Modifier = Modifier
) {
    PropelCard(
        elevation = PropelCardElevation.Standard,
        modifier = modifier
    ) {
        Column(
            verticalArrangement = Arrangement.spacedBy(TaNaMaoDimens.spacing2)
        ) {
            Icon(
                imageVector = icon,
                contentDescription = null,
                tint = MaterialTheme.colorScheme.primary,
                modifier = Modifier.size(24.dp)
            )
            Text(
                text = value,
                style = TaNaMaoTextStyles.moneyMedium,
                color = MaterialTheme.colorScheme.primary,
                fontWeight = FontWeight.Bold
            )
            Text(
                text = title,
                style = MaterialTheme.typography.bodySmall,
                color = MaterialTheme.colorScheme.onSurfaceVariant
            )
        }
    }
}

@Composable
private fun ActiveBenefitsSummary(
    benefits: List<UserBenefit>,
    onViewAll: () -> Unit,
    modifier: Modifier = Modifier
) {
    Column(
        modifier = modifier
            .fillMaxWidth()
            .padding(vertical = TaNaMaoDimens.spacing2),
        verticalArrangement = Arrangement.spacedBy(TaNaMaoDimens.spacing3)
    ) {
        Row(
            modifier = Modifier.fillMaxWidth(),
            horizontalArrangement = Arrangement.SpaceBetween,
            verticalAlignment = Alignment.CenterVertically
        ) {
            Text(
                text = "Benefícios Ativos",
                style = MaterialTheme.typography.titleMedium,
                fontWeight = FontWeight.SemiBold,
                color = MaterialTheme.colorScheme.onSurface
            )
            TextButton(onClick = onViewAll) {
                Text("Ver todos")
            }
        }

        benefits.take(3).forEach { benefit ->
            BenefitSummaryCard(benefit = benefit)
        }
    }
}

@Composable
private fun BenefitSummaryCard(benefit: UserBenefit) {
    PropelCard(
        elevation = PropelCardElevation.Standard,
        modifier = Modifier.fillMaxWidth()
    ) {
        Row(
            modifier = Modifier.fillMaxWidth(),
            horizontalArrangement = Arrangement.SpaceBetween,
            verticalAlignment = Alignment.CenterVertically
        ) {
            Column(modifier = Modifier.weight(1f)) {
                Text(
                    text = benefit.programName,
                    style = MaterialTheme.typography.bodyLarge,
                    fontWeight = FontWeight.SemiBold,
                    color = MaterialTheme.colorScheme.onSurface
                )
                benefit.monthlyValue?.let { value ->
                    Text(
                        text = value.formatCurrency(),
                        style = MaterialTheme.typography.bodyMedium,
                        color = MaterialTheme.colorScheme.primary
                    )
                }
            }
            Icon(
                imageVector = Icons.Outlined.CheckCircle,
                contentDescription = null,
                tint = MaterialTheme.colorScheme.primary,
                modifier = Modifier.size(24.dp)
            )
        }
    }
}

@Composable
private fun QuickActionsSection(
    onNavigateToChat: (String) -> Unit,
    modifier: Modifier = Modifier
) {
    Column(
        modifier = modifier
            .fillMaxWidth()
            .padding(vertical = TaNaMaoDimens.spacing2),
        verticalArrangement = Arrangement.spacedBy(TaNaMaoDimens.spacing3)
    ) {
        Text(
            text = "Ações Rápidas",
            style = MaterialTheme.typography.titleMedium,
            fontWeight = FontWeight.SemiBold,
            color = MaterialTheme.colorScheme.onSurface
        )

        Row(
            modifier = Modifier.fillMaxWidth(),
            horizontalArrangement = Arrangement.spacedBy(TaNaMaoDimens.spacing3)
        ) {
            QuickActionCard(
                title = "Verificar dinheiro",
                icon = Icons.Outlined.AccountBalance,
                onClick = { onNavigateToChat("verificar meu dinheiro esquecido") },
                modifier = Modifier.weight(1f)
            )
            QuickActionCard(
                title = "Meus benefícios",
                icon = Icons.Outlined.Payments,
                onClick = { onNavigateToChat("meus benefícios") },
                modifier = Modifier.weight(1f)
            )
        }
    }
}

@Composable
private fun QuickActionCard(
    title: String,
    icon: ImageVector,
    onClick: () -> Unit,
    modifier: Modifier = Modifier
) {
    PropelCard(
        elevation = PropelCardElevation.Standard,
        modifier = modifier,
        onClick = onClick
    ) {
        Column(
            horizontalAlignment = Alignment.CenterHorizontally,
            verticalArrangement = Arrangement.spacedBy(TaNaMaoDimens.spacing2)
        ) {
            Icon(
                imageVector = icon,
                contentDescription = null,
                tint = MaterialTheme.colorScheme.primary,
                modifier = Modifier.size(32.dp)
            )
            Text(
                text = title,
                style = MaterialTheme.typography.bodySmall,
                color = MaterialTheme.colorScheme.onSurface,
                textAlign = androidx.compose.ui.text.style.TextAlign.Center
            )
        }
    }
}

@Composable
private fun RecentConsultationsSection(
    consultations: List<ConsultationHistory>,
    onViewAll: () -> Unit,
    modifier: Modifier = Modifier
) {
    Column(
        modifier = modifier
            .fillMaxWidth()
            .padding(vertical = TaNaMaoDimens.spacing2),
        verticalArrangement = Arrangement.spacedBy(TaNaMaoDimens.spacing3)
    ) {
        Row(
            modifier = Modifier.fillMaxWidth(),
            horizontalArrangement = Arrangement.SpaceBetween,
            verticalAlignment = Alignment.CenterVertically
        ) {
            Text(
                text = "Consultas Recentes",
                style = MaterialTheme.typography.titleMedium,
                fontWeight = FontWeight.SemiBold,
                color = MaterialTheme.colorScheme.onSurface
            )
            TextButton(onClick = onViewAll) {
                Text("Ver histórico")
            }
        }

        consultations.forEach { consultation ->
            ConsultationCard(consultation = consultation)
        }
    }
}

@Composable
private fun ConsultationCard(consultation: ConsultationHistory) {
    PropelCard(
        elevation = PropelCardElevation.Standard,
        modifier = Modifier.fillMaxWidth()
    ) {
        Row(
            modifier = Modifier.fillMaxWidth(),
            horizontalArrangement = Arrangement.spacedBy(TaNaMaoDimens.spacing3),
            verticalAlignment = Alignment.CenterVertically
        ) {
            Icon(
                imageVector = getIconForConsultationType(consultation.type),
                contentDescription = null,
                tint = MaterialTheme.colorScheme.primary,
                modifier = Modifier.size(24.dp)
            )
            Column(modifier = Modifier.weight(1f)) {
                Text(
                    text = consultation.query.take(50) + if (consultation.query.length > 50) "..." else "",
                    style = MaterialTheme.typography.bodyMedium,
                    fontWeight = FontWeight.Medium,
                    color = MaterialTheme.colorScheme.onSurface
                )
                Text(
                    text = consultation.date.formatBrazilian(),
                    style = MaterialTheme.typography.bodySmall,
                    color = MaterialTheme.colorScheme.onSurfaceVariant
                )
            }
            if (consultation.success) {
                Icon(
                    imageVector = Icons.Outlined.CheckCircle,
                    contentDescription = "Sucesso",
                    tint = MaterialTheme.colorScheme.primary,
                    modifier = Modifier.size(20.dp)
                )
            }
        }
    }
}

@Composable
private fun SettingsSection(
    onPrivacyClick: () -> Unit,
    onSettingsClick: () -> Unit,
    modifier: Modifier = Modifier
) {
    Column(
        modifier = modifier
            .fillMaxWidth()
            .padding(vertical = TaNaMaoDimens.spacing2),
        verticalArrangement = Arrangement.spacedBy(TaNaMaoDimens.spacing2)
    ) {
        Text(
            text = "Configurações",
            style = MaterialTheme.typography.titleMedium,
            fontWeight = FontWeight.SemiBold,
            color = MaterialTheme.colorScheme.onSurface
        )

        SettingsItem(
            icon = Icons.Outlined.Lock,
            title = "Privacidade e Segurança",
            description = "LGPD e controle de dados",
            onClick = onPrivacyClick
        )

        SettingsItem(
            icon = Icons.Outlined.Settings,
            title = "Configurações",
            description = "Tema e preferências",
            onClick = onSettingsClick
        )
    }
}

@Composable
private fun SettingsItem(
    icon: ImageVector,
    title: String,
    description: String,
    onClick: () -> Unit
) {
    PropelCard(
        elevation = PropelCardElevation.Standard,
        modifier = Modifier.fillMaxWidth(),
        onClick = onClick
    ) {
        Row(
            modifier = Modifier.fillMaxWidth(),
            horizontalArrangement = Arrangement.spacedBy(TaNaMaoDimens.spacing3),
            verticalAlignment = Alignment.CenterVertically
        ) {
            Icon(
                imageVector = icon,
                contentDescription = null,
                tint = MaterialTheme.colorScheme.primary,
                modifier = Modifier.size(24.dp)
            )
            Column(modifier = Modifier.weight(1f)) {
                Text(
                    text = title,
                    style = MaterialTheme.typography.bodyMedium,
                    fontWeight = FontWeight.Medium,
                    color = MaterialTheme.colorScheme.onSurface
                )
                Text(
                    text = description,
                    style = MaterialTheme.typography.bodySmall,
                    color = MaterialTheme.colorScheme.onSurfaceVariant
                )
            }
            Icon(
                imageVector = Icons.Outlined.ChevronRight,
                contentDescription = null,
                tint = MaterialTheme.colorScheme.onSurfaceVariant,
                modifier = Modifier.size(20.dp)
            )
        }
    }
}

private fun getIconForConsultationType(type: ConsultationType): ImageVector {
    return when (type) {
        ConsultationType.ELIGIBILITY_CHECK -> Icons.Outlined.Search
        ConsultationType.MONEY_CHECK -> Icons.Outlined.AccountBalance
        ConsultationType.DOCUMENT_GUIDANCE -> Icons.Outlined.Description
        ConsultationType.LOCATION_SEARCH -> Icons.Outlined.LocationOn
        ConsultationType.PRESCRIPTION_PROCESSING -> Icons.Outlined.Medication
        ConsultationType.GENERAL_QUESTION -> Icons.Outlined.HelpOutline
    }
}

@Composable
private fun ForgottenMoneySection(
    forgottenMoney: ForgottenMoneyInfo?,
    isLoading: Boolean,
    onCheckMoney: () -> Unit,
    onNavigateToMoney: () -> Unit,
    modifier: Modifier = Modifier
) {
    Column(
        modifier = modifier
            .fillMaxWidth()
            .padding(vertical = TaNaMaoDimens.spacing2),
        verticalArrangement = Arrangement.spacedBy(TaNaMaoDimens.spacing3)
    ) {
        Row(
            modifier = Modifier.fillMaxWidth(),
            horizontalArrangement = Arrangement.SpaceBetween,
            verticalAlignment = Alignment.CenterVertically
        ) {
            Text(
                text = "Dinheiro Esquecido",
                style = MaterialTheme.typography.titleMedium,
                fontWeight = FontWeight.SemiBold,
                color = MaterialTheme.colorScheme.onSurface
            )
            
            if (forgottenMoney == null && !isLoading) {
                TextButton(onClick = onCheckMoney) {
                    Text("Verificar")
                }
            }
        }

        when {
            isLoading -> {
                PropelCard(
                    elevation = PropelCardElevation.Standard,
                    modifier = Modifier.fillMaxWidth()
                ) {
                    Row(
                        modifier = Modifier
                            .fillMaxWidth()
                            .padding(TaNaMaoDimens.spacing4),
                        horizontalArrangement = Arrangement.Center,
                        verticalAlignment = Alignment.CenterVertically
                    ) {
                        CircularProgressIndicator(
                            modifier = Modifier.size(24.dp),
                            strokeWidth = 2.dp
                        )
                        Spacer(modifier = Modifier.width(TaNaMaoDimens.spacing3))
                        Text(
                            text = "Verificando dinheiro esquecido...",
                            style = MaterialTheme.typography.bodyMedium,
                            color = MaterialTheme.colorScheme.onSurfaceVariant
                        )
                    }
                }
            }
            
            forgottenMoney?.hasMoney == true -> {
                // Show money found card
                Card(
                    modifier = Modifier
                        .fillMaxWidth()
                        .clickable { onNavigateToMoney() },
                    colors = CardDefaults.cardColors(
                        containerColor = MaterialTheme.colorScheme.primaryContainer
                    ),
                    shape = RoundedCornerShape(TaNaMaoDimens.cardRadius)
                ) {
                    Column(
                        modifier = Modifier
                            .fillMaxWidth()
                            .padding(TaNaMaoDimens.spacing4),
                        verticalArrangement = Arrangement.spacedBy(TaNaMaoDimens.spacing3)
                    ) {
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
                                    imageVector = Icons.Outlined.AccountBalanceWallet,
                                    contentDescription = null,
                                    tint = MaterialTheme.colorScheme.primary,
                                    modifier = Modifier.size(28.dp)
                                )
                                Column {
                                    Text(
                                        text = "Você tem dinheiro esquecido!",
                                        style = MaterialTheme.typography.titleSmall,
                                        fontWeight = FontWeight.Bold,
                                        color = MaterialTheme.colorScheme.onPrimaryContainer
                                    )
                                    Text(
                                        text = "Total disponível",
                                        style = MaterialTheme.typography.bodySmall,
                                        color = MaterialTheme.colorScheme.onPrimaryContainer.copy(alpha = 0.7f)
                                    )
                                }
                            }
                            Text(
                                text = forgottenMoney.total.formatCurrency(),
                                style = TaNaMaoTextStyles.moneyLarge,
                                fontWeight = FontWeight.Bold,
                                color = MaterialTheme.colorScheme.primary
                            )
                        }
                        
                        Divider(color = MaterialTheme.colorScheme.onPrimaryContainer.copy(alpha = 0.2f))
                        
                        // Breakdown by source
                        Column(
                            verticalArrangement = Arrangement.spacedBy(TaNaMaoDimens.spacing2)
                        ) {
                            if (forgottenMoney.pisPasep > 0) {
                                ForgottenMoneyItem(
                                    label = "PIS/PASEP",
                                    value = forgottenMoney.pisPasep
                                )
                            }
                            if (forgottenMoney.svr > 0) {
                                ForgottenMoneyItem(
                                    label = "Valores a Receber (BC)",
                                    value = forgottenMoney.svr
                                )
                            }
                            if (forgottenMoney.fgts > 0) {
                                ForgottenMoneyItem(
                                    label = "FGTS",
                                    value = forgottenMoney.fgts
                                )
                            }
                        }
                        
                        Button(
                            onClick = onNavigateToMoney,
                            modifier = Modifier.fillMaxWidth(),
                            colors = ButtonDefaults.buttonColors(
                                containerColor = MaterialTheme.colorScheme.primary
                            )
                        ) {
                            Text("Ver detalhes e resgatar")
                        }
                    }
                }
            }
            
            forgottenMoney?.hasMoney == false -> {
                // Show no money found card
                PropelCard(
                    elevation = PropelCardElevation.Standard,
                    modifier = Modifier.fillMaxWidth()
                ) {
                    Row(
                        modifier = Modifier
                            .fillMaxWidth()
                            .padding(TaNaMaoDimens.spacing4),
                        horizontalArrangement = Arrangement.spacedBy(TaNaMaoDimens.spacing3),
                        verticalAlignment = Alignment.CenterVertically
                    ) {
                        Icon(
                            imageVector = Icons.Outlined.CheckCircle,
                            contentDescription = null,
                            tint = MaterialTheme.colorScheme.onSurfaceVariant,
                            modifier = Modifier.size(24.dp)
                        )
                        Text(
                            text = "Nenhum dinheiro esquecido encontrado no momento",
                            style = MaterialTheme.typography.bodyMedium,
                            color = MaterialTheme.colorScheme.onSurfaceVariant
                        )
                    }
                }
            }
            
            else -> {
                // Initial state - show prompt to check
                PropelCard(
                    elevation = PropelCardElevation.Standard,
                    modifier = Modifier
                        .fillMaxWidth()
                        .clickable { onNavigateToMoney() }
                ) {
                    Row(
                        modifier = Modifier
                            .fillMaxWidth()
                            .padding(TaNaMaoDimens.spacing4),
                        horizontalArrangement = Arrangement.spacedBy(TaNaMaoDimens.spacing3),
                        verticalAlignment = Alignment.CenterVertically
                    ) {
                        Icon(
                            imageVector = Icons.Outlined.AccountBalanceWallet,
                            contentDescription = null,
                            tint = MaterialTheme.colorScheme.primary,
                            modifier = Modifier.size(28.dp)
                        )
                        Column(modifier = Modifier.weight(1f)) {
                            Text(
                                text = "Verifique seu dinheiro esquecido",
                                style = MaterialTheme.typography.titleSmall,
                                fontWeight = FontWeight.Medium,
                                color = MaterialTheme.colorScheme.onSurface
                            )
                            Text(
                                text = "PIS/PASEP, Valores a Receber e FGTS",
                                style = MaterialTheme.typography.bodySmall,
                                color = MaterialTheme.colorScheme.onSurfaceVariant
                            )
                        }
                        Icon(
                            imageVector = Icons.Outlined.ChevronRight,
                            contentDescription = null,
                            tint = MaterialTheme.colorScheme.onSurfaceVariant
                        )
                    }
                }
            }
        }
    }
}

@Composable
private fun ForgottenMoneyItem(
    label: String,
    value: Double
) {
    Row(
        modifier = Modifier.fillMaxWidth(),
        horizontalArrangement = Arrangement.SpaceBetween,
        verticalAlignment = Alignment.CenterVertically
    ) {
        Text(
            text = label,
            style = MaterialTheme.typography.bodyMedium,
            color = MaterialTheme.colorScheme.onPrimaryContainer
        )
        Text(
            text = value.formatCurrency(),
            style = MaterialTheme.typography.bodyMedium,
            fontWeight = FontWeight.SemiBold,
            color = MaterialTheme.colorScheme.primary
        )
    }
}
