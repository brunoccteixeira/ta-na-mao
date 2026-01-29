package br.gov.tanamao.presentation.ui.history

import androidx.lifecycle.ViewModel
import androidx.lifecycle.viewModelScope
import br.gov.tanamao.domain.model.ConsultationHistory
import br.gov.tanamao.domain.model.ConsultationType
import br.gov.tanamao.data.local.repository.ConsultationHistoryRepository
import dagger.hilt.android.lifecycle.HiltViewModel
import kotlinx.coroutines.flow.*
import kotlinx.coroutines.launch
import javax.inject.Inject

@HiltViewModel
class HistoryViewModel @Inject constructor(
    private val consultationHistoryRepository: ConsultationHistoryRepository
) : ViewModel() {

    private val _uiState = MutableStateFlow(HistoryUiState())
    val uiState: StateFlow<HistoryUiState> = _uiState.asStateFlow()

    init {
        loadHistory()
    }

    fun setFilter(filter: HistoryFilter) {
        viewModelScope.launch {
            val allHistory = _uiState.value.allHistory
            val filtered = when (filter) {
                HistoryFilter.ALL -> allHistory
                HistoryFilter.MONEY -> allHistory.filter { it.type == ConsultationType.MONEY_CHECK }
                HistoryFilter.ELIGIBILITY -> allHistory.filter { it.type == ConsultationType.ELIGIBILITY_CHECK }
                HistoryFilter.DOCUMENTS -> allHistory.filter { it.type == ConsultationType.DOCUMENT_GUIDANCE }
                HistoryFilter.LOCATIONS -> allHistory.filter { it.type == ConsultationType.LOCATION_SEARCH }
            }
            _uiState.update { state ->
                state.copy(selectedFilter = filter, filteredHistory = filtered)
            }
        }
    }

    fun refresh() {
        loadHistory()
    }

    private fun loadHistory() {
        viewModelScope.launch {
            _uiState.update { it.copy(isLoading = true) }
            
            // Load from Room database
            consultationHistoryRepository.getAllHistory()
                .collect { history ->
                    val filtered = when (_uiState.value.selectedFilter) {
                        HistoryFilter.ALL -> history
                        HistoryFilter.MONEY -> history.filter { it.type == ConsultationType.MONEY_CHECK }
                        HistoryFilter.ELIGIBILITY -> history.filter { it.type == ConsultationType.ELIGIBILITY_CHECK }
                        HistoryFilter.DOCUMENTS -> history.filter { it.type == ConsultationType.DOCUMENT_GUIDANCE }
                        HistoryFilter.LOCATIONS -> history.filter { it.type == ConsultationType.LOCATION_SEARCH }
                    }
                    
                    _uiState.update {
                        it.copy(
                            allHistory = history,
                            filteredHistory = filtered,
                            isLoading = false
                        )
                    }
                }
            
            // If database is empty, load mock data
            val count = consultationHistoryRepository.getCount()
            if (count == 0) {
                val mockHistory = loadMockHistory()
                consultationHistoryRepository.saveAll(mockHistory)
            }
        }
    }

    private fun loadMockHistory(): List<ConsultationHistory> {
        return listOf(
            ConsultationHistory(
                id = "1",
                date = java.time.LocalDate.now().minusDays(1),
                type = br.gov.tanamao.domain.model.ConsultationType.MONEY_CHECK,
                query = "verificar meu dinheiro esquecido",
                result = "Encontrado R$ 500,00 no PIS/PASEP",
                toolsUsed = listOf("consultar_dinheiro_esquecido"),
                success = true
            ),
            ConsultationHistory(
                id = "2",
                date = java.time.LocalDate.now().minusDays(3),
                type = br.gov.tanamao.domain.model.ConsultationType.ELIGIBILITY_CHECK,
                query = "tenho direito a bolsa família?",
                result = "Você é elegível para Bolsa Família",
                toolsUsed = listOf("verificar_elegibilidade"),
                success = true
            ),
            ConsultationHistory(
                id = "3",
                date = java.time.LocalDate.now().minusDays(5),
                type = br.gov.tanamao.domain.model.ConsultationType.DOCUMENT_GUIDANCE,
                query = "que documentos preciso para BPC?",
                result = "Checklist gerado com 8 documentos",
                toolsUsed = listOf("gerar_checklist"),
                success = true
            ),
            ConsultationHistory(
                id = "4",
                date = java.time.LocalDate.now().minusDays(7),
                type = br.gov.tanamao.domain.model.ConsultationType.LOCATION_SEARCH,
                query = "onde fica o CRAS mais próximo?",
                result = "CRAS encontrado a 2km",
                toolsUsed = listOf("buscar_cras"),
                success = true
            )
        )
    }
}

enum class HistoryFilter(val label: String) {
    ALL("Todos"),
    MONEY("Dinheiro"),
    ELIGIBILITY("Elegibilidade"),
    DOCUMENTS("Documentos"),
    LOCATIONS("Locais")
}

data class HistoryUiState(
    val allHistory: List<ConsultationHistory> = emptyList(),
    val filteredHistory: List<ConsultationHistory> = emptyList(),
    val selectedFilter: HistoryFilter = HistoryFilter.ALL,
    val isLoading: Boolean = true
)


