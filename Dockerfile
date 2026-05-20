# ==============================================================
# BASE
# ==============================================================

FROM python:3.10-slim AS base

ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1 \
    POETRY_VERSION=2.4.1 \
    PATH="/opt/venv/bin:$PATH"

WORKDIR /usr/src/app

# System dependencies
RUN apt-get update && apt-get install -y --no-install-recommends \
    build-essential \
    curl \
    libpq-dev \
    netcat-openbsd \
    && rm -rf /var/lib/apt/lists/*

# Install Poetry
RUN pip install --no-cache-dir "poetry==$POETRY_VERSION"

# ==============================================================
# DEPENDENCIES
# ==============================================================

FROM base AS dependencies

# RUN python -m venv /opt/venv

COPY pyproject.toml poetry.lock* ./

RUN poetry config virtualenvs.create false \
    && poetry install --no-interaction --no-ansi --without dev

# ==============================================================
# DEVELOPMENT
# ==============================================================

FROM dependencies AS development

RUN poetry install --no-interaction --no-ansi --with dev

COPY . .

ENV APP_MODULE=app.main:app \
    PORT=8000

EXPOSE 8000

HEALTHCHECK --interval=30s --timeout=5s --retries=3 \
    CMD curl -f http://localhost:${PORT}/health || exit 1

CMD ["sh", "-c", "uvicorn $APP_MODULE --host 0.0.0.0 --port $PORT --reload"]

# ==============================================================
# PRODUCTION
# ==============================================================

FROM dependencies AS production

RUN groupadd -r appgroup \
    && useradd -r -g appgroup appuser

COPY --chown=appuser:appgroup . .

USER appuser

ENV APP_MODULE=app.main:app \
    PORT=8000

EXPOSE 8000

HEALTHCHECK --interval=30s --timeout=5s --retries=3 \
    CMD curl -f http://localhost:${PORT}/health || exit 1

CMD ["sh", "-c", "uvicorn $APP_MODULE --host 0.0.0.0 --port $PORT"]
