# Руководство по развертыванию AI Bot Architect

Это руководство поможет вам развернуть AI Bot Architect на продакшн сервере или локально для разработки.

## 📋 Требования

### Системные требования
- Python 3.11+
- PostgreSQL 13+
- Redis 6+
- Docker и Docker Compose (рекомендуется)
- Минимум 4GB RAM
- 2+ CPU cores

### API ключи
- **Anthropic API key** (обязательно) - для Claude
- **OpenAI API key** (опционально) - резервная модель
- **Timeweb Cloud API key** (опционально) - для автодеплоя
- **Web Search API key** (опционально) - для исследований

## 🚀 Быстрый старт с Docker

### 1. Клонирование и настройка

```bash
git clone https://github.com/yourusername/ai-bot-architect.git
cd ai-bot-architect

# Копирование конфигурации
cp .env.example .env
```

### 2. Настройка переменных окружения

Отредактируйте `.env` файл:

```env
# AI Providers (обязательно)
ANTHROPIC_API_KEY=your_claude_api_key_here

# Telegram Bot (создайте бота через @BotFather)
TELEGRAM_BOT_TOKEN=your_bot_token_here
BOT_USERNAME=your_bot_username

# База данных (автоматически настроится в Docker)
DATABASE_URL=postgresql+asyncpg://postgres:postgres@db:5432/ai_bot_architect
REDIS_URL=redis://redis:6379/0

# Безопасность (сгенерируйте случайные строки)
JWT_SECRET_KEY=your-super-secret-jwt-key-here
ENCRYPTION_KEY=your-encryption-key-here
API_SECRET_KEY=your-api-secret-key-here

# Режим разработки
DEBUG=False
LOG_LEVEL=INFO
```

### 3. Запуск с Docker Compose

```bash
# Сборка и запуск всех сервисов
docker-compose up -d

# Просмотр логов
docker-compose logs -f app

# Проверка статуса
docker-compose ps
```

### 4. Инициализация базы данных

```bash
# Применение миграций
docker-compose exec app alembic upgrade head

# Создание тестовых данных (опционально)
docker-compose exec app python -c "from app.db.init_db import init_db; init_db()"
```

### 5. Проверка работоспособности

```bash
# Проверка API
curl http://localhost:8000/health

# Проверка документации
open http://localhost:8000/docs
```

## 🔧 Локальная разработка

### 1. Настройка окружения

```bash
# Создание виртуального окружения
python -m venv venv
source venv/bin/activate  # Linux/Mac
# venv\Scripts\activate  # Windows

# Установка зависимостей
pip install -r requirements.txt
```

### 2. Настройка локальной базы данных

```bash
# Запуск PostgreSQL и Redis
docker-compose up -d db redis

# Или установка локально:
# PostgreSQL: https://postgresql.org/download/
# Redis: https://redis.io/download
```

### 3. Запуск приложения

```bash
# Применение миграций
alembic upgrade head

# Запуск FastAPI сервера
uvicorn app.main:app --reload --host 0.0.0.0 --port 8000

# Запуск в отдельном терминале для разработки
python -m app.main
```

## 📱 Создание Telegram бота

### 1. Создание бота через BotFather

```
1. Откройте Telegram и найдите @BotFather
2. Отправьте команду /newbot
3. Следуйте инструкциям для создания бота
4. Сохраните полученный токен в .env файл
```

### 2. Настройка webhook (для продакшн)

```bash
# Автоматическая настройка через API
curl -X POST "https://api.telegram.org/bot<YOUR_BOT_TOKEN>/setWebhook" \
     -H "Content-Type: application/json" \
     -d '{"url": "https://yourdomain.com/api/v1/webhook"}'

# Проверка webhook
curl "https://api.telegram.org/bot<YOUR_BOT_TOKEN>/getWebhookInfo"
```

## 🌐 Продакшн развертывание

### На VPS/Dedicated сервере

#### 1. Подготовка сервера

```bash
# Обновление системы
sudo apt update && sudo apt upgrade -y

# Установка Docker
curl -fsSL https://get.docker.com -o get-docker.sh
sudo sh get-docker.sh
sudo usermod -aG docker $USER

# Установка Docker Compose
sudo apt install docker-compose-plugin
```

#### 2. Настройка файрвола

```bash
sudo ufw allow 22    # SSH
sudo ufw allow 80    # HTTP
sudo ufw allow 443   # HTTPS
sudo ufw enable
```

#### 3. Настройка SSL сертификата

```bash
# Установка Certbot
sudo apt install certbot

# Получение сертификата (замените yourdomain.com)
sudo certbot certonly --standalone -d yourdomain.com

# Настройка автообновления
sudo crontab -e
# Добавьте: 0 12 * * * /usr/bin/certbot renew --quiet
```

#### 4. Продакшн конфигурация

Создайте `docker-compose.prod.yml`:

```yaml
version: '3.8'

services:
  app:
    build: .
    restart: unless-stopped
    environment:
      - DEBUG=False
      - DATABASE_URL=postgresql+asyncpg://postgres:${DB_PASSWORD}@db:5432/ai_bot_architect
    depends_on:
      - db
      - redis
    volumes:
      - ./logs:/app/logs
      - ./uploads:/app/uploads

  nginx:
    image: nginx:alpine
    restart: unless-stopped
    ports:
      - "80:80"
      - "443:443"
    volumes:
      - ./nginx.conf:/etc/nginx/nginx.conf:ro
      - ./ssl:/etc/nginx/ssl:ro
    depends_on:
      - app

  db:
    image: postgres:15-alpine
    restart: unless-stopped
    environment:
      POSTGRES_DB: ai_bot_architect
      POSTGRES_USER: postgres
      POSTGRES_PASSWORD: ${DB_PASSWORD}
    volumes:
      - postgres_data:/var/lib/postgresql/data
      - ./backups:/backups

  redis:
    image: redis:7-alpine
    restart: unless-stopped
    volumes:
      - redis_data:/data

volumes:
  postgres_data:
  redis_data:
```

#### 5. Запуск в продакшн

```bash
# Запуск с продакшн конфигурацией
docker-compose -f docker-compose.prod.yml up -d

# Настройка логирования
docker-compose -f docker-compose.prod.yml logs -f --tail=100
```

### На Timeweb Cloud

#### 1. Создание приложения

```bash
# Через веб-интерфейс Timeweb Cloud:
# 1. Создайте новое приложение
# 2. Выберите Python 3.11
# 3. Загрузите код из Git репозитория
```

#### 2. Настройка переменных окружения

```
В панели Timeweb Cloud добавьте все переменные из .env файла
```

#### 3. Настройка базы данных

```
1. Создайте PostgreSQL базу данных
2. Обновите DATABASE_URL в переменных окружения
3. Примените миграции через консоль приложения
```

## 📊 Мониторинг и логирование

### Настройка логирования

```bash
# Просмотр логов
docker-compose logs -f app

# Настройка ротации логов
sudo nano /etc/logrotate.d/ai-bot-architect
```

### Мониторинг производительности

```bash
# Установка Prometheus и Grafana
docker-compose -f monitoring.yml up -d

# Доступ к метрикам
curl http://localhost:8000/metrics
```

### Health checks

```bash
# Проверка здоровья приложения
curl http://localhost:8000/health

# Проверка статуса агентов
curl http://localhost:8000/api/v1/agents/status

# Проверка статистики
curl http://localhost:8000/api/v1/stats
```

## 🔄 Обновление

### Обновление в Docker

```bash
# Остановка сервисов
docker-compose down

# Обновление кода
git pull origin main

# Пересборка и запуск
docker-compose up -d --build

# Применение миграций
docker-compose exec app alembic upgrade head
```

### Backup и восстановление

```bash
# Создание backup базы данных
docker-compose exec db pg_dump -U postgres ai_bot_architect > backup.sql

# Восстановление из backup
docker-compose exec -T db psql -U postgres ai_bot_architect < backup.sql
```

## 🛠️ Устранение неполадок

### Частые проблемы

#### 1. Ошибка подключения к базе данных
```bash
# Проверка статуса PostgreSQL
docker-compose ps db

# Проверка логов базы данных
docker-compose logs db
```

#### 2. Ошибки API ключей
```bash
# Проверка переменных окружения
docker-compose exec app env | grep API_KEY

# Тестирование подключения к Claude
curl -H "x-api-key: YOUR_KEY" https://api.anthropic.com/v1/messages
```

#### 3. Проблемы с webhook
```bash
# Проверка webhook статуса
curl "https://api.telegram.org/bot<TOKEN>/getWebhookInfo"

# Сброс webhook
curl -X POST "https://api.telegram.org/bot<TOKEN>/setWebhook" \
     -d "url="
```

### Логи и диагностика

```bash
# Подробные логи приложения
docker-compose logs -f --tail=1000 app

# Проверка использования ресурсов
docker stats

# Подключение к контейнеру для отладки
docker-compose exec app bash
```

## 🔐 Безопасность

### Рекомендации по безопасности

1. **Используйте сильные пароли** для всех сервисов
2. **Настройте файрвол** и закройте ненужные порты
3. **Регулярно обновляйте** систему и зависимости
4. **Используйте HTTPS** для всех соединений
5. **Настройте backup** базы данных
6. **Мониторьте логи** на подозрительную активность

### Настройка SSL

```nginx
# nginx.conf для HTTPS
server {
    listen 443 ssl http2;
    server_name yourdomain.com;
    
    ssl_certificate /etc/nginx/ssl/fullchain.pem;
    ssl_certificate_key /etc/nginx/ssl/privkey.pem;
    
    location / {
        proxy_pass http://app:8000;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
    }
}
```

## 📞 Поддержка

Если у вас возникли проблемы:

1. Проверьте [документацию](README.md)
2. Просмотрите [Issues на GitHub](https://github.com/yourusername/ai-bot-architect/issues)
3. Создайте новый Issue с подробным описанием проблемы

---

**AI Bot Architect** - создание ботов будущего! 🚀