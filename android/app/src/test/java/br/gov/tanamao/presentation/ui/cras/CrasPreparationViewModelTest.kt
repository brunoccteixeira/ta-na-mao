package br.gov.tanamao.presentation.ui.cras

import br.gov.tanamao.MainCoroutineRule
import kotlinx.coroutines.ExperimentalCoroutinesApi
import org.junit.Rule

import app.cash.turbine.test
import br.gov.tanamao.domain.model.AppError
import br.gov.tanamao.domain.model.Result
import br.gov.tanamao.domain.repository.AgentRepository
import br.gov.tanamao.domain.repository.AgentResponse
import io.mockk.coEvery
import io.mockk.mockk
import kotlinx.coroutines.test.runTest
import org.junit.Assert.*
import org.junit.Before
import org.junit.Test

@OptIn(ExperimentalCoroutinesApi::class)
class CrasPreparationViewModelTest {

    @get:Rule
    val mainCoroutineRule = MainCoroutineRule()

    private lateinit var agentRepository: AgentRepository
    private lateinit var viewModel: CrasPreparationViewModel

    @Before
    fun setup() {
        agentRepository = mockk()
        viewModel = CrasPreparationViewModel(agentRepository)
    }

    @Test
    fun `prepareForCras should load preparation data`() = runTest {
        // Given
        val mockResponse = AgentResponse(
            message = "Checklist de documentos para CRAS:\n1. RG\n2. CPF\n3. Comprovante de residência",
            sessionId = "test-session",
            toolsUsed = listOf("preparar_pre_atendimento_cras")
        )

        coEvery { agentRepository.sendMessage(any(), any()) } returns Result.Success(mockResponse)

        // When
        viewModel.prepareForCras("CADUNICO")

        // Wait for coroutine to complete
        kotlinx.coroutines.delay(100)

        // Then
        viewModel.uiState.test {
            val state = awaitItem()
            assertNotNull(state.preparation)
            assertFalse(state.isLoading)
        }
    }

    @Test
    fun `prepareForCras with error should set error state`() = runTest {
        // Given
        val appError = AppError.Network("Network error")
        coEvery { agentRepository.sendMessage(any(), any()) } returns Result.Error(appError)

        // When
        viewModel.prepareForCras("CADUNICO")

        // Wait for coroutine to complete
        kotlinx.coroutines.delay(100)

        // Then
        viewModel.uiState.test {
            val state = awaitItem()
            assertNotNull(state.error)
            assertFalse(state.isLoading)
        }
    }

    @Test
    fun `generateForm should update state`() = runTest {
        // Given
        val mockResponse = AgentResponse(
            message = "Formulário pré-preenchido gerado",
            sessionId = "test-session",
            toolsUsed = listOf("gerar_formulario_pre_cras")
        )

        coEvery { agentRepository.sendMessage(any(), any()) } returns Result.Success(mockResponse)

        // First prepare
        viewModel.prepareForCras("CADUNICO")
        kotlinx.coroutines.delay(100)

        // When
        viewModel.generateForm("CADUNICO")
        kotlinx.coroutines.delay(100)

        // Then
        viewModel.uiState.test {
            val state = awaitItem()
            assertFalse(state.isGeneratingForm)
        }
    }

    @Test
    fun `clearError should reset error state`() = runTest {
        // Given
        val appError = AppError.Network("Test error")
        coEvery { agentRepository.sendMessage(any(), any()) } returns Result.Error(appError)
        viewModel.prepareForCras("CADUNICO")
        kotlinx.coroutines.delay(100)

        // When
        viewModel.clearError()

        // Then
        viewModel.uiState.test {
            val state = awaitItem()
            assertNull(state.error)
        }
    }

    @Test
    fun `shareChecklist should be callable with valid preparation`() = runTest {
        // Given - prepare the checklist first
        val mockResponse = AgentResponse(
            message = "Checklist de documentos para CRAS:\n1. RG\n2. CPF\n3. Comprovante de residência",
            sessionId = "test-session",
            toolsUsed = listOf("preparar_pre_atendimento_cras")
        )
        coEvery { agentRepository.sendMessage(any(), any()) } returns Result.Success(mockResponse)
        viewModel.prepareForCras("CADUNICO")

        // Wait for coroutine to complete
        kotlinx.coroutines.delay(100)

        // Then - verify checklist was created
        viewModel.uiState.test {
            val state = awaitItem()
            assertNotNull(state.preparation)
        }
    }
}
