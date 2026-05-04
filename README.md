# Game Searcher Backend

Бэкенд-сервис для поиска, анализа и рекомендации видеоигр на основе данных из Steam.

## О проекте

Проект автоматизирует сбор информации об играх и игроках из открытых источников, предоставляет удобное REST API для поиска, фильтрации, лайков и персонализированных рекомендаций.

**Основные возможности:**
- Парсинг игр из Steam (цены, описания, жанры, достижения, скриншоты)
- REST API с документацией Swagger
- Авторизация и управление лайками
- Поиск и фильтрация игр
- Рекомендательная система на основе предпочтений
- Асинхронные задачи (Celery) для обновления данных
- Кэширование (Redis)
- Облачное хранение изображений (S3)

## Стек технологий

| Категория | Технологии |
|-----------|-------------|
| Язык | Python 3.11+ |
| Фреймворк | FastAPI |
| Базы данных | PostgreSQL |
| Миграции | Alembic |
| Кэш и брокер | Redis |
| Фоновые задачи | Celery |
| Парсинг | Playwright, BeautifulSoup4, `steam` API |
| Хранилище | MinIO / AWS S3 (boto3) |
| Контейнеризация | Docker |

## Быстрый старт

### Локальный запуск

```bash
# 1. Клонирование
git clone https://github.com/Mr-Syrus/GameSearcherBackend.git
cd GameSearcherBackend

# 2. Виртуальное окружение
python -m venv venv
source venv/bin/activate   # Linux/Mac
# venv\Scripts\activate    Windows

# 3. Установка зависимостей
pip install -r requirements.txt

# 4. Настройка .env (скопируйте .env.example и заполните)
cp .env.example .env

# 5. Миграции БД
alembic upgrade head

# 6. Запуск Redis (Docker)
docker run -d -p 6379:6379 redis

# 7. Запуск Celery (отдельный терминал)
celery -A app.tasks worker --loglevel=info

# 8. Запуск API
uvicorn app.main:app --reload
