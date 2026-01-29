# Componentes UI - App Android Tá na Mão

Este documento descreve o Design System e os componentes reutilizáveis do app Android Tá na Mão.

## Design System

### Paleta de Cores

```kotlin
// presentation/theme/Color.kt

// Primary Colors
val Primary = Color(0xFF0D9488)       // Teal 600
val PrimaryDark = Color(0xFF0F766E)   // Teal 700
val PrimaryLight = Color(0xFF14B8A6)  // Teal 500

// Secondary Colors
val Secondary = Color(0xFF10B981)     // Emerald 500
val SecondaryDark = Color(0xFF059669) // Emerald 600

// Background Colors
val BackgroundDark = Color(0xFF020617)   // Slate 950
val SurfaceDark = Color(0xFF0F172A)      // Slate 900
val SurfaceVariantDark = Color(0xFF1E293B) // Slate 800

val BackgroundLight = Color(0xFFF8FAFC)  // Slate 50
val SurfaceLight = Color(0xFFFFFFFF)     // White
val SurfaceVariantLight = Color(0xFFF1F5F9) // Slate 100

// Text Colors
val TextPrimaryDark = Color(0xFFF1F5F9)  // Slate 100
val TextSecondaryDark = Color(0xFF94A3B8) // Slate 400
val TextTertiaryDark = Color(0xFF475569)  // Slate 600

val TextPrimaryLight = Color(0xFF0F172A)  // Slate 900
val TextSecondaryLight = Color(0xFF64748B) // Slate 500

// Semantic Colors
val Success = Color(0xFF22C55E)    // Green 500
val Warning = Color(0xFFF59E0B)    // Amber 500
val Error = Color(0xFFEF4444)      // Red 500
val Info = Color(0xFF3B82F6)       // Blue 500

// Coverage Scale Colors
val CoverageExcellent = Color(0xFF166534)  // Green 800
val CoverageGood = Color(0xFF22C55E)       // Green 500
val CoverageRegular = Color(0xFFFACC15)    // Yellow 400
val CoverageLow = Color(0xFFF97316)        // Orange 500
val CoverageCritical = Color(0xFFDC2626)   // Red 600

// Program Colors
val ColorBolsaFamilia = Color(0xFF3B82F6)  // Blue
val ColorBPC = Color(0xFF8B5CF6)           // Purple
val ColorFarmacia = Color(0xFF06B6D4)      // Cyan
val ColorTSEE = Color(0xFF22C55E)          // Green
val ColorDignidade = Color(0xFFEC4899)     // Pink
```

### Tipografia

```kotlin
// presentation/theme/Type.kt

val TaNaMaoTypography = Typography(
    // Headlines
    headlineLarge = TextStyle(
        fontFamily = FontFamily.Default,
        fontWeight = FontWeight.Bold,
        fontSize = 32.sp,
        lineHeight = 40.sp
    ),
    headlineMedium = TextStyle(
        fontFamily = FontFamily.Default,
        fontWeight = FontWeight.Bold,
        fontSize = 28.sp,
        lineHeight = 36.sp
    ),
    headlineSmall = TextStyle(
        fontFamily = FontFamily.Default,
        fontWeight = FontWeight.SemiBold,
        fontSize = 24.sp,
        lineHeight = 32.sp
    ),

    // Titles
    titleLarge = TextStyle(
        fontFamily = FontFamily.Default,
        fontWeight = FontWeight.SemiBold,
        fontSize = 22.sp,
        lineHeight = 28.sp
    ),
    titleMedium = TextStyle(
        fontFamily = FontFamily.Default,
        fontWeight = FontWeight.Medium,
        fontSize = 16.sp,
        lineHeight = 24.sp
    ),
    titleSmall = TextStyle(
        fontFamily = FontFamily.Default,
        fontWeight = FontWeight.Medium,
        fontSize = 14.sp,
        lineHeight = 20.sp
    ),

    // Body
    bodyLarge = TextStyle(
        fontFamily = FontFamily.Default,
        fontWeight = FontWeight.Normal,
        fontSize = 16.sp,
        lineHeight = 24.sp
    ),
    bodyMedium = TextStyle(
        fontFamily = FontFamily.Default,
        fontWeight = FontWeight.Normal,
        fontSize = 14.sp,
        lineHeight = 20.sp
    ),
    bodySmall = TextStyle(
        fontFamily = FontFamily.Default,
        fontWeight = FontWeight.Normal,
        fontSize = 12.sp,
        lineHeight = 16.sp
    ),

    // Labels
    labelLarge = TextStyle(
        fontFamily = FontFamily.Default,
        fontWeight = FontWeight.Medium,
        fontSize = 14.sp,
        lineHeight = 20.sp
    ),
    labelMedium = TextStyle(
        fontFamily = FontFamily.Default,
        fontWeight = FontWeight.Medium,
        fontSize = 12.sp,
        lineHeight = 16.sp
    ),
    labelSmall = TextStyle(
        fontFamily = FontFamily.Default,
        fontWeight = FontWeight.Medium,
        fontSize = 11.sp,
        lineHeight = 16.sp
    )
)
```

### Tema

```kotlin
// presentation/theme/Theme.kt

private val DarkColorScheme = darkColorScheme(
    primary = Primary,
    onPrimary = Color.White,
    primaryContainer = PrimaryDark,
    secondary = Secondary,
    onSecondary = Color.White,
    background = BackgroundDark,
    onBackground = TextPrimaryDark,
    surface = SurfaceDark,
    onSurface = TextPrimaryDark,
    surfaceVariant = SurfaceVariantDark,
    onSurfaceVariant = TextSecondaryDark,
    error = Error,
    onError = Color.White
)

private val LightColorScheme = lightColorScheme(
    primary = Primary,
    onPrimary = Color.White,
    primaryContainer = PrimaryLight,
    secondary = Secondary,
    onSecondary = Color.White,
    background = BackgroundLight,
    onBackground = TextPrimaryLight,
    surface = SurfaceLight,
    onSurface = TextPrimaryLight,
    surfaceVariant = SurfaceVariantLight,
    onSurfaceVariant = TextSecondaryLight,
    error = Error,
    onError = Color.White
)

@Composable
fun TaNaMaoTheme(
    darkTheme: Boolean = isSystemInDarkTheme(),
    content: @Composable () -> Unit
) {
    val colorScheme = if (darkTheme) DarkColorScheme else LightColorScheme

    MaterialTheme(
        colorScheme = colorScheme,
        typography = TaNaMaoTypography,
        content = content
    )
}
```

---

## Componentes Reutilizáveis

### 1. StatCard (KPI Card)

```kotlin
// presentation/components/StatCard.kt

@Composable
fun StatCard(
    title: String,
    value: String,
    subtitle: String? = null,
    icon: ImageVector? = null,
    iconTint: Color = MaterialTheme.colorScheme.primary,
    modifier: Modifier = Modifier
) {
    Card(
        modifier = modifier,
        colors = CardDefaults.cardColors(
            containerColor = MaterialTheme.colorScheme.surfaceVariant
        ),
        shape = RoundedCornerShape(12.dp)
    ) {
        Column(
            modifier = Modifier
                .fillMaxWidth()
                .padding(16.dp)
        ) {
            Row(
                verticalAlignment = Alignment.CenterVertically,
                horizontalArrangement = Arrangement.SpaceBetween,
                modifier = Modifier.fillMaxWidth()
            ) {
                Text(
                    text = title,
                    style = MaterialTheme.typography.labelMedium,
                    color = MaterialTheme.colorScheme.onSurfaceVariant
                )
                icon?.let {
                    Icon(
                        imageVector = it,
                        contentDescription = null,
                        tint = iconTint,
                        modifier = Modifier.size(20.dp)
                    )
                }
            }

            Spacer(modifier = Modifier.height(8.dp))

            Text(
                text = value,
                style = MaterialTheme.typography.headlineSmall,
                color = MaterialTheme.colorScheme.onSurface,
                fontWeight = FontWeight.Bold
            )

            subtitle?.let {
                Text(
                    text = it,
                    style = MaterialTheme.typography.bodySmall,
                    color = MaterialTheme.colorScheme.onSurfaceVariant
                )
            }
        }
    }
}

// Uso
@Preview
@Composable
fun StatCardPreview() {
    TaNaMaoTheme {
        StatCard(
            title = "População",
            value = "215M",
            subtitle = "habitantes",
            icon = Icons.Default.People
        )
    }
}
```

### 2. ProgramCard

```kotlin
// presentation/components/ProgramCard.kt

@Composable
fun ProgramCard(
    program: Program,
    isSelected: Boolean,
    onClick: () -> Unit,
    modifier: Modifier = Modifier
) {
    val backgroundColor = if (isSelected) {
        MaterialTheme.colorScheme.primaryContainer
    } else {
        MaterialTheme.colorScheme.surfaceVariant
    }

    Card(
        modifier = modifier.clickable(onClick = onClick),
        colors = CardDefaults.cardColors(containerColor = backgroundColor),
        shape = RoundedCornerShape(12.dp)
    ) {
        Column(
            modifier = Modifier
                .fillMaxWidth()
                .padding(16.dp)
        ) {
            Row(
                verticalAlignment = Alignment.CenterVertically,
                horizontalArrangement = Arrangement.SpaceBetween,
                modifier = Modifier.fillMaxWidth()
            ) {
                Text(
                    text = program.name,
                    style = MaterialTheme.typography.titleMedium,
                    fontWeight = FontWeight.SemiBold
                )

                ProgramBadge(code = program.code)
            }

            Spacer(modifier = Modifier.height(12.dp))

            // Stats Row
            Row(
                horizontalArrangement = Arrangement.SpaceBetween,
                modifier = Modifier.fillMaxWidth()
            ) {
                StatItem(
                    label = "Beneficiários",
                    value = program.nationalStats?.totalBeneficiaries?.formatNumber() ?: "-"
                )
                StatItem(
                    label = "Famílias",
                    value = program.nationalStats?.totalFamilies?.formatNumber() ?: "-"
                )
                StatItem(
                    label = "Valor",
                    value = program.nationalStats?.totalValueBrl?.formatCurrency() ?: "-"
                )
            }

            // Freshness indicator
            program.nationalStats?.latestDataDate?.let { date ->
                Spacer(modifier = Modifier.height(8.dp))
                Text(
                    text = "Atualizado: ${date.formatMonthYear()}",
                    style = MaterialTheme.typography.bodySmall,
                    color = MaterialTheme.colorScheme.onSurfaceVariant
                )
            }
        }
    }
}

@Composable
private fun StatItem(label: String, value: String) {
    Column {
        Text(
            text = value,
            style = MaterialTheme.typography.titleSmall,
            fontWeight = FontWeight.Bold
        )
        Text(
            text = label,
            style = MaterialTheme.typography.labelSmall,
            color = MaterialTheme.colorScheme.onSurfaceVariant
        )
    }
}

@Composable
fun ProgramBadge(code: ProgramCode) {
    val color = when (code) {
        ProgramCode.CADUNICO -> ColorBolsaFamilia
        ProgramCode.BPC -> ColorBPC
        ProgramCode.FARMACIA_POPULAR -> ColorFarmacia
        ProgramCode.TSEE -> ColorTSEE
        ProgramCode.DIGNIDADE_MENSTRUAL -> ColorDignidade
    }

    Surface(
        shape = RoundedCornerShape(4.dp),
        color = color.copy(alpha = 0.2f)
    ) {
        Text(
            text = code.abbreviation,
            modifier = Modifier.padding(horizontal = 8.dp, vertical = 4.dp),
            style = MaterialTheme.typography.labelSmall,
            color = color,
            fontWeight = FontWeight.Bold
        )
    }
}
```

### 3. CoverageBar (Progress Bar)

```kotlin
// presentation/components/CoverageBar.kt

@Composable
fun CoverageBar(
    coverage: Float, // 0.0 to 1.0
    modifier: Modifier = Modifier,
    height: Dp = 8.dp,
    showLabel: Boolean = true
) {
    val color = getCoverageColor(coverage)
    val percentage = (coverage * 100).toInt()

    Column(modifier = modifier) {
        if (showLabel) {
            Row(
                modifier = Modifier.fillMaxWidth(),
                horizontalArrangement = Arrangement.SpaceBetween
            ) {
                Text(
                    text = "Cobertura",
                    style = MaterialTheme.typography.labelSmall,
                    color = MaterialTheme.colorScheme.onSurfaceVariant
                )
                Text(
                    text = "$percentage%",
                    style = MaterialTheme.typography.labelSmall,
                    fontWeight = FontWeight.Bold,
                    color = color
                )
            }
            Spacer(modifier = Modifier.height(4.dp))
        }

        Box(
            modifier = Modifier
                .fillMaxWidth()
                .height(height)
                .clip(RoundedCornerShape(height / 2))
                .background(MaterialTheme.colorScheme.surfaceVariant)
        ) {
            Box(
                modifier = Modifier
                    .fillMaxWidth(coverage.coerceIn(0f, 1f))
                    .fillMaxHeight()
                    .background(color)
            )
        }
    }
}

@Composable
fun getCoverageColor(coverage: Float): Color {
    return when {
        coverage >= 0.8f -> CoverageExcellent
        coverage >= 0.6f -> CoverageGood
        coverage >= 0.4f -> CoverageRegular
        coverage >= 0.2f -> CoverageLow
        else -> CoverageCritical
    }
}
```

### 4. SearchBar

```kotlin
// presentation/components/SearchBar.kt

@OptIn(ExperimentalMaterial3Api::class)
@Composable
fun TaNaMaoSearchBar(
    query: String,
    onQueryChange: (String) -> Unit,
    onSearch: (String) -> Unit,
    placeholder: String = "Buscar município...",
    modifier: Modifier = Modifier
) {
    var active by remember { mutableStateOf(false) }

    SearchBar(
        query = query,
        onQueryChange = onQueryChange,
        onSearch = {
            onSearch(query)
            active = false
        },
        active = active,
        onActiveChange = { active = it },
        modifier = modifier.fillMaxWidth(),
        placeholder = {
            Text(
                text = placeholder,
                color = MaterialTheme.colorScheme.onSurfaceVariant
            )
        },
        leadingIcon = {
            Icon(
                imageVector = Icons.Default.Search,
                contentDescription = "Buscar"
            )
        },
        trailingIcon = {
            if (query.isNotEmpty()) {
                IconButton(onClick = { onQueryChange("") }) {
                    Icon(
                        imageVector = Icons.Default.Clear,
                        contentDescription = "Limpar"
                    )
                }
            }
        },
        colors = SearchBarDefaults.colors(
            containerColor = MaterialTheme.colorScheme.surfaceVariant
        )
    ) {
        // Search suggestions can go here
    }
}
```

### 5. RankingList

```kotlin
// presentation/components/RankingList.kt

@Composable
fun RankingList(
    items: List<RankingItem>,
    onItemClick: (RankingItem) -> Unit,
    modifier: Modifier = Modifier
) {
    LazyColumn(
        modifier = modifier,
        verticalArrangement = Arrangement.spacedBy(8.dp)
    ) {
        items(items) { item ->
            RankingListItem(
                item = item,
                onClick = { onItemClick(item) }
            )
        }
    }
}

@Composable
fun RankingListItem(
    item: RankingItem,
    onClick: () -> Unit,
    modifier: Modifier = Modifier
) {
    Card(
        modifier = modifier
            .fillMaxWidth()
            .clickable(onClick = onClick),
        colors = CardDefaults.cardColors(
            containerColor = MaterialTheme.colorScheme.surfaceVariant
        )
    ) {
        Row(
            modifier = Modifier
                .fillMaxWidth()
                .padding(12.dp),
            verticalAlignment = Alignment.CenterVertically
        ) {
            // Rank Badge
            RankBadge(rank = item.rank)

            Spacer(modifier = Modifier.width(12.dp))

            // Municipality Info
            Column(modifier = Modifier.weight(1f)) {
                Text(
                    text = item.name,
                    style = MaterialTheme.typography.titleSmall,
                    fontWeight = FontWeight.SemiBold
                )
                Text(
                    text = item.ibgeCode,
                    style = MaterialTheme.typography.bodySmall,
                    color = MaterialTheme.colorScheme.onSurfaceVariant
                )
            }

            // Metric
            Column(horizontalAlignment = Alignment.End) {
                Text(
                    text = "${(item.coverageRate * 100).toInt()}%",
                    style = MaterialTheme.typography.titleMedium,
                    fontWeight = FontWeight.Bold,
                    color = getCoverageColor(item.coverageRate)
                )
                Text(
                    text = item.totalBeneficiaries.formatNumber(),
                    style = MaterialTheme.typography.bodySmall,
                    color = MaterialTheme.colorScheme.onSurfaceVariant
                )
            }
        }
    }
}

@Composable
fun RankBadge(rank: Int) {
    val (emoji, color) = when (rank) {
        1 -> "🥇" to Color(0xFFFFD700)
        2 -> "🥈" to Color(0xFFC0C0C0)
        3 -> "🥉" to Color(0xFFCD7F32)
        else -> "$rank" to MaterialTheme.colorScheme.onSurfaceVariant
    }

    if (rank <= 3) {
        Text(
            text = emoji,
            fontSize = 24.sp
        )
    } else {
        Surface(
            shape = CircleShape,
            color = MaterialTheme.colorScheme.surface,
            modifier = Modifier.size(32.dp)
        ) {
            Box(contentAlignment = Alignment.Center) {
                Text(
                    text = emoji,
                    style = MaterialTheme.typography.labelMedium,
                    color = color
                )
            }
        }
    }
}
```

### 6. MapLegend

```kotlin
// presentation/components/MapLegend.kt

@Composable
fun MapLegend(
    metric: MetricType,
    modifier: Modifier = Modifier
) {
    val items = when (metric) {
        MetricType.COVERAGE -> listOf(
            LegendItem("80%+", CoverageExcellent),
            LegendItem("60-79%", CoverageGood),
            LegendItem("40-59%", CoverageRegular),
            LegendItem("20-39%", CoverageLow),
            LegendItem("<20%", CoverageCritical)
        )
        MetricType.BENEFICIARIES -> listOf(
            LegendItem("Alto", CoverageExcellent),
            LegendItem("Médio-Alto", CoverageGood),
            LegendItem("Médio", CoverageRegular),
            LegendItem("Médio-Baixo", CoverageLow),
            LegendItem("Baixo", CoverageCritical)
        )
        // ... other metrics
    }

    Card(
        modifier = modifier,
        colors = CardDefaults.cardColors(
            containerColor = MaterialTheme.colorScheme.surface.copy(alpha = 0.9f)
        )
    ) {
        Column(modifier = Modifier.padding(12.dp)) {
            Text(
                text = metric.label,
                style = MaterialTheme.typography.labelMedium,
                fontWeight = FontWeight.SemiBold
            )

            Spacer(modifier = Modifier.height(8.dp))

            items.forEach { item ->
                LegendRow(item = item)
            }
        }
    }
}

@Composable
private fun LegendRow(item: LegendItem) {
    Row(
        verticalAlignment = Alignment.CenterVertically,
        modifier = Modifier.padding(vertical = 2.dp)
    ) {
        Box(
            modifier = Modifier
                .size(16.dp)
                .background(item.color, RoundedCornerShape(2.dp))
        )
        Spacer(modifier = Modifier.width(8.dp))
        Text(
            text = item.label,
            style = MaterialTheme.typography.bodySmall
        )
    }
}

data class LegendItem(val label: String, val color: Color)
```

### 7. ProgramChip

```kotlin
// presentation/components/ProgramChip.kt

@OptIn(ExperimentalMaterial3Api::class)
@Composable
fun ProgramChip(
    program: Program,
    isSelected: Boolean,
    onClick: () -> Unit,
    modifier: Modifier = Modifier
) {
    val programColor = getProgramColor(program.code)

    FilterChip(
        selected = isSelected,
        onClick = onClick,
        label = {
            Text(
                text = program.code.abbreviation,
                fontWeight = if (isSelected) FontWeight.Bold else FontWeight.Normal
            )
        },
        modifier = modifier,
        colors = FilterChipDefaults.filterChipColors(
            selectedContainerColor = programColor.copy(alpha = 0.2f),
            selectedLabelColor = programColor
        ),
        border = FilterChipDefaults.filterChipBorder(
            borderColor = if (isSelected) programColor else MaterialTheme.colorScheme.outline,
            selectedBorderColor = programColor
        )
    )
}

@Composable
fun ProgramChipGroup(
    programs: List<Program>,
    selectedProgram: ProgramCode?,
    onProgramSelected: (ProgramCode?) -> Unit,
    modifier: Modifier = Modifier
) {
    LazyRow(
        modifier = modifier,
        horizontalArrangement = Arrangement.spacedBy(8.dp),
        contentPadding = PaddingValues(horizontal = 16.dp)
    ) {
        // "Todos" chip
        item {
            FilterChip(
                selected = selectedProgram == null,
                onClick = { onProgramSelected(null) },
                label = { Text("Todos") }
            )
        }

        items(programs) { program ->
            ProgramChip(
                program = program,
                isSelected = selectedProgram == program.code,
                onClick = { onProgramSelected(program.code) }
            )
        }
    }
}

fun getProgramColor(code: ProgramCode): Color = when (code) {
    ProgramCode.CADUNICO -> ColorBolsaFamilia
    ProgramCode.BPC -> ColorBPC
    ProgramCode.FARMACIA_POPULAR -> ColorFarmacia
    ProgramCode.TSEE -> ColorTSEE
    ProgramCode.DIGNIDADE_MENSTRUAL -> ColorDignidade
}
```

### 8. LoadingState

```kotlin
// presentation/components/LoadingState.kt

@Composable
fun LoadingOverlay(
    isLoading: Boolean,
    modifier: Modifier = Modifier,
    content: @Composable () -> Unit
) {
    Box(modifier = modifier) {
        content()

        if (isLoading) {
            Box(
                modifier = Modifier
                    .matchParentSize()
                    .background(MaterialTheme.colorScheme.surface.copy(alpha = 0.7f)),
                contentAlignment = Alignment.Center
            ) {
                CircularProgressIndicator(
                    color = MaterialTheme.colorScheme.primary
                )
            }
        }
    }
}

@Composable
fun SkeletonCard(modifier: Modifier = Modifier) {
    Card(
        modifier = modifier,
        colors = CardDefaults.cardColors(
            containerColor = MaterialTheme.colorScheme.surfaceVariant
        )
    ) {
        Column(modifier = Modifier.padding(16.dp)) {
            SkeletonBox(
                modifier = Modifier
                    .fillMaxWidth(0.6f)
                    .height(16.dp)
            )
            Spacer(modifier = Modifier.height(12.dp))
            SkeletonBox(
                modifier = Modifier
                    .fillMaxWidth(0.4f)
                    .height(24.dp)
            )
            Spacer(modifier = Modifier.height(8.dp))
            SkeletonBox(
                modifier = Modifier
                    .fillMaxWidth(0.3f)
                    .height(12.dp)
            )
        }
    }
}

@Composable
fun SkeletonBox(modifier: Modifier = Modifier) {
    val shimmerColors = listOf(
        MaterialTheme.colorScheme.surface.copy(alpha = 0.6f),
        MaterialTheme.colorScheme.surface.copy(alpha = 0.2f),
        MaterialTheme.colorScheme.surface.copy(alpha = 0.6f)
    )

    val transition = rememberInfiniteTransition(label = "shimmer")
    val translateAnim by transition.animateFloat(
        initialValue = 0f,
        targetValue = 1000f,
        animationSpec = infiniteRepeatable(
            animation = tween(1200, easing = LinearEasing),
            repeatMode = RepeatMode.Restart
        ),
        label = "shimmer"
    )

    Box(
        modifier = modifier
            .clip(RoundedCornerShape(4.dp))
            .background(
                brush = Brush.linearGradient(
                    colors = shimmerColors,
                    start = Offset(translateAnim - 200, 0f),
                    end = Offset(translateAnim, 0f)
                )
            )
    )
}
```

---

## Formatadores

```kotlin
// presentation/util/Formatters.kt

fun Long.formatNumber(): String {
    return when {
        this >= 1_000_000_000 -> String.format("%.1fB", this / 1_000_000_000.0)
        this >= 1_000_000 -> String.format("%.1fM", this / 1_000_000.0)
        this >= 1_000 -> String.format("%.1fk", this / 1_000.0)
        else -> NumberFormat.getNumberInstance(Locale("pt", "BR")).format(this)
    }
}

fun Int.formatNumber(): String = this.toLong().formatNumber()

fun Double.formatCurrency(): String {
    val format = NumberFormat.getCurrencyInstance(Locale("pt", "BR"))
    return format.format(this)
}

fun Double.formatPercent(): String {
    return String.format("%.1f%%", this * 100)
}

fun LocalDate.formatMonthYear(): String {
    val months = listOf(
        "Jan", "Fev", "Mar", "Abr", "Mai", "Jun",
        "Jul", "Ago", "Set", "Out", "Nov", "Dez"
    )
    return "${months[this.monthValue - 1]}/${this.year}"
}

val ProgramCode.abbreviation: String
    get() = when (this) {
        ProgramCode.CADUNICO -> "BF"
        ProgramCode.BPC -> "BPC"
        ProgramCode.FARMACIA_POPULAR -> "Farm"
        ProgramCode.TSEE -> "TSEE"
        ProgramCode.DIGNIDADE_MENSTRUAL -> "Dig"
    }
```

---

## Ícones Customizados

```kotlin
// presentation/components/Icons.kt

object TaNaMaoIcons {
    val Population = Icons.Default.People
    val Families = Icons.Default.FamilyRestroom
    val Beneficiaries = Icons.Default.VolunteerActivism
    val Coverage = Icons.Default.PieChart
    val Gap = Icons.Default.Warning
    val Value = Icons.Default.AttachMoney
    val Map = Icons.Default.Map
    val Search = Icons.Default.Search
    val Chat = Icons.Default.Chat
    val Settings = Icons.Default.Settings
    val Back = Icons.Default.ArrowBack
    val Filter = Icons.Default.FilterList
    val Sort = Icons.Default.Sort
    val Refresh = Icons.Default.Refresh
    val Share = Icons.Default.Share
    val Download = Icons.Default.Download
}
```
