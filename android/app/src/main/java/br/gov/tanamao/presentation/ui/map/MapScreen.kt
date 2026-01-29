package br.gov.tanamao.presentation.ui.map

import android.Manifest
import android.content.pm.PackageManager
import androidx.activity.compose.rememberLauncherForActivityResult
import androidx.activity.result.contract.ActivityResultContracts
import androidx.compose.foundation.background
import androidx.compose.foundation.clickable
import androidx.compose.foundation.layout.*
import androidx.compose.foundation.lazy.LazyColumn
import androidx.compose.foundation.lazy.items
import androidx.compose.foundation.shape.CircleShape
import androidx.compose.foundation.shape.RoundedCornerShape
import androidx.compose.material.icons.Icons
import androidx.compose.material.icons.automirrored.outlined.ArrowBack
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
import androidx.compose.ui.text.style.TextOverflow
import androidx.compose.ui.unit.dp
import androidx.core.content.ContextCompat
import androidx.hilt.navigation.compose.hiltViewModel
import br.gov.tanamao.presentation.components.PropelButton
import br.gov.tanamao.presentation.components.PropelButtonSize
import br.gov.tanamao.presentation.components.PropelButtonStyle
import br.gov.tanamao.presentation.theme.*
import com.google.android.gms.location.LocationServices

/**
 * Nearby Services Screen - Citizen focused
 * Shows pharmacies and CRAS (social assistance centers) nearby
 */
@OptIn(ExperimentalMaterial3Api::class)
@Composable
fun MapScreen(
    onNavigateToMunicipality: (String) -> Unit,
    onNavigateBack: () -> Unit,
    viewModel: MapViewModel = hiltViewModel()
) {
    val uiState by viewModel.uiState.collectAsState()
    val context = LocalContext.current

    // Location permission
    var hasLocationPermission by remember {
        mutableStateOf(
            ContextCompat.checkSelfPermission(
                context,
                Manifest.permission.ACCESS_FINE_LOCATION
            ) == PackageManager.PERMISSION_GRANTED
        )
    }

    val locationPermissionLauncher = rememberLauncherForActivityResult(
        contract = ActivityResultContracts.RequestPermission()
    ) { isGranted ->
        hasLocationPermission = isGranted
        if (isGranted) {
            // Get location and reload
            val fusedLocationClient = LocationServices.getFusedLocationProviderClient(context)
            try {
                fusedLocationClient.lastLocation.addOnSuccessListener { location ->
                    location?.let {
                        viewModel.setLocation(it.latitude, it.longitude)
                    }
                }
            } catch (e: SecurityException) {
                // Permission denied
            }
        }
    }

    // Request location on first load
    LaunchedEffect(hasLocationPermission) {
        if (hasLocationPermission) {
            val fusedLocationClient = LocationServices.getFusedLocationProviderClient(context)
            try {
                fusedLocationClient.lastLocation.addOnSuccessListener { location ->
                    location?.let {
                        viewModel.setLocation(it.latitude, it.longitude)
                    }
                }
            } catch (e: SecurityException) {
                // Permission denied
            }
        } else {
            locationPermissionLauncher.launch(Manifest.permission.ACCESS_FINE_LOCATION)
        }
    }

    Box(
        modifier = Modifier
            .fillMaxSize()
            .background(BackgroundPrimary)
    ) {
        Column(modifier = Modifier.fillMaxSize()) {
            // Top Bar
            NearbyTopBar(
                onNavigateBack = onNavigateBack,
                onRefresh = { viewModel.refresh() }
            )

            // Service Type Selector
            ServiceTypeSelector(
                selectedType = uiState.selectedServiceType,
                onTypeSelected = { viewModel.selectServiceType(it) },
                modifier = Modifier.padding(horizontal = TaNaMaoDimens.screenPaddingHorizontal)
            )

            Spacer(modifier = Modifier.height(TaNaMaoDimens.spacing3))

            // Content
            when {
                uiState.isLoading -> {
                    Box(
                        modifier = Modifier.fillMaxSize(),
                        contentAlignment = Alignment.Center
                    ) {
                        Column(
                            horizontalAlignment = Alignment.CenterHorizontally,
                            verticalArrangement = Arrangement.spacedBy(TaNaMaoDimens.spacing3)
                        ) {
                            CircularProgressIndicator(color = AccentOrange)
                            Text(
                                text = "Buscando ${uiState.selectedServiceType.label.lowercase()}...",
                                style = MaterialTheme.typography.bodyMedium,
                                color = TextSecondary
                            )
                        }
                    }
                }

                uiState.error != null -> {
                    ErrorContent(
                        message = uiState.error!!,
                        onRetry = { viewModel.refresh() }
                    )
                }

                uiState.locations.isEmpty() -> {
                    EmptyContent(
                        serviceType = uiState.selectedServiceType,
                        fallbackMessage = uiState.fallbackMessage,
                        nationalChains = uiState.nationalChains,
                        hasLocation = uiState.hasLocation,
                        onRequestLocation = {
                            locationPermissionLauncher.launch(Manifest.permission.ACCESS_FINE_LOCATION)
                        }
                    )
                }

                else -> {
                    LocationsList(
                        locations = uiState.locations,
                        serviceType = uiState.selectedServiceType,
                        onLocationClick = { viewModel.selectLocation(it) },
                        onMapsClick = { viewModel.openMaps(it) },
                        onWazeClick = { viewModel.openWaze(it) },
                        onCallClick = { viewModel.callPhone(it) },
                        onWhatsAppClick = { viewModel.openWhatsApp(it) },
                        modifier = Modifier.fillMaxSize()
                    )
                }
            }
        }

        // Location Detail Bottom Sheet
        uiState.selectedLocation?.let { location ->
            LocationDetailSheet(
                location = location,
                serviceType = uiState.selectedServiceType,
                onDismiss = { viewModel.selectLocation(null) },
                onMapsClick = { viewModel.openMaps(location) },
                onWazeClick = { viewModel.openWaze(location) },
                onCallClick = { viewModel.callPhone(location) },
                onWhatsAppClick = { viewModel.openWhatsApp(location) }
            )
        }
    }
}

@Composable
private fun NearbyTopBar(
    onNavigateBack: () -> Unit,
    onRefresh: () -> Unit
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
        IconButton(
            onClick = onNavigateBack,
            modifier = Modifier
                .size(40.dp)
                .clip(CircleShape)
                .background(BackgroundTertiary)
        ) {
            Icon(
                imageVector = Icons.AutoMirrored.Outlined.ArrowBack,
                contentDescription = "Voltar",
                tint = TextPrimary
            )
        }

        Text(
            text = "Serviços perto de você",
            style = MaterialTheme.typography.titleLarge,
            fontWeight = FontWeight.Bold,
            color = TextPrimary
        )

        IconButton(
            onClick = onRefresh,
            modifier = Modifier
                .size(40.dp)
                .clip(CircleShape)
                .background(BackgroundTertiary)
        ) {
            Icon(
                imageVector = Icons.Filled.Refresh,
                contentDescription = "Atualizar",
                tint = TextPrimary
            )
        }
    }
}

@Composable
private fun ServiceTypeSelector(
    selectedType: ServiceType,
    onTypeSelected: (ServiceType) -> Unit,
    modifier: Modifier = Modifier
) {
    Row(
        modifier = modifier
            .fillMaxWidth()
            .clip(RoundedCornerShape(TaNaMaoDimens.cardRadius))
            .background(BackgroundTertiary)
            .padding(TaNaMaoDimens.spacing1),
        horizontalArrangement = Arrangement.spacedBy(TaNaMaoDimens.spacing1)
    ) {
        ServiceType.entries.forEach { type ->
            val isSelected = type == selectedType
            Box(
                modifier = Modifier
                    .weight(1f)
                    .clip(RoundedCornerShape(TaNaMaoDimens.cardRadiusSmall))
                    .background(if (isSelected) AccentOrange else Color.Transparent)
                    .clickable { onTypeSelected(type) }
                    .padding(vertical = TaNaMaoDimens.spacing3),
                contentAlignment = Alignment.Center
            ) {
                Row(
                    horizontalArrangement = Arrangement.spacedBy(TaNaMaoDimens.spacing2),
                    verticalAlignment = Alignment.CenterVertically
                ) {
                    Icon(
                        imageVector = if (type == ServiceType.PHARMACY) Icons.Filled.LocalPharmacy else Icons.Filled.Apartment,
                        contentDescription = null,
                        tint = if (isSelected) TextOnAccent else TextSecondary,
                        modifier = Modifier.size(20.dp)
                    )
                    Text(
                        text = type.label,
                        style = MaterialTheme.typography.labelLarge,
                        fontWeight = if (isSelected) FontWeight.Bold else FontWeight.Medium,
                        color = if (isSelected) TextOnAccent else TextSecondary
                    )
                }
            }
        }
    }
}

@Composable
private fun LocationsList(
    locations: List<ServiceLocation>,
    serviceType: ServiceType,
    onLocationClick: (ServiceLocation) -> Unit,
    onMapsClick: (ServiceLocation) -> Unit,
    onWazeClick: (ServiceLocation) -> Unit,
    onCallClick: (ServiceLocation) -> Unit,
    onWhatsAppClick: (ServiceLocation) -> Unit,
    modifier: Modifier = Modifier
) {
    LazyColumn(
        modifier = modifier.padding(horizontal = TaNaMaoDimens.screenPaddingHorizontal),
        contentPadding = PaddingValues(bottom = TaNaMaoDimens.bottomNavHeight + 16.dp),
        verticalArrangement = Arrangement.spacedBy(TaNaMaoDimens.spacing3)
    ) {
        // Header
        item {
            Text(
                text = "Encontrei ${locations.size} ${serviceType.label.lowercase()}:",
                style = MaterialTheme.typography.titleSmall,
                fontWeight = FontWeight.SemiBold,
                color = TextSecondary
            )
        }

        // Location cards
        items(locations) { location ->
            LocationCard(
                location = location,
                serviceType = serviceType,
                onClick = { onLocationClick(location) },
                onMapsClick = { onMapsClick(location) },
                onCallClick = { onCallClick(location) }
            )
        }

        // Tips
        item {
            TipsCard(serviceType = serviceType)
        }
    }
}

@Composable
private fun LocationCard(
    location: ServiceLocation,
    serviceType: ServiceType,
    onClick: () -> Unit,
    onMapsClick: () -> Unit,
    onCallClick: () -> Unit
) {
    Column(
        modifier = Modifier
            .fillMaxWidth()
            .clip(RoundedCornerShape(TaNaMaoDimens.cardRadius))
            .background(BackgroundSecondary)
            .clickable(onClick = onClick)
            .padding(TaNaMaoDimens.cardPadding),
        verticalArrangement = Arrangement.spacedBy(TaNaMaoDimens.spacing3)
    ) {
        // Header
        Row(
            modifier = Modifier.fillMaxWidth(),
            horizontalArrangement = Arrangement.SpaceBetween,
            verticalAlignment = Alignment.Top
        ) {
            Column(modifier = Modifier.weight(1f)) {
                Text(
                    text = location.nome,
                    style = MaterialTheme.typography.titleMedium,
                    fontWeight = FontWeight.SemiBold,
                    color = TextPrimary,
                    maxLines = 2,
                    overflow = TextOverflow.Ellipsis
                )
                Spacer(modifier = Modifier.height(4.dp))
                Text(
                    text = location.endereco,
                    style = MaterialTheme.typography.bodySmall,
                    color = TextSecondary,
                    maxLines = 2,
                    overflow = TextOverflow.Ellipsis
                )
            }

            // Status badge
            location.abertoAgora?.let { aberto ->
                Box(
                    modifier = Modifier
                        .clip(RoundedCornerShape(TaNaMaoDimens.chipRadius))
                        .background(if (aberto) StatusActive.copy(alpha = 0.2f) else BackgroundTertiary)
                        .padding(horizontal = TaNaMaoDimens.spacing2, vertical = 4.dp)
                ) {
                    Text(
                        text = if (aberto) "Aberto" else "Fechado",
                        style = MaterialTheme.typography.labelSmall,
                        color = if (aberto) StatusActive else TextTertiary
                    )
                }
            }
        }

        // Info row
        Row(
            modifier = Modifier.fillMaxWidth(),
            horizontalArrangement = Arrangement.spacedBy(TaNaMaoDimens.spacing4)
        ) {
            location.distancia?.let { dist ->
                Row(
                    horizontalArrangement = Arrangement.spacedBy(4.dp),
                    verticalAlignment = Alignment.CenterVertically
                ) {
                    Icon(
                        imageVector = Icons.Outlined.DirectionsWalk,
                        contentDescription = null,
                        tint = TextTertiary,
                        modifier = Modifier.size(16.dp)
                    )
                    Text(
                        text = dist,
                        style = MaterialTheme.typography.bodySmall,
                        color = TextSecondary
                    )
                }
            }

            location.horario?.let { horario ->
                Row(
                    horizontalArrangement = Arrangement.spacedBy(4.dp),
                    verticalAlignment = Alignment.CenterVertically
                ) {
                    Icon(
                        imageVector = Icons.Outlined.Schedule,
                        contentDescription = null,
                        tint = TextTertiary,
                        modifier = Modifier.size(16.dp)
                    )
                    Text(
                        text = horario,
                        style = MaterialTheme.typography.bodySmall,
                        color = TextSecondary,
                        maxLines = 1,
                        overflow = TextOverflow.Ellipsis
                    )
                }
            }

            if (location.delivery == true) {
                Row(
                    horizontalArrangement = Arrangement.spacedBy(4.dp),
                    verticalAlignment = Alignment.CenterVertically
                ) {
                    Icon(
                        imageVector = Icons.Outlined.DeliveryDining,
                        contentDescription = null,
                        tint = StatusActive,
                        modifier = Modifier.size(16.dp)
                    )
                    Text(
                        text = "Entrega",
                        style = MaterialTheme.typography.bodySmall,
                        color = StatusActive
                    )
                }
            }
        }

        // Action buttons
        Row(
            modifier = Modifier.fillMaxWidth(),
            horizontalArrangement = Arrangement.spacedBy(TaNaMaoDimens.spacing2)
        ) {
            // Maps button
            if (location.mapsLink != null) {
                ActionChip(
                    icon = Icons.Filled.Map,
                    text = "Como chegar",
                    onClick = onMapsClick,
                    modifier = Modifier.weight(1f)
                )
            }

            // Call button
            if (location.telefone != null) {
                ActionChip(
                    icon = Icons.Filled.Phone,
                    text = "Ligar",
                    onClick = onCallClick,
                    modifier = Modifier.weight(1f)
                )
            }
        }
    }
}

@Composable
private fun ActionChip(
    icon: ImageVector,
    text: String,
    onClick: () -> Unit,
    modifier: Modifier = Modifier
) {
    Row(
        modifier = modifier
            .clip(RoundedCornerShape(TaNaMaoDimens.chipRadius))
            .background(AccentOrangeSubtle)
            .clickable(onClick = onClick)
            .padding(horizontal = TaNaMaoDimens.spacing3, vertical = TaNaMaoDimens.spacing2),
        horizontalArrangement = Arrangement.Center,
        verticalAlignment = Alignment.CenterVertically
    ) {
        Icon(
            imageVector = icon,
            contentDescription = null,
            tint = AccentOrange,
            modifier = Modifier.size(18.dp)
        )
        Spacer(modifier = Modifier.width(TaNaMaoDimens.spacing2))
        Text(
            text = text,
            style = MaterialTheme.typography.labelMedium,
            fontWeight = FontWeight.Medium,
            color = AccentOrange
        )
    }
}

@Composable
private fun TipsCard(serviceType: ServiceType) {
    Column(
        modifier = Modifier
            .fillMaxWidth()
            .clip(RoundedCornerShape(TaNaMaoDimens.cardRadius))
            .background(AccentOrangeSubtle)
            .padding(TaNaMaoDimens.cardPadding),
        verticalArrangement = Arrangement.spacedBy(TaNaMaoDimens.spacing2)
    ) {
        Row(
            horizontalArrangement = Arrangement.spacedBy(TaNaMaoDimens.spacing2),
            verticalAlignment = Alignment.CenterVertically
        ) {
            Icon(
                imageVector = Icons.Filled.Lightbulb,
                contentDescription = null,
                tint = AccentOrange,
                modifier = Modifier.size(20.dp)
            )
            Text(
                text = "O que levar",
                style = MaterialTheme.typography.titleSmall,
                fontWeight = FontWeight.SemiBold,
                color = TextPrimary
            )
        }

        if (serviceType == ServiceType.PHARMACY) {
            Text(
                text = "CPF\nReceita médica (validade 120 dias)",
                style = MaterialTheme.typography.bodySmall,
                color = TextSecondary
            )
            Text(
                text = "Não precisa ir ao CRAS! Vá direto na farmácia.",
                style = MaterialTheme.typography.bodySmall,
                fontWeight = FontWeight.Medium,
                color = StatusActive
            )
        } else {
            Text(
                text = "CPF de todos da família\nDocumento com foto\nConta de luz ou água com seu endereço",
                style = MaterialTheme.typography.bodySmall,
                color = TextSecondary
            )
        }
    }
}

@Composable
private fun EmptyContent(
    serviceType: ServiceType,
    fallbackMessage: String?,
    nationalChains: List<String>,
    hasLocation: Boolean,
    onRequestLocation: () -> Unit
) {
    Column(
        modifier = Modifier
            .fillMaxSize()
            .padding(TaNaMaoDimens.spacing4),
        horizontalAlignment = Alignment.CenterHorizontally,
        verticalArrangement = Arrangement.Center
    ) {
        Icon(
            imageVector = if (serviceType == ServiceType.PHARMACY)
                Icons.Outlined.LocalPharmacy else Icons.Outlined.Apartment,
            contentDescription = null,
            tint = TextTertiary,
            modifier = Modifier.size(64.dp)
        )

        Spacer(modifier = Modifier.height(TaNaMaoDimens.spacing4))

        if (!hasLocation) {
            Text(
                text = "Precisamos da sua localização",
                style = MaterialTheme.typography.titleMedium,
                fontWeight = FontWeight.SemiBold,
                color = TextPrimary,
                textAlign = TextAlign.Center
            )
            Spacer(modifier = Modifier.height(TaNaMaoDimens.spacing2))
            Text(
                text = "Para encontrar ${serviceType.label.lowercase()} perto de você, precisamos saber onde você está.",
                style = MaterialTheme.typography.bodyMedium,
                color = TextSecondary,
                textAlign = TextAlign.Center
            )
            Spacer(modifier = Modifier.height(TaNaMaoDimens.spacing4))
            PropelButton(
                text = "Permitir localização",
                onClick = onRequestLocation,
                style = PropelButtonStyle.Primary,
                leadingIcon = Icons.Filled.MyLocation
            )
        } else {
            Text(
                text = "Não encontramos ${serviceType.label.lowercase()} próximos",
                style = MaterialTheme.typography.titleMedium,
                fontWeight = FontWeight.SemiBold,
                color = TextPrimary,
                textAlign = TextAlign.Center
            )

            if (fallbackMessage != null) {
                Spacer(modifier = Modifier.height(TaNaMaoDimens.spacing2))
                Text(
                    text = fallbackMessage,
                    style = MaterialTheme.typography.bodyMedium,
                    color = TextSecondary,
                    textAlign = TextAlign.Center
                )
            }

            if (nationalChains.isNotEmpty() && serviceType == ServiceType.PHARMACY) {
                Spacer(modifier = Modifier.height(TaNaMaoDimens.spacing4))
                Text(
                    text = "Redes credenciadas em todo o Brasil:",
                    style = MaterialTheme.typography.titleSmall,
                    fontWeight = FontWeight.Medium,
                    color = TextPrimary
                )
                Spacer(modifier = Modifier.height(TaNaMaoDimens.spacing2))
                nationalChains.forEach { chain ->
                    Text(
                        text = "• $chain",
                        style = MaterialTheme.typography.bodyMedium,
                        color = TextSecondary
                    )
                }
            }

            if (serviceType == ServiceType.CRAS) {
                Spacer(modifier = Modifier.height(TaNaMaoDimens.spacing4))
                Text(
                    text = "Ligue para o Disque Social: 121 (gratuito)",
                    style = MaterialTheme.typography.bodyMedium,
                    fontWeight = FontWeight.Medium,
                    color = AccentOrange,
                    textAlign = TextAlign.Center
                )
            }
        }
    }
}

@Composable
private fun ErrorContent(
    message: String,
    onRetry: () -> Unit
) {
    Column(
        modifier = Modifier
            .fillMaxSize()
            .padding(TaNaMaoDimens.spacing4),
        horizontalAlignment = Alignment.CenterHorizontally,
        verticalArrangement = Arrangement.Center
    ) {
        Icon(
            imageVector = Icons.Outlined.CloudOff,
            contentDescription = null,
            tint = StatusBlocked,
            modifier = Modifier.size(64.dp)
        )
        Spacer(modifier = Modifier.height(TaNaMaoDimens.spacing4))
        Text(
            text = "Ops, deu um problema",
            style = MaterialTheme.typography.titleMedium,
            fontWeight = FontWeight.SemiBold,
            color = TextPrimary
        )
        Spacer(modifier = Modifier.height(TaNaMaoDimens.spacing2))
        Text(
            text = message,
            style = MaterialTheme.typography.bodyMedium,
            color = TextSecondary,
            textAlign = TextAlign.Center
        )
        Spacer(modifier = Modifier.height(TaNaMaoDimens.spacing4))
        PropelButton(
            text = "Tentar de novo",
            onClick = onRetry,
            style = PropelButtonStyle.Primary,
            leadingIcon = Icons.Filled.Refresh
        )
    }
}

@OptIn(ExperimentalMaterial3Api::class)
@Composable
private fun LocationDetailSheet(
    location: ServiceLocation,
    serviceType: ServiceType,
    onDismiss: () -> Unit,
    onMapsClick: () -> Unit,
    onWazeClick: () -> Unit,
    onCallClick: () -> Unit,
    onWhatsAppClick: () -> Unit
) {
    ModalBottomSheet(
        onDismissRequest = onDismiss,
        containerColor = BackgroundSecondary
    ) {
        Column(
            modifier = Modifier
                .fillMaxWidth()
                .padding(
                    start = TaNaMaoDimens.spacing4,
                    end = TaNaMaoDimens.spacing4,
                    bottom = TaNaMaoDimens.spacing6
                ),
            verticalArrangement = Arrangement.spacedBy(TaNaMaoDimens.spacing4)
        ) {
            // Header
            Column {
                Text(
                    text = location.nome,
                    style = MaterialTheme.typography.titleLarge,
                    fontWeight = FontWeight.Bold,
                    color = TextPrimary
                )
                Spacer(modifier = Modifier.height(4.dp))
                Text(
                    text = location.endereco,
                    style = MaterialTheme.typography.bodyMedium,
                    color = TextSecondary
                )
            }

            // Info
            Column(
                modifier = Modifier
                    .fillMaxWidth()
                    .clip(RoundedCornerShape(TaNaMaoDimens.cardRadius))
                    .background(BackgroundTertiary)
                    .padding(TaNaMaoDimens.cardPadding),
                verticalArrangement = Arrangement.spacedBy(TaNaMaoDimens.spacing3)
            ) {
                location.distancia?.let {
                    InfoRow(icon = Icons.Outlined.DirectionsWalk, label = "Distância", value = it)
                }
                location.horario?.let {
                    InfoRow(icon = Icons.Outlined.Schedule, label = "Horário", value = it)
                }
                location.telefone?.let {
                    InfoRow(icon = Icons.Outlined.Phone, label = "Telefone", value = it)
                }
                if (location.delivery == true) {
                    InfoRow(icon = Icons.Outlined.DeliveryDining, label = "Entrega", value = "Disponível")
                }
            }

            // Action buttons
            Column(verticalArrangement = Arrangement.spacedBy(TaNaMaoDimens.spacing2)) {
                if (location.mapsLink != null) {
                    PropelButton(
                        text = "Abrir no Google Maps",
                        onClick = onMapsClick,
                        style = PropelButtonStyle.Primary,
                        size = PropelButtonSize.Large,
                        fullWidth = true,
                        leadingIcon = Icons.Filled.Map
                    )
                }

                if (location.wazeLink != null) {
                    PropelButton(
                        text = "Abrir no Waze",
                        onClick = onWazeClick,
                        style = PropelButtonStyle.Secondary,
                        size = PropelButtonSize.Large,
                        fullWidth = true,
                        leadingIcon = Icons.Filled.Navigation
                    )
                }

                if (location.telefone != null) {
                    PropelButton(
                        text = "Ligar",
                        onClick = onCallClick,
                        style = PropelButtonStyle.Secondary,
                        size = PropelButtonSize.Large,
                        fullWidth = true,
                        leadingIcon = Icons.Filled.Phone
                    )
                }

                if (location.whatsappLink != null) {
                    PropelButton(
                        text = "WhatsApp",
                        onClick = onWhatsAppClick,
                        style = PropelButtonStyle.Secondary,
                        size = PropelButtonSize.Large,
                        fullWidth = true,
                        leadingIcon = Icons.Filled.Chat
                    )
                }
            }
        }
    }
}

@Composable
private fun InfoRow(
    icon: ImageVector,
    label: String,
    value: String
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
                imageVector = icon,
                contentDescription = null,
                tint = AccentOrange,
                modifier = Modifier.size(20.dp)
            )
            Text(
                text = label,
                style = MaterialTheme.typography.bodyMedium,
                color = TextSecondary
            )
        }
        Text(
            text = value,
            style = MaterialTheme.typography.bodyMedium,
            fontWeight = FontWeight.Medium,
            color = TextPrimary
        )
    }
}
