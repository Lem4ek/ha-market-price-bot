import os
from aiogram import Bot, Dispatcher, executor
from handlers import register_handlers

TOKEN = os.getenv("TELEGRAM_TOKEN")
CHAT_ID = int(os.getenv("CHAT_ID"))

bot = Bot(token=TOKEN)
dp = Dispatcher(bot)

register_handlers(dp, CHAT_ID)

executor.start_polling(dp)
