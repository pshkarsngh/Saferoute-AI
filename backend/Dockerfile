# SafeRoute AI — backend image (Phase 1 foundation)
# Rules (15_DEPLOYMENT.md): non-root user, minimal base, no baked secrets, image scan.
FROM python:3.12-slim

# Prevent Python from writing .pyc and buffering logs.
ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1

WORKDIR /app

# Install deps first (layer cache friendly).
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# App code. Secrets come from env at runtime — never baked into the image.
COPY app ./app

# Non-root user.
RUN useradd --create-home --shell /usr/sbin/nologin saferoute
USER saferoute

EXPOSE 8000

HEALTHCHECK --interval=30s --timeout=5s --start-period=15s --retries=3 \
  CMD python -c "import urllib.request,sys; sys.exit(0 if urllib.request.urlopen('http://localhost:8000/api/v1/health', timeout=3).status==200 else 1)"

CMD ["uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "8000"]