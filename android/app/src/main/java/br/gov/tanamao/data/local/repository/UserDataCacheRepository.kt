package br.gov.tanamao.data.local.repository

import br.gov.tanamao.data.local.database.dao.UserDataCacheDao
import br.gov.tanamao.data.local.database.entity.UserDataCacheEntity
import com.google.gson.Gson
import com.google.gson.reflect.TypeToken
import javax.inject.Inject

class UserDataCacheRepository @Inject constructor(
    private val dao: UserDataCacheDao,
    private val gson: Gson
) {
    suspend fun getCachedUserData(): CachedUserData? {
        val entity = dao.get("user_data") ?: return null
        
        // Check if expired
        if (System.currentTimeMillis() > entity.expiresAt) {
            dao.delete("user_data")
            return null
        }
        
        return try {
            gson.fromJson(entity.data, CachedUserData::class.java)
        } catch (e: Exception) {
            null
        }
    }

    suspend fun saveUserData(data: CachedUserData) {
        val json = gson.toJson(data)
        dao.insert(
            UserDataCacheEntity(
                id = "user_data",
                data = json
            )
        )
    }

    suspend fun clearCache() {
        dao.delete("user_data")
    }

    suspend fun cleanupExpired() {
        dao.deleteExpired()
    }
}

data class CachedUserData(
    // Store as serializable maps for Gson compatibility
    val benefits: List<Map<String, Any>> = emptyList(),
    val stats: Map<String, Any> = emptyMap(),
    val userName: String? = null,
    val totalReceived: Double? = null,
    val totalReceivedThisYear: Double? = null,
    val lastUpdated: Long = System.currentTimeMillis()
)



