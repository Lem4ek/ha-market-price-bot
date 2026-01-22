import requests
import json

OPTIONS_PATH = "/data/options.json"

with open(OPTIONS_PATH, "r") as f:
    options = json.load(f)

HA_URL = options["ha_url"]
HA_TOKEN = options["ha_token"]

HEADERS = {
    "Authorization": f"Bearer {HA_TOKEN}",
    "Content-Type": "application/json",
}

def set_price_sensor(entity_id, price, title, shop, url):
    payload = {
        "state": price,
        "attributes": {
            "friendly_name": title,
            "shop": shop,
            "url": url,
            "unit_of_measurement": "₽",
            "device_class": "monetary",
        },
    }

    r = requests.post(
        f"{HA_URL}/api/states/{entity_id}",
        headers=HEADERS,
        json=payload,
        timeout=15,
    )

    r.raise_for_status()
