#!/bin/sh

openssl rand -hex 32 > /app/hs256_secret.key
export AUTH__SECRET_KEY=$(cat /app/hs256_secret.key)

chown -R wschat-user:wschat-group /app/$APP__MIGRATIONS_FILEPATH
chown -R wschat-user:wschat-group /app/logs

exec gosu wschat-user sh -c "
    alembic revision --autogenerate -m 'initial migration' &&
    alembic upgrade head &&
    uvicorn src.main:app --host $APP__UVICORN_HOST --port $APP__UVICORN_PORT
"
