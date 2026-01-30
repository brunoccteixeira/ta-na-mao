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

    // ============ BENEFITS API V2 (Unified Catalog) ============

    /**
     * Get paginated list of benefits with optional filters.
     */
    @GET("v2/benefits/")
    suspend fun getBenefitsV2(
        @Query("scope") scope: String? = null,
        @Query("state") state: String? = null,
        @Query("municipality_ibge") municipalityIbge: String? = null,
        @Query("sector") sector: String? = null,
        @Query("category") category: String? = null,
        @Query("status") status: String? = null,
        @Query("search") search: String? = null,
        @Query("page") page: Int = 1,
        @Query("limit") limit: Int = 50
    ): BenefitListResponseDto

    /**
     * Get benefits catalog statistics.
     */
    @GET("v2/benefits/stats")
    suspend fun getBenefitsStats(): BenefitStatsResponseDto

    /**
     * Get benefits by geographic location (federal + state + municipal + sectoral).
     */
    @GET("v2/benefits/by-location/{state_code}")
    suspend fun getBenefitsByLocation(
        @Path("state_code") stateCode: String,
        @Query("municipality_ibge") municipalityIbge: String? = null
    ): BenefitsByLocationResponseDto

    /**
     * Get a single benefit by ID.
     */
    @GET("v2/benefits/{benefit_id}")
    suspend fun getBenefitDetailV2(
        @Path("benefit_id") benefitId: String
    ): BenefitDetailDto

    // ============ ELIGIBILITY API V2 ============

    /**
     * Full eligibility check against all benefits.
     */
    @POST("v2/benefits/eligibility/check")
    suspend fun checkEligibility(
        @Body request: EligibilityRequestDto
    ): EligibilityResponseDto

    /**
     * Quick eligibility count (lighter response).
     */
    @GET("v2/benefits/eligibility/quick")
    suspend fun quickEligibilityCheck(
        @Query("estado") estado: String,
        @Query("renda_familiar_mensal") rendaFamiliarMensal: Double,
        @Query("pessoas_na_casa") pessoasNaCasa: Int,
        @Query("cadastrado_cadunico") cadastradoCadunico: Boolean
    ): QuickEligibilityResponseDto
}
