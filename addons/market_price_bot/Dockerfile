ARG BUILD_FROM
FROM $BUILD_FROM

ENV LANG=C.UTF-8

WORKDIR /app

# 1️⃣ Устанавливаем Python и pip
RUN apk add --no-cache \
    python3 \
    py3-pip \
    py3-setuptools

# 2️⃣ Копируем зависимости
COPY requirements.txt /app/requirements.txt

# 3️⃣ Ставим Python-библиотеки
RUN pip3 install --no-cache-dir -r /app/requirements.txt

# 4️⃣ Копируем код
COPY bot /app/bot
COPY run.sh /app/run.sh

# 5️⃣ Запуск
CMD ["sh", "/app/run.sh"]
