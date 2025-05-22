import requests
from bs4 import BeautifulSoup
import re

HEADERS = {
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko)"
                  " Chrome/114.0.0.0 Safari/537.36"
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

def fetch_target():
    url = "https://www.target.com/s?searchTerm=lego"
    res = requests.get(url, headers=HEADERS)
    soup = BeautifulSoup(res.text, "html.parser")
    deals = []

    items = soup.find_all("li", {"data-test": "product-listgrid-item"})

    for item in items:
        title_tag = item.find("a", {"data-test": "product-title"})
        price_current = item.find("div", {"data-test": "product-price"})
        price_original = item.find("span", {"class": "h-padding-h-tight"})

        if title_tag and price_current:
            title = title_tag.text.strip()
            current_price = parse_price(price_current.text) or 0
            original_price = parse_price(price_original.text) if price_original else current_price

            if original_price and original_price > current_price:
                url_path = title_tag["href"]
                deals.append({
                    "store": "Target",
                    "title": title,
                    "url": "https://www.target.com" + url_path,
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

def fetch_lego_com():
    url = "https://www.lego.com/en-us/themes/star-wars"  # Example category
    res = requests.get(url, headers=HEADERS)
    soup = BeautifulSoup(res.text, "html.parser")
    deals = []

    items = soup.find_all("div", {"class": "product-card"})

    for item in items:
        title_tag = item.find("a", {"class": "product-card-link"})
        price_current_tag = item.find("span", {"class": "product-price--current"})
        price_original_tag = item.find("span", {"class": "product-price--original"})

        if title_tag and price_current_tag and price_original_tag:
            title = title_tag.text.strip()
            current_price = parse_price(price_current_tag.text)
            original_price = parse_price(price_original_tag.text)

            if original_price and original_price > current_price:
                url_path = title_tag["href"]
                deals.append({
                    "store": "LEGO.com",
                    "title": title,
                    "url": "https://www.lego.com" + url_path,
                    "current_price": current_price,
                    "original_price": original_price,
                    "discount": round(original_price - current_price, 2)
                })
    return deals

def fetch_amazon():
    url = "https://www.amazon.com/s?k=lego"
    res = requests.get(url, headers=HEADERS)
    soup = BeautifulSoup(res.text, "html.parser")
    deals = []

    # Amazon is hard to scrape, but let's try a simple approach
    items = soup.find_all("div", {"data-component-type": "s-search-result"})

    for item in items:
        title_tag = item.find("h2")
        price_whole = item.find("span", {"class": "a-price-whole"})
        price_fraction = item.find("span", {"class": "a-price-fraction"})
        price_original_tag = item.find("span", {"class": "a-text-price"})

        if title_tag and price_whole and price_fraction:
            title = title_tag.text.strip()
            current_price = parse_price(price_whole.text + "." + price_fraction.text)
            original_price = parse_price(price_original_tag.text) if price_original_tag else current_price

            if original_price and original_price > current_price:
                link_tag = title_tag.find("a", href=True)
                url_path = link_tag["href"] if link_tag else "#"
                deals.append({
                    "store": "Amazon",
                    "title": title,
                    "url": "https://www.amazon.com" + url_path,
                    "current_price": current_price,
                    "original_price": original_price,
                    "discount": round(original_price - current_price, 2)
                })
    return deals

def main():
    all_deals = []
    all_deals.extend(fetch_walmart())
    all_deals.extend(fetch_target())
    all_deals.extend(fetch_bestbuy())
    all_deals.extend(fetch_lego_com())
    all_deals.extend(fetch_amazon())

    # Sort by current price, low to high
    sorted_deals = sorted(all_deals, key=lambda x: x["current_price"])

    print("All LEGO deals on sale (sorted cheapest → expensive):\n")
    for d in sorted_deals:
        print(f"{d['store']}: {d['title']}")
        print(f"  Price: ${d['current_price']} (was ${d['original_price']}) — Save ${d['discount']}")
        print(f"  Link: {d['url']}\n")

if __name__ == "__main__":
    main()
