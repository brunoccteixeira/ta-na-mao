# Tá na Mão - Android App

App Android nativo para acesso a benefícios sociais brasileiros com assistente IA integrado.

## Stack Tecnológica

| Tecnologia | Versão | Uso |
|------------|--------|-----|
| Kotlin | 1.9+ | Linguagem principal |
| Jetpack Compose | 1.5+ | UI declarativa |
| Material 3 | - | Design system |
| Hilt | 2.48+ | Injeção de dependência |
| Retrofit | 2.9+ | HTTP client |
| Google Maps Compose | 4.3+ | Mapas inline |
| Navigation Compose | - | Navegação |

## Arquitetura

```
app/src/main/java/br/gov/tanamao/
├── data/
│   ├── api/
│   │   ├── TaNaMaoApi.kt         # Interface Retrofit
│   │   └── dto/
│   │       └── AgentDto.kt       # DTOs do agente
│   └── repository/
│       └── AgentRepositoryImpl.kt
│
├── domain/
│   ├── model/
│   │   ├── Chat.kt               # Modelos de chat
│   │   └── Benefit.kt            # Modelos de benefício
│   └── repository/
│       └── AgentRepository.kt    # Interface
│
├── di/
│   ├── AppModule.kt              # Módulo principal
│   ├── NetworkModule.kt          # Retrofit config
│   └── RepositoryModule.kt       # Bindings
│
└── presentation/
    ├── components/
    │   ├── chat/
    │   │   ├── MessageBubble.kt      # Bolhas de mensagem
    │   │   ├── LocationMapCard.kt    # Card com mapa
    │   │   └── ImagePickerSheet.kt   # Seletor de imagem
    │   └── PropelButton.kt           # Design system
    │
    ├── theme/
    │   ├── Color.kt              # Paleta de cores
    │   ├── Type.kt               # Tipografia
    │   └── Theme.kt              # Tema Material 3
    │
    ├── ui/
    │   ├── chat/
    │   │   ├── ChatScreen.kt     # Tela de chat
    │   │   └── ChatViewModel.kt  # ViewModel do chat
    │   ├── home/
    │   │   └── HomeScreen.kt     # Tela inicial
    │   └── benefits/
    │       └── BenefitsScreen.kt # Lista de benefícios
    │
    └── util/
        └── ImageUtils.kt         # Processamento de imagem
```

## Funcionalidades

### 1. Chat com Agente IA

O chat conecta com o backend FastAPI e utiliza o agente Gemini 2.0 Flash.

**Fluxo:**
1. `ChatViewModel.startConversation()` → `POST /agent/start`
2. `ChatViewModel.sendMessage()` → `POST /agent/chat`
3. Resposta parseada para detectar tipo (texto, localização, etc.)

**Tipos de mensagem:**
- `TEXT` - Mensagem de texto simples
- `QUICK_REPLIES` - Botões de resposta rápida
- `LOCATION` - Card com mapa inline
- `IMAGE` - Imagem enviada pelo usuário
- `ELIGIBILITY_RESULT` - Resultado de verificação
- `DOCUMENT_LIST` - Lista de documentos necessários
- `LOADING` - Indicador de carregamento
- `ERROR` - Mensagem de erro

### 2. Mapa Inline

Quando o agente usa `buscar_cras` ou `buscar_farmacia`, o app:

1. Detecta coordenadas na resposta via regex
2. Cria `MessageMetadata.LocationCard` com lat/lng
3. Renderiza `LocationMapCard` com:
   - Google Maps embed (200dp)
   - Nome e endereço
   - Botões: Maps | Waze | Ligar

**Código relevante:** `ChatViewModel.extractLocationData()`

### 3. Upload de Receita Médica

**Fluxo:**
1. Usuário clica no botão de anexo (clip)
2. `ImagePickerSheet` apresenta opções: Câmera ou Galeria
3. Imagem capturada é processada por `ImageUtils`:
   - Correção de rotação EXIF
   - Compressão (max 1024px)
   - Conversão para Base64
4. `ChatViewModel.sendImageMessage()` envia ao backend
5. Backend processa com Gemini Vision

**Permissões necessárias:**
- `CAMERA`
- `READ_MEDIA_IMAGES` (Android 13+)
- `READ_EXTERNAL_STORAGE` (Android 12 e anteriores)

## Build

### Debug
```bash
./gradlew assembleDebug
# Output: app/build/outputs/apk/debug/app-debug.apk
```

### Release
```bash
./gradlew assembleRelease
# Requer keystore configurado em build.gradle
```

### Instalar no dispositivo
```bash
./gradlew installDebug
# ou
adb install app/build/outputs/apk/debug/app-debug.apk
```

## Configuração

### Google Maps API Key

1. Obtenha uma chave em [Google Cloud Console](https://console.cloud.google.com/apis/credentials)
2. Habilite "Maps SDK for Android"
3. Adicione em `local.properties`:
```properties
MAPS_API_KEY=AIzaSy...
```

### URL do Backend

Edite `di/NetworkModule.kt`:

```kotlin
// Emulador Android
private const val BASE_URL = "http://10.0.2.2:8000/api/v1/"

// Dispositivo físico na mesma rede
private const val BASE_URL = "http://192.168.x.x:8000/api/v1/"

// Produção
private const val BASE_URL = "https://api.tanamao.gov.br/api/v1/"
```

## Testes

```bash
# Testes unitários
./gradlew test

# Testes instrumentados
./gradlew connectedAndroidTest
```

## Design System

O app usa um design system inspirado no [Propel.app](https://propel.app):

### Cores principais
- `AccentOrange` (#FF6B35) - Ações primárias
- `StatusActive` (#4CAF50) - Status online/sucesso
- `BackgroundPrimary` (#121212) - Fundo principal (dark)
- `TextPrimary` (#FFFFFF) - Texto principal

### Componentes
- `PropelButton` - Botões estilizados
- `PropelIconButton` - Botões de ícone
- `PropelCard` - Cards com sombra
- `MessageBubble` - Bolhas de chat

## Estrutura de Dados

### ChatMessage
```kotlin
data class ChatMessage(
    val id: String,
    val content: String,
    val sender: MessageSender,  // USER, ASSISTANT, SYSTEM
    val type: MessageType,
    val metadata: MessageMetadata? = null,
    val timestamp: Long
)
```

### LocationCard (Metadata)
```kotlin
data class LocationCard(
    val name: String,
    val address: String,
    val distance: String?,
    val latitude: Double,
    val longitude: Double,
    val phone: String?,
    val hours: String?,
    val mapsUrl: String?,
    val wazeUrl: String?
)
```

### ImageData (Metadata)
```kotlin
data class ImageData(
    val base64: String,
    val mimeType: String = "image/jpeg",
    val caption: String?
)
```

## Troubleshooting

### Mapa não aparece
- Verifique se `MAPS_API_KEY` está configurada
- Confirme que a API está habilitada no Google Cloud Console
- Verifique o SHA-1 do app no Console

### Erro de conexão com backend
- Confirme que o backend está rodando
- Para emulador, use `10.0.2.2` (não `localhost`)
- Verifique se o firewall permite conexões

### Câmera não funciona
- Confirme permissões no AndroidManifest.xml
- FileProvider deve estar configurado corretamente
- Teste em dispositivo físico (emulador pode ter limitações)

## Próximos Passos

- [ ] Implementar autenticação gov.br
- [ ] Adicionar notificações push
- [ ] Cache offline com Room
- [ ] Testes de UI com Espresso
- [ ] CI/CD com GitHub Actions
