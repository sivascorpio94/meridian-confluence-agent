FROM python:3.12-slim AS runtime

ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1 \
    PIP_NO_CACHE_DIR=1 \
    API_HOST=0.0.0.0 \
    API_PORT=8000

WORKDIR /app

RUN groupadd --system meridian \
    && useradd --system --gid meridian --create-home meridian

COPY pyproject.toml README.md ./
COPY src ./src
COPY eval ./eval
COPY experiments ./experiments
COPY sql ./sql

RUN python -m pip install --upgrade pip \
    && python -m pip install .

USER meridian

EXPOSE 8000

HEALTHCHECK --interval=30s --timeout=5s --start-period=15s --retries=3 \
    CMD python -c "import urllib.request; urllib.request.urlopen('http://127.0.0.1:8000/health', timeout=3)"

CMD ["python", "-m", "src.run_api"]
