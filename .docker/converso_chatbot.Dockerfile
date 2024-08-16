ARG BUILD_TYPE
FROM tiangolo/uvicorn-gunicorn:python3.10 AS base

WORKDIR /app/

COPY converso_chatbot/pyproject.toml converso_chatbot/poetry.lock ./

# Install Poetry and dependencies, don't install the project itself
RUN pip install poetry && \
        poetry config virtualenvs.create false && \
        poetry install --no-root

# Poetry install debugpy
RUN poetry add debugpy --group dev

COPY converso_chatbot .

# Install the project
RUN poetry install --only-root

ENV PYTHONPATH=/app

ARG BUILD_TYPE
RUN echo "Building for ${BUILD_TYPE}"

# Setting debug manually because skaffold debug is not working
# Set env for container
FROM base AS build_development
ENV PYTHONUNBUFFERED=1
ENTRYPOINT ["python", "-m", "debugpy", "--listen", "0.0.0.0:5678", "-m", "uvicorn", "converso_chatbot.main:app", "--reload", "--host", "0.0.0.0", "--port", "8000"]
#COPY client_secret.json /

FROM base AS build_testing
ENTRYPOINT ["python", "-m", "uvicorn", "converso_chatbot.main:app", "--reload", "--host", "0.0.0.0", "--port", "8000"]

FROM base AS build_production
ENTRYPOINT ["python", "-m", "uvicorn", "converso_chatbot.main:app", "--reload", "--host", "0.0.0.0", "--port", "8000"]

FROM build_${BUILD_TYPE}