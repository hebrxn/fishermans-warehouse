import streamlit as st
import pandas as pd
import sqlite3
import json
from pathlib import Path
from datetime import datetime
import uuid

BASE = Path(__file__).parent
DATA = BASE / "data"
ASSETS = BASE / "assets"
CATALOGUE = DATA / "products.csv"
DB = DATA / "store.db"

st.set_page_config(page_title="Fisherman's Warehouse | Durban", page_icon="🎣", layout="wide")

# ---------- Local demo data / persistence ----------
REQUIRED = ["sku","name","category","description","price","stock","image","weight_kg","length_cm","width_cm","height_cm"]
DEFAULT = [
    ["FW001","Saltwater Spinning Rod","Rods","A versatile rod for shore and rock fishing.",1299,8,"https://images.unsplash.com/photo-1517504734587-289d6b7de2d5?auto=format&fit=crop&w=1000&q=85",0.8,120,8,8],
    ["FW002","Fishing Lure Selection","Lures","A selection of lures for your next session.",189,24,"https://images.unsplash.com/photo-1530053969600-caed2596d242?auto=format&fit=crop&w=1000&q=85",0.2,20,12,5],
    ["FW003","Tackle Accessories","Terminal Tackle","Hooks, swivels, sinkers and rigging essentials.",99,35,"https://images.unsplash.com/photo-1502680390469-be75c86b636f?auto=format&fit=crop&w=1000&q=85",0.1,15,10,5],
    ["FW004","Coastal Fishing Reel","Reels","A dependable reel option for coastal fishing.",899,6,"https://images.unsplash.com/photo-1544551763-46a013bb70d5?auto=format&fit=crop&w=1000&q=85",0.7,25,20,15],
    ["FW005","Fishing Line","Line","Fishing line for your next rig or replacement spool.",149,18,"https://images.unsplash.com/photo-1518837695005-2083093ee35b?auto=format&fit=crop&w=1000&q=85",0.3,15,10,8],
    ["FW006","Landing Net","Accessories","Useful landing net for shore and boat fishing.",349,5,"https://images.unsplash.com/photo-1500375592092-40eb2168fd21?auto=format&fit=crop&w=1000&q=85",1.0,70,35,10],
]
if not CATALOGUE.exists():
    pd.DataFrame(DEFAULT, columns=REQUIRED).to_csv(CATALOGUE,index=False)

def load_products():
    df = pd.read_csv(CATALOGUE).fillna("")
    for c in ["price","stock","weight_kg","length_cm","width_cm","height_cm"]:
        if c not in df: df[c] = 0
        df[c] = pd.to_numeric(df[c], errors="coerce").fillna(0)
    for c in REQUIRED:
        if c not in df: df[c] = ""
    return df

def db():
    con = sqlite3.connect(DB)
    con.execute("""CREATE TABLE IF NOT EXISTS enquiries (
        id TEXT PRIMARY KEY, created TEXT, customer TEXT, email TEXT, phone TEXT,
        address TEXT, city TEXT, postal TEXT, items TEXT, subtotal REAL, status TEXT)""")
    con.commit()
    return con

products = load_products()
st.session_state.setdefault("cart", {})

# ---------- Styling ----------
st.markdown("""
<style>
@import url('https://fonts.googleapis.com/css2?family=Barlow+Condensed:wght@600;700;800&family=Inter:wght@400;500;600;700;800&display=swap');
:root {
  --fw-navy:#03264c;
  --fw-navy-deep:#021a36;
  --fw-yellow:#e7d600;
  --fw-cyan:#2c9bbf;
  --fw-white:#ffffff;
  --fw-ink:#10243a;
  --fw-muted:#536579;
  --fw-bg:#f3f6fa;
}
html, body, [class*="css"] {font-family:Inter,sans-serif; color:var(--fw-ink);}
.stApp {background:var(--fw-bg); color:var(--fw-ink);}
.block-container {max-width:1380px; padding-top:1rem; padding-bottom:3rem;}
/* Brand strip and masthead */
.topline {background:var(--fw-navy); color:#fff; text-align:center; padding:10px 12px; border-radius:6px; font-size:12px; letter-spacing:.13em; font-weight:800; border-bottom:4px solid var(--fw-yellow);}
.brandname {font-family:'Barlow Condensed',sans-serif; font-size:clamp(28px,4vw,42px); font-weight:800; line-height:1; color:var(--fw-navy);}
.tagline {font-size:11px; letter-spacing:.2em; color:var(--fw-navy); font-weight:800; margin-top:7px;}
/* Hero */
.hero {padding:68px 7%; border-radius:16px; color:#fff; background:linear-gradient(100deg,rgba(2,26,54,.97),rgba(3,38,76,.78)),url('https://images.unsplash.com/photo-1502680390469-be75c86b636f?auto=format&fit=crop&w=1800&q=85') center/cover; border:2px solid var(--fw-yellow);}
.hero .eyebrow {color:var(--fw-yellow); font-weight:800; font-size:12px; letter-spacing:.2em;}
.hero h1 {font-family:'Barlow Condensed',sans-serif; font-size:clamp(48px,7vw,82px); font-weight:800; line-height:.9; text-transform:uppercase; margin:12px 0; color:#fff;}
.hero p {max-width:560px; color:#fff; font-size:16px; line-height:1.65;}
.section-kicker {color:var(--fw-navy); font-weight:800; font-size:11px; letter-spacing:.2em;}
h1,h2,h3,h4,h5,h6,[data-testid="stHeader"] {color:var(--fw-navy)!important;}
h2 {font-family:'Barlow Condensed',sans-serif; font-size:36px!important; text-transform:uppercase;}
/* Product tiles and price */
.product-card {background:#fff; border:1px solid #cbd5e1; border-radius:13px; padding:12px; height:100%;}
.price {font-size:21px; font-weight:800; color:var(--fw-navy);}
.smallmuted, [data-testid="stCaptionContainer"], .stCaption {color:var(--fw-muted)!important;}
/* Dark feature panels */
.info-panel {background:var(--fw-navy); color:#fff; border:2px solid var(--fw-yellow); border-radius:13px; padding:22px;}
.info-panel h3,.info-panel p {color:#fff!important;}
/* Navigation */
div[role="radiogroup"] {background:#fff; border:1px solid #cbd5e1; border-radius:10px; padding:8px;}
div[role="radiogroup"] label, div[role="radiogroup"] p {color:var(--fw-navy)!important; font-weight:700!important;}
/* Inputs: explicit light surfaces and dark text for reliable contrast */
.stTextInput label,.stTextArea label,.stNumberInput label,.stSelectbox label,.stRadio label,.stFileUploader label,
[data-testid="stWidgetLabel"] p {color:var(--fw-navy)!important; font-weight:700!important;}
.stTextInput input,.stTextArea textarea,.stNumberInput input,
.stSelectbox [data-baseweb="select"] > div,
[data-baseweb="input"] input {background:#fff!important; color:#10243a!important; border-color:#9aabba!important; -webkit-text-fill-color:#10243a!important;}
input::placeholder,textarea::placeholder {color:#617286!important; opacity:1!important; -webkit-text-fill-color:#617286!important;}
[data-baseweb="select"] * {color:#10243a!important;}
[data-baseweb="popover"],[data-baseweb="menu"],[role="listbox"] {background:#fff!important; color:#10243a!important;}
[role="option"] {color:#10243a!important;}
/* Buttons */
div.stButton>button[kind="primary"],button[kind="primary"],[data-testid="stFormSubmitButton"] button {
  background:var(--fw-yellow)!important; color:var(--fw-navy)!important; border:2px solid var(--fw-navy)!important; font-weight:800!important;
}
div.stButton>button,button {border-radius:8px;}
div.stButton>button:not([kind="primary"]) {background:#fff!important; color:var(--fw-navy)!important; border:1px solid var(--fw-navy)!important; font-weight:700!important;}
/* Metrics, tables, alerts and form surfaces */
[data-testid="stMetric"] {background:#fff; color:var(--fw-navy); border:1px solid #cbd5e1; border-radius:10px; padding:12px;}
[data-testid="stMetricLabel"],[data-testid="stMetricValue"] {color:var(--fw-navy)!important;}
[data-testid="stDataFrame"],[data-testid="stTable"] {background:#fff;}
[data-testid="stForm"] {background:#fff; border:1px solid #cbd5e1; border-radius:12px; padding:16px;}
[data-testid="stAlert"] {color:var(--fw-ink)!important;}
hr {border-color:#cbd5e1!important;}
footer {visibility:hidden;}
</style>
""", unsafe_allow_html=True)

# ---------- Header ----------
st.markdown('<div class="topline">DURBAN, SOUTH AFRICA &nbsp; • &nbsp; TACKLE UP FOR YOUR NEXT ADVENTURE</div>', unsafe_allow_html=True)
h1,h2c = st.columns([1,5], vertical_alignment="center")
with h1:
    logo = ASSETS / "logo.png"
    if logo.exists(): st.image(str(logo), width=112)
    else: st.markdown("## 🎣")
with h2c:
    st.markdown('<div class="brandname">FISHERMAN’S WAREHOUSE</div><div class="tagline">TACKLE • BAIT • OUTDOOR</div>', unsafe_allow_html=True)
st.divider()

pages = ["Home & Shop","Delivery & Checkout","Contact","Store Admin"]
page = st.radio("Navigation", pages, horizontal=True, label_visibility="collapsed")

if page == "Home & Shop":
    st.markdown("""<div class="hero"><div class="eyebrow">YOUR LOCAL FISHING STORE • DURBAN</div>
    <h1>Make every<br>cast count.</h1>
    <p>Explore fishing tackle, rods, reels, lures and essentials for your next session. Add your favourites to the basket and send us an order enquiry.</p></div>""", unsafe_allow_html=True)
    st.write("")
    st.markdown('<div class="section-kicker">FIND YOUR NEXT FAVOURITE</div>',unsafe_allow_html=True)
    st.header("Shop fishing gear")
    a,b=st.columns([2,1])
    with a: search=st.text_input("Search the catalogue",placeholder="Try rods, reels, hooks, line...")
    with b: category=st.selectbox("Shop by category",["All categories"]+sorted(products.category.astype(str).unique().tolist()))
    shown=products.copy()
    if search:
        shown=shown[shown.apply(lambda r: search.lower() in " ".join(map(str,r.values)).lower(),axis=1)]
    if category!="All categories": shown=shown[shown.category==category]
    if shown.empty: st.info("No products matched your search.")
    cols=st.columns(3)
    for i,(_,p) in enumerate(shown.iterrows()):
        with cols[i%3]:
            with st.container(border=True):
                if str(p.image).startswith("http"): st.image(str(p.image),use_container_width=True)
                st.caption(str(p.category).upper())
                st.subheader(str(p["name"]))
                st.write(str(p.description))
                st.markdown(f'<div class="price">R {p.price:,.2f}</div>',unsafe_allow_html=True)
                st.caption(f"{int(p.stock)} shown in catalogue")
                if p.stock > 0:
                    qty=st.number_input("Quantity",1,max(1,int(p.stock)),1,key="qty_"+str(p.sku))
                    if st.button("Add to basket",key="add_"+str(p.sku),type="primary",use_container_width=True):
                        current=st.session_state.cart.get(str(p.sku),0)
                        st.session_state.cart[str(p.sku)]=min(int(p.stock),current+qty)
                        st.toast("Added to your basket")
                else: st.warning("Out of stock")
    st.divider()
    st.markdown("### Why shop with Fisherman's Warehouse?")
    x,y,z=st.columns(3)
    x.markdown("🎣 **Fishing focused**  \nTackle and essentials for your next outing.")
    y.markdown("📍 **Durban store**  \nLocal store support and collection enquiries.")
    z.markdown("🚚 **Courier delivery**  \nRequest delivery pricing at checkout.")

elif page == "Delivery & Checkout":
    st.header("Your basket")
    if not st.session_state.cart:
        st.info("Your basket is empty. Visit Home & Shop to add products.")
    else:
        items=[]; subtotal=0
        for sku,qty in list(st.session_state.cart.items()):
            hit=products[products.sku.astype(str)==sku]
            if hit.empty: continue
            p=hit.iloc[0]; line=float(p.price)*int(qty); subtotal+=line
            items.append({"SKU":sku,"Product":p["name"],"Qty":qty,"Price":f"R {p.price:,.2f}","Total":f"R {line:,.2f}"})
        st.dataframe(pd.DataFrame(items),use_container_width=True,hide_index=True)
        st.metric("Basket subtotal",f"R {subtotal:,.2f}")
        st.caption("Courier charges are not included. A live Courier Guy quote requires merchant API credentials and confirmation of the account's API specification.")
        with st.form("checkout_form"):
            st.subheader("Delivery details")
            c1,c2=st.columns(2)
            with c1:
                customer=st.text_input("Full name *")
                email=st.text_input("Email")
                phone=st.text_input("Mobile number *")
                city=st.text_input("Town / city *")
            with c2:
                postal=st.text_input("Postal code *")
                address=st.text_area("Street address *")
                delivery_method=st.radio("How would you like your order?",["Courier delivery – quote required","Collect from Durban store"],horizontal=False)
            submitted=st.form_submit_button("Send order enquiry",type="primary",use_container_width=True)
        if submitted:
            if not all([customer,phone,city]) or (delivery_method.startswith("Courier") and not all([postal,address])):
                st.error("Please complete all required fields.")
            else:
                con=db()
                order_id="FW-"+uuid.uuid4().hex[:8].upper()
                con.execute("INSERT INTO enquiries VALUES (?,?,?,?,?,?,?,?,?,?,?)",
                    (order_id,datetime.now().isoformat(timespec="seconds"),customer,email,phone,address,city,postal,
                     json.dumps(items),subtotal,"New enquiry – "+delivery_method))
                con.commit(); con.close()
                st.success(f"Enquiry received in this app. Reference: {order_id}")
                st.info("This is an enquiry workflow, not a payment or confirmed order. The store must confirm stock, delivery cost and payment with you.")
                st.session_state.cart={}
    st.divider()
    st.subheader("Courier Guy delivery")
    st.write("The checkout collects the destination and parcel details needed for a courier quote. Live Courier Guy pricing, booking and tracking will be switched on once the merchant API credentials and correct endpoint/schema are supplied.")

elif page == "Contact":
    st.header("Visit Fisherman's Warehouse")
    st.markdown('<div class="info-panel"><h3>Fisherman’s Warehouse • Durban</h3><p>42 Sylvester Ntuli (Brickhill) Road<br>Durban, 4001<br>KwaZulu-Natal, South Africa</p><p>Store telephone, WhatsApp and email details can be added once confirmed.</p></div>',unsafe_allow_html=True)
    st.write("")
    st.subheader("Send an enquiry")
    with st.form("contact_form"):
        name=st.text_input("Your name"); contact=st.text_input("Email or phone"); message=st.text_area("How can we help?")
        send=st.form_submit_button("Submit enquiry",type="primary")
        if send:
            if name and contact and message: st.success("Thank you. This demo has captured your enquiry in the current session.")
            else: st.error("Please complete all fields.")

else:
    st.header("Store administration")
    st.warning("Prototype admin area. Add authentication before publishing this page publicly.")
    st.subheader("Product catalogue")
    st.write("Digitot is not connected yet. Until Digitot supplies an approved API/export, manage this demo catalogue using CSV.")
    st.download_button("Download current product catalogue",products.to_csv(index=False).encode("utf-8"),"products.csv","text/csv")
    upload=st.file_uploader("Upload updated catalogue CSV",type=["csv"])
    if upload:
        try:
            incoming=pd.read_csv(upload)
            missing=set(REQUIRED)-set(incoming.columns)
            if missing: st.error("Missing columns: "+", ".join(sorted(missing)))
            else:
                incoming.to_csv(CATALOGUE,index=False)
                st.success("Catalogue file updated. Restart the app to reload products.")
        except Exception as e: st.error(f"Could not read CSV: {e}")
    st.divider()
    st.subheader("Customer order enquiries")
    if DB.exists():
        con=db()
        orders=pd.read_sql_query("SELECT id,created,customer,phone,city,subtotal,status FROM enquiries ORDER BY created DESC",con)
        con.close()
        if orders.empty: st.info("No enquiries received yet.")
        else: st.dataframe(orders,use_container_width=True,hide_index=True)
    else: st.info("No enquiries received yet.")
    st.divider()
    st.subheader("Integration status")
    st.markdown("""
    - **Digitot POS & Inventory:** Pending API/export access and technical documentation.
    - **The Courier Guy:** Pending merchant API credentials and confirmed rate endpoint/schema.
    - **Payments:** Not connected; no card details are collected.
    - **Stock safety:** Demo catalogue quantities only; do not treat as live store stock.
    """)

st.divider()
st.caption("Fisherman's Warehouse Durban • Online storefront prototype. Product names, prices, stock and imagery are demonstration content until replaced with the verified Digitot catalogue.")
