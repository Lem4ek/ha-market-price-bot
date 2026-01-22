import logging
import json
from aiogram import Bot, Dispatcher, executor, types

from parser_ozon import parse_ozon
from parser_wb import parse_wb
from ha_client import set_price_sensor
from utils import make_entity_id

logging.basicConfig(level=logging.INFO)

OPTIONS_PATH = "/data/options.json"

with open(OPTIONS_PATH, "r") as f:
    options = json.load(f)

TOKEN = options["telegram_token"]

bot = Bot(token=TOKEN, parse_mode="HTML")
dp = Dispatcher(bot)


@dp.message_handler(commands=["start"])
async def start(message: types.Message):
    await message.answer(
        "👋 Я отслеживаю цены товаров.\n\n"
        "Пришли ссылку на товар из Ozon или Wildberries."
    )


@dp.message_handler(commands=["list"])
async def list_cmd(message: types.Message):
    await message.answer("📦 Список товаров пока пуст.")


@dp.message_handler(regexp=r"https?://")
async def handle_link(message: types.Message):
    url = message.text.strip()

    if "ozon.ru" in url:
        title, price = parse_ozon(url)
        shop = "ozon"
    elif "wildberries.ru" in url:
        title, price = parse_wb(url)
        shop = "wb"
    else:
        await message.answer("❌ Поддерживаются только Ozon и Wildberries")
        return

    entity_id = make_entity_id(title)

    set_price_sensor(
        entity_id=entity_id,
        price=price,
        title=title,
        shop=shop,
        url=url,
    )

    await message.answer(
        f"🛒 <b>{title}</b>\n\n"
        f"💰 Цена сейчас: <b>{price} ₽</b>\n"
        f"📡 Сенсор создан в Home Assistant"
    )


if __name__ == "__main__":
    logging.info("Market Price Bot started")
    executor.start_polling(dp, skip_updates=True)
