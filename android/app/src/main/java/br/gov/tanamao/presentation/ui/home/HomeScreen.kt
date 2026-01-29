package br.gov.tanamao.presentation.ui.home

import androidx.compose.animation.*
import androidx.compose.foundation.background
import androidx.compose.foundation.clickable
import androidx.compose.foundation.layout.*
import androidx.compose.foundation.lazy.LazyRow
import androidx.compose.foundation.lazy.items
import androidx.compose.foundation.rememberScrollState
import androidx.compose.foundation.shape.CircleShape
import androidx.compose.foundation.shape.RoundedCornerShape
import androidx.compose.foundation.verticalScroll
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
import br.gov.tanamao.domain.model.BenefitStatus as DomainBenefitStatus
import br.gov.tanamao.presentation.components.*
import br.gov.tanamao.presentation.components.BenefitStatus as UiBenefitStatus
import br.gov.tanamao.presentation.theme.Success
import br.gov.tanamao.presentation.theme.TaNaMaoColors
import br.gov.tanamao.presentation.theme.TaNaMaoDimens
import br.gov.tanamao.presentation.theme.TaNaMaoTextStyles
import br.gov.tanamao.presentation.util.formatNumber
import br.gov.tanamao.presentation.components.PropelButton
import br.gov.tanamao.presentation.components.PropelButtonStyle

@Composable
fun HomeScreen(
    onNavigateToMap: () -> Unit,
    onNavigateToSearch: () -> Unit,
    onNavigateToChat: () -> Unit,
    onNavigateToChatWithMessage: (String) -> Unit = { onNavigateToChat() },
    onNavigateToWallet: () -> Unit = {},
    onNavigateToBenefit: (String) -> Unit = {},
    onNavigateToProfile: () -> Unit = {},
    onNavigateToMoney: () -> Unit = {},
    viewModel: HomeViewModel = hiltViewModel()
) {
    val uiState by viewModel.uiState.collectAsState()
    val scrollState = rememberScrollState()

    Box(
        modifier = Modifier
            .fillMaxSize()
            .background(MaterialTheme.colorScheme.background)
    ) {
        Column(
            modifier = Modifier
                .fillMaxSize()
                .verticalScroll(scrollState)
        ) {
            // Top Bar
            HomeTopBar(
                userName = uiState.userName,
                unreadCount = uiState.unreadAlertsCount,
                onProfileClick = onNavigateToProfile
            )

            // Content
            Column(
                modifier = Modifier.padding(horizontal = TaNaMaoDimens.screenPaddingHorizontal),
                verticalArrangement = Arrangement.spacedBy(TaNaMaoDimens.sectionSpacing)
            ) {
                // Priority Alert Banners (show all high priority alerts)
                uiState.alerts
                    .filter { it.priority == AlertPriority.HIGH || it.priority == AlertPriority.URGENT }
                    .take(2) // Show max 2 alerts
                    .forEach { alert ->
                        AlertBanner(
                            title = alert.title,
                            message = alert.message,
                            type = alert.type.toAlertType(),
                            action = alert.actionLabel,
                            onAction = {
                                // Determinar mensagem baseado no tipo de alerta
                                val initialMessage = when (alert.type) {
                                    AlertCategory.ACTION_REQUIRED -> "quero pedir remédios pelo Farmácia Popular"
                                    AlertCategory.NEW_BENEFIT -> "quais benefícios eu recebo"
                                    AlertCategory.DEADLINE -> "que documentos preciso"
                                    else -> ""
                                }
                                if (initialMessage.isNotEmpty()) {
                                    onNavigateToChatWithMessage(initialMessage)
                                } else {
                                    onNavigateToChat()
                                }
                            },
                            onDismiss = { viewModel.dismissAlert(alert.id) }
                        )
                        Spacer(modifier = Modifier.height(TaNaMaoDimens.spacing2))
                    }

                // Dinheiro Esquecido Card
                MoneyForgottenCard(
                    onNavigateToMoney = onNavigateToMoney,
                    onCheckMoney = { onNavigateToChatWithMessage("verificar meu dinheiro esquecido") }
                )

                // Wallet Summary Card
                uiState.walletSummary?.let { wallet ->
                    WalletSummarySection(
                        walletSummary = wallet,
                        onViewAll = onNavigateToWallet
                    )
                }

                // User Benefits Carousel
                if (uiState.userBenefits.isNotEmpty()) {
                    BenefitsCarouselSection(
                        benefits = uiState.userBenefits,
                        onBenefitClick = onNavigateToBenefit,
                        onViewAll = onNavigateToWallet
                    )
                }

                // Eligibility CTA
                if (uiState.eligibleBenefits.isNotEmpty()) {
                    EligibilityCTASection(
                        eligibleCount = uiState.eligibleBenefits.size,
                        onClick = onNavigateToChat
                    )
                }

                // Próximos Pagamentos (mais relevante para cidadão)
                NextPaymentsSection(
                    userBenefits = uiState.userBenefits,
                    onViewCalendar = onNavigateToWallet
                )

                // Perto de Você
                NearbyServicesSection(
                    onFindCras = { onNavigateToChatWithMessage("onde fica o posto de assistência social") },
                    onFindPharmacy = { onNavigateToChatWithMessage("quero pedir remédios pelo Farmácia Popular") }
                )

                // Quick Actions
                QuickActionsSection(
                    onMapClick = onNavigateToMap,
                    onSearchClick = onNavigateToSearch,
                    onChatClick = onNavigateToChat
                )

                // Error message
                uiState.error?.let { error ->
                    AlertInline(
                        message = error,
                        type = AlertType.Error
                    )
                }

                Spacer(modifier = Modifier.height(TaNaMaoDimens.bottomNavHeight + 32.dp))
            }
        }

        // Loading overlay
        if (uiState.isLoading && uiState.nationalStats == null) {
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
private fun HomeTopBar(
    userName: String?,
    unreadCount: Int,
    onProfileClick: () -> Unit
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
        // Greeting
        Column {
            Text(
                text = "Olá${userName?.let { ", $it" } ?: ""}!",
                style = MaterialTheme.typography.headlineSmall,
                fontWeight = FontWeight.Bold,
                color = MaterialTheme.colorScheme.onBackground
            )
            Text(
                text = "Seus benefícios em um só lugar",
                style = MaterialTheme.typography.bodyMedium,
                color = MaterialTheme.colorScheme.onSurfaceVariant
            )
        }

        // Profile button with badge
        Box {
            PropelIconButton(
                icon = Icons.Outlined.Person,
                onClick = onProfileClick,
                style = PropelButtonStyle.Dark,
                size = 48.dp
            )

            if (unreadCount > 0) {
                Box(
                    modifier = Modifier
                        .align(Alignment.TopEnd)
                        .size(18.dp)
                        .clip(CircleShape)
                        .background(MaterialTheme.colorScheme.primary),
                    contentAlignment = Alignment.Center
                ) {
                    Text(
                        text = if (unreadCount > 9) "9+" else unreadCount.toString(),
                        style = TaNaMaoTextStyles.badge,
                        color = MaterialTheme.colorScheme.onPrimary
                    )
                }
            }
        }
    }
}

@Composable
private fun WalletSummarySection(
    walletSummary: WalletSummary,
    onViewAll: () -> Unit
) {
    BenefitSummaryCard(
        totalMonthlyValue = walletSummary.totalMonthlyValue.formatAsCurrency(),
        activeBenefitsCount = walletSummary.activeBenefitsCount,
        eligibleBenefitsCount = walletSummary.eligibleBenefitsCount,
        onViewAll = onViewAll
    )
}

@Composable
private fun BenefitsCarouselSection(
    benefits: List<UserBenefit>,
    onBenefitClick: (String) -> Unit,
    onViewAll: () -> Unit
) {
    Column(verticalArrangement = Arrangement.spacedBy(TaNaMaoDimens.spacing3)) {
        // Header
        Row(
            modifier = Modifier.fillMaxWidth(),
            horizontalArrangement = Arrangement.SpaceBetween,
            verticalAlignment = Alignment.CenterVertically
        ) {
            Text(
                text = "Seus Benefícios",
                style = MaterialTheme.typography.titleMedium,
                fontWeight = FontWeight.SemiBold,
                color = MaterialTheme.colorScheme.onSurface
            )
            PropelTextButton(
                text = "Ver todos",
                onClick = onViewAll
            )
        }

        // Carousel
        LazyRow(
            horizontalArrangement = Arrangement.spacedBy(TaNaMaoDimens.spacing3),
            contentPadding = PaddingValues(end = TaNaMaoDimens.spacing4)
        ) {
            items(benefits) { benefit ->
                BenefitCardCompact(
                    programName = benefit.programName,
                    programCode = benefit.programCode,
                    status = benefit.status.toBenefitStatus(),
                    value = benefit.monthlyValue?.formatAsCurrency(),
                    onClick = { onBenefitClick(benefit.id) }
                )
            }
        }
    }
}

@Composable
private fun EligibilityCTASection(
    eligibleCount: Int,
    onClick: () -> Unit
) {
    PromoBanner(
        title = "Você pode ter direito a mais $eligibleCount benefício${if (eligibleCount > 1) "s" else ""}!",
        subtitle = "Descubra se você tem direito a benefícios",
        icon = Icons.Filled.AutoAwesome,
        actionLabel = "Verificar agora",
        onAction = onClick
    )
}

@Composable
private fun NextPaymentsSection(
    userBenefits: List<UserBenefit>,
    onViewCalendar: () -> Unit
) {
    // Filter only benefits with monetary value (exclude Farmácia Popular, etc.)
    val paymentBenefits = userBenefits.filter {
        it.status == DomainBenefitStatus.ACTIVE && it.monthlyValue != null
    }

    if (paymentBenefits.isEmpty()) return

    Column(verticalArrangement = Arrangement.spacedBy(TaNaMaoDimens.spacing3)) {
        // Header
        Row(
            modifier = Modifier.fillMaxWidth(),
            horizontalArrangement = Arrangement.SpaceBetween,
            verticalAlignment = Alignment.CenterVertically
        ) {
            Text(
                text = "Próximos Pagamentos",
                style = MaterialTheme.typography.titleMedium,
                fontWeight = FontWeight.SemiBold,
                color = MaterialTheme.colorScheme.onSurface
            )
            PropelTextButton(
                text = "Ver calendário",
                onClick = onViewCalendar
            )
        }

        // Payment cards - sorted by next payment date
        paymentBenefits
            .sortedBy { it.nextPaymentDate }
            .take(2)
            .forEach { benefit ->
                val daysUntil = benefit.nextPaymentDate?.let {
                    java.time.temporal.ChronoUnit.DAYS.between(java.time.LocalDate.now(), it).toInt()
                } ?: 15

                PaymentReminderCard(
                    programName = benefit.programName,
                    programCode = benefit.programCode,
                    value = benefit.monthlyValue?.formatAsCurrency() ?: "R$ --",
                    daysUntilPayment = daysUntil.coerceAtLeast(0),
                    onClick = { }
                )
            }
    }
}

@Composable
private fun PaymentReminderCard(
    programName: String,
    programCode: String,
    value: String,
    daysUntilPayment: Int,
    onClick: () -> Unit
) {
    val programColor = TaNaMaoColors.programColor(programCode)

    PropelCard(
        onClick = onClick,
        elevation = PropelCardElevation.Standard,
        contentPadding = PaddingValues(TaNaMaoDimens.spacing4)
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
                // Program indicator
                Box(
                    modifier = Modifier
                        .size(40.dp)
                        .clip(RoundedCornerShape(TaNaMaoDimens.cardRadiusSmall))
                        .background(programColor.copy(alpha = 0.2f)),
                    contentAlignment = Alignment.Center
                ) {
                    Icon(
                        imageVector = Icons.Default.AccountBalanceWallet,
                        contentDescription = null,
                        tint = programColor,
                        modifier = Modifier.size(20.dp)
                    )
                }

                Column {
                    Text(
                        text = programName,
                        style = MaterialTheme.typography.bodyMedium,
                        fontWeight = FontWeight.SemiBold,
                        color = MaterialTheme.colorScheme.onSurface
                    )
                    Text(
                        text = when {
                            daysUntilPayment == 0 -> "Disponível hoje!"
                            daysUntilPayment == 1 -> "Amanhã"
                            daysUntilPayment <= 7 -> "Em $daysUntilPayment dias"
                            else -> "Em ${daysUntilPayment} dias"
                        },
                        style = MaterialTheme.typography.bodySmall,
                        color = if (daysUntilPayment <= 3) Success else MaterialTheme.colorScheme.onSurfaceVariant
                    )
                }
            }

            Text(
                text = value,
                style = MaterialTheme.typography.titleMedium,
                fontWeight = FontWeight.Bold,
                color = MaterialTheme.colorScheme.primary
            )
        }
    }
}

@Composable
private fun NearbyServicesSection(
    onFindCras: () -> Unit,
    onFindPharmacy: () -> Unit
) {
    Column(verticalArrangement = Arrangement.spacedBy(TaNaMaoDimens.spacing3)) {
        Text(
            text = "Perto de Você",
            style = MaterialTheme.typography.titleMedium,
            fontWeight = FontWeight.SemiBold,
            color = MaterialTheme.colorScheme.onSurface
        )

        Row(
            modifier = Modifier.fillMaxWidth(),
            horizontalArrangement = Arrangement.spacedBy(TaNaMaoDimens.spacing3)
        ) {
            NearbyServiceCard(
                icon = Icons.Default.Business,
                title = "CRAS",
                subtitle = "Cadastro e benefícios",
                onClick = onFindCras,
                modifier = Modifier.weight(1f)
            )
            NearbyServiceCard(
                icon = Icons.Default.LocalPharmacy,
                title = "Farmácias",
                subtitle = "Remédios gratuitos",
                onClick = onFindPharmacy,
                modifier = Modifier.weight(1f)
            )
        }
    }
}

@Composable
private fun NearbyServiceCard(
    icon: ImageVector,
    title: String,
    subtitle: String,
    onClick: () -> Unit,
    modifier: Modifier = Modifier
) {
    PropelCard(
        modifier = modifier,
        onClick = onClick,
        elevation = PropelCardElevation.Standard,
        contentPadding = PaddingValues(TaNaMaoDimens.spacing3)
    ) {
        Row(
            verticalAlignment = Alignment.CenterVertically,
            horizontalArrangement = Arrangement.spacedBy(TaNaMaoDimens.spacing3)
        ) {
            Box(
                modifier = Modifier
                    .size(40.dp)
                    .clip(RoundedCornerShape(TaNaMaoDimens.cardRadiusSmall))
                    .background(MaterialTheme.colorScheme.primaryContainer),
                contentAlignment = Alignment.Center
            ) {
                Icon(
                    imageVector = icon,
                    contentDescription = null,
                    tint = MaterialTheme.colorScheme.primary,
                    modifier = Modifier.size(20.dp)
                )
            }

            Column {
                Text(
                    text = title,
                    style = MaterialTheme.typography.bodyMedium,
                    fontWeight = FontWeight.SemiBold,
                    color = MaterialTheme.colorScheme.onSurface
                )
                Text(
                    text = subtitle,
                    style = MaterialTheme.typography.bodySmall,
                    color = MaterialTheme.colorScheme.onSurfaceVariant
                )
            }
        }
    }
}

@Composable
private fun QuickActionsSection(
    onMapClick: () -> Unit,
    onSearchClick: () -> Unit,
    onChatClick: () -> Unit
) {
    Column(verticalArrangement = Arrangement.spacedBy(TaNaMaoDimens.spacing3)) {
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
                icon = Icons.Outlined.Map,
                label = "Mapa",
                description = "Ver cobertura",
                onClick = onMapClick,
                modifier = Modifier.weight(1f)
            )
            QuickActionCard(
                icon = Icons.Outlined.Search,
                label = "Buscar",
                description = "Municípios",
                onClick = onSearchClick,
                modifier = Modifier.weight(1f)
            )
            QuickActionCard(
                icon = Icons.Outlined.Chat,
                label = "Assistente",
                description = "Tirar dúvidas",
                onClick = onChatClick,
                modifier = Modifier.weight(1f)
            )
        }
    }
}

@Composable
private fun QuickActionCard(
    icon: ImageVector,
    label: String,
    description: String,
    onClick: () -> Unit,
    modifier: Modifier = Modifier
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
            verticalArrangement = Arrangement.spacedBy(TaNaMaoDimens.spacing2)
        ) {
            Box(
                modifier = Modifier
                    .size(44.dp)
                    .clip(RoundedCornerShape(TaNaMaoDimens.cardRadiusSmall))
                    .background(MaterialTheme.colorScheme.primaryContainer),
                contentAlignment = Alignment.Center
            ) {
                Icon(
                    imageVector = icon,
                    contentDescription = label,
                    tint = MaterialTheme.colorScheme.primary,
                    modifier = Modifier.size(24.dp)
                )
            }

            Column(horizontalAlignment = Alignment.CenterHorizontally) {
                Text(
                    text = label,
                    style = MaterialTheme.typography.labelMedium,
                    fontWeight = FontWeight.SemiBold,
                    color = MaterialTheme.colorScheme.onSurface
                )
                Text(
                    text = description,
                    style = MaterialTheme.typography.bodySmall,
                    color = MaterialTheme.colorScheme.onSurfaceVariant
                )
            }
        }
    }
}

@Composable
private fun MoneyForgottenCard(
    onNavigateToMoney: () -> Unit,
    onCheckMoney: () -> Unit
) {
    PropelCardAccent(
        elevation = PropelCardElevation.Elevated,
        modifier = Modifier.fillMaxWidth()
    ) {
        Row(
            modifier = Modifier.fillMaxWidth(),
            horizontalArrangement = Arrangement.SpaceBetween,
            verticalAlignment = Alignment.CenterVertically
        ) {
            Row(
                modifier = Modifier.weight(1f),
                horizontalArrangement = Arrangement.spacedBy(TaNaMaoDimens.spacing3),
                verticalAlignment = Alignment.CenterVertically
            ) {
                Box(
                    modifier = Modifier
                        .size(48.dp)
                        .clip(RoundedCornerShape(8.dp))
                        .background(MaterialTheme.colorScheme.primaryContainer),
                    contentAlignment = Alignment.Center
                ) {
                    Icon(
                        imageVector = Icons.Outlined.AccountBalance,
                        contentDescription = null,
                        tint = MaterialTheme.colorScheme.primary,
                        modifier = Modifier.size(24.dp)
                    )
                }
                Column {
                    Text(
                        text = "Dinheiro Esquecido",
                        style = MaterialTheme.typography.titleMedium,
                        fontWeight = FontWeight.Bold,
                        color = MaterialTheme.colorScheme.onSurface
                    )
                    Text(
                        text = "R$ 42 bilhões disponíveis",
                        style = MaterialTheme.typography.bodySmall,
                        color = MaterialTheme.colorScheme.onSurfaceVariant
                    )
                }
            }
            PropelButton(
                text = "Verificar",
                leadingIcon = Icons.Outlined.Search,
                onClick = onCheckMoney,
                style = PropelButtonStyle.Primary
            )
        }
    }
}

// Extension functions to convert domain models to UI models
private fun DomainBenefitStatus.toBenefitStatus(): UiBenefitStatus {
    return when (this) {
        DomainBenefitStatus.ACTIVE -> UiBenefitStatus.Active
        DomainBenefitStatus.PENDING -> UiBenefitStatus.Pending
        DomainBenefitStatus.ELIGIBLE -> UiBenefitStatus.Eligible
        DomainBenefitStatus.NOT_ELIGIBLE -> UiBenefitStatus.NotEligible
        DomainBenefitStatus.BLOCKED -> UiBenefitStatus.Blocked
    }
}

private fun AlertCategory.toAlertType(): AlertType {
    return when (this) {
        AlertCategory.NEW_BENEFIT -> AlertType.NewBenefit
        AlertCategory.ACTION_REQUIRED -> AlertType.Action
        AlertCategory.PAYMENT -> AlertType.Success
        AlertCategory.DEADLINE -> AlertType.Warning
        AlertCategory.INFO -> AlertType.Action
        AlertCategory.WARNING -> AlertType.Warning
    }
}
