FROM python:3.12-slim

ENV PYTHONDONTWRITEBYTECODE=1
ENV PYTHONUNBUFFERED=1

ARG USER_NAME=wschat-user
ARG USER_GROUP=wschat-group
ARG USER_UID=1000
ARG USER_GID=1000

WORKDIR /app

COPY pyproject.toml poetry.lock requirements.txt ./

RUN rm -rf /var/cache/apt && rm -rf /var/lib/apt/lists/* \
    && apt-get update && apt-get install --no-install-recommends -y \
    gosu libpq-dev openssl \
    && apt-get clean && rm -rf /var/lib/apt/lists/* \
    && pip install --no-cache-dir --upgrade pip==25.0.1 \
    && pip install --no-cache-dir -r requirements.txt \
    && poetry config virtualenvs.create false \
    && poetry install --only main --no-interaction --no-ansi --verbose \
    && poetry cache clear pypi --all \
    && addgroup --system --gid $USER_GID $USER_GROUP \
    && adduser --system --no-create-home $USER_NAME --uid $USER_UID --ingroup $USER_GROUP

EXPOSE 8000

COPY . .

RUN chown -R $USER_NAME:$USER_GROUP /app \
    && mv ./scripts/launch.sh /docker-entrypoint.sh \
    && chmod +x /docker-entrypoint.sh

ENTRYPOINT [ "/docker-entrypoint.sh" ]
