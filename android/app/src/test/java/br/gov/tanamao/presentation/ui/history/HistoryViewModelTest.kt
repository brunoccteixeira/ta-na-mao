package br.gov.tanamao.presentation.ui.history

import br.gov.tanamao.MainCoroutineRule
import kotlinx.coroutines.ExperimentalCoroutinesApi
import org.junit.Rule

import app.cash.turbine.test
import br.gov.tanamao.domain.model.ConsultationHistory
import br.gov.tanamao.domain.model.ConsultationType
import br.gov.tanamao.data.local.repository.ConsultationHistoryRepository
import io.mockk.coEvery
import io.mockk.every
import io.mockk.mockk
import kotlinx.coroutines.flow.flowOf
import kotlinx.coroutines.test.runTest
import org.junit.Assert.*
import org.junit.Before
import org.junit.Test
import java.time.LocalDate

@OptIn(ExperimentalCoroutinesApi::class)
class HistoryViewModelTest {

    @get:Rule
    val mainCoroutineRule = MainCoroutineRule()

    private lateinit var consultationHistoryRepository: ConsultationHistoryRepository
    private lateinit var viewModel: HistoryViewModel

    @Before
    fun setup() {
        consultationHistoryRepository = mockk()
        coEvery { consultationHistoryRepository.getCount() } returns 0
        coEvery { consultationHistoryRepository.saveAll(any()) } returns Unit
        every { consultationHistoryRepository.getAllHistory() } returns flowOf(emptyList())
    }

    @Test
    fun `initial state should be loading`() = runTest {
        // Given
        every { consultationHistoryRepository.getAllHistory() } returns flowOf(emptyList())

        // When
        val newViewModel = HistoryViewModel(consultationHistoryRepository)

        // Then
        newViewModel.uiState.test {
            val state = awaitItem()
            assertTrue(state.isLoading)
        }
    }

    @Test
    fun `loadHistory should update state with history on success`() = runTest {
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
            ),
            ConsultationHistory(
                id = "2",
                date = LocalDate.now().minusDays(2),
                type = ConsultationType.ELIGIBILITY_CHECK,
                query = "tenho direito?",
                result = "Sim, você é elegível",
                toolsUsed = listOf("verificar_elegibilidade"),
                success = true
            )
        )

        every { consultationHistoryRepository.getAllHistory() } returns flowOf(mockHistory)
        coEvery { consultationHistoryRepository.getCount() } returns 2

        // When
        val newViewModel = HistoryViewModel(consultationHistoryRepository)

        // Wait for flow to emit
        kotlinx.coroutines.delay(100)

        // Then
        newViewModel.uiState.test {
            val state = awaitItem()
            assertFalse(state.isLoading)
            assertEquals(2, state.allHistory.size)
        }
    }

    @Test
    fun `setFilter should update selected filter`() = runTest {
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
            ),
            ConsultationHistory(
                id = "2",
                date = LocalDate.now().minusDays(2),
                type = ConsultationType.ELIGIBILITY_CHECK,
                query = "tenho direito?",
                result = "Sim",
                toolsUsed = listOf("verificar_elegibilidade"),
                success = true
            )
        )

        every { consultationHistoryRepository.getAllHistory() } returns flowOf(mockHistory)
        coEvery { consultationHistoryRepository.getCount() } returns 2
        coEvery { consultationHistoryRepository.saveAll(any()) } returns Unit

        // When
        viewModel = HistoryViewModel(consultationHistoryRepository)

        // Wait for initial load
        kotlinx.coroutines.delay(100)

        viewModel.setFilter(HistoryFilter.MONEY)

        // Wait for filter to be applied
        kotlinx.coroutines.delay(50)

        // Then
        viewModel.uiState.test {
            val state = awaitItem()
            assertEquals(HistoryFilter.MONEY, state.selectedFilter)
        }
    }

    @Test
    fun `setFilter ELIGIBILITY should update filter state`() = runTest {
        // Given
        val mockHistory = listOf(
            ConsultationHistory(
                id = "1",
                date = LocalDate.now().minusDays(1),
                type = ConsultationType.MONEY_CHECK,
                query = "verificar dinheiro",
                result = "Encontrado",
                toolsUsed = listOf("consultar_dinheiro_esquecido"),
                success = true
            ),
            ConsultationHistory(
                id = "2",
                date = LocalDate.now().minusDays(2),
                type = ConsultationType.ELIGIBILITY_CHECK,
                query = "tenho direito?",
                result = "Sim",
                toolsUsed = listOf("verificar_elegibilidade"),
                success = true
            )
        )

        every { consultationHistoryRepository.getAllHistory() } returns flowOf(mockHistory)
        coEvery { consultationHistoryRepository.getCount() } returns 2
        coEvery { consultationHistoryRepository.saveAll(any()) } returns Unit

        // When
        viewModel = HistoryViewModel(consultationHistoryRepository)

        kotlinx.coroutines.delay(100)

        viewModel.setFilter(HistoryFilter.ELIGIBILITY)

        kotlinx.coroutines.delay(50)

        // Then
        viewModel.uiState.test {
            val state = awaitItem()
            assertEquals(HistoryFilter.ELIGIBILITY, state.selectedFilter)
        }
    }

    @Test
    fun `refresh should reload history`() = runTest {
        // Given
        val mockHistory = listOf(
            ConsultationHistory(
                id = "1",
                date = LocalDate.now(),
                type = ConsultationType.MONEY_CHECK,
                query = "verificar",
                result = "Encontrado",
                toolsUsed = listOf("consultar_dinheiro_esquecido"),
                success = true
            )
        )

        every { consultationHistoryRepository.getAllHistory() } returns flowOf(mockHistory)
        coEvery { consultationHistoryRepository.getCount() } returns 1

        // When
        viewModel = HistoryViewModel(consultationHistoryRepository)

        kotlinx.coroutines.delay(100)

        viewModel.refresh()

        kotlinx.coroutines.delay(100)

        // Then
        viewModel.uiState.test {
            val state = awaitItem()
            assertFalse(state.isLoading)
            assertEquals(1, state.allHistory.size)
        }
    }

    @Test
    fun `empty database should load mock history`() = runTest {
        // Given
        every { consultationHistoryRepository.getAllHistory() } returns flowOf(emptyList())
        coEvery { consultationHistoryRepository.getCount() } returns 0
        coEvery { consultationHistoryRepository.saveAll(any()) } returns Unit

        // When
        val newViewModel = HistoryViewModel(consultationHistoryRepository)

        // Wait for flow and saveAll to complete
        kotlinx.coroutines.delay(100)

        // Then
        newViewModel.uiState.test {
            val state = awaitItem()
            assertFalse(state.isLoading)
        }
    }
}
