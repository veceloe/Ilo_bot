"""
Основные API эндпоинты v1 для AI Bot Architect.
"""

from fastapi import APIRouter, HTTPException, Depends, BackgroundTasks
from typing import Dict, Any, List
from pydantic import BaseModel

from app.core.orchestrator import BotArchitectOrchestrator


# Создание роутера
api_router = APIRouter()


# Pydantic модели для API
class BotCreationRequest(BaseModel):
    """Запрос на создание бота."""
    description: str
    domain: str = ""
    target_audience: str = ""
    business_type: str = ""
    project_name: str = "telegram_bot"
    create_new_bot: bool = False
    deployment_config: Dict[str, Any] = {}


class BotCreationResponse(BaseModel):
    """Ответ на запрос создания бота."""
    status: str
    session_id: str
    message: str
    progress_url: str


class SessionProgressResponse(BaseModel):
    """Ответ с прогрессом сессии."""
    session_id: str
    status: str
    progress: int
    current_step: str
    created_at: str
    updated_at: str
    errors: List[str]
    final_result: Dict[str, Any] = None


class SessionDetailsResponse(BaseModel):
    """Детальная информация о сессии."""
    session_id: str
    status: str
    progress: int
    current_step: str
    created_at: str
    updated_at: str
    errors: List[str]
    final_result: Dict[str, Any] = None
    research_summary: List[str] = []
    requirements_summary: str = ""
    generated_files_count: int = 0
    quality_score: float = 0.0
    deployment_url: str = ""
    bot_username: str = ""


# Dependency для получения оркестратора
async def get_orchestrator() -> BotArchitectOrchestrator:
    """Получение экземпляра оркестратора."""
    # В реальном приложении это будет инжектиться из состояния FastAPI
    from app.main import app
    if hasattr(app, 'state') and hasattr(app.state, 'orchestrator'):
        return app.state.orchestrator
    raise HTTPException(status_code=503, detail="Orchestrator not available")


@api_router.post("/bots", response_model=BotCreationResponse)
async def create_bot(
    request: BotCreationRequest,
    background_tasks: BackgroundTasks,
    orchestrator: BotArchitectOrchestrator = Depends(get_orchestrator)
):
    """
    Создание нового Telegram-бота.
    
    Запускает полный цикл создания бота:
    1. Исследование предметной области
    2. Сбор требований
    3. Генерация кода
    4. Тестирование
    5. Развертывание
    """
    try:
        # Преобразование запроса в формат для оркестратора
        request_data = {
            "description": request.description,
            "domain": request.domain,
            "target_audience": request.target_audience,
            "business_type": request.business_type,
            "project_name": request.project_name,
            "create_new_bot": request.create_new_bot,
            "deployment_config": request.deployment_config
        }
        
        # Запуск процесса создания бота
        session_id = await orchestrator.start_bot_creation_session(request_data)
        
        return BotCreationResponse(
            status="started",
            session_id=session_id,
            message="Процесс создания бота запущен",
            progress_url=f"/api/v1/sessions/{session_id}/progress"
        )
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@api_router.get("/sessions/{session_id}/progress", response_model=SessionProgressResponse)
async def get_session_progress(
    session_id: str,
    orchestrator: BotArchitectOrchestrator = Depends(get_orchestrator)
):
    """Получение прогресса создания бота."""
    try:
        progress = await orchestrator.get_session_progress(session_id)
        
        if not progress:
            raise HTTPException(status_code=404, detail="Session not found")
        
        return SessionProgressResponse(**progress)
        
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@api_router.get("/sessions/{session_id}", response_model=SessionDetailsResponse)
async def get_session_details(
    session_id: str,
    orchestrator: BotArchitectOrchestrator = Depends(get_orchestrator)
):
    """Получение детальной информации о сессии."""
    try:
        details = await orchestrator.get_session_details(session_id)
        
        if not details:
            raise HTTPException(status_code=404, detail="Session not found")
        
        return SessionDetailsResponse(**details)
        
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@api_router.delete("/sessions/{session_id}")
async def cancel_session(
    session_id: str,
    orchestrator: BotArchitectOrchestrator = Depends(get_orchestrator)
):
    """Отмена сессии создания бота."""
    try:
        success = await orchestrator.cancel_session(session_id)
        
        if not success:
            raise HTTPException(status_code=404, detail="Session not found")
        
        return {"status": "cancelled", "session_id": session_id}
        
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@api_router.get("/sessions")
async def get_active_sessions(
    orchestrator: BotArchitectOrchestrator = Depends(get_orchestrator)
):
    """Получение списка активных сессий."""
    try:
        sessions = await orchestrator.get_active_sessions()
        return {"sessions": sessions, "count": len(sessions)}
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@api_router.post("/sessions/cleanup")
async def cleanup_old_sessions(
    max_age_hours: int = 24,
    orchestrator: BotArchitectOrchestrator = Depends(get_orchestrator)
):
    """Очистка старых сессий."""
    try:
        removed_count = await orchestrator.cleanup_old_sessions(max_age_hours)
        return {
            "status": "success",
            "removed_sessions": removed_count,
            "message": f"Удалено {removed_count} старых сессий"
        }
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@api_router.get("/stats")
async def get_system_stats(
    orchestrator: BotArchitectOrchestrator = Depends(get_orchestrator)
):
    """Получение статистики системы."""
    try:
        active_sessions = await orchestrator.get_active_sessions()
        
        # Подсчет статистики
        total_sessions = len(orchestrator.sessions)
        active_count = len(active_sessions)
        completed_count = sum(
            1 for session in orchestrator.sessions.values()
            if session.status.value == "completed"
        )
        failed_count = sum(
            1 for session in orchestrator.sessions.values()
            if session.status.value == "failed"
        )
        
        return {
            "total_sessions": total_sessions,
            "active_sessions": active_count,
            "completed_sessions": completed_count,
            "failed_sessions": failed_count,
            "success_rate": completed_count / max(total_sessions, 1) * 100,
            "orchestrator_initialized": orchestrator.is_initialized
        }
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


# Эндпоинты для работы с агентами (для отладки)
@api_router.get("/agents/status")
async def get_agents_status(
    orchestrator: BotArchitectOrchestrator = Depends(get_orchestrator)
):
    """Получение статуса всех агентов."""
    try:
        agents_status = {}
        
        for agent_name, agent in orchestrator.agents.items():
            if hasattr(agent, 'get_stats'):
                agents_status[agent_name] = agent.get_stats()
            else:
                agents_status[agent_name] = {
                    "status": "active",
                    "name": agent.name if hasattr(agent, 'name') else agent_name
                }
        
        return {
            "agents": agents_status,
            "total_agents": len(orchestrator.agents)
        }
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


# Эндпоинт для тестирования отдельных агентов
@api_router.post("/agents/{agent_name}/test")
async def test_agent(
    agent_name: str,
    test_data: Dict[str, Any],
    orchestrator: BotArchitectOrchestrator = Depends(get_orchestrator)
):
    """Тестирование отдельного агента."""
    try:
        if agent_name not in orchestrator.agents:
            raise HTTPException(status_code=404, detail=f"Agent '{agent_name}' not found")
        
        agent = orchestrator.agents[agent_name]
        result = await agent.process(test_data)
        
        return {
            "agent": agent_name,
            "test_result": result,
            "status": "success"
        }
        
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


# Здоровье API
@api_router.get("/health")
async def api_health():
    """Проверка здоровья API."""
    return {
        "status": "healthy",
        "api_version": "v1",
        "timestamp": "2024-01-01T00:00:00Z"
    }