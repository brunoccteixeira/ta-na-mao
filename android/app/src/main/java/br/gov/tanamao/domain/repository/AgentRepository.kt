package br.gov.tanamao.domain.repository

import br.gov.tanamao.domain.model.Result

/**
 * Repository interface for conversational agent operations.
 */
interface AgentRepository {

    /**
     * Check if the agent is available and configured.
     */
    suspend fun getStatus(): Result<AgentStatus>

    /**
     * Start a new conversation session with the agent.
     */
    suspend fun startSession(): Result<AgentSession>

    /**
     * Send a message to the agent and receive a response.
     * @param imageBase64 Optional image in base64 format (e.g., prescription photo)
     */
    suspend fun sendMessage(
        message: String,
        sessionId: String,
        imageBase64: String? = null
    ): Result<AgentResponse>

    /**
     * Reset an existing conversation session.
     */
    suspend fun resetSession(sessionId: String): Result<Unit>

    /**
     * End and cleanup a conversation session.
     */
    suspend fun endSession(sessionId: String): Result<Unit>
}

/**
 * Agent availability status.
 */
data class AgentStatus(
    val available: Boolean,
    val model: String,
    val tools: List<String>
)

/**
 * Agent session information.
 */
data class AgentSession(
    val sessionId: String,
    val welcomeMessage: String
)

/**
 * Response from the agent.
 */
data class AgentResponse(
    val message: String,
    val sessionId: String,
    val toolsUsed: List<String>
)
