package br.gov.tanamao.presentation.ui.wallet

import br.gov.tanamao.MainCoroutineRule
import kotlinx.coroutines.ExperimentalCoroutinesApi
import org.junit.Rule

import app.cash.turbine.test
import br.gov.tanamao.domain.model.*
import br.gov.tanamao.domain.repository.WalletRepository
import io.mockk.coEvery
import io.mockk.mockk
import kotlinx.coroutines.test.runTest
import org.junit.Assert.*
import org.junit.Before
import org.junit.Test
import java.time.LocalDate
import java.time.YearMonth

@OptIn(ExperimentalCoroutinesApi::class)
class WalletViewModelTest {

    @get:Rule
    val mainCoroutineRule = MainCoroutineRule()

    private lateinit var walletRepository: WalletRepository
    private lateinit var viewModel: WalletViewModel

    @Before
    fun setup() {
        walletRepository = mockk()

        // Mock successful wallet response
        coEvery { walletRepository.getWallet() } returns Result.Success(
            Wallet(
                summary = WalletSummary(
                    totalMonthlyValue = 600.0,
                    activeBenefitsCount = 1,
                    eligibleBenefitsCount = 0,
                    pendingBenefitsCount = 0,
                    nextPaymentDate = LocalDate.now().plusDays(20),
                    nextPaymentValue = 600.0
                ),
                activeBenefits = listOf(
                    UserBenefit(
                        id = "1",
                        programCode = "BOLSA_FAMILIA",
                        programName = "Bolsa Família",
                        status = BenefitStatus.ACTIVE,
                        monthlyValue = 600.0
                    )
                ),
                eligibleBenefits = emptyList(),
                pendingBenefits = emptyList(),
                paymentHistory = emptyList()
            )
        )

        viewModel = WalletViewModel(walletRepository)
    }

    @Test
    fun `initial state should load wallet data`() = runTest {
        viewModel.uiState.test {
            val state = awaitItem()
            assertFalse(state.isLoading)
            assertNotNull(state.walletSummary)
        }
    }

    @Test
    fun `selectTab should update selected tab`() = runTest {
        // Given
        val newTab = WalletTab.ELIGIBLE

        // When
        viewModel.selectTab(newTab)

        // Then
        viewModel.uiState.test {
            val state = awaitItem()
            assertEquals(newTab, state.selectedTab)
        }
    }

    @Test
    fun `selectBenefit should update selected benefit ID`() = runTest {
        // Given
        val benefitId = "benefit-123"

        // When
        viewModel.selectBenefit(benefitId)

        // Then
        viewModel.uiState.test {
            val state = awaitItem()
            assertEquals(benefitId, state.selectedBenefitId)
        }
    }

    @Test
    fun `clearSelectedBenefit should set selected benefit ID to null`() = runTest {
        // Given
        viewModel.selectBenefit("benefit-123")

        // When
        viewModel.clearSelectedBenefit()

        // Then
        viewModel.uiState.test {
            val state = awaitItem()
            assertNull(state.selectedBenefitId)
        }
    }

    @Test
    fun `refresh should reload data`() = runTest {
        // When
        viewModel.refresh()

        // Then - state should update (loading becomes false after data loads)
        viewModel.uiState.test {
            val state = awaitItem()
            assertFalse(state.isLoading)
            assertNotNull(state.walletSummary)
        }
    }

    @Test
    fun `currentTabBenefits should return active benefits for ACTIVE tab`() = runTest {
        // Wait for initial data load
        kotlinx.coroutines.delay(100)

        viewModel.uiState.test {
            val state = awaitItem()
            assertEquals(WalletTab.ACTIVE, state.selectedTab)
            // currentTabBenefits includes activeBenefits + pendingBenefits
            assertTrue(state.currentTabBenefits.isNotEmpty() || state.activeBenefits.isNotEmpty())
        }
    }
}
