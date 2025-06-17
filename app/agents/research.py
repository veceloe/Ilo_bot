"""
Research Agent - исследует предметную область и находит best practices.
"""

import logging
from typing import Any, Dict, List, Optional
import json

from .base import BaseAgent
from app.core.config import ModelConfig


logger = logging.getLogger(__name__)


class ResearchAgent(BaseAgent):
    """
    Агент для исследования предметной области и поиска лучших практик
    создания Telegram-ботов в конкретной нише.
    """

    def __init__(self):
        super().__init__(
            name="Research Agent",
            system_prompt=ModelConfig.RESEARCH_AGENT_SYSTEM_PROMPT + """
            
            Ваши основные задачи:
            1. Анализ предметной области пользователя
            2. Поиск существующих решений и best practices
            3. Идентификация ключевых функций и интеграций
            4. Анализ пользовательского опыта в данной нише
            5. Рекомендации по архитектуре и технологиям
            
            Всегда предоставляйте конкретные, практические рекомендации 
            с примерами и обоснованием.
            """,
            temperature=0.3  # Больше креативности для исследований
        )

    async def process(self, input_data: Dict[str, Any]) -> Dict[str, Any]:
        """
        Основной метод исследования предметной области.
        
        Args:
            input_data: {
                "domain": "описание предметной области",
                "user_description": "описание требований пользователя",
                "target_audience": "целевая аудитория",
                "business_type": "тип бизнеса"
            }
            
        Returns:
            Результат исследования с рекомендациями
        """
        try:
            domain = input_data.get("domain", "")
            user_description = input_data.get("user_description", "")
            target_audience = input_data.get("target_audience", "")
            business_type = input_data.get("business_type", "")

            # Формирование исследовательского запроса
            research_query = self._build_research_query(
                domain, user_description, target_audience, business_type
            )

            # Проведение исследования
            research_result = await self.generate_response(research_query)

            # Парсинг и структурирование результата
            structured_result = await self._structure_research_result(research_result)

            return {
                "status": "success",
                "research_data": structured_result,
                "recommendations": await self._generate_recommendations(structured_result),
                "competitive_analysis": await self._analyze_competitors(domain),
                "technical_insights": await self._get_technical_insights(domain)
            }

        except Exception as e:
            logger.error(f"Ошибка в исследовании: {e}")
            return {
                "status": "error",
                "error": str(e),
                "fallback_data": self._get_fallback_research_data()
            }

    def _build_research_query(
        self, 
        domain: str, 
        user_description: str, 
        target_audience: str, 
        business_type: str
    ) -> str:
        """Построение исследовательского запроса."""
        query = f"""
        Проведите глубокое исследование для создания Telegram-бота в следующей области:

        Предметная область: {domain}
        Описание проекта: {user_description}
        Целевая аудитория: {target_audience}
        Тип бизнеса: {business_type}

        Исследуйте следующие аспекты:

        1. АНАЛИЗ ПРЕДМЕТНОЙ ОБЛАСТИ:
        - Ключевые особенности и специфика ниши
        - Основные бизнес-процессы
        - Типичные задачи и проблемы пользователей
        - Регулятивные требования (если применимо)

        2. BEST PRACTICES:
        - Успешные примеры ботов в этой области
        - Эффективные UX/UI паттерны
        - Оптимальные пользовательские сценарии
        - Проверенные технические решения

        3. ФУНКЦИОНАЛЬНЫЕ ТРЕБОВАНИЯ:
        - Обязательные функции для данной ниши
        - Желательные дополнительные возможности
        - Интеграции с внешними сервисами
        - Требования к производительности

        4. ТЕХНИЧЕСКИЕ РЕКОМЕНДАЦИИ:
        - Подходящая архитектура
        - Необходимые интеграции
        - Рекомендации по базе данных
        - Соображения безопасности

        Предоставьте структурированный анализ в формате JSON.
        """
        return query

    async def _structure_research_result(self, research_text: str) -> Dict[str, Any]:
        """Структурирование результата исследования."""
        structuring_prompt = f"""
        Проанализируйте следующий исследовательский материал и структурируйте его в JSON формате:

        {research_text}

        Создайте структурированный JSON со следующими секциями:
        {{
            "domain_analysis": {{
                "key_features": [],
                "business_processes": [],
                "user_problems": [],
                "regulatory_requirements": []
            }},
            "best_practices": {{
                "successful_examples": [],
                "ux_patterns": [],
                "user_scenarios": [],
                "technical_solutions": []
            }},
            "functional_requirements": {{
                "mandatory_features": [],
                "optional_features": [],
                "integrations": [],
                "performance_requirements": []
            }},
            "technical_recommendations": {{
                "architecture": "",
                "database": "",
                "security": [],
                "scalability": []
            }}
        }}
        """

        structured_response = await self.generate_response(structuring_prompt)
        
        try:
            # Попытка распарсить JSON
            return json.loads(structured_response)
        except json.JSONDecodeError:
            # Fallback: создание базовой структуры
            return self._create_basic_structure(research_text)

    async def _generate_recommendations(self, research_data: Dict[str, Any]) -> List[str]:
        """Генерация конкретных рекомендаций."""
        recommendations_prompt = f"""
        На основе исследовательских данных:
        {json.dumps(research_data, ensure_ascii=False, indent=2)}

        Сгенерируйте 5-7 конкретных, действенных рекомендаций для создания 
        Telegram-бота в этой области. Каждая рекомендация должна содержать:
        - Конкретное действие
        - Обоснование
        - Ожидаемый результат

        Формат ответа: список строк с рекомендациями.
        """

        recommendations_text = await self.generate_response(recommendations_prompt)
        
        # Разбиение на отдельные рекомендации
        recommendations = [
            rec.strip() 
            for rec in recommendations_text.split('\n') 
            if rec.strip() and not rec.strip().startswith('•')
        ]
        
        return recommendations[:7]  # Максимум 7 рекомендаций

    async def _analyze_competitors(self, domain: str) -> Dict[str, Any]:
        """Анализ конкурентов в предметной области."""
        competitor_prompt = f"""
        Проанализируйте конкурентов и существующие решения в области: {domain}

        Найдите:
        1. Основных игроков на рынке
        2. Их ключевые особенности
        3. Преимущества и недостатки
        4. Возможности для дифференциации

        Представьте анализ в структурированном виде.
        """

        competitor_analysis = await self.generate_response(competitor_prompt)
        
        return {
            "analysis": competitor_analysis,
            "differentiation_opportunities": await self._find_differentiation_opportunities(
                domain, competitor_analysis
            )
        }

    async def _get_technical_insights(self, domain: str) -> Dict[str, Any]:
        """Получение технических инсайтов для предметной области."""
        technical_prompt = f"""
        Предоставьте технические инсайты для создания Telegram-бота в области: {domain}

        Включите:
        1. Специфичные технические требования
        2. Рекомендуемые библиотеки и фреймворки
        3. Паттерны архитектуры
        4. Соображения производительности
        5. Вопросы безопасности
        """

        technical_insights = await self.generate_response(technical_prompt)
        
        return {
            "insights": technical_insights,
            "recommended_technologies": self._extract_technologies(technical_insights)
        }

    async def _find_differentiation_opportunities(
        self, 
        domain: str, 
        competitor_analysis: str
    ) -> List[str]:
        """Поиск возможностей для дифференциации."""
        diff_prompt = f"""
        На основе анализа конкурентов:
        {competitor_analysis}

        Найдите 3-5 конкретных возможностей для создания уникального 
        предложения в области {domain}.
        """

        opportunities = await self.generate_response(diff_prompt)
        return [
            opp.strip() 
            for opp in opportunities.split('\n') 
            if opp.strip()
        ][:5]

    def _extract_technologies(self, technical_text: str) -> List[str]:
        """Извлечение рекомендуемых технологий из текста."""
        # Простой парсинг технологий (можно улучшить с помощью NLP)
        technologies = []
        lines = technical_text.split('\n')
        
        for line in lines:
            if any(keyword in line.lower() for keyword in ['библиотек', 'фреймворк', 'технологи', 'api']):
                # Извлечение названий в кавычках или после двоеточия
                import re
                tech_matches = re.findall(r'[A-Za-z0-9_-]+(?:\.[A-Za-z0-9_-]+)*', line)
                technologies.extend(tech_matches)
        
        return list(set(technologies))[:10]  # Уникальные, максимум 10

    def _create_basic_structure(self, research_text: str) -> Dict[str, Any]:
        """Создание базовой структуры при ошибке парсинга JSON."""
        return {
            "domain_analysis": {
                "key_features": ["Анализ предметной области"],
                "business_processes": ["Основные бизнес-процессы"],
                "user_problems": ["Типичные проблемы пользователей"],
                "regulatory_requirements": []
            },
            "best_practices": {
                "successful_examples": ["Требуется дополнительное исследование"],
                "ux_patterns": ["Стандартные паттерны UX"],
                "user_scenarios": ["Базовые пользовательские сценарии"],
                "technical_solutions": ["Проверенные технические решения"]
            },
            "functional_requirements": {
                "mandatory_features": ["Базовая функциональность"],
                "optional_features": ["Дополнительные возможности"],
                "integrations": ["Необходимые интеграции"],
                "performance_requirements": ["Стандартные требования производительности"]
            },
            "technical_recommendations": {
                "architecture": "Микросервисная архитектура",
                "database": "PostgreSQL",
                "security": ["Базовые меры безопасности"],
                "scalability": ["Горизонтальное масштабирование"]
            },
            "raw_research": research_text
        }

    def _get_fallback_research_data(self) -> Dict[str, Any]:
        """Базовые данные исследования при ошибке."""
        return {
            "status": "partial",
            "message": "Использованы базовые рекомендации",
            "basic_recommendations": [
                "Реализовать основные команды бота",
                "Добавить inline-клавиатуру для навигации",
                "Интегрировать базу данных для хранения состояний",
                "Реализовать обработку ошибок",
                "Добавить логирование действий пользователей"
            ]
        }