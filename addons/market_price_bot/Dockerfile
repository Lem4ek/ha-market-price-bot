ARG BUILD_FROM
FROM $BUILD_FROM

WORKDIR /app

# Python уже есть в base-образе
RUN apk add --no-cache python3 py3-pip

COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

COPY bot /app/bot

CMD ["python3", "/app/bot/main.py"]
