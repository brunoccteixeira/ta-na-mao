package br.gov.tanamao.presentation.ui.wallet

import androidx.lifecycle.ViewModel
import androidx.lifecycle.viewModelScope
import br.gov.tanamao.domain.model.*
import br.gov.tanamao.domain.repository.WalletRepository
import dagger.hilt.android.lifecycle.HiltViewModel
import kotlinx.coroutines.flow.*
import kotlinx.coroutines.launch
import java.time.LocalDate
import java.time.YearMonth
import javax.inject.Inject

@HiltViewModel
class WalletViewModel @Inject constructor(
    private val walletRepository: WalletRepository
) : ViewModel() {

    private val _uiState = MutableStateFlow(WalletUiState())
    val uiState: StateFlow<WalletUiState> = _uiState.asStateFlow()

    init {
        loadWalletData()
    }

    fun selectTab(tab: WalletTab) {
        _uiState.update { it.copy(selectedTab = tab) }
    }

    fun refresh() {
        loadWalletData()
    }

    fun selectBenefit(benefitId: String) {
        _uiState.update { it.copy(selectedBenefitId = benefitId) }
    }

    fun clearSelectedBenefit() {
        _uiState.update { it.copy(selectedBenefitId = null) }
    }

    private fun loadWalletData() {
        viewModelScope.launch {
            _uiState.update { it.copy(isLoading = true) }

            when (val result = walletRepository.getWallet()) {
                is Result.Success -> {
                    val wallet = result.data
                    _uiState.update {
                        it.copy(
                            isLoading = false,
                            walletSummary = wallet.summary,
                            activeBenefits = wallet.activeBenefits,
                            eligibleBenefits = wallet.eligibleBenefits,
                            pendingBenefits = wallet.pendingBenefits,
                            paymentHistory = wallet.paymentHistory.groupByMonth(),
                            error = null
                        )
                    }
                }
                is Result.Error -> {
                    // Fallback to mock data if API fails
                    loadMockData()
                    _uiState.update {
                        it.copy(
                            isLoading = false,
                            error = result.exception.getUserMessage()
                        )
                    }
                }
                Result.Loading -> {
                    _uiState.update { it.copy(isLoading = true) }
                }
            }
        }
    }

    /**
     * Fallback mock data when API is unavailable
     */
    private fun loadMockData() {
        val activeBenefits = listOf(
            UserBenefit(
                id = "1",
                programCode = "BOLSA_FAMILIA",
                programName = "Bolsa Familia",
                status = BenefitStatus.ACTIVE,
                monthlyValue = 600.0,
                lastPaymentDate = LocalDate.now().minusDays(10),
                nextPaymentDate = LocalDate.now().plusDays(20)
            ),
            UserBenefit(
                id = "2",
                programCode = "FARMACIA_POPULAR",
                programName = "Farmacia Popular",
                status = BenefitStatus.ACTIVE,
                monthlyValue = null
            ),
            UserBenefit(
                id = "3",
                programCode = "TSEE",
                programName = "Tarifa Social de Energia",
                status = BenefitStatus.ACTIVE,
                monthlyValue = 80.0
            )
        )

        val eligibleBenefits = listOf(
            UserBenefit(
                id = "4",
                programCode = "BPC",
                programName = "BPC/LOAS",
                status = BenefitStatus.ELIGIBLE,
                monthlyValue = 1412.0,
                eligibilityDetails = EligibilityDetails(
                    criteria = listOf(
                        EligibilityCriterion("Idade", "Pessoa com 65 anos ou mais", true),
                        EligibilityCriterion("Renda", "Renda per capita inferior a 1/4 do salario minimo", true),
                        EligibilityCriterion("CadUnico", "Cadastro atualizado no CadUnico", true)
                    ),
                    assessmentDate = LocalDate.now(),
                    overallScore = 0.95f,
                    recommendation = "Voce atende aos criterios principais. Recomendamos iniciar a solicitacao."
                )
            ),
            UserBenefit(
                id = "5",
                programCode = "DIGNIDADE_MENSTRUAL",
                programName = "Dignidade Menstrual",
                status = BenefitStatus.ELIGIBLE,
                monthlyValue = null
            )
        )

        val pendingBenefits = listOf(
            UserBenefit(
                id = "6",
                programCode = "PIS_PASEP",
                programName = "Abono Salarial PIS/PASEP",
                status = BenefitStatus.PENDING,
                monthlyValue = 1412.0
            )
        )

        val paymentHistory = listOf(
            PaymentHistoryItem(
                id = "p1",
                programCode = "BOLSA_FAMILIA",
                programName = "Bolsa Familia",
                date = LocalDate.now().minusDays(10),
                value = 600.0,
                reference = YearMonth.now().minusMonths(1),
                status = PaymentStatus.PAID
            ),
            PaymentHistoryItem(
                id = "p2",
                programCode = "TSEE",
                programName = "Tarifa Social",
                date = LocalDate.now().minusDays(10),
                value = 80.0,
                reference = YearMonth.now().minusMonths(1),
                status = PaymentStatus.PAID
            ),
            PaymentHistoryItem(
                id = "p3",
                programCode = "BOLSA_FAMILIA",
                programName = "Bolsa Familia",
                date = LocalDate.now().minusMonths(1).minusDays(10),
                value = 600.0,
                reference = YearMonth.now().minusMonths(2),
                status = PaymentStatus.PAID
            ),
            PaymentHistoryItem(
                id = "p4",
                programCode = "TSEE",
                programName = "Tarifa Social",
                date = LocalDate.now().minusMonths(1).minusDays(10),
                value = 80.0,
                reference = YearMonth.now().minusMonths(2),
                status = PaymentStatus.PAID
            ),
            PaymentHistoryItem(
                id = "p5",
                programCode = "BOLSA_FAMILIA",
                programName = "Bolsa Familia",
                date = LocalDate.now().minusMonths(2).minusDays(10),
                value = 600.0,
                reference = YearMonth.now().minusMonths(3),
                status = PaymentStatus.PAID
            )
        )

        val walletSummary = WalletSummary(
            totalMonthlyValue = 680.0,
            activeBenefitsCount = activeBenefits.size,
            eligibleBenefitsCount = eligibleBenefits.size,
            pendingBenefitsCount = pendingBenefits.size,
            nextPaymentDate = LocalDate.now().plusDays(20),
            nextPaymentValue = 600.0
        )

        _uiState.update {
            it.copy(
                isLoading = false,
                walletSummary = walletSummary,
                activeBenefits = activeBenefits,
                eligibleBenefits = eligibleBenefits,
                pendingBenefits = pendingBenefits,
                paymentHistory = paymentHistory.groupByMonth(),
                error = null
            )
        }
    }
}

enum class WalletTab {
    ACTIVE,
    ELIGIBLE,
    HISTORY
}

data class WalletUiState(
    val isLoading: Boolean = false,
    val error: String? = null,
    val selectedTab: WalletTab = WalletTab.ACTIVE,
    val selectedBenefitId: String? = null,

    // Wallet data
    val walletSummary: WalletSummary? = null,
    val activeBenefits: List<UserBenefit> = emptyList(),
    val eligibleBenefits: List<UserBenefit> = emptyList(),
    val pendingBenefits: List<UserBenefit> = emptyList(),
    val paymentHistory: List<PaymentHistoryGroup> = emptyList()
) {
    val currentTabBenefits: List<UserBenefit>
        get() = when (selectedTab) {
            WalletTab.ACTIVE -> activeBenefits + pendingBenefits
            WalletTab.ELIGIBLE -> eligibleBenefits
            WalletTab.HISTORY -> emptyList()
        }

    val totalHistoryValue: Double
        get() = paymentHistory.sumOf { it.totalValue }
}
