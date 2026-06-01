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
# 2. ADVANCED MOBILE CSS
# ==========================================
st.markdown("""
<style>
    @import url('https://fonts.googleapis.com/css2?family=Tajawal:wght@400;500;700&display=swap');
    
    * {
        font-family: 'Tajawal', sans-serif;
        direction: rtl;
    }
    .main-title {
        font-size: 30px;
        font-weight: 700;
        color: #E91E63;
        text-align: center;
        margin-bottom: 5px;
    }
    .sub-title {
        text-align: center;
        color: #9C27B0;
        font-size: 14px;
        margin-bottom: 20px;
    }
    .card {
        background-color: white;
        padding: 15px;
        border-radius: 12px;
        box-shadow: 0px 4px 10px rgba(0,0,0,0.04);
        text-align: center;
        margin-bottom: 12px;
        border: 1px solid #F3E5F5;
    }
    .metric {
        font-size: 22px;
        font-weight: 700;
        color: #E91E63;
        margin-top: 4px;
    }
    .stButton>button {
        width: 100%;
        border-radius: 10px !important;
        padding: 12px 20px !important;
        font-size: 16px !important;
        font-weight: bold !important;
    }
    /* أزرار مخصصة ملونة للموبايل */
    div.stButton > button:first-child {
        background-color: #E91E63 !important;
        color: white !important;
        border: none !important;
    }
    .sales-card {
        background-color: #E8F5E9;
        border-right: 5px solid #4CAF50;
    }
    .expense-card {
        background-color: #FFEBEE;
        border-right: 5px solid #F44336;
    }
    .debt-card {
        background-color: #FFF3E0;
        border-right: 5px solid #FF9800;
    }
</style>
""", unsafe_allow_html=True)

st.markdown("<div class='main-title'>💄 إدارة كوزمتك يارا</div>", unsafe_allow_html=True)
st.markdown("<div class='sub-title'>الإصدار التجاري الاحترافي v2.0 - جاهز للمحل</div>", unsafe_allow_html=True)

# ==========================================
# 3. DATA LAYER (CRUD WITH LOGIC)
# ==========================================
def load_data():
    try:
        response = supabase.table(TABLE_NAME).select("*").execute()
        return response.data
    except Exception as e:
        return []

if 'cached_data' not in st.session_state:
    st.session_state['cached_data'] = load_data()

def refresh_db():
    st.session_state['cached_data'] = load_data()

# استخراج البيانات ومعالجتها كـ DataFrames منفصلة ديناميكياً
raw_data = st.session_state['cached_data']
df_all = pd.DataFrame(raw_data) if raw_data else pd.DataFrame()

# تنظيف البيانات وتحويل الأنواع للتأكد من عدم حدوث أخطاء حسابية
if not df_all.empty:
    df_all['purchase_price'] = pd.to_numeric(df_all.get('purchase_price', 0), errors='coerce').fillna(0)
    df_all['sale_price'] = pd.to_numeric(df_all.get('sale_price', 0), errors='coerce').fillna(0)
    df_all['quantity'] = pd.to_numeric(df_all.get('quantity', 0), errors='coerce').fillna(0)
    df_all['min_quantity'] = pd.to_numeric(df_all.get('min_quantity', 3), errors='coerce').fillna(3)
    if 'type' not in df_all.columns:
        df_all['type'] = 'product'
    df_all['type'] = df_all['type'].fillna('product')

    # فصل البيانات حسب طبيعتها البرمجية
    df_products = df_all[df_all['type'] == 'product']
    df_sales_log = df_all[df_all['type'] == 'sale_record']
    df_expenses_log = df_all[df_all['type'] == 'expense_record']
    df_debts_log = df_all[df_all['type'] == 'debt_record']
else:
    df_products = df_sales_log = df_expenses_log = df_debts_log = pd.DataFrame()

# ==========================================
# 4. TABS SYSTEM (MOBILE-FIRST NAVIGATION)
# ==========================================
tab_dash, tab_cashier, tab_add, tab_stock, tab_exp_debt = st.tabs([
    "📊 الـرئيسية", 
    "⚡ كاشير المبيعات", 
    "➕ مادة جديدة", 
    "📦 الجرد الحالي", 
    "💸 المصاريف والديون"
])

# ==========================================
# TAB 1: MAIN DASHBOARD
# ==========================================
with tab_dash:
    if not df_products.empty:
        # حساب المبيعات الحقيقية من سجل المبيعات
        total_sales_val = (df_sales_log['sale_price'] * df_sales_log['quantity']).sum() if not df_sales_log.empty else 0
        total_sales_cost = (df_sales_log['purchase_price'] * df_sales_log['quantity']).sum() if not df_sales_log.empty else 0
        
        # حساب المصاريف والديون
        total_expenses_val = df_expenses_log['purchase_price'].sum() if not df_expenses_log.empty else 0
        total_debts_val = df_debts_log['sale_price'].sum() if not df_debts_log.empty else 0
        
        # الأرباح الصافية الحقيقية = (مبيعات - تكلفة شراء المواد المباعة) - المصاريف
        real_profit = (total_sales_val - total_sales_cost) - total_expenses_val
        
        # قيمة رأس المال الحالي الموجود بالمخزن
        current_stock_capital = (df_products['purchase_price'] * df_products['quantity']).sum()

        col1, col2 = st.columns(2)
        with col1:
            st.markdown(f"<div class='card' style='background-color:#E8F5E9;'>💰 إجمالي المبيعات الحقيقية<div class='metric' style='color:#2E7D32;'>{total_sales_val:,.0f} د.ع</div></div>", unsafe_allow_html=True)
            st.markdown(f"<div class='card'>📦 قيمة البضاعة بالمخزن (رأس المال)<div class='metric'>{current_stock_capital:,.0f} د.ع</div></div>", unsafe_allow_html=True)
            st.markdown(f"<div class='card' style='background-color:#FFEBEE;'>💸 إجمالي المصاريف المخصومة<div class='metric' style='color:#C62828;'>{total_expenses_val:,.0f} د.ع</div></div>", unsafe_allow_html=True)
        with col2:
            st.markdown(f"<div class='card' style='background-color:#F3E5F5;'>✨ صافي الأرباح الفعلية اليومية<div class='metric' style='color:#4A148C;'>{real_profit:,.0f} د.ع</div></div>", unsafe_allow_html=True)
            st.markdown(f"<div class='card'>🏷️ عدد المواد النشطة بالمخزن<div class='metric'>{len(df_products)} مادة</div></div>", unsafe_allow_html=True)
            st.markdown(f"<div class='card' style='background-color:#FFF3E0;'>💳 الديون المطلوبة من الزبائن<div class='metric' style='color:#EF6C00;'>{total_debts_val:,.0f} د.ع</div></div>", unsafe_allow_html=True)

        # التنبيهات الذكية لنقص المخزون
        low_stock = df_products[df_products['quantity'] <= df_products['min_quantity']]
        if not low_stock.empty:
            st.error(f"⚠️ تنبيه المدير: هناك ({len(low_stock)}) مواد أوشكت على النفاذ من الرفوف!")
            with st.expander("🔍 استعراض المواد المطلوبة للمحل فوراً"):
                st.dataframe(low_stock[['name', 'quantity']].rename(columns={'name':'المادة', 'quantity':'الكمية المتبقية'}), use_container_width=True)
    else:
        st.info("👋 النظام جاهز ومؤمن بالكامل. يرجى البدء بتعبئة المواد أو تحديث البيانات.")

# ==========================================
# TAB 2: CASHIER MODULE (تسجيل المبيعات الذكي مع إنقاص المخزن)
# ==========================================
with tab_cashier:
    st.write("### ⚡ واجهة البيع السريع (الكاشير)")
    if not df_products.empty:
        prod_list = df_products['name'].tolist()
        
        with st.form("cashier_form"):
            selected_item = st.selectbox("🛍️ اختر المنتج المباع", prod_list)
            sell_qty = st.number_input("🔢 الكمية المباعة", min_value=1, step=1, value=1)
            custom_sell_price = st.number_input("💰 سعر البيع الفعلي (يمكنك تعديله إذا قمت بعمل خصم)", min_value=0, value=0)
            
            # جلب بيانات المادة المحددة تلقائياً
            item_data = df_products[df_products['name'] == selected_item].iloc[0]
            current_qty = int(item_data['quantity'])
            standard_sell_price = float(item_data['sale_price'])
            pur_price = float(item_data['purchase_price'])
            
            st.info(f"💡 متوفر حالياً بالمخزن: {current_qty} قطعة | سعر البيع الافتراضي: {standard_sell_price:,.0f} د.ع")
            
            submit_sale = st.form_submit_button("🛒 تأكيد البيع وطباعة الحركة")
            
            if submit_sale:
                if sell_qty > current_qty:
                    st.error(f"❌ خطأ: الكمية المطلوبة أكبر من المتوفر في المخزن! (المتاح {current_qty} فقط)")
                else:
                    final_sell_price = custom_sell_price if custom_sell_price > 0 else standard_sell_price
                    
                    # 1. تسجيل حركة مبيعات في السيرفر
                    sale_record = {
                        "name": f"بيع: {selected_item}",
                        "category": item_data['category'],
                        "quantity": int(sell_qty),
                        "purchase_price": float(pur_price), # للحفاظ على حسابات تكلفة الأرباح الصافية
                        "sale_price": float(final_sell_price),
                        "type": "sale_record",
                        "supplier": item_data['supplier']
                    }
                    
                    # 2. تحديث المخزن (إنقاص الكمية) للـ المنتج الأصلي
                    new_qty = current_qty - sell_qty
                    try:
                        # إرسال حركة البيع
                        supabase.table(TABLE_NAME).insert(sale_record).execute()
                        # تحديث كمية المنتج بالمخزن
                        supabase.table(TABLE_NAME).update({"quantity": new_qty}).eq("id", int(item_data['id'])).execute()
                        
                        st.success(f"✅ تم تسجيل العملية بنجاح! تم خصم {sell_qty} قطع من المخزن.")
                        refresh_db()
                        st.rerun()
                    except Exception as e:
                        st.error(f"حدث خطأ أثناء الاتصال بالسيرفر: {e}")
    else:
        st.warning("لا توجد منتجات في المخزن للبيع. قم بإضافة مواد أولاً.")

# ==========================================
# TAB 3: ADD NEW PRODUCT
# ==========================================
with tab_add:
    st.write("### 📥 إدخال وجبة بضاعة جديدة للمحل")
    with st.form("add_new_product_form", clear_on_submit=True):
        p_name = st.text_input("🏷️ اسم المادة بالتفصيل")
        cat_choices = ["عطور", "كريمات", "مستحضرات تجميل", "غسول", "معطرات", "منتجات شعر", "أدوات شخصية"]
        p_cat = st.selectbox("🗂️ التصنيف الرئيسي", cat_choices)
        p_custom_cat = st.text_input("✍️ أو اكتب تصنيف جديد")
        p_supp = st.text_input("🚚 اسم المورد / الشركة")
        
        c1, c2 = st.columns(2)
        with c1:
            p_pur = st.number_input("💵 سعر الشراء الجملة (د.ع)", min_value=0, step=250, value=0)
            p_qty = st.number_input("📦 الكمية الداخلة للمحل", min_value=1, step=1, value=1)
        with c2:
            p_sal = st.number_input("💰 سعر البيع المفرد (د.ع)", min_value=0, step=250, value=0)
            p_min = st.number_input("⚠️ حد التنبيه للنقص", min_value=1, step=1, value=3)
            
        save_product = st.form_submit_button("💾 حفظ المادة بالمخزن")
        
        if save_product:
            if not p_name:
                st.error("❌ يجب كتابة اسم المادة")
            else:
                final_category = p_custom_cat.strip() if p_custom_cat.strip() else p_cat
                # التحقق إذا كانت المادة موجودة سابقاً لزيادة كميتها بدلاً من تكرارها
                existing_match = df_products[df_products['name'] == p_name] if not df_products.empty else pd.DataFrame()
                
                try:
                    if not existing_match.empty:
                        # المادة موجودة، نقوم بزيادة الكمية وتحديث الأسعار
                        old_id = int(existing_match.iloc[0]['id'])
                        old_qty = int(existing_match.iloc[0]['quantity'])
                        supabase.table(TABLE_NAME).update({
                            "quantity": old_qty + int(p_qty),
                            "purchase_price": float(p_pur),
                            "sale_price": float(p_sal)
                        }).eq("id", old_id).execute()
                        st.success("🔄 هذه المادة موجودة مسبقاً، تم زيادة كميتها وتحديث أسعارها بنجاح!")
                    else:
                        # مادة جديدة تماماً
                        product_row = {
                            "name": p_name,
                            "category": final_category,
                            "supplier": p_supp if p_supp else "عام",
                            "purchase_price": float(p_pur),
                            "sale_price": float(p_sal),
                            "quantity": int(p_qty),
                            "min_quantity": int(p_min),
                            "type": "product"
                        }
                        supabase.table(TABLE_NAME).insert(product_row).execute()
                        st.success("🎉 تم تسجيل المادة الجديدة بالمخزن بنجاح!")
                    
                    refresh_db()
                    st.rerun()
                except Exception as e:
                    st.error(f"فشل الحفظ بالسيرفر: {e}")

# ==========================================
# TAB 4: STOCK MANAGEMENT & AUDIT
# ==========================================
with tab_stock:
    st.write("### 📦 جرد وتقييم مخزن كوزمتك يارا الحالي")
    if st.button("🔄 تحديث ومزامنة البيانات اللحظية مع السيرفر"):
        refresh_db()
        st.success("تم تحديث وجرد البيانات الفورية!")
        st.rerun()
        
    if not df_products.empty:
        q_search = st.text_input("🔍 اكتب اسم المادة أو الشركة للبحث الفوري...")
        df_f = df_products.copy()
        if q_search:
            df_f = df_f[df_f['name'].str.contains(q_search, case=False, na=False) | df_f['supplier'].str.contains(q_search, case=False, na=False)]
            
        # العرض بالكروت الذكية السلسة جداً لشاشات الهاتف
        for idx, row in df_f.iterrows():
            st.markdown(f"""
            <div style="background-color: white; padding: 12px; border-radius: 8px; border-right: 5px solid #E91E63; box-shadow: 0 2px 5px rgba(0,0,0,0.03); margin-bottom: 10px;">
                <b style="color: #9C27B0; font-size: 16px;">🛍️ {row['name']}</b><br>
                <small style="color:gray;">🚚 المورد: {row['supplier']} | 🗂️ {row['category']}</small>
                <div style="display: flex; justify-content: space-between; margin-top: 8px; font-size: 14px;">
                    <span>📦 المخزون: <b>{int(row['quantity'])} قطعة</b></span>
                    <span>💵 الشراء: <b>{float(row['purchase_price']):,.0f}</b></span>
                    <span style="color:#2E7D32;">💰 البيع: <b>{float(row['sale_price']):,.0f} د.ع</b></span>
                </div>
            </div>
            """, unsafe_allow_html=True)
            
        csv_bin = df_f.to_csv(index=False).encode('utf-8-sig')
        st.download_button("📥 تحميل ورقة الجرد بصيغة Excel لمدير المحل", csv_bin, "YARA_Inventory.csv", "text/csv")
    else:
        st.info("المخزن فارغ حالياً.")

# ==========================================
# TAB 5: EXPENSES & DEBTS (إدارة النفقات والديون الخارجية للزبائن)
# ==========================================
with tab_exp_debt:
    st.write("### 💸 إدارة النفقات والديون الخارجية")
    
    col_e1, col_e2 = st.columns(2)
    
    with col_e1:
        st.write("#### 🔻 تسجيل مصروف جديد (إيجار، كهرباء، كيس...)")
        with st.form("expense_form", clear_on_submit=True):
            exp_title = st.text_input("📌 بيان المصروف (مثال: أجور مولدة، رصيد، أكياس محملة)")
            exp_amount = st.number_input("💵 المبلغ المخصوم (د.ع)", min_value=0, step=250, value=0)
            submit_exp = st.form_submit_button("🛑 خصم وتسجيل المصروف")
            
            if submit_exp:
                if not exp_title or exp_amount <= 0:
                    st.error("يرجى ملء البيانات بشكل صحيح")
                else:
                    try:
                        supabase.table(TABLE_NAME).insert({
                            "name": f"مصروف: {exp_title}",
                            "category": "مصاريف تشغيلية",
                            "purchase_price": float(exp_amount), # حفظ قيمة المصروف هنا
                            "sale_price": 0,
                            "quantity": 1,
                            "type": "expense_record",
                            "supplier": "المحل"
                        }).execute()
                        st.success("تم تسجيل وخصم المبلغ من صافي الأرباح!")
                        refresh_db()
                        st.rerun()
                    except Exception as e:
                        st.error(f"خلل بالسيرفر: {e}")

    with col_e2:
        st.write("#### 🔸 تسجيل دين خارجي على زبون")
        with st.form("debt_form", clear_on_submit=True):
            debtor_name = st.text_input("👤 اسم الزبون أو المدين")
            debt_amount = st.number_input("💵 مبلغ الدين المطلّوب (د.ع)", min_value=0, step=250, value=0)
            submit_debt = st.form_submit_button("⚠️ تثبيت الدين في السجلات")
            
            if submit_debt:
                if not debtor_name or debt_amount <= 0:
                    st.error("يرجى كتابة الاسم والمبلغ")
                else:
                    try:
                        supabase.table(TABLE_NAME).insert({
                            "name": f"دين: {debtor_name}",
                            "category": "ديون العملاء",
                            "purchase_price": 0,
                            "sale_price": float(debt_amount), # حفظ قيمة الدين هنا
                            "quantity": 1,
                            "type": "debt_record",
                            "supplier": debtor_name
                        }).execute()
                        st.success("تم تثبيت الدين بذمة الزبون بنجاح!")
                        refresh_db()
                        st.rerun()
                    except Exception as e:
                        st.error(f"خلل بالسيرفر: {e}")

    # استعراض كشوفات الحركة السريعة لمدير المحل
    st.write("---")
    st.write("### 📜 السجلات الأخيرة المقيدة اليوم")
    
    cx1, cx2 = st.columns(2)
    with cx1:
        st.write("##### 📑 سجل المصاريف المقيدة:")
        if not df_expenses_log.empty:
            st.dataframe(df_expenses_log[['name', 'purchase_price']].rename(columns={'name':'البيان', 'purchase_price':'المبلغ د.ع'}), use_container_width=True)
    with cx2:
        st.write("##### 📑 سجل ديون الزبائن الحالية:")
        if not df_debts_log.empty:
            st.dataframe(df_debts_log[['name', 'sale_price']].rename(columns={'name':'المدين', 'sale_price':'مبلغ الدين د.ع'}), use_container_width=True)
