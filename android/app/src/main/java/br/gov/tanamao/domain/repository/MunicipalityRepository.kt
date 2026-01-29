package br.gov.tanamao.domain.repository

import br.gov.tanamao.domain.model.*
import kotlinx.coroutines.flow.Flow

/**
 * Repository interface for municipality-related data.
 */
interface MunicipalityRepository {

    /**
     * Search municipalities by name.
     */
    fun search(query: String, limit: Int = 20): Flow<Result<List<MunicipalitySearchResult>>>

    /**
     * Get detailed information for a municipality.
     */
    suspend fun getMunicipality(ibgeCode: String): Result<Municipality>

    /**
     * Get all programs available in a municipality.
     */
    suspend fun getMunicipalityPrograms(ibgeCode: String): Result<List<MunicipalityProgram>>
}
