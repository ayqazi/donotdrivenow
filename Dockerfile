FROM python:3.12-alpine as build

# Increase to expire all following cached layers
ENV expire_caches=20240511

RUN --mount=type=cache,target=/var/cache/apk <<EOL
apk update
apk add gcc musl-dev libffi-dev python3-dev
EOL

ENV PYTHONUNBUFFERED=1 \
    PYTHONDONTWRITEBYTECODE=1 \
    PIP_NO_CACHE_DIR=off \
    PIP_DISABLE_PIP_VERSION_CHECK=on \
    PIP_DEFAULT_TIMEOUT=100 \
    POETRY_CACHE_DIR=/app/.pypoetry-cache \
    POETRY_VIRTUALENVS_IN_PROJECT=true

RUN pip install --upgrade pip && \
    pip install 'poetry~=1.8'

WORKDIR /app

COPY poetry.lock pyproject.toml ./

RUN poetry install

COPY --chown=1000:1000 . ./

FROM python:3.12-alpine
RUN --mount=type=cache,target=/var/cache/apk <<EOL
adduser -D app -u 1000
EOL

WORKDIR /app
COPY --chown=1000:1000 --from=build /app ./

ENTRYPOINT [".venv/bin/python3", "-m", "litestar", "run", "-H", "0.0.0.0"]
