# Guia de Testes - Tá na Mão Android

Este guia consolida todas as formas de testar o app Android.

## Opção 1: Android Studio (Recomendado)

A forma mais simples e com melhor experiência de desenvolvimento.

### Passos:

1. **Abrir o projeto**
   ```bash
   # File > Open > Escolha a pasta "android"
   ```

2. **Aguardar sincronização do Gradle**
   - Aguarde até aparecer "Gradle sync finished"

3. **Criar/Iniciar Emulador**
   - Device Manager > Create Device > Escolha um modelo (ex: Pixel 5)
   - Ou clique no ▶️ para iniciar emulador existente

4. **Executar o App**
   - Clique no botão ▶️ Run (ou `Shift + F10`)

**Vantagens:**
- Tudo automático
- Emulador integrado
- Debug fácil
- Hot reload
- Logs visuais

---

## Opção 2: Dispositivo Físico via USB

### Pré-requisitos:
- Ativar "Opções de desenvolvedor" no celular
- Ativar "Depuração USB"
- Autorizar o computador quando solicitado

### Passos:

```bash
cd android

# Verificar conexão
~/Library/Android/sdk/platform-tools/adb devices
# Deve mostrar seu dispositivo

# Configurar Java (se necessário)
export JAVA_HOME=/usr/local/opt/openjdk@17

# Build e instalar
./gradlew installDebug
```

---

## Opção 3: Build APK Manual

Para gerar um APK e instalar manualmente:

```bash
cd android
export JAVA_HOME=/usr/local/opt/openjdk@17
./gradlew :app:assembleDebug
```

O APK será gerado em:
```
app/build/outputs/apk/debug/app-debug.apk
```

**Para instalar:**
- Via ADB: `adb install app/build/outputs/apk/debug/app-debug.apk`
- Ou transfira para o celular e instale manualmente

---

## Testes Automatizados

### Testes Unitários (ViewModels)

```bash
# Rodar todos os testes unitários
./gradlew testDebugUnitTest

# Rodar testes específicos
./gradlew testDebugUnitTest --tests "br.gov.tanamao.presentation.ui.home.HomeViewModelTest"
```

**ViewModels com cobertura de testes:**
- HomeViewModelTest
- ChatViewModelTest
- SearchViewModelTest
- WalletViewModelTest
- MunicipalityViewModelTest
- SettingsViewModelTest
- MapViewModelTest

### Testes Instrumentados (UI)

```bash
# Requer emulador ou dispositivo conectado
./gradlew connectedDebugAndroidTest
```

### Lint

```bash
./gradlew lint
```

---

## Checklist de Funcionalidades

Após instalar o app, verifique:

### Home
- [ ] Dashboard carrega
- [ ] Alertas aparecem
- [ ] KPIs exibidos
- [ ] Quick actions funcionam

### Carteira
- [ ] Aba "Ativos" mostra benefícios
- [ ] Aba "Elegíveis" lista sugestões
- [ ] Aba "Histórico" mostra timeline

### Chat IA
- [ ] Enviar mensagem funciona
- [ ] Agente responde
- [ ] Quick replies funcionam

### Perfil
- [ ] Dados carregam
- [ ] "Dinheiro Esquecido" aparece
- [ ] Exportação LGPD funciona

### Configurações
- [ ] Toggle de tema funciona (Claro/Escuro/Sistema)
- [ ] Privacidade acessível

### Navegação
- [ ] Bottom navigation funciona
- [ ] Todas as telas acessíveis

---

## Comandos Úteis

```bash
# Build completo
./gradlew build

# Limpar e rebuild
./gradlew clean build

# Ver dependências
./gradlew :app:dependencies

# Ver tasks disponíveis
./gradlew tasks
```

---

## Troubleshooting

### "No devices found"
- Conecte um dispositivo ou inicie um emulador

### "Java 17 required"
```bash
# Instalar Java 17 (veja SETUP_JAVA.md)
export JAVA_HOME=$(/usr/libexec/java_home -v 17)
```

### "SDK not found"
- Abra Android Studio > Settings > Android SDK
- Instale Android SDK 34

### Build lento
- Gradle daemon já está habilitado
- Memória já configurada em `gradle.properties`

---

## Notas

- **Backend**: Certifique-se de que está rodando em `http://localhost:8000`
- **Emulador**: Use `10.0.2.2` em vez de `localhost` para acessar o backend
- **Dispositivo Físico**: Use o IP da sua máquina na rede local

---

*Para configuração de Java, veja [SETUP_JAVA.md](SETUP_JAVA.md)*
*Para arquitetura e design, veja [docs/](docs/)*
