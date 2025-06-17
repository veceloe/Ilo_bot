"""
Requirements Agent - собирает детальные требования и формирует техническое задание.
"""

import logging
from typing import Any, Dict, List, Optional, Tuple
import json
from datetime import datetime

from .base import BaseAgent
from app.core.config import ModelConfig, settings


logger = logging.getLogger(__name__)


class RequirementsAgent(BaseAgent):
    """
    Агент для сбора детальных требований от пользователя 
    и формирования технического задания.
    """

    def __init__(self):
        super().__init__(
            name="Requirements Agent",
            system_prompt=ModelConfig.REQUIREMENTS_AGENT_SYSTEM_PROMPT + """
            
            Ваши основные задачи:
            1. Проведение интервью с пользователем для сбора требований
            2. Выявление скрытых потребностей и edge cases
            3. Валидация технической реализуемости
            4. Формирование детального технического задания
            5. Определение приоритетов функций
            
            Принципы работы:
            - Задавайте конкретные, целенаправленные вопросы
            - Избегайте технического жаргона при общении с пользователем
            - Всегда уточняйте детали и edge cases
            - Предлагайте лучшие практики и альтернативы
            
            Формат общения: дружелюбный, профессиональный, понятный.
            """,
            temperature=0.2  # Низкая температура для точности
        )
        
        self.requirements_data: Dict[str, Any] = {}
        self.interview_stage = "initial"
        self.max_iterations = settings.max_requirements_iterations

    async def process(self, input_data: Dict[str, Any]) -> Dict[str, Any]:
        """
        Основной метод сбора требований.
        
        Args:
            input_data: {
                "user_input": "сообщение пользователя",
                "stage": "этап интервью",
                "research_data": "данные исследования",
                "conversation_history": "история диалога"
            }
            
        Returns:
            Результат с вопросами или финальным ТЗ
        """
        try:
            user_input = input_data.get("user_input", "")
            stage = input_data.get("stage", "initial")
            research_data = input_data.get("research_data", {})
            conversation_history = input_data.get("conversation_history", [])

            # Обновление внутреннего состояния
            self.interview_stage = stage
            if research_data:
                self.requirements_data["research"] = research_data

            # Анализ входящего сообщения пользователя
            if user_input:
                await self._process_user_input(user_input)

            # Определение следующего действия
            if self._is_requirements_complete():
                # Формирование финального ТЗ
                technical_specification = await self._generate_technical_specification()
                return {
                    "status": "complete",
                    "technical_specification": technical_specification,
                    "requirements_summary": await self._generate_requirements_summary(),
                    "next_action": "code_generation"
                }
            else:
                # Генерация следующих вопросов
                questions = await self._generate_next_questions()
                return {
                    "status": "in_progress",
                    "questions": questions,
                    "progress": self._calculate_progress(),
                    "next_action": "continue_interview",
                    "suggestions": await self._generate_suggestions()
                }

        except Exception as e:
            logger.error(f"Ошибка в сборе требований: {e}")
            return {
                "status": "error",
                "error": str(e),
                "fallback_questions": self._get_fallback_questions()
            }

    async def _process_user_input(self, user_input: str) -> None:
        """Обработка и анализ ввода пользователя."""
        analysis_prompt = f"""
        Проанализируйте ответ пользователя на предыдущие вопросы:
        "{user_input}"

        Текущие собранные требования:
        {json.dumps(self.requirements_data, ensure_ascii=False, indent=2)}

        Извлеките и структурируйте новую информацию в следующих категориях:
        1. Функциональные требования
        2. Пользователи и роли
        3. Бизнес-процессы
        4. Интеграции
        5. Ограничения и требования к производительности
        6. UI/UX предпочтения

        Верните JSON с обновленными данными.
        """

        analysis_result = await self.generate_response(analysis_prompt)
        
        try:
            new_data = json.loads(analysis_result)
            self._merge_requirements_data(new_data)
        except json.JSONDecodeError:
            # Простой парсинг при ошибке JSON
            await self._simple_text_parsing(user_input, analysis_result)

    def _merge_requirements_data(self, new_data: Dict[str, Any]) -> None:
        """Объединение новых данных с существующими требованиями."""
        for category, data in new_data.items():
            if category not in self.requirements_data:
                self.requirements_data[category] = {}
                
            if isinstance(data, dict):
                self.requirements_data[category].update(data)
            elif isinstance(data, list):
                existing = self.requirements_data[category].get("items", [])
                self.requirements_data[category]["items"] = existing + data
            else:
                self.requirements_data[category]["value"] = data

    async def _simple_text_parsing(self, user_input: str, analysis: str) -> None:
        """Простой парсинг текста при ошибке JSON."""
        # Базовое извлечение ключевых слов и фраз
        if "функция" in user_input.lower() or "возможность" in user_input.lower():
            if "functions" not in self.requirements_data:
                self.requirements_data["functions"] = []
            self.requirements_data["functions"].append(user_input)

        if "пользователь" in user_input.lower() or "клиент" in user_input.lower():
            if "users" not in self.requirements_data:
                self.requirements_data["users"] = []
            self.requirements_data["users"].append(user_input)

    async def _generate_next_questions(self) -> List[str]:
        """Генерация следующих вопросов для пользователя."""
        context = {
            "current_data": self.requirements_data,
            "stage": self.interview_stage,
            "progress": self._calculate_progress()
        }

        questions_prompt = f"""
        На основе текущих собранных требований:
        {json.dumps(self.requirements_data, ensure_ascii=False, indent=2)}

        Этап интервью: {self.interview_stage}
        Прогресс: {self._calculate_progress():.1%}

        Сгенерируйте 2-3 важных вопроса для более детального понимания проекта.
        
        Приоритеты для вопросов:
        1. Критически важные недостающие детали
        2. Уточнение бизнес-логики
        3. Технические ограничения
        4. Пользовательский опыт
        5. Edge cases и исключения

        Формат: список четких, понятных вопросов без технического жаргона.
        Каждый вопрос должен помочь собрать конкретную недостающую информацию.
        """

        questions_response = await self.generate_response(questions_prompt)
        
        # Парсинг вопросов
        questions = [
            q.strip().lstrip('1234567890.-• ')
            for q in questions_response.split('\n')
            if q.strip() and '?' in q
        ]
        
        return questions[:3]  # Максимум 3 вопроса за раз

    async def _generate_suggestions(self) -> List[str]:
        """Генерация предложений и рекомендаций для пользователя."""
        suggestions_prompt = f"""
        На основе текущих требований:
        {json.dumps(self.requirements_data, ensure_ascii=False, indent=2)}

        Предложите 2-3 полезных рекомендации или дополнительных возможности,
        которые пользователь мог не учесть, но которые улучшат его бот.

        Формат: конкретные, практичные предложения с кратким объяснением пользы.
        """

        suggestions_response = await self.generate_response(suggestions_prompt)
        
        return [
            s.strip().lstrip('1234567890.-• ')
            for s in suggestions_response.split('\n')
            if s.strip()
        ][:3]

    def _is_requirements_complete(self) -> bool:
        """Проверка готовности требований для генерации ТЗ."""
        required_categories = [
            "functions",      # Основные функции
            "users",         # Типы пользователей
            "business_logic" # Бизнес-логика
        ]
        
        # Базовая проверка наличия ключевых категорий
        has_required = all(
            category in self.requirements_data 
            for category in required_categories
        )
        
        # Проверка достаточности деталей
        has_details = (
            len(str(self.requirements_data)) > 500 and  # Достаточно деталей
            self._calculate_progress() > 0.7  # Прогресс более 70%
        )
        
        return has_required and has_details

    def _calculate_progress(self) -> float:
        """Расчет прогресса сбора требований (0.0 - 1.0)."""
        total_categories = 10  # Общее количество желаемых категорий
        current_categories = len(self.requirements_data)
        
        # Базовый прогресс по количеству категорий
        category_progress = min(current_categories / total_categories, 1.0)
        
        # Дополнительный вес за детализацию
        detail_weight = min(len(str(self.requirements_data)) / 2000, 1.0)
        
        return (category_progress * 0.7) + (detail_weight * 0.3)

    async def _generate_technical_specification(self) -> Dict[str, Any]:
        """Генерация финального технического задания."""
        spec_prompt = f"""
        На основе собранных требований создайте детальное техническое задание:
        {json.dumps(self.requirements_data, ensure_ascii=False, indent=2)}

        Структура ТЗ:
        {{
            "project_overview": {{
                "name": "Название проекта",
                "description": "Описание",
                "target_audience": "Целевая аудитория",
                "business_goals": []
            }},
            "functional_requirements": {{
                "core_features": [],
                "optional_features": [],
                "user_roles": [],
                "user_scenarios": []
            }},
            "technical_requirements": {{
                "architecture": "Архитектура",
                "database_schema": {{}},
                "integrations": [],
                "performance": {{}},
                "security": []
            }},
            "ui_ux_requirements": {{
                "interface_type": "Тип интерфейса",
                "navigation": "Навигация",
                "design_principles": []
            }},
            "deployment": {{
                "hosting": "Хостинг",
                "scalability": "Масштабируемость",
                "monitoring": []
            }},
            "timeline": {{
                "phases": [],
                "milestones": []
            }}
        }}

        Создайте подробное, реализуемое ТЗ в формате JSON.
        """

        spec_response = await self.generate_response(spec_prompt)
        
        try:
            return json.loads(spec_response)
        except json.JSONDecodeError:
            return self._create_fallback_specification()

    async def _generate_requirements_summary(self) -> str:
        """Генерация краткого резюме требований."""
        summary_prompt = f"""
        Создайте краткое, понятное резюме проекта на основе собранных требований:
        {json.dumps(self.requirements_data, ensure_ascii=False, indent=2)}

        Резюме должно включать:
        1. Основная цель проекта
        2. Ключевые функции (3-5 основных)
        3. Целевая аудитория
        4. Особенности и уникальность

        Формат: 2-3 абзаца, понятный язык.
        """

        return await self.generate_response(summary_prompt)

    def _create_fallback_specification(self) -> Dict[str, Any]:
        """Создание базового ТЗ при ошибке."""
        return {
            "project_overview": {
                "name": "Telegram Bot",
                "description": "Пользовательский Telegram-бот",
                "target_audience": "Пользователи Telegram",
                "business_goals": ["Автоматизация процессов", "Улучшение клиентского сервиса"]
            },
            "functional_requirements": {
                "core_features": [
                    "Обработка команд",
                    "Интерактивная клавиатура",
                    "Хранение данных пользователей"
                ],
                "optional_features": [],
                "user_roles": ["Пользователь", "Администратор"],
                "user_scenarios": ["Регистрация", "Основное взаимодействие"]
            },
            "technical_requirements": {
                "architecture": "Монолитная архитектура",
                "database_schema": {"users": {}, "sessions": {}},
                "integrations": [],
                "performance": {"response_time": "< 2 секунд"},
                "security": ["Базовая авторизация", "Валидация данных"]
            },
            "ui_ux_requirements": {
                "interface_type": "Conversational UI",
                "navigation": "Inline клавиатура",
                "design_principles": ["Простота", "Интуитивность"]
            },
            "deployment": {
                "hosting": "Timeweb Cloud",
                "scalability": "Горизонтальное масштабирование",
                "monitoring": ["Логирование", "Метрики производительности"]
            },
            "timeline": {
                "phases": ["Разработка", "Тестирование", "Развертывание"],
                "milestones": ["MVP", "Beta", "Release"]
            },
            "source_data": self.requirements_data
        }

    def _get_fallback_questions(self) -> List[str]:
        """Базовые вопросы при ошибке."""
        return [
            "Какую основную задачу должен решать ваш бот?",
            "Кто будет основными пользователями бота?",
            "Какие действия пользователи смогут выполнять через бота?"
        ]

    def reset_session(self) -> None:
        """Сброс сессии для нового интервью."""
        self.requirements_data.clear()
        self.interview_stage = "initial"
        self.clear_history()
        logger.info("Сессия сбора требований сброшена")