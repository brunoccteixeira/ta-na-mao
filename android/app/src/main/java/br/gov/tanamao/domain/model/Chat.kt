package br.gov.tanamao.domain.model

import java.time.LocalDateTime
import java.util.UUID

/**
 * Chat message in the eligibility assistant conversation
 */
data class ChatMessage(
    val id: String = UUID.randomUUID().toString(),
    val content: String,
    val sender: MessageSender,
    val timestamp: LocalDateTime = LocalDateTime.now(),
    val type: MessageType = MessageType.TEXT,
    val metadata: MessageMetadata? = null,
    val status: MessageStatus = MessageStatus.SENT
)

enum class MessageSender {
    USER,
    ASSISTANT,
    SYSTEM
}

enum class MessageType {
    /** Plain text message */
    TEXT,
    /** Quick reply options for user */
    QUICK_REPLIES,
    /** Eligibility result card */
    ELIGIBILITY_RESULT,
    /** Document checklist */
    DOCUMENT_LIST,
    /** Location/map card */
    LOCATION,
    /** Loading/typing indicator */
    LOADING,
    /** Error message */
    ERROR,
    /** Image message (e.g., prescription photo) */
    IMAGE,
    /** Money check result (PIS/PASEP, SVR, FGTS) */
    MONEY_RESULT,
    /** Medicine availability result */
    MEDICINE_RESULT
}

enum class MessageStatus {
    SENDING,
    SENT,
    DELIVERED,
    READ,
    ERROR
}

/**
 * Metadata associated with special message types
 */
sealed class MessageMetadata {
    data class QuickReplies(
        val options: List<QuickReplyOption>
    ) : MessageMetadata()

    data class EligibilityResult(
        val programCode: String,
        val programName: String,
        val isEligible: Boolean,
        val score: Float,
        val criteria: List<EligibilityCriterion>,
        val recommendation: String
    ) : MessageMetadata()

    data class DocumentList(
        val title: String,
        val documents: List<DocumentItem>
    ) : MessageMetadata()

    data class LocationCard(
        val name: String,
        val address: String,
        val distance: String?,
        val latitude: Double,
        val longitude: Double,
        val phone: String? = null,
        val hours: String? = null,
        val mapsUrl: String? = null,
        val wazeUrl: String? = null
    ) : MessageMetadata()

    data class ImageData(
        val base64: String,
        val mimeType: String = "image/jpeg",
        val caption: String? = null
    ) : MessageMetadata()

    data class MoneyResult(
        val totalAmount: Double?,
        val types: List<MoneyTypeResult>
    ) : MessageMetadata()

    data class MedicineResult(
        val medicines: List<MedicineInfo>
    ) : MessageMetadata()
}

data class MedicineInfo(
    val name: String,
    val isAvailable: Boolean,
    val dosage: String? = null,
    val quantity: String? = null
)

data class QuickReplyOption(
    val id: String,
    val label: String,
    val value: String,
    val icon: String? = null
)

data class DocumentItem(
    val name: String,
    val description: String?,
    val isRequired: Boolean = true,
    val isProvided: Boolean = false
)

/**
 * Chat conversation state
 */
data class ChatConversation(
    val id: String = UUID.randomUUID().toString(),
    val messages: List<ChatMessage> = emptyList(),
    val startedAt: LocalDateTime = LocalDateTime.now(),
    val context: ChatContext = ChatContext()
)

/**
 * Context collected during conversation for eligibility assessment
 */
data class ChatContext(
    val cpf: String? = null,
    val nis: String? = null,
    val birthDate: String? = null,
    val income: Double? = null,
    val familySize: Int? = null,
    val hasDisability: Boolean? = null,
    val isElderly: Boolean? = null,
    val municipality: String? = null,
    val programsOfInterest: List<String> = emptyList(),
    val collectedData: Map<String, Any> = emptyMap()
)

/**
 * Predefined conversation flows
 */
enum class ChatFlow {
    WELCOME,
    ELIGIBILITY_CHECK,
    DOCUMENT_GUIDANCE,
    LOCATION_FINDER,
    FAQ,
    GENERAL_QUESTION
}

/**
 * AI Assistant configuration
 */
data class AssistantConfig(
    val systemPrompt: String,
    val maxTokens: Int = 1000,
    val temperature: Float = 0.7f,
    val model: String = "gpt-4"
)

/**
 * Welcome messages for the assistant
 */
object ChatDefaults {
    val welcomeMessage = ChatMessage(
        content = "Oi! Eu sou o assistente do Tá na Mão. Posso te ajudar a:\n\n📷 **Pegar remédios de graça** - manda foto da receita\n\n• Saber se você tem direito a alguma ajuda\n• Ver que papéis você precisa levar\n• Encontrar onde se cadastrar\n\nComo posso ajudar?",
        sender = MessageSender.ASSISTANT,
        type = MessageType.TEXT
    )

    val welcomeQuickReplies = ChatMessage(
        content = "",
        sender = MessageSender.ASSISTANT,
        type = MessageType.QUICK_REPLIES,
        metadata = MessageMetadata.QuickReplies(
            options = listOf(
                QuickReplyOption("money", "💰 Dinheiro esquecido", "verificar_dinheiro_esquecido", "money"),
                QuickReplyOption("prescription", "📷 Enviar receita", "upload_prescription", "camera"),
                QuickReplyOption("eligibility", "Tenho direito?", "check_eligibility", "search"),
                QuickReplyOption("documents", "Que papéis preciso?", "documents", "description"),
                QuickReplyOption("locations", "Onde me cadastrar?", "locations", "location")
            )
        )
    )
}
