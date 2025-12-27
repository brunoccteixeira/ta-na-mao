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

### Dados do CadÚnico (Base para Cálculo de Cobertura)

```bash
# 4. CadÚnico REAL via API MiSocial (RECOMENDADO)
python -m app.jobs.ingest_misocial_cadunico --periodo 202411

# Para ingestão histórica completa (2019-2024):
python -m app.jobs.ingest_misocial_cadunico --historical --start-year 2019 --end-year 2024
```

### Dados de Programas Sociais

```bash
# 5. Bolsa Família - Portal da Transparência
python -m app.jobs.ingest_bolsa_familia 2024 10

# 6. BPC/LOAS - Portal da Transparência
python -m app.jobs.ingest_bpc_real 2024 10

# 6. Farmácia Popular - OpenDataSUS
python -m app.jobs.ingest_farmacia_real

# 7. TSEE - ANEEL
python -m app.jobs.ingest_tsee

# 8. Dignidade Menstrual - OpenDataSUS
python -m app.jobs.ingest_dignidade

# 9. Auxílio Gás - Portal da Transparência
python -m app.jobs.ingest_auxilio_gas 2024 10

# 10. Seguro Defeso - Portal da Transparência
python -m app.jobs.ingest_seguro_defeso 2024 10

# 11. Auxílio Inclusão - Portal da Transparência
python -m app.jobs.ingest_auxilio_inclusao 2024 10

# 12. Garantia-Safra - Portal da Transparência (agricultores semiárido)
python -m app.jobs.ingest_garantia_safra 2024 3

# 13. Dados históricos (10 anos de Farmácia Popular)
python -m app.jobs.ingest_historical
```

---

## Scripts de Ingestão

### 1. ingest_misocial_cadunico.py ⭐ NOVO

**Fonte**: API MiSocial do MDS (Ministério do Desenvolvimento Social)

**URL**: https://aplicacoes.mds.gov.br/sagi/servicos/misocial/

**Uso**:
```bash
# Testar conexão
python -m app.jobs.ingest_misocial_cadunico --test

# Ingerir período específico
python -m app.jobs.ingest_misocial_cadunico --periodo 202411

# Ingestão histórica (2019-2024)
python -m app.jobs.ingest_misocial_cadunico --historical --start-year 2019 --end-year 2024
```

**O que faz**:
- Consulta API SOLR do MiSocial (dados oficiais do CadÚnico)
- Extrai dados demográficos completos por município
- Salva na tabela `cadunico_data`
- Bulk upsert para performance (5.570 municípios em ~2 min)

**Dados extraídos**:
- Total de famílias e pessoas cadastradas
- Faixas de pobreza (extrema pobreza, pobreza, baixa renda)
- Distribuição etária (0-5, 6-14, 15-17, 18-64, 65+)

**Resultado esperado**:
```
Finding most recent period with data...
Most recent period: 202411
Fetching CadÚnico data for period 202411...
Retrieved 5571 municipality records
Saved 5571 records, skipped 0
```

**Dados disponíveis**: Janeiro/2019 até o mês atual (~73 períodos)

---

### 2. ingest_bolsa_familia.py

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
- Salva na tabela `beneficiary_data` como programa BOLSA_FAMILIA

**Resultado esperado**:
```
INGESTING BOLSA FAMÍLIA DATA - 2024/10
Loaded 5589 SIAFI to IBGE mappings
Downloaded 367,172,266 bytes
Processed 20,658,029 rows... (5570 municipalities)
Total families: 20,658,029
```

**Nota**: O Bolsa Família agora é tratado como programa social separado. O CadÚnico real é ingerido via `ingest_misocial_cadunico.py`.

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

### 6. ingest_auxilio_gas.py ⭐ NOVO

**Fonte**: Portal da Transparência (CGU)

**URL**: https://portaldatransparencia.gov.br/download-de-dados/auxilio-gas

**Uso**:
```bash
# Ingerir mês específico
python -m app.jobs.ingest_auxilio_gas 2024 10

# Argumentos:
#   ano  - Ano (2022-2025)
#   mes  - Mês (1-12)
```

**O que faz**:
- Baixa ZIP do Portal da Transparência
- Converte códigos SIAFI para IBGE
- Agrega dados por município (famílias e valores)
- Salva na tabela `beneficiary_data` como programa AUXILIO_GAS

**Nota**: Auxílio Gás é pago BIMESTRALMENTE, então apenas meses pares têm dados significativos.

**Resultado esperado**:
```
INGESTING AUXÍLIO GÁS DATA - 2024/10
Loaded 5589 SIAFI to IBGE mappings
Downloaded 45,678,901 bytes
Processed 5,789,432 rows... (5570 municipalities)
Total families: 5,789,432
```

---

### 7. ingest_seguro_defeso.py ⭐ NOVO

**Fonte**: Portal da Transparência (CGU)

**URL**: https://portaldatransparencia.gov.br/download-de-dados/seguro-defeso

**Uso**:
```bash
# Ingerir mês específico
python -m app.jobs.ingest_seguro_defeso 2024 10

# Argumentos:
#   ano  - Ano (2019-2025)
#   mes  - Mês (1-12)
```

**O que faz**:
- Baixa ZIP do Portal da Transparência
- Converte códigos SIAFI para IBGE
- Agrega dados por município (beneficiários e valores)
- Salva na tabela `beneficiary_data` como programa SEGURO_DEFESO

**Nota**: Seguro Defeso é pago durante períodos de defeso (reprodução de peixes), que variam por espécie e região. Dados podem ser esparsos em alguns meses.

**Resultado esperado**:
```
INGESTING SEGURO DEFESO DATA - 2024/10
Loaded 5589 SIAFI to IBGE mappings
Downloaded 12,345,678 bytes
Processed 423,000 rows... (3200 municipalities)
Total beneficiaries: 423,000
```

---

### 8. ingest_auxilio_inclusao.py ⭐ NOVO

**Fonte**: Portal da Transparência (CGU)

**URL**: https://portaldatransparencia.gov.br/download-de-dados/auxilio-inclusao

**Uso**:
```bash
# Ingerir mês específico
python -m app.jobs.ingest_auxilio_inclusao 2024 10

# Argumentos:
#   ano  - Ano (2022-2025)
#   mes  - Mês (1-12)
```

**O que faz**:
- Baixa ZIP do Portal da Transparência
- Converte códigos SIAFI para IBGE
- Agrega dados por município (beneficiários e valores)
- Salva na tabela `beneficiary_data` como programa AUXILIO_INCLUSAO

**Nota**: Auxílio Inclusão substitui o BPC para pessoas com deficiência que ingressam no mercado de trabalho formal. Valor de meio salário mínimo.

**Resultado esperado**:
```
INGESTING AUXÍLIO INCLUSÃO DATA - 2024/10
Loaded 5589 SIAFI to IBGE mappings
Downloaded 5,678,901 bytes
Processed 45,000 rows... (2800 municipalities)
Total beneficiaries: 45,000
```

---

### 9. ingest_garantia_safra.py ⭐ NOVO

**Fonte**: Portal da Transparência (CGU)

**URL**: https://portaldatransparencia.gov.br/download-de-dados/garantia-safra

**Uso**:
```bash
# Ingerir mês específico
python -m app.jobs.ingest_garantia_safra 2024 3

# Argumentos:
#   ano  - Ano (2019-2025)
#   mes  - Mês (1-12)
```

**O que faz**:
- Baixa ZIP do Portal da Transparência
- Converte códigos SIAFI para IBGE
- Agrega dados por município (beneficiários e valores)
- Salva na tabela `beneficiary_data` como programa GARANTIA_SAFRA

**Nota**: Garantia-Safra é pago para agricultores do semiárido que perdem safra por seca ou excesso de chuvas. Os pagamentos ocorrem principalmente de janeiro a junho.

**Resultado esperado**:
```
INGESTING GARANTIA-SAFRA DATA - 2024/03
Loaded 5589 SIAFI to IBGE mappings
Downloaded 25,678,901 bytes
Processed 560,000 rows... (744 municipalities)
Total beneficiaries: 560,000
Total value: R$ 672,000,000.00
```

---

### 10. ingest_historical.py

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
| Auxílio Gás | Portal da Transparência | ~5.8 milhões famílias |
| Seguro Defeso | Portal da Transparência | ~400-600 mil pescadores |
| Auxílio Inclusão | Portal da Transparência | ~45 mil beneficiários |
| Garantia-Safra | Portal da Transparência | ~560 mil agricultores |

---

---

## Scripts Alternativos CadÚnico

Existem 3 métodos alternativos para ingestão de dados do CadÚnico além do Bolsa Família:

### ingest_basedosdados_cadunico.py

**Fonte**: Base dos Dados (BigQuery)

**Uso**:
```bash
# Requer autenticação Google Cloud
python -m app.jobs.ingest_basedosdados_cadunico --state SP --periodo 202312

# Argumentos:
#   --test         Modo teste (apenas 1 município)
#   --state XX     Filtrar por estado
#   --periodo YYYYMM  Período específico
```

**O que faz**:
- Extrai dados do CadÚnico via BigQuery (Base dos Dados)
- Requer projeto GCP configurado e autenticação
- Dados mais granulares que Bolsa Família

**Pré-requisitos**:
- `pip install basedosdados`
- Configurar credenciais Google Cloud

---

### ingest_sagi_cadunico.py

**Fonte**: SAGI RI (Secretaria de Avaliação e Gestão da Informação)

**Uso**:
```bash
# Via HTTP (padrão)
python -m app.jobs.ingest_sagi_cadunico --state SP

# Via browser automation (quando HTTP falha)
python -m app.jobs.ingest_sagi_cadunico --browser

# Argumentos:
#   --test IBGE_CODE   Testar município específico
#   --state XX         Filtrar por estado
#   --browser          Usar Playwright para automação
```

**O que faz**:
- Consulta API SAGI RI via HTTP POST
- Fallback para automação de browser com Playwright
- Dados demográficos detalhados (faixas de renda, idade)

**Pré-requisitos**:
- Para modo browser: `pip install playwright && playwright install`

---

### ingest_cadunico_real.py

**Fonte**: Observatório MDS / Qlik (RIv3 API)

**Uso**:
```bash
python -m app.jobs.ingest_cadunico_real --state SP
```

**O que faz**:
- Consulta endpoints RIv3 do Observatório MDS
- Endpoints alternativos quando SAGI falha

**Status**: Experimental - usar como fallback

---

## Scripts Legados (DEPRECATED)

⚠️ **Os scripts abaixo são versões anteriores e não devem ser usados em produção.**

### ingest_bpc.py (DEPRECATED)

Use `ingest_bpc_real.py` em vez deste. O script antigo requer token de API que não está mais disponível.

### ingest_farmacia.py (DEPRECATED)

Use `ingest_farmacia_real.py` em vez deste. O script antigo usa dados simulados.

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

# Novos programas (Portal da Transparência)
0 3 5 * * cd /path/to/backend && source venv/bin/activate && python -m app.jobs.ingest_auxilio_gas $(date -d "-2 months" +\%Y) $(date -d "-2 months" +\%m)
0 3 5 * * cd /path/to/backend && source venv/bin/activate && python -m app.jobs.ingest_seguro_defeso $(date -d "-2 months" +\%Y) $(date -d "-2 months" +\%m)
0 3 5 * * cd /path/to/backend && source venv/bin/activate && python -m app.jobs.ingest_auxilio_inclusao $(date -d "-2 months" +\%Y) $(date -d "-2 months" +\%m)
```
