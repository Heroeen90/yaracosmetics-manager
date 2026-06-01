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
    # تم تغيير اسم الجدول هنا ليتطابق مع الجدول الذي أنشأته
    try:
        return supabase.table("yara-cosmetics").select("*").execute().data
    except Exception as e:
        return []

products = get_products()

# =========================
# CALCULATIONS
# =========================
total_products = len(products) if products else 0

# حساب المبيعات والمشتريات بناءً على البيانات المتوفرة في جدول المنتجات الحالي كحسابات أولية
total_sales = sum([float(p.get("sale_price") or 0) * int(p.get("quantity") or 0) for p in products]) if products else 0
total_purchases = sum([float(p.get("purchase_price") or 0) * int(p.get("quantity") or 0) for p in products]) if products else 0
total_expenses = 0
total_debts = 0

profit = total_sales - total_purchases

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
        💰 قيمة المبيعات المتوقعة
        <div class='metric'>{total_sales:,.0f} IQD</div>
    </div>
    """, unsafe_allow_html=True)

with col3:
    st.markdown(f"""
    <div class='card'>
        🛒 تكلفة رأس المال
        <div class='metric'>{total_purchases:,.0f} IQD</div>
    </div>
    """, unsafe_allow_html=True)

with col4:
    st.markdown(f"""
    <div class='card'>
        📈 الربح المتوقع
        <div class='metric'>{profit:,.0f} IQD</div>
    </div>
    """, unsafe_allow_html=True)

st.divider()

# =========================
# TABLES SECTION
# =========================
st.subheader("📦 جدول المنتجات المتوفرة")

if products:
    df = pd.DataFrame(products)
    # ترتيب الأعمدة بشكل منسق للعرض
    cols_order = ['id', 'name', 'category', 'supplier', 'purchase_price', 'sale_price', 'quantity', 'min_quantity', 'created_at']
    existing_cols = [c for c in cols_order if c in df.columns]
    df = df[existing_cols]
    st.dataframe(df, use_container_width=True)
else:
    st.info("لا توجد منتجات مضافة في جدول yara-cosmetics حتى الآن. يرجى إضافة منتج من لوحة تحكم Supabase لتظهر هنا.")
