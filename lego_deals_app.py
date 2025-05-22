import streamlit as st
import requests
from bs4 import BeautifulSoup
import re

HEADERS = {
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) "
                  "AppleWebKit/537.36 (KHTML, like Gecko) "
                  "Chrome/113.0.0.0 Safari/537.36"
}

def is_50_percent_off(price, original):
    try:
        p = float(re.sub(r"[^\d.]", "", price))
        o = float(re.sub(r"[^\d.]", "", original))
        return o > 0 and (p / o) <= 0.5
    except:
        return False

def fetch_walmart_deals():
    url = "https://www.walmart.com/search?q=lego"
    response = requests.get(url, headers=HEADERS)
    soup = BeautifulSoup(response.text, "html.parser")
    items = soup.select("div[data-item-id]")
    deals = []

    for item in items:
        title_tag = item.select_one("a span")
        price_tag = item.select_one("span[data-automation-id='product-price']")
        original_tag = item.select_one("span.line-through")

        if title_tag and price_tag and original_tag:
            if is_50_percent_off(price_tag.text, original_tag.text):
                link = item.select_one("a")["href"]
                deals.append({
                    "title": title_tag.text.strip(),
                    "url": "https://www.walmart.com" + link
                })
    return deals

def fetch_target_deals():
    url = "https://www.target.com/s?searchTerm=lego"
    response = requests.get(url, headers=HEADERS)
    soup = BeautifulSoup(response.text, "html.parser")
    items = soup.select("li[data-test='list-entry-product-card']")
    deals = []

    for item in items:
        title_tag = item.select_one("a[data-test='product-title']")
        price_box = item.select_one("div[data-test='product-price']")
        prices = re.findall(r"\$\d+\.\d+", price_box.text if price_box else "")
        if title_tag and len(prices) >= 2:
            if is_50_percent_off(prices[0], prices[1]):
                deals.append({
                    "title": title_tag.text.strip(),
                    "url": "https://www.target.com" + title_tag['href']
                })
    return deals

def show_deals(deals, retailer_name):
    if deals:
        st.subheader(f"{retailer_name} Deals (50% Off or More)")
        for deal in deals:
            st.markdown(f"- [{deal['title']}]({deal['url']})")
    else:
        st.info(f"No 50% off deals found at {retailer_name}.")

# --- Streamlit App UI ---
st.set_page_config(page_title="LEGO Deal Finder", page_icon="🧱")
st.title("🧱 LEGO 50% Off Deal Finder")

with st.spinner("Searching for deals..."):
    walmart_deals = fetch_walmart_deals()
    target_deals = fetch_target_deals()

show_deals(walmart_deals, "Walmart")
show_deals(target_deals, "Target")

st.subheader("Other Retailers")
st.markdown("- [Amazon LEGO 50% Off Search](https://www.amazon.com/s?k=lego+50+percent+off)")
st.markdown("- [LEGO.com Sales & Deals](https://www.lego.com/en-us/categories/sales-and-deals)")
