# Game Searcher Backend

Backend service for searching, analyzing, and recommending video games based on Steam data.

## About the Project

The project automates the collection of information about games and players from open sources, providing a convenient REST API for searching, filtering, likes, and personalized recommendations.

**Key Features:**
- Steam game parsing (prices, descriptions, genres, achievements, screenshots)
- REST API with Swagger documentation
- Authorization and like management
- Game search and filtering
- Recommendation system based on preferences
- Asynchronous tasks (Celery) for data updates
- Caching (Redis)
- Cloud image storage (S3)

## Tech Stack

| Category | Technologies |
|----------|--------------|
| Language | Python 3.11+ |
| Framework | FastAPI |
| Databases | PostgreSQL |
| Migrations | Alembic |
| Cache & Broker | Redis |
| Background Tasks | Celery |
| Parsing | Playwright, BeautifulSoup4, `steam` API |
| Storage | MinIO / AWS S3 (boto3) |
| Containerization | Docker |

## Quick Start

### Local Setup

```bash
# 1. Clone the repository
git clone https://github.com/Mr-Syrus/GameSearcherBackend.git
cd GameSearcherBackend

# 2. Virtual environment
python -m venv venv
source venv/bin/activate   # Linux/Mac
# venv\Scripts\activate    Windows

# 3. Install dependencies
pip install -r requirements.txt

# 4. Configure .env (copy .env.example and fill it in)
cp .env.example .env

# 5. Database migrations
alembic upgrade head

# 6. Start Redis (Docker)
docker run -d -p 6379:6379 redis

# 7. Start Celery (separate terminal)
celery -A app.tasks worker --loglevel=info

# 8. Start the API
uvicorn app.main:app --reload
