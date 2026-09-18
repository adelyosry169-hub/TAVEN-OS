"""
common.py
---------
الملف المشترك بين كل صفحات TAVEN OS:
- تعريف الأقسام المالية (SECTIONS)
- تسجيل الدخول (require_login)
- القراءة/الحفظ من TAVEN.xlsx + المزامنة مع جوجل درايف
- جدول قابل للتعديل بيتحفظ أوتوماتيك ومعاه تراجع/إعادة (editable_table)
- التنسيق العام (CSS) والتنبيه الغضبان
"""

import os
import pandas as pd
import streamlit as st

import gdrive

EXCEL_FILE = "TAVEN.xlsx"
MAX_HISTORY = 10

# ==================================================================
# الأقسام المالية (تستخدمها صفحة "Input & Output المالية")
# لاحظ: كل الأقسام فيها حقل "Date" آخر حقل، عشان صفحة التحليلات
# تقدر ترسم اتجاه الأرقام عبر الوقت.
# ==================================================================
SECTIONS = {
    "PARTNERS": {
        "label": "الشركاء (PARTNERS)",
        "columns": ["Partner", "Contribution", "Purpose", "Date"],
        "fields": [
            {"name": "Partner", "label": "اسم الشريك", "type": "text"},
            {"name": "Contribution", "label": "المساهمة (EGP)", "type": "number", "min": 0.0, "step": 1000.0},
            {"name": "Purpose", "label": "الغرض من المساهمة", "type": "text"},
            {"name": "Date", "label": "التاريخ", "type": "date"},
        ],
        "total_field": "Contribution",
        "add_label": "+ إضافة مساهمة",
    },
    "FINANCE": {
        "label": "المالية (FINANCE)",
        "columns": ["Category", "Subcategory", "Qty", "Unit Cost", "Total", "Date"],
        "fields": [
            {"name": "Category", "label": "النوع", "type": "text", "default": "Fabric"},
            {"name": "Subcategory", "label": "الوصف", "type": "text", "default": "Cotton"},
            {"name": "Qty", "label": "الكمية", "type": "int", "min": 1, "default": 1, "step": 1},
            {"name": "Unit Cost", "label": "سعر القطعة (EGP)", "type": "number", "min": 0.0, "step": 10.0},
            {"name": "Date", "label": "التاريخ", "type": "date"},
        ],
        "computed_field": {"name": "Total", "of": ["Qty", "Unit Cost"]},
        "total_field": "Total",
        "add_label": "+ تسجيل مصروف",
    },
    "OPERATIONS": {
        "label": "العمليات (OPERATIONS)",
        "columns": ["Material", "Weight", "Cost/KG", "Supplier", "Cost", "Date"],
        "fields": [
            {"name": "Material", "label": "اسم الخام", "type": "text"},
            {"name": "Weight", "label": "الوزن (KG)", "type": "number", "min": 0.1, "default": 1.0, "step": 1.0},
            {"name": "Cost/KG", "label": "سعر الكيلو (EGP)", "type": "number", "min": 0.0, "step": 10.0},
            {"name": "Supplier", "label": "المورد", "type": "text"},
            {"name": "Date", "label": "التاريخ", "type": "date"},
        ],
        "computed_field": {"name": "Cost", "of": ["Weight", "Cost/KG"]},
        "total_field": "Cost",
        "add_label": "+ تسجيل خام",
    },
    "EXTRA_EXPENSES": {
        "label": "مصاريف إضافية (EXTRA EXPENSES)",
        "columns": ["Expense Name", "Qty", "Unit Cost", "Total", "Notes", "Date"],
        "fields": [
            {"name": "Expense Name", "label": "اسم المصروف", "type": "text"},
            {"name": "Qty", "label": "الكمية", "type": "int", "min": 1, "default": 1, "step": 1},
            {"name": "Unit Cost", "label": "سعر الوحدة (EGP)", "type": "number", "min": 0.0, "step": 10.0},
            {"name": "Notes", "label": "ملاحظات", "type": "text"},
            {"name": "Date", "label": "التاريخ", "type": "date"},
        ],
        "computed_field": {"name": "Total", "of": ["Qty", "Unit Cost"]},
        "total_field": "Total",
        "add_label": "+ إضافة مصروف",
    },
    "SALES": {
        "label": "المبيعات (SALES)",
        "columns": ["Product", "Qty Sold", "Unit Price", "Total Revenue", "Amount Collected", "Date"],
        "fields": [
            {"name": "Product", "label": "اسم المنتج", "type": "text"},
            {"name": "Qty Sold", "label": "الكمية المباعة", "type": "int", "min": 1, "default": 1, "step": 1},
            {"name": "Unit Price", "label": "سعر البيع للوحدة (EGP)", "type": "number", "min": 0.0, "step": 10.0},
            {"name": "Amount Collected", "label": "المبلغ المحصّل فعليًا (EGP)", "type": "number", "min": 0.0, "step": 100.0},
            {"name": "Date", "label": "التاريخ", "type": "date"},
        ],
        "computed_field": {"name": "Total Revenue", "of": ["Qty Sold", "Unit Price"]},
        "total_field": "Total Revenue",
        "add_label": "+ تسجيل عملية بيع",
    },
    # المصنع أولًا، الموديل ثانيًا، زي ما طلبت بالظبط
    "MANUFACTURING": {
        "label": "التصنيع (Manufacturing)",
        "columns": ["Factory", "Model", "Qty", "Unit Price", "Total", "Date"],
        "fields": [
            {"name": "Factory", "label": "اسم المصنع", "type": "text"},
            {"name": "Model", "label": "اسم الموديل", "type": "text"},
            {"name": "Qty", "label": "الكمية", "type": "int", "min": 1, "default": 1, "step": 1},
            {"name": "Unit Price", "label": "سعر القطعة (EGP)", "type": "number", "min": 0.0, "step": 10.0},
            {"name": "Date", "label": "التاريخ", "type": "date"},
        ],
        "computed_field": {"name": "Total", "of": ["Qty", "Unit Price"]},
        "total_field": "Total",
        "add_label": "+ تسجيل أمر تصنيع",
    },
}

SHEET_NAMES = list(SECTIONS.keys())

# ==================================================================
# شيتات مستقلة تستخدمها باقي الصفحات
# ==================================================================
EXTRA_SHEETS_COLUMNS = {
    "CHAT": ["Time", "Sender", "Message"],
    "IDEAS": ["Date", "Type", "Title", "Notes"],
    "ADS_CAMPAIGNS": ["Campaign Name", "Daily Spend", "Monthly Spend"],
    "TASKS": ["ID", "Description", "Type", "Assigned To", "Status", "Claimed By"],
    "VISION": ["Target Name", "Type", "Target Value", "Actual Value"],
}

ALL_SHEETS = SHEET_NAMES + list(EXTRA_SHEETS_COLUMNS.keys())


def _default_for(name: str) -> pd.DataFrame:
    """نسخة نظيفة فاضية بالأعمدة الصح — من غير أي بيانات تجريبية."""
    if name in SECTIONS:
        return pd.DataFrame(columns=SECTIONS[name]["columns"])
    return pd.DataFrame(columns=EXTRA_SHEETS_COLUMNS[name])


# ==================================================================
# القراءة والحفظ (مع مزامنة جوجل درايف لو متظبطة)
# ==================================================================
def load_all_fresh() -> dict:
    """يقرأ كل الشيتات من ملف الإكسيل مباشرة من غير أي كاش. لو جوجل
    درايف متظبط، بينزل آخر نسخة منه الأول عشان البيانات تفضل متزامنة
    بين كل الأجهزة/الجلسات."""
    if gdrive.is_configured():
        gdrive.download_file(EXCEL_FILE)

    data = {}
    if os.path.exists(EXCEL_FILE):
        try:
            xls = pd.ExcelFile(EXCEL_FILE)
            for name in ALL_SHEETS:
                if name in xls.sheet_names:
                    data[name] = pd.read_excel(xls, sheet_name=name)
        except Exception as e:
            st.warning(f"تعذر قراءة {EXCEL_FILE}: {e}")
    for name in ALL_SHEETS:
        if name not in data:
            data[name] = _default_for(name)
    return data


def save_sheet(name: str, df: pd.DataFrame):
    """يحفظ شيت واحد، ويعيد كتابة الملف كله محليًا، وبعدين يرفعه على
    جوجل درايف لو متظبط، عشان أي تعديل أو حذف يتحفظ فورًا وبشكل دائم."""
    data = load_all_fresh()
    data[name] = df
    try:
        with pd.ExcelWriter(EXCEL_FILE, engine="openpyxl") as writer:
            for n, d in data.items():
                d.to_excel(writer, sheet_name=n, index=False)
    except PermissionError:
        return False, "الملف مفتوح في برنامج تاني — اقفله وحاول تاني."
    except Exception as e:
        return False, str(e)

    if gdrive.is_configured():
        gdrive.upload_file(EXCEL_FILE)

    return True, None


# ==================================================================
# جدول قابل للتعديل بيتحفظ أوتوماتيك + تراجع/إعادة (Undo/Redo)
# ==================================================================
def _history(name: str) -> dict:
    key = f"_history_{name}"
    if key not in st.session_state:
        st.session_state[key] = {"past": [], "future": []}
    return st.session_state[key]


def record_change(name: str, df_before: pd.DataFrame):
    h = _history(name)
    h["past"].append(df_before.copy())
    if len(h["past"]) > MAX_HISTORY:
        h["past"].pop(0)
    h["future"].clear()


def undo_redo_controls(name: str, current_df: pd.DataFrame):
    h = _history(name)
    c1, c2, c3 = st.columns([1, 1, 6])
    if c1.button("⬅️ تراجع", key=f"undo_{name}", disabled=not h["past"], use_container_width=True):
        h["future"].append(current_df.copy())
        restored = h["past"].pop()
        save_sheet(name, restored)
        st.rerun()
    if c2.button("إعادة ➡️", key=f"redo_{name}", disabled=not h["future"], use_container_width=True):
        h["past"].append(current_df.copy())
        restored = h["future"].pop()
        save_sheet(name, restored)
        st.rerun()
    c3.caption(f"🕘 تراجع/إعادة لحد {MAX_HISTORY} خطوات لورا")


def editable_table(name: str, df: pd.DataFrame, num_rows: str = "dynamic", key: str = None, show_undo: bool = True):
    """جدول Streamlit عادي، لكن أي تعديل (إضافة/حذف/تغيير) بيتحفظ
    أوتوماتيك على طول من غير زرار حفظ، ومعاه تراجع/إعادة لحد 10 خطوات."""
    key = key or f"editor_{name}"
    if show_undo:
        undo_redo_controls(name, df)

    edited = st.data_editor(df, num_rows=num_rows, use_container_width=True, key=key)

    if not edited.equals(df):
        record_change(name, df)
        ok, err = save_sheet(name, edited)
        if ok:
            st.toast("تم الحفظ أوتوماتيك ✅", icon="💾")
        else:
            st.error(f"فشل الحفظ التلقائي: {err}")
        return edited

    return df


# ==================================================================
# تسجيل الدخول
# ==================================================================
def _valid_credentials(username: str, password: str) -> bool:
    try:
        creds = dict(st.secrets.get("credentials", {}))
    except Exception:
        creds = {}
    return username in creds and str(creds[username]) == password


def _login_form():
    st.markdown(
        """
        <div style="text-align:center; margin-top:60px;">
            <h1 style="font-size:3rem;">⚡ TAVEN OS</h1>
            <p style="color:#94a3b8;">النظام الإداري والمالي لبراند TAVEN</p>
        </div>
        """,
        unsafe_allow_html=True,
    )
    _, mid, _ = st.columns([1, 1.2, 1])
    with mid:
        with st.form("login_form"):
            st.subheader("🔐 تسجيل الدخول")
            username = st.text_input("اسم المستخدم")
            password = st.text_input("كلمة المرور", type="password")
            submitted = st.form_submit_button("دخول", use_container_width=True)

        if submitted:
            if _valid_credentials(username, password):
                st.session_state.authenticated = True
                st.session_state.username = username
                st.rerun()
            else:
                angry_warning("اسم المستخدم أو كلمة المرور غلط! جرب تاني")


def sidebar_user_box():
    with st.sidebar:
        st.markdown("---")
        st.caption(f"👤 مسجل دخول باسم: **{st.session_state.get('username', '')}**")
        if st.button("🚪 تسجيل خروج", key="logout_btn", use_container_width=True):
            st.session_state.authenticated = False
            st.session_state.pop("username", None)
            st.rerun()
        st.caption(gdrive.status_message())


def require_login():
    """حط السطر ده أول حاجة في كل صفحة (بعد set_page_config و inject_theme_css).
    لو مش مسجل دخول، هيوقف السكريبت هنا ويعرض فورم الدخول."""
    if not st.session_state.get("authenticated"):
        _login_form()
        st.stop()
    sidebar_user_box()


# ==================================================================
# التنسيق العام
# ==================================================================
def inject_theme_css():
    st.markdown(
        """
<style>
@import url('https://fonts.googleapis.com/css2?family=Inter:wght@400;500;600;700&display=swap');

@keyframes fadeIn {
    0% { opacity: 0; transform: translateY(10px); }
    100% { opacity: 1; transform: translateY(0); }
}
@keyframes shake {
    0%, 100% { transform: translateX(0); }
    20%, 60% { transform: translateX(-8px); }
    40%, 80% { transform: translateX(8px); }
}

html, body, [class*="css"] {
    font-family: 'Inter', sans-serif;
}

.stApp {
    animation: fadeIn 0.4s ease-in-out;
}

div[data-testid="stMetric"] {
    background: var(--secondary-background-color);
    border: 1px solid rgba(99, 102, 241, 0.25);
    border-radius: 12px;
    padding: 14px;
    box-shadow: 0 2px 10px rgba(0, 0, 0, 0.15);
    transition: transform 0.15s ease-in-out;
}
div[data-testid="stMetric"]:hover {
    transform: translateY(-2px);
}

.stButton>button {
    border-radius: 8px;
    background: linear-gradient(135deg, #6366f1, #4338ca);
    color: #ffffff !important;
    font-weight: 600;
    border: none;
    width: 100%;
    padding: 10px;
    transition: transform 0.12s ease-in-out, box-shadow 0.12s ease-in-out;
}
.stButton>button:hover {
    transform: translateY(-1px);
    box-shadow: 0 4px 14px rgba(99, 102, 241, 0.45);
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

/* استجابة أفضل على الموبايل */
@media (max-width: 640px) {
    div[data-testid="stMetric"] { padding: 8px; }
    div[data-testid="stMetricValue"] { font-size: 1.1rem; }
    .stButton>button { padding: 8px; font-size: 0.9rem; }
}
</style>
""",
        unsafe_allow_html=True,
    )


def angry_warning(message: str = "في حقل فاضي يا أسطى! كمّل البيانات الأول"):
    st.markdown(f'<div class="angry-alert">😡 {message}</div>', unsafe_allow_html=True)
