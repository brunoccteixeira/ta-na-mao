package br.gov.tanamao.presentation.ui.wallet

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
import br.gov.tanamao.domain.model.*
import br.gov.tanamao.domain.model.BenefitStatus as DomainBenefitStatus
import br.gov.tanamao.presentation.components.*
import br.gov.tanamao.presentation.components.BenefitStatus as UiBenefitStatus
import br.gov.tanamao.presentation.theme.StatusActive
import br.gov.tanamao.presentation.theme.StatusEligible
import br.gov.tanamao.presentation.theme.StatusPending
import br.gov.tanamao.presentation.theme.TaNaMaoColors
import br.gov.tanamao.presentation.theme.TaNaMaoDimens
import br.gov.tanamao.presentation.theme.TaNaMaoTextStyles
import br.gov.tanamao.presentation.theme.Error as ErrorColor
import br.gov.tanamao.presentation.theme.Warning as WarningColor
import java.time.YearMonth

@OptIn(ExperimentalMaterial3Api::class)
@Composable
fun WalletScreen(
    onNavigateBack: () -> Unit,
    onNavigateToBenefit: (String) -> Unit = {},
    onNavigateToChat: () -> Unit = {},
    viewModel: WalletViewModel = hiltViewModel()
) {
    val uiState by viewModel.uiState.collectAsState()

    Box(
        modifier = Modifier
            .fillMaxSize()
            .background(MaterialTheme.colorScheme.background)
    ) {
        Column(modifier = Modifier.fillMaxSize()) {
            // Top Bar
            WalletTopBar(onNavigateBack = onNavigateBack)

            // Wallet Summary
            uiState.walletSummary?.let { summary ->
                WalletSummaryHeader(
                    summary = summary,
                    modifier = Modifier.padding(horizontal = TaNaMaoDimens.screenPaddingHorizontal)
                )
            }

            Spacer(modifier = Modifier.height(TaNaMaoDimens.spacing4))

            // Tab Bar
            WalletTabBar(
                selectedTab = uiState.selectedTab,
                activeBenefitsCount = uiState.activeBenefits.size + uiState.pendingBenefits.size,
                eligibleBenefitsCount = uiState.eligibleBenefits.size,
                onTabSelected = viewModel::selectTab,
                modifier = Modifier.padding(horizontal = TaNaMaoDimens.screenPaddingHorizontal)
            )

            Spacer(modifier = Modifier.height(TaNaMaoDimens.spacing4))

            // Content
            AnimatedContent(
                targetState = uiState.selectedTab,
                transitionSpec = {
                    fadeIn() + slideInHorizontally { width ->
                        if (targetState.ordinal > initialState.ordinal) width else -width
                    } togetherWith fadeOut() + slideOutHorizontally { width ->
                        if (targetState.ordinal > initialState.ordinal) -width else width
                    }
                },
                label = "tab_content"
            ) { tab ->
                when (tab) {
                    WalletTab.ACTIVE -> ActiveBenefitsList(
                        benefits = uiState.activeBenefits + uiState.pendingBenefits,
                        isLoading = uiState.isLoading,
                        onBenefitClick = onNavigateToBenefit
                    )
                    WalletTab.ELIGIBLE -> EligibleBenefitsList(
                        benefits = uiState.eligibleBenefits,
                        isLoading = uiState.isLoading,
                        onBenefitClick = onNavigateToBenefit,
                        onApplyClick = { onNavigateToChat() }
                    )
                    WalletTab.HISTORY -> PaymentHistoryList(
                        historyGroups = uiState.paymentHistory,
                        isLoading = uiState.isLoading
                    )
                }
            }
        }

        // Loading overlay
        if (uiState.isLoading && uiState.walletSummary == null) {
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
private fun WalletTopBar(onNavigateBack: () -> Unit) {
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
            text = "Minha Carteira",
            style = MaterialTheme.typography.titleLarge,
            fontWeight = FontWeight.Bold,
            color = MaterialTheme.colorScheme.onBackground
        )

        // Placeholder for symmetry
        Spacer(modifier = Modifier.size(48.dp))
    }
}

@Composable
private fun WalletSummaryHeader(
    summary: WalletSummary,
    modifier: Modifier = Modifier
) {
    PropelCardAccent(
        modifier = modifier.fillMaxWidth(),
        elevation = PropelCardElevation.Elevated
    ) {
        Column(
            modifier = Modifier.fillMaxWidth(),
            verticalArrangement = Arrangement.spacedBy(TaNaMaoDimens.spacing4)
        ) {
            // Total value
            Column {
                Text(
                    text = "Valor mensal total",
                    style = MaterialTheme.typography.bodyMedium,
                    color = MaterialTheme.colorScheme.onSurfaceVariant
                )
                Text(
                    text = summary.totalMonthlyValue.formatAsCurrency(),
                    style = TaNaMaoTextStyles.moneyLarge,
                    color = MaterialTheme.colorScheme.primary
                )
            }

            // Next payment info
            summary.nextPaymentDate?.let { date ->
                Row(
                    modifier = Modifier
                        .fillMaxWidth()
                        .clip(RoundedCornerShape(TaNaMaoDimens.cardRadiusSmall))
                        .background(MaterialTheme.colorScheme.surface)
                        .padding(TaNaMaoDimens.spacing3),
                    horizontalArrangement = Arrangement.SpaceBetween,
                    verticalAlignment = Alignment.CenterVertically
                ) {
                    Row(
                        horizontalArrangement = Arrangement.spacedBy(TaNaMaoDimens.spacing2),
                        verticalAlignment = Alignment.CenterVertically
                    ) {
                        Icon(
                            imageVector = Icons.Outlined.CalendarToday,
                            contentDescription = null,
                            tint = MaterialTheme.colorScheme.primary,
                            modifier = Modifier.size(20.dp)
                        )
                        Column {
                            Text(
                                text = "Próximo pagamento",
                                style = MaterialTheme.typography.labelSmall,
                                color = MaterialTheme.colorScheme.onSurfaceVariant
                            )
                            Text(
                                text = date.formatBrazilian(),
                                style = MaterialTheme.typography.bodyMedium,
                                fontWeight = FontWeight.SemiBold,
                                color = MaterialTheme.colorScheme.onSurface
                            )
                        }
                    }

                    summary.nextPaymentValue?.let { value ->
                        Text(
                            text = value.formatAsCurrency(),
                            style = TaNaMaoTextStyles.moneyMedium,
                            color = MaterialTheme.colorScheme.primary
                        )
                    }
                }
            }

            // Stats row
            Row(
                modifier = Modifier.fillMaxWidth(),
                horizontalArrangement = Arrangement.SpaceEvenly
            ) {
                WalletStatPill(
                    value = summary.activeBenefitsCount.toString(),
                    label = "Ativos",
                    color = StatusActive
                )
                WalletStatPill(
                    value = summary.eligibleBenefitsCount.toString(),
                    label = "Posso receber?",
                    color = StatusEligible
                )
                WalletStatPill(
                    value = summary.pendingBenefitsCount.toString(),
                    label = "Pendentes",
                    color = StatusPending
                )
            }
        }
    }
}

@Composable
private fun WalletStatPill(
    value: String,
    label: String,
    color: Color
) {
    Column(horizontalAlignment = Alignment.CenterHorizontally) {
        Text(
            text = value,
            style = MaterialTheme.typography.headlineSmall,
            fontWeight = FontWeight.Bold,
            color = color
        )
        Text(
            text = label,
            style = MaterialTheme.typography.labelSmall,
            color = MaterialTheme.colorScheme.onSurfaceVariant
        )
    }
}

@Composable
private fun WalletTabBar(
    selectedTab: WalletTab,
    activeBenefitsCount: Int,
    eligibleBenefitsCount: Int,
    onTabSelected: (WalletTab) -> Unit,
    modifier: Modifier = Modifier
) {
    Row(
        modifier = modifier
            .fillMaxWidth()
            .clip(RoundedCornerShape(TaNaMaoDimens.cardRadius))
            .background(MaterialTheme.colorScheme.surfaceVariant)
            .padding(4.dp),
        horizontalArrangement = Arrangement.spacedBy(4.dp)
    ) {
        WalletTabItem(
            label = "Ativos",
            count = activeBenefitsCount,
            selected = selectedTab == WalletTab.ACTIVE,
            onClick = { onTabSelected(WalletTab.ACTIVE) },
            modifier = Modifier.weight(1f)
        )
        WalletTabItem(
            label = "Posso receber?",
            count = eligibleBenefitsCount,
            selected = selectedTab == WalletTab.ELIGIBLE,
            onClick = { onTabSelected(WalletTab.ELIGIBLE) },
            modifier = Modifier.weight(1f)
        )
        WalletTabItem(
            label = "Histórico",
            count = null,
            selected = selectedTab == WalletTab.HISTORY,
            onClick = { onTabSelected(WalletTab.HISTORY) },
            modifier = Modifier.weight(1f)
        )
    }
}

@Composable
private fun WalletTabItem(
    label: String,
    count: Int?,
    selected: Boolean,
    onClick: () -> Unit,
    modifier: Modifier = Modifier
) {
    val backgroundColor = if (selected) MaterialTheme.colorScheme.primary else Color.Transparent
    val textColor = if (selected) MaterialTheme.colorScheme.onPrimary else MaterialTheme.colorScheme.onSurfaceVariant

    Box(
        modifier = modifier
            .clip(RoundedCornerShape(TaNaMaoDimens.cardRadiusSmall))
            .background(backgroundColor)
            .padding(vertical = TaNaMaoDimens.spacing3)
            .clickable(onClick = onClick),
        contentAlignment = Alignment.Center
    ) {
        Row(
            horizontalArrangement = Arrangement.spacedBy(TaNaMaoDimens.spacing1),
            verticalAlignment = Alignment.CenterVertically
        ) {
            Text(
                text = label,
                style = MaterialTheme.typography.labelMedium,
                fontWeight = if (selected) FontWeight.SemiBold else FontWeight.Normal,
                color = textColor
            )
            count?.let {
                if (it > 0) {
                    Box(
                        modifier = Modifier
                            .size(18.dp)
                            .clip(RoundedCornerShape(9.dp))
                            .background(if (selected) MaterialTheme.colorScheme.onPrimary.copy(alpha = 0.2f) else MaterialTheme.colorScheme.surface),
                        contentAlignment = Alignment.Center
                    ) {
                        Text(
                            text = it.toString(),
                            style = TaNaMaoTextStyles.badge,
                            color = textColor
                        )
                    }
                }
            }
        }
    }
}

@Composable
private fun ActiveBenefitsList(
    benefits: List<UserBenefit>,
    isLoading: Boolean,
    onBenefitClick: (String) -> Unit
) {
    if (benefits.isEmpty() && !isLoading) {
        EmptyStateView(
            icon = Icons.Outlined.AccountBalanceWallet,
            title = "Nenhum benefício ativo",
            message = "Você não recebe benefícios no momento. Veja se tem direito na aba 'Posso receber?'"
        )
    } else {
        LazyColumn(
            modifier = Modifier.fillMaxSize(),
            contentPadding = PaddingValues(
                horizontal = TaNaMaoDimens.screenPaddingHorizontal,
                vertical = TaNaMaoDimens.spacing2
            ),
            verticalArrangement = Arrangement.spacedBy(TaNaMaoDimens.spacing3)
        ) {
            items(benefits) { benefit ->
                BenefitCard(
                    programName = benefit.programName,
                    programCode = benefit.programCode,
                    status = benefit.status.toBenefitStatus(),
                    value = benefit.monthlyValue?.formatAsCurrency(),
                    nextPaymentDate = benefit.nextPaymentDate?.formatBrazilian(),
                    onClick = { onBenefitClick(benefit.id) }
                )
            }

            item {
                Spacer(modifier = Modifier.height(TaNaMaoDimens.bottomNavHeight + 16.dp))
            }
        }
    }
}

@Composable
private fun EligibleBenefitsList(
    benefits: List<UserBenefit>,
    isLoading: Boolean,
    onBenefitClick: (String) -> Unit,
    onApplyClick: (String) -> Unit
) {
    if (benefits.isEmpty() && !isLoading) {
        EmptyStateView(
            icon = Icons.Outlined.Search,
            title = "Sem benefícios disponíveis",
            message = "Não encontramos novos benefícios para você no momento. Continue atualizando seus dados no CadÚnico."
        )
    } else {
        LazyColumn(
            modifier = Modifier.fillMaxSize(),
            contentPadding = PaddingValues(
                horizontal = TaNaMaoDimens.screenPaddingHorizontal,
                vertical = TaNaMaoDimens.spacing2
            ),
            verticalArrangement = Arrangement.spacedBy(TaNaMaoDimens.spacing3)
        ) {
            items(benefits) { benefit ->
                EligibleBenefitCard(
                    benefit = benefit,
                    onViewDetails = { onBenefitClick(benefit.id) },
                    onApply = { onApplyClick(benefit.programCode) }
                )
            }

            item {
                Spacer(modifier = Modifier.height(TaNaMaoDimens.bottomNavHeight + 16.dp))
            }
        }
    }
}

@Composable
private fun EligibleBenefitCard(
    benefit: UserBenefit,
    onViewDetails: () -> Unit,
    onApply: () -> Unit
) {
    val programColor = TaNaMaoColors.programColor(benefit.programCode)

    PropelCard(
        modifier = Modifier.fillMaxWidth(),
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
                verticalAlignment = Alignment.Top
            ) {
                Row(
                    horizontalArrangement = Arrangement.spacedBy(TaNaMaoDimens.spacing3),
                    verticalAlignment = Alignment.CenterVertically
                ) {
                    Box(
                        modifier = Modifier
                            .size(TaNaMaoDimens.programIconContainer)
                            .clip(RoundedCornerShape(TaNaMaoDimens.cardRadiusSmall))
                            .background(programColor.copy(alpha = 0.15f)),
                        contentAlignment = Alignment.Center
                    ) {
                        Icon(
                            imageVector = getProgramIcon(benefit.programCode),
                            contentDescription = null,
                            tint = programColor,
                            modifier = Modifier.size(TaNaMaoDimens.iconSizeMedium)
                        )
                    }

                    Column {
                        Text(
                            text = benefit.programName,
                            style = MaterialTheme.typography.titleSmall,
                            fontWeight = FontWeight.SemiBold,
                            color = MaterialTheme.colorScheme.onSurface
                        )
                        BenefitStatusBadge(status = UiBenefitStatus.Eligible)
                    }
                }

                benefit.monthlyValue?.let { value ->
                    Column(horizontalAlignment = Alignment.End) {
                        Text(
                            text = "até",
                            style = MaterialTheme.typography.labelSmall,
                            color = MaterialTheme.colorScheme.onSurfaceVariant
                        )
                        Text(
                            text = value.formatAsCurrency(),
                            style = TaNaMaoTextStyles.moneyMedium,
                            color = StatusEligible
                        )
                        Text(
                            text = "/mês",
                            style = MaterialTheme.typography.labelSmall,
                            color = MaterialTheme.colorScheme.onSurfaceVariant
                        )
                    }
                }
            }

            // Eligibility score
            benefit.eligibilityDetails?.let { details ->
                Row(
                    modifier = Modifier
                        .fillMaxWidth()
                        .clip(RoundedCornerShape(TaNaMaoDimens.cardRadiusSmall))
                        .background(StatusEligible.copy(alpha = 0.1f))
                        .padding(TaNaMaoDimens.spacing3),
                    horizontalArrangement = Arrangement.SpaceBetween,
                    verticalAlignment = Alignment.CenterVertically
                ) {
                    Row(
                        horizontalArrangement = Arrangement.spacedBy(TaNaMaoDimens.spacing2),
                        verticalAlignment = Alignment.CenterVertically
                    ) {
                        Icon(
                            imageVector = Icons.Filled.CheckCircle,
                            contentDescription = null,
                            tint = StatusEligible,
                            modifier = Modifier.size(20.dp)
                        )
                        Text(
                            text = "Compatibilidade",
                            style = MaterialTheme.typography.bodySmall,
                            color = MaterialTheme.colorScheme.onSurfaceVariant
                        )
                    }
                    Text(
                        text = "${(details.overallScore * 100).toInt()}%",
                        style = TaNaMaoTextStyles.percentage,
                        fontWeight = FontWeight.Bold,
                        color = StatusEligible
                    )
                }
            }

            // Actions
            Row(
                modifier = Modifier.fillMaxWidth(),
                horizontalArrangement = Arrangement.spacedBy(TaNaMaoDimens.spacing3)
            ) {
                PropelButton(
                    text = "Ver detalhes",
                    onClick = onViewDetails,
                    style = PropelButtonStyle.Secondary,
                    size = PropelButtonSize.Medium,
                    modifier = Modifier.weight(1f)
                )
                PropelButton(
                    text = "Solicitar",
                    onClick = onApply,
                    style = PropelButtonStyle.Primary,
                    size = PropelButtonSize.Medium,
                    leadingIcon = Icons.Filled.ArrowForward,
                    modifier = Modifier.weight(1f)
                )
            }
        }
    }
}

@Composable
private fun PaymentHistoryList(
    historyGroups: List<PaymentHistoryGroup>,
    isLoading: Boolean
) {
    if (historyGroups.isEmpty() && !isLoading) {
        EmptyStateView(
            icon = Icons.Outlined.Receipt,
            title = "Nenhum pagamento registrado",
            message = "O histórico de pagamentos aparecerá aqui quando você começar a receber benefícios."
        )
    } else {
        LazyColumn(
            modifier = Modifier.fillMaxSize(),
            contentPadding = PaddingValues(
                horizontal = TaNaMaoDimens.screenPaddingHorizontal,
                vertical = TaNaMaoDimens.spacing2
            ),
            verticalArrangement = Arrangement.spacedBy(TaNaMaoDimens.spacing4)
        ) {
            historyGroups.forEach { group ->
                item(key = group.yearMonth.toString()) {
                    PaymentMonthHeader(
                        yearMonth = group.yearMonth,
                        totalValue = group.totalValue
                    )
                }

                items(group.payments, key = { it.id }) { payment ->
                    PaymentHistoryItem(payment = payment)
                }
            }

            item {
                Spacer(modifier = Modifier.height(TaNaMaoDimens.bottomNavHeight + 16.dp))
            }
        }
    }
}

@Composable
private fun PaymentMonthHeader(
    yearMonth: YearMonth,
    totalValue: Double
) {
    Row(
        modifier = Modifier.fillMaxWidth(),
        horizontalArrangement = Arrangement.SpaceBetween,
        verticalAlignment = Alignment.CenterVertically
    ) {
        Text(
            text = yearMonth.formatBrazilian(),
            style = MaterialTheme.typography.titleSmall,
            fontWeight = FontWeight.SemiBold,
            color = MaterialTheme.colorScheme.onSurface
        )
        Text(
            text = totalValue.formatAsCurrency(),
            style = TaNaMaoTextStyles.moneyMedium,
            color = MaterialTheme.colorScheme.primary
        )
    }
}

@Composable
private fun PaymentHistoryItem(payment: PaymentHistoryItem) {
    val programColor = TaNaMaoColors.programColor(payment.programCode)
    val statusColor = when (payment.status) {
        PaymentStatus.PAID -> StatusActive
        PaymentStatus.PENDING -> StatusPending
        PaymentStatus.FAILED -> ErrorColor
        PaymentStatus.RETURNED -> WarningColor
    }

    PropelCard(
        modifier = Modifier.fillMaxWidth(),
        elevation = PropelCardElevation.Flat
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
                Box(
                    modifier = Modifier
                        .size(40.dp)
                        .clip(RoundedCornerShape(TaNaMaoDimens.cardRadiusSmall))
                        .background(programColor.copy(alpha = 0.15f)),
                    contentAlignment = Alignment.Center
                ) {
                    Icon(
                        imageVector = getProgramIcon(payment.programCode),
                        contentDescription = null,
                        tint = programColor,
                        modifier = Modifier.size(20.dp)
                    )
                }

                Column {
                    Text(
                        text = payment.programName,
                        style = MaterialTheme.typography.bodyMedium,
                        fontWeight = FontWeight.Medium,
                        color = MaterialTheme.colorScheme.onSurface
                    )
                    Text(
                        text = payment.date.formatBrazilian(),
                        style = MaterialTheme.typography.bodySmall,
                        color = MaterialTheme.colorScheme.onSurfaceVariant
                    )
                }
            }

            Column(horizontalAlignment = Alignment.End) {
                Text(
                    text = payment.value.formatAsCurrency(),
                    style = MaterialTheme.typography.bodyMedium,
                    fontWeight = FontWeight.SemiBold,
                    color = statusColor
                )
                Text(
                    text = when (payment.status) {
                        PaymentStatus.PAID -> "Pago"
                        PaymentStatus.PENDING -> "Pendente"
                        PaymentStatus.FAILED -> "Falhou"
                        PaymentStatus.RETURNED -> "Devolvido"
                    },
                    style = MaterialTheme.typography.labelSmall,
                    color = statusColor
                )
            }
        }
    }
}

@Composable
private fun EmptyStateView(
    icon: androidx.compose.ui.graphics.vector.ImageVector,
    title: String,
    message: String
) {
    Box(
        modifier = Modifier
            .fillMaxSize()
            .padding(TaNaMaoDimens.screenPaddingHorizontal),
        contentAlignment = Alignment.Center
    ) {
        Column(
            horizontalAlignment = Alignment.CenterHorizontally,
            verticalArrangement = Arrangement.spacedBy(TaNaMaoDimens.spacing3)
        ) {
            Box(
                modifier = Modifier
                    .size(80.dp)
                    .clip(RoundedCornerShape(TaNaMaoDimens.cardRadius))
                    .background(MaterialTheme.colorScheme.surfaceVariant),
                contentAlignment = Alignment.Center
            ) {
                Icon(
                    imageVector = icon,
                    contentDescription = null,
                    tint = MaterialTheme.colorScheme.onSurfaceVariant,
                    modifier = Modifier.size(40.dp)
                )
            }

            Text(
                text = title,
                style = MaterialTheme.typography.titleMedium,
                fontWeight = FontWeight.SemiBold,
                color = MaterialTheme.colorScheme.onSurface
            )

            Text(
                text = message,
                style = MaterialTheme.typography.bodyMedium,
                color = MaterialTheme.colorScheme.onSurfaceVariant,
                modifier = Modifier.padding(horizontal = TaNaMaoDimens.spacing4)
            )
        }
    }
}

// Extension function
private fun DomainBenefitStatus.toBenefitStatus(): UiBenefitStatus {
    return when (this) {
        DomainBenefitStatus.ACTIVE -> UiBenefitStatus.Active
        DomainBenefitStatus.PENDING -> UiBenefitStatus.Pending
        DomainBenefitStatus.ELIGIBLE -> UiBenefitStatus.Eligible
        DomainBenefitStatus.NOT_ELIGIBLE -> UiBenefitStatus.NotEligible
        DomainBenefitStatus.BLOCKED -> UiBenefitStatus.Blocked
    }
}
