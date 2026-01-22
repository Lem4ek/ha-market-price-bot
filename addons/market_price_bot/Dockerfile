FROM python:3.11-alpine

ENV PYTHONUNBUFFERED=1

WORKDIR /app

RUN apk add --no-cache \
    gcc \
    musl-dev \
    linux-headers \
    libffi-dev \
    openssl-dev \
    tzdata

COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

COPY bot /app/bot
COPY run.sh /app/run.sh
RUN chmod +x /app/run.sh

CMD ["/app/run.sh"]
