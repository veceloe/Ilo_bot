"""
Основной модуль AI Bot Architect.

Точка входа для FastAPI приложения.
"""

import logging
from contextlib import asynccontextmanager
from typing import Dict, Any

from fastapi import FastAPI, HTTPException, BackgroundTasks
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse

from app.core.config import settings
from app.api.v1.api import api_router
from app.core.orchestrator import BotArchitectOrchestrator


# Настройка логирования
logging.basicConfig(
    level=getattr(logging, settings.log_level),
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s"
)
logger = logging.getLogger(__name__)

# Глобальный оркестратор
orchestrator: BotArchitectOrchestrator = None


@asynccontextmanager
async def lifespan(app: FastAPI):
    """Управление жизненным циклом приложения."""
    global orchestrator
    
    # Startup
    logger.info("Запуск AI Bot Architect...")
    
    # Инициализация оркестратора
    orchestrator = BotArchitectOrchestrator()
    await orchestrator.initialize()
    
    # Сохранение в состоянии приложения
    app.state.orchestrator = orchestrator
    
    logger.info("AI Bot Architect успешно запущен!")
    
    yield
    
    # Shutdown
    logger.info("Завершение работы AI Bot Architect...")
    
    if orchestrator:
        await orchestrator.shutdown()
    
    logger.info("AI Bot Architect остановлен.")


# Создание FastAPI приложения
app = FastAPI(
    title="AI Bot Architect",
    description="Революционная платформа для создания Telegram-ботов с помощью AI",
    version="1.0.0",
    docs_url="/docs" if settings.debug else None,
    redoc_url="/redoc" if settings.debug else None,
    lifespan=lifespan
)

# Настройка CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"] if settings.debug else ["https://yourdomain.com"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Подключение API роутеров
app.include_router(api_router, prefix="/api/v1")


@app.get("/")
async def root():
    """Корневой эндпоинт."""
    return {
        "message": "AI Bot Architect API",
        "version": "1.0.0",
        "status": "running",
        "docs": "/docs" if settings.debug else "disabled"
    }


@app.get("/health")
async def health_check():
    """Проверка здоровья приложения."""
    try:
        orchestrator_status = "healthy" if app.state.orchestrator else "not_initialized"
        
        return {
            "status": "healthy",
            "timestamp": "2024-01-01T00:00:00Z",
            "orchestrator": orchestrator_status,
            "environment": "development" if settings.debug else "production"
        }
    except Exception as e:
        logger.error(f"Health check failed: {e}")
        raise HTTPException(status_code=503, detail="Service unhealthy")


@app.post("/api/v1/create-bot")
async def create_bot_endpoint(
    request_data: Dict[str, Any],
    background_tasks: BackgroundTasks
):
    """
    Главный эндпоинт для создания ботов.
    
    Запускает полный цикл создания бота:
    1. Исследование предметной области
    2. Сбор требований
    3. Генерация кода
    4. Тестирование
    5. Развертывание
    """
    try:
        if not app.state.orchestrator:
            raise HTTPException(status_code=503, detail="Orchestrator not initialized")
        
        # Запуск процесса создания бота в фоновом режиме
        session_id = await app.state.orchestrator.start_bot_creation_session(request_data)
        
        return {
            "status": "started",
            "session_id": session_id,
            "message": "Процесс создания бота запущен",
            "progress_url": f"/api/v1/sessions/{session_id}/progress"
        }
        
    except Exception as e:
        logger.error(f"Error starting bot creation: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@app.get("/api/v1/sessions/{session_id}/progress")
async def get_session_progress(session_id: str):
    """Получение прогресса создания бота."""
    try:
        if not app.state.orchestrator:
            raise HTTPException(status_code=503, detail="Orchestrator not initialized")
        
        progress = await app.state.orchestrator.get_session_progress(session_id)
        
        if not progress:
            raise HTTPException(status_code=404, detail="Session not found")
        
        return progress
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error getting session progress: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@app.exception_handler(Exception)
async def global_exception_handler(request, exc):
    """Глобальный обработчик исключений."""
    logger.error(f"Unhandled exception: {exc}", exc_info=True)
    
    return JSONResponse(
        status_code=500,
        content={
            "error": "Internal server error",
            "detail": str(exc) if settings.debug else "Something went wrong"
        }
    )


if __name__ == "__main__":
    import uvicorn
    
    uvicorn.run(
        "app.main:app",
        host="0.0.0.0",
        port=8000,
        reload=settings.debug,
        log_level=settings.log_level.lower()
    )