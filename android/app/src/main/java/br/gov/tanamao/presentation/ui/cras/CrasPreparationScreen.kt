package br.gov.tanamao.presentation.ui.cras

import android.content.Intent
import androidx.compose.foundation.background
import androidx.compose.foundation.clickable
import androidx.compose.foundation.layout.*
import androidx.compose.foundation.lazy.LazyColumn
import androidx.compose.foundation.shape.RoundedCornerShape
import androidx.compose.material.icons.Icons
import androidx.compose.material.icons.filled.*
import androidx.compose.material.icons.outlined.*
import androidx.compose.material3.*
import androidx.compose.runtime.*
import androidx.compose.ui.Alignment
import androidx.compose.ui.Modifier
import androidx.compose.ui.draw.clip
import androidx.compose.ui.platform.LocalContext
import androidx.compose.ui.text.font.FontWeight
import androidx.compose.ui.unit.dp
import androidx.hilt.navigation.compose.hiltViewModel
import br.gov.tanamao.domain.model.DocumentItem
import br.gov.tanamao.presentation.components.*
import br.gov.tanamao.presentation.theme.TaNaMaoDimens

@OptIn(ExperimentalMaterial3Api::class)
@Composable
fun CrasPreparationScreen(
    program: String,
    onNavigateBack: () -> Unit,
    viewModel: CrasPreparationViewModel = hiltViewModel()
) {
    val context = LocalContext.current
    val uiState by viewModel.uiState.collectAsState()

    LaunchedEffect(program) {
        viewModel.prepareForCras(program)
    }

    Box(
        modifier = Modifier
            .fillMaxSize()
            .background(MaterialTheme.colorScheme.background)
    ) {
        Column(modifier = Modifier.fillMaxSize()) {
            // Top Bar
            CrasTopBar(
                onNavigateBack = onNavigateBack,
                program = program
            )

            LazyColumn(
                modifier = Modifier.fillMaxSize(),
                contentPadding = PaddingValues(horizontal = TaNaMaoDimens.screenPaddingHorizontal),
                verticalArrangement = Arrangement.spacedBy(TaNaMaoDimens.spacing4)
            ) {
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

                uiState.preparation?.let { preparation ->
                    // Checklist
                    item {
                        DocumentChecklistSection(
                            checklist = preparation.checklist,
                            documents = preparation.checklist.documents
                        )
                    }

                    // Estimated Time
                    item {
                        EstimatedTimeCard(
                            timeMinutes = preparation.estimatedTime
                        )
                    }

                    // Tips
                    if (preparation.tips.isNotEmpty()) {
                        item {
                            TipsSection(tips = preparation.tips)
                        }
                    }

                    // Share Checklist Button
                    item {
                        PropelButton(
                            text = "Compartilhar checklist",
                            leadingIcon = Icons.Outlined.Share,
                            onClick = {
                                viewModel.shareChecklist(context, preparation.checklist)
                            },
                            style = PropelButtonStyle.Secondary,
                            modifier = Modifier.fillMaxWidth()
                        )
                    }

                    // Form
                    preparation.form?.let { form ->
                        item {
                            FormSection(
                                form = form,
                                onGenerateForm = { viewModel.generateForm(program) },
                                onShareForm = { viewModel.shareForm(context, form) },
                                isGenerating = uiState.isGeneratingForm
                            )
                        }
                    } ?: item {
                        PropelButton(
                            text = "Gerar formulário pré-preenchido",
                            leadingIcon = Icons.Outlined.Description,
                            onClick = { viewModel.generateForm(program) },
                            style = PropelButtonStyle.Primary,
                            modifier = Modifier.fillMaxWidth()
                        )
                    }
                }

                // Error
                uiState.error?.let { error ->
                    item {
                        ErrorCard(message = error, onDismiss = { viewModel.clearError() })
                    }
                }
            }
        }
    }
}

@Composable
private fun CrasTopBar(
    onNavigateBack: () -> Unit,
    program: String
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
            text = "Preparação CRAS",
            style = MaterialTheme.typography.titleLarge,
            fontWeight = FontWeight.Bold,
            color = MaterialTheme.colorScheme.onBackground
        )

        Spacer(modifier = Modifier.size(48.dp))
    }
}

@Composable
private fun DocumentChecklistSection(
    checklist: br.gov.tanamao.domain.model.DocumentChecklist,
    documents: List<DocumentItem>
) {
    PropelCard(
        elevation = PropelCardElevation.Standard,
        modifier = Modifier.fillMaxWidth()
    ) {
        Column(
            modifier = Modifier.fillMaxWidth(),
            verticalArrangement = Arrangement.spacedBy(TaNaMaoDimens.spacing3)
        ) {
            Text(
                text = checklist.title,
                style = MaterialTheme.typography.titleMedium,
                fontWeight = FontWeight.Bold,
                color = MaterialTheme.colorScheme.onSurface
            )

            Text(
                text = "${checklist.totalDocuments} documentos • ${checklist.estimatedTime} min",
                style = MaterialTheme.typography.bodySmall,
                color = MaterialTheme.colorScheme.onSurfaceVariant
            )

            documents.forEach { document ->
                DocumentItemRow(document = document)
            }
        }
    }
}

@Composable
private fun DocumentItemRow(document: DocumentItem) {
    Row(
        modifier = Modifier
            .fillMaxWidth()
            .clip(RoundedCornerShape(TaNaMaoDimens.cardRadiusSmall))
            .background(MaterialTheme.colorScheme.surfaceVariant)
            .padding(TaNaMaoDimens.spacing3),
        horizontalArrangement = Arrangement.spacedBy(TaNaMaoDimens.spacing2),
        verticalAlignment = Alignment.CenterVertically
    ) {
        Checkbox(
            checked = document.isProvided,
            onCheckedChange = null, // Read-only for now
            colors = CheckboxDefaults.colors(
                checkedColor = MaterialTheme.colorScheme.primary
            )
        )
        Column(modifier = Modifier.weight(1f)) {
            Text(
                text = document.name,
                style = MaterialTheme.typography.bodyMedium,
                fontWeight = if (document.isRequired) FontWeight.SemiBold else FontWeight.Normal,
                color = MaterialTheme.colorScheme.onSurface
            )
            document.description?.let {
                Text(
                    text = it,
                    style = MaterialTheme.typography.bodySmall,
                    color = MaterialTheme.colorScheme.onSurfaceVariant
                )
            }
        }
    }
}

@Composable
private fun EstimatedTimeCard(timeMinutes: Int) {
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
                imageVector = Icons.Outlined.Schedule,
                contentDescription = null,
                tint = MaterialTheme.colorScheme.primary,
                modifier = Modifier.size(24.dp)
            )
            Column {
                Text(
                    text = "Tempo estimado",
                    style = MaterialTheme.typography.bodySmall,
                    color = MaterialTheme.colorScheme.onSurfaceVariant
                )
                Text(
                    text = "$timeMinutes minutos",
                    style = MaterialTheme.typography.titleMedium,
                    fontWeight = FontWeight.Bold,
                    color = MaterialTheme.colorScheme.onSurface
                )
            }
        }
    }
}

@Composable
private fun TipsSection(tips: List<String>) {
    PropelCard(
        elevation = PropelCardElevation.Standard,
        modifier = Modifier.fillMaxWidth()
    ) {
        Column(
            modifier = Modifier.fillMaxWidth(),
            verticalArrangement = Arrangement.spacedBy(TaNaMaoDimens.spacing3)
        ) {
            Text(
                text = "Dicas",
                style = MaterialTheme.typography.titleMedium,
                fontWeight = FontWeight.Bold,
                color = MaterialTheme.colorScheme.onSurface
            )

            tips.forEach { tip ->
                Row(
                    modifier = Modifier.fillMaxWidth(),
                    horizontalArrangement = Arrangement.spacedBy(TaNaMaoDimens.spacing2),
                    verticalAlignment = Alignment.Top
                ) {
                    Icon(
                        imageVector = Icons.Outlined.Info,
                        contentDescription = null,
                        tint = MaterialTheme.colorScheme.primary,
                        modifier = Modifier.size(18.dp)
                    )
                    Text(
                        text = tip,
                        style = MaterialTheme.typography.bodyMedium,
                        color = MaterialTheme.colorScheme.onSurface,
                        modifier = Modifier.weight(1f)
                    )
                }
            }
        }
    }
}

@Composable
private fun FormSection(
    form: br.gov.tanamao.domain.model.PreFilledForm,
    onGenerateForm: () -> Unit,
    onShareForm: () -> Unit,
    isGenerating: Boolean
) {
    PropelCard(
        elevation = PropelCardElevation.Standard,
        modifier = Modifier.fillMaxWidth()
    ) {
        Column(
            modifier = Modifier.fillMaxWidth(),
            verticalArrangement = Arrangement.spacedBy(TaNaMaoDimens.spacing3)
        ) {
            Text(
                text = form.title,
                style = MaterialTheme.typography.titleMedium,
                fontWeight = FontWeight.Bold,
                color = MaterialTheme.colorScheme.onSurface
            )

            form.fields.forEach { field ->
                OutlinedTextField(
                    value = field.value ?: "",
                    onValueChange = {}, // Read-only for now
                    label = { Text(field.label) },
                    placeholder = { Text(field.placeholder ?: "") },
                    enabled = false,
                    modifier = Modifier.fillMaxWidth()
                )
            }

            if (form.printableText != null) {
                PropelButton(
                    text = "Compartilhar formulário",
                    leadingIcon = Icons.Outlined.Share,
                    onClick = onShareForm,
                    style = PropelButtonStyle.Secondary,
                    modifier = Modifier.fillMaxWidth()
                )
            }
        }
    }
}

@Composable
private fun ErrorCard(message: String, onDismiss: () -> Unit) {
    PropelCard(
        elevation = PropelCardElevation.Standard,
        modifier = Modifier.fillMaxWidth()
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
                    imageVector = Icons.Outlined.Error,
                    contentDescription = null,
                    tint = MaterialTheme.colorScheme.error,
                    modifier = Modifier.size(24.dp)
                )
                Text(
                    text = message,
                    style = MaterialTheme.typography.bodyMedium,
                    color = MaterialTheme.colorScheme.error,
                    modifier = Modifier.weight(1f)
                )
            }
            IconButton(onClick = onDismiss) {
                Icon(
                    imageVector = Icons.Outlined.Close,
                    contentDescription = "Fechar",
                    tint = MaterialTheme.colorScheme.onSurfaceVariant
                )
            }
        }
    }
}

