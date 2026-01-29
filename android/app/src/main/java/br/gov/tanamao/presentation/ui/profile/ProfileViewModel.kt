package br.gov.tanamao.presentation.ui.profile

import androidx.lifecycle.ViewModel
import androidx.lifecycle.viewModelScope
import br.gov.tanamao.domain.model.*
import br.gov.tanamao.domain.model.Result
import br.gov.tanamao.domain.model.formatBrazilian
import br.gov.tanamao.domain.repository.AgentRepository
import br.gov.tanamao.data.local.repository.ConsultationHistoryRepository
import br.gov.tanamao.data.local.repository.UserDataCacheRepository
import br.gov.tanamao.data.local.repository.CachedUserData
import br.gov.tanamao.presentation.util.AgentResponseParser
import dagger.hilt.android.lifecycle.HiltViewModel
import kotlinx.coroutines.flow.*
import kotlinx.coroutines.launch
import java.time.LocalDate
import android.content.Context
import android.content.Intent
import javax.inject.Inject

@HiltViewModel
class ProfileViewModel @Inject constructor(
    private val agentRepository: AgentRepository,
    private val consultationHistoryRepository: ConsultationHistoryRepository,
    private val userDataCacheRepository: UserDataCacheRepository
) : ViewModel() {

    private val _uiState = MutableStateFlow(ProfileUiState())
    val uiState: StateFlow<ProfileUiState> = _uiState.asStateFlow()

    init {
        loadProfileData()
    }

    fun refresh() {
        loadProfileData()
    }

    fun loadProfileData() {
        viewModelScope.launch {
            _uiState.update { it.copy(isLoading = true, error = null) }
            
            // Load consolidated user data
            loadUserData()
            
            // Load consultation history (mock for now, will be replaced with Room later)
            loadConsultationHistory()
            
            _uiState.update { it.copy(isLoading = false) }
        }
    }

    private suspend fun loadUserData() {
        // Try to load from cache first
        val cachedData = userDataCacheRepository.getCachedUserData()
        val cacheAge = cachedData?.let { System.currentTimeMillis() - it.lastUpdated } ?: Long.MAX_VALUE
        val isCacheValid = cacheAge < 3600000 // 1 hour
        
        // For now, always load fresh data to ensure accuracy
        // Cache is used to store data for offline access, but we prioritize fresh data
        // NOTE: Full cache deserialization can be implemented when needed.
        // Current approach: Cache stores serializable Maps, fresh data is always loaded for accuracy.
        // To implement: Convert Maps back to UserBenefit objects when cache is valid (< 1 hour)
        
        // Load fresh data from agent
        loadFreshUserData()
    }
    
    private suspend fun loadFreshUserData() {
        when (val result = agentRepository.sendMessage("meus dados", "")) {
            is Result.Success -> {
                val response = result.data.message
                val benefits = AgentResponseParser.parseUserBenefits(response)
                
                // Extract user name using parser
                val userName = AgentResponseParser.extractUserName(response) ?: "Usuário"

                // Calculate stats
                val totalMonthly = benefits.sumOf { it.monthlyValue ?: 0.0 }
                val activeCount = benefits.count { it.status == BenefitStatus.ACTIVE }

                // Extract total received using parser
                val totalReceived = AgentResponseParser.extractTotalReceived(response) ?: 0.0

                // Save to cache with serializable data
                try {
                    // Convert benefits to serializable format
                    val serializableBenefits = benefits.map { benefit ->
                        mapOf(
                            "id" to benefit.id,
                            "programCode" to benefit.programCode,
                            "programName" to benefit.programName,
                            "status" to benefit.status.name,
                            "monthlyValue" to (benefit.monthlyValue ?: 0.0),
                            "nextPaymentDate" to (benefit.nextPaymentDate?.toString() ?: "")
                        )
                    }

                    userDataCacheRepository.saveUserData(
                        CachedUserData(
                            benefits = serializableBenefits,
                            userName = userName,
                            totalReceived = totalReceived,
                            totalReceivedThisYear = totalReceived * 0.7
                        )
                    )
                } catch (e: Exception) {
                    // Cache save failed, continue anyway
                }
                
                val stats = ProfileStats(
                    totalReceived = totalReceived,
                    totalReceivedThisYear = totalReceived * 0.7, // Estimate
                    activeBenefitsCount = activeCount,
                    totalMonthlyValue = totalMonthly,
                    consultationsCount = _uiState.value.consultationHistory.size,
                    lastConsultationDate = _uiState.value.consultationHistory.firstOrNull()?.date,
                    benefitsDiscovered = benefits.size
                )
                
                _uiState.update { state ->
                    state.copy(
                        userName = userName ?: "Usuário",
                        benefits = benefits,
                        stats = stats,
                        error = null
                    )
                }
            }
            is Result.Error -> {
                // Use mock data as fallback
                loadMockData()
            }
            Result.Loading -> {
                // Keep loading state
            }
        }
    }

    private fun loadConsultationHistory() {
        viewModelScope.launch {
            // Load from Room database
            consultationHistoryRepository.getAllHistory()
                .collect { history ->
                    _uiState.update { it.copy(consultationHistory = history) }
                }
        }
        
        // Fallback mock data if database is empty
        viewModelScope.launch {
            val count = consultationHistoryRepository.getCount()
            if (count == 0) {
                val mockHistory = listOf(
                    ConsultationHistory(
                        id = "1",
                        date = LocalDate.now().minusDays(2),
                        type = ConsultationType.MONEY_CHECK,
                        query = "verificar meu dinheiro esquecido",
                        result = "Encontrado R$ 500,00 no PIS/PASEP",
                        toolsUsed = listOf("consultar_dinheiro_esquecido"),
                        success = true
                    ),
                    ConsultationHistory(
                        id = "2",
                        date = LocalDate.now().minusDays(5),
                        type = ConsultationType.ELIGIBILITY_CHECK,
                        query = "tenho direito a bolsa família?",
                        result = "Você é elegível para Bolsa Família",
                        toolsUsed = listOf("verificar_elegibilidade"),
                        success = true
                    ),
                    ConsultationHistory(
                        id = "3",
                        date = LocalDate.now().minusDays(10),
                        type = ConsultationType.GENERAL_QUESTION,
                        query = "que documentos preciso para BPC?",
                        result = "Checklist gerado com 8 documentos",
                        toolsUsed = listOf("gerar_checklist"),
                        success = true
                    )
                )
                consultationHistoryRepository.saveAll(mockHistory)
            }
        }
    }

    private fun loadMockData() {
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
            )
        )
        
        val mockStats = ProfileStats(
            totalReceived = 12000.0,
            totalReceivedThisYear = 8400.0,
            activeBenefitsCount = 2,
            totalMonthlyValue = 2012.0,
            consultationsCount = 3,
            lastConsultationDate = LocalDate.now().minusDays(2),
            benefitsDiscovered = 2
        )
        
        _uiState.update {
            it.copy(
                userName = "Maria",
                benefits = mockBenefits,
                stats = mockStats,
                error = null
            )
        }
    }

    /**
     * Export user data for LGPD compliance
     * Returns a formatted string with all user data
     */
    fun exportUserData(): String {
        val state = _uiState.value
        val sb = StringBuilder()
        
        sb.appendLine("=== DADOS DO USUÁRIO - TÁ NA MÃO ===")
        sb.appendLine("Data de exportação: ${LocalDate.now()}")
        sb.appendLine()
        
        sb.appendLine("--- Informações Pessoais ---")
        sb.appendLine("Nome: ${state.userName ?: "Não informado"}")
        sb.appendLine()
        
        state.stats?.let { stats ->
            sb.appendLine("--- Estatísticas ---")
            sb.appendLine("Total recebido: R$ ${String.format("%.2f", stats.totalReceived)}")
            sb.appendLine("Total recebido este ano: R$ ${String.format("%.2f", stats.totalReceivedThisYear)}")
            sb.appendLine("Benefícios ativos: ${stats.activeBenefitsCount}")
            sb.appendLine("Valor mensal total: R$ ${String.format("%.2f", stats.totalMonthlyValue)}")
            sb.appendLine("Benefícios descobertos: ${stats.benefitsDiscovered}")
            sb.appendLine("Consultas realizadas: ${stats.consultationsCount}")
            stats.lastConsultationDate?.let {
                sb.appendLine("Última consulta: ${it.formatBrazilian()}")
            }
            sb.appendLine()
        }
        
        if (state.benefits.isNotEmpty()) {
            sb.appendLine("--- Benefícios ---")
            state.benefits.forEachIndexed { index, benefit ->
                sb.appendLine("${index + 1}. ${benefit.programName}")
                sb.appendLine("   Status: ${benefit.status.name}")
                benefit.monthlyValue?.let {
                    sb.appendLine("   Valor mensal: R$ ${String.format("%.2f", it)}")
                }
                benefit.nextPaymentDate?.let {
                    sb.appendLine("   Próximo pagamento: ${it.formatBrazilian()}")
                }
                sb.appendLine()
            }
        }
        
        if (state.consultationHistory.isNotEmpty()) {
            sb.appendLine("--- Histórico de Consultas ---")
            state.consultationHistory.forEachIndexed { index, consultation ->
                sb.appendLine("${index + 1}. ${consultation.date.formatBrazilian()}")
                sb.appendLine("   Tipo: ${consultation.type.name}")
                sb.appendLine("   Consulta: ${consultation.query}")
                sb.appendLine("   Resultado: ${consultation.result}")
                sb.appendLine("   Sucesso: ${if (consultation.success) "Sim" else "Não"}")
                sb.appendLine()
            }
        }
        
        sb.appendLine("=== FIM DO RELATÓRIO ===")
        return sb.toString()
    }
    
    /**
     * Share user data via Android Intent
     * Opens the share chooser to allow user to export their data
     */
    fun shareUserData(context: Context) {
        val shareText = exportUserData()
        val shareIntent = Intent().apply {
            action = Intent.ACTION_SEND
            type = "text/plain"
            putExtra(Intent.EXTRA_TEXT, shareText)
        }
        context.startActivity(Intent.createChooser(shareIntent, "Exportar meus dados"))
    }
    
    /**
     * Check for forgotten money (PIS/PASEP, SVR, FGTS)
     * Returns true if there's forgotten money available
     */
    fun checkForgottenMoney() {
        viewModelScope.launch {
            _uiState.update { it.copy(isLoading = true, error = null) }
            
            when (val result = agentRepository.sendMessage("consultar dinheiro esquecido", "")) {
                is Result.Success -> {
                    val response = result.data.message
                    val toolsUsed = result.data.toolsUsed ?: emptyList()
                    
                    // Use parser to extract money information
                    val moneyResult = AgentResponseParser.parseMoneyCheckResult(response, toolsUsed)
                    
                    if (moneyResult != null) {
                        val pisType = moneyResult.types.find { it.type == "PIS_PASEP" }
                        val svrType = moneyResult.types.find { it.type == "SVR" }
                        val fgtsType = moneyResult.types.find { it.type == "FGTS" }
                        
                        val pisAmount = pisType?.amount ?: 0.0
                        val svrAmount = svrType?.amount ?: 0.0
                        val fgtsAmount = fgtsType?.amount ?: 0.0
                        val totalForgotten = moneyResult.totalAmount ?: (pisAmount + svrAmount + fgtsAmount)
                        
                        _uiState.update { state ->
                            state.copy(
                                forgottenMoney = ForgottenMoneyInfo(
                                    total = totalForgotten,
                                    pisPasep = pisAmount,
                                    svr = svrAmount,
                                    fgts = fgtsAmount,
                                    hasMoney = moneyResult.hasMoney
                                ),
                                isLoading = false,
                                error = null
                            )
                        }
                    } else {
                        // Fallback if parser doesn't find anything
                        _uiState.update { state ->
                            state.copy(
                                forgottenMoney = ForgottenMoneyInfo(
                                    total = 0.0,
                                    pisPasep = 0.0,
                                    svr = 0.0,
                                    fgts = 0.0,
                                    hasMoney = false
                                ),
                                isLoading = false,
                                error = null
                            )
                        }
                    }
                }
                is Result.Error -> {
                    _uiState.update {
                        it.copy(
                            isLoading = false,
                            error = "Erro ao verificar dinheiro esquecido: ${result.exception.getUserMessage()}"
                        )
                    }
                }
                Result.Loading -> {
                    // Keep loading state
                }
            }
        }
    }
}

data class ProfileUiState(
    val userName: String? = null,
    val benefits: List<UserBenefit> = emptyList(),
    val stats: ProfileStats? = null,
    val consultationHistory: List<ConsultationHistory> = emptyList(),
    val forgottenMoney: ForgottenMoneyInfo? = null,
    val isLoading: Boolean = true,
    val error: String? = null
)

data class ForgottenMoneyInfo(
    val total: Double,
    val pisPasep: Double,
    val svr: Double,
    val fgts: Double,
    val hasMoney: Boolean
)

