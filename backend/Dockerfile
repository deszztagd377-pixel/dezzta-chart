FROM python:3.12-alpine3.24

ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1 \
    PIP_NO_CACHE_DIR=1

WORKDIR /app

COPY requirements.txt ./requirements.txt
RUN python -m pip install -r requirements.txt \
    && apk add --no-cache su-exec

COPY app ./app

RUN addgroup -g 10001 appuser \
    && adduser -D -H -u 10001 -G appuser appuser \
    && mkdir -p /data \
    && chown -R appuser:appuser /app /data

# Start briefly as root to normalize the mounted volume's top-level ownership,
# then replace the shell with the application running as the unprivileged user.
USER root:root

EXPOSE 8000

HEALTHCHECK --interval=30s --timeout=5s --start-period=20s --retries=3 \
  CMD python -c "import os, urllib.request; urllib.request.urlopen('http://127.0.0.1:' + os.getenv('PORT', '8000') + '/health', timeout=3)"

CMD ["sh", "-c", "find /data -mindepth 0 -maxdepth 1 -exec chown 10001:10001 {} + && exec su-exec 10001:10001 uvicorn app.main:app --host 0.0.0.0 --port \"${PORT:-8000}\" --ws-max-size 65536 --ws-max-queue 16"]
