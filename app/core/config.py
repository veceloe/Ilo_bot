"""
Конфигурация приложения AI Bot Architect.
"""

import os
from typing import List, Optional

from pydantic import Field
from pydantic_settings import BaseSettings


class Settings(BaseSettings):
    """Основные настройки приложения."""

    # API Keys
    anthropic_api_key: str = Field(..., env="ANTHROPIC_API_KEY")
    openai_api_key: Optional[str] = Field(None, env="OPENAI_API_KEY")
    
    # Telegram Bot
    telegram_bot_token: str = Field(..., env="TELEGRAM_BOT_TOKEN")
    telegram_webhook_url: Optional[str] = Field(None, env="TELEGRAM_WEBHOOK_URL")
    bot_username: str = Field(..., env="BOT_USERNAME")
    
    # Database
    database_url: str = Field(..., env="DATABASE_URL")
    redis_url: str = Field(..., env="REDIS_URL")
    
    # Deployment
    timeweb_api_key: Optional[str] = Field(None, env="TIMEWEB_API_KEY")
    timeweb_project_id: Optional[str] = Field(None, env="TIMEWEB_PROJECT_ID")
    botfather_token: Optional[str] = Field(None, env="BOTFATHER_TOKEN")
    
    # Security
    jwt_secret_key: str = Field(..., env="JWT_SECRET_KEY")
    encryption_key: str = Field(..., env="ENCRYPTION_KEY")
    api_secret_key: str = Field(..., env="API_SECRET_KEY")
    
    # Application
    debug: bool = Field(True, env="DEBUG")
    log_level: str = Field("INFO", env="LOG_LEVEL")
    max_bot_generation_time: int = Field(300, env="MAX_BOT_GENERATION_TIME")
    max_requirements_iterations: int = Field(5, env="MAX_REQUIREMENTS_ITERATIONS")
    
    # External Services
    web_search_api_key: Optional[str] = Field(None, env="WEB_SEARCH_API_KEY")
    payment_provider_key: Optional[str] = Field(None, env="PAYMENT_PROVIDER_KEY")
    
    # File Upload
    upload_path: str = Field("./uploads", env="UPLOAD_PATH")
    max_file_size: int = Field(10485760, env="MAX_FILE_SIZE")  # 10MB
    allowed_extensions: List[str] = Field(
        ["txt", "pdf", "docx", "jpg", "png"], 
        env="ALLOWED_EXTENSIONS"
    )
    
    # Rate Limiting
    rate_limit_per_minute: int = Field(10, env="RATE_LIMIT_PER_MINUTE")
    rate_limit_per_hour: int = Field(100, env="RATE_LIMIT_PER_HOUR")
    
    # Monitoring
    sentry_dsn: Optional[str] = Field(None, env="SENTRY_DSN")
    metrics_enabled: bool = Field(True, env="METRICS_ENABLED")

    class Config:
        env_file = ".env"
        case_sensitive = False
        extra = "allow"

    @property
    def is_production(self) -> bool:
        """Проверка production окружения."""
        return not self.debug

    @property
    def database_url_sync(self) -> str:
        """Синхронный URL для базы данных (для Alembic)."""
        return self.database_url.replace("+asyncpg", "")


# Глобальная конфигурация
settings = Settings()


class ModelConfig:
    """Конфигурация для AI моделей."""
    
    # Claude настройки
    CLAUDE_MODEL = "claude-3-5-sonnet-20241022"
    CLAUDE_MAX_TOKENS = 4096
    CLAUDE_TEMPERATURE = 0.1
    
    # OpenAI настройки (резервная модель)
    OPENAI_MODEL = "gpt-4-turbo-preview"
    OPENAI_MAX_TOKENS = 4096
    OPENAI_TEMPERATURE = 0.1
    
    # Специализированные промпты
    RESEARCH_AGENT_SYSTEM_PROMPT = """
    Вы - Research Agent в системе AI Bot Architect. Ваша задача - исследовать предметную область 
    и находить best practices для создания Telegram-ботов в конкретной нише.
    """
    
    REQUIREMENTS_AGENT_SYSTEM_PROMPT = """
    Вы - Requirements Agent в системе AI Bot Architect. Ваша задача - собирать детальные требования 
    от пользователя и формировать техническое задание для создания бота.
    """
    
    CODE_GENERATION_AGENT_SYSTEM_PROMPT = """
    Вы - Code Generation Agent в системе AI Bot Architect. Ваша задача - создавать production-ready 
    код для Telegram-ботов на основе технического задания.
    """


class TelegramConfig:
    """Конфигурация для Telegram Bot API."""
    
    # Ограничения API
    MAX_MESSAGE_LENGTH = 4096
    MAX_CAPTION_LENGTH = 1024
    MAX_BUTTONS_PER_ROW = 8
    MAX_ROWS_PER_KEYBOARD = 100
    
    # Таймауты
    REQUEST_TIMEOUT = 30
    POLLING_TIMEOUT = 60
    
    # Webhook настройки
    WEBHOOK_PATH = "/webhook"
    WEBHOOK_SECRET_TOKEN_LENGTH = 32


# Экспорт основных настроек
__all__ = ["settings", "ModelConfig", "TelegramConfig"]