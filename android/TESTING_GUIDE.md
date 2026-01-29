# Guia de Testes - Tá na Mão Android

## Pré-requisitos

### 1. Java 17 (Obrigatório)

O Android Gradle Plugin 8.3.2 requer Java 17. Veja [SETUP_JAVA.md](SETUP_JAVA.md) para instruções de instalação.

**Verificar versão:**
```bash
java -version
# Deve mostrar: openjdk version "17.x.x"
```

### 2. Android SDK

- Android SDK 34
- Android Build Tools
- Configurado via Android Studio ou linha de comando

## Build do App

### Configurar Java 17

**Opção 1: Variável de ambiente (temporário)**
```bash
export JAVA_HOME=$(/usr/libexec/java_home -v 17)
cd android
./gradlew :app:assembleDebug
```

**Opção 2: gradle.properties (permanente)**
Adicione ao `android/gradle.properties`:
```properties
org.gradle.java.home=/Library/Java/JavaVirtualMachines/temurin-17.jdk/Contents/Home
```

### Build APK

```bash
cd android
./gradlew :app:assembleDebug
```

APK gerado em: `app/build/outputs/apk/debug/app-debug.apk`

### Build Release

```bash
./gradlew :app:assembleRelease
```

## Executar Testes

### Testes Unitários

```bash
# Todos os testes
./gradlew test

# Testes específicos
./gradlew test --tests "br.gov.tanamao.presentation.ui.profile.ProfileViewModelTest"

# Com cobertura
./gradlew test jacocoTestReport
```

### Testes Instrumentados (UI)

Requer dispositivo/emulador conectado:

```bash
# Todos os testes instrumentados
./gradlew connectedDebugAndroidTest

# Testes específicos
./gradlew connectedDebugAndroidTest --tests "*.HomeScreenTest"
```

## Instalar no Dispositivo

### Via ADB

```bash
# Listar dispositivos
adb devices

# Instalar APK
adb install app/build/outputs/apk/debug/app-debug.apk

# Ou via gradle
./gradlew installDebug
```

### Via Android Studio

1. Conectar dispositivo/emulador
2. Clicar em "Run" (▶️)
3. Selecionar dispositivo
4. App será instalado e executado

## Checklist de Testes Funcionais

### Perfil do Usuário
- [ ] Tela de perfil carrega
- [ ] Nome do usuário é exibido
- [ ] Estatísticas são exibidas
- [ ] Seção "Dinheiro Esquecido" aparece
- [ ] Verificação automática de dinheiro esquecido funciona
- [ ] Card de dinheiro encontrado é exibido corretamente
- [ ] Navegação para tela Money funciona

### Exportação de Dados (LGPD)
- [ ] Botão "Exportar meus dados" em Privacidade
- [ ] Dialog aparece ao clicar
- [ ] Botão "Exportar" funciona
- [ ] Chooser do Android abre
- [ ] Dados podem ser compartilhados/salvos

### Chat com Agente
- [ ] Chat abre corretamente
- [ ] Mensagens são enviadas
- [ ] Respostas do agente são recebidas
- [ ] Parsing de respostas funciona
- [ ] Botões contextuais aparecem

### Navegação
- [ ] Bottom navigation funciona
- [ ] Navegação entre telas funciona
- [ ] Deep links funcionam (se implementados)

## Troubleshooting

### Erro: "Java 17 required"
- Instale Java 17 (veja SETUP_JAVA.md)
- Configure JAVA_HOME ou gradle.properties

### Erro: "SDK not found"
- Abra Android Studio
- Configure SDK via SDK Manager
- Ou defina ANDROID_HOME

### Testes falhando
- Verifique se mocks estão corretos
- Verifique se dependências estão instaladas
- Execute `./gradlew clean` e tente novamente

### Build lento
- Use Gradle daemon: `org.gradle.daemon=true` em gradle.properties
- Aumente memória: `org.gradle.jvmargs=-Xmx4096m`

## Comandos Úteis

```bash
# Limpar build
./gradlew clean

# Ver dependências
./gradlew :app:dependencies

# Lint
./gradlew lint

# Verificar código
./gradlew check

# Build + Test + Lint
./gradlew build
```


