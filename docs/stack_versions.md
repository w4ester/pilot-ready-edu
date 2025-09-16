# Edinfinite Stack Versions (2025-09-16)

## Backend (Python 3.11)
- FastAPI `>=0.110,<0.111`
- Uvicorn `>=0.29,<0.31`
- Starlette `>=0.37,<0.38`
- Pydantic `>=2.7,<2.8`
- Pydantic-Settings `>=2.3,<2.5`
- Typing-Extensions `>=4.9,<5.0`
- Python-Dotenv `>=1.0,<2.0`
- HTTPX `>=0.26,<0.29`
- Python-Multipart `>=0.0.9,<0.1`

### Database & ORM
- PostgreSQL 16.x (dev also supports local 14.17)
- Extensions: `citext`, `pgcrypto`, `pgvector`
- SQLAlchemy `==2.0.43`
- Alembic `>=1.13,<1.17` (1.16.5 recommended)
- Psycopg[binary] `>=3.1,<3.3`
- pgvector (Python) `==0.4.1`

### Auth & Security
- passlib[bcrypt] `>=1.7,<2.0`
- argon2-cffi `>=23,<27`
- pyjwt[crypto] `>=2.7,<3.0`
- authlib `>=1.2,<2.0`
- python-jose[cryptography] `>=3.3,<4.0`

### Optional Integrations
- Caching / Queue: redis `>=5.0,<6.0`, celery `>=5.3,<6.0`
- Observability: opentelemetry api/sdk/instrumentation `>=1.25,<2.0`
- AI Providers: openai `>=1.3,<2.0`, anthropic `>=0.36,<1.0`, google-generativeai `>=0.6,<1.0`, tiktoken `>=0.6,<0.8`
- RAG / Documents: pypdf, unstructured, python-pptx, openpyxl, pandas
- Images / Audio: pillow, rapidocr-onnxruntime
- Testing: pytest `>=7.4,<9.0`, pytest-asyncio `>=0.23,<0.25`, anyio `>=4.3,<5.0`
- Dev tools: black `>=24.4,<25.0`, ruff `>=0.4,<1.0`

## Frontend (Node 20 LTS)
- SvelteKit `^2.x`
- Svelte `^4.2.0`
- Vite `^5.0.0`
- TypeScript `^5.4.0`
- Monaco Editor `^0.50.0`
