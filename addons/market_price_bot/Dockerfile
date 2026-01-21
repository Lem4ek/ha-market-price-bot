ARG BUILD_FROM
FROM $BUILD_FROM

ENV LANG=C.UTF-8

WORKDIR /app

# Python + pip
RUN apk add --no-cache \
    python3 \
    py3-pip \
    py3-setuptools

# зависимости
COPY requirements.txt /app/requirements.txt
RUN pip3 install --no-cache-dir --break-system-packages -r /app/requirements.txt

# код
COPY bot /app/bot
COPY run.sh /app/run.sh

# ПРАВИЛЬНЫЙ CMD
CMD ["/app/run.sh"]
