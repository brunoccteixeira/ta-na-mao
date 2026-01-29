package br.gov.tanamao.presentation.ui.home

import androidx.lifecycle.ViewModel
import androidx.lifecycle.viewModelScope
import br.gov.tanamao.domain.model.*
import br.gov.tanamao.domain.repository.AggregationRepository
import br.gov.tanamao.domain.repository.ProgramRepository
import br.gov.tanamao.domain.repository.AgentRepository
import br.gov.tanamao.presentation.util.AgentResponseParser
import dagger.hilt.android.lifecycle.HiltViewModel
import kotlinx.coroutines.flow.*
import kotlinx.coroutines.launch
import java.time.LocalDate
import javax.inject.Inject

@HiltViewModel
class HomeViewModel @Inject constructor(
    private val programRepository: ProgramRepository,
    private val aggregationRepository: AggregationRepository,
    private val agentRepository: AgentRepository
) : ViewModel() {

    private val _uiState = MutableStateFlow(HomeUiState())
    val uiState: StateFlow<HomeUiState> = _uiState.asStateFlow()

    init {
        loadData()
        loadUserData() // Load real user data from agent
    }

    fun selectProgram(code: ProgramCode?) {
        _uiState.update { it.copy(selectedProgram = code) }
        loadNationalStats(code)
    }

    fun refresh() {
        loadData()
        loadUserData()
    }

    fun dismissAlert(alertId: String) {
        _uiState.update { state ->
            state.copy(
                alerts = state.alerts.filterNot { it.id == alertId }
            )
        }
    }

    fun markAlertAsRead(alertId: String) {
        _uiState.update { state ->
            state.copy(
                alerts = state.alerts.map { alert ->
                    if (alert.id == alertId) alert.copy(isRead = true) else alert
                }
            )
        }
    }

    private fun loadData() {
        loadPrograms()
        loadNationalStats(_uiState.value.selectedProgram)
    }

    private fun loadPrograms() {
        viewModelScope.launch {
            programRepository.getPrograms().collect { result ->
                when (result) {
                    is Result.Loading -> {
                        _uiState.update { it.copy(isLoading = true) }
                    }
                    is Result.Success -> {
                        _uiState.update {
                            it.copy(
                                isLoading = false,
                                programs = result.data,
                                error = null
                            )
                        }
                    }
                    is Result.Error -> {
                        _uiState.update {
                            it.copy(
                                isLoading = false,
                                error = result.exception.getUserMessage()
                            )
                        }
                    }
                }
            }
        }
    }

    private fun loadNationalStats(program: ProgramCode?) {
        viewModelScope.launch {
            _uiState.update { it.copy(isLoading = true) }

            when (val result = aggregationRepository.getNational(program)) {
                is Result.Success -> {
                    _uiState.update {
                        it.copy(
                            isLoading = false,
                            nationalStats = result.data,
                            error = null
                        )
                    }
                }
                is Result.Error -> {
                    _uiState.update {
                        it.copy(
                            isLoading = false,
                            error = result.exception.getUserMessage()
                        )
                    }
                }
                is Result.Loading -> {
                    // Already handled above
                }
            }
        }
    }

    /**
     * Load user data from agent (meus_dados and gerar_alertas_beneficios)
     */
    private fun loadUserData() {
        viewModelScope.launch {
            // Load consolidated user data
            loadConsolidatedUserData()
            
            // Load proactive alerts
            loadProactiveAlerts()
        }
    }

    private suspend fun loadConsolidatedUserData() {
        // Call agent with "meus dados" to get consolidated view
        when (val result = agentRepository.sendMessage("meus dados", "")) {
            is Result.Success -> {
                val response = result.data.message
                // Parse response using improved parser
                val benefits = AgentResponseParser.parseUserBenefits(response)
                val parsedData = parseUserDataResponse(response, benefits)
                _uiState.update { state ->
                    state.copy(
                        userBenefits = parsedData.benefits,
                        walletSummary = parsedData.walletSummary,
                        userName = parsedData.userName
                    )
                }
            }
            is Result.Error -> {
                // Fallback to mock data if agent fails
                loadMockUserData()
            }
            Result.Loading -> {
                // Keep loading state
            }
        }
    }

    private suspend fun loadProactiveAlerts() {
        // Call agent with "meus alertas" to get proactive alerts
        when (val result = agentRepository.sendMessage("meus alertas", "")) {
            is Result.Success -> {
                val response = result.data.message
                // Use improved parser
                val alerts = AgentResponseParser.parseAlerts(response)
                _uiState.update { state ->
                    state.copy(alerts = alerts)
                }
            }
            is Result.Error -> {
                // Fallback to mock alerts if agent fails
                // Alerts will be loaded from mock data if needed
            }
            Result.Loading -> {
                // Keep loading state
            }
        }
    }

    /**
     * Parse user data response from agent
     */
    private fun parseUserDataResponse(response: String, parsedBenefits: List<UserBenefit>): ParsedUserData {
        // Use benefits already parsed by AgentResponseParser
        val benefits = parsedBenefits.toMutableList()
        var walletSummary: WalletSummary? = null
        var userName: String? = null
        
        // Benefits already parsed by AgentResponseParser
        
        // Extract total monthly value
        val totalPattern = Regex("""total[:\s]+R\$\s*([\d.,]+)""", RegexOption.IGNORE_CASE)
        val totalMatch = totalPattern.find(response)
        val totalValue = AgentResponseParser.parseBrazilianCurrency(totalMatch?.groupValues?.get(1)) ?: 0.0
        
        if (totalValue > 0 || benefits.isNotEmpty()) {
            walletSummary = WalletSummary(
                totalMonthlyValue = totalValue,
                activeBenefitsCount = benefits.size,
                eligibleBenefitsCount = 0,
                pendingBenefitsCount = 0,
                nextPaymentDate = null,
                nextPaymentValue = totalValue
            )
        }
        
        // Extract user name if present
        val namePattern = Regex("""(?:Olá|Oi|Olá,)\s+([A-Z][a-z]+)""", RegexOption.IGNORE_CASE)
        val nameMatch = namePattern.find(response)
        userName = nameMatch?.groupValues?.get(1)
        
        return ParsedUserData(
            benefits = benefits,
            walletSummary = walletSummary,
            userName = userName
        )
    }

    // Alerts parsing moved to AgentResponseParser

    /**
     * Data class for parsed user data
     */
    private data class ParsedUserData(
        val benefits: List<UserBenefit>,
        val walletSummary: WalletSummary?,
        val userName: String?
    )

    /**
     * Fallback mock data if agent is unavailable
     */
    private fun loadMockUserData() {
        val mockBenefits = listOf(
            UserBenefit(
                id = "1",
                programCode = "BOLSA_FAMILIA",
                programName = "Bolsa Família",
                status = BenefitStatus.ACTIVE,
                monthlyValue = 600.0,
                nextPaymentDate = LocalDate.now().plusDays(15)
            ),
            UserBenefit(
                id = "2",
                programCode = "BPC",
                programName = "BPC/LOAS",
                status = BenefitStatus.ACTIVE,
                monthlyValue = 1412.0,
                nextPaymentDate = LocalDate.now().plusDays(10)
            ),
            UserBenefit(
                id = "3",
                programCode = "FARMACIA_POPULAR",
                programName = "Farmácia Popular",
                status = BenefitStatus.ACTIVE,
                monthlyValue = null
            ),
            UserBenefit(
                id = "4",
                programCode = "TSEE",
                programName = "Tarifa Social",
                status = BenefitStatus.PENDING
            )
        )

        val mockAlerts = listOf(
            UserAlert(
                id = "a1",
                type = AlertCategory.ACTION_REQUIRED,
                title = "Medicamento acabando!",
                message = "Sua Losartana (hipertensão) deve acabar em 5 dias. Retire mais na farmácia.",
                actionLabel = "Buscar farmácia",
                actionRoute = "chat",
                createdAt = LocalDate.now(),
                priority = AlertPriority.HIGH
            ),
            UserAlert(
                id = "a2",
                type = AlertCategory.NEW_BENEFIT,
                title = "Você pode ter direito a uma ajuda!",
                message = "Você pode receber ajuda para idosos ou pessoas com deficiência. Descubra agora.",
                actionLabel = "Tenho direito?",
                actionRoute = "chat",
                createdAt = LocalDate.now(),
                priority = AlertPriority.HIGH
            ),
            UserAlert(
                id = "a3",
                type = AlertCategory.PAYMENT,
                title = "Pagamento confirmado",
                message = "Bolsa Família de R$ 600,00 disponível em 15 dias.",
                createdAt = LocalDate.now().minusDays(1),
                priority = AlertPriority.NORMAL
            )
        )

        val mockWalletSummary = WalletSummary(
            totalMonthlyValue = 600.0,
            activeBenefitsCount = 2,
            eligibleBenefitsCount = 1,
            pendingBenefitsCount = 1,
            nextPaymentDate = LocalDate.now().plusDays(5),
            nextPaymentValue = 600.0
        )

        _uiState.update {
            it.copy(
                userBenefits = mockBenefits,
                alerts = mockAlerts,
                walletSummary = mockWalletSummary,
                userName = "Maria"
            )
        }
    }
}

data class HomeUiState(
    // Loading and error states
    val isLoading: Boolean = false,
    val error: String? = null,

    // User info
    val userName: String? = null,

    // Program data (existing)
    val programs: List<Program> = emptyList(),
    val selectedProgram: ProgramCode? = null,
    val nationalStats: NationalStats? = null,

    // User benefits (new - for Propel-style home)
    val userBenefits: List<UserBenefit> = emptyList(),
    val alerts: List<UserAlert> = emptyList(),
    val walletSummary: WalletSummary? = null
) {
    val activeBenefits: List<UserBenefit>
        get() = userBenefits.filter { it.status == BenefitStatus.ACTIVE }

    val eligibleBenefits: List<UserBenefit>
        get() = userBenefits.filter { it.status == BenefitStatus.ELIGIBLE }

    val unreadAlertsCount: Int
        get() = alerts.count { !it.isRead }

    val highPriorityAlert: UserAlert?
        get() = alerts.firstOrNull { it.priority == AlertPriority.HIGH || it.priority == AlertPriority.URGENT }
}
