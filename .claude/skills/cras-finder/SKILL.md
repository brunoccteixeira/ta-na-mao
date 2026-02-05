---
name: cras-finder
description: Encontrar CRAS próximos por CEP ou GPS
---

## Função
Localiza CRAS (Centro de Referência de Assistência Social) mais próximos por CEP ou GPS.

## Fonte de Dados
1. **Primária**: Banco de dados `cras_locations` (~8.300 CRAS nacionais)
2. **Fallback**: JSON de exemplo (desenvolvimento)
3. **Coordenadas**: Google Places API

## Tool do Agente
`backend/app/agent/tools/buscar_cras.py`

## API
- GET /api/v1/nearby/cras?lat=-23.55&lng=-46.63&limit=5
- GET /api/v1/admin/cras/stats (estatísticas)

## Atualização de Dados
- Job: `backend/app/jobs/ingest_cras.py`
- Fonte: Censo SUAS / MDS
- Frequência: Mensal (dia 11, 4h)
- Trigger manual: POST /api/v1/admin/jobs/cras/run

## MCP
GoogleMapsMCP (Places API para busca por coordenadas)
