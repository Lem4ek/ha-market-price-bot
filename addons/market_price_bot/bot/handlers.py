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

    @dp.message_handler(lambda m: "ozon.ru" in m.text or "wildberries.ru" in m.text)
    async def handle_link(message: types.Message):
        url = message.text.strip()

        item = parse_ozon(url) if "ozon.ru" in url else parse_wb(url)
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
