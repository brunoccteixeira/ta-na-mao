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

@HiltViewModel
class ChatViewModel @Inject constructor(
    private val agentRepository: AgentRepository
) : ViewModel() {

    private val _uiState = MutableStateFlow(ChatUiState())
    val uiState: StateFlow<ChatUiState> = _uiState.asStateFlow()

    private var sessionId: String? = null
    private var isOfflineMode: Boolean = false

    init {
        startConversation()
    }

    fun sendMessage(content: String) {
        if (content.isBlank()) return

        val userMessage = ChatMessage(
            content = content.trim(),
            sender = MessageSender.USER
        )

        addMessage(userMessage)
        processWithAgent(content)
    }

    fun handleQuickReply(option: QuickReplyOption) {
        val userMessage = ChatMessage(
            content = option.label,
            sender = MessageSender.USER
        )
        addMessage(userMessage)
        processWithAgent(option.label)
    }

    fun handleEligibilityAction(action: String) {
        val message = when {
            action.startsWith("documents_") -> "Quais documentos preciso para ${action.removePrefix("documents_")}?"
            action.startsWith("apply_") -> "Como solicitar ${action.removePrefix("apply_")}?"
            action.startsWith("criteria_") -> "Explique os critérios de ${action.removePrefix("criteria_")}"
            else -> action
        }
        sendMessage(message)
    }

    fun sendImageMessage(imageBase64: String) {
        // Add user message with image preview
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

        // Send to backend
        viewModelScope.launch {
            setLoading(true)

            // If offline mode, show mock response
            if (isOfflineMode || sessionId == null) {
                addMessage(ChatMessage(
                    content = """📋 **Receita recebida!**

Para processar sua receita médica e verificar medicamentos disponíveis no Farmácia Popular, o app precisa estar conectado ao servidor.

**Enquanto isso, você pode:**
1. Levar a receita diretamente a uma farmácia credenciada
2. Verificar medicamentos gratuitos em: gov.br/farmacia-popular

**Medicamentos gratuitos mais comuns:**
• Captopril, Losartana (hipertensão)
• Metformina, Glibenclamida (diabetes)
• Salbutamol, Beclometasona (asma)""",
                    sender = MessageSender.ASSISTANT,
                    type = MessageType.TEXT
                ))
                addMessage(ChatMessage(
                    content = "",
                    sender = MessageSender.ASSISTANT,
                    type = MessageType.QUICK_REPLIES,
                    metadata = MessageMetadata.QuickReplies(listOf(
                        QuickReplyOption("farm", "Buscar farmácia", "farmacia", "location"),
                        QuickReplyOption("back", "Voltar ao início", "restart", "help")
                    ))
                ))
                setLoading(false)
                return@launch
            }

            // Send message with image as dedicated parameter
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
                        content = "Não foi possível processar a receita no momento. Tente novamente mais tarde ou leve a receita diretamente a uma farmácia credenciada.",
                        sender = MessageSender.ASSISTANT,
                        type = MessageType.TEXT
                    ))
                }
                Result.Loading -> {}
            }
            setLoading(false)
        }
    }

    fun clearConversation() {
        viewModelScope.launch {
            sessionId?.let { id ->
                agentRepository.resetSession(id)
            }
            _uiState.update { ChatUiState() }
            startConversation()
        }
    }

    private fun startConversation() {
        viewModelScope.launch {
            setLoading(true)

            when (val result = agentRepository.startSession()) {
                is Result.Success -> {
                    sessionId = result.data.sessionId
                    isOfflineMode = false

                    val welcomeMessage = ChatMessage(
                        content = result.data.welcomeMessage,
                        sender = MessageSender.ASSISTANT,
                        type = MessageType.TEXT
                    )
                    addMessage(welcomeMessage)

                    // Add default quick replies
                    addMessage(ChatDefaults.welcomeQuickReplies)
                }
                is Result.Error -> {
                    // Fallback to offline mode if backend unavailable
                    isOfflineMode = true
                    addMessage(ChatDefaults.welcomeMessage)
                    addMessage(ChatDefaults.welcomeQuickReplies)
                }
                Result.Loading -> {}
            }
            setLoading(false)
        }
    }

    private fun processWithAgent(input: String) {
        viewModelScope.launch {
            setLoading(true)

            // If in offline mode, use mock responses
            if (isOfflineMode || sessionId == null) {
                val mockResponse = generateMockResponse(input)
                addMessage(ChatMessage(
                    content = mockResponse,
                    sender = MessageSender.ASSISTANT,
                    type = MessageType.TEXT
                ))
                // Add relevant quick replies
                val quickReplies = generateMockQuickReplies(input)
                if (quickReplies.isNotEmpty()) {
                    addMessage(ChatMessage(
                        content = "",
                        sender = MessageSender.ASSISTANT,
                        type = MessageType.QUICK_REPLIES,
                        metadata = MessageMetadata.QuickReplies(quickReplies)
                    ))
                }
                setLoading(false)
                return@launch
            }

            when (val result = agentRepository.sendMessage(input, sessionId!!)) {
                is Result.Success -> {
                    val response = result.data
                    sessionId = response.sessionId

                    // Parse the response and create appropriate message types
                    val messages = parseAgentResponse(response.message, response.toolsUsed)
                    messages.forEach { addMessage(it) }
                }
                is Result.Error -> {
                    // Switch to offline mode on error
                    isOfflineMode = true
                    val mockResponse = generateMockResponse(input)
                    addMessage(ChatMessage(
                        content = mockResponse,
                        sender = MessageSender.ASSISTANT,
                        type = MessageType.TEXT
                    ))
                }
                Result.Loading -> {}
            }
            setLoading(false)
        }
    }

    private fun generateMockResponse(input: String): String {
        val inputLower = input.lowercase()
        return when {
            inputLower.contains("elegib") || inputLower.contains("verificar") || inputLower.contains("direito") ->
                """Para saber se você tem direito a alguma ajuda, me conta:

• Quanto de dinheiro entra na sua casa todo mês?
• Quantas pessoas moram com você?
• Você tem cadastro no governo (CadÚnico)?

Com isso, vou te mostrar as ajudas que você pode receber.

**Principais ajudas:**
- Bolsa Família: para famílias com pouca renda
- Ajuda para idosos e pessoas com deficiência (BPC)
- Desconto na conta de luz"""

            inputLower.contains("documento") ->
                """📋 **Papéis que você vai precisar:**

**Para se cadastrar no governo (CadÚnico):**
• RG e CPF de todos da família
• Conta de luz ou água (comprova onde mora)
• Papel que mostra quanto ganha (se trabalha)
• Certidão de nascimento ou casamento

**Para Bolsa Família:**
• Ter cadastro no governo atualizado

**Para ajuda a idosos e deficientes (BPC):**
• CPF de quem vai receber
• Papel do médico (se for pessoa com deficiência)
• Comprovante de quanto a família ganha"""

            inputLower.contains("cras") || inputLower.contains("cadastr") || inputLower.contains("onde") || inputLower.contains("posto") ->
                """🏢 **Como encontrar o posto de assistência social (CRAS):**

Me fala seu CEP que eu acho o mais perto de você!

**O que é o CRAS?**
É o lugar onde você vai para:
• Fazer o cadastro no governo (CadÚnico)
• Pedir ajudas do governo
• Tirar dúvidas sobre benefícios

**Horário:** Geralmente das 8h às 17h, de segunda a sexta."""

            inputLower.contains("farmácia") || inputLower.contains("medicamento") || inputLower.contains("receita") || inputLower.contains("remédio") ->
                """💊 **Remédios de graça:**

Você pode pegar remédios de graça na farmácia!

**Remédios gratuitos:**
• Para pressão alta
• Para diabetes
• Para asma

**O que levar:**
1. Receita do médico
2. Documento com CPF
3. Ir na farmácia que tem o programa

Me manda uma foto da receita que eu te ajudo!"""

            else ->
                """Entendi! Posso ajudar você com:

• **Saber se você tem direito** a ajudas do governo
• **Ver os papéis** que você precisa levar
• **Encontrar o posto** de assistência social perto de você
• **Pegar remédios de graça** na farmácia

O que você gostaria de saber?"""
        }
    }

    private fun generateMockQuickReplies(input: String): List<QuickReplyOption> {
        val inputLower = input.lowercase()
        return when {
            inputLower.contains("elegib") || inputLower.contains("verificar") -> listOf(
                QuickReplyOption("docs", "Ver documentos", "documents", "description"),
                QuickReplyOption("cras", "Encontrar CRAS", "locations", "location")
            )
            inputLower.contains("documento") -> listOf(
                QuickReplyOption("cras", "Encontrar CRAS", "locations", "location"),
                QuickReplyOption("back", "Voltar ao início", "restart", "help")
            )
            inputLower.contains("cras") || inputLower.contains("onde") -> listOf(
                QuickReplyOption("docs", "Ver documentos", "documents", "description"),
                QuickReplyOption("back", "Voltar ao início", "restart", "help")
            )
            inputLower.contains("farmácia") || inputLower.contains("receita") -> listOf(
                QuickReplyOption("docs", "Ver documentos", "documents", "description"),
                QuickReplyOption("back", "Voltar ao início", "restart", "help")
            )
            else -> listOf(
                QuickReplyOption("eligibility", "Tenho direito?", "check_eligibility", "search"),
                QuickReplyOption("documents", "Que papéis preciso?", "documents", "description"),
                QuickReplyOption("locations", "Onde me cadastrar?", "locations", "location")
            )
        }
    }

    private fun parseAgentResponse(message: String, toolsUsed: List<String>): List<ChatMessage> {
        val messages = mutableListOf<ChatMessage>()

        // Check if response is about money found
        val moneyResult = AgentResponseParser.parseMoneyCheckResult(message, toolsUsed)
        if (moneyResult != null && moneyResult.hasMoney) {
            // Add text message first
            val textPart = message.substringBefore("R$").trim()
            if (textPart.isNotBlank()) {
                messages.add(ChatMessage(
                    content = textPart,
                    sender = MessageSender.ASSISTANT,
                    type = MessageType.TEXT
                ))
            }
            
            // Add money result card
            messages.add(ChatMessage(
                content = "Dinheiro encontrado",
                sender = MessageSender.ASSISTANT,
                type = MessageType.TEXT, // Will be handled specially in UI
                metadata = MessageMetadata.MoneyResult(
                    totalAmount = moneyResult.totalAmount,
                    types = moneyResult.types
                )
            ))
            
            // Add quick replies for money guides
            val moneyReplies = listOf(
                QuickReplyOption("pis", "Guia PIS/PASEP", "guia PIS PASEP", "money"),
                QuickReplyOption("svr", "Guia SVR", "guia SVR", "money"),
                QuickReplyOption("fgts", "Guia FGTS", "guia FGTS", "money")
            )
            messages.add(ChatMessage(
                content = "",
                sender = MessageSender.ASSISTANT,
                type = MessageType.QUICK_REPLIES,
                metadata = MessageMetadata.QuickReplies(moneyReplies)
            ))
            
            return messages
        }

        // Check if response contains location data (CRAS or pharmacy)
        val locationData = extractLocationData(message, toolsUsed)
        if (locationData != null) {
            // Add text message first
            val textPart = message.substringBefore("Coordenadas:").trim()
                .ifEmpty { message.substringBefore("Endereço:").trim() }
                .ifEmpty { message }

            if (textPart.isNotBlank() && textPart != message) {
                messages.add(ChatMessage(
                    content = textPart,
                    sender = MessageSender.ASSISTANT,
                    type = MessageType.TEXT
                ))
            }

            // Add location card
            messages.add(ChatMessage(
                content = locationData.name,
                sender = MessageSender.ASSISTANT,
                type = MessageType.LOCATION,
                metadata = locationData
            ))
        } else {
            // Regular text message
            messages.add(ChatMessage(
                content = message,
                sender = MessageSender.ASSISTANT,
                type = MessageType.TEXT
            ))
        }

        // Add follow-up quick replies based on tools used
        val quickReplies = generateQuickReplies(toolsUsed)
        if (quickReplies.isNotEmpty()) {
            messages.add(ChatMessage(
                content = "",
                sender = MessageSender.ASSISTANT,
                type = MessageType.QUICK_REPLIES,
                metadata = MessageMetadata.QuickReplies(quickReplies)
            ))
        }

        return messages
    }

    private fun extractLocationData(message: String, toolsUsed: List<String>): MessageMetadata.LocationCard? {
        // Check if location tools were used
        val hasLocationTool = toolsUsed.any { it in listOf("buscar_cras", "buscar_farmacia") }
        if (!hasLocationTool) return null

        // Try to extract coordinates and location info from the message
        // Pattern: Look for latitude/longitude in the response
        val latPattern = Regex("""lat[itude]*["\s:]+(-?\d+\.?\d*)""", RegexOption.IGNORE_CASE)
        val lngPattern = Regex("""l[o]?ng[itude]*["\s:]+(-?\d+\.?\d*)""", RegexOption.IGNORE_CASE)

        val latMatch = latPattern.find(message)
        val lngMatch = lngPattern.find(message)

        if (latMatch != null && lngMatch != null) {
            val lat = latMatch.groupValues[1].toDoubleOrNull()
            val lng = lngMatch.groupValues[1].toDoubleOrNull()

            if (lat != null && lng != null) {
                // Extract name and address
                val namePattern = Regex("""nome["\s:]+["']?([^"'\n,]+)["']?""", RegexOption.IGNORE_CASE)
                val addressPattern = Regex("""endere[cç]o["\s:]+["']?([^"'\n]+)["']?""", RegexOption.IGNORE_CASE)
                val phonePattern = Regex("""telefone["\s:]+["']?([^"'\n,]+)["']?""", RegexOption.IGNORE_CASE)
                val hoursPattern = Regex("""hor[aá]rio["\s:]+["']?([^"'\n]+)["']?""", RegexOption.IGNORE_CASE)

                val name = namePattern.find(message)?.groupValues?.get(1)?.trim()
                    ?: if ("buscar_cras" in toolsUsed) "CRAS" else "Farmácia"
                val address = addressPattern.find(message)?.groupValues?.get(1)?.trim() ?: ""
                val phone = phonePattern.find(message)?.groupValues?.get(1)?.trim()
                val hours = hoursPattern.find(message)?.groupValues?.get(1)?.trim()

                // Generate action URLs
                val mapsUrl = "https://www.google.com/maps/dir/?api=1&destination=$lat,$lng"
                val wazeUrl = "https://waze.com/ul?ll=$lat,$lng&navigate=yes"

                return MessageMetadata.LocationCard(
                    name = name,
                    address = address,
                    distance = null,
                    latitude = lat,
                    longitude = lng,
                    phone = phone,
                    hours = hours,
                    mapsUrl = mapsUrl,
                    wazeUrl = wazeUrl
                )
            }
        }

        return null
    }

    private fun generateQuickReplies(toolsUsed: List<String>): List<QuickReplyOption> {
        return when {
            "consultar_dinheiro_esquecido" in toolsUsed || "verificar_dinheiro_por_perfil" in toolsUsed -> listOf(
                QuickReplyOption("pis", "Guia PIS/PASEP", "guia PIS PASEP", "money"),
                QuickReplyOption("svr", "Guia SVR", "guia SVR", "money"),
                QuickReplyOption("fgts", "Guia FGTS", "guia FGTS", "money"),
                QuickReplyOption("back", "Voltar ao início", "restart", "help")
            )
            "guia_pis_pasep" in toolsUsed -> listOf(
                QuickReplyOption("check", "Verificar meu PIS/PASEP", "verificar meu dinheiro esquecido", "money"),
                QuickReplyOption("back", "Voltar ao início", "restart", "help")
            )
            "guia_svr" in toolsUsed -> listOf(
                QuickReplyOption("check", "Verificar meu SVR", "verificar meu dinheiro esquecido", "money"),
                QuickReplyOption("back", "Voltar ao início", "restart", "help")
            )
            "guia_fgts" in toolsUsed -> listOf(
                QuickReplyOption("check", "Verificar meu FGTS", "verificar meu dinheiro esquecido", "money"),
                QuickReplyOption("back", "Voltar ao início", "restart", "help")
            )
            "buscar_cras" in toolsUsed || "buscar_farmacia" in toolsUsed -> listOf(
                QuickReplyOption("docs", "Ver documentos", "documents", "description"),
                QuickReplyOption("other", "Buscar outro local", "locations", "location")
            )
            "gerar_checklist" in toolsUsed -> listOf(
                QuickReplyOption("find", "Encontrar CRAS", "locations", "location"),
                QuickReplyOption("back", "Voltar ao início", "restart", "help")
            )
            "verificar_elegibilidade" in toolsUsed || "consultar_beneficios" in toolsUsed -> listOf(
                QuickReplyOption("docs", "Ver documentos", "documents", "description"),
                QuickReplyOption("cras", "Encontrar CRAS", "locations", "location")
            )
            "processar_receita" in toolsUsed -> listOf(
                QuickReplyOption("farm", "Buscar farmácia", "farmacia", "location"),
                QuickReplyOption("back", "Voltar ao início", "restart", "help")
            )
            else -> emptyList()
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

data class ChatUiState(
    val messages: List<ChatMessage> = emptyList(),
    val isLoading: Boolean = false,
    val error: String? = null,
    val context: ChatContext = ChatContext(),
    val currentFlow: ChatFlow = ChatFlow.WELCOME
)
