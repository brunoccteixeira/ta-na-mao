package br.gov.tanamao.data.local.database.entity

import androidx.room.Entity
import androidx.room.PrimaryKey

@Entity(tableName = "user_data_cache")
data class UserDataCacheEntity(
    @PrimaryKey
    val id: String = "user_data",
    val data: String, // JSON string of user data
    val lastUpdated: Long = System.currentTimeMillis(),
    val expiresAt: Long = System.currentTimeMillis() + (24 * 60 * 60 * 1000) // 24 hours
)



