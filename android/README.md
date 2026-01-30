# Tá na Mão - Android App

App Android nativo para acesso a benefícios sociais brasileiros, com design inspirado no [Propel.app](https://propel.app).

## ✨ Destaques

- **Design Propel-style**: Dark theme elegante com accent laranja
- **Carteira de Benefícios**: Visualização completa de benefícios ativos, elegíveis e histórico
- **Chat de Triagem IA**: Assistente conversacional para verificação de elegibilidade
- **LGPD Compliant**: Controles granulares de privacidade e consentimento

## Screenshots

| Home | Carteira | Chat | Busca |
|------|----------|------|-------|
| Dashboard com alertas | 3 tabs: Ativos/Elegíveis/Histórico | Assistente IA | Busca de municípios |

## Arquitetura

```
┌─────────────────────────────────────────────────────────────────┐
│                         UI Layer                                 │
│  ┌─────────────┐ ┌─────────────┐ ┌─────────────┐ ┌────────────┐ │
│  │ HomeScreen  │ │WalletScreen │ │ ChatScreen  │ │SearchScreen│ │
│  └──────┬──────┘ └──────┬──────┘ └──────┬──────┘ └─────┬──────┘ │
│         ▼               ▼               ▼              ▼        │
│  ┌─────────────┐ ┌─────────────┐ ┌─────────────┐ ┌────────────┐ │
│  │HomeViewModel│ │WalletViewMdl│ │ChatViewModel│ │SearchViewMd│ │
│  └─────────────┘ └─────────────┘ └─────────────┘ └────────────┘ │
└────────────────────────────┬────────────────────────────────────┘
                             │
┌────────────────────────────▼────────────────────────────────────┐
│                       Domain Layer                               │
│  ┌─────────────┐ ┌─────────────┐ ┌─────────────┐                │
│  │ UserBenefit │ │   Wallet    │ │    Chat     │  Models        │
│  └─────────────┘ └─────────────┘ └─────────────┘                │
│  ┌──────────────────────────────────────────────┐               │
│  │          Repository Interfaces                │               │
│  └──────────────────────────────────────────────┘               │
└────────────────────────────┬────────────────────────────────────┘
                             │
┌────────────────────────────▼────────────────────────────────────┐
│                        Data Layer                                │
│  ┌─────────────┐ ┌─────────────┐ ┌─────────────┐                │
│  │ TaNaMaoApi  │ │  DataStore  │ │    Room     │                │
│  └─────────────┘ └─────────────┘ └─────────────┘                │
└─────────────────────────────────────────────────────────────────┘
```

## Stack Tecnológica

| Categoria | Tecnologia |
|-----------|------------|
| **Linguagem** | Kotlin 1.9+ |
| **UI** | Jetpack Compose + Material 3 |
| **Arquitetura** | MVVM + Clean Architecture |
| **DI** | Hilt |
| **Navegação** | Navigation Compose |
| **Networking** | Retrofit + OkHttp |
| **State** | StateFlow + Compose State |
| **Storage** | DataStore (preferences) |
| **Concurrency** | Coroutines + Flow |

## Features MVP

### 1. 🏠 Home Dashboard
- Resumo de benefícios ativos com valores
- Alertas proativos (pagamentos, novos benefícios, prazos)
- Indicadores nacionais (KPIs)
- Quick actions para navegação rápida

### 2. 💰 Carteira de Benefícios
- **Aba Ativos**: Benefícios que o usuário recebe atualmente
- **Aba Elegíveis**: Benefícios que podem ser solicitados
- **Aba Histórico**: Timeline completa de pagamentos

### 3. 💬 Chat de Triagem (IA)
- Assistente conversacional inteligente
- Verificação interativa de elegibilidade
- Sugestões personalizadas de benefícios
- Quick replies para navegação rápida

### 4. 👤 Perfil do Usuário
- **Visão Consolidada**: Estatísticas de benefícios e consultas
- **Dinheiro Esquecido**: Verificação automática de PIS/PASEP, SVR e FGTS
  - Visualização de valores disponíveis por tipo
  - Card destacado quando há dinheiro disponível
  - Breakdown detalhado (PIS/PASEP, Valores a Receber, FGTS)
  - Navegação para tela Money para ver detalhes e resgatar
- **Histórico de Consultas**: Últimas consultas realizadas
- **Benefícios Ativos**: Resumo dos benefícios recebendo

### 5. 🔐 Privacidade (LGPD)
- Tela de consentimento no primeiro acesso
- Configurações granulares de dados e notificações
- **Exportação de Dados**: Exportação completa de dados pessoais
  - Relatório formatado com todas as informações
  - Compartilhamento via Intent do Android
  - Conformidade com LGPD
- Exclusão de dados pessoais

### 5. ⚙️ Configurações
- **Toggle de Tema**: Claro, Escuro ou Sistema (segue configuração do dispositivo)
- Preferência persistida com DataStore
- Acesso via Perfil → Aparência → Tema do aplicativo

## Estrutura do Projeto

```
android/app/src/main/java/br/gov/tanamao/
├── MainActivity.kt                    # Entry point
├── TaNaMaoApp.kt                      # Application class
│
├── data/
│   ├── api/
│   │   └── TaNaMaoApi.kt             # Retrofit endpoints
│   ├── preferences/
│   │   ├── PrivacyPreferences.kt     # DataStore LGPD
│   │   └── ThemePreferences.kt       # DataStore tema (claro/escuro/sistema)
│   └── repository/                    # Implementações
│
├── domain/
│   ├── model/
│   │   ├── UserBenefit.kt            # Modelo de benefício
│   │   ├── Wallet.kt                 # Modelo da carteira
│   │   └── Chat.kt                   # Modelo de mensagens
│   └── repository/
│       ├── WalletRepository.kt
│       └── ChatRepository.kt
│
├── presentation/
│   ├── components/                    # Design System
│   │   ├── PropelCard.kt             # Card base (3 elevações)
│   │   ├── PropelButton.kt           # Botões (6 estilos)
│   │   ├── BenefitCard.kt            # Card de benefício
│   │   ├── AlertBanner.kt            # Banners de alerta
│   │   ├── BottomNavBar.kt           # Navegação inferior
│   │   ├── StatCard.kt               # Cards de estatística
│   │   ├── CoverageBar.kt            # Barra de cobertura
│   │   └── chat/
│   │       ├── MessageBubble.kt      # Bolha de mensagem
│   │       ├── QuickReplyChips.kt    # Chips de resposta
│   │       └── EligibilityResultCard.kt
│   │
│   ├── navigation/
│   │   └── TaNaMaoNavHost.kt         # Rotas + BottomNav
│   │
│   ├── theme/
│   │   ├── Color.kt                  # Paleta Propel
│   │   ├── Theme.kt                  # Dark theme default
│   │   ├── Type.kt                   # Tipografia
│   │   └── Dimens.kt                 # Sistema de espaçamento
│   │
│   ├── ui/
│   │   ├── home/
│   │   │   ├── HomeScreen.kt
│   │   │   └── HomeViewModel.kt
│   │   ├── wallet/
│   │   │   ├── WalletScreen.kt
│   │   │   └── WalletViewModel.kt
│   │   ├── chat/
│   │   │   ├── ChatScreen.kt
│   │   │   └── ChatViewModel.kt
│   │   ├── search/
│   │   │   ├── SearchScreen.kt
│   │   │   └── SearchViewModel.kt
│   │   ├── profile/
│   │   │   ├── ProfileScreen.kt         # Perfil do usuário
│   │   │   └── ProfileViewModel.kt       # ViewModel com exportação LGPD
│   │   ├── money/
│   │   │   ├── MoneyScreen.kt            # Tela de dinheiro esquecido
│   │   │   └── MoneyViewModel.kt
│   │   ├── alerts/
│   │   │   └── AlertsScreen.kt
│   │   ├── consent/
│   │   │   └── ConsentScreen.kt
│   │   ├── settings/
│   │   │   ├── PrivacySettingsScreen.kt  # Privacidade e segurança
│   │   │   ├── SettingsScreen.kt         # Configurações de tema
│   │   │   └── SettingsViewModel.kt      # ViewModel de tema
│   │   ├── map/
│   │   │   └── MapScreen.kt
│   │   └── details/
│   │       └── MunicipalityScreen.kt
│   │
│   └── util/
│       ├── Formatters.kt
│       └── AgentResponseParser.kt       # Parser de respostas do agente
```

## Quick Start

### Pré-requisitos

- Android Studio Hedgehog (2023.1.1)+
- JDK 17+
- Android SDK 34

### Instalação

```bash
# Clonar repositório
git clone https://github.com/tanamao/tanamao.git
cd tanamao/android

# Abrir no Android Studio
open -a "Android Studio" .

# Ou via linha de comando
./gradlew assembleDebug
```

### Configuração

Criar `local.properties`:

```properties
# API Base URL
api.base.url=https://api.tanamao.gov.br/v1/

# Google Maps (opcional)
google.maps.api.key=YOUR_API_KEY
```

### Build & Run

```bash
# Debug
./gradlew assembleDebug

# Release
./gradlew assembleRelease

# Instalar no dispositivo
./gradlew installDebug
```

## Design System

### Paleta de Cores (Propel-style)

```kotlin
// Accent (Laranja)
AccentOrange       = #F99500   // Primary accent
AccentOrangeLight  = #FFAB33   // Hover/pressed
AccentOrangeDark   = #CC7A00   // Darker variant
AccentOrangeSubtle = #1A1A0F   // 10% para backgrounds

// Backgrounds (Dark Theme - OLED optimized)
BackgroundPrimary   = #000000  // Pure black
BackgroundSecondary = #0F0F0F  // Slightly elevated
BackgroundTertiary  = #1A1A1A  // Cards default
BackgroundElevated  = #242424  // Elevated cards
BackgroundInput     = #1F1F1F  // Input fields

// Text
TextPrimary   = #FFFFFF   // Títulos, valores
TextSecondary = #B3B3B3   // Subtítulos
TextTertiary  = #666666   // Labels, hints
TextOnAccent  = #000000   // Texto sobre laranja

// Status
StatusActive   = #22C55E  // Verde (recebendo)
StatusPending  = #F59E0B  // Amarelo (aguardando)
StatusEligible = #3B82F6  // Azul (elegível)
StatusBlocked  = #EF4444  // Vermelho (bloqueado)
```

### Componentes

#### PropelCard

```kotlin
// 3 níveis de elevação
PropelCard(
    elevation = PropelCardElevation.Flat,     // Background sem elevação
    elevation = PropelCardElevation.Standard, // Elevação padrão
    elevation = PropelCardElevation.Elevated  // Maior destaque
) { content() }
```

#### PropelButton

```kotlin
// 6 estilos de botão
PropelButton(
    text = "Verificar",
    style = PropelButtonStyle.Primary,   // Laranja preenchido
    style = PropelButtonStyle.Secondary, // Outline laranja
    style = PropelButtonStyle.Ghost,     // Sem background
    style = PropelButtonStyle.Outline,   // Borda cinza
    style = PropelButtonStyle.Danger,    // Vermelho
    style = PropelButtonStyle.Success,   // Verde
    size = PropelButtonSize.Small / Medium / Large,
    leadingIcon = Icons.Filled.Search,
    fullWidth = true
)
```

#### BenefitCard

```kotlin
BenefitCard(
    title = "Bolsa Família",
    subtitle = "Dezembro 2024",
    value = "R$ 600,00",
    status = BenefitStatus.ACTIVE,  // ACTIVE, PENDING, ELIGIBLE, BLOCKED
    icon = Icons.Filled.Payments,
    onClick = { }
)
```

### Dimensões (Grid 4dp)

```kotlin
TaNaMaoDimens.spacing1  = 4.dp
TaNaMaoDimens.spacing2  = 8.dp
TaNaMaoDimens.spacing3  = 12.dp
TaNaMaoDimens.spacing4  = 16.dp
TaNaMaoDimens.spacing5  = 20.dp
TaNaMaoDimens.spacing6  = 24.dp

TaNaMaoDimens.cardRadius       = 16.dp
TaNaMaoDimens.cardRadiusSmall  = 12.dp
TaNaMaoDimens.chipRadius       = 20.dp

TaNaMaoDimens.bottomNavHeight  = 80.dp
TaNaMaoDimens.screenPaddingHorizontal = 16.dp
```

### Tipografia

| Style | Uso | Size |
|-------|-----|------|
| `displayLarge` | Números hero | 57sp |
| `headlineLarge` | Títulos principais | 32sp |
| `titleLarge` | Títulos de cards | 22sp |
| `titleMedium` | Subtítulos | 16sp |
| `bodyLarge` | Texto principal | 16sp |
| `bodyMedium` | Texto secundário | 14sp |
| `labelMedium` | Badges, chips | 12sp |

## Navegação

### Rotas Definidas

| Rota | Tela | Tab? |
|------|------|------|
| `home` | Dashboard principal | ✅ |
| `search` | Busca de municípios | ✅ |
| `chat` | Assistente IA | ✅ |
| `profile` | Configurações LGPD | ✅ |
| `wallet` | Carteira de benefícios | |
| `map` | Mapa interativo | |
| `alerts` | Central de alertas | |
| `consent` | Consentimento LGPD | |
| `settings` | Configurações (tema) | |
| `municipality/{ibgeCode}` | Detalhes município | |
| `benefit/{benefitId}` | Detalhes benefício | |

### Bottom Navigation

```
┌───────────────────────────────────────────────────┐
│   🏠 Home   │   🔍 Buscar   │   💬 Chat   │   👤 Perfil   │
└───────────────────────────────────────────────────┘
```

## Backend API

O app consome a API REST do backend Tá na Mão:

### Endpoints Principais

| Endpoint | Descrição |
|----------|-----------|
| `GET /programs/` | Lista programas sociais |
| `GET /programs/{code}/ranking` | Ranking de municípios |
| `GET /municipalities/search?q=` | Busca municípios |
| `GET /municipalities/{ibge}` | Detalhes do município |
| `GET /aggregations/national` | KPIs nacionais |
| `GET /aggregations/states` | Dados por estado |
| `GET /geo/states` | GeoJSON estados |

## Programas Sociais

| Programa | Beneficiários | Descrição |
|----------|---------------|-----------|
| **Bolsa Família** | 20.6M famílias | Transferência de renda |
| **BPC/LOAS** | 6.2M | Idosos 65+ e PCD |
| **Farmácia Popular** | 12.4M | Medicamentos gratuitos |
| **TSEE** | 14.3M | Desconto energia |
| **Dignidade Menstrual** | 358k | Absorventes gratuitos |

## Testes

O app possui uma suíte completa de testes automatizados:

### Testes Unitários (ViewModels)

```bash
# Rodar todos os testes unitários
./gradlew testDebugUnitTest

# Rodar testes específicos
./gradlew testDebugUnitTest --tests "br.gov.tanamao.presentation.ui.home.HomeViewModelTest"
```

**ViewModels com testes:**
- ✅ `HomeViewModelTest`
- ✅ `ChatViewModelTest`
- ✅ `SearchViewModelTest`
- ✅ `WalletViewModelTest`
- ✅ `MunicipalityViewModelTest`
- ✅ `SettingsViewModelTest`
- ✅ `MapViewModelTest`

**Tecnologias:**
- JUnit 4
- MockK para mocks
- Turbine para testes de Flow
- Coroutines Test

### Testes Instrumentados (UI)

```bash
# Rodar testes instrumentados (requer emulador/dispositivo)
./gradlew connectedDebugAndroidTest
```

**Testes criados:**
- `MainActivityTest` - Teste básico da activity principal
- `HomeScreenTest` - Testes da tela home (estrutura criada)
- `SearchScreenTest` - Testes da tela de busca (estrutura criada)

**Tecnologias:**
- Espresso
- Compose Testing
- Hilt Android Testing

### CI/CD

Os testes são executados automaticamente via GitHub Actions no CI/CD.

### Outros Comandos

```bash
# Lint
./gradlew lint
```

## Build para Produção

### Configurar Signing

1. Criar keystore (se não existir):
```bash
keytool -genkey -v -keystore tanamao-release.keystore \
  -alias tanamao -keyalg RSA -keysize 2048 -validity 10000
```

2. Configurar `local.properties`:
```properties
KEYSTORE_PATH=tanamao-release.keystore
KEYSTORE_PASSWORD=sua_senha
KEY_ALIAS=tanamao
KEY_PASSWORD=sua_senha
```

### Build APK Release

```bash
./gradlew assembleRelease
# APK assinado em: app/build/outputs/apk/release/app-release.apk
```

### Build AAB para Play Store

```bash
./gradlew bundleRelease
# AAB em: app/build/outputs/bundle/release/app-release.aab
```

### Verificar Assinatura

```bash
# Verificar se APK está assinado
~/Library/Android/sdk/build-tools/34.0.0/apksigner verify --verbose app-release.apk
```

**Output esperado:**
```
Verifies
Verified using v2 scheme (APK Signature Scheme v2): true
```

## Roadmap

### v1.0 (MVP) ✅ - Play Store Ready
- [x] Design System Propel-style
- [x] Home Dashboard com alertas
- [x] Carteira de Benefícios (3 tabs)
- [x] Chat de Triagem IA
- [x] Configurações LGPD
- [x] Busca de Municípios
- [x] Mapa interativo
- [x] **WalletRepository** - Integração real com API
- [x] **BenefitDetailScreen** - Tela de detalhes do benefício
- [x] **Signing configurado** - APK assinado para Play Store
- [x] **R8/ProGuard** - Minificação e ofuscação

### v1.1 (Planejado)
- [ ] Integração gov.br
- [ ] Push notifications (FCM)
- [ ] Biometria/PIN
- [ ] Offline mode
- [ ] Onboarding flow

### v1.2 (Futuro)
- [ ] Widget Android
- [ ] Deep links
- [ ] Instant App
- [ ] Wear OS support

## Documentação

### Guias Principais
- **[TESTING.md](TESTING.md)** - Guia completo de testes, build e checklist
- **[SETUP_JAVA.md](SETUP_JAVA.md)** - Instalação do Java 17

### Arquitetura e Design (docs/)
- [ARCHITECTURE.md](docs/ARCHITECTURE.md) - Arquitetura detalhada
- [DESIGN_SYSTEM.md](docs/DESIGN_SYSTEM.md) - Componentes e paleta
- [API_INTEGRATION.md](docs/API_INTEGRATION.md) - Integração com backend
- [FEATURES.md](docs/FEATURES.md) - Features implementadas

## Contribuição

1. Fork o repositório
2. Crie sua branch (`git checkout -b feature/nova-feature`)
3. Commit suas mudanças (`git commit -m 'Add nova feature'`)
4. Push para a branch (`git push origin feature/nova-feature`)
5. Abra um Pull Request

## Licença

MIT License - Dados públicos do Governo Federal do Brasil.

---

Desenvolvido com 🧡 para o cidadão brasileiro.
