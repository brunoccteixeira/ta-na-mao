package br.gov.tanamao.presentation.ui.search

import androidx.lifecycle.ViewModel
import androidx.lifecycle.viewModelScope
import br.gov.tanamao.domain.model.MunicipalitySearchResult
import br.gov.tanamao.domain.model.Result
import br.gov.tanamao.domain.repository.MunicipalityRepository
import dagger.hilt.android.lifecycle.HiltViewModel
import kotlinx.coroutines.FlowPreview
import kotlinx.coroutines.flow.*
import kotlinx.coroutines.launch
import javax.inject.Inject

@OptIn(FlowPreview::class)
@HiltViewModel
class SearchViewModel @Inject constructor(
    private val municipalityRepository: MunicipalityRepository
) : ViewModel() {

    private val _uiState = MutableStateFlow(SearchUiState())
    val uiState: StateFlow<SearchUiState> = _uiState.asStateFlow()

    private val _queryFlow = MutableStateFlow("")

    init {
        // Debounce search queries
        viewModelScope.launch {
            _queryFlow
                .debounce(300)
                .filter { it.length >= 2 }
                .distinctUntilChanged()
                .collectLatest { query ->
                    search(query)
                }
        }
    }

    fun onQueryChange(query: String) {
        _uiState.update { it.copy(query = query) }
        _queryFlow.value = query

        if (query.length < 2) {
            _uiState.update { it.copy(results = emptyList()) }
        }
    }

    private fun search(query: String) {
        viewModelScope.launch {
            municipalityRepository.search(query).collect { result ->
                when (result) {
                    is Result.Loading -> {
                        _uiState.update { it.copy(isLoading = true) }
                    }
                    is Result.Success -> {
                        _uiState.update {
                            it.copy(
                                isLoading = false,
                                results = result.data,
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
}

data class SearchUiState(
    val query: String = "",
    val isLoading: Boolean = false,
    val results: List<MunicipalitySearchResult> = emptyList(),
    val error: String? = null
)
