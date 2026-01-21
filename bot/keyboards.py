from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton

def confirm_kb():
    kb = InlineKeyboardMarkup()
    kb.add(
        InlineKeyboardButton("✅ Да", callback_data="confirm_yes"),
        InlineKeyboardButton("❌ Нет", callback_data="confirm_no")
    )
    return kb

def interval_kb():
    kb = InlineKeyboardMarkup(row_width=2)
    for h in (3, 6, 9, 12):
        kb.insert(
            InlineKeyboardButton(f"{h} часов", callback_data=f"interval_{h}")
        )
    return kb
