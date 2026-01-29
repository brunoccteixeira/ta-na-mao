package br.gov.tanamao.presentation.ui.money

import androidx.lifecycle.ViewModel
import androidx.lifecycle.viewModelScope
import br.gov.tanamao.domain.model.MoneyCheckResult
import br.gov.tanamao.domain.model.MoneyForgotten
import br.gov.tanamao.domain.model.MoneyType
import br.gov.tanamao.domain.model.MoneyTypeResult
import br.gov.tanamao.domain.model.Result
import br.gov.tanamao.domain.repository.AgentRepository
import br.gov.tanamao.presentation.util.AgentResponseParser
import dagger.hilt.android.lifecycle.HiltViewModel
import kotlinx.coroutines.flow.*
import kotlinx.coroutines.launch
import javax.inject.Inject

@HiltViewModel
class MoneyViewModel @Inject constructor(
    private val agentRepository: AgentRepository
) : ViewModel() {

    private val _uiState = MutableStateFlow(MoneyUiState())
    val uiState: StateFlow<MoneyUiState> = _uiState.asStateFlow()

    init {
        loadMoneyOverview()
    }

    fun checkMyMoney(cpf: String? = null) {
        viewModelScope.launch {
            _uiState.update { it.copy(isChecking = true, error = null) }
            
            // Call agent with message to check forgotten money
            val message = if (cpf != null) {
                "verificar meu dinheiro esquecido, meu CPF é $cpf"
            } else {
                "verificar meu dinheiro esquecido"
            }
            
            when (val result = agentRepository.sendMessage(message, "")) {
                is Result.Success -> {
                    // Parse response using improved parser
                    val parsedResult = AgentResponseParser.parseMoneyCheckResult(
                        result.data.message,
                        result.data.toolsUsed
                    ) ?: MoneyCheckResult(
                        hasMoney = result.data.message.contains("tem dinheiro", ignoreCase = true),
                        message = result.data.message
                    )
                    
                    _uiState.update {
                        it.copy(
                            isChecking = false,
                            checkResult = parsedResult
                        )
                    }
                }
                is Result.Error -> {
                    _uiState.update {
                        it.copy(
                            isChecking = false,
                            error = result.exception.message ?: "Erro ao verificar dinheiro esquecido"
                        )
                    }
                }
                is Result.Loading -> {
                    // Already set isChecking = true
                }
            }
        }
    }

    fun navigateToGuide(type: String) {
        viewModelScope.launch {
            val message = when (type) {
                "PIS_PASEP" -> "guia PIS PASEP"
                "SVR" -> "guia SVR"
                "FGTS" -> "guia FGTS"
                else -> "guia dinheiro esquecido"
            }
            
            // This will be handled by navigation to chat with message
            _uiState.update { it.copy(navigateToGuide = type) }
        }
    }

    fun clearNavigation() {
        _uiState.update { it.copy(navigateToGuide = null) }
    }

    fun refresh() {
        loadMoneyOverview()
    }

    private fun loadMoneyOverview() {
        // Static overview data - R$ 42 bilhões disponíveis
        val overview = MoneyForgotten(
            totalAvailable = 42_000_000_000.0,
            pisPasep = MoneyType(
                name = "PIS/PASEP",
                totalAvailable = 26_300_000_000.0,
                eligiblePeople = 10_500_000,
                deadline = null,
                description = "Abono salarial e saque do PIS/PASEP não resgatados",
                guideSteps = listOf(
                    "Acesse o site da Caixa ou Banco do Brasil",
                    "Informe seu CPF e data de nascimento",
                    "Verifique se há valores disponíveis",
                    "Siga as instruções para saque"
                )
            ),
            svr = MoneyType(
                name = "Valores a Receber (SVR)",
                totalAvailable = 9_000_000_000.0,
                eligiblePeople = 0, // Varies
                deadline = null,
                description = "Valores esquecidos no Banco Central",
                guideSteps = listOf(
                    "Acesse o site do Banco Central",
                    "Informe seu CPF",
                    "Verifique valores disponíveis",
                    "Siga as instruções para recebimento"
                )
            ),
            fgts = MoneyType(
                name = "FGTS",
                totalAvailable = 7_800_000_000.0,
                eligiblePeople = 0, // Varies
                deadline = "30/12/2025",
                description = "Saque emergencial do FGTS disponível até dezembro de 2025",
                guideSteps = listOf(
                    "Acesse o app FGTS ou site da Caixa",
                    "Verifique se você tem direito ao saque",
                    "Siga as instruções para saque",
                    "Prazo: até 30 de dezembro de 2025"
                )
            )
        )

        _uiState.update {
            it.copy(
                overview = overview,
                isLoading = false
            )
        }
    }
}

data class MoneyUiState(
    val overview: MoneyForgotten? = null,
    val checkResult: MoneyCheckResult? = null,
    val isLoading: Boolean = true,
    val isChecking: Boolean = false,
    val error: String? = null,
    val navigateToGuide: String? = null
)

