package br.gov.tanamao.presentation.components.chat

import android.content.Intent
import android.net.Uri
import androidx.compose.foundation.background
import androidx.compose.foundation.layout.*
import androidx.compose.foundation.shape.RoundedCornerShape
import androidx.compose.material.icons.Icons
import androidx.compose.material.icons.filled.*
import androidx.compose.material3.*
import androidx.compose.runtime.*
import androidx.compose.ui.Alignment
import androidx.compose.ui.Modifier
import androidx.compose.ui.draw.clip
import androidx.compose.ui.platform.LocalContext
import androidx.compose.ui.text.font.FontWeight
import androidx.compose.ui.unit.dp
import br.gov.tanamao.domain.model.MessageMetadata
import br.gov.tanamao.presentation.components.PropelButton
import br.gov.tanamao.presentation.components.PropelButtonSize
import br.gov.tanamao.presentation.components.PropelButtonStyle
import br.gov.tanamao.presentation.theme.TaNaMaoDimens
import com.google.android.gms.maps.model.CameraPosition
import com.google.android.gms.maps.model.LatLng
import com.google.maps.android.compose.*

/**
 * Card showing location with embedded Google Maps
 */
@Composable
fun LocationMapCard(
    location: MessageMetadata.LocationCard,
    modifier: Modifier = Modifier
) {
    val context = LocalContext.current
    val position = LatLng(location.latitude, location.longitude)
    val cameraPositionState = rememberCameraPositionState {
        this.position = CameraPosition.fromLatLngZoom(position, 15f)
    }

    Column(
        modifier = modifier
            .fillMaxWidth()
            .padding(
                start = 40.dp,
                top = TaNaMaoDimens.spacing2,
                bottom = TaNaMaoDimens.spacing2
            )
    ) {
        Column(
            modifier = Modifier
                .fillMaxWidth()
                .clip(RoundedCornerShape(TaNaMaoDimens.cardRadius))
                .background(MaterialTheme.colorScheme.surfaceVariant),
            verticalArrangement = Arrangement.spacedBy(0.dp)
        ) {
            // Google Maps embed
            Box(
                modifier = Modifier
                    .fillMaxWidth()
                    .height(180.dp)
                    .clip(RoundedCornerShape(topStart = TaNaMaoDimens.cardRadius, topEnd = TaNaMaoDimens.cardRadius))
            ) {
                GoogleMap(
                    modifier = Modifier.fillMaxSize(),
                    cameraPositionState = cameraPositionState,
                    uiSettings = MapUiSettings(
                        zoomControlsEnabled = false,
                        mapToolbarEnabled = false,
                        myLocationButtonEnabled = false,
                        compassEnabled = false
                    ),
                    properties = MapProperties(
                        mapType = MapType.NORMAL
                    )
                ) {
                    Marker(
                        state = MarkerState(position = position),
                        title = location.name,
                        snippet = location.address
                    )
                }
            }

            // Location info
            Column(
                modifier = Modifier
                    .fillMaxWidth()
                    .padding(TaNaMaoDimens.cardPadding),
                verticalArrangement = Arrangement.spacedBy(TaNaMaoDimens.spacing3)
            ) {
                // Name and address
                Column(verticalArrangement = Arrangement.spacedBy(TaNaMaoDimens.spacing1)) {
                    Text(
                        text = location.name,
                        style = MaterialTheme.typography.titleMedium,
                        fontWeight = FontWeight.SemiBold,
                        color = MaterialTheme.colorScheme.onSurface
                    )

                    if (location.address.isNotBlank()) {
                        Row(
                            horizontalArrangement = Arrangement.spacedBy(TaNaMaoDimens.spacing2),
                            verticalAlignment = Alignment.CenterVertically
                        ) {
                            Icon(
                                imageVector = Icons.Filled.LocationOn,
                                contentDescription = null,
                                tint = MaterialTheme.colorScheme.onSurfaceVariant,
                                modifier = Modifier.size(16.dp)
                            )
                            Text(
                                text = location.address,
                                style = MaterialTheme.typography.bodyMedium,
                                color = MaterialTheme.colorScheme.onSurfaceVariant
                            )
                        }
                    }
                }

                // Hours and phone
                if (location.hours != null || location.phone != null) {
                    Column(
                        modifier = Modifier
                            .fillMaxWidth()
                            .clip(RoundedCornerShape(TaNaMaoDimens.cardRadiusSmall))
                            .background(MaterialTheme.colorScheme.surface)
                            .padding(TaNaMaoDimens.spacing3),
                        verticalArrangement = Arrangement.spacedBy(TaNaMaoDimens.spacing2)
                    ) {
                        location.hours?.let { hours ->
                            Row(
                                horizontalArrangement = Arrangement.spacedBy(TaNaMaoDimens.spacing2),
                                verticalAlignment = Alignment.CenterVertically
                            ) {
                                Icon(
                                    imageVector = Icons.Filled.Schedule,
                                    contentDescription = null,
                                    tint = MaterialTheme.colorScheme.primary,
                                    modifier = Modifier.size(18.dp)
                                )
                                Text(
                                    text = hours,
                                    style = MaterialTheme.typography.bodySmall,
                                    color = MaterialTheme.colorScheme.onSurface
                                )
                            }
                        }

                        location.phone?.let { phone ->
                            Row(
                                horizontalArrangement = Arrangement.spacedBy(TaNaMaoDimens.spacing2),
                                verticalAlignment = Alignment.CenterVertically
                            ) {
                                Icon(
                                    imageVector = Icons.Filled.Phone,
                                    contentDescription = null,
                                    tint = MaterialTheme.colorScheme.primary,
                                    modifier = Modifier.size(18.dp)
                                )
                                Text(
                                    text = phone,
                                    style = MaterialTheme.typography.bodySmall,
                                    color = MaterialTheme.colorScheme.onSurface
                                )
                            }
                        }
                    }
                }

                // Distance if available
                location.distance?.let { distance ->
                    Row(
                        horizontalArrangement = Arrangement.spacedBy(TaNaMaoDimens.spacing2),
                        verticalAlignment = Alignment.CenterVertically
                    ) {
                        Icon(
                            imageVector = Icons.Filled.DirectionsWalk,
                            contentDescription = null,
                            tint = MaterialTheme.colorScheme.primary,
                            modifier = Modifier.size(16.dp)
                        )
                        Text(
                            text = distance,
                            style = MaterialTheme.typography.labelMedium,
                            fontWeight = FontWeight.Medium,
                            color = MaterialTheme.colorScheme.primary
                        )
                    }
                }

                // Action buttons
                Row(
                    modifier = Modifier.fillMaxWidth(),
                    horizontalArrangement = Arrangement.spacedBy(TaNaMaoDimens.spacing2)
                ) {
                    // Google Maps button
                    PropelButton(
                        text = "Maps",
                        onClick = {
                            val uri = location.mapsUrl ?: "https://www.google.com/maps/dir/?api=1&destination=${location.latitude},${location.longitude}"
                            context.startActivity(Intent(Intent.ACTION_VIEW, Uri.parse(uri)))
                        },
                        style = PropelButtonStyle.Secondary,
                        size = PropelButtonSize.Small,
                        leadingIcon = Icons.Filled.Map,
                        modifier = Modifier.weight(1f)
                    )

                    // Waze button
                    PropelButton(
                        text = "Waze",
                        onClick = {
                            val uri = location.wazeUrl ?: "https://waze.com/ul?ll=${location.latitude},${location.longitude}&navigate=yes"
                            context.startActivity(Intent(Intent.ACTION_VIEW, Uri.parse(uri)))
                        },
                        style = PropelButtonStyle.Secondary,
                        size = PropelButtonSize.Small,
                        leadingIcon = Icons.Filled.Navigation,
                        modifier = Modifier.weight(1f)
                    )

                    // Call button (if phone available)
                    if (location.phone != null) {
                        PropelButton(
                            text = "Ligar",
                            onClick = {
                                val phoneNumber = location.phone.replace(Regex("[^0-9]"), "")
                                context.startActivity(Intent(Intent.ACTION_DIAL, Uri.parse("tel:$phoneNumber")))
                            },
                            style = PropelButtonStyle.Primary,
                            size = PropelButtonSize.Small,
                            leadingIcon = Icons.Filled.Call,
                            modifier = Modifier.weight(1f)
                        )
                    }
                }
            }
        }
    }
}

/**
 * Simplified location card without map (for when Maps SDK unavailable)
 */
@Composable
fun LocationCardSimple(
    location: MessageMetadata.LocationCard,
    modifier: Modifier = Modifier
) {
    val context = LocalContext.current

    Column(
        modifier = modifier
            .fillMaxWidth()
            .padding(
                start = 40.dp,
                top = TaNaMaoDimens.spacing2,
                bottom = TaNaMaoDimens.spacing2
            )
    ) {
        Column(
            modifier = Modifier
                .fillMaxWidth()
                .clip(RoundedCornerShape(TaNaMaoDimens.cardRadius))
                .background(MaterialTheme.colorScheme.surfaceVariant)
                .padding(TaNaMaoDimens.cardPadding),
            verticalArrangement = Arrangement.spacedBy(TaNaMaoDimens.spacing3)
        ) {
            // Header with icon
            Row(
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
                        imageVector = Icons.Filled.LocationOn,
                        contentDescription = null,
                        tint = MaterialTheme.colorScheme.primary,
                        modifier = Modifier.size(28.dp)
                    )
                }

                Column {
                    Text(
                        text = location.name,
                        style = MaterialTheme.typography.titleMedium,
                        fontWeight = FontWeight.SemiBold,
                        color = MaterialTheme.colorScheme.onSurface
                    )
                    if (location.address.isNotBlank()) {
                        Text(
                            text = location.address,
                            style = MaterialTheme.typography.bodySmall,
                            color = MaterialTheme.colorScheme.onSurfaceVariant
                        )
                    }
                }
            }

            // Info section
            if (location.hours != null || location.phone != null) {
                Column(
                    modifier = Modifier
                        .fillMaxWidth()
                        .clip(RoundedCornerShape(TaNaMaoDimens.cardRadiusSmall))
                        .background(MaterialTheme.colorScheme.surface)
                        .padding(TaNaMaoDimens.spacing3),
                    verticalArrangement = Arrangement.spacedBy(TaNaMaoDimens.spacing2)
                ) {
                    location.hours?.let { hours ->
                        Row(
                            horizontalArrangement = Arrangement.spacedBy(TaNaMaoDimens.spacing2),
                            verticalAlignment = Alignment.CenterVertically
                        ) {
                            Icon(
                                imageVector = Icons.Filled.Schedule,
                                contentDescription = null,
                                tint = MaterialTheme.colorScheme.primary,
                                modifier = Modifier.size(18.dp)
                            )
                            Text(
                                text = hours,
                                style = MaterialTheme.typography.bodySmall,
                                color = MaterialTheme.colorScheme.onSurface
                            )
                        }
                    }

                    location.phone?.let { phone ->
                        Row(
                            horizontalArrangement = Arrangement.spacedBy(TaNaMaoDimens.spacing2),
                            verticalAlignment = Alignment.CenterVertically
                        ) {
                            Icon(
                                imageVector = Icons.Filled.Phone,
                                contentDescription = null,
                                tint = MaterialTheme.colorScheme.primary,
                                modifier = Modifier.size(18.dp)
                            )
                            Text(
                                text = phone,
                                style = MaterialTheme.typography.bodySmall,
                                color = MaterialTheme.colorScheme.onSurface
                            )
                        }
                    }
                }
            }

            // Action buttons
            Row(
                modifier = Modifier.fillMaxWidth(),
                horizontalArrangement = Arrangement.spacedBy(TaNaMaoDimens.spacing2)
            ) {
                PropelButton(
                    text = "Abrir no Maps",
                    onClick = {
                        val uri = location.mapsUrl ?: "https://www.google.com/maps/dir/?api=1&destination=${location.latitude},${location.longitude}"
                        context.startActivity(Intent(Intent.ACTION_VIEW, Uri.parse(uri)))
                    },
                    style = PropelButtonStyle.Secondary,
                    size = PropelButtonSize.Medium,
                    leadingIcon = Icons.Filled.Map,
                    modifier = Modifier.weight(1f)
                )

                if (location.phone != null) {
                    PropelButton(
                        text = "Ligar",
                        onClick = {
                            val phoneNumber = location.phone.replace(Regex("[^0-9]"), "")
                            context.startActivity(Intent(Intent.ACTION_DIAL, Uri.parse("tel:$phoneNumber")))
                        },
                        style = PropelButtonStyle.Primary,
                        size = PropelButtonSize.Medium,
                        leadingIcon = Icons.Filled.Call,
                        modifier = Modifier.weight(1f)
                    )
                }
            }
        }
    }
}
