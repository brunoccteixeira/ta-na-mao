package br.gov.tanamao.domain.model

/**
 * Model for CRAS pre-attendance preparation
 */
data class CrasPreparation(
    val program: String,
    val checklist: DocumentChecklist,
    val form: PreFilledForm? = null,
    val estimatedTime: Int, // minutes
    val tips: List<String> = emptyList(),
    val eligibility: EligibilityInfo? = null
)

data class DocumentChecklist(
    val title: String,
    val documents: List<DocumentItem>,
    val totalDocuments: Int,
    val estimatedTime: Int // minutes
)

data class PreFilledForm(
    val title: String,
    val fields: List<FormField>,
    val printableText: String? = null
)

data class FormField(
    val label: String,
    val value: String? = null,
    val placeholder: String? = null,
    val isRequired: Boolean = true,
    val fieldType: FieldType = FieldType.TEXT
)

enum class FieldType {
    TEXT,
    NUMBER,
    DATE,
    SELECT,
    CHECKBOX
}

data class EligibilityInfo(
    val isEligible: Boolean?,
    val reason: String,
    val nextSteps: List<String> = emptyList()
)



