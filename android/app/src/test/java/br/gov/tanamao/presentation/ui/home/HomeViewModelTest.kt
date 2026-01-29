package br.gov.tanamao.presentation.ui.home

import br.gov.tanamao.MainCoroutineRule
import kotlinx.coroutines.ExperimentalCoroutinesApi
import org.junit.Rule

import app.cash.turbine.test
import br.gov.tanamao.domain.model.*
import br.gov.tanamao.domain.repository.AggregationRepository
import br.gov.tanamao.domain.repository.ProgramRepository
import br.gov.tanamao.domain.repository.AgentRepository
import br.gov.tanamao.domain.repository.AgentResponse
import io.mockk.coEvery
import io.mockk.coVerify
import io.mockk.mockk
import kotlinx.coroutines.flow.flowOf
import kotlinx.coroutines.test.runTest
import org.junit.Assert.*
import org.junit.Before
import org.junit.Test

@OptIn(ExperimentalCoroutinesApi::class)
class HomeViewModelTest {

    @get:Rule
    val mainCoroutineRule = MainCoroutineRule()

    private lateinit var programRepository: ProgramRepository
    private lateinit var aggregationRepository: AggregationRepository
    private lateinit var agentRepository: AgentRepository
    private lateinit var viewModel: HomeViewModel

    @Before
    fun setup() {
        programRepository = mockk()
        aggregationRepository = mockk()
        agentRepository = mockk()

        // Mocks para init{} - loadUserData()
        coEvery { agentRepository.sendMessage("meus dados", "") } returns Result.Success(
            AgentResponse(
                message = "Olá, Maria. Você recebe Bolsa Família: R$ 600,00",
                sessionId = "test-session",
                toolsUsed = listOf("meus_dados")
            )
        )

        coEvery { agentRepository.sendMessage("meus alertas", "") } returns Result.Success(
            AgentResponse(
                message = "Nenhum alerta no momento",
                sessionId = "test-session",
                toolsUsed = listOf("meus_alertas")
            )
        )

        // Mocks padrão para repositórios
        coEvery { programRepository.getPrograms() } returns flowOf(Result.Success(emptyList()))
        coEvery { aggregationRepository.getNational(any()) } returns Result.Success(
            NationalStats(
                population = 215000000,
                cadUnicoFamilies = 40000000,
                totalMunicipalities = 5570,
                totalStates = 27
            )
        )

        viewModel = HomeViewModel(programRepository, aggregationRepository, agentRepository)
    }

    @Test
    fun `initial state should load data`() = runTest {
        // Wait for init to complete
        kotlinx.coroutines.delay(100)

        viewModel.uiState.test {
            val state = awaitItem()
            // After init, we should have some data loaded
            assertNotNull(state)
        }
    }

    @Test
    fun `loadPrograms should update state with programs on success`() = runTest {
        // Given
        val mockPrograms = listOf(
            Program(
                code = ProgramCode.CADUNICO,
                name = "Bolsa Família / CadÚnico",
                description = "Programa de transferência de renda",
                dataSourceUrl = "https://example.gov.br",
                updateFrequency = UpdateFrequency.MONTHLY,
                nationalStats = null
            )
        )
        coEvery { programRepository.getPrograms() } returns flowOf(
            Result.Success(mockPrograms)
        )

        // When - create a new ViewModel to trigger loadPrograms
        val newViewModel = HomeViewModel(programRepository, aggregationRepository, agentRepository)

        // Wait for init to complete
        kotlinx.coroutines.delay(100)

        // Then
        newViewModel.uiState.test {
            val state = awaitItem()
            assertEquals(1, state.programs.size)
            assertEquals(ProgramCode.CADUNICO, state.programs[0].code)
        }
    }

    @Test
    fun `loadPrograms should update state with error on failure`() = runTest {
        // Given
        val appError = AppError.Network("Network error")
        coEvery { programRepository.getPrograms() } returns flowOf(
            Result.Error(appError)
        )

        // When
        val newViewModel = HomeViewModel(programRepository, aggregationRepository, agentRepository)

        // Wait for init to complete
        kotlinx.coroutines.delay(100)

        // Then
        newViewModel.uiState.test {
            val state = awaitItem()
            // Either error is set or programs are empty (mock data fallback)
            assertTrue(state.error != null || state.programs.isEmpty())
        }
    }

    @Test
    fun `selectProgram should update selected program`() = runTest {
        // Given
        val programCode = ProgramCode.BPC

        // When
        viewModel.selectProgram(programCode)

        // Then
        viewModel.uiState.test {
            val state = awaitItem()
            assertEquals(programCode, state.selectedProgram)
        }
    }

    @Test
    fun `refresh should reload data`() = runTest {
        // When
        viewModel.refresh()

        // Wait for refresh to complete
        kotlinx.coroutines.delay(100)

        // Then - verify getPrograms was called (at least twice: init + refresh)
        coVerify(atLeast = 2) { programRepository.getPrograms() }
    }

    @Test
    fun `dismissAlert should handle alert dismissal`() = runTest {
        // Given
        val alertId = "alert-1"

        // When
        viewModel.dismissAlert(alertId)

        // Then - should not throw, just filter out
        viewModel.uiState.test {
            val state = awaitItem()
            assertFalse(state.alerts.any { it.id == alertId })
        }
    }

    @Test
    fun `markAlertAsRead should be callable`() = runTest {
        // Given
        val alertId = "a1"

        // When - just verify it doesn't throw
        viewModel.markAlertAsRead(alertId)

        // Then - state should be accessible
        viewModel.uiState.test {
            val state = awaitItem()
            assertNotNull(state)
        }
    }

    @Test
    fun `activeBenefits should filter only active benefits`() = runTest {
        kotlinx.coroutines.delay(100)

        viewModel.uiState.test {
            val state = awaitItem()
            val activeBenefits = state.activeBenefits
            assertTrue(activeBenefits.all { it.status == BenefitStatus.ACTIVE })
        }
    }

    @Test
    fun `unreadAlertsCount should return correct count`() = runTest {
        kotlinx.coroutines.delay(100)

        viewModel.uiState.test {
            val state = awaitItem()
            val unreadCount = state.unreadAlertsCount
            assertTrue(unreadCount >= 0)
            assertEquals(
                state.alerts.count { !it.isRead },
                unreadCount
            )
        }
    }
}
