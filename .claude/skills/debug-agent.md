# Skill: Debug do Agente

## Arquivos do Agente
- `backend/app/agent/agent.py` - TaNaMaoAgent principal
- `backend/app/agent/orchestrator.py` - Orquestrador de fluxo
- `backend/app/agent/tools/` - 25+ ferramentas MCP
- `backend/app/agent/subagents/` - Sub-agentes especializados

## Debugging Sistemático (5 Passos)

### 1. REPRODUZIR: Isolar o problema
```bash
# Testar endpoint diretamente
curl -X POST "http://localhost:8000/api/v1/agent/v2/chat" \
  -H "Content-Type: application/json" \
  -d '{"message": "quero saber meus benefícios", "session_id": "debug-001"}'
```

### 2. LOCALIZAR: Identificar onde falha
```bash
# Verificar logs do FastAPI
docker compose logs -f backend

# Verificar Redis (sessões)
redis-cli KEYS "session:*"
redis-cli GET "session:debug-001"
```

### 3. ISOLAR: Testar componentes individualmente
```python
# Testar ferramenta específica
from app.agent.tools.consulta_beneficios import consultar_cpf
resultado = await consultar_cpf("12345678901")
print(resultado)
```

### 4. CORRIGIR: Aplicar fix mínimo
- Fazer mudança cirúrgica
- Não refatorar código adjacente
- Manter estilo existente

### 5. VERIFICAR: Confirmar correção
```bash
# Re-testar cenário original
curl -X POST "http://localhost:8000/api/v1/agent/v2/chat" \
  -H "Content-Type: application/json" \
  -d '{"message": "quero saber meus benefícios", "session_id": "debug-002"}'

# Rodar testes relacionados
pytest backend/tests/test_agent.py -v
```

## Checklist de Diagnóstico

| Sintoma | Verificar | Comando |
|---------|-----------|---------|
| 500 Error | Logs do backend | `docker compose logs backend` |
| Timeout | Conexão com APIs | `curl -I https://api.example.com` |
| Sessão perdida | Redis | `redis-cli PING` |
| Tool não executa | Permissões MCP | Verificar `.mcp.json` |
| Resposta vazia | Prompt do agente | Verificar `agent.py` |

## Logs Estruturados
```bash
# Habilitar debug logging
export LOG_LEVEL=DEBUG
uvicorn app.main:app --reload

# Filtrar por módulo
docker compose logs backend 2>&1 | grep "agent"
docker compose logs backend 2>&1 | grep "ERROR"
```

## Testar Ferramentas Isoladamente
```python
# backend/scripts/test_tool.py
import asyncio
from app.agent.tools.consulta_cras import buscar_cras

async def main():
    resultado = await buscar_cras(lat=-23.5505, lng=-46.6333)
    print(resultado)

asyncio.run(main())
```
