
import pandas as pd
import streamlit as st
import common

st.set_page_config(page_title="TAVEN CO — Vision & Targets", page_icon="T", layout="wide")
common.inject_theme_css()
common.page_header("Vision & Targets","حوّل أهدافك إلى أرقام يمكن متابعتها","Vision & Targets")
df=common.load_all_fresh()["VISION"]
left,right=st.columns([1.6,1])
with left:
    common.card_open("Targets")
    if df.empty: st.info("أضف أول هدف من اليمين.")
    else:
        for _,r in df.iterrows():
            target=float(r.get("Target Value",0) or 0); actual=float(r.get("Actual Value",0) or 0)
            pct=min(actual/target,1) if target else 0
            st.markdown(f"**{r.get('Target Name','')}** · {r.get('Type','')}")
            st.progress(pct)
            st.caption(f"المحقق {actual:,.0f} / المطلوب {target:,.0f} · {pct*100:.0f}%")
            st.divider()
    common.card_close()
    common.card_open("Edit data")
    common.editable_table("VISION",df,key="vision_table")
    common.card_close()
with right:
    common.card_open("New target")
    name=st.text_input("اسم الهدف"); typ=st.selectbox("النوع",["شهري","ثانوي"])
    target=st.number_input("القيمة المطلوبة",min_value=0.0,step=100.0); actual=st.number_input("المحقق حاليًا",min_value=0.0,step=100.0)
    if st.button("إضافة هدف",type="primary",use_container_width=True):
        if not name.strip(): st.error("أدخل اسم الهدف.")
        else:
            row={"Target Name":name,"Type":typ,"Target Value":target,"Actual Value":actual}
            ok,err=common.save_sheet("VISION",pd.concat([df,pd.DataFrame([row])],ignore_index=True))
            if ok: st.toast("تمت الإضافة",icon="✓"); st.rerun()
            else: st.error(err)
    common.card_close()
common.end_page()
