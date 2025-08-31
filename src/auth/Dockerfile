FROM python:3.13-slim AS base

ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1 \
    PIP_DISABLE_PIP_VERSION_CHECK=1 \
    PIP_NO_CACHE_DIR=1

WORKDIR /auth

# --- Builder for dependencies (wheels) ---
FROM base AS builder

# Use pip's new resolver and compile wheels into a local dir for caching
COPY requirements.txt ./requirements.txt
RUN python -m venv /opt/venv \
    && . /opt/venv/bin/activate \
    && pip install --upgrade pip setuptools wheel \
    && pip wheel -r auth/requirements.txt --wheel-dir=/wheels


# --- Runtime image ---
FROM base AS runtime

# Create virtualenv and install from prebuilt wheels
RUN python -m venv /opt/venv
ENV PATH="/opt/venv/bin:$PATH"

COPY --from=builder /wheels /wheels
RUN pip install --no-index --find-links=/wheels -r auth/requirements.txt \
    && rm -rf /wheels

WORKDIR /auth

# Copy only application code
COPY . .

# Expose uvicorn port
EXPOSE 8000

# Start the FastAPI app
CMD ["uvicorn", "main:app", "--host", "0.0.0.0", "--port", "8000"]
