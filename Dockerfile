FROM python:3.14.2-slim

ENV NVM_VERSION=v0.40.3

WORKDIR /app

RUN apt-get update && apt-get install -y \
    postgresql-client \
    gcc \
    && rm -rf /var/lib/apt/lists/*

COPY . .

RUN pip install --no-cache-dir -r requirements.txt

RUN apt-get update -q -y && apt-get install -y \
    curl \
    git \
    && rm -rf /var/lib/apt/lists/* \
    && curl -o- https://raw.githubusercontent.com/nvm-sh/nvm/${NVM_VERSION}/install.sh | bash

EXPOSE 8000
