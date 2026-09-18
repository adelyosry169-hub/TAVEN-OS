
from datetime import date
import pandas as pd
import streamlit as st
import common

st.set_page_config(page_title="TAVEN CO — Ideas & Plans", page_icon="T", layout="wide")
common.inject_theme_css()
common.page_header("Ideas & Plans","حوّل الأفكار إلى سجل منظم وخطط قابلة للمتابعة","Ideas & Plans")
df=common.load_all_fresh()["IDEAS"]
left,right=st.columns([1.6,1])
with left:
    common.card_open("Idea backlog")
    common.editable_table("IDEAS",df,key="ideas_table")
    common.card_close()
with right:
    common.card_open("New idea")
    typ=st.selectbox("النوع",["فكرة","خطة","كولكشن جديد","اقتراح عميل","ملاحظة"])
    title=st.text_input("العنوان"); notes=st.text_area("التفاصيل")
    if st.button("إضافة",type="primary",use_container_width=True):
        if not title.strip(): st.error("أدخل عنوانًا.")
        else:
            updated=pd.concat([df,pd.DataFrame([{"Date":str(date.today()),"Type":typ,"Title":title,"Notes":notes}])],ignore_index=True)
            ok,err=common.save_sheet("IDEAS",updated)
            if ok: st.toast("تمت الإضافة",icon="✓"); st.rerun()
            else: st.error(err)
    common.card_close()
common.card_open("Collection gallery")
imgs=st.file_uploader("صور",type=["png","jpg","jpeg"],accept_multiple_files=True)
if imgs:
    cols=st.columns(4)
    for i,img in enumerate(imgs): cols[i%4].image(img,use_container_width=True)
else: st.caption("المعرض مؤقت للجلسة الحالية.")
common.card_close(); common.end_page()
