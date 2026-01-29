package br.gov.tanamao.presentation.ui.profile

import br.gov.tanamao.MainCoroutineRule
import kotlinx.coroutines.ExperimentalCoroutinesApi
import org.junit.Rule

import app.cash.turbine.test
import br.gov.tanamao.domain.model.*
import br.gov.tanamao.domain.model.Result
import br.gov.tanamao.domain.model.AppError
import br.gov.tanamao.domain.repository.AgentRepository
import br.gov.tanamao.domain.repository.AgentResponse
import br.gov.tanamao.data.local.repository.ConsultationHistoryRepository
import br.gov.tanamao.data.local.repository.UserDataCacheRepository
import io.mockk.coEvery
import io.mockk.coVerify
import io.mockk.every
import io.mockk.mockk
import kotlinx.coroutines.flow.flowOf
import kotlinx.coroutines.test.runTest
import org.junit.Assert.*
import org.junit.Before
import org.junit.Test
import java.time.LocalDate

@OptIn(ExperimentalCoroutinesApi::class)
class ProfileViewModelTest {

    @get:Rule
    val mainCoroutineRule = MainCoroutineRule()

    private lateinit var agentRepository: AgentRepository
    private lateinit var consultationHistoryRepository: ConsultationHistoryRepository
    private lateinit var userDataCacheRepository: UserDataCacheRepository
    private lateinit var viewModel: ProfileViewModel

    @Before
    fun setup() {
        agentRepository = mockk()
        consultationHistoryRepository = mockk()
        userDataCacheRepository = mockk()

        // Mock default behaviors
        every { consultationHistoryRepository.getAllHistory() } returns flowOf(emptyList())
        coEvery { consultationHistoryRepository.getCount() } returns 0
        coEvery { consultationHistoryRepository.saveAll(any()) } returns Unit
        coEvery { userDataCacheRepository.getCachedUserData() } returns null
        coEvery { userDataCacheRepository.saveUserData(any()) } returns Unit

        // Mock para loadProfileData() chamado no init{}
        coEvery { agentRepository.sendMessage("meus dados", "") } returns Result.Success(
            AgentResponse(
                message = "Olá, Usuário. Você recebe Bolsa Família: R$ 600,00. Total recebido: R$ 12000,00",
                sessionId = "test-session",
                toolsUsed = listOf("meus_dados")
            )
        )
    }

    @Test
    fun `initial state should be loading then loaded`() = runTest {
        // When
        val newViewModel = ProfileViewModel(
            agentRepository,
            consultationHistoryRepository,
            userDataCacheRepository
        )

        // Wait for init to complete
        kotlinx.coroutines.delay(100)

        // Then
        newViewModel.uiState.test {
            val state = awaitItem()
            // After init completes, loading should be false
            assertFalse(state.isLoading)
        }
    }

    @Test
    fun `loadProfileData should update state with user data on success`() = runTest {
        // Given
        val mockResponse = AgentResponse(
            message = "Olá, Maria. Você recebe Bolsa Família: R$ 600,00. Total recebido: R$ 12000,00",
            sessionId = "test-session",
            toolsUsed = listOf("meus_dados")
        )

        coEvery { agentRepository.sendMessage("meus dados", "") } returns Result.Success(mockResponse)

        // When
        val newViewModel = ProfileViewModel(
            agentRepository,
            consultationHistoryRepository,
            userDataCacheRepository
        )

        // Wait for init to complete
        kotlinx.coroutines.delay(100)

        // Then
        newViewModel.uiState.test {
            val state = awaitItem()
            assertFalse(state.isLoading)
            assertNotNull(state.userName)
        }
    }

    @Test
    fun `loadProfileData should use mock data on error`() = runTest {
        // Given
        val appError = AppError.Network("Network error")
        coEvery { agentRepository.sendMessage(any(), any()) } returns Result.Error(appError)

        // When
        val newViewModel = ProfileViewModel(
            agentRepository,
            consultationHistoryRepository,
            userDataCacheRepository
        )

        // Wait for init to complete
        kotlinx.coroutines.delay(100)

        // Then
        newViewModel.uiState.test {
            val state = awaitItem()
            assertFalse(state.isLoading)
            // Mock data should be loaded
            assertNotNull(state.userName)
        }
    }

    @Test
    fun `refresh should reload profile data`() = runTest {
        // Given
        val mockResponse = AgentResponse(
            message = "Olá, João. Você recebe BPC: R$ 1412,00",
            sessionId = "test-session",
            toolsUsed = listOf("meus_dados")
        )

        coEvery { agentRepository.sendMessage("meus dados", "") } returns Result.Success(mockResponse)

        // When
        viewModel = ProfileViewModel(
            agentRepository,
            consultationHistoryRepository,
            userDataCacheRepository
        )

        kotlinx.coroutines.delay(100)
        viewModel.refresh()
        kotlinx.coroutines.delay(100)

        // Then
        coVerify(atLeast = 2) { agentRepository.sendMessage("meus dados", "") }
    }

    @Test
    fun `checkForgottenMoney should update state with money info`() = runTest {
        // Given
        val mockResponse = AgentResponse(
            message = "Você tem R$ 500,00 disponível no PIS/PASEP e R$ 200,00 no SVR",
            sessionId = "test-session",
            toolsUsed = listOf("consultar_dinheiro_esquecido")
        )

        coEvery { agentRepository.sendMessage("consultar dinheiro esquecido", "") } returns Result.Success(mockResponse)

        // When
        viewModel = ProfileViewModel(
            agentRepository,
            consultationHistoryRepository,
            userDataCacheRepository
        )

        kotlinx.coroutines.delay(100)
        viewModel.checkForgottenMoney()
        kotlinx.coroutines.delay(100)

        // Then
        viewModel.uiState.test {
            val state = awaitItem()
            assertNotNull(state.forgottenMoney)
            assertFalse(state.isLoading)
        }
    }

    @Test
    fun `checkForgottenMoney with error should set error state`() = runTest {
        // Given
        val appError = AppError.Network("Network error")
        coEvery { agentRepository.sendMessage("consultar dinheiro esquecido", "") } returns Result.Error(appError)

        // When
        viewModel = ProfileViewModel(
            agentRepository,
            consultationHistoryRepository,
            userDataCacheRepository
        )

        kotlinx.coroutines.delay(100)
        viewModel.checkForgottenMoney()
        kotlinx.coroutines.delay(100)

        // Then
        viewModel.uiState.test {
            val state = awaitItem()
            assertNotNull(state.error)
            assertFalse(state.isLoading)
        }
    }

    @Test
    fun `exportUserData should generate formatted report`() = runTest {
        // Given
        val mockResponse = AgentResponse(
            message = "Olá, Maria. Você recebe Bolsa Família: R$ 600,00",
            sessionId = "test-session",
            toolsUsed = listOf("meus_dados")
        )

        coEvery { agentRepository.sendMessage("meus dados", "") } returns Result.Success(mockResponse)

        // When
        viewModel = ProfileViewModel(
            agentRepository,
            consultationHistoryRepository,
            userDataCacheRepository
        )

        // Wait for data to load
        kotlinx.coroutines.delay(100)

        val exportedData = viewModel.exportUserData()

        // Then
        assertTrue(exportedData.contains("DADOS DO USUÁRIO"))
    }

    @Test
    fun `loadConsultationHistory should update state with history`() = runTest {
        // Given
        val mockHistory = listOf(
            ConsultationHistory(
                id = "1",
                date = LocalDate.now().minusDays(1),
                type = ConsultationType.MONEY_CHECK,
                query = "verificar dinheiro",
                result = "Encontrado R$ 500,00",
                toolsUsed = listOf("consultar_dinheiro_esquecido"),
                success = true
            )
        )

        every { consultationHistoryRepository.getAllHistory() } returns flowOf(mockHistory)
        coEvery { consultationHistoryRepository.getCount() } returns 1

        // When
        val newViewModel = ProfileViewModel(
            agentRepository,
            consultationHistoryRepository,
            userDataCacheRepository
        )

        // Wait for init to complete
        kotlinx.coroutines.delay(100)

        // Then
        newViewModel.uiState.test {
            val state = awaitItem()
            assertEquals(1, state.consultationHistory.size)
            assertEquals(ConsultationType.MONEY_CHECK, state.consultationHistory[0].type)
        }
    }
}
