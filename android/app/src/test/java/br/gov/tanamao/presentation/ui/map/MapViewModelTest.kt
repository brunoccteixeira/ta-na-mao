package br.gov.tanamao.presentation.ui.map

import br.gov.tanamao.MainCoroutineRule
import kotlinx.coroutines.ExperimentalCoroutinesApi
import org.junit.Rule

import android.content.Context
import app.cash.turbine.test
import br.gov.tanamao.data.api.TaNaMaoApi
import br.gov.tanamao.data.api.dto.NearbyResponseDto
import io.mockk.coEvery
import io.mockk.mockk
import kotlinx.coroutines.test.runTest
import org.junit.Assert.*
import org.junit.Before
import org.junit.Test

@OptIn(ExperimentalCoroutinesApi::class)
class MapViewModelTest {

    @get:Rule
    val mainCoroutineRule = MainCoroutineRule()

    private lateinit var api: TaNaMaoApi
    private lateinit var context: Context
    private lateinit var viewModel: MapViewModel

    @Before
    fun setup() {
        api = mockk(relaxed = true)
        context = mockk(relaxed = true)

        // Mock API responses for init{} - loadNearbyServices()
        coEvery { api.getNearbyPharmacies(any(), any(), any(), any()) } returns NearbyResponseDto(
            sucesso = true,
            encontrados = 0,
            locais = emptyList(),
            mensagem = null,
            redesNacionais = null
        )
        coEvery { api.getNearbyCras(any(), any(), any(), any()) } returns NearbyResponseDto(
            sucesso = true,
            encontrados = 0,
            locais = emptyList(),
            mensagem = null,
            redesNacionais = null
        )

        viewModel = MapViewModel(api, context)
    }

    @Test
    fun `initial state should have default service type`() = runTest {
        viewModel.uiState.test {
            val state = awaitItem()
            assertEquals(ServiceType.PHARMACY, state.selectedServiceType)
            assertNull(state.error)
        }
    }

    @Test
    fun `selectServiceType should update selected service type`() = runTest {
        // Given
        val newType = ServiceType.CRAS

        // When
        viewModel.selectServiceType(newType)

        // Then
        viewModel.uiState.test {
            val state = awaitItem()
            assertEquals(newType, state.selectedServiceType)
        }
    }

    @Test
    fun `setLocation should update location state`() = runTest {
        // Given
        val lat = -23.5505
        val lng = -46.6333

        // When
        viewModel.setLocation(lat, lng)

        // Then
        viewModel.uiState.test {
            val state = awaitItem()
            assertTrue(state.hasLocation)
            assertEquals(lat, state.latitude)
            assertEquals(lng, state.longitude)
        }
    }

    @Test
    fun `initial service type should be PHARMACY`() = runTest {
        viewModel.uiState.test {
            val state = awaitItem()
            assertEquals(ServiceType.PHARMACY, state.selectedServiceType)
        }
    }

    @Test
    fun `selectLocation should update selected location`() = runTest {
        // Given
        val location = ServiceLocation(
            nome = "Farmácia Test",
            endereco = "Rua Test, 123",
            distancia = "500m",
            distanciaMetros = 500,
            telefone = "11999999999",
            horario = "08:00-18:00",
            abertoAgora = true,
            delivery = false,
            mapsLink = "https://maps.google.com",
            wazeLink = null,
            whatsappLink = null
        )

        // When
        viewModel.selectLocation(location)

        // Then
        viewModel.uiState.test {
            val state = awaitItem()
            assertEquals(location, state.selectedLocation)
        }
    }

    @Test
    fun `selectLocation with null should clear selected location`() = runTest {
        // Given
        val location = ServiceLocation(
            nome = "Test",
            endereco = "Test",
            distancia = null,
            distanciaMetros = null,
            telefone = null,
            horario = null,
            abertoAgora = null,
            delivery = null,
            mapsLink = null,
            wazeLink = null,
            whatsappLink = null
        )
        viewModel.selectLocation(location)

        // When
        viewModel.selectLocation(null)

        // Then
        viewModel.uiState.test {
            val state = awaitItem()
            assertNull(state.selectedLocation)
        }
    }
}
