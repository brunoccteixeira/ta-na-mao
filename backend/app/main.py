"""FastAPI application entry point for Tá na Mão API."""

import traceback
from contextlib import asynccontextmanager

from fastapi import FastAPI, Request, status
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
from fastapi.exceptions import RequestValidationError
from sqlalchemy.exc import SQLAlchemyError

from app.config import settings
from app.core.logging import setup_logging, get_logger
from app.core.exceptions import TaNaMaoException
from app.middleware.metrics import MetricsMiddleware, get_metrics
from app.routers import municipalities, programs, aggregations, geo, agent, webhook, admin, nearby, sms, voice, carta, benefits_v2, partners, advisors, referrals
from app.agent.mcp import init_mcp, mcp_manager, BrasilAPIMCP, GoogleMapsMCP, PDFOcrMCP

# Setup structured logging
setup_logging(environment=settings.ENVIRONMENT)
logger = get_logger(__name__)


@asynccontextmanager
async def lifespan(app: FastAPI):
    """Application lifespan events."""
    # Startup
    logger.info(
        "application_starting",
        app_name=settings.APP_NAME,
        version=settings.APP_VERSION,
        environment=settings.ENVIRONMENT,
    )

    # Initialize MCP servers if enabled
    if settings.MCP_ENABLED:
        try:
            logger.info("mcp_initializing", config_path=settings.MCP_CONFIG_PATH)
            init_mcp(settings.MCP_CONFIG_PATH)

            # Register MCP wrappers
            mcp_manager.register_wrapper("brasil-api", BrasilAPIMCP)
            mcp_manager.register_wrapper("google-maps", GoogleMapsMCP)
            mcp_manager.register_wrapper("pdf-ocr", PDFOcrMCP)

            # Start all configured MCP servers
            results = await mcp_manager.start_all()
            for server_name, success in results.items():
                if success:
                    logger.info("mcp_server_started", server=server_name)
                else:
                    logger.warning("mcp_server_failed", server=server_name)

        except Exception as e:
            logger.error("mcp_initialization_failed", error=str(e))
            # Continue startup even if MCP fails - tools have fallbacks
    else:
        logger.info("mcp_disabled")

    yield

    # Shutdown
    if settings.MCP_ENABLED:
        try:
            logger.info("mcp_stopping")
            await mcp_manager.stop_all()
            logger.info("mcp_stopped")
        except Exception as e:
            logger.error("mcp_stop_failed", error=str(e))

    logger.info("application_shutting_down")


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

# Add metrics middleware
app.add_middleware(MetricsMiddleware)

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
app.include_router(
    nearby.router,
    prefix="/api/v1",
    tags=["Nearby Services"],
)
app.include_router(
    sms.router,
    prefix="/api/v1/sms",
    tags=["SMS"],
)
app.include_router(
    voice.router,
    prefix="/api/v1/voice",
    tags=["Voice"],
)
app.include_router(
    carta.router,
    tags=["Carta de Encaminhamento"],
)
app.include_router(
    benefits_v2.router,
    prefix="/api/v2/benefits",
    tags=["Benefícios (v2)"],
)
app.include_router(
    partners.router,
    prefix="/api/v1/partners",
    tags=["Parceiros"],
)
app.include_router(
    advisors.router,
    prefix="/api/v1/advisory",
    tags=["Anjo Social"],
)
app.include_router(
    referrals.router,
    prefix="/api/v1/referrals",
    tags=["Indicações"],
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
    """Health check endpoint with detailed status."""
    from app.database import engine
    from sqlalchemy import text
    import redis
    
    health_status = {
        "status": "healthy",
        "checks": {},
    }
    
    # Check database (async)
    try:
        async with engine.begin() as conn:
            await conn.execute(text("SELECT 1"))
        health_status["checks"]["database"] = "healthy"
    except Exception as e:
        health_status["status"] = "unhealthy"
        health_status["checks"]["database"] = f"unhealthy: {str(e)}"
        logger.error("health_check_database_failed", error=str(e))
    
    # Check Redis
    try:
        redis_client = redis.from_url(settings.REDIS_URL)
        redis_client.ping()
        health_status["checks"]["redis"] = "healthy"
    except Exception as e:
        health_status["status"] = "unhealthy"
        health_status["checks"]["redis"] = f"unhealthy: {str(e)}"
        logger.error("health_check_redis_failed", error=str(e))
    
    status_code = 200 if health_status["status"] == "healthy" else 503
    return JSONResponse(content=health_status, status_code=status_code)


@app.get("/metrics", tags=["Monitoring"])
async def metrics():
    """Prometheus metrics endpoint."""
    from fastapi.responses import Response
    return Response(content=get_metrics(), media_type="text/plain")


# Exception handlers
@app.exception_handler(TaNaMaoException)
async def tanamao_exception_handler(request: Request, exc: TaNaMaoException):
    """Handle custom Tá na Mão exceptions."""
    logger.error(
        "tanamao_exception",
        message=exc.message,
        status_code=exc.status_code,
        details=exc.details,
        path=request.url.path,
        method=request.method,
    )
    return JSONResponse(
        status_code=exc.status_code,
        content={
            "error": exc.message,
            "details": exc.details,
        },
    )


@app.exception_handler(RequestValidationError)
async def validation_exception_handler(request: Request, exc: RequestValidationError):
    """Handle request validation errors."""
    logger.warning(
        "validation_error",
        errors=exc.errors(),
        path=request.url.path,
        method=request.method,
    )
    return JSONResponse(
        status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
        content={
            "error": "Validation error",
            "details": exc.errors(),
        },
    )


@app.exception_handler(SQLAlchemyError)
async def database_exception_handler(request: Request, exc: SQLAlchemyError):
    """Handle database errors."""
    logger.error(
        "database_error",
        error=str(exc),
        error_type=type(exc).__name__,
        path=request.url.path,
        method=request.method,
        traceback=traceback.format_exc(),
    )
    return JSONResponse(
        status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
        content={
            "error": "Database error",
            "message": "An internal error occurred. Please try again later.",
        },
    )


@app.exception_handler(Exception)
async def general_exception_handler(request: Request, exc: Exception):
    """Handle all other exceptions."""
    logger.error(
        "unhandled_exception",
        error=str(exc),
        error_type=type(exc).__name__,
        path=request.url.path,
        method=request.method,
        traceback=traceback.format_exc(),
    )
    return JSONResponse(
        status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
        content={
            "error": "Internal server error",
            "message": "An unexpected error occurred. Please try again later.",
        },
    )


# Middleware for request logging
@app.middleware("http")
async def log_requests(request: Request, call_next):
    """Log all HTTP requests."""
    import uuid
    request_id = str(uuid.uuid4())
    
    from app.core.logging import bind_request_context
    bind_request_context(request_id=request_id)
    
    logger.info(
        "request_started",
        method=request.method,
        path=request.url.path,
        query_params=dict(request.query_params),
    )
    
    try:
        response = await call_next(request)
        logger.info(
            "request_completed",
            method=request.method,
            path=request.url.path,
            status_code=response.status_code,
        )
        return response
    except Exception as e:
        logger.error(
            "request_failed",
            method=request.method,
            path=request.url.path,
            error=str(e),
        )
        raise
    finally:
        from app.core.logging import clear_request_context
        clear_request_context()

