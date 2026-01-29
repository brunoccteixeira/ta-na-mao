"""Application configuration using Pydantic Settings."""

from functools import lru_cache

from pydantic_settings import BaseSettings


class Settings(BaseSettings):
    """Application settings loaded from environment variables."""

    # Application
    APP_NAME: str = "Tá na Mão API"
    APP_VERSION: str = "0.1.0"
    ENVIRONMENT: str = "development"
    DEBUG: bool = True

    # Database
    DATABASE_URL: str = "postgresql://tanamao:tanamao_dev_2024@localhost:5432/tanamao"

    # Redis
    REDIS_URL: str = "redis://localhost:6379/0"

    # CORS
    CORS_ORIGINS: list[str] = ["http://localhost:3000", "http://localhost:3001", "http://localhost:5173"]

    # External APIs
    IBGE_API_BASE_URL: str = "https://servicodados.ibge.gov.br/api/v3"
    IBGE_LOCALIDADES_URL: str = "https://servicodados.ibge.gov.br/api/v1/localidades"

    # Cache TTLs (seconds)
    CACHE_TTL_GEOJSON: int = 86400  # 24 hours
    CACHE_TTL_AGGREGATIONS: int = 3600  # 1 hour
    CACHE_TTL_MUNICIPALITIES: int = 1800  # 30 minutes

    # Agent (Gemini)
    GOOGLE_API_KEY: str = ""  # Chave da API do Google AI Studio
    AGENT_MODEL: str = "gemini-2.0-flash-exp"  # Modelo Gemini a usar

    # Twilio (WhatsApp, SMS, Voice)
    TWILIO_ACCOUNT_SID: str = ""  # Account SID do Twilio
    TWILIO_AUTH_TOKEN: str = ""  # Auth Token do Twilio
    TWILIO_WHATSAPP_FROM: str = "whatsapp:+14155238886"  # Numero WhatsApp (sandbox padrao)
    TWILIO_WEBHOOK_URL: str = ""  # URL do webhook para respostas
    TWILIO_SMS_FROM: str = ""  # Numero para SMS
    TWILIO_VOICE_FROM: str = ""  # Numero para Voice (0800)

    # SMS Provider (twilio, zenvia, infobip)
    SMS_PROVIDER: str = "twilio"

    # Zenvia (alternativa para SMS)
    ZENVIA_API_TOKEN: str = ""
    ZENVIA_SMS_FROM: str = ""  # Numero curto (ex: 28282)

    # Voice/TTS
    VOICE_PROVIDER: str = "twilio"
    VOICE_LANGUAGE: str = "pt-BR"
    VOICE_VOICE: str = "Polly.Camila"  # Amazon Polly voice

    # Webhook base URL (para configurar nos provedores)
    WEBHOOK_BASE_URL: str = ""

    # MCP Configuration
    MCP_ENABLED: bool = True
    MCP_CONFIG_PATH: str = ".mcp.json"
    MCP_TIMEOUT: int = 30000  # ms

    class Config:
        env_file = ".env"
        env_file_encoding = "utf-8"
    
    def validate_critical_settings(self) -> None:
        """Validate critical settings on startup.
        
        Raises:
            ValueError: If critical settings are missing or invalid
        """
        errors = []
        
        # Validate database URL
        if not self.DATABASE_URL or "postgresql" not in self.DATABASE_URL:
            errors.append("DATABASE_URL must be a valid PostgreSQL connection string")
        
        # Validate Redis URL
        if not self.REDIS_URL or "redis" not in self.REDIS_URL:
            errors.append("REDIS_URL must be a valid Redis connection string")
        
        # Validate environment
        if self.ENVIRONMENT not in ["development", "staging", "production"]:
            errors.append("ENVIRONMENT must be one of: development, staging, production")
        
        # Production-specific validations
        if self.ENVIRONMENT == "production":
            if not self.GOOGLE_API_KEY:
                errors.append("GOOGLE_API_KEY is required in production")
            if not self.TWILIO_ACCOUNT_SID:
                errors.append("TWILIO_ACCOUNT_SID is required in production")
            if not self.TWILIO_AUTH_TOKEN:
                errors.append("TWILIO_AUTH_TOKEN is required in production")
            if not self.CORS_ORIGINS or len(self.CORS_ORIGINS) == 0:
                errors.append("CORS_ORIGINS must be configured in production")
        
        if errors:
            raise ValueError(f"Configuration errors: {', '.join(errors)}")


@lru_cache()
def get_settings() -> Settings:
    """Get cached settings instance."""
    settings = Settings()
    # Validate on first access
    settings.validate_critical_settings()
    return settings


settings = get_settings()
