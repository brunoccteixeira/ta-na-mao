# 🚀 Como Testar o App - Guia Simples

## Opção 1: Android Studio (MAIS SIMPLES) ⭐

### Passos:

1. **Abrir o projeto no Android Studio**
   ```bash
   # Abra o Android Studio e selecione:
   # File > Open > Escolha a pasta "android"
   ```

2. **Aguardar sincronização**
   - O Android Studio vai sincronizar o Gradle automaticamente
   - Aguarde até aparecer "Gradle sync finished"

3. **Criar/Iniciar Emulador**
   - Clique no ícone de dispositivo (Device Manager) na barra superior
   - Se não tiver emulador: **Create Device** > Escolha um modelo (ex: Pixel 5)
   - Se já tiver: Clique no ▶️ (Play) para iniciar

4. **Executar o App**
   - Clique no botão ▶️ **Run** (ou pressione `Shift + F10`)
   - Ou clique com botão direito em `app` > **Run 'app'**

✅ **Pronto!** O app será instalado e executado automaticamente no emulador.

---

## Opção 2: Dispositivo Físico via USB

### Passos:

1. **Conectar o celular via USB**
   - Ative "Depuração USB" nas opções de desenvolvedor
   - Autorize o computador quando aparecer o aviso

2. **Verificar conexão**
   ```bash
   cd android
   ~/Library/Android/sdk/platform-tools/adb devices
   # Deve mostrar seu dispositivo
   ```

3. **Instalar via Gradle**
   ```bash
   cd android
   export JAVA_HOME=/usr/local/opt/openjdk@17
   ./gradlew installDebug
   ```

✅ **Pronto!** O app será instalado no seu celular.

---

## Opção 3: Build APK e Instalar Manualmente

### Passos:

1. **Gerar APK**
   ```bash
   cd android
   export JAVA_HOME=/usr/local/opt/openjdk@17
   ./gradlew :app:assembleDebug
   ```

2. **Localizar o APK**
   - O APK estará em: `android/app/build/outputs/apk/debug/app-debug.apk`

3. **Instalar no celular**
   - Envie o APK para o celular (email, WhatsApp, etc.)
   - Abra o arquivo no celular e instale
   - ⚠️ Pode precisar permitir "Fontes desconhecidas"

---

## 🎯 Recomendação: Android Studio

**A opção mais simples é usar o Android Studio** porque:
- ✅ Tudo é automático
- ✅ Emulador integrado
- ✅ Debug fácil
- ✅ Hot reload
- ✅ Logs visuais

### Se não tiver Android Studio instalado:

1. **Baixar**: https://developer.android.com/studio
2. **Instalar**: Siga o instalador
3. **Abrir projeto**: File > Open > pasta "android"
4. **Aguardar**: Gradle vai configurar tudo automaticamente

---

## ⚡ Comandos Rápidos

```bash
# Ir para pasta do projeto
cd "/Users/brunoteixeira/Downloads/Ta na Mao/android"

# Configurar Java (só precisa fazer uma vez por sessão)
export JAVA_HOME=/usr/local/opt/openjdk@17

# Build e instalar em dispositivo conectado
./gradlew installDebug

# Apenas build (gerar APK)
./gradlew :app:assembleDebug

# Executar testes
./gradlew test
```

---

## ❓ Problemas Comuns

### "No devices found"
- **Solução**: Conecte um dispositivo ou inicie um emulador

### "Gradle sync failed"
- **Solução**: Verifique se Java 17 está configurado (já está ✅)

### "SDK not found"
- **Solução**: O SDK está em `~/Library/Android/sdk` (já configurado ✅)

---

**Dica**: Use o Android Studio para a melhor experiência! 🎉


