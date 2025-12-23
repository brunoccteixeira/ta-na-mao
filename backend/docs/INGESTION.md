# Guia de Ingestão de Dados

Este documento descreve como executar os scripts de ingestão de dados do sistema Tá na Mão.

## Pré-requisitos

1. **Ambiente Python configurado**:
   ```bash
   cd backend
   source venv/bin/activate
   pip install -r requirements.txt
   ```

2. **Banco de dados PostgreSQL/PostGIS rodando**:
   ```bash
   docker-compose up -d
   ```

3. **Migrações aplicadas**:
   ```bash
   alembic upgrade head
   ```

---

## Ordem Recomendada de Ingestão

### Primeira Execução (Dados Base)

```bash
# 1. Estados e municípios do IBGE
python -m app.jobs.ingest_ibge

# 2. População (opcional, mas recomendado)
python -m app.jobs.ingest_population

# 3. Geometrias municipais (para mapas)
python -m app.jobs.ingest_mun_geometries
```

### Dados de Programas Sociais

```bash
# 4. Bolsa Família (CadÚnico proxy) - Portal da Transparência
python -m app.jobs.ingest_bolsa_familia 2024 10

# 5. BPC/LOAS - Portal da Transparência
python -m app.jobs.ingest_bpc_real 2024 10

# 6. Farmácia Popular - OpenDataSUS
python -m app.jobs.ingest_farmacia_real

# 7. TSEE - ANEEL
python -m app.jobs.ingest_tsee

# 8. Dignidade Menstrual - OpenDataSUS
python -m app.jobs.ingest_dignidade

# 9. Dados históricos (10 anos de Farmácia Popular)
python -m app.jobs.ingest_historical
```

---

## Scripts de Ingestão

### 1. ingest_bolsa_familia.py

**Fonte**: Portal da Transparência (CGU)

**Uso**:
```bash
# Ingerir mês específico
python -m app.jobs.ingest_bolsa_familia 2024 10

# Argumentos:
#   ano  - Ano (2023-2025)
#   mes  - Mês (1-12)
```

**O que faz**:
- Baixa ZIP do Portal da Transparência (~350MB)
- Converte códigos SIAFI para IBGE usando `data/siafi_ibge_mapping.csv`
- Agrega dados por município (famílias e valores)
- Salva como dados CadÚnico (proxy)
- Estima distribuição por faixa de renda (60% extrema pobreza, 40% pobreza)

**Resultado esperado**:
```
INGESTING BOLSA FAMÍLIA DATA - 2024/10
Loaded 5589 SIAFI to IBGE mappings
Downloaded 367,172,266 bytes
Processed 20,658,029 rows... (5570 municipalities)
Total families: 20,658,029
Estimated persons: 68,169,036
```

**Nota**: O Bolsa Família é usado como proxy para o CadÚnico pois 100% dos beneficiários estão cadastrados no Cadastro Único.

---

### 2. ingest_bpc_real.py

**Fonte**: Portal da Transparência (CGU)

**Uso**:
```bash
# Ingerir mês específico
python -m app.jobs.ingest_bpc_real 2024 10

# Argumentos:
#   ano  - Ano (2019-2025)
#   mes  - Mês (1-12)
```

**O que faz**:
- Baixa CSV do Portal da Transparência (~180MB)
- Converte códigos SIAFI para IBGE usando `data/siafi_ibge_mapping.csv`
- Salva dados de beneficiários por município

**Resultado esperado**:
```
Downloaded 182,123,456 bytes
Processing 6,231,589 beneficiary records...
Saved 5,570 municipality records
```

---

### 3. ingest_farmacia_real.py

**Fonte**: OpenDataSUS (Ministério da Saúde)

**Uso**:
```bash
python -m app.jobs.ingest_farmacia_real
```

**O que faz**:
- Baixa ZIP de `demas-dados-abertos.s3.amazonaws.com/csv/pfpbben.csv.zip`
- Extrai e processa CSV com dados mensais
- Seleciona automaticamente o período mais recente

**Resultado esperado**:
```
Downloaded 45,678,901 bytes from OpenDataSUS
Selected period: 202510
Found 5,570 municipalities with 12,430,549 beneficiaries
```

---

### 4. ingest_tsee.py

**Fonte**: ANEEL (Agência Nacional de Energia Elétrica)

**Uso**:
```bash
python -m app.jobs.ingest_tsee
```

**O que faz**:
- Baixa CSV de dados abertos da ANEEL
- Processa dados de Tarifa Social de Energia Elétrica
- Agrega por estado/distribuidora

**Resultado esperado**:
```
Downloading TSEE data from ANEEL...
Processing 14,328,607 beneficiaries
```

---

### 5. ingest_dignidade.py

**Fonte**: OpenDataSUS (Ministério da Saúde)

**Uso**:
```bash
python -m app.jobs.ingest_dignidade
```

**O que faz**:
- Baixa dados do programa Dignidade Menstrual
- URL: `demas-dados-abertos.s3.amazonaws.com/csv/pfpbdm.csv.zip`
- Processa absorventes distribuídos via Farmácia Popular

**Resultado esperado**:
```
Downloaded Dignidade Menstrual data
Found 5,570 municipalities with 357,730 beneficiaries
```

---

### 6. ingest_historical.py

**Fonte**: OpenDataSUS

**Uso**:
```bash
# Ingerir todos os dados históricos
python -m app.jobs.ingest_historical

# Apenas Farmácia Popular (2016-2025)
python -m app.jobs.ingest_historical farmacia

# Apenas Dignidade Menstrual (2024-2025)
python -m app.jobs.ingest_historical dignidade
```

**O que faz**:
- Processa TODOS os períodos disponíveis no arquivo ZIP
- Farmácia Popular: 10 anos de dados (2016-2025)
- Dignidade Menstrual: 2024-2025
- Cria série histórica mensal para análises temporais

**Resultado esperado**:
```
INGESTING FARMÁCIA POPULAR HISTORICAL DATA
Found 120 periods
  201601: created 5570, updated 0
  201602: created 5570, updated 0
  ...
  202510: created 0, updated 5570
Total: created 668,400, updated 5,570
```

---

## Scripts Auxiliares

### ingest_ibge.py

Carrega lista de estados e municípios da API do IBGE.

```bash
python -m app.jobs.ingest_ibge
```

### ingest_population.py

Atualiza população estimada dos municípios.

```bash
python -m app.jobs.ingest_population
```

### ingest_mun_geometries.py

Baixa geometrias (MultiPolygon) dos municípios para renderização de mapas.

```bash
python -m app.jobs.ingest_mun_geometries
```

### update_coverage.py

Recalcula taxas de cobertura após novas ingestões.

```bash
python -m app.jobs.update_coverage
```

---

## Troubleshooting

### Erro: "Municipality not found"

O código SIAFI não tem mapeamento para IBGE. Verifique se o arquivo `data/siafi_ibge_mapping.csv` está atualizado.

### Erro: "Connection closed unexpectedly"

Durante ingestão de grandes volumes, o PostgreSQL pode fechar conexões. Solução:
- Processar períodos individualmente
- Usar commits frequentes
- Aumentar `idle_in_transaction_session_timeout` no PostgreSQL

### Erro: "HTTP 403/429"

APIs governamentais podem ter rate limiting. Solução:
- Aguardar alguns minutos
- Usar a flag `--retry` quando disponível
- Verificar se a URL ainda está válida

### Dados zerados ou muito baixos

Verificar se o período solicitado existe na fonte. Alguns programas não têm dados para todos os meses.

---

## Verificação de Consistência

Após ingestão, verifique os totais:

```bash
# Via API
curl http://localhost:8000/api/v1/programs/

# Resultado esperado:
# - CadÚnico (Bolsa Família): ~20.6M famílias
# - BPC: ~6.2M beneficiários
# - Farmácia Popular: ~12.4M beneficiários
# - TSEE: ~14.3M beneficiários
# - Dignidade Menstrual: ~358k beneficiários
```

### Dados Oficiais de Referência

| Programa | Fonte Oficial | Total Esperado |
|----------|---------------|----------------|
| Bolsa Família (CadÚnico) | Portal da Transparência | ~21 milhões famílias |
| BPC/LOAS | Portal da Transparência | ~6 milhões |
| Farmácia Popular | gov.br/saude | ~24.7M/ano (~12M/mês) |
| TSEE | ANEEL | ~14 milhões |
| Dignidade Menstrual | gov.br/saude | ~2.5M acumulado |

---

## Automação (Cron)

Para manter dados atualizados, configure cron jobs:

```bash
# Atualizar mensalmente (dia 5 de cada mês às 3h)
# Bolsa Família (dados com 2 meses de atraso)
0 3 5 * * cd /path/to/backend && source venv/bin/activate && python -m app.jobs.ingest_bolsa_familia $(date -d "-2 months" +\%Y) $(date -d "-2 months" +\%m)

# Outros programas
0 3 5 * * cd /path/to/backend && source venv/bin/activate && python -m app.jobs.ingest_farmacia_real
0 3 5 * * cd /path/to/backend && source venv/bin/activate && python -m app.jobs.ingest_dignidade
0 3 5 * * cd /path/to/backend && source venv/bin/activate && python -m app.jobs.ingest_tsee
```
