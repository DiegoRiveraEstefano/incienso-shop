# syntax=docker/dockerfile:1.7
FROM python:3.14-slim-bookworm AS base

# Install uv from the official image
COPY --from=ghcr.io/astral-sh/uv:latest /uv /uvx /bin/

# Environment variables
ENV PYTHONUNBUFFERED=1 \
    PYTHONDONTWRITEBYTECODE=1 \
    UV_COMPILE_BYTECODE=1 \
    UV_LINK_MODE=copy \
    PATH="/app/.venv/bin:$PATH" \
    DJANGO_SETTINGS_MODULE=config.settings.production

WORKDIR /app

# Install runtime system packages and build tools
RUN apt-get update && apt-get install --no-install-recommends -y \
    build-essential \
    libpq-dev \
    libpq5 \
    sqlite3 \
    libsqlite3-0 \
    curl \
    gettext \
    libjpeg62-turbo \
    zlib1g \
    libpng16-16 \
    ca-certificates \
    && rm -rf /var/lib/apt/lists/*

# Create application user
RUN groupadd -g 1000 django && \
    useradd -u 1000 -g django -m -s /bin/bash django

# Install Python dependencies first (leverage Docker layer caching)
COPY pyproject.toml uv.lock .python-version ./
RUN uv sync --frozen --no-dev --no-install-project

# Copy application code
COPY . .

# Install project package into virtualenv
RUN uv sync --frozen --no-dev

# Prepare persistent data and cache directories with proper permissions
RUN mkdir -p /app/data /app/data/cache/diskcache /app/staticfiles /app/incienso_shop/media \
    && chown -R django:django /app

# Copy scripts and set execution permissions
COPY compose/web/entrypoint.sh /entrypoint.sh
COPY compose/web/start.sh /start.sh
RUN sed -i 's/\r$//' /entrypoint.sh /start.sh \
    && chmod +x /entrypoint.sh /start.sh

USER django

EXPOSE 8000

ENTRYPOINT ["/entrypoint.sh"]
CMD ["/start.sh"]
