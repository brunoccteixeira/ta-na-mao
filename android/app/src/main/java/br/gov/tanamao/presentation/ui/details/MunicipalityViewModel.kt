package br.gov.tanamao.presentation.ui.details

import androidx.lifecycle.ViewModel
import androidx.lifecycle.viewModelScope
import br.gov.tanamao.domain.model.Municipality
import br.gov.tanamao.domain.model.MunicipalityProgram
import br.gov.tanamao.domain.model.Result
import br.gov.tanamao.domain.repository.MunicipalityRepository
import dagger.hilt.android.lifecycle.HiltViewModel
import kotlinx.coroutines.flow.MutableStateFlow
import kotlinx.coroutines.flow.StateFlow
import kotlinx.coroutines.flow.asStateFlow
import kotlinx.coroutines.flow.update
import kotlinx.coroutines.launch
import javax.inject.Inject

@HiltViewModel
class MunicipalityViewModel @Inject constructor(
    private val municipalityRepository: MunicipalityRepository
) : ViewModel() {

    private val _uiState = MutableStateFlow(MunicipalityUiState())
    val uiState: StateFlow<MunicipalityUiState> = _uiState.asStateFlow()

    fun loadMunicipality(ibgeCode: String) {
        viewModelScope.launch {
            _uiState.update { it.copy(isLoading = true, error = null) }

            // Load municipality details
            when (val result = municipalityRepository.getMunicipality(ibgeCode)) {
                is Result.Success -> {
                    _uiState.update {
                        it.copy(municipality = result.data)
                    }
                }
                is Result.Error -> {
                    _uiState.update {
                        it.copy(
                            isLoading = false,
                            error = result.exception.getUserMessage()
                        )
                    }
                    return@launch
                }
                is Result.Loading -> { /* handled above */ }
            }

            // Load programs
            when (val result = municipalityRepository.getMunicipalityPrograms(ibgeCode)) {
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
                is Result.Loading -> { /* handled above */ }
            }
        }
    }
}

data class MunicipalityUiState(
    val isLoading: Boolean = false,
    val error: String? = null,
    val municipality: Municipality? = null,
    val programs: List<MunicipalityProgram> = emptyList()
)
