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
└── tools/
    ├── validar_cpf.py
    ├── buscar_cep.py
    ├── consultar_api.py
    ├── checklist.py
    ├── buscar_cras.py
    ├── buscar_farmacia.py
    ├── processar_receita.py   # Gemini Vision
    ├── enviar_whatsapp.py     # Twilio
    ├── preparar_pedido.py     # Orquestração
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

## Próximos Passos (Sprint 7+)

- [ ] Integração Rappi Farmácia (delivery)
- [ ] Integração iFood Farmácia
- [ ] Tracking em tempo real
- [ ] Notificações proativas
- [ ] Assistência por voz (STT/TTS)
- [ ] Gerar PDF pré-preenchido
