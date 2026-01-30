package br.gov.tanamao.data.local.database.entity

import androidx.room.Entity
import androidx.room.PrimaryKey
import br.gov.tanamao.data.api.dto.BenefitSummaryDto
import br.gov.tanamao.data.api.dto.EstimatedValueDto
import com.google.gson.Gson

/**
 * Room entity for caching benefits from API v2.
 * Stores benefits for offline access.
 */
@Entity(tableName = "benefits_cache")
data class BenefitCacheEntity(
    @PrimaryKey
    val id: String,
    val name: String,
    val shortDescription: String,
    val scope: String,
    val state: String?,
    val municipalityIbge: String?,
    val estimatedValueJson: String?, // JSON serialized EstimatedValueDto
    val status: String,
    val icon: String?,
    val category: String?,
    val lastUpdated: Long = System.currentTimeMillis(),
    val expiresAt: Long = System.currentTimeMillis() + (24 * 60 * 60 * 1000) // 24 hours
) {
    /**
     * Convert to API DTO format.
     */
    fun toDto(): BenefitSummaryDto {
        val estimatedValue = estimatedValueJson?.let {
            try {
                Gson().fromJson(it, EstimatedValueDto::class.java)
            } catch (e: Exception) {
                null
            }
        }

        return BenefitSummaryDto(
            id = id,
            name = name,
            shortDescription = shortDescription,
            scope = scope,
            state = state,
            municipalityIbge = municipalityIbge,
            estimatedValue = estimatedValue,
            status = status,
            icon = icon,
            category = category
        )
    }

    companion object {
        /**
         * Create entity from API DTO.
         */
        fun fromDto(dto: BenefitSummaryDto, ttlMs: Long = 24 * 60 * 60 * 1000): BenefitCacheEntity {
            val estimatedValueJson = dto.estimatedValue?.let {
                try {
                    Gson().toJson(it)
                } catch (e: Exception) {
                    null
                }
            }

            return BenefitCacheEntity(
                id = dto.id,
                name = dto.name,
                shortDescription = dto.shortDescription,
                scope = dto.scope,
                state = dto.state,
                municipalityIbge = dto.municipalityIbge,
                estimatedValueJson = estimatedValueJson,
                status = dto.status,
                icon = dto.icon,
                category = dto.category,
                lastUpdated = System.currentTimeMillis(),
                expiresAt = System.currentTimeMillis() + ttlMs
            )
        }
    }
}
