package br.gov.tanamao.data.local.database

import androidx.room.Database
import androidx.room.RoomDatabase
import androidx.room.TypeConverters
import br.gov.tanamao.data.local.database.dao.BenefitCacheDao
import br.gov.tanamao.data.local.database.dao.ConsultationHistoryDao
import br.gov.tanamao.data.local.database.dao.UserDataCacheDao
import br.gov.tanamao.data.local.database.entity.BenefitCacheEntity
import br.gov.tanamao.data.local.database.entity.ConsultationHistoryEntity
import br.gov.tanamao.data.local.database.entity.UserDataCacheEntity

@Database(
    entities = [
        ConsultationHistoryEntity::class,
        UserDataCacheEntity::class,
        BenefitCacheEntity::class
    ],
    version = 2, // Incremented for new entity
    exportSchema = false
)
@TypeConverters(Converters::class)
abstract class AppDatabase : RoomDatabase() {
    abstract fun consultationHistoryDao(): ConsultationHistoryDao
    abstract fun userDataCacheDao(): UserDataCacheDao
    abstract fun benefitCacheDao(): BenefitCacheDao
}



