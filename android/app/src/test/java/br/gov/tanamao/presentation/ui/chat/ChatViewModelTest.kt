package br.gov.tanamao.presentation.ui.chat

import br.gov.tanamao.MainCoroutineRule
import kotlinx.coroutines.ExperimentalCoroutinesApi
import org.junit.Rule

import app.cash.turbine.test
import br.gov.tanamao.domain.model.*
import br.gov.tanamao.domain.repository.AgentRepository
import br.gov.tanamao.domain.repository.AgentResponse
import br.gov.tanamao.domain.repository.AgentSession
import io.mockk.coEvery
import io.mockk.coVerify
import io.mockk.mockk
import kotlinx.coroutines.test.runTest
import org.junit.Assert.*
import org.junit.Before
import org.junit.Test

@OptIn(ExperimentalCoroutinesApi::class)
class ChatViewModelTest {

    @get:Rule
    val mainCoroutineRule = MainCoroutineRule()

    private lateinit var repository: AgentRepository
    private lateinit var viewModel: ChatViewModel

    @Before
    fun setup() {
        repository = mockk()

        // Mock startSession chamado no init{}
        coEvery { repository.startSession() } returns Result.Success(
            AgentSession(
                sessionId = "test-session-123",
                welcomeMessage = "Olá! Como posso ajudar?"
            )
        )

        // Mock sendMessage genérico
        coEvery { repository.sendMessage(any(), any(), any()) } returns Result.Success(
            AgentResponse(
                message = "Resposta teste",
                sessionId = "test-session-123",
                toolsUsed = emptyList()
            )
        )

        viewModel = ChatViewModel(repository)
    }

    @Test
    fun `initial state should have welcome message`() = runTest {
        viewModel.uiState.test {
            val state = awaitItem()
            assertTrue(state.messages.isNotEmpty())
            val firstMessage = state.messages.first()
            assertEquals(MessageSender.ASSISTANT, firstMessage.sender)
        }
    }

    @Test
    fun `sendMessage should add user message`() = runTest {
        // Given
        val userMessage = "Olá"

        // When
        viewModel.sendMessage(userMessage)

        // Then - wait for state to update
        kotlinx.coroutines.delay(100)

        viewModel.uiState.test {
            val state = awaitItem()
            val messages = state.messages
            assertTrue(messages.any { it.content == userMessage && it.sender == MessageSender.USER })
        }
    }

    @Test
    fun `sendMessage should not send empty message`() = runTest {
        // Given - count initial sendMessage calls from init
        val initialState = viewModel.uiState.value

        // When
        viewModel.sendMessage("   ")

        // Then - state should not change (no new message added)
        viewModel.uiState.test {
            val state = awaitItem()
            // Messages should not include a blank message
            assertFalse(state.messages.any { it.content.isBlank() && it.sender == MessageSender.USER })
        }
    }

    @Test
    fun `handleQuickReply should add quick reply as message`() = runTest {
        // Given
        val quickReply = QuickReplyOption(
            id = "check_eligibility",
            label = "Verificar elegibilidade",
            value = "check_eligibility"
        )

        // When
        viewModel.handleQuickReply(quickReply)

        // Then - wait for state to update
        kotlinx.coroutines.delay(100)

        viewModel.uiState.test {
            val state = awaitItem()
            assertTrue(state.messages.any { it.content == quickReply.label })
        }
    }
}
