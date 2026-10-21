FROM python:3.12-slim

ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1 \
    HOST=0.0.0.0 \
    PORT=5000 \
    DATABASE_PATH=/data/students.db \
    FRONTEND_DIR=/app/frontend

WORKDIR /app

COPY backend/requirements.txt /app/backend/requirements.txt
RUN pip install --no-cache-dir -r /app/backend/requirements.txt gunicorn==23.0.0

COPY backend /app/backend
COPY frontend /app/frontend

# Run as a non-root user; /data holds the SQLite file (mounted as a volume)
RUN useradd --create-home appuser && mkdir -p /data && chown -R appuser /data /app
USER appuser

WORKDIR /app/backend
EXPOSE 5000

HEALTHCHECK --interval=15s --timeout=5s --start-period=10s --retries=3 \
  CMD python -c "import urllib.request,sys; sys.exit(0 if urllib.request.urlopen('http://127.0.0.1:5000/api/health', timeout=3).status == 200 else 1)"

# One worker + threads keeps SQLite access simple and safe
CMD ["gunicorn", "--bind", "0.0.0.0:5000", "--workers", "1", "--threads", "4", "app:create_app()"]
