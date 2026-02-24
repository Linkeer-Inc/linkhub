FROM python:3.14.3-slim

WORKDIR /app

RUN groupadd --system --gid 10001 appgroup && \
    useradd  --system --uid 10001 --gid appgroup \
    --no-create-home --shell /sbin/nologin appuser 

RUN apt-get update && apt-get install -y \
    postgresql-client \
    gcc \
    && rm -rf /var/lib/apt/lists/*

COPY --chown=appuser:appgroup . .

RUN pip install --no-cache-dir -r requirements.txt \
    && python3 manage.py collectstatic --noinput \
    && chown -R appuser:appgroup /app/storage/ \
    && chmod -R 644 /app/storage 

EXPOSE 8000

USER appuser
