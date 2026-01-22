ARG BUILD_FROM
FROM ${BUILD_FROM}

# Устанавливаем зависимости системы (для playwright и matplotlib)
RUN apt-get update && apt-get install -y --no-install-recommends \
    libnss3 libatk-bridge2.0-0 libdrm2 libxkbcommon0 libgbm1 \
    libasound2 libatk1.0-0 libatspi2.0-0 libxcomposite1 libxdamage1 \
    libxrandr2 fonts-liberation \
    && rm -rf /var/lib/apt/lists/*

# Устанавливаем playwright
RUN pip install --no-cache-dir playwright && playwright install-deps chromium && playwright install chromium

WORKDIR /app

# Копируем файлы
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

COPY bot.py run.sh ./

RUN chmod a+x run.sh

CMD [ "/app/run.sh" ]