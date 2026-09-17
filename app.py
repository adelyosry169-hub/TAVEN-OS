import os
import pandas as pd
import streamlit as st

# ================== إعدادات عامة للصفحة ==================
st.set_page_config(
    page_title="TAVEN OS",
    page_icon="⚡",
    layout="wide",
    initial_sidebar_state="collapsed",
)

st.markdown(
    """
<style>
    @keyframes fadeIn {
        0% { opacity: 0; transform: translateY(10px); }
        100% { opacity: 1; transform: translateY(0); }
    }
    .stApp {
        background-color: #f7f9fc;
        animation: fadeIn 0.5s ease-in-out;
    }
    div[data-testid="stMetric"] {
        background: #ffffff;
        border: 1px solid #e2e8f0;
        border-radius: 10px;
        padding: 12px;
        box-shadow: 0 2px 8px rgba(0,0,0,0.04);
    }
    .stButton>button {
        border-radius: 8px;
        background: linear-gradient(135deg, #2563eb, #1d4ed8);
        color: white;
        font-weight: bold;
        border: none;
        width: 100%;
        padding: 10px;
    }
</style>
""",
    unsafe_allow_html=True,
)

EXCEL_FILE = "TAVEN.xlsx"

# ==================================================================
# تعريف الصفحات (SECTIONS)
# ------------------------------------------------------------------
# عشان تضيف صفحة جديدة مستقبلًا: انسخ أي عنصر تحت وغيّر البيانات،
# مش محتاج تكتب كود جديد أو تكرر منطق الجدول/الفورم من الأول.
# ==================================================================
SECTIONS = {
    "PARTNERS": {
        "label": "الشركاء (PARTNERS)",
        "default": pd.DataFrame(
            [
                {"Partner": "Partner A", "Contribution": 50000, "Purpose": "Initial Inventory Funding"},
                {"Partner": "Partner B", "Contribution": 30000, "Purpose": "Marketing & Ads Capital"},
            ]
        ),
        "fields": [
            {"name": "Partner", "label": "اسم الشريك", "type": "text"},
            {"name": "Contribution", "label": "المساهمة (EGP)", "type": "number", "min": 0.0, "step": 1000.0},
            {"name": "Purpose", "label": "الغرض من المساهمة", "type": "text"},
        ],
        "total_field": "Contribution",
        "add_label": "+ إضافة مساهمة",
    },
    "FINANCE": {
        "label": "المالية (FINANCE)",
        "default": pd.DataFrame(
            [
                {"Category": "Fabric", "Subcategory": "French Terry", "Qty": 100, "Unit Cost": 150, "Total": 15000},
                {"Category": "Ads", "Subcategory": "Meta Ads", "Qty": 1, "Unit Cost": 5000, "Total": 5000},
            ]
        ),
        "fields": [
            {"name": "Category", "label": "النوع", "type": "text", "default": "Fabric"},
            {"name": "Subcategory", "label": "الوصف", "type": "text", "default": "Cotton"},
            {"name": "Qty", "label": "الكمية", "type": "int", "min": 1, "default": 1, "step": 1},
            {"name": "Unit Cost", "label": "سعر القطعة (EGP)", "type": "number", "min": 0.0, "step": 10.0},
        ],
        "computed_field": {"name": "Total", "of": ["Qty", "Unit Cost"]},
        "total_field": "Total",
        "add_label": "+ تسجيل مصروف",
    },
    "OPERATIONS": {
        "label": "العمليات (OPERATIONS)",
        "default": pd.DataFrame(
            [
                {"Material": "French Terry Cotton 400GSM", "Cost": 15000, "Weight": 100, "Cost/KG": 150, "Supplier": "Nile Textiles"},
                {"Material": "Ribbing Fabric", "Cost": 2400, "Weight": 20, "Cost/KG": 120, "Supplier": "Delta Weave"},
            ]
        ),
        "fields": [
            {"name": "Material", "label": "اسم الخام", "type": "text"},
            {"name": "Weight", "label": "الوزن (KG)", "type": "number", "min": 0.1, "default": 1.0, "step": 1.0},
            {"name": "Cost/KG", "label": "سعر الكيلو (EGP)", "type": "number", "min": 0.0, "step": 10.0},
            {"name": "Supplier", "label": "المورد", "type": "text"},
        ],
        "computed_field": {"name": "Cost", "of": ["Weight", "Cost/KG"]},
        "total_field": "Cost",
        "add_label": "+ تسجيل خام",
    },
    "EXTRA_EXPENSES": {
        "label": "مصاريف إضافية (EXTRA EXPENSES)",
        "default": pd.DataFrame(
            [
                {"Expense Name": "Shipping & Delivery", "Qty": 10, "Unit Cost": 50, "Total": 500, "Notes": "Sample Shipping"},
            ]
        ),
        "fields": [
            {"name": "Expense Name", "label": "اسم المصروف", "type": "text"},
            {"name": "Qty", "label": "الكمية", "type": "int", "min": 1, "default": 1, "step": 1},
            {"name": "Unit Cost", "label": "سعر الوحدة (EGP)", "type": "number", "min": 0.0, "step": 10.0},
            {"name": "Notes", "label": "ملاحظات", "type": "text"},
        ],
        "computed_field": {"name": "Total", "of": ["Qty", "Unit Cost"]},
        "total_field": "Total",
        "add_label": "+ إضافة مصروف",
    },
    # صفحة جديدة اتضافت كمثال حي — دلوقتي Gross Val / Realized حقيقيين
    # وجايين من بيانات فعلية بدل ما يكونوا أرقام ثابتة في الكود
    "SALES": {
        "label": "المبيعات (SALES)",
        "default": pd.DataFrame(
            [
                {"Product": "T-Shirt Basic", "Qty Sold": 10, "Unit Price": 1160, "Total Revenue": 11600, "Amount Collected": 5000},
            ]
        ),
        "fields": [
            {"name": "Product", "label": "اسم المنتج", "type": "text"},
            {"name": "Qty Sold", "label": "الكمية المباعة", "type": "int", "min": 1, "default": 1, "step": 1},
            {"name": "Unit Price", "label": "سعر البيع للوحدة (EGP)", "type": "number", "min": 0.0, "step": 10.0},
            {"name": "Amount Collected", "label": "المبلغ المحصّل فعليًا (EGP)", "type": "number", "min": 0.0, "step": 100.0},
        ],
        "computed_field": {"name": "Total Revenue", "of": ["Qty Sold", "Unit Price"]},
        "total_field": "Total Revenue",
        "add_label": "+ تسجيل عملية بيع",
    },
}

SHEET_NAMES = list(SECTIONS.keys())


# ================== تحميل / حفظ البيانات ==================
@st.cache_data(show_spinner=False)
def _read_excel_file(path):
    """يقرأ كل الشيتات من الملف مرة واحدة. لو شيت ناقص أو الملف مش موجود
    بيستخدم البيانات الافتراضية بدل ما يعمل كراش."""
    data = {}
    if os.path.exists(path):
        try:
            xls = pd.ExcelFile(path)
            for name in SHEET_NAMES:
                if name in xls.sheet_names:
                    data[name] = pd.read_excel(xls, sheet_name=name)
        except Exception as e:
            st.warning(f"تعذر قراءة {path}، هيتم استخدام بيانات افتراضية مؤقتًا. الخطأ: {e}")
    for name in SHEET_NAMES:
        if name not in data:
            data[name] = SECTIONS[name]["default"].copy()
    return data


def init_state():
    """يحمّل البيانات في session_state مرة واحدة بس عند أول تشغيل للجلسة.
    بعد كده كل التعديلات بتحصل في الذاكرة (session_state) وتنعكس فورًا
    على الداشبورد، وميتلمسش ملف الإكسيل غير لما تدوس زرار الحفظ."""
    if "data" not in st.session_state:
        st.session_state.data = _read_excel_file(EXCEL_FILE)


def persist_to_excel():
    """يحفظ كل الشيتات مرة واحدة في نفس الملف (أأمن من الكتابة شيت شيت)."""
    try:
        with pd.ExcelWriter(EXCEL_FILE, engine="openpyxl") as writer:
            for name in SHEET_NAMES:
                st.session_state.data[name].to_excel(writer, sheet_name=name, index=False)
        _read_excel_file.clear()  # نفضّي الكاش عشان القراءة الجاية تبقى محدثة
        return True, None
    except PermissionError:
        return False, "الملف مفتوح في برنامج تاني (زي Excel) — اقفله وحاول تاني."
    except Exception as e:
        return False, str(e)


init_state()

# ================== الهيدر والمؤشرات (بتتحدث لحظيًا) ==================
st.title("⚡ TAVEN OS")

sales_df = st.session_state.data["SALES"]
finance_df = st.session_state.data["FINANCE"]
ops_df = st.session_state.data["OPERATIONS"]
extra_df = st.session_state.data["EXTRA_EXPENSES"]

gross_val = sales_df["Total Revenue"].sum() if "Total Revenue" in sales_df else 0
realized = sales_df["Amount Collected"].sum() if "Amount Collected" in sales_df else 0

# ملحوظة: بقينا بنجمع مصاريف Operations كمان (كانت ناقصة في النسخة القديمة)
total_exp = (
    (finance_df["Total"].sum() if "Total" in finance_df else 0)
    + (ops_df["Cost"].sum() if "Cost" in ops_df else 0)
    + (extra_df["Total"].sum() if "Total" in extra_df else 0)
)
net_profit = realized - total_exp

m1, m2, m3, m4 = st.columns(4)
m1.metric("Gross Val (إجمالي المبيعات)", f"{gross_val:,.0f} EGP")
m2.metric("Realized (المحصّل فعليًا)", f"{realized:,.0f} EGP")
m3.metric("Total Exp (المصاريف)", f"{total_exp:,.0f} EGP")
m4.metric("Net Profit (صافي الربح)", f"{net_profit:,.0f} EGP")

st.markdown("---")

section_key = st.radio(
    "اختر القسم / SECTION",
    SHEET_NAMES,
    format_func=lambda k: SECTIONS[k]["label"],
    horizontal=True,
)

st.markdown("---")


# ================== دالة عامة لعرض أي قسم ==================
def render_section(key):
    cfg = SECTIONS[key]

    col_table, col_form = st.columns([2.2, 1])

    with col_table:
        st.subheader(f"جدول {cfg['label']}")
        edited = st.data_editor(
            st.session_state.data[key],
            num_rows="dynamic",
            use_container_width=True,
            key=f"editor_{key}",
        )
        # أي تعديل (حذف صف / تغيير رقم / إضافة صف يدويًا) بيترحّل فورًا
        # لـ session_state، وده اللي بيخلي المؤشرات فوق تتحدث تلقائيًا
        st.session_state.data[key] = edited

        total_field = cfg.get("total_field")
        if total_field and total_field in edited:
            st.info(f"📊 إجمالي {cfg['label']}: {edited[total_field].sum():,.2f} EGP")

        if st.button("💾 حفظ نهائي في ملف الإكسيل", key=f"save_{key}"):
            ok, err = persist_to_excel()
            if ok:
                st.success("تم الحفظ في TAVEN.xlsx بنجاح!")
            else:
                st.error(f"فشل الحفظ: {err}")

    with col_form:
        st.subheader("إضافة سجل جديد")
        values = {}
        for f in cfg["fields"]:
            widget_key = f"input_{key}_{f['name']}"
            if f["type"] == "text":
                values[f["name"]] = st.text_input(
                    f["label"], value=f.get("default", ""), key=widget_key
                )
            elif f["type"] == "int":
                values[f["name"]] = st.number_input(
                    f["label"],
                    min_value=f.get("min", 0),
                    value=f.get("default", f.get("min", 0)),
                    step=f.get("step", 1),
                    key=widget_key,
                )
            else:  # number (float)
                values[f["name"]] = st.number_input(
                    f["label"],
                    min_value=float(f.get("min", 0.0)),
                    value=float(f.get("default", f.get("min", 0.0))),
                    step=float(f.get("step", 1.0)),
                    key=widget_key,
                )

        computed = cfg.get("computed_field")
        if computed:
            a, b = computed["of"]
            auto_val = float(values[a]) * float(values[b])
            values[computed["name"]] = auto_val
            st.markdown(f"### 💵 الإجمالي: **{auto_val:,.2f} EGP**")

        # أول حقل نصي في الفورم بيتعامل معاه كـ"حقل مطلوب" (زي المنطق الأصلي)
        required_field = next((f["name"] for f in cfg["fields"] if f["type"] == "text"), None)

        if st.button(cfg["add_label"], key=f"add_{key}"):
            if required_field and not str(values.get(required_field, "")).strip():
                st.warning("من فضلك املأ الحقل الأساسي الأول قبل الإضافة.")
            else:
                new_row = pd.DataFrame([values])
                st.session_state.data[key] = pd.concat(
                    [st.session_state.data[key], new_row], ignore_index=True
                )
                st.success("تمت الإضافة للجدول! (اضغط 'حفظ نهائي' لو عايز تثبّتها في ملف الإكسيل)")
                st.rerun()


render_section(section_key)
