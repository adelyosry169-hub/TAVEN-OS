import pandas as pd
import streamlit as st
import common

st.set_page_config(page_title="TAVEN OS - Input & Output المالية", page_icon="💰", layout="wide")
common.inject_theme_css()

SECTIONS = common.SECTIONS
SHEET_NAMES = common.SHEET_NAMES

# نحمّل نسخة شغل في الـ session مرة واحدة بس، وبعدين كل تعديل بيحصل
# في الذاكرة فورًا (بدون ما نلمس الملف كل حرف بيتكتب). زرار الحفظ
# هو اللي بيثبّت النسخة دي في TAVEN.xlsx.
if "io_data" not in st.session_state:
    fresh = common.load_all_fresh()
    st.session_state.io_data = {name: fresh[name] for name in SHEET_NAMES}

st.title("💰 Input & Output المالية")

# بنحجز مكان للمؤشرات هنا فوق، لكن هنملاه في آخر السكريبت بعد ما نتأكد
# إن آخر تعديل في الجدول (لو حصل في نفس هذا الـ run) اتسجل فعلاً.
# ده اللي بيخلي الأرقام تتحدث لحظيًا من غير أي تأخير دورة كاملة.
header_slot = st.empty()

section_key = st.radio(
    "اختر القسم",
    SHEET_NAMES,
    format_func=lambda k: SECTIONS[k]["label"],
    horizontal=True,
)

st.markdown("---")


def render_section(key):
    cfg = SECTIONS[key]
    col_table, col_form = st.columns([2.2, 1])

    with col_table:
        st.subheader(f"جدول {cfg['label']}")
        edited = st.data_editor(
            st.session_state.io_data[key],
            num_rows="dynamic",
            use_container_width=True,
            key=f"editor_{key}",
        )
        st.session_state.io_data[key] = edited

        total_field = cfg.get("total_field")
        if total_field and total_field in edited:
            st.info(f"📊 إجمالي {cfg['label']}: {edited[total_field].sum():,.2f} EGP")

        if st.button("💾 حفظ نهائي في ملف الإكسيل", key=f"save_{key}"):
            ok, err = common.save_sheet(key, edited)
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

        # أول حقل نصي بنعتبره الحقل المطلوب (زي المنطق الأصلي)
        required_field = next((f["name"] for f in cfg["fields"] if f["type"] == "text"), None)

        if st.button(cfg["add_label"], key=f"add_{key}"):
            if required_field and not str(values.get(required_field, "")).strip():
                common.angry_warning(f"مينفعش تسيب '{required_field}' فاضي يا أسطى! كمّل البيانات")
            else:
                new_row = pd.DataFrame([values])
                st.session_state.io_data[key] = pd.concat(
                    [st.session_state.io_data[key], new_row], ignore_index=True
                )
                st.success("تمت الإضافة للجدول! (اضغط 'حفظ نهائي' عشان تثبّتها في الإكسيل)")
                st.rerun()


render_section(section_key)

# ================== حساب المؤشرات بعد ما القسم اتحدّث فعليًا ==================
d = st.session_state.io_data
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
