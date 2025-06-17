"""
Базовый класс для всех AI агентов в системе AI Bot Architect.
"""

import logging
from abc import ABC, abstractmethod
from typing import Any, Dict, List, Optional, Union
from datetime import datetime

from anthropic import Anthropic
from openai import OpenAI

from app.core.config import settings, ModelConfig


logger = logging.getLogger(__name__)


class BaseAgent(ABC):
    """Базовый класс для всех AI агентов."""

    def __init__(
        self,
        name: str,
        system_prompt: str,
        use_claude: bool = True,
        temperature: float = 0.1,
        max_tokens: int = 4096
    ):
        """
        Инициализация базового агента.
        
        Args:
            name: Имя агента
            system_prompt: Системный промпт агента
            use_claude: Использовать Claude вместо OpenAI
            temperature: Температура генерации
            max_tokens: Максимальное количество токенов
        """
        self.name = name
        self.system_prompt = system_prompt
        self.use_claude = use_claude
        self.temperature = temperature
        self.max_tokens = max_tokens
        
        # Инициализация AI клиентов
        if self.use_claude:
            self.claude_client = Anthropic(api_key=settings.anthropic_api_key)
        else:
            self.openai_client = OpenAI(api_key=settings.openai_api_key)
        
        # История сообщений для контекста
        self.message_history: List[Dict[str, Any]] = []
        
        # Метрики агента
        self.stats = {
            "requests_count": 0,
            "total_tokens": 0,
            "errors_count": 0,
            "created_at": datetime.now()
        }
        
        logger.info(f"Инициализирован агент: {self.name}")

    async def generate_response(
        self, 
        user_message: str, 
        context: Optional[Dict[str, Any]] = None,
        preserve_history: bool = True
    ) -> str:
        """
        Генерация ответа от AI модели.
        
        Args:
            user_message: Сообщение пользователя
            context: Дополнительный контекст
            preserve_history: Сохранять ли историю сообщений
            
        Returns:
            Ответ от AI модели
        """
        try:
            # Подготовка сообщений
            messages = self._prepare_messages(user_message, context)
            
            # Генерация ответа
            if self.use_claude:
                response = await self._generate_claude_response(messages)
            else:
                response = await self._generate_openai_response(messages)
            
            # Сохранение в историю
            if preserve_history:
                self.message_history.append({
                    "user": user_message,
                    "assistant": response,
                    "timestamp": datetime.now(),
                    "context": context
                })
            
            # Обновление статистики
            self.stats["requests_count"] += 1
            
            return response
            
        except Exception as e:
            self.stats["errors_count"] += 1
            logger.error(f"Ошибка генерации ответа в агенте {self.name}: {e}")
            raise

    def _prepare_messages(
        self, 
        user_message: str, 
        context: Optional[Dict[str, Any]] = None
    ) -> List[Dict[str, str]]:
        """Подготовка сообщений для AI модели."""
        messages = [
            {"role": "system", "content": self.system_prompt}
        ]
        
        # Добавление контекста
        if context:
            context_message = self._format_context(context)
            messages.append({
                "role": "system", 
                "content": f"Дополнительный контекст: {context_message}"
            })
        
        # Добавление истории (последние 5 сообщений)
        for msg in self.message_history[-5:]:
            messages.extend([
                {"role": "user", "content": msg["user"]},
                {"role": "assistant", "content": msg["assistant"]}
            ])
        
        # Добавление текущего сообщения
        messages.append({"role": "user", "content": user_message})
        
        return messages

    async def _generate_claude_response(
        self, 
        messages: List[Dict[str, str]]
    ) -> str:
        """Генерация ответа через Claude API."""
        try:
            response = await self.claude_client.messages.create(
                model=ModelConfig.CLAUDE_MODEL,
                max_tokens=self.max_tokens,
                temperature=self.temperature,
                messages=[msg for msg in messages if msg["role"] != "system"],
                system=next(
                    (msg["content"] for msg in messages if msg["role"] == "system"), 
                    self.system_prompt
                )
            )
            
            return response.content[0].text
            
        except Exception as e:
            logger.error(f"Ошибка Claude API: {e}")
            raise

    async def _generate_openai_response(
        self, 
        messages: List[Dict[str, str]]
    ) -> str:
        """Генерация ответа через OpenAI API."""
        try:
            response = await self.openai_client.chat.completions.create(
                model=ModelConfig.OPENAI_MODEL,
                messages=messages,
                temperature=self.temperature,
                max_tokens=self.max_tokens
            )
            
            return response.choices[0].message.content
            
        except Exception as e:
            logger.error(f"Ошибка OpenAI API: {e}")
            raise

    def _format_context(self, context: Dict[str, Any]) -> str:
        """Форматирование контекста для включения в промпт."""
        formatted_context = []
        
        for key, value in context.items():
            if isinstance(value, (dict, list)):
                formatted_context.append(f"{key}: {str(value)[:200]}...")
            else:
                formatted_context.append(f"{key}: {value}")
        
        return "\n".join(formatted_context)

    def clear_history(self) -> None:
        """Очистка истории сообщений."""
        self.message_history.clear()
        logger.info(f"История агента {self.name} очищена")

    def get_stats(self) -> Dict[str, Any]:
        """Получение статистики агента."""
        return {
            **self.stats,
            "uptime": datetime.now() - self.stats["created_at"],
            "success_rate": (
                (self.stats["requests_count"] - self.stats["errors_count"]) 
                / max(self.stats["requests_count"], 1)
            )
        }

    @abstractmethod
    async def process(self, input_data: Dict[str, Any]) -> Dict[str, Any]:
        """
        Основной метод обработки данных агентом.
        
        Должен быть реализован в каждом наследующем классе.
        
        Args:
            input_data: Входные данные для обработки
            
        Returns:
            Результат обработки
        """
        pass

    def __repr__(self) -> str:
        return f"<{self.__class__.__name__}(name='{self.name}')>"