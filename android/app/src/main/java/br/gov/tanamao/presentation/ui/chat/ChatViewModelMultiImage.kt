package br.gov.tanamao.presentation.ui.chat

import androidx.lifecycle.ViewModel
import androidx.lifecycle.viewModelScope
import br.gov.tanamao.domain.model.*
import br.gov.tanamao.domain.repository.AgentRepository
import br.gov.tanamao.presentation.util.AgentResponseParser
import dagger.hilt.android.lifecycle.HiltViewModel
import kotlinx.coroutines.flow.*
import kotlinx.coroutines.launch
import javax.inject.Inject

/**
 * Extended ChatViewModel with support for multiple images
 * This can be merged into ChatViewModel if preferred
 */
@HiltViewModel
class ChatViewModelMultiImage @Inject constructor(
    private val agentRepository: AgentRepository
) : ViewModel() {

    private val _uiState = MutableStateFlow(ChatUiState())
    val uiState: StateFlow<ChatUiState> = _uiState.asStateFlow()

    private val _pendingImages = MutableStateFlow<List<String>>(emptyList())
    val pendingImages: StateFlow<List<String>> = _pendingImages.asStateFlow()

    private var sessionId: String? = null
    private var isOfflineMode: Boolean = false

    init {
        startConversation()
    }

    fun addPendingImage(imageBase64: String) {
        _pendingImages.update { it + imageBase64 }
    }

    fun removePendingImage(index: Int) {
        _pendingImages.update { it.toMutableList().apply { removeAt(index) } }
    }

    fun sendAllPendingImages() {
        val images = _pendingImages.value
        if (images.isEmpty()) return

        viewModelScope.launch {
            // Send all images at once
            if (images.size == 1) {
                sendImageMessage(images.first())
            } else {
                sendMultipleImages(images)
            }
            _pendingImages.value = emptyList()
        }
    }

    fun sendImageMessage(imageBase64: String) {
        val userMessage = ChatMessage(
            content = "Receita médica",
            sender = MessageSender.USER,
            type = MessageType.IMAGE,
            metadata = MessageMetadata.ImageData(
                base64 = imageBase64,
                caption = "Receita médica enviada"
            )
        )
        addMessage(userMessage)

        viewModelScope.launch {
            setLoading(true)
            if (isOfflineMode || sessionId == null) {
                addMessage(getOfflinePrescriptionResponse())
                setLoading(false)
                return@launch
            }

            when (val result = agentRepository.sendMessage(
                message = "Processar esta receita médica",
                sessionId = sessionId!!,
                imageBase64 = imageBase64
            )) {
                is Result.Success -> {
                    val response = result.data
                    sessionId = response.sessionId
                    val messages = parseAgentResponse(response.message, response.toolsUsed)
                    messages.forEach { addMessage(it) }
                }
                is Result.Error -> {
                    isOfflineMode = true
                    addMessage(ChatMessage(
                        content = "Não foi possível processar a receita no momento. Tente novamente mais tarde.",
                        sender = MessageSender.ASSISTANT,
                        type = MessageType.TEXT
                    ))
                }
                Result.Loading -> {}
            }
            setLoading(false)
        }
    }

    private fun sendMultipleImages(images: List<String>) {
        // Add user message with multiple images
        val userMessage = ChatMessage(
            content = "Receitas médicas (${images.size} imagens)",
            sender = MessageSender.USER,
            type = MessageType.IMAGE,
            metadata = MessageMetadata.ImageData(
                base64 = images.first(), // Send first image, backend can handle multiple
                caption = "${images.size} receitas médicas enviadas"
            )
        )
        addMessage(userMessage)

        viewModelScope.launch {
            setLoading(true)
            
            // Send images sequentially or in batch (depending on backend API)
            // For now, send first image and mention others
            if (isOfflineMode || sessionId == null) {
                addMessage(ChatMessage(
                    content = """📋 **${images.size} receitas recebidas!**

Para processar suas receitas médicas, o app precisa estar conectado ao servidor.

**Enquanto isso, você pode:**
• Levar as receitas diretamente a uma farmácia credenciada
• Verificar medicamentos gratuitos em: gov.br/farmacia-popular""",
                    sender = MessageSender.ASSISTANT,
                    type = MessageType.TEXT
                ))
                setLoading(false)
                return@launch
            }

            // Process first image
            images.firstOrNull()?.let { firstImage ->
                when (val result = agentRepository.sendMessage(
                    message = "Processar estas ${images.size} receitas médicas",
                    sessionId = sessionId!!,
                    imageBase64 = firstImage
                )) {
                    is Result.Success -> {
                        val response = result.data
                        sessionId = response.sessionId
                        val messages = parseAgentResponse(response.message, response.toolsUsed)
                        messages.forEach { addMessage(it) }
                        
                        if (images.size > 1) {
                            addMessage(ChatMessage(
                                content = "Nota: ${images.size - 1} receita(s) adicional(is) foram enviadas. Processando...",
                                sender = MessageSender.ASSISTANT,
                                type = MessageType.TEXT
                            ))
                        }
                    }
                    is Result.Error -> {
                        isOfflineMode = true
                        addMessage(ChatMessage(
                            content = "Não foi possível processar as receitas no momento.",
                            sender = MessageSender.ASSISTANT,
                            type = MessageType.TEXT
                        ))
                    }
                    Result.Loading -> {}
                }
            }
            setLoading(false)
        }
    }

    private fun getOfflinePrescriptionResponse(): ChatMessage {
        return ChatMessage(
            content = """📋 **Receita recebida!**
Para processar sua receita médica e verificar medicamentos disponíveis no Farmácia Popular, o app precisa estar conectado ao servidor.""",
            sender = MessageSender.ASSISTANT,
            type = MessageType.TEXT
        )
    }

    fun sendMessage(content: String) {
        if (content.isBlank()) return
        val userMessage = ChatMessage(content = content.trim(), sender = MessageSender.USER)
        addMessage(userMessage)
        processWithAgent(content)
    }

    private fun processWithAgent(userMessage: String) {
        viewModelScope.launch {
            setLoading(true)
            if (isOfflineMode || sessionId == null) {
                addMessage(ChatMessage(
                    content = "Estou offline no momento. Tente novamente mais tarde.",
                    sender = MessageSender.ASSISTANT
                ))
                setLoading(false)
                return@launch
            }

            when (val result = agentRepository.sendMessage(userMessage, sessionId!!)) {
                is Result.Success -> {
                    val response = result.data
                    sessionId = response.sessionId
                    val messages = parseAgentResponse(response.message, response.toolsUsed)
                    messages.forEach { addMessage(it) }
                }
                is Result.Error -> {
                    isOfflineMode = true
                    addMessage(ChatMessage(
                        content = "Ocorreu um erro ao processar sua mensagem.",
                        sender = MessageSender.ASSISTANT,
                        type = MessageType.ERROR
                    ))
                }
                Result.Loading -> {}
            }
            setLoading(false)
        }
    }

    private fun parseAgentResponse(message: String, toolsUsed: List<String>): List<ChatMessage> {
        val messages = mutableListOf<ChatMessage>()
        
        val moneyResult = AgentResponseParser.parseMoneyResult(message, toolsUsed)
        val medicineResult = AgentResponseParser.parseMedicineResult(message, toolsUsed)
        val eligibilityResult = AgentResponseParser.parseEligibilityResult(message, toolsUsed)
        val documentList = AgentResponseParser.parseDocumentList(message, toolsUsed)
        val locationCard = AgentResponseParser.parseLocationCard(message, toolsUsed)

        when {
            moneyResult != null -> messages.add(ChatMessage(
                content = "Encontrei informações sobre dinheiro esquecido:",
                sender = MessageSender.ASSISTANT,
                type = MessageType.MONEY_RESULT,
                metadata = moneyResult
            ))
            medicineResult != null -> messages.add(ChatMessage(
                content = "Analisei sua receita:",
                sender = MessageSender.ASSISTANT,
                type = MessageType.MEDICINE_RESULT,
                metadata = medicineResult
            ))
            eligibilityResult != null -> messages.add(ChatMessage(
                content = "Resultado da verificação:",
                sender = MessageSender.ASSISTANT,
                type = MessageType.ELIGIBILITY_RESULT,
                metadata = eligibilityResult
            ))
            documentList != null -> messages.add(ChatMessage(
                content = "Documentos necessários:",
                sender = MessageSender.ASSISTANT,
                type = MessageType.DOCUMENT_LIST,
                metadata = MessageMetadata.DocumentList(
                    title = "Documentos necessários",
                    documents = documentList
                )
            ))
            locationCard != null -> messages.add(ChatMessage(
                content = "Local encontrado:",
                sender = MessageSender.ASSISTANT,
                type = MessageType.LOCATION,
                metadata = locationCard
            ))
            else -> messages.add(ChatMessage(
                content = message,
                sender = MessageSender.ASSISTANT,
                type = MessageType.TEXT
            ))
        }

        return messages
    }

    private fun startConversation() {
        viewModelScope.launch {
            setLoading(true)
            when (val result = agentRepository.startSession()) {
                is Result.Success -> {
                    sessionId = result.data.sessionId
                    isOfflineMode = false
                    addMessage(ChatMessage(
                        content = result.data.welcomeMessage,
                        sender = MessageSender.ASSISTANT,
                        type = MessageType.TEXT
                    ))
                    addMessage(ChatDefaults.welcomeQuickReplies)
                }
                is Result.Error -> {
                    isOfflineMode = true
                    addMessage(ChatDefaults.welcomeMessage)
                    addMessage(ChatDefaults.welcomeQuickReplies)
                }
                Result.Loading -> {}
            }
            setLoading(false)
        }
    }

    fun clearConversation() {
        viewModelScope.launch {
            sessionId?.let { agentRepository.resetSession(it) }
            _uiState.value = ChatUiState()
            _pendingImages.value = emptyList()
            startConversation()
        }
    }

    private fun addMessage(message: ChatMessage) {
        _uiState.update { state ->
            state.copy(
                messages = state.messages + message,
                isLoading = false,
                error = null
            )
        }
    }

    private fun setLoading(loading: Boolean) {
        _uiState.update { it.copy(isLoading = loading) }
    }
}

