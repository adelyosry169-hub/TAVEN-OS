
import pandas as pd
import streamlit as st
import common

st.set_page_config(page_title="TAVEN CO — Ads Manager", page_icon="T", layout="wide")
common.inject_theme_css()
common.page_header("Ads Manager","متابعة ميزانيات الحملات المسجلة يدويًا","Ads Manager")
df=common.load_all_fresh()["ADS_CAMPAIGNS"]
daily=float(df["Daily Spend"].sum()) if "Daily Spend" in df else 0
monthly=float(df["Monthly Spend"].sum()) if "Monthly Spend" in df else 0
a,b=st.columns(2)
with a: common.kpi("Daily spend",common.fmt_egp(daily))
with b: common.kpi("Monthly forecast",common.fmt_egp(monthly))
left,right=st.columns([1.6,1])
with left:
    common.card_open("Campaigns")
    common.editable_table("ADS_CAMPAIGNS",df,key="ads_table")
    common.card_close()
with right:
    common.card_open("New campaign")
    name=st.text_input("اسم الحملة"); spend=st.number_input("الصرف اليومي (EGP)",min_value=0.0,step=10.0)
    if st.button("إضافة حملة",type="primary",use_container_width=True):
        if not name.strip(): st.error("أدخل اسم الحملة.")
        else:
            updated=pd.concat([df,pd.DataFrame([{"Campaign Name":name,"Daily Spend":spend,"Monthly Spend":spend*30}])],ignore_index=True)
            ok,err=common.save_sheet("ADS_CAMPAIGNS",updated)
            if ok: st.toast("تمت الإضافة",icon="✓"); st.rerun()
            else: st.error(err)
    common.card_close()
common.end_page()
