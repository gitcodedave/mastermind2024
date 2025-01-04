FROM python:3.12-alpine

WORKDIR /app

RUN apk update && apk add --no-cache \
    build-base \
    mariadb-connector-c-dev \
    pkgconfig

COPY Pipfile* ./

RUN pip install pipenv

RUN pipenv install --deploy

COPY . .

EXPOSE 8000