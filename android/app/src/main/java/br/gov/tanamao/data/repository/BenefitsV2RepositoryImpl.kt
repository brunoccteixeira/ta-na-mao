package br.gov.tanamao.data.repository

import br.gov.tanamao.data.api.TaNaMaoApi
import br.gov.tanamao.data.api.dto.BenefitDetailDto
import br.gov.tanamao.data.api.dto.BenefitSummaryDto
import br.gov.tanamao.data.api.dto.BenefitStatsResponseDto
import br.gov.tanamao.data.api.dto.BenefitsByLocationResponseDto
import br.gov.tanamao.data.api.dto.CitizenProfileDto
import br.gov.tanamao.data.api.dto.EligibilityRequestDto
import br.gov.tanamao.data.api.dto.EligibilityResponseDto
import br.gov.tanamao.data.api.dto.QuickEligibilityResponseDto
import br.gov.tanamao.data.local.database.dao.BenefitCacheDao
import br.gov.tanamao.data.local.database.entity.BenefitCacheEntity
import br.gov.tanamao.di.IoDispatcher
import br.gov.tanamao.domain.model.AppError
import br.gov.tanamao.domain.model.Result
import br.gov.tanamao.domain.repository.BenefitsV2Repository
import kotlinx.coroutines.CoroutineDispatcher
import kotlinx.coroutines.flow.Flow
import kotlinx.coroutines.flow.first
import kotlinx.coroutines.flow.flow
import kotlinx.coroutines.flow.flowOn
import kotlinx.coroutines.withContext
import javax.inject.Inject
import javax.inject.Singleton

/**
 * Implementation of BenefitsV2Repository.
 * Uses cache-first strategy with API fallback.
 */
@Singleton
class BenefitsV2RepositoryImpl @Inject constructor(
    private val api: TaNaMaoApi,
    private val cacheDao: BenefitCacheDao,
    @IoDispatcher private val dispatcher: CoroutineDispatcher
) : BenefitsV2Repository {

    // ========== BENEFITS CATALOG ==========

    override fun getBenefits(forceRefresh: Boolean): Flow<Result<List<BenefitSummaryDto>>> = flow {
        emit(Result.Loading)

        // Try cache first (unless forcing refresh)
        if (!forceRefresh) {
            val cached = cacheDao.getAllOnce()
            if (cached.isNotEmpty()) {
                emit(Result.Success(cached.map { it.toDto() }))
            }
        }

        // Fetch from API
        try {
            val response = api.getBenefitsV2(limit = 500)

            // Update cache
            cacheDao.deleteAll()
            cacheDao.insertAll(response.items.map { BenefitCacheEntity.fromDto(it) })

            emit(Result.Success(response.items))
        } catch (e: Exception) {
            // If API fails and we have no cache, emit error
            val cached = cacheDao.getAllOnce()
            if (cached.isEmpty()) {
                emit(Result.Error(e.toAppError()))
            }
            // If we already emitted cache, just log the error
        }
    }.flowOn(dispatcher)

    override suspend fun getBenefitsByScope(
        scope: String,
        forceRefresh: Boolean
    ): Result<List<BenefitSummaryDto>> = withContext(dispatcher) {
        try {
            // Try cache first
            if (!forceRefresh) {
                val cached = cacheDao.getByScope(scope)
                if (cached.isNotEmpty()) {
                    return@withContext Result.Success(cached.map { it.toDto() })
                }
            }

            // Fetch from API
            val response = api.getBenefitsV2(scope = scope, limit = 200)
            Result.Success(response.items)
        } catch (e: Exception) {
            // Fallback to cache
            val cached = cacheDao.getByScope(scope)
            if (cached.isNotEmpty()) {
                Result.Success(cached.map { it.toDto() })
            } else {
                Result.Error(e.toAppError())
            }
        }
    }

    override suspend fun getBenefitsForState(
        stateCode: String,
        forceRefresh: Boolean
    ): Result<List<BenefitSummaryDto>> = withContext(dispatcher) {
        try {
            // Try cache first
            if (!forceRefresh) {
                val cached = cacheDao.getByState(stateCode)
                if (cached.isNotEmpty()) {
                    return@withContext Result.Success(cached.map { it.toDto() })
                }
            }

            // Fetch from API
            val response = api.getBenefitsByLocation(stateCode)
            val combined = response.federal + response.state + response.sectoral
            Result.Success(combined)
        } catch (e: Exception) {
            // Fallback to cache
            val cached = cacheDao.getByState(stateCode)
            if (cached.isNotEmpty()) {
                Result.Success(cached.map { it.toDto() })
            } else {
                Result.Error(e.toAppError())
            }
        }
    }

    override suspend fun getBenefitsForMunicipality(
        stateCode: String,
        municipalityIbge: String,
        forceRefresh: Boolean
    ): Result<BenefitsByLocationResponseDto> = withContext(dispatcher) {
        try {
            val response = api.getBenefitsByLocation(stateCode, municipalityIbge)
            Result.Success(response)
        } catch (e: Exception) {
            // Fallback to cache (build response from cached data)
            val cached = cacheDao.getByMunicipality(stateCode, municipalityIbge)
            if (cached.isNotEmpty()) {
                val dtos = cached.map { it.toDto() }
                val response = BenefitsByLocationResponseDto(
                    stateCode = stateCode,
                    stateName = stateCode, // Would need lookup
                    municipalityIbge = municipalityIbge,
                    municipalityName = null,
                    federal = dtos.filter { it.scope == "federal" },
                    state = dtos.filter { it.scope == "state" },
                    municipal = dtos.filter { it.scope == "municipal" },
                    sectoral = dtos.filter { it.scope == "sectoral" },
                    total = dtos.size
                )
                Result.Success(response)
            } else {
                Result.Error(e.toAppError())
            }
        }
    }

    override suspend fun getBenefitDetail(benefitId: String): Result<BenefitDetailDto> =
        withContext(dispatcher) {
            try {
                val response = api.getBenefitDetailV2(benefitId)
                Result.Success(response)
            } catch (e: Exception) {
                // For detail, we can return a partial result from cache
                val cached = cacheDao.getById(benefitId)
                if (cached != null) {
                    // Return a minimal BenefitDetailDto from cache
                    // Note: This is incomplete - full detail requires API
                    Result.Error(AppError.NotFound("Use cache summary instead"))
                } else {
                    Result.Error(e.toAppError())
                }
            }
        }

    override suspend fun searchBenefits(query: String): Result<List<BenefitSummaryDto>> =
        withContext(dispatcher) {
            try {
                val response = api.getBenefitsV2(search = query, limit = 50)
                Result.Success(response.items)
            } catch (e: Exception) {
                // Fallback to local search
                val cached = cacheDao.search(query)
                if (cached.isNotEmpty()) {
                    Result.Success(cached.map { it.toDto() })
                } else {
                    Result.Error(e.toAppError())
                }
            }
        }

    override suspend fun getStats(): Result<BenefitStatsResponseDto> = withContext(dispatcher) {
        try {
            val response = api.getBenefitsStats()
            Result.Success(response)
        } catch (e: Exception) {
            // Build stats from cache
            val count = cacheDao.getCount()
            if (count > 0) {
                val cached = cacheDao.getAllOnce()
                val byScope = cached.groupBy { it.scope }.mapValues { it.value.size }
                val byCategory = cached.groupBy { it.category ?: "Outros" }.mapValues { it.value.size }

                Result.Success(
                    BenefitStatsResponseDto(
                        totalBenefits = count,
                        byScope = byScope,
                        byCategory = byCategory,
                        statesCovered = cached.mapNotNull { it.state }.distinct().size,
                        municipalitiesCovered = cached.mapNotNull { it.municipalityIbge }.distinct().size
                    )
                )
            } else {
                Result.Error(e.toAppError())
            }
        }
    }

    // ========== ELIGIBILITY ==========

    override suspend fun checkEligibility(
        profile: CitizenProfileDto,
        scope: String?,
        includeNotApplicable: Boolean
    ): Result<EligibilityResponseDto> = withContext(dispatcher) {
        try {
            val request = EligibilityRequestDto(
                profile = profile,
                scope = scope,
                includeNotApplicable = includeNotApplicable
            )
            val response = api.checkEligibility(request)
            Result.Success(response)
        } catch (e: Exception) {
            Result.Error(e.toAppError())
        }
    }

    override suspend fun quickEligibilityCheck(
        estado: String,
        rendaFamiliarMensal: Double,
        pessoasNaCasa: Int,
        cadastradoCadunico: Boolean
    ): Result<QuickEligibilityResponseDto> = withContext(dispatcher) {
        try {
            val response = api.quickEligibilityCheck(
                estado = estado,
                rendaFamiliarMensal = rendaFamiliarMensal,
                pessoasNaCasa = pessoasNaCasa,
                cadastradoCadunico = cadastradoCadunico
            )
            Result.Success(response)
        } catch (e: Exception) {
            Result.Error(e.toAppError())
        }
    }

    // ========== CACHE MANAGEMENT ==========

    override suspend fun hasCachedData(): Boolean = withContext(dispatcher) {
        cacheDao.hasValidCache()
    }

    override suspend fun clearCache() = withContext(dispatcher) {
        cacheDao.deleteAll()
    }

    override suspend fun syncCache(): Result<Int> = withContext(dispatcher) {
        try {
            val response = api.getBenefitsV2(limit = 500)

            // Clear expired and insert new
            cacheDao.deleteExpired()
            cacheDao.insertAll(response.items.map { BenefitCacheEntity.fromDto(it) })

            Result.Success(response.items.size)
        } catch (e: Exception) {
            Result.Error(e.toAppError())
        }
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
