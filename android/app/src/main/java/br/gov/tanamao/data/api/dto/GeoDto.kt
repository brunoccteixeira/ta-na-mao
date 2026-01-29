package br.gov.tanamao.data.api.dto

import com.google.gson.annotations.SerializedName

/**
 * DTO for GeoJSON FeatureCollection response.
 */
data class GeoJsonResponseDto(
    val type: String, // "FeatureCollection"
    val features: List<GeoJsonFeatureDto>,
    val metadata: GeoJsonMetadataDto?
)

/**
 * DTO for a GeoJSON Feature.
 */
data class GeoJsonFeatureDto(
    val type: String, // "Feature"
    val properties: GeoJsonPropertiesDto,
    val geometry: GeoJsonGeometryDto
)

/**
 * DTO for GeoJSON Feature properties.
 */
data class GeoJsonPropertiesDto(
    @SerializedName("ibge_code") val ibgeCode: String,
    val name: String,
    val abbreviation: String?,
    val region: String?,
    val population: Long?,
    val beneficiaries: Long?,
    val families: Long?,
    val coverage: Double?
)

/**
 * DTO for GeoJSON geometry.
 */
data class GeoJsonGeometryDto(
    val type: String, // "MultiPolygon" or "Polygon"
    val coordinates: Any // Complex nested array
)

/**
 * DTO for GeoJSON metadata.
 */
data class GeoJsonMetadataDto(
    val count: Int,
    @SerializedName("state_id") val stateId: Int?,
    val simplified: Boolean
)

/**
 * DTO for bounds response.
 */
data class BoundsDto(
    val bounds: List<Double>, // [minLng, minLat, maxLng, maxLat]
    val center: List<Double>  // [lng, lat]
)

/**
 * DTO for health check response.
 */
data class HealthDto(
    val status: String
)
