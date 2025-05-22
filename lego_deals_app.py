import requests
from bs4 import BeautifulSoup
import re

HEADERS = {
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64)"
}

def is_50_percent_off(price, original):
    try:
        p = float(re.sub(r"[^\d.]", "", price))
        o = float(re.sub(r"[^\d.]", "", original))
        return o > 0 and (p / o) <= 0.5
    except:
        return False

def fetch_walmart_deals():
    url = "https://www.walmart.com/search/?query=lego"
    res = requests.get(url, headers=HEADERS)
    soup = BeautifulSoup(res.text, "html.parser")
    deals = []
    # Example selectors; you may need to adjust as Walmart updates site
    items = soup.select("div.search-result-gridview-item-wrapper")
    for item in items:
        title_tag = item.select_one("a.product-title-link span")
        price_current = item.select_one("span.price-characteristic")
        price_original = item.select_one("span.price-old")
        if title_tag and price_current and price_original:
            if is_50_percent_off(price_current.text, price_original.text):
                link = item.select_one("a.product-title-link")['href']
                deals.append({"title": title_tag.text.strip(), "url": "https://www.walmart.com" + link})
    return deals

def fetch_target_deals():
    url = "https://www.target.com/s?searchTerm=lego"
    res = requests.get(url, headers=HEADERS)
    soup = BeautifulSoup(res.text, "html.parser")
    deals = []
    items = soup.select("li.h-padding-h-tight")
    for item in items:
        title_tag = item.select_one("a[data-test='product-title']")
        price_current = item.select_one("div[data-test='product-price'] span[data-test='current-price']")
        price_original = item.select_one("div[data-test='product-price'] span[data-test='original-price']")
        if title_tag and price_current and price_original:
            if is_50_percent_off(price_current.text, price_original.text):
                link = title_tag['href']
                deals.append({"title": title_tag.text.strip(), "url": "https://www.target.com" + link})
    return deals

def fetch_bestbuy_deals():
    url = "https://www.bestbuy.com/site/searchpage.jsp?st=lego"
    res = requests.get(url, headers=HEADERS)
    soup = BeautifulSoup(res.text, "html.parser")
    deals = []
    items = soup.select("li.sku-item")
    for item in items:
        title_tag = item.select_one("h4.sku-header a")
        price_current = item.select_one("div.priceView-hero-price span")
        price_original = item.select_one("div.priceView-customer-price span")
        if title_tag and price_current and price_original:
            if is_50_percent_off(price_current.text, price_original.text):
                link = title_tag['href']
                deals.append({"title": title_tag.text.strip(), "url": "https://www.bestbuy.com" + link})
    return deals

def fetch_kohls_deals():
    url = "https://www.kohls.com/search.jsp?search=lego"
    res = requests.get(url, headers=HEADERS)
    soup = BeautifulSoup(res.text, "html.parser")
    deals = []
    items = soup.select("div.product")
    for item in items:
        title_tag = item.select_one("a.product-title-link")
        price_current = item.select_one("span.price")
        price_original = item.select_one("span.price-standard")
        if title_tag and price_current and price_original:
            if is_50_percent_off(price_current.text, price_original.text):
                deals.append({"title": title_tag.text.strip(), "url": "https://www.kohls.com" + title_tag['href']})
    return deals

import urllib3
urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)

def fetch_lego_com_deals():
    url = "https://www.lego.com/en-us/categories/sales-and-deals"
    res = requests.get(url, headers=HEADERS, verify=False)  # <-- disable SSL verify here
    soup = BeautifulSoup(res.text, "html.parser")
    deals = []
    items = soup.select("a.product-tile")
    for item in items:
        title_tag = item.select_one("h3.product-name")
        price_current = item.select_one("span.current-price")
        price_original = item.select_one("span.original-price")
        if title_tag and price_current and price_original:
            if is_50_percent_off(price_current.text, price_original.text):
                link = item['href']
                deals.append({"title": title_tag.text.strip(), "url": "https://www.lego.com" + link})
    return deals


def main():
    all_deals = []
    all_deals.extend(fetch_walmart_deals())
    all_deals.extend(fetch_target_deals())
    all_deals.extend(fetch_bestbuy_deals())
    all_deals.extend(fetch_kohls_deals())
    all_deals.extend(fetch_lego_com_deals())

    print(f"Found {len(all_deals)} deals 50% off or more:")
    for deal in all_deals:
        print(f"- {deal['title']} -> {deal['url']}")

if __name__ == "__main__":
    main()
