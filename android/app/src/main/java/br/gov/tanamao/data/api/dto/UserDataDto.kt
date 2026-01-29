package br.gov.tanamao.data.api.dto

import com.google.gson.annotations.SerializedName

/**
 * DTO for consolidated user data (meus_dados tool)
 */
data class UserDataResponseDto(
    val cpf: String? = null,
    @SerializedName("cpf_masked") val cpfMasked: String? = null,
    val nome: String? = null,
    val beneficios: UserBenefitsDto? = null,
    val valores: UserValuesDto? = null,
    val alertas: List<AlertDto> = emptyList(),
    val resumo: String
)

data class UserBenefitsDto(
    @SerializedName("bolsa_familia") val bolsaFamilia: BenefitStatusDto? = null,
    val bpc: BenefitStatusDto? = null,
    val cadunico: BenefitStatusDto? = null,
    @SerializedName("farmacia_popular") val farmaciaPopular: BenefitStatusDto? = null,
    val tsee: BenefitStatusDto? = null
)

data class BenefitStatusDto(
    val ativo: Boolean,
    val valor: Double? = null,
    @SerializedName("parcela_mes") val parcelaMes: String? = null,
    @SerializedName("data_referencia") val dataReferencia: String? = null,
    @SerializedName("ultima_atualizacao") val ultimaAtualizacao: String? = null
)

data class UserValuesDto(
    @SerializedName("total_mensal") val totalMensal: Double? = null,
    @SerializedName("beneficios_ativos") val beneficiosAtivos: Int = 0
)

data class AlertDto(
    val tipo: String, // CADUNICO_DESATUALIZADO, PAGAMENTO_ATRASADO, NOVO_BENEFICIO
    val titulo: String,
    val mensagem: String,
    val prioridade: String = "MEDIA", // ALTA, MEDIA, BAIXA
    val acao: String? = null
)



