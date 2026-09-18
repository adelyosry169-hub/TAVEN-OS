from datetime import date

import pandas as pd
import streamlit as st
import common

st.set_page_config(page_title="TAVEN OS - Input & Output المالية", page_icon="💰", layout="wide")
common.inject_theme_css()
common.require_login()

SECTIONS = common.SECTIONS
SHEET_NAMES = common.SHEET_NAMES

st.title("💰 Input & Output المالية")

# بنحجز مكان للمؤشرات هنا فوق، ونملاه في آخر السكريبت بعد ما نتأكد
# إن أي تعديل حصل دلوقتي اتحفظ فعلاً — عشان الأرقام تتحدث لحظيًا
# من غير أي تأخير دورة كاملة.
header_slot = st.empty()

# سيلكت بوكس بدل الأزرار الأفقية = أسهل على شاشة الموبايل الصغيرة
section_key = st.selectbox(
    "اختر القسم",
    SHEET_NAMES,
    format_func=lambda k: SECTIONS[k]["label"],
)

st.markdown("---")

data = common.load_all_fresh()


def render_section(key):
    cfg = SECTIONS[key]
    current_df = data[key]

    col_table, col_form = st.columns([2.2, 1])

    with col_table:
        st.subheader(f"جدول {cfg['label']}")
        st.caption("أي تعديل أو حذف هنا بيتحفظ أوتوماتيك على طول ✅")
        edited = common.editable_table(key, current_df)

        total_field = cfg.get("total_field")
        if total_field and total_field in edited and not edited.empty:
            st.info(f"📊 إجمالي {cfg['label']}: {edited[total_field].sum():,.2f} EGP")

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
            elif f["type"] == "date":
                values[f["name"]] = st.date_input(f["label"], value=date.today(), key=widget_key)
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

        # أول حقل نصي بنعتبره الحقل المطلوب
        required_field = next((f["name"] for f in cfg["fields"] if f["type"] == "text"), None)

        if st.button(cfg["add_label"], key=f"add_{key}"):
            if required_field and not str(values.get(required_field, "")).strip():
                common.angry_warning(f"مينفعش تسيب '{required_field}' فاضي يا أسطى! كمّل البيانات")
            else:
                values["Date"] = str(values.get("Date", date.today()))
                new_row = pd.DataFrame([values])
                before = current_df.copy()
                updated = pd.concat([current_df, new_row], ignore_index=True)
                common.record_change(key, before)
                ok, err = common.save_sheet(key, updated)
                if ok:
                    st.success("تمت الإضافة واتحفظت أوتوماتيك! ✅")
                    st.rerun()
                else:
                    st.error(err)


render_section(section_key)

# ================== حساب المؤشرات بعد ما القسم اتحدّث فعليًا ==================
d = common.load_all_fresh()
gross_val = d["SALES"]["Total Revenue"].sum() if "Total Revenue" in d["SALES"] else 0
realized = d["SALES"]["Amount Collected"].sum() if "Amount Collected" in d["SALES"] else 0
total_exp = (
    (d["FINANCE"]["Total"].sum() if "Total" in d["FINANCE"] else 0)
    + (d["OPERATIONS"]["Cost"].sum() if "Cost" in d["OPERATIONS"] else 0)
    + (d["EXTRA_EXPENSES"]["Total"].sum() if "Total" in d["EXTRA_EXPENSES"] else 0)
    + (d["MANUFACTURING"]["Total"].sum() if "Total" in d["MANUFACTURING"] else 0)
)
net_profit = realized - total_exp

with header_slot.container():
    m1, m2, m3, m4 = st.columns(4)
    m1.metric("Gross Val (إجمالي المبيعات)", f"{gross_val:,.0f} EGP")
    m2.metric("Realized (المحصّل فعليًا)", f"{realized:,.0f} EGP")
    m3.metric("Total Exp (فاينانس + عمليات + إضافية + تصنيع)", f"{total_exp:,.0f} EGP")
    m4.metric("Net Profit (صافي الربح)", f"{net_profit:,.0f} EGP")
    st.markdown("---")
