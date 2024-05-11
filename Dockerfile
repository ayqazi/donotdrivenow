FROM python:3.12-alpine

# Increase to expire all following cached layers
ENV expire_caches=20240511

RUN --mount=type=cache,target=/var/cache/apk <<EOL
apk update
apk add gcc musl-dev libffi-dev python3-dev
adduser -D app -u 1000
EOL

ENV PYTHONUNBUFFERED=1 \
    PYTHONDONTWRITEBYTECODE=1 \
    PIP_NO_CACHE_DIR=off \
    PIP_DISABLE_PIP_VERSION_CHECK=on \
    PIP_DEFAULT_TIMEOUT=100 \
    POETRY_CACHE_DIR=/app/.pypoetry-cache

RUN pip install --upgrade pip && \
    pip install 'poetry~=1.8'

USER 1000:1000
WORKDIR /app

COPY --chown=1000:1000 poetry.lock pyproject.toml ./

RUN poetry install

COPY --chown=1000:1000 . ./

ENTRYPOINT ["poetry", "run", "litestar", "run", "-H", "0.0.0.0"]
