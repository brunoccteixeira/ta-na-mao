# Quick Start - Tá na Mão Android

## ⚡ Início Rápido

### 1. Pré-requisitos

```bash
# Verificar Java (deve ser 17+)
java -version

# Se não tiver Java 17, instale (veja SETUP_JAVA.md)
```

### 2. Configurar Projeto

```bash
cd android

# Criar local.properties (se não existir)
cat > local.properties << EOF
# API Base URL (para emulador Android use 10.0.2.2)
TANAMAO_API_URL=http://10.0.2.2:8000/api/v1/
# Para dispositivo físico, use IP da sua máquina
# TANAMAO_API_URL=http://192.168.1.X:8000/api/v1/

# Google Maps API Key (opcional)
MAPS_API_KEY=sua_chave_aqui
EOF
```

### 3. Build e Teste

```bash
# Limpar build anterior
./gradlew clean

# Build APK Debug
./gradlew :app:assembleDebug

# APK gerado em: app/build/outputs/apk/debug/app-debug.apk

# Instalar no dispositivo conectado
./gradlew installDebug

# Ou executar testes
./gradlew test
```

### 4. Executar no Emulador/Dispositivo

**Via Android Studio:**
1. Abrir projeto no Android Studio
2. Conectar dispositivo/emulador
3. Clicar em Run (▶️)

**Via linha de comando:**
```bash
# Listar dispositivos
adb devices

# Instalar APK
adb install app/build/outputs/apk/debug/app-debug.apk

# Ou usar gradle
./gradlew installDebug
```

## 🔧 Troubleshooting

### Erro: Java 17 required
```bash
# Verificar versão
java -version

# Se não for 17+, instale (veja SETUP_JAVA.md)
# Depois configure:
export JAVA_HOME=$(/usr/libexec/java_home -v 17)
```

### Erro: SDK not found
```bash
# Abrir Android Studio
# File → Settings → Appearance & Behavior → System Settings → Android SDK
# Instalar Android SDK 34
```

### Build lento
```bash
# Aumentar memória do Gradle (já configurado em gradle.properties)
# Usar Gradle daemon (já habilitado)
```

## 📱 Testar Funcionalidades

Após instalar o app, teste:

1. **Perfil**
   - Abrir tela de perfil
   - Verificar se "Dinheiro Esquecido" aparece
   - Verificar se dados são carregados

2. **Exportação de Dados**
   - Ir em Configurações → Privacidade
   - Clicar em "Exportar meus dados"
   - Verificar se chooser do Android abre

3. **Chat**
   - Abrir chat
   - Enviar mensagem "meus dados"
   - Verificar resposta do agente

4. **Navegação**
   - Testar navegação entre telas
   - Verificar bottom navigation

## 🚀 Comandos Úteis

```bash
# Build completo
./gradlew build

# Apenas testes
./gradlew test

# Lint
./gradlew lint

# Limpar e rebuild
./gradlew clean build

# Ver dependências
./gradlew :app:dependencies

# Ver tasks disponíveis
./gradlew tasks
```

## 📝 Notas

- **Backend**: Certifique-se de que o backend está rodando em `http://localhost:8000`
- **Emulador**: Use `10.0.2.2` em vez de `localhost` para acessar o backend
- **Dispositivo Físico**: Use o IP da sua máquina na rede local

