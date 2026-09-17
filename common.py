"""
common.py
---------
ملف مشترك بين كل صفحات TAVEN OS: فيه تعريف الأقسام المالية، دوال القراءة/الحفظ
من ملف الإكسيل، وتنسيقات الـ CSS (بما فيها دعم الدارك/لايت مود والتنبيه الغضبان).

مهم: أي صفحة جديدة تضيفها تقدر تستورد من هنا:
    import common
"""

import os
import pandas as pd
import streamlit as st

EXCEL_FILE = "TAVEN.xlsx"

# ==================================================================
# الأقسام المالية (تستخدمها صفحة "Input & Output المالية")
# عشان تضيف قسم جديد: زوّد عنصر هنا بنفس الشكل، من غير أي كود إضافي.
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
    # قسم جديد: التصنيع — المصنع أول حاجة، بعدين الموديل، وبعدين الحساب الآلي
    "MANUFACTURING": {
        "label": "التصنيع (Manufacturing)",
        "default": pd.DataFrame(
            [
                {"Factory": "Sample Factory", "Model": "Hoodie V1", "Qty": 50, "Unit Price": 200, "Total": 10000},
            ]
        ),
        "fields": [
            {"name": "Factory", "label": "اسم المصنع", "type": "text"},
            {"name": "Model", "label": "اسم الموديل", "type": "text"},
            {"name": "Qty", "label": "الكمية", "type": "int", "min": 1, "default": 1, "step": 1},
            {"name": "Unit Price", "label": "سعر القطعة (EGP)", "type": "number", "min": 0.0, "step": 10.0},
        ],
        "computed_field": {"name": "Total", "of": ["Qty", "Unit Price"]},
        "total_field": "Total",
        "add_label": "+ تسجيل أمر تصنيع",
    },
}

SHEET_NAMES = list(SECTIONS.keys())

# ==================================================================
# شيتات مستقلة تستخدمها باقي الصفحات (شات / تاسكات / أفكار / ...)
# ==================================================================
EXTRA_SHEETS_DEFAULTS = {
    "CHAT": pd.DataFrame(columns=["Time", "Sender", "Message"]),
    "IDEAS": pd.DataFrame(columns=["Date", "Type", "Title", "Notes"]),
    "ADS_CAMPAIGNS": pd.DataFrame(columns=["Campaign Name", "Daily Spend", "Monthly Spend"]),
    "TASKS": pd.DataFrame(columns=["ID", "Description", "Type", "Assigned To", "Status", "Claimed By"]),
    "VISION": pd.DataFrame(columns=["Target Name", "Type", "Target Value", "Actual Value"]),
}

ALL_SHEETS = SHEET_NAMES + list(EXTRA_SHEETS_DEFAULTS.keys())


def _default_for(name: str) -> pd.DataFrame:
    if name in SECTIONS:
        return SECTIONS[name]["default"].copy()
    return EXTRA_SHEETS_DEFAULTS[name].copy()


def load_all_fresh() -> dict:
    """يقرأ كل الشيتات من ملف الإكسيل *مباشرة من غير أي كاش*.

    مهم جدًا للصفحات المشتركة زي الشات والتاسكات: كل شريك بيفتح
    التطبيق في براوزر/جلسة منفصلة، فلازم كل واحد يشوف آخر تحديث
    من الشريك التاني فورًا، مش نسخة قديمة متخزنة في كاش.
    """
    data = {}
    if os.path.exists(EXCEL_FILE):
        try:
            xls = pd.ExcelFile(EXCEL_FILE)
            for name in ALL_SHEETS:
                if name in xls.sheet_names:
                    data[name] = pd.read_excel(xls, sheet_name=name)
        except Exception as e:
            st.warning(f"تعذر قراءة {EXCEL_FILE}، هيتم استخدام بيانات افتراضية مؤقتًا. الخطأ: {e}")
    for name in ALL_SHEETS:
        if name not in data:
            data[name] = _default_for(name)
    return data


def save_sheet(name: str, df: pd.DataFrame):
    """يحفظ شيت واحد بس، لكن بيعيد كتابة الملف كله (كل الشيتات التانية
    بتتحفظ زي ما هي) عشان نتجنب تلف أي بيانات في شيتات تانية."""
    data = load_all_fresh()
    data[name] = df
    try:
        with pd.ExcelWriter(EXCEL_FILE, engine="openpyxl") as writer:
            for n, d in data.items():
                d.to_excel(writer, sheet_name=n, index=False)
        return True, None
    except PermissionError:
        return False, "الملف مفتوح في برنامج تاني (زي Excel) — اقفله وحاول تاني."
    except Exception as e:
        return False, str(e)


# ==================================================================
# التنسيق العام (يدعم الدارك/لايت مود + تنبيه الحقل الفاضي)
# ==================================================================
def inject_theme_css():
    st.markdown(
        """
<style>
@keyframes fadeIn {
    0% { opacity: 0; transform: translateY(10px); }
    100% { opacity: 1; transform: translateY(0); }
}
@keyframes shake {
    0%, 100% { transform: translateX(0); }
    20%, 60% { transform: translateX(-8px); }
    40%, 80% { transform: translateX(8px); }
}

/* بنستخدم متغيرات Streamlit بدل ألوان ثابتة عشان تتماشى مع
   الدارك مود واللايت مود أوتوماتيك، وميبقاش في حتت بيضا فاضلة */
.stApp {
    background-color: var(--background-color);
    animation: fadeIn 0.4s ease-in-out;
}
div[data-testid="stMetric"] {
    background: var(--secondary-background-color);
    border: 1px solid rgba(128, 128, 128, 0.25);
    border-radius: 10px;
    padding: 12px;
    box-shadow: 0 2px 8px rgba(0, 0, 0, 0.08);
}
div[data-testid="stMetric"] * {
    color: var(--text-color) !important;
}
.stButton>button {
    border-radius: 8px;
    background: linear-gradient(135deg, #2563eb, #1d4ed8);
    color: #ffffff !important;
    font-weight: bold;
    border: none;
    width: 100%;
    padding: 10px;
}
.angry-alert {
    animation: shake 0.4s ease-in-out 2;
    background: #fee2e2;
    color: #b91c1c;
    border: 1px solid #f87171;
    padding: 12px;
    border-radius: 8px;
    font-weight: bold;
    text-align: center;
    margin: 8px 0;
}
</style>
""",
        unsafe_allow_html=True,
    )


def angry_warning(message: str = "في حقل فاضي يا أسطى! كمّل البيانات الأول"):
    """تنبيه غضبان بأنيميشن اهتزاز لما حد يسيب حقل مطلوب فاضي."""
    st.markdown(f'<div class="angry-alert">😡 {message}</div>', unsafe_allow_html=True)
