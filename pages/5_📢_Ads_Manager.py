import pandas as pd
import streamlit as st
import common

st.set_page_config(page_title="TAVEN OS - Ads Manager", page_icon="📢", layout="wide")
common.inject_theme_css()
common.require_login()

st.title("📢 Ads Manager (Meta)")

data = common.load_all_fresh()
ads_df = data["ADS_CAMPAIGNS"]

col_table, col_form = st.columns([2, 1])

with col_table:
    st.subheader("الكامبينات الحالية")
    st.caption("أي تعديل أو حذف هنا بيتحفظ أوتوماتيك ✅")
    edited = common.editable_table("ADS_CAMPAIGNS", ads_df)

    if not edited.empty and "Daily Spend" in edited.columns:
        c1, c2 = st.columns(2)
        c1.metric("إجمالي الصرف اليومي (كل الكامبينات)", f"{edited['Daily Spend'].sum():,.0f} EGP")
        c2.metric("إجمالي الصرف الشهري المتوقع", f"{(edited['Daily Spend'].sum() * 30):,.0f} EGP")

with col_form:
    st.subheader("إضافة كامبين جديد")
    name = st.text_input("Campaign Name")
    daily = st.number_input("الصرف اليومي (EGP)", min_value=0.0, step=10.0)
    monthly = daily * 30
    st.markdown(f"### الصرف الشهري المتوقع: **{monthly:,.0f} EGP**")

    if st.button("+ إضافة كامبين"):
        if not name.strip():
            common.angry_warning("لازم اسم للكامبين الأول!")
        else:
            before = ads_df.copy()
            new_row = pd.DataFrame(
                [{"Campaign Name": name, "Daily Spend": daily, "Monthly Spend": monthly}]
            )
            updated = pd.concat([ads_df, new_row], ignore_index=True)
            common.record_change("ADS_CAMPAIGNS", before)
            ok, err = common.save_sheet("ADS_CAMPAIGNS", updated)
            if ok:
                st.success("اتضاف الكامبين واتحفظ! ✅")
                st.rerun()
            else:
                st.error(err)
