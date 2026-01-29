package br.gov.tanamao.data.local.database.dao

import androidx.room.*
import br.gov.tanamao.data.local.database.entity.UserDataCacheEntity

@Dao
interface UserDataCacheDao {
    @Query("SELECT * FROM user_data_cache WHERE id = :id")
    suspend fun get(id: String): UserDataCacheEntity?

    @Insert(onConflict = OnConflictStrategy.REPLACE)
    suspend fun insert(data: UserDataCacheEntity)

    @Query("DELETE FROM user_data_cache WHERE id = :id")
    suspend fun delete(id: String)

    @Query("DELETE FROM user_data_cache WHERE expiresAt < :currentTime")
    suspend fun deleteExpired(currentTime: Long = System.currentTimeMillis())
}



