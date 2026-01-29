package br.gov.tanamao.presentation.ui.benefit

import br.gov.tanamao.MainCoroutineRule
import kotlinx.coroutines.ExperimentalCoroutinesApi
import org.junit.Rule

import app.cash.turbine.test
import br.gov.tanamao.domain.model.*
import br.gov.tanamao.domain.model.Result
import br.gov.tanamao.domain.model.AppError
import br.gov.tanamao.domain.model.BenefitDetail
import br.gov.tanamao.domain.model.ContactInfo
import br.gov.tanamao.domain.model.ContactType
import br.gov.tanamao.domain.model.FaqItem
import br.gov.tanamao.domain.repository.WalletRepository
import io.mockk.coEvery
import io.mockk.mockk
import kotlinx.coroutines.test.runTest
import org.junit.Assert.*
import org.junit.Before
import org.junit.Test
import androidx.lifecycle.SavedStateHandle

@OptIn(ExperimentalCoroutinesApi::class)
class BenefitDetailViewModelTest {

    @get:Rule
    val mainCoroutineRule = MainCoroutineRule()

    private lateinit var walletRepository: WalletRepository
    private lateinit var savedStateHandle: SavedStateHandle
    private lateinit var viewModel: BenefitDetailViewModel

    @Before
    fun setup() {
        walletRepository = mockk()
        savedStateHandle = SavedStateHandle(mapOf("benefitId" to "BOLSA_FAMILIA"))
    }

    @Test
    fun `initial state should load benefit detail`() = runTest {
        // Given
        val mockBenefit = UserBenefit(
            id = "BOLSA_FAMILIA",
            programCode = "BOLSA_FAMILIA",
            programName = "Bolsa Família",
            status = BenefitStatus.ACTIVE,
            monthlyValue = 600.0
        )

        val mockDetail = BenefitDetail(
            benefit = mockBenefit,
            description = "Programa de transferência de renda",
            requirements = listOf("Renda per capita até R$ 218"),
            documents = listOf("RG", "CPF"),
            howToApply = "Cadastre-se no CadÚnico",
            contacts = emptyList(),
            faq = emptyList()
        )

        coEvery { walletRepository.getBenefitDetail("BOLSA_FAMILIA") } returns Result.Success(mockDetail)

        // When
        val newViewModel = BenefitDetailViewModel(walletRepository, savedStateHandle)

        // Wait for init to complete
        kotlinx.coroutines.delay(100)

        // Then
        newViewModel.uiState.test {
            val state = awaitItem()
            assertFalse(state.isLoading)
            assertNotNull(state.benefitDetail)
        }
    }

    @Test
    fun `loadBenefitDetail should use default data on error`() = runTest {
        // Given
        val appError = AppError.Network("Network error")
        coEvery { walletRepository.getBenefitDetail("BOLSA_FAMILIA") } returns Result.Error(appError)

        // When
        val newViewModel = BenefitDetailViewModel(walletRepository, savedStateHandle)

        // Wait for init to complete
        kotlinx.coroutines.delay(100)

        // Then
        newViewModel.uiState.test {
            val state = awaitItem()
            assertFalse(state.isLoading)
            // Default data should be loaded
            assertNotNull(state.benefitDetail)
        }
    }

    @Test
    fun `toggleFaqExpanded should expand and collapse FAQ items`() = runTest {
        // Given
        val mockDetail = BenefitDetail(
            benefit = UserBenefit(
                id = "BOLSA_FAMILIA",
                programCode = "BOLSA_FAMILIA",
                programName = "Bolsa Família",
                status = BenefitStatus.ACTIVE
            ),
            description = "Test",
            requirements = emptyList(),
            documents = emptyList(),
            howToApply = "Test",
            contacts = emptyList(),
            faq = listOf(
                FaqItem("Pergunta 1", "Resposta 1"),
                FaqItem("Pergunta 2", "Resposta 2")
            )
        )

        coEvery { walletRepository.getBenefitDetail("BOLSA_FAMILIA") } returns Result.Success(mockDetail)

        // When
        viewModel = BenefitDetailViewModel(walletRepository, savedStateHandle)

        // Wait for init to complete
        kotlinx.coroutines.delay(100)

        viewModel.toggleFaqExpanded(0)

        // Then
        viewModel.uiState.test {
            val state = awaitItem()
            assertTrue(state.expandedFaqIndex.contains(0))
        }

        // Toggle again to collapse
        viewModel.toggleFaqExpanded(0)

        viewModel.uiState.test {
            val state = awaitItem()
            assertFalse(state.expandedFaqIndex.contains(0))
        }
    }

    @Test
    fun `refresh should reload benefit detail`() = runTest {
        // Given
        val mockDetail = BenefitDetail(
            benefit = UserBenefit(
                id = "BOLSA_FAMILIA",
                programCode = "BOLSA_FAMILIA",
                programName = "Bolsa Família",
                status = BenefitStatus.ACTIVE
            ),
            description = "Test",
            requirements = emptyList(),
            documents = emptyList(),
            howToApply = "Test",
            contacts = emptyList(),
            faq = emptyList()
        )

        coEvery { walletRepository.getBenefitDetail("BOLSA_FAMILIA") } returns Result.Success(mockDetail)

        // When
        viewModel = BenefitDetailViewModel(walletRepository, savedStateHandle)

        kotlinx.coroutines.delay(100)

        viewModel.refresh()

        kotlinx.coroutines.delay(100)

        // Then - refresh should reload data
        viewModel.uiState.test {
            val state = awaitItem()
            assertFalse(state.isLoading)
            assertNotNull(state.benefitDetail)
        }
    }

    @Test
    fun `state should provide computed properties correctly`() = runTest {
        // Given
        val mockBenefit = UserBenefit(
            id = "BOLSA_FAMILIA",
            programCode = "BOLSA_FAMILIA",
            programName = "Bolsa Família",
            status = BenefitStatus.ACTIVE,
            monthlyValue = 600.0
        )

        val mockDetail = BenefitDetail(
            benefit = mockBenefit,
            description = "Programa de transferência",
            requirements = listOf("Renda até R$ 218"),
            documents = listOf("RG", "CPF"),
            howToApply = "Cadastre-se no CadÚnico",
            contacts = listOf(
                ContactInfo(ContactType.PHONE, "121", "Disque Social")
            ),
            faq = listOf(
                FaqItem("Quando recebo?", "Últimos 10 dias úteis")
            )
        )

        coEvery { walletRepository.getBenefitDetail("BOLSA_FAMILIA") } returns Result.Success(mockDetail)

        // When
        viewModel = BenefitDetailViewModel(walletRepository, savedStateHandle)

        kotlinx.coroutines.delay(100)

        // Then
        viewModel.uiState.test {
            val state = awaitItem()
            assertEquals("Bolsa Família", state.programName)
            assertEquals("Programa de transferência", state.description)
            assertEquals(1, state.requirements.size)
            assertEquals(2, state.documents.size)
            assertEquals("Cadastre-se no CadÚnico", state.howToApply)
            assertEquals(1, state.contacts.size)
            assertEquals(1, state.faq.size)
        }
    }
}
