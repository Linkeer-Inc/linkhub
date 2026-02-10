FROM python:3.14.2-slim

WORKDIR /app

RUN apt-get update && apt-get install -y \
    postgresql-client \
    gcc \
    && rm -rf /var/lib/apt/lists/*

COPY . .

RUN pip install --no-cache-dir -r requirements.txt \
    && python3 manage.py collectstatic --noinput

EXPOSE 8000
