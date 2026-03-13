FROM python:3.12-slim

WORKDIR /workspace

RUN apt-get update && apt-get install -y --no-install-recommends \
    build-essential \
    libpq-dev \
    && rm -rf /var/lib/apt/lists/*

COPY pyproject.toml /workspace/
RUN pip install --no-cache-dir -e .

COPY . /workspace

ENV PYTHONPATH=/workspace/packages:/workspace
