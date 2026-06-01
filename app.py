import streamlit as st
from supabase import create_client, Client
import pandas as pd
from datetime import datetime

# =========================
# CONFIG
# =========================
st.set_page_config(
    page_title="كوزمتك يارا",
    page_icon="💄",
    layout="wide"
)

# =========================
# SUPABASE CONNECTION
# =========================
SUPABASE_URL = st.secrets["SUPABASE_URL"]
SUPABASE_KEY = st.secrets["SUPABASE_KEY"]

supabase: Client = create_client(SUPABASE_URL, SUPABASE_KEY)

# =========================
# STYLE (FANCY UI)
# =========================
st.markdown("""
<style>
body {
    background-color: #FFF5FA;
}

.main-title {
    font-size: 42px;
    font-weight: bold;
    color: #E91E63;
    text-align: center;
}

.sub-title {
    text-align: center;
    color: #9C27B0;
    margin-bottom: 30px;
}

.card {
    background-color: white;
    padding: 20px;
    border-radius: 15px;
    box-shadow: 0px 4px 15px rgba(0,0,0,0.1);
    text-align: center;
}

.metric {
    font-size: 22px;
    font-weight: bold;
    color: #E91E63;
}
</style>
""", unsafe_allow_html=True)

# =========================
# TITLE
# =========================
st.markdown("<div class='main-title'>💄 كوزمتك يارا</div>", unsafe_allow_html=True)
st.markdown("<div class='sub-title'>لوحة التحكم الذكية لإدارة المتجر</div>", unsafe_allow_html=True)

# =========================
# LOAD DATA
# =========================
def get_products():
    return supabase.table("products").select("*").execute().data

def get_sales():
    return supabase.table("sales").select("*").execute().data

def get_purchases():
    return supabase.table("purchases").select("*").execute().data

def get_expenses():
    return supabase.table("expenses").select("*").execute().data

def get_debts():
    return supabase.table("debts").select("*").execute().data


products = get_products()
sales = get_sales()
purchases = get_purchases()
expenses = get_expenses()
debts = get_debts()

# =========================
# CALCULATIONS
# =========================
total_products = len(products)

total_sales = sum([s["total"] for s in sales]) if sales else 0
total_purchases = sum([p["total"] for p in purchases]) if purchases else 0
total_expenses = sum([e["amount"] for e in expenses]) if expenses else 0
total_debts = sum([d["amount"] - d["paid_amount"] for d in debts]) if debts else 0

profit = total_sales - total_purchases - total_expenses

# =========================
# DASHBOARD CARDS
# =========================
col1, col2, col3, col4 = st.columns(4)

with col1:
    st.markdown(f"""
    <div class='card'>
        📦 المنتجات
        <div class='metric'>{total_products}</div>
    </div>
    """, unsafe_allow_html=True)

with col2:
    st.markdown(f"""
    <div class='card'>
        💰 المبيعات
        <div class='metric'>{total_sales:,.0f} IQD</div>
    </div>
    """, unsafe_allow_html=True)

with col3:
    st.markdown(f"""
    <div class='card'>
        🛒 المشتريات
        <div class='metric'>{total_purchases:,.0f} IQD</div>
    </div>
    """, unsafe_allow_html=True)

with col4:
    st.markdown(f"""
    <div class='card'>
        📈 الربح
        <div class='metric'>{profit:,.0f} IQD</div>
    </div>
    """, unsafe_allow_html=True)

st.divider()

# =========================
# SECOND ROW
# =========================
col5, col6 = st.columns(2)

with col5:
    st.markdown(f"""
    <div class='card'>
        💸 المصاريف
        <div class='metric'>{total_expenses:,.0f} IQD</div>
    </div>
    """, unsafe_allow_html=True)

with col6:
    st.markdown(f"""
    <div class='card'>
        💳 الديون المستحقة
        <div class='metric'>{total_debts:,.0f} IQD</div>
    </div>
    """, unsafe_allow_html=True)

st.divider()

# =========================
# TABLES SECTION
# =========================
st.subheader("📦 المنتجات")

if products:
    df = pd.DataFrame(products)
    st.dataframe(df, use_container_width=True)
else:
    st.info("لا توجد منتجات بعد")

st.subheader("💳 الديون")

if debts:
    df2 = pd.DataFrame(debts)
    st.dataframe(df2, use_container_width=True)
else:
    st.info("لا توجد ديون")
