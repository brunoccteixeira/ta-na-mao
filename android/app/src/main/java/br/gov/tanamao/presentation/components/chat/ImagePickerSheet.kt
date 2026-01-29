package br.gov.tanamao.presentation.components.chat

import androidx.compose.foundation.background
import androidx.compose.foundation.clickable
import androidx.compose.foundation.layout.*
import androidx.compose.foundation.shape.RoundedCornerShape
import androidx.compose.material.icons.Icons
import androidx.compose.material.icons.filled.*
import androidx.compose.material3.*
import androidx.compose.runtime.*
import androidx.compose.ui.Alignment
import androidx.compose.ui.Modifier
import androidx.compose.ui.draw.clip
import androidx.compose.ui.graphics.vector.ImageVector
import androidx.compose.ui.text.font.FontWeight
import androidx.compose.ui.unit.dp
import br.gov.tanamao.presentation.theme.TaNaMaoDimens

/**
 * Bottom sheet for selecting image source (camera or gallery)
 */
@OptIn(ExperimentalMaterial3Api::class)
@Composable
fun ImagePickerSheet(
    onDismiss: () -> Unit,
    onCameraClick: () -> Unit,
    onGalleryClick: () -> Unit,
    modifier: Modifier = Modifier
) {
    ModalBottomSheet(
        onDismissRequest = onDismiss,
        sheetState = rememberModalBottomSheetState(),
        containerColor = MaterialTheme.colorScheme.surfaceVariant,
        dragHandle = {
            Box(
                modifier = Modifier
                    .padding(vertical = TaNaMaoDimens.spacing3)
                    .width(40.dp)
                    .height(4.dp)
                    .clip(RoundedCornerShape(2.dp))
                    .background(MaterialTheme.colorScheme.onSurfaceVariant)
            )
        },
        modifier = modifier
    ) {
        Column(
            modifier = Modifier
                .fillMaxWidth()
                .padding(
                    start = TaNaMaoDimens.spacing4,
                    end = TaNaMaoDimens.spacing4,
                    bottom = TaNaMaoDimens.spacing6
                ),
            verticalArrangement = Arrangement.spacedBy(TaNaMaoDimens.spacing3)
        ) {
            // Title
            Text(
                text = "Enviar receita médica",
                style = MaterialTheme.typography.titleMedium,
                fontWeight = FontWeight.SemiBold,
                color = MaterialTheme.colorScheme.onSurface,
                modifier = Modifier.padding(bottom = TaNaMaoDimens.spacing2)
            )

            // Camera option
            ImagePickerOption(
                icon = Icons.Filled.CameraAlt,
                title = "Tirar foto",
                description = "Usar a câmera para fotografar a receita",
                onClick = {
                    onDismiss()
                    onCameraClick()
                }
            )

            // Gallery option
            ImagePickerOption(
                icon = Icons.Filled.PhotoLibrary,
                title = "Escolher da galeria",
                description = "Selecionar uma foto existente",
                onClick = {
                    onDismiss()
                    onGalleryClick()
                }
            )

            // Info text
            Row(
                modifier = Modifier
                    .fillMaxWidth()
                    .padding(top = TaNaMaoDimens.spacing2)
                    .clip(RoundedCornerShape(TaNaMaoDimens.cardRadiusSmall))
                    .background(MaterialTheme.colorScheme.primaryContainer)
                    .padding(TaNaMaoDimens.spacing3),
                horizontalArrangement = Arrangement.spacedBy(TaNaMaoDimens.spacing2)
            ) {
                Icon(
                    imageVector = Icons.Filled.Info,
                    contentDescription = null,
                    tint = MaterialTheme.colorScheme.primary,
                    modifier = Modifier.size(20.dp)
                )
                Text(
                    text = "A foto da receita será processada para identificar os medicamentos e verificar disponibilidade no Farmácia Popular.",
                    style = MaterialTheme.typography.bodySmall,
                    color = MaterialTheme.colorScheme.onSurfaceVariant
                )
            }
        }
    }
}

@Composable
private fun ImagePickerOption(
    icon: ImageVector,
    title: String,
    description: String,
    onClick: () -> Unit
) {
    Row(
        modifier = Modifier
            .fillMaxWidth()
            .clip(RoundedCornerShape(TaNaMaoDimens.cardRadius))
            .background(MaterialTheme.colorScheme.surface)
            .clickable(onClick = onClick)
            .padding(TaNaMaoDimens.cardPadding),
        horizontalArrangement = Arrangement.spacedBy(TaNaMaoDimens.spacing3),
        verticalAlignment = Alignment.CenterVertically
    ) {
        Box(
            modifier = Modifier
                .size(48.dp)
                .clip(RoundedCornerShape(12.dp))
                .background(MaterialTheme.colorScheme.primaryContainer),
            contentAlignment = Alignment.Center
        ) {
            Icon(
                imageVector = icon,
                contentDescription = null,
                tint = MaterialTheme.colorScheme.primary,
                modifier = Modifier.size(24.dp)
            )
        }

        Column(modifier = Modifier.weight(1f)) {
            Text(
                text = title,
                style = MaterialTheme.typography.bodyLarge,
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
            imageVector = Icons.Filled.ChevronRight,
            contentDescription = null,
            tint = MaterialTheme.colorScheme.onSurfaceVariant,
            modifier = Modifier.size(24.dp)
        )
    }
}

/**
 * Compact attachment button for the chat input - camera icon for prescription
 */
@Composable
fun AttachmentButton(
    onClick: () -> Unit,
    modifier: Modifier = Modifier
) {
    Box(
        modifier = modifier
            .size(48.dp)
            .clip(RoundedCornerShape(24.dp))
            .background(MaterialTheme.colorScheme.primaryContainer)
            .clickable(onClick = onClick),
        contentAlignment = Alignment.Center
    ) {
        Icon(
            imageVector = Icons.Filled.CameraAlt,
            contentDescription = "Enviar receita médica",
            tint = MaterialTheme.colorScheme.primary,
            modifier = Modifier.size(24.dp)
        )
    }
}

/**
 * Preview of selected image before sending
 */
@Composable
fun ImagePreviewBar(
    imageBase64: String?,
    onRemove: () -> Unit,
    modifier: Modifier = Modifier
) {
    if (imageBase64 == null) return

    Row(
        modifier = modifier
            .fillMaxWidth()
            .background(MaterialTheme.colorScheme.surfaceVariant)
            .padding(TaNaMaoDimens.spacing2),
        horizontalArrangement = Arrangement.spacedBy(TaNaMaoDimens.spacing2),
        verticalAlignment = Alignment.CenterVertically
    ) {
        // Thumbnail
        Box(
            modifier = Modifier
                .size(48.dp)
                .clip(RoundedCornerShape(8.dp))
                .background(MaterialTheme.colorScheme.surface),
            contentAlignment = Alignment.Center
        ) {
            Icon(
                imageVector = Icons.Filled.Image,
                contentDescription = null,
                tint = MaterialTheme.colorScheme.primary,
                modifier = Modifier.size(24.dp)
            )
        }

        // Info
        Column(modifier = Modifier.weight(1f)) {
            Text(
                text = "Receita médica",
                style = MaterialTheme.typography.bodyMedium,
                fontWeight = FontWeight.Medium,
                color = MaterialTheme.colorScheme.onSurface
            )
            Text(
                text = "Pronta para enviar",
                style = MaterialTheme.typography.bodySmall,
                color = MaterialTheme.colorScheme.onSurfaceVariant
            )
        }

        // Remove button
        IconButton(
            onClick = onRemove,
            modifier = Modifier.size(32.dp)
        ) {
            Icon(
                imageVector = Icons.Filled.Close,
                contentDescription = "Remover",
                tint = MaterialTheme.colorScheme.onSurfaceVariant,
                modifier = Modifier.size(20.dp)
            )
        }
    }
}
