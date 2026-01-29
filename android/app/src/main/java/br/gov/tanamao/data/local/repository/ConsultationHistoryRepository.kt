package br.gov.tanamao.data.local.repository

import br.gov.tanamao.data.local.database.dao.ConsultationHistoryDao
import br.gov.tanamao.data.local.database.entity.ConsultationHistoryEntity
import br.gov.tanamao.domain.model.ConsultationHistory
import br.gov.tanamao.domain.model.ConsultationType
import kotlinx.coroutines.flow.Flow
import kotlinx.coroutines.flow.map
import java.time.LocalDate
import javax.inject.Inject

class ConsultationHistoryRepository @Inject constructor(
    private val dao: ConsultationHistoryDao
) {
    fun getAllHistory(): Flow<List<ConsultationHistory>> {
        return dao.getAllHistory().map { entities ->
            entities.map { it.toDomain() }
        }
    }

    fun getHistoryByType(type: ConsultationType): Flow<List<ConsultationHistory>> {
        return dao.getHistoryByType(type.name).map { entities ->
            entities.map { it.toDomain() }
        }
    }

    fun getHistoryFromDate(fromDate: LocalDate): Flow<List<ConsultationHistory>> {
        return dao.getHistoryFromDate(fromDate).map { entities ->
            entities.map { it.toDomain() }
        }
    }

    suspend fun save(consultation: ConsultationHistory) {
        dao.insert(consultation.toEntity())
    }

    suspend fun saveAll(consultations: List<ConsultationHistory>) {
        dao.insertAll(consultations.map { it.toEntity() })
    }

    suspend fun delete(consultation: ConsultationHistory) {
        dao.delete(consultation.toEntity())
    }

    suspend fun deleteOlderThan(beforeDate: LocalDate) {
        dao.deleteOlderThan(beforeDate)
    }

    suspend fun getCount(): Int {
        return dao.getCount()
    }
}

private fun ConsultationHistoryEntity.toDomain(): ConsultationHistory {
    return ConsultationHistory(
        id = id,
        date = date,
        type = ConsultationType.valueOf(type),
        query = query,
        result = result,
        toolsUsed = toolsUsed,
        success = success
    )
}

private fun ConsultationHistory.toEntity(): ConsultationHistoryEntity {
    return ConsultationHistoryEntity(
        id = id,
        date = date,
        type = type.name,
        query = query,
        result = result,
        toolsUsed = toolsUsed,
        success = success
    )
}



