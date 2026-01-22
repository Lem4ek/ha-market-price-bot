ARG BUILD_FROM=ghcr.io/home-assistant/aarch64-base:latest
FROM $BUILD_FROM

WORKDIR /app

# Ставим python + venv
RUN apk add --no-cache python3 py3-pip py3-virtualenv

# Создаём виртуальное окружение
RUN python3 -m venv /app/venv

# Делаем venv дефолтным
ENV PATH="/app/venv/bin:$PATH"

COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

COPY bot /app/bot
COPY rootfs /
RUN chmod +x /etc/services.d/bot/run

