package br.gov.tanamao.data.api.dto

import com.google.gson.annotations.SerializedName

/**
 * DTO for CRAS preparation response
 */
data class CrasPreparationResponseDto(
    val programa: String,
    val checklist: DocumentChecklistDto,
    val formulario: PreFilledFormDto? = null,
    @SerializedName("tempo_estimado") val tempoEstimado: Int, // minutes
    val dicas: List<String> = emptyList(),
    val elegibilidade: EligibilityInfoDto? = null
)

data class DocumentChecklistDto(
    val titulo: String,
    val documentos: List<DocumentItemDto>,
    @SerializedName("total_documentos") val totalDocumentos: Int,
    @SerializedName("tempo_estimado") val tempoEstimado: Int // minutes
)

data class DocumentItemDto(
    val nome: String,
    val descricao: String? = null,
    @SerializedName("obrigatorio") val obrigatorio: Boolean = true,
    @SerializedName("fornecido") val fornecido: Boolean = false
)

data class PreFilledFormDto(
    val titulo: String,
    val campos: List<FormFieldDto>,
    @SerializedName("texto_imprimivel") val textoImprimivel: String? = null
)

data class FormFieldDto(
    val label: String,
    val valor: String? = null,
    val placeholder: String? = null,
    @SerializedName("obrigatorio") val obrigatorio: Boolean = true,
    @SerializedName("tipo") val tipo: String = "TEXT" // TEXT, NUMBER, DATE, SELECT, CHECKBOX
)

data class EligibilityInfoDto(
    @SerializedName("elegivel") val elegivel: Boolean?,
    val motivo: String,
    @SerializedName("proximos_passos") val proximosPassos: List<String> = emptyList()
)



