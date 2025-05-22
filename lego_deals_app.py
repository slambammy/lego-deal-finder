import requests
from bs4 import BeautifulSoup
import re

HEADERS = {
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) "
                  "Chrome/114.0.0.0 Safari/537.36"
}

def parse_price(text):
    match = re.search(r"\$([\d,]+\.?\d*)", text)
    if match:
        return float(match.group(1).replace(",", ""))
    return None

def fetch_walmart():
    url = "https://www.walmart.com/search?q=lego"
    res = requests.get(url, headers=HEADERS)
    soup = BeautifulSoup(res.text, "html.parser")
    deals = []

    items = soup.find_all("div", {"data-item-id": True})

    for item in items:
        title_tag = item.find("a", {"class": re.compile(r"absolute.*hide-sibling-opacity")})
        price_spans = item.find_all("span", string=re.compile(r"\$\d"))

        prices = [parse_price(span.text) for span in price_spans if parse_price(span.text) is not None]
        if title_tag and len(prices) >= 2:
            current_price = min(prices)
            original_price = max(prices)
            if original_price > current_price:
                title = title_tag.text.strip()
                url_path = title_tag["href"]
                deals.append({
                    "store": "Walmart",
                    "title": title,
                    "url": "https://www.walmart.com" + url_path,
                    "current_price": current_price,
                    "original_price": original_price,
                    "discount": round(original_price - current_price, 2)
                })
    return deals

def fetch_bestbuy():
    url = "https://www.bestbuy.com/site/searchpage.jsp?st=lego"
    res = requests.get(url, headers=HEADERS)
    soup = BeautifulSoup(res.text, "html.parser")
    deals = []

    items = soup.find_all("li", {"class": "sku-item"})

    for item in items:
        title_tag = item.find("h4", {"class": "sku-header"})
        price_current_tag = item.find("div", {"class": "priceView-hero-price priceView-customer-price"})
        price_original_tag = item.find("div", {"class": "pricing-price__regular-price"})

        if title_tag and price_current_tag:
            title = title_tag.text.strip()
            current_price = parse_price(price_current_tag.text)
            original_price = parse_price(price_original_tag.text) if price_original_tag else current_price

            if original_price and original_price > current_price:
                link = title_tag.find("a")["href"]
                deals.append({
                    "store": "Best Buy",
                    "title": title,
                    "url": "https://www.bestbuy.com" + link,
                    "current_price": current_price,
                    "original_price": original_price,
                    "discount": round(original_price - current_price, 2)
                })
    return deals

def main():
    all_deals = []
    all_deals.extend(fetch_walmart())
    all_deals.extend(fetch_bestbuy())

    sorted_deals = sorted(all_deals, key=lambda x: x["current_price"])

    print("All LEGO deals on sale from Walmart and Best Buy (sorted cheapest → expensive):\n")
    for d in sorted_deals:
        print(f"{d['store']}: {d['title']}")
        print(f"  Price: ${d['current_price']} (was ${d['original_price']}) — Save ${d['discount']}")
        print(f"  Link: {d['url']}\n")

if __name__ == "__main__":
    main()
