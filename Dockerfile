FROM ubuntu:noble

ENV PYTHONDONTWRITEBYTECODE=1
ENV PYTHONUNBUFFERED=1
ENV PATH="/venv/bin:$PATH"

WORKDIR /app
RUN useradd -m django

# Install system dependencies
RUN apt-get update && apt-get install -y --no-install-recommends \
    libpq-dev \
    curl \
    gcc \
    gdal-bin \
    python3-dev \
    python3-pip \
    python3-setuptools \
    && rm -rf /var/lib/apt/lists/*
# Install Python dependencies
COPY requirements /requirements
RUN python3 -m pip install --break-system-packages uv
RUN uv venv /venv
RUN uv pip install  -r /requirements/base.txt
# Copy project
COPY . .

