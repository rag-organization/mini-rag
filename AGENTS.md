# mini-rag - Agent Instructions

## Project Overview
FastAPI-based RAG (Retrieval-Augmented Generation) service with PostgreSQL/pgvector and Qdrant vector DB support. Multi-provider LLM support (OpenAI, Cohere).

## Key Commands

### Local Development
```bash
# Install deps (uses uv in Docker, pip locally)
cd src && pip install -r requirements.txt

# Run locally (requires .env with all vars from .env.example)
uvicorn main:app --reload --host 0.0.0.0 --port 8000
```

### Docker (Production-like)
```bash
# From repo root
docker-compose -f docker/docker-compose.yml up --build

# Services: fastapi (8000), pgvector (5433), qdrant (6333), prometheus (9090), grafana (3000), nginx (80)
```

### Database Migrations (Alembic)
```bash
# Inside container (auto-runs on startup via entrypoint.sh)
cd /app/models/db_schemes/minirag && alembic upgrade head

# Create new migration
alembic revision --autogenerate -m "description"
```

## Architecture Notes

- **Entry point**: `src/main.py` - FastAPI app with lifespan for DB/LLM/VectorDB connections
- **Routes**: `src/routes/` - base (health), data (upload/process), nlp (index/search/rag)
- **Controllers**: `src/controllers/` - business logic (Data, Project, Process, NLP, Base)
- **Models**: `src/models/` - SQLAlchemy models + Pydantic schemas + enums
- **Stores**: `src/stores/` - Provider pattern for LLM (OpenAI/Cohere), VectorDB (Qdrant/PGVector), Processing (PDF/Text/Image/Table)
- **Config**: `src/helpers/config.py` - Pydantic Settings from `.env`

## Configuration

Required env vars (see `src/.env.example`):
- `POSTGRES_*` - PostgreSQL connection (pgvector)
- `GENERATION_BACKEND`, `EMBEDDING_BACKEND` - "OPENAI" or "COHERE"
- `OPENAI_API_KEY`, `COHERE_API_KEY` - LLM provider keys
- `VECTOR_DB_BACKEND` - "QDRANT" or "PGVECTOR"
- `FILE_ALLOWED_EXTENSIONS`, `FILE_MAX_SIZE`, `FILE_DEFAULT_CHUNK_SIZE`

## Testing
No test suite configured. Add pytest if needed.

## CI/CD
- `.github/workflows/develop-main.yml` - deploys `develop` branch via SSH + systemctl restart
- `.github/workflows/deploy-main.yml` - deploys `main` branch same way
- Target server runs `rag.service` (systemd)

## Gotchas
- Uses `uv` for fast pip installs in Docker (Dockerfile: `uv pip install -r requirements.txt --system`)
- Alembic runs automatically on container startup via `entrypoint.sh`
- Postgres healthcheck required before fastapi starts (docker-compose `depends_on: condition: service_healthy`)
- MongoDB config exists in code but commented out (PostgreSQL is primary)
- File uploads stored in `/app/assets` (mounted volume `fastapi_data`)