package br.gov.tanamao.data.local.database.entity

import androidx.room.Entity
import androidx.room.PrimaryKey
import java.time.LocalDate

@Entity(tableName = "consultation_history")
data class ConsultationHistoryEntity(
    @PrimaryKey
    val id: String,
    val date: LocalDate,
    val type: String, // ConsultationType as string
    val query: String,
    val result: String? = null,
    val toolsUsed: List<String> = emptyList(),
    val success: Boolean = true,
    val createdAt: Long = System.currentTimeMillis()
)



