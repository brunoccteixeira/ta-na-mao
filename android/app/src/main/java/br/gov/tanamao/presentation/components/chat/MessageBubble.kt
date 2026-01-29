package br.gov.tanamao.presentation.components.chat

import android.graphics.BitmapFactory
import android.util.Base64
import androidx.compose.animation.*
import androidx.compose.foundation.Image
import androidx.compose.foundation.background
import androidx.compose.foundation.layout.*
import androidx.compose.foundation.shape.CircleShape
import androidx.compose.foundation.shape.RoundedCornerShape
import androidx.compose.material.icons.Icons
import androidx.compose.material.icons.filled.*
import androidx.compose.material3.*
import androidx.compose.runtime.*
import androidx.compose.ui.Alignment
import androidx.compose.ui.Modifier
import androidx.compose.ui.draw.clip
import androidx.compose.ui.graphics.Color
import androidx.compose.ui.graphics.asImageBitmap
import androidx.compose.ui.layout.ContentScale
import androidx.compose.ui.text.font.FontWeight
import androidx.compose.ui.unit.dp
import br.gov.tanamao.domain.model.*
import br.gov.tanamao.presentation.theme.Error
import br.gov.tanamao.presentation.theme.StatusActive
import br.gov.tanamao.presentation.theme.TaNaMaoDimens
import java.time.LocalDateTime
import java.time.format.DateTimeFormatter

/**
 * Chat message bubble component
 */
@Composable
fun MessageBubble(
    message: ChatMessage,
    modifier: Modifier = Modifier,
    onQuickReplyClick: ((QuickReplyOption) -> Unit)? = null,
    onEligibilityAction: ((String) -> Unit)? = null
) {
    val isUser = message.sender == MessageSender.USER
    val isSystem = message.sender == MessageSender.SYSTEM

    when (message.type) {
        MessageType.LOADING -> LoadingBubble(modifier)
        MessageType.QUICK_REPLIES -> {
            val metadata = message.metadata as? MessageMetadata.QuickReplies
            metadata?.let {
                QuickReplyChips(
                    options = it.options,
                    onOptionClick = { option -> onQuickReplyClick?.invoke(option) },
                    modifier = modifier
                )
            }
        }
        MessageType.ELIGIBILITY_RESULT -> {
            val metadata = message.metadata as? MessageMetadata.EligibilityResult
            metadata?.let {
                EligibilityResultCard(
                    result = it,
                    onAction = onEligibilityAction,
                    modifier = modifier
                )
            }
        }
        MessageType.DOCUMENT_LIST -> {
            val metadata = message.metadata as? MessageMetadata.DocumentList
            metadata?.let {
                DocumentListCard(
                    title = it.title,
                    documents = it.documents,
                    modifier = modifier
                )
            }
        }
        MessageType.LOCATION -> {
            val metadata = message.metadata as? MessageMetadata.LocationCard
            metadata?.let {
                LocationMapCard(
                    location = it,
                    modifier = modifier
                )
            }
        }
        MessageType.IMAGE -> {
            val metadata = message.metadata as? MessageMetadata.ImageData
            ImageMessageBubble(
                imageData = metadata,
                isUser = isUser,
                timestamp = message.timestamp,
                modifier = modifier
            )
        }
        else -> {
            Row(
                modifier = modifier
                    .fillMaxWidth()
                    .padding(vertical = TaNaMaoDimens.spacing1),
                horizontalArrangement = if (isUser) Arrangement.End else Arrangement.Start
            ) {
                if (!isUser && !isSystem) {
                    AssistantAvatar()
                    Spacer(modifier = Modifier.width(TaNaMaoDimens.spacing2))
                }

                Column(
                    modifier = Modifier.widthIn(max = 300.dp),
                    horizontalAlignment = if (isUser) Alignment.End else Alignment.Start
                ) {
                    Box(
                        modifier = Modifier
                            .clip(
                                RoundedCornerShape(
                                    topStart = 16.dp,
                                    topEnd = 16.dp,
                                    bottomStart = if (isUser) 16.dp else 4.dp,
                                    bottomEnd = if (isUser) 4.dp else 16.dp
                                )
                            )
                            .background(
                                when {
                                    isUser -> MaterialTheme.colorScheme.primary
                                    isSystem -> MaterialTheme.colorScheme.surfaceVariant
                                    else -> MaterialTheme.colorScheme.surface
                                }
                            )
                            .padding(
                                horizontal = TaNaMaoDimens.spacing3,
                                vertical = TaNaMaoDimens.spacing2
                            )
                    ) {
                        Text(
                            text = message.content,
                            style = MaterialTheme.typography.bodyMedium,
                            color = if (isUser) MaterialTheme.colorScheme.onPrimary else MaterialTheme.colorScheme.onSurface
                        )
                    }

                    // Timestamp
                    Text(
                        text = message.timestamp.format(DateTimeFormatter.ofPattern("HH:mm")),
                        style = MaterialTheme.typography.labelSmall,
                        color = MaterialTheme.colorScheme.onSurfaceVariant,
                        modifier = Modifier.padding(
                            top = TaNaMaoDimens.spacing1,
                            start = if (isUser) 0.dp else TaNaMaoDimens.spacing1,
                            end = if (isUser) TaNaMaoDimens.spacing1 else 0.dp
                        )
                    )
                }
            }
        }
    }
}

@Composable
private fun AssistantAvatar() {
    Box(
        modifier = Modifier
            .size(32.dp)
            .clip(CircleShape)
            .background(MaterialTheme.colorScheme.primaryContainer),
        contentAlignment = Alignment.Center
    ) {
        Icon(
            imageVector = Icons.Filled.SmartToy,
            contentDescription = "Assistente",
            tint = MaterialTheme.colorScheme.primary,
            modifier = Modifier.size(18.dp)
        )
    }
}

@Composable
private fun LoadingBubble(modifier: Modifier = Modifier) {
    Row(
        modifier = modifier
            .fillMaxWidth()
            .padding(vertical = TaNaMaoDimens.spacing1),
        horizontalArrangement = Arrangement.Start
    ) {
        AssistantAvatar()
        Spacer(modifier = Modifier.width(TaNaMaoDimens.spacing2))

        Box(
            modifier = Modifier
                .clip(RoundedCornerShape(16.dp))
                .background(MaterialTheme.colorScheme.surface)
                .padding(
                    horizontal = TaNaMaoDimens.spacing4,
                    vertical = TaNaMaoDimens.spacing3
                )
        ) {
            TypingIndicator()
        }
    }
}

@Composable
private fun TypingIndicator() {
    var dotIndex by remember { mutableIntStateOf(0) }

    LaunchedEffect(Unit) {
        while (true) {
            kotlinx.coroutines.delay(300)
            dotIndex = (dotIndex + 1) % 4
        }
    }

    Row(
        horizontalArrangement = Arrangement.spacedBy(4.dp),
        verticalAlignment = Alignment.CenterVertically
    ) {
        repeat(3) { index ->
            val isActive = index <= dotIndex % 3
            Box(
                modifier = Modifier
                    .size(8.dp)
                    .clip(CircleShape)
                    .background(
                        if (isActive) MaterialTheme.colorScheme.primary else MaterialTheme.colorScheme.onSurfaceVariant
                    )
            )
        }
    }
}

@Composable
private fun DocumentListCard(
    title: String,
    documents: List<DocumentItem>,
    modifier: Modifier = Modifier
) {
    Column(
        modifier = modifier
            .fillMaxWidth()
            .padding(vertical = TaNaMaoDimens.spacing2)
    ) {
        Row(
            modifier = Modifier.padding(start = 40.dp),
            verticalAlignment = Alignment.CenterVertically
        ) {
            AssistantAvatar()
            Spacer(modifier = Modifier.width(TaNaMaoDimens.spacing2))
        }

        Spacer(modifier = Modifier.height(TaNaMaoDimens.spacing2))

        Column(
            modifier = Modifier
                .padding(start = 40.dp)
                .fillMaxWidth()
                .clip(RoundedCornerShape(TaNaMaoDimens.cardRadius))
                .background(MaterialTheme.colorScheme.surfaceVariant)
                .padding(TaNaMaoDimens.cardPadding),
            verticalArrangement = Arrangement.spacedBy(TaNaMaoDimens.spacing3)
        ) {
            Row(
                horizontalArrangement = Arrangement.spacedBy(TaNaMaoDimens.spacing2),
                verticalAlignment = Alignment.CenterVertically
            ) {
                Icon(
                    imageVector = Icons.Filled.Description,
                    contentDescription = null,
                    tint = MaterialTheme.colorScheme.primary,
                    modifier = Modifier.size(24.dp)
                )
                Text(
                    text = title,
                    style = MaterialTheme.typography.titleSmall,
                    fontWeight = FontWeight.SemiBold,
                    color = MaterialTheme.colorScheme.onSurface
                )
            }

            documents.forEach { doc ->
                Row(
                    modifier = Modifier.fillMaxWidth(),
                    horizontalArrangement = Arrangement.spacedBy(TaNaMaoDimens.spacing2),
                    verticalAlignment = Alignment.CenterVertically
                ) {
                    Icon(
                        imageVector = if (doc.isProvided) Icons.Filled.CheckCircle else Icons.Filled.RadioButtonUnchecked,
                        contentDescription = null,
                        tint = if (doc.isProvided) StatusActive else MaterialTheme.colorScheme.onSurfaceVariant,
                        modifier = Modifier.size(20.dp)
                    )
                    Column(modifier = Modifier.weight(1f)) {
                        Row {
                            Text(
                                text = doc.name,
                                style = MaterialTheme.typography.bodyMedium,
                                color = MaterialTheme.colorScheme.onSurface
                            )
                            if (doc.isRequired) {
                                Text(
                                    text = " *",
                                    style = MaterialTheme.typography.bodyMedium,
                                    color = Error
                                )
                            }
                        }
                        doc.description?.let {
                            Text(
                                text = it,
                                style = MaterialTheme.typography.bodySmall,
                                color = MaterialTheme.colorScheme.onSurfaceVariant
                            )
                        }
                    }
                }
            }
        }
    }
}

/**
 * Image message bubble for prescription photos
 */
@Composable
private fun ImageMessageBubble(
    imageData: MessageMetadata.ImageData?,
    isUser: Boolean,
    timestamp: LocalDateTime,
    modifier: Modifier = Modifier
) {
    Row(
        modifier = modifier
            .fillMaxWidth()
            .padding(vertical = TaNaMaoDimens.spacing1),
        horizontalArrangement = if (isUser) Arrangement.End else Arrangement.Start
    ) {
        if (!isUser) {
            AssistantAvatar()
            Spacer(modifier = Modifier.width(TaNaMaoDimens.spacing2))
        }

        Column(
            modifier = Modifier.widthIn(max = 250.dp),
            horizontalAlignment = if (isUser) Alignment.End else Alignment.Start
        ) {
            Box(
                modifier = Modifier
                    .clip(RoundedCornerShape(TaNaMaoDimens.cardRadius))
                    .background(if (isUser) MaterialTheme.colorScheme.primary else MaterialTheme.colorScheme.surface)
                    .padding(TaNaMaoDimens.spacing1)
            ) {
                Column {
                    // Image preview
                    if (imageData != null) {
                        val bitmap = remember(imageData.base64) {
                            try {
                                val bytes = Base64.decode(imageData.base64, Base64.DEFAULT)
                                BitmapFactory.decodeByteArray(bytes, 0, bytes.size)?.asImageBitmap()
                            } catch (e: Exception) {
                                null
                            }
                        }

                        bitmap?.let {
                            Image(
                                bitmap = it,
                                contentDescription = "Receita médica",
                                modifier = Modifier
                                    .fillMaxWidth()
                                    .heightIn(max = 200.dp)
                                    .clip(RoundedCornerShape(TaNaMaoDimens.cardRadiusSmall)),
                                contentScale = ContentScale.Fit
                            )
                        } ?: run {
                            // Fallback if image can't be decoded
                            Box(
                                modifier = Modifier
                                    .fillMaxWidth()
                                    .height(100.dp)
                                    .clip(RoundedCornerShape(TaNaMaoDimens.cardRadiusSmall))
                                    .background(MaterialTheme.colorScheme.surfaceVariant),
                                contentAlignment = Alignment.Center
                            ) {
                                Icon(
                                    imageVector = Icons.Filled.Image,
                                    contentDescription = null,
                                    tint = MaterialTheme.colorScheme.onSurfaceVariant,
                                    modifier = Modifier.size(40.dp)
                                )
                            }
                        }
                    } else {
                        // Placeholder
                        Box(
                            modifier = Modifier
                                .fillMaxWidth()
                                .height(100.dp)
                                .clip(RoundedCornerShape(TaNaMaoDimens.cardRadiusSmall))
                                .background(MaterialTheme.colorScheme.surfaceVariant),
                            contentAlignment = Alignment.Center
                        ) {
                            Icon(
                                imageVector = Icons.Filled.Image,
                                contentDescription = null,
                                tint = MaterialTheme.colorScheme.onSurfaceVariant,
                                modifier = Modifier.size(40.dp)
                            )
                        }
                    }

                    // Caption if available
                    imageData?.caption?.let { caption ->
                        Text(
                            text = caption,
                            style = MaterialTheme.typography.bodySmall,
                            color = if (isUser) MaterialTheme.colorScheme.onPrimary else MaterialTheme.colorScheme.onSurface,
                            modifier = Modifier.padding(
                                top = TaNaMaoDimens.spacing2,
                                start = TaNaMaoDimens.spacing2,
                                end = TaNaMaoDimens.spacing2
                            )
                        )
                    }
                }
            }

            // Timestamp
            Text(
                text = timestamp.format(DateTimeFormatter.ofPattern("HH:mm")),
                style = MaterialTheme.typography.labelSmall,
                color = MaterialTheme.colorScheme.onSurfaceVariant,
                modifier = Modifier.padding(
                    top = TaNaMaoDimens.spacing1,
                    start = if (isUser) 0.dp else TaNaMaoDimens.spacing1,
                    end = if (isUser) TaNaMaoDimens.spacing1 else 0.dp
                )
            )
        }
    }
}
