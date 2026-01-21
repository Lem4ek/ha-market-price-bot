ARG BUILD_FROM=ghcr.io/home-assistant/addon-base-python:3.12
FROM $BUILD_FROM

ENV LANG=C.UTF-8

WORKDIR /app

# Python зависимости
COPY requirements.txt /app/requirements.txt
RUN pip install --no-cache-dir -r /app/requirements.txt

# Код бота
COPY bot /app/bot
COPY run.sh /app/run.sh

# Запуск через s6
CMD ["/app/run.sh"]
