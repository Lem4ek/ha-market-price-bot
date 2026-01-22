import json
import logging

from aiogram import Bot, Dispatcher, executor, types

# ----------------------------
# ЛОГИ
# ----------------------------
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# ----------------------------
# ЧТЕНИЕ НАСТРОЕК HOME ASSISTANT
# ----------------------------
OPTIONS_PATH = "/data/options.json"

try:
    with open(OPTIONS_PATH, "r") as f:
        options = json.load(f)
except Exception as e:
    raise RuntimeError(f"Cannot read {OPTIONS_PATH}: {e}")

TOKEN = options.get("telegram_token")
CHAT_ID = options.get("chat_id")

if not TOKEN:
    raise RuntimeError("telegram_token is not set in add-on configuration")

# ----------------------------
# TELEGRAM BOT
# ----------------------------
bot = Bot(token=TOKEN, parse_mode="HTML")
dp = Dispatcher(bot)


@dp.message_handler(commands=["start"])
async def start_handler(message: types.Message):
    await message.answer(
        "👋 Привет!\n\n"
        "Отправь ссылку на товар с Ozon или Wildberries — "
        "я её поймаю 😉"
    )


@dp.message_handler()
async def any_message_handler(message: types.Message):
    text = message.text.strip()

    logger.info(f"Received message: {text}")

    # Пока просто отвечаем — это проверка, что бот живой
    await message.answer(
        "🔗 Ссылку получил!\n\n"
        f"<code>{text}</code>\n\n"
        "Дальше подключим отслеживание цены 📈"
    )


# ----------------------------
# START
# ----------------------------
if __name__ == "__main__":
    logger.info("Market Price Bot started")
    executor.start_polling(dp, skip_updates=True)
