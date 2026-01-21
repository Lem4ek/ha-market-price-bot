import sqlite3

db = sqlite3.connect("/data/market.db", check_same_thread=False)
cur = db.cursor()

cur.execute("""
CREATE TABLE IF NOT EXISTS items (
 id INTEGER PRIMARY KEY,
 title TEXT,
 url TEXT,
 price INTEGER,
 interval INTEGER
)
""")

pending = {}

def add_pending(chat_id, item):
    pending[chat_id] = item

def confirm_item(chat_id, interval):
    item = pending.pop(chat_id)
    cur.execute(
        "INSERT INTO items VALUES (NULL,?,?,?,?)",
        (item["title"], item["url"], item["price"], interval)
    )
    db.commit()
