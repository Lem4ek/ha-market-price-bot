import os
from aiogram import Bot, Dispatcher, executor
from handlers import register_handlers, set_scheduler
from scheduler import PriceScheduler

TOKEN = os.getenv("TELEGRAM_TOKEN")
CHAT_ID = int(os.getenv("CHAT_ID"))

bot = Bot(token=TOKEN)
dp = Dispatcher(bot)

scheduler = PriceScheduler(bot, CHAT_ID)
set_scheduler(scheduler)

register_handlers(dp, CHAT_ID)

scheduler.start()
executor.start_polling(dp)
