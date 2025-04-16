#!/bin/sh


alembic revision --autogenerate -m 'initial migration'
alembic upgrade head

uvicorn src.main:app \
      --host $APP__UVICORN_HOST \
      --port $APP__UVICORN_PORT
