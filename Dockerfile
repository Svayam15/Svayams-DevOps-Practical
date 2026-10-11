FROM python:3.12-slim

ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1

WORKDIR /app

# Dependencies first so this layer is cached when only code changes
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

COPY run.py .
COPY app ./app

# Version is injected by the pipeline (docker build --build-arg APP_VERSION=...)
ARG APP_VERSION=dev
ENV APP_VERSION=${APP_VERSION} \
    DATABASE_PATH=/data/students.db

# Run as a non-root user; /data holds the SQLite file
RUN useradd --system --uid 10001 appuser && mkdir /data && chown appuser /data
USER 10001

EXPOSE 5000

HEALTHCHECK --interval=30s --timeout=3s --retries=3 \
  CMD python -c "import urllib.request; urllib.request.urlopen('http://127.0.0.1:5000/health', timeout=2)"

# One worker + threads: prometheus_client keeps metrics per process, so several
# workers would each report different counters. Scale with pods instead.
CMD ["gunicorn", "-b", "0.0.0.0:5000", "-w", "1", "--threads", "4", "app:create_app()"]
