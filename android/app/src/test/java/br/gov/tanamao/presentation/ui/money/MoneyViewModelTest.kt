package br.gov.tanamao.presentation.ui.money

import br.gov.tanamao.MainCoroutineRule
import kotlinx.coroutines.ExperimentalCoroutinesApi
import org.junit.Rule

import br.gov.tanamao.domain.model.AppError
import br.gov.tanamao.domain.model.Result
import br.gov.tanamao.domain.repository.AgentRepository
import br.gov.tanamao.domain.repository.AgentResponse
import io.mockk.coEvery
import io.mockk.mockk
import kotlinx.coroutines.flow.first
import kotlinx.coroutines.test.runTest
import org.junit.Assert.*
import org.junit.Before
import org.junit.Test

@OptIn(ExperimentalCoroutinesApi::class)
class MoneyViewModelTest {

    @get:Rule
    val mainCoroutineRule = MainCoroutineRule()

    private lateinit var agentRepository: AgentRepository
    private lateinit var viewModel: MoneyViewModel

    @Before
    fun setup() {
        agentRepository = mockk()
        viewModel = MoneyViewModel(agentRepository)
    }

    @Test
    fun `initial state should load money overview`() = runTest {
        val state = viewModel.uiState.first()

        assertNotNull(state.overview)
        assertEquals(42_000_000_000.0, state.overview?.totalAvailable)
        assertFalse(state.isLoading)
    }

    @Test
    fun `checkMyMoney should update state with result`() = runTest {
        // Given
        val mockResponse = AgentResponse(
            message = "Você tem dinheiro disponível: R$ 500,00 no PIS/PASEP",
            sessionId = "test-session",
            toolsUsed = listOf("consultar_dinheiro_esquecido")
        )

        coEvery { agentRepository.sendMessage(any(), any()) } returns Result.Success(mockResponse)

        // When
        viewModel.checkMyMoney()

        // Wait for coroutine to complete
        kotlinx.coroutines.delay(100)

        // Then
        val state = viewModel.uiState.first()
        assertNotNull(state.checkResult)
        assertFalse(state.isChecking)
    }

    @Test
    fun `checkMyMoney with error should set error state`() = runTest {
        // Given
        val appError = AppError.Network("Network error")
        coEvery { agentRepository.sendMessage(any(), any()) } returns Result.Error(appError)

        // When
        viewModel.checkMyMoney()

        // Wait for coroutine to complete
        kotlinx.coroutines.delay(100)

        // Then
        val state = viewModel.uiState.first()
        assertNotNull(state.error)
        assertFalse(state.isChecking)
    }

    @Test
    fun `navigateToGuide should update navigation state`() = runTest {
        // When
        viewModel.navigateToGuide("PIS_PASEP")

        // Wait for state to update
        kotlinx.coroutines.delay(100)

        // Then
        val state = viewModel.uiState.first()
        assertEquals("PIS_PASEP", state.navigateToGuide)
    }

    @Test
    fun `clearNavigation should reset navigation state`() = runTest {
        // Given
        viewModel.navigateToGuide("PIS_PASEP")
        kotlinx.coroutines.delay(100)

        // When
        viewModel.clearNavigation()

        // Then
        val state = viewModel.uiState.first()
        assertNull(state.navigateToGuide)
    }

    @Test
    fun `refresh should reload overview`() = runTest {
        // When
        viewModel.refresh()

        // Then
        val state = viewModel.uiState.first()
        assertNotNull(state.overview)
    }
}
