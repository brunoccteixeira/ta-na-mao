package br.gov.tanamao.data.api.dto

import com.google.gson.annotations.SerializedName

/**
 * DTOs for Eligibility API v2 - unified eligibility check
 */

// ========== CITIZEN PROFILE ==========

/**
 * Citizen profile for eligibility evaluation.
 * Matches the backend CitizenProfile schema.
 */
data class CitizenProfileDto(
    val estado: String,
    @SerializedName("municipio_ibge") val municipioIbge: String? = null,
    @SerializedName("municipio_nome") val municipioNome: String? = null,

    // Basic info
    val idade: Int? = null,
    val cpf: String? = null,
    val nome: String? = null,
    val cep: String? = null,

    // Family
    @SerializedName("pessoas_na_casa") val pessoasNaCasa: Int = 1,
    @SerializedName("quantidade_filhos") val quantidadeFilhos: Int = 0,
    @SerializedName("tem_idoso_65_mais") val temIdoso65Mais: Boolean = false,
    @SerializedName("tem_gestante") val temGestante: Boolean = false,
    @SerializedName("tem_pcd") val temPcd: Boolean = false,
    @SerializedName("tem_crianca_0_a_6") val temCrianca0a6: Boolean = false,

    // Income
    @SerializedName("renda_familiar_mensal") val rendaFamiliarMensal: Double = 0.0,
    @SerializedName("trabalho_formal") val trabalhoFormal: Boolean = false,

    // Housing
    @SerializedName("tem_casa_propria") val temCasaPropria: Boolean = false,
    @SerializedName("moradia_zona_rural") val moradiaZonaRural: Boolean = false,

    // CadUnico and current benefits
    @SerializedName("cadastrado_cadunico") val cadastradoCadunico: Boolean = false,
    @SerializedName("nis_cadunico") val nisCadunico: String? = null,
    @SerializedName("recebe_bolsa_familia") val recebeBolsaFamilia: Boolean = false,
    @SerializedName("valor_bolsa_familia") val valorBolsaFamilia: Double? = null,
    @SerializedName("recebe_bpc") val recebeBpc: Boolean = false,

    // Work history
    @SerializedName("trabalhou_1971_1988") val trabalhou1971_1988: Boolean? = null,
    @SerializedName("tem_carteira_assinada") val temCarteiraAssinada: Boolean? = null,
    @SerializedName("tempo_carteira_assinada") val tempoCarteiraAssinada: Int? = null,
    @SerializedName("fez_saque_fgts") val fezSaqueFgts: Boolean? = null,

    // Sectoral
    val profissao: String? = null,
    @SerializedName("tem_mei") val temMei: Boolean = false,
    @SerializedName("trabalha_aplicativo") val trabalhaAplicativo: Boolean = false,
    @SerializedName("agricultor_familiar") val agricultorFamiliar: Boolean = false,
    @SerializedName("pescador_artesanal") val pescadorArtesanal: Boolean = false,
    @SerializedName("catador_reciclavel") val catadorReciclavel: Boolean = false,

    // Special conditions
    @SerializedName("mulher_menstruante") val mulherMenstruante: Boolean? = null,
    @SerializedName("idade_mulher") val idadeMulher: Int? = null,

    // Education
    val estudante: Boolean = false,
    @SerializedName("rede_publica") val redePublica: Boolean = false
)

// ========== ELIGIBILITY REQUEST ==========

/**
 * Request to evaluate eligibility.
 */
data class EligibilityRequestDto(
    val profile: CitizenProfileDto,
    val scope: String? = null, // "federal", "state", "municipal", "sectoral"
    @SerializedName("include_not_applicable") val includeNotApplicable: Boolean = false
)

// ========== ELIGIBILITY RESPONSE ==========

/**
 * Full eligibility evaluation response.
 */
data class EligibilityResponseDto(
    @SerializedName("profile_summary") val profileSummary: Map<String, Any>,
    val summary: EligibilitySummaryDto,
    @SerializedName("evaluated_at") val evaluatedAt: String
)

/**
 * Summary of eligibility evaluation.
 */
data class EligibilitySummaryDto(
    val eligible: List<BenefitEligibilityResultDto>,
    @SerializedName("likely_eligible") val likelyEligible: List<BenefitEligibilityResultDto>,
    val maybe: List<BenefitEligibilityResultDto>,
    @SerializedName("not_eligible") val notEligible: List<BenefitEligibilityResultDto>,
    @SerializedName("not_applicable") val notApplicable: List<BenefitEligibilityResultDto>,
    @SerializedName("already_receiving") val alreadyReceiving: List<BenefitEligibilityResultDto>,

    @SerializedName("total_analyzed") val totalAnalyzed: Int,
    @SerializedName("total_potential_monthly") val totalPotentialMonthly: Double,
    @SerializedName("total_potential_annual") val totalPotentialAnnual: Double,
    @SerializedName("total_potential_one_time") val totalPotentialOneTime: Double,

    @SerializedName("priority_steps") val prioritySteps: List<String>,
    @SerializedName("documents_needed") val documentsNeeded: List<String>
)

/**
 * Eligibility result for a single benefit.
 */
data class BenefitEligibilityResultDto(
    val benefit: BenefitSummaryDto,
    val status: String, // "eligible", "likely_eligible", "maybe", "not_eligible", "not_applicable", "already_receiving"
    @SerializedName("matched_rules") val matchedRules: List<String>,
    @SerializedName("failed_rules") val failedRules: List<String>,
    @SerializedName("inconclusive_rules") val inconclusiveRules: List<String>,
    @SerializedName("estimated_value") val estimatedValue: Double?,
    val reason: String?,
    @SerializedName("rule_details") val ruleDetails: List<RuleEvaluationResultDto>?
)

/**
 * Result of evaluating a single eligibility rule.
 */
data class RuleEvaluationResultDto(
    @SerializedName("rule_description") val ruleDescription: String,
    val passed: Boolean,
    val inconclusive: Boolean = false,
    val field: String,
    @SerializedName("expected_value") val expectedValue: Any,
    @SerializedName("actual_value") val actualValue: Any?
)

// ========== QUICK ELIGIBILITY ==========

/**
 * Quick eligibility check response (lighter version).
 */
data class QuickEligibilityResponseDto(
    @SerializedName("eligible_count") val eligibleCount: Int,
    @SerializedName("maybe_count") val maybeCount: Int,
    @SerializedName("total_potential_monthly") val totalPotentialMonthly: Double,
    @SerializedName("top_benefits") val topBenefits: List<TopBenefitDto>
)

/**
 * Summary of a top benefit for quick eligibility.
 */
data class TopBenefitDto(
    val name: String,
    val value: Double?
)
