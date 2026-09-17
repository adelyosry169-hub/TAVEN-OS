import pandas as pd
import streamlit as st
import common

st.set_page_config(page_title="TAVEN OS - Ads Manager", page_icon="📢", layout="wide")
common.inject_theme_css()

st.title("📢 Ads Manager (Meta)")

data = common.load_all_fresh()
ads_df = data["ADS_CAMPAIGNS"]

col_table, col_form = st.columns([2, 1])

with col_table:
    st.subheader("الكامبينات الحالية")
    edited = st.data_editor(ads_df, num_rows="dynamic", use_container_width=True, key="ads_editor")

    # نحدث الصرف الشهري أوتوماتيك = الصرف اليومي × 30، حتى لو الصف اتعدل يدوي
    if "Daily Spend" in edited.columns:
        edited["Monthly Spend"] = edited["Daily Spend"].fillna(0) * 30

    if st.button("💾 حفظ التعديلات"):
        ok, err = common.save_sheet("ADS_CAMPAIGNS", edited)
        if ok:
            st.success("تم الحفظ!")
        else:
            st.error(err)

    if not edited.empty and "Daily Spend" in edited.columns:
        c1, c2 = st.columns(2)
        c1.metric("إجمالي الصرف اليومي (كل الكامبينات)", f"{edited['Daily Spend'].sum():,.0f} EGP")
        c2.metric("إجمالي الصرف الشهري المتوقع", f"{edited['Monthly Spend'].sum():,.0f} EGP")

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
            new_row = pd.DataFrame(
                [{"Campaign Name": name, "Daily Spend": daily, "Monthly Spend": monthly}]
            )
            updated = pd.concat([ads_df, new_row], ignore_index=True)
            ok, err = common.save_sheet("ADS_CAMPAIGNS", updated)
            if ok:
                st.success("اتضاف الكامبين!")
                st.rerun()
            else:
                st.error(err)
