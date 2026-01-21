import requests, re

def parse_ozon(url):
    html = requests.get(url, headers={"User-Agent": "Mozilla/5.0"}).text
    price = int(re.search(r'"price":(\d+)', html).group(1))
    title = re.search(r'"name":"([^"]+)"', html).group(1)
    return {"title": title, "price": price, "url": url}
