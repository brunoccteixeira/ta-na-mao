# Migração para Async SQLAlchemy

Este documento descreve a migração do backend para usar SQLAlchemy assíncrono, melhorando significativamente a performance e concorrência.

## Mudanças Implementadas

### 1. Database Configuration (`app/database.py`)

**Antes (Síncrono):**
```python
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

engine = create_engine(DATABASE_URL)
SessionLocal = sessionmaker(bind=engine)

def get_db():
    db = SessionLocal()
    yield db
    db.close()
```

**Depois (Assíncrono):**
```python
from sqlalchemy.ext.asyncio import create_async_engine, AsyncSession, async_sessionmaker

engine = create_async_engine(DATABASE_URL.replace("postgresql://", "postgresql+asyncpg://"))
AsyncSessionLocal = async_sessionmaker(engine, class_=AsyncSession)

async def get_db() -> AsyncSession:
    async with AsyncSessionLocal() as session:
        try:
            yield session
            await session.commit()
        except Exception:
            await session.rollback()
            raise
```

### 2. Routers

**Antes:**
```python
@router.get("/")
async def list_programs(db: Session = Depends(get_db)):
    programs = db.query(Program).filter(Program.is_active == True).all()
    return programs
```

**Depois:**
```python
@router.get("/")
async def list_programs(db: AsyncSession = Depends(get_db)):
    stmt = select(Program).where(Program.is_active == True)
    result = await db.execute(stmt)
    programs = result.scalars().all()
    return programs
```

### 3. Principais Mudanças

- **`db.query()` → `select()` + `await db.execute()`**
- **`.filter()` → `.where()`**
- **`.first()` → `.scalar_one_or_none()`**
- **`.all()` → `.scalars().all()`**
- **`.count()` → `select(func.count())` + `await db.execute()`**
- **`.scalar()` → `await db.execute()` + `.scalar()`**

## Benefícios

### Performance
- **Melhor concorrência**: Múltiplas queries podem rodar simultaneamente
- **Não bloqueia o event loop**: Outras operações podem continuar enquanto aguarda I/O do banco
- **Melhor uso de recursos**: Menos threads, mais eficiente

### Escalabilidade
- Suporta mais requisições simultâneas
- Melhor para APIs com alta carga
- Ideal para operações I/O-bound

## Dependências

### Adicionadas
- `sqlalchemy[asyncio]` - Suporte async do SQLAlchemy
- `asyncpg` - Driver async para PostgreSQL (já estava)
- `greenlet` - Requerido para async SQLAlchemy
- `aiosqlite` - Para testes com SQLite async

### Mantidas
- `psycopg2-binary` - Ainda necessário para Alembic migrations (que são síncronas)

## Migração de Código

### Padrão de Conversão

1. **Queries simples:**
```python
# Antes
program = db.query(Program).filter(Program.code == code).first()

# Depois
stmt = select(Program).where(Program.code == code)
result = await db.execute(stmt)
program = result.scalar_one_or_none()
```

2. **Agregações:**
```python
# Antes
total = db.query(func.sum(BeneficiaryData.total_beneficiaries)).scalar()

# Depois
stmt = select(func.sum(BeneficiaryData.total_beneficiaries))
result = await db.execute(stmt)
total = result.scalar()
```

3. **Joins:**
```python
# Antes
results = db.query(BeneficiaryData, Municipality).join(Municipality).all()

# Depois
stmt = select(BeneficiaryData, Municipality).join(Municipality)
result = await db.execute(stmt)
results = result.all()
```

## Testes

Os testes foram atualizados para usar async:

```python
@pytest.mark.asyncio
async def test_list_programs(client, test_db):
    response = await client.get("/api/v1/programs/")
    assert response.status_code == 200
```

## Alembic Migrations

**Importante**: As migrations do Alembic ainda são síncronas. O Alembic não suporta async nativamente ainda. Para rodar migrations:

```bash
# Usa psycopg2 (síncrono)
alembic upgrade head
```

## Troubleshooting

### Erro: "asyncpg not found"
```bash
pip install asyncpg
```

### Erro: "greenlet required"
```bash
pip install greenlet
```

### DATABASE_URL não funciona
Certifique-se de que a URL está no formato correto:
- Síncrono: `postgresql://user:pass@host/db`
- Async: `postgresql+asyncpg://user:pass@host/db`

O código automaticamente converte, mas pode ser necessário ajustar manualmente.

## Performance Esperada

Com async SQLAlchemy, espera-se:
- **2-3x mais requisições simultâneas** em cenários I/O-bound
- **Menor latência** em operações concorrentes
- **Melhor uso de CPU** (menos threads, mais eficiente)

## Status da Migração

✅ **Migração 100% completa!**

Todos os routers foram convertidos para async:
- ✅ `programs.py`
- ✅ `aggregations.py`
- ✅ `municipalities.py`
- ✅ `geo.py`
- ✅ `admin.py`
- ✅ `webhook.py`
- ✅ `database.py` (engine e session)

O backend está completamente assíncrono e aproveitando ao máximo a performance async.

## Próximos Passos (Opcional)

1. Monitorar performance em produção
2. Considerar connection pooling otimizado para alta carga
3. Atualizar jobs de ingestão para async (se necessário, mas podem permanecer síncronos)


