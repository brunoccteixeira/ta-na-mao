package br.gov.tanamao.presentation.ui.benefit

import android.content.Intent
import android.net.Uri
import androidx.compose.animation.*
import androidx.compose.foundation.background
import androidx.compose.foundation.clickable
import androidx.compose.foundation.layout.*
import androidx.compose.foundation.lazy.LazyColumn
import androidx.compose.foundation.lazy.itemsIndexed
import androidx.compose.foundation.shape.CircleShape
import androidx.compose.foundation.shape.RoundedCornerShape
import androidx.compose.material.icons.Icons
import androidx.compose.material.icons.automirrored.filled.ArrowBack
import androidx.compose.material.icons.filled.*
import androidx.compose.material.icons.outlined.*
import androidx.compose.material3.*
import androidx.compose.runtime.*
import androidx.compose.ui.Alignment
import androidx.compose.ui.Modifier
import androidx.compose.ui.draw.clip
import androidx.compose.ui.graphics.Color
import androidx.compose.ui.graphics.vector.ImageVector
import androidx.compose.ui.platform.LocalContext
import androidx.compose.ui.text.font.FontWeight
import androidx.compose.ui.text.style.TextAlign
import androidx.compose.ui.unit.dp
import androidx.hilt.navigation.compose.hiltViewModel
import br.gov.tanamao.domain.model.*
import br.gov.tanamao.presentation.theme.*
import br.gov.tanamao.presentation.util.formatCurrency

@OptIn(ExperimentalMaterial3Api::class)
@Composable
fun BenefitDetailScreen(
    benefitId: String,
    onNavigateBack: () -> Unit,
    onNavigateToChat: (String) -> Unit = {},
    onNavigateToCras: (String) -> Unit = {},
    viewModel: BenefitDetailViewModel = hiltViewModel()
) {
    val uiState by viewModel.uiState.collectAsState()
    val context = LocalContext.current

    Scaffold(
        topBar = {
            TopAppBar(
                title = {
                    Text(
                        text = uiState.programName.ifEmpty { "Detalhes" },
                        style = MaterialTheme.typography.titleMedium
                    )
                },
                navigationIcon = {
                    IconButton(onClick = onNavigateBack) {
                        Icon(
                            imageVector = Icons.AutoMirrored.Filled.ArrowBack,
                            contentDescription = "Voltar"
                        )
                    }
                },
                colors = TopAppBarDefaults.topAppBarColors(
                    containerColor = BackgroundPrimary,
                    titleContentColor = TextPrimary
                )
            )
        },
        containerColor = BackgroundPrimary
    ) { paddingValues ->
        if (uiState.isLoading) {
            Box(
                modifier = Modifier
                    .fillMaxSize()
                    .padding(paddingValues),
                contentAlignment = Alignment.Center
            ) {
                CircularProgressIndicator(color = AccentOrange)
            }
        } else {
            LazyColumn(
                modifier = Modifier
                    .fillMaxSize()
                    .padding(paddingValues),
                contentPadding = PaddingValues(
                    horizontal = TaNaMaoDimens.screenPaddingHorizontal,
                    vertical = TaNaMaoDimens.spacing3
                ),
                verticalArrangement = Arrangement.spacedBy(TaNaMaoDimens.spacing4)
            ) {
                // Benefit Status Card
                item {
                    uiState.benefit?.let { benefit ->
                        BenefitStatusCard(benefit = benefit)
                    }
                }

                // Description Section
                item {
                    if (uiState.description.isNotEmpty()) {
                        SectionCard(
                            title = "Sobre o Programa",
                            icon = Icons.Outlined.Info
                        ) {
                            Text(
                                text = uiState.description,
                                style = MaterialTheme.typography.bodyMedium,
                                color = TextSecondary
                            )
                        }
                    }
                }

                // Requirements Section
                item {
                    if (uiState.requirements.isNotEmpty()) {
                        SectionCard(
                            title = "Requisitos",
                            icon = Icons.Outlined.CheckCircle
                        ) {
                            Column(
                                verticalArrangement = Arrangement.spacedBy(TaNaMaoDimens.spacing2)
                            ) {
                                uiState.requirements.forEach { requirement ->
                                    RequirementItem(text = requirement)
                                }
                            }
                        }
                    }
                }

                // Documents Section
                item {
                    if (uiState.documents.isNotEmpty()) {
                        SectionCard(
                            title = "Documentos Necessarios",
                            icon = Icons.Outlined.Description
                        ) {
                            Column(
                                verticalArrangement = Arrangement.spacedBy(TaNaMaoDimens.spacing2)
                            ) {
                                uiState.documents.forEach { document ->
                                    DocumentItem(text = document)
                                }
                            }
                        }
                    }
                }

                // How to Apply Section
                item {
                    if (uiState.howToApply.isNotEmpty()) {
                        SectionCard(
                            title = "Como Solicitar",
                            icon = Icons.Outlined.Assignment
                        ) {
                            Text(
                                text = uiState.howToApply,
                                style = MaterialTheme.typography.bodyMedium,
                                color = TextSecondary
                            )

                            Spacer(modifier = Modifier.height(TaNaMaoDimens.spacing3))

                            // Action buttons
                            Row(
                                modifier = Modifier.fillMaxWidth(),
                                horizontalArrangement = Arrangement.spacedBy(TaNaMaoDimens.spacing2)
                            ) {
                                ActionButton(
                                    text = "Buscar CRAS",
                                    icon = Icons.Outlined.LocationOn,
                                    modifier = Modifier.weight(1f),
                                    onClick = {
                                        onNavigateToChat("buscar CRAS perto de mim")
                                    }
                                )
                                ActionButton(
                                    text = "Tirar Duvidas",
                                    icon = Icons.Outlined.Chat,
                                    modifier = Modifier.weight(1f),
                                    onClick = {
                                        onNavigateToChat("como solicitar ${uiState.programName}")
                                    }
                                )
                            }
                        }
                    }
                }

                // Contacts Section
                item {
                    if (uiState.contacts.isNotEmpty()) {
                        SectionCard(
                            title = "Contatos Uteis",
                            icon = Icons.Outlined.Phone
                        ) {
                            Column(
                                verticalArrangement = Arrangement.spacedBy(TaNaMaoDimens.spacing2)
                            ) {
                                uiState.contacts.forEach { contact ->
                                    ContactItem(
                                        contact = contact,
                                        onClick = {
                                            when (contact.type) {
                                                ContactType.PHONE -> {
                                                    val intent = Intent(Intent.ACTION_DIAL).apply {
                                                        data = Uri.parse("tel:${contact.value}")
                                                    }
                                                    context.startActivity(intent)
                                                }
                                                ContactType.WEBSITE -> {
                                                    val intent = Intent(Intent.ACTION_VIEW).apply {
                                                        data = Uri.parse(contact.value)
                                                    }
                                                    context.startActivity(intent)
                                                }
                                                else -> {}
                                            }
                                        }
                                    )
                                }
                            }
                        }
                    }
                }

                // FAQ Section
                item {
                    if (uiState.faq.isNotEmpty()) {
                        SectionCard(
                            title = "Perguntas Frequentes",
                            icon = Icons.Outlined.QuestionAnswer
                        ) {
                            Column(
                                verticalArrangement = Arrangement.spacedBy(TaNaMaoDimens.spacing2)
                            ) {
                                uiState.faq.forEachIndexed { index, faqItem ->
                                    FaqItemCard(
                                        faqItem = faqItem,
                                        isExpanded = index in uiState.expandedFaqIndex,
                                        onClick = { viewModel.toggleFaqExpanded(index) }
                                    )
                                }
                            }
                        }
                    }
                }

                // Bottom spacer for navigation bar
                item {
                    Spacer(modifier = Modifier.height(80.dp))
                }
            }
        }

        // Error snackbar
        uiState.error?.let { error ->
            // Could show a snackbar here if needed
        }
    }
}

@Composable
private fun BenefitStatusCard(benefit: UserBenefit) {
    Card(
        modifier = Modifier.fillMaxWidth(),
        colors = CardDefaults.cardColors(
            containerColor = BackgroundTertiary
        ),
        shape = RoundedCornerShape(TaNaMaoDimens.cardRadius)
    ) {
        Column(
            modifier = Modifier.padding(TaNaMaoDimens.spacing4)
        ) {
            Row(
                modifier = Modifier.fillMaxWidth(),
                horizontalArrangement = Arrangement.SpaceBetween,
                verticalAlignment = Alignment.Top
            ) {
                Column(modifier = Modifier.weight(1f)) {
                    Text(
                        text = benefit.programName,
                        style = MaterialTheme.typography.titleLarge,
                        color = TextPrimary
                    )

                    Spacer(modifier = Modifier.height(TaNaMaoDimens.spacing1))

                    StatusBadge(status = benefit.status)
                }

                benefit.monthlyValue?.let { value ->
                    Column(horizontalAlignment = Alignment.End) {
                        Text(
                            text = "Valor mensal",
                            style = MaterialTheme.typography.bodySmall,
                            color = TextSecondary
                        )
                        Text(
                            text = value.formatAsCurrency(),
                            style = MaterialTheme.typography.headlineMedium,
                            color = AccentOrange,
                            fontWeight = FontWeight.Bold
                        )
                    }
                }
            }

            // Payment dates if available
            if (benefit.nextPaymentDate != null || benefit.lastPaymentDate != null) {
                Spacer(modifier = Modifier.height(TaNaMaoDimens.spacing3))
                HorizontalDivider(color = Divider)
                Spacer(modifier = Modifier.height(TaNaMaoDimens.spacing3))

                Row(
                    modifier = Modifier.fillMaxWidth(),
                    horizontalArrangement = Arrangement.SpaceEvenly
                ) {
                    benefit.lastPaymentDate?.let { date ->
                        PaymentDateInfo(
                            label = "Ultimo pagamento",
                            date = date.formatBrazilian()
                        )
                    }
                    benefit.nextPaymentDate?.let { date ->
                        PaymentDateInfo(
                            label = "Proximo pagamento",
                            date = date.formatBrazilian(),
                            isHighlighted = true
                        )
                    }
                }
            }
        }
    }
}

@Composable
private fun StatusBadge(status: BenefitStatus) {
    val (backgroundColor, textColor, text) = when (status) {
        BenefitStatus.ACTIVE -> Triple(
            AccentOrange.copy(alpha = 0.2f),
            AccentOrange,
            "Ativo"
        )
        BenefitStatus.PENDING -> Triple(
            Color(0xFFFFF3E0),
            Color(0xFFFF9800),
            "Pendente"
        )
        BenefitStatus.ELIGIBLE -> Triple(
            Color(0xFFE3F2FD),
            Color(0xFF2196F3),
            "Elegivel"
        )
        BenefitStatus.NOT_ELIGIBLE -> Triple(
            Color(0xFFFFEBEE),
            Color(0xFFF44336),
            "Nao Elegivel"
        )
        BenefitStatus.BLOCKED -> Triple(
            Color(0xFFFFEBEE),
            Color(0xFFF44336),
            "Bloqueado"
        )
    }

    Surface(
        color = backgroundColor,
        shape = RoundedCornerShape(4.dp)
    ) {
        Text(
            text = text,
            modifier = Modifier.padding(horizontal = 8.dp, vertical = 4.dp),
            style = MaterialTheme.typography.labelSmall,
            color = textColor,
            fontWeight = FontWeight.Medium
        )
    }
}

@Composable
private fun PaymentDateInfo(
    label: String,
    date: String,
    isHighlighted: Boolean = false
) {
    Column(horizontalAlignment = Alignment.CenterHorizontally) {
        Text(
            text = label,
            style = MaterialTheme.typography.bodySmall,
            color = TextSecondary
        )
        Text(
            text = date,
            style = MaterialTheme.typography.bodyMedium,
            color = if (isHighlighted) AccentOrange else TextPrimary,
            fontWeight = if (isHighlighted) FontWeight.Bold else FontWeight.Normal
        )
    }
}

@Composable
private fun SectionCard(
    title: String,
    icon: ImageVector,
    content: @Composable ColumnScope.() -> Unit
) {
    Card(
        modifier = Modifier.fillMaxWidth(),
        colors = CardDefaults.cardColors(
            containerColor = BackgroundTertiary
        ),
        shape = RoundedCornerShape(TaNaMaoDimens.cardRadius)
    ) {
        Column(
            modifier = Modifier.padding(TaNaMaoDimens.spacing4)
        ) {
            Row(
                verticalAlignment = Alignment.CenterVertically,
                modifier = Modifier.padding(bottom = TaNaMaoDimens.spacing3)
            ) {
                Icon(
                    imageVector = icon,
                    contentDescription = null,
                    tint = AccentOrange,
                    modifier = Modifier.size(24.dp)
                )
                Spacer(modifier = Modifier.width(TaNaMaoDimens.spacing2))
                Text(
                    text = title,
                    style = MaterialTheme.typography.titleMedium,
                    color = TextPrimary
                )
            }

            content()
        }
    }
}

@Composable
private fun RequirementItem(text: String) {
    Row(
        modifier = Modifier.fillMaxWidth(),
        verticalAlignment = Alignment.Top
    ) {
        Icon(
            imageVector = Icons.Default.CheckCircle,
            contentDescription = null,
            tint = Color(0xFF4CAF50),
            modifier = Modifier.size(20.dp)
        )
        Spacer(modifier = Modifier.width(TaNaMaoDimens.spacing2))
        Text(
            text = text,
            style = MaterialTheme.typography.bodyMedium,
            color = TextSecondary
        )
    }
}

@Composable
private fun DocumentItem(text: String) {
    Row(
        modifier = Modifier.fillMaxWidth(),
        verticalAlignment = Alignment.Top
    ) {
        Icon(
            imageVector = Icons.Outlined.Description,
            contentDescription = null,
            tint = AccentOrange,
            modifier = Modifier.size(20.dp)
        )
        Spacer(modifier = Modifier.width(TaNaMaoDimens.spacing2))
        Text(
            text = text,
            style = MaterialTheme.typography.bodyMedium,
            color = TextSecondary
        )
    }
}

@Composable
private fun ActionButton(
    text: String,
    icon: ImageVector,
    modifier: Modifier = Modifier,
    onClick: () -> Unit
) {
    OutlinedButton(
        onClick = onClick,
        modifier = modifier,
        colors = ButtonDefaults.outlinedButtonColors(
            contentColor = AccentOrange
        ),
        border = androidx.compose.foundation.BorderStroke(1.dp, AccentOrange)
    ) {
        Icon(
            imageVector = icon,
            contentDescription = null,
            modifier = Modifier.size(18.dp)
        )
        Spacer(modifier = Modifier.width(4.dp))
        Text(text = text, style = MaterialTheme.typography.labelMedium)
    }
}

@Composable
private fun ContactItem(
    contact: ContactInfo,
    onClick: () -> Unit
) {
    val icon = when (contact.type) {
        ContactType.PHONE -> Icons.Default.Phone
        ContactType.EMAIL -> Icons.Default.Email
        ContactType.WEBSITE -> Icons.Default.Language
        ContactType.ADDRESS -> Icons.Default.LocationOn
        ContactType.WHATSAPP -> Icons.Default.Chat
    }

    Row(
        modifier = Modifier
            .fillMaxWidth()
            .clip(RoundedCornerShape(8.dp))
            .clickable(onClick = onClick)
            .padding(TaNaMaoDimens.spacing2),
        verticalAlignment = Alignment.CenterVertically
    ) {
        Box(
            modifier = Modifier
                .size(40.dp)
                .background(AccentOrange.copy(alpha = 0.1f), CircleShape),
            contentAlignment = Alignment.Center
        ) {
            Icon(
                imageVector = icon,
                contentDescription = null,
                tint = AccentOrange,
                modifier = Modifier.size(20.dp)
            )
        }

        Spacer(modifier = Modifier.width(TaNaMaoDimens.spacing3))

        Column {
            contact.label?.let { label ->
                Text(
                    text = label,
                    style = MaterialTheme.typography.bodySmall,
                    color = TextSecondary
                )
            }
            Text(
                text = contact.value,
                style = MaterialTheme.typography.bodyMedium,
                color = AccentOrange
            )
        }
    }
}

@Composable
private fun FaqItemCard(
    faqItem: FaqItem,
    isExpanded: Boolean,
    onClick: () -> Unit
) {
    Surface(
        modifier = Modifier
            .fillMaxWidth()
            .clip(RoundedCornerShape(8.dp))
            .clickable(onClick = onClick),
        color = BackgroundSecondary
    ) {
        Column(
            modifier = Modifier.padding(TaNaMaoDimens.spacing3)
        ) {
            Row(
                modifier = Modifier.fillMaxWidth(),
                horizontalArrangement = Arrangement.SpaceBetween,
                verticalAlignment = Alignment.CenterVertically
            ) {
                Text(
                    text = faqItem.question,
                    style = MaterialTheme.typography.bodyMedium,
                    color = TextPrimary,
                    fontWeight = FontWeight.Medium,
                    modifier = Modifier.weight(1f)
                )
                Icon(
                    imageVector = if (isExpanded) Icons.Default.ExpandLess else Icons.Default.ExpandMore,
                    contentDescription = if (isExpanded) "Recolher" else "Expandir",
                    tint = TextSecondary
                )
            }

            AnimatedVisibility(visible = isExpanded) {
                Column {
                    Spacer(modifier = Modifier.height(TaNaMaoDimens.spacing2))
                    Text(
                        text = faqItem.answer,
                        style = MaterialTheme.typography.bodyMedium,
                        color = TextSecondary
                    )
                }
            }
        }
    }
}
