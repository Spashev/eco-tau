# Используйте официальный образ Python
FROM python:3.12-bullseye AS base

# Установите переменные среды
ENV LANG C.UTF-8
ENV LC_ALL C.UTF-8
ENV PYTHONFAULTHANDLER 1
ENV PYTHONBUFFERED 1
ENV PIP_DISABLE_PIP_VERSION_CHECK 1
ENV PYTHONDONTWRITEBYTECODE 1
ENV PYTHONUNBUFFERED 1
ENV ROOT=/app
ENV TZ=Asia/Astana

# Рабочая директория
WORKDIR $ROOT

# Add alpine mirrors
RUN set -eux; \
    apt-get update && apt-get install -y --no-install-recommends \
    apt-utils \
    libc-dev \
    gcc \
    gettext \
    screen \
    vim \
    build-essential \
    postgresql \
    postgresql-contrib \
    netcat-traditional \
    && apt-get clean && rm -rf /var/lib/apt/lists/*

# Копирование кода
COPY app/ $ROOT
COPY docker/start.sh docker/entrypoint.sh $ROOT/commands/
RUN chmod +x $ROOT/commands/*
ENV PATH="$ROOT/commands:$PATH"

# Обновление pip
RUN pip install --upgrade pip &&  pip install -r requirements.txt

EXPOSE 8000
EXPOSE 9000

# Установка точки входа
CMD ["entrypoint.sh", "start.sh"]
