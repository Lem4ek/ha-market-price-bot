FROM python:3.12-alpine

ENV PYTHONUNBUFFERED=1

WORKDIR /app

# системные зависимости
RUN apk add --no-cache \
    bash \
    curl \
    tzdata

# python зависимости
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# код
COPY bot /app/bot
COPY run.sh /app/run.sh
RUN chmod +x /app/run.sh

CMD ["/app/run.sh"]
