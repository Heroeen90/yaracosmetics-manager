import streamlit as st
from supabase import create_client, Client
import pandas as pd
from datetime import datetime
import plotly.express as px

# ==========================================
# 1. CONFIG & INITIALIZATION
# ==========================================
st.set_page_config(
    page_title="YARA Cosmetics Manager",
    page_icon="💄",
    layout="wide",
    initial_sidebar_state="collapsed"
)

# الاتصال بقاعدة البيانات
SUPABASE_URL = st.secrets["SUPABASE_URL"]
SUPABASE_KEY = st.secrets["SUPABASE_KEY"]
supabase: Client = create_client(SUPABASE_URL, SUPABASE_KEY)

TABLE_NAME = "yara-cosmetics"

# ==========================================
# 2. FANCY MOBILE-FIRST CSS
# ==========================================
st.markdown("""
<style>
    @import url('https://fonts.googleapis.com/css2?family=Tajawal:wght@400;500;700&display=swap');
    
    * {
        font-family: 'Tajawal', sans-serif;
        direction: rtl;
    }
    .main-title {
        font-size: 32px;
        font-weight: 700;
        color: #E91E63;
        text-align: center;
        margin-bottom: 5px;
    }
    .sub-title {
        text-align: center;
        color: #9C27B0;
        font-size: 16px;
        margin-bottom: 25px;
    }
    .card {
        background-color: white;
        padding: 18px;
        border-radius: 12px;
        box-shadow: 0px 4px 12px rgba(0,0,0,0.05);
        text-align: center;
        margin-bottom: 15px;
        border: 1px solid #F3E5F5;
    }
    .metric {
        font-size: 24px;
        font-weight: 700;
        color: #E91E63;
        margin-top: 5px;
    }
    .stButton>button {
        width: 100%;
        background-color: #E91E63 !important;
        color: white !important;
        border-radius: 10px !important;
        padding: 10px 20px !important;
        font-size: 18px !important;
        font-weight: bold !important;
        border: none !important;
        box-shadow: 0 4px 6px rgba(233, 30, 99, 0.2);
    }
    .stButton>button:hover {
        background-color: #C2185B !important;
    }
</style>
""", unsafe_allow_html=True)

st.markdown("<div class='main-title'>💄 كوزمتك يارا</div>", unsafe_allow_html=True)
st.markdown("<div class='sub-title'>النظام الذكي لإدارة المتجر والمخزون</div>", unsafe_allow_html=True)

# ==========================================
# 3. DATA FUNCTIONS (FIXED)
# ==========================================
def load_data():
    try:
        response = supabase.table(TABLE_NAME).select("*").execute()
        return response.data
    except Exception as e:
        st.error(f"خطأ في جلب البيانات: {e}")
        return []

# نظام كاش بسيط لمنع الانهيار أثناء الحفظ والتحديث
if 'cached_data' not in st.session_state:
    st.session_state['cached_data'] = load_data()

def insert_product(data):
    try:
        supabase.table(TABLE_NAME).insert(data).execute()
        # تحديث الكاش المحلي فوراً لتظهر البيانات الجديدة بدون rerun مفاجئ
        st.session_state['cached_data'] = load_data()
        st.success("🎉 تم حفظ المادة بنجاح في قاعدة البيانات!")
    except Exception as e:
        st.error(f"فشلت عملية الحفظ: {e}")

data_list = st.session_state['cached_data']
df_all = pd.DataFrame(data_list) if data_list else pd.DataFrame()

# ==========================================
# 4. NAVIGATION TABS
# ==========================================
tab_dash, tab_add, tab_stock = st.tabs(["📊 لوحة التحكم", "➕ إضافة حركة/منتج", "📦 جرد المخزون"])

# ==========================================
# TAB 1: DASHBOARD
# ==========================================
with tab_dash:
    if not df_all.empty:
        df_all['purchase_price'] = pd.to_numeric(df_all.get('purchase_price', 0), errors='coerce').fillna(0)
        df_all['sale_price'] = pd.to_numeric(df_all.get('sale_price', 0), errors='coerce').fillna(0)
        df_all['quantity'] = pd.to_numeric(df_all.get('quantity', 0), errors='coerce').fillna(0)
        df_all['min_quantity'] = pd.to_numeric(df_all.get('min_quantity', 3), errors='coerce').fillna(3)
        
        total_types = len(df_all)
        stock_value_purchase = (df_all['purchase_price'] * df_all['quantity']).sum()
        stock_value_sale = (df_all['sale_price'] * df_all['quantity']).sum()
        expected_profit = stock_value_sale - stock_value_purchase
        
        low_stock_df = df_all[df_all['quantity'] <= df_all['min_quantity']]
        
        col1, col2 = st.columns(2)
        with col1:
            st.markdown(f"<div class='card'>📦 عدد المواد الأصلي<div class='metric'>{total_types} مادة</div></div>", unsafe_allow_html=True)
            st.markdown(f"<div class='card'>💰 قيمة رأس المال (شراء)<div class='metric'>{stock_value_purchase:,.0f} د.ع</div></div>", unsafe_allow_html=True)
        with col2:
            st.markdown(f"<div class='card'>📈 إجمالي القيمة عند البيع<div class='metric'>{stock_value_sale:,.0f} د.ع</div></div>", unsafe_allow_html=True)
            st.markdown(f"<div class='card'>✨ الأرباح المتوقعة المتراكمة<div class='metric' style='color:#4CAF50;'>{expected_profit:,.0f} د.ع</div></div>", unsafe_allow_html=True)
        
        if not low_stock_df.empty:
            st.warning(f"⚠️ تنبيه: لديك ({len(low_stock_df)}) منتجات وصلت أو أقل من حد التنبيه!")
            with st.expander("🔍 عرض المنتجات الموشكة على النفاد"):
                st.dataframe(low_stock_df[['name', 'quantity', 'min_quantity']], use_container_width=True)
                
        st.write("### 📊 إحصائيات التصنيفات المتوفرة")
        if 'category' in df_all.columns:
            cat_counts = df_all['category'].value_counts().reset_index()
            cat_counts.columns = ['التصنيف', 'عدد المنتجات']
            fig = px.bar(cat_counts, x='التصنيف', y='عدد المنتجات', color='التصنيف', 
                         color_discrete_sequence=px.colors.qualitative.Pastel)
            fig.update_layout(showlegend=False, height=300, font=dict(family="Tajawal"))
            st.plotly_chart(fig, use_container_width=True)
    else:
        st.info("👋 مرحباً بك في نظام يارا! قاعدة البيانات فارغة حالياً. ابدأ بإضافة أول منتج من التبويب بالأعلى.")

# ==========================================
# TAB 2: ADD PRODUCT
# ==========================================
with tab_add:
    st.write("### 📥 نموذج إضافة مادة جديدة للمخزن")
    
    with st.form("add_product_form", clear_on_submit=True):
        prod_name = st.text_input("🏷️ اسم المنتج (مثال: عطر شانيل، غسول سيرافي...)")
        
        category_options = ["عطور", "كريمات", "مستحضرات تجميل", "غسول", "معطرات", "منتجات شعر", "أدوات شخصية"]
        prod_cat = st.selectbox("🗂️ التصنيف الاساسي", category_options)
        custom_cat = st.text_input("✍️ أو اكتب تصنيف جديد هنا")
        
        prod_supplier = st.text_input("🚚 اسم المورد / شركة التجهيز")
        
        col_p1, col_p2 = st.columns(2)
        with col_p1:
            prod_pur_price = st.number_input("💵 سعر الشراء للمفرد (د.ع)", min_value=0, step=250, value=0)
        with col_p2:
            prod_sale_price = st.number_input("💰 سعر البيع للمفرد (د.ع)", min_value=0, step=250, value=0)
            
        col_q1, col_q2 = st.columns(2)
        with col_q1:
            prod_quantity = st.number_input("📦 الكمية المتوفرة حالياً", min_value=0, step=1, value=1)
        with col_q2:
            prod_min_qty = st.number_input("⚠️ حد التنبيه للنقصان", min_value=1, step=1, value=3)
            
        prod_image = st.text_input("🔗 رابط صورة المنتج (اختياري)")
        
        # استخدام الدالة القياسية الصحيحة والآمنة للاستمارات
        submit_btn = st.form_submit_button("💾 حفظ المادة في النظام")
        
        if submit_btn:
            if not prod_name:
                st.error("❌ يرجى كتابة اسم المنتج أولاً!")
            else:
                final_cat = custom_cat.strip() if custom_cat.strip() else prod_cat
                new_row = {
                    "name": prod_name,
                    "category": final_cat,
                    "supplier": prod_supplier if prod_supplier else "غير محدد",
                    "purchase_price": float(prod_pur_price),
                    "sale_price": float(prod_sale_price),
                    "quantity": int(prod_quantity),
                    "min_quantity": int(prod_min_qty),
                    "image": prod_image if prod_image else None
                }
                insert_product(new_row)

# ==========================================
# TAB 3: STOCK MANAGEMENT
# ==========================================
with tab_stock:
    st.write("### 📦 جرد كلي للمخزن الحالي")
    
    # زر يدوي لتحديث البيانات في حال أردت المزامنة الفورية مع السيرفر
    if st.button("🔄 تحديث ومزامنة البيانات الآن"):
        st.session_state['cached_data'] = load_data()
        st.success("تم تحديث المخزن من السيرفر!")
    
    if not df_all.empty:
        search_query = st.text_input("🔍 ابحث عن أي منتج بالاسم أو التصنيف...")
        
        df_filtered = df_all.copy()
        if search_query:
            df_filtered = df_filtered[
                df_filtered['name'].str.contains(search_query, case=False, na=False) |
                df_filtered['category'].str.contains(search_query, case=False, na=False)
            ]
            
        display_cols = ['name', 'category', 'quantity', 'purchase_price', 'sale_price', 'supplier']
        st.dataframe(df_filtered[display_cols].rename(columns={
            'name': 'اسم المنتج',
            'category': 'التصنيف',
            'quantity': 'الكمية',
            'purchase_price': 'سعر الشراء',
            'sale_price': 'سعر البيع',
            'supplier': 'المورد'
        }), use_container_width=True)
        
        st.write("---")
        csv_data = df_filtered.to_csv(index=False).encode('utf-8-sig')
        st.download_button(
            label="📥 تحميل الجرد الحالي كملف Excel (CSV)",
            data=csv_data,
            file_name=f"YARA_Stock_{datetime.now().strftime('%Y-%m-%d')}.csv",
            mime="text/csv"
        )
    else:
        st.info("المخزن فارغ حالياً.")

