# 🚀 Teste Rápido do App - Opção Mais Simples

## Opção 1: Build APK e Instalar Manualmente (MAIS SIMPLES) ⭐

### Passo 1: Build do APK
```bash
cd android
export JAVA_HOME=/usr/local/opt/openjdk@17
./gradlew :app:assembleDebug
```

O APK será gerado em:
```
app/build/outputs/apk/debug/app-debug.apk
```

### Passo 2: Instalar no Celular
1. **Conecte seu celular Android via USB**
2. **Ative "Depuração USB" nas opções de desenvolvedor**
3. **Instale o APK:**
   ```bash
   ~/Library/Android/sdk/platform-tools/adb install app/build/outputs/apk/debug/app-debug.apk
   ```

Ou simplesmente transfira o arquivo `app-debug.apk` para o celular e instale manualmente.

---

## Opção 2: Instalar Direto (Se dispositivo conectado)

```bash
cd android
export JAVA_HOME=/usr/local/opt/openjdk@17
./gradlew installDebug
```

Isso faz build + instala automaticamente no dispositivo conectado.

---

## Opção 3: Android Studio (Mais Visual)

1. **Abra o Android Studio**
2. **File → Open** → Selecione a pasta `android`
3. **Aguarde o Gradle sync** (pode demorar na primeira vez)
4. **Conecte seu celular** ou inicie um emulador
5. **Clique no botão ▶️ Run** (ou Shift+F10)

---

## ⚡ Comando Rápido (Tudo em Um)

```bash
cd "/Users/brunoteixeira/Downloads/Ta na Mao/android" && \
export JAVA_HOME=/usr/local/opt/openjdk@17 && \
./gradlew :app:assembleDebug && \
echo "✅ APK gerado em: app/build/outputs/apk/debug/app-debug.apk"
```

---

## 📱 Verificar Dispositivos Conectados

```bash
~/Library/Android/sdk/platform-tools/adb devices
```

Se aparecer um dispositivo, você pode usar `./gradlew installDebug` diretamente!

