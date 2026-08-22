FROM python:3.14-alpine

WORKDIR /code

COPY pyproject.toml .
COPY poetry.lock .

RUN pip install --upgrade pip && \
  pip install poetry && \
  poetry config virtualenvs.create false && \
  poetry install --with test --no-interaction --no-ansi --no-root

RUN apk add --no-cache curl jq

COPY ./tests ./tests
COPY ./wg_easy_api ./wg_easy_api
