# Guia de Testes - Android

Este documento descreve como executar e escrever testes para o app Android do Tá na Mão.

## Estrutura de Testes

```
android/app/src/
├── test/                    # Testes unitários (rodam na JVM)
│   └── java/br/gov/tanamao/
│       ├── presentation/ui/
│       │   ├── home/HomeViewModelTest.kt
│       │   ├── search/SearchViewModelTest.kt
│       │   └── chat/ChatViewModelTest.kt
│       └── TestUtils.kt     # Utilitários para testes
│
└── androidTest/             # Testes instrumentados (rodam no dispositivo/emulador)
    └── java/br/gov/tanamao/
        ├── HiltTestActivity.kt
        ├── TestApplication.kt
        ├── HiltTestRunner.kt
        └── presentation/ui/
            ├── home/HomeScreenTest.kt
            └── search/SearchScreenTest.kt
```

## Tipos de Testes

### 1. Testes Unitários

Testam ViewModels e lógica de negócio sem dependências do Android.

**Exemplo:**
```kotlin
@Test
fun `loadPrograms should update state with programs on success`() = runTest {
    // Given
    val mockPrograms = listOf(createMockProgram())
    coEvery { repository.getPrograms() } returns flowOf(Result.Success(mockPrograms))

    // When
    viewModel.loadPrograms()

    // Then
    viewModel.uiState.test {
        val state = awaitItem()
        assertEquals(1, state.programs.size)
    }
}
```

### 2. Testes Instrumentados

Testam UI e integração com componentes Android.

**Exemplo:**
```kotlin
@Test
fun homeScreen_displaysTitle() {
    composeTestRule.setContent {
        HomeScreen()
    }
    composeTestRule.onNodeWithText("Dashboard").assertIsDisplayed()
}
```

## Executando Testes

### Testes Unitários

```bash
# Todos os testes unitários
./gradlew testDebugUnitTest

# Teste específico
./gradlew testDebugUnitTest --tests "HomeViewModelTest"

# Com cobertura
./gradlew testDebugUnitTest jacocoTestReport
```

### Testes Instrumentados

```bash
# Todos os testes instrumentados
./gradlew connectedDebugAndroidTest

# Teste específico
./gradlew connectedDebugAndroidTest --tests "HomeScreenTest"

# Em dispositivo específico
adb devices
./gradlew connectedDebugAndroidTest -Pandroid.testInstrumentationRunnerArguments.class=br.gov.tanamao.presentation.ui.home.HomeScreenTest
```

### Via Android Studio

1. **Testes Unitários:**
   - Clique com botão direito no arquivo de teste
   - Selecione "Run 'HomeViewModelTest'"

2. **Testes Instrumentados:**
   - Conecte um dispositivo ou inicie um emulador
   - Clique com botão direito no arquivo de teste
   - Selecione "Run 'HomeScreenTest'"

## Dependências de Teste

### Unit Tests
- `junit:junit` - Framework de testes
- `io.mockk:mockk` - Mocking library
- `app.cash.turbine:turbine` - Testing Flows
- `kotlinx-coroutines-test` - Testing coroutines
- `hilt-android-testing` - Hilt para testes

### Instrumented Tests
- `androidx.compose.ui:ui-test-junit4` - Compose testing
- `androidx.test.espresso:espresso-core` - Espresso (para views XML)
- `hilt-android-testing` - Hilt para testes instrumentados

## Escrevendo Testes

### Testando ViewModels

```kotlin
class MyViewModelTest {
    private lateinit var repository: MyRepository
    private lateinit var viewModel: MyViewModel

    @Before
    fun setup() {
        repository = mockk()
        viewModel = MyViewModel(repository)
    }

    @Test
    fun `test scenario`() = runTest {
        // Arrange
        coEvery { repository.getData() } returns flowOf(Result.Success(data))

        // Act
        viewModel.loadData()

        // Assert
        viewModel.uiState.test {
            val state = awaitItem()
            assertEquals(expected, state.data)
        }
    }
}
```

### Testando Compose UI

```kotlin
@HiltAndroidTest
class MyScreenTest {
    @get:Rule
    val hiltRule = HiltAndroidRule(this)

    @get:Rule
    val composeTestRule = createAndroidComposeRule<HiltTestActivity>()

    @Test
    fun screen_displaysContent() {
        composeTestRule.setContent {
            MyScreen()
        }
        composeTestRule.onNodeWithText("Expected Text").assertIsDisplayed()
    }
}
```

## Mocking com MockK

```kotlin
// Mock de repository
val repository = mockk<MyRepository>()

// Configurar comportamento
coEvery { repository.getData() } returns flowOf(Result.Success(data))
coEvery { repository.saveData(any()) } returns Result.Success(Unit)

// Verificar chamadas
coVerify { repository.getData() }
coVerify(exactly = 2) { repository.saveData(any()) }
```

## Testando Flows com Turbine

```kotlin
viewModel.uiState.test {
    // Skip estados iniciais
    skipItems(1)
    
    // Verificar estado
    val state = awaitItem()
    assertEquals(expected, state.data)
    
    // Verificar que não há mais itens
    awaitComplete()
}
```

## Testando Coroutines

```kotlin
@Test
fun `test with coroutines`() = runTest {
    // Usa TestDispatcher para controle de tempo
    val testDispatcher = StandardTestDispatcher()
    
    // Teste com delay
    viewModel.doSomething()
    advanceTimeBy(1000)
    
    // Verificar resultado
    assertEquals(expected, viewModel.state.value)
}
```

## Cobertura de Código

### Gerar Relatório

```bash
./gradlew testDebugUnitTest jacocoTestReport
```

O relatório estará em:
```
app/build/reports/jacoco/testDebugUnitTest/html/index.html
```

### Configurar Cobertura Mínima

Adicione ao `build.gradle.kts`:

```kotlin
tasks.jacocoTestReport {
    reports {
        xml.required.set(true)
        html.required.set(true)
    }
    finalizedBy(tasks.jacocoTestCoverageVerification)
}

tasks.jacocoTestCoverageVerification {
    violationRules {
        rule {
            limit {
                minimum = "0.70".toBigDecimal() // 70% cobertura mínima
            }
        }
    }
}
```

## Boas Práticas

1. **Nomes Descritivos**: Use nomes que descrevem o comportamento testado
   ```kotlin
   `loadPrograms should update state with programs on success`()
   ```

2. **Arrange-Act-Assert**: Organize testes em 3 partes claras

3. **Um Assert por Teste**: Foque em testar um comportamento por vez

4. **Mock Dependências**: Use mocks para isolar a unidade testada

5. **Test Utils**: Crie funções helper para dados de teste comuns

6. **Test Data Builders**: Use builders para criar objetos de teste complexos

## Troubleshooting

### Erro: "Hilt not initialized"
- Certifique-se de que `@HiltAndroidTest` está presente
- Verifique se `HiltAndroidRule` está configurado corretamente

### Erro: "Coroutine not completed"
- Use `runTest` para testes com coroutines
- Use `TestDispatcher` para controle de tempo

### Testes lentos
- Use `StandardTestDispatcher` para testes unitários
- Evite delays reais em testes

### Compose tests não encontram elementos
- Use `contentDescription` para elementos importantes
- Use `onNodeWithText` para textos visíveis
- Use `onNodeWithTag` para elementos sem texto

## Próximos Passos

1. Adicionar mais testes para ViewModels restantes
2. Adicionar testes de integração para repositories
3. Adicionar testes E2E para fluxos críticos
4. Configurar CI/CD para rodar testes automaticamente

