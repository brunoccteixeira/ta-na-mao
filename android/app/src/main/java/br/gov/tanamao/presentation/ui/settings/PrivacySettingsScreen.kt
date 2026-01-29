package br.gov.tanamao.presentation.ui.settings

import androidx.compose.foundation.background
import androidx.compose.foundation.clickable
import androidx.compose.foundation.layout.*
import androidx.compose.foundation.rememberScrollState
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
import androidx.compose.ui.platform.LocalContext
import androidx.hilt.navigation.compose.hiltViewModel
import br.gov.tanamao.presentation.components.*
import br.gov.tanamao.presentation.theme.*
import br.gov.tanamao.presentation.ui.profile.ProfileViewModel

@Composable
fun PrivacySettingsScreen(
    onNavigateBack: () -> Unit,
    onNavigateToSettings: () -> Unit = {},
    viewModel: ProfileViewModel = hiltViewModel()
) {
    val context = LocalContext.current
    
    // State for settings
    var analyticsEnabled by remember { mutableStateOf(false) }
    var crashReportsEnabled by remember { mutableStateOf(true) }
    var personalizationEnabled by remember { mutableStateOf(true) }
    var locationEnabled by remember { mutableStateOf(false) }

    var notificationsEnabled by remember { mutableStateOf(true) }
    var paymentAlerts by remember { mutableStateOf(true) }
    var benefitAlerts by remember { mutableStateOf(true) }
    var deadlineAlerts by remember { mutableStateOf(true) }

    var biometricEnabled by remember { mutableStateOf(false) }

    var showDeleteDialog by remember { mutableStateOf(false) }
    var showExportDialog by remember { mutableStateOf(false) }

    Box(
        modifier = Modifier
            .fillMaxSize()
            .background(BackgroundPrimary)
    ) {
        Column(modifier = Modifier.fillMaxSize()) {
            // Top Bar
            SettingsTopBar(
                title = "Privacidade e Segurança",
                onNavigateBack = onNavigateBack
            )

            Column(
                modifier = Modifier
                    .fillMaxSize()
                    .verticalScroll(rememberScrollState())
                    .padding(horizontal = TaNaMaoDimens.screenPaddingHorizontal),
                verticalArrangement = Arrangement.spacedBy(TaNaMaoDimens.sectionSpacing)
            ) {
                Spacer(modifier = Modifier.height(TaNaMaoDimens.spacing2))

                // Appearance Section
                SettingsSection(title = "Aparência") {
                    SettingsItem(
                        icon = Icons.Outlined.Palette,
                        title = "Tema do aplicativo",
                        description = "Claro, escuro ou automático",
                        onClick = onNavigateToSettings
                    )
                }

                // Data Collection Section
                SettingsSection(title = "Coleta de Dados") {
                    SettingsSwitch(
                        icon = Icons.Outlined.Analytics,
                        title = "Analytics",
                        description = "Ajuda a melhorar o app",
                        checked = analyticsEnabled,
                        onCheckedChange = { analyticsEnabled = it }
                    )

                    SettingsSwitch(
                        icon = Icons.Outlined.BugReport,
                        title = "Relatórios de erro",
                        description = "Envia erros automaticamente",
                        checked = crashReportsEnabled,
                        onCheckedChange = { crashReportsEnabled = it }
                    )

                    SettingsSwitch(
                        icon = Icons.Outlined.AutoAwesome,
                        title = "Personalização",
                        description = "Recomendações personalizadas",
                        checked = personalizationEnabled,
                        onCheckedChange = { personalizationEnabled = it }
                    )

                    SettingsSwitch(
                        icon = Icons.Outlined.LocationOn,
                        title = "Localização",
                        description = "Para encontrar pontos de atendimento",
                        checked = locationEnabled,
                        onCheckedChange = { locationEnabled = it }
                    )
                }

                // Notifications Section
                SettingsSection(title = "Notificações") {
                    SettingsSwitch(
                        icon = Icons.Outlined.Notifications,
                        title = "Notificações",
                        description = "Ativar/desativar todas",
                        checked = notificationsEnabled,
                        onCheckedChange = { notificationsEnabled = it }
                    )

                    if (notificationsEnabled) {
                        SettingsSwitch(
                            icon = Icons.Outlined.Payments,
                            title = "Alertas de pagamento",
                            description = "Avisos sobre depósitos",
                            checked = paymentAlerts,
                            onCheckedChange = { paymentAlerts = it }
                        )

                        SettingsSwitch(
                            icon = Icons.Outlined.CardGiftcard,
                            title = "Novos benefícios",
                            description = "Quando houver oportunidades",
                            checked = benefitAlerts,
                            onCheckedChange = { benefitAlerts = it }
                        )

                        SettingsSwitch(
                            icon = Icons.Outlined.Schedule,
                            title = "Prazos importantes",
                            description = "Recadastramento e outros",
                            checked = deadlineAlerts,
                            onCheckedChange = { deadlineAlerts = it }
                        )
                    }
                }

                // Security Section
                SettingsSection(title = "Segurança") {
                    SettingsSwitch(
                        icon = Icons.Outlined.Fingerprint,
                        title = "Biometria",
                        description = "Usar impressão digital ou rosto",
                        checked = biometricEnabled,
                        onCheckedChange = { biometricEnabled = it }
                    )

                    SettingsItem(
                        icon = Icons.Outlined.Password,
                        title = "Alterar senha",
                        description = "Última alteração há 30 dias",
                        onClick = { /* Navigate to change password */ }
                    )

                    SettingsItem(
                        icon = Icons.Outlined.Devices,
                        title = "Sessões ativas",
                        description = "1 dispositivo conectado",
                        onClick = { /* Navigate to sessions */ }
                    )
                }

                // Data Management Section
                SettingsSection(title = "Seus Dados") {
                    SettingsItem(
                        icon = Icons.Outlined.Download,
                        title = "Exportar meus dados",
                        description = "Baixar cópia dos seus dados",
                        onClick = { showExportDialog = true }
                    )

                    SettingsItem(
                        icon = Icons.Outlined.Policy,
                        title = "Política de Privacidade",
                        description = "Ler documento completo",
                        onClick = { /* Open privacy policy */ }
                    )

                    SettingsItem(
                        icon = Icons.Outlined.Article,
                        title = "Termos de Uso",
                        description = "Ler documento completo",
                        onClick = { /* Open terms */ }
                    )

                    SettingsItem(
                        icon = Icons.Outlined.DeleteForever,
                        title = "Excluir minha conta",
                        description = "Remover todos os dados",
                        onClick = { showDeleteDialog = true },
                        isDestructive = true
                    )
                }

                // LGPD info
                LGPDInfoCard()

                Spacer(modifier = Modifier.height(TaNaMaoDimens.bottomNavHeight + 16.dp))
            }
        }
    }

    // Delete confirmation dialog
    if (showDeleteDialog) {
        AlertDialog(
            onDismissRequest = { showDeleteDialog = false },
            containerColor = BackgroundElevated,
            icon = {
                Icon(
                    imageVector = Icons.Filled.Warning,
                    contentDescription = null,
                    tint = Error
                )
            },
            title = {
                Text(
                    "Excluir conta?",
                    color = TextPrimary
                )
            },
            text = {
                Text(
                    "Esta ação é irreversível. Todos os seus dados serão permanentemente excluídos.",
                    color = TextSecondary
                )
            },
            confirmButton = {
                PropelButton(
                    text = "Excluir",
                    onClick = {
                        showDeleteDialog = false
                        // Handle deletion
                    },
                    style = PropelButtonStyle.Danger,
                    size = PropelButtonSize.Small
                )
            },
            dismissButton = {
                PropelButton(
                    text = "Cancelar",
                    onClick = { showDeleteDialog = false },
                    style = PropelButtonStyle.Ghost,
                    size = PropelButtonSize.Small
                )
            }
        )
    }

    // Export dialog
    if (showExportDialog) {
        AlertDialog(
            onDismissRequest = { showExportDialog = false },
            containerColor = BackgroundElevated,
            icon = {
                Icon(
                    imageVector = Icons.Outlined.Download,
                    contentDescription = null,
                    tint = AccentOrange
                )
            },
            title = {
                Text(
                    "Exportar dados",
                    color = TextPrimary
                )
            },
            text = {
                Text(
                    "Seus dados serão preparados e você poderá compartilhá-los através de qualquer aplicativo instalado no seu dispositivo (e-mail, WhatsApp, salvar em arquivo, etc.).",
                    color = TextSecondary
                )
            },
            confirmButton = {
                PropelButton(
                    text = "Exportar",
                    onClick = {
                        showExportDialog = false
                        viewModel.shareUserData(context)
                    },
                    style = PropelButtonStyle.Primary,
                    size = PropelButtonSize.Small
                )
            },
            dismissButton = {
                PropelButton(
                    text = "Cancelar",
                    onClick = { showExportDialog = false },
                    style = PropelButtonStyle.Ghost,
                    size = PropelButtonSize.Small
                )
            }
        )
    }
}

@Composable
private fun SettingsTopBar(
    title: String,
    onNavigateBack: () -> Unit
) {
    Row(
        modifier = Modifier
            .fillMaxWidth()
            .statusBarsPadding()
            .padding(TaNaMaoDimens.screenPaddingHorizontal)
            .padding(vertical = TaNaMaoDimens.spacing3),
        horizontalArrangement = Arrangement.spacedBy(TaNaMaoDimens.spacing3),
        verticalAlignment = Alignment.CenterVertically
    ) {
        PropelIconButton(
            icon = Icons.Outlined.ArrowBack,
            onClick = onNavigateBack,
            style = PropelButtonStyle.Ghost
        )

        Text(
            text = title,
            style = MaterialTheme.typography.titleLarge,
            fontWeight = FontWeight.Bold,
            color = TextPrimary
        )
    }
}

@Composable
private fun SettingsSection(
    title: String,
    content: @Composable ColumnScope.() -> Unit
) {
    Column(verticalArrangement = Arrangement.spacedBy(TaNaMaoDimens.spacing2)) {
        Text(
            text = title,
            style = MaterialTheme.typography.labelMedium,
            color = TextTertiary,
            modifier = Modifier.padding(start = TaNaMaoDimens.spacing1)
        )

        PropelCard(
            modifier = Modifier.fillMaxWidth(),
            elevation = PropelCardElevation.Flat,
            contentPadding = PaddingValues(0.dp)
        ) {
            Column {
                content()
            }
        }
    }
}

@Composable
private fun SettingsSwitch(
    icon: ImageVector,
    title: String,
    description: String,
    checked: Boolean,
    onCheckedChange: (Boolean) -> Unit
) {
    Row(
        modifier = Modifier
            .fillMaxWidth()
            .padding(TaNaMaoDimens.cardPadding),
        horizontalArrangement = Arrangement.spacedBy(TaNaMaoDimens.spacing3),
        verticalAlignment = Alignment.CenterVertically
    ) {
        Icon(
            imageVector = icon,
            contentDescription = null,
            tint = if (checked) AccentOrange else TextTertiary,
            modifier = Modifier.size(24.dp)
        )

        Column(modifier = Modifier.weight(1f)) {
            Text(
                text = title,
                style = MaterialTheme.typography.bodyMedium,
                fontWeight = FontWeight.Medium,
                color = TextPrimary
            )
            Text(
                text = description,
                style = MaterialTheme.typography.bodySmall,
                color = TextSecondary
            )
        }

        Switch(
            checked = checked,
            onCheckedChange = onCheckedChange,
            colors = SwitchDefaults.colors(
                checkedThumbColor = AccentOrange,
                checkedTrackColor = AccentOrangeSubtle,
                uncheckedThumbColor = TextTertiary,
                uncheckedTrackColor = BackgroundElevated
            )
        )
    }
}

@Composable
private fun SettingsItem(
    icon: ImageVector,
    title: String,
    description: String,
    onClick: () -> Unit,
    isDestructive: Boolean = false
) {
    Row(
        modifier = Modifier
            .fillMaxWidth()
            .clip(RoundedCornerShape(0.dp))
            .clickable(onClick = onClick)
            .padding(TaNaMaoDimens.cardPadding),
        horizontalArrangement = Arrangement.spacedBy(TaNaMaoDimens.spacing3),
        verticalAlignment = Alignment.CenterVertically
    ) {
        Icon(
            imageVector = icon,
            contentDescription = null,
            tint = if (isDestructive) Error else TextSecondary,
            modifier = Modifier.size(24.dp)
        )

        Column(modifier = Modifier.weight(1f)) {
            Text(
                text = title,
                style = MaterialTheme.typography.bodyMedium,
                fontWeight = FontWeight.Medium,
                color = if (isDestructive) Error else TextPrimary
            )
            Text(
                text = description,
                style = MaterialTheme.typography.bodySmall,
                color = TextSecondary
            )
        }

        Icon(
            imageVector = Icons.Outlined.ChevronRight,
            contentDescription = null,
            tint = TextTertiary,
            modifier = Modifier.size(20.dp)
        )
    }
}

@Composable
private fun LGPDInfoCard() {
    Row(
        modifier = Modifier
            .fillMaxWidth()
            .clip(RoundedCornerShape(TaNaMaoDimens.cardRadius))
            .background(Info.copy(alpha = 0.1f))
            .padding(TaNaMaoDimens.cardPadding),
        horizontalArrangement = Arrangement.spacedBy(TaNaMaoDimens.spacing3)
    ) {
        Icon(
            imageVector = Icons.Filled.Info,
            contentDescription = null,
            tint = Info,
            modifier = Modifier.size(24.dp)
        )

        Column(modifier = Modifier.weight(1f)) {
            Text(
                text = "Seus direitos (LGPD)",
                style = MaterialTheme.typography.titleSmall,
                fontWeight = FontWeight.SemiBold,
                color = TextPrimary
            )
            Text(
                text = "Você tem direito a acessar, corrigir, portar e excluir seus dados pessoais. Entre em contato pelo suporte para exercer seus direitos.",
                style = MaterialTheme.typography.bodySmall,
                color = TextSecondary
            )
        }
    }
}
