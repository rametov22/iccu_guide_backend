FROM python:3.12-slim

# Ускоряет вывод Python и предотвращает создание .pyc файлов
ENV PYTHONDONTWRITEBYTECODE=1
ENV PYTHONUNBUFFERED=1
ENV PRODUCTION=1

# Установка системных зависимостей
RUN apt-get update && apt-get install -y --no-install-recommends \
    build-essential \
    libpq-dev \
    gcc \
    curl \
    gettext \
    libgdbm-dev \
    && apt-get clean \
    && rm -rf /var/lib/apt/lists/*

# Рабочая директория
WORKDIR /app

# Настройка pip
RUN pip config set global.break-system-packages true
RUN pip install --upgrade pip setuptools wheel

# Установка зависимостей проекта
COPY ../../backend/requirements/prod.txt .
RUN pip install --no-cache-dir -r prod.txt

# Копирование проекта
COPY ../../backend/ .

# Команда запуска
CMD ["python", "manage.py", "runserver", "0.0.0.0:8000"]