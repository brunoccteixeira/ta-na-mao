package br.gov.tanamao.presentation.ui.alerts

import androidx.compose.animation.*
import androidx.compose.foundation.background
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
import androidx.compose.ui.graphics.Color
import androidx.compose.ui.graphics.vector.ImageVector
import androidx.compose.ui.text.font.FontWeight
import androidx.compose.ui.unit.dp
import br.gov.tanamao.domain.model.*
import br.gov.tanamao.presentation.components.*
import br.gov.tanamao.presentation.theme.*
import java.time.LocalDate
import java.time.format.DateTimeFormatter
import java.time.temporal.ChronoUnit

@Composable
fun AlertsScreen(
    onNavigateBack: () -> Unit,
    onAlertClick: (UserAlert) -> Unit,
    alerts: List<UserAlert> = emptyList()
) {
    // Mock data for demonstration
    val mockAlerts = remember {
        listOf(
            UserAlert(
                id = "1",
                type = AlertCategory.NEW_BENEFIT,
                title = "Novo benefício disponível!",
                message = "Você pode ter direito à ajuda para idosos e pessoas com deficiência. Descubra agora.",
                actionLabel = "Verificar",
                actionRoute = "chat",
                createdAt = LocalDate.now(),
                priority = AlertPriority.HIGH
            ),
            UserAlert(
                id = "2",
                type = AlertCategory.PAYMENT,
                title = "Pagamento confirmado",
                message = "Seu Bolsa Família de R$ 600,00 foi depositado na conta Caixa.",
                createdAt = LocalDate.now().minusDays(1),
                isRead = true
            ),
            UserAlert(
                id = "3",
                type = AlertCategory.DEADLINE,
                title = "Prazo para recadastramento",
                message = "Seu cadastro no CadÚnico precisa ser atualizado até 15/01/2025.",
                actionLabel = "Agendar",
                createdAt = LocalDate.now().minusDays(2),
                priority = AlertPriority.HIGH
            ),
            UserAlert(
                id = "4",
                type = AlertCategory.INFO,
                title = "Tarifa Social atualizada",
                message = "O desconto da sua conta de luz foi renovado automaticamente.",
                createdAt = LocalDate.now().minusDays(5),
                isRead = true
            ),
            UserAlert(
                id = "5",
                type = AlertCategory.ACTION_REQUIRED,
                title = "Documentos pendentes",
                message = "Complete seu cadastro enviando o comprovante de residência.",
                actionLabel = "Enviar",
                createdAt = LocalDate.now().minusDays(7)
            )
        )
    }

    val displayAlerts = if (alerts.isEmpty()) mockAlerts else alerts
    val unreadCount = displayAlerts.count { !it.isRead }

    Box(
        modifier = Modifier
            .fillMaxSize()
            .background(BackgroundPrimary)
    ) {
        Column(modifier = Modifier.fillMaxSize()) {
            // Top Bar
            AlertsTopBar(
                unreadCount = unreadCount,
                onNavigateBack = onNavigateBack
            )

            if (displayAlerts.isEmpty()) {
                EmptyAlertsView()
            } else {
                LazyColumn(
                    modifier = Modifier.fillMaxSize(),
                    contentPadding = PaddingValues(
                        horizontal = TaNaMaoDimens.screenPaddingHorizontal,
                        vertical = TaNaMaoDimens.spacing3
                    ),
                    verticalArrangement = Arrangement.spacedBy(TaNaMaoDimens.spacing3)
                ) {
                    // Group by date
                    val today = displayAlerts.filter { it.createdAt == LocalDate.now() }
                    val yesterday = displayAlerts.filter {
                        it.createdAt == LocalDate.now().minusDays(1)
                    }
                    val older = displayAlerts.filter {
                        it.createdAt < LocalDate.now().minusDays(1)
                    }

                    if (today.isNotEmpty()) {
                        item {
                            DateHeader(text = "Hoje")
                        }
                        items(today) { alert ->
                            AlertCard(
                                alert = alert,
                                onClick = { onAlertClick(alert) }
                            )
                        }
                    }

                    if (yesterday.isNotEmpty()) {
                        item {
                            DateHeader(text = "Ontem")
                        }
                        items(yesterday) { alert ->
                            AlertCard(
                                alert = alert,
                                onClick = { onAlertClick(alert) }
                            )
                        }
                    }

                    if (older.isNotEmpty()) {
                        item {
                            DateHeader(text = "Anteriores")
                        }
                        items(older) { alert ->
                            AlertCard(
                                alert = alert,
                                onClick = { onAlertClick(alert) }
                            )
                        }
                    }

                    item {
                        Spacer(modifier = Modifier.height(TaNaMaoDimens.bottomNavHeight))
                    }
                }
            }
        }
    }
}

@Composable
private fun AlertsTopBar(
    unreadCount: Int,
    onNavigateBack: () -> Unit
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

        Row(
            horizontalArrangement = Arrangement.spacedBy(TaNaMaoDimens.spacing2),
            verticalAlignment = Alignment.CenterVertically
        ) {
            Text(
                text = "Notificações",
                style = MaterialTheme.typography.titleLarge,
                fontWeight = FontWeight.Bold,
                color = TextPrimary
            )

            if (unreadCount > 0) {
                Box(
                    modifier = Modifier
                        .clip(RoundedCornerShape(TaNaMaoDimens.chipRadius))
                        .background(AccentOrange)
                        .padding(horizontal = 8.dp, vertical = 2.dp)
                ) {
                    Text(
                        text = unreadCount.toString(),
                        style = TaNaMaoTextStyles.badge,
                        color = TextOnAccent
                    )
                }
            }
        }

        // Settings
        PropelIconButton(
            icon = Icons.Outlined.Settings,
            onClick = { /* Navigate to notification settings */ },
            style = PropelButtonStyle.Ghost
        )
    }
}

@Composable
private fun DateHeader(text: String) {
    Text(
        text = text,
        style = MaterialTheme.typography.labelMedium,
        color = TextTertiary,
        modifier = Modifier.padding(vertical = TaNaMaoDimens.spacing2)
    )
}

@Composable
private fun AlertCard(
    alert: UserAlert,
    onClick: () -> Unit
) {
    val iconData = getAlertIconData(alert.type)
    val isUnread = !alert.isRead

    PropelCard(
        modifier = Modifier.fillMaxWidth(),
        onClick = onClick,
        elevation = if (isUnread) PropelCardElevation.Elevated else PropelCardElevation.Flat,
        borderColor = if (alert.priority == AlertPriority.HIGH || alert.priority == AlertPriority.URGENT)
            iconData.color.copy(alpha = 0.5f) else null
    ) {
        Row(
            modifier = Modifier.fillMaxWidth(),
            horizontalArrangement = Arrangement.spacedBy(TaNaMaoDimens.spacing3)
        ) {
            // Icon
            Box(
                modifier = Modifier
                    .size(44.dp)
                    .clip(RoundedCornerShape(12.dp))
                    .background(iconData.color.copy(alpha = 0.15f)),
                contentAlignment = Alignment.Center
            ) {
                Icon(
                    imageVector = iconData.icon,
                    contentDescription = null,
                    tint = iconData.color,
                    modifier = Modifier.size(24.dp)
                )
            }

            // Content
            Column(
                modifier = Modifier.weight(1f),
                verticalArrangement = Arrangement.spacedBy(TaNaMaoDimens.spacing1)
            ) {
                Row(
                    modifier = Modifier.fillMaxWidth(),
                    horizontalArrangement = Arrangement.SpaceBetween,
                    verticalAlignment = Alignment.Top
                ) {
                    Text(
                        text = alert.title,
                        style = MaterialTheme.typography.titleSmall,
                        fontWeight = if (isUnread) FontWeight.SemiBold else FontWeight.Normal,
                        color = TextPrimary,
                        modifier = Modifier.weight(1f)
                    )

                    Text(
                        text = formatRelativeDate(alert.createdAt),
                        style = MaterialTheme.typography.labelSmall,
                        color = TextTertiary
                    )
                }

                Text(
                    text = alert.message,
                    style = MaterialTheme.typography.bodySmall,
                    color = TextSecondary,
                    maxLines = 2
                )

                // Action button
                alert.actionLabel?.let { label ->
                    Spacer(modifier = Modifier.height(TaNaMaoDimens.spacing1))
                    PropelTextButton(
                        text = label,
                        onClick = onClick,
                        color = iconData.color
                    )
                }
            }

            // Unread indicator
            if (isUnread) {
                Box(
                    modifier = Modifier
                        .size(8.dp)
                        .clip(CircleShape)
                        .background(AccentOrange)
                )
            }
        }
    }
}

@Composable
private fun EmptyAlertsView() {
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
                    .background(BackgroundTertiary),
                contentAlignment = Alignment.Center
            ) {
                Icon(
                    imageVector = Icons.Outlined.Notifications,
                    contentDescription = null,
                    tint = TextTertiary,
                    modifier = Modifier.size(40.dp)
                )
            }

            Text(
                text = "Nenhuma notificação",
                style = MaterialTheme.typography.titleMedium,
                fontWeight = FontWeight.SemiBold,
                color = TextPrimary
            )

            Text(
                text = "Você receberá alertas sobre seus benefícios, pagamentos e prazos aqui.",
                style = MaterialTheme.typography.bodyMedium,
                color = TextSecondary
            )
        }
    }
}

private data class AlertIconData(
    val icon: ImageVector,
    val color: Color
)

private fun getAlertIconData(category: AlertCategory): AlertIconData {
    return when (category) {
        AlertCategory.NEW_BENEFIT -> AlertIconData(Icons.Filled.CardGiftcard, StatusEligible)
        AlertCategory.ACTION_REQUIRED -> AlertIconData(Icons.Filled.Warning, Warning)
        AlertCategory.PAYMENT -> AlertIconData(Icons.Filled.Payments, StatusActive)
        AlertCategory.DEADLINE -> AlertIconData(Icons.Filled.Schedule, Error)
        AlertCategory.INFO -> AlertIconData(Icons.Filled.Info, Info)
        AlertCategory.WARNING -> AlertIconData(Icons.Filled.Warning, Warning)
    }
}

private fun formatRelativeDate(date: LocalDate): String {
    val today = LocalDate.now()
    val days = ChronoUnit.DAYS.between(date, today)

    return when {
        days == 0L -> "Hoje"
        days == 1L -> "Ontem"
        days < 7 -> "${days}d"
        days < 30 -> "${days / 7}sem"
        else -> date.format(DateTimeFormatter.ofPattern("dd/MM"))
    }
}
