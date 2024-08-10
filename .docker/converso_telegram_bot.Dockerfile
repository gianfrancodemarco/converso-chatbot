ARG BUILD_TYPE
FROM python:3.10.13-slim-bookworm AS base

WORKDIR /app/

COPY converso_telegram_bot/pyproject.toml converso_telegram_bot/poetry.lock ./

# Install Poetry and dependencies, don't install the project itself
RUN pip install poetry && \
        poetry config virtualenvs.create false && \
        poetry install --no-root

# Poetry install debugpy
RUN poetry add debugpy --group dev

COPY converso_telegram_bot .

# Install the project
RUN poetry install --only-root

ENV PYTHONPATH=/app

ARG BUILD_TYPE
RUN echo "Building for ${BUILD_TYPE}"

FROM base AS build_development

# Doing it manually because skaffold debug is not working

ENTRYPOINT ["python", "-u", "-m", "debugpy", "--listen", "0.0.0.0:5678", "converso_telegram_bot/main.py"]

FROM base AS build_testing
ENTRYPOINT ["python", "-m", "main.py"]

FROM base AS build_production
ENTRYPOINT ["python", "-m", "main.py"]

FROM build_${BUILD_TYPE}