package br.gov.tanamao.presentation.ui.cras

import android.content.Context
import android.content.Intent
import androidx.lifecycle.ViewModel
import androidx.lifecycle.viewModelScope
import br.gov.tanamao.domain.model.CrasPreparation
import br.gov.tanamao.domain.model.DocumentChecklist
import br.gov.tanamao.domain.model.PreFilledForm
import br.gov.tanamao.domain.model.Result
import br.gov.tanamao.domain.repository.AgentRepository
import br.gov.tanamao.presentation.util.AgentResponseParser
import dagger.hilt.android.lifecycle.HiltViewModel
import kotlinx.coroutines.flow.*
import kotlinx.coroutines.launch
import javax.inject.Inject

@HiltViewModel
class CrasPreparationViewModel @Inject constructor(
    private val agentRepository: AgentRepository
) : ViewModel() {

    private val _uiState = MutableStateFlow(CrasPreparationUiState())
    val uiState: StateFlow<CrasPreparationUiState> = _uiState.asStateFlow()

    fun prepareForCras(program: String, cpf: String? = null) {
        viewModelScope.launch {
            _uiState.update { it.copy(isLoading = true, error = null) }
            
            val message = if (cpf != null) {
                "preparar para atendimento no CRAS para $program, meu CPF é $cpf"
            } else {
                "preparar para atendimento no CRAS para $program"
            }
            
            when (val result = agentRepository.sendMessage(message, "")) {
                is Result.Success -> {
                    // Parse response using improved parser
                    val preparation = AgentResponseParser.parseCrasPreparation(
                        result.data.message,
                        program
                    ) ?: createMockPreparation(program, result.data.message)
                    
                    _uiState.update {
                        it.copy(
                            isLoading = false,
                            preparation = preparation
                        )
                    }
                }
                is Result.Error -> {
                    _uiState.update {
                        it.copy(
                            isLoading = false,
                            error = result.exception.message ?: "Erro ao preparar para CRAS"
                        )
                    }
                }
                is Result.Loading -> {
                    // Already set isLoading = true
                }
            }
        }
    }

    fun generateForm(program: String, cpf: String? = null) {
        viewModelScope.launch {
            _uiState.update { it.copy(isGeneratingForm = true, error = null) }
            
            val message = if (cpf != null) {
                "gerar formulário pré-preenchido para $program, meu CPF é $cpf"
            } else {
                "gerar formulário pré-preenchido para $program"
            }
            
            when (val result = agentRepository.sendMessage(message, "")) {
                is Result.Success -> {
                    // Parse response to extract form data
                    // For now, we'll update the existing preparation with form data
                    _uiState.update { state ->
                        state.copy(
                            isGeneratingForm = false,
                            preparation = state.preparation?.copy(
                                form = createMockForm(result.data.message)
                            )
                        )
                    }
                }
                is Result.Error -> {
                    _uiState.update {
                        it.copy(
                            isGeneratingForm = false,
                            error = result.exception.message ?: "Erro ao gerar formulário"
                        )
                    }
                }
                is Result.Loading -> {
                    // Already set isGeneratingForm = true
                }
            }
        }
    }

    fun clearError() {
        _uiState.update { it.copy(error = null) }
    }

    fun shareChecklist(context: Context, checklist: DocumentChecklist) {
        val shareText = buildString {
            appendLine("📋 Checklist de Documentos - CRAS")
            appendLine()
            appendLine(checklist.title)
            appendLine()
            checklist.documents.forEachIndexed { index, doc ->
                val checkmark = if (doc.isProvided) "✅" else "☐"
                appendLine("$checkmark ${index + 1}. ${doc.name}")
                doc.description?.let { appendLine("   $it") }
            }
            appendLine()
            appendLine("Tempo estimado: ${checklist.estimatedTime} minutos")
            appendLine()
            appendLine("Gerado pelo app Tá na Mão")
        }

        val shareIntent = Intent().apply {
            action = Intent.ACTION_SEND
            type = "text/plain"
            putExtra(Intent.EXTRA_TEXT, shareText)
        }
        context.startActivity(Intent.createChooser(shareIntent, "Compartilhar checklist"))
    }

    fun shareForm(context: Context, form: PreFilledForm) {
        val shareText = form.printableText ?: buildString {
            appendLine("📄 Formulário Pré-preenchido - CRAS")
            appendLine()
            appendLine(form.title)
            appendLine()
            form.fields.forEach { field ->
                appendLine("${field.label}: ${field.value ?: field.placeholder ?: ""}")
            }
            appendLine()
            appendLine("Gerado pelo app Tá na Mão")
        }

        val shareIntent = Intent().apply {
            action = Intent.ACTION_SEND
            type = "text/plain"
            putExtra(Intent.EXTRA_TEXT, shareText)
        }
        context.startActivity(Intent.createChooser(shareIntent, "Compartilhar formulário"))
    }

    private fun createMockPreparation(program: String, responseText: String): CrasPreparation {
        // This is a mock - in production, parse the actual response from the agent
        return CrasPreparation(
            program = program,
            checklist = br.gov.tanamao.domain.model.DocumentChecklist(
                title = "Documentos necessários",
                documents = listOf(
                    br.gov.tanamao.domain.model.DocumentItem(
                        name = "RG de todos da casa",
                        description = "Documento de identidade",
                        isRequired = true,
                        isProvided = false
                    ),
                    br.gov.tanamao.domain.model.DocumentItem(
                        name = "CPF de todos da casa",
                        description = "Cadastro de Pessoa Física",
                        isRequired = true,
                        isProvided = false
                    ),
                    br.gov.tanamao.domain.model.DocumentItem(
                        name = "Comprovante de residência",
                        description = "Conta de luz ou água",
                        isRequired = true,
                        isProvided = false
                    ),
                    br.gov.tanamao.domain.model.DocumentItem(
                        name = "Comprovante de renda",
                        description = "Últimos 3 meses",
                        isRequired = true,
                        isProvided = false
                    )
                ),
                totalDocuments = 4,
                estimatedTime = 15
            ),
            estimatedTime = 30,
            tips = listOf(
                "Chegue cedo para evitar filas",
                "Leve todos os documentos originais",
                "Se possível, agende horário antes",
                "Leve cópias dos documentos também"
            )
        )
    }

    private fun createMockForm(responseText: String): br.gov.tanamao.domain.model.PreFilledForm {
        // This is a mock - in production, parse the actual response from the agent
        return br.gov.tanamao.domain.model.PreFilledForm(
            title = "Formulário de Cadastro",
            fields = listOf(
                br.gov.tanamao.domain.model.FormField(
                    label = "Nome completo",
                    value = null,
                    placeholder = "Digite seu nome",
                    isRequired = true
                ),
                br.gov.tanamao.domain.model.FormField(
                    label = "CPF",
                    value = null,
                    placeholder = "000.000.000-00",
                    isRequired = true
                ),
                br.gov.tanamao.domain.model.FormField(
                    label = "Data de nascimento",
                    value = null,
                    placeholder = "DD/MM/AAAA",
                    isRequired = true
                )
            )
        )
    }
}

data class CrasPreparationUiState(
    val preparation: CrasPreparation? = null,
    val isLoading: Boolean = false,
    val isGeneratingForm: Boolean = false,
    val error: String? = null
)

