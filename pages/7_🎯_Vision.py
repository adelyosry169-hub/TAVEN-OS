import pandas as pd
import streamlit as st
import common

st.set_page_config(page_title="TAVEN OS - Vision & Targets", page_icon="🎯", layout="wide")
common.inject_theme_css()
common.require_login()

st.title("🎯 الرؤية والأهداف (Targets)")

data = common.load_all_fresh()
vision_df = data["VISION"]

col_table, col_form = st.columns([2, 1])

with col_table:
    st.subheader("الأهداف الحالية")
    st.caption("أي تعديل أو حذف هنا بيتحفظ أوتوماتيك ✅")
    edited = common.editable_table("VISION", vision_df)

    st.markdown("---")
    st.subheader("📊 نتيجة كل هدف")
    if not edited.empty and "Target Value" in edited.columns and "Actual Value" in edited.columns:
        for _, row in edited.iterrows():
            try:
                achieved = float(row["Actual Value"]) >= float(row["Target Value"])
            except (TypeError, ValueError):
                achieved = False
            icon = "✅" if achieved else "❌"
            color = "#052e16" if achieved else "#450a0a"
            text_color = "#4ade80" if achieved else "#f87171"
            st.markdown(
                f"<div style='background:{color}; color:{text_color}; padding:10px; "
                f"border-radius:8px; margin-bottom:6px; font-weight:600;'>"
                f"{icon} {row.get('Target Name', '')} ({row.get('Type', '')}) — "
                f"المطلوب: {row.get('Target Value', 0):,.0f} | المحقق: {row.get('Actual Value', 0):,.0f}"
                f"</div>",
                unsafe_allow_html=True,
            )
    else:
        st.caption("ضيف هدف جديد من الفورم على اليمين عشان تشوف النتيجة هنا.")

with col_form:
    st.subheader("إضافة هدف جديد")
    name = st.text_input("اسم الهدف")
    ttype = st.selectbox("النوع", ["شهري", "ثانوي"])
    target_val = st.number_input("القيمة المطلوبة", min_value=0.0, step=100.0)
    actual_val = st.number_input("القيمة المحققة حاليًا", min_value=0.0, step=100.0)

    if st.button("+ إضافة هدف"):
        if not name.strip():
            common.angry_warning("محتاج اسم للهدف الأول!")
        else:
            before = vision_df.copy()
            new_row = pd.DataFrame(
                [{"Target Name": name, "Type": ttype, "Target Value": target_val, "Actual Value": actual_val}]
            )
            updated = pd.concat([vision_df, new_row], ignore_index=True)
            common.record_change("VISION", before)
            ok, err = common.save_sheet("VISION", updated)
            if ok:
                st.success("اتضاف الهدف واتحفظ! ✅")
                st.rerun()
            else:
                st.error(err)
