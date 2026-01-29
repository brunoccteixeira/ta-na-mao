package br.gov.tanamao.data.repository

import br.gov.tanamao.data.api.TaNaMaoApi
import br.gov.tanamao.domain.model.*
import br.gov.tanamao.domain.repository.MunicipalityRepository
import kotlinx.coroutines.flow.Flow
import kotlinx.coroutines.flow.flow
import javax.inject.Inject
import javax.inject.Singleton

@Singleton
class MunicipalityRepositoryImpl @Inject constructor(
    private val api: TaNaMaoApi
) : MunicipalityRepository {

    override fun search(query: String, limit: Int): Flow<Result<List<MunicipalitySearchResult>>> = flow {
        emit(Result.Loading)
        try {
            val response = api.searchMunicipalities(query, limit)
            val results = response.map { dto ->
                MunicipalitySearchResult(
                    ibgeCode = dto.ibgeCode,
                    name = dto.name,
                    stateAbbreviation = stateIdToAbbreviation(dto.stateId),
                    population = dto.population
                )
            }
            emit(Result.Success(results))
        } catch (e: Exception) {
            emit(Result.Error(e.toAppError()))
        }
    }

    override suspend fun getMunicipality(ibgeCode: String): Result<Municipality> {
        return try {
            val dto = api.getMunicipality(ibgeCode)
            val municipality = Municipality(
                ibgeCode = dto.ibgeCode,
                name = dto.name,
                stateAbbreviation = dto.stateAbbreviation,
                stateName = dto.stateName,
                region = parseRegion(dto.region),
                population = dto.population,
                areaKm2 = dto.areaKm2,
                cadUnicoFamilies = dto.cadUnicoFamilies,
                totalBeneficiaries = dto.totalBeneficiaries,
                totalFamilies = dto.totalFamilies,
                totalValueBrl = dto.totalValueBrl,
                coverageRate = dto.coverageRate
            )
            Result.Success(municipality)
        } catch (e: Exception) {
            Result.Error(e.toAppError())
        }
    }

    override suspend fun getMunicipalityPrograms(ibgeCode: String): Result<List<MunicipalityProgram>> {
        return try {
            val response = api.getMunicipalityPrograms(ibgeCode)
            val programs = response.programs.map { dto ->
                MunicipalityProgram(
                    code = parseProgramCode(dto.code),
                    name = dto.name,
                    totalBeneficiaries = dto.totalBeneficiaries,
                    totalFamilies = dto.totalFamilies,
                    totalValueBrl = dto.totalValueBrl,
                    coverageRate = dto.coverageRate,
                    referenceDate = dto.referenceDate
                )
            }
            Result.Success(programs)
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

    private fun parseProgramCode(code: String): ProgramCode = when (code.uppercase()) {
        "CADUNICO", "BOLSA_FAMILIA", "BF" -> ProgramCode.CADUNICO
        "BPC", "BPC_LOAS" -> ProgramCode.BPC
        "FARMACIA_POPULAR", "FARMACIA" -> ProgramCode.FARMACIA_POPULAR
        "TSEE", "TARIFA_SOCIAL" -> ProgramCode.TSEE
        "DIGNIDADE_MENSTRUAL", "DIGNIDADE" -> ProgramCode.DIGNIDADE_MENSTRUAL
        else -> ProgramCode.CADUNICO
    }

    private fun stateIdToAbbreviation(stateId: Int): String = when (stateId) {
        11 -> "RO"
        12 -> "AC"
        13 -> "AM"
        14 -> "RR"
        15 -> "PA"
        16 -> "AP"
        17 -> "TO"
        21 -> "MA"
        22 -> "PI"
        23 -> "CE"
        24 -> "RN"
        25 -> "PB"
        26 -> "PE"
        27 -> "AL"
        28 -> "SE"
        29 -> "BA"
        31 -> "MG"
        32 -> "ES"
        33 -> "RJ"
        35 -> "SP"
        41 -> "PR"
        42 -> "SC"
        43 -> "RS"
        50 -> "MS"
        51 -> "MT"
        52 -> "GO"
        53 -> "DF"
        else -> "BR"
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
