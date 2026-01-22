FROM python:3.12-alpine

ENV PYTHONUNBUFFERED=1

WORKDIR /app

# системные и build зависимости
RUN apk add --no-cache \
    gcc \
    musl-dev \
    linux-headers \
    libffi-dev \
    openssl-dev \
    tzdata

# python зависимости
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# код бота
COPY bot /app/bot
COPY run.sh /app/run.sh
RUN chmod +x /app/run.sh

CMD ["/app/run.sh"]
