# Arquitetura do App Android

Este documento descreve a arquitetura do app Tá na Mão Android, seguindo os princípios de Clean Architecture com MVVM.

> **Status de Implementação**: Este documento descreve a arquitetura alvo. Alguns componentes estão em desenvolvimento. Veja [FEATURES.md](./FEATURES.md) para o status atual de cada funcionalidade.

## Visão Geral

```
┌─────────────────────────────────────────────────────────────┐
│                    PRESENTATION LAYER                        │
│  ┌─────────────┐  ┌─────────────┐  ┌─────────────────────┐  │
│  │   Screens   │  │  ViewModels │  │  UI State (Flow)    │  │
│  │  (Compose)  │──│             │──│  UiEvent, UiState   │  │
│  └─────────────┘  └─────────────┘  └─────────────────────┘  │
└───────────────────────────┬─────────────────────────────────┘
                            │
┌───────────────────────────▼─────────────────────────────────┐
│                      DOMAIN LAYER                            │
│  ┌─────────────┐  ┌─────────────┐  ┌─────────────────────┐  │
│  │  Use Cases  │  │   Models    │  │  Repository         │  │
│  │             │──│  (Entities) │──│  Interfaces         │  │
│  └─────────────┘  └─────────────┘  └─────────────────────┘  │
└───────────────────────────┬─────────────────────────────────┘
                            │
┌───────────────────────────▼─────────────────────────────────┐
│                       DATA LAYER                             │
│  ┌─────────────┐  ┌─────────────┐  ┌─────────────────────┐  │
│  │  Remote     │  │   Local     │  │  Repository         │  │
│  │  (Retrofit) │──│   (Room)    │──│  Implementations    │  │
│  └─────────────┘  └─────────────┘  └─────────────────────┘  │
└─────────────────────────────────────────────────────────────┘
```

## Camadas

### 1. Presentation Layer (UI)

Responsável pela interface do usuário e interações.

```kotlin
// Telas Compose
presentation/
├── ui/
│   ├── home/
│   │   ├── HomeScreen.kt
│   │   └── HomeViewModel.kt
│   ├── map/
│   │   ├── MapScreen.kt
│   │   └── MapViewModel.kt
│   ├── search/
│   │   ├── SearchScreen.kt
│   │   └── SearchViewModel.kt
│   ├── details/
│   │   ├── MunicipalityScreen.kt
│   │   └── MunicipalityViewModel.kt
│   └── chat/
│       ├── ChatScreen.kt
│       └── ChatViewModel.kt
├── components/
│   ├── ProgramCard.kt
│   ├── StatCard.kt
│   ├── SearchBar.kt
│   ├── RankingList.kt
│   └── ChartComponents.kt
├── navigation/
│   └── TaNaMaoNavHost.kt
└── theme/
    ├── Color.kt
    ├── Type.kt
    └── Theme.kt
```

#### ViewModel Pattern

```kotlin
@HiltViewModel
class HomeViewModel @Inject constructor(
    private val getNationalStats: GetNationalStatsUseCase,
    private val getPrograms: GetProgramsUseCase
) : ViewModel() {

    private val _uiState = MutableStateFlow(HomeUiState())
    val uiState: StateFlow<HomeUiState> = _uiState.asStateFlow()

    private val _events = Channel<HomeEvent>()
    val events = _events.receiveAsFlow()

    init {
        loadData()
    }

    fun onAction(action: HomeAction) {
        when (action) {
            is HomeAction.SelectProgram -> selectProgram(action.code)
            is HomeAction.RefreshData -> loadData()
            is HomeAction.NavigateToMap -> navigateToMap()
        }
    }

    private fun loadData() {
        viewModelScope.launch {
            _uiState.update { it.copy(isLoading = true) }

            combine(
                getNationalStats(),
                getPrograms()
            ) { stats, programs ->
                _uiState.update {
                    it.copy(
                        isLoading = false,
                        nationalStats = stats,
                        programs = programs
                    )
                }
            }.collect()
        }
    }
}

// UI State
data class HomeUiState(
    val isLoading: Boolean = false,
    val error: String? = null,
    val nationalStats: NationalStats? = null,
    val programs: List<Program> = emptyList(),
    val selectedProgram: ProgramCode? = null
)

// Actions (User Intents)
sealed class HomeAction {
    data class SelectProgram(val code: ProgramCode) : HomeAction()
    object RefreshData : HomeAction()
    object NavigateToMap : HomeAction()
}

// Events (One-time effects)
sealed class HomeEvent {
    data class ShowError(val message: String) : HomeEvent()
    data class NavigateTo(val route: String) : HomeEvent()
}
```

### 2. Domain Layer

Contém a lógica de negócio pura, sem dependências de framework.

```kotlin
domain/
├── model/
│   ├── Program.kt
│   ├── Municipality.kt
│   ├── NationalStats.kt
│   ├── StateData.kt
│   └── BeneficiaryData.kt
├── repository/
│   ├── ProgramRepository.kt
│   ├── MunicipalityRepository.kt
│   ├── AggregationRepository.kt
│   └── GeoRepository.kt
└── usecase/
    ├── GetProgramsUseCase.kt
    ├── GetNationalStatsUseCase.kt
    ├── SearchMunicipalitiesUseCase.kt
    ├── GetMunicipalityDetailsUseCase.kt
    ├── GetTimeSeriesUseCase.kt
    └── CheckEligibilityUseCase.kt
```

#### Use Case Pattern

```kotlin
class GetProgramsUseCase @Inject constructor(
    private val programRepository: ProgramRepository
) {
    operator fun invoke(): Flow<Result<List<Program>>> = flow {
        emit(Result.Loading)
        try {
            val programs = programRepository.getPrograms()
            emit(Result.Success(programs))
        } catch (e: Exception) {
            emit(Result.Error(e))
        }
    }
}

class SearchMunicipalitiesUseCase @Inject constructor(
    private val municipalityRepository: MunicipalityRepository
) {
    operator fun invoke(query: String): Flow<Result<List<Municipality>>> = flow {
        if (query.length < 2) {
            emit(Result.Success(emptyList()))
            return@flow
        }

        emit(Result.Loading)
        try {
            val results = municipalityRepository.search(query)
            emit(Result.Success(results))
        } catch (e: Exception) {
            emit(Result.Error(e))
        }
    }
}
```

#### Domain Models

```kotlin
data class Program(
    val code: ProgramCode,
    val name: String,
    val description: String,
    val dataSourceUrl: String,
    val updateFrequency: UpdateFrequency,
    val nationalStats: ProgramStats?
)

enum class ProgramCode {
    BPC,
    FARMACIA_POPULAR,
    TSEE,
    DIGNIDADE_MENSTRUAL,
    CADUNICO
}

data class Municipality(
    val ibgeCode: String,
    val name: String,
    val stateAbbreviation: String,
    val stateName: String,
    val region: Region,
    val population: Int,
    val areaKm2: Double?
)

data class NationalStats(
    val population: Long,
    val cadUnicoFamilies: Long,
    val totalBeneficiaries: Long,
    val totalFamilies: Long,
    val totalValueBrl: Double,
    val avgCoverageRate: Double,
    val municipalitiesCovered: Int
)

sealed class Result<out T> {
    object Loading : Result<Nothing>()
    data class Success<T>(val data: T) : Result<T>()
    data class Error(val exception: Throwable) : Result<Nothing>()
}
```

### 3. Data Layer

Implementa as interfaces de repositório e gerencia fontes de dados.

```kotlin
data/
├── api/
│   ├── TaNaMaoApi.kt
│   ├── dto/
│   │   ├── ProgramDto.kt
│   │   ├── MunicipalityDto.kt
│   │   ├── AggregationDto.kt
│   │   └── GeoJsonDto.kt
│   └── mapper/
│       └── DtoMappers.kt
├── db/
│   ├── TaNaMaoDatabase.kt
│   ├── dao/
│   │   ├── ProgramDao.kt
│   │   ├── MunicipalityDao.kt
│   │   └── CacheDao.kt
│   └── entity/
│       ├── ProgramEntity.kt
│       ├── MunicipalityEntity.kt
│       └── CacheEntity.kt
└── repository/
    ├── ProgramRepositoryImpl.kt
    ├── MunicipalityRepositoryImpl.kt
    ├── AggregationRepositoryImpl.kt
    └── GeoRepositoryImpl.kt
```

#### Repository Implementation

```kotlin
class ProgramRepositoryImpl @Inject constructor(
    private val api: TaNaMaoApi,
    private val dao: ProgramDao,
    private val dispatcher: CoroutineDispatcher
) : ProgramRepository {

    override suspend fun getPrograms(): List<Program> = withContext(dispatcher) {
        try {
            // Try network first
            val response = api.getPrograms()
            val programs = response.map { it.toDomain() }

            // Cache locally
            dao.insertAll(programs.map { it.toEntity() })

            programs
        } catch (e: Exception) {
            // Fallback to cache
            dao.getAll().map { it.toDomain() }
        }
    }

    override suspend fun getProgram(code: ProgramCode): Program = withContext(dispatcher) {
        val response = api.getProgram(code.name)
        response.toDomain()
    }

    override suspend fun getProgramRanking(
        code: ProgramCode,
        stateCode: String?,
        orderBy: String,
        limit: Int
    ): List<RankingItem> = withContext(dispatcher) {
        val response = api.getProgramRanking(code.name, stateCode, orderBy, limit)
        response.ranking.map { it.toDomain() }
    }
}
```

## Injeção de Dependências (Hilt)

```kotlin
di/
├── AppModule.kt
├── NetworkModule.kt
├── DatabaseModule.kt
└── RepositoryModule.kt
```

### Network Module

```kotlin
@Module
@InstallIn(SingletonComponent::class)
object NetworkModule {

    @Provides
    @Singleton
    fun provideOkHttpClient(): OkHttpClient {
        return OkHttpClient.Builder()
            .addInterceptor(HttpLoggingInterceptor().apply {
                level = HttpLoggingInterceptor.Level.BODY
            })
            .connectTimeout(30, TimeUnit.SECONDS)
            .readTimeout(30, TimeUnit.SECONDS)
            .build()
    }

    @Provides
    @Singleton
    fun provideRetrofit(okHttpClient: OkHttpClient): Retrofit {
        return Retrofit.Builder()
            .baseUrl(BuildConfig.TANAMAO_API_URL)
            .client(okHttpClient)
            .addConverterFactory(GsonConverterFactory.create())
            .build()
    }

    @Provides
    @Singleton
    fun provideTaNaMaoApi(retrofit: Retrofit): TaNaMaoApi {
        return retrofit.create(TaNaMaoApi::class.java)
    }
}
```

### Database Module

```kotlin
@Module
@InstallIn(SingletonComponent::class)
object DatabaseModule {

    @Provides
    @Singleton
    fun provideDatabase(@ApplicationContext context: Context): TaNaMaoDatabase {
        return Room.databaseBuilder(
            context,
            TaNaMaoDatabase::class.java,
            "tanamao.db"
        ).build()
    }

    @Provides
    fun provideProgramDao(database: TaNaMaoDatabase): ProgramDao {
        return database.programDao()
    }

    @Provides
    fun provideMunicipalityDao(database: TaNaMaoDatabase): MunicipalityDao {
        return database.municipalityDao()
    }
}
```

### Repository Module

```kotlin
@Module
@InstallIn(SingletonComponent::class)
abstract class RepositoryModule {

    @Binds
    @Singleton
    abstract fun bindProgramRepository(
        impl: ProgramRepositoryImpl
    ): ProgramRepository

    @Binds
    @Singleton
    abstract fun bindMunicipalityRepository(
        impl: MunicipalityRepositoryImpl
    ): MunicipalityRepository

    @Binds
    @Singleton
    abstract fun bindAggregationRepository(
        impl: AggregationRepositoryImpl
    ): AggregationRepository

    @Binds
    @Singleton
    abstract fun bindGeoRepository(
        impl: GeoRepositoryImpl
    ): GeoRepository
}
```

## Navegação

```kotlin
// navigation/TaNaMaoNavHost.kt
@Composable
fun TaNaMaoNavHost(
    navController: NavHostController,
    modifier: Modifier = Modifier
) {
    NavHost(
        navController = navController,
        startDestination = Screen.Home.route,
        modifier = modifier
    ) {
        composable(Screen.Home.route) {
            HomeScreen(
                onNavigateToMap = { navController.navigate(Screen.Map.route) },
                onNavigateToSearch = { navController.navigate(Screen.Search.route) },
                onNavigateToChat = { navController.navigate(Screen.Chat.route) }
            )
        }

        composable(Screen.Map.route) {
            MapScreen(
                onNavigateToMunicipality = { ibgeCode ->
                    navController.navigate(Screen.Municipality.createRoute(ibgeCode))
                },
                onNavigateBack = { navController.popBackStack() }
            )
        }

        composable(Screen.Search.route) {
            SearchScreen(
                onNavigateToMunicipality = { ibgeCode ->
                    navController.navigate(Screen.Municipality.createRoute(ibgeCode))
                },
                onNavigateBack = { navController.popBackStack() }
            )
        }

        composable(
            route = Screen.Municipality.route,
            arguments = listOf(navArgument("ibgeCode") { type = NavType.StringType })
        ) { backStackEntry ->
            val ibgeCode = backStackEntry.arguments?.getString("ibgeCode") ?: return@composable
            MunicipalityScreen(
                ibgeCode = ibgeCode,
                onNavigateBack = { navController.popBackStack() }
            )
        }

        composable(Screen.Chat.route) {
            ChatScreen(
                onNavigateBack = { navController.popBackStack() }
            )
        }
    }
}

sealed class Screen(val route: String) {
    object Home : Screen("home")
    object Map : Screen("map")
    object Search : Screen("search")
    object Chat : Screen("chat")
    object Municipality : Screen("municipality/{ibgeCode}") {
        fun createRoute(ibgeCode: String) = "municipality/$ibgeCode"
    }
}
```

## Fluxo de Dados

```
┌─────────────┐     ┌─────────────┐     ┌─────────────┐
│   Screen    │────▶│  ViewModel  │────▶│  Use Case   │
│  (Compose)  │◀────│             │◀────│             │
└─────────────┘     └─────────────┘     └─────────────┘
                                               │
                                               ▼
                                        ┌─────────────┐
                                        │ Repository  │
                                        │  Interface  │
                                        └─────────────┘
                                               │
                          ┌────────────────────┼────────────────────┐
                          ▼                    ▼                    ▼
                   ┌─────────────┐     ┌─────────────┐     ┌─────────────┐
                   │   Remote    │     │   Local     │     │   Memory    │
                   │   (API)     │     │   (Room)    │     │   Cache     │
                   └─────────────┘     └─────────────┘     └─────────────┘
```

## Estratégia de Cache

### Cache-First Strategy

```kotlin
override fun getPrograms(): Flow<List<Program>> = flow {
    // 1. Emit cached data immediately
    val cached = dao.getAll()
    if (cached.isNotEmpty()) {
        emit(cached.map { it.toDomain() })
    }

    // 2. Fetch fresh data from network
    try {
        val fresh = api.getPrograms()
        dao.insertAll(fresh.map { it.toEntity() })
        emit(fresh.map { it.toDomain() })
    } catch (e: Exception) {
        if (cached.isEmpty()) {
            throw e
        }
        // Keep using cached data if network fails
    }
}
```

### Cache Invalidation

```kotlin
@Entity(tableName = "cache_metadata")
data class CacheMetadata(
    @PrimaryKey val key: String,
    val lastUpdated: Long,
    val ttlMillis: Long
) {
    fun isExpired(): Boolean {
        return System.currentTimeMillis() > lastUpdated + ttlMillis
    }
}

// TTLs recomendados
object CacheTTL {
    const val PROGRAMS = 24 * 60 * 60 * 1000L      // 24 horas
    const val AGGREGATIONS = 60 * 60 * 1000L       // 1 hora
    const val MUNICIPALITIES = 7 * 24 * 60 * 60 * 1000L  // 7 dias
    const val GEOJSON = 30 * 24 * 60 * 60 * 1000L  // 30 dias
}
```

## Tratamento de Erros

```kotlin
sealed class AppError : Exception() {
    data class NetworkError(override val message: String) : AppError()
    data class ServerError(val code: Int, override val message: String) : AppError()
    data class NotFoundError(override val message: String) : AppError()
    data class UnknownError(override val cause: Throwable) : AppError()
}

fun Throwable.toAppError(): AppError = when (this) {
    is IOException -> AppError.NetworkError("Sem conexão com a internet")
    is HttpException -> when (code()) {
        404 -> AppError.NotFoundError("Recurso não encontrado")
        in 500..599 -> AppError.ServerError(code(), "Erro no servidor")
        else -> AppError.UnknownError(this)
    }
    else -> AppError.UnknownError(this)
}
```

## Testes

### Unit Tests

```kotlin
@Test
fun `getPrograms returns cached data when network fails`() = runTest {
    // Given
    val cachedPrograms = listOf(testProgram)
    coEvery { dao.getAll() } returns cachedPrograms.map { it.toEntity() }
    coEvery { api.getPrograms() } throws IOException()

    // When
    val result = repository.getPrograms()

    // Then
    assertEquals(cachedPrograms, result)
}
```

### Instrumented Tests

```kotlin
@HiltAndroidTest
class HomeScreenTest {
    @get:Rule
    val hiltRule = HiltAndroidRule(this)

    @get:Rule
    val composeRule = createComposeRule()

    @Test
    fun homeScreen_displaysKPIs() {
        composeRule.setContent {
            TaNaMaoTheme {
                HomeScreen()
            }
        }

        composeRule.onNodeWithText("População").assertIsDisplayed()
        composeRule.onNodeWithText("Famílias CadÚnico").assertIsDisplayed()
    }
}
```
