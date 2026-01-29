# Agentes de IA - App Android Tá na Mão

> ⚠️ **ESPECIFICAÇÃO TÉCNICA** - Este documento descreve a arquitetura planejada do assistente de IA. A implementação atual é um **placeholder**. O código descrito aqui ainda **NÃO está implementado** no app.

Este documento descreve o assistente virtual de IA integrado ao app Tá na Mão, que ajuda cidadãos a descobrir e acessar benefícios sociais.

## Status de Implementação

| Componente | Status | Notas |
|------------|--------|-------|
| ChatScreen UI | 🚧 Placeholder | Tela básica criada |
| ChatViewModel | ❌ Não existe | Especificado, não implementado |
| AgentService | ❌ Não existe | Especificado, não implementado |
| EligibilityEngine | ❌ Não existe | Especificado, não implementado |
| Integração LLM | ❌ Não existe | Requer API key OpenAI/Anthropic |

**Legenda**: ✅ Implementado | 🚧 Em Desenvolvimento | ❌ Não Implementado

---

## Visão Geral

O assistente "Tá na Mão" é um chatbot conversacional que:
- Identifica o perfil socioeconômico do cidadão
- Verifica elegibilidade para programas sociais
- Orienta sobre documentação necessária
- Indica pontos de atendimento mais próximos
- Responde dúvidas sobre benefícios

---

## Arquitetura do Assistente

```
┌─────────────────────────────────────────────────────────────┐
│                         UI Layer                             │
│  ┌─────────────┐  ┌─────────────┐  ┌─────────────────────┐  │
│  │  ChatScreen │  │  Messages   │  │  QuickReplies       │  │
│  └─────────────┘  └─────────────┘  └─────────────────────┘  │
└───────────────────────────┬─────────────────────────────────┘
                            │
┌───────────────────────────▼─────────────────────────────────┐
│                     ViewModel Layer                          │
│  ┌─────────────────────────────────────────────────────────┐│
│  │  ChatViewModel                                          ││
│  │  - Gerencia estado da conversa                          ││
│  │  - Processa mensagens do usuário                        ││
│  │  - Coordena com AgentService                            ││
│  └─────────────────────────────────────────────────────────┘│
└───────────────────────────┬─────────────────────────────────┘
                            │
┌───────────────────────────▼─────────────────────────────────┐
│                     Agent Layer                              │
│  ┌─────────────┐  ┌─────────────┐  ┌─────────────────────┐  │
│  │AgentService │  │PromptEngine │  │  FlowController     │  │
│  │             │──│             │──│                     │  │
│  └─────────────┘  └─────────────┘  └─────────────────────┘  │
└───────────────────────────┬─────────────────────────────────┘
                            │
┌───────────────────────────▼─────────────────────────────────┐
│                      LLM Integration                         │
│  ┌─────────────────────────────────────────────────────────┐│
│  │  OpenAI GPT-4 / Anthropic Claude                        ││
│  │  - Processa linguagem natural                           ││
│  │  - Gera respostas contextuais                           ││
│  │  - Mantém contexto da conversa                          ││
│  └─────────────────────────────────────────────────────────┘│
└─────────────────────────────────────────────────────────────┘
```

---

## Fluxos de Conversa

### 1. Fluxo de Boas-Vindas

```
AGENTE: Olá! Sou o assistente Tá na Mão. Estou aqui para
        ajudar você a descobrir os benefícios sociais
        disponíveis para sua família.

        O que você gostaria de fazer?

        [Verificar Benefícios] [Tirar Dúvidas] [Encontrar Atendimento]
```

### 2. Fluxo de Triagem de Elegibilidade

```
Etapa 1: Localização
─────────────────────
AGENTE: Para começar, preciso saber onde você mora.
        Qual é a sua cidade?

USUÁRIO: Campinas

AGENTE: Encontrei Campinas - SP (IBGE: 3509502).
        É essa cidade mesmo?

        [Sim, é essa] [Não, buscar outra]

Etapa 2: Composição Familiar
─────────────────────────────
AGENTE: Quantas pessoas moram na sua casa, incluindo você?

USUÁRIO: 4 pessoas

AGENTE: E qual é a renda total da família por mês?
        (Some todos os salários e rendimentos)

        [Até R$ 660]
        [R$ 660 a R$ 1.320]
        [R$ 1.320 a R$ 2.640]
        [Acima de R$ 2.640]

Etapa 3: Perfil Especial
─────────────────────────
AGENTE: Há alguma dessas situações na sua família?
        (Pode selecionar mais de uma)

        [Idoso (65+ anos)]
        [Pessoa com deficiência]
        [Gestante]
        [Criança (0-6 anos)]
        [Nenhuma das opções]

Etapa 4: Resultado
──────────────────
AGENTE: Com base nas informações, você pode ter direito a:

        ✅ Bolsa Família
           Valor estimado: R$ 600 + R$ 150/criança

        ✅ Farmácia Popular
           Medicamentos gratuitos para toda família

        ✅ Tarifa Social de Energia (TSEE)
           Desconto de até 65% na conta de luz

        ⚠️ BPC/LOAS
           Requer avaliação médica (para PCD)

        Quer saber como solicitar algum desses benefícios?

        [Bolsa Família] [Farmácia Popular] [TSEE] [BPC]
```

### 3. Fluxo de Documentação

```
AGENTE: Para solicitar o Bolsa Família, você vai precisar:

        📋 Documentos necessários:

        ✓ CPF de todos da família
        ✓ Certidão de nascimento ou casamento
        ✓ Comprovante de residência (luz, água ou contrato)
        ✓ Carteira de trabalho (se tiver)
        ✓ Comprovante de renda (se tiver)

        📍 Onde solicitar:

        O cadastro é feito no CRAS mais próximo da sua casa.
        Em Campinas, o CRAS mais perto de você é:

        CRAS Sul
        Rua Exemplo, 123 - Jardim Sul
        Tel: (19) 3xxx-xxxx
        Horário: Seg-Sex, 8h às 17h

        Posso ajudar com mais alguma coisa?

        [Ver outros benefícios] [Buscar outro CRAS] [Finalizar]
```

### 4. Fluxo de Dúvidas

```
USUÁRIO: O que é o BPC?

AGENTE: O BPC (Benefício de Prestação Continuada) é um
        benefício assistencial no valor de 1 salário mínimo
        (R$ 1.412 em 2024) pago mensalmente.

        👤 Quem tem direito:

        • Idosos com 65 anos ou mais, OU
        • Pessoas com deficiência de qualquer idade

        💰 Requisito de renda:

        • Renda familiar per capita de até 1/4 do salário
          mínimo (R$ 353/pessoa)

        ⚠️ Importante:

        • Não é aposentadoria (não precisa ter contribuído)
        • Não dá direito a 13º salário
        • É intransferível (não passa para herdeiros)

        Quer verificar se você tem direito ao BPC?

        [Verificar elegibilidade] [Outra dúvida] [Voltar]
```

---

## Implementação Técnica

### Model Classes

```kotlin
// agent/model/ChatMessage.kt

data class ChatMessage(
    val id: String = UUID.randomUUID().toString(),
    val role: MessageRole,
    val content: String,
    val timestamp: Long = System.currentTimeMillis(),
    val quickReplies: List<QuickReply>? = null,
    val metadata: Map<String, Any>? = null
)

enum class MessageRole {
    USER,
    ASSISTANT,
    SYSTEM
}

data class QuickReply(
    val id: String,
    val label: String,
    val value: String,
    val icon: String? = null
)

// agent/model/UserProfile.kt

data class UserProfile(
    val municipality: Municipality? = null,
    val familySize: Int? = null,
    val monthlyIncome: IncomeRange? = null,
    val specialConditions: Set<SpecialCondition> = emptySet(),
    val eligiblePrograms: List<EligibleProgram> = emptyList()
)

enum class IncomeRange {
    UP_TO_660,      // Extrema pobreza
    FROM_660_TO_1320,  // Pobreza
    FROM_1320_TO_2640, // Baixa renda
    ABOVE_2640      // Acima da faixa
}

enum class SpecialCondition {
    ELDERLY,        // 65+ anos
    DISABLED,       // Pessoa com deficiência
    PREGNANT,       // Gestante
    CHILD_0_6,      // Criança 0-6 anos
    NONE
}

data class EligibleProgram(
    val code: ProgramCode,
    val name: String,
    val estimatedValue: Double?,
    val confidence: EligibilityConfidence,
    val requirements: List<String>
)

enum class EligibilityConfidence {
    HIGH,      // Muito provável que seja elegível
    MEDIUM,    // Possivelmente elegível
    LOW,       // Precisa de mais informações
    NOT_ELIGIBLE // Não elegível
}
```

### Agent Service

```kotlin
// agent/AgentService.kt

@Singleton
class AgentService @Inject constructor(
    private val openAiClient: OpenAI,
    private val municipalityRepository: MunicipalityRepository,
    @IoDispatcher private val dispatcher: CoroutineDispatcher
) {
    private val conversationHistory = mutableListOf<ChatCompletionMessage>()
    private var userProfile = UserProfile()

    suspend fun processMessage(userMessage: String): ChatMessage = withContext(dispatcher) {
        // Add user message to history
        conversationHistory.add(
            ChatCompletionMessage(
                role = ChatRole.User,
                content = userMessage
            )
        )

        // Build system prompt with context
        val systemPrompt = buildSystemPrompt()

        // Call LLM
        val response = openAiClient.chatCompletion(
            ChatCompletionRequest(
                model = ModelId("gpt-4"),
                messages = listOf(
                    ChatCompletionMessage(
                        role = ChatRole.System,
                        content = systemPrompt
                    )
                ) + conversationHistory,
                temperature = 0.7,
                maxTokens = 500
            )
        )

        val assistantMessage = response.choices.first().message.content ?: ""

        // Add to history
        conversationHistory.add(
            ChatCompletionMessage(
                role = ChatRole.Assistant,
                content = assistantMessage
            )
        )

        // Parse response and extract quick replies
        parseAssistantResponse(assistantMessage)
    }

    private fun buildSystemPrompt(): String {
        return """
            Você é o assistente virtual "Tá na Mão", especializado em ajudar
            cidadãos brasileiros a descobrir e acessar benefícios sociais.

            CONTEXTO DO USUÁRIO:
            ${userProfile.toContextString()}

            PROGRAMAS DISPONÍVEIS:
            - Bolsa Família: Transferência de renda para famílias em vulnerabilidade
            - BPC/LOAS: Benefício de 1 salário mínimo para idosos 65+ ou PCD
            - Farmácia Popular: Medicamentos gratuitos ou com desconto
            - TSEE: Desconto na conta de energia elétrica
            - Dignidade Menstrual: Absorventes gratuitos

            REGRAS:
            1. Seja sempre cordial e acolhedor
            2. Use linguagem simples, evite termos técnicos
            3. Faça perguntas uma de cada vez
            4. Ofereça opções de resposta rápida quando possível
            5. Nunca prometa que o usuário VAI receber o benefício
            6. Sempre indique que a decisão final é do órgão responsável
            7. Formate listas com emojis para facilitar leitura

            FORMATO DE RESPOSTA:
            - Texto normal para explicações
            - [Texto entre colchetes] para botões de resposta rápida
        """.trimIndent()
    }

    private fun parseAssistantResponse(response: String): ChatMessage {
        // Extract quick replies from [brackets]
        val quickReplyRegex = """\[([^\]]+)\]""".toRegex()
        val matches = quickReplyRegex.findAll(response)

        val quickReplies = matches.map { match ->
            QuickReply(
                id = UUID.randomUUID().toString(),
                label = match.groupValues[1],
                value = match.groupValues[1]
            )
        }.toList()

        // Remove quick reply markers from content
        val cleanContent = response.replace(quickReplyRegex, "").trim()

        return ChatMessage(
            role = MessageRole.ASSISTANT,
            content = cleanContent,
            quickReplies = quickReplies.takeIf { it.isNotEmpty() }
        )
    }

    fun updateProfile(update: UserProfile.() -> UserProfile) {
        userProfile = userProfile.update()
    }

    fun resetConversation() {
        conversationHistory.clear()
        userProfile = UserProfile()
    }
}
```

### Eligibility Engine

```kotlin
// agent/EligibilityEngine.kt

@Singleton
class EligibilityEngine @Inject constructor() {

    fun checkEligibility(profile: UserProfile): List<EligibleProgram> {
        val results = mutableListOf<EligibleProgram>()

        // Bolsa Família
        checkBolsaFamilia(profile)?.let { results.add(it) }

        // BPC
        checkBPC(profile)?.let { results.add(it) }

        // Farmácia Popular
        checkFarmaciaPopular(profile)?.let { results.add(it) }

        // TSEE
        checkTSEE(profile)?.let { results.add(it) }

        // Dignidade Menstrual
        checkDignidadeMenstrual(profile)?.let { results.add(it) }

        return results
    }

    private fun checkBolsaFamilia(profile: UserProfile): EligibleProgram? {
        val familySize = profile.familySize ?: return null
        val income = profile.monthlyIncome ?: return null

        // Critério: renda per capita até R$ 218 (extrema pobreza) ou R$ 660 (pobreza)
        val isEligible = income == IncomeRange.UP_TO_660 ||
                         income == IncomeRange.FROM_660_TO_1320

        if (!isEligible) return null

        // Calcular valor estimado
        val baseValue = 600.0
        val childBonus = if (SpecialCondition.CHILD_0_6 in profile.specialConditions) {
            150.0 * (familySize / 2) // Estimativa de crianças
        } else 0.0

        return EligibleProgram(
            code = ProgramCode.CADUNICO,
            name = "Bolsa Família",
            estimatedValue = baseValue + childBonus,
            confidence = EligibilityConfidence.HIGH,
            requirements = listOf(
                "Cadastro no CadÚnico",
                "Renda familiar per capita até R$ 218 (extrema pobreza) ou até R$ 660 (pobreza)",
                "CPF de todos os membros da família",
                "Comprovante de residência"
            )
        )
    }

    private fun checkBPC(profile: UserProfile): EligibleProgram? {
        val hasElderly = SpecialCondition.ELDERLY in profile.specialConditions
        val hasDisabled = SpecialCondition.DISABLED in profile.specialConditions

        if (!hasElderly && !hasDisabled) return null

        val income = profile.monthlyIncome ?: return null
        val familySize = profile.familySize ?: 1

        // Critério: renda per capita até 1/4 do salário mínimo
        // R$ 1.412 / 4 = R$ 353 per capita
        val perCapitaLimit = 353.0 * familySize
        val isIncomeEligible = income == IncomeRange.UP_TO_660

        val confidence = when {
            hasDisabled -> EligibilityConfidence.MEDIUM // Precisa avaliação médica
            hasElderly && isIncomeEligible -> EligibilityConfidence.HIGH
            else -> EligibilityConfidence.LOW
        }

        return EligibleProgram(
            code = ProgramCode.BPC,
            name = "BPC/LOAS",
            estimatedValue = 1412.0, // 1 salário mínimo
            confidence = confidence,
            requirements = listOf(
                "Idade 65+ (idoso) OU deficiência comprovada",
                "Renda familiar per capita até R$ 353",
                "Cadastro no CadÚnico",
                "Avaliação social e médica (para PCD)"
            )
        )
    }

    private fun checkFarmaciaPopular(profile: UserProfile): EligibleProgram? {
        // Farmácia Popular tem critérios mais flexíveis
        // Disponível para quem tem CPF e receita médica
        return EligibleProgram(
            code = ProgramCode.FARMACIA_POPULAR,
            name = "Farmácia Popular",
            estimatedValue = null, // Varia conforme medicamentos
            confidence = EligibilityConfidence.HIGH,
            requirements = listOf(
                "CPF válido",
                "Receita médica (para alguns medicamentos)",
                "Cadastro no programa (feito na farmácia)"
            )
        )
    }

    private fun checkTSEE(profile: UserProfile): EligibleProgram? {
        val income = profile.monthlyIncome ?: return null

        // Critérios TSEE:
        // - Família inscrita no CadÚnico com renda até 1/2 SM per capita
        // - Família com membro BPC
        // - Família indígena/quilombola

        val isEligible = income == IncomeRange.UP_TO_660 ||
                         income == IncomeRange.FROM_660_TO_1320

        if (!isEligible) return null

        return EligibleProgram(
            code = ProgramCode.TSEE,
            name = "Tarifa Social de Energia Elétrica",
            estimatedValue = null, // Desconto de até 65%
            confidence = EligibilityConfidence.HIGH,
            requirements = listOf(
                "Cadastro no CadÚnico",
                "Renda familiar per capita até 1/2 salário mínimo",
                "Consumo mensal até 220 kWh",
                "Solicitação na distribuidora de energia"
            )
        )
    }

    private fun checkDignidadeMenstrual(profile: UserProfile): EligibleProgram? {
        // Disponível para mulheres cadastradas no CadÚnico
        val income = profile.monthlyIncome ?: return null

        val isEligible = income == IncomeRange.UP_TO_660 ||
                         income == IncomeRange.FROM_660_TO_1320

        if (!isEligible) return null

        return EligibleProgram(
            code = ProgramCode.DIGNIDADE_MENSTRUAL,
            name = "Dignidade Menstrual",
            estimatedValue = null, // Absorventes gratuitos
            confidence = EligibilityConfidence.MEDIUM, // Depende de ser mulher
            requirements = listOf(
                "Ser mulher em idade menstrual",
                "Cadastro no CadÚnico",
                "Retirada em farmácias credenciadas"
            )
        )
    }
}
```

### Chat ViewModel

```kotlin
// presentation/viewmodel/ChatViewModel.kt

@HiltViewModel
class ChatViewModel @Inject constructor(
    private val agentService: AgentService,
    private val eligibilityEngine: EligibilityEngine
) : ViewModel() {

    private val _uiState = MutableStateFlow(ChatUiState())
    val uiState: StateFlow<ChatUiState> = _uiState.asStateFlow()

    init {
        sendWelcomeMessage()
    }

    private fun sendWelcomeMessage() {
        val welcomeMessage = ChatMessage(
            role = MessageRole.ASSISTANT,
            content = """
                Olá! Sou o assistente Tá na Mão.

                Estou aqui para ajudar você a descobrir os benefícios sociais disponíveis para sua família.

                O que você gostaria de fazer?
            """.trimIndent(),
            quickReplies = listOf(
                QuickReply("1", "Verificar Benefícios", "verificar_beneficios"),
                QuickReply("2", "Tirar Dúvidas", "tirar_duvidas"),
                QuickReply("3", "Encontrar Atendimento", "encontrar_atendimento")
            )
        )

        _uiState.update {
            it.copy(messages = listOf(welcomeMessage))
        }
    }

    fun sendMessage(content: String) {
        viewModelScope.launch {
            // Add user message
            val userMessage = ChatMessage(
                role = MessageRole.USER,
                content = content
            )

            _uiState.update {
                it.copy(
                    messages = it.messages + userMessage,
                    isLoading = true
                )
            }

            // Process with agent
            try {
                val response = agentService.processMessage(content)

                _uiState.update {
                    it.copy(
                        messages = it.messages + response,
                        isLoading = false
                    )
                }
            } catch (e: Exception) {
                _uiState.update {
                    it.copy(
                        isLoading = false,
                        error = "Desculpe, ocorreu um erro. Tente novamente."
                    )
                }
            }
        }
    }

    fun selectQuickReply(reply: QuickReply) {
        sendMessage(reply.value)
    }

    fun resetConversation() {
        agentService.resetConversation()
        _uiState.update { ChatUiState() }
        sendWelcomeMessage()
    }
}

data class ChatUiState(
    val messages: List<ChatMessage> = emptyList(),
    val isLoading: Boolean = false,
    val error: String? = null
)
```

### Chat Screen

```kotlin
// presentation/ui/chat/ChatScreen.kt

@Composable
fun ChatScreen(
    viewModel: ChatViewModel = hiltViewModel(),
    onNavigateBack: () -> Unit
) {
    val uiState by viewModel.uiState.collectAsState()

    Scaffold(
        topBar = {
            ChatTopBar(
                onNavigateBack = onNavigateBack,
                onReset = viewModel::resetConversation
            )
        }
    ) { padding ->
        Column(
            modifier = Modifier
                .fillMaxSize()
                .padding(padding)
        ) {
            // Messages List
            LazyColumn(
                modifier = Modifier
                    .weight(1f)
                    .fillMaxWidth(),
                reverseLayout = true,
                contentPadding = PaddingValues(16.dp),
                verticalArrangement = Arrangement.spacedBy(12.dp)
            ) {
                items(uiState.messages.reversed()) { message ->
                    ChatBubble(
                        message = message,
                        onQuickReplyClick = viewModel::selectQuickReply
                    )
                }

                if (uiState.isLoading) {
                    item {
                        TypingIndicator()
                    }
                }
            }

            // Input Area
            ChatInput(
                onSend = viewModel::sendMessage,
                enabled = !uiState.isLoading
            )
        }
    }
}

@Composable
fun ChatBubble(
    message: ChatMessage,
    onQuickReplyClick: (QuickReply) -> Unit
) {
    val isUser = message.role == MessageRole.USER

    Column(
        modifier = Modifier.fillMaxWidth(),
        horizontalAlignment = if (isUser) Alignment.End else Alignment.Start
    ) {
        Surface(
            shape = RoundedCornerShape(
                topStart = 16.dp,
                topEnd = 16.dp,
                bottomStart = if (isUser) 16.dp else 4.dp,
                bottomEnd = if (isUser) 4.dp else 16.dp
            ),
            color = if (isUser) {
                MaterialTheme.colorScheme.primary
            } else {
                MaterialTheme.colorScheme.surfaceVariant
            },
            modifier = Modifier.widthIn(max = 300.dp)
        ) {
            Text(
                text = message.content,
                modifier = Modifier.padding(12.dp),
                color = if (isUser) {
                    MaterialTheme.colorScheme.onPrimary
                } else {
                    MaterialTheme.colorScheme.onSurfaceVariant
                }
            )
        }

        // Quick Replies
        message.quickReplies?.let { replies ->
            Spacer(modifier = Modifier.height(8.dp))
            FlowRow(
                horizontalArrangement = Arrangement.spacedBy(8.dp),
                verticalArrangement = Arrangement.spacedBy(8.dp)
            ) {
                replies.forEach { reply ->
                    QuickReplyChip(
                        reply = reply,
                        onClick = { onQuickReplyClick(reply) }
                    )
                }
            }
        }
    }
}

@Composable
fun QuickReplyChip(
    reply: QuickReply,
    onClick: () -> Unit
) {
    OutlinedButton(
        onClick = onClick,
        shape = RoundedCornerShape(20.dp),
        contentPadding = PaddingValues(horizontal = 16.dp, vertical = 8.dp)
    ) {
        Text(
            text = reply.label,
            style = MaterialTheme.typography.labelMedium
        )
    }
}

@Composable
fun TypingIndicator() {
    Row(
        modifier = Modifier.padding(8.dp),
        horizontalArrangement = Arrangement.spacedBy(4.dp)
    ) {
        repeat(3) { index ->
            val infiniteTransition = rememberInfiniteTransition(label = "typing")
            val alpha by infiniteTransition.animateFloat(
                initialValue = 0.3f,
                targetValue = 1f,
                animationSpec = infiniteRepeatable(
                    animation = tween(600, delayMillis = index * 200),
                    repeatMode = RepeatMode.Reverse
                ),
                label = "typing"
            )

            Box(
                modifier = Modifier
                    .size(8.dp)
                    .background(
                        MaterialTheme.colorScheme.primary.copy(alpha = alpha),
                        CircleShape
                    )
            )
        }
    }
}

@Composable
fun ChatInput(
    onSend: (String) -> Unit,
    enabled: Boolean
) {
    var text by remember { mutableStateOf("") }

    Surface(
        color = MaterialTheme.colorScheme.surface,
        shadowElevation = 8.dp
    ) {
        Row(
            modifier = Modifier
                .fillMaxWidth()
                .padding(8.dp),
            verticalAlignment = Alignment.CenterVertically
        ) {
            OutlinedTextField(
                value = text,
                onValueChange = { text = it },
                modifier = Modifier.weight(1f),
                placeholder = { Text("Digite sua mensagem...") },
                enabled = enabled,
                maxLines = 3,
                shape = RoundedCornerShape(24.dp)
            )

            Spacer(modifier = Modifier.width(8.dp))

            IconButton(
                onClick = {
                    if (text.isNotBlank()) {
                        onSend(text)
                        text = ""
                    }
                },
                enabled = enabled && text.isNotBlank()
            ) {
                Icon(
                    imageVector = Icons.Default.Send,
                    contentDescription = "Enviar",
                    tint = if (enabled && text.isNotBlank()) {
                        MaterialTheme.colorScheme.primary
                    } else {
                        MaterialTheme.colorScheme.onSurfaceVariant
                    }
                )
            }
        }
    }
}
```

---

## Configuração da API LLM

### OpenAI Setup

```kotlin
// di/AgentModule.kt

@Module
@InstallIn(SingletonComponent::class)
object AgentModule {

    @Provides
    @Singleton
    fun provideOpenAI(): OpenAI {
        return OpenAI(
            token = BuildConfig.LLM_API_KEY,
            timeout = Timeout(socket = 60.seconds)
        )
    }

    @Provides
    @Singleton
    fun provideAgentService(
        openAI: OpenAI,
        municipalityRepository: MunicipalityRepository,
        @IoDispatcher dispatcher: CoroutineDispatcher
    ): AgentService {
        return AgentService(openAI, municipalityRepository, dispatcher)
    }
}
```

### Anthropic Alternative

```kotlin
// Para usar Claude ao invés de GPT-4

interface AnthropicApi {
    @POST("v1/messages")
    suspend fun createMessage(
        @Header("x-api-key") apiKey: String,
        @Header("anthropic-version") version: String = "2023-06-01",
        @Body request: AnthropicRequest
    ): AnthropicResponse
}

data class AnthropicRequest(
    val model: String = "claude-3-sonnet-20240229",
    val max_tokens: Int = 1024,
    val messages: List<AnthropicMessage>
)

data class AnthropicMessage(
    val role: String, // "user" ou "assistant"
    val content: String
)
```

---

## Considerações de Privacidade

1. **Dados não armazenados no servidor**: Conversas são processadas em tempo real
2. **Sem coleta de dados pessoais**: Não salvamos CPF, endereço ou dados sensíveis
3. **Contexto local**: Perfil do usuário é mantido apenas na sessão
4. **Opt-in para histórico**: Usuário pode escolher salvar conversas localmente
5. **Política clara**: Informar que dados são processados por LLM externo
