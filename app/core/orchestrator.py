"""
Главный оркестратор AI Bot Architect.

Управляет всеми агентами и workflow создания ботов.
"""

import logging
import asyncio
import uuid
from typing import Dict, Any, Optional, List
from datetime import datetime
from enum import Enum

from app.agents import (
    ResearchAgent,
    RequirementsAgent, 
    CodeGenerationAgent,
    TestingAgent,
    DeploymentAgent
)


logger = logging.getLogger(__name__)


class SessionStatus(Enum):
    """Статусы сессии создания бота."""
    INITIALIZING = "initializing"
    RESEARCH = "research"
    REQUIREMENTS = "requirements"
    CODE_GENERATION = "code_generation"
    TESTING = "testing"
    DEPLOYMENT = "deployment"
    COMPLETED = "completed"
    FAILED = "failed"


class BotCreationSession:
    """Сессия создания бота."""
    
    def __init__(self, session_id: str, initial_data: Dict[str, Any]):
        self.session_id = session_id
        self.status = SessionStatus.INITIALIZING
        self.created_at = datetime.now()
        self.updated_at = datetime.now()
        
        # Входные данные
        self.initial_data = initial_data
        
        # Данные этапов
        self.research_data: Optional[Dict[str, Any]] = None
        self.requirements_data: Optional[Dict[str, Any]] = None
        self.code_generation_data: Optional[Dict[str, Any]] = None
        self.testing_data: Optional[Dict[str, Any]] = None
        self.deployment_data: Optional[Dict[str, Any]] = None
        
        # Прогресс
        self.progress = 0
        self.current_step = "Инициализация"
        self.errors: List[str] = []
        
        # Результат
        self.final_result: Optional[Dict[str, Any]] = None

    def update_status(self, status: SessionStatus, progress: int, step: str):
        """Обновление статуса сессии."""
        self.status = status
        self.progress = progress
        self.current_step = step
        self.updated_at = datetime.now()

    def add_error(self, error: str):
        """Добавление ошибки."""
        self.errors.append(f"[{datetime.now().isoformat()}] {error}")
        logger.error(f"Session {self.session_id}: {error}")

    def to_dict(self) -> Dict[str, Any]:
        """Преобразование сессии в словарь."""
        return {
            "session_id": self.session_id,
            "status": self.status.value,
            "progress": self.progress,
            "current_step": self.current_step,
            "created_at": self.created_at.isoformat(),
            "updated_at": self.updated_at.isoformat(),
            "errors": self.errors,
            "final_result": self.final_result
        }


class BotArchitectOrchestrator:
    """
    Главный оркестратор для управления процессом создания ботов.
    
    Координирует работу всех агентов в правильной последовательности.
    """

    def __init__(self):
        self.sessions: Dict[str, BotCreationSession] = {}
        self.agents: Dict[str, Any] = {}
        self.is_initialized = False

    async def initialize(self):
        """Инициализация оркестратора и всех агентов."""
        logger.info("Инициализация оркестратора...")
        
        try:
            # Создание агентов
            self.agents = {
                "research": ResearchAgent(),
                "requirements": RequirementsAgent(),
                "code_generation": CodeGenerationAgent(),
                "testing": TestingAgent(),
                "deployment": DeploymentAgent()
            }
            
            self.is_initialized = True
            logger.info("Оркестратор успешно инициализирован")
            
        except Exception as e:
            logger.error(f"Ошибка инициализации оркестратора: {e}")
            raise

    async def shutdown(self):
        """Завершение работы оркестратора."""
        logger.info("Завершение работы оркестратора...")
        
        # Очистка ресурсов
        self.sessions.clear()
        self.agents.clear()
        self.is_initialized = False
        
        logger.info("Оркестратор остановлен")

    async def start_bot_creation_session(self, request_data: Dict[str, Any]) -> str:
        """
        Запуск новой сессии создания бота.
        
        Args:
            request_data: Начальные данные от пользователя
            
        Returns:
            ID созданной сессии
        """
        if not self.is_initialized:
            raise RuntimeError("Orchestrator not initialized")

        # Создание новой сессии
        session_id = str(uuid.uuid4())
        session = BotCreationSession(session_id, request_data)
        self.sessions[session_id] = session
        
        logger.info(f"Создана новая сессия: {session_id}")
        
        # Запуск workflow в фоновом режиме
        asyncio.create_task(self._run_bot_creation_workflow(session))
        
        return session_id

    async def get_session_progress(self, session_id: str) -> Optional[Dict[str, Any]]:
        """Получение прогресса сессии."""
        session = self.sessions.get(session_id)
        return session.to_dict() if session else None

    async def _run_bot_creation_workflow(self, session: BotCreationSession):
        """
        Основной workflow создания бота.
        
        Последовательно выполняет все этапы:
        1. Research
        2. Requirements gathering  
        3. Code generation
        4. Testing
        5. Deployment
        """
        try:
            logger.info(f"Запуск workflow для сессии {session.session_id}")

            # Этап 1: Исследование предметной области
            await self._run_research_stage(session)
            
            # Этап 2: Сбор требований
            await self._run_requirements_stage(session)
            
            # Этап 3: Генерация кода
            await self._run_code_generation_stage(session)
            
            # Этап 4: Тестирование
            await self._run_testing_stage(session)
            
            # Этап 5: Развертывание
            await self._run_deployment_stage(session)
            
            # Завершение
            session.update_status(SessionStatus.COMPLETED, 100, "Завершено")
            logger.info(f"Workflow для сессии {session.session_id} успешно завершен")

        except Exception as e:
            session.add_error(f"Ошибка workflow: {e}")
            session.update_status(SessionStatus.FAILED, session.progress, f"Ошибка: {e}")
            logger.error(f"Workflow для сессии {session.session_id} завершен с ошибкой: {e}")

    async def _run_research_stage(self, session: BotCreationSession):
        """Этап исследования предметной области."""
        session.update_status(SessionStatus.RESEARCH, 10, "Исследование предметной области")
        
        research_agent = self.agents["research"]
        
        # Подготовка данных для исследования
        research_input = {
            "domain": session.initial_data.get("domain", ""),
            "user_description": session.initial_data.get("description", ""),
            "target_audience": session.initial_data.get("target_audience", ""),
            "business_type": session.initial_data.get("business_type", "")
        }
        
        # Проведение исследования
        research_result = await research_agent.process(research_input)
        
        if research_result.get("status") == "success":
            session.research_data = research_result
            session.update_status(SessionStatus.RESEARCH, 20, "Исследование завершено")
        else:
            raise Exception(f"Ошибка исследования: {research_result.get('error', 'Unknown error')}")

    async def _run_requirements_stage(self, session: BotCreationSession):
        """Этап сбора требований."""
        session.update_status(SessionStatus.REQUIREMENTS, 25, "Анализ требований")
        
        requirements_agent = self.agents["requirements"]
        
        # Подготовка данных для анализа требований
        requirements_input = {
            "user_input": session.initial_data.get("description", ""),
            "research_data": session.research_data,
            "stage": "analysis"
        }
        
        # Проведение анализа требований
        requirements_result = await requirements_agent.process(requirements_input)
        
        if requirements_result.get("status") in ["success", "complete"]:
            session.requirements_data = requirements_result
            session.update_status(SessionStatus.REQUIREMENTS, 40, "Требования собраны")
        else:
            raise Exception(f"Ошибка сбора требований: {requirements_result.get('error', 'Unknown error')}")

    async def _run_code_generation_stage(self, session: BotCreationSession):
        """Этап генерации кода."""
        session.update_status(SessionStatus.CODE_GENERATION, 45, "Генерация кода")
        
        code_agent = self.agents["code_generation"]
        
        # Подготовка данных для генерации кода
        code_input = {
            "technical_specification": session.requirements_data.get("technical_specification", {}),
            "research_data": session.research_data,
            "requirements_summary": session.requirements_data.get("requirements_summary", ""),
            "project_name": session.initial_data.get("project_name", "telegram_bot")
        }
        
        # Генерация кода
        code_result = await code_agent.process(code_input)
        
        if code_result.get("status") == "success":
            session.code_generation_data = code_result
            session.update_status(SessionStatus.CODE_GENERATION, 65, "Код сгенерирован")
        else:
            raise Exception(f"Ошибка генерации кода: {code_result.get('error', 'Unknown error')}")

    async def _run_testing_stage(self, session: BotCreationSession):
        """Этап тестирования."""
        session.update_status(SessionStatus.TESTING, 70, "Тестирование кода")
        
        testing_agent = self.agents["testing"]
        
        # Подготовка данных для тестирования
        testing_input = {
            "generated_files": session.code_generation_data.get("generated_files", {}),
            "technical_specification": session.requirements_data.get("technical_specification", {}),
            "project_structure": session.code_generation_data.get("project_structure", {}),
            "archive_path": session.code_generation_data.get("archive_path", "")
        }
        
        # Проведение тестирования
        testing_result = await testing_agent.process(testing_input)
        
        if testing_result.get("status") == "success":
            session.testing_data = testing_result
            
            # Проверка качества
            quality_score = testing_result.get("quality_score", 0)
            if quality_score >= 70:  # Минимальный приемлемый балл
                session.update_status(SessionStatus.TESTING, 85, f"Тестирование пройдено (качество: {quality_score}%)")
            else:
                raise Exception(f"Код не прошел проверку качества (балл: {quality_score}%)")
        else:
            raise Exception(f"Ошибка тестирования: {testing_result.get('error', 'Unknown error')}")

    async def _run_deployment_stage(self, session: BotCreationSession):
        """Этап развертывания."""
        session.update_status(SessionStatus.DEPLOYMENT, 90, "Развертывание")
        
        deployment_agent = self.agents["deployment"]
        
        # Подготовка данных для развертывания
        deployment_input = {
            "archive_path": session.code_generation_data.get("archive_path", ""),
            "technical_specification": session.requirements_data.get("technical_specification", {}),
            "project_name": session.initial_data.get("project_name", "telegram_bot"),
            "deployment_config": session.initial_data.get("deployment_config", {}),
            "create_new_bot": session.initial_data.get("create_new_bot", False)
        }
        
        # Развертывание
        deployment_result = await deployment_agent.process(deployment_input)
        
        if deployment_result.get("status") == "success":
            session.deployment_data = deployment_result
            
            # Сохранение финального результата
            session.final_result = {
                "bot_url": deployment_result.get("deployment_url", ""),
                "bot_username": deployment_result.get("bot_username", ""),
                "dashboard_url": deployment_result.get("dashboard_url", ""),
                "management_instructions": deployment_result.get("management_instructions", []),
                "quality_score": session.testing_data.get("quality_score", 0),
                "generated_files_count": len(session.code_generation_data.get("generated_files", {})),
                "deployment_logs": deployment_result.get("deployment_logs", [])
            }
            
            session.update_status(SessionStatus.DEPLOYMENT, 95, "Развертывание завершено")
        else:
            raise Exception(f"Ошибка развертывания: {deployment_result.get('error', 'Unknown error')}")

    async def get_session_details(self, session_id: str) -> Optional[Dict[str, Any]]:
        """Получение детальной информации о сессии."""
        session = self.sessions.get(session_id)
        if not session:
            return None

        details = session.to_dict()
        
        # Добавление дополнительных данных
        if session.research_data:
            details["research_summary"] = session.research_data.get("recommendations", [])
        
        if session.requirements_data:
            details["requirements_summary"] = session.requirements_data.get("requirements_summary", "")
        
        if session.code_generation_data:
            details["generated_files_count"] = len(session.code_generation_data.get("generated_files", {}))
        
        if session.testing_data:
            details["quality_score"] = session.testing_data.get("quality_score", 0)
            details["test_results"] = session.testing_data.get("test_results", {})
        
        if session.deployment_data:
            details["deployment_url"] = session.deployment_data.get("deployment_url", "")
            details["bot_username"] = session.deployment_data.get("bot_username", "")
        
        return details

    async def cancel_session(self, session_id: str) -> bool:
        """Отмена сессии."""
        session = self.sessions.get(session_id)
        if not session:
            return False
        
        session.update_status(SessionStatus.FAILED, session.progress, "Отменено пользователем")
        logger.info(f"Сессия {session_id} отменена")
        return True

    async def get_active_sessions(self) -> List[Dict[str, Any]]:
        """Получение списка активных сессий."""
        active_statuses = {SessionStatus.INITIALIZING, SessionStatus.RESEARCH, 
                          SessionStatus.REQUIREMENTS, SessionStatus.CODE_GENERATION,
                          SessionStatus.TESTING, SessionStatus.DEPLOYMENT}
        
        active_sessions = [
            session.to_dict() 
            for session in self.sessions.values() 
            if session.status in active_statuses
        ]
        
        return active_sessions

    async def cleanup_old_sessions(self, max_age_hours: int = 24):
        """Очистка старых сессий."""
        current_time = datetime.now()
        sessions_to_remove = []
        
        for session_id, session in self.sessions.items():
            age_hours = (current_time - session.created_at).total_seconds() / 3600
            if age_hours > max_age_hours:
                sessions_to_remove.append(session_id)
        
        for session_id in sessions_to_remove:
            del self.sessions[session_id]
            logger.info(f"Удалена старая сессия: {session_id}")
        
        return len(sessions_to_remove)