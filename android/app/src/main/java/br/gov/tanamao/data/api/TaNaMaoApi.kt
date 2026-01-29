package br.gov.tanamao.data.api

import br.gov.tanamao.data.api.dto.*
import retrofit2.http.Body
import retrofit2.http.DELETE
import retrofit2.http.GET
import retrofit2.http.POST
import retrofit2.http.Path
import retrofit2.http.Query

/**
 * Retrofit API interface for Tá na Mão backend.
 */
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

    @GET("geo/bounds")
    suspend fun getBounds(
        @Query("state_code") stateCode: String? = null
    ): BoundsDto

    // ============ HEALTH ============

    @GET("health")
    suspend fun healthCheck(): HealthDto

    // ============ AGENT (Conversational AI) ============

    @GET("agent/status")
    suspend fun getAgentStatus(): AgentStatusDto

    @POST("agent/start")
    suspend fun startAgentConversation(): WelcomeResponseDto

    @POST("agent/chat")
    suspend fun sendAgentMessage(@Body request: ChatRequestDto): ChatResponseDto

    @POST("agent/reset/{session_id}")
    suspend fun resetAgentConversation(@Path("session_id") sessionId: String)

    @DELETE("agent/session/{session_id}")
    suspend fun endAgentSession(@Path("session_id") sessionId: String)

    // ============ NEARBY SERVICES ============

    @GET("nearby/farmacias")
    suspend fun getNearbyPharmacies(
        @Query("latitude") latitude: Double? = null,
        @Query("longitude") longitude: Double? = null,
        @Query("cep") cep: String? = null,
        @Query("programa") programa: String = "FARMACIA_POPULAR",
        @Query("raio_metros") raioMetros: Int = 3000,
        @Query("limite") limite: Int = 5
    ): NearbyResponseDto

    @GET("nearby/cras")
    suspend fun getNearbyCras(
        @Query("latitude") latitude: Double? = null,
        @Query("longitude") longitude: Double? = null,
        @Query("cep") cep: String? = null,
        @Query("raio_metros") raioMetros: Int = 10000,
        @Query("limite") limite: Int = 3
    ): NearbyResponseDto

    // ============ MONEY FORGOTTEN (Dinheiro Esquecido) ============
    // These are called via agent chat, but we can add convenience methods
    // The actual calls go through agent/chat endpoint with specific messages

    // ============ USER DATA (meus_dados) ============
    // Called via agent/chat with message "meus dados" or "meus benefícios"
    // Response will be in ChatResponseDto.response field

    // ============ ALERTS (gerar_alertas_beneficios) ============
    // Called via agent/chat with message "meus alertas" or "alertas"
    // Response will be in ChatResponseDto.response field

    // ============ CRAS PREPARATION ============
    // Called via agent/chat with message "preparar para CRAS" or "checklist CRAS"
    // Response will be in ChatResponseDto.response field
}
