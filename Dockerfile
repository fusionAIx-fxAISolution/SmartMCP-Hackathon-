FROM python:3.12-slim

ENV PYTHONUNBUFFERED=1 \
    PIP_NO_CACHE_DIR=1

WORKDIR /app

COPY pyproject.toml /app/pyproject.toml
COPY app /app/app
COPY README.md /app/README.md

RUN pip install --upgrade pip && pip install .

EXPOSE 8000
EXPOSE 8081

CMD ["python", "-m", "app.main"]
