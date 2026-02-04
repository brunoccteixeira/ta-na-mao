# Documentação da API

API REST para consulta de dados de programas sociais brasileiros.

**Base URL**: `http://localhost:8000/api/v1`

**Documentação Interativa**: `http://localhost:8000/docs` (Swagger UI)

---

## Visão Geral

| Recurso | Endpoints | Descrição |
|---------|-----------|-----------|
| Programs | `/programs/` | Programas sociais rastreados |
| Aggregations | `/aggregations/` | Estatísticas agregadas |
| Municipalities | `/municipalities/` | Dados municipais |
| Geo | `/geo/` | GeoJSON para mapas |
| Admin | `/admin/` | Painel administrativo (penetração, alertas, export) |
| **Agent V2** | `/agent/v2/` | Chat conversacional com sub-agentes |
| **Webhook** | `/webhook/whatsapp/` | Integração WhatsApp via Twilio |
| **Nearby** | `/nearby/` | Farmácias e CRAS próximos (GPS/CEP) |
| **Partners** | `/partners/` | Parceiros (bancos, fintechs) e conversões |
| **Advisory** | `/advisory/` | Anjo Social - escalonamento para assessores humanos |
| **Referrals** | `/referrals/` | Programa de indicação member-get-member |

---

## Programas

### Listar Programas

```http
GET /api/v1/programs/
```

Retorna todos os programas ativos com estatísticas nacionais.

**Resposta**:
```json
[
  {
    "code": "FARMACIA_POPULAR",
    "name": "Farmácia Popular do Brasil",
    "description": "Medicamentos gratuitos ou com desconto",
    "data_source_url": "https://opendatasus.saude.gov.br/...",
    "update_frequency": "monthly",
    "national_stats": {
      "total_beneficiaries": 12430549,
      "total_families": 9944439,
      "total_value_brl": 372916470.0,
      "latest_data_date": "2025-10-01"
    }
  }
]
```

### Detalhes de Programa

```http
GET /api/v1/programs/{code}
```

**Parâmetros**:
- `code`: Código do programa (BPC, FARMACIA_POPULAR, TSEE, DIGNIDADE_MENSTRUAL)

**Exemplo**:
```bash
curl "http://localhost:8000/api/v1/programs/BPC"
```

### Ranking de Municípios

```http
GET /api/v1/programs/{code}/ranking
```

**Parâmetros**:
- `code`: Código do programa
- `state_code` (opcional): Filtrar por estado (ex: SP, RJ)
- `order_by`: beneficiaries | coverage | value (default: beneficiaries)
- `limit`: 1-100 (default: 20)

**Exemplo**:
```bash
curl "http://localhost:8000/api/v1/programs/FARMACIA_POPULAR/ranking?state_code=SP&limit=10"
```

**Resposta**:
```json
{
  "program_code": "FARMACIA_POPULAR",
  "program_name": "Farmácia Popular do Brasil",
  "order_by": "beneficiaries",
  "ranking": [
    {
      "rank": 1,
      "ibge_code": "3550308",
      "name": "São Paulo",
      "total_beneficiaries": 456789,
      "total_families": 365431,
      "coverage_rate": 0.45,
      "total_value_brl": 13703670.0,
      "reference_date": "2025-10-01"
    }
  ]
}
```

---

## Agregações

### Agregação Nacional

```http
GET /api/v1/aggregations/national
```

**Parâmetros**:
- `program` (opcional): Filtrar por programa

**Exemplo**:
```bash
curl "http://localhost:8000/api/v1/aggregations/national?program=BPC"
```

### Agregação por Estados

```http
GET /api/v1/aggregations/states
```

Retorna estatísticas para os 27 estados brasileiros.

**Parâmetros**:
- `program` (opcional): Filtrar por programa

**Exemplo**:
```bash
curl "http://localhost:8000/api/v1/aggregations/states?program=FARMACIA_POPULAR"
```

**Resposta**:
```json
{
  "level": "states",
  "count": 27,
  "states": [
    {
      "ibge_code": "35",
      "name": "São Paulo",
      "abbreviation": "SP",
      "region": "SE",
      "population": 44411238,
      "municipality_count": 645,
      "total_beneficiaries": 2345678,
      "total_families": 1876542,
      "cadunico_families": 4567890,
      "total_value_brl": 70370340.0,
      "avg_coverage_rate": 0.41
    }
  ]
}
```

### Detalhes de Estado

```http
GET /api/v1/aggregations/states/{state_code}
```

**Parâmetros**:
- `state_code`: Sigla do estado (SP, RJ, MG, etc.)
- `program` (opcional): Filtrar por programa

**Exemplo**:
```bash
curl "http://localhost:8000/api/v1/aggregations/states/SP?program=BPC"
```

### Agregação por Regiões

```http
GET /api/v1/aggregations/regions
```

Agrupa dados pelas 5 regiões brasileiras (N, NE, CO, SE, S).

**Parâmetros**:
- `program` (opcional): Filtrar por programa

**Exemplo**:
```bash
curl "http://localhost:8000/api/v1/aggregations/regions?program=TSEE"
```

### Série Temporal

```http
GET /api/v1/aggregations/time-series
```

Retorna dados mensais para gráficos de tendência.

**Parâmetros**:
- `program` (opcional): Filtrar por programa
- `state_code` (opcional): Filtrar por estado

**Exemplo**:
```bash
curl "http://localhost:8000/api/v1/aggregations/time-series?program=FARMACIA_POPULAR"
```

**Resposta**:
```json
{
  "level": "time_series",
  "count": 120,
  "data": [
    {
      "date": "2016-01-01",
      "month": "Jan/16",
      "total_beneficiaries": 10023278,
      "total_families": 8018622,
      "total_value_brl": 300698340.0,
      "avg_coverage_rate": 0.38
    },
    {
      "date": "2016-02-01",
      "month": "Feb/16",
      "total_beneficiaries": 9876543,
      "...": "..."
    }
  ]
}
```

### Demografia (CadÚnico)

```http
GET /api/v1/aggregations/demographics
```

Retorna dados demográficos do CadÚnico.

**Parâmetros**:
- `state_code` (opcional): Filtrar por estado

**Resposta**:
```json
{
  "level": "demographics",
  "total_families": 21456789,
  "total_persons": 65432100,
  "income_brackets": {
    "extreme_poverty": 8765432,
    "poverty": 6543210,
    "low_income": 6148147
  },
  "age_distribution": {
    "0_5": 5432100,
    "6_14": 9876543,
    "15_17": 3456789,
    "18_64": 40123456,
    "65_plus": 6543212
  }
}
```

---

## Admin (Painel Administrativo)

Endpoints para painel administrativo com visão detalhada de cobertura.

### Taxa de Penetração

```http
GET /api/v1/admin/penetration
```

Retorna taxa de penetração por município com paginação e filtros avançados.

**Parâmetros**:
- `state_code` (opcional): Filtrar por estado (ex: SP, RJ)
- `program` (opcional): Filtrar por programa
- `min_population` (opcional): População mínima
- `max_population` (opcional): População máxima
- `min_coverage` (opcional): Cobertura mínima (0-100)
- `max_coverage` (opcional): Cobertura máxima (0-100)
- `order_by`: coverage | gap | population | value | name | beneficiaries (default: coverage)
- `order_dir`: asc | desc (default: asc)
- `limit`: 1-500 (default: 50)
- `offset`: Paginação (default: 0)

**Exemplo**:
```bash
curl "http://localhost:8000/api/v1/admin/penetration?state_code=SP&order_by=gap&order_dir=desc&limit=25"
```

**Resposta**:
```json
{
  "level": "penetration",
  "total_count": 5570,
  "page_size": 25,
  "offset": 0,
  "filters": {"state": "SP", "program": null},
  "data": [
    {
      "ibge_code": "3550308",
      "municipality": "São Paulo",
      "state": "SP",
      "region": "SE",
      "population": 12300000,
      "cadunico_families": 1500000,
      "total_beneficiaries": 680000,
      "total_families": 544000,
      "total_value_brl": 8000000000.0,
      "coverage_rate": 45.3,
      "gap": 956000
    }
  ]
}
```

### Alertas de Cobertura

```http
GET /api/v1/admin/alerts
```

Retorna municípios com baixa cobertura, categorizados por severidade.

**Parâmetros**:
- `threshold_critical`: Limite crítico em % (default: 20)
- `threshold_warning`: Limite de alerta em % (default: 40)
- `program` (opcional): Filtrar por programa
- `state_code` (opcional): Filtrar por estado
- `limit`: 1-200 (default: 50)

**Exemplo**:
```bash
curl "http://localhost:8000/api/v1/admin/alerts?threshold_critical=15&state_code=RJ"
```

**Resposta**:
```json
{
  "summary": {
    "critical_count": 127,
    "warning_count": 340,
    "thresholds": {"critical": 20, "warning": 40},
    "biggest_gap": {"municipality": "São Paulo", "state": "SP", "gap": 956000}
  },
  "alerts": [
    {
      "type": "critical",
      "ibge_code": "3550308",
      "municipality": "São Paulo",
      "state": "SP",
      "population": 12300000,
      "coverage_rate": 15.2,
      "total_beneficiaries": 186960,
      "message": "Cobertura de 15.2% - CRÍTICO"
    }
  ]
}
```

### Exportar Dados

```http
GET /api/v1/admin/export
```

Exporta dados para download em CSV ou JSON.

**Parâmetros**:
- `format`: csv | json (default: csv)
- `scope`: national | state (default: national)
- `state_code` (opcional): Estado para scope=state
- `program` (opcional): Filtrar por programa

**Exemplo**:
```bash
# Exportar CSV de SP
curl "http://localhost:8000/api/v1/admin/export?format=csv&scope=state&state_code=SP" -o export_sp.csv

# Exportar JSON nacional
curl "http://localhost:8000/api/v1/admin/export?format=json&scope=national"
```

**Resposta (JSON)**:
```json
{
  "export_date": "2024-12-27T10:30:00",
  "scope": "national",
  "state": null,
  "program": null,
  "total_rows": 5570,
  "data": [...]
}
```

### Resumo Admin

```http
GET /api/v1/admin/summary
```

Retorna estatísticas rápidas para o dashboard administrativo.

**Exemplo**:
```bash
curl "http://localhost:8000/api/v1/admin/summary"
```

**Resposta**:
```json
{
  "total_municipalities": 5570,
  "total_states": 27,
  "total_population": 212000000,
  "total_beneficiaries": 85000000,
  "total_value_brl": 42000000000.0,
  "avg_coverage_rate": 67.5,
  "critical_municipalities": 127,
  "programs_tracked": 10
}
```

---

## Agente V2 (Chat Conversacional)

O sistema de agente permite interação conversacional com cidadãos via chat ou WhatsApp.
Utiliza arquitetura multi-agente com orquestrador e sub-agentes especializados.

### Iniciar Sessão

```http
POST /api/v1/agent/v2/start
```

Inicia nova sessão de conversa e retorna mensagem de boas-vindas.

**Request Body**:
```json
{
  "session_id": "optional-custom-id"
}
```

**Resposta**:
```json
{
  "text": "Olá! Sou o Tá na Mão, seu assistente de benefícios sociais...",
  "session_id": "abc123-def456",
  "ui_components": [],
  "suggested_actions": [
    {"label": "Pedir remédios", "action_type": "send_message", "payload": "quero pedir remédios"},
    {"label": "Ver benefícios", "action_type": "send_message", "payload": "quero ver meus benefícios"},
    {"label": "Documentos necessários", "action_type": "send_message", "payload": "que documentos preciso"}
  ],
  "flow_state": null,
  "tools_used": []
}
```

### Enviar Mensagem

```http
POST /api/v1/agent/v2/chat
```

Processa mensagem do cidadão e retorna resposta estruturada (formato A2UI).

**Request Body**:
```json
{
  "message": "quero pedir remédios",
  "session_id": "abc123-def456",
  "image_base64": null,
  "location": {
    "latitude": -23.5505,
    "longitude": -46.6333
  }
}
```

**Resposta**:
```json
{
  "text": "Beleza! Para pedir remédios da Farmácia Popular, me manda uma FOTO da receita ou DIGITA o nome dos remédios.",
  "session_id": "abc123-def456",
  "ui_components": [
    {
      "type": "info_card",
      "data": {
        "title": "Farmácia Popular",
        "description": "Medicamentos gratuitos ou com até 90% de desconto"
      }
    }
  ],
  "suggested_actions": [
    {"label": "📷 Tirar foto da receita", "action_type": "camera", "payload": "prescription"},
    {"label": "✍️ Digitar remédios", "action_type": "send_message", "payload": "digitar"}
  ],
  "flow_state": "pharmacy:receita",
  "tools_used": []
}
```

### Chat via WhatsApp (Webhook)

```http
POST /api/v1/webhook/whatsapp/chat
```

Recebe mensagens de cidadãos via Twilio WhatsApp e responde em formato TwiML.

**Form Data** (enviado pelo Twilio):
| Campo | Tipo | Descrição |
|-------|------|-----------|
| `From` | string | Número WhatsApp (ex: "whatsapp:+5511999998888") |
| `Body` | string | Texto da mensagem |
| `MediaUrl0` | string | URL de imagem anexada (se houver) |
| `Latitude` | string | Latitude se enviou localização |
| `Longitude` | string | Longitude se enviou localização |
| `ProfileName` | string | Nome do perfil do usuário |

**Resposta** (TwiML):
```xml
<?xml version="1.0" encoding="UTF-8"?>
<Response>
    <Message>Olá! Para pedir remédios da Farmácia Popular, me manda uma FOTO da receita...</Message>
</Response>
```

### Tipos de UI Components

O campo `ui_components` pode conter:

| Tipo | Descrição |
|------|-----------|
| `benefit_card` | Card de benefício com nome, status, valor estimado |
| `checklist` | Lista de documentos necessários com checkboxes |
| `pharmacy_card` | Card de farmácia com endereço, telefone, distância |
| `medication_list` | Lista de medicamentos com preço e disponibilidade |
| `order_status` | Status do pedido com etapas de progresso |
| `map_location` | Localização no mapa (CRAS, farmácia) |
| `info_card` | Card informativo genérico |

### Tipos de Actions

O campo `suggested_actions` contém botões sugeridos:

| action_type | Descrição | payload |
|-------------|-----------|---------|
| `send_message` | Envia mensagem de texto | Texto a enviar |
| `camera` | Abre câmera | Tipo de foto (ex: "prescription") |
| `open_url` | Abre URL externa | URL completa |
| `call_phone` | Liga para telefone | Número formatado |
| `share` | Compartilha conteúdo | Dados a compartilhar |
| `location` | Solicita localização | - |

### Fluxos de Conversa

O agente suporta três fluxos principais:

| Fluxo | Sub-agente | Estados |
|-------|------------|---------|
| `pharmacy` | FarmaciaSubAgent | INICIO → RECEITA → MEDICAMENTOS → LOCALIZACAO → FARMACIA → CONFIRMACAO |
| `benefit` | BeneficioSubAgent | INICIO → CONSULTA_CPF → RESULTADO → ORIENTACAO |
| `docs` | DocumentacaoSubAgent | INICIO → PROGRAMA → CHECKLIST → LOCALIZACAO → CRAS |

---

## Municípios

### Listar Municípios

```http
GET /api/v1/municipalities/
```

**Parâmetros**:
- `state_id` (opcional): Filtrar por ID do estado
- `state_code` (opcional): Filtrar por sigla (SP, RJ, etc.)
- `search` (opcional): Buscar por nome
- `page`: Página (default: 1)
- `limit`: Itens por página (default: 50, max: 200)

**Exemplo**:
```bash
curl "http://localhost:8000/api/v1/municipalities/?state_code=SP&search=Paulo&limit=10"
```

### Buscar Municípios

```http
GET /api/v1/municipalities/search
```

**Parâmetros**:
- `q`: Query de busca (mínimo 2 caracteres)
- `limit`: Máximo de resultados (default: 20)

**Exemplo**:
```bash
curl "http://localhost:8000/api/v1/municipalities/search?q=Campinas"
```

### Detalhes de Município

```http
GET /api/v1/municipalities/{ibge_code}
```

**Parâmetros**:
- `ibge_code`: Código IBGE de 7 dígitos
- `program` (opcional): Filtrar dados por programa

**Exemplo**:
```bash
curl "http://localhost:8000/api/v1/municipalities/3509502?program=FARMACIA_POPULAR"
```

**Resposta**:
```json
{
  "ibge_code": "3509502",
  "name": "Campinas",
  "state_abbreviation": "SP",
  "state_name": "São Paulo",
  "region": "SE",
  "population": 1223237,
  "area_km2": 794.571,
  "cadunico_families": 89456,
  "total_beneficiaries": 45678,
  "total_families": 36542,
  "total_value_brl": 1370340.0,
  "coverage_rate": 0.51
}
```

### Programas do Município

```http
GET /api/v1/municipalities/{ibge_code}/programs
```

Retorna dados de todos os programas para um município específico.

**Exemplo**:
```bash
curl "http://localhost:8000/api/v1/municipalities/3509502/programs"
```

**Resposta**:
```json
{
  "ibge_code": "3509502",
  "name": "Campinas",
  "programs": [
    {
      "code": "BPC",
      "name": "BPC/LOAS",
      "total_beneficiaries": 12345,
      "total_families": 9876,
      "total_value_brl": 16049700.0,
      "coverage_rate": 0.14,
      "reference_date": "2024-10-01"
    },
    {
      "code": "FARMACIA_POPULAR",
      "name": "Farmácia Popular do Brasil",
      "total_beneficiaries": 45678,
      "...": "..."
    }
  ]
}
```

---

## GeoJSON (Mapas)

### Estados (GeoJSON)

```http
GET /api/v1/geo/states
```

Retorna FeatureCollection com geometrias dos estados.

**Parâmetros**:
- `simplified`: true | false (default: true) - Geometria simplificada
- `program` (opcional): Incluir dados do programa
- `metric` (opcional): beneficiaries | coverage | gap

**Exemplo**:
```bash
curl "http://localhost:8000/api/v1/geo/states?program=BPC"
```

### Municípios (GeoJSON)

```http
GET /api/v1/geo/municipalities
```

**Importante**: Sempre filtre por estado para evitar problemas de performance.

**Parâmetros**:
- `state_id` (opcional): Filtrar por ID do estado
- `state_code` (opcional): Filtrar por sigla
- `simplified`: true | false (default: true)
- `program` (opcional): Incluir dados do programa

**Exemplo**:
```bash
curl "http://localhost:8000/api/v1/geo/municipalities?state_code=SP&program=FARMACIA_POPULAR"
```

### Município Individual (GeoJSON)

```http
GET /api/v1/geo/municipalities/{ibge_code}
```

Retorna Feature com geometria de um único município.

**Exemplo**:
```bash
curl "http://localhost:8000/api/v1/geo/municipalities/3509502"
```

### Bounding Box

```http
GET /api/v1/geo/bounds
```

Retorna coordenadas para `fitBounds()` do Leaflet.

**Parâmetros**:
- `state_code` (opcional): Bounds de um estado específico

**Resposta**:
```json
{
  "bounds": [-53.11, -25.31, -44.16, -19.78],
  "center": [-48.64, -22.55]
}
```

---

## Códigos de Programa

| Código | Nome | Descrição |
|--------|------|-----------|
| `BOLSA_FAMILIA` | Bolsa Família | Transferência de renda para famílias em vulnerabilidade |
| `CADUNICO` | CadÚnico | Cadastro Único para Programas Sociais (via Bolsa Família) |
| `BPC` | BPC/LOAS | Benefício de Prestação Continuada (idosos 65+ e PcD) |
| `FARMACIA_POPULAR` | Farmácia Popular | Medicamentos gratuitos ou subsidiados |
| `TSEE` | Tarifa Social | Desconto na conta de energia elétrica |
| `DIGNIDADE_MENSTRUAL` | Dignidade Menstrual | Absorventes gratuitos via Farmácia Popular |
| `PIS_PASEP` | Cotas PIS/PASEP | Resgate de cotas do fundo PIS/PASEP (1971-1988) |
| `AUXILIO_GAS` | Auxílio Gás | Auxílio para compra de botijão de gás (bimestral) |
| `SEGURO_DEFESO` | Seguro Defeso | Benefício para pescadores artesanais |
| `AUXILIO_INCLUSAO` | Auxílio Inclusão | Meio salário mínimo para PcD que trabalha formalmente |
| `GARANTIA_SAFRA` | Garantia-Safra | Benefício para agricultores do semiárido |
| `PNAE` | PNAE | Programa Nacional de Alimentação Escolar |

### Campos Adicionais nas Respostas

Além dos campos documentados, os endpoints de programa podem retornar:

| Campo | Tipo | Descrição |
|-------|------|-----------|
| `municipalities_covered` | int | Número de municípios com dados |
| `total_municipalities` | int | Total de municípios do Brasil (5.570) |
| `coverage_percentage` | float | Percentual de cobertura municipal |

---

## Códigos de Estado

| Região | Estados |
|--------|---------|
| Norte (N) | AC, AM, AP, PA, RO, RR, TO |
| Nordeste (NE) | AL, BA, CE, MA, PB, PE, PI, RN, SE |
| Centro-Oeste (CO) | DF, GO, MS, MT |
| Sudeste (SE) | ES, MG, RJ, SP |
| Sul (S) | PR, RS, SC |

---

## Serviços Próximos (Nearby)

Endpoints para buscar farmácias e CRAS próximos ao cidadão usando GPS ou CEP.

### Farmácias Próximas

```http
GET /api/v1/nearby/farmacias
```

Busca farmácias credenciadas no Farmácia Popular próximas ao cidadão.

**Parâmetros**:
- `latitude` (opcional): Latitude do usuário
- `longitude` (opcional): Longitude do usuário
- `cep` (opcional): CEP do usuário (alternativa às coordenadas)
- `programa`: FARMACIA_POPULAR | DIGNIDADE_MENSTRUAL (default: FARMACIA_POPULAR)
- `raio_metros`: Raio de busca em metros (default: 3000)
- `limite`: Número máximo de farmácias (default: 5)

**Exemplo**:
```bash
# Por GPS
curl "http://localhost:8000/api/v1/nearby/farmacias?latitude=-23.5505&longitude=-46.6333&limite=5"

# Por CEP
curl "http://localhost:8000/api/v1/nearby/farmacias?cep=04010-100"
```

**Resposta**:
```json
{
  "sucesso": true,
  "encontrados": 3,
  "locais": [
    {
      "nome": "Drogasil Vila Mariana",
      "endereco": "Rua Domingos de Moraes, 1234",
      "distancia": "850m",
      "distancia_metros": 850,
      "telefone": "(11) 3333-4444",
      "horario": "07:00-22:00",
      "aberto_agora": true,
      "delivery": true,
      "links": {
        "maps": "https://maps.google.com/...",
        "waze": "https://waze.com/...",
        "whatsapp": "https://wa.me/..."
      }
    }
  ],
  "mensagem": null,
  "redes_nacionais": ["Drogasil", "Droga Raia", "Pague Menos"]
}
```

**IMPORTANTE**: Para Farmácia Popular, o cidadão vai **direto na farmácia** com receita e documentos. Não precisa ir ao CRAS.

### CRAS Próximos

```http
GET /api/v1/nearby/cras
```

Busca CRAS (postos de assistência social) próximos ao cidadão.

**Parâmetros**:
- `latitude` (opcional): Latitude do usuário
- `longitude` (opcional): Longitude do usuário
- `cep` (opcional): CEP do usuário (alternativa às coordenadas)
- `raio_metros`: Raio de busca em metros (default: 10000)
- `limite`: Número máximo de CRAS (default: 3)

**Exemplo**:
```bash
curl "http://localhost:8000/api/v1/nearby/cras?latitude=-23.5505&longitude=-46.6333"
```

**O CRAS é o local para**:
- Fazer ou atualizar CadÚnico
- Solicitar Bolsa Família
- Iniciar pedido de BPC/LOAS
- Solicitar Tarifa Social de Energia

---

## Carta de Encaminhamento

Endpoints para geração e validação de cartas de encaminhamento para CRAS.

### Gerar Carta

```http
POST /api/v1/carta/gerar
```

Gera carta de encaminhamento com PDF e QR Code.

**Request Body**:
```json
{
  "cpf": "12345678900",
  "nome": "Maria da Silva",
  "data_nascimento": "1985-03-15",
  "endereco": "Rua das Flores, 123",
  "cep": "08471-000",
  "telefone": "11999991234",
  "composicao_familiar": [
    {"nome": "Maria da Silva", "idade": 40, "parentesco": "Responsável"},
    {"nome": "João da Silva", "idade": 42, "parentesco": "Cônjuge"},
    {"nome": "Ana da Silva", "idade": 12, "parentesco": "Filha"}
  ],
  "renda_familiar": 800.00,
  "beneficios_solicitados": ["BOLSA_FAMILIA", "TSEE"],
  "documentos_conferidos": ["RG", "CPF", "COMPROVANTE_RESIDENCIA"],
  "cras_destino": {
    "nome": "CRAS Cidade Tiradentes I",
    "endereco": "Rua Inácio Monteiro, 6.900",
    "telefone": "(11) 2286-1234"
  }
}
```

**Resposta**:
```json
{
  "sucesso": true,
  "codigo_validacao": "TNM-2026-ABC123",
  "validade": "2026-02-28",
  "pdf_base64": "JVBERi0xLjQK...",
  "pdf_url": "https://api.tanamao.app/carta/TNM-2026-ABC123/pdf",
  "qr_code_base64": "iVBORw0KGgo...",
  "link_validacao": "https://api.tanamao.app/carta/TNM-2026-ABC123"
}
```

### Consultar Carta

```http
GET /api/v1/carta/{codigo}
```

Consulta dados de uma carta existente.

**Parâmetros**:
- `codigo`: Código de validação (ex: TNM-2026-ABC123)

**Exemplo**:
```bash
curl "http://localhost:8000/api/v1/carta/TNM-2026-ABC123"
```

**Resposta**:
```json
{
  "codigo": "TNM-2026-ABC123",
  "valida": true,
  "criada_em": "2026-01-28T14:32:00",
  "validade": "2026-02-28",
  "cidadao": {
    "nome": "Maria da Silva",
    "cpf_masked": "***.456.789-**"
  },
  "beneficios_solicitados": ["BOLSA_FAMILIA", "TSEE"],
  "cras_destino": "CRAS Cidade Tiradentes I"
}
```

### Download PDF

```http
GET /api/v1/carta/{codigo}/pdf
```

Retorna o PDF da carta para download.

**Parâmetros**:
- `codigo`: Código de validação

**Exemplo**:
```bash
curl "http://localhost:8000/api/v1/carta/TNM-2026-ABC123/pdf" -o carta.pdf
```

**Resposta**: Arquivo PDF com `Content-Type: application/pdf`

### Validar Carta (QR Code)

```http
POST /api/v1/carta/{codigo}/validar
```

Valida uma carta pelo QR Code (usado pelo atendente CRAS).

**Parâmetros**:
- `codigo`: Código de validação

**Request Body** (opcional):
```json
{
  "atendente_id": "12345",
  "cras_codigo": "SP-CID-001"
}
```

**Resposta**:
```json
{
  "valida": true,
  "status": "ATIVA",
  "cidadao": {
    "nome": "Maria da Silva",
    "cpf_masked": "***.456.789-**",
    "data_nascimento": "1985-03-15"
  },
  "composicao_familiar": [
    {"nome": "Maria da Silva", "idade": 40, "parentesco": "Responsável"},
    {"nome": "João da Silva", "idade": 42, "parentesco": "Cônjuge"}
  ],
  "renda_familiar": 800.00,
  "renda_per_capita": 200.00,
  "beneficios_solicitados": ["BOLSA_FAMILIA", "TSEE"],
  "elegibilidade_estimada": {
    "BOLSA_FAMILIA": {"elegivel": true, "motivo": "Renda per capita R$200 < R$218"},
    "TSEE": {"elegivel": true, "motivo": "Inscrito no CadÚnico"}
  },
  "documentos_conferidos": ["RG", "CPF", "COMPROVANTE_RESIDENCIA"],
  "documentos_faltantes": ["CERTIDAO_NASCIMENTO_FILHOS"],
  "mensagem_atendente": "Carta válida. Verificar documentos faltantes antes de prosseguir."
}
```

**Status possíveis**:
- `ATIVA`: Carta válida e dentro do prazo
- `EXPIRADA`: Carta fora do prazo de validade
- `UTILIZADA`: Carta já foi utilizada em atendimento
- `INVALIDA`: Código não encontrado

---

## Tratamento de Erros

### 404 - Not Found

```json
{
  "detail": "Program not found"
}
```

### 422 - Validation Error

```json
{
  "detail": [
    {
      "loc": ["query", "limit"],
      "msg": "ensure this value is less than or equal to 100",
      "type": "value_error.number.not_le"
    }
  ]
}
```

---

## Exemplos de Uso

### Dashboard Nacional

```bash
# Todos os programas
curl "http://localhost:8000/api/v1/programs/"

# Estatísticas nacionais
curl "http://localhost:8000/api/v1/aggregations/national"
```

### Mapa por Estado

```bash
# GeoJSON dos estados com dados
curl "http://localhost:8000/api/v1/geo/states?program=BPC"

# Municípios de SP
curl "http://localhost:8000/api/v1/geo/municipalities?state_code=SP&program=BPC"
```

### Análise Temporal

```bash
# Série histórica Farmácia Popular
curl "http://localhost:8000/api/v1/aggregations/time-series?program=FARMACIA_POPULAR"

# Série histórica SP
curl "http://localhost:8000/api/v1/aggregations/time-series?program=FARMACIA_POPULAR&state_code=SP"
```

### Comparação Regional

```bash
# Dados por região
curl "http://localhost:8000/api/v1/aggregations/regions?program=TSEE"
```

---

## API v2 - Catálogo Unificado de Benefícios

A API v2 fornece acesso ao catálogo unificado de 229+ benefícios sociais brasileiros (federais, estaduais, municipais e setoriais), com motor de elegibilidade integrado.

**Base URL**: `http://localhost:8000/api/v2/benefits`

### Visão Geral

| Endpoint | Método | Descrição |
|----------|--------|-----------|
| `/` | GET | Listar benefícios com filtros |
| `/stats` | GET | Estatísticas do catálogo |
| `/by-location/{state}` | GET | Benefícios por localização |
| `/{id}` | GET | Detalhes de um benefício |
| `/eligibility/check` | POST | Avaliação completa de elegibilidade |
| `/eligibility/quick` | POST | Avaliação rápida |

### Listar Benefícios

```http
GET /api/v2/benefits/
```

**Parâmetros**:
- `scope` (opcional): federal | state | municipal | sectoral
- `state` (opcional): Código UF (SP, RJ, etc.)
- `municipality_ibge` (opcional): Código IBGE do município
- `sector` (opcional): pescador | agricultor | entregador | catador | mei
- `category` (opcional): Filtrar por categoria
- `search` (opcional): Busca por nome/descrição
- `status` (opcional): active | suspended | ended (default: active)
- `page`: Página (default: 1)
- `limit`: Itens por página (default: 50, max: 200)

**Exemplos**:
```bash
# Todos os benefícios federais
curl "http://localhost:8000/api/v2/benefits/?scope=federal"

# Benefícios estaduais de SP
curl "http://localhost:8000/api/v2/benefits/?scope=state&state=SP"

# Buscar por nome
curl "http://localhost:8000/api/v2/benefits/?search=bolsa"

# Benefícios para pescadores
curl "http://localhost:8000/api/v2/benefits/?sector=pescador"
```

**Resposta**:
```json
{
  "items": [
    {
      "id": "federal-bolsa-familia",
      "name": "Bolsa Família",
      "shortDescription": "Ajuda mensal para famílias com pouca renda",
      "scope": "federal",
      "state": null,
      "municipalityIbge": null,
      "estimatedValue": {
        "type": "monthly",
        "min": 142,
        "max": 900,
        "description": "Valor varia conforme composição familiar"
      },
      "status": "active",
      "icon": "🏠",
      "category": "Transferência de Renda"
    }
  ],
  "total": 229,
  "page": 1,
  "limit": 50,
  "pages": 5
}
```

### Estatísticas do Catálogo

```http
GET /api/v2/benefits/stats
```

**Resposta**:
```json
{
  "totalBenefits": 229,
  "byScope": {
    "federal": 16,
    "state": 106,
    "municipal": 97,
    "sectoral": 10
  },
  "byCategory": {
    "Transferência de Renda": 45,
    "Habitação": 32,
    "Saúde": 28,
    "Transporte": 24
  },
  "statesCovered": 27,
  "municipalitiesCovered": 40
}
```

### Benefícios por Localização

```http
GET /api/v2/benefits/by-location/{state_code}
```

Retorna todos os benefícios aplicáveis para uma localização (federal + estadual + municipal).

**Parâmetros**:
- `state_code`: Código UF (obrigatório)
- `municipality_ibge` (opcional): Código IBGE para incluir benefícios municipais

**Exemplos**:
```bash
# Benefícios de SP (federal + estadual)
curl "http://localhost:8000/api/v2/benefits/by-location/SP"

# Benefícios de São Paulo capital (federal + estadual + municipal)
curl "http://localhost:8000/api/v2/benefits/by-location/SP?municipality_ibge=3550308"
```

**Resposta**:
```json
{
  "state": "SP",
  "municipality_ibge": "3550308",
  "total": 28,
  "federal": [...],
  "state": [...],
  "municipal": [...],
  "sectoral": [...]
}
```

### Detalhes de Benefício

```http
GET /api/v2/benefits/{id}
```

**Exemplos**:
```bash
curl "http://localhost:8000/api/v2/benefits/federal-bolsa-familia"
curl "http://localhost:8000/api/v2/benefits/sp-bolsa-povo"
curl "http://localhost:8000/api/v2/benefits/sp-saopaulo-bolsa-trabalho"
```

**Resposta**:
```json
{
  "id": "federal-bolsa-familia",
  "name": "Bolsa Família",
  "shortDescription": "Ajuda mensal para famílias com pouca renda",
  "scope": "federal",
  "state": null,
  "municipalityIbge": null,
  "sector": null,
  "estimatedValue": {
    "type": "monthly",
    "min": 142,
    "max": 900,
    "description": "Valor varia conforme composição familiar"
  },
  "eligibilityRules": [
    {
      "field": "rendaPerCapita",
      "operator": "lte",
      "value": 218,
      "description": "Renda por pessoa de até R$ 218 por mês"
    },
    {
      "field": "cadastradoCadunico",
      "operator": "eq",
      "value": true,
      "description": "Inscrito no Cadastro Único"
    }
  ],
  "whereToApply": "CRAS mais próximo",
  "documentsRequired": ["CPF de todos da família", "Certidão de nascimento", "Comprovante de residência"],
  "howToApply": ["Vá ao CRAS da sua cidade", "Leve os documentos", "Faça o Cadastro Único"],
  "sourceUrl": "https://www.gov.br/mds/...",
  "lastUpdated": "2024-01-15",
  "status": "active",
  "icon": "🏠",
  "category": "Transferência de Renda"
}
```

### Avaliação de Elegibilidade (Completa)

```http
POST /api/v2/benefits/eligibility/check
```

Avalia a elegibilidade de um cidadão para todos os benefícios aplicáveis.

**Request Body**:
```json
{
  "profile": {
    "estado": "SP",
    "municipioIbge": "3550308",
    "pessoasNaCasa": 4,
    "quantidadeFilhos": 2,
    "temIdoso65Mais": false,
    "temGestante": false,
    "temPcd": false,
    "temCrianca0a6": true,
    "rendaFamiliarMensal": 800,
    "trabalhoFormal": false,
    "temCasaPropria": false,
    "cadastradoCadunico": true,
    "recebeBolsaFamilia": false,
    "recebeBpc": false,
    "temMei": false,
    "agricultorFamiliar": false,
    "pescadorArtesanal": false,
    "estudante": false,
    "redePublica": false
  },
  "scope": null,
  "includeNotApplicable": false
}
```

**Resposta**:
```json
{
  "profileSummary": {
    "estado": "SP",
    "municipio": "São Paulo",
    "pessoasNaCasa": 4,
    "rendaFamiliar": 800,
    "rendaPerCapita": 200,
    "cadastradoCadunico": true
  },
  "summary": {
    "eligible": [
      {
        "benefit": {
          "id": "federal-bolsa-familia",
          "name": "Bolsa Família",
          "shortDescription": "Ajuda mensal para famílias com pouca renda",
          "estimatedValue": {"type": "monthly", "min": 142, "max": 900}
        },
        "status": "eligible",
        "matchedRules": ["Renda por pessoa de até R$ 218", "Inscrito no Cadastro Único"],
        "failedRules": [],
        "inconclusiveRules": [],
        "estimatedValue": 492,
        "reason": "Você atende a todos os requisitos"
      }
    ],
    "likelyEligible": [...],
    "maybe": [...],
    "notEligible": [],
    "notApplicable": [],
    "alreadyReceiving": [],
    "totalAnalyzed": 28,
    "totalPotentialMonthly": 1542,
    "totalPotentialAnnual": 1412,
    "totalPotentialOneTime": 5000,
    "prioritySteps": [
      "Faça ou atualize seu Cadastro Único no CRAS",
      "Solicite o Bolsa Família - CRAS mais próximo"
    ],
    "documentsNeeded": ["CPF de todos da família", "Comprovante de residência"]
  },
  "evaluatedAt": "2026-01-29T23:45:00"
}
```

### Avaliação Rápida

```http
POST /api/v2/benefits/eligibility/quick
```

Avaliação simplificada com poucos parâmetros.

**Query Parameters**:
- `estado`: UF (obrigatório)
- `renda_familiar`: Renda mensal da família (obrigatório)
- `pessoas_na_casa`: Pessoas na casa (default: 1)
- `cadastrado_cadunico`: Está no CadÚnico? (default: false)

**Exemplo**:
```bash
curl -X POST "http://localhost:8000/api/v2/benefits/eligibility/quick?estado=SP&renda_familiar=800&pessoas_na_casa=4&cadastrado_cadunico=true"
```

**Resposta**:
```json
{
  "estado": "SP",
  "rendaPerCapita": 200,
  "totalEligible": 8,
  "totalLikelyEligible": 4,
  "totalPotentialMonthly": 1542,
  "topBenefits": [
    {"id": "federal-bolsa-familia", "name": "Bolsa Família", "estimatedValue": 492},
    {"id": "federal-tsee", "name": "Tarifa Social de Energia", "estimatedValue": 60}
  ],
  "nextStep": "Faça ou atualize seu Cadastro Único no CRAS"
}
```

### Status de Elegibilidade

| Status | Descrição |
|--------|-----------|
| `eligible` | Atende a todos os requisitos |
| `likely_eligible` | Provavelmente elegível, verificar presencialmente |
| `maybe` | Pode ter direito, verificar no CRAS |
| `not_eligible` | Não atende aos requisitos |
| `not_applicable` | Benefício não disponível na região/setor |
| `already_receiving` | Já recebe este benefício |

### Operadores de Regras

| Operador | Descrição |
|----------|-----------|
| `eq` | Igual a |
| `neq` | Diferente de |
| `lt` | Menor que |
| `lte` | Menor ou igual a |
| `gt` | Maior que |
| `gte` | Maior ou igual a |
| `in` | Está na lista |
| `not_in` | Não está na lista |
| `has` | Tem valor (truthy) |
| `not_has` | Não tem valor (falsy) |

### Campos do Perfil do Cidadão

| Campo | Tipo | Descrição |
|-------|------|-----------|
| `estado` | string | UF (obrigatório) |
| `municipioIbge` | string | Código IBGE do município |
| `idade` | number | Idade do cidadão |
| `pessoasNaCasa` | number | Total de pessoas na residência |
| `quantidadeFilhos` | number | Filhos menores de 18 anos |
| `temIdoso65Mais` | boolean | Tem idoso 65+ na família |
| `temGestante` | boolean | Tem gestante na família |
| `temPcd` | boolean | Tem pessoa com deficiência |
| `temCrianca0a6` | boolean | Tem criança de 0 a 6 anos |
| `rendaFamiliarMensal` | number | Renda total da família |
| `trabalhoFormal` | boolean | Tem trabalho com carteira |
| `temCasaPropria` | boolean | Possui casa própria |
| `cadastradoCadunico` | boolean | Inscrito no CadÚnico |
| `recebeBolsaFamilia` | boolean | Já recebe Bolsa Família |
| `recebeBpc` | boolean | Já recebe BPC |
| `temMei` | boolean | É MEI |
| `agricultorFamiliar` | boolean | É agricultor familiar |
| `pescadorArtesanal` | boolean | É pescador artesanal |
| `catadorReciclavel` | boolean | É catador de recicláveis |
| `trabalhaAplicativo` | boolean | Trabalha como entregador/motorista de app |
| `estudante` | boolean | É estudante |
| `redePublica` | boolean | Estuda em rede pública |

---

## Ecossistema de Parceiros

APIs para gerenciamento de parceiros, assessores sociais (Anjo Social) e programa de indicações.

### Parceiros

**Base URL**: `/api/v1/partners`

#### Listar Parceiros

```http
GET /api/v1/partners/
```

Retorna todos os parceiros ativos (bancos, fintechs, serviços).

**Resposta**:
```json
[
  {
    "slug": "caixa",
    "nome": "Caixa Tem",
    "descricao": "App da Caixa para receber benefícios sociais",
    "categoria": "banco",
    "url": "https://www.caixa.gov.br/caixa-tem/",
    "ativo": true
  }
]
```

#### Detalhes do Parceiro

```http
GET /api/v1/partners/{slug}
```

**Parâmetros**:
- `slug`: Identificador único do parceiro (ex: caixa, nubank)

**Exemplo**:
```bash
curl "http://localhost:8000/api/v1/partners/caixa"
```

#### Registrar Conversão

```http
POST /api/v1/partners/conversions
```

Registra evento de conversão (impressão, clique, redirecionamento).

**Request Body**:
```json
{
  "partner_slug": "caixa",
  "session_id": "abc123",
  "event": "click",
  "source": "home_page",
  "metadata": {"benefit_context": "bolsa_familia"}
}
```

**Eventos possíveis**: `impression`, `click`, `redirect`, `signup`

#### Estatísticas de Conversão (Admin)

```http
GET /api/v1/partners/conversions/stats
```

**Parâmetros**:
- `partner_slug` (opcional): Filtrar por parceiro
- `days`: Período em dias (default: 30, max: 365)

---

### Anjo Social (Advisory)

Sistema de escalonamento para assessores humanos em casos complexos.

**Base URL**: `/api/v1/advisory`

#### Criar Caso

```http
POST /api/v1/advisory/cases/
```

Cria um novo caso de assessoria (geralmente via escalonamento da IA).

**Request Body**:
```json
{
  "citizen_session_id": "abc123",
  "benefits": ["BPC", "BOLSA_FAMILIA"],
  "escalation_reason": "Idoso 65+ com dificuldade de acesso",
  "priority": "high",
  "citizen_context": {
    "uf": "SP",
    "idade_estimada": 72,
    "situacao": "idoso_sozinho"
  }
}
```

**Prioridades**: `low`, `medium`, `high`, `emergency`

**Resposta**:
```json
{
  "id": "550e8400-e29b-41d4-a716-446655440000",
  "status": "pending",
  "advisorId": null
}
```

#### Consultar Caso

```http
GET /api/v1/advisory/cases/{case_id}
```

Retorna detalhes completos do caso com assessor e notas.

#### Atualizar Caso

```http
PATCH /api/v1/advisory/cases/{case_id}
```

Atualiza status, prioridade ou atribui assessor.

**Request Body**:
```json
{
  "status": "in_progress",
  "priority": "high",
  "advisor_id": "550e8400-e29b-41d4-a716-446655440001"
}
```

**Status possíveis**: `pending`, `assigned`, `in_progress`, `resolved`, `closed`

#### Adicionar Nota

```http
POST /api/v1/advisory/cases/{case_id}/notes
```

**Request Body**:
```json
{
  "author": "Maria Silva",
  "content": "Cidadão agendado para CRAS dia 15/02"
}
```

#### Listar Casos

```http
GET /api/v1/advisory/cases/
```

**Parâmetros**:
- `advisor_id` (opcional): Filtrar por assessor
- `status` (opcional): Filtrar por status
- `priority` (opcional): Filtrar por prioridade
- `limit`: Máximo de resultados (default: 50)
- `offset`: Paginação

#### Listar Assessores

```http
GET /api/v1/advisory/advisors/
```

Retorna assessores ativos.

#### Criar Assessor

```http
POST /api/v1/advisory/advisors/
```

**Request Body**:
```json
{
  "name": "Maria Silva",
  "email": "maria@cras.gov.br",
  "role": "assistente_social",
  "organization": "CRAS Centro",
  "specialties": ["BPC", "BOLSA_FAMILIA", "MCMV"]
}
```

#### Dashboard do Assessor

```http
GET /api/v1/advisory/advisors/{advisor_id}/dashboard
```

Retorna dashboard com casos ativos e estatísticas.

**Resposta**:
```json
{
  "advisor": {"name": "Maria Silva", "role": "assistente_social"},
  "active_cases": 12,
  "pending_cases": 5,
  "resolved_this_month": 23,
  "avg_resolution_days": 3.5,
  "cases": [...]
}
```

---

### Indicações (Referrals)

Programa de indicação member-get-member anônimo.

**Base URL**: `/api/v1/referrals`

#### Registrar Compartilhamento

```http
POST /api/v1/referrals/
```

Registra quando um usuário compartilha seu link de indicação.

**Request Body**:
```json
{
  "referral_code": "ABC123",
  "method": "whatsapp"
}
```

**Métodos**: `whatsapp`, `copy`, `sms`

#### Registrar Conversão

```http
POST /api/v1/referrals/conversion
```

Registra quando um indicado completa o wizard.

**Request Body**:
```json
{
  "referral_code": "ABC123"
}
```

#### Estatísticas (Admin)

```http
GET /api/v1/referrals/stats
```

**Parâmetros**:
- `days`: Período em dias (default: 30)

**Resposta**:
```json
{
  "period_days": 30,
  "total_shares": 1234,
  "total_conversions": 456,
  "unique_sharers": 890,
  "unique_conversions": 345,
  "conversion_rate": 0.3876,
  "by_method": {
    "whatsapp": 800,
    "copy": 300,
    "sms": 134
  }
}
```
