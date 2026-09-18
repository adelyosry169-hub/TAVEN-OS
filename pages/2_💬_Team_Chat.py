
from datetime import datetime
import pandas as pd
import streamlit as st
import common

st.set_page_config(page_title="TAVEN CO — Team Chat", page_icon="T", layout="wide")
common.inject_theme_css()
common.page_header("Team Chat","مساحة سريعة لتواصل الفريق وتسجيل القرارات","Team Chat")
data=common.load_all_fresh(); df=data["CHAT"]
left,right=st.columns([1.5,1])
with left:
    common.card_open("Conversation","آخر الرسائل المحفوظة على TAVEN.xlsx")
    if df.empty: st.info("لا توجد رسائل بعد.")
    else:
        for _,r in df.tail(40).iterrows():
            st.markdown(f"**{r.get('Sender','')}** · {r.get('Time','')}")
            st.write(r.get("Message",""))
            st.divider()
    common.card_close()
with right:
    common.card_open("New message")
    sender=st.selectbox("المرسل",["عادل","الياباني","الروسي"])
    msg=st.text_area("الرسالة",height=150)
    if st.button("إرسال",type="primary",use_container_width=True):
        if not msg.strip(): st.error("اكتب رسالة أولًا.")
        else:
            updated=pd.concat([df,pd.DataFrame([{"Time":datetime.now().strftime("%Y-%m-%d %H:%M"),"Sender":sender,"Message":msg}])],ignore_index=True)
            ok,err=common.save_sheet("CHAT",updated)
            if ok: st.toast("تم الإرسال",icon="✓"); st.rerun()
            else: st.error(err)
    common.card_close()
common.end_page()
