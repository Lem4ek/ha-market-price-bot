import sqlite3

DB_PATH = "/data/market.db"

db = sqlite3.connect(DB_PATH, check_same_thread=False)
db.row_factory = sqlite3.Row
cur = db.cursor()

cur.execute("""
CREATE TABLE IF NOT EXISTS items (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    title TEXT,
    url TEXT,
    price INTEGER,
    interval INTEGER
)
""")
db.commit()

pending = {}

def add_pending(chat_id, item):
    pending[chat_id] = item

def confirm_item(chat_id, interval):
    item = pending.pop(chat_id)
    cur.execute(
        "INSERT INTO items (title, url, price, interval) VALUES (?,?,?,?)",
        (item["title"], item["url"], item["price"], interval)
    )
    db.commit()

def get_items():
    cur.execute("SELECT * FROM items")
    return cur.fetchall()

def update_price(item_id, new_price):
    cur.execute(
        "UPDATE items SET price = ? WHERE id = ?",
        (new_price, item_id)
    )
    db.commit()
