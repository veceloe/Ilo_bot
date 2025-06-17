"""
AI Агенты для создания Telegram-ботов.

Содержит специализированных агентов для различных этапов создания ботов:
- Research Agent: исследование предметной области
- Requirements Agent: сбор и анализ требований
- Code Generation Agent: генерация кода
- Testing Agent: тестирование ботов
- Deployment Agent: развертывание
"""

from .base import BaseAgent
from .research import ResearchAgent
from .requirements import RequirementsAgent
from .code_generation import CodeGenerationAgent
from .testing import TestingAgent
from .deployment import DeploymentAgent

__all__ = [
    "BaseAgent",
    "ResearchAgent", 
    "RequirementsAgent",
    "CodeGenerationAgent",
    "TestingAgent",
    "DeploymentAgent"
]