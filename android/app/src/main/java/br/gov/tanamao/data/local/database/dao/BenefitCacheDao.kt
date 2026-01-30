package br.gov.tanamao.data.local.database.dao

import androidx.room.Dao
import androidx.room.Insert
import androidx.room.OnConflictStrategy
import androidx.room.Query
import br.gov.tanamao.data.local.database.entity.BenefitCacheEntity
import kotlinx.coroutines.flow.Flow

/**
 * DAO for benefits cache operations.
 * Provides offline access to benefits catalog.
 */
@Dao
interface BenefitCacheDao {

    /**
     * Get all non-expired cached benefits.
     */
    @Query("SELECT * FROM benefits_cache WHERE expiresAt > :now ORDER BY name ASC")
    fun getAll(now: Long = System.currentTimeMillis()): Flow<List<BenefitCacheEntity>>

    /**
     * Get all non-expired cached benefits (suspend version for one-time reads).
     */
    @Query("SELECT * FROM benefits_cache WHERE expiresAt > :now ORDER BY name ASC")
    suspend fun getAllOnce(now: Long = System.currentTimeMillis()): List<BenefitCacheEntity>

    /**
     * Get a single benefit by ID if not expired.
     */
    @Query("SELECT * FROM benefits_cache WHERE id = :id AND expiresAt > :now")
    suspend fun getById(id: String, now: Long = System.currentTimeMillis()): BenefitCacheEntity?

    /**
     * Get benefits by scope.
     */
    @Query("SELECT * FROM benefits_cache WHERE scope = :scope AND expiresAt > :now ORDER BY name ASC")
    suspend fun getByScope(scope: String, now: Long = System.currentTimeMillis()): List<BenefitCacheEntity>

    /**
     * Get benefits by state (federal + state-specific).
     */
    @Query("""
        SELECT * FROM benefits_cache
        WHERE (scope = 'federal' OR (scope = 'state' AND state = :stateCode) OR (scope = 'sectoral'))
        AND expiresAt > :now
        ORDER BY name ASC
    """)
    suspend fun getByState(stateCode: String, now: Long = System.currentTimeMillis()): List<BenefitCacheEntity>

    /**
     * Get benefits for a specific municipality (federal + state + municipal).
     */
    @Query("""
        SELECT * FROM benefits_cache
        WHERE (
            scope = 'federal'
            OR (scope = 'state' AND state = :stateCode)
            OR (scope = 'municipal' AND municipalityIbge = :municipalityIbge)
            OR scope = 'sectoral'
        )
        AND expiresAt > :now
        ORDER BY name ASC
    """)
    suspend fun getByMunicipality(
        stateCode: String,
        municipalityIbge: String,
        now: Long = System.currentTimeMillis()
    ): List<BenefitCacheEntity>

    /**
     * Search benefits by name or description.
     */
    @Query("""
        SELECT * FROM benefits_cache
        WHERE (name LIKE '%' || :query || '%' OR shortDescription LIKE '%' || :query || '%')
        AND expiresAt > :now
        ORDER BY name ASC
    """)
    suspend fun search(query: String, now: Long = System.currentTimeMillis()): List<BenefitCacheEntity>

    /**
     * Get count of cached benefits.
     */
    @Query("SELECT COUNT(*) FROM benefits_cache WHERE expiresAt > :now")
    suspend fun getCount(now: Long = System.currentTimeMillis()): Int

    /**
     * Insert or replace benefits.
     */
    @Insert(onConflict = OnConflictStrategy.REPLACE)
    suspend fun insertAll(benefits: List<BenefitCacheEntity>)

    /**
     * Insert or replace a single benefit.
     */
    @Insert(onConflict = OnConflictStrategy.REPLACE)
    suspend fun insert(benefit: BenefitCacheEntity)

    /**
     * Delete expired entries.
     */
    @Query("DELETE FROM benefits_cache WHERE expiresAt < :now")
    suspend fun deleteExpired(now: Long = System.currentTimeMillis())

    /**
     * Delete all entries (for full refresh).
     */
    @Query("DELETE FROM benefits_cache")
    suspend fun deleteAll()

    /**
     * Check if cache has valid (non-expired) data.
     */
    @Query("SELECT COUNT(*) > 0 FROM benefits_cache WHERE expiresAt > :now")
    suspend fun hasValidCache(now: Long = System.currentTimeMillis()): Boolean
}
