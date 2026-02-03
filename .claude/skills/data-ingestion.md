# Skill: Ingestão de Dados

## Jobs Disponíveis

| Job | Fonte | Comando |
|-----|-------|---------|
| IBGE | Estados/municípios | `python -m app.jobs.ingest_ibge` |
| Bolsa Família | Portal da Transparência | `python -m app.jobs.ingest_bolsa_familia` |
| BPC/LOAS | Dados reais | `python -m app.jobs.ingest_bpc_real` |
| Farmácia Popular | Unidades credenciadas | `python -m app.jobs.ingest_farmacia_real` |
| TSEE | Tarifa Social Energia | `python -m app.jobs.ingest_tsee` |
| Auxílio Gás | Auxílio Gás Brasil | `python -m app.jobs.ingest_auxilio_gas` |
| Seguro Defeso | Pescadores | `python -m app.jobs.ingest_seguro_defeso` |
| CadÚnico | SAGI/MDS | `python -m app.jobs.ingest_sagi_cadunico` |
| Geometrias | Mapas municipais | `python -m app.jobs.ingest_mun_geometries` |
| População | IBGE população | `python -m app.jobs.ingest_population` |

## Pré-requisitos
```bash
# 1. Estar no diretório backend
cd backend

# 2. PostgreSQL rodando
docker compose up -d db

# 3. Variáveis de ambiente
source .env

# 4. Migrations aplicadas
alembic upgrade head
```

## Executar Ingestão Completa
```bash
cd backend

# Ordem recomendada
python -m app.jobs.ingest_ibge          # Base: estados e municípios
python -m app.jobs.ingest_population    # População por município
python -m app.jobs.ingest_bolsa_familia # Maior programa
python -m app.jobs.ingest_bpc_real      # BPC/LOAS
python -m app.jobs.ingest_tsee          # Tarifa Social
python -m app.jobs.ingest_farmacia_real # Farmácias
```

## Verificar Ingestão
```sql
-- Contar registros por tabela
SELECT 'municipios' as tabela, COUNT(*) FROM municipios
UNION ALL
SELECT 'beneficiarios', COUNT(*) FROM beneficiarios
UNION ALL
SELECT 'programas', COUNT(*) FROM programas;
```

## Diretório
```
backend/app/jobs/
├── ingest_ibge.py
├── ingest_bolsa_familia.py
├── ingest_bpc_real.py
├── ingest_farmacia_real.py
├── ingest_tsee.py
├── ingest_auxilio_gas.py
├── ingest_seguro_defeso.py
├── ingest_sagi_cadunico.py
├── ingest_mun_geometries.py
├── ingest_population.py
└── indexar_beneficiarios.py
```

## Troubleshooting

| Erro | Causa | Solução |
|------|-------|---------|
| Connection refused | DB não iniciado | `docker compose up -d db` |
| Table not found | Migrations pendentes | `alembic upgrade head` |
| API rate limit | Muitas requisições | Aguardar e retry |
| Memory error | Dataset grande | Processar em chunks |
