"""FastAPI application entry point for Tá na Mão API."""

from contextlib import asynccontextmanager

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from app.config import settings
from app.routers import municipalities, programs, aggregations, geo, agent, webhook, admin


@asynccontextmanager
async def lifespan(app: FastAPI):
    """Application lifespan events."""
    # Startup
    print(f"Starting {settings.APP_NAME} v{settings.APP_VERSION}")
    yield
    # Shutdown
    print("Shutting down...")


app = FastAPI(
    title=settings.APP_NAME,
    version=settings.APP_VERSION,
    description="""
    API para o Dashboard de Benefícios Sociais - Tá na Mão

    Fornece dados de penetração de programas sociais brasileiros
    com granularidade municipal (~5.570 municípios).

    ## Programas Rastreados
    - **TSEE** - Tarifa Social de Energia Elétrica
    - **Farmácia Popular** - Programa Farmácia Popular do Brasil
    - **Dignidade Menstrual** - Programa de Absorventes
    - **PIS/PASEP** - Cotas do PIS/PASEP
    - **CadÚnico** - Cadastro Único para Programas Sociais

    ## Agente Conversacional
    Inclui agente de IA para assistência ao cidadão via `/api/v1/agent/`
    """,
    lifespan=lifespan,
)

# Configure CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.CORS_ORIGINS,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Include routers
app.include_router(
    municipalities.router,
    prefix="/api/v1/municipalities",
    tags=["Municípios"],
)
app.include_router(
    programs.router,
    prefix="/api/v1/programs",
    tags=["Programas"],
)
app.include_router(
    aggregations.router,
    prefix="/api/v1/aggregations",
    tags=["Agregações"],
)
app.include_router(
    geo.router,
    prefix="/api/v1/geo",
    tags=["GeoJSON"],
)
app.include_router(
    agent.router,
    prefix="/api/v1/agent",
    tags=["Agente"],
)
app.include_router(
    webhook.router,
    prefix="/api/v1",
    tags=["Webhooks"],
)
app.include_router(
    admin.router,
    prefix="/api/v1/admin",
    tags=["Admin"],
)


@app.get("/", tags=["Health"])
async def root():
    """Root endpoint with API info."""
    return {
        "name": settings.APP_NAME,
        "version": settings.APP_VERSION,
        "status": "running",
        "docs": "/docs",
    }


@app.get("/health", tags=["Health"])
async def health_check():
    """Health check endpoint."""
    return {"status": "healthy"}
