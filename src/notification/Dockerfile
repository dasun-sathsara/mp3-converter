FROM python:3.13-slim

ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1 \
    PIP_DISABLE_PIP_VERSION_CHECK=1 \
    PIP_NO_CACHE_DIR=1

WORKDIR /notification

COPY pyproject.toml ./
RUN pip install --upgrade pip setuptools wheel \
    && pip install -e .

COPY . .

CMD ["python", "main.py"]
