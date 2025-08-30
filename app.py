import streamlit as st
import requests
from bs4 import BeautifulSoup

st.set_page_config(page_title="Multi-Store Product Search", layout="wide")

# --- Amazon Scraper (until you provide API keys) ---
def search_amazon(query):
    url = f"https://www.amazon.in/s?k={query.replace(' ', '+')}"
    headers = {
        "User-Agent": "Mozilla/5.0",
        "Accept-Language": "en-US,en;q=0.9"
    }
    resp = requests.get(url, headers=headers, timeout=10)
    soup = BeautifulSoup(resp.text, "html.parser")
    results = []
    for item in soup.select("div.s-result-item[data-asin]"):
        title = item.select_one("h2 span")
        link = item.select_one("h2 a")
        price = item.select_one(".a-price span.a-offscreen")
        image = item.select_one("img.s-image")
        if title and link and price and image:
            results.append({
                "title": title.text.strip(),
                "url": "https://www.amazon.in" + link.get("href"),
                "price": price.text.strip(),
                "image": image.get("src"),
                "source": "Amazon"
            })
        if len(results) >= 10:
            break
    return results

# --- Flipkart Affiliate API Integration ---
def search_flipkart(query):
    AFF_ID = "rishilbabu"
    TOKEN = "b19165477d9d4076a058547b247b380c"
    headers = {
        "Fk-Affiliate-Id": AFF_ID,
        "Fk-Affiliate-Token": TOKEN
    }
    url = f"https://affiliate-api.flipkart.net/affiliate/search/json?query={query.replace(' ', '%20')}"
    try:
        resp = requests.get(url, headers=headers, timeout=10)
        data = resp.json()
        results = []
        for product in data.get('products', []):
            info = product.get('productBaseInfoV1', {})
            title = info.get('title')
            price = info.get('flipkartSellingPrice', {}).get('amount')
            currency = info.get('flipkartSellingPrice', {}).get('currency', 'INR')
            image = info.get('imageUrls', {}).get('200x200')
            url = info.get('affiliateUrl')
            if title and price and image and url:
                results.append({
                    "title": title,
                    "url": url,
                    "price": f"{currency} {price}",
                    "image": image,
                    "source": "Flipkart"
                })
            if len(results) >= 10:
                break
        return results
    except Exception as e:
        return []

st.title("🛒 Multi-Store Product Search (Amazon & Flipkart)")

query = st.text_input("Enter product name", "")

if query:
    with st.spinner("Searching..."):
        amazon = search_amazon(query)
        flipkart = search_flipkart(query)
        results = amazon + flipkart

    if results:
        for item in results:
            col1, col2 = st.columns([1, 5])
            with col1:
                st.image(item["image"], width=100)
            with col2:
                st.markdown(f"**[{item['title']}]({item['url']})**")
                st.write(f"{item['price']}  \nSource: {item['source']}")
                st.markdown("---")
    else:
        st.warning("No products found. Try another search term.")
else:
    st.info("Type a product name and hit Enter to search.")

st.caption("Prototype app | Amazon uses scraping, Flipkart uses Affiliate API | Built with Streamlit")
