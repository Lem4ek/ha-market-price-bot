import requests, re

def parse_wb(url):
    html = requests.get(
        url,
        headers={"User-Agent": "Mozilla/5.0"}
    ).text

    price = int(re.search(r'"salePriceU":(\d+)', html).group(1)) // 100
    title = re.search(r'"goodsName":"([^"]+)"', html).group(1)

    return {"title": title, "price": price, "url": url}
