# Integração com API - App Android Tá na Mão

Este documento descreve como integrar o app Android com a API REST do backend Tá na Mão.

## Configuração Base

### Base URL

```kotlin
// BuildConfig ou local.properties
const val BASE_URL = "http://10.0.2.2:8000/api/v1/"  // Emulador
// const val BASE_URL = "http://192.168.x.x:8000/api/v1/"  // Device físico
// const val BASE_URL = "https://api.tanamao.gov.br/api/v1/"  // Produção
```

### Retrofit Setup

```kotlin
// data/api/TaNaMaoApi.kt
interface TaNaMaoApi {

    // ============ PROGRAMS ============

    @GET("programs/")
    suspend fun getPrograms(): List<ProgramDto>

    @GET("programs/{code}")
    suspend fun getProgram(@Path("code") code: String): ProgramDetailDto

    @GET("programs/{code}/ranking")
    suspend fun getProgramRanking(
        @Path("code") code: String,
        @Query("state_code") stateCode: String? = null,
        @Query("order_by") orderBy: String = "beneficiaries",
        @Query("limit") limit: Int = 20
    ): RankingResponseDto

    // ============ MUNICIPALITIES ============

    @GET("municipalities/")
    suspend fun getMunicipalities(
        @Query("state_code") stateCode: String? = null,
        @Query("search") search: String? = null,
        @Query("page") page: Int = 1,
        @Query("limit") limit: Int = 50
    ): PaginatedResponseDto<MunicipalityDto>

    @GET("municipalities/search")
    suspend fun searchMunicipalities(
        @Query("q") query: String,
        @Query("limit") limit: Int = 20
    ): List<MunicipalitySearchDto>

    @GET("municipalities/{ibge_code}")
    suspend fun getMunicipality(
        @Path("ibge_code") ibgeCode: String,
        @Query("program") program: String? = null
    ): MunicipalityDetailDto

    @GET("municipalities/{ibge_code}/programs")
    suspend fun getMunicipalityPrograms(
        @Path("ibge_code") ibgeCode: String
    ): MunicipalityProgramsDto

    // ============ AGGREGATIONS ============

    @GET("aggregations/national")
    suspend fun getNationalAggregation(
        @Query("program") program: String? = null
    ): NationalAggregationDto

    @GET("aggregations/states")
    suspend fun getStatesAggregation(
        @Query("program") program: String? = null
    ): StatesAggregationDto

    @GET("aggregations/states/{state_code}")
    suspend fun getStateDetail(
        @Path("state_code") stateCode: String,
        @Query("program") program: String? = null
    ): StateDetailDto

    @GET("aggregations/regions")
    suspend fun getRegionsAggregation(
        @Query("program") program: String? = null
    ): RegionsAggregationDto

    @GET("aggregations/time-series")
    suspend fun getTimeSeries(
        @Query("program") program: String? = null,
        @Query("state_code") stateCode: String? = null
    ): TimeSeriesDto

    @GET("aggregations/demographics")
    suspend fun getDemographics(
        @Query("state_code") stateCode: String? = null
    ): DemographicsDto

    // ============ GEO (GeoJSON) ============

    @GET("geo/states")
    suspend fun getStatesGeoJson(
        @Query("simplified") simplified: Boolean = true,
        @Query("program") program: String? = null,
        @Query("metric") metric: String? = null
    ): GeoJsonResponseDto

    @GET("geo/municipalities")
    suspend fun getMunicipalitiesGeoJson(
        @Query("state_code") stateCode: String,
        @Query("simplified") simplified: Boolean = true,
        @Query("program") program: String? = null
    ): GeoJsonResponseDto

    // NOTA: Endpoint geo/municipalities/{ibge_code} removido - usar geo/municipalities com filtro

    @GET("geo/bounds")
    suspend fun getBounds(
        @Query("state_code") stateCode: String? = null
    ): BoundsDto

    // ============ HEALTH ============

    @GET("health")
    suspend fun healthCheck(): HealthDto
}
```

---

## Data Transfer Objects (DTOs)

### Programs DTOs

```kotlin
// data/api/dto/ProgramDto.kt

data class ProgramDto(
    val code: String,
    val name: String,
    val description: String,
    @SerializedName("data_source_url") val dataSourceUrl: String,
    @SerializedName("update_frequency") val updateFrequency: String,
    @SerializedName("national_stats") val nationalStats: ProgramStatsDto?
)

data class ProgramStatsDto(
    @SerializedName("total_beneficiaries") val totalBeneficiaries: Long,
    @SerializedName("total_families") val totalFamilies: Long,
    @SerializedName("total_value_brl") val totalValueBrl: Double,
    @SerializedName("latest_data_date") val latestDataDate: String?
)

data class ProgramDetailDto(
    val code: String,
    val name: String,
    val description: String,
    @SerializedName("data_source_url") val dataSourceUrl: String,
    @SerializedName("update_frequency") val updateFrequency: String,
    @SerializedName("national_stats") val nationalStats: ProgramDetailStatsDto?
)

data class ProgramDetailStatsDto(
    @SerializedName("total_beneficiaries") val totalBeneficiaries: Long,
    @SerializedName("total_families") val totalFamilies: Long,
    @SerializedName("total_value_brl") val totalValueBrl: Double,
    @SerializedName("avg_coverage_rate") val avgCoverageRate: Double,
    @SerializedName("municipalities_covered") val municipalitiesCovered: Int,
    @SerializedName("total_municipalities") val totalMunicipalities: Int,
    @SerializedName("coverage_percentage") val coveragePercentage: Double
)
```

### Municipality DTOs

```kotlin
// data/api/dto/MunicipalityDto.kt

data class MunicipalityDto(
    @SerializedName("ibge_code") val ibgeCode: String,
    val name: String,
    @SerializedName("state_id") val stateId: Int,
    val population: Int?,
    @SerializedName("area_km2") val areaKm2: Double?
)

data class MunicipalitySearchDto(
    @SerializedName("ibge_code") val ibgeCode: String,
    val name: String,
    @SerializedName("state_id") val stateId: Int,
    val population: Int?
)

data class MunicipalityDetailDto(
    @SerializedName("ibge_code") val ibgeCode: String,
    val name: String,
    @SerializedName("state_abbreviation") val stateAbbreviation: String,
    @SerializedName("state_name") val stateName: String,
    val region: String,
    val population: Int,
    @SerializedName("area_km2") val areaKm2: Double?,
    @SerializedName("cadunico_families") val cadUnicoFamilies: Int?,
    @SerializedName("total_beneficiaries") val totalBeneficiaries: Int?,
    @SerializedName("total_families") val totalFamilies: Int?,
    @SerializedName("total_value_brl") val totalValueBrl: Double?,
    @SerializedName("coverage_rate") val coverageRate: Double?
)

data class MunicipalityProgramsDto(
    @SerializedName("ibge_code") val ibgeCode: String,
    val name: String,
    val programs: List<MunicipalityProgramDto>
)

data class MunicipalityProgramDto(
    val code: String,
    val name: String,
    @SerializedName("total_beneficiaries") val totalBeneficiaries: Int?,
    @SerializedName("total_families") val totalFamilies: Int?,
    @SerializedName("total_value_brl") val totalValueBrl: Double?,
    @SerializedName("coverage_rate") val coverageRate: Double?,
    @SerializedName("reference_date") val referenceDate: String?
)

data class PaginatedResponseDto<T>(
    val items: List<T>,
    val total: Int,
    val page: Int,
    val limit: Int,
    val pages: Int
)
```

### Aggregation DTOs

```kotlin
// data/api/dto/AggregationDto.kt

data class NationalAggregationDto(
    val level: String,
    val population: Long,
    @SerializedName("cadunico_families") val cadUnicoFamilies: Long,
    @SerializedName("total_municipalities") val totalMunicipalities: Int,
    @SerializedName("total_states") val totalStates: Int,
    @SerializedName("program_stats") val programStats: ProgramStatsDto?
)

data class StatesAggregationDto(
    val level: String,
    val count: Int,
    val states: List<StateAggregationDto>
)

data class StateAggregationDto(
    @SerializedName("ibge_code") val ibgeCode: String,
    val name: String,
    val abbreviation: String,
    val region: String,
    val population: Long,
    @SerializedName("municipality_count") val municipalityCount: Int,
    @SerializedName("total_beneficiaries") val totalBeneficiaries: Long?,
    @SerializedName("total_families") val totalFamilies: Long?,
    @SerializedName("cadunico_families") val cadUnicoFamilies: Long?,
    @SerializedName("total_value_brl") val totalValueBrl: Double?,
    @SerializedName("avg_coverage_rate") val avgCoverageRate: Double?
)

data class StateDetailDto(
    val level: String,
    val state: StateInfoDto,
    @SerializedName("municipality_count") val municipalityCount: Int,
    val municipalities: List<MunicipalityAggregationDto>
)

data class StateInfoDto(
    @SerializedName("ibge_code") val ibgeCode: String,
    val name: String,
    val abbreviation: String,
    val region: String
)

data class MunicipalityAggregationDto(
    @SerializedName("ibge_code") val ibgeCode: String,
    val name: String,
    val population: Int,
    @SerializedName("total_beneficiaries") val totalBeneficiaries: Int?,
    @SerializedName("total_families") val totalFamilies: Int?,
    @SerializedName("avg_coverage_rate") val avgCoverageRate: Double?
)

data class RegionsAggregationDto(
    val level: String,
    val count: Int,
    val regions: List<RegionAggregationDto>
)

data class RegionAggregationDto(
    val code: String,
    val name: String,
    val population: Long,
    @SerializedName("state_count") val stateCount: Int,
    @SerializedName("municipality_count") val municipalityCount: Int,
    @SerializedName("total_beneficiaries") val totalBeneficiaries: Long?,
    @SerializedName("total_families") val totalFamilies: Long?,
    @SerializedName("total_value_brl") val totalValueBrl: Double?,
    @SerializedName("avg_coverage_rate") val avgCoverageRate: Double?
)

data class TimeSeriesDto(
    val level: String,
    val count: Int,
    val data: List<TimeSeriesPointDto>
)

data class TimeSeriesPointDto(
    val date: String,
    val month: String,
    @SerializedName("total_beneficiaries") val totalBeneficiaries: Long,
    @SerializedName("total_families") val totalFamilies: Long,
    @SerializedName("total_value_brl") val totalValueBrl: Double,
    @SerializedName("avg_coverage_rate") val avgCoverageRate: Double
)

data class DemographicsDto(
    val level: String,
    @SerializedName("total_families") val totalFamilies: Long,
    @SerializedName("total_persons") val totalPersons: Long,
    @SerializedName("income_brackets") val incomeBrackets: IncomeBracketsDto,
    @SerializedName("age_distribution") val ageDistribution: AgeDistributionDto
)

data class IncomeBracketsDto(
    @SerializedName("extreme_poverty") val extremePoverty: Long,
    val poverty: Long,
    @SerializedName("low_income") val lowIncome: Long
)

data class AgeDistributionDto(
    @SerializedName("0_5") val age0to5: Long,
    @SerializedName("6_14") val age6to14: Long,
    @SerializedName("15_17") val age15to17: Long,
    @SerializedName("18_64") val age18to64: Long,
    @SerializedName("65_plus") val age65plus: Long
)
```

### GeoJSON DTOs

```kotlin
// data/api/dto/GeoJsonDto.kt

data class GeoJsonResponseDto(
    val type: String, // "FeatureCollection"
    val features: List<GeoJsonFeatureDto>,
    val metadata: GeoJsonMetadataDto?
)

data class GeoJsonFeatureDto(
    val type: String, // "Feature"
    val properties: GeoJsonPropertiesDto,
    val geometry: GeoJsonGeometryDto
)

data class GeoJsonPropertiesDto(
    @SerializedName("ibge_code") val ibgeCode: String,
    val name: String,
    val abbreviation: String?,
    val region: String?,
    val beneficiaries: Long?,
    val families: Long?,
    val coverage: Double?
)

data class GeoJsonGeometryDto(
    val type: String, // "MultiPolygon" or "Polygon"
    val coordinates: Any // List<List<List<List<Double>>>> for MultiPolygon
)

data class GeoJsonMetadataDto(
    val count: Int,
    @SerializedName("state_id") val stateId: Int?,
    val simplified: Boolean
)

data class BoundsDto(
    val bounds: List<Double>, // [minLng, minLat, maxLng, maxLat]
    val center: List<Double>  // [lng, lat]
)
```

### Ranking DTO

```kotlin
// data/api/dto/RankingDto.kt

data class RankingResponseDto(
    @SerializedName("program_code") val programCode: String,
    @SerializedName("program_name") val programName: String,
    @SerializedName("order_by") val orderBy: String,
    val ranking: List<RankingItemDto>
)

data class RankingItemDto(
    val rank: Int,
    @SerializedName("ibge_code") val ibgeCode: String,
    val name: String,
    @SerializedName("total_beneficiaries") val totalBeneficiaries: Int,
    @SerializedName("total_families") val totalFamilies: Int,
    @SerializedName("coverage_rate") val coverageRate: Double,
    @SerializedName("total_value_brl") val totalValueBrl: Double,
    @SerializedName("reference_date") val referenceDate: String
)
```

---

## DTO Mappers

```kotlin
// data/api/mapper/DtoMappers.kt

fun ProgramDto.toDomain(): Program = Program(
    code = ProgramCode.valueOf(code),
    name = name,
    description = description,
    dataSourceUrl = dataSourceUrl,
    updateFrequency = UpdateFrequency.valueOf(updateFrequency.uppercase()),
    nationalStats = nationalStats?.toDomain()
)

fun ProgramStatsDto.toDomain(): ProgramStats = ProgramStats(
    totalBeneficiaries = totalBeneficiaries,
    totalFamilies = totalFamilies,
    totalValueBrl = totalValueBrl,
    latestDataDate = latestDataDate?.let { LocalDate.parse(it) }
)

fun MunicipalityDetailDto.toDomain(): Municipality = Municipality(
    ibgeCode = ibgeCode,
    name = name,
    stateAbbreviation = stateAbbreviation,
    stateName = stateName,
    region = Region.valueOf(region),
    population = population,
    areaKm2 = areaKm2,
    cadUnicoFamilies = cadUnicoFamilies,
    totalBeneficiaries = totalBeneficiaries,
    totalFamilies = totalFamilies,
    totalValueBrl = totalValueBrl,
    coverageRate = coverageRate
)

fun NationalAggregationDto.toDomain(): NationalStats = NationalStats(
    population = population,
    cadUnicoFamilies = cadUnicoFamilies,
    totalMunicipalities = totalMunicipalities,
    totalStates = totalStates,
    programStats = programStats?.toDomain()
)

fun TimeSeriesPointDto.toDomain(): TimeSeriesPoint = TimeSeriesPoint(
    date = LocalDate.parse(date),
    monthLabel = month,
    totalBeneficiaries = totalBeneficiaries,
    totalFamilies = totalFamilies,
    totalValueBrl = totalValueBrl,
    avgCoverageRate = avgCoverageRate
)
```

---

## Repository Implementation

```kotlin
// data/repository/ProgramRepositoryImpl.kt

class ProgramRepositoryImpl @Inject constructor(
    private val api: TaNaMaoApi,
    private val dao: ProgramDao,
    @IoDispatcher private val dispatcher: CoroutineDispatcher
) : ProgramRepository {

    override fun getPrograms(): Flow<Result<List<Program>>> = flow {
        emit(Result.Loading)

        // Try cache first
        val cached = dao.getAll()
        if (cached.isNotEmpty()) {
            emit(Result.Success(cached.map { it.toDomain() }))
        }

        // Fetch fresh data
        try {
            val response = api.getPrograms()
            val programs = response.map { it.toDomain() }

            // Update cache
            dao.deleteAll()
            dao.insertAll(programs.map { it.toEntity() })

            emit(Result.Success(programs))
        } catch (e: Exception) {
            if (cached.isEmpty()) {
                emit(Result.Error(e.toAppError()))
            }
            // Keep using cache if network fails
        }
    }.flowOn(dispatcher)

    override suspend fun getProgram(code: ProgramCode): Result<Program> =
        withContext(dispatcher) {
            try {
                val response = api.getProgram(code.name)
                Result.Success(response.toDomain())
            } catch (e: Exception) {
                Result.Error(e.toAppError())
            }
        }

    override suspend fun getRanking(
        code: ProgramCode,
        stateCode: String?,
        orderBy: String,
        limit: Int
    ): Result<List<RankingItem>> = withContext(dispatcher) {
        try {
            val response = api.getProgramRanking(code.name, stateCode, orderBy, limit)
            Result.Success(response.ranking.map { it.toDomain() })
        } catch (e: Exception) {
            Result.Error(e.toAppError())
        }
    }
}
```

```kotlin
// data/repository/AggregationRepositoryImpl.kt

class AggregationRepositoryImpl @Inject constructor(
    private val api: TaNaMaoApi,
    @IoDispatcher private val dispatcher: CoroutineDispatcher
) : AggregationRepository {

    override suspend fun getNational(program: ProgramCode?): Result<NationalStats> =
        withContext(dispatcher) {
            try {
                val response = api.getNationalAggregation(program?.name)
                Result.Success(response.toDomain())
            } catch (e: Exception) {
                Result.Error(e.toAppError())
            }
        }

    override suspend fun getStates(program: ProgramCode?): Result<List<StateStats>> =
        withContext(dispatcher) {
            try {
                val response = api.getStatesAggregation(program?.name)
                Result.Success(response.states.map { it.toDomain() })
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
            val response = api.getTimeSeries(program?.name, stateCode)
            emit(Result.Success(response.data.map { it.toDomain() }))
        } catch (e: Exception) {
            emit(Result.Error(e.toAppError()))
        }
    }.flowOn(dispatcher)

    override suspend fun getDemographics(stateCode: String?): Result<Demographics> =
        withContext(dispatcher) {
            try {
                val response = api.getDemographics(stateCode)
                Result.Success(response.toDomain())
            } catch (e: Exception) {
                Result.Error(e.toAppError())
            }
        }
}
```

---

## Error Handling

```kotlin
// data/api/error/ApiError.kt

sealed class AppError : Exception() {
    data class Network(override val message: String = "Sem conexão com a internet") : AppError()
    data class Server(val code: Int, override val message: String) : AppError()
    data class NotFound(override val message: String = "Recurso não encontrado") : AppError()
    data class Timeout(override val message: String = "Tempo de conexão esgotado") : AppError()
    data class Unknown(override val cause: Throwable) : AppError()
}

fun Throwable.toAppError(): AppError = when (this) {
    is SocketTimeoutException -> AppError.Timeout()
    is UnknownHostException -> AppError.Network()
    is IOException -> AppError.Network()
    is HttpException -> when (code()) {
        404 -> AppError.NotFound()
        in 500..599 -> AppError.Server(code(), message())
        else -> AppError.Unknown(this)
    }
    else -> AppError.Unknown(this)
}

// Extension para exibir mensagem amigável
fun AppError.getUserMessage(): String = when (this) {
    is AppError.Network -> "Verifique sua conexão com a internet"
    is AppError.Server -> "Erro no servidor. Tente novamente mais tarde"
    is AppError.NotFound -> "Dados não encontrados"
    is AppError.Timeout -> "Conexão demorou muito. Tente novamente"
    is AppError.Unknown -> "Erro inesperado. Tente novamente"
}
```

---

## Network Module (Hilt)

```kotlin
// di/NetworkModule.kt

@Module
@InstallIn(SingletonComponent::class)
object NetworkModule {

    @Provides
    @Singleton
    fun provideOkHttpClient(): OkHttpClient {
        return OkHttpClient.Builder()
            .addInterceptor(HttpLoggingInterceptor().apply {
                level = if (BuildConfig.DEBUG) {
                    HttpLoggingInterceptor.Level.BODY
                } else {
                    HttpLoggingInterceptor.Level.NONE
                }
            })
            .addInterceptor { chain ->
                val request = chain.request().newBuilder()
                    .addHeader("Accept", "application/json")
                    .addHeader("User-Agent", "TaNaMao-Android/${BuildConfig.VERSION_NAME}")
                    .build()
                chain.proceed(request)
            }
            .connectTimeout(30, TimeUnit.SECONDS)
            .readTimeout(30, TimeUnit.SECONDS)
            .writeTimeout(30, TimeUnit.SECONDS)
            .build()
    }

    @Provides
    @Singleton
    fun provideGson(): Gson {
        return GsonBuilder()
            .setDateFormat("yyyy-MM-dd")
            .create()
    }

    @Provides
    @Singleton
    fun provideRetrofit(
        okHttpClient: OkHttpClient,
        gson: Gson
    ): Retrofit {
        return Retrofit.Builder()
            .baseUrl(BuildConfig.TANAMAO_API_URL)
            .client(okHttpClient)
            .addConverterFactory(GsonConverterFactory.create(gson))
            .build()
    }

    @Provides
    @Singleton
    fun provideTaNaMaoApi(retrofit: Retrofit): TaNaMaoApi {
        return retrofit.create(TaNaMaoApi::class.java)
    }
}
```

---

## Uso nos ViewModels

```kotlin
// presentation/viewmodel/HomeViewModel.kt

@HiltViewModel
class HomeViewModel @Inject constructor(
    private val getNationalStats: GetNationalStatsUseCase,
    private val getPrograms: GetProgramsUseCase
) : ViewModel() {

    private val _uiState = MutableStateFlow(HomeUiState())
    val uiState: StateFlow<HomeUiState> = _uiState.asStateFlow()

    init {
        loadData()
    }

    fun selectProgram(code: ProgramCode?) {
        _uiState.update { it.copy(selectedProgram = code) }
        loadNationalStats(code)
    }

    private fun loadData() {
        viewModelScope.launch {
            // Load programs
            getPrograms().collect { result ->
                when (result) {
                    is Result.Loading -> _uiState.update { it.copy(isLoading = true) }
                    is Result.Success -> _uiState.update {
                        it.copy(isLoading = false, programs = result.data)
                    }
                    is Result.Error -> _uiState.update {
                        it.copy(isLoading = false, error = result.exception.getUserMessage())
                    }
                }
            }
        }

        loadNationalStats(null)
    }

    private fun loadNationalStats(program: ProgramCode?) {
        viewModelScope.launch {
            when (val result = getNationalStats(program)) {
                is Result.Success -> _uiState.update {
                    it.copy(nationalStats = result.data)
                }
                is Result.Error -> _uiState.update {
                    it.copy(error = result.exception.getUserMessage())
                }
                else -> {}
            }
        }
    }
}

data class HomeUiState(
    val isLoading: Boolean = false,
    val error: String? = null,
    val programs: List<Program> = emptyList(),
    val selectedProgram: ProgramCode? = null,
    val nationalStats: NationalStats? = null
)
```

---

## Exemplos de Chamadas

### Buscar Município

```kotlin
// No ViewModel
fun searchMunicipality(query: String) {
    if (query.length < 2) return

    viewModelScope.launch {
        searchMunicipalities(query).collect { result ->
            when (result) {
                is Result.Success -> {
                    _uiState.update { it.copy(searchResults = result.data) }
                }
                is Result.Error -> {
                    // Handle error
                }
            }
        }
    }
}
```

### Carregar GeoJSON para Mapa

```kotlin
// No ViewModel de Mapa
fun loadStatesGeoJson(program: ProgramCode? = null) {
    viewModelScope.launch {
        when (val result = geoRepository.getStatesGeoJson(program = program)) {
            is Result.Success -> {
                _uiState.update { it.copy(geoJsonFeatures = result.data) }
            }
            is Result.Error -> {
                _uiState.update { it.copy(error = result.exception.getUserMessage()) }
            }
        }
    }
}
```

### Carregar Time Series

```kotlin
// No ViewModel de Detalhes
fun loadTimeSeries(program: ProgramCode, stateCode: String? = null) {
    viewModelScope.launch {
        aggregationRepository.getTimeSeries(program, stateCode).collect { result ->
            when (result) {
                is Result.Success -> {
                    _uiState.update { it.copy(timeSeries = result.data) }
                }
                is Result.Error -> {
                    _uiState.update { it.copy(error = result.exception.getUserMessage()) }
                }
            }
        }
    }
}
```

---

## API v2 - Catálogo Unificado de Benefícios

A API v2 fornece acesso ao catálogo unificado de 229+ benefícios sociais brasileiros, com motor de elegibilidade integrado e suporte offline via Room cache.

### Endpoints

```kotlin
// TaNaMaoApi.kt - Benefits API v2

@GET("v2/benefits/")
suspend fun getBenefitsV2(
    @Query("scope") scope: String? = null,
    @Query("state") state: String? = null,
    @Query("search") search: String? = null,
    @Query("page") page: Int = 1,
    @Query("limit") limit: Int = 50
): BenefitListResponseDto

@GET("v2/benefits/stats")
suspend fun getBenefitsStats(): BenefitStatsResponseDto

@GET("v2/benefits/by-location/{state_code}")
suspend fun getBenefitsByLocation(
    @Path("state_code") stateCode: String,
    @Query("municipality_ibge") municipalityIbge: String? = null
): BenefitsByLocationResponseDto

@GET("v2/benefits/{benefit_id}")
suspend fun getBenefitDetailV2(
    @Path("benefit_id") benefitId: String
): BenefitDetailDto

@POST("v2/benefits/eligibility/check")
suspend fun checkEligibility(
    @Body request: EligibilityRequestDto
): EligibilityResponseDto
```

### DTOs

```kotlin
// data/api/dto/BenefitV2Dto.kt

data class BenefitSummaryDto(
    val id: String,
    val name: String,
    @SerializedName("short_description") val shortDescription: String,
    val scope: String, // "federal", "state", "municipal", "sectoral"
    val state: String?,
    @SerializedName("estimated_value") val estimatedValue: EstimatedValueDto?,
    val status: String,
    val icon: String?,
    val category: String?
)

// data/api/dto/EligibilityV2Dto.kt

data class CitizenProfileDto(
    val estado: String,
    @SerializedName("municipio_ibge") val municipioIbge: String? = null,
    @SerializedName("pessoas_na_casa") val pessoasNaCasa: Int = 1,
    @SerializedName("renda_familiar_mensal") val rendaFamiliarMensal: Double = 0.0,
    @SerializedName("cadastrado_cadunico") val cadastradoCadunico: Boolean = false,
    // ... outros campos
)

data class EligibilityResponseDto(
    @SerializedName("profile_summary") val profileSummary: Map<String, Any>,
    val summary: EligibilitySummaryDto,
    @SerializedName("evaluated_at") val evaluatedAt: String
)
```

### Room Cache

O app usa Room para cache offline dos benefícios:

```kotlin
// data/local/database/entity/BenefitCacheEntity.kt

@Entity(tableName = "benefits_cache")
data class BenefitCacheEntity(
    @PrimaryKey val id: String,
    val name: String,
    val shortDescription: String,
    val scope: String,
    val state: String?,
    val estimatedValueJson: String?,
    val status: String,
    val icon: String?,
    val category: String?,
    val lastUpdated: Long = System.currentTimeMillis(),
    val expiresAt: Long = System.currentTimeMillis() + (24 * 60 * 60 * 1000)
)

// data/local/database/dao/BenefitCacheDao.kt

@Dao
interface BenefitCacheDao {
    @Query("SELECT * FROM benefits_cache WHERE expiresAt > :now")
    fun getAll(now: Long = System.currentTimeMillis()): Flow<List<BenefitCacheEntity>>

    @Query("SELECT * FROM benefits_cache WHERE scope = :scope AND expiresAt > :now")
    suspend fun getByScope(scope: String, now: Long = System.currentTimeMillis()): List<BenefitCacheEntity>

    @Insert(onConflict = OnConflictStrategy.REPLACE)
    suspend fun insertAll(benefits: List<BenefitCacheEntity>)

    @Query("DELETE FROM benefits_cache")
    suspend fun deleteAll()
}
```

### Repository

```kotlin
// data/repository/BenefitsV2RepositoryImpl.kt

@Singleton
class BenefitsV2RepositoryImpl @Inject constructor(
    private val api: TaNaMaoApi,
    private val cacheDao: BenefitCacheDao,
    @IoDispatcher private val dispatcher: CoroutineDispatcher
) : BenefitsV2Repository {

    override fun getBenefits(forceRefresh: Boolean): Flow<Result<List<BenefitSummaryDto>>> = flow {
        emit(Result.Loading)

        // Cache-first strategy
        if (!forceRefresh) {
            val cached = cacheDao.getAllOnce()
            if (cached.isNotEmpty()) {
                emit(Result.Success(cached.map { it.toDto() }))
            }
        }

        // Fetch from API
        try {
            val response = api.getBenefitsV2(limit = 500)
            cacheDao.deleteAll()
            cacheDao.insertAll(response.items.map { BenefitCacheEntity.fromDto(it) })
            emit(Result.Success(response.items))
        } catch (e: Exception) {
            val cached = cacheDao.getAllOnce()
            if (cached.isEmpty()) {
                emit(Result.Error(e.toAppError()))
            }
        }
    }.flowOn(dispatcher)

    override suspend fun checkEligibility(
        profile: CitizenProfileDto,
        scope: String?,
        includeNotApplicable: Boolean
    ): Result<EligibilityResponseDto> = withContext(dispatcher) {
        try {
            val request = EligibilityRequestDto(profile, scope, includeNotApplicable)
            Result.Success(api.checkEligibility(request))
        } catch (e: Exception) {
            Result.Error(e.toAppError())
        }
    }
}
```

### Uso no ViewModel

```kotlin
@HiltViewModel
class BenefitsViewModel @Inject constructor(
    private val repository: BenefitsV2Repository
) : ViewModel() {

    private val _uiState = MutableStateFlow(BenefitsUiState())
    val uiState: StateFlow<BenefitsUiState> = _uiState.asStateFlow()

    init {
        loadBenefits()
    }

    fun loadBenefits(forceRefresh: Boolean = false) {
        viewModelScope.launch {
            repository.getBenefits(forceRefresh).collect { result ->
                when (result) {
                    is Result.Loading -> _uiState.update { it.copy(isLoading = true) }
                    is Result.Success -> _uiState.update {
                        it.copy(isLoading = false, benefits = result.data)
                    }
                    is Result.Error -> _uiState.update {
                        it.copy(isLoading = false, error = result.exception.getUserMessage())
                    }
                }
            }
        }
    }

    fun checkEligibility(profile: CitizenProfileDto) {
        viewModelScope.launch {
            _uiState.update { it.copy(isCheckingEligibility = true) }

            when (val result = repository.checkEligibility(profile)) {
                is Result.Success -> _uiState.update {
                    it.copy(
                        isCheckingEligibility = false,
                        eligibilityResult = result.data
                    )
                }
                is Result.Error -> _uiState.update {
                    it.copy(
                        isCheckingEligibility = false,
                        error = result.exception.getUserMessage()
                    )
                }
            }
        }
    }
}

data class BenefitsUiState(
    val isLoading: Boolean = false,
    val isCheckingEligibility: Boolean = false,
    val benefits: List<BenefitSummaryDto> = emptyList(),
    val eligibilityResult: EligibilityResponseDto? = null,
    val error: String? = null
)
```
