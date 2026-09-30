# S9 — E-GAZ-AUDIT serving obrazi
FROM python:3.12-slim

WORKDIR /app
ENV PYTHONDONTWRITEBYTECODE=1 PYTHONUNBUFFERED=1 CARBON_MODEL_DIR=/app/models

COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

COPY src/ src/
COPY scripts/ scripts/
COPY docs/ docs/
COPY tests/ tests/
# models/ va data/ — volume yoki build oldidan `make demo` natijasi
COPY models/ models/
COPY data/ data/

EXPOSE 8001
HEALTHCHECK --interval=30s --timeout=5s CMD python3 -c "import urllib.request;urllib.request.urlopen('http://127.0.0.1:8001/v1/health')"

CMD ["uvicorn", "src.api.app:app", "--host", "0.0.0.0", "--port", "8001"]
