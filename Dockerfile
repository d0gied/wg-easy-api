FROM python:3.14-alpine

WORKDIR /code

COPY requirements.txt .

RUN pip install \
  --no-cache-dir \
  --upgrade \
  --root-user-action=ignore \
  -r requirements.txt

RUN apk add --no-cache curl jq

COPY ./tests ./tests
COPY ./wg_easy_api ./wg_easy_api
