package br.gov.tanamao.domain.repository

import br.gov.tanamao.domain.model.*
import kotlinx.coroutines.flow.Flow

/**
 * Repository interface for aggregation-related data.
 */
interface AggregationRepository {

    /**
     * Get national-level aggregation.
     */
    suspend fun getNational(program: ProgramCode? = null): Result<NationalStats>

    /**
     * Get state-level aggregations.
     */
    suspend fun getStates(program: ProgramCode? = null): Result<List<StateStats>>

    /**
     * Get region-level aggregations.
     */
    suspend fun getRegions(program: ProgramCode? = null): Result<List<RegionStats>>

    /**
     * Get time series data.
     */
    fun getTimeSeries(
        program: ProgramCode? = null,
        stateCode: String? = null
    ): Flow<Result<List<TimeSeriesPoint>>>

    /**
     * Get demographics data.
     */
    suspend fun getDemographics(stateCode: String? = null): Result<Demographics>
}
