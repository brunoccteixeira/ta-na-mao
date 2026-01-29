# Configuração de Java 17 para Build Android

## Problema
O Android Gradle Plugin 8.3.2 requer Java 17, mas o sistema está usando Java 14.

## Solução: Instalar Java 17

### Opção 1: Usando Homebrew (Recomendado)

```bash
# Instalar Homebrew se não tiver
/bin/bash -c "$(curl -fsSL https://raw.githubusercontent.com/Homebrew/install/HEAD/install.sh)"

# Instalar Java 17
brew install openjdk@17

# Configurar JAVA_HOME
echo 'export JAVA_HOME=$(/usr/libexec/java_home -v 17)' >> ~/.zshrc
source ~/.zshrc
```

### Opção 2: Download Direto da Oracle/Adoptium

1. Baixar Java 17 de: https://adoptium.net/temurin/releases/?version=17
2. Instalar o .dmg
3. Configurar JAVA_HOME:
   ```bash
   export JAVA_HOME=/Library/Java/JavaVirtualMachines/temurin-17.jdk/Contents/Home
   ```

### Opção 3: Usar SDKMAN

```bash
# Instalar SDKMAN
curl -s "https://get.sdkman.io" | bash
source "$HOME/.sdkman/bin/sdkman-init.sh"

# Instalar Java 17
sdk install java 17.0.9-tem

# Usar Java 17
sdk use java 17.0.9-tem
```

## Verificar Instalação

```bash
java -version
# Deve mostrar: openjdk version "17.x.x"
```

## Configurar no Projeto

Após instalar Java 17, adicione ao `gradle.properties`:

```properties
org.gradle.java.home=/Library/Java/JavaVirtualMachines/temurin-17.jdk/Contents/Home
```

Ou configure JAVA_HOME antes de executar gradle:

```bash
export JAVA_HOME=$(/usr/libexec/java_home -v 17)
cd android
./gradlew :app:assembleDebug
```

## Testar Build

```bash
cd android
./gradlew :app:assembleDebug
```

Se funcionar, o APK estará em: `app/build/outputs/apk/debug/app-debug.apk`


