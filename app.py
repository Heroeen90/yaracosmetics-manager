import streamlit as st
from supabase import create_client, Client
import pandas as pd
from datetime import datetime

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
    @import url('https://fonts.googleapis.com/css2?family=Tajawal:wght=400;500;700&display=swap');
    
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
        padding: 10px 20px !important;
        font-size: 16px !important;
        font-weight: bold !important;
    }
    div.stButton > button:first-child {
        background-color: #E91E63 !important;
        color: white !important;
        border: none !important;
    }
</style>
""", unsafe_allow_html=True)

st.markdown("<div class='main-title'>💄 إدارة كوزمتك يارا</div>", unsafe_allow_html=True)
st.markdown("<div class='sub-title'>الإصدار التجاري v3.0 - حماية الديون والتسديد الجزئي</div>", unsafe_allow_html=True)

# ==========================================
# 3. DATA LAYER
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

raw_data = st.session_state['cached_data']
df_all = pd.DataFrame(raw_data) if raw_data else pd.DataFrame()

if not df_all.empty:
    df_all['purchase_price'] = pd.to_numeric(df_all.get('purchase_price', 0), errors='coerce').fillna(0)
    df_all['sale_price'] = pd.to_numeric(df_all.get('sale_price', 0), errors='coerce').fillna(0)
    df_all['quantity'] = pd.to_numeric(df_all.get('quantity', 0), errors='coerce').fillna(0)
    df_all['min_quantity'] = pd.to_numeric(df_all.get('min_quantity', 3), errors='coerce').fillna(3)
    if 'type' not in df_all.columns:
        df_all['type'] = 'product'
    df_all['type'] = df_all['type'].fillna('product')

    df_products = df_all[df_all['type'] == 'product']
    df_sales_log = df_all[df_all['type'] == 'sale_record']
    df_expenses_log = df_all[df_all['type'] == 'expense_record']
    
    # جلب الديون النشطة فقط (التي مبلّغها أكبر من 0 وليست مسددة بالكامل)
    df_debts_log = df_all[(df_all['type'] == 'debt_record') & (df_all['sale_price'] > 0)]
else:
    df_products = df_sales_log = df_expenses_log = df_debts_log = pd.DataFrame()

# ==========================================
# 4. TABS SYSTEM
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
    if not df_products.empty or not df_sales_log.empty or not df_expenses_log.empty or not df_debts_log.empty:
        total_sales_val = (df_sales_log['sale_price'] * df_sales_log['quantity']).sum() if not df_sales_log.empty else 0
        total_sales_cost = (df_sales_log['purchase_price'] * df_sales_log['quantity']).sum() if not df_sales_log.empty else 0
        
        total_expenses_val = df_expenses_log['purchase_price'].sum() if not df_expenses_log.empty else 0
        total_debts_val = df_debts_log['sale_price'].sum() if not df_debts_log.empty else 0
        
        real_profit = (total_sales_val - total_sales_cost) - total_expenses_val
        current_stock_capital = (df_products['purchase_price'] * df_products['quantity']).sum() if not df_products.empty else 0

        col1, col2 = st.columns(2)
        with col1:
            st.markdown(f"<div class='card' style='background-color:#E8F5E9;'>💰 إجمالي المبيعات الحقيقية<div class='metric' style='color:#2E7D32;'>{total_sales_val:,.0f} د.ع</div></div>", unsafe_allow_html=True)
            st.markdown(f"<div class='card'>📦 قيمة البضاعة بالمخزن (رأس المال)<div class='metric'>{current_stock_capital:,.0f} د.ع</div></div>", unsafe_allow_html=True)
            st.markdown(f"<div class='card' style='background-color:#FFEBEE;'>💸 إجمالي المصاريف المخصومة<div class='metric' style='color:#C62828;'>{total_expenses_val:,.0f} د.ع</div></div>", unsafe_allow_html=True)
        with col2:
            st.markdown(f"<div class='card' style='background-color:#F3E5F5;'>✨ صافي الأرباح الفعلية اليومية<div class='metric' style='color:#4A148C;'>{real_profit:,.0f} د.ع</div></div>", unsafe_allow_html=True)
            st.markdown(f"<div class='card'>🏷️ عدد المواد النشطة بالمخزن<div class='metric'>{len(df_products)} مادة</div></div>", unsafe_allow_html=True)
            st.markdown(f"<div class='card' style='background-color:#FFF3E0;'>💳 الديون النشطة المطلوبة من الزبائن<div class='metric' style='color:#EF6C00;'>{total_debts_val:,.0f} د.ع</div></div>", unsafe_allow_html=True)

        low_stock = df_products[df_products['quantity'] <= df_products['min_quantity']] if not df_products.empty else pd.DataFrame()
        if not low_stock.empty:
            st.error(f"⚠️ تنبيه المدير: هناك ({len(low_stock)}) مواد أوشكت على النفاذ من الرفوف!")
    else:
        st.info("👋 النظام جاهز ومؤمن بالكامل. يرجى البدء بتعبئة المواد أو تحديث البيانات.")

# ==========================================
# TAB 2: CASHIER MODULE
# ==========================================
with tab_cashier:
    st.write("### ⚡ واجهة البيع السريع (الكاشير)")
    if not df_products.empty:
        prod_list = df_products['name'].tolist()
        
        with st.form("cashier_form"):
            selected_item = st.selectbox("🛍️ اختر المنتج المباع", prod_list)
            sell_qty = st.number_input("🔢 الكمية المباعة", min_value=1, step=1, value=1)
            custom_sell_price = st.number_input("💰 سعر البيع الفعلي (يمكنك تعديله إذا قمت بعمل خصم)", min_value=0, value=0)
            
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
                    
                    sale_record = {
                        "name": f"بيع: {selected_item}",
                        "category": item_data['category'],
                        "quantity": int(sell_qty),
                        "purchase_price": float(pur_price),
                        "sale_price": float(final_sell_price),
                        "type": "sale_record",
                        "supplier": item_data['supplier']
                    }
                    
                    new_qty = current_qty - sell_qty
                    try:
                        supabase.table(TABLE_NAME).insert(sale_record).execute()
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
                existing_match = df_products[df_products['name'] == p_name] if not df_products.empty else pd.DataFrame()
                
                try:
                    if not existing_match.empty:
                        old_id = int(existing_match.iloc[0]['id'])
                        old_qty = int(existing_match.iloc[0]['quantity'])
                        supabase.table(TABLE_NAME).update({
                            "quantity": old_qty + int(p_qty),
                            "purchase_price": float(p_pur),
                            "sale_price": float(p_sal)
                        }).eq("id", old_id).execute()
                        st.success("🔄 هذه المادة موجودة مسبقاً، تم زيادة كميتها وتحديث أسعارها بنجاح!")
                    else:
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
# TAB 5: EXPENSES & DEBTS (نسخة إدارة الديون المطورة بالكامل والتسديد الجزئي)
# ==========================================
with tab_exp_debt:
    st.write("### 💸 إدارة النفقات والديون الخارجية")
    
    col_e1, col_e2 = st.columns(2)
    
    with col_e1:
        st.write("#### 🔻 تسجيل مصروف جديد")
        with st.form("expense_form", clear_on_submit=True):
            exp_title = st.text_input("📌 بيان المصروف (مثال: أجور مولدة، إيجار...)")
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
                            "purchase_price": float(exp_amount),
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
            debtor_name = st.text_input("👤 اسم الزبون أو المدين (مثال: كرار)")
            debt_amount = st.number_input("💵 مبلغ الدين المطلوب (د.ع)", min_value=0, step=250, value=0)
            submit_debt = st.form_submit_button("⚠️ تثبيت الدين في السجلات")
            
            if submit_debt:
                if not debtor_name or debt_amount <= 0:
                    st.error("يرجى كتابة الاسم والمبلغ")
                else:
                    try:
                        supabase.table(TABLE_NAME).insert({
                            "name": f"دين: {debtor_name}",
                            "category": "مطلوب حالياً",
                            "purchase_price": 0,
                            "sale_price": float(debt_amount),
                            "quantity": 1,
                            "type": "debt_record",
                            "supplier": debtor_name
                        }).execute()
                        st.success(f"تم تثبيت دين بقيمة {debt_amount:,.0f} د.ع بذمة {debtor_name}!")
                        refresh_db()
                        st.rerun()
                    except Exception as e:
                        st.error(f"خلل بالسيرفر: {e}")

    # استعراض وتحديث الديون والمصاريف مع إظهار التاريخ والوقت والتسديد الذكي
    st.write("---")
    st.write("### 📜 السجلات والكشوفات اللحظية الموثقة")
    
    cx1, cx2 = st.columns(2)
    
    with cx1:
        st.write("##### 📑 سجل المصاريف المقيدة اليوم:")
        if not df_expenses_log.empty:
            df_exp_display = df_expenses_log.copy()
            df_exp_display['التاريخ'] = pd.to_datetime(df_exp_display['created_at']).dt.strftime('%Y-%m-%d %H:%M')
            st.dataframe(df_exp_display[['name', 'purchase_price', 'التاريخ']].rename(columns={
                'name':'البيان', 'purchase_price':'المبلغ د.ع'
            }), use_container_width=True)
        else:
            st.info("لا توجد مصاريف مقيدة حالياً.")
            
    with cx2:
        st.write("##### 📑 سجل ديون الزبائن النشطة (التسديد الآمن والجزئي):")
        if not df_debts_log.empty:
            for idx, d_row in df_debts_log.iterrows():
                d_id = int(d_row['id'])
                d_name = d_row['supplier']
                d_amt = float(d_row['sale_price'])
                d_date = pd.to_datetime(d_row['created_at']).strftime('%Y-%m-%d %H:%M')
                
                # كرت عرض الدين
                st.markdown(f"""
                <div style="background-color: #FFF3E0; padding: 12px; border-radius: 8px; border-right: 5px solid #FF9800; margin-bottom: 5px;">
                    <span style="font-size:16px; font-weight:bold; color:#E65100;">👤 الزبون: {d_name}</span><br>
                    <span style="font-size:14px; color:#555;">💵 الدين المتبقي الحالي: <b style="font-size:16px; color:#E91E63;">{d_amt:,.0f} د.ع</b></span><br>
                    <small style="color:gray;">📅 تاريخ التثبيت: {d_date}</small>
                </div>
                """, unsafe_allow_html=True)
                
                # آلية الأمان والتسديد الذكي (توسيع عند الضغط للوقاية من النقرات العشوائية)
                with st.expander(f"💳 خيارات تسديد حساب {d_name}"):
                    # صندوق إدخال مبلغ التسديد الفعلي
                    paid_amount = st.number_input(
                        f"المبلغ المدفوع واصلاً من {d_name} (د.ع)", 
                        min_value=0.0, 
                        max_value=d_amt, 
                        value=d_amt, 
                        step=250.0, 
                        key=f"amt_{d_id}"
                    )
                    
                    # زر التأكيد النهائي لحماية البيانات
                    confirm_pay = st.button(f"⚠️ تأكيد خصم {paid_amount:,.0f} د.ع نهائياً", key=f"btn_{d_id}")
                    
                    if confirm_pay:
                        if paid_amount <= 0:
                            st.error("الرجاء إدخال مبلغ صحيح أكبر من صفر")
                        else:
                            try:
                                # حساب المتبقي الجديد على الزبون
                                remaining_debt = d_amt - paid_amount
                                
                                if remaining_debt <= 0:
                                    # إذا سدد المبلغ بالكامل، يتم تصفير القيمة وتحديث الحالة
                                    supabase.table(TABLE_NAME).update({
                                        "sale_price": 0,
                                        "category": "تم التسديد بالكامل"
                                    }).eq("id", d_id).execute()
                                    st.success(f"🎉 تم تسديد الدين بالكامل وإغلاق حساب {d_name}!")
                                else:
                                    # إذا سدد تسديداً جزئياً، يتم تحديث القيمة المتبقية فقط في قاعدة البيانات
                                    supabase.table(TABLE_NAME).update({
                                        "sale_price": float(remaining_debt),
                                        "category": "تسديد جزئي مستمر"
                                    }).eq("id", d_id).execute()
                                    st.success(f"✅ تم خصم الواصل بنجاح! المتبقي حالياً بذمة {d_name} هو: {remaining_debt:,.0f} د.ع")
                                
                                refresh_db()
                                st.rerun()
                            except Exception as e:
                                st.error(f"خلل في التحديث بالسيرفر: {e}")
        else:
            st.info("ممتاز! لا توجد ديون نشطة بذمة الزبائن حالياً.")

