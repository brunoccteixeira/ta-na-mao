package br.gov.tanamao.di

import android.content.Context
import androidx.room.Room
import br.gov.tanamao.data.local.database.AppDatabase
import br.gov.tanamao.data.local.database.dao.BenefitCacheDao
import br.gov.tanamao.data.local.database.dao.ConsultationHistoryDao
import br.gov.tanamao.data.local.database.dao.UserDataCacheDao
import dagger.Module
import dagger.Provides
import dagger.hilt.InstallIn
import dagger.hilt.android.qualifiers.ApplicationContext
import dagger.hilt.components.SingletonComponent
import javax.inject.Singleton

@Module
@InstallIn(SingletonComponent::class)
object DatabaseModule {

    @Provides
    @Singleton
    fun provideAppDatabase(@ApplicationContext context: Context): AppDatabase {
        return Room.databaseBuilder(
            context,
            AppDatabase::class.java,
            "tanamao_database"
        )
            .fallbackToDestructiveMigration() // For development only
            .build()
    }

    @Provides
    fun provideConsultationHistoryDao(database: AppDatabase): ConsultationHistoryDao {
        return database.consultationHistoryDao()
    }

    @Provides
    fun provideUserDataCacheDao(database: AppDatabase): UserDataCacheDao {
        return database.userDataCacheDao()
    }

    @Provides
    fun provideBenefitCacheDao(database: AppDatabase): BenefitCacheDao {
        return database.benefitCacheDao()
    }
}



