FROM python:3.12-slim

ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1 \
    PIP_NO_CACHE_DIR=1 \
    DATA_DIR=/data \
    SQLITE_PATH=/data/db.sqlite3 \
    MEDIA_ROOT=/data/media \
    BUNDLED_MEDIA_ROOT=/app/media \
    STATIC_ROOT=/app/staticfiles \
    DEBUG=0 \
    DJANGO_LOAD_SAMPLE_DATA=1

WORKDIR /app

RUN pip install --no-cache-dir uv

COPY pyproject.toml uv.lock ./
RUN uv export --frozen --no-dev --format requirements-txt --output-file requirements.txt
RUN pip install --no-cache-dir -r requirements.txt

COPY . .
COPY docker/entrypoint.sh /entrypoint.sh

RUN chmod +x /entrypoint.sh \
    && mkdir -p /data

EXPOSE 8000
VOLUME ["/data"]

HEALTHCHECK --interval=30s --timeout=5s --start-period=30s --retries=3 \
  CMD python -c "import urllib.request; urllib.request.urlopen('http://127.0.0.1:8000/healthz/', timeout=3)"

ENTRYPOINT ["/entrypoint.sh"]
CMD ["gunicorn", "config.wsgi:application", "--bind", "0.0.0.0:8000", "--workers", "2", "--threads", "4", "--timeout", "120"]
