
import streamlit as st
import pandas as pd
import time
import random
from io import StringIO

st.set_page_config(page_title="AI Shopping Assistant - MVP", layout="wide")

st.title("AI Shopping Assistant — MVP (Streamlit)")
st.write("Demo: enter a product query and see price comparisons across platforms. This MVP returns mock results when APIs/network are not configured.")

with st.expander("How this MVP works (short)"):
    st.markdown("""
- Enter a product name or description (e.g. \"formal shirt under 1500\").
- Optionally provide affiliate/API keys (Amazon Product Advertising, Flipkart Affiliate).  
- Click **Search**.  
- The app will try to fetch live data if keys/network are available. Otherwise it returns **mocked results** for validation.
- You can download search results as CSV.
""")

st.markdown("---")

col1, col2 = st.columns([3,1])

with col1:
    query = st.text_input("Product query", placeholder="e.g. Noise headphones under 2000")
    num_results = st.slider("Number of results to show per platform", 1, 5, 3)
    run_search = st.button("Search")

with col2:
    st.subheader("Optional (advanced)")
    st.text_input("Amazon Access Key (optional)", key="amz_key", placeholder="AKIA...")
    st.text_input("Amazon Secret Key (optional)", key="amz_secret", type="password")
    st.text_input("Flipkart Affiliate ID (optional)", key="flip_affid", placeholder="your_aff_id")
    use_mock = st.checkbox("Force mock results (recommended for quick demo)", value=True)
    st.markdown(" ")

def generate_mock_results(query, n=3):
    platforms = ["Amazon", "Flipkart", "Myntra"]
    sample_products = [
        "Formal Shirt Slim Fit",
        "Running Shoes Lightweight",
        "Bluetooth Headphones OverEar",
        "Smartphone Protective Case",
        "Stainless Steel Water Bottle",
        "Office Backpack 20L",
        "LED Desk Lamp",
        "Executive Formal Shoes",
        "Yoga Mat Non-slip",
        "Noise Cancelling Earbuds"
    ]
    rows = []
    for platform in platforms:
        for i in range(n):
            product = random.choice(sample_products)
            title = f\"{product} — {query.split(' under ')[0].strip().title()}\" if 'under' in query else f\"{product} — {query.title()}\"
            price = random.randint(499, 4999)
            price = int(price * (1 + (0.02 * (platforms.index(platform)))))
            rows.append({
                "platform": platform,
                "title": title,
                "price": price,
                "currency": "INR",
                "link": f\"https://{platform.lower()}.example.com/search?q={query.replace(' ', '+')}&p={i+1}\",
                "delivery_estimate": f\"{random.randint(1,5)} days\"
            })
    rows = sorted(rows, key=lambda r: r["price"])
    return rows

def results_to_df(rows):
    df = pd.DataFrame(rows)
    df = df[["platform", "title", "price", "currency", "delivery_estimate", "link"]]
    return df

if run_search:
    if not query:
        st.warning("Please enter a product query.")
    else:
        st.info(f"Searching for: {query}")
        progress = st.progress(0)
        all_rows = []
        try:
            if use_mock:
                for p in range(0,100,20):
                    progress.progress(p+10)
                    time.sleep(0.06)
                all_rows = generate_mock_results(query, n=num_results)
                st.success("Mock results generated (no external APIs called).")
            else:
                # Fallback to mock in this demo
                all_rows = generate_mock_results(query, n=num_results)
                progress.progress(100)
        except Exception as ex:
            st.error(f"Search failed: {ex}")
            all_rows = generate_mock_results(query, n=num_results)

        df = results_to_df(all_rows)
        st.markdown("### Price Comparison (sorted by price)")
        st.dataframe(df, height=300)

        st.markdown("### Split by platform")
        platforms = df["platform"].unique().tolist()
        for p in platforms:
            st.markdown(f"**{p}**")
            sub = df[df["platform"]==p].reset_index(drop=True)
            st.table(sub[["title","price","currency","delivery_estimate","link"]])

        csv_buffer = StringIO()
        df.to_csv(csv_buffer, index=False)
        b = csv_buffer.getvalue().encode()
        st.download_button("Download results as CSV", data=b, file_name="search_results.csv", mime="text/csv")

        st.markdown("---")
        st.markdown("### Next steps (for Phase 2)")
        st.markdown(\"\"\"
- Hook up Amazon Product Advertising API and Flipkart Affiliate API for live results.
- Add caching & rate-limiting for quicker responses.
- Add user accounts and wishlist.
- Connect WhatsApp notifications for deal alerts.
\"\"\")

st.markdown("---")
st.header("Run this app locally")
st.markdown(r\"\"\"
1. Install dependencies:
```
pip install streamlit pandas
```
2. Save this file as `app.py` and run:
```
streamlit run app.py
```
3. Open the displayed local URL in your browser.
\"\"\")
