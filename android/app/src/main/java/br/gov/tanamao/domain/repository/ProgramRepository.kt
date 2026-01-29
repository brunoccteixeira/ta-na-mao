package br.gov.tanamao.domain.repository

import br.gov.tanamao.domain.model.*
import kotlinx.coroutines.flow.Flow

/**
 * Repository interface for program-related data.
 */
interface ProgramRepository {

    /**
     * Get all programs with their national statistics.
     */
    fun getPrograms(): Flow<Result<List<Program>>>

    /**
     * Get detailed information for a specific program.
     */
    suspend fun getProgram(code: ProgramCode): Result<Program>

    /**
     * Get ranking of municipalities for a program.
     */
    suspend fun getRanking(
        code: ProgramCode,
        stateCode: String? = null,
        orderBy: RankingOrderBy = RankingOrderBy.BENEFICIARIES,
        limit: Int = 20
    ): Result<List<RankingItem>>
}
