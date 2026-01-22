#!/usr/bin/env bash
set -e

# Передаём переменные окружения из config.yaml → .env или прямо в python
# Можно использовать python-dotenv, но для простоты передаём через env

exec python3 /app/bot.py