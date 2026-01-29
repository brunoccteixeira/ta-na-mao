package br.gov.tanamao.presentation.ui.map

import android.content.Context
import android.content.Intent
import android.net.Uri
import androidx.lifecycle.ViewModel
import androidx.lifecycle.viewModelScope
import br.gov.tanamao.data.api.TaNaMaoApi
import br.gov.tanamao.data.api.dto.ServiceLocationDto
import dagger.hilt.android.lifecycle.HiltViewModel
import dagger.hilt.android.qualifiers.ApplicationContext
import kotlinx.coroutines.flow.MutableStateFlow
import kotlinx.coroutines.flow.StateFlow
import kotlinx.coroutines.flow.asStateFlow
import kotlinx.coroutines.flow.update
import kotlinx.coroutines.launch
import javax.inject.Inject

/**
 * Service type for nearby search
 */
enum class ServiceType(val label: String, val icon: String) {
    PHARMACY("Farmácias", "local_pharmacy"),
    CRAS("Postos de Assistência", "apartment")
}

/**
 * UI State for the Map screen - citizen focused
 */
data class NearbyUiState(
    val isLoading: Boolean = true,
    val error: String? = null,
    val selectedServiceType: ServiceType = ServiceType.PHARMACY,
    val locations: List<ServiceLocation> = emptyList(),
    val selectedLocation: ServiceLocation? = null,
    val hasLocation: Boolean = false,
    val latitude: Double? = null,
    val longitude: Double? = null,
    val fallbackMessage: String? = null,
    val nationalChains: List<String> = emptyList()
)

/**
 * Service location model for UI
 */
data class ServiceLocation(
    val nome: String,
    val endereco: String,
    val distancia: String?,
    val distanciaMetros: Int?,
    val telefone: String?,
    val horario: String?,
    val abertoAgora: Boolean?,
    val delivery: Boolean?,
    val mapsLink: String?,
    val wazeLink: String?,
    val whatsappLink: String?
)

@HiltViewModel
class MapViewModel @Inject constructor(
    private val api: TaNaMaoApi,
    @ApplicationContext private val context: Context
) : ViewModel() {

    private val _uiState = MutableStateFlow(NearbyUiState())
    val uiState: StateFlow<NearbyUiState> = _uiState.asStateFlow()

    init {
        // Start with pharmacies by default
        loadNearbyServices(ServiceType.PHARMACY)
    }

    /**
     * Set user location and reload services
     */
    fun setLocation(latitude: Double, longitude: Double) {
        _uiState.update {
            it.copy(
                hasLocation = true,
                latitude = latitude,
                longitude = longitude
            )
        }
        loadNearbyServices(_uiState.value.selectedServiceType)
    }

    /**
     * Select service type and load
     */
    fun selectServiceType(type: ServiceType) {
        _uiState.update { it.copy(selectedServiceType = type) }
        loadNearbyServices(type)
    }

    /**
     * Load nearby services based on type and location
     */
    fun loadNearbyServices(type: ServiceType) {
        viewModelScope.launch {
            _uiState.update { it.copy(isLoading = true, error = null) }

            try {
                val lat = _uiState.value.latitude
                val lng = _uiState.value.longitude

                val response = when (type) {
                    ServiceType.PHARMACY -> {
                        api.getNearbyPharmacies(
                            latitude = lat,
                            longitude = lng,
                            limite = 10
                        )
                    }
                    ServiceType.CRAS -> {
                        api.getNearbyCras(
                            latitude = lat,
                            longitude = lng,
                            limite = 5
                        )
                    }
                }

                val locations = response.locais.map { it.toServiceLocation() }

                _uiState.update {
                    it.copy(
                        isLoading = false,
                        locations = locations,
                        fallbackMessage = response.mensagem,
                        nationalChains = response.redesNacionais ?: emptyList(),
                        error = null
                    )
                }
            } catch (e: Exception) {
                _uiState.update {
                    it.copy(
                        isLoading = false,
                        error = "Não foi possível buscar serviços. Verifique sua conexão."
                    )
                }
            }
        }
    }

    /**
     * Select a location for detail view
     */
    fun selectLocation(location: ServiceLocation?) {
        _uiState.update { it.copy(selectedLocation = location) }
    }

    /**
     * Open Google Maps with directions
     */
    fun openMaps(location: ServiceLocation) {
        val link = location.mapsLink ?: return
        try {
            val intent = Intent(Intent.ACTION_VIEW, Uri.parse(link)).apply {
                flags = Intent.FLAG_ACTIVITY_NEW_TASK
            }
            context.startActivity(intent)
        } catch (e: Exception) {
            // Fallback to search
            val searchIntent = Intent(
                Intent.ACTION_VIEW,
                Uri.parse("https://www.google.com/maps/search/${Uri.encode(location.endereco)}")
            ).apply {
                flags = Intent.FLAG_ACTIVITY_NEW_TASK
            }
            context.startActivity(searchIntent)
        }
    }

    /**
     * Open Waze with navigation
     */
    fun openWaze(location: ServiceLocation) {
        val link = location.wazeLink ?: return
        try {
            val intent = Intent(Intent.ACTION_VIEW, Uri.parse(link)).apply {
                flags = Intent.FLAG_ACTIVITY_NEW_TASK
            }
            context.startActivity(intent)
        } catch (e: Exception) {
            // Waze not installed, open in browser
            val webIntent = Intent(Intent.ACTION_VIEW, Uri.parse(link)).apply {
                flags = Intent.FLAG_ACTIVITY_NEW_TASK
            }
            context.startActivity(webIntent)
        }
    }

    /**
     * Open WhatsApp chat
     */
    fun openWhatsApp(location: ServiceLocation) {
        val link = location.whatsappLink ?: return
        try {
            val intent = Intent(Intent.ACTION_VIEW, Uri.parse(link)).apply {
                flags = Intent.FLAG_ACTIVITY_NEW_TASK
            }
            context.startActivity(intent)
        } catch (e: Exception) {
            // WhatsApp not installed
        }
    }

    /**
     * Call phone number
     */
    fun callPhone(location: ServiceLocation) {
        val phone = location.telefone ?: return
        val cleanPhone = phone.replace(Regex("[^0-9]"), "")
        try {
            val intent = Intent(Intent.ACTION_DIAL, Uri.parse("tel:$cleanPhone")).apply {
                flags = Intent.FLAG_ACTIVITY_NEW_TASK
            }
            context.startActivity(intent)
        } catch (e: Exception) {
            // Cannot open dialer
        }
    }

    /**
     * Refresh current service type
     */
    fun refresh() {
        loadNearbyServices(_uiState.value.selectedServiceType)
    }

    private fun ServiceLocationDto.toServiceLocation(): ServiceLocation {
        return ServiceLocation(
            nome = nome,
            endereco = endereco,
            distancia = distancia,
            distanciaMetros = distanciaMetros,
            telefone = telefone,
            horario = horario,
            abertoAgora = abertoAgora,
            delivery = delivery,
            mapsLink = links?.maps ?: links?.direcoes,
            wazeLink = links?.waze,
            whatsappLink = links?.whatsapp
        )
    }
}
