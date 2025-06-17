# AI Bot Architect 🤖✨

Революционный AI-агент для создания Telegram-ботов на основе естественного описания требований. Используя возможности Claude 4 Sonnet и агентную архитектуру, система создаёт полнофункциональных ботов без необходимости программирования.

## 🚀 Ключевые возможности

- **Естественное описание требований** - опишите бота обычными словами
- **Мультимодальный ввод** - текст, голос, изображения, документы
- **Deep Research** - система исследует предметную область и best practices
- **Intelligent Requirements Engineering** - AI задаёт уточняющие вопросы
- **Автоматическая генерация кода** - создание production-ready кода
- **Автодеплой** - развертывание на Timeweb Cloud одним кликом

## 🏗️ Архитектура

Система построена на базе специализированных AI-агентов:

- **Research Agent** - исследование предметной области
- **Requirements Agent** - сбор и анализ требований  
- **Code Generation Agent** - генерация кода бота
- **Testing Agent** - тестирование функциональности
- **Deployment Agent** - развертывание и мониторинг

## 🛠️ Технологический стек

- **AI/ML**: Claude 4 Sonnet, LangChain, LangGraph
- **Backend**: FastAPI, Aiogram, SQLAlchemy
- **Database**: PostgreSQL, Redis
- **Deployment**: Timeweb Cloud, Docker
- **Integrations**: Telegram Bot API, Payment APIs

## 📦 Установка

```bash
# Клонирование репозитория
git clone https://github.com/yourusername/ai-bot-architect.git
cd ai-bot-architect

# Создание виртуального окружения
python -m venv venv
source venv/bin/activate  # Linux/Mac
# venv\Scripts\activate  # Windows

# Установка зависимостей
pip install -r requirements.txt

# Настройка переменных окружения
cp .env.example .env
# Отредактируйте .env файл с вашими API ключами
```

## ⚙️ Конфигурация

Создайте `.env` файл с необходимыми переменными:

```env
# AI Providers
ANTHROPIC_API_KEY=your_claude_api_key
OPENAI_API_KEY=your_openai_api_key

# Telegram
TELEGRAM_BOT_TOKEN=your_bot_token
TELEGRAM_WEBHOOK_URL=your_webhook_url

# Database
DATABASE_URL=postgresql+asyncpg://user:password@localhost/ai_bot_architect
REDIS_URL=redis://localhost:6379

# Deployment
TIMEWEB_API_KEY=your_timeweb_api_key
BOTFATHER_TOKEN=your_botfather_token

# Security
JWT_SECRET_KEY=your_jwt_secret
ENCRYPTION_KEY=your_encryption_key
```

## 🚦 Запуск

```bash
# Миграции базы данных
alembic upgrade head

# Запуск FastAPI сервера
uvicorn app.main:app --host 0.0.0.0 --port 8000 --reload

# Запуск Telegram бота
python -m app.bot.main
```

## 📝 Использование

1. **Отправьте описание** вашего бота AI Bot Architect в Telegram
2. **Ответьте на вопросы** системы для уточнения требований
3. **Получите техническое задание** для проверки
4. **Дождитесь генерации кода** и автоматического развертывания
5. **Получите готового бота** с инструкциями по использованию

### Примеры описаний ботов:

```
"Нужен бот для приёма заказов пиццы с оплатой и доставкой"

"Создай бота для записи к врачу с календарём и напоминаниями"

"Хочу бота для продажи курсов с возможностью просмотра уроков"
```

## 🧪 Тестирование

```bash
# Запуск всех тестов
pytest

# Тестирование с покрытием
pytest --cov=app tests/

# Тестирование конкретного модуля
pytest tests/test_agents.py -v
```

## 📁 Структура проекта

```
ai-bot-architect/
├── app/
│   ├── agents/          # AI агенты
│   ├── api/            # FastAPI эндпоинты
│   ├── bot/            # Telegram bot
│   ├── core/           # Основная логика
│   ├── db/             # База данных
│   ├── integrations/   # Внешние интеграции
│   └── utils/          # Утилиты
├── tests/              # Тесты
├── docs/               # Документация
└── deploy/             # Скрипты развертывания
```

## 🤝 Участие в разработке

1. Форкните репозиторий
2. Создайте feature branch (`git checkout -b feature/amazing-feature`)
3. Закоммитьте изменения (`git commit -m 'Add amazing feature'`)
4. Запушьте в branch (`git push origin feature/amazing-feature`)
5. Откройте Pull Request

## 📄 Лицензия

Этот проект лицензирован под MIT License - см. файл [LICENSE](LICENSE) для деталей.

## 🙏 Благодарности

- Anthropic за Claude API
- Telegram за Bot API
- Сообщество LangChain за отличные инструменты
- Все контрибьюторы проекта

---

**AI Bot Architect** - будущее создания ботов уже здесь! 🚀