from aiogram import types
from keyboards import confirm_kb, interval_kb
from storage import add_pending, confirm_item
from parsers.ozon import parse_ozon
from parsers.wb import parse_wb

scheduler_ref = None

def set_scheduler(scheduler):
    global scheduler_ref
    scheduler_ref = scheduler

def register_handlers(dp, chat_id):

    @dp.message_handler(content_types=types.ContentType.TEXT)
    async def handle_link(message: types.Message):
        text = message.text or ""

        if "ozon.ru" not in text and "wildberries.ru" not in text:
            return

        await message.answer("🔍 Ссылку получил, обрабатываю…")

        item = parse_ozon(text) if "ozon.ru" in text else parse_wb(text)
        add_pending(chat_id, item)

        await message.answer(
            f"📦 {item['title']}\n💰 {item['price']} ₽\n\nДобавить в отслеживание?",
            reply_markup=confirm_kb()
        )

    @dp.callback_query_handler(lambda c: c.data == "confirm_yes")
    async def confirm(callback: types.CallbackQuery):
        await callback.message.answer(
            "⏱ Выбери интервал отслеживания:",
            reply_markup=interval_kb()
        )

    @dp.callback_query_handler(lambda c: c.data.startswith("interval_"))
    async def interval(callback: types.CallbackQuery):
        hours = int(callback.data.split("_")[1])
        item = confirm_item(chat_id, hours)

        if scheduler_ref:
            scheduler_ref.add_item_job(item)

        await callback.message.answer(
            f"✅ Товар добавлен\n⏱ Проверка каждые {hours} ч"
        )
