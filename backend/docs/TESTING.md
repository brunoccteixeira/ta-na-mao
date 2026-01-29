# Guia de Testes - Tá na Mão Backend

## Visão Geral

O backend do Tá na Mão possui uma suíte de testes automatizados que cobre:
- **195 testes** passando
- **77% de cobertura** de código

## Executando os Testes

### Requisitos

```bash
# Instalar dependências de teste
pip install pytest pytest-asyncio pytest-cov httpx aiosqlite
```

### Modos de Execução

#### 1. Testes Rápidos (SQLite em memória)

```bash
cd backend
pytest -v
```

Usa SQLite in-memory, ideal para desenvolvimento rápido. Alguns testes que requerem PostgreSQL serão pulados.

#### 2. Testes Completos (PostgreSQL)

```bash
# Subir infraestrutura
docker-compose up -d db redis

# Rodar testes com PostgreSQL
USE_POSTGRES_TESTS=1 pytest -v --cov=app --cov-report=term
```

Usa o banco PostgreSQL real, testando funcionalidades como PostGIS e JSONB.

### Opções Úteis

```bash
# Rodar um arquivo específico
pytest tests/test_tools.py -v

# Rodar teste específico
pytest tests/test_tools.py::TestValidarCpf::test_cpf_valido -v

# Com cobertura detalhada
pytest --cov=app --cov-report=html

# Parar no primeiro erro
pytest -x

# Mostrar saída de print
pytest -s
```

## Estrutura de Testes

```
tests/
├── conftest.py           # Fixtures compartilhadas
├── test_agent.py         # Testes do agente principal
├── test_aggregations.py  # Testes de agregações de dados
├── test_cache.py         # Testes de cache Redis
├── test_context.py       # Testes de contexto de conversa
├── test_more_tools.py    # Testes adicionais de ferramentas
├── test_orchestrator.py  # Testes do orquestrador
├── test_programs.py      # Testes de programas sociais
├── test_response_types.py# Testes de tipos de resposta A2UI
├── test_routers.py       # Testes de endpoints da API
├── test_session_redis.py # Testes de sessão Redis
├── test_subagents.py     # Testes dos sub-agentes
└── test_tools.py         # Testes das ferramentas do agente
```

## Descrição dos Arquivos de Teste

### `conftest.py`
Configuração central com fixtures reutilizáveis:
- `test_db`: Sessão de banco de dados isolada (rollback automático)
- `client`: Cliente HTTP assíncrono para testar a API
- `mock_redis`: Redis mockado para testes unitários
- `sample_program_data`, `sample_municipality_data`, `sample_state_data`: Dados de exemplo

### `test_tools.py`
Testa as ferramentas do agente:
- `validar_cpf` - Validação de CPF
- `buscar_cep` - Consulta de CEP
- `gerar_checklist` - Geração de checklists de documentos
- `dinheiro_esquecido` - Consulta de programas de dinheiro esquecido
- `processar_receita` - Processamento de receitas médicas
- `medicamentos_farmacia_popular` - Consulta de medicamentos

### `test_context.py`
Testa o gerenciamento de contexto:
- `CitizenProfile` - Perfil do cidadão
- `ConversationContext` - Contexto da conversa
- `FlowData` - Dados de fluxo (Farmácia, Benefício, Documentação)
- Estados e transições de fluxo

### `test_response_types.py`
Testa os tipos de resposta A2UI:
- `UIComponent` - Componentes de UI (cards, listas, alertas)
- `Action` - Ações (enviar mensagem, ligar, abrir mapa)
- `AgentResponse` - Resposta estruturada do agente
- `MedicationItem`, `ChecklistItem` - Itens de dados

### `test_subagents.py`
Testa os sub-agentes especializados:
- `FarmaciaSubAgent` - Fluxo de Farmácia Popular
- `BeneficioSubAgent` - Consulta de benefícios
- `DocumentacaoSubAgent` - Orientação sobre documentos
- Transições de estado e comandos de cancelamento

### `test_routers.py`
Testa os endpoints da API:
- `/api/v1/admin/*` - Endpoints administrativos
- `/api/v1/geo/*` - Dados geográficos
- `/api/v1/municipalities/*` - Municípios
- `/api/v1/nearby/*` - Locais próximos
- `/api/v1/webhook/*` - Webhooks (WhatsApp)

### `test_cache.py`
Testa o sistema de cache:
- `get_cache`, `set_cache`, `delete_cache` - Operações básicas
- `clear_cache_pattern` - Limpeza por padrão
- `IntentClassifier` - Classificador de intenções
- Exceções customizadas (`NotFoundError`, `ValidationError`, etc.)

### `test_orchestrator.py`
Testa o orquestrador principal:
- Classificação de intenção
- Roteamento para sub-agentes
- Fallback para LLM
- Gerenciamento de sessão

## Fixtures Principais

### `@requires_postgres`
Decorator para testes que requerem PostgreSQL:

```python
from tests.conftest import requires_postgres

@requires_postgres
class TestGeoRouter:
    async def test_get_states(self, client, test_db):
        response = await client.get("/api/v1/geo/states")
        assert response.status_code == 200
```

### `test_db`
Sessão de banco isolada com rollback automático:

```python
async def test_create_program(self, test_db):
    program = Program(code="TEST", name="Teste")
    test_db.add(program)
    await test_db.commit()
    # Dados serão removidos automaticamente após o teste
```

### `mock_redis`
Redis mockado para testes unitários:

```python
def test_cache_hit(self, mock_redis):
    mock_redis.get.return_value = '{"key": "value"}'
    
    result = cache.get_cache("test_key")
    
    assert result == {"key": "value"}
```

## Padrões de Teste

### Testes Assíncronos

```python
import pytest

class TestAsyncFeature:
    @pytest.mark.asyncio
    async def test_async_operation(self):
        result = await some_async_function()
        assert result is not None
```

### Mocking de APIs Externas

```python
from unittest.mock import patch, AsyncMock

@pytest.mark.asyncio
async def test_external_api(self):
    with patch("httpx.AsyncClient") as mock_client:
        mock_instance = AsyncMock()
        mock_client.return_value.__aenter__.return_value = mock_instance
        mock_instance.get.return_value = MagicMock(
            json=lambda: {"data": "value"},
            raise_for_status=lambda: None
        )
        
        result = await function_that_calls_api()
        assert result["data"] == "value"
```

### Testes de Endpoint

```python
@requires_postgres
class TestMyRouter:
    @pytest.mark.asyncio
    async def test_endpoint(self, client, test_db):
        response = await client.get("/api/v1/resource")
        
        assert response.status_code == 200
        data = response.json()
        assert "items" in data
```

## Cobertura de Código

### Configuração (`.coveragerc`)

```ini
[run]
source = app
omit =
    app/jobs/*              # Scripts de ingestão
    app/agent/tools/google_places.py  # API externa
    app/agent/session_redis.py        # Requer Redis real
    # ... outros módulos excluídos

[report]
exclude_lines =
    pragma: no cover
    def __repr__
    raise AssertionError
    raise NotImplementedError
    if __name__ == .__main__.:
```

### Gerar Relatório HTML

```bash
pytest --cov=app --cov-report=html
open htmlcov/index.html
```

### Meta de Cobertura

O projeto mantém uma meta mínima de **70% de cobertura**:

```bash
pytest --cov=app --cov-fail-under=70
```

## Troubleshooting

### Erro: "Test requires PostgreSQL"
Certifique-se de que o PostgreSQL está rodando e defina a variável:
```bash
USE_POSTGRES_TESTS=1 pytest
```

### Erro: "ModuleNotFoundError"
Instale as dependências de teste:
```bash
pip install -r requirements.txt
pip install pytest pytest-asyncio pytest-cov httpx aiosqlite
```

### Testes Lentos
Execute apenas testes unitários (sem PostgreSQL):
```bash
pytest -v  # Sem USE_POSTGRES_TESTS
```

### Conflito de Dados
Os testes usam SAVEPOINT/ROLLBACK para isolamento. Se houver conflitos:
1. Verifique se `test_db` está sendo usado corretamente
2. Use UUIDs para dados de teste (veja `sample_program_data`)

## CI/CD

Exemplo de configuração para GitHub Actions:

```yaml
name: Tests

on: [push, pull_request]

jobs:
  test:
    runs-on: ubuntu-latest
    
    services:
      postgres:
        image: postgis/postgis:15-3.3
        env:
          POSTGRES_DB: tanamao_test
          POSTGRES_USER: test
          POSTGRES_PASSWORD: test
        ports:
          - 5432:5432
      
      redis:
        image: redis:7
        ports:
          - 6379:6379
    
    steps:
      - uses: actions/checkout@v4
      
      - name: Setup Python
        uses: actions/setup-python@v5
        with:
          python-version: '3.11'
      
      - name: Install dependencies
        run: |
          cd backend
          pip install -r requirements.txt
          pip install pytest pytest-asyncio pytest-cov
      
      - name: Run tests
        env:
          USE_POSTGRES_TESTS: 1
          DATABASE_URL: postgresql://test:test@localhost:5432/tanamao_test
        run: |
          cd backend
          pytest --cov=app --cov-fail-under=70
```

## Contribuindo

Ao adicionar novas funcionalidades:

1. **Escreva testes primeiro** (TDD quando possível)
2. **Mantenha cobertura >= 70%**
3. **Use fixtures existentes** do `conftest.py`
4. **Marque testes PostgreSQL** com `@requires_postgres`
5. **Mock APIs externas** para testes rápidos e confiáveis
