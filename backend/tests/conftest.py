"""
Configurações e fixtures compartilhadas para testes.

Imports are done inside fixtures to allow unit tests to run even when
some dependencies (like google.generativeai) are not installed.
"""

import os
import pytest
import asyncio
from typing import Generator, AsyncGenerator
from unittest.mock import Mock, MagicMock


# Check if we're using SQLite (test mode) or PostgreSQL
# Set USE_POSTGRES_TESTS=1 to run integration tests with real PostgreSQL
USE_POSTGRES = os.environ.get("USE_POSTGRES_TESTS", "0") == "1"
IS_SQLITE_TEST = not USE_POSTGRES


# Skip marker for tests requiring PostgreSQL
requires_postgres = pytest.mark.skipif(
    IS_SQLITE_TEST,
    reason="Test requires PostgreSQL with PostGIS/JSONB support (set USE_POSTGRES_TESTS=1)"
)


# Tables with PostgreSQL-specific features (not supported in SQLite)
# - states, municipalities: PostGIS geometry columns
# - pedidos, beneficiary_data: JSONB columns
TABLES_POSTGRES_ONLY = {"states", "municipalities", "pedidos", "beneficiary_data"}


@pytest.fixture(scope="session")
def event_loop() -> Generator:
    """Cria event loop para testes async."""
    loop = asyncio.get_event_loop_policy().new_event_loop()
    yield loop
    loop.close()


@pytest.fixture(autouse=True)
def mock_google_api_key(monkeypatch):
    """Mocka GOOGLE_API_KEY para testes."""
    monkeypatch.setenv("GOOGLE_API_KEY", "test-api-key")


@pytest.fixture(autouse=True)
def mock_twilio_credentials(monkeypatch):
    """Mocka credenciais Twilio para testes."""
    monkeypatch.setenv("TWILIO_ACCOUNT_SID", "test-account-sid")
    monkeypatch.setenv("TWILIO_AUTH_TOKEN", "test-auth-token")
    monkeypatch.setenv("TWILIO_WHATSAPP_FROM", "whatsapp:+14155238886")


# Database fixtures for testing (async)
@pytest.fixture(scope="function")
async def test_db():
    """Cria banco de dados para testes (async).

    Uses SQLite in-memory by default. Set USE_POSTGRES_TESTS=1 for PostgreSQL.

    IMPORTANT: Uses SAVEPOINT/ROLLBACK to isolate each test - no data persists.
    """
    # Lazy imports
    from httpx import AsyncClient
    from sqlalchemy.ext.asyncio import AsyncSession, create_async_engine, async_sessionmaker
    from sqlalchemy.pool import NullPool
    from app.database import Base
    from app.config import settings

    if USE_POSTGRES:
        # Use real PostgreSQL database
        db_url = settings.DATABASE_URL
        if db_url.startswith("postgresql://"):
            db_url = db_url.replace("postgresql://", "postgresql+asyncpg://", 1)

        engine = create_async_engine(
            db_url,
            echo=False,
            poolclass=NullPool,
        )

        # Create a connection and start a transaction
        async with engine.connect() as conn:
            # Start outer transaction that will be rolled back
            trans = await conn.begin()

            # Create a session bound to this connection
            TestingSessionLocal = async_sessionmaker(
                bind=conn,
                class_=AsyncSession,
                expire_on_commit=False,
                join_transaction_mode="create_savepoint",
            )

            async with TestingSessionLocal() as session:
                try:
                    yield session
                finally:
                    # Always rollback - no data should persist between tests
                    await session.rollback()

            # Rollback the outer transaction
            await trans.rollback()

        await engine.dispose()
    else:
        # Use SQLite in-memory for unit tests
        engine = create_async_engine(
            "sqlite+aiosqlite:///:memory:",
            echo=False,
            poolclass=NullPool,
        )

        # Filter out PostgreSQL-only tables (not supported in SQLite)
        tables_to_create = [
            table for table in Base.metadata.sorted_tables
            if table.name not in TABLES_POSTGRES_ONLY
        ]

        async with engine.begin() as conn:
            for table in tables_to_create:
                await conn.run_sync(table.create, checkfirst=True)

        TestingSessionLocal = async_sessionmaker(
            engine,
            class_=AsyncSession,
            expire_on_commit=False,
        )

        async with TestingSessionLocal() as session:
            try:
                yield session
                await session.commit()
            except Exception:
                await session.rollback()
                raise

        async with engine.begin() as conn:
            for table in reversed(tables_to_create):
                await conn.run_sync(table.drop, checkfirst=True)

        await engine.dispose()


@pytest.fixture
async def client(test_db):
    """Cria cliente de teste FastAPI com banco de dados mockado (async)."""
    # Lazy imports
    from httpx import AsyncClient
    from sqlalchemy.ext.asyncio import AsyncSession
    from app.main import app
    from app.database import get_db

    async def override_get_db():
        try:
            yield test_db
        finally:
            pass

    app.dependency_overrides[get_db] = override_get_db

    async with AsyncClient(app=app, base_url="http://test") as test_client:
        yield test_client

    app.dependency_overrides.clear()


@pytest.fixture
def mock_redis(monkeypatch):
    """Mocka Redis para testes."""
    from app.core import cache
    mock_redis_client = MagicMock()
    mock_redis_client.get.return_value = None
    mock_redis_client.setex.return_value = True
    mock_redis_client.delete.return_value = True
    mock_redis_client.keys.return_value = []
    monkeypatch.setattr(cache, "get_redis_client", lambda: mock_redis_client)
    return mock_redis_client


@pytest.fixture
def sample_program_data():
    """Dados de exemplo para programa social.

    Usa código único para evitar conflito com dados existentes.
    """
    import uuid
    unique_id = uuid.uuid4().hex[:8]
    return {
        "code": f"TEST_PROGRAM_{unique_id}",
        "name": f"Programa de Teste {unique_id}",
        "description": "Programa de teste para testes automatizados",
        "is_active": True,
    }


@pytest.fixture
def sample_municipality_data():
    """Dados de exemplo para município.

    Usa código único para evitar conflito com dados existentes.
    """
    import uuid
    unique_id = uuid.uuid4().hex[:8]
    return {
        "ibge_code": f"99{unique_id[:5]}",  # Código fictício (não existe estado 99)
        "name": f"Município Teste {unique_id}",
        "state_id": 1,
        "population": 100000,
        "area_km2": 500.0,
    }


@pytest.fixture
def sample_state_data():
    """Dados de exemplo para estado.

    Usa código único para evitar conflito com dados existentes.
    """
    import uuid
    unique_id = uuid.uuid4().hex[:6]
    return {
        "ibge_code": f"9{unique_id[:1]}",  # Código fictício (90-99)
        "name": f"Estado Teste {unique_id}",
        "abbreviation": f"T{unique_id[:1].upper()}",
        "region": "TE",
    }
