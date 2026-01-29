package br.gov.tanamao.data.api.dto

import com.google.gson.annotations.SerializedName

/**
 * DTO for chat request to agent.
 */
data class ChatRequestDto(
    val message: String,
    @SerializedName("session_id") val sessionId: String? = null,
    @SerializedName("image_base64") val imageBase64: String? = null
)

/**
 * DTO for chat response from agent.
 */
data class ChatResponseDto(
    val response: String,
    @SerializedName("session_id") val sessionId: String,
    @SerializedName("tools_used") val toolsUsed: List<String> = emptyList()
)

/**
 * DTO for welcome response when starting conversation.
 */
data class WelcomeResponseDto(
    val message: String,
    @SerializedName("session_id") val sessionId: String
)

/**
 * DTO for agent status check.
 */
data class AgentStatusDto(
    val available: Boolean,
    val model: String,
    val tools: List<String>
)

/**
 * DTO for error response from agent.
 */
data class AgentErrorDto(
    val error: String,
    val detail: String? = null
)
