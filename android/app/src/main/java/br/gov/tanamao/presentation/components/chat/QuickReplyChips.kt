package br.gov.tanamao.presentation.components.chat

import androidx.compose.foundation.background
import androidx.compose.foundation.border
import androidx.compose.foundation.clickable
import androidx.compose.foundation.layout.*
import androidx.compose.foundation.lazy.LazyRow
import androidx.compose.foundation.lazy.items
import androidx.compose.foundation.shape.RoundedCornerShape
import androidx.compose.material.icons.Icons
import androidx.compose.material.icons.outlined.*
import androidx.compose.material3.*
import androidx.compose.runtime.Composable
import androidx.compose.ui.Alignment
import androidx.compose.ui.Modifier
import androidx.compose.ui.draw.clip
import androidx.compose.ui.graphics.vector.ImageVector
import androidx.compose.ui.unit.dp
import br.gov.tanamao.domain.model.QuickReplyOption
import br.gov.tanamao.presentation.theme.TaNaMaoDimens

/**
 * Quick reply chips for chat interaction
 */
@Composable
fun QuickReplyChips(
    options: List<QuickReplyOption>,
    onOptionClick: (QuickReplyOption) -> Unit,
    modifier: Modifier = Modifier
) {
    LazyRow(
        modifier = modifier
            .fillMaxWidth()
            .padding(vertical = TaNaMaoDimens.spacing2),
        horizontalArrangement = Arrangement.spacedBy(TaNaMaoDimens.spacing2),
        contentPadding = PaddingValues(horizontal = TaNaMaoDimens.spacing2)
    ) {
        items(options) { option ->
            QuickReplyChip(
                option = option,
                onClick = { onOptionClick(option) }
            )
        }
    }
}

@Composable
private fun QuickReplyChip(
    option: QuickReplyOption,
    onClick: () -> Unit
) {
    Row(
        modifier = Modifier
            .clip(RoundedCornerShape(TaNaMaoDimens.chipRadius))
            .border(
                width = 1.dp,
                color = MaterialTheme.colorScheme.primary,
                shape = RoundedCornerShape(TaNaMaoDimens.chipRadius)
            )
            .background(MaterialTheme.colorScheme.primary)
            .clickable(onClick = onClick)
            .padding(
                horizontal = TaNaMaoDimens.spacing3,
                vertical = TaNaMaoDimens.spacing2
            ),
        horizontalArrangement = Arrangement.spacedBy(TaNaMaoDimens.spacing2),
        verticalAlignment = Alignment.CenterVertically
    ) {
        option.icon?.let { iconName ->
            Icon(
                imageVector = getIconForName(iconName),
                contentDescription = null,
                tint = MaterialTheme.colorScheme.onPrimary,
                modifier = Modifier.size(18.dp)
            )
        }

        Text(
            text = option.label,
            style = MaterialTheme.typography.labelMedium,
            color = MaterialTheme.colorScheme.onPrimary
        )
    }
}

/**
 * Grid layout for quick replies
 */
@Composable
fun QuickReplyGrid(
    options: List<QuickReplyOption>,
    onOptionClick: (QuickReplyOption) -> Unit,
    modifier: Modifier = Modifier,
    columns: Int = 2
) {
    Column(
        modifier = modifier
            .fillMaxWidth()
            .padding(TaNaMaoDimens.spacing3),
        verticalArrangement = Arrangement.spacedBy(TaNaMaoDimens.spacing2)
    ) {
        options.chunked(columns).forEach { rowOptions ->
            Row(
                modifier = Modifier.fillMaxWidth(),
                horizontalArrangement = Arrangement.spacedBy(TaNaMaoDimens.spacing2)
            ) {
                rowOptions.forEach { option ->
                    QuickReplyCard(
                        option = option,
                        onClick = { onOptionClick(option) },
                        modifier = Modifier.weight(1f)
                    )
                }
                // Fill remaining space if odd number
                if (rowOptions.size < columns) {
                    repeat(columns - rowOptions.size) {
                        Spacer(modifier = Modifier.weight(1f))
                    }
                }
            }
        }
    }
}

@Composable
private fun QuickReplyCard(
    option: QuickReplyOption,
    onClick: () -> Unit,
    modifier: Modifier = Modifier
) {
    Box(
        modifier = modifier
            .clip(RoundedCornerShape(TaNaMaoDimens.cardRadius))
            .border(
                width = 1.dp,
                color = MaterialTheme.colorScheme.outline,
                shape = RoundedCornerShape(TaNaMaoDimens.cardRadius)
            )
            .background(MaterialTheme.colorScheme.surface)
            .clickable(onClick = onClick)
            .padding(TaNaMaoDimens.spacing3)
    ) {
        Row(
            horizontalArrangement = Arrangement.spacedBy(TaNaMaoDimens.spacing2),
            verticalAlignment = Alignment.CenterVertically
        ) {
            option.icon?.let { iconName ->
                Box(
                    modifier = Modifier
                        .size(36.dp)
                        .clip(RoundedCornerShape(8.dp))
                        .background(MaterialTheme.colorScheme.primaryContainer),
                    contentAlignment = Alignment.Center
                ) {
                    Icon(
                        imageVector = getIconForName(iconName),
                        contentDescription = null,
                        tint = MaterialTheme.colorScheme.primary,
                        modifier = Modifier.size(20.dp)
                    )
                }
            }

            Text(
                text = option.label,
                style = MaterialTheme.typography.bodyMedium,
                color = MaterialTheme.colorScheme.onSurface
            )
        }
    }
}

/**
 * Suggested questions chips
 */
@Composable
fun SuggestedQuestions(
    questions: List<String>,
    onQuestionClick: (String) -> Unit,
    modifier: Modifier = Modifier
) {
    Column(
        modifier = modifier
            .fillMaxWidth()
            .padding(TaNaMaoDimens.spacing2),
        verticalArrangement = Arrangement.spacedBy(TaNaMaoDimens.spacing2)
    ) {
        Text(
            text = "Perguntas frequentes",
            style = MaterialTheme.typography.labelSmall,
            color = MaterialTheme.colorScheme.onSurfaceVariant
        )

        questions.forEach { question ->
            SuggestedQuestionChip(
                question = question,
                onClick = { onQuestionClick(question) }
            )
        }
    }
}

@Composable
private fun SuggestedQuestionChip(
    question: String,
    onClick: () -> Unit
) {
    Row(
        modifier = Modifier
            .fillMaxWidth()
            .clip(RoundedCornerShape(TaNaMaoDimens.cardRadiusSmall))
            .background(MaterialTheme.colorScheme.surfaceVariant)
            .clickable(onClick = onClick)
            .padding(TaNaMaoDimens.spacing3),
        horizontalArrangement = Arrangement.spacedBy(TaNaMaoDimens.spacing2),
        verticalAlignment = Alignment.CenterVertically
    ) {
        Icon(
            imageVector = Icons.Outlined.HelpOutline,
            contentDescription = null,
            tint = MaterialTheme.colorScheme.primary,
            modifier = Modifier.size(18.dp)
        )
        Text(
            text = question,
            style = MaterialTheme.typography.bodyMedium,
            color = MaterialTheme.colorScheme.onSurfaceVariant
        )
    }
}

private fun getIconForName(name: String): ImageVector {
    return when (name.lowercase()) {
        "search" -> Icons.Outlined.Search
        "description", "document" -> Icons.Outlined.Description
        "location", "map" -> Icons.Outlined.LocationOn
        "help", "question" -> Icons.Outlined.HelpOutline
        "money", "payment" -> Icons.Outlined.AccountBalance
        "person", "profile" -> Icons.Outlined.Person
        "family" -> Icons.Outlined.FamilyRestroom
        "calendar" -> Icons.Outlined.CalendarToday
        "check" -> Icons.Outlined.CheckCircle
        "info" -> Icons.Outlined.Info
        "camera" -> Icons.Outlined.CameraAlt
        else -> Icons.Outlined.ArrowForward
    }
}
