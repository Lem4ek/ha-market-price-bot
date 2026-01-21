ARG BUILD_FROM
FROM $BUILD_FROM

ENV LANG C.UTF-8

WORKDIR /app

COPY requirements.txt /app/
RUN pip3 install --no-cache-dir -r /app/requirements.txt

COPY bot /app/bot
COPY run.sh /app/run.sh

CMD ["sh", "/app/run.sh"]
