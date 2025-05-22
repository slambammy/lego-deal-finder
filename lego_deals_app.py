import streamlit as st
import requests
from bs4 import BeautifulSoup
import re

HEADERS = {
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64)"
}

def is_10_dollars_off(current, original):
    try:
        p = float(re.sub(r"[^\d.]", "", current))
        o = float(re.sub(r"[^\d.]", "", original))
        return (o - p) >= 10
    except:
        return False

def fetch_walmart_deals():
    url = "https://www.walmart.com/search/?query=lego"
    res = requests.get(url, headers=HEADERS)
    soup = BeautifulSoup(res.text, "html.parser")
    deals = []
    items = soup.select("div.search-result-gridview-item-wrapper")
    for item in items:
        title_tag = item.select_one("a.product-title-link span")
        price_current = item.select_one("span.price-characteristic")
        price_original = item.select_one("span.price-old")
        if title_tag and price_current and price_original:
            if is_10_dollars_off(price_current.text, price_original.text):
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
            if is_10_dollars_off(price_current.text, price_original.text):
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
            if is_10_dollars_off(price_current.text, price_original.text):
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
            if is_10_dollars_off(price_current.text, price_original.text):
                deals.append({"title": title_tag.text.strip(), "url": "https://www.kohls.com" + title_tag['href']})
    return deals

def fetch_amazon_deals():
    url = "https://www.amazon.com/s?k=lego"
    res = requests.get(url, headers=HEADERS)
    soup = BeautifulSoup(res.text, "html.parser")
    deals = []
    items = soup.select("div.s-result-item[data-component-type='s-search-result']")
    for item in items:
        title_tag = item.select_one("h2 a span")
        link_tag = item.select_one("h2 a")
        price_whole = item.select_one("span.a-price-whole")
        price_fraction = item.select_one("span.a-price-fraction")
        original_price = item.select_one("span.a-text-price span.a-offscreen")
        if title_tag and price_whole and original_price and link_tag:
            current_price = price_whole.text + (price_fraction.text if price_fraction else "")
            if is_10_dollars_off(current_price, original_price.text):
                deals.append({"title": title_tag.text.strip(), "url": "https://www.amazon.com" + link_tag['href']})
    return deals

# Streamlit UI
st.title("🧱 LEGO Deal Finder – $10 Off or More")
st.markdown("Shows LEGO deals with **$10 or more** in savings from major stores.")

if st.button("Find Deals Now"):
    with st.spinner("Searching for LEGO deals..."):
        all_deals = []
        all_deals.extend(fetch_walmart_deals())
        all_deals.extend(fetch_target_deals())
        all_deals.extend(fetch_bestbuy_deals())
        all_deals.extend(fetch_kohls_deals())
        all_deals.extend(fetch_amazon_deals())

        if all_deals:
            st.success(f"Found {len(all_deals)} LEGO deals with $10+ discounts:")
            for deal in all_deals:
                st.markdown(f"- [{deal['title']}]({deal['url']})")
        else:
            st.info("No LEGO discounts of $10+ found right now. Try again later!")
