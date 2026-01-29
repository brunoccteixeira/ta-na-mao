package br.gov.tanamao.data.local.database.dao

import androidx.room.*
import br.gov.tanamao.data.local.database.entity.ConsultationHistoryEntity
import kotlinx.coroutines.flow.Flow
import java.time.LocalDate

@Dao
interface ConsultationHistoryDao {
    @Query("SELECT * FROM consultation_history ORDER BY date DESC, createdAt DESC")
    fun getAllHistory(): Flow<List<ConsultationHistoryEntity>>

    @Query("SELECT * FROM consultation_history WHERE type = :type ORDER BY date DESC")
    fun getHistoryByType(type: String): Flow<List<ConsultationHistoryEntity>>

    @Query("SELECT * FROM consultation_history WHERE date >= :fromDate ORDER BY date DESC")
    fun getHistoryFromDate(fromDate: LocalDate): Flow<List<ConsultationHistoryEntity>>

    @Insert(onConflict = OnConflictStrategy.REPLACE)
    suspend fun insert(consultation: ConsultationHistoryEntity)

    @Insert(onConflict = OnConflictStrategy.REPLACE)
    suspend fun insertAll(consultations: List<ConsultationHistoryEntity>)

    @Delete
    suspend fun delete(consultation: ConsultationHistoryEntity)

    @Query("DELETE FROM consultation_history WHERE date < :beforeDate")
    suspend fun deleteOlderThan(beforeDate: LocalDate)

    @Query("SELECT COUNT(*) FROM consultation_history")
    suspend fun getCount(): Int
}



