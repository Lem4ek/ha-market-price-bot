import asyncio
import logging
import json
import re
from datetime import datetime, timedelta
import aiosqlite
from aiogram import Bot, Dispatcher, types
from aiogram.filters import Command
from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton, CallbackQuery
from playwright.async_api import async_playwright, BrowserContext
from apscheduler.schedulers.asyncio import AsyncIOScheduler
import os
from dotenv import load_dotenv

load_dotenv()

TOKEN = os.getenv("TELEGRAM_TOKEN")
PROXY_SERVER = os.getenv("PROXY_SERVER")          # http://user:pass@ip:port
PROXY_USERNAME = os.getenv("PROXY_USERNAME")
PROXY_PASSWORD = os.getenv("PROXY_PASSWORD")

DEFAULT_INTERVAL_H = 6
GLOBAL_CHECK_TICK_MIN = 5   # тикать часто, но проверять реально реже

bot = Bot(token=TOKEN)
dp = Dispatcher()

DB_FILE = "prices.db"

async def init_db():
    async with aiosqlite.connect(DB_FILE) as db:
        await db.execute("""
            CREATE TABLE IF NOT EXISTS tracking (
                user_id INTEGER,
                url TEXT PRIMARY KEY,
                last_price REAL,
                title TEXT,
                last_check TEXT,
                history TEXT,           -- json str
                last_notified TEXT
            )
        """)
        await db.execute("""
            CREATE TABLE IF NOT EXISTS users_settings (
                user_id INTEGER PRIMARY KEY,
                interval_hours INTEGER DEFAULT ?
            )
        """, (DEFAULT_INTERVAL_H,))
        await db.commit()

# ------------------ Playwright + Proxy ------------------

async def get_browser_context(playwright):
    browser = await playwright.chromium.launch(headless=True)
    context = await browser.new_context(
        viewport={'width': 1920, 'height': 1080},
        user_agent='Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/131.0.0.0 Safari/537.36',
        proxy={
            'server': PROXY_SERVER,
            'username': PROXY_USERNAME,
            'password': PROXY_PASSWORD
        } if PROXY_SERVER else None
    )
    # stealth можно добавить через playwright-stealth, но для простоты пока базово
    return context

async def parse_ozon_price(url: str, context: BrowserContext) -> tuple[float | None, str | None]:
    page = await context.new_page()
    try:
        await page.goto(url, wait_until="networkidle", timeout=45000)
        await page.wait_for_timeout(3000)  # дать прогрузиться

        # 2026 — часто цена в window.__NUXT__ или window.__OZON_STATE__
        content = await page.content()
        price = None
        title = await page.title()

        # Попытка 1: JSON в скрипте (application/ld+json)
        json_ld = await page.evaluate("""() => {
            const script = document.querySelector('script[type="application/ld+json"]');
            return script ? script.innerText : null;
        }""")
        if json_ld:
            try:
                data = json.loads(json_ld)
                price = float(data.get("offers", {}).get("price", 0) or 0)
            except:
                pass

        # Попытка 2: поиск по тексту / классам (меняются, но часто работают)
        if not price:
            price_text = await page.evaluate("""() => {
                const els = document.querySelectorAll('[data-auto="mainPrice"], .ui-price, [itemprop="price"]');
                for (let el of els) {
                    let t = el.innerText.replace(/[^0-9]/g, '');
                    if (t && parseInt(t) > 100) return parseFloat(t);
                }
                return null;
            }""")
            if price_text:
                price = price_text

        return price, title.strip() if title else None
    except Exception as e:
        logging.error(f"Ozon parse error {url}: {e}")
        return None, None
    finally:
        await page.close()

async def parse_wb_price(url: str, context: BrowserContext) -> tuple[float | None, str | None]:
    page = await context.new_page()
    try:
        await page.goto(url, wait_until="networkidle", timeout=45000)
        await page.wait_for_timeout(2500)

        title = await page.title()

        # WB часто кладёт в window.__WB_DATA__ или data атрибуты
        price_str = await page.evaluate("""() => {
            const priceEl = document.querySelector('[data-auto="mainPrice"]') || 
                            document.querySelector('.price-block__final-price') ||
                            document.querySelector('[itemprop="price"]');
            return priceEl ? priceEl.innerText.replace(/[^0-9]/g, '') : null;
        }""")

        price = float(price_str) if price_str and price_str.isdigit() else None
        return price, title.strip() if title else None
    except Exception as e:
        logging.error(f"WB parse error {url}: {e}")
        return None, None
    finally:
        await page.close()

async def get_price(url: str, playwright):
    async with await get_browser_context(playwright) as context:
        if "ozon.ru" in url:
            return await parse_ozon_price(url, context)
        elif "wildberries.ru" in url:
            return await parse_wb_price(url, context)
        return None, None

# ------------------ Логика проверки ------------------

async def get_user_interval(user_id: int) -> int:
    async with aiosqlite.connect(DB_FILE) as db:
        row = await (await db.execute(
            "SELECT interval_hours FROM users_settings WHERE user_id = ?", (user_id,)
        )).fetchone()
        return row[0] if row else DEFAULT_INTERVAL_H

async def set_user_interval(user_id: int, hours: int):
    async with aiosqlite.connect(DB_FILE) as db:
        await db.execute(
            "INSERT OR REPLACE INTO users_settings VALUES (?, ?)",
            (user_id, hours)
        )
        await db.commit()

async def should_check(last_check: str | None, interval_h: int) -> bool:
    if not last_check:
        return True
    try:
        last = datetime.strptime(last_check, "%Y-%m-%d %H:%M")
        return datetime.now() >= last + timedelta(hours=interval_h)
    except:
        return True

async def check_prices():
    async with async_playwright() as p:
        async with aiosqlite.connect(DB_FILE) as db:
            users_cur = await db.execute("SELECT DISTINCT user_id FROM tracking")
            user_ids = [r[0] async for r in users_cur]

            for uid in user_ids:
                interval = await get_user_interval(uid)
                items_cur = await db.execute(
                    "SELECT url, last_price, title, history, last_check FROM tracking WHERE user_id = ?",
                    (uid,)
                )
                items = await items_cur.fetchall()

                for url, last_p, title, hist_str, last_c in items:
                    if not await should_check(last_c, interval):
                        continue

                    price, name = await get_price(url, p)
                    if price is None:
                        continue

                    now_str = datetime.now().strftime("%Y-%m-%d %H:%M")
                    hist = json.loads(hist_str) if hist_str else []
                    hist.append({"t": now_str, "p": price})
                    if len(hist) > 180:
                        hist = hist[-180:]

                    await db.execute(
                        "UPDATE tracking SET last_price=?, last_check=?, history=?, title=? WHERE url=?",
                        (price, now_str, json.dumps(hist), name or title, url)
                    )

                    if last_p is not None and price != last_p:
                        diff = price - last_p
                        sign = "↓" if diff < 0 else "↑"
                        text = (
                            f"Изменение цены!\n"
                            f"{title or name or 'Товар'}\n"
                            f"Было: {last_p:,.0f} ₽\nСтало: {price:,.0f} ₽ {sign} {abs(diff):,.0f} ₽\n"
                            f"{url}"
                        )

                        kb = None
                        if diff < -50:  # сильное снижение → кнопка отписки
                            kb = InlineKeyboardMarkup(inline_keyboard=[[
                                InlineKeyboardButton("Отписаться от товара", callback_data=f"unsub|{url}")
                            ]])

                        # График
                        if len(hist) >= 4:
                            import matplotlib.pyplot as plt
                            import io
                            dates = [datetime.strptime(d["t"], "%Y-%m-%d %H:%M") for d in hist]
                            prices = [d["p"] for d in hist]

                            fig, ax = plt.subplots(figsize=(7, 3.5))
                            ax.plot(dates, prices, marker='o', color='#1e88e5')
                            ax.grid(True, alpha=0.3)
                            plt.xticks(rotation=30)
                            plt.tight_layout()

                            buf = io.BytesIO()
                            fig.savefig(buf, format='png', dpi=120)
                            buf.seek(0)
                            plt.close(fig)

                            await bot.send_photo(uid, photo=buf, caption=text, reply_markup=kb)
                        else:
                            await bot.send_message(uid, text, reply_markup=kb)

                    await db.commit()

# ------------------ Хендлеры ------------------

@dp.message(Command("start"))
async def start(m: types.Message):
    await m.answer(
        "Кидай ссылку на товар с Ozon или Wildberries — начну отслеживать цену.\n\n"
        "/list — список + отписка\n"
        "/settings — выбрать интервал проверки (3/6/9/12 ч)"
    )

@dp.message(lambda m: "ozon.ru" in m.text or "wildberries.ru" in m.text)
async def add_by_link(m: types.Message):
    url = m.text.strip().split()[0]  # берём первую ссылку
    if not url.startswith("http"):
        url = "https://" + url

    async with async_playwright() as p:
        price, title = await get_price(url, p)

    if price is None:
        await m.reply("Не удалось получить цену. Возможно блокировка или неверная ссылка.")
        return

    now = datetime.now().strftime("%Y-%m-%d %H:%M")
    hist = json.dumps([{"t": now, "p": price}])

    async with aiosqlite.connect(DB_FILE) as db:
        await db.execute(
            """INSERT OR REPLACE INTO tracking 
               (user_id, url, last_price, title, last_check, history) 
               VALUES (?, ?, ?, ?, ?, ?)""",
            (m.from_user.id, url, price, title, now, hist)
        )
        await db.commit()

    await m.reply(f"✅ Добавлен\n{title or '—'}\n{price:,.0f} ₽")

@dp.message(Command("list"))
async def list_cmd(m: types.Message):
    async with aiosqlite.connect(DB_FILE) as db:
        cur = await db.execute(
            "SELECT url, title, last_price FROM tracking WHERE user_id = ?",
            (m.from_user.id,)
        )
        rows = await cur.fetchall()

    if not rows:
        await m.reply("Нет отслеживаемых товаров.")
        return

    text = "Твои товары:\n\n"
    buttons = []
    for url, title, price in rows:
        short = title[:40] + "…" if title and len(title) > 40 else (title or url[:50]+"…")
        text += f"• {short} — {price:,.0f} ₽\n"
        buttons.append([InlineKeyboardButton(f"Отписаться: {short}", callback_data=f"unsub|{url}")])

    kb = InlineKeyboardMarkup(inline_keyboard=buttons)
    await m.reply(text, reply_markup=kb, disable_web_page_preview=True)

@dp.message(Command("settings"))
async def settings(m: types.Message):
    kb = InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton("3 часа", callback_data="int:3")],
        [InlineKeyboardButton("6 часов", callback_data="int:6")],
        [InlineKeyboardButton("9 часов", callback_data="int:9")],
        [InlineKeyboardButton("12 часов", callback_data="int:12")],
    ])
    cur_int = await get_user_interval(m.from_user.id)
    await m.reply(f"Текущий интервал: {cur_int} ч\nВыбери:", reply_markup=kb)

@dp.callback_query(lambda c: c.data.startswith("int:"))
async def set_int_cb(c: CallbackQuery):
    h = int(c.data.split(":")[1])
    await set_user_interval(c.from_user.id, h)
    await c.message.edit_text(f"Интервал: каждые {h} часов")
    await c.answer()

@dp.callback_query(lambda c: c.data.startswith("unsub|"))
async def unsubscribe_cb(c: CallbackQuery):
    url = c.data.split("|", 1)[1]
    async with aiosqlite.connect(DB_FILE) as db:
        await db.execute("DELETE FROM tracking WHERE user_id = ? AND url = ?", (c.from_user.id, url))
        await db.commit()
    await c.message.edit_reply_markup(None)
    await c.answer("Отписка выполнена", show_alert=True)

async def main():
    await init_db()
    scheduler = AsyncIOScheduler()
    scheduler.add_job(check_prices, 'interval', minutes=GLOBAL_CHECK_TICK_MIN)
    scheduler.start()
    await dp.start_polling(bot, allowed_updates=types.AllowedUpdates.MESSAGE)

if __name__ == "__main__":
    logging.basicConfig(level=logging.INFO)
    asyncio.run(main())