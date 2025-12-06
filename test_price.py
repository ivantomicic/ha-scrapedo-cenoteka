import requests
from bs4 import BeautifulSoup

URL = "https://cenoteka.rs/p/salto-pale-ale-033l/"
SCRAPE_DO_TOKEN = "8d43d47f5a594b5999966fd7fbfa05a04726c2e8da7"

scrape_url = (
    "http://api.scrape.do/"
    f"?url={URL}"
    f"&token={SCRAPE_DO_TOKEN}"
    "&output=raw"
)

resp = requests.get(scrape_url, timeout=30)
resp.raise_for_status()

soup = BeautifulSoup(resp.text, "lxml")

prices_by_store = {}

rows = soup.select(".bg-white .prices_offline_col .row")

for row in rows:
    img = row.select_one("img[alt]")
    price_el = row.select_one(".product_price")

    if not img or not price_el:
        continue

    store = img["alt"].strip()
    price_text = price_el.get_text(strip=True)

    try:
        price = float(price_text.replace(".", "").replace(",", "."))
    except ValueError:
        continue

    prices_by_store[store] = price

print(prices_by_store)