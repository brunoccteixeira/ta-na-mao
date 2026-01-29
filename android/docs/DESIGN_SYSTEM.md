# Design System - Tá na Mão Android

Design system inspirado no [Propel.app](https://propel.app) - dark theme elegante com accent laranja.

## Visão Geral

O design system foi completamente redesenhado para oferecer uma experiência visual moderna, acessível e otimizada para telas OLED.

### Princípios

1. **Dark-first**: Dark theme como padrão, otimizado para OLED
2. **Accent único**: Laranja #F99500 como cor de destaque principal
3. **Grid 4dp**: Sistema de espaçamento baseado em múltiplos de 4dp
4. **Hierarquia clara**: Tipografia com pesos distintos para criar hierarquia

---

## Paleta de Cores

### Accent (Laranja Propel)

```kotlin
// presentation/theme/Color.kt

val AccentOrange       = Color(0xFFF99500)  // Primary accent
val AccentOrangeLight  = Color(0xFFFFAB33)  // Hover/pressed states
val AccentOrangeDark   = Color(0xFFCC7A00)  // Darker variant
val AccentOrangeSubtle = Color(0xFF1A1A0F)  // 10% opacity para backgrounds
```

### Backgrounds (OLED Optimized)

```kotlin
val BackgroundPrimary   = Color(0xFF000000)  // Pure black - main bg
val BackgroundSecondary = Color(0xFF0F0F0F)  // Slightly elevated
val BackgroundTertiary  = Color(0xFF1A1A1A)  // Cards default
val BackgroundElevated  = Color(0xFF242424)  // Elevated cards, modals
val BackgroundInput     = Color(0xFF1F1F1F)  // Text fields
```

### Text

```kotlin
val TextPrimary   = Color(0xFFFFFFFF)  // White - titles, values
val TextSecondary = Color(0xFFB3B3B3)  // Gray - subtitles
val TextTertiary  = Color(0xFF666666)  // Dark gray - hints, labels
val TextOnAccent  = Color(0xFF000000)  // Black - text on orange buttons
```

### Status Colors

```kotlin
val StatusActive   = Color(0xFF22C55E)  // Green - receiving benefit
val StatusPending  = Color(0xFFF59E0B)  // Yellow - pending/processing
val StatusEligible = Color(0xFF3B82F6)  // Blue - can apply
val StatusBlocked  = Color(0xFFEF4444)  // Red - blocked/denied
```

### Semantic Colors

```kotlin
val Success = Color(0xFF22C55E)  // Green
val Warning = Color(0xFFF59E0B)  // Amber
val Error   = Color(0xFFEF4444)  // Red
val Info    = Color(0xFF3B82F6)  // Blue
```

### Program Colors

```kotlin
val BolsaFamilia     = Color(0xFF3B82F6)  // Blue
val BPC              = Color(0xFF8B5CF6)  // Purple
val FarmaciaPopular  = Color(0xFF06B6D4)  // Cyan
val TSEE             = Color(0xFF22C55E)  // Green
val DignidadeMenstrual = Color(0xFFEC4899)  // Pink
```

---

## Tipografia

```kotlin
// presentation/theme/Type.kt

// Display - Números hero
displayLarge  = 57.sp, Bold
displayMedium = 45.sp, Bold
displaySmall  = 36.sp, Bold

// Headlines - Títulos de seção
headlineLarge  = 32.sp, Bold
headlineMedium = 28.sp, Bold
headlineSmall  = 24.sp, SemiBold

// Titles - Títulos de cards
titleLarge  = 22.sp, SemiBold
titleMedium = 16.sp, SemiBold
titleSmall  = 14.sp, Medium

// Body - Texto principal
bodyLarge  = 16.sp, Normal
bodyMedium = 14.sp, Normal
bodySmall  = 12.sp, Normal

// Labels - Badges, chips, hints
labelLarge  = 14.sp, Medium
labelMedium = 12.sp, Medium
labelSmall  = 11.sp, Medium
```

---

## Dimensões (Grid 4dp)

```kotlin
// presentation/theme/Dimens.kt

object TaNaMaoDimens {
    // Base spacing (múltiplos de 4dp)
    val spacing1 = 4.dp
    val spacing2 = 8.dp
    val spacing3 = 12.dp
    val spacing4 = 16.dp
    val spacing5 = 20.dp
    val spacing6 = 24.dp
    val spacing8 = 32.dp

    // Screen padding
    val screenPaddingHorizontal = 16.dp
    val screenPaddingVertical = 24.dp

    // Cards
    val cardRadius = 16.dp
    val cardRadiusSmall = 12.dp
    val cardPadding = 16.dp

    // Chips
    val chipRadius = 20.dp
    val chipHeight = 32.dp

    // Icons
    val iconSizeSmall = 16.dp
    val iconSizeMedium = 24.dp
    val iconSizeLarge = 32.dp

    // Navigation
    val bottomNavHeight = 80.dp
    val topBarHeight = 64.dp

    // Sections
    val sectionSpacing = 24.dp
}
```

---

## Componentes

### PropelCard

Card base com 3 níveis de elevação.

```kotlin
// presentation/components/PropelCard.kt

enum class PropelCardElevation {
    Flat,      // BackgroundTertiary, sem sombra
    Standard,  // BackgroundTertiary + sombra leve
    Elevated   // BackgroundElevated + sombra maior
}

@Composable
fun PropelCard(
    modifier: Modifier = Modifier,
    onClick: (() -> Unit)? = null,
    elevation: PropelCardElevation = PropelCardElevation.Standard,
    contentPadding: PaddingValues = PaddingValues(TaNaMaoDimens.cardPadding),
    content: @Composable ColumnScope.() -> Unit
)
```

**Uso:**
```kotlin
PropelCard(
    elevation = PropelCardElevation.Standard,
    onClick = { navigateToDetail() }
) {
    Text("Card content")
}
```

---

### PropelButton

Botões com 6 estilos e 3 tamanhos.

```kotlin
// presentation/components/PropelButton.kt

enum class PropelButtonStyle {
    Primary,    // Filled orange
    Secondary,  // Outline orange
    Ghost,      // Text only, transparent
    Outline,    // Gray border
    Danger,     // Red filled
    Success     // Green filled
}

enum class PropelButtonSize {
    Small,   // height = 36.dp
    Medium,  // height = 44.dp
    Large    // height = 52.dp
}

@Composable
fun PropelButton(
    text: String,
    onClick: () -> Unit,
    modifier: Modifier = Modifier,
    style: PropelButtonStyle = PropelButtonStyle.Primary,
    size: PropelButtonSize = PropelButtonSize.Medium,
    enabled: Boolean = true,
    fullWidth: Boolean = false,
    leadingIcon: ImageVector? = null,
    trailingIcon: ImageVector? = null
)
```

**Uso:**
```kotlin
// Primary CTA
PropelButton(
    text = "Verificar Elegibilidade",
    onClick = { checkEligibility() },
    style = PropelButtonStyle.Primary,
    size = PropelButtonSize.Large,
    leadingIcon = Icons.Filled.Search,
    fullWidth = true
)

// Secondary action
PropelButton(
    text = "Ver detalhes",
    onClick = { navigateToDetail() },
    style = PropelButtonStyle.Secondary
)

// Ghost/text button
PropelButton(
    text = "Cancelar",
    onClick = { dismiss() },
    style = PropelButtonStyle.Ghost
)
```

---

### PropelIconButton

Botão circular para ícones.

```kotlin
@Composable
fun PropelIconButton(
    icon: ImageVector,
    onClick: () -> Unit,
    modifier: Modifier = Modifier,
    style: PropelButtonStyle = PropelButtonStyle.Ghost,
    size: Dp = 48.dp,
    contentDescription: String? = null
)
```

**Uso:**
```kotlin
PropelIconButton(
    icon = Icons.Outlined.ArrowBack,
    onClick = { navigateBack() },
    style = PropelButtonStyle.Ghost
)
```

---

### BenefitCard

Card para exibir benefícios com status visual.

```kotlin
// presentation/components/BenefitCard.kt

enum class BenefitStatus {
    ACTIVE,    // Green - receiving
    PENDING,   // Yellow - processing
    ELIGIBLE,  // Blue - can apply
    BLOCKED    // Red - denied
}

@Composable
fun BenefitCard(
    title: String,
    subtitle: String,
    value: String,
    status: BenefitStatus,
    icon: ImageVector,
    onClick: () -> Unit,
    modifier: Modifier = Modifier
)
```

**Uso:**
```kotlin
BenefitCard(
    title = "Bolsa Família",
    subtitle = "Dezembro 2024",
    value = "R$ 600,00",
    status = BenefitStatus.ACTIVE,
    icon = Icons.Filled.Payments,
    onClick = { navigateToBenefit("bolsa_familia") }
)
```

---

### AlertBanner

Banner para alertas e notificações.

```kotlin
// presentation/components/AlertBanner.kt

enum class AlertType {
    INFO,      // Blue
    SUCCESS,   // Green
    WARNING,   // Orange
    ERROR      // Red
}

@Composable
fun AlertBanner(
    title: String,
    message: String,
    type: AlertType = AlertType.INFO,
    icon: ImageVector? = null,
    action: String? = null,
    onActionClick: (() -> Unit)? = null,
    onDismiss: (() -> Unit)? = null,
    modifier: Modifier = Modifier
)
```

**Uso:**
```kotlin
AlertBanner(
    title = "Novo pagamento disponível",
    message = "Seu benefício foi depositado hoje!",
    type = AlertType.SUCCESS,
    icon = Icons.Filled.Payments,
    action = "Ver detalhes",
    onActionClick = { navigateToPayment() }
)
```

---

### BottomNavBar (PropelBottomNavBar)

Navegação inferior com 4 destinos.

```kotlin
// presentation/components/BottomNavBar.kt

enum class BottomNavDestination {
    Home,     // 🏠 Home
    Search,   // 🔍 Buscar
    Chat,     // 💬 Chat
    Profile   // 👤 Perfil
}

@Composable
fun PropelBottomNavBar(
    currentRoute: String,
    onNavigate: (BottomNavDestination) -> Unit,
    modifier: Modifier = Modifier
)
```

**Design:**
- Altura: 80dp
- Background: BackgroundSecondary
- Ícone ativo: AccentOrange
- Ícone inativo: TextTertiary
- Label sempre visível

---

### StatCard

Card para exibir estatísticas/KPIs.

```kotlin
// presentation/components/StatCard.kt

@Composable
fun StatCard(
    title: String,
    value: String,
    subtitle: String? = null,
    icon: ImageVector? = null,
    iconTint: Color = AccentOrange,
    trend: StatTrend? = null,
    modifier: Modifier = Modifier
)

enum class StatTrend {
    UP, DOWN, STABLE
}
```

**Uso:**
```kotlin
StatCard(
    title = "Beneficiários",
    value = "21.6M",
    subtitle = "+2.3% este mês",
    icon = Icons.Filled.People,
    trend = StatTrend.UP
)
```

---

### CoverageBar

Barra de progresso para cobertura.

```kotlin
// presentation/components/CoverageBar.kt

@Composable
fun CoverageBar(
    coverage: Float,  // 0.0 to 1.0
    modifier: Modifier = Modifier,
    height: Dp = 8.dp,
    showLabel: Boolean = true
)
```

**Cores por faixa:**
- 80%+ : StatusActive (green)
- 60-79%: CoverageGood (light green)
- 40-59%: Warning (amber)
- 20-39%: AccentOrange (orange)
- <20%: Error (red)

---

### Chat Components

#### MessageBubble

```kotlin
// presentation/components/chat/MessageBubble.kt

@Composable
fun MessageBubble(
    message: ChatMessage,
    modifier: Modifier = Modifier
)
```

**Design:**
- User message: AccentOrange background, TextOnAccent text
- Bot message: BackgroundTertiary background, TextPrimary text
- Cantos arredondados: 16dp (canto do sender: 4dp)

#### QuickReplyChips

```kotlin
// presentation/components/chat/QuickReplyChips.kt

@Composable
fun QuickReplyChips(
    replies: List<QuickReply>,
    onReplyClick: (QuickReply) -> Unit,
    modifier: Modifier = Modifier
)
```

**Design:**
- Chips scrolláveis horizontalmente
- Background: BackgroundTertiary
- Border: AccentOrange quando hover

#### EligibilityResultCard

```kotlin
// presentation/components/chat/EligibilityResultCard.kt

@Composable
fun EligibilityResultCard(
    result: EligibilityResult,
    onBenefitClick: (String) -> Unit,
    modifier: Modifier = Modifier
)
```

---

## Animações

### Transições de Navegação

```kotlin
// Default enter/exit
enterTransition = fadeIn(tween(200)) + slideIntoContainer(Start, tween(300))
exitTransition = fadeOut(tween(200)) + slideOutOfContainer(Start, tween(300))

// Pop (back navigation)
popEnterTransition = fadeIn(tween(200)) + slideIntoContainer(End, tween(300))
popExitTransition = fadeOut(tween(200)) + slideOutOfContainer(End, tween(300))
```

### AnimatedVisibility

```kotlin
// Fade + Expand (vertical content)
AnimatedVisibility(
    visible = isVisible,
    enter = fadeIn() + expandVertically(),
    exit = fadeOut() + shrinkVertically()
)

// Slide (bottom sheets, navbars)
AnimatedVisibility(
    visible = isVisible,
    enter = slideInVertically(initialOffsetY = { it }),
    exit = slideOutVertically(targetOffsetY = { it })
)
```

---

## Acessibilidade

### Contraste

Todas as cores foram validadas para WCAG AA:
- TextPrimary (#FFFFFF) sobre BackgroundPrimary (#000000): 21:1
- AccentOrange (#F99500) sobre BackgroundPrimary (#000000): 9.4:1
- TextSecondary (#B3B3B3) sobre BackgroundTertiary (#1A1A1A): 8.2:1

### Content Descriptions

Todos os ícones interativos devem ter contentDescription:

```kotlin
Icon(
    imageVector = Icons.Filled.ArrowBack,
    contentDescription = "Voltar" // Always provide
)
```

### Touch Targets

Minimum touch target: 48dp × 48dp

```kotlin
IconButton(
    onClick = { },
    modifier = Modifier.size(48.dp) // Minimum size
) {
    Icon(/*...*/)
}
```

---

## Exemplos de Uso

### Tela Home

```kotlin
@Composable
fun HomeScreen() {
    Box(
        modifier = Modifier
            .fillMaxSize()
            .background(BackgroundPrimary)
    ) {
        Column {
            // Alert Banner
            AlertBanner(
                title = "Pagamento disponível",
                message = "Bolsa Família - R$ 600,00",
                type = AlertType.SUCCESS
            )

            // Benefits Section
            Text(
                text = "Seus Benefícios",
                style = MaterialTheme.typography.titleLarge,
                color = TextPrimary
            )

            // Benefit Cards
            BenefitCard(
                title = "Bolsa Família",
                value = "R$ 600,00",
                status = BenefitStatus.ACTIVE,
                /* ... */
            )

            // KPIs
            Row {
                StatCard(title = "Total", value = "R$ 850,00")
                StatCard(title = "Este mês", value = "R$ 600,00")
            }

            // CTA
            PropelButton(
                text = "Verificar novos benefícios",
                style = PropelButtonStyle.Primary,
                fullWidth = true,
                onClick = { /* ... */ }
            )
        }
    }
}
```

---

## Migração da Versão Anterior

### O que mudou

| Antes (v0.x) | Depois (v1.0) |
|--------------|---------------|
| Paleta Teal (#0D9488) | Paleta Orange (#F99500) |
| Light/Dark themes | Dark theme único |
| Espaçamento inconsistente | Grid 4dp |
| Cards Material padrão | PropelCard customizado |
| Botões Material padrão | PropelButton com 6 estilos |

### Arquivos Modificados

```
presentation/theme/
├── Color.kt       // Nova paleta completa
├── Theme.kt       // Dark theme único
├── Type.kt        // Tipografia atualizada
└── Dimens.kt      // NOVO - sistema de espaçamento

presentation/components/
├── PropelCard.kt     // NOVO
├── PropelButton.kt   // NOVO
├── BenefitCard.kt    // NOVO
├── AlertBanner.kt    // NOVO
├── BottomNavBar.kt   // NOVO
├── StatCard.kt       // Refatorado
├── CoverageBar.kt    // Refatorado
└── chat/
    ├── MessageBubble.kt        // NOVO
    ├── QuickReplyChips.kt      // NOVO
    └── EligibilityResultCard.kt // NOVO
```

---

## Referências

- [Propel.app](https://propel.app) - Inspiração de design
- [Material Design 3](https://m3.material.io/) - Base do design system
- [WCAG 2.1 AA](https://www.w3.org/WAI/WCAG21/quickref/) - Acessibilidade
