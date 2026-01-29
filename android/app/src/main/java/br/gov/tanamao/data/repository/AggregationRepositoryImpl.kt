package br.gov.tanamao.data.repository

import br.gov.tanamao.data.api.TaNaMaoApi
import br.gov.tanamao.domain.model.*
import br.gov.tanamao.domain.repository.AggregationRepository
import kotlinx.coroutines.flow.Flow
import kotlinx.coroutines.flow.flow
import java.time.LocalDate
import javax.inject.Inject
import javax.inject.Singleton

@Singleton
class AggregationRepositoryImpl @Inject constructor(
    private val api: TaNaMaoApi
) : AggregationRepository {

    override suspend fun getNational(program: ProgramCode?): Result<NationalStats> {
        return try {
            val dto = api.getNationalAggregation(program?.name)
            val stats = NationalStats(
                population = dto.population,
                cadUnicoFamilies = dto.cadUnicoFamilies,
                totalMunicipalities = dto.totalMunicipalities,
                totalStates = dto.totalStates,
                totalBeneficiaries = dto.programStats?.totalBeneficiaries,
                totalFamilies = dto.programStats?.totalFamilies,
                totalValueBrl = dto.programStats?.totalValueBrl,
                avgCoverageRate = null  // Not available in ProgramStatsDto
            )
            Result.Success(stats)
        } catch (e: Exception) {
            Result.Error(e.toAppError())
        }
    }

    override suspend fun getStates(program: ProgramCode?): Result<List<StateStats>> {
        return try {
            val dto = api.getStatesAggregation(program?.name)
            val states = dto.states.map { state ->
                StateStats(
                    ibgeCode = state.ibgeCode,
                    name = state.name,
                    abbreviation = state.abbreviation,
                    region = parseRegion(state.region),
                    population = state.population,
                    municipalityCount = state.municipalityCount,
                    totalBeneficiaries = state.totalBeneficiaries,
                    totalFamilies = state.totalFamilies,
                    cadUnicoFamilies = state.cadUnicoFamilies,
                    totalValueBrl = state.totalValueBrl,
                    avgCoverageRate = state.avgCoverageRate
                )
            }
            Result.Success(states)
        } catch (e: Exception) {
            Result.Error(e.toAppError())
        }
    }

    override suspend fun getRegions(program: ProgramCode?): Result<List<RegionStats>> {
        return try {
            val dto = api.getRegionsAggregation(program?.name)
            val regions = dto.regions.map { region ->
                RegionStats(
                    code = parseRegion(region.code),
                    name = region.name,
                    population = region.population,
                    stateCount = region.stateCount,
                    municipalityCount = region.municipalityCount,
                    totalBeneficiaries = region.totalBeneficiaries,
                    totalFamilies = region.totalFamilies,
                    totalValueBrl = region.totalValueBrl,
                    avgCoverageRate = region.avgCoverageRate
                )
            }
            Result.Success(regions)
        } catch (e: Exception) {
            Result.Error(e.toAppError())
        }
    }

    override fun getTimeSeries(
        program: ProgramCode?,
        stateCode: String?
    ): Flow<Result<List<TimeSeriesPoint>>> = flow {
        emit(Result.Loading)
        try {
            val dto = api.getTimeSeries(program?.name, stateCode)
            val points = dto.data.map { point ->
                TimeSeriesPoint(
                    date = LocalDate.parse(point.date),
                    monthLabel = point.month,
                    totalBeneficiaries = point.totalBeneficiaries,
                    totalFamilies = point.totalFamilies,
                    totalValueBrl = point.totalValueBrl,
                    avgCoverageRate = point.avgCoverageRate
                )
            }
            emit(Result.Success(points))
        } catch (e: Exception) {
            emit(Result.Error(e.toAppError()))
        }
    }

    override suspend fun getDemographics(stateCode: String?): Result<Demographics> {
        return try {
            val dto = api.getDemographics(stateCode)
            val demographics = Demographics(
                totalFamilies = dto.totalFamilies,
                totalPersons = dto.totalPersons,
                incomeBrackets = IncomeBrackets(
                    extremePoverty = dto.incomeBrackets.extremePoverty,
                    poverty = dto.incomeBrackets.poverty,
                    lowIncome = dto.incomeBrackets.lowIncome
                ),
                ageDistribution = AgeDistribution(
                    age0to5 = dto.ageDistribution.age0to5,
                    age6to14 = dto.ageDistribution.age6to14,
                    age15to17 = dto.ageDistribution.age15to17,
                    age18to64 = dto.ageDistribution.age18to64,
                    age65plus = dto.ageDistribution.age65plus
                )
            )
            Result.Success(demographics)
        } catch (e: Exception) {
            Result.Error(e.toAppError())
        }
    }

    private fun parseRegion(code: String): Region = when (code.uppercase()) {
        "N", "NORTE" -> Region.N
        "NE", "NORDESTE" -> Region.NE
        "CO", "CENTRO-OESTE" -> Region.CO
        "SE", "SUDESTE" -> Region.SE
        "S", "SUL" -> Region.S
        else -> Region.SE
    }
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
