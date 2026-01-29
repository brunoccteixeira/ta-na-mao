package br.gov.tanamao.data.repository

import br.gov.tanamao.data.api.TaNaMaoApi
import br.gov.tanamao.data.api.dto.ChatRequestDto
import br.gov.tanamao.di.IoDispatcher
import br.gov.tanamao.domain.model.AppError
import br.gov.tanamao.domain.model.Result
import br.gov.tanamao.domain.repository.AgentRepository
import br.gov.tanamao.domain.repository.AgentResponse
import br.gov.tanamao.domain.repository.AgentSession
import br.gov.tanamao.domain.repository.AgentStatus
import kotlinx.coroutines.CoroutineDispatcher
import kotlinx.coroutines.withContext
import retrofit2.HttpException
import java.io.IOException
import java.net.SocketTimeoutException
import java.net.UnknownHostException
import javax.inject.Inject
import javax.inject.Singleton

@Singleton
class AgentRepositoryImpl @Inject constructor(
    private val api: TaNaMaoApi,
    @IoDispatcher private val dispatcher: CoroutineDispatcher
) : AgentRepository {

    override suspend fun getStatus(): Result<AgentStatus> = withContext(dispatcher) {
        try {
            val response = api.getAgentStatus()
            Result.Success(
                AgentStatus(
                    available = response.available,
                    model = response.model,
                    tools = response.tools
                )
            )
        } catch (e: Exception) {
            Result.Error(e.toAppError())
        }
    }

    override suspend fun startSession(): Result<AgentSession> = withContext(dispatcher) {
        try {
            val response = api.startAgentConversation()
            Result.Success(
                AgentSession(
                    sessionId = response.sessionId,
                    welcomeMessage = response.message
                )
            )
        } catch (e: Exception) {
            Result.Error(e.toAppError())
        }
    }

    override suspend fun sendMessage(
        message: String,
        sessionId: String,
        imageBase64: String?
    ): Result<AgentResponse> =
        withContext(dispatcher) {
            try {
                val request = ChatRequestDto(
                    message = message,
                    sessionId = sessionId,
                    imageBase64 = imageBase64
                )
                val response = api.sendAgentMessage(request)
                Result.Success(
                    AgentResponse(
                        message = response.response,
                        sessionId = response.sessionId,
                        toolsUsed = response.toolsUsed
                    )
                )
            } catch (e: Exception) {
                Result.Error(e.toAppError())
            }
        }

    override suspend fun resetSession(sessionId: String): Result<Unit> = withContext(dispatcher) {
        try {
            api.resetAgentConversation(sessionId)
            Result.Success(Unit)
        } catch (e: Exception) {
            Result.Error(e.toAppError())
        }
    }

    override suspend fun endSession(sessionId: String): Result<Unit> = withContext(dispatcher) {
        try {
            api.endAgentSession(sessionId)
            Result.Success(Unit)
        } catch (e: Exception) {
            Result.Error(e.toAppError())
        }
    }

    private fun Throwable.toAppError(): AppError = when (this) {
        is SocketTimeoutException -> AppError.Timeout()
        is UnknownHostException -> AppError.Network()
        is IOException -> AppError.Network()
        is HttpException -> when (code()) {
            404 -> AppError.NotFound()
            503 -> AppError.Server(code(), "Agente não disponível")
            in 500..599 -> AppError.Server(code(), message())
            else -> AppError.Unknown(this)
        }
        else -> AppError.Unknown(this)
    }
}
