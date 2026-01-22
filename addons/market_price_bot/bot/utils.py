import re

def make_entity_id(title: str) -> str:
    safe = re.sub(r"[^a-z0-9]+", "_", title.lower())
    return f"sensor.market_price_{safe[:50]}"
