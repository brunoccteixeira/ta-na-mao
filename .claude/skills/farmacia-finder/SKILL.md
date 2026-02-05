---
name: farmacia-finder
description: Encontrar Farmácias Populares próximas
---

## Função
Localiza farmácias credenciadas no Programa Farmácia Popular do Brasil.

## Fonte de Dados
1. **Primária**: OpenDataSUS (~31.000 farmácias)
2. **Fallback**: i3geo WFS (estabelecimentos)
3. **Coordenadas**: Google Places API

## Tool do Agente
`backend/app/agent/tools/buscar_farmacia.py`

## API
GET /api/v1/nearby/farmacias?lat=-23.55&lng=-46.63&program=farmacia_popular

## Atualização de Dados
- Job: `backend/app/jobs/ingest_farmacia_real.py`
- Fonte: OpenDataSUS / SAGE/MS
- Frequência: Mensal (dia 7, 4h)
- Trigger manual: POST /api/v1/admin/jobs/farmacia/run

## MCP
GoogleMapsMCP (Places API para busca por coordenadas)
