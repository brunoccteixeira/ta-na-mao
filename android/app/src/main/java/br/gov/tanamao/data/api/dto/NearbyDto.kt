package br.gov.tanamao.data.api.dto

import com.google.gson.annotations.SerializedName

/**
 * Response for nearby services search
 */
data class NearbyResponseDto(
    val sucesso: Boolean,
    val encontrados: Int,
    val locais: List<ServiceLocationDto>,
    val mensagem: String? = null,
    @SerializedName("redes_nacionais")
    val redesNacionais: List<String>? = null
)

/**
 * Service location (pharmacy or CRAS)
 */
data class ServiceLocationDto(
    val nome: String,
    val endereco: String,
    val distancia: String? = null,
    @SerializedName("distancia_metros")
    val distanciaMetros: Int? = null,
    val telefone: String? = null,
    val horario: String? = null,
    @SerializedName("aberto_agora")
    val abertoAgora: Boolean? = null,
    val delivery: Boolean? = null,
    val links: ServiceLinksDto? = null
)

/**
 * Links for navigation and contact
 */
data class ServiceLinksDto(
    val maps: String? = null,
    val waze: String? = null,
    val whatsapp: String? = null,
    val direcoes: String? = null
)
