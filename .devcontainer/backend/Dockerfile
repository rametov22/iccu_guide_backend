FROM python:3.12-slim


ENV PYTHONDONTWRITEBYTECODE=1
ENV PYTHONUNBUFFERED=1
ENV PRODUCTION=0


RUN apt-get update && apt-get install -y --no-install-recommends \
    build-essential \
    libpq-dev \
    gcc \
    curl \
    gettext \
    libgdbm-dev \
    git \
    && apt-get clean \
    && rm -rf /var/lib/apt/lists/*


WORKDIR /app

COPY ../../backend/requirements/dev.txt .
RUN pip config set global.break-system-packages true
RUN pip install --no-cache-dir -r dev.txt


CMD ["python", "infinity"]
