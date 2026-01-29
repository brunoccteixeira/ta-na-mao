package br.gov.tanamao.presentation.ui.consent

import androidx.compose.animation.*
import androidx.compose.foundation.background
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
import androidx.compose.ui.text.style.TextAlign
import androidx.compose.ui.unit.dp
import br.gov.tanamao.presentation.components.*
import br.gov.tanamao.presentation.theme.*

/**
 * LGPD Consent Screen
 * Shown on first launch or when consent version is updated
 */
@Composable
fun ConsentScreen(
    onAccept: () -> Unit,
    onDecline: () -> Unit
) {
    var showDetails by remember { mutableStateOf(false) }
    var acceptedTerms by remember { mutableStateOf(false) }
    var acceptedPrivacy by remember { mutableStateOf(false) }

    val canProceed = acceptedTerms && acceptedPrivacy

    Box(
        modifier = Modifier
            .fillMaxSize()
            .background(BackgroundPrimary)
    ) {
        Column(
            modifier = Modifier
                .fillMaxSize()
                .verticalScroll(rememberScrollState())
                .padding(TaNaMaoDimens.screenPaddingHorizontal)
                .statusBarsPadding()
        ) {
            Spacer(modifier = Modifier.height(TaNaMaoDimens.spacing6))

            // Logo and title
            Column(
                modifier = Modifier.fillMaxWidth(),
                horizontalAlignment = Alignment.CenterHorizontally
            ) {
                Box(
                    modifier = Modifier
                        .size(80.dp)
                        .clip(RoundedCornerShape(20.dp))
                        .background(AccentOrangeSubtle),
                    contentAlignment = Alignment.Center
                ) {
                    Icon(
                        imageVector = Icons.Filled.Security,
                        contentDescription = null,
                        tint = AccentOrange,
                        modifier = Modifier.size(44.dp)
                    )
                }

                Spacer(modifier = Modifier.height(TaNaMaoDimens.spacing4))

                Text(
                    text = "Sua privacidade importa",
                    style = MaterialTheme.typography.headlineSmall,
                    fontWeight = FontWeight.Bold,
                    color = TextPrimary,
                    textAlign = TextAlign.Center
                )

                Spacer(modifier = Modifier.height(TaNaMaoDimens.spacing2))

                Text(
                    text = "Antes de começar, precisamos do seu consentimento para processar seus dados de acordo com a LGPD.",
                    style = MaterialTheme.typography.bodyMedium,
                    color = TextSecondary,
                    textAlign = TextAlign.Center
                )
            }

            Spacer(modifier = Modifier.height(TaNaMaoDimens.spacing6))

            // Data usage cards
            Column(verticalArrangement = Arrangement.spacedBy(TaNaMaoDimens.spacing3)) {
                DataUsageCard(
                    icon = Icons.Filled.Person,
                    title = "Dados pessoais",
                    description = "CPF, NIS e cadastro no governo para saber se você tem direito"
                )

                DataUsageCard(
                    icon = Icons.Filled.LocationOn,
                    title = "Localização",
                    description = "Para encontrar pontos de atendimento próximos (opcional)"
                )

                DataUsageCard(
                    icon = Icons.Filled.Notifications,
                    title = "Notificações",
                    description = "Alertas sobre pagamentos e novos benefícios"
                )
            }

            Spacer(modifier = Modifier.height(TaNaMaoDimens.spacing4))

            // Expandable details
            PropelCard(
                modifier = Modifier.fillMaxWidth(),
                onClick = { showDetails = !showDetails },
                elevation = PropelCardElevation.Flat
            ) {
                Column {
                    Row(
                        modifier = Modifier.fillMaxWidth(),
                        horizontalArrangement = Arrangement.SpaceBetween,
                        verticalAlignment = Alignment.CenterVertically
                    ) {
                        Text(
                            text = "Ver detalhes completos",
                            style = MaterialTheme.typography.bodyMedium,
                            fontWeight = FontWeight.Medium,
                            color = AccentOrange
                        )
                        Icon(
                            imageVector = if (showDetails) Icons.Filled.ExpandLess else Icons.Filled.ExpandMore,
                            contentDescription = null,
                            tint = AccentOrange
                        )
                    }

                    AnimatedVisibility(
                        visible = showDetails,
                        enter = expandVertically() + fadeIn(),
                        exit = shrinkVertically() + fadeOut()
                    ) {
                        Column(
                            modifier = Modifier.padding(top = TaNaMaoDimens.spacing3),
                            verticalArrangement = Arrangement.spacedBy(TaNaMaoDimens.spacing2)
                        ) {
                            DetailItem("Seus dados são criptografados em trânsito e em repouso")
                            DetailItem("Não compartilhamos dados com terceiros para fins comerciais")
                            DetailItem("Você pode solicitar a exclusão dos dados a qualquer momento")
                            DetailItem("Dados são usados só para ver se você tem direito a benefícios")
                            DetailItem("Conformidade total com a Lei Geral de Proteção de Dados (LGPD)")
                        }
                    }
                }
            }

            Spacer(modifier = Modifier.height(TaNaMaoDimens.spacing4))

            // Checkboxes
            Column(verticalArrangement = Arrangement.spacedBy(TaNaMaoDimens.spacing2)) {
                ConsentCheckbox(
                    checked = acceptedTerms,
                    onCheckedChange = { acceptedTerms = it },
                    label = "Li e aceito os Termos de Uso"
                )

                ConsentCheckbox(
                    checked = acceptedPrivacy,
                    onCheckedChange = { acceptedPrivacy = it },
                    label = "Li e aceito a Política de Privacidade"
                )
            }

            Spacer(modifier = Modifier.height(TaNaMaoDimens.spacing6))

            // Buttons
            Column(verticalArrangement = Arrangement.spacedBy(TaNaMaoDimens.spacing3)) {
                PropelButton(
                    text = "Aceitar e continuar",
                    onClick = onAccept,
                    style = PropelButtonStyle.Primary,
                    enabled = canProceed,
                    fullWidth = true,
                    leadingIcon = Icons.Filled.CheckCircle
                )

                PropelButton(
                    text = "Não aceito",
                    onClick = onDecline,
                    style = PropelButtonStyle.Ghost,
                    fullWidth = true
                )
            }

            Spacer(modifier = Modifier.height(TaNaMaoDimens.spacing4))

            // Security badge
            SecurityBadge(
                modifier = Modifier.align(Alignment.CenterHorizontally)
            )

            Spacer(modifier = Modifier.height(TaNaMaoDimens.bottomNavHeight))
        }
    }
}

@Composable
private fun DataUsageCard(
    icon: ImageVector,
    title: String,
    description: String
) {
    Row(
        modifier = Modifier
            .fillMaxWidth()
            .clip(RoundedCornerShape(TaNaMaoDimens.cardRadius))
            .background(BackgroundTertiary)
            .padding(TaNaMaoDimens.cardPadding),
        horizontalArrangement = Arrangement.spacedBy(TaNaMaoDimens.spacing3)
    ) {
        Box(
            modifier = Modifier
                .size(44.dp)
                .clip(RoundedCornerShape(12.dp))
                .background(AccentOrangeSubtle),
            contentAlignment = Alignment.Center
        ) {
            Icon(
                imageVector = icon,
                contentDescription = null,
                tint = AccentOrange,
                modifier = Modifier.size(24.dp)
            )
        }

        Column(modifier = Modifier.weight(1f)) {
            Text(
                text = title,
                style = MaterialTheme.typography.titleSmall,
                fontWeight = FontWeight.SemiBold,
                color = TextPrimary
            )
            Text(
                text = description,
                style = MaterialTheme.typography.bodySmall,
                color = TextSecondary
            )
        }
    }
}

@Composable
private fun DetailItem(text: String) {
    Row(
        horizontalArrangement = Arrangement.spacedBy(TaNaMaoDimens.spacing2),
        verticalAlignment = Alignment.Top
    ) {
        Icon(
            imageVector = Icons.Filled.Check,
            contentDescription = null,
            tint = StatusActive,
            modifier = Modifier.size(16.dp)
        )
        Text(
            text = text,
            style = MaterialTheme.typography.bodySmall,
            color = TextSecondary
        )
    }
}

@Composable
private fun ConsentCheckbox(
    checked: Boolean,
    onCheckedChange: (Boolean) -> Unit,
    label: String
) {
    Row(
        modifier = Modifier
            .fillMaxWidth()
            .clip(RoundedCornerShape(TaNaMaoDimens.cardRadiusSmall))
            .background(BackgroundTertiary)
            .padding(TaNaMaoDimens.spacing3),
        horizontalArrangement = Arrangement.spacedBy(TaNaMaoDimens.spacing2),
        verticalAlignment = Alignment.CenterVertically
    ) {
        Checkbox(
            checked = checked,
            onCheckedChange = onCheckedChange,
            colors = CheckboxDefaults.colors(
                checkedColor = AccentOrange,
                uncheckedColor = TextTertiary,
                checkmarkColor = TextOnAccent
            )
        )
        Text(
            text = label,
            style = MaterialTheme.typography.bodyMedium,
            color = TextPrimary,
            modifier = Modifier.weight(1f)
        )
        Icon(
            imageVector = Icons.Outlined.OpenInNew,
            contentDescription = "Abrir",
            tint = AccentOrange,
            modifier = Modifier.size(18.dp)
        )
    }
}

/**
 * Security badge component
 */
@Composable
fun SecurityBadge(modifier: Modifier = Modifier) {
    Row(
        modifier = modifier
            .clip(RoundedCornerShape(TaNaMaoDimens.chipRadius))
            .background(BackgroundTertiary)
            .padding(horizontal = TaNaMaoDimens.spacing3, vertical = TaNaMaoDimens.spacing2),
        horizontalArrangement = Arrangement.spacedBy(TaNaMaoDimens.spacing2),
        verticalAlignment = Alignment.CenterVertically
    ) {
        Icon(
            imageVector = Icons.Filled.VerifiedUser,
            contentDescription = null,
            tint = StatusActive,
            modifier = Modifier.size(16.dp)
        )
        Text(
            text = "Dados protegidos por criptografia",
            style = MaterialTheme.typography.labelSmall,
            color = TextSecondary
        )
    }
}
