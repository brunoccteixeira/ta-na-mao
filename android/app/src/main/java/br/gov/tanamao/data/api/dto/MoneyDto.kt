package br.gov.tanamao.data.api.dto

import com.google.gson.annotations.SerializedName

/**
 * DTO for money forgotten check response
 */
data class MoneyCheckResponseDto(
    val tem_dinheiro: Boolean,
    @SerializedName("valor_total") val valorTotal: Double? = null,
    val tipos: List<MoneyTypeResultDto> = emptyList(),
    val mensagem: String
)

data class MoneyTypeResultDto(
    val tipo: String, // PIS_PASEP, SVR, FGTS
    @SerializedName("tem_dinheiro") val temDinheiro: Boolean,
    val valor: Double? = null,
    val status: String,
    @SerializedName("proximos_passos") val proximosPassos: List<String> = emptyList()
)

/**
 * DTO for money forgotten overview
 */
data class MoneyOverviewDto(
    @SerializedName("total_disponivel") val totalDisponivel: Double,
    @SerializedName("pis_pasep") val pisPasep: MoneyTypeDto,
    val svr: MoneyTypeDto,
    val fgts: MoneyTypeDto
)

data class MoneyTypeDto(
    val nome: String,
    @SerializedName("total_disponivel") val totalDisponivel: Double,
    @SerializedName("pessoas_elegiveis") val pessoasElegiveis: Long,
    val prazo: String? = null,
    val descricao: String,
    @SerializedName("passos_guia") val passosGuia: List<String> = emptyList()
)



