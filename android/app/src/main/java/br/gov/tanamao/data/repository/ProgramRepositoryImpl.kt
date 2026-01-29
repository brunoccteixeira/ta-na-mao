package br.gov.tanamao.data.repository

import br.gov.tanamao.data.api.TaNaMaoApi
import br.gov.tanamao.data.api.dto.ProgramDto
import br.gov.tanamao.data.api.dto.RankingItemDto
import br.gov.tanamao.di.IoDispatcher
import br.gov.tanamao.domain.model.*
import br.gov.tanamao.domain.repository.ProgramRepository
import kotlinx.coroutines.CoroutineDispatcher
import kotlinx.coroutines.flow.Flow
import kotlinx.coroutines.flow.flow
import kotlinx.coroutines.flow.flowOn
import kotlinx.coroutines.withContext
import java.time.LocalDate
import javax.inject.Inject
import javax.inject.Singleton

@Singleton
class ProgramRepositoryImpl @Inject constructor(
    private val api: TaNaMaoApi,
    @IoDispatcher private val dispatcher: CoroutineDispatcher
) : ProgramRepository {

    override fun getPrograms(): Flow<Result<List<Program>>> = flow {
        emit(Result.Loading)
        try {
            val response = api.getPrograms()
            val programs = response.map { it.toDomain() }
            emit(Result.Success(programs))
        } catch (e: Exception) {
            emit(Result.Error(e.toAppError()))
        }
    }.flowOn(dispatcher)

    override suspend fun getProgram(code: ProgramCode): Result<Program> =
        withContext(dispatcher) {
            try {
                val response = api.getProgram(code.name)
                Result.Success(
                    Program(
                        code = ProgramCode.valueOf(response.code),
                        name = response.name,
                        description = response.description,
                        dataSourceUrl = response.dataSourceUrl,
                        updateFrequency = UpdateFrequency.valueOf(response.updateFrequency.uppercase()),
                        nationalStats = response.nationalStats?.let {
                            ProgramStats(
                                totalBeneficiaries = it.totalBeneficiaries,
                                totalFamilies = it.totalFamilies,
                                totalValueBrl = it.totalValueBrl,
                                avgCoverageRate = it.avgCoverageRate,
                                municipalitiesCovered = it.municipalitiesCovered,
                                totalMunicipalities = it.totalMunicipalities
                            )
                        }
                    )
                )
            } catch (e: Exception) {
                Result.Error(e.toAppError())
            }
        }

    override suspend fun getRanking(
        code: ProgramCode,
        stateCode: String?,
        orderBy: RankingOrderBy,
        limit: Int
    ): Result<List<RankingItem>> = withContext(dispatcher) {
        try {
            val response = api.getProgramRanking(code.name, stateCode, orderBy.value, limit)
            Result.Success(response.ranking.map { it.toDomain() })
        } catch (e: Exception) {
            Result.Error(e.toAppError())
        }
    }

    private fun ProgramDto.toDomain(): Program = Program(
        code = try { ProgramCode.valueOf(code) } catch (e: Exception) { ProgramCode.CADUNICO },
        name = name,
        description = description,
        dataSourceUrl = dataSourceUrl,
        updateFrequency = try { UpdateFrequency.valueOf(updateFrequency.uppercase()) } catch (e: Exception) { UpdateFrequency.MONTHLY },
        nationalStats = nationalStats?.let {
            ProgramStats(
                totalBeneficiaries = it.totalBeneficiaries,
                totalFamilies = it.totalFamilies,
                totalValueBrl = it.totalValueBrl,
                latestDataDate = it.latestDataDate?.let { date ->
                    try { LocalDate.parse(date) } catch (e: Exception) { null }
                }
            )
        }
    )

    private fun RankingItemDto.toDomain(): RankingItem = RankingItem(
        rank = rank,
        ibgeCode = ibgeCode,
        name = name,
        totalBeneficiaries = totalBeneficiaries,
        totalFamilies = totalFamilies,
        coverageRate = coverageRate,
        totalValueBrl = totalValueBrl,
        referenceDate = referenceDate
    )
}

// Extension to convert exceptions to AppError
private fun Throwable.toAppError(): AppError = when (this) {
    is java.net.SocketTimeoutException -> AppError.Timeout()
    is java.net.UnknownHostException -> AppError.Network()
    is java.io.IOException -> AppError.Network()
    is retrofit2.HttpException -> when (code()) {
        404 -> AppError.NotFound()
        in 500..599 -> AppError.Server(code(), message())
        else -> AppError.Unknown(this)
    }
    else -> AppError.Unknown(this)
}
