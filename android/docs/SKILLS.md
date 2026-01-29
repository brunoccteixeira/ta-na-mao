# Habilidades Técnicas - App Android Tá na Mão

Este documento descreve o stack tecnológico e as competências necessárias para desenvolver o app Android Tá na Mão.

## Stack Tecnológico Principal

### Linguagem e Runtime

| Tecnologia | Versão | Descrição |
|------------|--------|-----------|
| **Kotlin** | 1.9+ | Linguagem principal do projeto |
| **JDK** | 17+ | Java Development Kit |
| **Android SDK** | API 26-34 | Suporte Android 8.0 a 14 |

### UI Framework

| Tecnologia | Versão | Uso |
|------------|--------|-----|
| **Jetpack Compose** | 1.5+ | Framework declarativo de UI |
| **Material 3** | 1.2+ | Design system e componentes |
| **Navigation Compose** | 2.7+ | Navegação entre telas |
| **Accompanist** | 0.32+ | Utilitários para Compose |

### Arquitetura e DI

| Tecnologia | Versão | Uso |
|------------|--------|-----|
| **Hilt** | 2.48+ | Injeção de dependências |
| **ViewModel** | 2.6+ | Gerenciamento de estado |
| **Lifecycle** | 2.6+ | Lifecycle-aware components |

### Networking

| Tecnologia | Versão | Uso |
|------------|--------|-----|
| **Retrofit** | 2.9+ | Cliente HTTP REST |
| **OkHttp** | 4.12+ | HTTP client base |
| **Gson** | 2.10+ | Serialização JSON |

### Persistência Local

| Tecnologia | Versão | Uso |
|------------|--------|-----|
| **Room** | 2.6+ | Database SQLite abstraction |
| **DataStore** | 1.0+ | Preferências do usuário |

### Async/Reactive

| Tecnologia | Versão | Uso |
|------------|--------|-----|
| **Coroutines** | 1.7+ | Programação assíncrona |
| **Flow** | 1.7+ | Streams reativos |

### Mapas e Geo

| Tecnologia | Versão | Uso |
|------------|--------|-----|
| **Google Maps SDK** | 18.2+ | Renderização de mapas |
| **Maps Compose** | 4.3+ | Integração Maps + Compose |
| **GeoJSON** | - | Parsing de geometrias |

### Gráficos e Visualização

| Tecnologia | Versão | Uso |
|------------|--------|-----|
| **Vico** | 2.0+ | Charts para Compose |
| **MPAndroidChart** | 3.1+ | Alternativa para charts |

### IA e LLM

| Tecnologia | Versão | Uso |
|------------|--------|-----|
| **OpenAI SDK** | 3.0+ | Integração GPT |
| **Anthropic SDK** | 0.8+ | Integração Claude |

---

## Dependências Gradle (build.gradle.kts)

```kotlin
plugins {
    id("com.android.application")
    id("org.jetbrains.kotlin.android")
    id("com.google.dagger.hilt.android")
    id("com.google.devtools.ksp")
    id("com.google.android.libraries.mapsplatform.secrets-gradle-plugin")
}

android {
    namespace = "br.gov.tanamao"
    compileSdk = 34

    defaultConfig {
        applicationId = "br.gov.tanamao"
        minSdk = 26
        targetSdk = 34
        versionCode = 1
        versionName = "1.0.0"

        testInstrumentationRunner = "androidx.test.runner.AndroidJUnitRunner"
    }

    buildFeatures {
        compose = true
        buildConfig = true
    }

    composeOptions {
        kotlinCompilerExtensionVersion = "1.5.4"
    }
}

dependencies {
    // Core Android
    implementation("androidx.core:core-ktx:1.12.0")
    implementation("androidx.activity:activity-compose:1.8.1")
    implementation("androidx.lifecycle:lifecycle-runtime-ktx:2.6.2")
    implementation("androidx.lifecycle:lifecycle-viewmodel-compose:2.6.2")

    // Compose BOM
    implementation(platform("androidx.compose:compose-bom:2023.10.01"))
    implementation("androidx.compose.ui:ui")
    implementation("androidx.compose.ui:ui-graphics")
    implementation("androidx.compose.ui:ui-tooling-preview")
    implementation("androidx.compose.material3:material3")
    implementation("androidx.compose.material:material-icons-extended")

    // Navigation
    implementation("androidx.navigation:navigation-compose:2.7.5")

    // Hilt
    implementation("com.google.dagger:hilt-android:2.48.1")
    ksp("com.google.dagger:hilt-compiler:2.48.1")
    implementation("androidx.hilt:hilt-navigation-compose:1.1.0")

    // Networking
    implementation("com.squareup.retrofit2:retrofit:2.9.0")
    implementation("com.squareup.retrofit2:converter-gson:2.9.0")
    implementation("com.squareup.okhttp3:okhttp:4.12.0")
    implementation("com.squareup.okhttp3:logging-interceptor:4.12.0")

    // Room Database
    implementation("androidx.room:room-runtime:2.6.1")
    implementation("androidx.room:room-ktx:2.6.1")
    ksp("androidx.room:room-compiler:2.6.1")

    // DataStore
    implementation("androidx.datastore:datastore-preferences:1.0.0")

    // Coroutines
    implementation("org.jetbrains.kotlinx:kotlinx-coroutines-android:1.7.3")

    // Google Maps
    implementation("com.google.maps.android:maps-compose:4.3.0")
    implementation("com.google.android.gms:play-services-maps:18.2.0")
    implementation("com.google.android.gms:play-services-location:21.0.1")

    // Charts (Vico)
    implementation("com.patrykandpatrick.vico:compose:2.0.0-alpha.12")
    implementation("com.patrykandpatrick.vico:compose-m3:2.0.0-alpha.12")

    // Accompanist
    implementation("com.google.accompanist:accompanist-permissions:0.32.0")
    implementation("com.google.accompanist:accompanist-systemuicontroller:0.32.0")

    // Coil (Image Loading)
    implementation("io.coil-kt:coil-compose:2.5.0")

    // OpenAI SDK (para assistente IA)
    implementation("com.aallam.openai:openai-client:3.5.1")
    implementation("io.ktor:ktor-client-android:2.3.6")

    // Testing
    testImplementation("junit:junit:4.13.2")
    testImplementation("org.jetbrains.kotlinx:kotlinx-coroutines-test:1.7.3")
    testImplementation("io.mockk:mockk:1.13.8")
    androidTestImplementation("androidx.test.ext:junit:1.1.5")
    androidTestImplementation("androidx.test.espresso:espresso-core:3.5.1")
    androidTestImplementation("androidx.compose.ui:ui-test-junit4")
    debugImplementation("androidx.compose.ui:ui-tooling")
    debugImplementation("androidx.compose.ui:ui-test-manifest")
}
```

---

## Competências Necessárias

### Nível Júnior

| Competência | Descrição |
|-------------|-----------|
| Kotlin Basics | Sintaxe, null safety, data classes, sealed classes |
| Android Fundamentals | Activities, Fragments, Lifecycle, Intents |
| XML Layouts | Básico para entender legacy code |
| Git | Branching, merge, PR workflow |

### Nível Pleno

| Competência | Descrição |
|-------------|-----------|
| Jetpack Compose | Composables, State, Side-effects, Modifiers |
| MVVM Pattern | ViewModel, LiveData/StateFlow, Repository |
| Coroutines | suspend, launch, async, Flow operators |
| Retrofit | Interceptors, error handling, serialization |
| Room | Entities, DAOs, queries, migrations |
| Hilt | Modules, bindings, scopes, qualifiers |

### Nível Sênior

| Competência | Descrição |
|-------------|-----------|
| Clean Architecture | Camadas, boundaries, dependency rule |
| Testing | Unit tests, UI tests, integration tests |
| Performance | Profiling, memory leaks, ANR prevention |
| Security | ProGuard, certificate pinning, secure storage |
| CI/CD | GitHub Actions, Fastlane, Play Console |
| Google Maps | Custom markers, polygons, GeoJSON rendering |

---

## Bibliotecas por Funcionalidade

### Mapa Interativo

```kotlin
// Google Maps Compose
implementation("com.google.maps.android:maps-compose:4.3.0")
implementation("com.google.maps.android:maps-compose-utils:4.3.0")

// GeoJSON Parsing
implementation("com.google.maps.android:android-maps-utils:3.8.0")
```

**Uso**: Renderização de estados/municípios como polígonos coloridos (choropleth).

### Charts e Gráficos

```kotlin
// Vico Charts (recomendado para Compose)
implementation("com.patrykandpatrick.vico:compose:2.0.0-alpha.12")
implementation("com.patrykandpatrick.vico:compose-m3:2.0.0-alpha.12")
implementation("com.patrykandpatrick.vico:core:2.0.0-alpha.12")

// Alternativa: MPAndroidChart
implementation("com.github.PhilJay:MPAndroidChart:v3.1.0")
```

**Uso**: Gráficos de linha (time-series), barras (comparação de programas), pizza (demographics).

### Networking

```kotlin
// Retrofit + OkHttp
implementation("com.squareup.retrofit2:retrofit:2.9.0")
implementation("com.squareup.retrofit2:converter-gson:2.9.0")
implementation("com.squareup.okhttp3:okhttp:4.12.0")
implementation("com.squareup.okhttp3:logging-interceptor:4.12.0")
```

**Uso**: Consumo da API REST do backend Tá na Mão.

### Cache Local

```kotlin
// Room Database
implementation("androidx.room:room-runtime:2.6.1")
implementation("androidx.room:room-ktx:2.6.1")
ksp("androidx.room:room-compiler:2.6.1")

// DataStore para preferências
implementation("androidx.datastore:datastore-preferences:1.0.0")
```

**Uso**: Cache offline de programas, municípios e GeoJSON.

### Assistente IA

```kotlin
// OpenAI SDK
implementation("com.aallam.openai:openai-client:3.5.1")
implementation("io.ktor:ktor-client-android:2.3.6")

// Alternativa: HTTP direto para Anthropic
// Usar Retrofit com endpoint da API Claude
```

**Uso**: Chat com assistente virtual para verificação de elegibilidade.

### UI Components

```kotlin
// Material 3
implementation("androidx.compose.material3:material3:1.1.2")
implementation("androidx.compose.material:material-icons-extended:1.5.4")

// Accompanist
implementation("com.google.accompanist:accompanist-permissions:0.32.0")
implementation("com.google.accompanist:accompanist-systemuicontroller:0.32.0")
implementation("com.google.accompanist:accompanist-placeholder:0.32.0")
```

**Uso**: Componentes de UI, ícones, permissões, status bar.

---

## Ferramentas de Desenvolvimento

### IDE e Build

| Ferramenta | Versão | Uso |
|------------|--------|-----|
| Android Studio | Hedgehog+ | IDE principal |
| Gradle | 8.0+ | Build system |
| KSP | 1.9+ | Kotlin Symbol Processing |

### Qualidade de Código

| Ferramenta | Uso |
|------------|-----|
| **ktlint** | Linting e formatação Kotlin |
| **Detekt** | Análise estática de código |
| **SonarQube** | Code quality metrics |

### Testing

| Ferramenta | Uso |
|------------|-----|
| **JUnit 4/5** | Unit tests |
| **MockK** | Mocking para Kotlin |
| **Espresso** | UI tests |
| **Compose Testing** | Testes de UI Compose |

### CI/CD

| Ferramenta | Uso |
|------------|-----|
| **GitHub Actions** | CI pipeline |
| **Fastlane** | Deploy automation |
| **Firebase App Distribution** | Beta testing |
| **Play Console** | Publicação |

---

## Configuração Recomendada de Projeto

### settings.gradle.kts

```kotlin
pluginManagement {
    repositories {
        google()
        mavenCentral()
        gradlePluginPortal()
    }
}

dependencyResolutionManagement {
    repositoriesMode.set(RepositoriesMode.FAIL_ON_PROJECT_REPOS)
    repositories {
        google()
        mavenCentral()
    }
}

rootProject.name = "TaNaMao"
include(":app")
```

### gradle.properties

```properties
# Gradle
org.gradle.jvmargs=-Xmx2048m -Dfile.encoding=UTF-8
org.gradle.parallel=true
org.gradle.caching=true

# Android
android.useAndroidX=true
android.nonTransitiveRClass=true

# Kotlin
kotlin.code.style=official

# Compose
android.enableJetifier=false
```

### ProGuard Rules (proguard-rules.pro)

```proguard
# Retrofit
-keepattributes Signature
-keepattributes *Annotation*
-keep class retrofit2.** { *; }
-keepclassmembers,allowshrinking,allowobfuscation interface * {
    @retrofit2.http.* <methods>;
}

# Gson
-keep class br.gov.tanamao.data.api.dto.** { *; }
-keepclassmembers class br.gov.tanamao.data.api.dto.** { *; }

# Room
-keep class * extends androidx.room.RoomDatabase
-keep @androidx.room.Entity class *

# Google Maps
-keep class com.google.android.gms.maps.** { *; }
```

---

## Recursos de Aprendizado

### Documentação Oficial

- [Kotlin Language](https://kotlinlang.org/docs/)
- [Android Developers](https://developer.android.com/)
- [Jetpack Compose](https://developer.android.com/jetpack/compose)
- [Google Maps SDK](https://developers.google.com/maps/documentation/android-sdk)

### Cursos Recomendados

- Android Basics with Compose (Google)
- Advanced Android Development (Udacity)
- Kotlin Coroutines Deep Dive (Marcin Moskala)

### Referências de Arquitetura

- [Guide to App Architecture](https://developer.android.com/topic/architecture)
- [Now in Android](https://github.com/android/nowinandroid) - Sample app oficial
- [Clean Architecture](https://blog.cleancoder.com/uncle-bob/2012/08/13/the-clean-architecture.html)
