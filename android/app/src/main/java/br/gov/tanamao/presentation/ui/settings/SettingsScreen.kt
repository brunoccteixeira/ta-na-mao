package br.gov.tanamao.presentation.ui.settings

import androidx.compose.foundation.background
import androidx.compose.foundation.clickable
import androidx.compose.foundation.layout.*
import androidx.compose.foundation.shape.RoundedCornerShape
import androidx.compose.material.icons.Icons
import androidx.compose.material.icons.automirrored.outlined.ArrowBack
import androidx.compose.material.icons.outlined.*
import androidx.compose.material3.*
import androidx.compose.runtime.*
import androidx.compose.ui.Alignment
import androidx.compose.ui.Modifier
import androidx.compose.ui.draw.clip
import androidx.compose.ui.text.font.FontWeight
import androidx.compose.ui.unit.dp
import androidx.hilt.navigation.compose.hiltViewModel
import br.gov.tanamao.data.preferences.ThemeMode
import br.gov.tanamao.presentation.components.PropelButtonStyle
import br.gov.tanamao.presentation.components.PropelIconButton
import br.gov.tanamao.presentation.theme.TaNaMaoDimens

@Composable
fun SettingsScreen(
    onNavigateBack: () -> Unit,
    viewModel: SettingsViewModel = hiltViewModel()
) {
    val themeMode by viewModel.themeMode.collectAsState()

    Box(
        modifier = Modifier
            .fillMaxSize()
            .background(MaterialTheme.colorScheme.background)
    ) {
        Column(modifier = Modifier.fillMaxSize()) {
            // Top Bar
            SettingsTopBar(onNavigateBack = onNavigateBack)

            // Settings Content
            Column(
                modifier = Modifier
                    .fillMaxSize()
                    .padding(horizontal = TaNaMaoDimens.screenPaddingHorizontal),
                verticalArrangement = Arrangement.spacedBy(TaNaMaoDimens.spacing4)
            ) {
                // Theme Section
                SettingsSection(title = "Aparência") {
                    ThemeSelector(
                        selectedMode = themeMode,
                        onModeSelected = viewModel::setThemeMode
                    )
                }

                // App Info Section
                SettingsSection(title = "Sobre") {
                    SettingsInfoItem(
                        label = "Versão",
                        value = "1.0.0"
                    )
                    SettingsInfoItem(
                        label = "Desenvolvido por",
                        value = "Tá na Mão"
                    )
                }
            }
        }
    }
}

@Composable
private fun SettingsTopBar(onNavigateBack: () -> Unit) {
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
            icon = Icons.AutoMirrored.Outlined.ArrowBack,
            onClick = onNavigateBack,
            style = PropelButtonStyle.Ghost
        )

        Text(
            text = "Configurações",
            style = MaterialTheme.typography.titleLarge,
            fontWeight = FontWeight.Bold,
            color = MaterialTheme.colorScheme.onBackground
        )

        // Placeholder for symmetry
        Spacer(modifier = Modifier.size(48.dp))
    }
}

@Composable
private fun SettingsSection(
    title: String,
    content: @Composable ColumnScope.() -> Unit
) {
    Column(
        verticalArrangement = Arrangement.spacedBy(TaNaMaoDimens.spacing3)
    ) {
        Text(
            text = title,
            style = MaterialTheme.typography.titleMedium,
            fontWeight = FontWeight.SemiBold,
            color = MaterialTheme.colorScheme.onSurface
        )

        Column(
            modifier = Modifier
                .fillMaxWidth()
                .clip(RoundedCornerShape(TaNaMaoDimens.cardRadius))
                .background(MaterialTheme.colorScheme.surfaceVariant)
                .padding(TaNaMaoDimens.spacing4),
            verticalArrangement = Arrangement.spacedBy(TaNaMaoDimens.spacing3),
            content = content
        )
    }
}

@Composable
private fun ThemeSelector(
    selectedMode: ThemeMode,
    onModeSelected: (ThemeMode) -> Unit
) {
    Column(
        verticalArrangement = Arrangement.spacedBy(TaNaMaoDimens.spacing2)
    ) {
        Text(
            text = "Tema",
            style = MaterialTheme.typography.bodyMedium,
            fontWeight = FontWeight.Medium,
            color = MaterialTheme.colorScheme.onSurface
        )

        Row(
            modifier = Modifier.fillMaxWidth(),
            horizontalArrangement = Arrangement.spacedBy(TaNaMaoDimens.spacing2)
        ) {
            ThemeModeButton(
                icon = Icons.Outlined.PhoneAndroid,
                label = "Sistema",
                selected = selectedMode == ThemeMode.SYSTEM,
                onClick = { onModeSelected(ThemeMode.SYSTEM) },
                modifier = Modifier.weight(1f)
            )
            ThemeModeButton(
                icon = Icons.Outlined.LightMode,
                label = "Claro",
                selected = selectedMode == ThemeMode.LIGHT,
                onClick = { onModeSelected(ThemeMode.LIGHT) },
                modifier = Modifier.weight(1f)
            )
            ThemeModeButton(
                icon = Icons.Outlined.DarkMode,
                label = "Escuro",
                selected = selectedMode == ThemeMode.DARK,
                onClick = { onModeSelected(ThemeMode.DARK) },
                modifier = Modifier.weight(1f)
            )
        }
    }
}

@Composable
private fun ThemeModeButton(
    icon: androidx.compose.ui.graphics.vector.ImageVector,
    label: String,
    selected: Boolean,
    onClick: () -> Unit,
    modifier: Modifier = Modifier
) {
    val backgroundColor = if (selected) {
        MaterialTheme.colorScheme.primary
    } else {
        MaterialTheme.colorScheme.surface
    }
    val contentColor = if (selected) {
        MaterialTheme.colorScheme.onPrimary
    } else {
        MaterialTheme.colorScheme.onSurfaceVariant
    }

    Column(
        modifier = modifier
            .clip(RoundedCornerShape(TaNaMaoDimens.cardRadiusSmall))
            .background(backgroundColor)
            .clickable(onClick = onClick)
            .padding(TaNaMaoDimens.spacing3),
        horizontalAlignment = Alignment.CenterHorizontally,
        verticalArrangement = Arrangement.spacedBy(TaNaMaoDimens.spacing1)
    ) {
        Icon(
            imageVector = icon,
            contentDescription = label,
            tint = contentColor,
            modifier = Modifier.size(24.dp)
        )
        Text(
            text = label,
            style = MaterialTheme.typography.labelMedium,
            color = contentColor
        )
    }
}

@Composable
private fun SettingsInfoItem(
    label: String,
    value: String
) {
    Row(
        modifier = Modifier.fillMaxWidth(),
        horizontalArrangement = Arrangement.SpaceBetween,
        verticalAlignment = Alignment.CenterVertically
    ) {
        Text(
            text = label,
            style = MaterialTheme.typography.bodyMedium,
            color = MaterialTheme.colorScheme.onSurfaceVariant
        )
        Text(
            text = value,
            style = MaterialTheme.typography.bodyMedium,
            fontWeight = FontWeight.Medium,
            color = MaterialTheme.colorScheme.onSurface
        )
    }
}
