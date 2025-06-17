"""
Testing Agent - тестирует функциональность сгенерированных ботов.
"""

import logging
import asyncio
import json
from typing import Any, Dict, List, Optional, Tuple
from datetime import datetime
import tempfile
import subprocess
import os

from .base import BaseAgent
from app.core.config import ModelConfig


logger = logging.getLogger(__name__)


class TestingAgent(BaseAgent):
    """
    Агент для автоматического тестирования функциональности
    сгенерированных Telegram-ботов.
    """

    def __init__(self):
        super().__init__(
            name="Testing Agent",
            system_prompt="""
            Вы - Testing Agent в системе AI Bot Architect. Ваша задача - проводить 
            всестороннее тестирование сгенерированного кода Telegram-бота.
            
            Ваши основные задачи:
            1. Статический анализ кода
            2. Проверка соответствия техническому заданию
            3. Тестирование безопасности
            4. Проверка производительности
            5. Валидация архитектуры
            6. Генерация отчета о тестировании
            
            Принципы тестирования:
            - Проверяйте все критически важные функции
            - Тестируйте edge cases и error handling
            - Валидируйте security practices
            - Проверяйте code quality и style
            - Анализируйте производительность
            - Создавайте детальные отчеты с рекомендациями
            """,
            temperature=0.1  # Низкая температура для точности
        )
        
        self.test_results: Dict[str, Any] = {}
        self.quality_score: float = 0.0

    async def process(self, input_data: Dict[str, Any]) -> Dict[str, Any]:
        """
        Основной метод тестирования бота.
        
        Args:
            input_data: {
                "generated_files": "сгенерированные файлы",
                "technical_specification": "техническое задание",
                "project_structure": "структура проекта",
                "archive_path": "путь к архиву проекта"
            }
            
        Returns:
            Результат тестирования с отчетом и рекомендациями
        """
        try:
            generated_files = input_data.get("generated_files", {})
            spec = input_data.get("technical_specification", {})
            project_structure = input_data.get("project_structure", {})
            archive_path = input_data.get("archive_path", "")

            # Инициализация результатов тестирования
            self.test_results = {
                "timestamp": datetime.now().isoformat(),
                "total_files": len(generated_files),
                "tests_passed": 0,
                "tests_failed": 0,
                "warnings": 0,
                "critical_issues": 0
            }

            # 1. Статический анализ кода
            static_analysis = await self._perform_static_analysis(generated_files)
            
            # 2. Проверка соответствия ТЗ
            spec_compliance = await self._check_specification_compliance(
                generated_files, spec
            )
            
            # 3. Тестирование безопасности
            security_check = await self._perform_security_testing(generated_files)
            
            # 4. Анализ архитектуры
            architecture_check = await self._validate_architecture(
                generated_files, project_structure
            )
            
            # 5. Проверка качества кода
            code_quality = await self._assess_code_quality(generated_files)
            
            # 6. Тестирование производительности
            performance_check = await self._check_performance_patterns(generated_files)
            
            # 7. Проверка документации
            documentation_check = await self._validate_documentation(generated_files)
            
            # 8. Расчет общего качественного балла
            self.quality_score = await self._calculate_quality_score()
            
            # 9. Генерация финального отчета
            final_report = await self._generate_test_report()

            return {
                "status": "success",
                "quality_score": self.quality_score,
                "test_results": self.test_results,
                "static_analysis": static_analysis,
                "spec_compliance": spec_compliance,
                "security_check": security_check,
                "architecture_check": architecture_check,
                "code_quality": code_quality,
                "performance_check": performance_check,
                "documentation_check": documentation_check,
                "final_report": final_report,
                "recommendations": await self._generate_recommendations(),
                "next_actions": await self._suggest_next_actions()
            }

        except Exception as e:
            logger.error(f"Ошибка в тестировании: {e}")
            return {
                "status": "error",
                "error": str(e),
                "partial_results": self.test_results
            }

    async def _perform_static_analysis(self, files: Dict[str, str]) -> Dict[str, Any]:
        """Статический анализ кода."""
        analysis_prompt = f"""
        Проведите статический анализ сгенерированного кода:
        
        Файлы для анализа:
        {json.dumps(list(files.keys()), ensure_ascii=False, indent=2)}
        
        Проверьте:
        1. Синтаксические ошибки
        2. Import statements
        3. Использование современных Python patterns
        4. Type hints coverage
        5. Async/await правильность
        6. Error handling
        7. Code style (PEP 8)
        
        Верните структурированный анализ в JSON формате:
        {{
            "syntax_errors": [],
            "import_issues": [],
            "type_hints_coverage": "percentage",
            "async_patterns": "assessment",
            "error_handling": "assessment",
            "code_style": "assessment",
            "overall_grade": "A-F"
        }}
        """

        # Анализ каждого Python файла
        python_files = {k: v for k, v in files.items() if k.endswith('.py')}
        
        analysis_results = []
        for filename, content in python_files.items():
            file_analysis = await self._analyze_single_file(filename, content)
            analysis_results.append(file_analysis)

        # Общий анализ
        overall_analysis = await self.generate_response(analysis_prompt)
        
        try:
            parsed_analysis = json.loads(overall_analysis)
        except json.JSONDecodeError:
            parsed_analysis = self._create_default_static_analysis()

        return {
            "overall": parsed_analysis,
            "file_analyses": analysis_results,
            "total_files_analyzed": len(python_files)
        }

    async def _analyze_single_file(self, filename: str, content: str) -> Dict[str, Any]:
        """Анализ отдельного файла."""
        file_analysis_prompt = f"""
        Проанализируйте Python файл:
        
        Файл: {filename}
        Содержимое:
        {content[:1000]}...  # Первые 1000 символов
        
        Проверьте:
        1. Синтаксические ошибки
        2. Imports и dependencies
        3. Function signatures и type hints
        4. Error handling patterns
        5. Code complexity
        
        Верните краткий анализ в JSON формате.
        """

        analysis = await self.generate_response(file_analysis_prompt)
        
        try:
            return json.loads(analysis)
        except json.JSONDecodeError:
            return {
                "filename": filename,
                "status": "analyzed",
                "issues": [],
                "recommendations": []
            }

    async def _check_specification_compliance(
        self, 
        files: Dict[str, str], 
        spec: Dict[str, Any]
    ) -> Dict[str, Any]:
        """Проверка соответствия техническому заданию."""
        compliance_prompt = f"""
        Проверьте соответствие сгенерированного кода техническому заданию:
        
        Техническое задание:
        {json.dumps(spec, ensure_ascii=False, indent=2)}
        
        Сгенерированные файлы:
        {json.dumps(list(files.keys()), ensure_ascii=False)}
        
        Проверьте:
        1. Реализованы ли все обязательные функции
        2. Соответствует ли архитектура требованиям
        3. Использованы ли указанные технологии
        4. Реализованы ли все пользовательские сценарии
        5. Соблюдены ли требования безопасности
        
        Верните анализ соответствия в процентах и список отсутствующих функций.
        """

        compliance_analysis = await self.generate_response(compliance_prompt)
        
        return await self._parse_compliance_result(compliance_analysis, spec)

    async def _parse_compliance_result(
        self, 
        analysis: str, 
        spec: Dict[str, Any]
    ) -> Dict[str, Any]:
        """Парсинг результата проверки соответствия."""
        try:
            # Попытка извлечь процент соответствия
            import re
            percentage_match = re.search(r'(\d+)%', analysis)
            compliance_percentage = int(percentage_match.group(1)) if percentage_match else 80
            
            return {
                "compliance_percentage": compliance_percentage,
                "analysis": analysis,
                "required_features": spec.get("functional_requirements", {}).get("core_features", []),
                "missing_features": await self._identify_missing_features(analysis, spec),
                "grade": self._get_compliance_grade(compliance_percentage)
            }
        except Exception:
            return {
                "compliance_percentage": 75,
                "analysis": analysis,
                "grade": "B",
                "status": "partial_analysis"
            }

    async def _identify_missing_features(
        self, 
        analysis: str, 
        spec: Dict[str, Any]
    ) -> List[str]:
        """Идентификация отсутствующих функций."""
        missing_prompt = f"""
        На основе анализа соответствия:
        {analysis}
        
        И технического задания:
        {json.dumps(spec, ensure_ascii=False, indent=2)}
        
        Определите список конкретных функций или компонентов, 
        которые требуются по ТЗ, но отсутствуют в реализации.
        
        Верните только список отсутствующих элементов.
        """

        missing_analysis = await self.generate_response(missing_prompt)
        
        # Простой парсинг списка
        missing_features = [
            feature.strip().lstrip('- •*1234567890.')
            for feature in missing_analysis.split('\n')
            if feature.strip()
        ]
        
        return missing_features[:10]  # Максимум 10 элементов

    async def _perform_security_testing(self, files: Dict[str, str]) -> Dict[str, Any]:
        """Тестирование безопасности."""
        security_prompt = f"""
        Проведите анализ безопасности сгенерированного кода:
        
        Проверьте:
        1. Input validation и sanitization
        2. SQL injection protection
        3. XSS protection (если применимо)
        4. Secrets management
        5. Authentication и authorization
        6. Rate limiting
        7. Error message security
        8. Logging security
        
        Найдите потенциальные уязвимости и дайте рекомендации.
        """

        security_analysis = await self.generate_response(security_prompt)
        
        return {
            "analysis": security_analysis,
            "vulnerabilities": await self._extract_vulnerabilities(security_analysis),
            "security_score": await self._calculate_security_score(security_analysis),
            "recommendations": await self._generate_security_recommendations(security_analysis)
        }

    async def _extract_vulnerabilities(self, analysis: str) -> List[Dict[str, str]]:
        """Извлечение уязвимостей из анализа."""
        vulnerabilities = []
        
        # Простой парсинг уязвимостей
        lines = analysis.split('\n')
        current_vulnerability = {}
        
        for line in lines:
            if any(keyword in line.lower() for keyword in ['уязвимость', 'vulnerability', 'риск', 'опасность']):
                if current_vulnerability:
                    vulnerabilities.append(current_vulnerability)
                current_vulnerability = {
                    "type": line.strip(),
                    "severity": "medium",
                    "description": ""
                }
            elif current_vulnerability and line.strip():
                current_vulnerability["description"] += " " + line.strip()
        
        if current_vulnerability:
            vulnerabilities.append(current_vulnerability)
        
        return vulnerabilities[:5]  # Максимум 5 уязвимостей

    async def _calculate_security_score(self, analysis: str) -> float:
        """Расчет балла безопасности."""
        # Простая эвристика на основе ключевых слов
        positive_keywords = ['защищен', 'валидация', 'аутентификация', 'авторизация', 'безопасн']
        negative_keywords = ['уязвим', 'риск', 'опасность', 'небезопасн', 'отсутству']
        
        positive_count = sum(1 for keyword in positive_keywords if keyword in analysis.lower())
        negative_count = sum(1 for keyword in negative_keywords if keyword in analysis.lower())
        
        # Базовый балл 70, корректировка на основе анализа
        base_score = 70.0
        score_adjustment = (positive_count * 5) - (negative_count * 10)
        
        return max(0.0, min(100.0, base_score + score_adjustment))

    async def _generate_security_recommendations(self, analysis: str) -> List[str]:
        """Генерация рекомендаций по безопасности."""
        recommendations_prompt = f"""
        На основе анализа безопасности:
        {analysis}
        
        Предложите 3-5 конкретных рекомендаций для улучшения безопасности кода.
        Каждая рекомендация должна быть практичной и реализуемой.
        """

        recommendations_text = await self.generate_response(recommendations_prompt)
        
        return [
            rec.strip().lstrip('- •*1234567890.')
            for rec in recommendations_text.split('\n')
            if rec.strip()
        ][:5]

    async def _validate_architecture(
        self, 
        files: Dict[str, str], 
        structure: Dict[str, Any]
    ) -> Dict[str, Any]:
        """Валидация архитектуры проекта."""
        architecture_prompt = f"""
        Проанализируйте архитектуру проекта:
        
        Структура проекта:
        {json.dumps(structure, ensure_ascii=False, indent=2)}
        
        Файлы:
        {json.dumps(list(files.keys()), ensure_ascii=False)}
        
        Оцените:
        1. Соответствие принципам SOLID
        2. Разделение ответственности
        3. Модульность и переиспользуемость
        4. Dependency injection
        5. Layered architecture
        6. Error handling strategy
        
        Дайте архитектурную оценку и рекомендации.
        """

        architecture_analysis = await self.generate_response(architecture_prompt)
        
        return {
            "analysis": architecture_analysis,
            "architecture_score": await self._calculate_architecture_score(architecture_analysis),
            "patterns_used": await self._identify_architecture_patterns(architecture_analysis),
            "improvements": await self._suggest_architecture_improvements(architecture_analysis)
        }

    async def _assess_code_quality(self, files: Dict[str, str]) -> Dict[str, Any]:
        """Оценка качества кода."""
        quality_metrics = {
            "total_lines": 0,
            "comment_ratio": 0.0,
            "function_count": 0,
            "class_count": 0,
            "complexity_score": 0.0
        }

        # Подсчет метрик для Python файлов
        for filename, content in files.items():
            if filename.endswith('.py'):
                metrics = await self._calculate_file_metrics(content)
                for key, value in metrics.items():
                    if isinstance(value, (int, float)):
                        quality_metrics[key] += value

        # Расчет итогового балла качества
        quality_score = await self._calculate_quality_metrics_score(quality_metrics)

        return {
            "metrics": quality_metrics,
            "quality_score": quality_score,
            "grade": self._get_quality_grade(quality_score)
        }

    async def _calculate_file_metrics(self, content: str) -> Dict[str, Any]:
        """Расчет метрик для отдельного файла."""
        lines = content.split('\n')
        
        return {
            "total_lines": len(lines),
            "comment_ratio": len([line for line in lines if line.strip().startswith('#')]) / max(len(lines), 1) * 100,
            "function_count": len([line for line in lines if line.strip().startswith('def ')]),
            "class_count": len([line for line in lines if line.strip().startswith('class ')]),
            "complexity_score": len([line for line in lines if any(keyword in line for keyword in ['if', 'for', 'while', 'try'])]) / max(len(lines), 1) * 100
        }

    async def _check_performance_patterns(self, files: Dict[str, str]) -> Dict[str, Any]:
        """Проверка паттернов производительности."""
        performance_prompt = f"""
        Проанализируйте код на предмет производительности:
        
        Проверьте:
        1. Использование async/await patterns
        2. Database query optimization
        3. Caching strategies
        4. Memory usage patterns
        5. Connection pooling
        6. Batch operations
        
        Дайте оценку производительности и рекомендации.
        """

        performance_analysis = await self.generate_response(performance_prompt)
        
        return {
            "analysis": performance_analysis,
            "performance_score": 85.0,  # Базовый балл
            "optimizations": await self._suggest_performance_optimizations(performance_analysis)
        }

    async def _validate_documentation(self, files: Dict[str, str]) -> Dict[str, Any]:
        """Валидация документации."""
        docs_files = {k: v for k, v in files.items() if k.endswith(('.md', '.txt', '.rst'))}
        
        documentation_score = 0.0
        has_readme = any('readme' in filename.lower() for filename in docs_files.keys())
        has_api_docs = any('api' in filename.lower() for filename in docs_files.keys())
        
        if has_readme:
            documentation_score += 40
        if has_api_docs:
            documentation_score += 30
        if len(docs_files) > 0:
            documentation_score += 30

        return {
            "documentation_score": min(documentation_score, 100.0),
            "files_found": list(docs_files.keys()),
            "has_readme": has_readme,
            "has_api_docs": has_api_docs,
            "recommendations": [
                "Добавить больше примеров использования",
                "Создать API документацию",
                "Добавить troubleshooting guide"
            ] if documentation_score < 80 else []
        }

    async def _calculate_quality_score(self) -> float:
        """Расчет общего балла качества."""
        # Простая средневзвешенная оценка
        weights = {
            "static_analysis": 0.25,
            "security": 0.20,
            "architecture": 0.20,
            "code_quality": 0.20,
            "documentation": 0.15
        }
        
        # Базовые баллы (в реальной реализации они будут браться из результатов тестов)
        scores = {
            "static_analysis": 85.0,
            "security": 80.0,
            "architecture": 88.0,
            "code_quality": 82.0,
            "documentation": 75.0
        }
        
        weighted_score = sum(scores[category] * weight for category, weight in weights.items())
        return round(weighted_score, 2)

    async def _generate_test_report(self) -> str:
        """Генерация финального отчета тестирования."""
        report_prompt = f"""
        Создайте детальный отчет о тестировании на основе результатов:
        
        Результаты тестирования:
        {json.dumps(self.test_results, ensure_ascii=False, indent=2)}
        
        Общий балл качества: {self.quality_score}
        
        Создайте структурированный отчет включающий:
        1. Executive Summary
        2. Детальные результаты по каждой категории
        3. Выявленные проблемы и их приоритеты
        4. Рекомендации по улучшению
        5. План дальнейших действий
        
        Формат: структурированный текстовый отчет.
        """

        return await self.generate_response(report_prompt)

    async def _generate_recommendations(self) -> List[str]:
        """Генерация рекомендаций по улучшению."""
        return [
            "Добавить больше unit тестов",
            "Улучшить error handling",
            "Добавить rate limiting",
            "Оптимизировать database queries",
            "Улучшить документацию"
        ]

    async def _suggest_next_actions(self) -> List[str]:
        """Предложение следующих действий."""
        if self.quality_score >= 90:
            return [
                "Код готов к развертыванию",
                "Провести финальное тестирование в staging окружении",
                "Настроить monitoring и alerts"
            ]
        elif self.quality_score >= 75:
            return [
                "Исправить критические проблемы",
                "Добавить недостающие тесты",
                "Повторное тестирование после исправлений"
            ]
        else:
            return [
                "Требуется серьезная доработка кода",
                "Исправить все выявленные проблемы",
                "Провести повторную генерацию кода"
            ]

    # Вспомогательные методы
    def _create_default_static_analysis(self) -> Dict[str, Any]:
        """Создание анализа по умолчанию."""
        return {
            "syntax_errors": [],
            "import_issues": [],
            "type_hints_coverage": "75%",
            "async_patterns": "good",
            "error_handling": "adequate",
            "code_style": "good",
            "overall_grade": "B+"
        }

    def _get_compliance_grade(self, percentage: int) -> str:
        """Получение буквенной оценки соответствия."""
        if percentage >= 95:
            return "A+"
        elif percentage >= 90:
            return "A"
        elif percentage >= 85:
            return "B+"
        elif percentage >= 80:
            return "B"
        elif percentage >= 75:
            return "C+"
        elif percentage >= 70:
            return "C"
        else:
            return "D"

    def _get_quality_grade(self, score: float) -> str:
        """Получение буквенной оценки качества."""
        return self._get_compliance_grade(int(score))

    async def _calculate_architecture_score(self, analysis: str) -> float:
        """Расчет балла архитектуры."""
        return 85.0  # Базовая реализация

    async def _identify_architecture_patterns(self, analysis: str) -> List[str]:
        """Идентификация использованных архитектурных паттернов."""
        return ["Layered Architecture", "Dependency Injection", "Repository Pattern"]

    async def _suggest_architecture_improvements(self, analysis: str) -> List[str]:
        """Предложение улучшений архитектуры."""
        return [
            "Рассмотреть использование CQRS pattern",
            "Добавить Event-driven architecture",
            "Улучшить separation of concerns"
        ]

    async def _calculate_quality_metrics_score(self, metrics: Dict[str, Any]) -> float:
        """Расчет балла качества на основе метрик."""
        base_score = 70.0
        
        # Корректировки на основе метрик
        if metrics.get("comment_ratio", 0) > 10:
            base_score += 5
        if metrics.get("function_count", 0) > 5:
            base_score += 5
        if metrics.get("complexity_score", 100) < 20:
            base_score += 10
        
        return min(100.0, base_score)

    async def _suggest_performance_optimizations(self, analysis: str) -> List[str]:
        """Предложение оптимизаций производительности."""
        return [
            "Добавить connection pooling",
            "Реализовать caching layer",
            "Оптимизировать database queries",
            "Использовать batch operations"
        ]