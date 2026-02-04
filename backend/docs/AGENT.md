# Agente Conversacional Tá na Mão

Agente de IA que **FAZ** pelos cidadãos, não apenas explica.

## Visão Geral

O agente usa Google Gemini Flash 2.0 com function calling para:
- **Consultar benefícios por CPF** (Bolsa Família, BPC, CadÚnico)
- Gerar checklists de documentos
- Buscar CRAS e farmácias próximas
- Processar receitas médicas
- Enviar pedidos de medicamentos para farmácias

### Público-Alvo

- Idosos com pouca familiaridade digital
- Pessoas de baixa renda
- Baixa escolaridade
- Querem o benefício na mão, não tutorial

---

## Endpoints

### POST /api/v1/agent/chat

Envia mensagem para o agente.

```bash
curl -X POST "http://localhost:8000/api/v1/agent/chat" \
  -H "Content-Type: application/json" \
  -d '{"message": "Quero Bolsa Família", "session_id": "opcional"}'
```

**Request**:
```json
{
  "message": "Quero Bolsa Família",
  "session_id": "abc123"
}
```

**Response**:
```json
{
  "response": "Vou preparar tudo pra você!...",
  "session_id": "abc123",
  "tools_used": ["gerar_checklist", "buscar_cras"]
}
```

### GET /api/v1/agent/welcome

Retorna mensagem de boas-vindas.

---

## Tools Disponíveis

### 1. validar_cpf

Valida CPF brasileiro.

```python
validar_cpf(cpf="529.982.247-25")
# {"valido": True, "cpf_limpo": "52998224725"}
```

### 2. buscar_cep

Busca endereço pelo CEP via ViaCEP.

```python
buscar_cep(cep="01310-100")
# {"logradouro": "Av. Paulista", "bairro": "Bela Vista", "cidade": "São Paulo", ...}
```

### 3. gerar_checklist

Gera lista de documentos para um benefício.

```python
gerar_checklist(
    beneficio="BOLSA_FAMILIA",
    situacao={"tem_filhos": True, "gestante": True}
)
# {"checklist_texto": "DOCUMENTOS NECESSÁRIOS:\n✅ RG...", "total_docs": 8}
```

**Benefícios suportados**:
- `CADASTRO_UNICO`
- `BOLSA_FAMILIA`
- `BPC_LOAS`
- `TARIFA_SOCIAL_ENERGIA`
- `FARMACIA_POPULAR`
- `DIGNIDADE_MENSTRUAL`

### 4. buscar_cras

Busca CRAS próximos do cidadão.

```python
buscar_cras(cep="04010-100", limite=3)
# {"encontrados": 2, "cras": [...], "texto_formatado": "📍 CRAS mais próximos..."}
```

**Use para**: CadÚnico, Bolsa Família, BPC, Tarifa Social

### 5. buscar_farmacia

Busca farmácias credenciadas no Farmácia Popular.

```python
buscar_farmacia(cep="04010-100", programa="FARMACIA_POPULAR")
# {"encontrados": 5, "farmacias": [...], "texto_formatado": "💊 Farmácias..."}
```

**Retorna com links de ação**:
- Link Google Maps
- Link Waze
- Link WhatsApp (click-to-chat)
- Indicador de delivery

**Use para**: Farmácia Popular, Dignidade Menstrual

### 6. processar_receita

Extrai medicamentos de receita médica.

```python
# Via texto
processar_receita(texto="Losartana 50mg, Metformina 850mg")

# Via foto (base64 ou URL)
processar_receita(imagem_base64="...")
processar_receita(imagem_url="https://...")
```

**Response**:
```json
{
  "sucesso": true,
  "medicamentos": [
    {
      "nome": "Losartana",
      "dosagem": "50mg",
      "disponivel_farmacia_popular": true,
      "gratuito": true,
      "categoria": "Hipertensão"
    }
  ],
  "todos_disponiveis": true,
  "texto_resumo": "Identifiquei 2 medicamento(s) - todos gratuitos!"
}
```

### 7. preparar_pedido

Cria pedido e envia para farmácia via WhatsApp.

```python
preparar_pedido(
    cpf="12345678900",
    nome="Maria Silva",
    telefone="11999999999",
    medicamentos=[{"nome": "Losartana", "dosagem": "50mg"}],
    farmacia_id="drogasil_vila_mariana",
    ibge_code="3550308"
)
```

**Response**:
```json
{
  "sucesso": true,
  "pedido_numero": "PED-12345",
  "status": "PENDENTE",
  "farmacia": {"nome": "Drogasil Vila Mariana", ...},
  "mensagem": "Pedido enviado! Aguarde confirmação...",
  "proximos_passos": ["Aguarde confirmação", "Você receberá WhatsApp", ...]
}
```

### 8. consultar_pedido

Consulta status de um pedido.

```python
consultar_pedido(pedido_numero="PED-12345")
```

**Response**:
```json
{
  "encontrado": true,
  "pedido": {"numero": "PED-12345", "status": "PRONTO", ...},
  "status_texto": "PRONTO! Seus medicamentos estão esperando."
}
```

### 9. listar_pedidos_cidadao

Lista pedidos de um cidadão.

```python
listar_pedidos_cidadao(cpf="12345678900", apenas_ativos=True)
```

### 10. consultar_beneficio

Consulta benefícios que o cidadão **já recebe** por CPF.

```python
consultar_beneficio(cpf="52998224725")
```

**Response**:
```json
{
  "encontrado": true,
  "cpf_masked": "***982.247-**",
  "nome": "Maria Silva",
  "uf": "SP",
  "beneficios": {
    "bolsa_familia": {
      "ativo": true,
      "valor": 600.00,
      "parcela_mes": "2025-01",
      "data_referencia": "2025-01-20"
    },
    "bpc": {"ativo": false},
    "cadunico": {
      "ativo": true,
      "faixa_renda": "EXTREMA_POBREZA",
      "ultima_atualizacao": "2024-10-15"
    }
  },
  "texto_resumo": "BOLSA FAMILIA: R$ 600,00\n  Parcela: 2025-01\nCADUNICO: EXTREMA_POBREZA",
  "mensagem": "Encontrei! Beneficios ativos: Bolsa Familia (R$ 600,00), CadUnico ativo."
}
```

**Use quando**: cidadão perguntar "meu bolsa família tá vindo?", "quanto eu recebo?", "to cadastrado?"

**Fonte de dados**: Portal da Transparência (dados indexados no banco local)

### 11. verificar_elegibilidade

Verifica se cidadão pode ter direito a um benefício específico.

```python
verificar_elegibilidade(cpf="12345678900", programa="BPC")
```

**Response (já recebe)**:
```json
{
  "elegivel": true,
  "ja_recebe": true,
  "motivo": "Ja recebe BPC (IDOSO): R$ 1412.00",
  "proximos_passos": "Manter inscricao no CadUnico atualizada."
}
```

**Response (pode ser elegível)**:
```json
{
  "elegivel": null,
  "ja_recebe": false,
  "motivo": "Nao recebe BPC atualmente.",
  "proximos_passos": "1. Fazer inscricao no CadUnico\n2. Agendar pericia no INSS\n3. Comprovar renda..."
}
```

**Programas suportados**:
- `BOLSA_FAMILIA`
- `BPC`
- `FARMACIA_POPULAR`
- `DIGNIDADE_MENSTRUAL`
- `TSEE` (Tarifa Social de Energia)
- `CADUNICO`

---

## Fluxo de Pedido de Medicamentos

Estilo "iFood" para Farmácia Popular:

```
CIDADÃO                         AGENTE                          FARMÁCIA
   |                               |                               |
   |--- "Quero remédio" ---------->|                               |
   |                               |                               |
   |<-- "Qual remédio? Foto       |                               |
   |    ou digita o nome" --------|                               |
   |                               |                               |
   |--- "Losartana 50mg" --------->|                               |
   |                               |--- processar_receita -------->|
   |                               |                               |
   |<-- "Entendi! Losartana       |                               |
   |    GRATUITO. Envio pedido?" --|                               |
   |                               |                               |
   |--- "Sim" -------------------->|                               |
   |                               |--- buscar_farmacia ---------->|
   |<-- "Escolha a farmácia" ------|                               |
   |                               |                               |
   |--- "A primeira" ------------->|                               |
   |                               |--- preparar_pedido ---------->|
   |                               |                               |
   |                               |--- WhatsApp: "Pedido PED-123 |
   |                               |    Responda SIM ou NAO" ----->|
   |                               |                               |
   |<-- "Pedido enviado!          |                               |
   |    Aguarde confirmação..." ---|                               |
   |                               |                               |
   |                               |<-- "SIM PED-123" -------------|
   |                               |                               |
   |<-- WhatsApp: "PRONTO!        |                               |
   |    Vá buscar na Drogasil" ---|                               |
```

---

## Webhook WhatsApp

### POST /api/v1/webhook/whatsapp

Recebe respostas das farmácias via Twilio.

**Quando farmácia responde**:
- `SIM PED-12345` → Status → PRONTO, notifica cidadão
- `NAO PED-12345` → Status → CANCELADO, notifica cidadão

**Request (Twilio)**:
```
POST /api/v1/webhook/whatsapp
Content-Type: application/x-www-form-urlencoded

From=whatsapp:+5511999999999
Body=SIM PED-12345
MessageSid=SM...
```

**Response (TwiML)**:
```xml
<?xml version="1.0" encoding="UTF-8"?>
<Response>
    <Message>Obrigado! Pedido PED-12345 confirmado.</Message>
</Response>
```

### GET /api/v1/webhook/whatsapp

Verificação do webhook.

### POST /api/v1/webhook/whatsapp/status

Recebe atualizações de status de mensagens (delivered, read, failed).

---

## Configuração

### Variáveis de Ambiente

```env
# Gemini
GOOGLE_API_KEY=AIza...
AGENT_MODEL=gemini-2.0-flash-exp

# Twilio WhatsApp
TWILIO_ACCOUNT_SID=ACxxxxxxxx
TWILIO_AUTH_TOKEN=xxxxxxxx
TWILIO_WHATSAPP_FROM=whatsapp:+14155238886
TWILIO_WEBHOOK_URL=https://seu-dominio.com/api/v1/webhook/whatsapp
```

### Twilio Sandbox (Desenvolvimento)

1. Acesse [Twilio Console](https://console.twilio.com/us1/develop/sms/try-it-out/whatsapp-learn)
2. Envie mensagem de opt-in para o número sandbox
3. Configure webhook URL (use ngrok para localhost)
4. Teste enviando mensagens

### ngrok para Desenvolvimento

```bash
ngrok http 8000
# Use a URL https://xxx.ngrok.io/api/v1/webhook/whatsapp no Twilio
```

---

## Modelo de Dados: Pedido

```sql
CREATE TABLE pedidos (
    id VARCHAR(36) PRIMARY KEY,
    numero VARCHAR(10) UNIQUE,        -- PED-12345
    cpf_cidadao VARCHAR(11) NOT NULL,
    nome_cidadao VARCHAR(200),
    telefone_cidadao VARCHAR(15),
    farmacia_id VARCHAR(50) NOT NULL,
    farmacia_nome VARCHAR(200),
    farmacia_whatsapp VARCHAR(15),
    medicamentos JSONB NOT NULL,       -- [{nome, dosagem, quantidade}]
    receita_url TEXT,
    status VARCHAR(20) DEFAULT 'PENDENTE',
    criado_em TIMESTAMP,
    atualizado_em TIMESTAMP,
    confirmado_em TIMESTAMP,
    pronto_em TIMESTAMP,
    retirado_em TIMESTAMP,
    twilio_sid_farmacia VARCHAR(50),
    twilio_sid_cidadao VARCHAR(50),
    observacoes TEXT
);
```

### Status do Pedido

| Status | Descrição |
|--------|-----------|
| `PENDENTE` | Aguardando confirmação da farmácia |
| `CONFIRMADO` | Farmácia confirmou, preparando |
| `PRONTO` | Medicamentos prontos para retirada |
| `RETIRADO` | Cidadão retirou |
| `CANCELADO` | Cancelado (falta estoque, etc) |
| `EXPIRADO` | Não retirado no prazo |

---

## Medicamentos Farmácia Popular

Lista em `data/medicamentos_farmacia_popular.json`:

### Categorias Gratuitas

| Categoria | Exemplos |
|-----------|----------|
| Hipertensão | Losartana, Atenolol, Captopril |
| Diabetes | Metformina, Glibenclamida, Insulina |
| Asma | Salbutamol, Budesonida, Formoterol |
| Parkinson | Levodopa + Carbidopa |
| Osteoporose | Alendronato |
| Glaucoma | Maleato de Timolol |
| Anticoncepcional | Etinilestradiol + Levonorgestrel |
| Colesterol | Sinvastatina |

### Com Desconto

| Categoria | Desconto |
|-----------|----------|
| Incontinência (Oxibutinina) | 90% |
| Fraldas Geriátricas | 40% |

---

## Arquitetura

```
app/agent/
├── agent.py              # Classe TaNaMaoAgent (13 tools)
├── prompts.py            # System prompt e exemplos
├── mcp/                  # MCP Wrappers (Model Context Protocol)
│   ├── __init__.py       # Exports: init_mcp, mcp_manager, wrappers
│   ├── base.py           # MCPClient, MCPManager, init_mcp
│   ├── brasil_api.py     # BrasilAPIMCP (CEP, CNPJ, DDD)
│   ├── google_maps.py    # GoogleMapsMCP (Places, Geocoding)
│   └── pdf_ocr.py        # PDFOcrMCP (OCR de receitas)
└── tools/
    ├── validar_cpf.py
    ├── buscar_cep.py         # MCP: BrasilAPIMCP + Fallback: ViaCEP
    ├── consultar_api.py
    ├── checklist.py
    ├── buscar_cras.py
    ├── buscar_farmacia.py    # MCP: GoogleMapsMCP + Fallback: Google Places
    ├── processar_receita.py  # MCP: PDFOcrMCP + Fallback: Gemini Vision
    ├── enviar_whatsapp.py    # Twilio
    ├── preparar_pedido.py    # Orquestração
    └── consultar_beneficio.py # Consulta por CPF (Sprint 5)

app/routers/
├── agent.py              # POST /agent/chat
└── webhook.py            # POST /webhook/whatsapp

app/models/
├── pedido.py             # Modelo SQLAlchemy - Pedidos
└── beneficiario.py       # Modelo SQLAlchemy - Beneficiários (Sprint 5)

app/jobs/
├── ingest_bolsa_familia.py
├── ingest_bpc_real.py
├── ...
└── indexar_beneficiarios.py  # Indexa dados individuais (Sprint 5)

data/
├── medicamentos_farmacia_popular.json
├── documentos_por_beneficio.json
├── cras_exemplo.json
└── farmacias_exemplo.json
```

---

## Integração MCP (Model Context Protocol)

O agente utiliza MCPs para integração padronizada com serviços externos.

### Tools com MCP

| Tool | MCP Primário | Fallback | Descrição |
|------|--------------|----------|-----------|
| `buscar_cep` | BrasilAPIMCP | ViaCEP HTTP | Busca endereço por CEP |
| `buscar_farmacia` | GoogleMapsMCP | Google Places API | Busca farmácias próximas |
| `processar_receita` | PDFOcrMCP | Gemini Vision | OCR de receitas médicas |

### Como Funciona

1. **Startup**: MCPs são inicializados em `main.py` via `init_mcp()`
2. **Tool Call**: Cada tool tenta usar o MCP primeiro
3. **Fallback**: Se MCP falhar, usa API direta (HTTP)

### Configuração

```bash
# .env
MCP_ENABLED=true          # Ativar/desativar MCPs
MCP_CONFIG_PATH=.mcp.json # Arquivo de configuração
MCP_TIMEOUT=30000         # Timeout em ms
```

### Exemplo de Uso em Tool

```python
from app.agent.mcp import mcp_manager, BrasilAPIMCP

async def buscar_cep(cep: str) -> dict:
    # Tenta MCP primeiro
    wrapper = mcp_manager.get_wrapper("brasil-api")
    if wrapper and isinstance(wrapper, BrasilAPIMCP):
        resultado = await wrapper.buscar_cep(cep)
        if resultado:
            return resultado.to_dict()

    # Fallback para API direta
    return await _buscar_cep_viacep(cep)
```

Veja [MCP_SETUP.md](../../docs/MCP_SETUP.md) para documentação completa.

---

## Exemplos de Conversa

### Solicitar Bolsa Família

```
Cidadão: Quero Bolsa Família
Agente: [gerar_checklist] Preparei os documentos!
        ✅ RG de todos da casa
        ✅ CPF de todos
        ✅ Comprovante de endereço
        ...
        Me fala seu CEP que mostro o CRAS perto.

Cidadão: 04010-100
Agente: [buscar_cras] Encontrei!
        📍 CRAS Vila Mariana - 1,2km
        📞 (11) 3333-4444
        🗺️ Ver no mapa: [link]
```

### Consultar Benefícios por CPF

```
Cidadão: Meu Bolsa Família tá vindo?
Agente: Me fala seu CPF que eu consulto pra você.

Cidadão: 529.982.247-25
Agente: [consultar_beneficio] Achei!
        ✅ BOLSA FAMÍLIA: R$ 600,00
           Parcela: Janeiro/2025
        ✅ CADÚNICO: Ativo
           Faixa: Extrema pobreza

        Quer saber mais alguma coisa?
```

### Pedir Medicamentos

```
Cidadão: Quero meus remédios
Agente: Pode enviar foto da receita ou digitar o nome?

Cidadão: Losartana 50mg
Agente: [processar_receita] Entendi!
        - Losartana 50mg - GRATUITO!
        Quer que envie pra farmácia preparar?

Cidadão: Sim
Agente: [buscar_farmacia] Escolha:
        1. Drogasil Vila Mariana
        2. Droga Raia Paraíso

Cidadão: 1
Agente: Me passa seu nome, CPF e WhatsApp.

Cidadão: Maria, 12345678900, 11999999999
Agente: [preparar_pedido] PEDIDO ENVIADO!
        Número: PED-12345
        Você recebe WhatsApp quando estiver pronto!
```

---

## Fluxo de Consulta por CPF (Sprint 5)

```
CIDADÃO                         AGENTE
   |                               |
   |--- "Meu Bolsa Família        |
   |    tá vindo?" --------------->|
   |                               |
   |<-- "Me fala seu CPF          |
   |    que eu consulto" ----------|
   |                               |
   |--- "529.982.247-25" --------->|
   |                               |--- consultar_beneficio(cpf)
   |                               |
   |<-- "Achei! Você recebe:      |
   |    BOLSA FAMÍLIA: R$600      |
   |    Parcela: Janeiro/2025     |
   |    CADÚNICO: Ativo" ----------|
   |                               |
   |--- "E o BPC, tenho direito?">|
   |                               |--- verificar_elegibilidade(cpf, "BPC")
   |                               |
   |<-- "Você não recebe BPC.     |
   |    Para ter direito:         |
   |    1. Ter 65+ anos OU PCD    |
   |    2. Renda até 1/4 salário  |
   |    Quer que eu prepare os    |
   |    documentos?" --------------|
```

### Modelo de Dados: Beneficiário

```sql
CREATE TABLE beneficiarios (
    id SERIAL PRIMARY KEY,
    cpf_hash VARCHAR(64) UNIQUE NOT NULL,  -- SHA256 do CPF
    cpf_masked VARCHAR(14),                 -- ***456.789-**
    nis VARCHAR(11),
    nome VARCHAR(200),
    ibge_code VARCHAR(7) REFERENCES municipalities(ibge_code),
    uf VARCHAR(2),

    -- Bolsa Família
    bf_ativo BOOLEAN DEFAULT FALSE,
    bf_valor NUMERIC(10,2),
    bf_parcela_mes VARCHAR(7),              -- YYYY-MM
    bf_data_referencia DATE,

    -- BPC/LOAS
    bpc_ativo BOOLEAN DEFAULT FALSE,
    bpc_valor NUMERIC(10,2),
    bpc_tipo VARCHAR(20),                   -- IDOSO, PCD
    bpc_data_referencia DATE,

    -- CadÚnico
    cadunico_ativo BOOLEAN DEFAULT FALSE,
    cadunico_data_atualizacao DATE,
    cadunico_faixa_renda VARCHAR(50),       -- EXTREMA_POBREZA, POBREZA, BAIXA_RENDA

    -- Metadata
    criado_em TIMESTAMP,
    atualizado_em TIMESTAMP,
    fonte VARCHAR(50)
);
```

### Indexação de Dados

```bash
# Indexar Bolsa Família (1 mês)
python -m app.jobs.indexar_beneficiarios bolsa_familia 2024 10

# Indexar BPC (1 mês)
python -m app.jobs.indexar_beneficiarios bpc 2024 10

# Indexar todos
python -m app.jobs.indexar_beneficiarios all 2024 10
```

**Volume de dados**:
- Bolsa Família: ~21M registros/mês
- BPC: ~6M registros/mês
- Total: ~27M registros (estimado ~3GB)

**Privacidade**:
- CPF armazenado como hash SHA256 (não reversível)
- Consulta: usuário informa CPF → calcula hash → busca no banco
- Dados são públicos (Portal da Transparência)

---

## Sprints Concluídos

| Sprint | Descrição | Status |
|--------|-----------|--------|
| 1 | Checklist de Documentos | ✅ Completo |
| 2 | CRAS + Farmácias | ✅ Completo |
| 3 | Links de Ação (Maps/WhatsApp) | ✅ Completo |
| 4 | Preparação de Pedido (iFood-style) | ✅ Completo |
| 5 | Consulta Status por CPF | ✅ Completo |
| 6 | App Android (Modo Claro + Home) | ✅ Completo |

---

## Sprint 6: App Android - Modo Claro e Home Screen

### Implementações

1. **Modo Claro Automático**
   - App segue tema do sistema (claro/escuro)
   - Anteriormente era apenas dark mode
   - Arquivo: `Theme.kt` - `isSystemInDarkTheme()`

2. **Home Screen Redesenhada**
   - Removido: "Indicadores Nacionais" (foco em admin/governo)
   - Adicionado: Conteúdo para cidadãos

**Novas Seções:**

| Seção | Descrição |
|-------|-----------|
| `NextPaymentsSection` | Próximos pagamentos com countdown |
| `NearbyServicesSection` | CRAS e Farmácias próximas |

**Exemplo NextPaymentsSection:**
```
💰 PRÓXIMOS PAGAMENTOS
┌────────────────────────────────────┐
│ 🟠 Bolsa Família                   │
│ R$ 600,00           em 5 dias      │
└────────────────────────────────────┘
```

**Exemplo NearbyServicesSection:**
```
📍 SERVIÇOS PERTO DE VOCÊ
┌─────────────────┐ ┌─────────────────┐
│ 🏢 CRAS         │ │ 💊 Farmácias    │
│ Encontrar →     │ │ Encontrar →     │
└─────────────────┘ └─────────────────┘
```

### APK Atualizado

- **Localização:** `/Users/brunoteixeira/Downloads/TaNaMao-debug.apk`
- **Tamanho:** 23MB
- **Versão:** Debug com Sprint 6

---

## Sprint 7: Arquitetura V2 - Orchestrator + Sub-agents

### Nova Arquitetura

```
┌─────────────────────────────────────────────────────────────┐
│                    ORQUESTRADOR PRINCIPAL                    │
│         (Classifica intenção, roteia para sub-agente)       │
└─────────────────────────────────────────────────────────────┘
                              │
        ┌─────────────────────┼─────────────────────┐
        ▼                     ▼                     ▼
┌───────────────┐    ┌───────────────┐    ┌───────────────────┐
│  SUB-AGENT    │    │  SUB-AGENT    │    │    SUB-AGENT      │
│  Benefícios   │    │   Farmácia    │    │  Documentação     │
│               │    │               │    │                   │
│ - consultar   │    │ - processar   │    │ - gerar_checklist │
│ - verificar   │    │   receita     │    │ - buscar_cras     │
│ - elegibilid. │    │ - preparar    │    │ - orientar        │
└───────────────┘    └───────────────┘    └───────────────────┘
```

### Formato A2UI (Agent-to-User Interface)

Respostas estruturadas com componentes renderizáveis:

```json
{
  "text": "Encontrei 3 farmácias perto de você!",
  "ui_components": [
    {
      "type": "pharmacy_card",
      "data": {
        "name": "Drogasil Vila Mariana",
        "address": "Rua X, 123",
        "distance": "850m"
      }
    }
  ],
  "suggested_actions": [
    {"label": "Enviar pedido", "action_type": "send_message", "payload": "enviar para farmácia 1"}
  ]
}
```

### Endpoints V2

#### POST /api/v1/agent/v2/start

Inicia conversa com resposta A2UI.

```bash
curl -X POST "http://localhost:8000/api/v1/agent/v2/start"
```

#### POST /api/v1/agent/v2/chat

Chat com resposta estruturada.

```json
{
  "message": "quero remédios",
  "session_id": "abc123",
  "location": {
    "latitude": -23.5505,
    "longitude": -46.6333,
    "accuracy": 10
  }
}
```

**Response**:
```json
{
  "text": "Manda uma foto da receita ou digita o nome dos remédios",
  "session_id": "abc123",
  "ui_components": [],
  "suggested_actions": [
    {"label": "Tirar foto", "action_type": "camera", "payload": "prescription"},
    {"label": "Digitar", "action_type": "send_message", "payload": "digitar nome"}
  ],
  "flow_state": "pharmacy:receita",
  "tools_used": []
}
```

### WhatsApp Chat (Novo!)

#### POST /api/v1/webhook/whatsapp/chat

Endpoint para cidadãos conversarem via WhatsApp com o agente.

**Fluxo**:
1. Cidadão envia mensagem no WhatsApp
2. Twilio envia para nosso webhook
3. Orchestrator processa
4. Resposta A2UI é convertida para texto WhatsApp
5. TwiML é retornado para Twilio

**Request (Twilio)**:
```
POST /api/v1/webhook/whatsapp/chat
Content-Type: application/x-www-form-urlencoded

From=whatsapp:+5511999999999
Body=quero pedir remédios
ProfileName=Maria Silva
Latitude=-23.5505
Longitude=-46.6333
```

**Response (TwiML)**:
```xml
<?xml version="1.0" encoding="UTF-8"?>
<Response>
    <Message>Manda uma foto da receita ou digita o nome dos remédios...

*O que você quer fazer?*
1. Tirar foto
2. Digitar nome

_Digite o número ou o que você quer fazer_</Message>
</Response>
```

### Session Management

#### In-Memory (Desenvolvimento)
```python
from app.agent.context import session_manager

# Obtém ou cria sessão
context = session_manager.get_or_create("session-id")

# Reseta sessão
session_manager.reset("session-id")
```

#### Redis (Produção)

Sessões são automaticamente persistidas no Redis quando `ENVIRONMENT=production`.

```python
# Configuração em .env
ENVIRONMENT=production
REDIS_URL=redis://localhost:6379/0
```

**Características**:
- TTL de 24 horas
- Serialização automática via Pydantic
- Fallback para memória se Redis falhar

### Estrutura de Arquivos V2

```
app/agent/
├── orchestrator.py          # Orquestrador principal
├── intent_classifier.py     # Classificação de intenção
├── context.py               # Contexto e SessionManager
├── session_redis.py         # Redis SessionManager
├── response_types.py        # Types A2UI
├── whatsapp_formatter.py    # Converte A2UI → TwiML
└── subagents/
    ├── __init__.py
    ├── farmacia_agent.py    # Fluxo de medicamentos
    ├── beneficio_agent.py   # Consulta de benefícios
    └── documentacao_agent.py # Checklist + CRAS
```

### Geolocalização

O sistema suporta geolocalização para:
- Buscar farmácias próximas (Google Places API)
- Buscar CRAS próximos
- Calcular distâncias

**Frontend**: Hook `useGeolocation` captura GPS do browser
**Backend**: `CitizenProfile.update_from_geolocation()` armazena

### Testes

```bash
# Rodar todos os testes
pytest backend/tests/

# Testes de sub-agents
pytest backend/tests/test_subagents.py -v

# Testes do orchestrator
pytest backend/tests/test_orchestrator.py -v
```

---

## Sprint 8: Acessibilidade e Linguagem Simples

### Público-Alvo

O app é para **cidadãos de baixa renda e baixa escolaridade**. Toda interface usa linguagem simples.

### Glossário de Substituições

| Termo Técnico | Linguagem Simples |
|---------------|-------------------|
| Verificar elegibilidade | Tenho direito? / Posso receber? |
| CRAS | Posto de assistência social |
| BPC/LOAS | Ajuda para idosos e pessoas com deficiência |
| CadÚnico | Cadastro do governo para receber ajudas |
| TSEE | Desconto na conta de luz |
| Renda per capita | Dinheiro que cada pessoa da casa ganha |
| PCD | Pessoa com deficiência |
| Laudo médico | Papel do médico |
| Farmácia credenciada | Farmácia que dá remédio de graça |

### Botões Contextuais

O orchestrator agora adapta os botões sugeridos baseado no contexto:

**Após "Tenho direito?"**:
- Bolsa Família
- Remédio de graça (Farmácia Popular)
- Ajuda para idosos (BPC)
- Desconto na luz (Tarifa Social)

**Durante fluxo Farmácia Popular**:
- Encontrar Farmácia (nunca CRAS)
- Enviar receita

**Arquivo**: `orchestrator.py` linha 324-361

### Endpoints Nearby

Novos endpoints REST para o mapa do cidadão:

```bash
# Farmácias próximas
GET /api/v1/nearby/farmacias?latitude=-23.55&longitude=-46.63

# CRAS próximos
GET /api/v1/nearby/cras?latitude=-23.55&longitude=-46.63
```

Veja documentação completa em `docs/API.md` seção "Serviços Próximos".

---

## Sprint 9: Entregador de Direitos - 3 Pilares

Implementação da visão estratégica consolidada: transformar o Tá na Mão de "tutorial de cadastro" para "entregador de direitos".

### Pilar 1: Dinheiro Esquecido (R$ 42 bilhões disponíveis)

Novas tools para ajudar cidadãos a resgatar dinheiro esquecido:

| Tool | Descrição |
|------|-----------|
| `consultar_dinheiro_esquecido` | Mostra todos os tipos de dinheiro esquecido |
| `guia_pis_pasep` | Passo-a-passo para PIS/PASEP (R$ 26 bi) |
| `guia_svr` | Passo-a-passo para Valores a Receber BC (R$ 8-10 bi) |
| `guia_fgts` | Passo-a-passo para FGTS (R$ 7,8 bi) |
| `verificar_dinheiro_por_perfil` | Triagem baseada no perfil do cidadão |

**Exemplo de uso:**
```
Usuário: "Tenho dinheiro pra receber?"
Agente: Usa consultar_dinheiro_esquecido → mostra PIS/PASEP, SVR e FGTS
```

### Pilar 2: Copiloto de Navegação

Novas tools para consolidar dados e alertar proativamente:

| Tool | Descrição |
|------|-----------|
| `meus_dados` | Visão consolidada: benefícios, valores, alertas |
| `gerar_alertas_beneficios` | Alertas proativos: CadÚnico desatualizado, prazos |

**Funcionalidades de meus_dados:**
- Lista todos os benefícios ativos
- Mostra valores recebidos mensalmente
- Gera alertas automáticos (CadÚnico >2 anos, pagamento atrasado)
- Sugere benefícios que o cidadão pode ter direito
- Indica oportunidade de dinheiro esquecido

**Exemplo de uso:**
```
Usuário: "O que eu recebo?"
Agente: Usa meus_dados → mostra Bolsa Família R$600 + alerta CadÚnico desatualizado
```

### Pilar 3: Ponte CRAS ↔ Digital

Novas tools para preparar atendimento presencial:

| Tool | Descrição |
|------|-----------|
| `preparar_pre_atendimento_cras` | Checklist personalizada de documentos |
| `gerar_formulario_pre_cras` | Formulário pré-preenchido para levar |

**Funcionalidades:**
- Gera checklist personalizada baseada na situação
- Calcula tempo estimado de atendimento
- Dicas para o atendimento (chegar cedo, prioridade, etc)
- Verifica elegibilidade preliminar
- Reduz tempo de atendimento de 2h para 30min

**Exemplo de uso:**
```
Usuário: "Quero fazer Bolsa Família"
Agente: Usa preparar_pre_atendimento_cras → gera checklist + dicas
Usuário: [informa dados da família]
Agente: Usa gerar_formulario_pre_cras → gera formulário pronto para levar
```

### Total de Tools

- **Sprint 8**: 16 tools
- **Sprint 9**: 25 tools (+9 novas)

---

## Sprint 10: Carteira de Direitos

### Novas Tools de Triagem

#### triagem_universal

Triagem multi-benefício consolidada que avalia elegibilidade para todos os programas de uma vez.

```python
triagem_universal(
    renda_familiar=800.00,
    pessoas_domicilio=4,
    tem_idoso_65=False,
    tem_pcd=False,
    tem_crianca=True,
    tem_gestante=False,
    inscrito_cadunico=True,
    cpf="12345678900"  # opcional
)
```

**Response**:
```json
{
  "sucesso": true,
  "total_beneficios_elegiveis": 3,
  "renda_per_capita": 200.00,
  "beneficios": [
    {
      "programa": "BOLSA_FAMILIA",
      "nome": "Bolsa Família",
      "elegivel": true,
      "motivo": "Renda per capita R$200 está abaixo do limite de R$218",
      "valor_estimado": 600.00,
      "proximos_passos": ["Comparecer ao CRAS", "Atualizar CadÚnico"]
    },
    {
      "programa": "TSEE",
      "nome": "Tarifa Social de Energia",
      "elegivel": true,
      "motivo": "Inscrito no CadÚnico com renda até meio salário mínimo",
      "valor_estimado": 50.00,
      "proximos_passos": ["Solicitar na distribuidora de energia"]
    },
    {
      "programa": "AUXILIO_GAS",
      "nome": "Auxílio Gás",
      "elegivel": true,
      "motivo": "Inscrito no CadÚnico",
      "valor_estimado": 104.00,
      "proximos_passos": ["Benefício automático via Bolsa Família"]
    }
  ],
  "nao_elegiveis": [
    {
      "programa": "BPC",
      "nome": "BPC/LOAS",
      "elegivel": false,
      "motivo": "Requer pessoa idosa (65+) ou com deficiência no domicílio"
    }
  ],
  "texto_resumo": "Você pode ter direito a 3 benefícios! Valor estimado: R$ 754/mês"
}
```

**Benefícios avaliados**:
- Bolsa Família
- BPC/LOAS (Idoso e PCD)
- Tarifa Social de Energia (TSEE)
- Auxílio Gás
- Farmácia Popular
- Garantia-Safra
- Seguro Defeso
- Minha Casa Minha Vida

#### gerar_carta_encaminhamento

Gera carta de encaminhamento em PDF com QR Code para validação no CRAS.

```python
gerar_carta_encaminhamento(
    cpf="12345678900",
    nome="Maria da Silva",
    data_nascimento="1985-03-15",
    endereco="Rua das Flores, 123",
    cep="08471-000",
    telefone="11999991234",
    composicao_familiar=[
        {"nome": "Maria da Silva", "idade": 40, "parentesco": "Responsável"},
        {"nome": "João da Silva", "idade": 42, "parentesco": "Cônjuge"},
        {"nome": "Ana da Silva", "idade": 12, "parentesco": "Filha"}
    ],
    renda_familiar=800.00,
    beneficios_solicitados=["BOLSA_FAMILIA", "TSEE"],
    documentos_conferidos=["RG", "CPF", "COMPROVANTE_RESIDENCIA"],
    ibge_code="3550308"  # para buscar CRAS
)
```

**Response**:
```json
{
  "sucesso": true,
  "codigo_validacao": "TNM-2026-ABC123",
  "validade": "2026-02-28",
  "pdf_base64": "JVBERi0xLjQK...",
  "qr_code_base64": "iVBORw0KGgo...",
  "link_validacao": "https://api.tanamao.app/carta/TNM-2026-ABC123",
  "cras_sugerido": {
    "nome": "CRAS Cidade Tiradentes I",
    "endereco": "Rua Inácio Monteiro, 6.900",
    "telefone": "(11) 2286-1234",
    "horario": "Seg-Sex 8h-17h"
  },
  "documentos_faltantes": ["CERTIDAO_NASCIMENTO_FILHOS"],
  "tempo_atendimento_estimado": "30 minutos",
  "texto_instrucoes": "Leve esta carta impressa ou no celular ao CRAS. O atendente pode escanear o QR Code para ver seus dados."
}
```

**Conteúdo da Carta PDF**:
1. Cabeçalho com logo e código de validação
2. Dados do cidadão (nome, CPF mascarado, endereço)
3. Composição familiar
4. Renda declarada e per capita
5. Benefícios solicitados com elegibilidade estimada
6. Checklist de documentos (conferidos e faltantes)
7. CRAS de destino
8. QR Code para validação online
9. Aviso para atendente

### Regras de Elegibilidade

Cada benefício tem seu módulo de regras em `app/agent/tools/regras_elegibilidade/`:

| Arquivo | Benefício | Critérios Principais |
|---------|-----------|---------------------|
| `bolsa_familia.py` | Bolsa Família | Renda per capita ≤ R$218 + CadÚnico |
| `bpc.py` | BPC/LOAS | Idoso 65+ ou PCD + renda ≤ 1/4 SM |
| `tsee.py` | Tarifa Social | CadÚnico + renda ≤ 1/2 SM |
| `auxilio_gas.py` | Auxílio Gás | CadÚnico + Bolsa Família ou renda ≤ 1/2 SM |
| `farmacia_popular.py` | Farmácia Popular | Receita médica (CadÚnico = prioridade) |
| `garantia_safra.py` | Garantia-Safra | Agricultor familiar semiárido |
| `seguro_defeso.py` | Seguro Defeso | Pescador artesanal + período defeso |
| `mcmv.py` | Minha Casa Minha Vida | Renda até R$8.600 (faixa 3) |

### Fluxo EligibilityWizard

```
CIDADÃO                         WIZARD                          AGENTE
   |                               |                               |
   |--- Clica FAB "Descobrir" ---->|                               |
   |                               |                               |
   |<-- Etapa 1: Dados Básicos ----|                               |
   |    (CPF opcional, cidade)     |                               |
   |                               |                               |
   |--- Preenche dados ----------->|                               |
   |                               |                               |
   |<-- Etapa 2: Família ----------|                               |
   |    (quantas pessoas, idades)  |                               |
   |                               |                               |
   |--- Preenche família --------->|                               |
   |                               |                               |
   |<-- Etapa 3: Renda ------------|                               |
   |    (slider de renda)          |                               |
   |                               |                               |
   |--- Seleciona renda ---------->|                               |
   |                               |                               |
   |<-- Etapa 4: Especial ---------|                               |
   |    (idoso, PCD, gestante)     |                               |
   |                               |                               |
   |--- Marca condições ---------->|                               |
   |                               |--- triagem_universal -------->|
   |                               |                               |
   |<-- RESULTADO: Carteira -------|<-- Benefícios elegíveis ------|
   |    de Direitos                |                               |
   |                               |                               |
   |--- "Gerar Carta" ------------>|                               |
   |                               |--- gerar_carta_encaminhamento>|
   |                               |                               |
   |<-- PDF + QR Code -------------|<-- Carta gerada --------------|
```

### Endpoints da Carta

Veja documentação completa em `docs/API.md` seção "Carta de Encaminhamento".

| Endpoint | Método | Descrição |
|----------|--------|-----------|
| `/api/v1/carta/gerar` | POST | Gera carta com PDF |
| `/api/v1/carta/{codigo}` | GET | Consulta carta |
| `/api/v1/carta/{codigo}/pdf` | GET | Download PDF |
| `/api/v1/carta/{codigo}/validar` | POST | Valida QR Code |

### Total de Tools Atualizado

| Sprint | Tools | Total |
|--------|-------|-------|
| Sprint 8 | 16 | 16 |
| Sprint 9 | +9 | 25 |
| Sprint 10 | +2 | **27** |

---

## Sprint 11: Crédito Imobiliário (MCMV)

### Módulo MCMV Reescrito

O módulo `mcmv.py` foi completamente reescrito com 7 critérios de elegibilidade:

1. **Renda Familiar** - Faixas atualizadas 2026
2. **Situação de Moradia** - Aluguel, cedido, rua, área de risco
3. **Propriedade Atual** - Não pode ter imóvel em nome
4. **Grupos Prioritários** - Situação de rua, violência doméstica, área de risco
5. **Cadastro Único** - Requerido para Faixa 1
6. **Localização** - Para verificar programas locais
7. **Beneficiários BPC/Bolsa Família** - Imóvel 100% gratuito na Faixa 1

#### Faixas de Renda 2026

| Faixa | Renda Familiar | Subsídio | Imóvel Máximo |
|-------|----------------|----------|---------------|
| Faixa 1 | Até R$ 2.850 | Até 95% | R$ 190.000 |
| Faixa 2 | R$ 2.850 - R$ 4.700 | Até 80% | R$ 264.000 |
| Faixa 3 | R$ 4.700 - R$ 8.600 | Até 50% | R$ 350.000 |
| **Faixa 4** (Nova) | R$ 8.600 - R$ 12.000 | Até 30% | R$ 500.000 |

**Benefício especial**: Beneficiários de BPC ou Bolsa Família na Faixa 1 podem receber imóvel **100% gratuito**.

### Novas Tools

#### 12. simulador_mcmv

Simulador de financiamento habitacional MCMV.

**Funções disponíveis:**

| Função | Descrição |
|--------|-----------|
| `simular_financiamento_mcmv()` | Simulação completa com subsídio, parcela e economia |
| `simular_reforma()` | Programa Reforma Casa Brasil |
| `comparar_modalidades()` | Compara aquisição vs reforma vs locação |

**Exemplo de uso:**
```python
simular_financiamento_mcmv(
    renda_familiar=3000.00,
    valor_imovel=180000.00,
    entrada=10000.00,
    prazo_meses=420,  # 35 anos
    sistema="SAC",     # SAC ou PRICE
    uf="SP"
)
```

**Response:**
```json
{
  "sucesso": true,
  "faixa": 2,
  "valor_imovel": 180000.00,
  "entrada": 10000.00,
  "valor_financiado": 170000.00,
  "subsidio_estimado": 47500.00,
  "valor_final_financiado": 122500.00,
  "primeira_parcela": 850.00,
  "ultima_parcela": 320.00,
  "custo_total": 198000.00,
  "economia_vs_aluguel": 180000.00,
  "taxa_juros_anual": 7.66,
  "sistema": "SAC",
  "prazo_anos": 35
}
```

**Comparar modalidades:**
```python
comparar_modalidades(
    renda_familiar=3000.00,
    valor_imovel=180000.00,
    aluguel_atual=1200.00
)
```

**Response:**
```json
{
  "aquisicao": {
    "parcela_media": 585.00,
    "custo_total_35_anos": 245700.00,
    "patrimonio_final": 180000.00
  },
  "reforma": {
    "elegivel": true,
    "valor_maximo": 50000.00,
    "parcela_estimada": 300.00
  },
  "locacao": {
    "custo_mensal": 1200.00,
    "custo_total_35_anos": 504000.00,
    "patrimonio_final": 0
  },
  "recomendacao": "Aquisição via MCMV - economia de R$258.300 vs locação"
}
```

#### 13. carta_habitacao

Gera carta de encaminhamento específica para habitação.

**Função:**
- `gerar_carta_habitacao()` - Carta com simulação, checklist e QR Code

**Exemplo de uso:**
```python
gerar_carta_habitacao(
    cpf="12345678900",
    nome="Maria da Silva",
    renda_familiar=3000.00,
    composicao_familiar=[
        {"nome": "Maria", "idade": 35, "parentesco": "Responsável"},
        {"nome": "João", "idade": 38, "parentesco": "Cônjuge"}
    ],
    situacao_moradia="ALUGUEL",
    valor_imovel_desejado=180000.00,
    municipio="São Paulo",
    uf="SP",
    beneficiario_bpc=False,
    beneficiario_bf=True
)
```

**Response:**
```json
{
  "sucesso": true,
  "codigo_validacao": "TNM-HAB-2026-XYZ789",
  "validade": "2026-02-28",
  "faixa_mcmv": 2,
  "encaminhamento": "CAIXA",
  "simulacao_incluida": {
    "valor_financiado": 170000.00,
    "subsidio": 47500.00,
    "parcela_estimada": 585.00
  },
  "checklist_documentos": [
    "RG e CPF de todos os compradores",
    "Comprovante de renda (3 últimos meses)",
    "Comprovante de residência",
    "Certidão de casamento ou nascimento",
    "Extrato FGTS",
    "Declaração de Imposto de Renda"
  ],
  "pdf_base64": "JVBERi0xLjQK...",
  "qr_code_base64": "iVBORw0KGgo...",
  "instrucoes": "Leve esta carta à agência CAIXA mais próxima para iniciar o processo."
}
```

**Lógica de encaminhamento:**

| Faixa | Situação | Encaminhamento |
|-------|----------|----------------|
| Faixa 1 (sem CadÚnico) | Não inscrito | CRAS (fazer CadÚnico primeiro) |
| Faixa 1 (com CadÚnico) | Inscrito | Prefeitura (lista de espera) |
| Faixa 2, 3, 4 | Qualquer | CAIXA (financiamento direto) |

### CitizenProfile - Novos Campos

O modelo `CitizenProfile` em `regras_elegibilidade/__init__.py` foi expandido com 12 novos campos para MCMV:

```python
# Campos de habitação
situacao_moradia: str  # "PROPRIA", "ALUGUEL", "CEDIDA", "RUA", "AREA_RISCO"
possui_imovel: bool
valor_aluguel_atual: float
tempo_municipio_anos: int
grupo_prioritario: str  # "SITUACAO_RUA", "VIOLENCIA", "AREA_RISCO", None
beneficiario_bpc: bool
beneficiario_bf: bool
municipio: str
uf: str
valor_imovel_desejado: float
tem_fgts: bool
saldo_fgts: float
```

### Programa Reforma Casa Brasil

Nova modalidade adicionada para quem já tem casa própria mas precisa reformar:

**Critérios:**
- Possuir imóvel em situação irregular ou precária
- Renda familiar até R$ 4.700 (Faixas 1 e 2)
- Inscrito no CadÚnico

**Benefício:**
- Até R$ 50.000 para reforma
- Subsídio de até 95% (Faixa 1) ou 50% (Faixa 2)
- Parcelas a partir de R$ 80/mês

### Atualização na Triagem Universal

O campo `habitacao` em `triagem_universal.py` foi enriquecido:

```json
{
  "habitacao": {
    "programa": "MCMV",
    "elegivel": true,
    "faixa": 2,
    "motivo": "Renda de R$3.000 elegível para Faixa 2",
    "subsidio_estimado": "Até 80%",
    "valor_maximo_imovel": 264000.00,
    "beneficio_especial": null,
    "alternativas": ["REFORMA_CASA_BRASIL"],
    "proximos_passos": [
      "Procurar agência CAIXA",
      "Levar documentos de renda",
      "Escolher imóvel dentro do limite"
    ]
  }
}
```

### Documentos Atualizados

`documentos_por_beneficio.json` agora inclui:

```json
{
  "MCMV": {
    "obrigatorios": [
      "RG e CPF de todos os compradores",
      "Comprovante de renda (3 últimos meses)",
      "Comprovante de residência",
      "Certidão de casamento/nascimento",
      "Extrato FGTS",
      "Declaração de IR (se declarante)"
    ],
    "faixa_1": [
      "Cadastro no CadÚnico",
      "Comprovante de inscrição no CadÚnico"
    ],
    "grupos_prioritarios": [
      "Documento comprobatório da situação (BO, laudo, etc)"
    ]
  },
  "MCMV_REFORMAS": {
    "obrigatorios": [
      "Documento do imóvel (matrícula/contrato)",
      "Laudo de vistoria (será feito pela CAIXA)",
      "RG e CPF do proprietário",
      "Comprovante de renda"
    ]
  }
}
```

### Total de Tools Atualizado

| Sprint | Tools | Total |
|--------|-------|-------|
| Sprint 8 | 16 | 16 |
| Sprint 9 | +9 | 25 |
| Sprint 10 | +2 | 27 |
| Sprint 11 | +2 | **29** |

---

## Próximos Passos (Sprint 12+)

### Prioridade ALTA
- [ ] Integração CAIXA API (pré-cadastro, agendamento, status)
- [ ] Notificações proativas (push + WhatsApp)
- [ ] Tracking de pedidos de medicamentos

### Prioridade MÉDIA
- [ ] Assistência por voz (STT/TTS)
- [ ] Analytics dashboard
- [ ] Multi-idioma (Espanhol, Inglês)

### Prioridade BAIXA
- [ ] Integração Rappi/iFood Farmácia (delivery)
- [ ] Widget white-label CAIXA

---

## Sprint 12: Ecossistema de Parceiros e Marketplace

Novas tools para integração com parceiros, assessoria humana e serviços financeiros.

### Novas Tools

#### 30. escalonar_anjo_social

Escalona casos complexos para assessores humanos (Anjo Social).

**Quando usar**: Idoso 65+, PCD, 3+ benefícios, emergência, documentação complexa, recurso negado.

```python
escalonar_anjo_social(
    motivo="Idoso 72 anos com dificuldade de acesso digital",
    beneficios=["BPC", "BOLSA_FAMILIA"],
    prioridade="high",  # low, medium, high, emergency
    session_id="abc123",
    uf="SP",
    contexto_cidadao={"idade_estimada": 72, "situacao": "idoso_sozinho"}
)
```

**Response**:
```json
{
  "sucesso": true,
  "escalonamento": {
    "case_id": "abc12345",
    "status": "assigned",
    "prioridade": "high",
    "motivo": "Idoso 72 anos com dificuldade de acesso digital"
  },
  "assessor": {
    "nome": "Maria Silva",
    "cargo": "Assistente Social",
    "organizacao": "do CRAS Centro"
  },
  "mensagem_cidadao": "Entendi que sua situação precisa de acompanhamento especial. Vou conectar você com Maria Silva...",
  "prazo_contato": "3 dias úteis"
}
```

**Critérios automáticos de escalonamento**:
- `idoso_65`: Pessoa idosa (65+) com dificuldade de acesso
- `pcd`: Pessoa com deficiência que precisa de BPC/LOAS
- `multiplos_beneficios`: Situação complexa com 3+ benefícios
- `emergencia`: Vulnerabilidade extrema ou emergência social
- `documentacao_complexa`: Dificuldade com documentação ou burocracia
- `recurso_negado`: Benefício negado que precisa de recurso/revisão

#### 31. recomendar_conta_bancaria

Recomenda conta bancária adequada baseada nos benefícios elegíveis.

```python
recomendar_conta_bancaria(
    uf="SP",
    beneficios_elegiveis=["BOLSA_FAMILIA", "BPC", "AUXILIO_GAS"]
)
```

**Response**:
```json
{
  "sucesso": true,
  "parceiro": {
    "nome": "Caixa Tem",
    "slug": "caixa",
    "descricao": "App da Caixa para receber benefícios sociais",
    "vantagens": ["Conta 100% grátis", "Pix ilimitado", "Bolsa Família direto no app"],
    "como_abrir": "Baixe o app Caixa Tem na Play Store...",
    "url": "https://www.caixa.gov.br/caixa-tem/"
  },
  "motivo": "A Caixa Econômica Federal é o banco que paga os benefícios sociais do governo...",
  "beneficios_no_banco": ["BOLSA_FAMILIA", "BPC", "AUXILIO_GAS"]
}
```

**Lógica**: CAIXA é priorizada para benefícios federais (Bolsa Família, BPC, FGTS, etc). Para outros casos, sugere alternativas como Nubank.

#### 32. comparar_planos_celular

Compara planos de celular pré-pago e controle com foco em economia.

```python
comparar_planos_celular(uso="só whatsapp")
```

**Response**:
```json
{
  "sucesso": true,
  "planos": [
    {
      "operadora": "Claro",
      "nome": "Claro Pre 7 dias",
      "tipo": "Pre-pago",
      "preco": "R$ 7,99/semana",
      "dados": "2GB por semana",
      "apps_ilimitados": ["WhatsApp"],
      "ligacoes": "100 minutos"
    }
  ],
  "dica": "Se você usa só WhatsApp, um plano pré-pago semanal é mais econômico...",
  "mensagem_cidadao": "Comparei os planos mais baratos das operadoras..."
}
```

#### 33. comparar_contas_bancarias

Compara contas bancárias digitais gratuitas.

```python
comparar_contas_bancarias()
```

**Response**:
```json
{
  "sucesso": true,
  "contas": [
    {
      "banco": "Caixa Tem",
      "tipo": "Conta poupança digital",
      "taxa_mensal": "Grátis",
      "pix": "Ilimitado e grátis",
      "vantagens": ["Recebe Bolsa Família e BPC automaticamente"],
      "ideal_para": "Quem recebe benefício do governo",
      "destaque": true
    },
    {
      "banco": "Nubank",
      "tipo": "Conta corrente digital",
      "vantagens": ["Dinheiro rende automaticamente (100% CDI)"],
      "ideal_para": "Uso no dia a dia com cartão"
    }
  ],
  "recomendacao_beneficiarios": "Caixa Tem"
}
```

#### 34. verificar_tarifa_energia

Verifica elegibilidade para TSEE (Tarifa Social de Energia) e calcula economia.

```python
verificar_tarifa_energia(uf="SP", consumo_kwh=150)
```

**Response**:
```json
{
  "sucesso": true,
  "consumo_kwh": 150,
  "desconto_percentual": 10,
  "valor_estimado_sem_desconto": 127.50,
  "valor_estimado_com_desconto": 114.75,
  "economia_mensal": 12.75,
  "economia_anual": 153.00,
  "faixas_desconto": [
    {"ate_kwh": 30, "desconto": 65},
    {"ate_kwh": 100, "desconto": 40},
    {"ate_kwh": 220, "desconto": 10}
  ],
  "dicas_economia": ["Desligue aparelhos da tomada...", "Use lâmpadas LED..."],
  "como_solicitar": "Ligue para a distribuidora de energia..."
}
```

#### 35. buscar_vagas

Busca vagas de emprego acessíveis ao público CadÚnico.

```python
buscar_vagas(uf="SP", cidade="São Paulo", perfil="primeiro emprego")
```

**Response**:
```json
{
  "sucesso": true,
  "vagas": [
    {
      "titulo": "Auxiliar de Serviços Gerais",
      "empresa": "Via SINE / Portal Emprega Brasil",
      "tipo": "CLT",
      "requisitos": "Ensino fundamental, sem experiência necessária",
      "faixa_salarial": "R$ 1.412 - R$ 1.600",
      "onde_buscar": "Portal Emprega Brasil (gov.br/trabalho) ou SINE da sua cidade"
    }
  ],
  "como_buscar": {
    "sine": "SINE de São Paulo, SP (presencial, grátis)",
    "portal": "Portal Emprega Brasil: gov.br/trabalho"
  },
  "mensagem_cidadao": "Dica: Se você recebe Bolsa Família, o SINE tem vagas prioritárias..."
}
```

#### 36. buscar_cursos

Busca cursos de capacitação gratuitos (SENAI, SENAC, SEBRAE, AVAMEC).

```python
buscar_cursos(uf="SP", area="informatica", escolaridade="fundamental")
```

**Response**:
```json
{
  "sucesso": true,
  "cursos": [
    {
      "nome": "Operador de Computador",
      "instituicao": "SENAC",
      "modalidade": "Presencial e EAD",
      "duracao": "160 horas",
      "requisito": "Ensino fundamental completo",
      "inscricao": "https://www.ead.senac.br",
      "areas": ["informatica", "tecnologia"]
    }
  ],
  "dica_pronatec": "O PRONATEC oferece cursos técnicos gratuitos para inscritos no CadÚnico..."
}
```

#### 37. simular_microcredito

Simula opções de microcrédito produtivo (CrediAmigo, PRONAF, PNMPO).

```python
simular_microcredito(valor=5000.00, finalidade="comprar mercadoria")
```

**Response**:
```json
{
  "sucesso": true,
  "programas": [
    {
      "nome": "CrediAmigo",
      "banco": "Banco do Nordeste",
      "valor_max": "R$ 21.000",
      "juros": "1.98% ao mês (subsidiado)",
      "parcelas": "Até 12x",
      "valor_parcela": "R$ 471.60",
      "requisitos": ["Empreendedor informal ou MEI", "Renda até 3 salários mínimos"],
      "como_solicitar": "Vá a uma agência do Banco do Nordeste..."
    },
    {
      "nome": "PRONAF - Crédito Rural",
      "banco": "Banco do Brasil / CAIXA",
      "juros": "0,5% a 4% ao ano (subsidiado)",
      "requisitos": ["Agricultor familiar com DAP/CAF"]
    }
  ],
  "mensagem_cidadao": "NUNCA pegue empréstimo com agiota... Os programas do governo são muito mais baratos."
}
```

### Total de Tools Atualizado

| Sprint | Tools | Total |
|--------|-------|-------|
| Sprint 8 | 16 | 16 |
| Sprint 9 | +9 | 25 |
| Sprint 10 | +2 | 27 |
| Sprint 11 | +2 | 29 |
| Sprint 12 | +8 | **37** |

### Arquitetura do Ecossistema

```
┌─────────────────────────────────────────────────────────────┐
│                        AGENTE IA                             │
│         (Detecta situação complexa ou necessidade)          │
└─────────────────────────────────────────────────────────────┘
                              │
        ┌─────────────────────┼─────────────────────┐
        ▼                     ▼                     ▼
┌───────────────┐    ┌───────────────┐    ┌───────────────────┐
│  ANJO SOCIAL  │    │   PARCEIROS   │    │    MARKETPLACE    │
│ (Assessoria)  │    │  (Financeiro) │    │    (Serviços)     │
│               │    │               │    │                   │
│ - Escalonar   │    │ - Caixa Tem   │    │ - Planos celular  │
│ - Acompanhar  │    │ - Nubank      │    │ - Cursos grátis   │
│ - Resolver    │    │ - Microcrédito│    │ - Vagas emprego   │
└───────────────┘    └───────────────┘    └───────────────────┘
```
