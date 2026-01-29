# Skill: Segurança Multi-Camada

Checklist de segurança para código que lida com dados sensíveis (CPF, benefícios).

## Camada 1: Validação de Entrada

### CPF
```python
import re

def validar_cpf(cpf: str) -> bool:
    # Remove caracteres não numéricos
    cpf = re.sub(r'[^0-9]', '', cpf)

    # Verifica tamanho
    if len(cpf) != 11:
        return False

    # Verifica se não são todos iguais
    if cpf == cpf[0] * 11:
        return False

    # Validação dos dígitos verificadores
    # ... implementar algoritmo
    return True
```

### Sanitização
```python
from html import escape

def sanitizar_input(texto: str) -> str:
    # Remove HTML/scripts
    texto = escape(texto)
    # Limita tamanho
    texto = texto[:1000]
    return texto
```

## Camada 2: Autenticação & Autorização

### Verificar Sessão
```python
async def verificar_sessao(session_id: str) -> bool:
    session = await redis.get(f"session:{session_id}")
    return session is not None
```

### Rate Limiting
```python
from slowapi import Limiter

limiter = Limiter(key_func=get_remote_address)

@app.get("/api/v1/beneficios")
@limiter.limit("10/minute")
async def consultar_beneficios():
    pass
```

## Camada 3: Dados em Trânsito

### HTTPS Obrigatório
```python
# Em produção, forçar HTTPS
if not request.url.scheme == "https":
    raise HTTPException(status_code=400)
```

### Headers de Segurança
```python
from fastapi.middleware.cors import CORSMiddleware

app.add_middleware(
    CORSMiddleware,
    allow_origins=["https://tanamao.gov.br"],
    allow_methods=["GET", "POST"],
    allow_headers=["*"],
)
```

## Camada 4: Dados em Repouso

### Não Logar Dados Sensíveis
```python
# ERRADO
logger.info(f"Consultando CPF: {cpf}")

# CERTO
logger.info(f"Consultando CPF: ***{cpf[-4:]}")
```

### Variáveis de Ambiente
```bash
# Nunca commitar .env
# Usar .env.example como template
DATABASE_URL=
REDIS_URL=
API_KEY=
```

## Camada 5: Monitoramento

### Alertas de Segurança
```python
# Detectar tentativas suspeitas
if tentativas_falhas > 5:
    logger.warning(f"Múltiplas falhas de autenticação: {ip}")
    await notificar_admin(ip)
```

## Checklist de Revisão de Código

| Item | Verificar |
|------|-----------|
| CPF | Validação e mascaramento em logs |
| SQL | Queries parametrizadas (SQLAlchemy) |
| Inputs | Sanitização de texto do usuário |
| Sessões | Expiração e invalidação |
| Senhas | Nunca em texto plano |
| APIs | Rate limiting configurado |
| Logs | Sem dados sensíveis |
| .env | Não commitado |

## Dados Sensíveis no Projeto

- CPF
- NIS (Número de Identificação Social)
- Valores de benefícios
- Endereços
- Telefones
- Informações de saúde (laudos BPC)
