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
| `CADUNICO` | CadÚnico/Bolsa Família | Cadastro Único (via dados Bolsa Família) |
| `BPC` | BPC/LOAS | Benefício de Prestação Continuada |
| `FARMACIA_POPULAR` | Farmácia Popular | Medicamentos gratuitos/subsidiados |
| `TSEE` | Tarifa Social | Desconto na conta de energia |
| `DIGNIDADE_MENSTRUAL` | Dignidade Menstrual | Absorventes gratuitos |

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
